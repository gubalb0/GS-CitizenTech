"""Pre-processamento de texto (NLP): normalizacao e mascaramento de dados pessoais."""
import re
import unicodedata

_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_TEL = re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b")


def normalizar(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def mascarar_pii(t: str) -> tuple[str, bool]:
    """Remove CPF, e-mail e telefone do texto antes de qualquer saida/log (minimizacao)."""
    original = t
    t = _CPF.sub("[CPF]", t)
    t = _EMAIL.sub("[EMAIL]", t)
    t = _TEL.sub("[TEL]", t)
    return t, t != original
