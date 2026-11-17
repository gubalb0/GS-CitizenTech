"""Fase 4D.4 - diagnostico OFFLINE sobre dados REAIS ja existentes (150 saidas brutas da rodada 4.3 e 21 da validacao seletiva) + varredura do corpus.
Sem modelo/LM Studio/API; nenhum modulo e alterado (B1/B2 = monkeypatch em memoria restaurado com asserção; C = filtros pos-hoc que so podem bloquear).
Saida: real_4d4.json (apoio de CASOS_REAIS_4D4.md)."""
import csv
import glob
import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(r"D:\Downloads\GS\RPA")
sys.path.insert(0, str(RAIZ))
from citizentech.assistente import avaliacao_e2e as AE  # noqa: E402
from citizentech.assistente import evidencias as EV  # noqa: E402
from citizentech.assistente import geracao as G  # noqa: E402
from citizentech.assistente.catalogo import Catalogo  # noqa: E402
from citizentech.assistente.retriever import Indice  # noqa: E402

AQUI = pathlib.Path(__file__).parent
D = RAIZ / "docs" / "assistente" / "diagnostico_4_4" / "fase4"
corpus, val, *_ = AE.preparar()
cat, idx = Catalogo.de_corpus(corpus), Indice.carregar(AE.IDX)
orig = {json.loads(ln)["qid"]: json.loads(ln) for ln in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8")}
aud = {r["qid"]: r["classificacao_independente"] for r in csv.DictReader(open(RAIZ / "docs/assistente/auditoria_independente_4_3/auditoria_independente_150.csv", encoding="utf-8-sig"), delimiter=";")}
regs = {json.loads(ln)["run_id"]: json.loads(ln) for f in sorted(glob.glob(str(D / "validacao_seletiva*.jsonl"))) for ln in open(f, encoding="utf-8")}


class F:
    def __init__(s, b): s.b = b
    def completar(s, m, temperatura=None): return {"conteudo": s.b, "finish": "stop", "tokens_prompt": 0, "tokens_saida": 0, "tokens_raciocinio": 0, "latencia_s": 0.0}


def itens_texto(p, flag):
    cfg = G.ConfigGeracao(priorizar_atributo=flag)
    ctx = G.montar_contexto(p, idx.buscar(p, k=5, modo="bm25"), cfg)
    return {it.id: it.texto_original for it in ctx.itens}


def rodar(p, bruto, flag=False):
    cfg = G.ConfigGeracao(priorizar_atributo=flag)
    return G.gerar_resposta(p, idx.buscar(p, k=5, modo="bm25"), F(bruto), cfg, catalogo=cat)


def rels(r):
    return [x for x in ((r.verificacao or {}).get("evidencia") or {}).get("protecao", {}).get("relacoes", []) if x["origem"] == "citacao"]


def filtro_C(pergunta, resposta, rl, textos, modo):
    """C simplificada (mesma definicao da 4D.3): cada nome saliente da pergunta repetido na resposta deve constar no chunk de uma citacao nao conflitante.
    modo 'estado' = 4D.3 (conflito = estado do rotulo); modo 'causas' = conflito = causas_do_conflito nao vazias (nocao do proprio pipeline). Diagnostico, nao proposta."""
    nomes = [n for n in EV.termos_salientes(pergunta)["nomes"] if n in EV._nf(resposta)]
    for n in nomes:
        def ruim(x): return x["estado"] == "conflito" if modo == "estado" else bool(x["causas_do_conflito"])
        if not any(n in EV._nf(textos[x["fonte"]]) and not ruim(x) for x in rl):
            return n
    return None


def variante_termos(modo):
    def f(resposta, pergunta):
        q = set(EV.tokens_de_uso(pergunta))
        nomes = set(EV.termos_salientes(pergunta)["nomes"])
        if modo == "B1":
            q = {t for t in q if t not in nomes}
        elif modo == "B2":
            q = set()
        qrad = {EV._radical(w) for w in q if len(w) >= 6 and not w.isdigit()}
        out = [t for t in EV.tokens_de_uso(resposta) if t and t not in EV.PALAVRAS_FUNCIONAIS and t not in EV.GENERICAS and t not in q and not (len(t) >= 6 and not t.isdigit() and EV._radical(t) in qrad)]
        return list(dict.fromkeys(out))
    return f


def avaliar(chave, p, bruto, flag, classe):
    base = rodar(p, bruto, flag)
    rl, tx = rels(base), itens_texto(p, flag)
    resp = json.loads(bruto).get("resposta", "") if bruto else ""
    ent = base.status in ("respondida", "parcial")
    out = {"id": chave, "pergunta": p, "classe_4_3_ou_nd": classe, "status_baseline": base.status, "problemas": (base.verificacao or {}).get("problemas"), "entregue": ent,
           "estados_citacoes": [x["estado"] for x in rl], "causas": [x["causas_do_conflito"] for x in rl]}
    out["C_estado_bloqueia"] = filtro_C(p, resp, rl, tx, "estado") if ent else None
    out["C_causas_bloqueia"] = filtro_C(p, resp, rl, tx, "causas") if ent else None
    return out


orig_tdu = EV.termos_de_uso
res150 = [avaliar(q["qid"], q["pergunta"], orig[q["qid"]]["saida"]["telemetria"]["saida_bruta"], False, aud[q["qid"]]) for q in val]
res21 = [avaliar(rid, r["saida"]["pergunta"], r["saida"]["telemetria"]["saida_bruta"], bool(r["flag_priorizar_atributo"]), "n/d (sem gabarito humano; ver auditoria 4C)") for rid, r in regs.items()]
dentro = {}
for modo in ("B1", "B2"):
    EV.termos_de_uso = variante_termos(modo)
    try:
        dentro[modo] = {"150": [x["id"] for x, q in zip(res150, val) if (rodar(q["pergunta"], orig[q["qid"]]["saida"]["telemetria"]["saida_bruta"]).status in ("respondida", "parcial")) != x["entregue"]],
                        "21": [rid for rid, r in regs.items() if (rodar(r["saida"]["pergunta"], r["saida"]["telemetria"]["saida_bruta"], bool(r["flag_priorizar_atributo"])).status in ("respondida", "parcial")) != next(y["entregue"] for y in res21 if y["id"] == rid)]}
    finally:
        EV.termos_de_uso = orig_tdu
assert EV.termos_de_uso is orig_tdu

# ---- varredura do corpus: itens de lista 'N - Titular: ...' e sua fragilidade quanto ao 'cue' de competencia
itens_titular = []
for d in corpus:
    for m in re.finditer(r"\d{1,3}\s*-\s*Titular:[^;]*(?:;\s*Suplente:[^;]*)?", d["texto_completo"]):
        itens_titular.append({"doc": d["id"], "item": m.group(0)[:200], "cue_competencia": EV.cue_de_atributo(m.group(0), "COMPETENCIA")})
cue_hits = [x for x in itens_titular if x["cue_competencia"]]
out = {"res150_entregues": [x for x in res150 if x["entregue"]], "res150_C_bloqueios": [x["id"] for x in res150 if x["C_estado_bloqueia"] or x["C_causas_bloqueia"]],
       "res21_entregues": [x for x in res21 if x["entregue"]], "B1B2_mudancas": dentro, "itens_titular_total": len(itens_titular), "itens_titular_com_cue_competencia": cue_hits,
       "docs_com_titular": sorted({x["doc"] for x in itens_titular})}
(AQUI / "real_4d4.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
print("entregues150", len(out["res150_entregues"]), "C bloqueia (150):", [(x["id"], x["classe_4_3_ou_nd"], x["C_estado_bloqueia"], x["C_causas_bloqueia"]) for x in res150 if x["C_estado_bloqueia"] or x["C_causas_bloqueia"]])
print("entregues21", len(out["res21_entregues"]), "C bloqueia (21):", [(x["id"], x["C_estado_bloqueia"], x["C_causas_bloqueia"]) for x in res21 if x["C_estado_bloqueia"] or x["C_causas_bloqueia"]])
print("B1B2", dentro); print("itens titular", len(itens_titular), "docs", out["docs_com_titular"], "cue hits", len(cue_hits), cue_hits[:5])
