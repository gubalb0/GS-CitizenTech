"""
Interface Gradio do assistente de voz — Direitos do Consumidor (CitizenTech).

Fluxo completo por voz: apertar para falar (ou upload de áudio) -> transcrição ->
resposta em texto + áudio falado -> tabela de latências. Exibe o texto junto do áudio
para acessibilidade e conferência.

Execução:  python app.py
"""
import gradio as gr

import config
from src.consent import registrar_consentimento, texto_consentimento
from src.pipeline import Assistente

assistente = Assistente()


def responder(audio, consentiu, historico_chat):
    historico_chat = historico_chat or []

    if not consentiu:
        aviso = "Para usar o assistente, marque o aceite do aviso de privacidade acima."
        historico_chat = historico_chat + [{"role": "assistant", "content": aviso}]
        return historico_chat, None, "", _tabela_latencia({})

    if audio is None:
        historico_chat = historico_chat + [
            {"role": "assistant", "content": "Não recebi nenhum áudio. Grave ou envie um arquivo."}
        ]
        return historico_chat, None, "", _tabela_latencia({})

    registrar_consentimento(True)
    resultado = assistente.processar_turno(audio)

    historico_chat = historico_chat + [
        {"role": "user", "content": resultado["transcricao"]},
        {"role": "assistant", "content": resultado["resposta"]},
    ]
    detalhe = (
        f"**Transcrição:** {resultado['transcricao']}\n\n"
        f"**Resposta (texto):** {resultado['resposta']}\n\n"
        f"**Texto adaptado para fala:** {resultado['resposta_falada']}"
    )
    return (
        historico_chat,
        resultado["audio_resposta"],
        detalhe,
        _tabela_latencia(resultado["latencias"]),
    )


def _tabela_latencia(marcas):
    etapas = ["stt", "rag", "llm", "adaptacao", "tts", "total"]
    return [[e, marcas.get(e, "-")] for e in etapas]


def nova_conversa():
    assistente.nova_conversa()
    return [], None, "", _tabela_latencia({})


with gr.Blocks(title="Assistente de Voz — Direitos do Consumidor") as demo:
    gr.Markdown(
        "# 🗣️ Assistente de Voz — Direitos do Consumidor (CitizenTech)\n"
        "Fale sua dúvida sobre direitos do consumidor. O assistente transcreve, "
        "responde e fala a resposta."
    )
    gr.Markdown(f"> **{texto_consentimento()}**")
    consentiu = gr.Checkbox(
        label="Li e concordo com o aviso de privacidade acima (LGPD).", value=False
    )

    with gr.Row():
        with gr.Column():
            audio_in = gr.Audio(
                sources=["microphone", "upload"],
                type="filepath",
                label="Apertar para falar ou enviar arquivo de áudio",
            )
            with gr.Row():
                btn_enviar = gr.Button("Enviar", variant="primary")
                btn_nova = gr.Button("Nova conversa")
        with gr.Column():
            chat = gr.Chatbot(label="Conversa (transcrição → resposta)", height=300)
            audio_out = gr.Audio(label="Resposta falada", autoplay=True)

    detalhe_out = gr.Markdown()
    tabela = gr.Dataframe(
        headers=["Etapa", "Segundos"],
        value=_tabela_latencia({}),
        label="Latência por etapa",
        interactive=False,
    )

    estado = gr.State([])
    btn_enviar.click(
        responder,
        inputs=[audio_in, consentiu, estado],
        outputs=[chat, audio_out, detalhe_out, tabela],
    ).then(lambda c: c, inputs=chat, outputs=estado)
    btn_nova.click(nova_conversa, outputs=[chat, audio_out, detalhe_out, tabela]).then(
        lambda: [], outputs=estado
    )


if __name__ == "__main__":
    print(f"Modelo STT: {config.STT_MODEL_SIZE} | LLM: {config.LLM_MODEL} | Voz: {config.TTS_VOICE}")
    demo.launch()
