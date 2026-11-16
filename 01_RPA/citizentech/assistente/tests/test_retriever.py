import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from citizentech.assistente.bm25 import BM25, top_k_deterministico  # noqa: E402
from citizentech.assistente.chunking import ConfigChunk  # noqa: E402
from citizentech.assistente.codificador import CodificadorFalso  # noqa: E402
from citizentech.assistente.dedup import agrupar_duplicatas, documentos_canonicos  # noqa: E402
from citizentech.assistente.metricas import (cobertura_total_at_k, hit_at_k, ranking_de_documentos, recall_at_k,  # noqa: E402
                                             reciprocal_rank, posicao_primeiro_relevante)
from citizentech.assistente.retriever import Indice  # noqa: E402
from citizentech.assistente.texto_busca import normalizar_busca  # noqa: E402


def d(i, texto, ed=1, ref="r", sec="Seção III", **kw):
    base = {"id": i, "edicao": ed, "data_edicao": "2025-01-0%d" % (ed % 9 + 1), "referencia": ref, "secao": sec,
            "tipo_documento": "Extrato", "numero_documento": f"EXTRATO {i}", "texto_completo": texto, "data": "2025-01-01",
            "topicos": [], "localidades": ["gama"], "tipo_unidade": ["hospital"], "programas": []}
    base.update(kw)
    return base


LONGO = " ".join(f"Art. {i}º O hospital regional de Planaltina adquiriu seringas descartáveis e luvas cirúrgicas lote {i}." for i in range(1, 30))
CORPUS = [
    d(1, "A UBS Vila Esperança vacina idosos contra gripe até 30 de junho."),
    d(2, "Reconhecimento de dívida: pagamento de R$ 69.281,56 ao Hospital das Clínicas e Pronto Socorro de Fraturas.", ed=2, ref="165/2021"),
    d(3, "Reconhecimento de dívida: pagamento de R$ 69.281,56 ao Hospital das Clínicas e Pronto Socorro de Fraturas.", ed=2, ref="165/2021"),  # dup de 2
    d(4, "Aquisição de ataduras de crepom para o Hospital Regional de Samambaia.", ed=3),
    d(5, LONGO, ed=4, ref="gigante"),
    d(6, "Credenciamento de clínica oftalmológica para cirurgia de catarata.", ed=5),
]
CFG = ConfigChunk("estrutura", 60, 0)
COD = CodificadorFalso()


@pytest.fixture(scope="module")
def idx():
    return Indice.construir(CORPUS, CFG, COD)


# -------------------------------------------------------------------- normalizacao e BM25
def test_normalizar_busca():
    assert normalizar_busca("Atenção Primária à Saúde, R$ 69.281,56!") == ["atencao", "primaria", "a", "saude", "r", "69", "281", "56"]
    assert normalizar_busca(None) == [] and normalizar_busca("") == []
    assert normalizar_busca("seringas luvas", radical_leve=True) == ["seringa", "luva"]


def test_bm25_ordem_e_zero_resultados():
    bm = BM25().ajustar(["gato preto", "cachorro branco", "gato e cachorro juntos"])
    idx_, sc = bm.buscar("gato", 5)
    assert list(idx_) == [0, 2] and sc[0] >= sc[1] > 0
    assert len(bm.buscar("elefante", 5)[0]) == 0           # termo fora do vocabulario
    assert len(bm.buscar("", 5)[0]) == 0


def test_bm25_parametros_invalidos_e_nao_ajustado():
    with pytest.raises(ValueError):
        BM25(k1=0)
    with pytest.raises(ValueError):
        BM25(b=1.5)
    with pytest.raises(RuntimeError):
        BM25().pontuar("x")


def test_top_k_desempate_pelo_menor_indice():
    s = np.array([1.0, 3.0, 3.0, 2.0, 3.0])
    assert list(top_k_deterministico(s, 2)) == [1, 2]
    assert list(top_k_deterministico(s, 10)) == [1, 2, 4, 3, 0]
    assert len(top_k_deterministico(np.array([]), 3)) == 0


# -------------------------------------------------------------------- deduplicacao
def test_deduplicacao_preserva_ids():
    dup = agrupar_duplicatas(CORPUS)
    assert dup.canonico_de[3] == 2 and dup.grupos[2] == [2, 3]
    assert dup.n_documentos_redundantes == 1 and dup.n_grupos_com_duplicata == 1
    canon = documentos_canonicos(CORPUS, dup)
    assert [x["id"] for x in canon] == [1, 2, 4, 5, 6]
    assert next(x for x in canon if x["id"] == 2)["ids_equivalentes"] == [2, 3]


def test_mesmo_texto_chave_diferente_nao_e_duplicata():
    a, b = d(10, "texto igual", ed=7), d(11, "texto igual", ed=8)
    assert agrupar_duplicatas([a, b]).n_documentos_redundantes == 0


def test_indice_nao_repete_documento_duplicado_no_top_k(idx):
    r = idx.buscar("reconhecimento de dívida Hospital das Clínicas", k=5, modo="bm25")
    assert [x.doc_id for x in r].count(2) == 1 and 3 not in [x.doc_id for x in r]
    assert r[0].ids_equivalentes == [2, 3]


def test_sem_dedup_permite_duplicata():
    i2 = Indice.construir(CORPUS, CFG, COD, dedup=False)
    ids = [x.doc_id for x in i2.buscar("reconhecimento de dívida Hospital das Clínicas", k=5, modo="bm25")]
    assert 2 in ids and 3 in ids


# -------------------------------------------------------------------- buscas
def test_busca_lexical(idx):
    r = idx.buscar("ataduras de crepom", k=3, modo="bm25")
    assert r[0].doc_id == 4 and set(r[0].ranks) == {"bm25"} and r[0].score > 0


def test_busca_vetorial(idx):
    r = idx.buscar("cirurgia de catarata oftalmológica", k=3, modo="vetorial", codificador=COD)
    assert r[0].doc_id == 6 and set(r[0].ranks) == {"vetorial"}


def test_busca_hibrida_combina_e_rastreia_origem(idx):
    r = idx.buscar("vacina idosos gripe", k=3, modo="hibrido", codificador=COD)
    assert r[0].doc_id == 1 and set(r[0].ranks) == {"bm25", "vetorial"}
    esperado = 1 / (60 + r[0].ranks["bm25"]) + 1 / (60 + r[0].ranks["vetorial"])
    assert r[0].score == pytest.approx(esperado)


def test_rrf_ordem_exata_com_listas_conhecidas(idx, monkeypatch):
    """Listas fixas: A=[0,1,2] (lexical), B=[2,0,3] (vetorial). RRF k=60 => 0 e 2 empatam? Nao: calculamos explicitamente."""
    monkeypatch.setattr(idx.bm25, "buscar", lambda q, n: (np.array([0, 1, 2]), np.array([3.0, 2.0, 1.0])))
    monkeypatch.setattr(idx, "_rank_vetorial", lambda q, n, j: ([2, 0, 3], np.zeros(len(idx.chunks))))
    r = idx.buscar("qualquer", k=4, modo="hibrido", vetor_consulta=np.zeros(COD.dimensao, np.float32))
    esperado = {0: 1 / 61 + 1 / 62, 1: 1 / 62, 2: 1 / 63 + 1 / 61, 3: 1 / 63}
    ordem = sorted(esperado, key=lambda i: (-esperado[i], i))
    assert [x.chunk_id for x in r] == [idx.chunks[i]["chunk_id"] for i in ordem]
    assert r[0].ranks in ({"bm25": 1, "vetorial": 2}, {"bm25": 3, "vetorial": 1})
    assert 3 in {int(idx.chunks.index(next(c for c in idx.chunks if c["chunk_id"] == x.chunk_id))) for x in r}   # so vetorial entra


def test_ranking_deterministico(idx):
    a = [x.chunk_id for x in idx.buscar("hospital regional seringas", k=8, modo="hibrido", codificador=COD)]
    b = [x.chunk_id for x in idx.buscar("hospital regional seringas", k=8, modo="hibrido", codificador=COD)]
    assert a == b and len(set(a)) == len(a)


def test_consulta_sem_resultados(idx):
    assert idx.buscar("", k=5, modo="hibrido", codificador=COD) == []
    assert idx.buscar("   ", k=5, modo="bm25") == []
    assert idx.buscar("zzzzxxxx qqqq", k=5, modo="bm25") == []           # nada lexical
    h = idx.buscar("zzzzxxxx qqqq", k=3, modo="hibrido", codificador=COD)  # so o vetorial responde
    assert all(set(x.ranks) == {"vetorial"} for x in h)


def test_max_por_doc_diversifica(idx):
    sem = idx.buscar("hospital regional Planaltina seringas luvas", k=6, modo="bm25")
    com = idx.buscar("hospital regional Planaltina seringas luvas", k=6, modo="bm25", max_por_doc=1)
    assert [x.doc_id for x in sem].count(5) > 1
    assert [x.doc_id for x in com].count(5) == 1 and len({x.doc_id for x in com}) == len(com)


def test_documento_gigante_e_indexado_sem_corte(idx):
    n_giga = sum(1 for c in idx.chunks if c["doc_id"] == "dodf-5")
    assert n_giga > 5
    ultimo = max((c for c in idx.chunks if c["doc_id"] == "dodf-5"), key=lambda c: c["ordem"])
    assert "lote 29" in ultimo["texto"]                       # o final do documento esta no indice


def test_metadados_e_rastreabilidade(idx):
    r = idx.buscar("ataduras de crepom", k=1, modo="bm25")[0]
    assert r.chunk_id.startswith("dodf-4:est60o0:") and r.doc_id == 4
    for k in ("edicao", "data_edicao", "secao", "referencia", "char_inicio", "char_fim", "n_tokens", "ordem"):
        assert k in r.metadados
    c = next(c for c in idx.chunks if c["chunk_id"] == r.chunk_id)
    assert CORPUS[3]["texto_completo"][r.metadados["char_inicio"]:r.metadados["char_fim"]].strip() == c["texto"]


def test_troca_de_configuracao_sem_duplicar_logica():
    a = Indice.construir(CORPUS, ConfigChunk("estrutura", 60, 0), COD)
    b = Indice.construir(CORPUS, ConfigChunk("tamanho", 40, 4), COD)
    assert a.config.nome != b.config.nome and len(a.chunks) != len(b.chunks)
    assert a.buscar("ataduras crepom", k=1, modo="bm25")[0].doc_id == b.buscar("ataduras crepom", k=1, modo="bm25")[0].doc_id == 4


def test_multiplas_janelas_por_chunk_usa_maximo():
    cod = CodificadorFalso(janela_palavras=5)
    i2 = Indice.construir(CORPUS, ConfigChunk("estrutura", 400, 0), cod)
    assert len(i2.vetores) > len(i2.chunks) and i2.janela_inicio[-1] == len(i2.vetores)
    assert i2.buscar("cirurgia catarata", k=1, modo="vetorial", codificador=cod)[0].doc_id == 6
    assert i2.buscar("cirurgia catarata", k=1, modo="vetorial", codificador=cod, janela="primeira")  # modo truncado funciona


# -------------------------------------------------------------------- persistencia / reconstrucao
def test_salvar_carregar_reconstroi_resultados_identicos(idx, tmp_path):
    idx.salvar(tmp_path / "i")
    novo = Indice.carregar(tmp_path / "i", COD.nome)
    for q in ("vacina idosos gripe", "ataduras crepom", "seringas luvas hospital"):
        for modo in ("bm25", "vetorial", "hibrido"):
            a = idx.buscar(q, k=6, modo=modo, codificador=COD)
            b = novo.buscar(q, k=6, modo=modo, codificador=COD)
            assert [(x.chunk_id, round(x.score, 6)) for x in a] == [(x.chunk_id, round(x.score, 6)) for x in b]
    assert novo.manifesto["duplicatas_redundantes"] == 1


def test_carregar_indice_invalido(tmp_path, idx):
    with pytest.raises(FileNotFoundError):
        Indice.carregar(tmp_path / "nao_existe")
    idx.salvar(tmp_path / "i")
    with pytest.raises(ValueError):
        Indice.carregar(tmp_path / "i", "outro-modelo")
    np.save(tmp_path / "i" / "vetores.npy", np.zeros((3, 4), np.float32))
    with pytest.raises(ValueError):
        Indice.carregar(tmp_path / "i")


def test_checkpoint_de_embeddings_retoma(tmp_path):
    chamadas = []

    class Contador(CodificadorFalso):
        def codificar_janelas(self, t):
            chamadas.append(len(t))
            return super().codificar_janelas(t)

    c = Contador()
    Indice.construir(CORPUS, CFG, c, checkpoint=tmp_path)
    n1 = len(chamadas)
    Indice.construir(CORPUS, CFG, c, checkpoint=tmp_path)
    assert n1 >= 1 and len(chamadas) == n1               # segunda vez usa o checkpoint


# -------------------------------------------------------------------- erros e entradas invalidas
@pytest.mark.parametrize("kw,exc", [({"k": 0}, ValueError), ({"k": -3}, ValueError), ({"k": 2.5}, ValueError),
                                    ({"modo": "semantico"}, ValueError), ({"rrf_k": 0}, ValueError),
                                    ({"max_por_doc": 0}, ValueError), ({"janela": "x"}, ValueError)])
def test_parametros_invalidos(idx, kw, exc):
    with pytest.raises(exc):
        idx.buscar("ataduras", codificador=COD, **kw)


def test_consulta_invalida(idx):
    with pytest.raises(TypeError):
        idx.buscar(None)
    with pytest.raises(TypeError):
        idx.buscar(123)
    with pytest.raises(ValueError):
        idx.buscar("ataduras", modo="vetorial")           # sem codificador nem vetor


def test_corpus_vazio():
    with pytest.raises(ValueError):
        Indice.construir([], CFG, COD)
    with pytest.raises(ValueError):
        Indice.construir([d(1, "   ")], CFG, COD)


# -------------------------------------------------------------------- metricas (MULTI, equivalentes)
def test_metricas_multi_e_equivalentes():
    esperados = [{2, 3}, {7}, {9}]                          # MULTI: 3 publicacoes, a 1a com ids equivalentes
    ranking = [5, 3, 8, 9, 1, 7]
    assert recall_at_k(esperados, ranking, 1) == 0
    assert recall_at_k(esperados, ranking, 2) == pytest.approx(1 / 3)       # 3 equivale ao grupo {2,3}
    assert recall_at_k(esperados, ranking, 10) == 1.0
    assert hit_at_k(esperados, ranking, 2) and not hit_at_k(esperados, ranking, 1)
    assert not cobertura_total_at_k(esperados, ranking, 4) and cobertura_total_at_k(esperados, ranking, 6)
    assert reciprocal_rank(esperados, ranking) == 0.5 and posicao_primeiro_relevante(esperados, ranking) == 2
    assert reciprocal_rank([{99}], ranking) == 0.0 and posicao_primeiro_relevante([{99}], ranking) is None
    with pytest.raises(ValueError):
        recall_at_k([], ranking, 3)


def test_ranking_de_documentos_pela_primeira_aparicao():
    assert ranking_de_documentos([4, 4, 2, 4, 9, 2]) == [4, 2, 9]
