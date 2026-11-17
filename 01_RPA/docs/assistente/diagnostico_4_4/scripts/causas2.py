import json, csv
from collections import Counter, defaultdict
C = json.load(open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\causas_abstencoes_indevidas.json", encoding="utf-8"))
REP = json.load(open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\replay_contexto.json"))
FP_VERIF = {"val-031", "val-032", "val-045", "val-047", "val-087", "val-097", "val-106", "val-141"}      # verificador rejeitou evidencia valida (diagnostico manual, secao 3)
GER_BLOQ = {"val-062", "val-108", "val-126"}                                                                   # bloqueio legitimo: citacao fabricada/ilegivel/emendada
POLITICA = {"val-009", "val-054", "val-095", "val-135"}                                                         # status convertido em 'ambigua' por regra 4.1-4.3 com respostas equivalentes/duplicadas
rows = []
for x in C:
    q = x["qid"]; pos = x["doc_resposta_no_contexto"]
    if q == "val-097": pos = "enviado"                      # o replay mostra que o chunk citado foi enviado (a flag 'enviado' da rodada assumia prefixo)
    if q in FP_VERIF: c = "3. Verificador rejeitando evidencia valida"
    elif q in GER_BLOQ: c = "5. Geracao incapaz (citacao fabricada/ilegivel/emendada; bloqueio legitimo)"
    elif q in POLITICA: c = "2. Filtro/politica de identificabilidade excessivo (respostas equivalentes)"
    elif pos == "nao_recuperado": c = "1. Recuperacao inadequada (doc da resposta nao recuperado)"
    elif pos == "recuperado_nao_enviado": c = "6. Falta de contexto (recuperado, nao enviado)"
    elif pos == "sem_doc_identificado": c = "7. Pergunta aberta sem documento unico (resposta parcial exigida)"
    elif x["verificador_reprovou"]: c = "5. Geracao incapaz (afirmacoes sem apoio; bloqueio legitimo)"
    else: c = "5. Geracao/modelo se absteve (doc no contexto, sem reprovacao)"
    sec = []
    if x["status"] == "fora_do_escopo": sec.append("4. fora_do_escopo indevido")
    if x["lista"]: sec.append("pergunta aberta/lista")
    rows.append({"qid": q, "status": x["status"], "causa_primaria": c, "causas_secundarias": "; ".join(sec), "doc_no_contexto": pos, "grupo_rodada": x["grupo"], "confianca_auditor": x["confianca"]})
cnt = Counter(r["causa_primaria"] for r in rows)
for k, v in sorted(cnt.items()): print(v, k, [r["qid"] for r in rows if r["causa_primaria"] == k])
print("fora_do_escopo (secundaria):", sum("4." in r["causas_secundarias"] for r in rows), "| lista:", sum("lista" in r["causas_secundarias"] for r in rows), "| total", len(rows))
with open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\causas_56_abstencoes_indevidas.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=";"); w.writeheader(); w.writerows(rows)
