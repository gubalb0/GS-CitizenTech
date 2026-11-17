"""Etapa 4.4 / Fase 1: grupos A/B pela evidencia REAL do contexto enviado (nao pela posicao no ranking)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from citizentech.assistente import grupos as GR  # noqa: E402
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto  # noqa: E402
from citizentech.assistente.retriever import Resultado  # noqa: E402

CURTO = "Contrato com a empresa Alfa para manutencao de equipamentos no hospital regional."
LONGO = " ".join(f"palavra{k}" for k in range(300))
PERGUNTA = "pergunta curta sobre manutencao"
CFG = ConfigGeracao(orcamento_tokens=1500)      # orcamento apertado: o chunk LONGO (posicao 2) nao cabe e e pulado


def res(i, texto, doc=None, equiv=None):
    m = {"edicao": 10 + i, "data_edicao": f"2025-01-{10 + i:02d}", "secao": "Seção III", "referencia": f"{i}/2025", "tipo_documento": "Extrato",
         "numero_documento": f"EXTRATO {i}", "ordem": 0, "n_chunks_doc": 1}
    d = doc or i
    return Resultado(i, f"dodf-{d}:est300o30:0000", d, 10.0 - i, texto, equiv or [d], {"bm25": i}, m)


@pytest.fixture
def ranking():
    # posicoes 1..4; a posicao 2 estoura o orcamento e e pulada; o contexto real = posicoes 1, 3, 4 (NAO e um prefixo)
    return [res(1, CURTO), res(2, LONGO), res(3, CURTO), res(4, CURTO)]


def test_o_contexto_real_nao_e_prefixo_do_ranking(ranking):
    itens = GR.itens_enviados(PERGUNTA, ranking, CFG)
    assert [i.doc_id for i in itens] == [1, 3, 4]
    assert [i.doc_id for i in itens] != [r.doc_id for r in ranking[:len(itens)]]      # o metodo antigo (res[:n]) daria [1, 2, 3]


def test_grupo_usa_o_chunk_realmente_enviado_e_nao_o_prefixo(ranking):
    itens = GR.itens_enviados(PERGUNTA, ranking, CFG)
    assert GR.grupo_ab([{4}], itens) == ("A", 1)       # doc 4 foi enviado, embora a posicao 4 esteja alem do "n enviados" = 3
    assert GR.grupo_ab([{2}], itens) == ("B", 0)       # doc 2 esta no 2o lugar do ranking mas foi descartado: o metodo antigo diria A


def test_metodo_antigo_erra_nos_dois_sentidos(ranking):
    itens = GR.itens_enviados(PERGUNTA, ranking, CFG)
    n = len(itens)
    antigo = {r.doc_id for r in ranking[:n]}
    assert 2 in antigo and 4 not in antigo                                   # falso A para o doc 2 e falso B para o doc 4
    assert GR.grupo_ab([{2}], itens)[0] == "B" and GR.grupo_ab([{4}], itens)[0] == "A"


def test_flag_enviado_por_chunk_id(ranking):
    itens = GR.itens_enviados(PERGUNTA, ranking, CFG)
    assert GR.marcar_enviados(ranking, itens) == [True, False, True, True]


def test_duplicatas_equivalentes_contam_como_enviadas():
    r = [res(1, CURTO, doc=1, equiv=[1, 777])]
    itens = GR.itens_enviados(PERGUNTA, r, CFG)
    assert GR.grupo_ab([{777}], itens) == ("A", 1)


def test_n_enviadas_conta_publicacoes_esperadas_distintas():
    r = [res(1, CURTO), res(3, CURTO)]
    itens = GR.itens_enviados(PERGUNTA, r, CFG)
    assert GR.grupo_ab([{1}, {3}, {99}], itens) == ("A", 2)
    assert GR.grupo_ab([{99}], itens) == ("B", 0)


def test_divergencia_com_a_telemetria_falha_em_vez_de_adivinhar(ranking):
    with pytest.raises(ValueError):
        GR.itens_enviados(PERGUNTA, ranking, CFG, n_esperado=2)
    assert len(GR.itens_enviados(PERGUNTA, ranking, CFG, n_esperado=3)) == 3


def test_avaliacao_e2e_nao_usa_mais_o_prefixo_do_ranking():
    src = (Path(__file__).resolve().parents[1] / "avaliacao_e2e.py").read_text(encoding="utf-8")
    assert "res[:n_env]" not in src and "x.posicao <= n_env" not in src
    assert "GR.grupo_ab" in src and "GR.marcar_enviados" in src


RODADA = Path(__file__).resolve().parents[3] / "data_assistente" / "derivados" / "geracao_e2e_41_20261114-130608.jsonl"
IDX = Path(__file__).resolve().parents[3] / "data_assistente" / "indices" / "est300o30"


@pytest.mark.skipif(not (RODADA.exists() and IDX.exists()), reason="rodada/indice 4.3 indisponiveis")
def test_val_097_da_rodada_43_e_grupo_A_pelo_contexto_real():
    """Regressao com dados reais (somente leitura; sem LLM): o chunk do doc 105 foi enviado, embora a rodada o marcasse como nao enviado."""
    from citizentech.assistente import avaliacao_e2e as AE
    from citizentech.assistente.retriever import Indice
    corpus, val, assoc, dup, esperados, docs = AE.preparar()
    o = next(json.loads(l) for l in RODADA.open(encoding="utf-8") if '"qid": "val-097"' in l)
    assert o["grupo"] == "B"                                   # resultado ORIGINAL preservado (nao e alterado)
    i = next(k for k, q in enumerate(val) if q["qid"] == "val-097")
    idx = Indice.carregar(IDX)
    cfg = ConfigGeracao()
    resultados = idx.buscar(val[i]["pergunta"], k=cfg.max_chunks, modo="bm25")
    itens = GR.itens_enviados(val[i]["pergunta"], resultados, cfg, n_esperado=o["saida"]["telemetria"]["chunks_enviados"])
    assert GR.grupo_ab(esperados[i], itens)[0] == "A"
    assert any(f["chunk_id"] == "dodf-105:est300o30:0000" and not f["enviado"] for f in o["fontes_recuperadas"])
    assert GR.marcar_enviados(resultados, itens)[3] is True    # posicao 4 (doc 105) enviada
