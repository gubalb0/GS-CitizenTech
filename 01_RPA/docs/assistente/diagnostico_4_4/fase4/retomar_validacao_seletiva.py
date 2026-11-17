"""Fase 4B - RETOMADA autorizada da validacao seletiva: ordens 8..21 do manifesto, em blocos de ate 3 geracoes, com descarregar/recarregar o modelo entre blocos.
Nao altera pipeline/manifesto/parametros/modelo; grava num JSONL NOVO. Para (sem repetir) em qualquer divergencia de configuracao, RAM, erro tecnico ou contexto."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import executar_validacao_seletiva as E  # noqa: E402  (reaproveita constantes, mem() e Monitor; nao executa main)

from citizentech.assistente import avaliacao_e2e as AE  # noqa: E402
from citizentech.assistente import geracao as G  # noqa: E402
from citizentech.assistente.catalogo import Catalogo  # noqa: E402
from citizentech.assistente.retriever import Indice  # noqa: E402

LMS = r"C:\Users\henry\.lmstudio\bin\lms.exe"
BLOCOS = [[8, 9, 10], [11, 12, 13], [14, 15, 16], [17, 18, 19], [20, 21]]
RAM_POS_CARGA_MB = 3000   # 3 GB = 3.000 MB (decisao do responsavel, 2026-11-16; antes 3072)


def lms(*a, timeout=300):
    return subprocess.run([LMS, *a], capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")


def config_efetiva():
    j = json.loads(lms("ps", "--json").stdout or "[]")
    return j[0] if j else None


def hashes_ok():
    for n, h in E.HASHES_CODIGO.items():
        if E.sha((Path(r"D:\Downloads\GS\RPA\citizentech\assistente") / n).read_bytes())[:16] != h:
            return False
    return E.sha((E.AQUI / "protocolo_validacao_manifestos.json").read_bytes())[:16] == E.HASH_MANIFESTO


def parar(out, feitas, motivo, extra=None):
    fim = {"concluidas_nesta_retomada": feitas, "parada": {"motivo": motivo, **(extra or {})}}
    print("PARADA", json.dumps(fim, ensure_ascii=False), flush=True)
    out.with_suffix(".resumo.json").write_text(json.dumps(fim, ensure_ascii=False, indent=1), encoding="utf-8")
    lms("unload", "qwen3-8b"); lms("server", "stop")
    sys.exit(0)


def main():
    man = json.loads((E.AQUI / "protocolo_validacao_manifestos.json").read_text(encoding="utf-8"))
    anterior = E.AQUI / "validacao_seletiva_20261116-155046.jsonl"
    feitas_ant = {json.loads(l)["ordem"] for l in anterior.open(encoding="utf-8")}
    assert feitas_ant == set(range(1, 8)), feitas_ant
    out = E.AQUI / f"validacao_seletiva_retomada_{time.strftime('%Y%m%d-%H%M%S')}.jsonl"
    assert not out.exists()
    print("saida:", out, flush=True)
    seq = {e["ordem"]: e for e in man["sequencia"]}
    corpus, val, *_ = AE.preparar()
    cat, idx = Catalogo.de_corpus(corpus), Indice.carregar(AE.IDX)
    feitas = 0
    for bi, bloco in enumerate(BLOCOS, 1):
        # --- pre-carga: modelo anterior descarregado, servidor encerrado, RAM, hashes
        lms("unload", "qwen3-8b"); lms("server", "stop"); time.sleep(4)
        if config_efetiva() is not None:
            parar(out, feitas, "modelo anterior nao foi descarregado", {"bloco": bi})
        ram0 = E.mem()
        if not hashes_ok():
            parar(out, feitas, "hash de codigo/manifesto diverge", {"bloco": bi})
        print(f"[bloco {bi}] pre-carga: {ram0}", flush=True)
        lms("server", "start"); time.sleep(3)
        lms("load", "qwen_qwen3-8b", "--identifier", "qwen3-8b", "--context-length", "8192", "-y", timeout=600); time.sleep(15)
        cfgm = config_efetiva()
        ram1 = E.mem()
        print(f"[bloco {bi}] pos-carga: {ram1} | config: {json.dumps({k: cfgm.get(k) for k in ('identifier','modelKey','contextLength','parallel','status')} if cfgm else None)} quant={(cfgm or {}).get('quantization')}", flush=True)
        ok = bool(cfgm) and cfgm.get("identifier") == "qwen3-8b" and cfgm.get("contextLength") == 8192 and cfgm.get("parallel") == 4 and (cfgm.get("quantization") or {}).get("name") == "Q4_K_M" \
            and "Qwen3-8B-Q4_K_M" in (cfgm.get("path") or "")
        if not ok:
            parar(out, feitas, "configuracao efetiva diverge do protocolo", {"bloco": bi, "config": cfgm})
        if ram1["ram_livre_mb"] < RAM_POS_CARGA_MB:
            parar(out, feitas, "RAM livre < 3 GB apos carregar o modelo", {"bloco": bi, "mem": ram1})
        if not G.ClienteLMStudio(G.ConfigGeracao()).disponivel():
            parar(out, feitas, "servidor/modelo indisponivel", {"bloco": bi})
        for ordem in bloco:
            ex = seq[ordem]; slot = man["slots"][ex["slot"]]
            s0 = E.mem()
            if s0["ram_livre_mb"] < E.LIM_RAM_MB or s0["commit_pct"] > E.LIM_COMMIT:
                parar(out, feitas, "memoria antes da geracao", {"antes_de": ex["run_id"], "mem": s0})
            cfg = G.ConfigGeracao(priorizar_atributo=bool(slot["flag_priorizar_atributo"]))
            res = idx.buscar(slot["pergunta"], k=cfg.max_chunks, modo="bm25")
            ctx = G.montar_contexto(slot["pergunta"], res, cfg)
            if E.sha(ctx.mensagens[1]["content"]) != slot["hash_contexto"] or E.sha(E.js(ctx.mensagens)) != slot["hash_mensagens"]:
                parar(out, feitas, "contexto diverge do manifesto", {"antes_de": ex["run_id"]})
            mon = E.Monitor(); mon.start()
            t0 = time.perf_counter(); inicio = time.strftime("%Y-%m-%dT%H:%M:%S")
            r = G.gerar_resposta(slot["pergunta"], res, G.ClienteLMStudio(cfg), cfg, catalogo=cat)
            dt = time.perf_counter() - t0
            mon.stop.set(); mon.join()
            d = r.para_dict(); t = d["telemetria"]
            reg = {"ordem": ex["ordem"], "run_id": ex["run_id"], "slot": ex["slot"], "repeticao": ex["repeticao"], "condicao": ex["condicao"], "papel": ex["papel"], "qid": slot["qid"],
                   "inicio": inicio, "duracao_s": round(dt, 2), "flag_priorizar_atributo": cfg.priorizar_atributo, "hash_contexto": slot["hash_contexto"], "hash_parametros": slot["hash_parametros"],
                   "chunks_enviados": [c["chunk_id"] for c in slot["chunks_enviados"]], "tokens_contexto_estimados": ctx.tokens_estimados, "bloco_de_carga": bi,
                   "config_efetiva_lm_studio": {k: cfgm.get(k) for k in ("identifier", "modelKey", "path", "contextLength", "parallel", "quantization", "status")},
                   "memoria": {"antes": s0, "pos_carga_do_bloco": ram1, "ram_livre_min_mb": mon.min_ram, "commit_max_pct": mon.max_commit, "amostras": mon.n, "depois": E.mem()}, "saida": d}
            with out.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(reg, ensure_ascii=False) + "\n"); fh.flush()
            feitas += 1
            print(f"[{ex['ordem']:02d}/21] {ex['run_id']} status={d['status']} {dt:.1f}s tokens_prompt={t.get('tokens_prompt')} ram_min={mon.min_ram}MB commit_max={mon.max_commit}% erro={t.get('erro_tecnico')}", flush=True)
            if t.get("erro_tecnico") or mon.min_ram < E.LIM_RAM_MB or mon.max_commit > E.LIM_COMMIT:
                parar(out, feitas, "erro tecnico/memoria durante a geracao", {"apos": ex["run_id"], "erro": t.get("erro_tecnico"), "ram_min": mon.min_ram, "commit_max": mon.max_commit})
            time.sleep(2)
    lms("unload", "qwen3-8b"); lms("server", "stop")
    fim = {"concluidas_nesta_retomada": feitas, "parada": None, "arquivo": str(out)}
    print("FIM", json.dumps(fim, ensure_ascii=False), flush=True)
    out.with_suffix(".resumo.json").write_text(json.dumps(fim, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
