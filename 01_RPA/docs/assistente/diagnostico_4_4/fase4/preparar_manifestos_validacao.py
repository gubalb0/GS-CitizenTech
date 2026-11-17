"""Fase 4B - PREPARACAO do protocolo de validacao seletiva. OFFLINE: monta contextos/mensagens/requisicoes (sem enviar nada a modelo) e grava os manifestos congelados.
Nao chama LM Studio nem API; nao altera pipeline, corpus, indices, gabaritos ou snapshots. Saida: protocolo_validacao_manifestos.json"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import avaliacao_e2e as AE
from citizentech.assistente import geracao as G
from citizentech.assistente.retriever import Indice

RAIZ = Path(r"D:\Downloads\GS\RPA")
AQUI = Path(__file__).parent
sha = lambda b: hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()
js = lambda o: json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

ALVOS = {"val-074": ["A", "B"], "val-087": ["A", "B"]}
CONTROLES = {"val-006": "Correta (respondida)", "val-024": "Correta, mas parcial (respondida)", "val-025": "Abstencao correta (fora_do_escopo)"}
REPS = 3

corpus, val, assoc, dup, esp, docs = AE.preparar()
idx = Indice.carregar(AE.IDX)
perg = {q["qid"]: q["pergunta"] for q in val}
orig = {json.loads(l)["qid"]: json.loads(l) for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8")}
cfg_off, cfg_on = G.ConfigGeracao(), G.ConfigGeracao(priorizar_atributo=True)

codigo = {n: sha((RAIZ / "citizentech" / "assistente" / n).read_bytes()) for n in ("geracao.py", "evidencias.py", "catalogo.py")}
snap = {n: sha((RAIZ / "data_assistente" / "versoes" / n).read_bytes()) for n in ("geracao_44_fase4b_cand.py", "evidencias_44_fase4b_cand.py", "geracao_44_fase4a.py", "evidencias_44_fase4a.py")}
assert codigo["geracao.py"] == snap["geracao_44_fase4b_cand.py"] and codigo["evidencias.py"] == snap["evidencias_44_fase4b_cand.py"], "codigo vivo difere do snapshot candidato"
sysmsg = G.PROMPT_SISTEMA


def corpo_requisicao(cfg, mensagens):
    """Exatamente o corpo montado por ClienteLMStudio.completar (sem seed: o pipeline nao define seed)."""
    return {"model": cfg.modelo, "messages": mensagens, "temperature": cfg.temperatura, "top_p": cfg.top_p, "max_tokens": cfg.max_tokens_saida, "stream": False,
            "response_format": {"type": "json_schema", "json_schema": {"name": "resposta_cidadao", "strict": True, "schema": G.ESQUEMA_SAIDA}}}


def montar(qid, cond):
    cfg = cfg_on if cond == "B" else cfg_off
    res = idx.buscar(perg[qid], k=cfg.max_chunks, modo="bm25")
    c = G.montar_contexto(perg[qid], res, cfg)
    corpo = corpo_requisicao(cfg, c.mensagens)
    params = {k: v for k, v in corpo.items() if k != "messages"}
    por_id = {r.chunk_id: r for r in res}
    return {"qid": qid, "pergunta": perg[qid], "flag_priorizar_atributo": cfg.priorizar_atributo,
            "versao_politica": G.VERSAO_POLITICA, "versao_prompt": G.VERSAO_PROMPT,
            "hash_prompt_sistema": sha(sysmsg), "hash_mensagens": sha(js(c.mensagens)), "hash_contexto": sha(c.mensagens[1]["content"]), "hash_parametros": sha(js(params)),
            "hash_corpo_requisicao": sha(js(corpo)),
            "parametros": {**params, "response_format": "json_schema:resposta_cidadao(strict) hash=" + sha(js(G.ESQUEMA_SAIDA))[:16], "seed": None, "tentativas_json": cfg.tentativas_json,
                           "temperatura_retentativa": 0.0, "orcamento_tokens": cfg.orcamento_tokens, "max_chunks": cfg.max_chunks, "razao_qwen": cfg.razao_qwen, "max_tokens_chunk": cfg.max_tokens_chunk},
            "chunks_enviados": [{"id_prompt": i.id, "chunk_id": i.chunk_id, "doc_id": i.doc_id, "posicao_ranking": i.posicao, "sha256_texto": sha(i.texto_original), "tokens_estimados": i.tokens_estimados} for i in c.itens],
            "tokens_contexto_estimados": c.tokens_estimados, "selecao_s1": c.selecao if cfg.priorizar_atributo else []}, c


def referencia_historica(qid):
    s = orig[qid]["saida"]
    return {"status": s["status"], "resposta": s["resposta"], "problemas": (s.get("verificacao") or {}).get("problemas"), "tentativas": s["telemetria"]["tentativas"],
            "tokens_contexto_estimados": s["telemetria"]["tokens_contexto_estimados"], "tokens_prompt_real": s["telemetria"]["tokens_prompt"],
            "versao_politica_da_rodada": s["telemetria"]["versao_politica"], "resposta_referencia_benchmark": orig[qid]["resposta_referencia"]}


slots = {}
for qid, conds in ALVOS.items():
    for cond in conds:
        slots[f"{qid}-{cond}"], _ = montar(qid, cond)
        slots[f"{qid}-{cond}"].update({"condicao": cond, "papel": "alvo", "referencia_historica_4_3": referencia_historica(qid)})
for qid, rot in CONTROLES.items():
    slots[f"{qid}-C"], _ = montar(qid, "A")
    slots[f"{qid}-C"].update({"condicao": "C", "papel": "controle", "classe_auditoria_4_3": rot, "referencia_historica_4_3": referencia_historica(qid)})

# ordem sequencial: 1 geracao por vez; blocos por repeticao; ordem A/B alternada (ABBA) para neutralizar deriva/ordem
execs = []
for r in range(1, REPS + 1):
    ab = ["A", "B"] if r % 2 else ["B", "A"]
    bloco = [f"val-074-{ab[0]}", f"val-074-{ab[1]}", f"val-087-{ab[0]}", f"val-087-{ab[1]}"] if r % 2 else [f"val-087-{ab[0]}", f"val-087-{ab[1]}", f"val-074-{ab[0]}", f"val-074-{ab[1]}"]
    bloco += [f"{q}-C" for q in (CONTROLES if r % 2 else reversed(list(CONTROLES)))]
    for s in bloco:
        execs.append({"ordem": len(execs) + 1, "run_id": f"{s}-r{r}", "slot": s, "repeticao": r, "condicao": slots[s]["condicao"], "papel": slots[s]["papel"]})

# --- auditoria de consistencia (A x B so diferem no contexto)
cons = {}
for qid in ALVOS:
    a, b = slots[f"{qid}-A"], slots[f"{qid}-B"]
    cons[qid] = {"hash_prompt_sistema_igual": a["hash_prompt_sistema"] == b["hash_prompt_sistema"], "hash_parametros_igual": a["hash_parametros"] == b["hash_parametros"],
                 "versao_prompt_igual": a["versao_prompt"] == b["versao_prompt"], "pergunta_igual": a["pergunta"] == b["pergunta"],
                 "hash_contexto_diferente": a["hash_contexto"] != b["hash_contexto"], "chunks_A": [c["chunk_id"] for c in a["chunks_enviados"]], "chunks_B": [c["chunk_id"] for c in b["chunks_enviados"]],
                 "so_o_contexto_difere": a["hash_prompt_sistema"] == b["hash_prompt_sistema"] and a["hash_parametros"] == b["hash_parametros"] and a["hash_contexto"] != b["hash_contexto"]}
base_a = {}
for qid in list(ALVOS) + list(CONTROLES):
    s = slots[f"{qid}-A"] if qid in ALVOS else slots[f"{qid}-C"]
    base_a[qid] = {"contexto_reproduz_rodada_4_3": s["tokens_contexto_estimados"] == orig[qid]["saida"]["telemetria"]["tokens_contexto_estimados"] and
                   len(s["chunks_enviados"]) == orig[qid]["saida"]["telemetria"]["chunks_enviados"]}
ctrl_ctx_igual_com_flag = {}
for qid in CONTROLES:
    on, _ = montar(qid, "B")
    ctrl_ctx_igual_com_flag[qid] = on["hash_contexto"] == slots[f"{qid}-C"]["hash_contexto"]
man = {"descricao": "Manifestos congelados da validacao seletiva da Fase 4B (versao candidata). NENHUMA geracao foi executada na elaboracao deste arquivo.",
       "gerado_por": "preparar_manifestos_validacao.py (offline)", "versao_pipeline": G.VERSAO_POLITICA, "hash_codigo_vivo": codigo, "hash_snapshots": snap,
       "modelo": {"id_api": cfg_off.modelo, "arquivo": "Qwen3-8B Q4_K_M (bartowski)", "runtime": "LM Studio 0.4.28, llama.cpp Vulkan 2.73.0 (memoria do projeto, D2)", "contexto_lm_studio": 8192,
                  "a_registrar_na_execucao": ["id/arquivo do modelo carregado (GET /v1/models)", "versao do LM Studio e do runtime", "GPU offload, flash attention, batch size, threads (captura da configuracao ativa, sem altera-la)", "RAM livre antes/durante"]},
       "slots": slots, "sequencia": execs, "n_geracoes_recomendado": len(execs), "auditoria_de_consistencia": {"A_x_B": cons, "contexto_A_reproduz_rodada_4_3": base_a,
                                                                                                             "controles_contexto_identico_com_flag_ligada": ctrl_ctx_igual_com_flag}}
dest = AQUI / "protocolo_validacao_manifestos.json"
assert not dest.exists(), "nao sobrescrever manifesto existente"
dest.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
print("manifesto:", dest, "| execucoes:", len(execs), "| sha256:", sha(dest.read_bytes())[:16])
print(json.dumps(man["auditoria_de_consistencia"], ensure_ascii=False, indent=1))
for k, v in slots.items():
    print(k, v["tokens_contexto_estimados"], [c["chunk_id"][5:] for c in v["chunks_enviados"]], v["hash_contexto"][:10], v["hash_parametros"][:10])
