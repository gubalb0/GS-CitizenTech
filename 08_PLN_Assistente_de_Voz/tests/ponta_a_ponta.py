"""
Teste de ponta a ponta — latência média por etapa e total.

O enunciado pede 10 conversas completas com pelo menos 3 turnos, incluindo uma
pergunta de continuação e uma recusa. Para automatizar a MEDIÇÃO DE LATÊNCIA sem
depender de 30+ áudios gravados, este script sintetiza a fala de cada turno com o
próprio TTS e a usa como entrada do pipeline (mic -> STT -> ... -> TTS).

Para o relatório, rode também conversas reais pela interface (app.py); o vídeo de
entrega deve ser uma conversa real por voz.

Uso:  python tests/ponta_a_ponta.py
Gera logs/latencia_e2e.csv (já alimentado também por logs/latencia.csv do pipeline).
"""
import csv
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.pipeline import Assistente
from src.tts import TTS

# 10 conversas, cada uma com 3 turnos (inclui continuação e, na última, uma recusa).
CONVERSAS = [
    ["Comprei um celular pela internet e me arrependi, posso devolver?", "E onde eu faço isso?", "E se a loja não quiser devolver o dinheiro?"],
    ["Meu eletrodoméstico quebrou, qual o prazo de garantia?", "E se for um alimento estragado?", "Onde eu reclamo disso?"],
    ["Fui cobrado duas vezes na fatura do cartão, o que fazer?", "Tenho direito a receber de volta?", "E como peço esse valor?"],
    ["Meu produto novo veio com defeito, o que a loja deve fazer?", "E se ela não resolver em trinta dias?", "Quais documentos eu preciso guardar?"],
    ["A propaganda prometia uma coisa e veio outra, isso é permitido?", "O que eu posso fazer?", "Onde registro a reclamação de graça?"],
    ["Meu nome foi negativado sem eu dever nada, o que faço?", "Tenho direito a indenização?", "Preciso de advogado para isso?"],
    ["Qual lei protege o consumidor no Brasil?", "O Procon pode punir a empresa?", "E se mesmo assim não resolver?"],
    ["Minha geladeira essencial quebrou, preciso esperar trinta dias?", "E se eu quiser o dinheiro de volta?", "Onde eu reclamo?"],
    ["Posso processar uma empresa sem advogado?", "E se eu não tiver dinheiro para advogado?", "Guardo quais comprovantes?"],
    ["Comprei um remédio vencido, qual o prazo para reclamar?", "Estou com dor no peito, o que devo tomar?", "E onde registro a reclamação do remédio?"],
]


def main():
    assistente = Assistente()
    tts_entrada = TTS()  # usado só para gerar o áudio de entrada dos turnos

    registros = []
    for ci, turnos in enumerate(CONVERSAS, start=1):
        assistente.nova_conversa()
        print(f"\n=== Conversa {ci} ===")
        for ti, texto in enumerate(turnos, start=1):
            audio_in, _ = tts_entrada.sintetizar(
                texto, caminho_saida=config.TMP_DIR / f"in_{ci}_{ti}.mp3"
            )
            # apagar_audio=True exercita a retenção mínima (LGPD)
            r = assistente.processar_turno(audio_in, apagar_audio=True)
            lat = r["latencias"]
            registros.append({
                "conversa": ci, "turno": ti,
                "stt": lat.get("stt"), "rag": lat.get("rag"), "llm": lat.get("llm"),
                "adaptacao": lat.get("adaptacao"), "tts": lat.get("tts"),
                "total": lat.get("total"),
            })
            print(f"  Turno {ti}: total={lat.get('total')}s  (STT {lat.get('stt')} | LLM {lat.get('llm')} | TTS {lat.get('tts')})")

    saida = config.LOG_DIR / "latencia_e2e.csv"
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(registros[0].keys()))
        w.writeheader()
        w.writerows(registros)

    print("\n===== MÉDIAS (segundos) =====")
    for etapa in ["stt", "rag", "llm", "adaptacao", "tts", "total"]:
        vals = [r[etapa] for r in registros if r[etapa] is not None]
        if vals:
            print(f"  {etapa:<10}: média {statistics.mean(vals):.2f}  (máx {max(vals):.2f})")
    print(f"CSV salvo em: {saida}")


if __name__ == "__main__":
    main()
