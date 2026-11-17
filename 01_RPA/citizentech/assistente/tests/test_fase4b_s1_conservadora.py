"""Etapa 4.4 / Fase 4B (CANDIDATA, nao validada) - S1 conservadora integrada: so promove chunk de rotulo explicito se o contexto selecionado nao cobre o atributo.
Cobertura = criterio ESTRUTURAL (rotulo em posicao de rotulo ou, so para VALOR, 'R$ n' em prosa, com a entidade no proprio chunk); nao e cobertura semantica."""
import inspect
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_fase4a import chunk  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402
from citizentech.assistente import geracao as G  # noqa: E402
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto  # noqa: E402

OFF, ON = ConfigGeracao(), ConfigGeracao(priorizar_atributo=True)
NEUTRO = " ".join(f"item{i} texto administrativo de preenchimento sem relação com o assunto." for i in range(60))
QV = "Qual é o valor autorizado para pagamento ao Hospital Lago Sul?"
QC = "Quais as competências da Coordenação de Regulação da Região Sul em 2025?"
CAND_V = "Processo: 1/2025. Interessado: HOSPITAL LAGO SUL S/A. Valor: R$ 10,00 (dez reais), relativo ao Termo 7/2020."


def ctx(pergunta, selecionados, candidato):
    ch = [chunk(k + 1, t + " " + NEUTRO, 100 + k, ordem=0, n=1) for k, t in enumerate(selecionados)]
    ch.append(chunk(len(ch) + 1, candidato + " " + NEUTRO, 200, ordem=0, n=1))
    assert ch[-1].chunk_id not in {i.chunk_id for i in montar_contexto(pergunta, ch, OFF).itens}       # sem a flag o candidato e descartado pelo orcamento
    c = montar_contexto(pergunta, ch, ON)
    return c, ch


def promovido(c, ch):
    return ch[-1].chunk_id in {i.chunk_id for i in c.itens}


def motivo(c, ch):
    return [x["motivo"] for x in c.selecao if x["chunk_id"] == ch[-1].chunk_id][0]


def test_1_sem_evidencia_do_atributo_e_candidato_com_rotulo_explicito_promove():
    c, ch = ctx(QV, ["Aviso geral da Secretaria sobre o Hospital Lago Sul.", "Outro aviso.", "Mais um aviso."], CAND_V)
    assert promovido(c, ch) and any(x["decisao"] == "priorizado" for x in c.selecao) and c.tokens_estimados <= 3000


def test_2_evidencia_equivalente_sem_rotulo_em_prosa_nao_promove():
    prosa = "Interessado: HOSPITAL LAGO SUL S/A. RECONHEÇO A DÍVIDA, no valor de R$ 78.213,91 (setenta e oito mil reais)."
    c, ch = ctx(QV, [prosa, "Outro aviso.", "Mais um aviso."], CAND_V)
    assert not promovido(c, ch) and "promocao redundante evitada" in motivo(c, ch) and "valor_tipado" in motivo(c, ch)


def test_3_rotulo_presente_mas_entidade_incorreta_nao_conta_como_cobertura():
    outra = "Interessado: HOSPITAL SANTA MARTA LTDA. Valor: R$ 99,00 (noventa e nove reais)."
    c, ch = ctx(QV, [outra, "Outro aviso.", "Mais um aviso."], CAND_V)
    assert promovido(c, ch)


def test_4_atributo_incidental_nao_conta_como_cobertura():
    inc = "Coordenação de Regulação da Região Sul, 2025. O relator disse que a competência do plenário é discutível e que compete a outro órgão decidir."
    cand = "Coordenação de Regulação da Região Sul, 2025. IV - Compete à CRSSU discutir e deliberar sobre os serviços regulados."
    c, ch = ctx(QC, [inc, "Outro aviso.", "Mais um aviso."], cand)
    assert promovido(c, ch)


def test_5_duas_evidencias_equivalentes_ja_no_contexto_nao_promove():
    a = "Interessado: HOSPITAL LAGO SUL S/A. Valor: R$ 1,00 (um real)."
    b = "Interessado: HOSPITAL LAGO SUL S/A. Valor: R$ 2,00 (dois reais)."
    c, ch = ctx(QV, [a, b, "Mais um aviso."], CAND_V)
    assert not promovido(c, ch)


def test_6_evidencia_conflitante_a_selecao_nao_resolve_conflito():
    a = "Interessado: HOSPITAL LAGO SUL S/A. Valor: R$ 1,00 (um real)."
    b = "Interessado: HOSPITAL LAGO SUL S/A. Valor: R$ 500,00 (quinhentos reais)."
    c, ch = ctx(QV, [a, b, "Mais um aviso."], CAND_V)
    assert not promovido(c, ch)                                                 # ha cobertura; o conflito de valores fica para a verificacao (nao para a selecao)


def test_cobertura_estrutural_unitaria():
    assert EV.cobertura_do_chunk("Valor: R$ 5,00", "valor", "VALOR", ["lago", "sul"]) is None
    assert EV.cobertura_do_chunk("Hospital Lago Sul. Valor: R$ 5,00", "valor", "VALOR", ["lago", "sul"])["tipo"] == "rotulo"
    assert EV.cobertura_do_chunk("Hospital Lago Sul, rua X.", "endereco", "ENDERECO", ["lago", "sul"]) is None
    assert EV.cobertura_do_chunk("Hospital Lago Sul R$ 5,00", "competencias", "COMPETENCIA", ["lago", "sul"]) is None
    assert EV.cobertura_do_chunk("Hospital Lago Sul R$ 5,00", "valor", "VALOR", []) is None
    assert EV.cobertura_do_chunk("Hospital Lago Sul no valor de R$ 5,00", "valor", "VALOR", ["lago", "sul"])["tipo"] == "valor_tipado"


def test_flag_desligada_por_padrao_comportamento_anterior_e_nao_usa_gabarito():
    assert ConfigGeracao().priorizar_atributo is False
    ch = [chunk(1, "Hospital Lago Sul. Valor: R$ 1,00. " + NEUTRO, 1), chunk(2, CAND_V + " " + NEUTRO, 2)]
    assert montar_contexto(QV, ch, OFF).selecao == []
    assert list(inspect.signature(EV.cobertura_do_chunk).parameters) == ["texto", "cab", "fam", "nomes"]               # so recebe texto/atributo/nomes da pergunta
    fonte = (inspect.getsource(EV.cobertura_do_chunk) + inspect.getsource(G.montar_contexto)).lower()
    assert "esperad" not in fonte and "gabarito" not in fonte


# ------------------------------------------------------------ regressoes especificas sobre os 150 (sem modelo)
RAIZ = Path(__file__).resolve().parents[3]
IDX = RAIZ / "data_assistente" / "indices" / "est300o30"


@pytest.fixture(scope="module")
def ctxs150():
    from citizentech.assistente import avaliacao_e2e as AE
    from citizentech.assistente.retriever import Indice
    corpus, val, *_ = AE.preparar()
    idx = Indice.carregar(IDX)
    out = {}
    for q in val:
        res = idx.buscar(q["pergunta"], k=OFF.max_chunks, modo="bm25")
        out[q["qid"]] = (montar_contexto(q["pergunta"], res, OFF), montar_contexto(q["pergunta"], res, ON))
    return out


def ids(c):
    return [i.chunk_id for i in c.itens]


@pytest.mark.skipif(not IDX.exists(), reason="indice indisponivel")
@pytest.mark.parametrize("qid", ["val-011", "val-080", "val-125", "val-133"])
def test_regressao_promocao_redundante_evitada(ctxs150, qid):
    c0, c1 = ctxs150[qid]
    assert ids(c0) == ids(c1) and any("promocao redundante evitada" in x["motivo"] for x in c1.selecao)


@pytest.mark.skipif(not IDX.exists(), reason="indice indisponivel")
def test_regressao_val_074_promove_o_objeto_e_val_087_a_frase_de_competencia(ctxs150):
    c0, c1 = ctxs150["val-074"]
    assert "dodf-28:est300o30:0000" in ids(c1) and "dodf-28:est300o30:0000" not in ids(c0) and c1.tokens_estimados <= 3000
    c0, c1 = ctxs150["val-087"]
    assert "dodf-174:est300o30:0003" in ids(c1) and "dodf-174:est300o30:0002" in ids(c1) and c1.tokens_estimados <= 3000


@pytest.mark.skipif(not IDX.exists(), reason="indice indisponivel")
def test_regressao_150_so_074_e_087_mudam_e_orcamento(ctxs150):
    mud = {k for k, (c0, c1) in ctxs150.items() if ids(c0) != ids(c1)}
    assert mud == {"val-074", "val-087"} and len(ctxs150) - len(mud) == 148
    assert max(c1.tokens_estimados for c0, c1 in ctxs150.values()) <= 3000 and all(c0.selecao == [] for c0, c1 in ctxs150.values())
    for k in mud:                                                               # ordem relativa dos chunks que permanecem
        c0, c1 = ctxs150[k]
        assert [x for x in ids(c1) if x in ids(c0)] == [x for x in ids(c0) if x in ids(c1)]
