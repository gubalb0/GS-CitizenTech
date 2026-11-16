"""Carga dos arquivos Parquet originais do DODF Public Health QA (somente leitura) e utilitarios de texto."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DIR_ORIGINAL = RAIZ / "data_assistente" / "dodf_original"
ARQ_CORPUS = DIR_ORIGINAL / "corpus-00000-of-00001.parquet"
ARQ_VALIDACAO = DIR_ORIGINAL / "validation-00000-of-00001.parquet"
# O conjunto de TESTE (350) nao e carregado por este modulo de proposito: reservado para a avaliacao final.

CAMPOS_CORPUS = ["id", "edicao", "data_edicao", "referencia", "secao", "tipo_documento", "numero_documento",
                 "texto_completo", "data", "topicos", "localidades", "tipo_unidade", "programas"]


def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def verificar_integridade(manifesto: Path = DIR_ORIGINAL / "MANIFESTO.json") -> dict[str, bool]:
    """Confere o SHA-256 de cada arquivo original contra o manifesto."""
    m = json.loads(manifesto.read_text(encoding="utf-8"))
    return {a["arquivo"]: sha256_arquivo(DIR_ORIGINAL / a["arquivo"]) == a["sha256"] for a in m["arquivos"]}


def carregar_corpus() -> list[dict]:
    import pandas as pd
    df = pd.read_parquet(ARQ_CORPUS)
    regs = df.to_dict("records")
    for r in regs:
        for k in ("topicos", "localidades", "tipo_unidade", "programas"):
            r[k] = [str(x) for x in (r[k] if r[k] is not None else [])]
        r["id"] = int(r["id"])
        r["edicao"] = int(r["edicao"])
    return regs


def carregar_validacao() -> list[dict]:
    import pandas as pd
    regs = pd.read_parquet(ARQ_VALIDACAO).to_dict("records")
    for i, r in enumerate(regs):
        r["qid"] = f"val-{i:03d}"  # id estavel = posicao no arquivo original
    return regs


def norm_espacos(t: str | None) -> str:
    """Normalizacao minima: NFC e espacos/quebras colapsados. NAO remove acentos nem muda caixa."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", t or "")).strip()


def norm_forte(t: str | None) -> str:
    """Sem acentos, minusculas, espacos colapsados (para o segundo nivel de comparacao textual)."""
    t = unicodedata.normalize("NFKD", (t or "").lower())
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c))).strip()
