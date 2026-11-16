"""
Base de conhecimento do tema (RAG) — Direitos do Consumidor.

Usamos recuperação por TF-IDF (scikit-learn) sobre os trechos do arquivo
data/knowledge/consumidor.md. Justificativa da escolha (relatório):
- Roda 100% em CPU, sem baixar modelos de embedding pesados.
- Latência muito baixa, adequada à base pequena e curada do CDC.
- Fornece ao LLM informação confiável e citável (artigos do CDC), reduzindo alucinação.

Se nenhum trecho ultrapassa o score mínimo, retornamos vazio — sinal para o LLM
dizer que não sabe, em vez de inventar.
"""
import re

import config


class BaseConhecimento:
    def __init__(self, caminho=None, top_k=None, min_score=None):
        self.caminho = caminho or (config.KNOWLEDGE_DIR / "consumidor.md")
        self.top_k = top_k or config.RAG_TOP_K
        self.min_score = min_score if min_score is not None else config.RAG_MIN_SCORE
        self._chunks = self._carregar_chunks()
        self._vectorizer = None
        self._matriz = None
        self._indexar()

    def _carregar_chunks(self):
        texto = self.caminho.read_text(encoding="utf-8")
        # Quebra por seções "## titulo"; cada seção vira um trecho recuperável.
        partes = re.split(r"\n(?=##\s)", texto)
        chunks = [p.strip() for p in partes if p.strip() and p.strip().startswith("##")]
        return chunks

    def _indexar(self):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
        self._matriz = self._vectorizer.fit_transform(self._chunks)

    def recuperar(self, pergunta):
        """Retorna lista de (trecho, score) mais relevantes acima do score mínimo."""
        from sklearn.metrics.pairwise import cosine_similarity

        q = self._vectorizer.transform([pergunta])
        scores = cosine_similarity(q, self._matriz)[0]
        ranking = sorted(
            zip(self._chunks, scores), key=lambda x: x[1], reverse=True
        )[: self.top_k]
        return [(c, float(s)) for c, s in ranking if s >= self.min_score]

    def contexto_para_prompt(self, pergunta):
        """Monta o bloco de contexto (texto) que será injetado no prompt do LLM."""
        trechos = self.recuperar(pergunta)
        if not trechos:
            return ""
        blocos = [t for t, _ in trechos]
        return "\n\n".join(blocos)
