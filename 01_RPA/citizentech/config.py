"""Configuracao via variaveis de ambiente (.env opcional, sem dependencias externas)."""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _carregar_dotenv(caminho: Path) -> None:
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        k, v = linha.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_carregar_dotenv(RAIZ / ".env")


def _float(nome, padrao):
    try:
        return float(os.environ.get(nome, padrao))
    except ValueError:
        return float(padrao)


CEP_API_URL = os.environ.get("CEP_API_URL", "https://viacep.com.br/ws/{cep}/json/")
CEP_TIMEOUT_S = _float("CEP_TIMEOUT_S", 4)
CEP_MAX_RETRIES = int(_float("CEP_MAX_RETRIES", 3))
CEP_BACKOFF_S = _float("CEP_BACKOFF_S", 1.0)
CONFIANCA_MINIMA = _float("CONFIANCA_MINIMA", 0.45)

DIR_INBOX = RAIZ / "data" / "inbox"
DIR_SAIDA = RAIZ / "saida"
DIR_LOGS = RAIZ / "logs"
ARQ_TREINO = RAIZ / "data" / "treino.csv"
ARQ_TESTE = RAIZ / "data" / "teste_rotulado.csv"
ARQ_TESTE_CEGO = RAIZ / "data" / "teste_cego.csv"
ARQ_MODELO = RAIZ / "data" / "modelo" / "classificador.joblib"
ARQ_ESTADO = RAIZ / "data" / "estado.db"
