"""Fase 4D.7 - COPIA de executar_4d5.py (so troca o modulo para prototipo_vinculo_4d7, entradas em ../fase4d5 somente leitura e saidas fora do projeto). Original: executa o prototipo (offline, sem modelo) nos casos sinteticos e nos 5 casos reais. Verifica o congelamento da rotulagem antes de executar."""
import csv
import glob
import hashlib
import json
import pathlib
import sys
from collections import Counter

RAIZ = pathlib.Path(r"D:\Downloads\GS\RPA")
sys.path.insert(0, str(RAIZ))
OUT = pathlib.Path(__file__).parent
AQUI = OUT.parent / "fase4d5"   # insumos (somente leitura): casos, especificacao e congelamento da 4D.5
SCR = pathlib.Path(r"C:/Users/henry/AppData/Local/Temp/claude/1d1f73d24e18fb6a/619b1d2d-4dd6-4445-ba09-b40d8dcd3ae8/scratchpad")   # saidas brutas intermediarias fora do projeto
sys.path.insert(0, str(OUT))
from prototipo_vinculo_4d7 import F, Publicacao, afirmacoes, avaliar  # noqa: E402

cong = json.loads((AQUI / "CONGELAMENTO_ROTULAGEM_4D5.json").read_text(encoding="utf-8"))
for n, h in cong["sha256"].items():
    assert hashlib.sha256((AQUI / n).read_bytes()).hexdigest() == h, f"rotulagem alterada depois do congelamento: {n}"
SINT = json.loads((AQUI / "CASOS_SINTETICOS_4D5.json").read_text(encoding="utf-8"))["casos"]
REAIS = json.loads((AQUI / "ESPECIFICACAO_REAIS_4D5.json").read_text(encoding="utf-8"))
NIV = ["N1", "N2", "N3", "N4"]


def classe(esp, aceita):
    if esp == "sustentado":
        return "TP" if aceita else "FN_perda_de_recall"
    if esp.startswith("nao_sustentado"):
        return "FP_falso_vinculo" if aceita else "TN"
    if esp == "sustentado_documental":
        return "doc_aceito" if aceita else "doc_rejeitado(so_documental)"
    return "incerto_aceito" if aceita else "incerto_rejeitado"


linhas = []


def registrar(origem, cid, alvo, esp, res, nota=""):
    linhas.append({"origem": origem, "id": cid, "alvo": alvo, "esperado": esp, "estados": res["niveis"], "aceita": res["aceita"], "classe": {n: classe(esp, res["aceita"][n]) for n in NIV},
                   "detalhes": res.get("detalhes"), "unidades_citadas": res["unidades_citadas"], "unidades_atributo": res["unidades_atributo"], "nota": (res.get("nota", "") + " " + nota).strip()})


# ---------------- sinteticos
for c in SINT:
    pubs = {}
    for pid, chunks in c["publicacoes"].items():
        texto, cs, pos = "", {}, 0
        for k, ct in enumerate(chunks):
            texto += (" " if texto else "") + ct
            cs[f"{pid}:c{k + 1}"] = ct
        pubs[pid] = Publicacao(pid, texto, cs)
    pid_cit = c["citacoes"][0]["pub"]
    pub = pubs[pid_cit]
    trechos = [x["texto"] for x in c["citacoes"] if x["pub"] == pid_cit]
    outras_pubs = [(p, pb.texto) for p, pb in pubs.items() if p != pid_cit]
    cls = afirmacoes(c["resposta"], c["pergunta"])
    for al in c["alvos"]:
        alvo_f = F(al["trecho_da_resposta"])
        cl = next((x for x in cls if alvo_f in F(x["texto"])), cls[0])
        toks_ent = {t for fm in c["entidade"]["formas"] for t in fm.split()}
        termos = [t for t in cl["termos"] if t not in toks_ent]
        res = avaliar(pub, trechos, termos, c["entidade"], c["atributo_familia"], [F(o) for o in c["outras_entidades"]], outras_pubs)
        registrar("sintetico", c["id"], al["trecho_da_resposta"], al["vinculo_esperado"], res, f"clausula='{cl['texto'][:60]}' termos={termos}")

# ---------------- reais
from citizentech.assistente import avaliacao_e2e as AE  # noqa: E402
from citizentech.assistente import geracao as G  # noqa: E402
from citizentech.assistente.retriever import Indice  # noqa: E402

corpus, val, *_ = AE.preparar()
docs = {d["id"]: d for d in corpus}
idx = Indice.carregar(AE.IDX)
V = {x["qid"]: x for x in val}
orig = {json.loads(ln)["qid"]: json.loads(ln) for ln in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8")}
regs = {json.loads(ln)["run_id"]: json.loads(ln) for f in sorted(glob.glob(str(RAIZ / "docs/assistente/diagnostico_4_4/fase4/validacao_seletiva*.jsonl"))) for ln in open(f, encoding="utf-8")}


def contexto(perg, flag=False):
    return G.montar_contexto(perg, idx.buscar(perg, k=5, modo="bm25"), G.ConfigGeracao(priorizar_atributo=flag))


def bruto_de(cid):
    if cid.startswith("val-087-A"):
        s = regs[cid]["saida"]
        return s["pergunta"], json.loads(s["telemetria"]["saida_bruta"]), bool(regs[cid]["flag_priorizar_atributo"])
    return V[cid]["pergunta"], json.loads(orig[cid]["saida"]["telemetria"]["saida_bruta"]), False


def pub_real(ctx, doc):
    its = {i.chunk_id: i.texto_original for i in ctx.itens if i.doc_id == doc}
    return Publicacao(str(doc), docs[doc]["texto_completo"], its), its


for cid, sp in REAIS.items():
    perg, bruto, flag = bruto_de(cid)
    ctx = contexto(perg, flag)
    citados = [e for e in bruto["evidencias"]]
    fonte_item = {i.id: i for i in ctx.itens}
    if cid == "val-083":
        for item, esp in sp["itens"].items():
            e = next(x for x in bruto["evidencias"] if item.lower() in x["trecho"].lower())
            it = fonte_item[e["fonte"]]
            pub, _ = pub_real(ctx, it.doc_id)
            termos = [t for t in __import__("citizentech.assistente.evidencias", fromlist=["x"]).tokens_de_uso(item) if len(t) > 2]
            res = avaliar(pub, [e["trecho"]], termos, sp["entidades"][0], sp["atributo_familia"], [F(o) for o in sp["outras_entidades"]], [])
            registrar("real", cid, f"item {item} (doc {it.doc_id})", esp, res, "destinatário avaliado como entidade")
        continue
    docs_pub = {}
    for e in sp["entidades"]:
        cl = next((x for x in afirmacoes(bruto["resposta"], perg) if any(F(fm) in F(x["texto"]) for fm in e["formas"])), None)
        if cl is None:
            cl = afirmacoes(bruto["resposta"], perg)[0]
        toks_ent = {t for fm in e["formas"] for t in fm.split()}
        termos = [t for t in cl["termos"] if t not in toks_ent]
        pubs_citadas = {}
        for ev in citados:
            if ev["fonte"] in fonte_item and fonte_item[ev["fonte"]].doc_id == sp["doc"]:
                pubs_citadas.setdefault(sp["doc"], []).append(ev["trecho"])
        if sp["doc"] not in pubs_citadas:   # val-087 etc.: todos os itens citados do documento
            raise SystemExit(f"{cid}: nenhuma citação no doc {sp['doc']}")
        pub, its = pub_real(ctx, sp["doc"])
        res = avaliar(pub, pubs_citadas[sp["doc"]], termos, e, sp["atributo_familia"], [F(o) for o in sp["outras_entidades"]], [])
        x = sp["esperado"][e["nome"]]
        registrar("real", cid, e["nome"], x["vinculo"], res, f"clausula='{cl['texto'][:80]}' termos={termos}; chunks_do_contexto={sorted(its)}")

# ---------------- saidas
with open(SCR / "resultados_niveis_4d7_bruto.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["origem", "id", "alvo", "esperado"] + [f"{n}_estado" for n in NIV] + [f"{n}_aceita" for n in NIV] + [f"{n}_classe" for n in NIV] + ["nota"])
    for L in linhas:
        w.writerow([L["origem"], L["id"], L["alvo"], L["esperado"]] + [L["estados"][n] for n in NIV] + [L["aceita"][n] for n in NIV] + [L["classe"][n] for n in NIV] + [L["nota"]])
(SCR / "resultados_4d7_detalhe.json").write_text(json.dumps(linhas, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
for origem in ("sintetico", "real"):
    print("=====", origem)
    for n in NIV:
        c = Counter(L["classe"][n] for L in linhas if L["origem"] == origem)
        tp, fp, fn = c["TP"], c["FP_falso_vinculo"], c["FN_perda_de_recall"]
        print(n, dict(c), "precisao", round(tp / (tp + fp), 2) if tp + fp else None, "recall", round(tp / (tp + fn), 2) if tp + fn else None)
for L in linhas:
    print(L["origem"][:3], L["id"], "|", L["alvo"][:28], "|", L["esperado"], "|", [L["estados"][n] for n in NIV], [int(L["aceita"][n]) for n in NIV])
