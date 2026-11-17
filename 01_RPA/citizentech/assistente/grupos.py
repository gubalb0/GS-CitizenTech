"""Etapa 4.4 / Fase 1 - grupos A/B pela evidencia REAL do contexto enviado ao modelo.

Problema (diagnostico 4.4): a rodada 4.3 marcava `enviado = posicao <= chunks_enviados` e `grupo` com `res[:n_env]`, supondo que os
chunks enviados fossem os primeiros do ranking. `montar_contexto` PULA chunks que estouram o orcamento e segue com os seguintes,
entao o conjunto enviado nem sempre e um prefixo (11 de 150 casos na rodada 4.3; val-097 mudava de grupo).

Aqui o conjunto enviado e o devolvido por `montar_contexto` (os mesmos `ItemContexto` do prompt): funcao pura, deterministica, sem LLM.
Grupo A = alguma publicacao esperada (ou duplicata equivalente) esta entre os chunks ENVIADOS; B = nao.
"""
from __future__ import annotations

from .geracao import ConfigGeracao, ItemContexto, montar_contexto


def itens_enviados(pergunta: str, resultados: list, cfg: ConfigGeracao, n_esperado: int | None = None) -> list[ItemContexto]:
    """Reconstroi os itens que foram ao prompt. Se `n_esperado` (telemetria `chunks_enviados`) for dado e divergir, falha: nunca adivinha."""
    itens = montar_contexto(pergunta, resultados, cfg).itens
    if n_esperado is not None and len(itens) != n_esperado:
        raise ValueError(f"contexto reconstruido ({len(itens)} itens) diverge da telemetria ({n_esperado}): configuracao/recuperacao diferente da rodada")
    return itens


def docs_enviados(itens: list[ItemContexto]) -> set[int]:
    """ids canonicos e equivalentes (duplicatas) das publicacoes presentes no contexto enviado."""
    out: set[int] = set()
    for i in itens:
        out.add(int(i.doc_id))
        out.update(int(x) for x in i.ids_equivalentes)
    return out


def grupo_ab(esperados: list[set[int]], itens: list[ItemContexto]) -> tuple[str, int]:
    """(grupo, n_esperadas_enviadas). `esperados`: lista de conjuntos de ids equivalentes, um por publicacao esperada."""
    env = docs_enviados(itens)
    n = sum(1 for g in esperados if set(g) & env)
    return ("A" if n >= 1 else "B"), n


def marcar_enviados(resultados: list, itens: list[ItemContexto]) -> list[bool]:
    """Flag `enviado` por resultado, pelo chunk_id realmente enviado (e nao pela posicao)."""
    ids = {i.chunk_id for i in itens}
    return [r.chunk_id in ids for r in resultados]
