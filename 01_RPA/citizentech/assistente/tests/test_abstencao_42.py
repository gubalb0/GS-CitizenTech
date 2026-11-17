"""Etapa 4.2 — politica conservadora de abstencao (identificabilidade da publicacao)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from citizentech.assistente import evidencias as EV  # noqa: E402
from citizentech.assistente import geracao as G  # noqa: E402
from citizentech.assistente.catalogo import Catalogo  # noqa: E402
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
        self.rs = list(rs)

    def post(self, url, json=None, timeout=None):
        return self.rs.pop(0) if len(self.rs) > 1 else self.rs[0]


def cli(*rs):
    return ClienteLMStudio(ConfigGeracao(), Sessao(*rs))


def saida(status="respondida", resposta="x", fontes=None, evid=None, just="", cand=None):
    return {"candidatas": cand or [], "status": status, "resposta": resposta, "fontes": fontes or [], "evidencias": evid or [], "justificativa": just}


def ev(f, t):
    return {"fonte": f, "trecho": t}


def doc(i, texto, ref=None, data="2025-06-05", tipo="Reconhecimento de dívida", **kw):
    d = {"id": i, "edicao": 90 + i, "data_edicao": data, "secao": "Seção III", "referencia": ref or f"0000{i}/2024", "tipo_documento": tipo,
         "numero_documento": "RECONHECIMENTO DE DÍVIDA", "texto_completo": texto, "localidades": [], "tipo_unidade": [], "ids_equivalentes": [i]}
    d.update(kw)
    return d


def res(d, pos=1):
    m = {k: d[k] for k in ("edicao", "data_edicao", "secao", "referencia", "tipo_documento", "numero_documento")}
    m.update({"ordem": 0, "n_chunks_doc": 1})
    return Resultado(pos, f"dodf-{d['id']}:est300o30:0000", d["id"], 20.0 - pos, d["texto_completo"], d["ids_equivalentes"], {"bm25": pos}, m)


SL1 = doc(1, "Interessado: HOSPITAL SANTA LÚCIA. Valor: R$57.102,73 (cinquenta e sete mil), Termo de Credenciamento nº 223/2021.", data="2025-03-05")
SL2 = doc(2, "Interessado: HOSPITAL SANTA LÚCIA. Valor: R$131,05 (cento e trinta e um reais), Termo de Credenciamento nº 382/2021.", data="2025-11-17")
PN = doc(3, "Interessado: HOSPITAL PRONTONORTE. Valor: R$419,04 (quatrocentos e dezenove reais), Termo de Credenciamento nº 91/2020.", data="2025-05-29")
COM = doc(4, "O prazo máximo para a Comissão Eleitoral da Candangolândia concluir o processo eleitoral é de 60 (sessenta) dias, a contar da publicação do ato.",
          tipo="Resolução", ref="12/2025", numero_documento="RESOLUÇÃO Nº 12/2025")
COM_REP = doc(5, "RESOLUÇÃO republicada. O prazo máximo para a Comissão Eleitoral da Candangolândia concluir o processo eleitoral é de 60 (sessenta) dias, a contar da publicação do ato.",
              tipo="Resolução", ref="12/2025", numero_documento="RESOLUÇÃO Nº 12/2025 (*)", data="2025-06-01")
GIGANTE = doc(6, "Pauta do tribunal. Hospital Santa Lúcia. " + " ".join(f"item{i} palavra{i}" for i in range(2000)) + " valor total. " +
              " ".join(f"outro{i}" for i in range(2000)) + " dívida reconhecida.", tipo="Extrato de pauta", ref="41/2025", numero_documento="EXTRATO DE PAUTA")


def resp_A(valor="R$57.102,73", trecho="Valor: R$57.102,73"):
    return saida(resposta=f"O valor é {valor}.", fontes=["C1"], evid=[ev("C1", trecho)])


# ---------------------------------------------------------------- 1. especifica sem identificadores suficientes -> abstencao
def test_pergunta_especifica_sem_identificadores_suficientes_abstem_se():
    cat = Catalogo([SL1, SL2, PN])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(SL1)], cli(ok(resp_A())), catalogo=cat)
    assert r.status == "ambigua" and r.verificacao["divergencia"] == "publicacao_nao_identificavel"
    assert "R$57.102,73" not in r.resposta and "R$131,05" not in r.resposta           # nenhum valor entregue
    assert "Informe a data, o número ou o documento" in r.resposta and "00002/2024" in r.resposta      # lista a outra publicacao
    assert r.telemetria["identificabilidade"]["n_concorrentes"] == 1 and "R$57.102,73" in r.telemetria["resposta_modelo_descartada"]


# ---------------------------------------------------------------- 2. especifica com publicacao identificavel -> resposta
def test_pergunta_especifica_com_publicacao_identificavel_responde_normalmente():
    cat = Catalogo([SL1, SL2, PN])
    o = saida(resposta="O valor é R$419,04.", fontes=["C1"], evid=[ev("C1", "Valor: R$419,04")])
    r = gerar_resposta("Qual o valor da dívida reconhecida ao Hospital Prontonorte?", [res(PN)], cli(ok(o)), catalogo=cat)
    assert r.status == "respondida" and r.verificacao["completude"] == "completa" and "Fonte: Reconhecimento de dívida 00003/2024" in r.resposta
    assert r.telemetria["identificabilidade"]["n_concorrentes"] == 0 and r.fontes[0]["doc_id"] == 3
    # com numero que distingue a publicacao entre as do mesmo hospital
    r2 = gerar_resposta("Qual o valor do Termo de Credenciamento nº 223/2021 do Hospital Santa Lúcia?", [res(SL1)], cli(ok(resp_A())), catalogo=cat)
    assert r2.status == "respondida"


# ---------------------------------------------------------------- 3. duas publicacoes concorrentes -> ambiguidade
def test_duas_publicacoes_concorrentes_no_contexto_geram_ambiguidade_sem_entregar_valor():
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(SL1, 1), res(SL2, 2)], cli(ok(resp_A())), catalogo=Catalogo([SL1, SL2]))
    assert r.status == "ambigua" and r.verificacao["divergencia"] == "publicacoes_semelhantes"
    assert "R$57.102,73" not in r.resposta and "Informe a data" in r.resposta


# ---------------------------------------------------------------- 4. pergunta geral com evidencia suficiente -> responde
def test_pergunta_geral_com_evidencia_suficiente_continua_respondivel():
    o = saida(resposta="O prazo máximo é de 60 dias.", fontes=["C1"], evid=[ev("C1", "concluir o processo eleitoral é de 60 (sessenta) dias")])
    r = gerar_resposta("Qual é o prazo máximo para a Comissão Eleitoral da Candangolândia concluir o processo eleitoral?", [res(COM)], cli(ok(o)), catalogo=Catalogo([COM, SL1]))
    assert r.status == "respondida"
    # republicacao do mesmo ato (mesmo trecho): nao e ambiguidade
    r2 = gerar_resposta("Qual é o prazo máximo para a Comissão Eleitoral da Candangolândia concluir o processo eleitoral?", [res(COM)], cli(ok(o)), catalogo=Catalogo([COM, COM_REP]))
    assert r2.status == "respondida" and r2.telemetria["identificabilidade"]["n_concordantes"] == 1


def test_documento_gigante_com_termos_dispersos_nao_e_concorrente():
    cat = Catalogo([SL1, GIGANTE])
    r = gerar_resposta("Qual o valor da dívida reconhecida ao Hospital Santa Lúcia?", [res(SL1)], cli(ok(resp_A())), catalogo=cat)
    assert r.status == "respondida"        # o gigante contem as palavras, mas distantes entre si (fora da janela)


def test_concorrente_que_sustenta_o_mesmo_fato_nao_gera_ambiguidade():
    outro = doc(7, "Outro ato. O valor pago ao HOSPITAL SANTA LÚCIA foi R$57.102,73 conforme o mesmo processo, republicação com texto diferente.", data="2025-04-01")
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(SL1)], cli(ok(resp_A())), catalogo=Catalogo([SL1, outro]))
    assert r.status == "respondida" and r.telemetria["identificabilidade"]["n_concordantes"] == 1


# ---------------------------------------------------------------- 5. MULTI / lista com cobertura incompleta -> parcial
def test_pergunta_multi_continua_parcial_com_aviso():
    o = saida(resposta="Foram adquiridas seringas.", fontes=["C1"], evid=[ev("C1", "seringas")])
    d = doc(8, "Hospital Regional de Planaltina: aquisição de seringas descartáveis, dispensa nº 5/2025.", tipo="Extrato")
    r = gerar_resposta("Quais itens foram adquiridos para o Hospital Regional de Planaltina?", [res(d)], cli(ok(o)), catalogo=Catalogo([d, SL1]))
    assert r.status == "parcial" and "resposta parcial" in r.resposta and r.verificacao["completude"] == "lista_nao_exaustiva"


# ---------------------------------------------------------------- 6. composta -> partes independentes
def test_pergunta_composta_partes_independentes_com_catalogo():
    cat = Catalogo([SL1, SL2, PN])
    oa = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")], cand=[{"fonte": "C1", "resposta_possivel": "R$57.102,73"}])
    ob = saida(resposta="O valor é R$419,04.", fontes=["C1"], evid=[ev("C1", "Valor: R$419,04")], cand=[{"fonte": "C1", "resposta_possivel": "R$419,04"}])
    rec = lambda p: [res(SL1)] if "Santa" in p else [res(PN)]    # noqa: E731
    r = gerar_resposta_composta("Qual o valor do Termo de Credenciamento nº 223/2021 do Hospital Santa Lúcia? E também: qual o valor da dívida do Hospital Prontonorte?",
                                rec, cli(ok(oa), ok(ob)), catalogo=cat)
    assert r.status == "respondida" and "R$57.102,73" in r.resposta and "R$419,04" in r.resposta
    assert [p["status"] for p in r.telemetria["partes"]] == ["respondida", "respondida"]


# ---------------------------------------------------------------- 7. publicacao errada com valor semelhante -> bloqueio/abstencao
def test_publicacao_errada_com_valor_semelhante_e_bloqueada():
    errada = doc(9, "Interessado: HOSPITAL SANTA LÚCIA. Valor: R$57.102,70 (cinquenta e sete mil), Termo nº 224/2021.", data="2025-03-05")
    o = saida(resposta="O valor é R$57.102,70.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,70")])
    r = gerar_resposta("Qual o valor do Termo de Credenciamento nº 223/2021 do Hospital Santa Lúcia?", [res(errada)], cli(ok(o)), catalogo=Catalogo([SL1, errada]))
    assert r.status == "insuficiente" and any("numero=223/2021" in p for p in r.verificacao["problemas"])
    # hospital certo, outra publicacao no corpus com outro valor e sem numero na pergunta -> abstem-se
    r2 = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(errada)], cli(ok(o)), catalogo=Catalogo([SL1, errada]))
    assert r2.status == "ambigua" and "R$57.102,70" not in r2.resposta


# ---------------------------------------------------------------- 8. ausencia de fonte correta -> nenhuma resposta completa indevida
def test_ausencia_da_fonte_correta_nao_gera_resposta_completa():
    """So existe no contexto uma publicacao semelhante (outra instancia); a correta (Termo 223/2021) nao foi recuperada."""
    cat = Catalogo([SL1, SL2, PN])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(SL2)], cli(ok(resp_A("R$131,05", "Valor: R$131,05"))), catalogo=cat)
    assert r.status != "respondida" and r.status != "parcial" and "R$131,05" not in r.resposta
    r_h = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(PN)], cli(ok(resp_A("R$419,04", "Valor: R$419,04"))), catalogo=cat)
    assert r_h.status == "insuficiente"       # outro hospital: reprovada pelo alinhamento


# ---------------------------------------------------------------- sem catalogo: heuristica conservadora; unidades do catalogo
def test_sem_catalogo_exige_discriminador_e_nao_entrega_valor():
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(SL1)], cli(ok(resp_A())))
    assert r.status == "ambigua" and r.telemetria["identificabilidade"]["motivo"] == "heuristica_sem_catalogo" and "R$57.102,73" not in r.resposta
    r2 = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia em 2025?", [res(SL1)], cli(ok(resp_A())))
    assert r2.status == "respondida"


def test_catalogo_unidade():
    cat = Catalogo([SL1, SL2, COM])
    assert len(cat) == 3 and cat.canonico(2) == 2
    r = cat.concorrentes("Qual o valor pago ao Hospital Santa Lúcia?", 1)
    assert r["avaliavel"] and [c["id"] for c in r["concorrentes"]] == [2]
    assert not cat.concorrentes("Qual o valor?", 999)["avaliavel"]
    assert EV.tokens_especificos("O valor é R$57.102,73 pago ao Hospital SANTA LÚCIA em 2025 (12 meses).", "Qual o valor?") == ["r$57.102,73", "lucia"] or "r$57.102,73" in EV.tokens_especificos("O valor é R$57.102,73.", "q?")
    assert G.VERSAO_POLITICA.startswith("fail-closed-4.")
