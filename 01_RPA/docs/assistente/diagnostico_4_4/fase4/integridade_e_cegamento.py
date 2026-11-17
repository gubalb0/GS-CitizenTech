"""Fase 4B - verificacao de integridade das 21 execucoes + geracao do arquivo CEGO (saidas embaralhadas, sem condicao/slot/repeticao). OFFLINE (sem modelo)."""
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).parent
sha = lambda b: hashlib.sha256(b).hexdigest()
A1 = AQUI / "validacao_seletiva_20261116-155046.jsonl"
A2 = AQUI / "validacao_seletiva_retomada_20261116-161042.jsonl"
man = json.loads((AQUI / "protocolo_validacao_manifestos.json").read_text(encoding="utf-8"))
regs = [json.loads(l) for f in (A1, A2) for l in f.open(encoding="utf-8")]
seq = {e["run_id"]: e for e in man["sequencia"]}
rel = {"n_registros": len(regs), "run_ids_unicos": len({r["run_id"] for r in regs}), "run_ids_esperados": len(seq),
       "lacunas": sorted(set(seq) - {r["run_id"] for r in regs}), "extras": sorted({r["run_id"] for r in regs} - set(seq)),
       "ordens": sorted(r["ordem"] for r in regs) == list(range(1, 22)),
       "por_slot": dict(Counter(r["slot"] for r in regs)), "repeticoes_por_slot_3": all(v == 3 for v in Counter(r["slot"] for r in regs).values()) and len(Counter(r["slot"] for r in regs)) == 7}
bad = []
for r in regs:
    s = man["slots"][r["slot"]]; t = r["saida"]["telemetria"]
    if r["hash_contexto"] != s["hash_contexto"] or r["hash_parametros"] != s["hash_parametros"] or r["chunks_enviados"] != [c["chunk_id"] for c in s["chunks_enviados"]]: bad.append((r["run_id"], "hash/chunks"))
    if r["flag_priorizar_atributo"] != s["flag_priorizar_atributo"] or r["condicao"] != seq[r["run_id"]]["condicao"]: bad.append((r["run_id"], "flag/condicao"))
    if t.get("erro_tecnico") or not t.get("chamou_modelo") or t.get("temperatura") != 0.3 or t.get("modelo") != "qwen3-8b": bad.append((r["run_id"], "telemetria"))
    if r["papel"] == "controle" and r["flag_priorizar_atributo"]: bad.append((r["run_id"], "controle com flag"))
rel["divergencias"] = bad
rel["tentativas>1"] = [r["run_id"] for r in regs if r["saida"]["telemetria"].get("tentativas", 1) > 1]
rel["ram_livre_min_mb_global"] = min(r["memoria"]["ram_livre_min_mb"] for r in regs); rel["commit_max_pct_global"] = max(r["memoria"]["commit_max_pct"] for r in regs)
rel["duracao_total_s"] = round(sum(r["duracao_s"] for r in regs), 1)
rel["tokens_prompt_por_slot"] = {s: sorted({r["saida"]["telemetria"]["tokens_prompt"] for r in regs if r["slot"] == s}) for s in man["slots"]}
rel["sha256_arquivos"] = {A1.name: sha(A1.read_bytes())[:16], A2.name: sha(A2.read_bytes())[:16]}
(AQUI / "validacao_seletiva_integridade.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(rel, ensure_ascii=False, indent=1))

# ---- arquivo cego
rng = random.Random(20261116)
ordem = list(range(len(regs))); rng.shuffle(ordem)
cego, mapa = [], {}
for k, i in enumerate(ordem, 1):
    r = regs[i]; d = r["saida"]; t = d["telemetria"]
    try:
        bruto = json.loads(t["saida_bruta"])
    except Exception:
        bruto = {"_erro": "saida_bruta nao e JSON valido", "texto": t["saida_bruta"]}
    cod = f"S{k:02d}"
    mapa[cod] = {"run_id": r["run_id"], "slot": r["slot"], "condicao": r["condicao"], "qid": r["qid"], "repeticao": r["repeticao"]}
    cego.append({"codigo": cod, "pergunta": r["saida"]["pergunta"], "saida_bruta_modelo": bruto,
                 "pipeline": {"status": d["status"], "resposta_final": d["resposta"], "problemas": (d["verificacao"] or {}).get("problemas")}})
(AQUI / "validacao_seletiva_CEGO.json").write_text(json.dumps(cego, ensure_ascii=False, indent=1), encoding="utf-8")
(AQUI / "validacao_seletiva_MAPA_nao_abrir_antes_da_avaliacao.json").write_text(json.dumps(mapa, ensure_ascii=False, indent=1), encoding="utf-8")
print("cego:", len(cego))
