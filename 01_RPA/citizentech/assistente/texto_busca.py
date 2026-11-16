"""Normalizacao textual para a busca lexical (BM25).

Decisao: minusculas, sem acentos (NFKD), tokens alfanumericos `\\w+`; numeros ("165/2021", "R$ 69.281,56") viram tokens
numericos separados. Sem lista de stopwords (o IDF do BM25 ja as penaliza). Radical leve opcional (`radical_leve=True`):
remove "s" final de palavras com mais de 4 letras (plural simples). Nao ha stemmer completo para evitar dependencia externa.
"""
from __future__ import annotations

import re
import unicodedata

_TOKEN = re.compile(r"\w+", re.UNICODE)


def normalizar_busca(texto: str | None, radical_leve: bool = False) -> list[str]:
    if not texto:
        return []
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    toks = _TOKEN.findall(t)
    if radical_leve:
        toks = [w[:-1] if len(w) > 4 and w.endswith("s") and not w.isdigit() else w for w in toks]
    return toks
