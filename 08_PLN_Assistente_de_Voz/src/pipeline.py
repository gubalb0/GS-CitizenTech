"""
Orquestração de um turno da conversa: microfone → STT → RAG → LLM → adaptação → TTS.

Mantém instâncias únicas dos módulos (carregamento preguiçoso) e cronometra cada etapa.
Aplica a retenção mínima: apaga o áudio do usuário após a transcrição, salvo config.
"""
import os

import config
from src.knowledge import BaseConhecimento
from src.latency import LatencyTracker
from src.llm import LLM
from src.speech_adapter import adaptar
from src.stt import STT
from src.tts import TTS


class Assistente:
    """Reúne os módulos e mantém o estado da conversa (memória no LLM)."""

    def __init__(self):
        self.stt = STT()
        self.base = BaseConhecimento()
        self.llm = LLM()
        self.tts = TTS()

    def nova_conversa(self):
        self.llm.limpar_memoria()

    def processar_turno(self, caminho_audio, apagar_audio=None):
        """Processa um turno a partir de um arquivo de áudio.

        Retorna um dict com transcrição, resposta (texto e falada), caminho do áudio
        de resposta e as latências de cada etapa.
        """
        if apagar_audio is None:
            apagar_audio = not config.KEEP_AUDIO_AFTER_TRANSCRIPTION

        t = LatencyTracker()

        with t.step("stt"):
            transcricao, _ = self.stt.transcrever(caminho_audio)

        # Retenção mínima (LGPD): áudio do usuário é apagado após a transcrição.
        if apagar_audio:
            try:
                os.remove(caminho_audio)
            except OSError:
                pass

        with t.step("rag"):
            contexto = self.base.contexto_para_prompt(transcricao)

        with t.step("llm"):
            resposta, _ = self.llm.responder(transcricao, contexto)

        with t.step("adaptacao"):
            resposta_falada = adaptar(resposta)

        with t.step("tts"):
            caminho_resp, _ = self.tts.sintetizar(resposta_falada)

        total = t.total_desde_inicio()
        t.salvar_csv(extra={"modelo_llm": config.LLM_MODEL, "stt": config.STT_MODEL_SIZE})

        return {
            "transcricao": transcricao,
            "resposta": resposta,
            "resposta_falada": resposta_falada,
            "audio_resposta": caminho_resp,
            "latencias": t.marcas,
            "latencia_total": total,
        }
