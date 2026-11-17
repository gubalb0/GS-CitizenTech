"""Auditoria de encerramento da 4A - diagnostico SOMENTE LEITURA da montagem de contexto (sem LLM; orcamento e funcoes de contexto inalterados)."""
import json, re, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA")
from collections import Counter
from citizentech.assistente import avaliacao_e2e as AE, evidencias as EV, grupos as GR, geracao as G
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto, estimar_tokens, contar_tokens, _cabecalho, neutralizar, PROMPT_SISTEMA
from citizentech.assistente.retriever import Indice
corpus, val, assoc, dup, esp, docs = AE.preparar(); idx = Indice.carregar(AE.IDX); cfg = ConfigGeracao()
orig = {json.loads(l)["qid"]: json.loads(l) for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8")}
def espelho(pergunta, res):
    """Espelha montar_contexto registrando tokens e motivo por chunk (somente leitura)."""
    base = estimar_tokens(PROMPT_SISTEMA + pergunta + "/no_think PERGUNTA DO CIDADÃO: <DOCUMENTOS_NAO_CONFIAVEIS>", cfg.razao_qwen) + 40
    total, n_env, linhas = base, 0, []
    for r in res:
        if n_env >= cfg.max_chunks:
            linhas.append({"chunk": r.chunk_id, "doc": r.doc_id, "pos": r.posicao, "tokens": None, "enviado": False, "motivo": "max_chunks"}); continue
        orig_t = r.texto; cortado = False
        if contar_tokens(orig_t) > cfg.max_tokens_chunk:
            pal = orig_t.split()
            while pal and contar_tokens(" ".join(pal)) > cfg.max_tokens_chunk: pal = pal[: int(len(pal) * 0.9)]
            orig_t, cortado = " ".join(pal) + " [...]", True
        bloco = f"[C{n_env + 1}] {_cabecalho(r.metadados or {}, n_env)}{' | trecho cortado' if cortado else ''}\n{neutralizar(orig_t)}\n[/C{n_env + 1}]"
        n = estimar_tokens(bloco, cfg.razao_qwen)
        if total + n > cfg.orcamento_tokens:
            linhas.append({"chunk": r.chunk_id, "doc": r.doc_id, "pos": r.posicao, "tokens": n, "enviado": False, "motivo": f"orcamento (acumulado {total} + {n} > {cfg.orcamento_tokens})"}); continue
        total += n; n_env += 1
        linhas.append({"chunk": r.chunk_id, "doc": r.doc_id, "pos": r.posicao, "tokens": n, "enviado": True, "motivo": "enviado"})
    return base, total, linhas
def cues(pergunta):
    cab = EV.cabeca_do_atributo(pergunta); fam = EV.familia_do_atributo(cab)
    pal = {w for w, f in EV.FAM_ROTULO.items() if fam and f in EV.COMPATIVEL.get(fam, {fam})}
    return cab, fam, pal
def tem(texto, cab, pal):
    t = EV._nf(texto); ws = set(re.findall(r"[a-z]+", t))
    return {"familia": sorted(ws & pal), "cabeca": bool(cab and len(cab) >= 6 and cab[:6] in t)}
out, resumo = {}, Counter()
cands_4b = []
for q, e in zip(val, esp):
    k = q["qid"]; res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25")
    base, total, linhas = espelho(q["pergunta"], res)
    real = [i.chunk_id for i in montar_contexto(q["pergunta"], res, cfg).itens]
    assert [l["chunk"] for l in linhas if l["enviado"]] == real, k
    cab, fam, pal = cues(q["pergunta"])
    for l, r in zip(linhas, res):
        l.update(tem(r.texto, cab, pal))
    desc = [l for l in linhas if not l["enviado"]]
    resumo["perguntas"] += 1; resumo["com_descarte"] += bool(desc)
    env_fam = any(l["familia"] for l in linhas if l["enviado"]); desc_fam = [l for l in desc if l["familia"]]
    if fam and desc_fam and not env_fam: cands_4b.append(k)
    out[k] = {"cabeca": cab, "familia": fam, "base_tokens": base, "total_tokens": total, "chunks": linhas, "cue_familia_so_em_descartado": bool(fam and desc_fam and not env_fam)}
resumo["perguntas_com_cue_de_familia_apenas_em_chunk_descartado"] = len(cands_4b)
print(dict(resumo)); print("candidatas a priorizacao por atributo:", cands_4b)
tk = [l["tokens"] for v in out.values() for l in v["chunks"] if l["tokens"]]
print("tokens por chunk: min %d med %d max %d | base do prompt (med) %d | enviados por pergunta:" % (min(tk), sorted(tk)[len(tk)//2], max(tk), sorted(v["base_tokens"] for v in out.values())[75]), Counter(sum(l["enviado"] for l in v["chunks"]) for v in out.values()))
# simulacao S1: chunks com cue de familia do atributo primeiro (ordem estavel), mesmo orcamento
sim = {}
for q, e in zip(val, esp):
    k = q["qid"]; res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25"); cab, fam, pal = cues(q["pergunta"])
    ord_ = sorted(range(len(res)), key=lambda i: (0 if (fam and tem(res[i].texto, cab, pal)["familia"]) else 1, i)) if fam else list(range(len(res)))
    res2 = [res[i] for i in ord_]
    it0 = montar_contexto(q["pergunta"], res, cfg).itens; it1 = montar_contexto(q["pergunta"], res2, cfg).itens
    g0, g1 = GR.grupo_ab(e, it0)[0], GR.grupo_ab(e, it1)[0]
    sim[k] = {"mudou_o_conjunto": {i.chunk_id for i in it0} != {i.chunk_id for i in it1}, "grupo0": g0, "grupo1": g1, "familia": fam}
mud = [k for k, v in sim.items() if v["mudou_o_conjunto"]]
print("S1 (priorizar chunk com rotulo da familia do atributo): perguntas com contexto diferente:", len(mud), mud)
print("   grupos A/B que mudam:", [(k, sim[k]["grupo0"], sim[k]["grupo1"]) for k in mud if sim[k]["grupo0"] != sim[k]["grupo1"]])
for k in ("val-087", "val-063", "val-074", "val-086", "val-147"):
    v = out[k]; print(k, v["cabeca"], v["familia"], [(l["pos"], l["doc"], l["tokens"], l["enviado"], l["motivo"][:40], l["familia"], l["cabeca"]) for l in v["chunks"]], "-> S1 muda:", sim[k]["mudou_o_conjunto"])
json.dump({"por_pergunta": out, "simulacao_S1": sim, "candidatas_priorizacao": cands_4b}, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase4\auditoria_4a_contexto.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- S1 forte: so rotulos que repetem o proprio atributo pedido ('compete'/'competencia' para 'competencias'; 'valor' para 'valor'...)
def cue_forte(pergunta):
    cab = EV.cabeca_do_atributo(pergunta); fam = EV.familia_do_atributo(cab)
    if not fam: return cab, fam, set()
    return cab, fam, {w for w, f in EV.FAM_ROTULO.items() if f == fam and (w[:5] == cab[:5])}
sim2 = {}
for q, e in zip(val, esp):
    k = q["qid"]; res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25"); cab, fam, pal = cue_forte(q["pergunta"])
    ord_ = sorted(range(len(res)), key=lambda i: (0 if (pal and tem(res[i].texto, cab, pal)["familia"]) else 1, i)) if pal else list(range(len(res)))
    res2 = [res[i] for i in ord_]
    it0 = montar_contexto(q["pergunta"], res, cfg).itens; it1 = montar_contexto(q["pergunta"], res2, cfg).itens
    sim2[k] = {"mudou": {i.chunk_id for i in it0} != {i.chunk_id for i in it1}, "g0": GR.grupo_ab(e, it0)[0], "g1": GR.grupo_ab(e, it1)[0], "sent0": [i.chunk_id[-4:] for i in it0], "sent1": [i.chunk_id[-4:] for i in it1], "forte": sorted(pal)}
m2 = [k for k, v in sim2.items() if v["mudou"]]
print("\nS1 FORTE: perguntas com contexto diferente:", len(m2), m2)
print("   val-087:", sim2["val-087"]); print("   grupos A/B que mudam:", [(k, sim2[k]["g0"], sim2[k]["g1"]) for k in m2 if sim2[k]["g0"] != sim2[k]["g1"]])
dad = [k for k, v in orig.items() if v["saida"]["status"] in ("respondida", "parcial")]
print("   respostas dadas na 4.3 cujo contexto mudaria:", [k for k in m2 if k in dad])
json.dump(sim2, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase4\auditoria_4a_contexto_S1forte.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- S2: priorizar o chunk que cobre MAIS nomes proprios/localidades da pergunta (mesmo orcamento)
def cobertura_nomes(res, pergunta):
    nomes = EV.termos_salientes(pergunta)["nomes"]
    return [sum(1 for n in nomes if n in EV._nf(r.texto)) for r in res], nomes
sim3 = {}
for q, e in zip(val, esp):
    k = q["qid"]; res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25"); cov, nomes = cobertura_nomes(res, q["pergunta"])
    ord_ = sorted(range(len(res)), key=lambda i: (-cov[i], i)); res2 = [res[i] for i in ord_]
    it0 = montar_contexto(q["pergunta"], res, cfg).itens; it1 = montar_contexto(q["pergunta"], res2, cfg).itens
    sim3[k] = {"mudou": {i.chunk_id for i in it0} != {i.chunk_id for i in it1}, "g0": GR.grupo_ab(e, it0)[0], "g1": GR.grupo_ab(e, it1)[0], "cov": cov, "nomes": nomes}
m3 = [k for k, v in sim3.items() if v["mudou"]]
print("\nS2 (priorizar cobertura de nomes da pergunta): contexto diferente em", len(m3), "perguntas | grupos A->B:", [(k, sim3[k]["g0"], sim3[k]["g1"]) for k in m3 if sim3[k]["g0"] == "A" and sim3[k]["g1"] == "B"], "| B->A:", [k for k in m3 if sim3[k]["g0"] == "B" and sim3[k]["g1"] == "A"])
print("   respostas dadas na 4.3 cujo contexto mudaria:", [k for k in m3 if k in dad])
for k in ("val-087", "val-063", "val-074", "val-086", "val-147"): print("  ", k, sim3[k]["nomes"], sim3[k]["cov"], "muda:", sim3[k]["mudou"])
