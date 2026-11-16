# Áudios de teste do STT

Grave aqui os **20 áudios** exigidos pelo enunciado para avaliar o STT (WER):

- pelo menos **3 vozes diferentes** (integrantes do grupo);
- pelo menos **5 áudios com ruído de fundo** (TV, rua, ventilador, etc.);
- fale perguntas sobre direitos do consumidor (pode usar as de `../perguntas.json`).

## Formato
- `.wav` ou `.mp3`, mono, qualquer taxa (o Whisper reamostra sozinho).
- Sugestão de nomes: `voz1_pergunta01.wav`, `voz2_ruido_pergunta03.wav`, etc.

## Depois de gravar
1. Preencha `../transcricoes_ref.json` com `{ "nome_do_arquivo": "texto exato falado" }`.
2. Rode `python tests/avaliar_stt.py` para calcular o **WER** comparando os
   modelos Whisper `base` e `small` (a comparação de duas opções do enunciado).

> Esta pasta entra no repositório como "material de teste" (entregável 3).
