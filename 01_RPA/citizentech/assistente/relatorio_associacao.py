"""Executa a associacao QA -> documento no conjunto de VALIDACAO e grava os derivados em data_assistente/derivados/.
Uso: python -m citizentech.assistente.relatorio_associacao"""
import json

from . import associacao as A
from . import dados as D

SAIDA = D.RAIZ / "data_assistente" / "derivados"


def main() -> dict:
    integ = D.verificar_integridade()
    if not all(integ.values()):
        raise SystemExit(f"Integridade falhou: {integ}")
    corpus, val = D.carregar_corpus(), D.carregar_validacao()
    assoc = A.associar_todas(corpus, val)
    res = A.resumo(assoc)
    nu = A.perguntas_nao_univocas(val, assoc)
    SAIDA.mkdir(parents=True, exist_ok=True)
    with (SAIDA / "associacao_validacao.jsonl").open("w", encoding="utf-8") as fh:
        for a in assoc:
            fh.write(json.dumps(a, ensure_ascii=False) + "\n")
    (SAIDA / "associacao_resumo.json").write_text(
        json.dumps({"integridade": integ, "resumo": res, "perguntas_nao_univocas": nu}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"resumo": res, "nao_univocas": len(nu)}


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=2))
