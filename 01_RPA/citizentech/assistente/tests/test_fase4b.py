"""Etapa 4.4 / Fase 4B (PREPARACAO, nao validada) - mecanismo B v2: necessidade do trecho sem limiar de comprimento. Testes sinteticos T1-T6."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_fase4a import COMP, MEMB, OUTRA, Q87, chunk, entregue, o87, rels, rodar  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402

C1 = "Art. 4º Competência e Disposições Gerais da CRSSU em 2025. " + COMP + " " + MEMB
SP_COMP = "Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados"
SP_MEMB = "Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: substituto"
SP_OUTRA = "Titular: Maria da Silva, representante da Região Norte"


def test_termos_de_uso_sem_limiar_de_comprimento():
    t = EV.termos_de_uso("A CRSSU deve ter 12 vagas em HRG e UTI.", Q87)
    assert "12" in t and "hrg" in t and "uti" in t and "crssu" in t and "a" not in t and "em" not in t and "e" not in t
    assert EV.termos_de_uso("Sim.", Q87) == []


def test_T1_span_correto_mais_secundario_conflitante_nao_usado_entrega():
    r = rodar(Q87, [chunk(1, C1, 174), chunk(2, OUTRA, 175)],
              o87("Compete à CRSSU discutir e deliberar.", [("C1", SP_COMP), ("C2", SP_OUTRA)], fontes=("C1", "C2")))
    assert entregue(r), r.verificacao
    x = [x for x in rels(r) if x["chunk_id"].startswith("dodf-175")][0]
    assert x["estado_associacao"] == "conflitante" and x["necessaria"] is False and x["bloqueia"] is False      # conflito registrado, nao bloqueia


def test_T2_resposta_de_uma_palavra_e_fail_closed_com_span_conflitante():
    # uso nao mensuravel: nenhum termo da resposta; com span conflitante presente, mantem o bloqueio
    r = rodar(Q87, [chunk(1, C1, 174), chunk(2, OUTRA, 175)], o87("Sim.", [("C1", SP_COMP), ("C2", SP_OUTRA)], fontes=("C1", "C2")))
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["rotulo_incompativel_com_atributo"]
    assert all(x["medida_de_uso"] == "nao_mensuravel" for x in rels(r))
    # sem span conflitante, a resposta curta segue entregue
    r2 = rodar(Q87, [chunk(1, C1, 174)], o87("Sim.", [("C1", SP_COMP)]))
    assert entregue(r2)


def test_T3_somente_numeros_pequenos_sao_medidos():
    c = chunk(1, "Art. 4º Competência da CRSSU em 2025. Compete à CRSSU emitir 12 pareceres e 30 laudos. " + MEMB.replace("(HRG)", "(HRG) 12"), 174)
    r = rodar(Q87, [c, chunk(2, "Comitê de Ética da Região Norte, 2025: 1 - Titular: Ana, 7 membros.", 175)],
              o87("12 pareceres e 30 laudos.", [("C1", "Compete à CRSSU emitir 12 pareceres e 30 laudos"), ("C2", "Titular: Ana, 7 membros")], fontes=("C1", "C2")))
    assert entregue(r), r.verificacao
    assert EV.termos_de_uso("12 e 30", Q87) == ["12", "30"]
    x = [x for x in rels(r) if x["chunk_id"].startswith("dodf-175")][0]
    assert x["necessaria"] is False and x["bloqueia"] is False


def test_T4_termo_em_dois_spans_um_conflitante_nao_bloqueia():
    c1 = chunk(1, "Art. 4º IV - Compete à CRSSU deliberar sobre o credenciamento de leitos em 2025.", 174)
    c2 = chunk(2, "Comitê da Coordenação de Regulação da Região Sul, 2025: 1 - Titular: Ana, responsável pelo credenciamento de leitos.", 175)
    r = rodar(Q87, [c1, c2], o87("Compete deliberar sobre o credenciamento de leitos.",
                                 [("C1", "Compete à CRSSU deliberar sobre o credenciamento de leitos"), ("C2", "Titular: Ana, responsável pelo credenciamento de leitos")], fontes=("C1", "C2")))
    assert entregue(r), r.verificacao
    assert all(not x["bloqueia"] for x in rels(r))


def test_T5_siglas_contam_como_termo_de_uso():
    c1 = chunk(1, "Art. 4º " + COMP, 174)
    c2 = chunk(2, MEMB, 174, ordem=1, n=5)
    # sigla HRG so existe no span conflitante -> necessario -> bloqueia
    r = rodar(Q87, [c1, c2], o87("Compete à CRSSU discutir e deliberar, com o HRG.", [("C1", SP_COMP), ("C2", SP_MEMB)], fontes=("C1", "C2")))
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["rotulo_incompativel_com_atributo"]
    assert "hrg" in " ".join(x for r_ in rels(r) for x in r_["termos_exclusivos"]) or any(x["necessaria"] for x in rels(r))
    # sigla CRSSU apoiada pelo span correto -> entrega
    r2 = rodar(Q87, [c1, c2], o87("Compete à CRSSU discutir e deliberar.", [("C1", SP_COMP), ("C2", SP_MEMB)], fontes=("C1", "C2")))
    assert entregue(r2), r2.verificacao


def test_T6_unico_span_conflitante_com_resposta_nao_mensuravel_continua_bloqueando():
    c = chunk(1, "Art. 2º Designar membros da Coordenação de Regulação da Região Sul (CRSSU) em 2025: 4 - Titular: Diretor do Hospital Regional do Gama (HRG).", 174)
    r = rodar(Q87, [c], o87("Sim.", [("C1", "Titular: Diretor do Hospital Regional do Gama (HRG)")]))
    assert r.status == "insuficiente" and r.verificacao["problemas"] == ["rotulo_incompativel_com_atributo"]
    assert rels(r)[0]["medida_de_uso"] == "nao_mensuravel" and rels(r)[0]["necessaria"] is True


def test_necessidade_independe_de_comprimento_de_palavras_longas():
    # resposta com palavra longa irrelevante (generica da pergunta) nao pode tornar necessario um span que so a sustenta por palavra da pergunta
    r = rodar(Q87, [chunk(1, C1, 174), chunk(2, OUTRA, 175)],
              o87("Compete à CRSSU discutir e deliberar sobre a regulação da Região Sul.", [("C1", SP_COMP), ("C2", SP_OUTRA)], fontes=("C1", "C2")))
    assert entregue(r), r.verificacao
