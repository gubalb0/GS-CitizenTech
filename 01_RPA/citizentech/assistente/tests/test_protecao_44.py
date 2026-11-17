"""Etapa 4.4 / Fase 3 - protecao contra respostas incorretas: a evidencia precisa sustentar o ATRIBUTO pedido (entidade, atributo, valor, periodo, localidade, escopo).

Cada mecanismo (M1..M5) tem teste positivo (evidencia suficiente), negativo (evidencia superficialmente parecida que nao responde ao atributo) e de regressao.
Nenhum mecanismo promove status: so rebaixa para `insuficiente` ou reescreve o texto de uma `parcial`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_geracao import cli, ok, saida  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402
from citizentech.assistente import geracao as G  # noqa: E402
from citizentech.assistente.geracao import gerar_resposta  # noqa: E402
from citizentech.assistente.retriever import Resultado  # noqa: E402


def chunk(pos, texto, doc, ordem=0, n=1, data="2025-07-02", **meta):
    m = {"edicao": 121, "data_edicao": data, "secao": "Seção III", "referencia": f"{doc}/2025", "tipo_documento": "Extrato",
         "numero_documento": f"EXTRATO {doc}", "ordem": ordem, "n_chunks_doc": n}
    m.update(meta)
    return Resultado(pos, f"dodf-{doc}:est300o30:{ordem:04d}", doc, 20.0 - pos, texto, [doc, 5000 + doc], {"bm25": pos}, m)


def rodar(pergunta, chunks, obj, catalogo=None):
    c, _ = cli(ok(obj))
    return gerar_resposta(pergunta, chunks, c, catalogo=catalogo)


def entregue(r):
    return r.status in ("respondida", "parcial")


# =============================================================== M1 - ausencia, remissao e cobertura
HOME = ("O Chefe do Departamento vem AUTORIZAR a inexigibilidade para credenciar a empresa HOSPITAL HOME, CNPJ: 37.108.388/0001-59, endereço: SGAS 613, Asa Sul, "
        "interessada em se credenciar nas especialidades elencadas na carta proposta doc. sei n° 160711978, para prestação de serviços aos policiais militares, "
        "conforme Edital de Credenciamento nº 01/2024, cujo objeto é SERVIÇOS ASSISTENCIAIS CLÍNICOS E CIRÚRGICOS ELETIVOS E DE URGÊNCIA E EMERGÊNCIA, 2025.")
OBJ = "SERVIÇOS ASSISTENCIAIS CLÍNICOS E CIRÚRGICOS ELETIVOS E DE URGÊNCIA E EMERGÊNCIA"


def resp_home(resposta):
    return saida(resposta=resposta, fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": OBJ}],
                 evid=[{"fonte": "C1", "trecho": "interessada em se credenciar nas especialidades elencadas na carta proposta doc. sei n° 160711978"}])


def test_unidades_de_m1():
    assert EV.cabeca_do_atributo("Quais especialidades médicas foram propostas pela empresa?") == "especialidades"
    assert EV.cabeca_do_atributo("Qual é o valor autorizado para pagamento?") == "valor"
    assert EV.cabeca_do_atributo("Quais são as competências da Coordenação?") == "competencias"
    assert EV.cabeca_do_atributo("Quem foi responsável pela autorização?") == "quem"
    assert EV.cabeca_do_atributo("Até quando serão recebidas propostas?") == "quando"
    assert EV.afirmacao_negativa("Não foram especificadas as denominações.") and EV.afirmacao_negativa("A proposta não especifica detalhes.")
    assert EV.afirmacao_negativa("O contrato não consta do extrato.")
    assert EV.afirmacao_negativa("O valor é R$ 10,00 para 30 dias.") is None and EV.afirmacao_negativa("Foram adquiridos três itens.") is None
    c = EV.cobertura_da_publicacao({"7": [{"ordem": 0, "n_chunks_doc": 3, "chunk_id": "a"}, {"ordem": 1, "n_chunks_doc": 3, "chunk_id": "b"}]})
    assert c["7"] == {"total": 3, "analisados": 2, "completa": False}
    assert EV.cobertura_da_publicacao({"7": [{"ordem": 0, "n_chunks_doc": 1, "chunk_id": "a"}]})["7"]["completa"]
    assert not EV.cobertura_da_publicacao({"7": [{"ordem": 0, "n_chunks_doc": None, "chunk_id": "a"}]})["7"]["completa"]      # total desconhecido: nunca "completa"


def test_m1_remissao_a_documento_nao_publicado_val_136():
    r = rodar("Quais especialidades médicas foram propostas pela empresa credenciada no Hospital Home em 2025?", [chunk(1, HOME, 94)], resp_home(f"As especialidades são {OBJ}."))
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["remissao_a_documento_nao_publicado"]
    assert "160711978" in r.resposta and "documento não publicado" in r.resposta
    assert "não existe" not in r.resposta.lower() and "não consta" not in r.resposta.lower()          # nao afirma ausencia
    assert r.verificacao["evidencia"]["protecao"]["remissao"]["sei"] == "160711978"


def test_m1_remissao_negativo_outro_atributo_na_mesma_publicacao_nao_bloqueia():
    r = rodar("Quais serviços foram credenciados pelo Hospital Home em 2025?", [chunk(1, HOME, 94)], resp_home(f"Foram credenciados {OBJ}."))
    assert entregue(r), r.verificacao                        # 'servicos' != 'especialidades': a remissao nao se aplica
    txt = HOME.replace("especialidades elencadas na carta", "valores elencados na tabela")
    r2 = rodar("Quais especialidades médicas foram propostas pelo Hospital Home em 2025?", [chunk(1, txt, 94)], resp_home(f"As especialidades são {OBJ}."))
    assert r2.verificacao.get("problemas") != ["remissao_a_documento_nao_publicado"]


def test_m1_negativa_com_contexto_parcial_nao_afirma_ausencia_val_039_141():
    texto = "Primeiro trecho do documento: grade de distribuição de São Sebastião, códigos SES P08000369 P08002053 e regiões de saúde em 2025."
    o = saida(resposta="Não foram especificadas as denominações das unidades.", fontes=["C1"], cand=[],
              evid=[{"fonte": "C1", "trecho": "grade de distribuição, códigos SES P08000369 P08002053"}])
    r = rodar("Quais unidades de saúde em São Sebastião receberão equipamentos em 2025?", [chunk(1, texto, 303, ordem=0, n=40)], o)
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["ausencia_nao_encontrada_contexto_parcial"]
    assert "1 de 40" in r.resposta and "não significa que ela não conste" in r.resposta
    assert r.verificacao["evidencia"]["protecao"]["afirmacao_negativa"]["cobertura"][list(r.verificacao["evidencia"]["protecao"]["afirmacao_negativa"]["cobertura"])[0]]["completa"] is False


def test_m1_negativa_apos_analise_integral_e_mensagem_distinta():
    texto = "Termo de credenciamento do hospital em 2025, sem lista de unidades."
    o = saida(resposta="Não consta a lista de unidades.", fontes=["C1"], cand=[], evid=[{"fonte": "C1", "trecho": "Termo de credenciamento do hospital em 2025"}])
    r = rodar("Quais unidades constam do termo de credenciamento do hospital em 2025?", [chunk(1, texto, 12, ordem=0, n=1)], o)
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["ausencia_apos_analise_integral"]
    assert "integralmente" in r.resposta and "não identifiquei" in r.resposta and "não significa" not in r.resposta
    assert r.resposta != G.MSG_NAO_ENCONTRADA                 # mensagens distintas para as tres situacoes
    # mesma negativa com a publicacao parcialmente analisada (2 de 3 trechos) usa a outra mensagem
    r2 = rodar("Quais unidades constam do termo de credenciamento do hospital em 2025?",
               [chunk(1, texto, 12, ordem=0, n=3), chunk(2, "Segundo trecho do termo de 2025.", 12, ordem=1, n=3)], o)
    assert r2.verificacao["problemas"] == ["ausencia_nao_encontrada_contexto_parcial"] and "2 de 3" in r2.resposta


def test_m1_resposta_afirmativa_correta_nao_e_afetada_regressao():
    texto = "Contrato nº 1025/2024 para alimentação hospitalar nas UPAs 24H de Ceilândia, vigência 12 meses, 2025."
    o = saida(resposta="O serviço é o fornecimento de alimentação hospitalar.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "alimentação hospitalar"}],
              evid=[{"fonte": "C1", "trecho": "alimentação hospitalar nas UPAs 24H de Ceilândia"}])
    r = rodar("Qual é o serviço contratado para as UPAs de Ceilândia em 2025?", [chunk(1, texto, 28, n=3)], o)
    assert entregue(r)


def test_m1_nunca_promove_status():
    texto = "Primeiro trecho de um documento grande de 2025."
    for st in ("insuficiente", "ambigua", "fora_do_escopo"):
        o = saida(status=st, resposta="Não consta.", fontes=["C1"], evid=[{"fonte": "C1", "trecho": "Primeiro trecho de um documento"}], just="x")
        assert rodar("Qual o valor em 2025?", [chunk(1, texto, 5, n=9)], o).status == st


# =============================================================== M2 - atributo pedido x rotulo do valor (entidade, atributo, valor)
def test_m2_unidades_rotulo_e_familias():
    t = "Edital de credenciamento, cujo objeto é SERVIÇOS ASSISTENCIAIS CLÍNICOS. Valor do Contrato : R$ 2.449.859,97. Titular: Diretor do Hospital X; Suplente: substituto."
    assert EV.rotulo_do_valor(t, "SERVIÇOS ASSISTENCIAIS CLÍNICOS") == {"rotulo": "objeto", "familia": "OBJETO"}
    assert EV.rotulo_do_valor(t, "R$ 2.449.859,97")["familia"] == "VALOR"
    assert EV.rotulo_do_valor(t, "Titular: Diretor do Hospital X")["familia"] == "MEMBRO"
    assert EV.rotulo_do_valor("As Deliberações deverão nortear as gerências.", "As Deliberações deverão nortear as gerências") is None      # desconhecido
    assert EV.conflito_atributo_rotulo("especialidades", {"rotulo": "objeto", "familia": "OBJETO"})
    assert not EV.conflito_atributo_rotulo("servicos", {"rotulo": "objeto", "familia": "OBJETO"})            # objeto E o servico
    assert not EV.conflito_atributo_rotulo("servicos", {"rotulo": "especialidades", "familia": "ESPECIALIDADE"})
    assert not EV.conflito_atributo_rotulo("competencias", None) and not EV.conflito_atributo_rotulo("desconhecida", {"rotulo": "objeto", "familia": "OBJETO"})


SEM_REMISSAO = ("O Chefe do Departamento vem AUTORIZAR a inexigibilidade para credenciar a empresa HOSPITAL HOME, em 2025, "
                "conforme Edital de Credenciamento nº 01/2024, cujo objeto é " + OBJ + ".")


def test_m2_entidade_correta_atributo_errado_especialidades_x_objeto():
    r = rodar("Quais especialidades médicas foram credenciadas no Hospital Home em 2025?", [chunk(1, SEM_REMISSAO, 94)],
              saida(resposta=f"As especialidades são {OBJ}.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": OBJ}],
                    evid=[{"fonte": "C1", "trecho": "conforme Edital de Credenciamento nº 01/2024, cujo objeto é " + OBJ}]))
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["rotulo_incompativel_com_atributo"]
    rel = r.verificacao["evidencia"]["protecao"]["relacoes"][0]
    assert rel["familia_atributo"] == "ESPECIALIDADE" and rel["rotulo"]["familia"] == "OBJETO" and rel["estado"] == "conflito" and "home" in rel["entidade"]


def test_m2_positivo_servicos_sao_o_objeto_e_registra_a_relacao():
    r = rodar("Quais serviços foram credenciados no Hospital Home em 2025?", [chunk(1, SEM_REMISSAO, 94)],
              saida(resposta=f"Foram credenciados {OBJ}.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": OBJ}],
                    evid=[{"fonte": "C1", "trecho": "conforme Edital de Credenciamento nº 01/2024, cujo objeto é " + OBJ}]))
    assert entregue(r)
    rels = r.verificacao["evidencia"]["protecao"]["relacoes"]
    assert rels and not any(x["estado"] == "conflito" for x in rels) and any(x["estado"] == "compativel" for x in rels)
    assert rels[0]["atributo"] == "servicos" and rels[0]["valor"].startswith("SERVIÇOS") and rels[0]["rotulo"]["rotulo"] == "objeto"


MEMBROS = ("Art. 4º Competência e Disposições Gerais da CRSSU em 2025. Art. 2º Designar os membros da Coordenação de Regulação: 1 - Titular: Diretor do Hospital Regional do Gama (HRG); "
           "Suplente: Substituto legal do cargo; 2 - Titular: Superintendente da Região Sul.")


def test_m2_valor_de_membro_nao_responde_competencia_val_087():
    o = saida(resposta="A Coordenação de Regulação tem competência no Hospital Regional do Gama.", fontes=["C1"],
              cand=[{"fonte": "C1", "resposta_possivel": "Titular: Diretor do Hospital Regional do Gama (HRG)"}],
              evid=[{"fonte": "C1", "trecho": "Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: Substituto legal do cargo"}])
    r = rodar("Quais as competências da Coordenação de Regulação da Região Sul em 2025?", [chunk(1, MEMBROS, 174)], o)
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["rotulo_incompativel_com_atributo"]
    # positivo: a mesma publicacao com o rotulo 'Compete' no valor entregue passa
    comp = MEMBROS + " IV - Compete à CRSSU discutir e deliberar sobre a direção dos serviços regulados em 2025."
    o2 = saida(resposta="Compete à CRSSU discutir e deliberar sobre a direção dos serviços regulados.", fontes=["C1"],
               cand=[{"fonte": "C1", "resposta_possivel": "discutir e deliberar sobre a direção dos serviços regulados"}],
               evid=[{"fonte": "C1", "trecho": "Compete à CRSSU discutir e deliberar sobre a direção dos serviços regulados"}])
    assert entregue(rodar("Quais as competências da Coordenação de Regulação da Região Sul em 2025?", [chunk(1, comp, 174)], o2))


def test_m2_atributo_valor_nao_aceita_objeto():
    txt = "Contrato 055363/2025 em 2025. Objeto: prestação de SERVIÇO DE CIRURGIA DE CABEÇA E PESCOÇO. Valor do Contrato : R$ 2.449.859,97."
    o = saida(resposta="O valor é prestação de SERVIÇO DE CIRURGIA DE CABEÇA E PESCOÇO.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "prestação de SERVIÇO DE CIRURGIA DE CABEÇA E PESCOÇO"}],
              evid=[{"fonte": "C1", "trecho": "Objeto: prestação de SERVIÇO DE CIRURGIA DE CABEÇA E PESCOÇO"}])
    assert rodar("Qual é o valor do contrato em 2025?", [chunk(1, txt, 1450)], o).verificacao["problemas"] == ["rotulo_incompativel_com_atributo"]
    o2 = saida(resposta="O valor é R$ 2.449.859,97.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "R$ 2.449.859,97"}],
               evid=[{"fonte": "C1", "trecho": "Valor do Contrato : R$ 2.449.859,97"}])
    assert entregue(rodar("Qual é o valor do contrato em 2025?", [chunk(1, txt, 1450)], o2))


def test_m2_rotulo_desconhecido_nao_bloqueia():
    txt = "Em 2025, as Deliberações da Coordenação deverão nortear as respectivas gerências de regulação no cumprimento das atribuições regimentais."
    o = saida(resposta="Devem nortear as gerências de regulação.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "nortear as respectivas gerências de regulação"}],
              evid=[{"fonte": "C1", "trecho": "deverão nortear as respectivas gerências de regulação"}])
    r = rodar("Quais as competências da Coordenação em 2025?", [chunk(1, txt, 174)], o)
    assert entregue(r) and all(x["estado"] == "desconhecido" for x in r.verificacao["evidencia"]["protecao"]["relacoes"])


# =============================================================== M3 - item de lista nao e resposta conclusiva
LISTA_RES = ("RESULTADO DEFINITIVO 2025. 401 - Acupuntura - Hospital de Base (HBDF) - 0342102160, AMANDA T, 67.37, 1. 402 - Anestesiologia - Hospital Regional da Asa Norte (HRAN), 0342100680, ARTHUR R, 96.29, 1. "
             "402 - Anestesiologia - Hospital Regional do Gama (HRG) - 0342101062, VANESSA DE SOUSA LEAL LIMA, 90.01, 1. 403 - Cirurgia Geral - Hospital Regional do Gama (HRG), 0342102864, MARINA S, 86.56, 1. "
             "403 - Cirurgia Geral - Hospital Regional de Sobradinho (HRS), 0342101004, ANNA B, 89.65, 1.")
REG = "402 - Anestesiologia - Hospital Regional do Gama (HRG) - 0342101062, VANESSA DE SOUSA LEAL LIMA, 90.01, 1."


def _o047(resposta):
    return saida(resposta=resposta, fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": REG}], evid=[{"fonte": "C1", "trecho": REG}])


def test_m3_unidades():
    assert EV.item_do_registro(REG) == "402 - Anestesiologia - Hospital Regional do Gama (HRG)"
    assert EV.estrutura_de_lista(LISTA_RES, REG)["registros"] >= 3
    assert EV.estrutura_de_lista("Contrato com a empresa Alfa para manutenção de equipamentos.", "manutenção de equipamentos") is None       # texto corrido: sem molde numerico
    assert EV.estrutura_de_lista("402 - Anestesiologia - Hospital X (HX), 1.", "402 - Anestesiologia - Hospital X (HX), 1.") is None           # um unico registro
    assert EV.exclusividade("O programa de residência disponível no Hospital Regional do Gama é Anestesiologia.", "programas")
    assert not EV.exclusividade("Entre os programas, consta Anestesiologia no Hospital Regional do Gama.", "programas")
    assert not EV.exclusividade("O Hospital Regional do Gama adquiriu máscara PFF2.", "itens")


def test_m3_item_de_lista_vira_texto_nao_conclusivo_e_continua_parcial_val_047():
    r = rodar("Quais programas de residência médica estão disponíveis no Hospital Regional do Gama em 2025?", [chunk(1, LISTA_RES, 141, n=1)],
              _o047("O programa de residência médica disponível no Hospital Regional do Gama é Anestesiologia."))
    assert r.status == "parcial"                                                       # nunca promove nem rebaixa
    corpo = r.resposta.split("\n\n")[0]
    assert corpo.startswith("Entre os itens encontrados em") and "402 - Anestesiologia - Hospital Regional do Gama (HRG)" in corpo
    assert "lista não é exaustiva" in corpo and "AVISO: resposta parcial" in r.resposta
    assert "VANESSA" not in r.resposta and "0342101062" not in r.resposta             # so o item verificado (prefixo literal), sem dados pessoais
    assert "O programa de residência" not in r.resposta                                # a frase conclusiva do modelo nao e entregue
    assert r.verificacao["evidencia"]["protecao"]["lista"]["registros_no_chunk"] >= 3
    assert EV.casar_citacao(EV.item_do_registro(REG), LISTA_RES)["status"] == "literal"          # o item entregue e literal no chunk


def test_m3_negativos_sem_estrutura_de_lista_ou_sem_exclusividade_o_texto_nao_muda():
    p = "Quais programas de residência médica estão disponíveis no Hospital Regional do Gama em 2025?"
    # (a) a mesma frase exclusiva, mas o chunk tem um unico registro (nao e lista)
    r = rodar(p, [chunk(1, "RESULTADO 2025. " + REG, 141)], _o047("O programa de residência médica disponível no Hospital Regional do Gama é Anestesiologia."))
    assert r.status == "parcial" and r.resposta.startswith("O programa de residência")
    # (b) lista, mas a resposta ja e nao exclusiva
    r2 = rodar(p, [chunk(1, LISTA_RES, 141)], _o047("Entre os programas com candidatos aprovados no Hospital Regional do Gama consta Anestesiologia."))
    assert r2.resposta.startswith("Entre os programas com candidatos")
    # (c) dois itens verificados distintos: nao e recomposto
    o = saida(resposta="O programa disponível no Hospital Regional do Gama é Anestesiologia e Cirurgia Geral.", fontes=["C1"],
              cand=[{"fonte": "C1", "resposta_possivel": REG}, {"fonte": "C1", "resposta_possivel": "403 - Cirurgia Geral - Hospital Regional do Gama (HRG), 0342102864, MARINA S, 86.56, 1."}],
              evid=[{"fonte": "C1", "trecho": REG}])
    r3 = rodar(p, [chunk(1, LISTA_RES, 141)], o)
    assert not r3.resposta.startswith("Entre os itens encontrados")


def test_m3_candidata_nao_verificada_nao_vira_item():
    o = saida(resposta="O programa disponível no Hospital Regional do Gama é Neurologia.", fontes=["C1"],
              cand=[{"fonte": "C1", "resposta_possivel": "404 - Neurologia - Hospital Regional do Gama (HRG), 1, 2, 3."}],       # nao existe no chunk
              evid=[{"fonte": "C1", "trecho": REG}])
    r = rodar("Quais programas de residência médica estão disponíveis no Hospital Regional do Gama em 2025?", [chunk(1, LISTA_RES, 141)], o)
    assert r.status == "insuficiente" and "404 - Neurologia" not in r.resposta          # candidata inexistente no chunk: nem aprovada nem usada como item


def test_m3_nao_altera_resposta_correta_de_item_unico_sem_exclusividade_regressao():
    texto = "Em 2025: a aquisição do item identificado pelo Código SES 6542, MASCARA DE PROTEÇÃO RESPIRATORIA PFF2 (EQUIVALENTE A N95), para o Hospital Regional de Brazlândia."
    o = saida(resposta="O Hospital Regional de Brazlândia adquiriu a máscara PFF2, código SES 6542.", fontes=["C1"],
              cand=[{"fonte": "C1", "resposta_possivel": "MASCARA DE PROTEÇÃO RESPIRATORIA PFF2 (EQUIVALENTE A N95)"}],
              evid=[{"fonte": "C1", "trecho": "o item identificado pelo Código SES 6542, MASCARA DE PROTEÇÃO RESPIRATORIA PFF2 (EQUIVALENTE A N95)"}])
    r = rodar("Quais itens de proteção respiratória foram adquiridos para o Hospital Regional de Brazlândia em 2025?", [chunk(1, texto, 441)], o)
    assert r.status == "parcial" and r.resposta.startswith("O Hospital Regional de Brazlândia adquiriu")


# =============================================================== M4 - periodos semanticamente equivalentes
def _d(s):
    d, m, a = s.split("/")
    return int(a), int(m), int(d)


def test_m4_unidades_interpretacao_de_periodos():
    q = EV.periodo_da_pergunta("Quais insumos foram adquiridos no período de 31 de julho a 22 de agosto de 2025?")
    assert q == {"inicio": (2025, 7, 31), "fim": (2025, 8, 22), "tipo": "generico"}
    assert EV.periodo_da_pergunta("Quais contratos foram publicados entre 01/07/2025 e 31/07/2025?")["tipo"] == "publicacao"
    assert EV.periodo_da_pergunta("Qual contrato esteve vigente de 01/01/2025 a 31/12/2025?")["tipo"] == "vigencia"
    assert EV.periodo_da_pergunta("Qual o valor do contrato em junho de 2025?") is None
    dec = EV.periodos_declarados("no período de 31/01/2025 à 06/02/2025 (Processo SisMateriais); Vigência: de 01/01/2025 a 31/12/2025.")
    assert [(d["tipo"], d["inicio"], d["fim"]) for d in dec] == [("referencia", (2025, 1, 31), (2025, 2, 6)), ("vigencia", (2025, 1, 1), (2025, 12, 31))]
    assert EV.periodos_declarados("RATIFICO em 17 de janeiro de 2025; assinatura em 22/09/2025.") == []          # datas de atos nao sao periodos


def test_m4_so_compara_periodos_do_mesmo_sentido():
    ger = {"inicio": (2025, 7, 31), "fim": (2025, 8, 22), "tipo": "generico"}
    ref_fora = {"tipo": "referencia", "inicio": (2025, 1, 31), "fim": (2025, 2, 6)}
    vig_fora = {"tipo": "vigencia", "inicio": (2025, 1, 1), "fim": (2025, 2, 6)}
    assert EV.periodos_incompativeis(ger, [ref_fora]) == [ref_fora]
    assert EV.periodos_incompativeis(ger, [vig_fora]) == []                                    # vigencia nao e o periodo de referencia dos atos
    assert EV.periodos_incompativeis({**ger, "tipo": "vigencia"}, [ref_fora]) == []            # e o inverso
    assert EV.periodos_incompativeis(ger, [{"tipo": "referencia", "inicio": (2025, 8, 20), "fim": (2025, 9, 1)}]) == []          # sobreposicao parcial: compativel
    pub = {"inicio": (2025, 7, 1), "fim": (2025, 7, 31), "tipo": "publicacao"}
    assert EV.periodos_incompativeis(pub, [], "2025-08-02") and not EV.periodos_incompativeis(pub, [], "2025-07-15")


NEUTRO = "Dados de 31/07/2025 e 22/08/2025."          # termos da pergunta presentes no texto (alinhamento da Fase 2), sem declarar periodo
OK_ = ("Extrato de dispensas, no período de 31/07/2025 a 22/08/2025 (Processo SisMateriais): aquisição do item MIDAZOLAM SOLUÇÃO INJETÁVEL para o Hospital Regional de Taguatinga.")
PER = ("Extrato de dispensas, no período de 31/01/2025 à 06/02/2025 (Processo SisMateriais): aquisição do item HEPARINA SÓDICA SOLUÇÃO INJETÁVEL para o Hospital Regional de Taguatinga.")
Q50 = "Quais insumos farmacêuticos foram adquiridos para o Hospital Regional de Taguatinga no período de 31 de julho a 22 de agosto de 2025?"
M, H = "MIDAZOLAM SOLUÇÃO INJETÁVEL", "HEPARINA SÓDICA SOLUÇÃO INJETÁVEL"


def _o50_dois():
    return saida(resposta=f"Foram adquiridos {M} e {H}.", fontes=["C1", "C2"],
                 cand=[{"fonte": "C1", "resposta_possivel": M}, {"fonte": "C2", "resposta_possivel": H}],
                 evid=[{"fonte": "C1", "trecho": f"aquisição do item {M}"}, {"fonte": "C2", "trecho": f"aquisição do item {H}"}])


def test_m4_valor_correto_com_periodo_incorreto_val_050():
    r = rodar(Q50, [chunk(1, OK_, 1307, data="2025-08-25"), chunk(2, PER + " " + NEUTRO, 196, ordem=4, n=6, data="2025-02-10")], _o50_dois())
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["periodo_incompativel"]
    assert "31/01/2025" in r.resposta and "31/07/2025" in r.resposta and "não é possível responder" in r.resposta
    per = r.verificacao["evidencia"]["protecao"]["periodos"]
    assert per[-1]["incompativeis"][0]["tipo"] == "referencia"
    # positivo: as duas publicacoes declaram periodos que coincidem ou se sobrepoem ao pedido
    ok2 = PER.replace("31/01/2025 à 06/02/2025", "20/08/2025 a 05/09/2025")
    assert entregue(rodar(Q50, [chunk(1, OK_, 1307, data="2025-08-25"), chunk(2, ok2 + " " + NEUTRO, 196, data="2025-09-06")], _o50_dois()))
    # a mesma resposta so com a publicacao correta tambem passa
    o1 = saida(resposta=f"Foi adquirido {M}.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": M}], evid=[{"fonte": "C1", "trecho": f"aquisição do item {M}"}])
    assert entregue(rodar(Q50, [chunk(1, OK_, 1307, data="2025-08-25")], o1))


VIG = ("Contrato 123/2025 da empresa Alfa, Vigência: de 01/01/2025 a 06/02/2025. Objeto: manutenção de equipamentos do Hospital Regional de Taguatinga. " + NEUTRO)
O_OBJ = saida(resposta="O objeto é manutenção de equipamentos.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "manutenção de equipamentos"}],
              evid=[{"fonte": "C1", "trecho": "Objeto: manutenção de equipamentos do Hospital Regional de Taguatinga"}])


def test_m4_nao_confunde_vigencia_com_periodo_de_referencia_nem_publicacao():
    # periodo generico x publicacao que so declara VIGENCIA: sentidos diferentes -> nao bloqueia
    assert entregue(rodar("Qual é o objeto do contrato do Hospital Regional de Taguatinga no período de 31 de julho a 22 de agosto de 2025?", [chunk(1, VIG, 55)], O_OBJ))
    # a mesma pergunta explicitamente sobre vigencia: a vigencia declarada e comparada e conflita
    r = rodar("Qual é o objeto do contrato do Hospital Regional de Taguatinga com vigência de 31/07/2025 a 22/08/2025?", [chunk(1, VIG, 55)], O_OBJ)
    assert r.verificacao["problemas"] == ["periodo_incompativel"]
    # publicacao: compara a data da edicao
    pj = "publicado entre 01/07/2025 e 31/07/2025?"
    rp = rodar(f"Qual é o objeto do contrato do Hospital Regional de Taguatinga {pj}", [chunk(1, VIG + " 01/07/2025 31/07/2025", 55, data="2025-09-15")], O_OBJ)
    assert rp.verificacao["problemas"] == ["periodo_incompativel"]
    ok_ = rodar("Qual é o objeto do contrato do Hospital Regional de Taguatinga publicado entre 01/09/2025 e 30/09/2025?", [chunk(1, VIG + " 01/09/2025 30/09/2025", 55, data="2025-09-15")], O_OBJ)
    assert entregue(ok_)


def test_m4_pergunta_sem_intervalo_e_publicacao_sem_periodo_declarado_nao_sao_afetadas_regressao():
    assert entregue(rodar("Qual é o objeto do contrato do Hospital Regional de Taguatinga em 2025?", [chunk(1, "Contrato Alfa em 2025. Objeto: manutenção de equipamentos do Hospital Regional de Taguatinga.", 56)], O_OBJ))
    o1 = saida(resposta=f"Foi adquirido {M}.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": M}], evid=[{"fonte": "C1", "trecho": f"aquisição do item {M}"}])
    r = rodar(Q50, [chunk(1, f"Aquisição do item {M} para o Hospital Regional de Taguatinga. {NEUTRO}", 1307, data="2025-08-25")], o1)
    assert entregue(r) and r.verificacao["evidencia"]["protecao"]["periodos"][0]["declarados"] == []          # sem periodo declarado: registrado, sem bloqueio


# =============================================================== M5 - identificador x localidade/entidade (so por associacao estrutural)
from citizentech.assistente.catalogo import Catalogo  # noqa: E402

GAZ = ["asa sul", "asa norte", "taguatinga", "ceilandia", "sudoeste", "aguas claras"]


def cat5():
    return Catalogo([{"id": 1, "ids_equivalentes": [1], "texto_completo": "x", "localidades": ["Asa Sul", "Asa Norte", "Taguatinga", "Ceilândia", "Sudoeste", "Águas Claras"]}])


ONCO = ("Matriz: SHLS 716, Centro Clínico Sul, Brasília - DF, CNPJ: 11.859.927/0001-06. Filial (1): SGAS 915 Edifício Vital – Asa Sul – CEP: 70390-108 CNPJ: 11.859.927/0003-60. "
        "Filial (2): SGAS 915 Conj. O Salas 227 – Asa Sul – CEP: 7039-150 CNPJ: 11.859.927/0008-74. "
        "Filial (3): ST SHL/NORTE LOTE 09 BLOCO B ED. Biosphere Health Center – Asa Norte - CEP: 70770-560 CNPJ: 11.859.927/0007-93. "
        "Filial (4): SETOR E SUL Hospital Santa Marta – Taguatinga Sul CNPJ: 11.859.927/0009-55. Credenciamento 2025.")
Q130 = "Quais empresas foram credenciadas para prestar serviços assistenciais na Asa Sul em 2025?"


def _o130(cnpj, nome=None):
    return saida(resposta=f"A empresa de CNPJ {cnpj} foi credenciada.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": f"CNPJ: {cnpj}"}],
                 evid=[{"fonte": "C1", "trecho": f"CNPJ: {cnpj}"}])


def test_m5_unidades_associacao_estrutural():
    a = EV.associacao_estrutural(ONCO, "11.859.927/0007-93", GAZ)
    assert a["via"] == "registro_numerado" and a["localidades"] == ["asa norte"]
    b = EV.associacao_estrutural(ONCO, "11.859.927/0003-60", GAZ)
    assert b["localidades"] == ["asa sul"]
    c = EV.associacao_estrutural("empresa VISÃO HOSPITAL, CNPJ: 37.114.071/0001-25, ENDEREÇO: SEPS 714/914, Ed Talento - Asa Sul, Telefone: (61) 3442-4000", "37.114.071/0001-25", GAZ)
    assert c["via"] == "rotulo_endereco" and c["localidades"] == ["asa sul"]
    # so proximidade (sem registro numerado nem campo rotulado): nao ha associacao
    assert EV.associacao_estrutural("A empresa Alfa fica na Asa Norte. A empresa Beta, CNPJ 11.111.111/0001-11, atende bem.", "11.111.111/0001-11", GAZ) is None
    assert EV.associacao_estrutural("sem o identificador", "11.111.111/0001-11", GAZ) is None


def test_m5_localidade_mencionada_no_documento_mas_nao_associada_a_entidade_val_130():
    cat = cat5()
    r = rodar(Q130, [chunk(1, ONCO, 6)], _o130("11.859.927/0007-93", "Biosphere Health Center"), catalogo=cat)
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["localidade_conflitante_no_registro"]
    assert "asa norte" in r.resposta and "asa sul" in r.resposta and "11.859.927/0007-93" in r.resposta
    a = r.verificacao["evidencia"]["protecao"]["associacao_estrutural"][0]
    assert a["via"] == "registro_numerado" and a["localidades"] == ["asa norte"]
    # positivo: o CNPJ da filial da Asa Sul passa
    assert entregue(rodar(Q130, [chunk(1, ONCO, 6)], _o130("11.859.927/0003-60", "Instituto de Câncer"), catalogo=cat))


def test_m5_rotulo_endereco_positivo_e_negativo():
    cat = cat5()
    txt = "Credenciar a empresa VISÃO HOSPITAL DE OLHOS, CNPJ: 37.114.071/0001-25, ENDEREÇO: SEPS 714/914, Ed Talento - {loc}, Telefone: (61) 3442-4000, em 2025. Atendimento também a pacientes da Asa Sul."
    o = _o130("37.114.071/0001-25", "VISÃO HOSPITAL DE OLHOS")
    assert entregue(rodar(Q130, [chunk(1, txt.format(loc="Asa Sul"), 920)], o, catalogo=cat))
    r = rodar(Q130, [chunk(1, txt.format(loc="Asa Norte"), 920)], o, catalogo=cat)
    assert r.verificacao["problemas"] == ["localidade_conflitante_no_registro"]


def test_m5_proximidade_textual_sozinha_nao_bloqueia():
    cat = cat5()
    txt = "A empresa Alfa fica na Asa Norte. A empresa Beta Ltda, CNPJ 11.111.111/0001-11, foi credenciada para serviços assistenciais em 2025 na Asa Sul."
    o = _o130("11.111.111/0001-11", "Beta Ltda")
    r = rodar(Q130, [chunk(1, txt, 77)], o, catalogo=cat)
    assert entregue(r) and r.verificacao["evidencia"]["protecao"]["associacao_estrutural"] == []        # nenhuma associacao estrutural: sem decisao


def test_m5_regiao_nao_conflita_com_cidade_dentro_dela():
    cat = cat5()
    txt = ("Matriz: Taguatinga Centro, CNPJ: 22.222.222/0001-22. Filial (1): Ceilândia Sul, CNPJ: 33.333.333/0001-33. Credenciamento em 2025 na Região de Saúde Sudoeste.")
    o = _o130("22.222.222/0001-22", "Alfa")
    r = rodar("Quais empresas foram credenciadas na Região de Saúde Sudoeste em 2025?", [chunk(1, txt, 78)], o, catalogo=cat)
    assert entregue(r)                                                                  # 'sudoeste' e regiao: nao conflita com 'taguatinga'


def test_m5_atributo_correto_com_entidade_de_outro_registro():
    cat = cat5()
    txt = ("Matriz: Hospital Alfa em Taguatinga, CNPJ: 44.444.444/0001-44. Filial (1): Hospital Beta em Taguatinga, CNPJ: 55.555.555/0001-55. Credenciamento 2025.")
    o = saida(resposta="O CNPJ do Hospital Alfa é 55.555.555/0001-55.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "CNPJ: 55.555.555/0001-55"}],
              evid=[{"fonte": "C1", "trecho": "CNPJ: 55.555.555/0001-55"}])
    r = rodar("Quais são os CNPJ do Hospital Alfa em Taguatinga em 2025?", [chunk(1, txt, 79)], o, catalogo=cat)
    assert r.verificacao["problemas"] == ["entidade_em_outro_registro"] and "alfa" in r.resposta
    o2 = saida(resposta="O CNPJ do Hospital Alfa é 44.444.444/0001-44.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "CNPJ: 44.444.444/0001-44"}],
               evid=[{"fonte": "C1", "trecho": "CNPJ: 44.444.444/0001-44"}])
    assert entregue(rodar("Quais são os CNPJ do Hospital Alfa em Taguatinga em 2025?", [chunk(1, txt, 79)], o2, catalogo=cat))


def test_m5_sem_catalogo_ou_sem_identificador_nao_decide():
    assert entregue(rodar(Q130, [chunk(1, ONCO, 6)], _o130("11.859.927/0007-93", "Biosphere Health Center")))          # sem catalogo: M5 inativo (Fase 2 inalterada)
    o = saida(resposta="A filial foi credenciada.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "Taguatinga Sul"}], evid=[{"fonte": "C1", "trecho": "Hospital Santa Marta – Taguatinga Sul"}])
    assert "localidade_conflitante_no_registro" not in rodar(Q130, [chunk(1, ONCO, 6)], o, catalogo=cat5()).verificacao.get("problemas", [])


# =============================================================== cada mecanismo e necessario (se removido, o cenario correspondente volta a ser entregue)
import pytest  # noqa: E402


def _cenario_m1():
    """Negativa com contexto parcial (val-039/141). Obs.: o caso val-136 e bloqueado por M1 (remissao) E por M2 (rotulo): defesa em profundidade, por isso nao serve de teste de necessidade de M1."""
    texto = "Primeiro trecho do documento: grade de distribuição de São Sebastião, códigos SES P08000369 P08002053 e regiões de saúde em 2025."
    o = saida(resposta="Não foram especificadas as denominações das unidades.", fontes=["C1"], cand=[], evid=[{"fonte": "C1", "trecho": "grade de distribuição de São Sebastião, códigos SES P08000369 P08002053"}])
    return rodar("Quais unidades de saúde em São Sebastião receberão equipamentos em 2025?", [chunk(1, texto, 303, ordem=0, n=40)], o)


def _cenario_m2():
    return rodar("Quais especialidades médicas foram credenciadas no Hospital Home em 2025?", [chunk(1, SEM_REMISSAO, 94)],
                 saida(resposta=f"As especialidades são {OBJ}.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": OBJ}],
                       evid=[{"fonte": "C1", "trecho": "conforme Edital de Credenciamento nº 01/2024, cujo objeto é " + OBJ}]))


def _cenario_m3():
    return rodar("Quais programas de residência médica estão disponíveis no Hospital Regional do Gama em 2025?", [chunk(1, LISTA_RES, 141, n=1)],
                 _o047("O programa de residência médica disponível no Hospital Regional do Gama é Anestesiologia."))


def _cenario_m4():
    return rodar(Q50, [chunk(1, OK_, 1307, data="2025-08-25"), chunk(2, PER + " " + NEUTRO, 196, ordem=4, n=6, data="2025-02-10")], _o50_dois())


def _cenario_m5():
    return rodar(Q130, [chunk(1, ONCO, 6)], _o130("11.859.927/0007-93"), catalogo=cat5())


@pytest.mark.parametrize("mec,cenario,protegido", [
    ("M1", _cenario_m1, lambda r: r.status == "insuficiente"),
    ("M2", _cenario_m2, lambda r: r.status == "insuficiente"),
    ("M3", _cenario_m3, lambda r: r.status == "parcial" and r.resposta.startswith("Entre os itens encontrados")),
    ("M4", _cenario_m4, lambda r: r.status == "insuficiente"),
    ("M5", _cenario_m5, lambda r: r.status == "insuficiente"),
])
def test_cada_mecanismo_e_necessario_remover_um_reabre_o_erro(monkeypatch, mec, cenario, protegido):
    assert protegido(cenario())                                                       # com todos os mecanismos
    monkeypatch.setattr(G, "PROTECOES_44", set(G.PROTECOES_44) - {mec})
    r = cenario()
    assert not protegido(r), f"{mec} removido e o cenario continua protegido: o teste nao exercita o mecanismo"
    assert entregue(r)                                                                # o erro volta a ser entregue (comportamento da Fase 2)


def test_nenhum_mecanismo_promove_status_nem_cria_resposta(monkeypatch):
    for fn in (_cenario_m1, _cenario_m2, _cenario_m3, _cenario_m4, _cenario_m5):
        antes = fn()
        monkeypatch.setattr(G, "PROTECOES_44", set())
        base = fn()
        monkeypatch.setattr(G, "PROTECOES_44", {"M1", "M2", "M3", "M4", "M5"})
        ordem = {"insuficiente": 0, "ambigua": 0, "fora_do_escopo": 0, "parcial": 1, "respondida": 2}
        assert ordem[antes.status] <= ordem[base.status]


# =============================================================== replay offline dos 150 (saidas brutas gravadas; sem LLM)
import json  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]
RODADA = RAIZ / "data_assistente" / "derivados" / "geracao_e2e_41_20261114-130608.jsonl"
IDX = RAIZ / "data_assistente" / "indices" / "est300o30"


@pytest.mark.skipif(not (RODADA.exists() and IDX.exists()), reason="rodada/indice 4.3 indisponiveis")
def test_replay_150_fase3_so_rebaixa_ou_reescreve_e_preserva_corretas_e_bloqueios(monkeypatch):
    """Fase 3 ISOLADA: os mecanismos de associacao da Fase 4A (A_DEST, A_LOC) ficam desligados aqui; o efeito combinado e verificado em test_fase4a.py."""
    monkeypatch.setattr(G, "PROTECOES_44", set(G.PROTECOES_44) - {"A_DEST", "A_LOC"})
    from citizentech.assistente import avaliacao_e2e as AE
    from citizentech.assistente.geracao import ConfigGeracao
    from citizentech.assistente.retriever import Indice

    class Falso:
        def __init__(self, bruto, cfg):
            self.bruto, self.cfg = bruto, cfg

        def completar(self, msgs, temperatura=None):
            return {"conteudo": self.bruto, "finish": "stop", "tokens_prompt": 0, "tokens_saida": 0, "tokens_raciocinio": 0, "latencia_s": 0.0}

    corpus, val, assoc, dup, esperados, docs = AE.preparar()
    idx, cat, cfg = Indice.carregar(IDX), Catalogo.de_corpus(corpus), ConfigGeracao()
    orig = {json.loads(l)["qid"]: json.loads(l) for l in RODADA.open(encoding="utf-8")}
    buscas = {q["qid"]: idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25") for q in val}

    def rodar_tudo():
        return {q["qid"]: gerar_resposta(q["pergunta"], buscas[q["qid"]], Falso(orig[q["qid"]]["saida"]["telemetria"]["saida_bruta"], cfg), cfg, catalogo=cat) for q in val}

    novo = rodar_tudo()
    ativo = set(G.PROTECOES_44)
    try:
        G.PROTECOES_44.clear()
        base = rodar_tudo()                         # comportamento da Fase 2
    finally:
        G.PROTECOES_44.update(ativo)
    ordem = {"insuficiente": 0, "ambigua": 0, "fora_do_escopo": 0, "parcial": 1, "respondida": 2}
    mudaram = {k for k in novo if novo[k].status != base[k].status or novo[k].resposta != base[k].resposta}
    assert mudaram == {"val-039", "val-047", "val-050", "val-087", "val-130", "val-136", "val-141"}
    for k in mudaram:                                                              # nunca promove
        assert ordem[novo[k].status] <= ordem[base[k].status]
    for k in ("val-039", "val-050", "val-087", "val-130", "val-136", "val-141"):
        assert novo[k].status == "insuficiente"
    assert novo["val-047"].status == "parcial" and novo["val-047"].resposta.startswith("Entre os itens encontrados") and "AVISO: resposta parcial" in novo["val-047"].resposta
    for k in ("val-044", "val-031", "val-032"):                                    # justificaveis: inalterados
        assert novo[k].status == "parcial" and novo[k].resposta == base[k].resposta
    for k in ("val-062", "val-108", "val-126"):                                    # bloqueios legitimos preservados, pelos mesmos motivos da Fase 2
        assert novo[k].status == "insuficiente" and novo[k].verificacao["problemas"] == base[k].verificacao["problemas"]
    rot = {r["qid"]: r["classificacao_independente"] for r in __import__("csv").DictReader(
        (RAIZ / "docs" / "assistente" / "auditoria_independente_4_3" / "auditoria_independente_150.csv").open(encoding="utf-8-sig"), delimiter=";")}
    for k, o in orig.items():                                                      # as 7 corretas e as 16 corretas-mas-parciais da auditoria: status e texto inalterados
        if rot[k] in ("Correta", "Correta, mas parcial") and o["saida"]["status"] in ("respondida", "parcial"):
            assert novo[k].status == o["saida"]["status"] and novo[k].resposta == o["saida"]["resposta"], k
    for k in novo:                                                                 # as abstencoes da 4.3 (ambigua, insuficiente, fora_do_escopo) nao mudam
        if orig[k]["saida"]["status"] not in ("respondida", "parcial") and k not in {"val-031", "val-032", "val-044", "val-045", "val-047", "val-083", "val-087", "val-097", "val-106", "val-141"}:
            assert novo[k].status == orig[k]["saida"]["status"] and novo[k].resposta == orig[k]["saida"]["resposta"], k
