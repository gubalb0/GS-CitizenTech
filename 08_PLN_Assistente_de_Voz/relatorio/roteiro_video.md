# Roteiro do vídeo (até 5 minutos)
### Assistente de Voz — Direitos do Consumidor (CitizenTech)

> Objetivo da entrega: uma conversa **real por voz** com **pelo menos 3 turnos**,
> incluindo **1 pergunta de continuação** e **1 recusa**. Mostrar também o texto na tela
> e a latência. Integrantes: Vinicius Araujo (RM564504), Gustavo Balbo (RM561711),
> Henry Gimenez (RM563217).

---

## Antes de gravar (checklist)
- [ ] Ollama rodando em modo CPU. Se precisar: `setx OLLAMA_NUM_GPU 0`, reabra o terminal,
      e deixe o serviço ativo.
- [ ] No terminal, dentro da pasta do projeto: `python app.py`
- [ ] Abrir o navegador no endereço mostrado (ex.: http://127.0.0.1:7860)
- [ ] Testar o microfone 1 vez antes de gravar “pra valer”.
- [ ] Iniciar a gravação de tela (com áudio do microfone e do alto-falante).
- [ ] Ambiente silencioso para a fala sair limpa.

---

## Estrutura e tempo (total ~4:30)

| Bloco | Tempo | O que fazer |
|---|---|---|
| 1. Abertura | 0:00–0:30 | Apresentação e tema |
| 2. Consentimento (LGPD) | 0:30–0:50 | Mostrar e marcar o aviso |
| 3. Turno 1 (normal) | 0:50–1:40 | Primeira pergunta por voz |
| 4. Turno 2 (continuação) | 1:40–2:30 | Pergunta de continuação (memória) |
| 5. Turno 3 (recusa) | 2:30–3:20 | Pergunta fora do tema |
| 6. Turno 4 (bônus) | 3:20–4:00 | Mais um direito (opcional) |
| 7. Latência + fechamento | 4:00–4:30 | Mostrar tabela de latência e encerrar |

---

## 1. Abertura (0:00–0:30)
**Falar para a câmera/tela:**
> “Olá! Somos o grupo CitizenTech. Este é o nosso assistente de voz sobre **direitos do
> consumidor**. Ele foi feito pensando em pessoas como a Dona Maria, de 67 anos, que tem
> dificuldade de ler em telas e prefere falar. O cidadão fala, o assistente entende e
> **responde falando**. Tudo roda localmente, no computador. Vamos demonstrar.”

**Ação:** mostrar a tela inicial do Gradio (título e campos).

## 2. Consentimento — LGPD (0:30–0:50)
**Falar:**
> “Antes de tudo, aparece o aviso de privacidade. Voz é um dado pessoal, então avisamos
> que a conversa é gravada e processada, que o áudio é apagado após a transcrição e que
> só o texto da resposta vai para o serviço de voz. Vou marcar que concordo.”

**Ação:** ler rapidamente o aviso e **marcar o checkbox** de consentimento.

## 3. Turno 1 — pergunta normal (0:50–1:40)
**Ação:** apertar **“apertar para falar”** e dizer:
> 🎤 *“Comprei um celular pela internet e me arrependi. Posso devolver?”*

**Ação:** clicar em **Enviar**. Esperar a resposta falada.
**Mostrar na tela:** a **transcrição** e a **resposta em texto** (acessibilidade).
**Resposta esperada (o assistente fala):** que sim, há o direito de arrependimento de
7 dias para compras pela internet, com devolução integral.

**Falar:** “Repare que ele mostra o que eu disse e a resposta, além de falar.”

## 4. Turno 2 — CONTINUAÇÃO / memória (1:40–2:30)
**Ação:** apertar para falar e dizer **sem repetir o contexto**:
> 🎤 *“E onde eu faço isso?”*

**Ação:** Enviar. 
**Destacar:** “Ele **lembrou** que eu estava falando da compra pela internet — isso é a
**memória da conversa**.”
**Resposta esperada:** orienta a procurar a loja/vendedor e, se não resolver,
consumidor.gov.br ou o Procon.

## 5. Turno 3 — RECUSA / fora do escopo (2:30–3:20)
**Ação:** apertar para falar e dizer:
> 🎤 *“Estou com dor no peito, o que devo tomar?”*

**Ação:** Enviar.
**Destacar:** “Aqui ele **recusa**, porque é um tema de saúde, não de consumidor, e me
orienta a procurar um profissional. Ele não inventa resposta.”
**Resposta esperada:** “Desculpe, só posso ajudar com dúvidas sobre direitos do
consumidor…” + sugestão de procurar um médico/serviço de saúde.

## 6. Turno 4 — bônus (opcional) (3:20–4:00)
**Ação:** apertar para falar e dizer:
> 🎤 *“Fui cobrado duas vezes na fatura, tenho direito a algo?”*

**Resposta esperada:** direito à devolução em dobro do valor cobrado indevidamente.

## 7. Latência e fechamento (4:00–4:30)
**Ação:** apontar para a **tabela de latência por etapa** (STT, RAG, LLM, adaptação,
TTS, total).
**Falar:**
> “A ferramenta também registra a latência de cada etapa. Em CPU, cada resposta leva em
> torno de 10 segundos. Resumindo: o assistente escuta, entende com um modelo de
> linguagem usando uma base do Código de Defesa do Consumidor, e responde falando — com
> cuidado com a LGPD, recusando temas fora do escopo e sem inventar respostas. Obrigado!”

---

## Dicas de gravação
- Fale pausado e perto do microfone; os áudios de teste mostraram que ruído de fundo
  piora a transcrição.
- Se a resposta demorar, não corte — mostra a latência real (pode acelerar na edição).
- Deixe visível na tela a transcrição e a resposta em texto durante cada turno.
- Confira que o áudio da resposta (alto-falante) está sendo capturado na gravação.
- Mantenha abaixo de 5 minutos; o alvo de ~4:30 dá margem.
