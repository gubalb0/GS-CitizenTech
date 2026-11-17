"""Consolida os julgamentos manuais da auditoria independente 4.3 em CSV/JSON e calcula as metricas. Somente leitura sobre os dados originais."""
import csv, json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import julgamentos_dadas as D, julgamentos_abst_1 as A1, julgamentos_abst_2 as A2, julgamentos_abst_3 as A3, julgamentos_abst_4 as A4, julgamentos_abst_5 as A5, julgamentos_multi as M

OUT = Path(__file__).resolve().parent.parent
F = json.load(open(OUT / "fatos_por_pergunta.json", encoding="utf-8"))
AB = {}
for m in (A1, A2, A3, A4, A5):
    AB.update(m.J)
rows = []
for f in F:
    q = f["qid"]
    if q in D.J:
        cl, sem, conf, just = D.J[q]
        # status adequado: respondida so e adequada se Correta e sem afirmacao sem evidencia; parcial e adequada se Correta mas parcial (ou Correta) sem afirmacao sem evidencia
        adequado = (cl in ("Correta", "Correta, mas parcial")) and not sem
        tipo = "resposta dada"
    else:
        cl, adeq, conf, just = AB[q]
        sem = False
        adequado = adeq if cl != "Abstencao indevida" else False
        tipo = "abstencao"
    nev = len(f["evidencias"]); nlit = sum(1 for e in f["evidencias"] if e["literal_no_doc_citado"])
    rows.append({"qid": q, "grupo_benchmark": f["grupo"], "multi": f["multi"], "nao_univoca": f["nao_univoca"], "pergunta": f["pergunta"],
                 "status_do_sistema": f["status"], "tipo": tipo, "classificacao_independente": cl, "status_do_sistema_adequado": adequado,
                 "afirmacao_sem_evidencia": sem, "confianca_do_auditor": conf,
                 "n_concorrentes_apontados_pelo_sistema": len(f["concorrentes_sistema"]),
                 "citacoes_literais/total": f"{nlit}/{nev}" if nev else "", "docs_citados": " ".join(map(str, f["docs_citados"])),
                 "justificativa_e_referencias_documentais": just})
with (OUT / "auditoria_independente_150.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=";"); w.writeheader(); w.writerows(rows)

# ---- MULTI
auto = {r["qid"]: r for r in csv.DictReader(open(OUT.parent / "auditoria_multi_dataset.csv", encoding="utf-8-sig"), delimiter=";")}
mrows = []
for q, (cl, dec, resp, irr, conf_, confa, just) in M.J.items():
    a = auto[q]
    mrows.append({"qid": q, "pergunta": a["pergunta"], "n_publicacoes_associadas_dataset": a["n_publicacoes_associadas"], "classificacao_automatica_anterior": a["classificacao"],
                  "classificacao_independente": cl, "decisao": dec, "docs_que_realmente_respondem": resp, "docs_associados_irrelevantes": irr,
                  "conflito_entre_publicacoes_independentes": conf_, "confianca": confa, "justificativa": just})
with (OUT / "auditoria_independente_21_multi.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(mrows[0]), delimiter=";"); w.writeheader(); w.writerows(mrows)

# ---- metricas
def met(rs):
    c = Counter(r["classificacao_independente"] for r in rs)
    dadas = [r for r in rs if r["tipo"] == "resposta dada"]
    ab = [r for r in rs if r["tipo"] == "abstencao"]
    resp = [r for r in rs if r["status_do_sistema"] == "respondida"]
    par = [r for r in rs if r["status_do_sistema"] == "parcial"]
    ok = lambda r: r["classificacao_independente"] in ("Correta", "Correta, mas parcial")
    okstrict = lambda r: r["classificacao_independente"] == "Correta"
    ab_ok = [r for r in ab if r["classificacao_independente"] in ("Ambigua de fato", "Abstencao correta")]
    return {"n": len(rs), "respostas_dadas": len(dadas), "corretas": c["Correta"], "corretas_mas_parciais": c["Correta, mas parcial"], "incorretas": c["Incorreta"],
            "respostas_com_afirmacao_sem_evidencia": sum(r["afirmacao_sem_evidencia"] for r in dadas),
            "abstencoes": len(ab), "ambiguas_de_fato": c["Ambigua de fato"], "abstencoes_corretas": c["Abstencao correta"], "abstencoes_indevidas": c["Abstencao indevida"],
            "precisao_respostas_completas(status=respondida)_estrita": (f"{sum(okstrict(r) and not r['afirmacao_sem_evidencia'] for r in resp)}/{len(resp)}" if resp else "-"),
            "precisao_respostas_completas_flexivel(correta ou parcial correta)": (f"{sum(ok(r) for r in resp)}/{len(resp)}" if resp else "-"),
            "precisao_respostas_parciais(status=parcial)_corretas_ou_parciais": (f"{sum(ok(r) for r in par)}/{len(par)}" if par else "-"),
            "taxa_de_abstencao_adequada(ambigua+abst.correta / abstencoes)": (f"{len(ab_ok)}/{len(ab)} = {100*len(ab_ok)/len(ab):.1f}%" if ab else "-"),
            "classificacoes_inadequadas": sum(not r["status_do_sistema_adequado"] for r in rs)}
G = lambda f: [r for r in rows if f(r)]
conc = lambda r: r["classificacao_independente"] == "Ambigua de fato" or r["n_concorrentes_apontados_pelo_sistema"] > 0
res = {"geral(150)": met(rows), "grupoA_fonte_correta_enviada": met(G(lambda r: r["grupo_benchmark"] == "A")), "grupoB_fonte_correta_nao_enviada": met(G(lambda r: r["grupo_benchmark"] == "B")),
       "MULTI(dataset)": met(G(lambda r: r["multi"])), "nao_MULTI": met(G(lambda r: not r["multi"])), "com_publicacoes_concorrentes": met(G(conc)),
       "sensibilidade_so_confianca_alta_ou_media": met(G(lambda r: r["confianca_do_auditor"] in ("alta", "media")))}
res["confianca_do_auditor(contagem)"] = dict(Counter(r["confianca_do_auditor"] for r in rows))
res["multi21"] = dict(Counter((m["classificacao_automatica_anterior"].split(" (")[0], m["classificacao_independente"], m["decisao"].split(" ")[0]) .__repr__() for m in mrows))
res["multi21_decisao"] = dict(Counter(m["decisao"].split(" ")[0] for m in mrows))
res["multi21_classe_independente"] = dict(Counter(m["classificacao_independente"] for m in mrows))
(OUT / "metricas.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=1))
