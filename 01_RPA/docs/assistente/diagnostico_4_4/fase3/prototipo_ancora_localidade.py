"""Fase 3 - prototipo (analise): localidade MAIS PROXIMA do identificador citado na resposta (CNPJ/numero/valor), no chunk citado."""
import json, re, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import avaliacao_e2e as AE
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto
from citizentech.assistente.retriever import Indice
from citizentech.assistente.dados import norm_forte
corpus, val, assoc, dup, esp, docs = AE.preparar(); idx = Indice.carregar(AE.IDX); cfg = ConfigGeracao()
GAZ = sorted({norm_forte(l) for d in corpus for l in (d.get("localidades") or [])}, key=len, reverse=True)
R = {}
for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8"):
    o = json.loads(l); R[o["qid"]] = o
def posicoes_loc(t):
    f = norm_forte(t); out = []
    for g in GAZ:
        for m in re.finditer(rf"(?<!\w){re.escape(g)}(?!\w)", f): out.append((m.start(), g))
    return f, out
for q in val:
    k = q["qid"]; o = R[k]
    if o["saida"]["status"] not in ("respondida", "parcial"): continue
    Lq = {g for g in GAZ if re.search(rf"(?<!\w){re.escape(g)}(?!\w)", norm_forte(q["pergunta"]))}
    if not Lq: continue
    b = json.loads(o["saida"]["telemetria"]["saida_bruta"]); itens = {i.id: i for i in montar_contexto(q["pergunta"], idx.buscar(q["pergunta"], k=5, modo="bm25"), cfg).itens}
    anc = set(re.findall(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|R\$\s?[\d.,]+|\b\d{5,}[\d/.\-]*\b", b["resposta"]))
    achados = []
    for f in set(b["fontes"]):
        f_txt, locs = posicoes_loc(itens[f].texto_original)
        for a in anc:
            a_n = norm_forte(a).replace(" ", "")
            for m in re.finditer(re.escape(a_n), f_txt.replace(" ", "")):   # aproximacao: posicao no texto sem espacos ~ proporcional; usa busca direta
                pass
            p = f_txt.find(norm_forte(a))
            if p < 0 or not locs: continue
            viz = min(locs, key=lambda x: abs(x[0] - p)); dist = abs(viz[0] - p)
            if dist <= 300: achados.append((f, a[:22], viz[1], dist, "OK" if viz[1] in Lq else "CONFLITO"))
    print(k, o["saida"]["status"][:4], sorted(Lq), achados[:4])
