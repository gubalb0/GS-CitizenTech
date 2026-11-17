"""Reconstrucao OFFLINE (sem LLM) dos chunks realmente enviados: Indice.buscar(bm25) + montar_contexto. Somente leitura."""
import json, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import avaliacao_e2e as AE
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto
from citizentech.assistente.retriever import Indice
corpus, val, assoc, dup, esperados, docs = AE.preparar()
idx = Indice.carregar(AE.IDX); cfg = ConfigGeracao()
R = {}
for l in open(r"D:\Downloads\GS\RPA\data_assistente\derivados\geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8"):
    o = json.loads(l); R[o["qid"]] = o
out = {}
for q, esp in zip(val, esperados):
    o = R[q["qid"]]
    res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25")
    ctx = montar_contexto(q["pergunta"], res, cfg)
    tel = o["saida"]["telemetria"]
    ids_run = [f["chunk_id"] for f in o["fontes_recuperadas"]]
    sent = {i.doc_id for i in ctx.itens}
    for i in ctx.itens: sent |= set(i.ids_equivalentes)
    pref = [r.chunk_id for r in res[:len(ctx.itens)]]
    out[q["qid"]] = {"mesma_recuperacao": [r.chunk_id for r in res] == ids_run, "n_enviados_replay": len(ctx.itens), "n_enviados_run": tel["chunks_enviados"],
                     "enviados_replay": [i.chunk_id for i in ctx.itens], "enviados_eh_prefixo": [i.chunk_id for i in ctx.itens] == pref, "grupo_run": o["grupo"],
                     "grupo_real": "A" if any(g & sent for g in esp) else "B"}
json.dump(out, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\replay_contexto.json", "w"), indent=1)
from collections import Counter
print("mesma recuperacao:", Counter(v["mesma_recuperacao"] for v in out.values()), "| n_enviados igual:", Counter(v["n_enviados_replay"] == v["n_enviados_run"] for v in out.values()))
mud = [(k, v["grupo_run"], v["grupo_real"]) for k, v in out.items() if v["grupo_run"] != v["grupo_real"]]
print("grupo muda:", len(mud), mud)
print("nao-prefixo:", [k for k,v in out.items() if not v["enviados_eh_prefixo"]])
