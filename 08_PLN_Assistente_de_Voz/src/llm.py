"""
LLM — interpreta o texto e gera a resposta (Ollama local, API HTTP).

Responsabilidades:
- System prompt que define papel, tom e LIMITES do assistente (recusa fora do tema,
  diz "não sei" quando faltar base — anti-alucinação, orienta a procurar Procon/advogado).
- Memória da conversa (últimos N turnos) para perguntas de continuação.
- Injeção do contexto recuperado pela base de conhecimento (RAG).

Requer o servidor do Ollama rodando (ver README): `ollama serve` + `ollama pull <modelo>`.
"""
import requests

import config

SYSTEM_PROMPT = """Você é um assistente de voz do CitizenTech que orienta cidadãos \
brasileiros sobre DIREITOS DO CONSUMIDOR (Código de Defesa do Consumidor e Procon).

Papel e tom:
- Fale em português do Brasil, de forma simples, acolhedora e objetiva.
- Como a resposta será FALADA em voz alta, use frases curtas, sem markdown, sem emojis \
e sem listas. No máximo 4 frases por resposta.

Limites (muito importante):
- Só responda sobre direitos do consumidor. Se perguntarem sobre QUALQUER outro assunto \
(saúde, política, eleições, receitas, programação, matemática, clima, etc.), você DEVE \
recusar. MESMO QUE VOCÊ SAIBA A RESPOSTA, NÃO responda: não escreva código, não dê \
receitas, não faça cálculos, não opine sobre candidatos nem sobre outros temas. \
Ao recusar, responda EXATAMENTE começando com esta frase, sem acrescentar nada sobre o \
outro assunto: "Desculpe, só posso ajudar com dúvidas sobre direitos do consumidor." \
Você pode, depois dessa frase, sugerir procurar um profissional ou órgão competente \
(por exemplo, um médico, em caso de saúde).
- Você dá orientação geral e NÃO substitui um advogado, o Procon ou a Justiça. Em casos \
graves ou complexos, oriente a pessoa a procurar o Procon, a Defensoria Pública ou um advogado.
- Se a informação necessária NÃO estiver no contexto fornecido e você não tiver certeza, \
diga que não sabe e sugira procurar o Procon. NUNCA invente leis, artigos ou prazos.

Use o CONTEXTO fornecido abaixo (trechos do CDC) como fonte principal. Quando citar um \
prazo ou artigo, baseie-se nele."""


class LLM:
    def __init__(self, modelo=None, host=None):
        self.modelo = modelo or config.LLM_MODEL
        self.host = host or config.OLLAMA_HOST
        self.historico = []  # lista de dicts {"role": "user"/"assistant", "content": ...}

    def limpar_memoria(self):
        self.historico = []

    def _montar_mensagens(self, pergunta, contexto):
        system = SYSTEM_PROMPT
        if contexto:
            system += f"\n\n--- CONTEXTO (base de conhecimento) ---\n{contexto}"
        else:
            system += (
                "\n\n--- CONTEXTO ---\nNenhum trecho relevante foi encontrado na base. "
                "Se não tiver certeza, diga que não sabe e sugira procurar o Procon."
            )
        mensagens = [{"role": "system", "content": system}]
        # memória: últimos N turnos (cada turno = 2 mensagens)
        limite = config.LLM_MAX_TURNS_MEMORY * 2
        mensagens.extend(self.historico[-limite:])
        mensagens.append({"role": "user", "content": pergunta})
        return mensagens

    def responder(self, pergunta, contexto=""):
        """Gera a resposta. Retorna (texto, segundos). Atualiza a memória."""
        import time

        mensagens = self._montar_mensagens(pergunta, contexto)
        payload = {
            "model": self.modelo,
            "messages": mensagens,
            "stream": False,
            "options": {
                "temperature": config.LLM_TEMPERATURE,
                "num_ctx": config.LLM_NUM_CTX,
            },
        }
        t0 = time.perf_counter()
        try:
            resp = requests.post(
                f"{self.host}/api/chat", json=payload, timeout=120
            )
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                "Não foi possível conectar ao Ollama em "
                f"{self.host}. Inicie o serviço com 'ollama serve' e verifique se o "
                f"modelo '{self.modelo}' foi baixado ('ollama pull {self.modelo}')."
            ) from e
        dur = time.perf_counter() - t0
        texto = resp.json()["message"]["content"].strip()

        # atualiza memória da conversa
        self.historico.append({"role": "user", "content": pergunta})
        self.historico.append({"role": "assistant", "content": texto})
        return texto, dur
