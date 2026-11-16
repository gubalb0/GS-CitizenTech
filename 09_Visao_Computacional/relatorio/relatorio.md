# Visão Computacional para Manutenção Urbana — CitizenTech
## Detecção de fissuras em concreto para triagem de inspeção

**Integrantes:** Vinicius Araujo (RM564504), Gustavo Balbo (RM561711), Henry Gimenez (RM563217)

---

## 1. Problema e integração ao CitizenTech
Fissuras, buracos e danos em edificações e vias ajudam a administração municipal a planejar
inspeções. Incorporamos ao CitizenTech um módulo de **visão computacional** que recebe uma
imagem (ou vídeo) de concreto/pavimento e **sinaliza a necessidade de inspeção**, mostrando a
classe (com/sem fissura) e a **confiança** do modelo.

- **Tarefa escolhida:** classificação binária de fissuras em superfícies de concreto
  (recomendada para o prazo de 4 horas).
- **Uso:** triagem — priorizar locais para um técnico inspecionar.
- **Limite explícito:** a presença de fissura **não** determina a gravidade do dano nem a
  segurança estrutural; o módulo apoia a triagem, não substitui a avaliação de engenharia.

## 2. Dados e preparação
- **Base utilizada:** *Concrete Crack Images for Classification* (40 mil imagens 227×227,
  pastas `Positive`/`Negative`); o código também aceita o **SDNET2018** (mesma estrutura).
- **Amostra utilizada:** para viabilizar o treino em CPU no tempo da atividade, sorteamos
  aleatoriamente (seed fixa) **1000 imagens por classe** (2000 no total) da base real. Para
  usar a base completa, basta aumentar a amostra ou apontar `DATA_DIR` e reexecutar.
- **Pré-processamento:** redimensionamento para **224×224**, conversão RGB e **normalização
  ImageNet** (média/desvio exigidos pelos pesos pré-treinados); *data augmentation* (flips)
  só no treino.
- **Split sem vazamento:** divisão no **nível da imagem**, **estratificada** por classe —
  **treino 1400 / validação 300 / teste 300** (70/15/15). Nenhum recorte da mesma imagem
  original é distribuído entre conjuntos diferentes.

## 3. Arquitetura e justificativa
- **Transfer learning com MobileNetV2** (pré-treinada na ImageNet), com a cabeça trocada para
  2 classes e **backbone congelado** (*feature extraction*): treina rápido em CPU e evita
  overfitting com amostra pequena.
- **Por que MobileNetV2:** arquitetura **leve e rápida**, ideal para **CPU** e para manter
  **FPS alto** no monitoramento contínuo, sem sacrificar qualidade (ganha a representação da
  ImageNet via transfer learning).
- **Limiar de confiança:** 0,5 por padrão. Para **triagem**, interessa **recall alto** (não
  perder fissuras); baixar o limiar aumenta o recall (menos fissuras perdidas) ao custo de
  mais alarmes falsos — é o equilíbrio qualidade × sensibilidade discutido na seção 5.

## 4. Resultados (conjunto de teste, 300 imagens)

| Métrica | Valor |
|---|---|
| Acurácia | 0,997 |
| Precisão | 1,000 |
| Recall | 0,993 |
| F1 | 0,997 |

**Matriz de confusão** (ver `resultados/matriz_confusao.png`):

|  | Previsto: Negative | Previsto: Positive |
|---|---|---|
| **Real: Negative** | 150 (VN) | 0 (FP) |
| **Real: Positive** | 1 (FN) | 149 (VP) |

Evolução no treino (4 épocas): acurácia de validação de **0,987 -> 0,993**, estabilizando cedo
— o transfer learning aproveita bem a representação da ImageNet.

### Desempenho (latência e FPS)
- **Equipamento:** CPU (Windows 10, 16 GB RAM, **sem GPU**).
- **Resolução de entrada:** 224×224.
- **Latência média:** **53,2 ms/imagem** -> **18,8 FPS** (classificação de imagens).
- **Vídeo (monitoramento):** 60 quadros processados a **28,0 FPS** (35,7 ms/quadro),
  incluindo leitura, inferência e anotação de cada quadro.

## 5. Análise de erros (acertos × erros)
Dos 300 exemplos de teste, apenas **1 erro**:
- **1 Falso Negativo** (fissura -> classificada sem fissura), arquivo `Positive/11796_1.jpg`,
  com confiança **baixa (0,55)**, bem no limiar — uma fissura **tênue/fina** de baixo contraste
  com o fundo de concreto. Para triagem é o tipo de erro mais crítico (um dano real passa
  despercebido), mas ocorreu perto do limiar.
- **Nenhum Falso Positivo**: o modelo não confundiu textura/sombra de superfícies íntegras com
  fissura (precisão 1,000 na amostra de teste).

**Implicação prática:** como o único erro (FN) ocorreu perto do limiar, **baixar o limiar**
(ex.: 0,35) tende a recuperar esse tipo de fissura sutil, priorizando não perder danos ao custo
de poucos alarmes falsos — adequado a uma triagem depois confirmada por um técnico. É um ajuste
de política, não de modelo.

## 6. Integração ao CitizenTech e demonstração
Interface em **Gradio** (`app.py`) com três modos:
1. **Imagem:** envia uma foto -> classe + confiança + sinalização "necessita inspeção".
2. **Vídeo (monitoramento):** processa um vídeo curto, **anota cada quadro** (classe,
   confiança e alerta) e informa o FPS — simula o monitoramento urbano.
3. **Sequência de imagens:** processa um lote de fotos, listando as que precisam de inspeção.

Vídeo de demonstração anotado em `exemplos/video_demo_anotado.mp4` (gerado pelo
`scripts/04_gerar_video_demo.py`), montado a partir de **imagens reais** da base (sequência
alternando trechos íntegros e com fissura, simulando a câmera passando por regiões danificadas).

## 7. Limitações e melhorias futuras
- **Amostra, não a base completa:** treinamos com 2000 imagens (1000/classe) para rodar no
  prazo em CPU; a base tem 40 mil. Ampliar a amostra tende a manter ou melhorar as métricas.
  As métricas altas também refletem que a *Concrete Crack* é uma base relativamente "limpa"
  (patches recortados e bem enquadrados); cenários de campo (SDNET2018) são mais difíceis.
- **Classificação, não localização:** para **localizar** o dano (caixas delimitadoras) e tratar
  buracos/trincas em malha, migrar para **detecção de objetos** com o **RDD2022** (YOLO/Faster
  R-CNN), relatando **mAP**.
- **Robustez:** ampliar com mais sombras, molhado, baixa luz e obstáculos; considerar
  *fine-tuning* parcial do backbone e mais épocas.
- **Triagem responsável:** manter o aviso de que o módulo **não** avalia segurança estrutural.

## 8. Como reproduzir
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python scripts/01_preparar_dados.py   # gera a amostra (ou usa a base real em data/crackdataset)
python scripts/02_treinar.py          # transfer learning MobileNetV2
python scripts/03_avaliar.py          # métricas + matriz de confusão + latência/FPS
python scripts/04_gerar_video_demo.py # vídeo de demonstração anotado (opcional)
python app.py                         # interface CitizenTech (imagem + vídeo + sequência)
```
Para usar a **base real**: coloque as imagens em `data/crackdataset/Positive` e
`data/crackdataset/Negative` (e ajuste `N_POR_CLASSE`/`USAR_SINTETICO` em `config.py`).
