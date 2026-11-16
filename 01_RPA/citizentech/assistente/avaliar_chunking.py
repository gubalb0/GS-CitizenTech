"""Compara configuracoes de chunking no corpus DODF completo (somente VALIDACAO; o teste de 350 NAO e usado).
Uso: python -m citizentech.assistente.avaliar_chunking

Metricas (nenhuma depende de retriever ou LLM):
- numero e tamanho dos chunks (tokens de superficie), inflacao de tokens por overlap;
- qualidade de fronteira: % de fronteiras internas que caem em fim de frase/item ([.;:]) — "corte limpo";
- PROXY de integridade de evidencia (perguntas NAO-MULTI): fracao em que TODOS os valores-chave da resposta presentes no
  documento (R$, CNPJ, numero de processo, numero/ano) ficam no MESMO chunk. Os valores-chave vem do texto da resposta e do
  documento exato (associacao comprovada); nao ha gabarito inventado. Perguntas MULTI ficam fora desse proxy.
"""
import json
import re
import statistics as st
import time

from . import associacao as A
from . import dados as D
from .chunking import ConfigChunk, chunkear_corpus, contar_tokens

SAIDA = D.RAIZ / "data_assistente" / "derivados"
CONFIGS = [ConfigChunk(e, m, o) for e in ("tamanho", "estrutura") for m in (300, 500, 700) for o in (0, round(m * 0.1))]

_VALOR = [re.compile(p) for p in (r"R\$\s?\d[\d\.]*,\d{2}", r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", r"\d{5}-\d{8}/\d{4}-\d{2}",
                                  r"\b\d{1,5}/\d{4}\b")]


def _sem_esp(t: str) -> str:
    return re.sub(r"\s+", "", t)


def valores_chave(resposta: str, texto_doc: str) -> list[str]:
    doc = _sem_esp(texto_doc)
    achados = []
    for p in _VALOR:
        for m in p.finditer(resposta):
            v = _sem_esp(m.group(0))
            if v in doc and v not in achados:
                achados.append(v)
    return achados


def _corte_limpo(texto_doc: str, pos: int) -> bool:
    """A fronteira em `pos` (inicio do chunk) e limpa se o texto anterior (sem espacos) termina em [.;:]."""
    ant = texto_doc[:pos].rstrip()
    return bool(ant) and ant[-1] in ".;:"


def avaliar(cfg: ConfigChunk, corpus, docs_por_id, qa_nao_multi) -> dict:
    t0 = time.perf_counter()
    chunks = chunkear_corpus(corpus, cfg)
    dt = time.perf_counter() - t0
    nt = [c["n_tokens"] for c in chunks]
    por_doc: dict[str, list[dict]] = {}
    for c in chunks:
        por_doc.setdefault(c["doc_id"], []).append(c)
    internas = limpas = 0
    for did, lst in por_doc.items():
        txt = docs_por_id[int(did.split("-")[1])]["texto_completo"]
        for c in lst[1:]:
            internas += 1
            limpas += _corte_limpo(txt, c["char_inicio"])
    ev_ok = ev_n = 0
    for q, doc_ids in qa_nao_multi:
        d = docs_por_id[doc_ids[0]]
        vals = valores_chave(q["resposta"], d["texto_completo"])
        if not vals:
            continue
        ev_n += 1
        lst = por_doc.get(f"dodf-{doc_ids[0]}", [])
        ev_ok += any(all(v in _sem_esp(c["texto"]) for v in vals) for c in lst)
    return {"config": cfg.nome, "estrategia": cfg.estrategia, "max_tokens": cfg.max_tokens, "overlap": cfg.overlap_tokens,
            "n_chunks": len(chunks), "docs_com_chunks": len(por_doc), "tokens_total_nos_chunks": sum(nt),
            "tokens_medio": round(st.mean(nt), 1), "tokens_mediana": st.median(nt), "tokens_p10": sorted(nt)[len(nt) // 10],
            "tokens_p90": sorted(nt)[int(len(nt) * .9)], "tokens_max": max(nt), "acima_do_limite": sum(x > cfg.max_tokens for x in nt),
            "chunks_menores_que_metade": round(sum(x < cfg.max_tokens / 2 for x in nt) / len(nt), 3),
            "fronteiras_internas": internas, "fronteiras_limpas_pct": round(100 * limpas / internas, 1) if internas else None,
            "evidencia_unica": {"perguntas_avaliaveis": ev_n, "no_mesmo_chunk": ev_ok,
                                "pct": round(100 * ev_ok / ev_n, 1) if ev_n else None},
            "tempo_s": round(dt, 2)}


def main() -> dict:
    if not all(D.verificar_integridade().values()):
        raise SystemExit("integridade falhou")
    corpus, val = D.carregar_corpus(), D.carregar_validacao()
    assoc = A.associar_todas(corpus, val)
    docs = {d["id"]: d for d in corpus}
    qa_nm = [(q, a["doc_ids"]) for q, a in zip(val, assoc) if not a["multi"] and a["estado"] == "resolvida"]
    total_tokens = sum(contar_tokens(d["texto_completo"]) for d in corpus)
    res = {"corpus_tokens_superficie": total_tokens, "docs": len(corpus), "perguntas_nao_multi_usadas": len(qa_nm),
           "configs": [avaliar(c, corpus, docs, qa_nm) for c in CONFIGS]}
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "chunking_comparacao.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    return res


if __name__ == "__main__":
    r = main()
    print("corpus: docs", r["docs"], "| tokens de superficie", r["corpus_tokens_superficie"], "| perguntas nao-MULTI:", r["perguntas_nao_multi_usadas"])
    cab = f"{'config':<12}{'chunks':>8}{'tok_tot':>10}{'med':>6}{'p10':>5}{'p90':>5}{'max':>5}{'<50%':>6}{'fr.limpas%':>11}{'evid%':>7}{'n':>4}{'seg':>6}"
    print(cab)
    for c in r["configs"]:
        e = c["evidencia_unica"]
        print(f"{c['config']:<12}{c['n_chunks']:>8}{c['tokens_total_nos_chunks']:>10}{c['tokens_medio']:>6.0f}{c['tokens_p10']:>5}{c['tokens_p90']:>5}"
              f"{c['tokens_max']:>5}{c['chunks_menores_que_metade']:>6.2f}{(c['fronteiras_limpas_pct'] or 0):>11}{(e['pct'] or 0):>7}{e['perguntas_avaliaveis']:>4}{c['tempo_s']:>6}")
