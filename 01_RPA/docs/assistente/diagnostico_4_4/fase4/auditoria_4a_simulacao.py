"""Auditoria de encerramento da 4A - SIMULACAO OFFLINE (somente leitura) de politicas mais conservadoras sobre relacoes `nao_verificavel`. Nao altera o pipeline."""
import csv, json, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\scripts")
from replay_verificador import replay
from collections import Counter, defaultdict
novo = replay()
rot = {r["qid"]: r["classificacao_independente"] for r in csv.DictReader(open(r"D:\Downloads\GS\RPA\docs\assistente\auditoria_independente_4_3\auditoria_independente_150.csv", encoding="utf-8-sig"), delimiter=";")}
EXTRA = {"val-031": "Correta, mas parcial", "val-032": "Correta, mas parcial", "val-044": "Parcialmente sustentada", "val-047": "Parcialmente sustentada"}   # auditoria complementar da Fase 3
def rotulo(k): return rot[k] if rot[k] in ("Correta", "Correta, mas parcial", "Incorreta") and k not in EXTRA and novo[k]["status"] in ("respondida", "parcial") and k in rot and rot[k] != "Abstencao indevida" else EXTRA.get(k, rot[k])
ent = {k: v for k, v in novo.items() if v["status"] in ("respondida", "parcial")}
linhas = []
for k, v in ent.items():
    rels = (v["verificacao"].get("evidencia") or {}).get("protecao", {}).get("relacoes", [])
    nv = [r for r in rels if r["estado_associacao"] == "nao_verificavel"]
    nec = [r for r in rels if r["necessaria"]]
    nv_nec = [r for r in nec if r["estado_associacao"] == "nao_verificavel"]
    conf_nec = [r for r in nec if r["estado_associacao"] == "confirmada"]
    unid = lambda rs: {(r["fonte"]) for r in rs}
    linhas.append({"qid": k, "status": v["status"], "rotulo": rotulo(k), "n_rel": len(rels), "n_nv": len(nv), "unid_nv": len(unid(nv)), "n_nec": len(nec), "unid_nec": len(unid(nec)), "n_nv_nec": len(nv_nec), "unid_nv_nec": len(unid(nv_nec)), "n_conf_nec": len(conf_nec),
                   "P_qualquer_nv": bool(nv), "P_nv_necessaria": bool(nv_nec), "P_nenhuma_necessaria_confirmada": bool(nec) and not conf_nec, "P_todas_necessarias_nv": bool(nec) and len(nv_nec) == len(nec)})
json.dump(linhas, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase4\auditoria_4a_simulacao.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("entregues:", len(ent), Counter(l["rotulo"] for l in linhas))
for pol in ("P_qualquer_nv", "P_nv_necessaria", "P_nenhuma_necessaria_confirmada", "P_todas_necessarias_nv"):
    af = [l for l in linhas if l[pol]]
    print(pol, "afetadas:", len(af), dict(Counter(l["rotulo"] for l in af)), "| qids bons afetados:", [l["qid"] for l in af if l["rotulo"] in ("Correta", "Correta, mas parcial")][:30], "| incorretas:", [l["qid"] for l in af if l["rotulo"] == "Incorreta"])
print("sem relacoes:", [l["qid"] for l in linhas if l["n_rel"] == 0])
for l in linhas:
    if l["rotulo"] == "Incorreta" or l["qid"] in ("val-044", "val-047", "val-031", "val-032"): print(l["qid"], l["rotulo"], {k: l[k] for k in ("n_rel", "n_nv", "n_nec", "n_nv_nec", "n_conf_nec")})
