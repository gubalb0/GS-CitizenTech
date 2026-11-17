"""Avaliacao END-TO-END DIAGNOSTICA (Etapa 4.1): retriever congelado (est300o30, BM25, top-5) -> gerador, nas 150 perguntas de validacao.

ATENCAO: as 150 perguntas ja foram usadas no desenvolvimento do retriever. Esta avaliacao e diagnostica (separa falha de
recuperacao de falha de geracao); NAO e uma medida independente de generalizacao. O conjunto de teste (350) nao e usado.

Uma UNICA rodada identificada (run_id), sem retomar nem misturar execucoes. Se o servidor cair (3 erros tecnicos seguidos), a
rodada e invalidada e interrompida. Uso: python -m citizentech.assistente.avaliacao_e2e
Saida: data_assistente/derivados/geracao_e2e_41_<run_id>.jsonl e .meta.json
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from . import associacao as A
from . import dados as D
from . import geracao as G
from .avaliar_chunking import _sem_esp, valores_chave
from .catalogo import Catalogo
from .dedup import agrupar_duplicatas
from .geracao import ClienteLMStudio, ConfigGeracao, gerar_resposta
from .retriever import Indice

SAIDA = D.RAIZ / "data_assistente" / "derivados"
IDX = D.RAIZ / "data_assistente" / "indices" / "est300o30"
NAO_UNIVOCAS = {"val-005", "val-018", "val-023", "val-120", "val-122", "val-146"}
LIMITACAO = re.compile(r"resposta parcial|parcial|apenas|somente|n[aã]o (?:h[aá]|consta|constam|foram|foi)|outras publica|limit|insuficien|n[aã]o foi poss", re.I)


def preparar():
    corpus, val = D.carregar_corpus(), D.carregar_validacao()
    assoc = A.associar_todas(corpus, val)
    dup = agrupar_duplicatas(corpus)
    esperados = []
    for a in assoc:
        gs = []
        for b in a["blocos"]:
            g = {dup.canonico_de[i] for i in b["doc_ids"]}
            if g and g not in gs:
                gs.append(g)
        esperados.append(gs)
    docs = {d["id"]: d for d in corpus}
    return corpus, val, assoc, dup, esperados, docs


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def metadados_rodada(run_id: str, cfg: ConfigGeracao, cliente: ClienteLMStudio) -> dict:
    pkg = Path(__file__).parent
    try:
        import requests
        modelos = [m["id"] for m in requests.get(cfg.url.replace("/chat/completions", "/models"), timeout=5).json().get("data", [])]
    except Exception:
        modelos = []
    return {"run_id": run_id, "etapa": "4.3", "inicio": datetime.now().isoformat(timespec="seconds"), "versao_prompt": G.VERSAO_PROMPT, "versao_politica": G.VERSAO_POLITICA,
            "modelo": "Qwen3-8B Q4_K_M (bartowski/Qwen_Qwen3-8B-GGUF)", "modelos_carregados": modelos,
            "runtime": "LM Studio 0.4.28, llama.cpp Vulkan 2.73.0, RX 6750 XT", "parallel_lmstudio": 1, "contexto_lmstudio": 8192,
            "parametros_geracao": asdict(cfg), "retriever": {"config": "est300o30", "modo": "bm25", "k": cfg.max_chunks, "congelado": True},
            "sha256_16": {"geracao.py": _sha(pkg / "geracao.py"), "evidencias.py": _sha(pkg / "evidencias.py"), "avaliacao_e2e.py": _sha(Path(__file__))},
            "conjunto": "validacao (150 perguntas); o teste de 350 NAO foi usado", "diagnostica": True}


def main(limite: int | None = None) -> Path:
    corpus, val, assoc, dup, esperados, docs = preparar()
    idx = Indice.carregar(IDX)
    catalogo = Catalogo.de_corpus(corpus)          # Etapa 4.2: teste de identificabilidade da publicacao (somente leitura do corpus)
    cfg = ConfigGeracao()
    cli = ClienteLMStudio(cfg)
    if not cli.disponivel():
        raise SystemExit("LM Studio indisponivel ou modelo nao carregado: rodada nao iniciada")
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    arq = SAIDA / f"geracao_e2e_41_{run_id}.jsonl"      # (prefixo 41 mantido por compatibilidade; a etapa esta no .meta.json)
    meta = metadados_rodada(run_id, cfg, cli)
    meta["catalogo_identificabilidade"] = {"docs_canonicos": len(catalogo), "janela_proximidade_chars": Catalogo.JANELA, "regra": "4.3 (4.2 + relevancia por janela com cobertura parcial)",
                                           "comparacao_com": "20261114-014826 (Etapa 4.2); mesmo modelo, runtime, parametros, retriever, indices e orcamento de contexto"}
    (SAIDA / f"geracao_e2e_41_{run_id}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    seguidos = 0
    with arq.open("w", encoding="utf-8") as fh:
        for q, a, esp in list(zip(val, assoc, esperados))[:limite]:
            t0 = time.perf_counter()
            res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25")
            t_ret = time.perf_counter() - t0
            ctx_docs = {r.doc_id for r in res}
            vals = []
            if not a["multi"]:
                vals = valores_chave(q["resposta"], docs[a["blocos"][0]["doc_ids"][0]]["texto_completo"])
            t1 = time.perf_counter()
            r = gerar_resposta(q["pergunta"], res, cli, cfg, catalogo=catalogo).para_dict()
            dt = time.perf_counter() - t1
            tel = r["telemetria"]
            n_env = tel.get("chunks_enviados", 0)
            enviados = [x.doc_id for x in res[:n_env]]
            ctx_txt = _sem_esp(" ".join(x.texto for x in res[:n_env]))
            achados_env = sum(1 for g in esp if g & set(enviados))
            sem = _sem_esp(r["resposta"] or "")
            fontes_docs = {f["doc_id"] for f in r["fontes"]}
            o = {"run_id": run_id, "qid": q["qid"], "pergunta": q["pergunta"], "multi": a["multi"], "nao_univoca": q["qid"] in NAO_UNIVOCAS,
                 "n_esperadas": len(esp), "recuperou_fonte_correta_top5": any(g & ctx_docs for g in esp),
                 "grupo": "A" if achados_env >= 1 else "B",       # A: a fonte correta estava entre os chunks ENVIADOS ao gerador
                 "n_esperadas_enviadas": achados_env, "enviou_todas_as_esperadas": achados_env == len(esp), "valores_chave": vals,
                 "contexto_enviado_tem_todos_os_valores": bool(vals) and all(_sem_esp(v) in ctx_txt for v in vals),
                 "cita_fonte_correta": any(g & fontes_docs for g in esp), "cita_so_fontes_corretas": bool(fontes_docs) and all(any(d in g for g in esp) for d in fontes_docs),
                 "declara_limitacao_heuristica": bool(LIMITACAO.search((r["resposta"] or "") + " " + (r["justificativa"] or ""))),
                 "resposta_referencia": q["resposta"], "erro_tecnico": tel.get("erro_tecnico"),
                 "fontes_recuperadas": [{"posicao": x.posicao, "chunk_id": x.chunk_id, "doc_id": x.doc_id, "score": round(x.score, 3), "enviado": x.posicao <= n_env,
                                         "tipo_documento": x.metadados.get("tipo_documento"), "referencia": x.metadados.get("referencia"),
                                         "data_edicao": x.metadados.get("data_edicao"), "edicao": x.metadados.get("edicao"), "secao": x.metadados.get("secao"),
                                         "ids_equivalentes": x.ids_equivalentes, "trecho_inicial": x.texto[:300]} for x in res],
                 "tempo_recuperacao_s": round(t_ret, 4), "tempo_geracao_s": round(dt, 2), "saida": r}
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"{q['qid']} grupo={o['grupo']} status={r['status']:<14} {dt:.1f}s erro={tel.get('erro_tecnico')} tokens_prompt={tel.get('tokens_prompt')}", flush=True)
            seguidos = seguidos + 1 if tel.get("erro_tecnico") in ("servidor_indisponivel", "timeout", "resposta_invalida_do_servidor") else 0
            if seguidos >= 3:
                print("RODADA INVALIDADA: 3 erros tecnicos seguidos de servidor", flush=True)
                (SAIDA / f"geracao_e2e_41_{run_id}.INVALIDA").write_text("servidor indisponivel durante a rodada", encoding="utf-8")
                raise SystemExit(2)
    (SAIDA / f"geracao_e2e_41_{run_id}.meta.json").write_text(
        json.dumps({**json.loads((SAIDA / f"geracao_e2e_41_{run_id}.meta.json").read_text(encoding="utf-8")), "fim": datetime.now().isoformat(timespec="seconds"), "completa": True}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return arq


if __name__ == "__main__":
    main()
