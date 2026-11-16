"""Chunking de publicacoes do DODF: por TAMANHO (janela de tokens) e por ESTRUTURA documental (+ tamanho).

Observacoes sobre os dados (medidas no corpus completo): os textos NAO tem quebras de linha; a estrutura precisa ser
inferida por marcadores textuais (Art., §, Considerando, Clausula, incisos, itens "1)", ";" e fim de frase).

Unidade de tamanho: "token de superficie" = `\\w+|[^\\w\\s]` (palavra ou pontuacao). E deterministico e independente
de modelo; NAO e o token do Qwen3 nem do modelo de embeddings (ver relatorio: razao de calibracao).

IDs estaveis: documento `dodf-<id>`; chunk `<doc_id>:<config>:<ordem 4 digitos>`.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)

METADADOS = ("edicao", "data_edicao", "secao", "referencia", "tipo_documento", "numero_documento", "data",
             "topicos", "localidades", "tipo_unidade", "programas")

# Inicio de unidade documental (so vale apos fim de frase/item ou inicio do texto)
_INICIO_FORTE = (r"(?:Art\.?\s?\d+|§\s?\d+|Par[aá]grafo\s+[uú]nico|PAR[AÁ]GRAFO|CONSIDERANDO|Considerando|CL[AÁ]USULA|Cl[aá]usula|"
                 r"CAP[IÍ]TULO|Cap[ií]tulo|SE[CÇ][AÃ]O\s+[IVX]+|ANEXO|Anexo|T[IÍ]TULO\s+[IVX]+|Processo:|PARTES:|OBJETO:|"
                 r"\d{1,3}\)\s|\d{1,3}\.\d{0,2}\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ]|[IVXLC]{1,6}\s?[-–]\s|[a-z]\)\s)")
_FORTE = re.compile(r"(?<=[.;:])\s+(?=" + _INICIO_FORTE + ")")
_FRASE = re.compile(r"(?<=[.;?!])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9“\"(])")
_ABREV = {"art", "arts", "n", "nº", "no", "dr", "dra", "sr", "sra", "ltda", "inc", "s", "a", "p", "pp", "av", "cia", "ex", "etc",
          "sec", "res", "proc", "ed", "ilmo", "exmo", "cel", "prof", "m", "mt", "kg", "cj", "qd", "lt", "sl", "bl", "ap", "r", "tel", "cep"}


def contar_tokens(texto: str) -> int:
    return sum(1 for _ in TOKEN_RE.finditer(texto or ""))


@dataclass(frozen=True)
class ConfigChunk:
    estrategia: str  # "tamanho" | "estrutura"
    max_tokens: int
    overlap_tokens: int = 0

    def __post_init__(self):
        if self.estrategia not in ("tamanho", "estrutura"):
            raise ValueError("estrategia deve ser 'tamanho' ou 'estrutura'")
        if self.max_tokens < 20:
            raise ValueError("max_tokens muito pequeno")
        if not 0 <= self.overlap_tokens < self.max_tokens // 2:
            raise ValueError("overlap deve ser >= 0 e < max_tokens/2")

    @property
    def nome(self) -> str:
        return f"{self.estrategia[:3]}{self.max_tokens}o{self.overlap_tokens}"


def doc_id(d: dict) -> str:
    return f"dodf-{int(d['id'])}"


# ---------------------------------------------------------------- segmentacao
def _cortes(texto: str, padrao: re.Pattern, ignorar_abrev: bool) -> list[int]:
    """Posicoes (inicio da proxima unidade) onde `padrao` separa unidades."""
    pos = []
    for m in padrao.finditer(texto):
        if ignorar_abrev:
            # nao separa o numerador de um item ("1.6.2.3.2.") do seu titulo
            palavra = re.search(r"(\S+)$", texto[max(0, m.start() - 40):m.start()])
            if palavra and re.fullmatch(r"\d+(?:\.\d+)+\.", palavra.group(1)):
                continue
            ant = re.search(r"([^\W\d_]+|\d+)\.?$", texto[max(0, m.start() - 12):m.start()])
            if ant and ant.group(1).lower().rstrip(".") in _ABREV and texto[m.start() - 1] == ".":
                continue
        pos.append(m.end())
    return pos


def _atomos(texto: str, ini: int, fim: int, max_tokens: int, nivel: int = 0) -> list[tuple[int, int]]:
    """Divide texto[ini:fim] em atomos <= max_tokens: unidades fortes -> frases -> janelas de palavras."""
    if contar_tokens(texto[ini:fim]) <= max_tokens:
        return [(ini, fim)]
    if nivel >= 2:
        return _janelas_palavras(texto, ini, fim, max_tokens)
    padrao, abrev = ((_FORTE, False), (_FRASE, True))[nivel]
    sub = texto[ini:fim]
    cortes = _cortes(sub, padrao, abrev)
    lim = [0] + cortes + [len(sub)]
    partes = [(ini + a, ini + b) for a, b in zip(lim, lim[1:]) if sub[a:b].strip()]
    if len(partes) <= 1:
        return _atomos(texto, ini, fim, max_tokens, nivel + 1)
    out: list[tuple[int, int]] = []
    for a, b in partes:
        out.extend(_atomos(texto, a, b, max_tokens, nivel + 1))
    return out

def _janelas_palavras(texto: str, ini: int, fim: int, max_tokens: int) -> list[tuple[int, int]]:
    """Ultimo recurso: corta em fronteira de token (sem overlap), nunca dentro de uma palavra."""
    toks = [(ini + m.start(), ini + m.end()) for m in TOKEN_RE.finditer(texto[ini:fim])]
    out, i = [], 0
    while i < len(toks):
        j = min(i + max_tokens, len(toks))
        out.append((toks[i][0], toks[j - 1][1]))
        i = j
    return out


# ---------------------------------------------------------------- estrategias
def _spans_tamanho(texto: str, cfg: ConfigChunk) -> list[tuple[int, int]]:
    toks = [(m.start(), m.end()) for m in TOKEN_RE.finditer(texto)]
    n = len(toks)
    if n == 0:
        return []
    if n <= cfg.max_tokens:
        return [(toks[0][0], toks[-1][1])]
    passo = cfg.max_tokens - cfg.overlap_tokens
    spans, i = [], 0
    while True:
        j = min(i + cfg.max_tokens, n)
        spans.append((toks[i][0], toks[j - 1][1]))
        if j == n:
            break
        i += passo
    return spans


def _spans_estrutura(texto: str, cfg: ConfigChunk) -> list[tuple[int, int]]:
    if not texto.strip():
        return []
    total = contar_tokens(texto)
    if total <= cfg.max_tokens:
        s = texto.strip()
        a = texto.index(s[0])
        return [(a, a + len(s))]
    atomos = [(a, b) for a, b in _atomos(texto, 0, len(texto), cfg.max_tokens) if texto[a:b].strip()]
    ntok = [contar_tokens(texto[a:b]) for a, b in atomos]
    spans, i = [], 0
    while i < len(atomos):
        soma, j = 0, i
        while j < len(atomos) and (soma + ntok[j] <= cfg.max_tokens or j == i):
            soma += ntok[j]
            j += 1
        spans.append((atomos[i][0], atomos[j - 1][1]))
        if j >= len(atomos):
            break
        # overlap: recua atomos inteiros cuja soma <= overlap, garantindo progresso
        k, ov = j, 0
        while k - 1 > i and ov + ntok[k - 1] <= cfg.overlap_tokens:
            k -= 1
            ov += ntok[k]
        i = k
    return spans


def _cabecalho(d: dict) -> str:
    partes = [str(d.get("tipo_documento") or "").strip(), str(d.get("numero_documento") or "").strip()]
    cab = " - ".join(p for p in partes if p)
    return f"{cab} (DODF {d.get('data_edicao', '')}, {d.get('secao', '')})".strip()


def chunkear_documento(d: dict, cfg: ConfigChunk) -> list[dict]:
    """Retorna lista de chunks (dict) com metadados originais preservados. Documento vazio -> []."""
    texto = d.get("texto_completo") or ""
    if not texto.strip():
        return []
    spans = _spans_tamanho(texto, cfg) if cfg.estrategia == "tamanho" else _spans_estrutura(texto, cfg)
    did = doc_id(d)
    cab = _cabecalho(d)
    meta = {k: d.get(k) for k in METADADOS}
    out = []
    for ordem, (a, b) in enumerate(spans):
        t = texto[a:b].strip()
        if not t:
            continue
        out.append({"chunk_id": f"{did}:{cfg.nome}:{ordem:04d}", "doc_id": did, "ordem": ordem, "config": cfg.nome,
                    "estrategia": cfg.estrategia, "texto": t, "texto_indexacao": f"{cab}\n{t}",
                    "n_tokens": contar_tokens(t), "char_inicio": a, "char_fim": b,
                    "hash": hashlib.sha1(t.encode("utf-8")).hexdigest()[:12], **meta})
    for c in out:
        c["n_chunks_doc"] = len(out)
    return out


def chunkear_corpus(corpus: list[dict], cfg: ConfigChunk) -> list[dict]:
    chunks: list[dict] = []
    for d in corpus:
        chunks.extend(chunkear_documento(d, cfg))
    return chunks

