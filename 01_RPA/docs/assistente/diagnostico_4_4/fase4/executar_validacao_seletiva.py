"""Fase 4B - EXECUTOR da validacao seletiva (21 geracoes, uma por vez). Autorizado explicitamente. Nao altera pipeline/manifesto/snapshots.
Trava: exige o hash do manifesto. Para o lote (sem repetir) se: RAM livre < 1,5 GB, memoria comprometida > 90 %, timeout/erro tecnico, divergencia de contexto vs manifesto.
Saida: validacao_seletiva_<timestamp>.jsonl (arquivo novo, append + flush por execucao)."""
import ctypes
import hashlib
import json
import sys
import threading
import time
from dataclasses import asdict
from pathlib import Path

import psutil

sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import avaliacao_e2e as AE
from citizentech.assistente import geracao as G
from citizentech.assistente.catalogo import Catalogo
from citizentech.assistente.retriever import Indice

AQUI = Path(__file__).parent
HASH_MANIFESTO = "43fb09685404714c"
HASHES_CODIGO = {"geracao.py": "46862831592d09fc", "evidencias.py": "742031bb9934a3d9", "catalogo.py": "8e44143ba1d092f5"}
LIM_RAM_MB, LIM_COMMIT = 1536, 90.0
sha = lambda b: hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()
js = lambda o: json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class MS(ctypes.Structure):
    _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong), ("tpf", ctypes.c_ulonglong),
                ("apf", ctypes.c_ulonglong), ("tv", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong), ("ae", ctypes.c_ulonglong)]


def mem():
    m = MS(); m.l = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return {"ram_livre_mb": m.ap // 2**20, "commit_pct": round(100.0 * (m.tpf - m.apf) / m.tpf, 1), "swap_usado_mb": psutil.swap_memory().used // 2**20}


class Monitor(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True); self.stop = threading.Event(); self.min_ram = 10**9; self.max_commit = 0.0; self.n = 0
    def run(self):
        while not self.stop.is_set():
            s = mem(); self.min_ram = min(self.min_ram, s["ram_livre_mb"]); self.max_commit = max(self.max_commit, s["commit_pct"]); self.n += 1
            self.stop.wait(2.0)


def main():
    man_path = AQUI / "protocolo_validacao_manifestos.json"
    assert sha(man_path.read_bytes())[:16] == HASH_MANIFESTO, "hash do manifesto diverge"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    for n, h in HASHES_CODIGO.items():
        assert sha((Path(r"D:\Downloads\GS\RPA\citizentech\assistente") / n).read_bytes())[:16] == h, f"hash de {n} diverge"
    assert len(man["slots"]) == 7 and len(man["sequencia"]) == 21 and G.ConfigGeracao().priorizar_atributo is False
    cfg_base = G.ConfigGeracao()
    cli0 = G.ClienteLMStudio(cfg_base)
    assert cli0.disponivel(), "LM Studio/modelo qwen3-8b indisponivel"
    corpus, val, *_ = AE.preparar()
    cat = Catalogo.de_corpus(corpus)
    idx = Indice.carregar(AE.IDX)
    out = AQUI / f"validacao_seletiva_{time.strftime('%Y%m%d-%H%M%S')}.jsonl"
    assert not out.exists()
    print("saida:", out, flush=True)
    feitas, parada = 0, None
    for ex in man["sequencia"]:
        slot = man["slots"][ex["slot"]]
        s0 = mem()
        if s0["ram_livre_mb"] < LIM_RAM_MB or s0["commit_pct"] > LIM_COMMIT:
            parada = {"antes_de": ex["run_id"], "motivo": "memoria", "mem": s0}; break
        cfg = G.ConfigGeracao(priorizar_atributo=bool(slot["flag_priorizar_atributo"]))
        res = idx.buscar(slot["pergunta"], k=cfg.max_chunks, modo="bm25")
        ctx = G.montar_contexto(slot["pergunta"], res, cfg)
        if sha(ctx.mensagens[1]["content"]) != slot["hash_contexto"] or sha(js(ctx.mensagens)) != slot["hash_mensagens"]:
            parada = {"antes_de": ex["run_id"], "motivo": "contexto diverge do manifesto"}; break
        mon = Monitor(); mon.start()
        t0 = time.perf_counter(); inicio = time.strftime("%Y-%m-%dT%H:%M:%S")
        r = G.gerar_resposta(slot["pergunta"], res, G.ClienteLMStudio(cfg), cfg, catalogo=cat)
        dt = time.perf_counter() - t0
        mon.stop.set(); mon.join()
        d = r.para_dict()
        reg = {"ordem": ex["ordem"], "run_id": ex["run_id"], "slot": ex["slot"], "repeticao": ex["repeticao"], "condicao": ex["condicao"], "papel": ex["papel"], "qid": slot["qid"],
               "inicio": inicio, "duracao_s": round(dt, 2), "flag_priorizar_atributo": cfg.priorizar_atributo, "hash_contexto": slot["hash_contexto"], "hash_parametros": slot["hash_parametros"],
               "chunks_enviados": [c["chunk_id"] for c in slot["chunks_enviados"]], "tokens_contexto_estimados": ctx.tokens_estimados,
               "memoria": {"antes": s0, "ram_livre_min_mb": mon.min_ram, "commit_max_pct": mon.max_commit, "amostras": mon.n, "depois": mem()}, "saida": d}
        with out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(reg, ensure_ascii=False) + "\n"); fh.flush()
        feitas += 1
        t = d["telemetria"]
        print(f"[{ex['ordem']:02d}/21] {ex['run_id']} status={d['status']} {dt:.1f}s tokens_prompt={t.get('tokens_prompt')} ram_min={mon.min_ram}MB commit_max={mon.max_commit}% erro={t.get('erro_tecnico')}", flush=True)
        if t.get("erro_tecnico") or mon.min_ram < LIM_RAM_MB or mon.max_commit > LIM_COMMIT:
            parada = {"apos": ex["run_id"], "motivo": "erro tecnico/memoria durante a geracao", "erro": t.get("erro_tecnico"), "ram_min": mon.min_ram, "commit_max": mon.max_commit}; break
        time.sleep(2)
    fim = {"concluidas": feitas, "parada": parada, "arquivo": str(out)}
    print("FIM", json.dumps(fim, ensure_ascii=False), flush=True)
    with out.with_suffix(".resumo.json").open("w", encoding="utf-8") as fh:
        json.dump(fim, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
