"""Deduplicacao de publicacoes identicas do corpus (mesma chave estrutural E mesmo texto).

Nada e descartado: cada grupo tem um documento canonico (menor id) e a lista de ids equivalentes, preservada nos chunks
e usada na avaliacao (qualquer id equivalente e fonte valida).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .dados import norm_espacos


@dataclass
class Duplicatas:
    canonico_de: dict[int, int] = field(default_factory=dict)      # id -> id canonico
    grupos: dict[int, list[int]] = field(default_factory=dict)     # id canonico -> ids equivalentes (inclui o canonico)

    @property
    def n_grupos_com_duplicata(self) -> int:
        return sum(1 for v in self.grupos.values() if len(v) > 1)

    @property
    def n_documentos_redundantes(self) -> int:
        return sum(len(v) - 1 for v in self.grupos.values())


def chave_duplicata(d: dict) -> tuple:
    return (d["edicao"], d["data_edicao"], d["secao"], d.get("referencia") or "", norm_espacos(d.get("texto_completo")))


def agrupar_duplicatas(corpus: list[dict]) -> Duplicatas:
    por_chave: dict[tuple, list[int]] = {}
    for d in corpus:
        por_chave.setdefault(chave_duplicata(d), []).append(int(d["id"]))
    r = Duplicatas()
    for ids in por_chave.values():
        ids = sorted(ids)
        r.grupos[ids[0]] = ids
        for i in ids:
            r.canonico_de[i] = ids[0]
    return r


def documentos_canonicos(corpus: list[dict], dup: Duplicatas | None = None) -> list[dict]:
    """Um documento por grupo (o de menor id), com `ids_equivalentes`. Preserva a ordem original do corpus."""
    dup = dup or agrupar_duplicatas(corpus)
    out = []
    for d in corpus:
        if dup.canonico_de[int(d["id"])] == int(d["id"]):
            out.append({**d, "ids_equivalentes": dup.grupos[int(d["id"])]})
    return out
