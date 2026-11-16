"""
Passo 1 — preparar os dados.

Se DATA_DIR já tiver Positive/ e Negative/ (base REAL: Concrete Crack / SDNET2018),
apenas confere. Caso contrário, e se USAR_SINTETICO=True, gera a amostra sintética.

Uso:  python scripts/01_preparar_dados.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.dados import gerar_sinteticos, split_estratificado


def _ja_tem_dados():
    pos = config.DATA_DIR / "Positive"
    neg = config.DATA_DIR / "Negative"
    return pos.exists() and neg.exists() and any(pos.iterdir()) and any(neg.iterdir())


def main():
    if _ja_tem_dados():
        print(f"Base encontrada em {config.DATA_DIR}. Usando os dados existentes.")
    elif config.USAR_SINTETICO:
        print("Base real não encontrada — gerando amostra SINTÉTICA de fissuras...")
        total = gerar_sinteticos()
        print(f"{total} imagens geradas em {config.DATA_DIR}")
    else:
        print(f"Coloque a base em {config.DATA_DIR}/Positive e /Negative e rode de novo.")
        return

    treino, val, teste = split_estratificado()
    print(f"Split (sem vazamento): treino={len(treino)}  val={len(val)}  teste={len(teste)}")


if __name__ == "__main__":
    main()
