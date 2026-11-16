"""
Configuração central do assistente de voz (CitizenTech - Direitos do Consumidor).

Centralizar as escolhas aqui permite trocar qualquer módulo (STT, LLM, TTS)
sem reescrever o resto do código — atende ao requisito de modularidade.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos do projeto
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
LOG_DIR = BASE_DIR / "logs"
TMP_DIR = BASE_DIR / "tmp"

for _d in (LOG_DIR, TMP_DIR):
    _d.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# STT  (Speech-to-Text) — faster-whisper rodando em CPU
# ---------------------------------------------------------------------------
# Tamanhos disponíveis para a COMPARAÇÃO exigida no enunciado: "base" x "small".
# "small" = mais preciso; "base" = mais rápido. Troque aqui e rode os testes.
STT_MODEL_SIZE = "small"          # alternativas: "tiny", "base", "small", "medium"
STT_DEVICE = "cpu"
STT_COMPUTE_TYPE = "int8"         # int8 é o mais rápido/leve em CPU
STT_LANGUAGE = "pt"
STT_BEAM_SIZE = 1                 # 1 = mais rápido (greedy); 5 = mais preciso

# ---------------------------------------------------------------------------
# LLM — Ollama local (servidor HTTP em http://localhost:11434)
# ---------------------------------------------------------------------------
# Para a COMPARAÇÃO de modelos: troque entre "qwen2.5:3b-instruct" e "llama3.2:3b".
OLLAMA_HOST = "http://localhost:11434"
LLM_MODEL = "qwen2.5:3b-instruct"   # alternativa testada: "llama3.2:3b"
LLM_TEMPERATURE = 0.3               # baixa = menos alucinação, mais consistente
LLM_NUM_CTX = 4096                  # janela de contexto (tokens)
LLM_MAX_TURNS_MEMORY = 6            # nº de turnos (user+assistant) mantidos na memória

# ---------------------------------------------------------------------------
# RAG — base de conhecimento do tema (Direitos do Consumidor / CDC)
# ---------------------------------------------------------------------------
RAG_TOP_K = 3                      # nº de trechos recuperados por pergunta
RAG_MIN_SCORE = 0.05              # abaixo disso considera-se "sem contexto relevante"

# ---------------------------------------------------------------------------
# TTS — edge-tts (vozes sintéticas prontas de pt-BR, sem clonagem)
# ---------------------------------------------------------------------------
# AVISO LGPD: edge-tts envia o TEXTO da resposta aos servidores da Microsoft
# para sintetizar o áudio. O áudio do usuário NUNCA sai da máquina (STT é local).
TTS_VOICE = "pt-BR-AntonioNeural"   # alternativas: "pt-BR-FranciscaNeural", "pt-BR-ThalitaNeural"
TTS_RATE = "+0%"
TTS_PITCH = "+0Hz"

# ---------------------------------------------------------------------------
# Privacidade / LGPD
# ---------------------------------------------------------------------------
# Retenção mínima: por padrão NÃO guardamos o áudio do cidadão após a transcrição.
KEEP_AUDIO_AFTER_TRANSCRIPTION = False

CONSENT_TEXT = (
    "Aviso de privacidade (LGPD): esta conversa é gravada e processada apenas para "
    "responder você. O áudio é transcrito no seu computador e apagado em seguida "
    "(não guardamos áudios). Apenas o TEXTO da resposta é enviado ao serviço de voz "
    "da Microsoft (edge-tts) para gerar o áudio falado. Este assistente dá orientação "
    "geral sobre direitos do consumidor e não substitui um advogado, o Procon ou a Justiça."
)
