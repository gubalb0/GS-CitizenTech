"""Avaliacao do retriever nas 150 perguntas de VALIDACAO (o teste de 350 NAO e usado).
Uso: python -m citizentech.assistente.avaliar_retriever [config ...]

Relevancia = associacao comprovada (associacao.py): cada bloco do texto_publicacao e uma publicacao esperada; ids
duplicados sao equivalentes (grupo). Perguntas MULTI tem varias publicacoes esperadas. Metricas no nivel de PUBLICACAO:
o ranking de publicacoes e formado pela primeira aparicao de cada publicacao na lista de chunks recuperados.
"""
import json
import statistics as st
import sys
import time
from pathlib import Path

import numpy as np
import psutil

from . import associacao as A
from . import dados as D
from . import metricas as M
from .avaliar_chunking import _sem_esp, valores_chave
from .chunking import ConfigChunk, chunkear_corpus, contar_tokens
from .codificador import CodificadorE5
from .dedup import agrupar_duplicatas
from .retriever import Indice

RAIZ_IDX = D.RAIZ / "data_assistente" / "indices"
SAIDA = D.RAIZ / "data_assistente" / "derivados"
KS = (1, 3, 5, 10)
LIMITE_GIGANTE_TOKENS = 20_000        # documento "gigante": > 20 mil tokens de superficie (definicao desta avaliacao)

VARIANTES = {   # nome -> parametros de buscar()
    "bm25": {"modo": "bm25"},
    "vetorial": {"modo": "vetorial"},
    "hibrido": {"modo": "hibrido"},
    "vetorial_so_1a_janela": {"modo": "vetorial", "janela": "primeira"},      # simula truncamento em 512 tokens
    "hibrido_so_1a_janela": {"modo": "hibrido", "janela": "primeira"},
    "hibrido_max3_por_doc": {"modo": "hibrido", "max_por_doc": 3},
    "hibrido_rrf20": {"modo": "hibrido", "rrf_k": 20},
    "hibrido_rrf100": {"modo": "hibrido", "rrf_k": 100},
}


def preparar():
    corpus, val = D.carregar_corpus(), D.carregar_validacao()
    assoc = A.associar_todas(corpus, val)
    dup = agrupar_duplicatas(corpus)
    esperados = []
    for a in assoc:
        grupos = []
        for b in a["blocos"]:
            g = {dup.canonico_de[i] for i in b["doc_ids"]}
            if g and g not in grupos:          # blocos que apontam para a mesma publicacao canonica contam uma vez
                grupos.append(g)
        esperados.append(grupos)
    nu = json.loads((SAIDA / "associacao_resumo.json").read_text(encoding="utf-8"))["perguntas_nao_univocas"]
    pares_reais = [(n["q1"], n["q2"]) for n in nu if n["pergunta_identica"] or n["q1"] in ("val-005",)]
    nao_univocas = {q for p in pares_reais for q in p}
    tokens_doc = {d["id"]: contar_tokens(d["texto_completo"]) for d in corpus}
    gigantes = {dup.canonico_de[i] for i, n in tokens_doc.items() if n > LIMITE_GIGANTE_TOKENS}
    return corpus, val, assoc, dup, esperados, nao_univocas, gigantes


def indice_sem_dedup(idx: Indice, corpus: list[dict], dup) -> Indice:
    """Reconstroi um indice SEM deduplicacao reaproveitando os vetores do documento canonico (texto identico)."""
    from .bm25 import BM25
    chunks, vet, inicio = [], [], [0]
    pos = {(c["doc_numerico"], c["ordem"]): i for i, c in enumerate(idx.chunks)}
    nova = []
    for d in corpus:
        cano = dup.canonico_de[int(d["id"])]
        for c in chunkear_corpus([d], idx.config):
            ic = pos.get((cano, c["ordem"]))
            if ic is None:
                continue
            c["ids_equivalentes"] = [int(d["id"])]
            c["doc_numerico"] = int(d["id"])
            nova.append((c, ic))
    for c, ic in nova:
        a, b = idx.janela_inicio[ic], idx.janela_inicio[ic + 1]
        vet.append(idx.vetores[a:b])
        inicio.append(inicio[-1] + (b - a))
        chunks.append(c)
    b = idx.manifesto["bm25"]
    bm = BM25(b["k1"], b["b"], b["radical_leve"]).ajustar([c["texto_indexacao"] for c in chunks])
    return Indice(idx.config, chunks, bm, np.concatenate(vet), np.asarray(inicio), np.asarray([c["doc_numerico"] for c in chunks]),
                  {**idx.manifesto, "dedup": False})


def rodar(idx: Indice, queries, vq, params, canon_de=None, excluir_docs=None):
    """Retorna, por pergunta, (lista de chunks recuperados [Resultado], tempo em s)."""
    saidas = []
    for q, v in zip(queries, vq):
        t0 = time.perf_counter()
        r = idx.buscar(q, k=100, k_candidatos=100, vetor_consulta=v, **params)
        dt = time.perf_counter() - t0
        if excluir_docs:
            r = [x for x in r if x.doc_id not in excluir_docs]
        saidas.append((r, dt))
    return saidas


def ranking_pub(resultados, canon_de=None):
    docs = [x.doc_id for x in resultados]
    if canon_de:
        docs = [canon_de[d] for d in docs]
    return M.ranking_de_documentos(docs)


def agregar(linhas):
    n = len(linhas)
    if n == 0:
        return {"n": 0}
    out = {"n": n, "MRR": round(sum(l["rr"] for l in linhas) / n, 4),
           "tem_ao_menos_uma_correta@10": round(sum(l["hit@10"] for l in linhas) / n, 4)}
    for k in KS:
        out[f"Recall@{k}"] = round(sum(l[f"recall@{k}"] for l in linhas) / n, 4)
        out[f"Hit@{k}"] = round(sum(l[f"hit@{k}"] for l in linhas) / n, 4)
    multi = [l for l in linhas if l["multi"]]
    if multi:
        out["MULTI_cobertura_total@10"] = round(sum(l["cobertura_total@10"] for l in multi) / len(multi), 4)
    return out


def avaliar_variante(nome, idx, queries, vq, val, assoc, esperados, nao_univocas, gigantes, params, evid, canon_de=None, excluir=None):
    saidas = rodar(idx, queries, vq, params, excluir_docs=excluir)
    linhas, detalhe = [], []
    for q, a, esp, (res, dt) in zip(val, assoc, esperados, saidas):
        rk = ranking_pub(res, canon_de)
        l = {"qid": q["qid"], "multi": a["multi"], "n_esperadas": len(esp), "nao_univoca": q["qid"] in nao_univocas,
             "rr": M.reciprocal_rank(esp, rk), "pos": M.posicao_primeiro_relevante(esp, rk), "tempo_s": dt}
        for k in KS:
            l[f"recall@{k}"] = M.recall_at_k(esp, rk, k)
            l[f"hit@{k}"] = M.hit_at_k(esp, rk, k)
        l["cobertura_total@10"] = M.cobertura_total_at_k(esp, rk, 10)
        top10 = res[:10]
        docs10 = [x.doc_id for x in top10]
        l["docs_distintos_top10_chunks"] = len(set(docs10))
        l["max_chunks_mesmo_doc_top10"] = max((docs10.count(d) for d in set(docs10)), default=0)
        l["slots_gigantes_top10"] = sum(d in gigantes for d in docs10)
        alvo = set().union(*esp) if esp else set()
        l["slots_irrelevantes_top10"] = sum(d not in alvo for d in docs10)
        if q["qid"] in evid:
            for k in (5, 10):
                txt = _sem_esp(" ".join(x.texto for x in res[:k]))
                l[f"evidencia_completa@{k}chunks"] = all(v in txt for v in evid[q["qid"]])
        linhas.append(l)
        detalhe.append({"qid": q["qid"], "pos": l["pos"], "top5_docs": rk[:5], "esperados": [sorted(g) for g in esp],
                        "top3_chunks": [x.chunk_id for x in res[:3]]})
    resumo = {"todas": agregar(linhas), "nao_multi": agregar([l for l in linhas if not l["multi"]]),
              "multi": agregar([l for l in linhas if l["multi"]]),
              "sem_nao_univocas": agregar([l for l in linhas if not l["nao_univoca"]]),
              "nao_univocas_apenas": agregar([l for l in linhas if l["nao_univoca"]])}
    t = [l["tempo_s"] for l in linhas]
    resumo["latencia_consulta_ms"] = {"mediana": round(1000 * st.median(t), 2), "p95": round(1000 * sorted(t)[int(.95 * len(t))], 2),
                                      "media": round(1000 * st.mean(t), 2)}
    resumo["diversidade_top10_chunks"] = {
        "docs_distintos_media": round(st.mean(l["docs_distintos_top10_chunks"] for l in linhas), 2),
        "max_chunks_mesmo_doc_media": round(st.mean(l["max_chunks_mesmo_doc_top10"] for l in linhas), 2),
        "slots_de_docs_gigantes_pct": round(100 * sum(l["slots_gigantes_top10"] for l in linhas) / (10 * len(linhas)), 2),
        "slots_irrelevantes_pct": round(100 * sum(l["slots_irrelevantes_top10"] for l in linhas) / (10 * len(linhas)), 2)}
    ev = [l for l in linhas if "evidencia_completa@5chunks" in l]
    if ev:
        resumo["evidencia_valores_chave"] = {"perguntas": len(ev),
                                             "completa_nos_5_primeiros_chunks_pct": round(100 * sum(l["evidencia_completa@5chunks"] for l in ev) / len(ev), 1),
                                             "completa_nos_10_primeiros_chunks_pct": round(100 * sum(l["evidencia_completa@10chunks"] for l in ev) / len(ev), 1)}
    return resumo, linhas, detalhe


def sensibilidade_bm25(nomes):
    """So lexical: k1, b e radical leve. Apenas leitura (analise de sensibilidade nas 150 perguntas de validacao);
    os parametros padrao do indice NAO sao alterados por esta funcao."""
    from .bm25 import BM25
    corpus, val, assoc, dup, esperados, _, _ = preparar()
    out = {}
    for nome in nomes:
        idx = Indice.carregar(RAIZ_IDX / nome)
        textos = [c["texto_indexacao"] for c in idx.chunks]
        docs = idx.doc_de_chunk
        res = {}
        for stem in (False, True):
            bm = BM25(1.5, 0.75, stem).ajustar(textos)
            for k1 in (0.9, 1.2, 1.5, 2.0):
                for b in (0.4, 0.75, 0.9):
                    bm.reponderar(k1, b)
                    mrr = r10 = h10 = 0.0
                    for q, esp in zip(val, esperados):
                        ix, _ = bm.buscar(q["pergunta"], 100)
                        rk = M.ranking_de_documentos([int(docs[i]) for i in ix])
                        mrr += M.reciprocal_rank(esp, rk)
                        r10 += M.recall_at_k(esp, rk, 10)
                        h10 += M.hit_at_k(esp, rk, 10)
                    n = len(val)
                    res[f"radical={int(stem)} k1={k1} b={b}"] = {"MRR": round(mrr / n, 4), "Recall@10": round(r10 / n, 4), "Hit@10": round(h10 / n, 4)}
        out[nome] = res
    (SAIDA / "retriever_sensibilidade_bm25.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


RAZAO_QWEN = 1.6   # tokens do Qwen3 por token de superficie (mediana medida em 12 chunks na Etapa 2)


def curva_orcamento(nomes, ks=(1, 2, 3, 4, 5, 6, 8)):
    """Compara configuracoes com o MESMO orcamento de contexto do gerador: os k primeiros CHUNKS (nao documentos),
    com o consumo medio estimado em tokens do Qwen3 (n_tokens de superficie x 1,6)."""
    corpus, val, assoc, dup, esperados, _, _ = preparar()
    docs = {d["id"]: d for d in corpus}
    evid = {}
    for q, a in zip(val, assoc):
        if not a["multi"] and a["estado"] == "resolvida":
            v = valores_chave(q["resposta"], docs[a["doc_ids"][0]]["texto_completo"])
            if v:
                evid[q["qid"]] = v
    cod = CodificadorE5()
    queries = [q["pergunta"] for q in val]
    vq = cod.codificar_consultas(queries)
    out = {}
    for nome in nomes:
        idx = Indice.carregar(RAIZ_IDX / nome, cod.nome)
        out[nome] = {}
        for modo in ("bm25", "vetorial", "hibrido"):
            res = [idx.buscar(q, k=max(ks), modo=modo, vetor_consulta=v) for q, v in zip(queries, vq)]
            tab = {}
            for k in ks:
                hit = rec = cob = ev = tok = 0.0
                n_ev = 0
                for q, esp, r in zip(val, esperados, res):
                    top = r[:k]
                    docs_k = {x.doc_id for x in top}
                    achados = sum(1 for g in esp if g & docs_k)
                    hit += achados >= 1
                    rec += achados / len(esp)
                    cob += achados == len(esp)
                    tok += sum(x.metadados["n_tokens"] for x in top) * RAZAO_QWEN
                    if q["qid"] in evid:
                        n_ev += 1
                        ev += all(v in _sem_esp(" ".join(x.texto for x in top)) for v in evid[q["qid"]])
                n = len(val)
                tab[k] = {"Hit": round(hit / n, 3), "Recall_pubs": round(rec / n, 3), "cobertura_total": round(cob / n, 3),
                          "evidencia_completa_pct": round(100 * ev / n_ev, 1), "tokens_qwen_medios": int(tok / n)}
            out[nome][modo] = tab
    (SAIDA / "retriever_orcamento_contexto.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main(nomes):
    corpus, val, assoc, dup, esperados, nao_univocas, gigantes = preparar()
    docs = {d["id"]: d for d in corpus}
    queries = [q["pergunta"] for q in val]
    evid = {}
    for q, a in zip(val, assoc):
        if not a["multi"] and a["estado"] == "resolvida":
            v = valores_chave(q["resposta"], docs[a["doc_ids"][0]]["texto_completo"])
            if v:
                evid[q["qid"]] = v
    cod = CodificadorE5()
    t0 = time.perf_counter()
    vq = cod.codificar_consultas(queries)
    t_enc = time.perf_counter() - t0
    lat_enc = []
    for q in queries[:30]:
        t = time.perf_counter(); cod.codificar_consultas([q]); lat_enc.append(time.perf_counter() - t)
    res_total = {"perguntas": len(val), "nao_univocas": sorted(nao_univocas), "docs_gigantes": {"limite_tokens": LIMITE_GIGANTE_TOKENS, "n": len(gigantes), "ids": sorted(gigantes)},
                 "perguntas_com_evidencia_avaliavel": len(evid),
                 "latencia_codificar_consulta_ms": {"lote_150_total_s": round(t_enc, 2), "individual_mediana": round(1000 * st.median(lat_enc), 1),
                                                    "individual_p95": round(1000 * sorted(lat_enc)[int(.95 * len(lat_enc))], 1)}, "configs": {}}
    for nome in nomes:
        pasta = RAIZ_IDX / nome
        rss0 = psutil.Process().memory_info().rss
        idx = Indice.carregar(pasta, cod.nome)
        rss1 = psutil.Process().memory_info().rss
        info = {"manifesto": idx.manifesto, "tamanho_em_disco_mb": round(idx.tamanho_em_disco(pasta) / 1e6, 1),
                "rss_incremental_ao_carregar_mb": round((rss1 - rss0) / 1e6, 1), "chunks_de_docs_gigantes_pct": round(
                    100 * sum(1 for c in idx.chunks if c["doc_numerico"] in gigantes) / len(idx.chunks), 1),
                "variantes": {}}
        todos_detalhes = {}
        for vn, params in VARIANTES.items():
            resumo, linhas, detalhe = avaliar_variante(vn, idx, queries, vq, val, assoc, esperados, nao_univocas, gigantes, params, evid)
            info["variantes"][vn] = resumo
            todos_detalhes[vn] = {"linhas": linhas, "detalhe": detalhe}
            print(f"[{nome}] {vn}: todas={resumo['todas']}", flush=True)
        # sem documentos gigantes (filtro no resultado, aproximado pelos 100 candidatos)
        resumo, linhas, detalhe = avaliar_variante("hibrido", idx, queries, vq, val, assoc, esperados, nao_univocas, gigantes,
                                                   VARIANTES["hibrido"], evid, excluir=gigantes)
        info["variantes"]["hibrido_sem_docs_gigantes(filtro)"] = resumo
        # sem deduplicacao (reaproveita os vetores do canonico)
        if nome == nomes[0] or True:
            sd = indice_sem_dedup(idx, corpus, dup)
            resumo, linhas, detalhe = avaliar_variante("hibrido", sd, queries, vq, val, assoc, esperados, nao_univocas, gigantes,
                                                       VARIANTES["hibrido"], evid, canon_de=dup.canonico_de)
            info["variantes"]["hibrido_sem_dedup"] = resumo
            # quantos slots de documentos do top-10 de publicacoes sao duplicatas de uma publicacao ja listada
            repet, consultas_com_dup = 0, 0
            for q, v in zip(queries, vq):
                r = sd.buscar(q, k=100, modo="hibrido", vetor_consulta=v)
                top = r[:10]
                ids = {x.doc_id for x in top}
                grupos = {dup.canonico_de[i] for i in ids}
                repet += len(ids) - len(grupos)          # documentos DISTINTOS que sao copias de uma publicacao ja presente
                consultas_com_dup += len(ids) > len(grupos)
            info["sem_dedup_documentos_copia_no_top10_chunks_total"] = repet
            info["sem_dedup_consultas_com_copia_no_top10"] = consultas_com_dup
            info["sem_dedup"] = {"documentos": len(corpus), "chunks": len(sd.chunks)}
        res_total["configs"][nome] = info
        (SAIDA / f"retriever_detalhe_{nome}.json").write_text(json.dumps(todos_detalhes, ensure_ascii=False), encoding="utf-8")
    (SAIDA / "retriever_avaliacao.json").write_text(json.dumps(res_total, ensure_ascii=False, indent=2), encoding="utf-8")
    return res_total


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--orcamento":
        curva_orcamento(args[1:] or ["est500o50", "est300o30"])
    elif args and args[0] == "--sensibilidade-bm25":
        sensibilidade_bm25(args[1:] or ["est500o50", "est300o30"])
    else:
        main(args or ["est500o50", "est300o30"])
