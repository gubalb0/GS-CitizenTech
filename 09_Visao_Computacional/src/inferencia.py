"""
Inferência para a integração no CitizenTech.

- prever_imagem: recebe uma imagem e devolve classe, confiança e a sinalização de
  "necessita inspeção" (triagem), com a latência.
- processar_video: roda o modelo quadro a quadro, anota rótulo+confiança, mede FPS e
  simula o monitoramento urbano (também aceita sequência de imagens).

IMPORTANTE (triagem): a presença de fissura NÃO determina gravidade nem segurança
estrutural — o resultado apenas sinaliza locais candidatos a INSPEÇÃO.
"""
import time

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

import config

_tf = transforms.Compose([
    transforms.Resize((config.IMG_SIZE, config.IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(config.NORM_MEAN, config.NORM_STD),
])


def _preparar(img_pil):
    return _tf(img_pil.convert("RGB")).unsqueeze(0).to(config.DEVICE)


@torch.no_grad()
def prever_imagem(modelo, img_pil):
    t0 = time.perf_counter()
    prob = torch.softmax(modelo(_preparar(img_pil)), dim=1).cpu().numpy()[0]
    dt = time.perf_counter() - t0
    p_fissura = float(prob[1])
    tem_fissura = p_fissura >= config.LIMIAR_CONFIANCA
    return {
        "classe": "Com fissura" if tem_fissura else "Sem fissura",
        "confianca": round(p_fissura if tem_fissura else 1 - p_fissura, 4),
        "prob_fissura": round(p_fissura, 4),
        "necessita_inspecao": bool(tem_fissura),
        "latencia_ms": round(dt * 1000, 2),
    }


@torch.no_grad()
def _prever_frame_bgr(modelo, frame_bgr):
    import cv2

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    prob = torch.softmax(modelo(_preparar(img)), dim=1).cpu().numpy()[0]
    p = float(prob[1])
    return ("Com fissura" if p >= config.LIMIAR_CONFIANCA else "Sem fissura"), p


def processar_video(modelo, caminho_entrada, caminho_saida=None, max_frames=None):
    """Processa um vídeo, anotando cada quadro. Retorna (caminho_saida, resumo)."""
    import cv2

    caminho_saida = str(caminho_saida or (config.TMP_DIR / "video_anotado.mp4"))
    cap = cv2.VideoCapture(str(caminho_entrada))
    fps_in = cap.get(cv2.CAP_PROP_FPS) or 20
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(
        caminho_saida, cv2.VideoWriter_fourcc(*"mp4v"), fps_in, (w, h)
    )

    n = 0
    n_fissura = 0
    t0 = time.perf_counter()
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        classe, p = _prever_frame_bgr(modelo, frame)
        alerta = p >= config.LIMIAR_CONFIANCA
        if alerta:
            n_fissura += 1
        cor = (0, 0, 255) if alerta else (0, 170, 0)
        texto = f"{classe}  {p*100:.0f}%" + ("  [INSPECIONAR]" if alerta else "")
        cv2.rectangle(frame, (0, 0), (w, 34), (30, 30, 30), -1)
        cv2.putText(frame, texto, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)
        writer.write(frame)
        n += 1
        if max_frames and n >= max_frames:
            break
    cap.release()
    writer.release()

    dt = time.perf_counter() - t0
    resumo = {
        "frames": n,
        "frames_com_fissura": n_fissura,
        "fps_processamento": round(n / dt, 1) if dt > 0 else 0,
        "latencia_media_ms": round(dt / max(n, 1) * 1000, 2),
    }
    return caminho_saida, resumo


def processar_sequencia(modelo, caminhos):
    """Monitoramento por sequência de imagens. Retorna lista de previsões + FPS."""
    resultados = []
    t0 = time.perf_counter()
    for c in caminhos:
        r = prever_imagem(modelo, Image.open(c))
        r["arquivo"] = str(c)
        resultados.append(r)
    dt = time.perf_counter() - t0
    fps = round(len(caminhos) / dt, 1) if dt > 0 else 0
    return resultados, fps
