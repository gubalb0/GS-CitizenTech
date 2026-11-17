"""Diagnostico 4.4 - causas das 56 abstencoes indevidas (somente leitura sobre a rodada 4.3 e a auditoria independente)."""
import csv, json, re, sys
from collections import Counter
sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import evidencias as EV
AUD = r"D:\Downloads\GS\RPA\docs\assistente\auditoria_independente_4_3"
R = {}
for l in open(r"D:\Downloads\GS\RPA\data_assistente\derivados\geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8"):
    o = json.loads(l); R[o["qid"]] = o
rows = list(csv.DictReader(open(AUD + r"\auditoria_independente_150.csv", encoding="utf-8-sig"), delimiter=";"))
def docs_da_just(t):
    ids = set()
    for m in re.finditer(r"\bdocs?\s+((?:\d{1,4}(?:\s*(?:/|,|e|ou)\s*)?)+)", t):
        ids |= {int(x) for x in re.findall(r"\d{1,4}", m.group(1))}
    return ids
out = []
for r in rows:
    if r["classificacao_independente"] != "Abstencao indevida": continue
    q = r["qid"]; o = R[q]; s = o["saida"]; t = s["telemetria"]; v = s["verificacao"]
    ans = docs_da_just(r["justificativa_e_referencias_documentais"])
    enviados = set(); recup = set()
    for f in o["fontes_recuperadas"]:
        recup |= set(f["ids_equivalentes"]) | {f["doc_id"]}
        if f["enviado"]: enviados |= set(f["ids_equivalentes"]) | {f["doc_id"]}
    ident = t.get("identificabilidade", {}) or {}
    pol = v.get("politica"); orig = v.get("status_original")
    probs = v.get("problemas", [])
    rej = any(p.split(":")[0] in ("trecho_nao_literal", "afirmacoes_nao_sustentadas_pela_evidencia", "valores_nao_sustentados", "evidencia_nao_corresponde_a_pergunta") for p in probs)
    pos = "enviado" if ans & enviados else ("recuperado_nao_enviado" if ans & recup else ("sem_doc_identificado" if not ans else "nao_recuperado"))
    out.append({"qid": q, "status": r["status_do_sistema"], "orig": orig, "grupo": o["grupo"], "lista": EV.eh_lista(o["pergunta"]), "singular": EV.eh_singular(o["pergunta"]),
                "docs_resposta(auditor)": sorted(ans), "doc_resposta_no_contexto": pos, "verificador_reprovou": rej, "problemas": probs,
                "ident": ident.get("decisao"), "motivo": ident.get("motivo"), "diverg": t.get("divergencia"), "confianca": r["confianca_do_auditor"], "pergunta": o["pergunta"][:90]})
for x in out: print(x["qid"], x["status"], "orig=" + str(x["orig"]), x["grupo"], "L" if x["lista"] else ("S" if x["singular"] else "?"), x["doc_resposta_no_contexto"], "REJ" if x["verificador_reprovou"] else "-", x["ident"], x["motivo"], x["diverg"], x["confianca"])
print(Counter(x["doc_resposta_no_contexto"] for x in out))
json.dump(out, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\causas_abstencoes_indevidas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
