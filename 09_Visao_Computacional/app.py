"""
Integração ao CitizenTech — Visão Computacional para Manutenção Urbana (Gradio).

Aba 1: recebe uma IMAGEM e mostra a classificação (com/sem fissura) + confiança do modelo.
Aba 2: processa um VÍDEO curto (ou sequência de imagens) para simular o monitoramento
       urbano, anotando cada quadro e informando o FPS.

Triagem: o resultado sinaliza locais candidatos a INSPEÇÃO. A presença de fissura, por si
só, NÃO determina a gravidade do dano nem a segurança estrutural.

Execução:  python app.py
"""
import gradio as gr
from PIL import Image

import config
from src.inferencia import prever_imagem, processar_video, processar_sequencia
from src.modelo import carregar

DISCLAIMER = (
    "⚠️ **Triagem apenas.** A presença de fissura não determina a gravidade do dano nem a "
    "segurança estrutural. O resultado indica locais candidatos a inspeção por um técnico."
)

modelo = carregar()


def classificar_imagem(img):
    if img is None:
        return {}, "Envie uma imagem."
    r = prever_imagem(modelo, Image.fromarray(img))
    rotulos = {"Com fissura": r["prob_fissura"], "Sem fissura": 1 - r["prob_fissura"]}
    triagem = "🔴 NECESSITA INSPEÇÃO" if r["necessita_inspecao"] else "🟢 Sem sinal de fissura"
    texto = (
        f"### {triagem}\n"
        f"- **Classe:** {r['classe']}\n"
        f"- **Confiança:** {r['confianca']*100:.1f}%\n"
        f"- **Prob. de fissura:** {r['prob_fissura']*100:.1f}%  (limiar {config.LIMIAR_CONFIANCA})\n"
        f"- **Latência:** {r['latencia_ms']} ms\n\n{DISCLAIMER}"
    )
    return rotulos, texto


def processar_video_ui(video):
    if video is None:
        return None, "Envie um vídeo."
    saida, resumo = processar_video(modelo, video)
    texto = (
        f"### Monitoramento processado\n"
        f"- **Quadros:** {resumo['frames']}\n"
        f"- **Quadros com fissura:** {resumo['frames_com_fissura']}\n"
        f"- **FPS de processamento:** {resumo['fps_processamento']}\n"
        f"- **Latência média:** {resumo['latencia_media_ms']} ms/quadro\n\n{DISCLAIMER}"
    )
    return saida, texto


def processar_sequencia_ui(arquivos):
    if not arquivos:
        return "Envie imagens."
    caminhos = [f.name for f in arquivos]
    resultados, fps = processar_sequencia(modelo, caminhos)
    n_fiss = sum(1 for r in resultados if r["necessita_inspecao"])
    linhas = [f"- {r['arquivo'].split(chr(92))[-1]}: {r['classe']} ({r['confianca']*100:.0f}%)"
              for r in resultados]
    return (f"### Sequência ({len(resultados)} imagens) — {fps} FPS\n"
            f"{n_fiss} com fissura (necessitam inspeção)\n\n" + "\n".join(linhas))


with gr.Blocks(title="CitizenTech — Manutenção Urbana (Visão Computacional)") as demo:
    gr.Markdown(
        "# 🏙️ CitizenTech — Detecção de Fissuras em Concreto\n"
        "Módulo de visão computacional para **triagem de locais que precisam de inspeção**."
    )
    with gr.Tab("Imagem"):
        with gr.Row():
            with gr.Column():
                img_in = gr.Image(type="numpy", label="Imagem de concreto/pavimento")
                btn_img = gr.Button("Classificar", variant="primary")
            with gr.Column():
                rotulo_out = gr.Label(label="Classificação", num_top_classes=2)
                texto_out = gr.Markdown()
        btn_img.click(classificar_imagem, inputs=img_in, outputs=[rotulo_out, texto_out])

    with gr.Tab("Vídeo (monitoramento)"):
        with gr.Row():
            with gr.Column():
                vid_in = gr.Video(label="Vídeo curto de via/edificação")
                btn_vid = gr.Button("Processar vídeo", variant="primary")
            with gr.Column():
                vid_out = gr.Video(label="Vídeo anotado")
                vid_txt = gr.Markdown()
        btn_vid.click(processar_video_ui, inputs=vid_in, outputs=[vid_out, vid_txt])

    with gr.Tab("Sequência de imagens"):
        seq_in = gr.File(file_count="multiple", label="Várias imagens (monitoramento)")
        btn_seq = gr.Button("Processar sequência", variant="primary")
        seq_out = gr.Markdown()
        btn_seq.click(processar_sequencia_ui, inputs=seq_in, outputs=seq_out)


if __name__ == "__main__":
    print(f"Modelo: {config.ARQUITETURA} | limiar: {config.LIMIAR_CONFIANCA} | device: {config.DEVICE}")
    demo.launch()
