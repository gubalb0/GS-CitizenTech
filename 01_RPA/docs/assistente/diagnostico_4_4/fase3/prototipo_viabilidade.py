"""Fase 3 - PROTOTIPO DE VIABILIDADE (analise; NAO e a implementacao e nao altera o repositorio). Mede, sobre as respostas dadas (4.3) e as liberadas na Fase 2,
quanto cada verificacao candidata sinalizaria, para estimar falsos bloqueios. Saidas gravadas em fase3/prototipo_resultado.json."""
import csv, json, re, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA")
sys.path.insert(0, r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\scripts")
from replay_verificador import replay, ClienteFalso
from citizentech.assistente import avaliacao_e2e as AE, dados as D
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto
from citizentech.assistente.retriever import Indice
from citizentech.assistente.catalogo import Catalogo
from citizentech.assistente.dados import norm_forte
AUD = r"D:\Downloads\GS\RPA\docs\assistente\auditoria_independente_4_3\auditoria_independente_150.csv"
rot = {r["qid"]: r for r in csv.DictReader(open(AUD, encoding="utf-8-sig"), delimiter=";")}
corpus, val, assoc, dup, esp, docs = AE.preparar(); idx = Indice.carregar(AE.IDX); cfg = ConfigGeracao(); cat = Catalogo.de_corpus(corpus)
GAZ = sorted({norm_forte(l) for d in corpus for l in (d.get("localidades") or [])}, key=len, reverse=True)
orig = {}
for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8"):
    o = json.loads(l); orig[o["qid"]] = o
out = replay()
dadas = [q for q, v in out.items() if v["status"] in ("respondida", "parcial")]
NEG = re.compile(r"\bn[aã]o (?:foi|foram|h[aá]|consta\w*|especific\w*|mencion\w*|informa\w*|identific\w*|dispon\w*|existe\w*)\b|\bsem (?:informa|especifica|men)", re.I)
MES = {"janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
def locs(t): 
    t = " " + norm_forte(t) + " "
    return {g for g in GAZ if f" {g} " in t}
def janela(txt, ini, fim=None):
    a = max(txt.rfind(s, 0, ini) for s in (". ", "; ", "Filial (", "\n"))
    a = max(a, ini - 260); b = min(len(txt), (fim or ini) + 260)
    for s in (". ", "; ", "Filial ("):
        j = txt.find(s, (fim or ini)); 
        if j != -1: b = min(b, j)
    return txt[a if a > 0 else 0:b]
def periodo_pergunta(p):
    n = norm_forte(p)
    m = re.search(r"(\d{1,2}) de (\w+)(?: de (\d{4}))? a (\d{1,2}) de (\w+) de (\d{4})", n)
    if m and m.group(2) in MES and m.group(5) in MES:
        y2 = int(m.group(6)); y1 = int(m.group(3) or y2)
        return (y1, MES[m.group(2)], int(m.group(1))), (y2, MES[m.group(5)], int(m.group(4)))
def periodo_doc(t):
    m = re.search(r"per[ií]odo de (\d{2})/(\d{2})/(\d{4}) (?:a|à|ate|até) (\d{2})/(\d{2})/(\d{4})", t, re.I)
    if m: return (int(m.group(3)), int(m.group(2)), int(m.group(1))), (int(m.group(6)), int(m.group(5)), int(m.group(4)))
res_p = {}
for q in val:
    k = q["qid"]
    if k not in dadas: continue
    o = orig[k]; b = json.loads(o["saida"]["telemetria"]["saida_bruta"]); r = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25")
    itens = {i.id: i for i in montar_contexto(q["pergunta"], r, cfg).itens}
    Lq = locs(q["pergunta"]); flags = {}
    neg = bool(NEG.search(b["resposta"]))
    if neg: flags["afirmacao_negativa"] = NEG.search(b["resposta"]).group(0)
    # localidade por registro
    confl = []
    for c in b.get("candidatas", []) + [{"fonte": e["fonte"], "resposta_possivel": e["trecho"]} for e in b.get("evidencias", [])]:
        it = itens.get(c["fonte"])
        if not it or not Lq: continue
        t = it.texto_original; pos = norm_forte(t).find(norm_forte(c["resposta_possivel"])[:40]) if False else t.lower().find(c["resposta_possivel"].lower()[:40])
        if pos < 0: continue
        w = janela(t, pos, pos + len(c["resposta_possivel"])); Lw = locs(w)
        if Lw and not (Lq & Lw): confl.append((it.id, sorted(Lw)))
    if confl: flags["localidade_conflitante_no_registro"] = confl
    # periodo declarado
    pp = periodo_pergunta(q["pergunta"])
    if pp:
        for i in itens.values():
            cid = cat.canonico(i.doc_id); pd = periodo_doc(cat.docs[cid].texto_nf if False else corpus_text) if False else None
    res_p[k] = {"status_fase2": out[k]["status"], "rotulo_auditor": rot[k]["classificacao_independente"], "flags": flags}
# periodo: texto original do corpus por documento
txt = {d["id"]: d["texto_completo"] or "" for d in corpus}
for q in val:
    k = q["qid"]
    if k not in res_p: continue
    pp = periodo_pergunta(q["pergunta"])
    if not pp: continue
    b = json.loads(orig[k]["saida"]["telemetria"]["saida_bruta"]); r = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25"); itens = {i.id: i for i in montar_contexto(q["pergunta"], r, cfg).itens}
    for f in set(b["fontes"]) | {e["fonte"] for e in b["evidencias"]}:
        it = itens[f]; pd = periodo_doc(txt[it.doc_id])
        if pd and (pd[1] < pp[0] or pd[0] > pp[1]): res_p[k]["flags"].setdefault("periodo_declarado_fora_do_pedido", []).append((it.id, it.doc_id, pd))
json.dump(res_p, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase3\prototipo_resultado.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
for k, v in res_p.items():
    print(k, v["status_fase2"][:4], "|", v["rotulo_auditor"][:22], "|", {a: (str(b)[:70]) for a, b in v["flags"].items()})
