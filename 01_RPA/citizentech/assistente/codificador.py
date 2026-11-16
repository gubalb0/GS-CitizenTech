"""Codificadores de texto -> vetor (busca vetorial). Interface comum para permitir trocar o modelo e testar sem baixa-lo.

Codificador real: `intfloat/multilingual-e5-small` (MIT; 12 camadas, 384 dimensoes, entrada maxima de 512 tokens do
tokenizador XLM-R/SentencePiece; exige prefixos "query: " e "passage: "). Roda em CPU com sentence-transformers.
Chunks maiores que o limite sao divididos em JANELAS (com o cabecalho contextual repetido); o chunk e pontuado pelo MAXIMO
entre as suas janelas. Nenhum texto e descartado por truncamento.
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Protocol

import numpy as np

from .texto_busca import normalizar_busca

MODELO_E5 = "intfloat/multilingual-e5-small"
HF_HOME_PADRAO = r"D:\hf_cache"


class Codificador(Protocol):
    nome: str
    dimensao: int

    def janelas(self, chunk: dict) -> list[str]: ...
    def codificar_janelas(self, textos: list[str]) -> np.ndarray: ...
    def codificar_consultas(self, consultas: list[str]) -> np.ndarray: ...


def _normalizar_linhas(m: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(m, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return (m / n).astype(np.float32)


class CodificadorE5:
    nome = MODELO_E5
    dimensao = 384

    def __init__(self, limite_tokens: int = 512, sobreposicao_janela: int = 64, batch: int = 16, dispositivo: str = "cpu",
                 hf_home: str | None = HF_HOME_PADRAO, revisao: str | None = None):
        if hf_home:
            os.environ.setdefault("HF_HOME", hf_home)
        from sentence_transformers import SentenceTransformer  # import tardio: pesado
        self.modelo = SentenceTransformer(MODELO_E5, device=dispositivo, revision=revisao)
        self.tokenizador = self.modelo.tokenizer
        self.limite = limite_tokens
        self.modelo.max_seq_length = limite_tokens
        self.sobreposicao = sobreposicao_janela
        self.batch = batch

    def _n_tokens(self, texto: str) -> int:
        return len(self.tokenizador(texto, add_special_tokens=False)["input_ids"])

    def janelas(self, chunk: dict) -> list[str]:
        texto = chunk["texto"]
        ti = chunk["texto_indexacao"]
        cab = ti[: len(ti) - len(texto)]
        completo = "passage: " + ti
        orcamento = self.limite - 2 - self._n_tokens("passage: " + cab)
        if orcamento < 64:
            raise ValueError("cabecalho contextual consome quase todo o limite de tokens")
        enc = self.tokenizador(texto, add_special_tokens=False, return_offsets_mapping=True)
        offs = enc["offset_mapping"]
        if len(offs) <= orcamento:
            return [completo]
        passo = orcamento - self.sobreposicao
        out, i = [], 0
        while True:
            j = min(i + orcamento, len(offs))
            out.append("passage: " + cab + texto[offs[i][0]:offs[j - 1][1]])
            if j == len(offs):
                break
            i += passo
        return out

    def codificar_janelas(self, textos: list[str]) -> np.ndarray:
        return self.modelo.encode(textos, batch_size=self.batch, normalize_embeddings=True, show_progress_bar=False,
                                  convert_to_numpy=True).astype(np.float32)

    def codificar_consultas(self, consultas: list[str]) -> np.ndarray:
        return self.modelo.encode(["query: " + c for c in consultas], batch_size=self.batch, normalize_embeddings=True,
                                  show_progress_bar=False, convert_to_numpy=True).astype(np.float32)


class CodificadorFalso:
    """Codificador deterministico para testes: saco de palavras com hashing (sem modelo, sem rede). Uma janela por chunk
    (ou varias se `janela_palavras` for informado, para testar o caminho de multiplas janelas)."""
    nome = "falso-hash-bow"

    def __init__(self, dimensao: int = 256, janela_palavras: int | None = None):
        self.dimensao = dimensao
        self.janela_palavras = janela_palavras

    def _vec(self, texto: str) -> np.ndarray:
        v = np.zeros(self.dimensao, dtype=np.float32)
        for w in normalizar_busca(texto):
            h = int(hashlib.md5(w.encode()).hexdigest()[:8], 16)
            v[h % self.dimensao] += 1.0
        return v

    def janelas(self, chunk: dict) -> list[str]:
        if not self.janela_palavras:
            return [chunk["texto_indexacao"]]
        pal = chunk["texto"].split()
        return [" ".join(pal[i:i + self.janela_palavras]) for i in range(0, max(len(pal), 1), self.janela_palavras)]

    def codificar_janelas(self, textos: list[str]) -> np.ndarray:
        return _normalizar_linhas(np.stack([self._vec(t) for t in textos])) if textos else np.zeros((0, self.dimensao), np.float32)

    def codificar_consultas(self, consultas: list[str]) -> np.ndarray:
        return self.codificar_janelas(consultas)
