"""Metricas de recuperacao no nivel de PUBLICACAO (documento canonico).

`esperados`: lista de grupos; cada grupo = conjunto de ids canonicos equivalentes aceitos para UMA publicacao esperada.
Perguntas MULTI tem varios grupos; as demais, um. `ranking`: lista de ids canonicos de documentos na ordem recuperada
(sem repeticao; cada documento na posicao do seu melhor chunk).
"""
from __future__ import annotations


def _grupos_encontrados(esperados: list[set[int]], ranking: list[int], k: int) -> int:
    topo = set(ranking[:k])
    return sum(1 for g in esperados if g & topo)


def recall_at_k(esperados: list[set[int]], ranking: list[int], k: int) -> float:
    if not esperados:
        raise ValueError("sem publicacoes esperadas")
    return _grupos_encontrados(esperados, ranking, k) / len(esperados)


def hit_at_k(esperados: list[set[int]], ranking: list[int], k: int) -> bool:
    return _grupos_encontrados(esperados, ranking, k) >= 1


def cobertura_total_at_k(esperados: list[set[int]], ranking: list[int], k: int) -> bool:
    return _grupos_encontrados(esperados, ranking, k) == len(esperados)


def reciprocal_rank(esperados: list[set[int]], ranking: list[int]) -> float:
    alvo = set().union(*esperados) if esperados else set()
    for pos, d in enumerate(ranking, start=1):
        if d in alvo:
            return 1.0 / pos
    return 0.0


def posicao_primeiro_relevante(esperados: list[set[int]], ranking: list[int]) -> int | None:
    alvo = set().union(*esperados) if esperados else set()
    for pos, d in enumerate(ranking, start=1):
        if d in alvo:
            return pos
    return None


def ranking_de_documentos(doc_ids_por_chunk: list[int]) -> list[int]:
    """Converte a lista de chunks recuperados (em ordem) em ranking de documentos unicos pela primeira aparicao."""
    vistos, out = set(), []
    for d in doc_ids_por_chunk:
        if d not in vistos:
            vistos.add(d)
            out.append(d)
    return out
