"""Replay offline (sem LLM): Fase 3 x linha de base da Fase 2 (mesmo codigo com PROTECOES_44 vazio = comportamento da Fase 2, validado contra a rodada 4.3
+ os 10 casos liberados na Fase 2)."""
import json, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\scripts")
from replay_verificador import replay, AE
from citizentech.assistente import geracao as G
BASE2_STATUS = {"val-031": "parcial", "val-032": "parcial", "val-044": "parcial", "val-047": "parcial", "val-083": "parcial", "val-087": "parcial", "val-141": "parcial",
                "val-045": "ambigua", "val-097": "ambigua", "val-106": "ambigua"}
def comparar(qids=None, mostrar=True):
    ativo = set(G.PROTECOES_44)
    G.PROTECOES_44.clear()
    base = replay(qids=qids)
    G.PROTECOES_44.update(ativo)
    novo = replay(qids=qids)
    orig = {}
    for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8"):
        o = json.loads(l); orig[o["qid"]] = o["saida"]
    # valida a linha de base (Fase 2) contra a rodada 4.3
    for k, v in base.items():
        esperado = BASE2_STATUS.get(k, orig[k]["status"])
        assert v["status"] == esperado, (k, v["status"], esperado)
        if k not in BASE2_STATUS and orig[k]["status"] in ("respondida", "parcial"):
            assert v["resposta"] == orig[k]["resposta"], k
    dif = {}
    for k, v in novo.items():
        b = base[k]
        if v["status"] != b["status"] or v["resposta"] != b["resposta"]:
            dif[k] = {"fase2": b["status"], "fase3": v["status"], "problemas": v["problemas"], "texto_mudou": v["resposta"] != b["resposta"], "texto_fase2": b["resposta"][:260], "texto_fase3": v["resposta"][:420]}
    if mostrar:
        print(len(novo), "casos; diferencas Fase 3 vs Fase 2:", len(dif))
        for k, d in dif.items(): print(" ", k, d["fase2"], "->", d["fase3"], d["problemas"], "| texto_mudou" if d["texto_mudou"] else "")
    return novo, base, dif
if __name__ == "__main__":
    comparar()
