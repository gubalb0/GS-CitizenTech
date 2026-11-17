"""Fase 4D.3 - execucao OFFLINE dos casos sinteticos (sem modelo/LM Studio/API) na implementacao atual e em variantes de referencia.
Le CASOS_DIAGNOSTICOS_4D3.json (rotulagem congelada) e NAO altera nenhum modulo: variantes B1/B2 sao monkeypatches EM MEMORIA de EV.termos_de_uso
(restaurados no fim, com asserção); C simplificada e D sao filtros pos-hoc sobre o resultado da baseline (so podem bloquear)."""
import csv
import hashlib
import json
import pathlib
import sys

RAIZ = pathlib.Path(r"D:\Downloads\GS\RPA")
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "citizentech" / "assistente" / "tests"))
from test_fase4a import chunk, o87, rodar  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402

AQUI = pathlib.Path(__file__).parent
cong = json.loads((AQUI / "CONGELAMENTO_ROTULAGEM_4D3.json").read_text(encoding="utf-8"))
for n, h in cong["sha256"].items():
    assert hashlib.sha256((AQUI / n).read_bytes()).hexdigest() == h, f"rotulagem alterada apos o congelamento: {n}"
CASOS = json.loads((AQUI / "CASOS_DIAGNOSTICOS_4D3.json").read_text(encoding="utf-8"))["casos"]
ENTREGUE = ("respondida", "parcial")


def descartados(resp, perg):
    q = set(EV.tokens_de_uso(perg))
    qrad = {EV._radical(w) for w in q if len(w) >= 6 and not w.isdigit()}
    d = {}
    for t in dict.fromkeys(EV.tokens_de_uso(resp)):
        rz = ("funcional" if t in EV.PALAVRAS_FUNCIONAIS else "generica" if t in EV.GENERICAS else "da_pergunta" if t in q
              else "radical_da_pergunta" if len(t) >= 6 and not t.isdigit() and EV._radical(t) in qrad else None)
        if rz:
            d.setdefault(rz, []).append(t)
    return d


def rodar_caso(c):
    chunks = [chunk(k + 1, ch["texto"], ch["doc"], ordem=ch["ordem"], n=ch["n_chunks_doc"]) for k, ch in enumerate(c["chunks"])]
    chave = {ch["chave"]: f"C{k + 1}" for k, ch in enumerate(c["chunks"])}
    spans = [(chave[x["chunk"]], x["span"]) for x in c["citacoes"]]
    obj = o87(c["resposta"], spans, fontes=tuple(sorted({f for f, _ in spans})))
    r = rodar(c["pergunta"], chunks, obj)
    prot = ((r.verificacao or {}).get("evidencia") or {}).get("protecao", {}) if r.verificacao else {}
    rl = [x for x in prot.get("relacoes", []) if x.get("origem") == "citacao"]
    textos = {chave[ch["chave"]]: ch["texto"] for ch in c["chunks"]}
    return r, rl, textos


def variante_termos(modo):
    def f(resposta, pergunta):
        q = set(EV.tokens_de_uso(pergunta))
        nomes = set(EV.termos_salientes(pergunta)["nomes"])
        if modo == "B1":
            q = {t for t in q if t not in nomes}
        elif modo == "B2":
            q = set()
        qrad = {EV._radical(w) for w in q if len(w) >= 6 and not w.isdigit()}
        out = [t for t in EV.tokens_de_uso(resposta) if t and t not in EV.PALAVRAS_FUNCIONAIS and t not in EV.GENERICAS and t not in q
               and not (len(t) >= 6 and not t.isdigit() and EV._radical(t) in qrad)]
        return list(dict.fromkeys(out))
    return f


def executar(c):
    r, rl, textos = rodar_caso(c)
    return {"status": r.status, "entregue": r.status in ENTREGUE, "problemas": (r.verificacao or {}).get("problemas"), "rl": rl, "textos": textos,
            "termos_de_uso": EV.termos_de_uso(c["resposta"], c["pergunta"])}


base = {c["id"]: executar(c) for c in CASOS}
orig_tdu = EV.termos_de_uso
var = {"baseline": {k: {"entregue": v["entregue"], "status": v["status"], "problemas": v["problemas"]} for k, v in base.items()}}
for modo in ("B1", "B2"):
    EV.termos_de_uso = variante_termos(modo)
    try:
        var[modo] = {c["id"]: {k: v for k, v in executar(c).items() if k in ("entregue", "status", "problemas")} for c in CASOS}
    finally:
        EV.termos_de_uso = orig_tdu
assert EV.termos_de_uso is orig_tdu


def filtro_C(c, b):
    """C simplificada: cada nome saliente da PERGUNTA que a RESPOSTA repete precisa constar no chunk de ao menos uma citacao cujo rotulo NAO conflita."""
    if not b["entregue"]:
        return b["entregue"], b["status"], b["problemas"]
    nomes = [n for n in EV.termos_salientes(c["pergunta"])["nomes"] if n in EV._nf(c["resposta"])]
    for n in nomes:
        if not any(n in EV._nf(b["textos"][x["fonte"]]) and x["estado"] != "conflito" for x in b["rl"]):
            return False, "insuficiente", [f"C_simplificada: '{n}' sem vinculo em trecho nao conflitante"]
    return True, b["status"], b["problemas"]


def filtro_D(c, b):
    """D: exige ao menos uma citacao com estado 'compativel' (rotulo da familia certa ou cue explicito); desconhecido NAO basta."""
    if not b["entregue"]:
        return b["entregue"], b["status"], b["problemas"]
    if not any(x["estado"] == "compativel" for x in b["rl"]):
        return False, "insuficiente", ["D: nenhuma citacao com rotulo compativel"]
    return True, b["status"], b["problemas"]


for nome, f in (("C_simplificada", filtro_C), ("D", filtro_D)):
    var[nome] = {}
    for c in CASOS:
        e, s, p = f(c, base[c["id"]])
        var[nome][c["id"]] = {"entregue": e, "status": s, "problemas": p}

# ---------- CSV baseline
campos = ["id", "familia", "classe_ref", "decisao_ideal", "confianca", "status_pipeline", "entregue", "avaliacao_vs_ideal", "problemas", "termos_de_uso", "descartados_por_origem_na_pergunta",
          "citacoes(fonte|rotulo|estado|causas|necessaria|bloqueia|termos_exclusivos)", "etapa_nao_executavel_offline"]


def avalia(ideal, entregue):
    if ideal == "indeterminado":
        return "inconclusivo"
    if ideal == "entregar":
        return "ok" if entregue else "FALSO_BLOQUEIO"
    return "FALSA_LIBERACAO" if entregue else "ok"


with open(AQUI / "RESULTADOS_BASELINE_4D3.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(campos)
    for c in CASOS:
        b = base[c["id"]]
        j = c["julgamento_referencia"]
        cits = " || ".join("|".join(str(x) for x in (y["fonte"], (y["rotulo"] or {}).get("rotulo"), y["estado"], ",".join(y["causas_do_conflito"]), y["necessaria"], y["bloqueia"], ",".join(y["termos_exclusivos"]))) for y in b["rl"])
        w.writerow([c["id"], c["familia"], j["classe"], j["decisao_ideal_do_pipeline"], j["confianca"], b["status"], b["entregue"], avalia(j["decisao_ideal_do_pipeline"], b["entregue"]),
                    json.dumps(b["problemas"], ensure_ascii=False), ",".join(b["termos_de_uso"]), json.dumps(descartados(c["resposta"], c["pergunta"]), ensure_ascii=False), cits,
                    "saida_real_do_modelo (a resposta candidata e fixa/sintetica; nada de geracao, retrieval ou montagem real de contexto)"])

# ---------- CSV variantes
VARS = ["baseline", "B1", "B2", "C_simplificada", "D"]
with open(AQUI / "COMPARACAO_VARIANTES_4D3.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["id", "classe_ref", "decisao_ideal"] + [f"{v}_entregue" for v in VARS] + [f"{v}_vs_ideal" for v in VARS])
    for c in CASOS:
        j = c["julgamento_referencia"]
        w.writerow([c["id"], j["classe"], j["decisao_ideal_do_pipeline"]] + [var[v][c["id"]]["entregue"] for v in VARS] + [avalia(j["decisao_ideal_do_pipeline"], var[v][c["id"]]["entregue"]) for v in VARS])

# ---------- resumo
resumo = {}
for v in VARS:
    r = {"falsos_bloqueios": [], "falsas_liberacoes": [], "corretas_preservadas": 0, "corretas_total": 0, "parciais_bloqueadas": [], "inconclusivos": []}
    for c in CASOS:
        j = c["julgamento_referencia"]
        e = var[v][c["id"]]["entregue"]
        a = avalia(j["decisao_ideal_do_pipeline"], e)
        if a == "FALSO_BLOQUEIO":
            r["falsos_bloqueios"].append(c["id"])
        if a == "FALSA_LIBERACAO":
            r["falsas_liberacoes"].append(c["id"])
        if a == "inconclusivo":
            r["inconclusivos"].append(f"{c['id']}={'entregue' if e else 'bloqueado'}")
        if j["classe"] == "correta" and j["decisao_ideal_do_pipeline"] == "entregar":
            r["corretas_total"] += 1
            r["corretas_preservadas"] += int(e)
        if j["classe"] == "correta_parcial" and j["decisao_ideal_do_pipeline"] == "entregar" and not e:
            r["parciais_bloqueadas"].append(c["id"])
    resumo[v] = r
mudancas = {v: [c["id"] for c in CASOS if var[v][c["id"]]["entregue"] != var["baseline"][c["id"]]["entregue"]] for v in VARS[1:]}
(AQUI / "resultados_4d3_detalhe.json").write_text(json.dumps({"resumo": resumo, "mudancas_vs_baseline": mudancas,
                                                              "por_caso": {c["id"]: {v: var[v][c["id"]] for v in VARS} for c in CASOS},
                                                              "relacoes_baseline": {k: [{kk: x[kk] for kk in ("fonte", "estado", "causas_do_conflito", "necessaria", "bloqueia", "termos_exclusivos", "medida_de_uso")} | {"rotulo": (x["rotulo"] or {}).get("rotulo")} for x in b["rl"]] for k, b in base.items()}},
                                                             ensure_ascii=False, indent=1, default=str), encoding="utf-8")
for c in CASOS:
    b = base[c["id"]]
    print(c["id"], c["julgamento_referencia"]["decisao_ideal_do_pipeline"][:5], "|", b["status"], b["problemas"], "|", {v: var[v][c["id"]]["entregue"] for v in VARS[1:]})
print(json.dumps(resumo, ensure_ascii=False, indent=1))
print("mudancas", mudancas)
