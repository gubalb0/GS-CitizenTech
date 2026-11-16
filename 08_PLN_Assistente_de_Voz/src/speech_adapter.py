"""
Adaptação do texto para fala (antes do TTS).

Ajusta a resposta do LLM para soar natural quando falada:
- remove markdown (**, ##, listas), emojis e links;
- expande siglas e símbolos (CDC, art., R$, %, nº);
- escreve números e datas de forma pronunciável (49 -> "quarenta e nove");
- quebra em frases curtas.
"""
import re

try:
    from num2words import num2words
except ImportError:  # fallback: mantém o número se a lib não estiver instalada
    num2words = None

SIGLAS = {
    "CDC": "Código de Defesa do Consumidor",
    "SPC": "S P C",
    "Serasa": "Serasa",
    "Procon": "Procon",
    "art.": "artigo",
    "Art.": "artigo",
    "arts.": "artigos",
    "nº": "número",
    "n°": "número",
    "§": "parágrafo",
    "UBS": "unidade básica de saúde",
}


def _remover_markdown(texto):
    texto = re.sub(r"```.*?```", " ", texto, flags=re.DOTALL)  # blocos de código
    texto = re.sub(r"`([^`]*)`", r"\1", texto)                 # código inline
    texto = re.sub(r"\*\*|__|\*|_|#+|>", "", texto)            # ênfase/títulos
    texto = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", texto)      # links [txt](url)
    texto = re.sub(r"^\s*[-•]\s*", "", texto, flags=re.MULTILINE)  # marcadores
    texto = re.sub(r"^\s*\d+\.\s*", "", texto, flags=re.MULTILINE)  # listas numeradas
    return texto


def _remover_emojis(texto):
    emoji = re.compile(
        "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]",
        flags=re.UNICODE,
    )
    return emoji.sub("", texto)


def _numero_por_extenso(match):
    if num2words is None:
        return match.group(0)
    return num2words(int(match.group(0)), lang="pt")


def _expandir(texto):
    for sigla, extenso in SIGLAS.items():
        texto = texto.replace(sigla, extenso)
    # "R$ 100" / "R$100,50" -> "100 reais" (número antes da palavra, como se fala)
    texto = re.sub(r"R\$\s?([\d\.,]+)", r"\1 reais", texto)
    texto = texto.replace("%", " por cento")
    # datas dd/mm/aaaa -> "dd de mês de aaaa" seria ideal; simplificamos trocando / por " "
    texto = re.sub(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", r"\1 \2 \3", texto)
    # números soltos por extenso (evita quebrar grandes sequências)
    texto = re.sub(r"\b\d{1,4}\b", _numero_por_extenso, texto)
    return texto


def adaptar(texto):
    """Pipeline completo de adaptação para fala."""
    texto = _remover_markdown(texto)
    texto = _remover_emojis(texto)
    texto = _expandir(texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{2,}", ". ", texto).replace("\n", ". ")
    texto = re.sub(r"\s+([.,!?])", r"\1", texto)
    texto = re.sub(r"\.{2,}", ".", texto)
    return texto.strip()
