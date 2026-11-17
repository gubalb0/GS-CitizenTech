"""Etapa 4.3b — MULTI declarado pelo dataset x multiplicidade REAL de evidencias no corpus (somente leitura; sem modelo, sem retriever).

Para cada pergunta da validacao com mais de uma publicacao esperada (associacao QA->documento da Etapa 2), mede quantas das publicacoes
associadas sao efetivamente relevantes: melhor janela de 1.500 caracteres cobrindo termos distintos da pergunta (mesma medida de
`Catalogo.melhor_janela`). Criterio fixado antes da leitura dos resultados: publicacao associada e 'efetivamente relevante' se sua
cobertura >= max(3, ceil(0.75 * melhor cobertura entre as associadas)). Nao altera dados originais.
Uso: python -m citizentech.assistente.auditoria_multi  ->  docs/assistente/auditoria_multi_dataset.csv (+ resumo .txt)
"""
from __future__ import annotations

import csv
import math

from . import dados as D
from .avaliacao_e2e import preparar
from .catalogo import Catalogo

NAO_UNIVOCAS = {"val-005", "val-018", "val-023", "val-120", "val-122", "val-146"}


def analisar() -> list[dict]:
    corpus, val, assoc, dup, esperados, docs = preparar()
    cat = Catalogo.de_corpus(corpus)
    linhas = []
    for q, a, esp in zip(val, assoc, esperados):
        if len(esp) < 2:
            continue
        s = cat._termos(q["pergunta"])
        cob = []
        for g in esp:
            cid = cat.canonico(sorted(g)[0])
            cob.append((cat.melhor_janela(cat.docs[cid], s), cid))
        mx = max(c for c, _ in cob)
        lim = max(Catalogo.MIN_TERMOS, math.ceil(0.75 * mx))
        efet = [cid for c, cid in cob if c >= lim]
        linhas.append({"qid": q["qid"], "multi_declarado_pelo_dataset": a["multi"], "n_publicacoes_associadas": len(esp), "n_efetivamente_relevantes": len(efet),
                       "cobertura_por_publicacao": " ".join(f"{cid}:{c}" for c, cid in cob), "melhor_cobertura": mx,
                       "classificacao": ("indeterminado (cobertura lexical < 3 termos)" if mx < Catalogo.MIN_TERMOS else "multiplicidade real" if len(efet) >= 2 else "associacao frouxa (1 relevante)"), "nao_univoca": q["qid"] in NAO_UNIVOCAS,
                       "pergunta": q["pergunta"]})
    return linhas


def main() -> None:
    L = analisar()
    out = D.RAIZ / "docs" / "assistente"
    with (out / "auditoria_multi_dataset.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(L[0]), delimiter=";")
        w.writeheader()
        w.writerows(L)
    real = [x for x in L if x["classificacao"] == "multiplicidade real"]
    from collections import Counter
    print(len(L), "perguntas com >=2 publicacoes associadas:", dict(Counter(x["classificacao"] for x in L)))
    for x in L:
        print(x["qid"], x["n_publicacoes_associadas"], x["n_efetivamente_relevantes"], x["classificacao"], "|", x["cobertura_por_publicacao"])


if __name__ == "__main__":
    main()
