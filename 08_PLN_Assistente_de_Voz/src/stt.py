"""
STT (Speech-to-Text) — transcrição de fala em português com faster-whisper.

Roda em CPU com quantização int8 (gratuito, privado: o áudio NÃO sai da máquina).
O tamanho do modelo é configurável em config.py para permitir a comparação
exigida no enunciado (ex.: "base" x "small").
"""
import config

_modelos = {}  # cache por tamanho, para não recarregar o modelo a cada chamada


def _carregar(tamanho):
    if tamanho not in _modelos:
        from faster_whisper import WhisperModel

        _modelos[tamanho] = WhisperModel(
            tamanho,
            device=config.STT_DEVICE,
            compute_type=config.STT_COMPUTE_TYPE,
        )
    return _modelos[tamanho]


class STT:
    def __init__(self, tamanho=None, idioma=None, beam_size=None):
        self.tamanho = tamanho or config.STT_MODEL_SIZE
        self.idioma = idioma or config.STT_LANGUAGE
        self.beam_size = beam_size or config.STT_BEAM_SIZE

    def transcrever(self, caminho_audio):
        """Transcreve um arquivo de áudio. Retorna (texto, segundos)."""
        import time

        modelo = _carregar(self.tamanho)
        t0 = time.perf_counter()
        segmentos, _info = modelo.transcribe(
            str(caminho_audio),
            language=self.idioma,
            beam_size=self.beam_size,
            vad_filter=True,  # ignora silêncios/ruído de fundo
        )
        texto = " ".join(seg.text.strip() for seg in segmentos).strip()
        dur = time.perf_counter() - t0
        return texto, dur
