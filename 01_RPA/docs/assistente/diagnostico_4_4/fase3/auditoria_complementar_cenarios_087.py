"""Auditoria complementar - cenarios A/B de val-087 sobre o codigo ATUAL (somente leitura; entrada sintetica; sem LLM; nada e gravado fora de fase3/)."""
import json, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA\citizentech\assistente\tests")
from test_protecao_44 import chunk, rodar, saida
Q = "Quais as competências da Coordenação de Regulação da Região Sul em 2025?"
COMP = "IV - Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados na Região de Saúde Sul."
MEMB = "Art. 2º Designar membros da Coordenação de Regulação da Região Sul (CRSSU): 1 - Titular: Gerente de Regulação; Suplente: substituto; 4 - Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: substituto."
OUTRA = "Comitê de Ética da Região Norte, 2025: 1 - Titular: Maria da Silva, representante da Região Norte."
def o(resp, spans, fontes=("C1",)):
    return saida(resposta=resp, fontes=list(fontes), cand=[{"fonte": f, "resposta_possivel": s} for f, s in spans], evid=[{"fonte": f, "trecho": s} for f, s in spans])
out = {}
def run(nome, chunks, obj):
    r = rodar(Q, chunks, obj)
    rel = [(x["valor"][:40], (x["rotulo"] or {}).get("rotulo"), x["estado"], x["chunk_id"][-4:]) for x in (r.verificacao.get("evidencia") or {}).get("protecao", {}).get("relacoes", [])]
    out[nome] = {"status": r.status, "problemas": r.verificacao.get("problemas"), "relacoes": rel}
    print(nome, "->", r.status, r.verificacao.get("problemas"), rel)
c1 = chunk(1, "Art. 4º Competência e Disposições Gerais da CRSSU em 2025. " + COMP + " " + MEMB, 174, n=1)
# A1: o rotulo 'titular' existe na publicacao (outra lista), mas a resposta so usa o trecho de competencia
run("A1_titular_na_publicacao_resposta_usa_so_a_competencia", [c1], o("Compete à CRSSU discutir e deliberar sobre a direção dos serviços regulados.", [("C1", "Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados")]))
# A2: a resposta cita tambem um trecho 'Titular:' de OUTRA entidade (comite diferente), sem usa-lo em nenhum termo da resposta
c2 = chunk(2, OUTRA, 175, n=1)
run("A2_trecho_titular_de_outra_entidade_citado_mas_nao_usado", [c1, c2], o("Compete à CRSSU discutir e deliberar sobre a direção dos serviços regulados.", [("C1", "Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados"), ("C2", "Titular: Maria da Silva, representante da Região Norte")], fontes=("C1", "C2")))
# B1 (val-087 real): a afirmacao 'no HRG' so existe no trecho de membros da propria entidade
run("B1_resposta_usa_a_lista_de_membros_da_propria_entidade_como_competencia", [c1], o("A Coordenação tem competência no Hospital Regional do Gama (HRG).", [("C1", "Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: substituto")]))
# B2: unico trecho da entidade e de membros
c3 = chunk(1, "Art. 2º Designar membros da Coordenação de Regulação da Região Sul (CRSSU) em 2025: 1 - Titular: Gerente de Regulação; 4 - Titular: Diretor do Hospital Regional do Gama (HRG).", 174, n=1)
run("B2_so_ha_lista_de_membros_para_a_entidade", [c3], o("A Coordenação é composta pelo Diretor do Hospital Regional do Gama (HRG).", [("C1", "Titular: Diretor do Hospital Regional do Gama (HRG)")]))
# C: rotulo no inicio do trecho mas com a competencia na mesma frase
run("C_prefixo_titular_com_competencia_na_mesma_frase", [chunk(1, "Em 2025, Titular: o Diretor do HRG, a quem compete deliberar sobre os serviços do Gama junto à Coordenação de Regulação da Região Sul.", 174, n=1)],
    o("Compete ao Diretor deliberar sobre os serviços do Gama.", [("C1", "Titular: o Diretor do HRG, a quem compete deliberar sobre os serviços do Gama")]))
json.dump(out, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase3\auditoria_complementar_cenarios_087.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
