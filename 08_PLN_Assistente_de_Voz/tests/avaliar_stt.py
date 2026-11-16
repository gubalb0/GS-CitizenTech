"""
Avaliação do STT — WER (Word Error Rate) com jiwer, comparando dois tamanhos de Whisper.

Esta é a COMPARAÇÃO de duas opções exigida no enunciado: whisper "base" x "small"
(qualidade x latência). Transcreve cada áudio da pasta tests/audios/ com os dois
modelos e calcula o WER contra a transcrição de referência.

Preparação (feita pelo grupo):
1. Grave 20 áudios em tests/audios/ (pelo menos 3 vozes diferentes, 5 com ruído de fundo).
2. Preencha tests/transcricoes_ref.json com {nome_do_arquivo: "texto falado"}.

Uso:  python tests/avaliar_stt.py
Gera logs/wer.csv com WER e latência por áudio e por modelo.
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.stt import STT

AUDIO_DIR = Path(__file__).parent / "audios"
REF = Path(__file__).parent / "transcricoes_ref.json"

MODELOS_COMPARADOS = ["base", "small"]  # as duas opções comparadas


def normalizar(txt):
    """Minúsculas, sem pontuação, espaços colapsados. Retorna string (o jiwer.wer
    aplica a tokenização por conta própria)."""
    import re

    txt = (txt or "").lower()
    txt = re.sub(r"[^\w\s]", " ", txt)
    return re.sub(r"\s+", " ", txt).strip()


def main():
    import jiwer

    if not REF.exists():
        print(f"Crie {REF} com as transcrições de referência antes de rodar.")
        return
    referencias = json.loads(REF.read_text(encoding="utf-8"))
    if not referencias:
        print("Nenhuma referência encontrada. Preencha transcricoes_ref.json.")
        return

    linhas = []
    resumo = {m: {"wer": [], "seg": []} for m in MODELOS_COMPARADOS}

    for tamanho in MODELOS_COMPARADOS:
        stt = STT(tamanho=tamanho)
        print(f"\n--- Modelo Whisper: {tamanho} ---")
        for arquivo, ref in referencias.items():
            caminho = AUDIO_DIR / arquivo
            if not caminho.exists():
                print(f"  (ausente) {arquivo}")
                continue
            hip, seg = stt.transcrever(caminho)
            wer = jiwer.wer(
                reference=normalizar(ref), hypothesis=normalizar(hip)
            )
            resumo[tamanho]["wer"].append(wer)
            resumo[tamanho]["seg"].append(seg)
            linhas.append({
                "modelo": tamanho, "arquivo": arquivo, "wer": round(wer, 3),
                "segundos": round(seg, 2), "referencia": ref, "hipotese": hip,
            })
            print(f"  {arquivo}: WER={wer:.2f}  ({seg:.1f}s)")

    saida = config.LOG_DIR / "wer.csv"
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    print("\n===== RESUMO (comparação) =====")
    for m in MODELOS_COMPARADOS:
        wl, sl = resumo[m]["wer"], resumo[m]["seg"]
        if wl:
            print(f"{m}: WER médio = {sum(wl)/len(wl):.3f} | latência média = {sum(sl)/len(sl):.2f}s")
    print(f"CSV salvo em: {saida}")


if __name__ == "__main__":
    main()
