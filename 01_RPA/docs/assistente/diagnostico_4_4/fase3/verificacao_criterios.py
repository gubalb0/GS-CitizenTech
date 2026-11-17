"""Verificacao LITERAL dos criterios de conclusao da Fase 3 sobre o replay offline das 150 saidas brutas (sem LLM). Nao adapta criterios: imprime PASS/FAIL."""
import csv, json, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\scripts")
from replay_fase3 import comparar, AE
from citizentech.assistente import evidencias as EV
novo, base, dif = comparar(mostrar=False)
orig = {}
for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8"):
    o = json.loads(l); orig[o["qid"]] = o["saida"]
rot = {r["qid"]: r["classificacao_independente"] for r in csv.DictReader(open(r"D:\Downloads\GS\RPA\docs\assistente\auditoria_independente_4_3\auditoria_independente_150.csv", encoding="utf-8-sig"), delimiter=";")}
ordem = {"insuficiente": 0, "ambigua": 0, "fora_do_escopo": 0, "parcial": 1, "respondida": 2}
R = []
def c(n, desc, ok, det=""):
    R.append({"criterio": n, "descricao": desc, "resultado": "PASS" if ok else "FAIL", "detalhe": det}); print(f"[{'PASS' if ok else 'FAIL'}] {n}. {desc} {det}")
c(1, "val-039, 050, 130, 136, 141 nao sao mais entregues como respondida/parcial", all(novo[k]["status"] == "insuficiente" for k in ("val-039", "val-050", "val-130", "val-136", "val-141")),
  str({k: novo[k]["status"] for k in ("val-039", "val-050", "val-130", "val-136", "val-141")}))
t47 = novo["val-047"]["resposta"]
c(2, "val-047 continua parcial, sem texto exclusivo", novo["val-047"]["status"] == "parcial" and t47.startswith("Entre os itens encontrados") and not EV.exclusividade(t47, "programas"), t47[:120])
c(3, "val-087 deixa de ser parcial com a frase atual", novo["val-087"]["status"] != "parcial", novo["val-087"]["status"])
c(4, "val-044, 031 e 032 permanecem parcial com o mesmo texto da Fase 2", all(novo[k]["status"] == "parcial" and novo[k]["resposta"] == base[k]["resposta"] for k in ("val-044", "val-031", "val-032")))
alvo5 = [k for k, r in rot.items() if r in ("Correta", "Correta, mas parcial") and orig[k]["status"] in ("respondida", "parcial")]
c(5, f"as {len(alvo5)} respostas dadas julgadas Correta/Correta-mas-parcial mantem status e texto da 4.3", all(novo[k]["status"] == orig[k]["status"] and novo[k]["resposta"] == orig[k]["resposta"] for k in alvo5), f"n={len(alvo5)}")
prom = [k for k in novo if ordem[novo[k]["status"]] > ordem[base[k]["status"]]]
c(6, "nenhuma promocao de status em relacao a Fase 2; todas as mudancas sao rebaixamentos ou reescrita de texto de parcial", not prom and all(ordem[novo[k]["status"]] < ordem[base[k]["status"]] or (novo[k]["status"] == base[k]["status"] == "parcial") for k in dif), f"mudancas={sorted(dif)}")
c(7, "val-062, 108 e 126 seguem bloqueados pelos mesmos motivos", all(novo[k]["status"] == "insuficiente" and novo[k]["problemas"] == base[k]["problemas"] for k in ("val-062", "val-108", "val-126")))
abst_mud = [k for k in novo if orig[k]["status"] not in ("respondida", "parcial") and k not in {"val-031", "val-032", "val-044", "val-045", "val-047", "val-083", "val-087", "val-097", "val-106", "val-141"} and (novo[k]["status"] != orig[k]["status"] or novo[k]["resposta"] != orig[k]["resposta"])]
c("extra", "nenhuma abstencao da 4.3 (alem dos 10 casos da Fase 2) mudou", not abst_mud, str(abst_mud))
json.dump({"criterios": R, "mudancas_fase3_vs_fase2": dif}, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase3\verificacao_criterios.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("FALHAS:", [r["criterio"] for r in R if r["resultado"] == "FAIL"])
