import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from citizentech.assistente.chunking import ConfigChunk, chunkear_documento, contar_tokens, doc_id  # noqa: E402


def doc(texto, i=1, **kw):
    d = {"id": i, "edicao": 10, "data_edicao": "2025-01-10", "referencia": "12/2025", "secao": "Seção III",
         "tipo_documento": "Portaria", "numero_documento": "PORTARIA Nº 12, DE 10 DE JANEIRO DE 2025", "texto_completo": texto,
         "data": "2025-01-10", "topicos": ["ubs"], "localidades": ["gama"], "tipo_unidade": ["hospital"], "programas": []}
    d.update(kw)
    return d


def artigos(n, palavras=40):
    return " ".join(f"Art. {i}º " + " ".join(f"palavra{i}x{j}" for j in range(palavras)) + "." for i in range(1, n + 1))


CFGS = [ConfigChunk("tamanho", 100, 10), ConfigChunk("estrutura", 100, 10), ConfigChunk("tamanho", 60, 0), ConfigChunk("estrutura", 60, 0)]


@pytest.mark.parametrize("cfg", CFGS)
def test_documento_curto_vira_um_chunk_com_metadados(cfg):
    d = doc("A UBS Vila Nova funciona das 8h às 16h.")
    ch = chunkear_documento(d, cfg)
    assert len(ch) == 1
    c = ch[0]
    assert c["texto"] == "A UBS Vila Nova funciona das 8h às 16h."
    assert c["doc_id"] == doc_id(d) == "dodf-1" and c["chunk_id"] == f"dodf-1:{cfg.nome}:0000"
    for k in ("edicao", "data_edicao", "secao", "referencia", "tipo_documento", "numero_documento", "topicos", "localidades"):
        assert c[k] == d[k]
    assert "PORTARIA" in c["texto_indexacao"] and c["texto_indexacao"].endswith(c["texto"])
    assert c["n_chunks_doc"] == 1 and c["char_inicio"] == 0


@pytest.mark.parametrize("cfg", CFGS)
@pytest.mark.parametrize("vazio", ["", "   \n\t ", None])
def test_documento_vazio(cfg, vazio):
    assert chunkear_documento(doc(vazio), cfg) == []


@pytest.mark.parametrize("cfg", CFGS)
def test_documento_longo_respeita_limite_e_cobre_todo_o_texto(cfg):
    t = artigos(30)
    ch = chunkear_documento(doc(t), cfg)
    assert len(ch) > 3
    assert all(c["n_tokens"] <= cfg.max_tokens for c in ch)
    cobertos = set()
    for c in ch:
        cobertos.update(range(c["char_inicio"], c["char_fim"]))
    assert all(i in cobertos for i, ch_ in enumerate(t) if not ch_.isspace())
    assert [c["ordem"] for c in ch] == list(range(len(ch)))
    assert len({c["chunk_id"] for c in ch}) == len(ch)


@pytest.mark.parametrize("cfg", CFGS)
def test_deterministico_e_ids_estaveis(cfg):
    a = chunkear_documento(doc(artigos(12)), cfg)
    b = chunkear_documento(doc(artigos(12)), cfg)
    assert [(c["chunk_id"], c["hash"]) for c in a] == [(c["chunk_id"], c["hash"]) for c in b]


def test_tamanho_overlap_exato():
    t = " ".join(f"w{i}" for i in range(300))
    ch = chunkear_documento(doc(t), ConfigChunk("tamanho", 100, 10))
    for a, b in zip(ch, ch[1:]):
        assert a["texto"].split()[-10:] == b["texto"].split()[:10]
    assert all(c["n_tokens"] <= 100 for c in ch)


def test_estrutura_comeca_em_fronteira_de_artigo_quando_cabe():
    ch = chunkear_documento(doc(artigos(30)), ConfigChunk("estrutura", 100, 0))
    assert all(re.match(r"Art\. \d+º", c["texto"]) for c in ch)
    # nenhum artigo (42 tokens) e partido entre chunks
    for c in ch:
        assert c["texto"].rstrip().endswith(".")


def test_estrutura_nao_corta_referencia_a_artigo_no_meio_da_frase():
    t = ("O SECRETÁRIO, no uso das atribuições que lhe conferem o Art. 49, § 1º, do Decreto nº 39.610, resolve: "
         + " ".join(f"item{i}" for i in range(80)) + ". Art. 2º Esta portaria entra em vigor. " + " ".join(f"fim{i}" for i in range(80)) + ".")
    for c in chunkear_documento(doc(t), ConfigChunk("estrutura", 90, 0)):
        assert not c["texto"].endswith("Art.") and not c["texto"].startswith("§")
        assert not c["texto"].startswith("1º,")


def test_estrutura_valores_monetarios_e_cnpj_nao_sao_partidos():
    t = ("Valor: R$ 169.905,44 (cento e sessenta e nove mil), CNPJ 01.273.401/0001-88. " * 20)
    ch = chunkear_documento(doc(t), ConfigChunk("estrutura", 40, 0))
    assert len(ch) > 2
    for c in ch:
        assert not re.search(r"R\$\s*$", c["texto"]) and not re.search(r"\d\.$", c["texto"].replace("0001-88.", "X"))
        assert c["texto"].count("R$") == len(re.findall(r"R\$ 169\.905,44", c["texto"]))


@pytest.mark.parametrize("cfg", CFGS)
def test_texto_irregular_sem_pontuacao_nao_excede_limite_nem_corta_palavra(cfg):
    t = " ".join(f"palavralonga{i}" for i in range(2000))
    ch = chunkear_documento(doc(t), cfg)
    assert all(c["n_tokens"] <= cfg.max_tokens for c in ch)
    palavras = set(t.split())
    for c in ch:
        assert all(w in palavras for w in c["texto"].split())


@pytest.mark.parametrize("cfg", CFGS)
def test_caracteres_especiais(cfg):
    t = "Aviso — “Não há vagas” às 8h; ção ñ ü 😀 R$ 1.234,56 nº 03/2025. " * 15
    ch = chunkear_documento(doc(t), cfg)
    assert ch and all(c["texto"] for c in ch)
    assert all(c["n_tokens"] <= cfg.max_tokens for c in ch)
    assert "😀" in " ".join(c["texto"] for c in ch)


def test_estrutura_com_overlap_sempre_progride():
    t = " ".join(f"Art. {i}º " + "x " * 28 + "." for i in range(1, 40))
    ch = chunkear_documento(doc(t), ConfigChunk("estrutura", 80, 39))
    assert len(ch) < 200  # sem laco infinito/explosao
    assert ch[-1]["char_fim"] >= len(t.rstrip()) - 1


def test_estrutura_overlap_repete_apenas_unidades_inteiras():
    ch = chunkear_documento(doc(artigos(20, palavras=8)), ConfigChunk("estrutura", 60, 20))
    for a, b in zip(ch, ch[1:]):
        assert b["char_inicio"] <= a["char_fim"]
        assert re.match(r"Art\. \d+º", b["texto"])


def test_estrutura_nao_separa_numerador_de_item_do_titulo():
    t = " ".join(f"1.6.2.{i}. UNIDADE NUMERO {i} " + "palavra " * 25 + "(Un)." for i in range(1, 40))
    ch = chunkear_documento(doc(t), ConfigChunk("estrutura", 80, 0))
    assert len(ch) > 3
    for c in ch:
        assert not re.search(r"\d+(?:\.\d+)+\.$", c["texto"]), c["texto"][-60:]


def test_config_invalida():
    with pytest.raises(ValueError):
        ConfigChunk("semantico", 100)
    with pytest.raises(ValueError):
        ConfigChunk("tamanho", 100, 60)
    with pytest.raises(ValueError):
        ConfigChunk("tamanho", 5)


def test_contar_tokens():
    assert contar_tokens("") == 0 and contar_tokens("R$ 1,5") == 5
