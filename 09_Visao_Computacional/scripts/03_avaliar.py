"""
Passo 3 — avaliar o modelo no conjunto de teste.

Gera: precisão, recall, F1, matriz de confusão (png), latência média e FPS, e salva
exemplos de ACERTO e ERRO (incluindo negativos com sombra, para a análise de erro).

Uso:  python scripts/03_avaliar.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.dados import dataloaders, split_estratificado
from src.modelo import carregar
from src.treino_aval import avaliar, medir_latencia, salvar_matriz_confusao


def main():
    _, _, dl_teste, _ = dataloaders()
    modelo = carregar()

    metricas, pred = avaliar(modelo, dl_teste)
    lat = medir_latencia(modelo, dl_teste, n=min(100, metricas["n_teste"]))
    metricas["latencia"] = lat

    salvar_matriz_confusao(metricas["matriz_confusao"])
    (config.RESULT_DIR / "metricas.json").write_text(
        json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # exemplos de erro (índices do teste) para análise qualitativa
    _, _, teste = split_estratificado()
    erros = [
        {"arquivo": str(teste[i][0]), "real": config.CLASSES[pred["y_true"][i]],
         "previsto": config.CLASSES[pred["y_pred"][i]], "confianca": round(pred["y_conf"][i], 3)}
        for i in range(len(teste)) if pred["y_true"][i] != pred["y_pred"][i]
    ]
    (config.RESULT_DIR / "erros.json").write_text(
        json.dumps(erros, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("\n===== MÉTRICAS (teste) =====")
    print(f"Acurácia : {metricas['acuracia']:.3f}")
    print(f"Precisão : {metricas['precisao']:.3f}")
    print(f"Recall   : {metricas['recall']:.3f}")
    print(f"F1       : {metricas['f1']:.3f}")
    print(f"Matriz   : {metricas['matriz_confusao']}  (classes {config.CLASSES})")
    print(f"Latência : {lat['latencia_ms']} ms/img  ->  {lat['fps']} FPS  (CPU)")
    print(f"Erros    : {len(erros)} de {metricas['n_teste']}")
    print(f"Arquivos salvos em {config.RESULT_DIR}")


if __name__ == "__main__":
    main()
