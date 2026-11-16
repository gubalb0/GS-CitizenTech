"""IA: classificador de texto (TF-IDF + Regressao Logistica) com caminho alternativo por palavras-chave."""
import csv
import logging
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from . import config
from .texto import normalizar

log = logging.getLogger("citizentech")

# Fallback seguro se o modelo nao puder ser carregado/treinado (confianca baixa => revisao humana)
PALAVRAS = {
    "agendamento_consulta": ["consulta", "marcar", "agendar", "agendamento", "remarcar"],
    "vacinacao": ["vacina", "vacinacao", "imunizar", "caderneta", "dose"],
    "medicamentos": ["remedio", "medicamento", "farmacia", "receita", "insulina"],
    "exames_resultados": ["exame", "resultado", "laudo", "ultrassom", "encaminhamento"],
    "visita_domiciliar": ["acamado", "acamada", "visita", "domicilio", "agente comunitario", "em casa"],
    "reclamacao_atendimento": ["reclamo", "reclamacao", "demora", "mal atendido", "grosseria", "fila"],
    "informacoes_gerais": ["horario", "documentos", "cartao sus", "informacao", "funciona"],
    "sintomas_urgentes": ["dor no peito", "falta de ar", "desmaio", "convulsao", "sangramento", "febre alta"],
}


def _ler(caminho: Path):
    with caminho.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return [normalizar(r["texto"]) for r in rows], [r["categoria"] for r in rows]


def treinar(arq_treino: Path = config.ARQ_TREINO, salvar_em: Path | None = config.ARQ_MODELO) -> Pipeline:
    X, y = _ler(arq_treino)
    modelo = Pipeline([
        # palavras + caracteres (3-5): robusto a erros de digitacao e variacoes morfologicas
        ("tfidf", FeatureUnion([
            ("palavras", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
            ("caracteres", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)),
        ])),
        ("clf", LogisticRegression(max_iter=1000, C=10)),
    ])
    modelo.fit(X, y)
    if salvar_em:
        salvar_em.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(modelo, salvar_em)
    log.info("Modelo treinado com %d exemplos sinteticos", len(X))
    return modelo


def carregar_modelo():
    try:
        if config.ARQ_MODELO.exists() and config.ARQ_MODELO.stat().st_mtime >= config.ARQ_TREINO.stat().st_mtime:
            return joblib.load(config.ARQ_MODELO)
        return treinar()
    except Exception as e:
        log.error("Modelo de IA indisponivel (%s: %s). Usando palavras-chave.", type(e).__name__, e)
        return None


def classificar(modelo, texto: str) -> tuple[str, float, str]:
    """Retorna (categoria, confianca, metodo). Nunca levanta excecao."""
    t = normalizar(texto)
    if modelo is not None:
        try:
            probs = modelo.predict_proba([t])[0]
            i = int(probs.argmax())
            return str(modelo.classes_[i]), float(probs[i]), "ml"
        except Exception as e:
            log.error("Falha na predicao ML (%s). Fallback palavras-chave.", e)
    pontos = {c: sum(p in t for p in ps) for c, ps in PALAVRAS.items()}
    cat, n = max(pontos.items(), key=lambda kv: kv[1])
    if n == 0:
        return "indefinida", 0.0, "palavras_chave"
    return cat, min(0.4, 0.2 * n), "palavras_chave"  # teto < limiar => sempre revisao humana
