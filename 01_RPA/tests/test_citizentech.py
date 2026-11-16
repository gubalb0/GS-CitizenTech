import csv
import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from citizentech import classificador, config, pipeline, regras  # noqa: E402
from citizentech.estado import Estado  # noqa: E402
from citizentech.geo import ConsultaCEP  # noqa: E402
from citizentech.ingestao import Registro, ler_inbox  # noqa: E402
from citizentech.texto import mascarar_pii  # noqa: E402
from citizentech.validacao import validar  # noqa: E402


@pytest.fixture(scope="module")
def modelo():
    return classificador.treinar(salvar_em=None)


class RespostaFalsa:
    def __init__(self, dados, status=200):
        self.dados, self.status = dados, status

    def raise_for_status(self):
        if self.status >= 400:
            raise requests.HTTPError(str(self.status))

    def json(self):
        return self.dados


class SessaoFalsa:
    def __init__(self, respostas):
        self.respostas, self.n = list(respostas), 0

    def get(self, url, timeout):
        self.n += 1
        r = self.respostas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


# ---- validacao / dados invalidos
@pytest.mark.parametrize("texto,cep,esperado", [
    ("", "", "texto_vazio"), ("buraco", "", "texto_curto_demais"),
    ("Texto valido e suficientemente longo.", "123", "cep_invalido"),
])
def test_validacao_rejeita(texto, cep, esperado):
    assert esperado in validar(Registro("1", texto, cep, "x"))


def test_validacao_aceita():
    assert validar(Registro("1", "A farmacia do posto esta sem insulina ha dias.", "01001-000", "x")) == []


def test_mascara_pii():
    t, mudou = mascarar_pii("CPF 123.456.789-09 email a@b.com tel (11) 91234-5678")
    assert mudou and "123.456" not in t and "a@b.com" not in t and "91234" not in t


# ---- ingestao: arquivos ausentes/corrompidos
def test_inbox_ausente(tmp_path):
    regs, falhas = ler_inbox(tmp_path / "nao_existe")
    assert regs == [] and falhas[0]["motivo"] == "diretorio_ausente"


def test_arquivo_corrompido_nao_derruba_lote(tmp_path):
    (tmp_path / "a.csv").write_bytes(b"\xff\xfe\x00\x81lixo")
    (tmp_path / "b.csv").write_text("id,texto,cep\n1,A farmacia do posto esta sem insulina ha dias.,\n", encoding="utf-8")
    regs, falhas = ler_inbox(tmp_path)
    assert len(regs) == 1 and len(falhas) == 1


# ---- IA
def test_ia_qualidade_minima(modelo):
    with config.ARQ_TESTE.open(encoding="utf-8") as fh:
        teste = list(csv.DictReader(fh))
    acertos = sum(classificador.classificar(modelo, r["texto"])[0] == r["categoria"] for r in teste)
    assert acertos / len(teste) >= 0.70  # guarda de regressao; valor medido ~0.74


def test_ia_fallback_palavras_chave():
    cat, conf, metodo = classificador.classificar(None, "Quero marcar uma consulta")
    assert cat == "agendamento_consulta" and metodo == "palavras_chave" and conf < config.CONFIANCA_MINIMA


def test_fallback_texto_desconhecido():
    assert classificador.classificar(None, "xyzzy qwerty")[0] == "indefinida"


# ---- regras
def test_regra_urgencia_e_revisao():
    d = regras.decidir("sintomas_urgentes", 0.95, "Estou com dor no peito e falta de ar")
    assert d["prioridade"] == "alta" and d["prazo_horas"] == 1 and d["status"] == "revisao_humana"
    # urgencia clinica detectada por regra mesmo se a IA errar a categoria -> humano
    assert regras.decidir("informacoes_gerais", 0.95, "meu pai desmaiou")["status"] == "revisao_humana"
    assert regras.decidir("agendamento_consulta", 0.2, "texto qualquer")["status"] == "revisao_humana"
    ok = regras.decidir("vacinacao", 0.9, "quero saber da vacina da gripe")
    assert ok["status"] == "encaminhado" and ok["prioridade"] == "normal" and ok["prazo_horas"] == 72


def test_resposta_urgente_traz_aviso_192():
    assert "192" in pipeline.gerar_resposta("P1", "x", 1, "revisao_humana", "alta")
    assert "192" not in pipeline.gerar_resposta("P1", "x", 72, "encaminhado", "normal")


# ---- API com retry / falhas
def test_retry_e_sucesso():
    s = SessaoFalsa([requests.Timeout(), RespostaFalsa({"bairro": "Se", "localidade": "Sao Paulo", "uf": "SP"})])
    api = ConsultaCEP(sessao=s, retries=3, backoff=0)
    assert api.buscar("01001000")["fonte"] == "viacep" and s.n == 2


def test_api_sempre_falha_nao_levanta():
    api = ConsultaCEP(sessao=SessaoFalsa([requests.ConnectionError()] * 3), retries=3, backoff=0)
    assert api.buscar("01001000")["fonte"] == "indisponivel"


def test_resposta_inesperada_tratada():
    api = ConsultaCEP(sessao=SessaoFalsa([RespostaFalsa(["x"])] * 2), retries=2, backoff=0)
    assert api.buscar("01001000")["fonte"] == "indisponivel"


def test_circuit_breaker():
    s = SessaoFalsa([requests.Timeout()] * 20)
    api = ConsultaCEP(sessao=s, retries=1, backoff=0)
    for cep in ["11111111", "22222222", "33333333", "44444444", "55555555"]:
        api.buscar(cep)
    assert s.n == 3 and api.buscar("66666666")["motivo"] == "circuit_breaker_aberto"


# ---- pipeline
def _inbox(tmp_path):
    d = tmp_path / "in"
    d.mkdir()
    (d / "a.csv").write_text(
        "id,texto,cep\n"
        "1,Quero marcar uma consulta com o clinico geral do posto.,\n"
        "2,Quero marcar uma consulta com o clinico geral do posto.,\n"
        "3,,\n"
        "4,A farmacia do posto esta sem insulina ha duas semanas.,abc\n", encoding="utf-8")
    return d


def test_pipeline_duplicado_invalido_e_idempotencia(tmp_path, modelo):
    est = Estado(tmp_path / "e.db")
    kw = dict(estado=est, cep_api=ConsultaCEP(sessao=SessaoFalsa([]), retries=1, backoff=0), modelo=modelo)
    r = pipeline.executar(_inbox(tmp_path), tmp_path / "s", **kw)
    assert (r["processados"], r["duplicados_ignorados"], r["rejeitados_invalidos"]) == (1, 1, 2)
    r2 = pipeline.executar(tmp_path / "in", tmp_path / "s2", **kw)
    assert r2["processados"] == 0 and r2["duplicados_ignorados"] == 2


def test_erro_isolado_nao_interrompe(tmp_path, modelo, monkeypatch):
    original = pipeline.processar_registro

    def quebra(r, *a, **k):
        if r.id == "1":
            raise RuntimeError("falha simulada")
        return original(r, *a, **k)

    (tmp_path / "in").mkdir()
    (tmp_path / "in" / "a.csv").write_text(
        "id,texto,cep\n1,Quero marcar uma consulta com o clinico geral do posto.,\n"
        "2,A farmacia do posto esta sem insulina ha duas semanas.,\n", encoding="utf-8")
    monkeypatch.setattr(pipeline, "processar_registro", quebra)
    r = pipeline.executar(tmp_path / "in", tmp_path / "s", estado=Estado(tmp_path / "e.db"),
                          cep_api=ConsultaCEP(sessao=SessaoFalsa([]), retries=1, backoff=0), modelo=modelo)
    assert r["erros_processamento"] == 1 and r["processados"] == 1
