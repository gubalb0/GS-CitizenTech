"""
Configuração central — Visão Computacional para Manutenção Urbana (CitizenTech).

Tarefa: classificação binária de fissuras em concreto (com fissura x sem fissura),
para apoiar a TRIAGEM de locais que precisam de inspeção.

Trocar para a base REAL (ex.: "Concrete Crack Images for Classification" ou SDNET2018):
basta apontar DATA_DIR para uma pasta com subpastas Positive/ e Negative/ e rodar os
scripts. O gerador sintético existe só para o pipeline rodar sem download.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "crackdataset"   # subpastas: Positive/ e Negative/
MODEL_DIR = BASE_DIR / "modelos"
RESULT_DIR = BASE_DIR / "resultados"
TMP_DIR = BASE_DIR / "tmp"

for _d in (MODEL_DIR, RESULT_DIR, TMP_DIR):
    _d.mkdir(parents=True, exist_ok=True)

CLASSES = ["Negative", "Positive"]   # 0 = sem fissura, 1 = com fissura

# --- Dados sintéticos (fallback) ---
USAR_SINTETICO = False       # False = usa a base REAL já presente em DATA_DIR
N_POR_CLASSE = 1000          # tamanho da amostra por classe (base real Concrete Crack)
SEED = 42

# --- Pré-processamento / modelo ---
IMG_SIZE = 224               # entrada da MobileNetV2 (ImageNet)
# normalização ImageNet (exigida pelos pesos pré-treinados)
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]

ARQUITETURA = "mobilenet_v2"  # leve e rápida em CPU -> bom FPS
CONGELAR_BACKBONE = True      # feature extraction: treina só a cabeça (rápido em CPU)

# --- Treino ---
EPOCAS = 4
BATCH = 32
LR = 1e-3
VAL_FRAC = 0.15
TEST_FRAC = 0.15

# --- Inferência / triagem ---
# Limiar de confiança para sinalizar "necessita inspeção". Acima disso, marca como fissura.
LIMIAR_CONFIANCA = 0.5
DEVICE = "cpu"

MODEL_PATH = MODEL_DIR / "classificador_fissura.pt"
