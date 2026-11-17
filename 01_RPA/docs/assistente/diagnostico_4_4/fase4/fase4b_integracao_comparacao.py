"""Fase 4B (candidata) - comparacao OFFLINE: baseline 4A (flag off) x S1 atual (4B-prep, resultado gravado) x S1 conservadora INTEGRADA (flag on) x prototipo. Sem modelo."""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import avaliacao_e2e as AE
from citizentech.assistente import grupos as GR
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto
from citizentech.assistente.retriever import Indice

AQUI = Path(__file__).parent
prep = json.load(open(AQUI / "fase4b_selecao_comparacao.json", encoding="utf-8"))["por_pergunta"]
proto = json.load(open(AQUI / "avaliacao_s1_conservadora.json", encoding="utf-8"))["por_pergunta"]
corpus, val, assoc, dup, esp, docs = AE.preparar()
idx = Indice.carregar(AE.IDX)
off, on = ConfigGeracao(), ConfigGeracao(priorizar_atributo=True)
orig = {json.loads(l)["qid"]: json.loads(l) for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8")}
out = {}
for q, e in zip(val, esp):
    k = q["qid"]
    res = idx.buscar(q["pergunta"], k=5, modo="bm25")
    c0, c2 = montar_contexto(q["pergunta"], res, off), montar_contexto(q["pergunta"], res, on)
    ids = lambda c: [i.chunk_id for i in c.itens]
    out[k] = {"baseline": ids(c0), "s1_atual_4b_prep": prep[k]["ids1"], "s1_conservadora": ids(c2), "tokens": [c0.tokens_estimados, prep[k]["tokens1"], c2.tokens_estimados],
              "grupos": [GR.grupo_ab(e, c0.itens)[0], prep[k]["grupo1"], GR.grupo_ab(e, c2.itens)[0]], "status_4_3": orig[k]["saida"]["status"],
              "decisoes": [x for x in c2.selecao if x["decisao"] != "mantido" or "evitada" in x["motivo"]] if c2.selecao else []}
atual = [k for k, v in out.items() if v["baseline"] != v["s1_atual_4b_prep"]]
cons = [k for k, v in out.items() if v["baseline"] != v["s1_conservadora"]]
res = {"s1_atual_altera": atual, "s1_conservadora_altera": cons, "inalterados_conservadora": len(out) - len(cons),
       "promocoes_redundantes_evitadas": [k for k in atual if k not in cons],
       "diverge_do_prototipo": [k for k, v in out.items() if v["s1_conservadora"] != proto[k]["s1_conservadora"]],
       "orcamento_max_tokens": {"baseline": max(v["tokens"][0] for v in out.values()), "s1_atual": max(v["tokens"][1] for v in out.values()), "s1_conservadora": max(v["tokens"][2] for v in out.values())},
       "entregues_4_3_afetadas": [k for k in cons if out[k]["status_4_3"] in ("respondida", "parcial")],
       "grupos_que_mudam": {k: out[k]["grupos"] for k in out if len(set(out[k]["grupos"])) > 1},
       "tokens_alterados": {k: out[k]["tokens"] for k in atual}, "chunks_promovidos": {k: [x["chunk_id"] for x in out[k]["decisoes"] if x["decisao"] == "priorizado"] for k in cons}}
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump({"resumo": res, "por_pergunta": out}, open(AQUI / "fase4b_integracao_comparacao.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
