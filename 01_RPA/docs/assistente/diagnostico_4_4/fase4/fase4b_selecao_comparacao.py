"""Fase 4B (preparacao) - comparacao OFFLINE da selecao de contexto: 4.4.4a (flag desligada) x S1 forte (flag ligada). Sem LLM, sem alterar retriever/orcamento."""
import json
import sys

sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import avaliacao_e2e as AE
from citizentech.assistente import grupos as GR
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto
from citizentech.assistente.retriever import Indice

corpus, val, assoc, dup, esp, docs = AE.preparar()
idx = Indice.carregar(AE.IDX)
cfg0, cfg1 = ConfigGeracao(), ConfigGeracao(priorizar_atributo=True)
orig = {json.loads(l)["qid"]: json.loads(l) for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8")}
out, mudaram = {}, []
for q, e in zip(val, esp):
    k = q["qid"]
    res = idx.buscar(q["pergunta"], k=cfg0.max_chunks, modo="bm25")
    c0, c1 = montar_contexto(q["pergunta"], res, cfg0), montar_contexto(q["pergunta"], res, cfg1)
    ids0, ids1 = [i.chunk_id for i in c0.itens], [i.chunk_id for i in c1.itens]
    ordem_rel = [x for x in ids1 if x in set(ids0)] == [x for x in ids0 if x in set(ids1)]
    g0, g1 = GR.grupo_ab(e, c0.itens)[0], GR.grupo_ab(e, c1.itens)[0]
    st = orig[k]["saida"]["status"]
    out[k] = {"mudou": ids0 != ids1, "conjunto_mudou": set(ids0) != set(ids1), "ids0": ids0, "ids1": ids1, "tokens0": c0.tokens_estimados, "tokens1": c1.tokens_estimados,
              "dentro_do_orcamento": c1.tokens_estimados <= cfg1.orcamento_tokens, "ordem_relativa_preservada": ordem_rel, "grupo0": g0, "grupo1": g1, "status_4_3": st,
              "entregue_4_3": st in ("respondida", "parcial"), "log": [x for x in c1.selecao if x["decisao"] not in ("mantido",) or x.get("rotulo_forte")]}
    if ids0 != ids1:
        mudaram.append(k)
res = {"total": len(out), "contextos_alterados": mudaram, "n_alterados": len(mudaram),
       "alterados_com_resposta_entregue_na_4_3": [k for k in mudaram if out[k]["entregue_4_3"]],
       "inalterados": len(out) - len(mudaram), "estouro_orcamento": [k for k, v in out.items() if not v["dentro_do_orcamento"]],
       "grupo_muda": [(k, out[k]["grupo0"], out[k]["grupo1"]) for k in mudaram if out[k]["grupo0"] != out[k]["grupo1"]],
       "ordem_relativa_violada": [k for k in mudaram if not out[k]["ordem_relativa_preservada"]],
       "tokens_alterados": {k: (out[k]["tokens0"], out[k]["tokens1"]) for k in mudaram}}
print(json.dumps(res, ensure_ascii=False, indent=1))
for k in ("val-087", "val-130"):
    print(k, json.dumps(out[k], ensure_ascii=False, indent=1))
json.dump({"resumo": res, "por_pergunta": out}, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase4\fase4b_selecao_comparacao.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
