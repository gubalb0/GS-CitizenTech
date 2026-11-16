# Visão Computacional para Manutenção Urbana — CitizenTech

Módulo de visão computacional que detecta **fissuras em concreto** para apoiar a **triagem
de locais que precisam de inspeção**, integrado ao protótipo CitizenTech. Recebe uma imagem
ou vídeo e devolve a classificação (com/sem fissura) e a **confiança** do modelo.

> **Triagem apenas:** a presença de fissura não determina a gravidade do dano nem a segurança
> estrutural — o resultado indica locais candidatos a inspeção por um técnico.

## Arquitetura
`imagem/vídeo → pré-processamento (224×224, normalização ImageNet) → MobileNetV2 (transfer
learning) → classe + confiança → triagem (limiar) → interface Gradio`

- **Modelo:** MobileNetV2 pré-treinada (ImageNet), cabeça trocada para 2 classes, backbone
  congelado (*feature extraction*) — leve e rápida em CPU (bom FPS).
- **Tarefa:** classificação binária (Positive = com fissura / Negative = sem fissura).

## Resultados (base real, conjunto de teste — 300 imagens)
| Métrica | Valor |
|---|---|
| Acurácia | 0,997 |
| Precisão | 1,000 |
| Recall | 0,993 |
| F1 | 0,997 |
| Latência | 53,2 ms/img → **18,8 FPS** (CPU, 224×224) |

Matriz de confusão e latência completas em `resultados/` e no relatório.

## Dados
- Base utilizada: **Concrete Crack Images for Classification** (40 mil imagens 227×227),
  estrutura `data/crackdataset/Positive` e `.../Negative`.
- **Amostra:** 1000 imagens por classe (2000 no total), sorteadas aleatoriamente da base,
  para viabilizar o treino em CPU no tempo da atividade. Split 1400/300/300 (70/15/15) no
  nível da imagem, estratificado — sem vazamento entre treino/validação/teste.

## Como executar
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

python scripts/01_preparar_dados.py    # dados (amostra ou base real)
python scripts/02_treinar.py           # treino (transfer learning)
python scripts/03_avaliar.py           # métricas + matriz de confusão + latência/FPS
python scripts/04_gerar_video_demo.py  # vídeo de demonstração anotado (opcional)
python app.py                          # interface CitizenTech
```

## Estrutura
```
VISAO_COMPUTACIONAL/
├── app.py                 # interface Gradio (imagem, vídeo, sequência)
├── config.py              # configurações (modelo, limiar, dados)
├── requirements.txt
├── src/
│   ├── dados.py           # preparação + gerador sintético + split sem vazamento
│   ├── modelo.py          # MobileNetV2 transfer learning
│   ├── treino_aval.py     # treino, métricas, matriz de confusão, latência
│   └── inferencia.py      # imagem, vídeo e sequência + confiança
├── scripts/               # 01 dados, 02 treino, 03 avaliação, 04 vídeo demo
├── resultados/            # métricas.json, matriz_confusao.png, erros.json
├── exemplos/              # vídeo de demonstração anotado
└── relatorio/             # relatorio.md + relatorio.pdf
```

## Integrantes
- Vinicius Araujo — RM564504
- Gustavo Balbo — RM561711
- Henry Gimenez — RM563217
