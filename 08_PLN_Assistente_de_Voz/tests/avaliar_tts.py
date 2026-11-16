"""
Avaliação do TTS — gera 10 áudios sintetizados e a planilha de avaliação humana.

Sintetiza 10 respostas (passadas pela adaptação para fala) em tests/tts_amostras/
e cria uma planilha CSV para pelo menos 3 pessoas darem nota de naturalidade e de
clareza (escala 1 a 5).

Uso:  python tests/avaliar_tts.py
Depois, abra logs/avaliacao_tts.csv e peça para 3 avaliadores preencherem as notas.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.speech_adapter import adaptar
from src.tts import TTS

SAIDA_AUDIO = Path(__file__).parent / "tts_amostras"

RESPOSTAS = [
    "Você tem direito de desistir da compra em até 7 dias por ter comprado pela internet. Peça o valor integral de volta, incluindo o frete.",
    "O prazo de garantia legal de um eletrodoméstico é de 90 dias, por ser um produto durável.",
    "Para alimentos, que são produtos não duráveis, o prazo para reclamar é de 30 dias.",
    "A loja tem até 30 dias para consertar o produto com defeito. Se não resolver, você pode pedir a troca, o dinheiro de volta ou um desconto.",
    "Se você foi cobrado a mais, tem direito a receber o dobro do valor pago indevidamente, com correção.",
    "Propaganda enganosa é proibida pelo Código de Defesa do Consumidor. O que foi anunciado obriga a empresa a cumprir.",
    "Você pode registrar sua reclamação de graça no site consumidor.gov.br ou procurar o Procon da sua cidade.",
    "Como a geladeira é um produto essencial, você pode exigir a solução de forma imediata, sem esperar os 30 dias.",
    "Guarde a nota fiscal, os comprovantes de pagamento e os números de protocolo. Eles são a prova do seu problema.",
    "Para causas de até 20 salários mínimos, você pode acionar o Juizado Especial sem precisar de advogado.",
]


def main():
    SAIDA_AUDIO.mkdir(exist_ok=True)
    tts = TTS()
    linhas = []
    for i, resposta in enumerate(RESPOSTAS, start=1):
        falavel = adaptar(resposta)
        destino = SAIDA_AUDIO / f"amostra_{i:02d}.mp3"
        _, seg = tts.sintetizar(falavel, caminho_saida=destino)
        print(f"amostra_{i:02d}.mp3 gerada ({seg:.1f}s)")
        linhas.append({
            "amostra": f"amostra_{i:02d}.mp3", "texto": resposta,
            "naturalidade_aval1": "", "clareza_aval1": "",
            "naturalidade_aval2": "", "clareza_aval2": "",
            "naturalidade_aval3": "", "clareza_aval3": "",
        })

    saida = config.LOG_DIR / "avaliacao_tts.csv"
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"\nÁudios em: {SAIDA_AUDIO}")
    print(f"Planilha para avaliação (notas 1 a 5) em: {saida}")


if __name__ == "__main__":
    main()
