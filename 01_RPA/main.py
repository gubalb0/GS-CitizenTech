"""Ponto de entrada unico.
  python main.py                 -> processa data/inbox
  python main.py --inbox PASTA   -> outra pasta de entrada
  python main.py --reset         -> limpa o estado de idempotencia antes de rodar
  python main.py --treinar       -> (re)treina o modelo com data/treino.csv
"""
import argparse
import sys
from pathlib import Path

import joblib

from citizentech import classificador, config
from citizentech.estado import Estado
from citizentech.logs import configurar_log
from citizentech.pipeline import executar


def _modelo_congelado(log, retreinado: bool):
    """Usa o modelo salvo como esta (nunca sobrescreve o modelo congelado). Se o arquivo nao puder
    ser lido (ex.: outra versao do scikit-learn), re-treina EM MEMORIA com data/treino.csv, sem gravar."""
    if retreinado:
        return "auto"  # --treinar ja gravou um novo modelo (invalida o congelamento; ver README)
    try:
        if config.ARQ_MODELO.exists():
            return joblib.load(config.ARQ_MODELO)
        return "auto"  # sem arquivo: carregar_modelo() treina e salva (primeira execucao)
    except Exception as e:
        log.warning("Modelo salvo ilegivel (%s: %s). Re-treinando em memoria, sem gravar.", type(e).__name__, e)
        return classificador.treinar(salvar_em=None)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CitizenTech RPA+IA - triagem de solicitacoes de cidadaos")
    ap.add_argument("--inbox", type=Path, default=config.DIR_INBOX)
    ap.add_argument("--saida", type=Path, default=config.DIR_SAIDA)
    ap.add_argument("--reset", action="store_true", help="limpa estado de idempotencia")
    ap.add_argument("--treinar", action="store_true", help="retreina o modelo")
    a = ap.parse_args(argv)
    log = configurar_log()
    try:
        if a.treinar:
            classificador.treinar()
        estado = Estado(config.ARQ_ESTADO)
        if a.reset:
            estado.limpar()
            log.info("Estado de idempotencia limpo")
        resumo = executar(a.inbox, a.saida, estado=estado, modelo=_modelo_congelado(log, a.treinar))
        estado.fechar()
        print(f"\nOK: {resumo['processados']} processados, {resumo['enviados_revisao_humana']} para revisao humana, "
              f"{resumo['rejeitados_invalidos']} rejeitados, {resumo['duplicados_ignorados']} duplicados. "
              f"Saidas em {a.saida}")
        return 0
    except Exception:
        log.exception("Falha fatal inesperada")
        return 1


if __name__ == "__main__":
    sys.exit(main())
