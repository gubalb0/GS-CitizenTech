"""Fase 4B - simulacao OFFLINE: baseline 4A x S1 atual x S1 conservadora (prototipo). Sem modelo."""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\Downloads\GS\RPA")
sys.path.insert(0, str(Path(__file__).parent))
from s1_conservadora_proto import montar_contexto_conservador

from citizentech.assistente import avaliacao_e2e as AE
from citizentech.assistente import evidencias as EV
from citizentech.assistente import grupos as GR
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto
from citizentech.assistente.retriever import Indice

corpus, val, assoc, dup, esp, docs = AE.preparar()
idx = Indice.carregar(AE.IDX)
off, on = ConfigGeracao(), ConfigGeracao(priorizar_atributo=True)
orig = {json.loads(l)["qid"]: json.loads(l) for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8")}
out = {}
for q, e in zip(val, esp):
    k, P = q["qid"], q["pergunta"]
    res = idx.buscar(P, k=5, modo="bm25")
    c0, c1 = montar_contexto(P, res, off), montar_contexto(P, res, on)
    c2, info = montar_contexto_conservador(P, res, off, on)
    f = lambda c: [i.chunk_id for i in c.itens]
    out[k] = {"pergunta": P, "baseline": f(c0), "s1_atual": f(c1), "s1_conservadora": f(c2), "tokens": [c0.tokens_estimados, c1.tokens_estimados, c2.tokens_estimados],
              "grupos": [GR.grupo_ab(e, c.itens)[0] for c in (c0, c1, c2)], "info": info, "status_4_3": orig[k]["saida"]["status"]}
atual = [k for k, v in out.items() if v["baseline"] != v["s1_atual"]]
cons = [k for k, v in out.items() if v["baseline"] != v["s1_conservadora"]]
res = {"s1_atual_altera": atual, "s1_conservadora_altera": cons, "promocoes_redundantes_evitadas": [k for k, v in out.items() if v["info"]["decisao"] == "promocao_redundante_evitada"],
       "orcamento_max": {"baseline": max(v["tokens"][0] for v in out.values()), "s1_atual": max(v["tokens"][1] for v in out.values()), "s1_conservadora": max(v["tokens"][2] for v in out.values())},
       "entregues_4_3_afetadas": [k for k in cons if orig[k]["saida"]["status"] in ("respondida", "parcial")],
       "conservadora_difere_do_atual_fora_dos_6": [k for k, v in out.items() if v["s1_atual"] != v["s1_conservadora"] and k not in atual]}
print(json.dumps(res, ensure_ascii=False, indent=1))
for k in atual:
    v = out[k]
    print(k, v["info"]["decisao"], "grupos", v["grupos"], "tokens", v["tokens"], "\n  cobertura selecionados:", {c[5:]: x for c, x in v["info"]["cobertura_selecionados"].items()})
json.dump({"resumo": res, "por_pergunta": out}, open(Path(__file__).with_name("avaliacao_s1_conservadora.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
