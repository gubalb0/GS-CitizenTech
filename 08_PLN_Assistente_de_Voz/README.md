# Assistente de Voz — Direitos do Consumidor (CitizenTech)

Assistente de voz em português que **escuta** o cidadão, **entende** a dúvida sobre
direitos do consumidor com um LLM e **responde falando**, sem ninguém precisar digitar.

> **Persona:** cidadão com baixa alfabetização digital, idoso ou com deficiência visual
> que foi cobrado indevidamente ou comprou um produto com defeito.
> **Problema:** acesso difícil a orientação confiável sobre o Código de Defesa do Consumidor.
> **ODS:** 16 (paz, justiça e instituições eficazes) e 12 (consumo responsável).

## Arquitetura (módulos separados, trocáveis)

```
microfone / upload de áudio
        │
        ▼
   [STT]  faster-whisper (CPU, int8)        src/stt.py
        │  transcreve fala -> texto (pt-BR)
        ▼
   [RAG]  base de conhecimento CDC (TF-IDF)  src/knowledge.py
        │  recupera trechos confiáveis do CDC
        ▼
   [LLM]  Ollama / Qwen2.5-3B + memória      src/llm.py
        │  system prompt: papel, tom, limites, recusa, anti-alucinação
        ▼
   [ADAPTAÇÃO para fala]                     src/speech_adapter.py
        │  tira markdown/emoji, expande siglas e números
        ▼
   [TTS]  edge-tts (voz sintética pt-BR)     src/tts.py
        │  texto -> áudio
        ▼
   alto-falante  +  texto na tela (Gradio)   app.py
```

Orquestração e latência: `src/pipeline.py`, `src/latency.py`. Consentimento: `src/consent.py`.

## Modelos usados (versão e licença)

| Componente | Modelo | Versão | Licença |
|---|---|---|---|
| STT | faster-whisper (Whisper `small`/`base`) | 1.0.3 | MIT (lib) / MIT (pesos Whisper) |
| LLM | Qwen2.5-3B-Instruct via Ollama | `qwen2.5:3b-instruct` | Qwen (Apache-2.0) |
| LLM (alt.) | Llama 3.2 3B via Ollama | `llama3.2:3b` | Llama 3.2 Community License |
| RAG | TF-IDF (scikit-learn) | 1.5.2 | BSD-3 |
| TTS | edge-tts (vozes Microsoft Neural pt-BR) | 6.1.12 | GPL-3.0 (lib) |
| UI | Gradio | 6.31.0 | Apache-2.0 |

## Por que local (e não nuvem)?
- **Privacidade/LGPD:** voz é dado pessoal (possivelmente biométrico). O áudio é
  transcrito **na própria máquina** e apagado em seguida; não depende de enviar a voz
  a terceiros.
- **Custo:** zero (sem APIs pagas).
- **Disponibilidade:** STT e LLM funcionam **offline**. (Exceção: o `edge-tts` envia o
  **texto** da resposta à Microsoft para gerar o áudio — informado ao usuário.)
- **Trade-off:** latência maior em CPU, mitigada com quantização `int8` e modelos 3B.

## Instalação

Pré-requisitos: **Python 3.12** e **Ollama**.

```powershell
# 1. Dependências Python
pip install -r requirements.txt

# 2. Ollama (servidor local de LLM) — baixe o instalador em https://ollama.com/download
#    Depois de instalar, baixe o modelo:
ollama pull qwen2.5:3b-instruct
#    (opcional, para a comparação de modelos)
ollama pull llama3.2:3b
```

O Ollama inicia o serviço automaticamente após a instalação (em `http://localhost:11434`).
Se precisar, rode manualmente: `ollama serve`.

## Como executar

```powershell
# Interface completa por voz
python app.py
```
Abra o endereço mostrado (geralmente http://127.0.0.1:7860). Marque o aviso de
privacidade, **aperte para falar** (ou envie um arquivo) e ouça a resposta. A
transcrição, a resposta em texto e a **tabela de latências** aparecem na tela.

### Solução de problemas: erro de CUDA no Ollama
Se o LLM retornar erro `500` com mensagem de **CUDA** (ex.: `the provided PTX was
compiled with an unsupported toolchain`), o Ollama está tentando usar uma GPU NVIDIA
com driver incompatível. Como este projeto foi pensado para **CPU**, force o modo CPU:

```powershell
# encerra o servidor atual
Get-Process -Name "ollama*" | Stop-Process -Force
# inicia em modo CPU (vale só para esta janela)
$env:OLLAMA_NUM_GPU = "0"; $env:CUDA_VISIBLE_DEVICES = "-1"
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve
```
Para tornar permanente: `setx OLLAMA_NUM_GPU 0` (reabra o terminal). Alternativa melhor
se você tiver GPU NVIDIA: **atualizar o driver** da placa — aí o Ollama usa a GPU e fica
bem mais rápido.

## Testes e métricas

```powershell
# LLM: % de acertos e % de recusas adequadas (30 perguntas; requer Ollama)
python tests/avaliar_llm.py

# STT: WER com jiwer, comparando Whisper base x small
#   -> primeiro grave os áudios em tests/audios/ e preencha tests/transcricoes_ref.json
python tests/avaliar_stt.py

# TTS: gera 10 áudios + planilha de avaliação humana (naturalidade/clareza 1-5)
python tests/avaliar_tts.py

# Ponta a ponta: 10 conversas x 3 turnos, latência média por etapa e total
python tests/ponta_a_ponta.py
```
Os CSVs são gerados em `logs/` (transitório); os **resultados finais da entrega** estão
versionados em **`resultados/`** (WER, avaliação do LLM, avaliação do TTS e latência e2e).

## Comparação de duas opções (exigida)
- **STT:** Whisper `base` vs `small` em `tests/avaliar_stt.py` (WER × latência).
- **LLM (opcional):** Qwen2.5-3B vs Llama3.2-3B — troque `LLM_MODEL` em `config.py`.

A escolha final é justificada no relatório com base em qualidade e latência.

## Ética, segurança e LGPD
- **Consentimento:** aviso exibido antes do uso; aceite registrado em `logs/consentimentos.csv`.
- **Retenção mínima:** áudio do usuário é apagado após a transcrição (`config.KEEP_AUDIO_AFTER_TRANSCRIPTION=False`).
- **Nuvem:** só o **texto** da resposta vai ao edge-tts (Microsoft) — informado ao usuário.
- **Limites:** o assistente recusa temas fora de direitos do consumidor e orienta a
  procurar Procon/Defensoria/advogado em casos complexos.
- **Alucinação:** sem contexto confiável, o assistente diz que não sabe.
- **Clonagem de voz:** proibida; usamos apenas vozes sintéticas prontas.

## Estrutura do projeto
```
PLN/
├── app.py                    # interface Gradio
├── config.py                 # configurações centrais (modelos, voz, LGPD)
├── requirements.txt
├── data/knowledge/consumidor.md   # base de conhecimento (RAG)
├── src/                      # módulos do pipeline
│   ├── stt.py  knowledge.py  llm.py  speech_adapter.py  tts.py
│   ├── pipeline.py  latency.py  consent.py
├── tests/                    # material de teste e avaliação
│   ├── perguntas.json  avaliar_llm.py  avaliar_stt.py  avaliar_tts.py  ponta_a_ponta.py
│   ├── audios/  transcricoes_ref.json
├── relatorio/relatorio.md    # rascunho do relatório (exportar p/ PDF)
└── logs/                     # CSVs de métricas (gerados)
```

## Integrantes
- Vinicius Araujo — RM564504
- Gustavo Balbo — RM561711
- Henry Gimenez — RM563217
