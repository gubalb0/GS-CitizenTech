"""Fase 3 - prototipo (analise): evidencias cujo chunk citado NAO contem a localidade/entidade da pergunta (vinculo no chunk, nao no documento)."""
import json, re, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import avaliacao_e2e as AE, evidencias as EV
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto, _texto_alvo
from citizentech.assistente.retriever import Indice
from citizentech.assistente.dados import norm_forte
corpus, val, assoc, dup, esp, docs = AE.preparar(); idx = Indice.carregar(AE.IDX); cfg = ConfigGeracao()
GAZ = sorted({norm_forte(l) for d in corpus for l in (d.get("localidades") or [])}, key=len, reverse=True)
R = {}
for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8"):
    o = json.loads(l); R[o["qid"]] = o
tot = 0
for q in val:
    k = q["qid"]; o = R[k]
    if o["saida"]["status"] not in ("respondida", "parcial"): continue
    f = norm_forte(q["pergunta"]); Lq = {g for g in GAZ if re.search(rf"(?<!\w){re.escape(g)}(?!\w)", f)}
    nomes = [n for n in EV.termos_salientes(q["pergunta"])["nomes"]]
    b = json.loads(o["saida"]["telemetria"]["saida_bruta"]); itens = {i.id: i for i in montar_contexto(q["pergunta"], idx.buscar(q["pergunta"], k=5, modo="bm25"), cfg).itens}
    sem = []
    for e in b["evidencias"]:
        t = norm_forte(itens[e["fonte"]].texto_original)
        falta_loc = Lq and not any(g in t for g in Lq)
        falta_nome = [n for n in nomes if n not in t]
        if falta_loc or falta_nome: sem.append((e["fonte"], "loc" if falta_loc else "", falta_nome[:3]))
    if sem: print(k, o["saida"]["status"][:4], "n_evid", len(b["evidencias"]), "sem vinculo no chunk:", sem)
