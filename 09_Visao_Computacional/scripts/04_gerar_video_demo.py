"""
Passo 4 (opcional) — gera um vídeo de demonstração do monitoramento urbano e o processa.

Monta um vídeo a partir de IMAGENS REAIS da base (sequência alternando trechos sem e com
fissura, simulando a câmera passando por regiões danificadas), roda o detector quadro a
quadro e salva o vídeo ANOTADO + um resumo de FPS. Serve para o vídeo de entrega e para
testar o pipeline de vídeo sem precisar de uma câmera.

Uso:  python scripts/04_gerar_video_demo.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.inferencia import processar_video
from src.modelo import carregar

EXEMPLOS = config.BASE_DIR / "exemplos"
EXEMPLOS.mkdir(exist_ok=True)


def _amostrar(classe, n, rng):
    arquivos = sorted((config.DATA_DIR / classe).glob("*.jpg"))
    idx = rng.permutation(len(arquivos))[:n]
    return [arquivos[i] for i in idx]


def gerar_video_bruto(caminho, fps=12, escala=512):
    """Sequência de imagens REAIS: trechos sem fissura -> com fissura -> sem -> com."""
    import cv2

    rng = np.random.default_rng(7)
    # blocos de monitoramento: alterna regiões íntegras e danificadas
    blocos = [("Negative", 15), ("Positive", 20), ("Negative", 10), ("Positive", 15)]
    caminhos = []
    for classe, n in blocos:
        caminhos += _amostrar(classe, n, rng)

    writer = cv2.VideoWriter(
        str(caminho), cv2.VideoWriter_fourcc(*"mp4v"), fps, (escala, escala)
    )
    for p in caminhos:
        img = Image.open(p).convert("RGB").resize((escala, escala))
        bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        writer.write(bgr)
    writer.release()


def main():
    bruto = EXEMPLOS / "video_bruto.mp4"
    print("Gerando vídeo de demonstração...")
    gerar_video_bruto(bruto)
    modelo = carregar()
    anotado = EXEMPLOS / "video_demo_anotado.mp4"
    saida, resumo = processar_video(modelo, bruto, anotado)
    print(f"Vídeo anotado: {saida}")
    print(f"Resumo: {resumo}")


if __name__ == "__main__":
    main()
