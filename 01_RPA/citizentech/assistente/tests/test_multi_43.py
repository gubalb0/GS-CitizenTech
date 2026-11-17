"""Etapa 4.3 — perguntas MULTI formuladas no singular: varias publicacoes independentes relevantes no corpus."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from citizentech.assistente import evidencias as EV  # noqa: E402,F401
from citizentech.assistente.catalogo import Catalogo  # noqa: E402
from citizentech.assistente.geracao import gerar_resposta, gerar_resposta_composta  # noqa: E402
from citizentech.assistente.tests.test_abstencao_42 import COM, COM_REP, SL1, SL2, cli, doc, ev, ok, res, saida  # noqa: E402

PERG = "Qual foi a modificação contratual realizada para equipamentos de radiologia no Hospital Regional de Ceilândia?"
# publicacao pedida: cobre 5 dos 6 termos da pergunta (nao traz 'realizada')
ADIT = doc(10, "Primeiro Termo Aditivo ao Contrato nº 51462/2024. Houve a modificação contratual com supressão de 5 equipamentos de radiologia "
               "(Raio X Panorâmico) no Hospital Regional de Ceilândia, reduzindo o valor global para R$ 1.080.420,48.", tipo="Extrato", ref="CONTRATO 51462/2024", data="2025-05-27")
# outra publicacao independente, tao relevante quanto a primeira (5 termos; falta 'modificacao', traz 'realizada'), com outro fato
ADIT2 = doc(11, "Segundo Termo Aditivo ao Contrato nº 60001/2023. A alteração contratual realizada prorrogou por 12 meses a manutenção de equipamentos de radiologia "
                "no Hospital Regional de Ceilândia, no valor de R$ 300.000,00.", tipo="Extrato", ref="CONTRATO 60001/2023", data="2025-08-10")
RUIDO = doc(12, "Dispensa de licitação para aquisição de eletrocardiógrafo para o Hospital Regional de Ceilândia, valor R$ 60.840,00.", tipo="Extrato", ref="DISPENSA 1/2025")
OUTRO_HOSP = doc(13, "Aquisição de seringas para o Hospital Regional de Planaltina, valor R$ 1.000,00.", tipo="Extrato", ref="DISPENSA 2/2025")


def saida_adit():
    return saida(resposta="Houve a supressão de 5 equipamentos de radiologia no Hospital Regional de Ceilândia.", fontes=["C1"],
                 evid=[ev("C1", "supressão de 5 equipamentos de radiologia")])


# 1. caso val-024: pergunta MULTI no singular; ha outra publicacao independente igualmente relevante -> nao escolher arbitrariamente
def test_multi_no_singular_com_outra_publicacao_relevante_nao_sai_completa():
    r = gerar_resposta(PERG, [res(ADIT)], cli(ok(saida_adit())), catalogo=Catalogo([ADIT, ADIT2, RUIDO, OUTRO_HOSP]))
    assert r.status == "ambigua" and r.verificacao["divergencia"] == "publicacao_nao_identificavel"
    assert "supressão" not in r.resposta and "Informe a data" in r.resposta
    assert r.telemetria["identificabilidade"]["n_relevantes_janela"] == 1                   # detectada por cobertura PARCIAL, em todo o corpus


# 1b. mesmo caso, mas o corpus so tem UMA publicacao relevante (o que ocorre com o val-024 real): resposta completa continua permitida
def test_uma_unica_publicacao_relevante_no_corpus_mantem_resposta_completa():
    r = gerar_resposta(PERG, [res(ADIT)], cli(ok(saida_adit())), catalogo=Catalogo([ADIT, RUIDO, OUTRO_HOSP]))
    assert r.status == "respondida" and "Fonte:" in r.resposta and r.telemetria["identificabilidade"]["n_relevantes_janela"] == 0


# 2. singular com duas publicacoes e valores diferentes -> ambigua, sem valor
def test_singular_duas_publicacoes_valores_diferentes():
    o = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    r = gerar_resposta("Qual o valor pago ao Hospital Santa Lúcia?", [res(SL1)], cli(ok(o)), catalogo=Catalogo([SL1, SL2]))
    assert r.status == "ambigua" and "R$57.102,73" not in r.resposta and "R$131,05" not in r.resposta


# 3. singular com varias publicacoes que dizem o mesmo (republicacao / ato-modelo) -> resposta, nao ambiguidade
def test_singular_publicacoes_equivalentes_nao_geram_ambiguidade():
    o = saida(resposta="O prazo é de 60 dias.", fontes=["C1"], evid=[ev("C1", "concluir o processo eleitoral é de 60 (sessenta) dias")])
    r = gerar_resposta("Qual o prazo máximo para a Comissão Eleitoral da Candangolândia concluir o processo eleitoral?", [res(COM)], cli(ok(o)),
                       catalogo=Catalogo([COM, COM_REP]))
    assert r.status == "respondida" and r.telemetria["identificabilidade"]["n_concorrentes"] == 0


# 4. plural com cobertura incompleta -> parcial, informando o que foi encontrado e o que nao foi confirmado
def test_plural_com_cobertura_incompleta_e_parcial_com_aviso_explicito():
    o = saida(resposta="Foram adquiridos eletrocardiógrafo.", fontes=["C1"], evid=[ev("C1", "aquisição de eletrocardiógrafo")])
    outras = [doc(20 + i, f"Dispensa de licitação para aquisição de material {i} no Hospital Regional de Ceilândia, valor R$ {i + 1}.000,00.", tipo="Extrato", ref=f"DISPENSA {i}/2025") for i in range(3)]
    r = gerar_resposta("Quais dispensas de licitação foram ratificadas para aquisição de material no Hospital Regional de Ceilândia?", [res(RUIDO)], cli(ok(o)), catalogo=Catalogo([RUIDO] + outras))
    assert r.status == "parcial" and "Fonte:" in r.resposta
    assert "não é possível confirmar que a lista está completa" in r.resposta and "ao menos 3 outra(s)" in r.resposta
    assert r.telemetria["cobertura_lista"] == {"publicacoes_analisadas": 1, "outras_relevantes_no_corpus": 3}


# 5. pergunta geral respondivel com uma publicacao: nao bloqueada
def test_pergunta_geral_respondivel_com_uma_publicacao_nao_e_bloqueada():
    cat = Catalogo([ADIT, ADIT2, RUIDO, OUTRO_HOSP])
    o = saida(resposta="Foi adquirido um eletrocardiógrafo portátil.", fontes=["C1"], evid=[ev("C1", "aquisição de eletrocardiógrafo")])
    r = gerar_resposta("Qual equipamento foi comprado por dispensa de licitação para o Hospital Regional de Ceilândia?", [res(RUIDO)], cli(ok(o)), catalogo=cat)
    assert r.status == "respondida"


# 6. republicacoes e duplicatas nao contam como publicacoes independentes
def test_duplicatas_e_republicacoes_nao_sao_publicacoes_independentes():
    dup = dict(ADIT, id=14, ids_equivalentes=[14])
    cat_dup = Catalogo([dict(ADIT, ids_equivalentes=[10, 14]), RUIDO])                    # o corpus deduplicado agrupa 10 e 14
    r = cat_dup.relevantes(PERG, [10])
    assert r["avaliavel"] and r["relevantes"] == []
    assert cat_dup.canonico(14) == 10
    # republicacao com os mesmos trechos de evidencia = concordante, nao relevante distinta
    rep = dict(ADIT, id=15, ids_equivalentes=[15], data_edicao="2025-06-01")
    r2 = Catalogo([ADIT, rep]).relevantes(PERG, [10], ["supressão de 5 equipamentos de radiologia"])
    assert r2["relevantes"] == [] and r2["concordantes"] == 1
    assert dup["id"] == 14


# 7. pergunta composta: cada parte e avaliada de forma independente
def test_pergunta_composta_partes_independentes_avaliadas_separadamente():
    cat = Catalogo([ADIT, ADIT2, SL1, OUTRO_HOSP])
    o1 = saida_adit()
    o2 = saida(resposta="O valor é R$57.102,73.", fontes=["C1"], evid=[ev("C1", "Valor: R$57.102,73")])
    rec = lambda p: [res(ADIT)] if "radiologia" in p else [res(SL1)]       # noqa: E731
    r = gerar_resposta_composta(PERG + " E também: qual o valor pago ao Hospital Santa Lúcia?", rec, cli(ok(o1), ok(o2)), catalogo=cat)
    st = [p["status"] for p in r.telemetria["partes"]]
    assert st == ["ambigua", "respondida"]                                  # 1a parte tem outra publicacao relevante; 2a e identificavel (so SL1)


# 8. politica em lote: relevancia exige minimo de termos
def test_relevancia_exige_minimo_de_termos():
    cat = Catalogo([RUIDO, OUTRO_HOSP])
    assert not cat.relevantes("Qual o valor?", [12])["avaliavel"]


# ---------------------------------------------------------------- regressao com o corpus REAL (pulada se os dados nao estiverem disponiveis)
def _corpus_real():
    import pytest
    try:
        from citizentech.assistente import avaliacao_e2e as E
        return E.preparar()
    except Exception as e:                                           # pragma: no cover
        pytest.skip(f"corpus real indisponivel: {e}")


def test_regressao_val_024_continua_respondida_com_o_corpus_real():
    """MULTI declarado pelo dataset (5 publicacoes associadas) != multiplicidade real: so a publicacao 718 trata da modificacao contratual."""
    corpus, val, assoc, dup, esp, docs = _corpus_real()
    i = next(k for k, q in enumerate(val) if q["qid"] == "val-024")
    assert assoc[i]["multi"] and len(esp[i]) == 5                    # o rotulo do dataset existe...
    cat = Catalogo.de_corpus(corpus)
    d = docs[718]
    trecho = "supressão de 5 (cinco) equipamentos de Raio X Panorâmico"
    from citizentech.assistente.dados import norm_forte
    assert norm_forte(trecho) in norm_forte(d["texto_completo"])
    rel = cat.relevantes(val[i]["pergunta"], [718], [trecho])
    assert rel["avaliavel"] and rel["relevantes"] == []              # ...mas o corpus so tem UMA publicacao relevante
    o = saida(resposta="Houve a supressão de 5 equipamentos de Raio X Panorâmico no Hospital Regional de Ceilândia.", fontes=["C1"], evid=[ev("C1", trecho)])
    r = gerar_resposta(val[i]["pergunta"], [res({**d, "ids_equivalentes": [d["id"]]})], cli(ok(o)), catalogo=cat)
    assert r.status == "respondida" and "Fonte:" in r.resposta
    assert r.telemetria["identificabilidade"]["n_relevantes_janela"] == 0


def test_auditoria_do_rotulo_multi_classifica_val_024_como_associacao_frouxa():
    _corpus_real()
    from citizentech.assistente.auditoria_multi import analisar
    x = {l["qid"]: l for l in analisar()}["val-024"]
    assert x["multi_declarado_pelo_dataset"] and x["n_publicacoes_associadas"] == 5 and x["n_efetivamente_relevantes"] == 1
    assert x["classificacao"].startswith("associacao frouxa")
