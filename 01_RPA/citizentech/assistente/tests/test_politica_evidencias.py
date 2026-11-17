"""Etapa 4.1 — politica fail-closed: alinhamento, sustentacao, periodo, conflitos, concorrentes, parcial/MULTI, compostas."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from citizentech.assistente import evidencias as EV  # noqa: E402
from citizentech.assistente import geracao as G  # noqa: E402
from citizentech.assistente.geracao import ClienteLMStudio, ConfigGeracao, gerar_resposta, gerar_resposta_composta  # noqa: E402
from citizentech.assistente.retriever import Resultado  # noqa: E402


class Resp:
    def __init__(self, corpo):
        self.status_code, self._c, self.text = 200, corpo, ""

    def json(self):
        return self._c


def ok(o):
    return Resp({"choices": [{"message": {"content": json.dumps(o, ensure_ascii=False)}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 900, "completion_tokens": 80}})


class Sessao:
    def __init__(self, *rs):
        self.rs, self.n = list(rs), 0

    def post(self, url, json=None, timeout=None):
        self.n += 1
        return self.rs.pop(0) if len(self.rs) > 1 else self.rs[0]


def cli(*rs):
    return ClienteLMStudio(ConfigGeracao(), Sessao(*rs))


def res(i, texto, doc=None, data="2025-06-05", tipo="Reconhecimento de dívida", ref=None, **meta):
    m = {"edicao": 90 + i, "data_edicao": data, "secao": "Seção III", "referencia": ref if ref is not None else f"0000{i}/2024", "tipo_documento": tipo,
         "numero_documento": "RECONHECIMENTO DE DÍVIDA", "ordem": 0, "n_chunks_doc": 1}
    m.update(meta)
    return Resultado(i, f"dodf-{doc or i}:est300o30:0000", doc or i, 20.0 - i, texto, [doc or i], {"bm25": i}, m)


def saida(status="respondida", resposta="x", fontes=None, evid=None, just="", cand=None):
    return {"candidatas": cand or [], "status": status, "resposta": resposta, "fontes": fontes or [], "evidencias": evid or [], "justificativa": just}


def ev(f, t):
    return {"fonte": f, "trecho": t}


def cand(f, t):
    return {"fonte": f, "resposta_possivel": t}


HOSP_A = "Interessado: HOSPITAL SANTA LÚCIA. Valor: R$57.102,73 (cinquenta e sete mil), relativo ao Termo de Credenciamento nº 223/2021, em 03/03/2025."
HOSP_A2 = "Interessado: HOSPITAL SANTA LÚCIA. Valor: R$131,05 (cento e trinta e um reais), relativo ao Termo de Credenciamento nº 382/2021, em 17/11/2025."
HOSP_B = "Interessado: HOSPITAL PRONTONORTE. Valor: R$419,04 (quatrocentos e dezenove reais), relativo ao Termo de Credenciamento nº 91/2020."
CHAM_259 = "O Instituto torna público o Chamamento nº 259/2025, até 31/10/2025, Aquisição de equipamentos para o Hospital da Criança de Brasília José Alencar."
CHAM_270 = "Resultado do Chamamento nº 270/2025: Aquisição de Medicamento (Pazopanibe) para o Hospital da Criança de Brasília José Alencar."


# ------------------------------------------------------------------ funcoes puras
def test_tipo_da_pergunta():
    assert EV.eh_singular("Qual é o valor autorizado?") and not EV.eh_lista("Qual é o valor autorizado?")
    assert EV.eh_lista("Quais itens foram adquiridos?") and not EV.eh_singular("Quais itens foram adquiridos?")
    assert EV.eh_lista("Qual hospital foi citado conforme as publicações do DODF?")


def test_termos_salientes_e_periodo():
    s = EV.termos_salientes("Qual o valor pago ao Hospital Santa Lúcia no Chamamento nº 270/2025 em junho de 2025?")
    assert set(s["nomes"]) >= {"santa", "lucia"} and "270/2025" in s["numeros"] and s["anos"] == ["2025"] and s["meses"] == ["junho"]
    assert "hospital" not in s["nomes"] and "chamamento" in s["nomes"]
    assert EV.periodo_ausente(s, "texto sem data", "2025-01-10") == ["junho"]
    assert EV.periodo_ausente(s, "texto", "2025-06-05") == []


def test_dividir_pergunta_composta():
    assert EV.dividir_pergunta_composta("Qual o valor do Hospital A? E também: qual o valor do Hospital B?") == ["Qual o valor do Hospital A?", "qual o valor do Hospital B?"]
    assert EV.dividir_pergunta_composta("Qual o valor pago ao Hospital Santa Lúcia?") == ["Qual o valor pago ao Hospital Santa Lúcia?"]
    assert len(EV.dividir_pergunta_composta("Qual o valor do hospital A? Quem assinou o contrato B?")) == 2


def test_classificacao_de_divergencias():
    c = lambda f, t, ids: {"fonte": f, "resposta_possivel": t, "literal": True, "ids_equivalentes": ids}   # noqa: E731
    d = {"C1": "2025-03-03", "C2": "2025-03-03", "C3": "2025-11-17"}
    assert EV.classificar_divergencia([c("C1", "R$ 10,00", [1]), c("C2", "R$ 20,00", [2])], d)["tipo"] == "divergentes_mesmo_periodo"
    assert EV.classificar_divergencia([c("C1", "R$ 10,00", [1]), c("C3", "R$ 20,00", [3])], d)["tipo"] == "periodos_diferentes"
    assert EV.classificar_divergencia([c("C1", "R$ 10,00", [1, 5]), c("C2", "R$ 20,00", [5])], d)["tipo"] == "duplicadas"
    assert EV.classificar_divergencia([c("C1", "R$ 10,00", [1]), c("C2", "R$10,00", [2])], d)["tipo"] == "respostas_equivalentes"
    assert EV.classificar_divergencia([{"fonte": "C1", "resposta_possivel": "R$ 1", "literal": False, "ids_equivalentes": [1]}], d)["tipo"] == "sem_divergencia"


# ------------------------------------------------------------------ fail-closed
def test_publicacao_semelhante_com_valor_diferente_nao_substitui_a_pedida():
    """Pergunta pede o Chamamento 270/2025; o modelo cita o 259/2025 (parecido): numero ausente na evidencia -> reprovada."""
    o = saida(resposta="O objeto é a aquisição de equipamentos.", fontes=["C1"], evid=[ev("C1", "Aquisição de equipamentos para o Hospital da Criança")])
    r = gerar_resposta("Qual é o objeto do Chamamento nº 270/2025 do Hospital da Criança de Brasília José Alencar?", [res(1, CHAM_259, tipo="Ineditorial", ref="CHAMAMENTO nº 259/2025")], cli(ok(o)))
    assert r.status == "insuficiente" and r.verificacao["rebaixada"]
    assert any(p.startswith("evidencia_nao_corresponde_a_pergunta") and "270/2025" in p for p in r.verificacao["problemas"])


def test_publicacao_correta_ausente_do_contexto_hospital_diferente():
    o = saida(resposta="O valor é R$419,04.", fontes=["C1"], evid=[ev("C1", "Valor: R$419,04")])
    r = gerar_resposta("Qual o valor da dívida reconhecida para o Hospital Santa Lúcia?", [res(1, HOSP_B)], cli(ok(o)))
    assert r.status == "insuficiente" and any("nome=santa" in p for p in r.verificacao["problemas"])


def test_valor_correto_associado_a_publicacao_errada():
    """O valor R$57.102,73 existe no C2, mas o hospital pedido (Prontonorte) esta no C1; a resposta cita C2."""
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C2"], evid=[ev("C2", "Valor: R$57.102,73")])
    r = gerar_resposta("Qual o valor da dívida do Hospital Prontonorte?", [res(1, HOSP_B), res(2, HOSP_A)], cli(ok(o)))
    assert r.status == "insuficiente" and any(p.startswith("evidencia_nao_corresponde_a_pergunta") for p in r.verificacao["problemas"])


def test_data_de_outro_periodo_reprova():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia em novembro de 2025?", [res(1, HOSP_A, data="2025-03-05")], cli(ok(o)))
    assert r.status == "insuficiente" and any("mes=novembro" in p for p in r.verificacao["problemas"])
    ok_r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia em março de 2025?", [res(1, HOSP_A, data="2025-03-05")], cli(ok(o)))
    assert ok_r.status == "respondida"


def test_citacao_existente_mas_que_nao_sustenta_a_afirmacao():
    """A evidencia e literal e o id existe, mas o nome/valor afirmado nao esta no trecho citado."""
    o = saida(resposta="O responsável foi Carlos Alberto Mendes.", fontes=["C1"], evid=[ev("C1", "Interessado: HOSPITAL SANTA LÚCIA")])
    r = gerar_resposta("Quem foi o responsável pelo pagamento ao Hospital Santa Lúcia?", [res(1, HOSP_A)], cli(ok(o)))
    assert r.status == "insuficiente" and any(p.startswith("afirmacoes_nao_sustentadas_pela_evidencia") and "carlos" in p for p in r.verificacao["problemas"])
    o2 = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Interessado: HOSPITAL SANTA LÚCIA")])     # valor existe no chunk, mas nao no trecho citado
    r2 = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(1, HOSP_A)], cli(ok(o2)))
    assert r2.status == "insuficiente"


def test_rastreabilidade_incompleta_reprova():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(1, HOSP_A, referencia=None, numero_documento=None)], cli(ok(o)))
    assert r.status == "insuficiente" and any(p.startswith("rastreabilidade_incompleta") for p in r.verificacao["problemas"])


def test_resposta_identifica_a_publicacao_e_so_com_dados_dos_metadados():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia em 2025?", [res(1, HOSP_A, doc=306, ref="00001791/2024")], cli(ok(o)))
    assert r.status == "respondida" and "Fonte: Reconhecimento de dívida 00001791/2024 (DODF edição 91, 2025-06-05, Seção III)" in r.resposta
    assert r.fontes[0]["doc_id"] == 306 and r.verificacao["completude"] == "completa"


# ------------------------------------------------------------------ conflito, periodos, duplicadas, concorrentes
def test_conflito_mesmo_periodo_nao_escolhe_arbitrariamente():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")], cand=[cand("C1", "R$57.102,73"), cand("C2", "R$131,05")])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(1, HOSP_A, data="2025-03-05"), res(2, HOSP_A2, data="2025-03-05")], cli(ok(o)))
    assert r.status == "ambigua" and r.verificacao["divergencia"] == "divergentes_mesmo_periodo" and "DIVERGENTES" in r.resposta
    assert "R$57.102,73" in r.resposta and "R$131,05" in r.resposta and len(r.fontes) == 2


def test_periodos_diferentes_sao_apresentados_com_datas():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")], cand=[cand("C1", "R$57.102,73"), cand("C2", "R$131,05")])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(1, HOSP_A, data="2025-03-05"), res(2, HOSP_A2, data="2025-11-18")], cli(ok(o)))
    assert r.status == "ambigua" and r.verificacao["divergencia"] == "periodos_diferentes" and "2025-03-05" in r.resposta and "2025-11-18" in r.resposta


def test_publicacoes_duplicadas_nao_geram_conflito():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")], cand=[cand("C1", "R$57.102,73"), cand("C2", "R$57.102,73")])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia em 2025?", [res(1, HOSP_A, doc=10), res(2, HOSP_A, doc=10)], cli(ok(o)))
    assert r.status == "respondida"


def test_publicacao_concorrente_igualmente_relevante_vira_ambigua_sem_candidatas():
    """O modelo nao listou candidatas, mas outra publicacao do mesmo hospital cobre os mesmos termos: nao pode substituir em silencio."""
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(1, HOSP_A), res(2, HOSP_A2)], cli(ok(o)))
    assert r.status == "ambigua" and r.verificacao["divergencia"] == "publicacoes_semelhantes" and len(r.fontes) == 2
    assert "R$57.102,73" not in r.resposta and "R$131,05" not in r.resposta and "R$57.102,73" in r.telemetria["resposta_modelo_descartada"]   # 4.2: o valor nao e entregue


def test_numero_da_pergunta_distingue_a_publicacao_e_evita_ambiguidade():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    r = gerar_resposta("Qual o valor do Termo de Credenciamento nº 223/2021 do Hospital Santa Lúcia?", [res(1, HOSP_A), res(2, HOSP_A2)], cli(ok(o)))
    assert r.status == "respondida"


def test_outra_publicacao_que_nao_cobre_os_termos_nao_e_concorrente():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia em 2025?", [res(1, HOSP_A), res(2, HOSP_B)], cli(ok(o)))
    assert r.status == "respondida"


# ------------------------------------------------------------------ parcial / MULTI
def test_pergunta_de_lista_nunca_e_resposta_completa():
    o = saida(resposta="Foram adquiridos seringas e luvas.", fontes=["C1"], evid=[ev("C1", "aquisição de seringas e luvas")])
    r = gerar_resposta("Quais itens foram adquiridos para o Hospital Regional de Planaltina?",
                       [res(1, "Hospital Regional de Planaltina: aquisição de seringas e luvas, conforme dispensa nº 5/2025.")], cli(ok(o)))
    assert r.status == "parcial" and "resposta parcial" in r.resposta and "pode haver outras publicações" in r.resposta and "Fonte:" in r.resposta
    assert r.verificacao["completude"] == "lista_nao_exaustiva"


def test_modelo_marca_parcial_e_o_codigo_mantem():
    o = saida("parcial", "Apenas o horário consta.", fontes=["C1"], evid=[ev("C1", "funciona das 8h às 16h")])
    r = gerar_resposta("Qual o horário e o endereço da sala de vacina?", [res(1, "A sala de vacina funciona das 8h às 16h.")], cli(ok(o)))
    assert r.status == "parcial"


def test_parcial_tambem_passa_pelo_verificador():
    o = saida("parcial", "O valor foi R$ 999,00.", fontes=["C1"], evid=[ev("C1", "funciona das 8h às 16h")])
    assert gerar_resposta("Quais valores?", [res(1, "A sala de vacina funciona das 8h às 16h.")], cli(ok(o))).status == "insuficiente"


# ------------------------------------------------------------------ pergunta composta
def test_pergunta_composta_nao_e_tratada_como_conflito():
    """Dois hospitais diferentes na mesma pergunta: partes independentes, ambas respondidas, sem 'ambigua'."""
    oa = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")], cand=[cand("C1", "R$57.102,73")])
    ob = saida(resposta="O valor é R$419,04.", fontes=["C1"], evid=[ev("C1", "Valor: R$419,04")], cand=[cand("C1", "R$419,04")])
    ctxs = {"santa": [res(1, HOSP_A)], "prontonorte": [res(1, HOSP_B)]}
    recuperar = lambda p: ctxs["santa"] if "Santa" in p else ctxs["prontonorte"]   # noqa: E731
    r = gerar_resposta_composta("Qual o valor pago ao Hospital Santa Lúcia em 2025? E também: qual o valor pago ao Hospital Prontonorte em 2025?", recuperar, cli(ok(oa), ok(ob)))
    assert r.status == "respondida" and "R$57.102,73" in r.resposta and "R$419,04" in r.resposta
    assert [p["status"] for p in r.telemetria["partes"]] == ["respondida", "respondida"] and len(r.fontes) == 2


def test_pergunta_composta_com_parte_sem_evidencia_e_parcial():
    oa = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    ob = saida("insuficiente", "x", just="não há informação")
    recuperar = lambda p: [res(1, HOSP_A)]   # noqa: E731
    r = gerar_resposta_composta("Qual o valor pago ao Hospital Santa Lúcia em 2025? E também: qual o endereço do Hospital Prontonorte em 2025?", recuperar, cli(ok(oa), ok(ob)))
    assert r.status == "parcial" and "não puderam ser verificadas" in r.resposta


def test_pergunta_simples_na_composta_delega():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    c = cli(ok(o))
    r = gerar_resposta_composta("Qual o valor pago ao Hospital Santa Lúcia em 2025?", lambda p: [res(1, HOSP_A)], c)
    assert r.status == "respondida" and c.http.n == 1


# ------------------------------------------------------------------ taxonomia
def test_status_validos_incluem_parcial():
    assert set(G.STATUS) == {"respondida", "parcial", "insuficiente", "ambigua", "fora_do_escopo"}
    assert "parcial" in G.ESQUEMA_SAIDA["properties"]["status"]["enum"]
    assert G.VERSAO_PROMPT == "v3" and G.VERSAO_POLITICA == "fail-closed-4.4.4d1-cand"


def test_telemetria_registra_versoes_e_scores():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(1, HOSP_A)], cli(ok(o)))
    assert r.telemetria["versao_prompt"] == "v3" and r.telemetria["scores_recebidos"] == [19.0]
