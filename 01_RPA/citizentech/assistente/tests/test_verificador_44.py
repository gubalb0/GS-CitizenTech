"""Etapa 4.4 / Fase 2 - verificador: falsos positivos corrigidos (com evidencia rastreavel) e bloqueios legitimos preservados.

Cada teste positivo tem um negativo correspondente: o que passou a ser aceito nunca pode ser aceito quando a evidencia vem de OUTRA publicacao,
de outro chunk (para a citacao), de numero inexistente ou de texto corrompido.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_geracao import cli, ok, saida  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402
from citizentech.assistente import geracao as G  # noqa: E402
from citizentech.assistente.geracao import gerar_resposta  # noqa: E402
from citizentech.assistente.retriever import Resultado  # noqa: E402


def chunk(pos, texto, doc, ordem=0, data="2025-07-02", **meta):
    m = {"edicao": 121, "data_edicao": data, "secao": "Seção III", "referencia": f"{doc}/2025", "tipo_documento": "Extrato",
         "numero_documento": f"EXTRATO {doc}", "ordem": ordem, "n_chunks_doc": 3}
    m.update(meta)
    return Resultado(pos, f"dodf-{doc}:est300o30:{ordem:04d}", doc, 20.0 - pos, texto, [doc, 5000 + doc], {"bm25": pos}, m)


def rodar(pergunta, chunks, obj, catalogo=None):
    c, _ = cli(ok(obj))
    return gerar_resposta(pergunta, chunks, c, catalogo=catalogo)


# ---------------------------------------------------------------- casar_citacao (val-047, val-032/045, val-062, val-097)
TXT = ("Unidade de Saúde CNES Endereço UBS 04 ITAPOÃ 4986725 DF 250, km 08, Fazenda Velha - Galpão da Associação dos Produtores Rurais "
       "UBS 03 JARDIM BOTÂNICO 4986725 DF 140, km 4,5 - Boxes 16, 18 e 23, Centro Comercial Alpha Center. Vigência: a contar da assinatura. "
       "402 - Anestesiologia - Hospital Regional do Gama (HRG), 0342101062, VANESSA DE SOUSA LEAL LIMA, 90.01, 1. "
       "Valor 10.301.6202.3135.0003 449051 R$ 5.250.814,42 Objeto: construção.")


def test_pontuacao_diferente_nao_impede_citacao_literal_val_047():
    c = EV.casar_citacao("402 - Anestesiologia - Hospital Regional do Gama (HRG) - 0342101062, VANESSA", TXT)
    assert c["status"] == "literal"                               # virgula do documento virou hifen na citacao


def test_digitos_continuam_exatos_e_separadores_de_numero_importam():
    assert EV.casar_citacao("R$ 5.250.814,42", TXT)["status"] == "literal"
    assert EV.casar_citacao("R$ 5.250.814,43", TXT)["status"] == "fabricada"          # digito trocado
    assert EV.casar_citacao("R$ 5,250,814.42", TXT)["status"] in ("fabricada", "nao_literal")     # separadores trocados nao equivalem


def test_n_ponto_o_e_n_o_equivalem():
    assert EV.casar_citacao("Convênio nº 026202/2024 dando", "foi o Convênio n.º 026202/2024 dando ciência")["status"] == "literal"


def test_emenda_de_linhas_e_reparada_e_so_o_literal_vale_val_032_045():
    q = "Unidade de Saúde CNES Endereço UBS 03 JARDIM BOTÂNICO 4986725 DF 140, km 4,5 - Boxes 16, 18 e 23, Centro Comercial Alpha Center"
    c = EV.casar_citacao(q, TXT)
    assert c["status"] == "reparada" and len(c["fragmentos"]) == 2
    assert "itapoa" not in c["verificado"] and "jardim botanico" in c["verificado"]       # a linha pulada NAO e evidencia


def test_emenda_fora_de_ordem_ou_dispersa_nao_e_reparada():
    desordem = "UBS 03 JARDIM BOTÂNICO 4986725 DF 140 Unidade de Saúde CNES Endereço UBS 04 ITAPOÃ"
    assert EV.casar_citacao(desordem, TXT)["status"] == "nao_literal"
    texto = "inicio do registro oficial " + " ".join(f"x{i}" for i in range(300)) + " fim do registro oficial"
    assert EV.casar_citacao("inicio do registro oficial fim do registro oficial", texto)["status"] == "nao_literal"      # fragmentos a >120 tokens


def test_cobertura_baixa_nao_e_reparada():
    assert EV.casar_citacao("UBS 03 JARDIM BOTÂNICO inventei varias palavras que nao existem no documento oficial de forma alguma jamais", TXT)["status"] == "nao_literal"


def test_numero_inexistente_e_fabricacao_val_062():
    q = "Espécie: contrato. Valor do Contrato: R$ 1.105.500,00 (um milhão)"
    txt = "Espécie: contrato. Valor do Contrato : R$ 2.449.859,97 (dois milhões). Empenho R$ 204.155,00"
    c = EV.casar_citacao(q, txt)
    assert c["status"] == "fabricada" and "1.105.500,00" in c["fabricados"]


def test_numero_cortado_no_fim_da_citacao_nao_e_fabricacao_val_097():
    c = EV.casar_citacao("NATUREZA DA DESPESA FONTE VALOR 10.301", "x NATUREZA DA DESPESA FONTE VALOR 10.301.6202.3135.0003 449051 R$ 5.250.814,42")
    assert c["status"] == "reparada" and c.get("truncada") and "5.250.814,42" not in c["verificado"]      # a citacao truncada NAO ganha o valor
    assert EV.casar_citacao("NATUREZA DA DESPESA FONTE VALOR 10.999", "x NATUREZA DA DESPESA FONTE VALOR 10.301.6202")["status"] == "fabricada"


def test_citacao_de_outro_chunk_nao_e_literal():
    assert EV.casar_citacao("instalação de tendas e prestação de serviço", "texto do outro chunk sem aquela frase")["status"] == "nao_literal"
    assert EV.casar_citacao("instalação de 11 tendas", "texto do outro chunk sem aquela frase")["status"] == "fabricada"      # numero ausente do chunk


def test_alfabeto_estranho():
    assert EV.tem_alfabeto_estranho("Diretor, CPE-07, 01 -超级") and not EV.tem_alfabeto_estranho("Atenção Básica, ação — nº 3 ≥ 75%")


# ---------------------------------------------------------------- periodo e alinhamento
def test_mes_por_data_numerica_val_106():
    sal = EV.termos_salientes("Termo de Compromisso assinado em junho de 2025?")
    assert EV.periodo_ausente(sal, "DATA DA ASSINATURA: 27/06/2025", "2025-07-02") == []
    assert EV.periodo_ausente(sal, "DATA DA ASSINATURA: 27/05/2025", "2025-07-02") == ["junho"]        # outro mes: continua ausente
    assert EV.periodo_ausente(sal, "sem datas", "2025-07-02") == ["junho"]


def test_alinhamento_aceita_nome_na_mesma_publicacao_com_origem_e_recusa_se_ausente_val_087_141():
    q = "Quais as competências da Coordenação de Regulação da Região Sul?"
    cit = [("As Deliberações deverão nortear as gerências de regulação", "2025-02-06")]
    pub = [("Art. 1º Instituir a Coordenação de Regulação da Região de Saúde Sul (CRSSU)", "documento_completo:174")]
    a = EV.alinhamento(q, cit, pub)
    assert a["ok"] and a["origens"]["coordenacao"] == "documento_completo:174"
    assert not EV.alinhamento(q, cit, None)["ok"]                                    # sem a mesma publicacao: continua reprovado
    assert not EV.alinhamento(q, cit, [("Art. 1º Instituir a Gerência de Planejamento", "documento_completo:9")])["ok"]


# ---------------------------------------------------------------- afirmacoes: candidata literal como evidencia adicional
def test_candidata_literal_sustenta_valor_fora_da_citacao_truncada_com_origem_val_097():
    resp = "O valor descentralizado é R$ 5.250.814,42."
    o = {}
    assert EV.afirmacoes_nao_sustentadas(resp, ["natureza da despesa fonte valor 10.301"], "Qual o valor?", "") == ["5.250.814,42"]
    assert EV.afirmacoes_nao_sustentadas(resp, ["natureza da despesa fonte valor 10.301"], "Qual o valor?", "",
                                         adicionais=[("R$ 5.250.814,42", "candidata_literal:dodf-105:est300o30:0000")], origens=o) == []
    assert o["5.250.814,42"].startswith("candidata_literal")
    assert EV.afirmacoes_nao_sustentadas("O valor é R$ 9.999.999,99.", ["x"], "Qual o valor?", "", adicionais=[("R$ 5.250.814,42", "c")]) == ["9.999.999,99"]


# ---------------------------------------------------------------- integracao (gerar_resposta com saida do modelo gravada)
PERG_097 = "Qual é o valor descentralizado para a construção da unidade básica de saúde no Gama em 2025?"
C097 = ("PLANO DE TRABALHO NATUREZA DA DESPESA FONTE VALOR 10.301.6202.3135.0003 449051 100 R$ 5.250.814,42 I – OBJETO: Construção da Unidade Básica de "
        "Saúde da Ponte Alta do Gama. II – DESCENTRALIZAÇÃO: conforme disponibilidade orçamentária, 2025.")


def test_val_097_valor_no_documento_e_na_candidata_mas_fora_da_citacao_truncada():
    o = saida(resposta="O valor descentralizado é R$ 5.250.814,42.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "R$ 5.250.814,42"}],
              evid=[{"fonte": "C1", "trecho": "PLANO DE TRABALHO NATUREZA DA DESPESA FONTE VALOR 10.301"}])
    r = rodar(PERG_097, [chunk(1, C097, 105)], o)
    assert r.status == "respondida" and r.verificacao["ok"]
    assert r.verificacao["evidencia"]["origem_dos_termos"]["5.250.814,42"].startswith("candidata_literal")
    assert r.evidencias[0]["citacao"] == "reparada"


def test_val_097_negativo_valor_que_nao_esta_no_documento_continua_bloqueado():
    o = saida(resposta="O valor descentralizado é R$ 9.999.999,99.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "R$ 9.999.999,99"}],
              evid=[{"fonte": "C1", "trecho": "NATUREZA DA DESPESA FONTE VALOR 10.301"}])
    r = rodar(PERG_097, [chunk(1, C097, 105)], o)
    assert r.status == "insuficiente"                      # candidata nao literal => nao e evidencia


def test_val_106_entidade_na_candidata_e_mes_em_data_numerica():
    txt = ("PROCESSO Nº 00060-1/2025 ESPÉCIE: Termo de Compromisso celebrado entre a DIVISA e o estabelecimento Hospital Lago Sul S/A, (Hospital Daher), "
           "situado no Lago Sul. OBJETO: Celebração do Termo de Compromisso. DATA DA ASSINATURA DO TERMO DE COMPROMISSO: 27/06/2025.")
    o = saida(resposta="O Hospital Lago Sul S/A, também conhecido como Hospital Daher, assinou o Termo de Compromisso em junho de 2025.", fontes=["C1"],
              cand=[{"fonte": "C1", "resposta_possivel": "Hospital Lago Sul S/A, (Hospital Daher)"}],
              evid=[{"fonte": "C1", "trecho": "DATA DA ASSINATURA DO TERMO DE COMPROMISSO: 27/06/2025."}])
    r = rodar("Qual instituição hospitalar em Lago Sul assinou um Termo de Compromisso em junho de 2025?", [chunk(1, txt, 994, data="2025-07-02")], o)
    assert r.status == "respondida", r.verificacao
    # negativo: a data numerica e de outro mes
    r2 = rodar("Qual instituição hospitalar em Lago Sul assinou um Termo de Compromisso em junho de 2025?", [chunk(1, txt.replace("27/06/2025", "27/05/2025"), 994, data="2025-07-02")],
               {**o, "evidencias": [{"fonte": "C1", "trecho": "DATA DA ASSINATURA DO TERMO DE COMPROMISSO: 27/05/2025."}]})
    assert r2.status == "insuficiente" and any("mes=junho" in p for p in r2.verificacao["problemas"])


def test_val_031_ano_no_chunk_vizinho_da_mesma_publicacao_e_aceito_e_de_outra_publicacao_nao():
    c1 = chunk(1, "Relatório assistencial do terceiro trimestre de 2023 do HCB, contrato de gestão.", 1464, ordem=0, data="2025-09-26")
    c2 = chunk(2, "Satisfação dos Pacientes — meta ≥75%; julho — 94,2%, agosto — 96,6%, setembro — 97,6%;", 1464, ordem=1, data="2025-09-26")
    o = saida(resposta="Os indicadores no terceiro trimestre de 2023 foram: 94,2% em julho, 96,6% em agosto e 97,6% em setembro.", fontes=["C2"],
              cand=[{"fonte": "C2", "resposta_possivel": "julho — 94,2%, agosto — 96,6%, setembro — 97,6%"}],
              evid=[{"fonte": "C2", "trecho": "julho — 94,2%, agosto — 96,6%, setembro — 97,6%"}])
    r = rodar("Quais foram os indicadores de satisfação dos pacientes no terceiro trimestre de 2023?", [c1, c2], o)
    assert r.status in ("respondida", "parcial") and r.verificacao["ok"], r.verificacao
    # negativo: o ano 2023 so aparece em OUTRA publicacao (doc 9999), nao na citada
    outro = chunk(1, "Relatório assistencial do terceiro trimestre de 2023 de outro hospital.", 9999, data="2025-09-26")
    r2 = rodar("Quais foram os indicadores de satisfação dos pacientes no terceiro trimestre de 2023?", [outro, c2], o)
    assert r2.status == "insuficiente"


def test_val_087_nome_so_no_documento_da_mesma_publicacao_nunca_de_outra():
    c1 = chunk(1, "As Deliberações deverão nortear as respectivas gerências de regulação, no cumprimento das atribuições regimentais de implementar normas.", 174, ordem=1)
    c0 = chunk(2, "Art. 1º Instituir a Coordenação de Regulação da Região de Saúde Sul (CRSSU), na forma de uma comissão.", 174, ordem=0)
    o = saida(resposta="A Coordenação nortear as gerências de regulação em 2025.", fontes=["C1"], cand=[],
              evid=[{"fonte": "C1", "trecho": "nortear as respectivas gerências de regulação"}])
    perg = "Quais as competências da Coordenação de Regulação da Região Sul em 2025?"
    assert rodar(perg, [c1, c0], o).status in ("respondida", "parcial")
    c0_outra = chunk(2, "Art. 1º Instituir a Coordenação de Regulação da Região de Saúde Sul (CRSSU), na forma de uma comissão.", 888, ordem=0)
    assert rodar(perg, [c1, c0_outra], o).status == "insuficiente"                    # o nome so existe em OUTRA publicacao


def test_val_032_emenda_aceita_com_so_o_literal_e_valor_da_linha_pulada_nao():
    texto = TXT
    q = "Unidade de Saúde CNES Endereço UBS 03 JARDIM BOTÂNICO 4986725 DF 140, km 4,5 - Boxes 16, 18 e 23, Centro Comercial Alpha Center"
    o = saida(resposta="A UBS 03 JARDIM BOTÂNICO foi incluída em 2025.", fontes=["C1"], cand=[{"fonte": "C1", "resposta_possivel": "UBS 03 JARDIM BOTÂNICO"}],
              evid=[{"fonte": "C1", "trecho": q}])
    perg = "Quais UBS no Jardim Botânico foram incluídas no contrato em 2025?"
    r = rodar(perg, [chunk(1, texto, 1451, data="2025-09-24")], o)
    assert r.status in ("respondida", "parcial") and r.evidencias[0]["citacao"] == "reparada"
    # negativo: a resposta afirma o que so esta na linha PULADA pela emenda (ITAPOÃ, CNES 250) e nao na candidata/citacao
    o2 = saida(resposta="A UBS 04 ITAPOÃ foi incluída em 2025.", fontes=["C1"], cand=[], evid=[{"fonte": "C1", "trecho": q}])
    assert rodar(perg, [chunk(1, texto, 1451, data="2025-09-24")], o2).status == "insuficiente"


def test_val_062_numero_fabricado_continua_bloqueado():
    texto = "Contrato nº 055363/2025. Valor do Contrato : R$ 2.449.859,97. Valor de empenho inicial: R$ 204.155,00. Emitido em 10/09/2025."
    o = saida(resposta="O valor foi R$ 1.105.500,00.", fontes=["C1"], cand=[], evid=[{"fonte": "C1", "trecho": "Valor do Contrato: R$ 1.105.500,00 (um milhão)"}])
    r = rodar("Qual o valor do contrato nº 055363/2025?", [chunk(1, texto, 1450)], o)
    assert r.status == "insuficiente" and any(p.startswith("citacao_fabricada") for p in r.verificacao["problemas"])


def test_val_108_caracteres_de_outro_alfabeto_bloqueiam_mesmo_com_o_resto_literal():
    texto = "SUPERINTENDÊNCIA DA REGIÃO DE SAÚDE OESTE - GERÊNCIA DE SERVIÇOS DE ATENÇÃO PRIMÁRIA Nº 07 DA CEILÂNDIA - Gerente, CPC-05, 01 - 2025"
    o = saida(resposta="A unidade é a GERÊNCIA DE SERVIÇOS DE ATENÇÃO PRIMÁRIA Nº 07 DA CEILÂNDIA.", fontes=["C1"],
              cand=[{"fonte": "C1", "resposta_possivel": "GERÊNCIA DE SERVIÇOS DE ATENÇÃO PRIMÁRIA Nº 07 DA CEILÂNDIA"}],
              evid=[{"fonte": "C1", "trecho": "GERÊNCIA DE SERVIÇOS DE ATENÇÃO PRIMÁRIA Nº 07 DA CEILÂNDIA - Gerente, CPC-05, 01 -超级"}])
    r = rodar("Qual unidade de atenção primária em Ceilândia em 2025?", [chunk(1, texto, 1052)], o)
    assert r.status == "insuficiente" and "caracteres_fora_do_alfabeto" in r.verificacao["problemas"]
    ok_ = {**o, "evidencias": [{"fonte": "C1", "trecho": "GERÊNCIA DE SERVIÇOS DE ATENÇÃO PRIMÁRIA Nº 07 DA CEILÂNDIA - Gerente, CPC-05, 01"}]}
    assert rodar("Qual unidade de atenção primária em Ceilândia em 2025?", [chunk(1, texto, 1052)], ok_).status in ("respondida", "parcial")


def test_val_126_citacao_literal_em_outro_chunk_da_mesma_publicacao_continua_bloqueada():
    c1 = chunk(1, "irregularidades relacionadas ao Convênio nº 026202/2024-SES/DF, que cuidam da instalação de 11 tendas e prestação de serviço de atendimento.", 1014, ordem=0)
    c2 = chunk(2, "A Corte determina ciência a Convênio nº 026202/2024-SES/DF, dando ciência ao relator no prazo.", 1014, ordem=1)
    o = saida(resposta="O objeto foi a instalação de 11 tendas.", fontes=["C2"], cand=[],
              evid=[{"fonte": "C2", "trecho": "Convênio nº 026202/2024-SES/DF, que cuidam da instalação de 11 tendas e prestação de serviço de atendimento"}])
    r = rodar("Qual foi o objeto do Convênio nº 026202/2024-SES/DF em 2025?", [c1, c2], o)
    assert r.status == "insuficiente"
    assert "citacao_em_outro_chunk:C2->C1" in r.verificacao["problemas"]             # diagnostico explicito: erro de rastreabilidade (chunk errado)


def test_candidata_de_fonte_sem_citacao_verificada_nao_e_evidencia_val_033():
    c1 = chunk(1, "serviço de manutenção no BERÇO AQUECIDO FANEM para o Hospital Regional de Ceilândia 2025.", 10, ordem=0)
    c3 = chunk(3, "serviço de manutenção corretiva no APARELHO DE ANESTESIA para o Hospital Regional de Ceilândia 2025.", 11, ordem=0)
    o = saida(resposta="Foram contratados: BERÇO AQUECIDO FANEM e APARELHO DE ANESTESIA.", fontes=["C1", "C2"],
              cand=[{"fonte": "C1", "resposta_possivel": "serviço de manutenção no BERÇO AQUECIDO FANEM"},
                    {"fonte": "C2", "resposta_possivel": "serviço de manutenção corretiva no APARELHO DE ANESTESIA"}],
              evid=[{"fonte": "C1", "trecho": "serviço de manutenção no BERÇO AQUECIDO FANEM"}])
    r = rodar("Quais serviços de manutenção foram contratados para o Hospital Regional de Ceilândia em 2025?", [c1, c3], o)
    assert r.status == "insuficiente" and any("anestesia" in p for p in r.verificacao["problemas"])


def test_fato_unico_nao_combina_publicacoes_diferentes():
    a = chunk(1, "O Hospital Alfa Saúde foi credenciado em 2025 conforme o termo de credenciamento.", 21)
    b = chunk(2, "O contrato com a empresa Beta Ltda tem o valor de R$ 3.141,59 em 2025.", 22)
    o = saida(resposta="Hospital Alfa Saúde tem valor R$ 3.141,59.", fontes=["C1", "C2"],
              cand=[{"fonte": "C1", "resposta_possivel": "Hospital Alfa Saúde"}, {"fonte": "C2", "resposta_possivel": "R$ 3.141,59"}],
              evid=[{"fonte": "C1", "trecho": "O Hospital Alfa Saúde foi credenciado em 2025"}, {"fonte": "C2", "trecho": "o valor de R$ 3.141,59 em 2025"}])
    r = rodar("Qual é o valor do Hospital Alfa Saúde em 2025?", [a, b], o)
    assert r.status == "insuficiente" and "evidencias_de_publicacoes_distintas_combinadas" in r.verificacao["problemas"]
    # mesma combinacao em pergunta de lista/composta continua permitida (cada termo na sua publicacao)
    r2 = rodar("Quais são o hospital e o valor do contrato em 2025?", [a, b], o)
    assert "evidencias_de_publicacoes_distintas_combinadas" not in r2.verificacao.get("problemas", [])


def test_niveis_de_evidencia_encontrada_x_atribuivel():
    n = EV.classificar_niveis("Hospital Alfa Saúde tem R$ 3.141,59.", "Qual o valor?", {"21": [("citacao_verificada", "Hospital Alfa Saúde foi credenciado")]},
                              ["O contrato da Beta tem R$ 3.141,59", "Hospital Alfa Saúde"], False)
    assert "3.141,59" in n["sem_evidencia"] and "3.141,59" in n["encontrada_so_em_outra_publicacao"]       # encontrada no contexto, NAO atribuivel
    assert n["atribuicao"].get("alfa")


# ---------------------------------------------------------------- regressao real (somente leitura; saidas brutas gravadas, sem LLM)
RAIZ = Path(__file__).resolve().parents[3]
RODADA = RAIZ / "data_assistente" / "derivados" / "geracao_e2e_41_20261114-130608.jsonl"
IDX = RAIZ / "data_assistente" / "indices" / "est300o30"


@pytest.mark.skipif(not (RODADA.exists() and IDX.exists()), reason="rodada/indice 4.3 indisponiveis")
def test_replay_da_rodada_43_so_muda_os_casos_esperados(monkeypatch):
    """Fase 2 ISOLADA: as protecoes da Fase 3 (PROTECOES_44) sao desligadas aqui; o efeito combinado e verificado em test_protecao_44.py."""
    monkeypatch.setattr(G, "PROTECOES_44", set())
    from citizentech.assistente import avaliacao_e2e as AE
    from citizentech.assistente.catalogo import Catalogo
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
    novo = {}
    for q in val:
        o = orig[q["qid"]]
        res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25")
        novo[q["qid"]] = gerar_resposta(q["pergunta"], res, Falso(o["saida"]["telemetria"]["saida_bruta"], cfg), cfg, catalogo=cat)
    mudaram = {k for k, r in novo.items() if r.status != orig[k]["saida"]["status"]}
    assert mudaram == {"val-031", "val-032", "val-044", "val-045", "val-047", "val-083", "val-087", "val-097", "val-106", "val-141"}
    for k in ("val-062", "val-108", "val-126"):                                    # bloqueios legitimos preservados
        assert novo[k].status == "insuficiente"
    for k in ("val-031", "val-032", "val-047", "val-087", "val-141"):
        assert novo[k].status == "parcial" and not any(p.startswith(("trecho_nao_literal", "afirmacoes", "valores_nao")) for p in novo[k].verificacao["problemas"])
    for k in ("val-045", "val-097", "val-106"):                                    # verificador aprova; a politica de identificabilidade (inalterada) decide
        assert novo[k].status == "ambigua" and novo[k].verificacao["divergencia"] == "publicacao_nao_identificavel"
    for k, o in orig.items():                                                      # nenhuma das 31 respostas dadas na 4.3 mudou de status nem de texto
        if o["saida"]["status"] in ("respondida", "parcial"):
            assert novo[k].status == o["saida"]["status"] and novo[k].resposta == o["saida"]["resposta"]
