"""
Passo 2 — treinar o classificador (transfer learning MobileNetV2).

Uso:  python scripts/02_treinar.py
Salva o modelo em modelos/classificador_fissura.pt e o histórico em resultados/.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.dados import dataloaders
from src.modelo import construir_modelo, salvar
from src.treino_aval import treinar


def main():
    dl_treino, dl_val, dl_teste, tamanhos = dataloaders()
    print(f"Conjuntos: {tamanhos}")
    modelo = construir_modelo()
    print(f"Arquitetura: {config.ARQUITETURA} | backbone congelado: {config.CONGELAR_BACKBONE}")
    historico = treinar(modelo, dl_treino, dl_val)
    caminho = salvar(modelo)
    print(f"Modelo salvo em: {caminho}")
    (config.RESULT_DIR / "historico_treino.json").write_text(
        json.dumps(historico, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
