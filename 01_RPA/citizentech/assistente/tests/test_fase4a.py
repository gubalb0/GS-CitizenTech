"""Etapa 4.4 / Fase 4A - integridade das relacoes entre evidencia, entidade, destinatario e atributo.

Mecanismo C: registro auditavel das relacoes (esquema relacoes/2). Mecanismo B: rotulo conflitante so bloqueia se o trecho sustenta termo da resposta.
Mecanismo A: associacao com destinatario e com a localidade perguntada. Nenhum mecanismo promove status.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_geracao import cli, ok, saida  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402
from citizentech.assistente import geracao as G  # noqa: E402
from citizentech.assistente.catalogo import Catalogo  # noqa: E402
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


def rels(r):
    return (r.verificacao.get("evidencia") or {}).get("protecao", {}).get("relacoes", [])


# =============================================================== Mecanismo C - registro auditavel (esquema relacoes/2)
RAT = ("RATIFICO em 14 de abril de 2025, a dispensa de licitação, Processo SEI nº 00060-00173080/2025-64, à empresa NEXO LTDA, cujo objeto é a aquisição do item identificado pelo "
       "Código SES 90462 - BUTILBROMETO DE ESCOPOLAMINA COMPRIMIDO OU DRÁGEA 10 MG, para atender as necessidades da Atenção Primária, no valor global de R$ 20.400,00; "
       "RATIFICO em 19 de setembro de 2025, a dispensa de licitação, Processo SEI nº 00060-00375706/2025-75, à empresa ALFA LTDA, cujo objeto é a aquisição do item identificado pelo "
       "Código SES 37167 - CLORETO DE SODIO SOLUCAO INJETAVEL 0,9% AMPOLA 10 ML, para atender as necessidades do Hospital Regional do Guará, no valor global de R$ 495,60. Guará 2025.")


def _o(resp, itens, fonte="C1"):
    return saida(resposta=resp, fontes=[fonte], cand=[{"fonte": fonte, "resposta_possivel": s} for s in itens], evid=[{"fonte": fonte, "trecho": s} for s in itens])


def test_c_esquema_versionado_e_campos_historicos_preservados():
    item = "Código SES 90462 - BUTILBROMETO DE ESCOPOLAMINA COMPRIMIDO OU DRÁGEA 10 MG, para atender as necessidades da Atenção Primária"
    r = rodar("Quais itens foram adquiridos para a Atenção Primária em 2025?", [chunk(1, RAT, 495, n=1)], _o("Foi adquirido BUTILBROMETO DE ESCOPOLAMINA COMPRIMIDO.", [item]))
    prot = r.verificacao["evidencia"]["protecao"]
    assert prot["esquema_relacoes"] == "relacoes/3" == EV.SCHEMA_RELACOES
    x = rels(r)[0]
    for antigo in ("entidade", "atributo", "familia_atributo", "valor", "rotulo", "origem", "chunk_id", "estado"):          # compatibilidade com o esquema da Fase 3
        assert antigo in x
    for novo in ("esquema", "publicacao", "doc_id", "fonte", "entidade_pergunta", "entidade_no_trecho", "atributo_pedido", "atributo_encontrado", "registro",
                 "estado_associacao", "justificativa", "necessaria", "termos_exclusivos", "bloqueia"):
        assert novo in x
    assert x["esquema"] == "relacoes/3" and x["estado"] in ("compativel", "conflito", "desconhecido") and x["estado_associacao"] in ("confirmada", "conflitante", "nao_verificavel")
    assert x["publicacao"].startswith("Extrato 495/2025") and x["doc_id"] == 495 and x["chunk_id"] == "dodf-495:est300o30:0000" and x["fonte"] == "C1"


def test_c_valor_completo_sem_truncamento_artificial():
    longo = "Código SES 90462 - BUTILBROMETO DE ESCOPOLAMINA COMPRIMIDO OU DRÁGEA 10 MG, para atender as necessidades da Atenção Primária, no valor global de R$ 20.400,00"
    assert len(longo) > 90
    r = rodar("Quais itens foram adquiridos para a Atenção Primária em 2025?", [chunk(1, RAT, 495)], _o("Foi adquirido BUTILBROMETO DE ESCOPOLAMINA.", [longo]))
    assert all(x["valor"] == longo for x in rels(r))


def test_c_identificador_do_registro_so_quando_existe_na_fonte():
    r = rodar("Quais itens foram adquiridos para a Atenção Primária em 2025?", [chunk(1, RAT, 495)],
              _o("Foi adquirido BUTILBROMETO DE ESCOPOLAMINA.", ["Código SES 90462 - BUTILBROMETO DE ESCOPOLAMINA COMPRIMIDO OU DRÁGEA 10 MG, para atender as necessidades da Atenção Primária"]))
    assert rels(r)[0]["registro"] == {"tipo": "ratificacao", "id": "SEI 00060-00173080/2025-64"}                      # id presente no texto (nao inventado)
    # registro sem identificador: texto corrido sem estrutura de registro
    r2 = rodar("Qual é o objeto do contrato da empresa Alfa em 2025?", [chunk(1, "Contrato da empresa Alfa em 2025. Objeto: manutenção de equipamentos do hospital.", 56)],
               _o("O objeto é manutenção de equipamentos.", ["Objeto: manutenção de equipamentos do hospital"]))
    assert rels(r2) and all(x["registro"] is None for x in rels(r2))                                                 # nada de id inventado
    numerado = ("Matriz: Alfa, CNPJ: 11.111.111/0001-11. Filial (1): Beta, CNPJ: 22.222.222/0001-22. Filial (2): Gama, CNPJ: 33.333.333/0001-33. Credenciamento 2025.")
    assert EV.registro_do_trecho(numerado, "CNPJ: 22.222.222/0001-22")["id"] == "filial (1)"
    assert EV.registro_do_trecho("sem estrutura nenhuma, CNPJ: 22.222.222/0001-22", "CNPJ: 22.222.222/0001-22") is None


def test_c_entidade_pergunta_x_entidade_no_trecho_e_atributo_pedido_x_encontrado():
    txt = "Edital de credenciamento 2025 do Hospital Home, cujo objeto é SERVIÇOS ASSISTENCIAIS CLÍNICOS E CIRÚRGICOS."
    r = rodar("Quais serviços foram credenciados no Hospital Home em 2025?", [chunk(1, txt, 94)], _o("Foram credenciados SERVIÇOS ASSISTENCIAIS CLÍNICOS E CIRÚRGICOS.", ["SERVIÇOS ASSISTENCIAIS CLÍNICOS E CIRÚRGICOS"]))
    x = rels(r)[0]
    assert x["entidade_pergunta"] == ["home"] and x["atributo_pedido"] == {"cabeca": "servicos", "familia": "OBJETO"}
    assert x["atributo_encontrado"] == {"rotulo": "objeto", "familia": "OBJETO"} and x["estado_associacao"] == "confirmada" and "compativel" in x["justificativa"]


def test_c_evidencia_sem_associacao_verificavel_fica_nao_verificavel_e_nao_bloqueia():
    txt = "Em 2025, as Deliberações da Coordenação deverão nortear as respectivas gerências de regulação no cumprimento das atribuições regimentais."
    r = rodar("Quais as competências da Coordenação em 2025?", [chunk(1, txt, 174)], _o("Devem nortear as gerências de regulação.", ["deverão nortear as respectivas gerências de regulação"]))
    assert entregue(r) and all(x["estado_associacao"] == "nao_verificavel" and x["bloqueia"] is False for x in rels(r))
    assert "nao verificavel" in rels(r)[0]["justificativa"]


# =============================================================== Mecanismo B - rotulo conflitante so bloqueia se o trecho sustenta termo da resposta
Q87 = "Quais as competências da Coordenação de Regulação da Região Sul em 2025?"
COMP = "IV - Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados na Região de Saúde Sul."
MEMB = "Art. 2º Designar membros da Coordenação de Regulação da Região Sul (CRSSU): 1 - Titular: Gerente de Regulação; Suplente: substituto; 4 - Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: substituto."
OUTRA = "Comitê de Ética da Região Norte, 2025: 1 - Titular: Maria da Silva, representante da Região Norte."


def o87(resp, spans, fontes=("C1",)):
    return saida(resposta=resp, fontes=list(fontes), cand=[{"fonte": f, "resposta_possivel": s} for f, s in spans], evid=[{"fonte": f, "trecho": s} for f, s in spans])


def test_b_unidades_termos_e_apoio_exclusivo():
    t = EV.termos_de_conteudo("Compete à CRSSU discutir e deliberar sobre a direção do Hospital Regional do Gama (HRG).", Q87)
    assert "crssu" in t and "discutir" in t and "hrg" in t and "compete" not in t and "regional" not in t          # genericas e palavras da pergunta ficam de fora
    ex = EV.apoio_exclusivo({"C1": "Compete à CRSSU discutir e deliberar", "C2": "Titular: Maria da Silva"}, ["crssu", "discutir", "maria"])
    assert ex == {"C1": ["crssu", "discutir"], "C2": ["maria"]}
    assert EV.apoio_exclusivo({"C1": "x", "C2": "y"}, [])["C2"]                                                         # sem termos: todas necessarias (conservador)
    assert EV.apoio_exclusivo({"C1": "discutir normas", "C2": "discutir regras"}, ["discutir"]) == {"C1": [], "C2": []}   # termo apoiado por duas unidades: nenhuma e exclusiva
    assert EV.cue_de_atributo("Titular: o Diretor, a quem compete deliberar", "COMPETENCIA") == "compete" and EV.cue_de_atributo("Titular: Maria", "COMPETENCIA") is None


def test_cenario_A1_titular_em_outra_parte_da_publicacao_resposta_usa_so_a_competencia():
    c1 = chunk(1, "Art. 4º Competência e Disposições Gerais da CRSSU em 2025. " + COMP + " " + MEMB, 174)
    r = rodar(Q87, [c1], o87("Compete à CRSSU discutir e deliberar sobre a direção dos serviços regulados.", [("C1", "Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados")]))
    assert entregue(r) and not any(x["bloqueia"] for x in rels(r))


def test_cenario_A2_trecho_titular_de_outra_entidade_citado_mas_nao_usado_nao_bloqueia():
    c1 = chunk(1, "Art. 4º Competência e Disposições Gerais da CRSSU em 2025. " + COMP + " " + MEMB, 174)
    c2 = chunk(2, OUTRA, 175)
    r = rodar(Q87, [c1, c2], o87("Compete à CRSSU discutir e deliberar sobre a direção dos serviços regulados.",
                                 [("C1", "Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados"), ("C2", "Titular: Maria da Silva, representante da Região Norte")], fontes=("C1", "C2")))
    assert entregue(r), r.verificacao
    x = [x for x in rels(r) if x["chunk_id"].startswith("dodf-175")][0]
    assert x["estado"] == "conflito" and x["estado_associacao"] == "conflitante" and x["necessaria"] is False and x["bloqueia"] is False     # o conflito continua REGISTRADO
    assert "nao bloqueia" in x["justificativa"]   # 4B-prep: redacao mudou; decisao identica


def test_cenario_B1_resposta_usa_a_lista_de_membros_da_propria_entidade_como_competencia():
    c1 = chunk(1, "Art. 4º Competência e Disposições Gerais da CRSSU em 2025. " + COMP + " " + MEMB, 174)
    r = rodar(Q87, [c1], o87("A Coordenação tem competência no Hospital Regional do Gama (HRG).", [("C1", "Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: substituto")]))
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["rotulo_incompativel_com_atributo"]
    assert any(x["bloqueia"] and x["estado_associacao"] == "conflitante" and x["necessaria"] for x in rels(r))


def test_cenario_B2_so_ha_lista_de_membros_para_a_entidade():
    c3 = chunk(1, "Art. 2º Designar membros da Coordenação de Regulação da Região Sul (CRSSU) em 2025: 1 - Titular: Gerente de Regulação; 4 - Titular: Diretor do Hospital Regional do Gama (HRG).", 174)
    r = rodar(Q87, [c3], o87("A Coordenação é composta pelo Diretor do Hospital Regional do Gama (HRG).", [("C1", "Titular: Diretor do Hospital Regional do Gama (HRG)")]))
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["rotulo_incompativel_com_atributo"]


def test_cenario_C_prefixo_titular_com_afirmacao_explicita_de_competencia_nao_bloqueia_automaticamente():
    r = rodar(Q87, [chunk(1, "Em 2025, Titular: o Diretor do HRG, a quem compete deliberar sobre os serviços do Gama junto à Coordenação de Regulação da Região Sul.", 174)],
              o87("Compete ao Diretor deliberar sobre os serviços do Gama.", [("C1", "Titular: o Diretor do HRG, a quem compete deliberar sobre os serviços do Gama")]))
    assert entregue(r)
    x = rels(r)[0]
    assert x["estado"] == "conflito" and x["estado_associacao"] == "nao_verificavel" and x["bloqueia"] is False and "compete" in x["justificativa"]      # relacao semantica nao verificada


def test_b_conflito_real_com_duas_unidades_continua_bloqueando():
    """val-087: a competencia vem de C1, mas o 'HRG' so existe na lista de membros (C2) -> o trecho conflitante e necessario."""
    c1 = chunk(1, "Art. 4º IX - As Deliberações deverão nortear as respectivas gerências de regulação, no cumprimento das atribuições regimentais de implementar normas em 2025.", 174, ordem=4, n=5)
    c2 = chunk(2, MEMB, 174, ordem=1, n=5)
    o = o87("A Coordenação tem competência para nortear as gerências de regulação, incluindo o Hospital Regional do Gama (HRG).",
            [("C1", "deverão nortear as respectivas gerências de regulação"), ("C2", "Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: substituto")], fontes=("C1", "C2"))
    r = rodar(Q87, [c1, c2], o)
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["rotulo_incompativel_com_atributo"]
    ex = {x["fonte"]: x["termos_exclusivos"] for x in rels(r)}
    assert "hrg" in ex["C2"] and "nortear" in " ".join(ex["C1"])


# =============================================================== Mecanismo A - associacao entre evidencia, destinatario e localidade da publicacao
LOCS = ["Guará", "Taguatinga", "Ceilândia", "Sudoeste", "Asa Sul"]


def cat_a(docs):
    """Catalogo minimo: `docs` = {id: (texto, [localidades])}; o gazetario vem de LOCS."""
    return Catalogo([{"id": i, "ids_equivalentes": [i], "texto_completo": t, "localidades": loc or []} for i, (t, loc) in docs.items()] +
                    [{"id": 9999, "ids_equivalentes": [9999], "texto_completo": "x", "localidades": LOCS}])


def reg_item(codigo, item, dest, data="14 de abril", sei="00060-00173080/2025-64"):
    return (f"RATIFICO em {data} de 2025, a dispensa de licitação, Processo SEI nº {sei}, à empresa NEXO LTDA, cujo objeto é a aquisição do item identificado pelo "
            f"Código SES {codigo} - {item}, para atender as necessidades {dest}, no valor global de R$ 100,00; ")


ITEM_AP = "VITAMINA D 400 UI/G."
ITEM_HR = "CLORETO DE SODIO SOLUCAO INJETAVEL 0,9% AMPOLA 10 ML"
T_AP_HR = reg_item(90462, ITEM_AP, "da Atenção Primária") + reg_item(37167, ITEM_HR, "do Hospital Regional do Guará", "19 de setembro", "00060-00375706/2025-75") + "Guará 2025."
Q_AP = "Quais itens foram adquiridos para atender as necessidades da Atenção Primária no Guará em 2025?"


def itens_o(resp, itens):
    return saida(resposta=resp, fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": s} for s in itens], evid=[{"fonte": "C1", "trecho": s} for s in itens])


def test_a_unidades_destinatario_da_pergunta_e_do_registro():
    assert EV.destinatario_da_pergunta(Q_AP) == "atencao primaria"                     # 'no Guara' e localidade, nao destinatario
    assert EV.destinatario_da_pergunta("Quais itens foram adquiridos para o Hospital Regional de Taguatinga em 2025?") == "hospital regional de taguatinga"
    assert EV.destinatario_da_pergunta("Qual o valor do contrato da empresa Alfa?") is None
    d = EV.destinatario_no_registro(T_AP_HR, f"Código SES 37167 - {ITEM_HR}")
    assert d["destinatario"] == "hospital regional do guara"
    # o destinatario de OUTRO registro nao e atribuido por proximidade: o item 1 so enxerga a sua propria clausula
    assert EV.destinatario_no_registro(T_AP_HR, f"Código SES 90462 - {ITEM_AP}")["destinatario"] == "atencao primaria"
    sem_dest = "RATIFICO em 1 de março de 2025, Processo SEI nº 00060-1111/2025-11, cujo objeto é a aquisição do item Código SES 111 - ITEM SEM DESTINO, no valor de R$ 1,00; " + reg_item(222, "OUTRO ITEM", "do Hospital X")
    assert EV.destinatario_no_registro(sem_dest, "Código SES 111 - ITEM SEM DESTINO") is None
    g = ["guara", "taguatinga", "ceilandia"]
    assert EV.comparar_destinatarios("atencao primaria", "atencao primaria", g)["estado"] == "confirmada"
    assert EV.comparar_destinatarios("atencao primaria", "hospital regional do guara", g)["estado"] == "conflitante"
    assert EV.comparar_destinatarios("hospital regional de taguatinga", "hospital regional do guara", g)["estado"] == "conflitante"      # mesma unidade generica, outra localidade
    assert EV.comparar_destinatarios("hospital regional de taguatinga", "hospital regional de taguatinga", g)["estado"] == "confirmada"
    assert EV.comparar_destinatarios(None, "hospital x", g)["estado"] == "nao_verificavel" and EV.comparar_destinatarios("hospital x", None, g)["estado"] == "nao_verificavel"


def test_a_entidade_correta_e_destinatario_correto_positivo():
    o = itens_o("Foi adquirido VITAMINA D 400 UI/G.", [f"Código SES 90462 - {ITEM_AP}, para atender as necessidades da Atenção Primária"])
    r = rodar(Q_AP, [chunk(1, T_AP_HR, 495)], o, catalogo=cat_a({495: (T_AP_HR, ["Guará"])}))
    assert entregue(r)
    x = [x for x in rels(r) if x["destinatario_no_trecho"]][0]
    assert x["destinatario_pergunta"] == "atencao primaria" and x["destinatario_no_trecho"] == "atencao primaria" and x["estado_associacao"] == "confirmada"
    assert x["registro"]["id"] == "SEI 00060-00173080/2025-64"


def test_a_produto_existente_mas_destinado_a_outra_unidade_val_083():
    o = itens_o(f"Foram adquiridos {ITEM_AP} e {ITEM_HR}.", [f"Código SES 90462 - {ITEM_AP}, para atender as necessidades da Atenção Primária", f"Código SES 37167 - {ITEM_HR}, para atender"])
    r = rodar(Q_AP, [chunk(1, T_AP_HR, 495)], o, catalogo=cat_a({495: (T_AP_HR, ["Guará"])}))
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["destinatario_conflitante"]
    assert "hospital regional do guará" in r.resposta.lower() and "atenção primária" in r.resposta.lower() or "atencao primaria" in r.resposta.lower()
    assert any(x["estado_associacao"] == "conflitante" and x["causas_do_conflito"] == ["destinatario"] and x["bloqueia"] for x in rels(r))
    assert any(x["estado_associacao"] == "confirmada" and x["destinatario_no_trecho"] == "atencao primaria" for x in rels(r))          # o item correto continua confirmado


def test_a_item_com_destinatario_conflitante_mas_nao_usado_na_resposta_nao_bloqueia():
    o = saida(resposta="Foi adquirido VITAMINA D 400 UI/G.", fontes=["C1"],
              cand=[{"fonte": "C1", "resposta_possivel": f"Código SES 90462 - {ITEM_AP}, para atender as necessidades da Atenção Primária"}, {"fonte": "C1", "resposta_possivel": f"Código SES 37167 - {ITEM_HR}, para atender"}],
              evid=[{"fonte": "C1", "trecho": f"Código SES 90462 - {ITEM_AP}, para atender as necessidades da Atenção Primária"}])
    r = rodar(Q_AP, [chunk(1, T_AP_HR, 495)], o, catalogo=cat_a({495: (T_AP_HR, ["Guará"])}))
    assert entregue(r)
    x = [x for x in rels(r) if "37167" in x["valor"]][0]
    assert x["estado_associacao"] == "conflitante" and x["necessaria"] is False and x["bloqueia"] is False                  # registrado, nao bloqueia


def test_a_entidade_correta_com_destinatario_diferente_mesma_unidade_outra_localidade():
    t = reg_item(35477, "CAIXA ORGANIZADORA 28 LITROS", "do Hospital Regional do Guará") + "Publicado para a região de Taguatinga e Guará em 2025."
    o = itens_o("Foi adquirida CAIXA ORGANIZADORA 28 LITROS.", ["Código SES 35477 - CAIXA ORGANIZADORA 28 LITROS, para atender as necessidades do Hospital Regional do Guará"])
    r = rodar("Quais itens foram adquiridos para o Hospital Regional de Taguatinga em 2025?", [chunk(1, t, 496)], o, catalogo=cat_a({496: (t, [])}))
    assert r.verificacao["problemas"] == ["destinatario_conflitante"]
    ok_ = rodar("Quais itens foram adquiridos para o Hospital Regional do Guará em 2025?", [chunk(1, t, 496)], o, catalogo=cat_a({496: (t, [])}))
    assert entregue(ok_)                                                                                                    # mesmo destinatario: passa


def test_a_localidade_mencionada_sem_destinatario_no_registro_e_nao_verificavel_e_nao_bloqueia():
    t = "RATIFICO em 14 de abril de 2025, Processo SEI nº 00060-1/2025-11, cujo objeto é a aquisição do item Código SES 90462 - VITAMINA D 400 UI/G., no valor de R$ 1,00. Atenção Primária, Guará 2025."
    o = itens_o("Foi adquirido VITAMINA D 400 UI/G.", ["Código SES 90462 - VITAMINA D 400 UI/G."])
    r = rodar(Q_AP, [chunk(1, t + " RATIFICO em 2 de maio de 2025, outro registro.", 497)], o, catalogo=cat_a({497: (t, ["Guará"])}))
    assert entregue(r) and all(x["estado_associacao"] == "nao_verificavel" and x["destinatario_no_trecho"] is None for x in rels(r))


def test_a_nao_associa_registros_independentes_por_proximidade():
    t = ("RATIFICO em 1 de março de 2025, Processo SEI nº 00060-1111/2025-11, cujo objeto é a aquisição do item Código SES 111 - ITEM A SEM DESTINO, no valor de R$ 1,00; "
         + reg_item(222, "ITEM B", "do Hospital Regional do Guará", "5 de março", "00060-2222/2025-22") + "Atenção Primária, Guará 2025.")
    o = itens_o("Foi adquirido ITEM A SEM DESTINO.", ["Código SES 111 - ITEM A SEM DESTINO"])
    r = rodar(Q_AP, [chunk(1, t, 498)], o, catalogo=cat_a({498: (t, ["Guará"])}))
    assert entregue(r)                                                                                                       # o destinatario do registro vizinho nao e herdado
    x = rels(r)[0]
    assert x["destinatario_no_trecho"] is None and x["registro"]["id"] == "SEI 00060-1111/2025-11"                          # id proprio do registro, nao o do vizinho


def test_a_publicacao_sem_vinculo_com_a_localidade_perguntada_val_149():
    q = "Quais ações de atenção primária serão executadas em Ceilândia durante 2025?"
    estatuto = "Art. 23. O INAS poderá desenvolver e implementar programas voltados à promoção da saúde, prevenção de doenças e atenção primária em 2025."
    decreto = "Fica criada a Gerência de Serviços de Atenção Primária nº 07 da Ceilândia, Gerente, CC-05, em 2025."
    o = saida(resposta="Serão executados programas voltados à promoção da saúde e prevenção de doenças; a Gerência nº 07 da Ceilândia participa.", fontes=["C1", "C2"],
              cand=[{"fonte": "C1", "resposta_possivel": "programas voltados à promoção da saúde, prevenção de doenças e atenção primária"}, {"fonte": "C2", "resposta_possivel": "Gerência de Serviços de Atenção Primária nº 07 da Ceilândia"}],
              evid=[{"fonte": "C1", "trecho": "programas voltados à promoção da saúde, prevenção de doenças e atenção primária"}, {"fonte": "C2", "trecho": "Gerência de Serviços de Atenção Primária nº 07 da Ceilândia"}])
    cats = lambda t1, loc1="": cat_a({1611: (t1, [loc1] if loc1 else []), 1052: (decreto, ["Ceilândia"])})      # noqa: E731
    r = rodar(q, [chunk(1, estatuto, 1611), chunk(2, decreto, 1052)], o, catalogo=cats(estatuto))
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["publicacao_sem_vinculo_com_a_localidade"]       # a localidade vem da OUTRA publicacao (Fase 2 aceita), mas o estatuto nao a menciona
    ruim = [x for x in rels(r) if x["publicacao_menciona_localidade"] is False]
    assert ruim and all(x["causas_do_conflito"] == ["localidade_da_publicacao"] and x["doc_id"] == 1611 for x in ruim)
    assert all(x["publicacao_menciona_localidade"] is True for x in rels(r) if x["doc_id"] == 1052)
    # positivo: a publicacao menciona a localidade em outro chunk (texto completo) ou nos metadados
    assert entregue(rodar(q, [chunk(1, estatuto, 1611), chunk(2, decreto, 1052)], o, catalogo=cats(estatuto + " Unidade na Ceilândia.")))
    assert entregue(rodar(q, [chunk(1, estatuto, 1611), chunk(2, decreto, 1052)], o, catalogo=cats(estatuto, "Ceilândia")))


def test_a_trecho_sem_associacao_verificavel_val_007_fica_nao_verificavel_e_mantem_comportamento():
    ata = "A secretária compartilha sobre sua visita à São Paulo e conheceu o Hospital da Mulher, onde equipamentos funcionam 24 horas. Reunião realizada em Taguatinga em 2025."
    o = itens_o("Há programas voltados à saúde da mulher, como o Hospital da Mulher.", ["conheceu o Hospital da Mulher, onde equipamentos funcionam 24 horas"])
    r = rodar("Quais serviços de saúde estão sendo implementados em Taguatinga em 2025?", [chunk(1, ata, 1449)], o, catalogo=cat_a({1449: (ata, [])}))
    assert entregue(r) and all(x["estado_associacao"] == "nao_verificavel" and x["bloqueia"] is False for x in rels(r))   # nao ha como provar a atribuicao: registrado, sem bloqueio novo


def test_a_cada_mecanismo_de_associacao_e_necessario(monkeypatch):
    o = itens_o(f"Foram adquiridos {ITEM_AP} e {ITEM_HR}.", [f"Código SES 90462 - {ITEM_AP}, para atender as necessidades da Atenção Primária", f"Código SES 37167 - {ITEM_HR}, para atender"])
    cenario = lambda: rodar(Q_AP, [chunk(1, T_AP_HR, 495)], o, catalogo=cat_a({495: (T_AP_HR, ["Guará"])}))        # noqa: E731
    assert cenario().status == "insuficiente"
    monkeypatch.setattr(G, "PROTECOES_44", set(G.PROTECOES_44) - {"A_DEST"})
    assert entregue(cenario())
    monkeypatch.undo()
    q = "Quais ações de atenção primária serão executadas em Ceilândia durante 2025?"
    estatuto = "Art. 23. O INAS poderá desenvolver programas voltados à promoção da saúde e prevenção de doenças e atenção primária em 2025."
    decreto = "Fica criada a Gerência de Serviços de Atenção Primária nº 07 da Ceilândia em 2025."
    o2 = saida(resposta="Serão executados programas voltados à promoção da saúde; a Gerência nº 07 da Ceilândia participa.", fontes=["C1", "C2"],
               cand=[{"fonte": "C1", "resposta_possivel": "programas voltados à promoção da saúde e prevenção de doenças"}, {"fonte": "C2", "resposta_possivel": "Gerência de Serviços de Atenção Primária nº 07 da Ceilândia"}],
               evid=[{"fonte": "C1", "trecho": "programas voltados à promoção da saúde e prevenção de doenças"}, {"fonte": "C2", "trecho": "Gerência de Serviços de Atenção Primária nº 07 da Ceilândia"}])
    c2 = lambda: rodar(q, [chunk(1, estatuto, 1611), chunk(2, decreto, 1052)], o2, catalogo=cat_a({1611: (estatuto, []), 1052: (decreto, ["Ceilândia"])}))    # noqa: E731
    assert c2().status == "insuficiente"
    monkeypatch.setattr(G, "PROTECOES_44", set(G.PROTECOES_44) - {"A_LOC"})
    assert entregue(c2())


# =============================================================== replay offline dos 150 x comportamento da Fase 3 (baseline gravado antes das alteracoes da Fase 4A)
import json  # noqa: E402

import pytest  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]
RODADA = RAIZ / "data_assistente" / "derivados" / "geracao_e2e_41_20261114-130608.jsonl"
IDX = RAIZ / "data_assistente" / "indices" / "est300o30"
BASE = RAIZ / "docs" / "assistente" / "diagnostico_4_4" / "fase4" / "replay_baseline_fase3_comportamento.json"


@pytest.mark.skipif(not (RODADA.exists() and IDX.exists() and BASE.exists()), reason="rodada/indice/baseline indisponiveis")
def test_replay_150_fase4a_so_muda_val_083_e_val_149_e_nunca_promove(monkeypatch):
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
    base = json.loads(BASE.read_text(encoding="utf-8"))
    novo = {q["qid"]: gerar_resposta(q["pergunta"], idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25"), Falso(orig[q["qid"]]["saida"]["telemetria"]["saida_bruta"], cfg), cfg, catalogo=cat)
            for q in val}
    ordem = {"insuficiente": 0, "ambigua": 0, "fora_do_escopo": 0, "parcial": 1, "respondida": 2}
    mudaram = {k for k, r in novo.items() if r.status != base[k]["status"] or r.resposta != base[k]["resposta"]}
    assert mudaram == {"val-083", "val-149"}
    assert novo["val-083"].status == "insuficiente" and novo["val-083"].verificacao["problemas"] == ["destinatario_conflitante"]
    assert novo["val-149"].status == "insuficiente" and novo["val-149"].verificacao["problemas"] == ["publicacao_sem_vinculo_com_a_localidade"]
    for k in mudaram:                                                                   # nunca promove
        assert ordem[novo[k].status] <= ordem[base[k]["status"]]
    for k in novo:                                                                      # nenhuma promocao em todo o conjunto; abstencoes da Fase 3 inalteradas
        assert ordem[novo[k].status] <= ordem[base[k]["status"]]
    for k in ("val-062", "val-108", "val-126", "val-087", "val-039", "val-050", "val-130", "val-136", "val-141"):          # bloqueios legitimos da Fase 3 preservados
        assert novo[k].status == "insuficiente" and novo[k].verificacao["problemas"] == base[k]["problemas"], k
    for k in ("val-007", "val-012", "val-100", "val-044", "val-047"):                  # inalterados (nao verificaveis ou fora do alcance desta fase)
        assert novo[k].status == base[k]["status"] and novo[k].resposta == base[k]["resposta"], k
    rot = {r["qid"]: r["classificacao_independente"] for r in __import__("csv").DictReader(
        (RAIZ / "docs" / "assistente" / "auditoria_independente_4_3" / "auditoria_independente_150.csv").open(encoding="utf-8-sig"), delimiter=";")}
    for k, o in orig.items():                                                           # as 23 respostas corretas/corretas-mas-parciais seguem iguais
        if rot[k] in ("Correta", "Correta, mas parcial") and o["saida"]["status"] in ("respondida", "parcial"):
            assert novo[k].status == o["saida"]["status"] and novo[k].resposta == o["saida"]["resposta"], k
    for k in ("val-007", "val-012", "val-100", "val-044", "val-047", "val-087"):       # esquema auditavel presente nos casos de regressao
        prot = (novo[k].verificacao.get("evidencia") or {}).get("protecao", {})
        assert prot.get("esquema_relacoes") == "relacoes/3" and all(x["estado_associacao"] in ("confirmada", "conflitante", "nao_verificavel") for x in prot.get("relacoes", [])), k
