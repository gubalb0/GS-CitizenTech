"""Constroi e salva os indices (BM25 + vetorial) das configuracoes de chunking.
Uso: python -m citizentech.assistente.construir_indice est500o50 est300o30
Saida: data_assistente/indices/<config>/ ; checkpoints de embeddings em data_assistente/indices/_ckpt/ (retomavel)."""
import json
import sys
import time

import psutil

from . import dados as D
from .chunking import ConfigChunk
from .codificador import CodificadorE5
from .retriever import Indice

CONFIGS = {"est500o50": ConfigChunk("estrutura", 500, 50), "est300o30": ConfigChunk("estrutura", 300, 30),
           "est700o70": ConfigChunk("estrutura", 700, 70), "tam500o50": ConfigChunk("tamanho", 500, 50)}
RAIZ_IDX = D.RAIZ / "data_assistente" / "indices"


def main(nomes: list[str]) -> None:
    if not all(D.verificar_integridade().values()):
        raise SystemExit("integridade dos dados falhou")
    corpus = D.carregar_corpus()
    cod = CodificadorE5()
    for nome in nomes:
        cfg = CONFIGS[nome]
        t0 = time.perf_counter()
        ultimo = [0.0]

        def prog(feito, total, dt):
            if time.perf_counter() - ultimo[0] > 30 or feito == total:
                ultimo[0] = time.perf_counter()
                print(f"[{nome}] janelas {feito}/{total} ({100 * feito / total:.1f}%) {dt:.0f}s", flush=True)

        idx = Indice.construir(corpus, cfg, cod, dedup=True, checkpoint=RAIZ_IDX / "_ckpt", progresso=prog)
        pasta = RAIZ_IDX / nome
        idx.salvar(pasta)
        idx.manifesto["tempo_total_construcao_s"] = round(time.perf_counter() - t0, 1)
        idx.manifesto["rss_mb_apos_construcao"] = int(psutil.Process().memory_info().rss / 1e6)
        idx.manifesto["tamanho_em_disco_bytes"] = idx.tamanho_em_disco(pasta)
        (pasta / "manifesto.json").write_text(json.dumps(idx.manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{nome}] PRONTO:", json.dumps(idx.manifesto, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or ["est500o50", "est300o30"])
