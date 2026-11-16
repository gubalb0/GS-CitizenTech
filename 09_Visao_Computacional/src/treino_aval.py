"""
Treino e avaliação do classificador de fissuras.

Avaliação (classificação): precisão, recall, F1 e matriz de confusão (sklearn),
além de análise de exemplos de acerto e erro.
"""
import json
import time

import numpy as np
import torch
import torch.nn as nn

import config


def treinar(modelo, dl_treino, dl_val):
    otim = torch.optim.Adam(
        [p for p in modelo.parameters() if p.requires_grad], lr=config.LR
    )
    criterio = nn.CrossEntropyLoss()
    historico = []
    for epoca in range(1, config.EPOCAS + 1):
        modelo.train()
        perda_soma = 0.0
        for x, y in dl_treino:
            x, y = x.to(config.DEVICE), y.to(config.DEVICE)
            otim.zero_grad()
            saida = modelo(x)
            perda = criterio(saida, y)
            perda.backward()
            otim.step()
            perda_soma += perda.item() * x.size(0)
        acc_val = _acuracia(modelo, dl_val)
        perda_media = perda_soma / len(dl_treino.dataset)
        historico.append({"epoca": epoca, "perda": round(perda_media, 4), "acc_val": round(acc_val, 4)})
        print(f"Época {epoca}/{config.EPOCAS}  perda={perda_media:.4f}  acc_val={acc_val:.4f}")
    return historico


@torch.no_grad()
def _acuracia(modelo, dl):
    modelo.eval()
    certos = total = 0
    for x, y in dl:
        x, y = x.to(config.DEVICE), y.to(config.DEVICE)
        pred = modelo(x).argmax(1)
        certos += (pred == y).sum().item()
        total += y.size(0)
    return certos / max(total, 1)


@torch.no_grad()
def avaliar(modelo, dl_teste):
    """Retorna métricas e as previsões para análise de erro."""
    from sklearn.metrics import (confusion_matrix, precision_recall_fscore_support,
                                 accuracy_score)

    modelo.eval()
    y_true, y_pred, y_conf = [], [], []
    for x, y in dl_teste:
        x = x.to(config.DEVICE)
        prob = torch.softmax(modelo(x), dim=1).cpu().numpy()
        pred = prob.argmax(1)
        conf = prob.max(1)
        y_true.extend(y.numpy().tolist())
        y_pred.extend(pred.tolist())
        y_conf.extend(conf.tolist())

    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred).tolist()
    metricas = {
        "acuracia": round(accuracy_score(y_true, y_pred), 4),
        "precisao": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "matriz_confusao": cm,          # [[TN, FP],[FN, TP]]
        "classes": config.CLASSES,
        "n_teste": len(y_true),
    }
    return metricas, {"y_true": y_true, "y_pred": y_pred, "y_conf": y_conf}


def salvar_matriz_confusao(cm, caminho=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    caminho = caminho or (config.RESULT_DIR / "matriz_confusao.png")
    cm = np.array(cm)
    fig, ax = plt.subplots(figsize=(4.5, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(config.CLASSES); ax.set_yticklabels(config.CLASSES)
    ax.set_xlabel("Previsto"); ax.set_ylabel("Real")
    ax.set_title("Matriz de confusão — fissuras")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=14)
    fig.colorbar(im, fraction=0.046)
    plt.tight_layout()
    plt.savefig(caminho, dpi=140)
    return caminho


def medir_latencia(modelo, dl_teste, n=100):
    """Latência média por imagem e FPS (CPU). Retorna dict."""
    modelo.eval()
    tempos = []
    vistos = 0
    with torch.no_grad():
        for x, _ in dl_teste:
            for i in range(x.size(0)):
                img = x[i:i + 1].to(config.DEVICE)
                t0 = time.perf_counter()
                _ = torch.softmax(modelo(img), dim=1)
                tempos.append(time.perf_counter() - t0)
                vistos += 1
                if vistos >= n:
                    break
            if vistos >= n:
                break
    lat = float(np.mean(tempos))
    return {"latencia_ms": round(lat * 1000, 2), "fps": round(1.0 / lat, 1), "n": vistos}
