"""Etapa 4.4 / Fase 4B (PREPARACAO, nao validada) - relacoes/3: dimensoes de associacao separadas. Aditivo: nenhuma decisao do pipeline muda."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_fase4a import ITEM_AP, ITEM_HR, MEMB, Q87, Q_AP, T_AP_HR, cat_a, chunk, entregue, itens_o, o87, rels, rodar  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402

CMP_OK = {"estado": "confirmada", "justificativa": "destinatario igual"}
CMP_CONF = {"estado": "conflitante", "justificativa": "destinatario diferente"}
CMP_NV = {"estado": "nao_verificavel", "justificativa": "sem destinatario no registro"}
ROT_OK = {"rotulo": "objeto", "familia": "OBJETO"}
ROT_MEMBRO = {"rotulo": "titular", "familia": "MEMBRO"}


def dim(**kw):
    base = dict(nomes_q=["alfa"], nomes_no_trecho=["alfa"], cab="itens", fam="OBJETO", rot=ROT_OK, estado_rotulo="compativel", cue=None, dq="atencao primaria", dt="atencao primaria",
                cmp=CMP_OK, lq=[], loc_registro=None, loc_pub=None)
    base.update(kw)
    return EV.dimensoes_da_relacao(**base)


def test_esquema_e_campos_por_dimensao():
    assert EV.SCHEMA_RELACOES == "relacoes/3"
    r = dim()
    assert set(r["dimensoes"]) == {"entidade", "destinatario", "atributo", "localidade"}
    for v in r["dimensoes"].values():
        assert v["estado"] in EV.ESTADOS_DIM and v["justificativa"] and v["origem"]


def test_destinatario_correto_atributo_incorreto_nao_confirma_a_relacao():
    r = dim(rot=ROT_MEMBRO, estado_rotulo="conflito", fam="COMPETENCIA", cab="competencias")
    assert r["dimensoes"]["destinatario"]["estado"] == "confirmada" and r["dimensoes"]["atributo"]["estado"] == "conflitante"
    assert r["estado_geral"] == "conflitante"


def test_destinatario_conflitante_atributo_correto_continua_conflitante():
    r = dim(cmp=CMP_CONF, dt="hospital regional do guara")
    assert r["dimensoes"]["atributo"]["estado"] == "confirmada" and r["dimensoes"]["destinatario"]["estado"] == "conflitante"
    assert r["estado_geral"] == "conflitante"


def test_localidade_confirmada_atributo_nao_verificavel_nao_vira_confirmada():
    r = dim(estado_rotulo="desconhecido", rot=None, lq=["guara"], loc_registro=["guara"], loc_pub=True)
    assert r["dimensoes"]["localidade"]["estado"] == "confirmada" and r["dimensoes"]["atributo"]["estado"] == "nao_verificavel"
    assert r["estado_geral"] == "nao_verificavel"


def test_todas_as_dimensoes_confirmadas():
    r = dim(lq=["guara"], loc_registro=["guara"], loc_pub=True)
    assert all(v["estado"] == "confirmada" for v in r["dimensoes"].values()) and r["estado_geral"] == "confirmada"


def test_ausencia_de_informacao_nao_e_confirmacao():
    r = dim(nomes_no_trecho=[], estado_rotulo="desconhecido", rot=None, dq=None, dt=None, cmp=CMP_NV, lq=["guara"], loc_registro=None, loc_pub=None)
    d = r["dimensoes"]
    assert d["entidade"]["estado"] == "nao_verificavel" and d["destinatario"]["estado"] == "nao_aplicavel" and d["atributo"]["estado"] == "nao_verificavel"
    assert d["localidade"]["estado"] == "nao_verificavel" and r["estado_geral"] == "nao_verificavel"


def test_localidade_conflitante_da_publicacao():
    r = dim(lq=["guara"], loc_registro=None, loc_pub=False)
    assert r["dimensoes"]["localidade"] == {**r["dimensoes"]["localidade"], "estado": "conflitante", "origem": "publicacao"} and r["estado_geral"] == "conflitante"


# ------------------------------------------------------------- integrados: campos antigos preservados + dimensoes no registro, decisoes iguais as da 4A
def test_integrado_destinatario_correto_e_dimensoes_no_registro():
    o = itens_o("Foi adquirido VITAMINA D 400 UI/G.", [f"Código SES 90462 - {ITEM_AP}, para atender as necessidades da Atenção Primária"])
    r = rodar(Q_AP, [chunk(1, T_AP_HR, 495)], o, catalogo=cat_a({495: (T_AP_HR, ["Guará"])}))
    assert entregue(r)
    x = [x for x in rels(r) if x["destinatario_no_trecho"]][0]
    assert x["estado_associacao"] == "confirmada" and x["dimensoes"]["destinatario"]["estado"] == "confirmada" and "estado_geral" in x
    assert x["dimensoes"]["localidade"]["estado"] in ("confirmada", "nao_verificavel")      # nao herda a confirmacao do destinatario


def test_integrado_destinatario_conflitante_val_083_mantem_bloqueio():
    o = itens_o(f"Foram adquiridos {ITEM_AP} e {ITEM_HR}.", [f"Código SES 90462 - {ITEM_AP}, para atender as necessidades da Atenção Primária", f"Código SES 37167 - {ITEM_HR}, para atender"])
    r = rodar(Q_AP, [chunk(1, T_AP_HR, 495)], o, catalogo=cat_a({495: (T_AP_HR, ["Guará"])}))
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["destinatario_conflitante"]
    assert any(x["dimensoes"]["destinatario"]["estado"] == "conflitante" and x["estado_geral"] == "conflitante" and x["bloqueia"] for x in rels(r))


def test_integrado_atributo_conflitante_registrado_na_dimensao():
    c = chunk(1, "Art. 2º Designar membros da Coordenação de Regulação da Região Sul (CRSSU) em 2025: 4 - Titular: Diretor do Hospital Regional do Gama (HRG).", 174)
    r = rodar(Q87, [c], o87("A Coordenação é composta pelo Diretor do HRG.", [("C1", "Titular: Diretor do Hospital Regional do Gama (HRG)")]))
    assert r.status == "insuficiente"
    x = rels(r)[0]
    assert x["dimensoes"]["atributo"]["estado"] == "conflitante" and x["estado_geral"] == "conflitante" and x["estado"] == "conflito"
