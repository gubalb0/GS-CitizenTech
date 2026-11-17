"""Testes SINTETICOS do prototipo S1 conservadora (analise offline; fora da suite do pacote). Rodar: python -m pytest docs/assistente/diagnostico_4_4/fase4/test_s1_conservadora_proto.py"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[3] / "citizentech" / "assistente" / "tests"))
sys.path.insert(0, str(AQUI.parents[3]))
from s1_conservadora_proto import cobertura_do_chunk, montar_contexto_conservador  # noqa: E402
from test_fase4a import chunk  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402
from citizentech.assistente.geracao import ConfigGeracao  # noqa: E402

OFF, ON = ConfigGeracao(), ConfigGeracao(priorizar_atributo=True)
NEUTRO = " ".join(f"item{i} texto administrativo de preenchimento sem relação com o assunto." for i in range(60))
QV = "Qual é o valor autorizado para pagamento ao Hospital Lago Sul?"
QC = "Quais as competências da Coordenação de Regulação da Região Sul em 2025?"
CAND_V = "Processo: 1/2025. Interessado: HOSPITAL LAGO SUL S/A. Valor: R$ 10,00 (dez reais), relativo ao Termo 7/2020."


def ctx(pergunta, selecionados, candidato, docs_sel=None):
    """selecionados: textos dos 3 primeiros chunks (grandes); candidato: 4o chunk (grande, so cabe se promovido)."""
    ch = [chunk(k + 1, t + " " + NEUTRO, 100 + k, ordem=0, n=1) for k, t in enumerate(selecionados)]
    ch.append(chunk(len(ch) + 1, candidato + " " + NEUTRO, 200, ordem=0, n=1))
    c, info = montar_contexto_conservador(pergunta, ch, OFF, ON)
    return c, info, ch


def promovido(c, ch):
    return ch[-1].chunk_id in {i.chunk_id for i in c.itens}


def test_1_sem_evidencia_do_atributo_e_candidato_com_rotulo_explicito_promove():
    c, info, ch = ctx(QV, ["Aviso geral da Secretaria sobre o Hospital Lago Sul.", "Outro aviso.", "Mais um aviso."], CAND_V)
    assert info["s1_atual_mudaria"] and info["decisao"] == "promovido" and promovido(c, ch)


def test_2_evidencia_equivalente_sem_rotulo_em_prosa_nao_promove():
    prosa = "Interessado: HOSPITAL LAGO SUL S/A. RECONHEÇO A DÍVIDA, no valor de R$ 78.213,91 (setenta e oito mil reais)."
    c, info, ch = ctx(QV, [prosa, "Outro aviso.", "Mais um aviso."], CAND_V)
    assert info["decisao"] == "promocao_redundante_evitada" and not promovido(c, ch)
    assert info["cobertura_selecionados"][ch[0].chunk_id]["tipo"] == "valor_tipado"       # cobertura reconhecida sem o rotulo 'Valor:'


def test_3_rotulo_presente_mas_entidade_incorreta_nao_conta_como_cobertura():
    outra = "Interessado: HOSPITAL SANTA MARTA LTDA. Valor: R$ 99,00 (noventa e nove reais)."
    c, info, ch = ctx(QV, [outra, "Outro aviso.", "Mais um aviso."], CAND_V)
    assert info["cobertura_selecionados"][ch[0].chunk_id] is None and info["decisao"] == "promovido" and promovido(c, ch)


def test_4_atributo_incidental_nao_conta_como_cobertura():
    inc = "Coordenação de Regulação da Região Sul, 2025. O relator disse que a competência do plenário é discutível e que compete a outro órgão decidir."
    cand = "Coordenação de Regulação da Região Sul, 2025. IV - Compete à CRSSU discutir e deliberar sobre os serviços regulados."
    c, info, ch = ctx(QC, [inc, "Outro aviso.", "Mais um aviso."], cand)
    assert info["cobertura_selecionados"][ch[0].chunk_id] is None and info["decisao"] == "promovido" and promovido(c, ch)


def test_5_duas_evidencias_equivalentes_ja_no_contexto_nao_promove():
    a = "Interessado: HOSPITAL LAGO SUL S/A. Valor: R$ 1,00 (um real)."
    b = "Interessado: HOSPITAL LAGO SUL S/A. Valor: R$ 2,00 (dois reais)."
    c, info, ch = ctx(QV, [a, b, "Mais um aviso."], CAND_V)
    assert info["decisao"] == "promocao_redundante_evitada" and not promovido(c, ch)


def test_6_evidencia_conflitante_no_contexto_a_regra_nao_resolve_conflito():
    # dois valores diferentes da mesma entidade: ha cobertura (nao promove), mas o CONFLITO nao e resolvido pela selecao - limitacao documentada
    a = "Interessado: HOSPITAL LAGO SUL S/A. Valor: R$ 1,00 (um real)."
    b = "Interessado: HOSPITAL LAGO SUL S/A. Valor: R$ 500,00 (quinhentos reais)."
    c, info, ch = ctx(QV, [a, b, "Mais um aviso."], CAND_V)
    assert not promovido(c, ch) and info["decisao"] == "promocao_redundante_evitada"


def test_rotulo_nao_e_cobertura_semantica_sem_nome_da_entidade_no_chunk():
    assert cobertura_do_chunk("Valor: R$ 5,00", "valor", "VALOR", ["lago", "sul"]) is None             # rotulo sem entidade
    assert cobertura_do_chunk("Hospital Lago Sul. Valor: R$ 5,00", "valor", "VALOR", ["lago", "sul"])["tipo"] == "rotulo"
    assert cobertura_do_chunk("Hospital Lago Sul, rua X.", "endereco", "ENDERECO", ["lago", "sul"]) is None     # familia sem forma tipada: so o rotulo conta
    assert cobertura_do_chunk("Hospital Lago Sul R$ 5,00", "competencias", "COMPETENCIA", ["lago", "sul"]) is None  # valor tipado so vale para a familia VALOR


def test_flag_desligada_nao_e_alterada_pelo_prototipo():
    assert ConfigGeracao().priorizar_atributo is False
