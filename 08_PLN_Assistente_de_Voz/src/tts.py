"""
TTS (Text-to-Speech) — sintetiza a resposta em áudio pt-BR com edge-tts.

Usa vozes SINTÉTICAS prontas (sem clonagem de voz real), conforme a ética do enunciado.

AVISO LGPD: o edge-tts envia o TEXTO da resposta aos servidores da Microsoft para
gerar o áudio. O áudio do cidadão (entrada) nunca sai da máquina — só o STT, que é local.
"""
import asyncio
import time
import uuid

import config

# O edge-tts é um serviço de nuvem e pode falhar de forma transitória
# (NoAudioReceived, limite de requisições). Tentamos novamente algumas vezes.
TENTATIVAS = 3
ESPERA_ENTRE_TENTATIVAS = 1.5  # segundos


class TTS:
    def __init__(self, voz=None, rate=None, pitch=None):
        self.voz = voz or config.TTS_VOICE
        self.rate = rate or config.TTS_RATE
        self.pitch = pitch or config.TTS_PITCH

    async def _sintetizar_async(self, texto, caminho_saida):
        import edge_tts

        comunicador = edge_tts.Communicate(
            texto, voice=self.voz, rate=self.rate, pitch=self.pitch
        )
        await comunicador.save(str(caminho_saida))

    def sintetizar(self, texto, caminho_saida=None):
        """Gera um arquivo mp3. Retorna (caminho, segundos). Tenta novamente em caso
        de falha transitória do serviço de nuvem."""
        if caminho_saida is None:
            caminho_saida = config.TMP_DIR / f"resposta_{uuid.uuid4().hex[:8]}.mp3"
        t0 = time.perf_counter()
        ultimo_erro = None
        for tentativa in range(1, TENTATIVAS + 1):
            try:
                asyncio.run(self._sintetizar_async(texto, caminho_saida))
                return str(caminho_saida), time.perf_counter() - t0
            except Exception as e:  # NoAudioReceived, erros de conexão, etc.
                ultimo_erro = e
                if tentativa < TENTATIVAS:
                    time.sleep(ESPERA_ENTRE_TENTATIVAS)
        raise RuntimeError(
            f"Falha no TTS (edge-tts) após {TENTATIVAS} tentativas: {ultimo_erro}"
        )
