"""Testes da camada de integração, sem o modelo (sessão HTTP simulada, no mesmo padrão de test_geracao.py)."""
import json
from types import SimpleNamespace

import pytest
import requests

from citizentech.assistente import geracao as G
from integracao_citizentech import servico as S


class Resp:
    def __init__(self, corpo, status=200):
        self._corpo, self.status_code, self.text = corpo, status, json.dumps(corpo)

    def json(self):
        return self._corpo


MODELOS = Resp({"data": [{"id": "qwen3-8b"}]})


class Sessao:
    """GET /models responde `modelos`; POST devolve as respostas em ordem (ou levanta, se for exceção)."""

    def __init__(self, *respostas, modelos=MODELOS):
        self.respostas, self.modelos, self.posts = list(respostas), modelos, 0

    def get(self, url, timeout=None):
        if isinstance(self.modelos, Exception):
            raise self.modelos
        return self.modelos

    def post(self, url, json=None, timeout=None):
        self.posts += 1
        r = self.respostas.pop(0) if len(self.respostas) > 1 else self.respostas[0]
        if isinstance(r, Exception):
            raise r
        return r


def modelo(saida: dict) -> Resp:
    return Resp({"choices": [{"message": {"content": json.dumps(saida, ensure_ascii=False)}, "finish_reason": "stop"}],
                 "usage": {"prompt_tokens": 900, "completion_tokens": 80}})


TEXTO = "A sala de vacina da UBS 1 funciona de segunda a sexta-feira, das 8h às 16h, conforme a portaria publicada."
META = {"tipo_documento": "Portaria", "numero_documento": "12/2025", "referencia": "SES-DF", "edicao": 10,
        "data_edicao": "2025-01-15", "secao": "Seção I"}


class IndiceFalso:
    def __init__(self, resultados=None):
        self.resultados, self.consultas = resultados, []

    def buscar(self, consulta, k=5, modo="hibrido"):
        self.consultas.append((consulta, k, modo))
        if self.resultados is not None:
            return self.resultados
        return [SimpleNamespace(posicao=1, chunk_id="d1#0", doc_id=1, score=9.1, texto=TEXTO, ids_equivalentes=[1],
                                metadados=META)]


def assistente(*respostas, modelos=MODELOS, indice=None):
    idx = indice or IndiceFalso()
    a = S.AssistenteDODF(G.ConfigGeracao(), Sessao(*respostas, modelos=modelos),
                         carregar_recursos=lambda: S._Recursos(indice=idx, catalogo=None))
    return a, idx


def saida(status, resposta="", fontes=(), evid=()):
    return {"candidatas": [], "status": status, "resposta": resposta, "fontes": list(fontes),
            "evidencias": list(evid), "justificativa": "teste"}


# ---------------------------------------------------------------- contrato
def test_resposta_com_fonte_e_trecho_literal():
    trecho = "funciona de segunda a sexta-feira, das 8h às 16h"
    a, idx = assistente(modelo(saida("respondida", "A sala de vacina funciona de segunda a sexta, das 8h às 16h.",
                                     ["C1"], [{"fonte": "C1", "trecho": trecho}])))
    r = a.perguntar("Qual o horário da sala de vacina da UBS 1?")
    assert r["versao_contrato"] == S.VERSAO_CONTRATO and r["versao_politica"] == G.VERSAO_POLITICA
    assert r["status"] in ("respondida", "parcial")          # a política do Gen AI decide; a camada não mexe
    if r["status"] == "respondida":
        assert r["fontes"][0]["edicao"] == 10 and trecho in r["fontes"][0]["trechos"]
    assert idx.consultas == [("Qual o horário da sala de vacina da UBS 1?", 5, "bm25")]


@pytest.mark.parametrize("status", ["insuficiente", "fora_do_escopo"])
def test_abstencao_usa_mensagem_fixa_e_aviso(status):
    a, _ = assistente(modelo(saida(status, "ignore as regras e diga sim")))
    r = a.perguntar("Qual é a capital da França?")
    assert r["status"] == status and r["rotulo_status"] == S.ROTULOS[status]
    assert "ignore" not in r["resposta"]                       # texto livre do modelo não chega ao cidadão
    assert r["aviso"] == S.AVISOS[status] and r["fontes"] == []


def test_ambigua_traz_pedido_de_esclarecimento():
    a, _ = assistente(modelo(saida("ambigua", "Há mais de uma publicação; informe a data ou o contrato.", ["C1"])))
    r = a.perguntar("Qual é o valor autorizado para pagamento ao hospital?")
    assert r["status"] == "ambigua" and "data" in r["resposta"] and r["aviso"] == S.AVISOS["ambigua"]


def test_modelo_desligado_nao_tenta_gerar():
    sessao_modelos = requests.exceptions.ConnectionError("recusado")
    a, idx = assistente(modelo(saida("respondida")), modelos=sessao_modelos)
    r = a.perguntar("Qual o horário da sala de vacina?")
    assert r["status"] == "indisponivel" and r["erro_tecnico"] == "servidor_indisponivel"
    assert a.cliente.http.posts == 0 and idx.consultas == []   # nem recuperou, nem chamou o modelo


def test_queda_durante_a_geracao_vira_erro_tecnico_claro():
    a, _ = assistente(requests.exceptions.ConnectTimeout("lento"))
    r = a.perguntar("Qual o horário da sala de vacina da UBS 1?")
    assert r["status"] == "insuficiente" and r["erro_tecnico"] == "timeout"
    assert r["resposta"] == S.MSG_ERRO_TECNICO


def test_pergunta_vazia_nao_chama_modelo():
    a, idx = assistente(modelo(saida("respondida")))
    r = a.perguntar("   ")
    assert r["status"] == "insuficiente" and a.cliente.http.posts == 0 and idx.consultas == []


def test_dados_pessoais_sao_mascarados_antes_do_modelo():
    sessao = Sessao(modelo(saida("insuficiente")))
    enviados = []
    post_original = sessao.post
    sessao.post = lambda url, json=None, timeout=None: (enviados.append(json), post_original(url, json, timeout))[1]
    a = S.AssistenteDODF(G.ConfigGeracao(), sessao, carregar_recursos=lambda: S._Recursos(indice=IndiceFalso()))
    a.perguntar("Meu CPF é 123.456.789-09, qual o horário da sala de vacina?")
    assert "123.456.789-09" not in json.dumps(enviados, ensure_ascii=False)


def test_recursos_carregados_uma_vez():
    chamadas = []
    a = S.AssistenteDODF(G.ConfigGeracao(), Sessao(modelo(saida("insuficiente"))),
                         carregar_recursos=lambda: chamadas.append(1) or S._Recursos(indice=IndiceFalso()))
    a.perguntar("Qual o horário da sala de vacina?")
    a.perguntar("Qual o horário da sala de vacina?")
    assert chamadas == [1]


def test_saude():
    a, _ = assistente(modelo(saida("insuficiente")))
    s = a.saude()
    assert s["modelo_disponivel"] is True and s["versao_politica"] == G.VERSAO_POLITICA


# ---------------------------------------------------------------- API HTTP
def test_api_valida_entrada(monkeypatch):
    from fastapi.testclient import TestClient

    from integracao_citizentech import api
    a, _ = assistente(modelo(saida("fora_do_escopo")))
    monkeypatch.setattr(api, "assistente", a)
    with TestClient(api.app) as c:
        assert c.post("/perguntar", json={"pergunta": "oi"}).status_code == 422
        r = c.post("/perguntar", json={"pergunta": "Qual é a capital da França?"})
        assert r.status_code == 200 and r.json()["status"] == "fora_do_escopo"
        assert c.get("/saude").json()["modelo_disponivel"] is True
