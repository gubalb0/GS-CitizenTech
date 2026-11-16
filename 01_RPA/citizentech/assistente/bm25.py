"""BM25 Okapi implementado com scipy.sparse (sem dependencia externa nova).

score(q, d) = sum_t idf(t) * tf(t,d) * (k1+1) / (tf(t,d) + k1 * (1 - b + b * |d| / avgdl)),
idf(t) = ln(1 + (N - df + 0.5) / (df + 0.5)).  Desempate deterministico: menor indice do documento primeiro.
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from .texto_busca import normalizar_busca


def top_k_deterministico(scores: np.ndarray, k: int, minimo_exclusivo: float | None = None) -> np.ndarray:
    """Indices dos k maiores scores, desempate pelo menor indice. Filtra score <= minimo_exclusivo se informado."""
    n = len(scores)
    if n == 0 or k <= 0:
        return np.empty(0, dtype=np.int64)
    k = min(k, n)
    cand = np.argpartition(-scores, k - 1)[:k] if k < n else np.arange(n)
    # inclui todos os empatados na fronteira para o desempate ser exato
    if k < n:
        corte = scores[cand].min()
        cand = np.nonzero(scores >= corte)[0]
    ordem = np.lexsort((cand, -scores[cand]))
    sel = cand[ordem][:k]
    if minimo_exclusivo is not None:
        sel = sel[scores[sel] > minimo_exclusivo]
    return sel


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75, radical_leve: bool = False):
        if k1 <= 0 or not 0 <= b <= 1:
            raise ValueError("parametros invalidos: k1>0 e 0<=b<=1")
        self.k1, self.b, self.radical_leve = k1, b, radical_leve
        self.vocab: dict[str, int] = {}
        self._tf: sp.csr_matrix | None = None
        self._pesos: sp.csc_matrix | None = None
        self.n_docs = 0

    def ajustar(self, textos: list[str]) -> "BM25":
        linhas, colunas, valores = [], [], []
        comprimentos = np.zeros(len(textos), dtype=np.float64)
        vocab: dict[str, int] = {}
        for i, t in enumerate(textos):
            toks = normalizar_busca(t, self.radical_leve)
            comprimentos[i] = len(toks)
            contagem: dict[int, int] = {}
            for w in toks:
                j = vocab.setdefault(w, len(vocab))
                contagem[j] = contagem.get(j, 0) + 1
            for j, c in contagem.items():
                linhas.append(i); colunas.append(j); valores.append(c)
        self.vocab = vocab
        self.n_docs = len(textos)
        self._tf = sp.csr_matrix((valores, (linhas, colunas)), shape=(self.n_docs, max(len(vocab), 1)), dtype=np.float64)
        self._comprimentos = comprimentos
        self._calcular_pesos()
        return self

    def _calcular_pesos(self) -> None:
        tf = self._tf.tocoo()
        n = self.n_docs
        df = np.bincount(tf.col, minlength=self._tf.shape[1]).astype(np.float64)
        idf = np.log(1.0 + (n - df + 0.5) / (df + 0.5))
        avgdl = self._comprimentos.mean() if n else 1.0
        norm = self.k1 * (1 - self.b + self.b * self._comprimentos[tf.row] / max(avgdl, 1e-9))
        w = idf[tf.col] * tf.data * (self.k1 + 1) / (tf.data + norm)
        self._pesos = sp.csc_matrix((w, (tf.row, tf.col)), shape=self._tf.shape)

    def reponderar(self, k1: float, b: float) -> None:
        """Recalcula os pesos com novos parametros sem reconstruir o vocabulario (usado na analise de sensibilidade)."""
        self.k1, self.b = k1, b
        self._calcular_pesos()

    def pontuar(self, consulta: str) -> np.ndarray:
        if self._pesos is None:
            raise RuntimeError("indice BM25 nao ajustado")
        ids = sorted({self.vocab[w] for w in normalizar_busca(consulta, self.radical_leve) if w in self.vocab})
        if not ids:
            return np.zeros(self.n_docs)
        return np.asarray(self._pesos[:, ids].sum(axis=1)).ravel()

    def buscar(self, consulta: str, k: int) -> tuple[np.ndarray, np.ndarray]:
        s = self.pontuar(consulta)
        idx = top_k_deterministico(s, k, minimo_exclusivo=0.0)
        return idx, s[idx]
