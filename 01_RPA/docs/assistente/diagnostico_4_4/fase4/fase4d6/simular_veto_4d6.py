"""Fase 4D.6 - SIMULACAO ISOLADA de politicas de veto sobre os resultados da 4D.5 (somente leitura). Versao UNICA deste script (sem reajustes apos ver resultados).
Entradas: ../fase4d5/resultados_4d5_detalhe.json, CASOS_SINTETICOS_4D5.json, ESPECIFICACAO_REAIS_4D5.json (rotulos 4D.5 NAO alterados), corpus (leitura).
Nao altera producao nem o prototipo 4D.5 (importado so para reutilizar funcoes puras)."""
import ast
import csv
import inspect
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

RAIZ = pathlib.Path(r"D:\Downloads\GS\RPA")
sys.path.insert(0, str(RAIZ))
AQUI = pathlib.Path(__file__).parent
D5 = AQUI.parent / "fase4d5"
sys.path.insert(0, str(D5))
import prototipo_vinculo_4d5 as P  # noqa: E402

from citizentech.assistente import avaliacao_e2e as AE  # noqa: E402
from citizentech.assistente import evidencias as EV  # noqa: E402

F = P.F
L = json.loads((D5 / "resultados_4d5_detalhe.json").read_text(encoding="utf-8"))
SINT = {c["id"]: c for c in json.loads((D5 / "CASOS_SINTETICOS_4D5.json").read_text(encoding="utf-8"))["casos"]}
REAIS = json.loads((D5 / "ESPECIFICACAO_REAIS_4D5.json").read_text(encoding="utf-8"))
corpus, *_ = AE.preparar()
DOCS = {d["id"]: d["texto_completo"] for d in corpus}
NIV = ["N1", "N2", "N3", "N4"]
GRUPO = {"sustentado": "pos", "nao_sustentado_outra_entidade": "neg_outra", "nao_sustentado_outro_atributo": "neg_outra", "nao_sustentado_herdado": "neg_herdado",
         "sustentado_documental": "doc", "ambiguo": "amb", "nao_verificavel": "nv"}


def contexto_do_alvo(x):
    """(publicacao, entidade, outras, termos, unidades_citadas) para procurar relacao explicita em OUTRAS unidades da publicacao."""
    if x["origem"] == "sintetico":
        c = SINT[x["id"]]
        pid = c["citacoes"][0]["pub"]
        pub = P.Publicacao(pid, " ".join(c["publicacoes"][pid]), {})
        m = re.search(r"termos=(\[[^\]]*\])", x["nota"])
        return pub, c["entidade"], [F(o) for o in c["outras_entidades"]], (ast.literal_eval(m.group(1)) if m else []), x["unidades_citadas"]
    sp = REAIS[x["id"]]
    if x["id"] == "val-083":
        doc = int(re.search(r"doc (\d+)", x["alvo"]).group(1))
        item = re.search(r"item (.+?) \(doc", x["alvo"]).group(1)
        termos = [t for t in EV.tokens_de_uso(item) if len(t) > 2]
        ent = sp["entidades"][0]
    else:
        doc = sp["doc"]
        ent = next(e for e in sp["entidades"] if e["nome"] == x["alvo"])
        termos = ast.literal_eval(re.search(r"termos=(\[[^\]]*\])", x["nota"]).group(1))
    return P.Publicacao(str(doc), DOCS[doc], {}), ent, [F(o) for o in sp["outras_entidades"]], termos, x["unidades_citadas"]


def documental_explicita(x):
    pub, ent, outras, termos, cit = contexto_do_alvo(x)[:5]
    if not termos:
        return []
    import math
    thr = max(1, math.ceil(0.4 * len(termos)))
    achados = []
    for u in pub.un:
        if u["i"] in cit:
            continue
        ments = P._mencoes(u, ent["formas"], ent.get("tipo"))
        if not ments or len(P._termos_na_unidade(u, termos)) < thr:
            continue
        rel, _ = P._relacao(u, ments, P._termos_na_unidade(u, termos), outras, ent["formas"])
        if rel == "explicita":
            achados.append(u["i"])
    return achados


def derivar(x):
    n = x["estados"]
    d = x["detalhes"] or {}
    n1d = d.get("N1", []) if isinstance(d, dict) else []
    contra_a = n["N1"] in ("outra_entidade", "outro_atributo")
    contra_b = any(t[1] == "sem_mencao" and re.search(r"\['", t[2]) for t in n1d)
    papeis3 = [t[1] for t in d.get("N3", [])] if isinstance(d, dict) else []
    papeis4 = [t[1] for t in d.get("N4", [])] if isinstance(d, dict) else []
    contra_c = {"N3": bool(papeis3) and all(p != "direta" for p in papeis3), "N4": bool(papeis4) and all(p != "direta" for p in papeis4)}
    broad = {"N3": x["aceita"]["N3"], "N4": x["aceita"]["N4"]}
    doc_expl = documental_explicita(x) if (broad["N4"] and n["N1"] != "explicita") else []
    sujeito = n["N4"] == "sujeito_da_publicacao"
    if n["N1"] == "sem_conteudo":
        cat = "nao_verificavel"
    elif contra_a or contra_b:
        cat = "conflitante"
    elif n["N1"] == "explicita":
        cat = "citada"
    elif n["N2"] == "adjacente_com_vinculo":
        cat = "complementar"
    elif n["N1"] == "coocorrencia" or n["N2"] == "adjacente_sem_vinculo":
        cat = "nao_relacionada"
    elif doc_expl or sujeito:
        cat = "documental"
    elif broad["N3"] or broad["N4"]:
        cat = "nao_verificavel"
    else:
        cat = "sem_vinculo_amplo"
    return {"cat": cat, "contra_a": contra_a, "contra_b": contra_b, "contra_c": contra_c, "doc_expl": doc_expl, "sujeito": sujeito}


def politica(nome, x, f, base):
    """Decisao ACEITA | REJEITA | ENCAMINHA para o vinculo da entidade na afirmacao."""
    broad = x["aceita"][base]
    n = x["estados"]
    if nome == "V0":
        return "ACEITA" if broad else "REJEITA"
    if nome == "V1":
        return "REJEITA" if (broad and (f["contra_a"] or f["contra_b"] or f["contra_c"][base])) else ("ACEITA" if broad else "REJEITA")
    if nome == "V2":
        return "ACEITA" if (broad and (n["N1"] == "explicita" or n["N2"] == "adjacente_com_vinculo")) else "REJEITA"
    if nome == "V3":
        if not broad:
            return "REJEITA"
        if f["contra_a"] or f["contra_b"]:
            return "REJEITA"
        if f["cat"] in ("citada", "complementar"):
            return "ACEITA"
        if f["cat"] == "documental":
            return "ENCAMINHA"
        return "ACEITA"
    raise ValueError(nome)


def metricas(linhas):
    m = defaultdict(Counter)
    for r in linhas:
        m[r["grupo"]][r["decisao"]] += 1
    g = lambda grp, d: m[grp][d]  # noqa: E731
    neg = ("neg_outra", "neg_herdado")
    return {
        "falsos_vinculos_aceitos": sum(g(k, "ACEITA") for k in neg),
        "negativos_encaminhados(nao_aceitos)": sum(g(k, "ENCAMINHA") for k in neg),
        "negativos_rejeitados": sum(g(k, "REJEITA") for k in neg),
        "legitimas_aceitas": g("pos", "ACEITA"), "legitimas_encaminhadas": g("pos", "ENCAMINHA"), "legitimas_rejeitadas": g("pos", "REJEITA"),
        "documentais_preservadas(aceita+encaminha)": g("doc", "ACEITA") + g("doc", "ENCAMINHA"), "documentais_rejeitadas": g("doc", "REJEITA"),
        "conflitantes_rejeitadas": f"{g('neg_outra', 'REJEITA')}/{sum(m['neg_outra'].values())}",
        "ambiguos(aceita/encaminha/rejeita)": f"{g('amb', 'ACEITA')}/{g('amb', 'ENCAMINHA')}/{g('amb', 'REJEITA')}",
        "nao_verificaveis(aceita/encaminha/rejeita)": f"{g('nv', 'ACEITA')}/{g('nv', 'ENCAMINHA')}/{g('nv', 'REJEITA')}",
    }


alvos = []
for x in L:
    f = derivar(x)
    alvos.append((x, f))
linhas = []
for x, f in alvos:
    for base in ("N3", "N4"):
        for pol in ("V0", "V1", "V2", "V3"):
            linhas.append({"conjunto": x["origem"], "id": x["id"], "alvo": x["alvo"], "esperado": x["esperado"], "grupo": GRUPO[x["esperado"]], "categoria": f["cat"], "base": base, "politica": pol,
                           "decisao": politica(pol, x, f, base), "N1": x["estados"]["N1"], "N2": x["estados"]["N2"], "N3": x["estados"]["N3"], "N4": x["estados"]["N4"],
                           "contra(a,b,c)": f"{int(f['contra_a'])},{int(f['contra_b'])},{int(f['contra_c'][base])}", "doc_explicita_em": f["doc_expl"]})
with open(AQUI / "RESULTADOS_VETO_4D6.csv", "w", newline="", encoding="utf-8-sig") as fh:
    cols = ["conjunto", "id", "alvo", "esperado", "categoria", "base", "politica", "decisao", "N1", "N2", "N3", "N4", "contra(a,b,c)", "doc_explicita_em"]
    w = csv.writer(fh, delimiter=";")
    w.writerow(cols)
    for r in linhas:
        w.writerow([r[c] for c in cols])
resumo = {}
rows_r = []
for conj in ("sintetico", "real"):
    for base in ("N3", "N4"):
        for pol in ("V0", "V1", "V2", "V3"):
            sel = [r for r in linhas if r["conjunto"] == conj and r["base"] == base and r["politica"] == pol]
            met = metricas(sel)
            resumo[f"{conj}|{base}|{pol}"] = met
            rows_r.append([conj, base, pol, len(sel)] + list(met.values()))
with open(AQUI / "RESUMO_VETO_4D6.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["conjunto", "base", "politica", "n_alvos"] + list(metricas([]).keys()))
    w.writerows(rows_r)

# ------------- sensibilidade
sens = {}
# (a) ablacao dos componentes de contradicao do V1 (base N4 e N3)
for conj in ("sintetico", "real"):
    for base in ("N3", "N4"):
        for nome, fn in (("a", lambda f, b: f["contra_a"]), ("a+b", lambda f, b: f["contra_a"] or f["contra_b"]), ("a+b+c", lambda f, b: f["contra_a"] or f["contra_b"] or f["contra_c"][b]), ("c_so", lambda f, b: f["contra_c"][b])):
            sel = [(x, f) for x, f in alvos if x["origem"] == conj]
            rows = [{"grupo": GRUPO[x["esperado"]], "decisao": ("REJEITA" if (x["aceita"][base] and fn(f, base)) else ("ACEITA" if x["aceita"][base] else "REJEITA"))} for x, f in sel]
            sens[f"ablacao V1[{nome}]|{conj}|{base}"] = {k: v for k, v in metricas(rows).items() if k in ("falsos_vinculos_aceitos", "legitimas_rejeitadas", "documentais_rejeitadas", "conflitantes_rejeitadas")}
# (b) N2 sem anafora / sem adjacencia (efeito na aceitacao via N2)
def n2_motivo(x):
    d = (x["detalhes"] or {}).get("N2", []) if isinstance(x["detalhes"], dict) else []
    return [t[1] for t in d]
for conj in ("sintetico", "real"):
    sel = [x for x, f in alvos if x["origem"] == conj]
    aceitos_n1 = [x["id"] for x in sel if x["aceita"]["N1"]]
    n2_total = [x["id"] for x in sel if x["aceita"]["N2"] and not x["aceita"]["N1"]]
    n2_anafora = [x["id"] for x in sel if x["aceita"]["N2"] and not x["aceita"]["N1"] and any("anafora" in m for m in n2_motivo(x))]
    n2_intro = [x["id"] for x in sel if x["aceita"]["N2"] and not x["aceita"]["N1"] and any("introduz" in m for m in n2_motivo(x))]
    sens[f"N2|{conj}"] = {"aceitos_so_por_N2": n2_total, "por_anafora": n2_anafora, "por_introducao_com_dois_pontos": n2_intro,
                          "perdidos_sem_anafora": [i for i in n2_total if i not in n2_intro], "perdidos_sem_adjacencia(N1 apenas)": n2_total}
# (c) aceitar relacoes documentais (V3 com documental ACEITA)
for conj in ("sintetico", "real"):
    for base in ("N4",):
        rows = []
        for x, f in alvos:
            if x["origem"] != conj:
                continue
            d = politica("V3", x, f, base)
            rows.append({"grupo": GRUPO[x["esperado"]], "decisao": "ACEITA" if d == "ENCAMINHA" else d})
        sens[f"V3 com documental aceito|{conj}|{base}"] = {k: v for k, v in metricas(rows).items() if k in ("falsos_vinculos_aceitos", "legitimas_rejeitadas", "documentais_preservadas(aceita+encaminha)")}
# (d) risco de confundir registros vizinhos: aceitacoes N1/N2 em alvo esperado negativo (deve ser 0) e N2 aceitos com outra entidade na unidade
sens["registros_vizinhos"] = {c: [x["id"] + ":" + x["alvo"][:20] for x, f in alvos if x["origem"] == c and x["aceita"]["N2"] and GRUPO[x["esperado"]].startswith("neg")] for c in ("sintetico", "real")}
sens["adjacente_sem_vinculo_(proximidade)"] = {c: [x["id"] for x, f in alvos if x["origem"] == c and x["estados"]["N2"] == "adjacente_sem_vinculo"] for c in ("sintetico", "real")}
# (e) risco de bloquear respostas corretas que repetem nomes da pergunta: positivos e documentais rejeitados por politica
risco = {}
for r in linhas:
    if r["grupo"] in ("pos", "doc") and r["decisao"] == "REJEITA":
        risco.setdefault(f"{r['conjunto']}|{r['base']}|{r['politica']}", []).append(f"{r['id']}({r['grupo']})")
sens["positivos_ou_documentais_rejeitados"] = risco
# (f) diagnostico val-083 VITAMINA D: causa real da coocorrencia (SEM corrigir o prototipo; copia local da funcao com a regex pretendida)
src = inspect.getsource(P._relacao)
linha_quebrada = [ln for ln in src.splitlines() if "ponto de abreviatura" in ln][0]
bytes_linha = linha_quebrada.encode("unicode_escape").decode()
src_ok = src.replace(linha_quebrada, "    entre = re.sub(r\"\\b(\\w{1,3})\\.\", r\"\\1\", entre)   # intencao: ponto de abreviatura nao e fronteira")
ns = dict(P.__dict__)
exec(src_ok, ns)
u = DOCS[495]
seg = P.segmentar(u)
uv = u[seg[33][0]:seg[33][1]]
unid = {"txt": uv, "f": F(uv), "i": 33, "chunks": []}
ments = P._mencoes(unid, ["atencao primaria"], "organizacao")
termos_v = [t for t in EV.tokens_de_uso("VITAMINA D") if len(t) > 2]
diag = {"unidade": uv, "termos_do_item": termos_v, "ocorrencias_do_termo": [m.start() for m in re.finditer(r"vitami", unid["f"])], "ocorrencias_de_400": [m.start() for m in re.finditer(r"400", unid["f"])],
        "relacao_com_prototipo_4D5_como_esta": P._relacao(unid, ments, P._termos_na_unidade(unid, termos_v), [], ["atencao primaria"]),
        "relacao_com_regex_de_abreviatura_pretendida(copia local, diagnostico)": ns["_relacao"](unid, ments, P._termos_na_unidade(unid, termos_v), [], ["atencao primaria"]),
        "linha_122_no_arquivo_4D5(unicode_escape)": bytes_linha}
sens["diagnostico_val083_vitamina"] = diag
(AQUI / "resultados_veto_4d6_detalhe.json").write_text(json.dumps({"alvos": [{"id": x["id"], "conjunto": x["origem"], "alvo": x["alvo"], "esperado": x["esperado"], "derivado": {k: v for k, v in f.items()}} for x, f in alvos],
                                                                  "resumo": resumo, "sensibilidade": sens}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
# ------------- saida resumida
print("categorias derivadas:", Counter((x["origem"], f["cat"]) for x, f in alvos))
for conj in ("sintetico", "real"):
    print("=====", conj)
    for base in ("N3", "N4"):
        for pol in ("V0", "V1", "V2", "V3"):
            print(base, pol, json.dumps(resumo[f"{conj}|{base}|{pol}"], ensure_ascii=False))
print(json.dumps(sens, ensure_ascii=False, indent=1, default=str)[:6000])
for x, f in alvos:
    print(x["origem"][:3], x["id"], x["alvo"][:26], "|", x["esperado"], "|", f["cat"], "|", f["contra_a"], f["contra_b"], f["contra_c"], f["doc_expl"], f["sujeito"])
