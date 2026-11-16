"""
Modelo — transferência de aprendizado com MobileNetV2 (pré-treinada na ImageNet).

MobileNetV2 foi escolhida por ser leve e rápida em CPU (bom FPS para o monitoramento
contínuo), mantendo boa qualidade via transfer learning. Por padrão congelamos o backbone
(feature extraction) e treinamos apenas a cabeça — viável em CPU no tempo da atividade.
"""
import torch
import torch.nn as nn
from torchvision import models

import config


def construir_modelo(congelar=None):
    congelar = config.CONGELAR_BACKBONE if congelar is None else congelar
    pesos = models.MobileNet_V2_Weights.IMAGENET1K_V1
    modelo = models.mobilenet_v2(weights=pesos)
    if congelar:
        for p in modelo.features.parameters():
            p.requires_grad = False
    # troca a cabeça para 2 classes (Negative/Positive)
    n_feat = modelo.classifier[1].in_features
    modelo.classifier[1] = nn.Linear(n_feat, len(config.CLASSES))
    return modelo.to(config.DEVICE)


def salvar(modelo, caminho=None):
    caminho = caminho or config.MODEL_PATH
    torch.save(modelo.state_dict(), caminho)
    return caminho


def carregar(caminho=None):
    caminho = caminho or config.MODEL_PATH
    modelo = construir_modelo()
    modelo.load_state_dict(torch.load(caminho, map_location=config.DEVICE))
    modelo.eval()
    return modelo
