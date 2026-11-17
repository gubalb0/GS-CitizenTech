"""SIMULADOR do LM Studio, só para testar a integração sem o modelo de 5 GB.

NÃO é o Gen AI e NÃO deve aparecer no vídeo nem em métricas: ele copia o começo do trecho [C1] como resposta.
Serve para provar que o caminho Zelo → serviço → recuperação BM25 → verificação → tela funciona.

    uvicorn integracao_citizentech.simulador_lmstudio:app --port 1234
"""
import json
import re
import unicodedata

from fastapi import FastAPI

app = FastAPI(title="Simulador do LM Studio (apenas testes)")
MODELO = "qwen3-8b"
_STOP = {"qual", "quais", "que", "de", "da", "do", "das", "dos", "em", "para", "a", "o", "e", "é", "foi", "um", "uma", "no", "na"}


def _palavras(t: str) -> set[str]:
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return {p for p in re.findall(r"[a-z0-9]{3,}", t) if p not in _STOP}


@app.get("/v1/models")
def modelos():
    return {"data": [{"id": MODELO, "object": "model"}]}


@app.post("/v1/chat/completions")
def completar(corpo: dict):
    usuario = next(m["content"] for m in corpo["messages"] if m["role"] == "user")
    pergunta = usuario.split("PERGUNTA DO CIDADÃO:", 1)[-1].split("\n", 1)[0]
    bloco = re.search(r"\[C1\][^\n]*\n(.*?)\n\[/C1\]", usuario, re.S)
    texto = bloco.group(1) if bloco else ""
    if not texto or len(_palavras(pergunta) & _palavras(texto)) < 2:
        saida = {"candidatas": [], "status": "fora_do_escopo", "resposta": "", "fontes": [], "evidencias": [],
                 "justificativa": "Simulador: a pergunta não tem relação com os trechos recuperados."}
    else:
        trecho = " ".join(texto.split()[:18])[:200]
        saida = {"candidatas": [{"fonte": "C1", "resposta_possivel": trecho}], "status": "respondida",
                 "resposta": trecho, "fontes": ["C1"], "evidencias": [{"fonte": "C1", "trecho": trecho}],
                 "justificativa": "Simulador: copia o início do trecho C1."}
    return {"choices": [{"message": {"content": json.dumps(saida, ensure_ascii=False)}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "completion_tokens_details": {"reasoning_tokens": 0}}}
