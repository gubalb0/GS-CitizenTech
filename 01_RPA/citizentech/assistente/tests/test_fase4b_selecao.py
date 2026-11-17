"""Etapa 4.4 / Fase 4B (PREPARACAO, nao validada) - S1 forte: priorizacao de chunk com rotulo EXPLICITO do atributo pedido. Isolado, reversivel (flag desligada por padrao)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_fase4a import Q87, chunk  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto  # noqa: E402

LIGADO = ConfigGeracao(priorizar_atributo=True)
DESLIGADO = ConfigGeracao()
FILL = " ".join(f"palavra{i} texto de preenchimento sobre a Coordenação de Regulação da Região Sul em 2025." for i in range(55))      # ~ chunk grande


def ids(ctx):
    return [i.chunk_id for i in ctx.itens]


def cenario(texto_alvo, n_fill=3):
    """n_fill chunks grandes (sem rotulo) + 1 chunk-alvo; o alvo so e descartado pelo orcamento."""
    ch = [chunk(k + 1, f"Coordenação de Regulação da Região Sul, 2025. {FILL}", 174, ordem=k, n=9) for k in range(n_fill)]
    ch.append(chunk(n_fill + 1, texto_alvo + " " + FILL, 174, ordem=n_fill, n=9))
    return ch


def test_flag_desligada_por_padrao_e_selecao_identica():
    assert ConfigGeracao().priorizar_atributo is False
    ch = cenario("IV - Compete à CRSSU discutir e deliberar sobre os serviços regulados da Coordenação de Regulação da Região Sul.")
    c = montar_contexto(Q87, ch, DESLIGADO)
    assert c.selecao == [] and ids(c) == ids(montar_contexto(Q87, ch, ConfigGeracao()))


def test_rotulo_forte_em_posicao_de_rotulo_e_priorizado_e_o_orcamento_e_o_mesmo():
    ch = cenario("IV - Compete à CRSSU discutir e deliberar sobre os serviços regulados.", n_fill=5)
    c0, c1 = montar_contexto(Q87, ch, DESLIGADO), montar_contexto(Q87, ch, LIGADO)
    alvo = ch[-1].chunk_id
    assert alvo not in ids(c0)                                                    # sem a flag, o alvo e descartado pelo orcamento
    assert alvo in ids(c1) and c1.tokens_estimados <= LIGADO.orcamento_tokens == 3000
    assert any(l["chunk_id"] == alvo and l["decisao"] == "priorizado" and l["rotulo_forte"] == "compete" for l in c1.selecao)
    assert [x for x in ids(c1) if x != alvo] == [x for x in ids(c0) if x in ids(c1) and x != alvo]      # ordem relativa dos demais preservada


def test_ocorrencia_incidental_nao_prioriza():
    cab, fam, n = "competencias", "COMPETENCIA", ["coordenacao", "regulacao", "sul"]
    txt = "Coordenação de Regulação da Região Sul. O Diretor afirmou que a sua competência no assunto é limitada e que compete a outro órgão decidir."
    assert EV.rotulo_forte_no_chunk(txt, cab, fam, n) is None                      # palavra no meio da frase


def test_familia_ampla_nao_prioriza():
    cab, fam, n = "competencias", "COMPETENCIA", ["coordenacao", "regulacao", "sul"]
    assert EV.rotulo_forte_no_chunk("Coordenação de Regulação da Região Sul. Atribuições: coordenar os serviços.", cab, fam, n) is None
    assert EV.rotulos_fortes(cab, fam) == {"competencia", "compete"}


def test_sem_associacao_com_a_entidade_nao_prioriza():
    cab, fam = "competencias", "COMPETENCIA"
    assert EV.rotulo_forte_no_chunk("Outra Entidade X. Art. 4º Competência: deliberar.", cab, fam, ["coordenacao", "regulacao", "sul"]) is None
    assert EV.rotulo_forte_no_chunk("Competência: deliberar.", cab, fam, []) is None            # sem nome na pergunta nao ha associacao
    # publicacao (outros chunks do mesmo documento) que trata da entidade confere a associacao
    assert EV.rotulo_forte_no_chunk("IV - Compete à CRSSU deliberar.", cab, fam, ["coordenacao", "regulacao", "sul"],
                                    "Coordenação de Regulação da Região Sul IV - Compete à CRSSU deliberar.")["rotulo"] == "compete"


def test_enumeradores_e_posicao_de_rotulo():
    cab, fam, n = "competencias", "COMPETENCIA", ["coordenacao"]
    for t in ("Coordenação. Art. 4º Competência e Disposições Gerais.", "Coordenação. III - algo. IV – Compete à X fazer.", "Coordenação.\nCompetência: fazer.", "Coordenação. § 2º Compete ao Diretor."):
        assert EV.rotulo_forte_no_chunk(t, cab, fam, n), t


def test_sem_candidato_descartado_a_selecao_nao_muda_e_registra_motivo():
    ch = [chunk(1, "Coordenação de Regulação da Região Sul, 2025. Competência: deliberar.", 174)]
    c0, c1 = montar_contexto(Q87, ch, DESLIGADO), montar_contexto(Q87, ch, LIGADO)
    assert ids(c0) == ids(c1) and c1.selecao and c1.selecao[0]["decisao"] == "mantido"


# ------------------------------------------------------------ regressao offline sobre os 150 (sem modelo)
import pytest  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]
IDX = RAIZ / "data_assistente" / "indices" / "est300o30"


@pytest.mark.skipif(not IDX.exists(), reason="indice indisponivel")
def test_selecao_150_so_os_casos_esperados_mudam_e_orcamento_respeitado():
    from citizentech.assistente import avaliacao_e2e as AE
    from citizentech.assistente.retriever import Indice
    corpus, val, *_ = AE.preparar()
    idx = Indice.carregar(IDX)
    mudou = {}
    for q in val:
        res = idx.buscar(q["pergunta"], k=DESLIGADO.max_chunks, modo="bm25")
        c0, c1 = montar_contexto(q["pergunta"], res, DESLIGADO), montar_contexto(q["pergunta"], res, LIGADO)
        assert c1.tokens_estimados <= 3000 and c0.selecao == []
        if ids(c0) != ids(c1):
            mudou[q["qid"]] = (c0, c1)
    assert set(mudou) == {"val-074", "val-087"}   # 4B-cand: S1 conservadora (a S1 pura da 4B-prep mudava tambem 011/080/125/133, promocoes redundantes: AVALIACAO_S1_CONSERVADORA.md)
    c1 = mudou["val-087"][1]
    assert "dodf-174:est300o30:0003" in ids(c1) and "dodf-174:est300o30:0002" in ids(c1)           # a frase de competencia (IV - Compete a CRSSU) entra no contexto
    assert "val-130" not in mudou and "val-097" not in mudou                                         # nao e regra generica: val-130 inalterado
