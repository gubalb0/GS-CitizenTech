"""Serviço HTTP local do assistente Gen AI, consumido pelo Zelo.

Executar a partir da pasta do projeto (onde fica `citizentech/`), com o LM Studio aberto:
    uvicorn integracao_citizentech.api:app --port 8100
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from integracao_citizentech.servico import AssistenteDODF

assistente = AssistenteDODF()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await run_in_threadpool(lambda: assistente.recursos)   # carrega corpus e índice antes da primeira pergunta
    yield


app = FastAPI(title="CitizenTech · Assistente de publicações oficiais (Gen AI)", version="1.0", lifespan=lifespan)


class Pergunta(BaseModel):
    pergunta: str = Field(min_length=5, max_length=500)


@app.get("/saude")
def saude():
    return assistente.saude()


@app.post("/perguntar")
async def perguntar(body: Pergunta):
    # gerar_resposta é bloqueante (12 a 30 s): roda fora do loop do servidor
    return await run_in_threadpool(assistente.perguntar, body.pergunta)
