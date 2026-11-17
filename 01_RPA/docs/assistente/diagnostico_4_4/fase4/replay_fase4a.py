"""Replay offline (sem LLM) da Fase 4A x comportamento da Fase 3 (baseline gravado antes das alteracoes: replay_baseline_fase3_comportamento.json)."""
import json, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\scripts")
from replay_verificador import replay
B = json.load(open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase4\replay_baseline_fase3_comportamento.json", encoding="utf-8"))
def comparar(mostrar=True):
    novo = replay(); dif = {}
    for k, v in novo.items():
        b = B[k]
        if v["status"] != b["status"] or v["resposta"] != b["resposta"]:
            dif[k] = {"fase3": b["status"], "fase4a": v["status"], "problemas": v["problemas"], "texto_fase3": b["resposta"], "texto_fase4a": v["resposta"]}
    if mostrar:
        print(len(novo), "casos; diferencas Fase 4A x Fase 3:", len(dif))
        for k, d in dif.items(): print(" ", k, d["fase3"], "->", d["fase4a"], d["problemas"])
    return novo, dif
if __name__ == "__main__": comparar()
