import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from citizentech.assistente import associacao as A  # noqa: E402


def d(i, ed, data, sec, ref, texto):
    return {"id": i, "edicao": ed, "data_edicao": data, "secao": sec, "referencia": ref, "texto_completo": texto}


CORPUS = [
    d(1, 10, "2025-01-10", "Seção III", "12/2025", "Valor: R$ 10,00 ao Hospital A."),
    d(2, 10, "2025-01-10", "Seção III", "99/2025", "Texto igual"),
    d(3, 10, "2025-01-10", "Seção III", "99/2025", "Texto igual"),          # duplicata idêntica
    d(4, 11, "2025-01-11", "Seção I", "7/2025", "Versão X do texto."),
    d(5, 11, "2025-01-11", "Seção I", "7/2025", "Versão Y do texto."),      # mesma chave, textos diferentes
    d(6, 12, "2025-01-12", "Seção III", "5/2025", "Hospital Ç  com   espaços\nquebrados"),
]


def qa(qid, pub, multi=False):
    return {"qid": qid, "fonte": "MULTI" if multi else "2025-01-10", "texto_publicacao": pub, "pergunta": "p", "resposta": "r"}


def run(pub, multi=False):
    return A.associar_pergunta(qa("q", pub, multi), A.indexar_corpus(CORPUS))


def test_dividir_blocos_multi():
    t = "Edição 10 — 2025-01-10 — Seção III — 12/2025\nAAA\n\nEdição 11 — 2025-01-11 — Seção I — 7/2025\nBBB"
    b = A.dividir_blocos(t)
    assert [x["corpo"] for x in b] == ["AAA", "BBB"] and b[1]["cabecalho"]["edicao"] == 11


def test_exata_unica():
    r = run("Edição 10 — 2025-01-10 — Seção III — 12/2025\nValor: R$ 10,00 ao Hospital A.")
    assert r["estado"] == "resolvida" and r["blocos"][0]["status"] == "exata_unica" and r["doc_ids"] == [1]


def test_exata_duplicatas_guarda_todos_os_ids():
    r = run("Edição 10 — 2025-01-10 — Seção III — 99/2025\nTexto igual")
    assert r["blocos"][0]["status"] == "exata_duplicatas" and r["doc_ids"] == [2, 3]


def test_mesma_chave_texto_decide_sem_similaridade():
    r = run("Edição 11 — 2025-01-11 — Seção I — 7/2025\nVersão Y do texto.")
    assert r["blocos"][0]["status"] == "exata_unica" and r["doc_ids"] == [5]


def test_ambigua_quando_nenhum_texto_bate_e_ha_varios_candidatos():
    r = run("Edição 11 — 2025-01-11 — Seção I — 7/2025\nVersão Z do texto.")
    assert r["blocos"][0]["status"] == "ambigua" and r["estado"] == "nao_resolvida" and r["doc_ids"] == []


def test_texto_divergente_com_um_candidato_nao_e_associado():
    r = run("Edição 10 — 2025-01-10 — Seção III — 12/2025\nValor: R$ 11,00 ao Hospital A.")
    assert r["blocos"][0]["status"] == "texto_divergente" and r["doc_ids"] == []


def test_sem_correspondencia():
    r = run("Edição 99 — 2025-01-10 — Seção III — 12/2025\nqualquer")
    assert r["blocos"][0]["status"] == "sem_correspondencia"
    r2 = run("texto sem cabecalho nenhum")
    assert r2["blocos"][0]["motivo"] == "bloco_sem_cabecalho_valido"


def test_espacos_normalizados_mas_acentos_exigem_nivel2():
    r = run("Edição 12 — 2025-01-12 — Seção III — 5/2025\nHospital Ç com espaços quebrados")
    assert r["blocos"][0]["status"] == "exata_unica"
    r2 = run("Edição 12 — 2025-01-12 — Seção III — 5/2025\nhospital c com espacos quebrados")
    assert r2["blocos"][0]["status"] == "exata_normalizada"


def test_multi_parcial():
    pub = ("Edição 10 — 2025-01-10 — Seção III — 12/2025\nValor: R$ 10,00 ao Hospital A.\n\n"
           "Edição 77 — 2025-01-10 — Seção III — 1/2025\nnao existe")
    r = run(pub, multi=True)
    assert r["multi"] and r["n_blocos"] == 2 and r["estado"] == "parcial" and r["doc_ids"] == [1]


def test_nao_univocas_sinaliza_pergunta_igual_com_documentos_diferentes():
    perguntas = [{"qid": "a", "pergunta": "Qual o valor pago ao Hospital Santa Lúcia?", "resposta": "10"},
                 {"qid": "b", "pergunta": "Qual o valor pago ao Hospital Santa Lúcia?", "resposta": "20"},
                 {"qid": "c", "pergunta": "Horário da farmácia central do posto", "resposta": "x"}]
    assoc = [{"qid": "a", "doc_ids": [1]}, {"qid": "b", "doc_ids": [2]}, {"qid": "c", "doc_ids": [3]}]
    n = A.perguntas_nao_univocas(perguntas, assoc)
    assert len(n) == 1 and (n[0]["q1"], n[0]["q2"]) == ("a", "b") and not n[0]["mesmos_docs"]
