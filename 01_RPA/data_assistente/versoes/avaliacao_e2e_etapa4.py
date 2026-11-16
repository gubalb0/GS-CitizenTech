"""Avaliacao END-TO-END DIAGNOSTICA: retriever congelado (est300o30, BM25, 5 chunks) -> gerador, nas 150 perguntas de validacao.

ATENCAO: as 150 perguntas ja foram usadas na avaliacao do retriever. Esta avaliacao e diagnostica (separa falha de
recuperacao de falha de geracao); NAO e uma medida independente de generalizacao. O conjunto de teste (350) nao e usado.
Uso: python -m citizentech.assistente.avaliacao_e2e   (retomavel; grava data_assistente/derivados/geracao_e2e.jsonl)
"""
from __future__ import annotations

import json
import re
import time

from . import associacao as A
from . import dados as D
from .avaliar_chunking import _sem_esp, valores_chave
from .dedup import agrupar_duplicatas
from .geracao import ClienteLMStudio, ConfigGeracao, gerar_resposta
from .retriever import Indice

SAIDA = D.RAIZ / "data_assistente" / "derivados"
IDX = D.RAIZ / "data_assistente" / "indices" / "est300o30"
NAO_UNIVOCAS = {"val-005", "val-018", "val-023", "val-120", "val-122", "val-146"}
LIMITACAO = re.compile(r"parcial|apenas|somente|n[aã]o (?:h[aá]|consta|constam|foram|foi)|outras publica|limit|insuficien|n[aã]o foi poss", re.I)


def preparar():
    corpus, val = D.carregar_corpus(), D.carregar_validacao()
    assoc = A.associar_todas(corpus, val)
    dup = agrupar_duplicatas(corpus)
    esperados = []
    for a in assoc:
        gs = []
        for b in a["blocos"]:
            g = {dup.canonico_de[i] for i in b["doc_ids"]}
            if g and g not in gs:
                gs.append(g)
        esperados.append(gs)
    docs = {d["id"]: d for d in corpus}
    return corpus, val, assoc, dup, esperados, docs


def main(limite: int | None = None) -> None:
    corpus, val, assoc, dup, esperados, docs = preparar()
    idx = Indice.carregar(IDX)
    cfg = ConfigGeracao()
    cli = ClienteLMStudio(cfg)
    arq = SAIDA / "geracao_e2e.jsonl"
    feitos = {json.loads(l)["qid"] for l in arq.open(encoding="utf-8")} if arq.exists() else set()
    with arq.open("a", encoding="utf-8") as fh:
        for q, a, esp in list(zip(val, assoc, esperados))[:limite]:
            if q["qid"] in feitos:
                continue
            t0 = time.perf_counter()
            res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25")
            t_ret = time.perf_counter() - t0
            ctx_docs = {r.doc_id for r in res}
            achados = sum(1 for g in esp if g & ctx_docs)
            vals = []
            if not a["multi"]:
                vals = valores_chave(q["resposta"], docs[a["blocos"][0]["doc_ids"][0]]["texto_completo"])
            ctx_txt = _sem_esp(" ".join(r.texto for r in res))
            t1 = time.perf_counter()
            r = gerar_resposta(q["pergunta"], res, cli).para_dict()
            dt = time.perf_counter() - t1
            sem = _sem_esp(r["resposta"] or "")
            fontes_docs = {f["doc_id"] for f in r["fontes"]}
            o = {"qid": q["qid"], "pergunta": q["pergunta"], "multi": a["multi"], "nao_univoca": q["qid"] in NAO_UNIVOCAS,
                 "n_esperadas": len(esp), "n_esperadas_no_contexto": achados, "recuperou_fonte_correta": achados >= 1,
                 "recuperou_todas": achados == len(esp), "valores_chave": vals,
                 "contexto_tem_todos_os_valores": bool(vals) and all(_sem_esp(v) in ctx_txt for v in vals),
                 "resposta_tem_todos_os_valores": bool(vals) and all(_sem_esp(v) in sem for v in vals),
                 "cita_fonte_correta": any(g & fontes_docs for g in esp), "cita_so_fontes_corretas": bool(fontes_docs) and all(any(d in g for g in esp) for d in fontes_docs),
                 "declara_limitacao_heuristica": bool(LIMITACAO.search((r["resposta"] or "") + " " + (r["justificativa"] or ""))),
                 "resposta_referencia": q["resposta"], "docs_no_contexto": [r_.doc_id for r_ in res], "chunk_ids_contexto": [r_.chunk_id for r_ in res],
                 "tempo_recuperacao_s": round(t_ret, 4), "tempo_geracao_s": round(dt, 2), "saida": r}
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"{q['qid']} ret={'OK' if o['recuperou_fonte_correta'] else '--'} status={r['status']:<15} {dt:.1f}s tokens_prompt={r['telemetria'].get('tokens_prompt')}", flush=True)


if __name__ == "__main__":
    main()
