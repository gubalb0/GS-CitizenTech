"""Fase 4D.3 - construcao do conjunto diagnostico SINTETICO (30 casos) com rotulagem de referencia.
Este script NAO importa o pipeline: a rotulagem e escrita aqui, antes de qualquer execucao. Saida: CASOS_DIAGNOSTICOS_4D3.json (e ROTULAGEM_4D3.md)."""
import datetime
import hashlib
import json
import pathlib
from collections import Counter

AQUI = pathlib.Path(__file__).parent

# ---------- mundo R (regulacao; mesmo vocabulario da Fase 4D.2 para permitir comparar com val-087) ----------
Q_G = "Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?"
Q_NG = "Quais as competências da Coordenação de Regulação da Região de Saúde Sul?"
HEAD = "Ordem de Serviço nº 93/2025. Coordenação de Regulação da Região de Saúde Sul (CRSSU). "
R = {
    "comp_g": (HEAD + "IV - Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados, inclusive os do Gama.",
               "IV - Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados, inclusive os do Gama"),
    "comp_ng": (HEAD + "IV - Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados.",
                "IV - Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados"),
    "neu": (HEAD + "IX - As Deliberações deverão nortear as gerências de regulação no cumprimento das atribuições regimentais de implementar as normas e protocolos de regulação.",
            "As Deliberações deverão nortear as gerências de regulação no cumprimento das atribuições regimentais de implementar as normas e protocolos de regulação"),
    "mem_g": (HEAD + "Art. 2º Designar membros: 4 - Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: substituto.",
              "4 - Titular: Diretor do Hospital Regional do Gama (HRG)"),
    "mem_ng": (HEAD + "Art. 2º Designar membros: 5 - Titular: Superintendente do Hospital Regional de Santa Maria (HRSM); Suplente: substituto.",
               "5 - Titular: Superintendente do Hospital Regional de Santa Maria (HRSM)"),
    "mem2": (HEAD + "Art. 2º Designar membros: 6 - Titular: Gerente de Regulação da GERSU; 7 - Titular: Ouvidor do Núcleo de Ouvidoria (NOV); Suplente: substituto.",
             "6 - Titular: Gerente de Regulação da GERSU"),
    "cue": (HEAD + "Titular: o Diretor do HRG do Gama, a quem compete deliberar sobre os serviços regulados do Gama.",
            "Titular: o Diretor do HRG do Gama, a quem compete deliberar sobre os serviços regulados do Gama"),
    "reuniao": (HEAD + "Art. 5º As reuniões ordinárias da CRSSU ocorrerão mensalmente, para discutir e deliberar sobre os serviços regulados.",
                "As reuniões ordinárias da CRSSU ocorrerão mensalmente, para discutir e deliberar sobre os serviços regulados"),
}
# ---------- mundo C (contratos) ----------
HA = "Extrato de Contrato nº 12/2025. Contratada: Alfa Serviços Ltda. "
HB = "Extrato de Contrato nº 13/2025. Contratada: Beta Engenharia Ltda. "
Q_A = "Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?"
C = {
    "oa": (HA + "Objeto: manutenção preventiva de equipamentos de imagem. Valor: R$ 80.000,00.", "Objeto: manutenção preventiva de equipamentos de imagem"),
    "ob": (HB + "Objeto: reforma da rede de gases medicinais. Valor: R$ 150.000,00.", "Objeto: reforma da rede de gases medicinais"),
    "va": (HA + "Valor: R$ 80.000,00. Vigência: 12 meses.", "Contratada: Alfa Serviços Ltda. Valor: R$ 80.000,00"),
    "vb": (HB + "Objeto: reforma da rede de gases medicinais. Valor: R$ 150.000,00.", "Contratada: Beta Engenharia Ltda. Objeto: reforma da rede de gases medicinais. Valor: R$ 150.000,00"),
    "opl": (HA + "Objeto: manutenção preventiva de equipamentos de imagem. Valor: R$ 80.000,00, para o Hospital Regional de Planaltina (HRP).",
            "Objeto: manutenção preventiva de equipamentos de imagem"),
    "vpl": (None, "Valor: R$ 80.000,00, para o Hospital Regional de Planaltina (HRP)"),
    "adit": ("Extrato de Termo Aditivo nº 5/2025. Partes: Alfa Serviços Ltda e Beta Engenharia Ltda. Objeto: prorrogação da vigência por mais 12 meses.",
             "Objeto: prorrogação da vigência por mais 12 meses"),
}


def ch(key, mundo, doc):
    return {"chave": key, "doc": doc, "ordem": 0, "n_chunks_doc": 1, "texto": mundo[key][0]}


def cit(chave, span):
    return {"chunk": chave, "span": span}


def rc(k, d, mundo=R):
    return ch(k, mundo, d)


def sp(k, mundo=R):
    return mundo[k][1]


def J(afirmacao, trecho, associada, so_pergunta, por_que):
    return {"afirmacao_avaliada": afirmacao, "trecho_que_sustenta_ou_contradiz": trecho, "entidade_associada_ao_atributo": associada, "informacao_so_da_pergunta": so_pergunta, "por_que": por_que}


CASOS = []


def caso(id, fam, desc, perg, resp, chunks, cits, ent, atr, rot, rel, classe, sem, sus, ideal, conf, j, papel=()):
    CASOS.append({"id": id, "familia": fam, "descricao": desc, "pergunta": perg, "resposta": resp, "chunks": chunks, "citacoes": cits,
                  "entidade": ent, "atributo": atr, "rotulo_do_trecho": rot, "relacao_entidade_atributo": rel,
                  "julgamento_referencia": {"classe": classe, "correcao_semantica": sem, "sustentacao_pelos_trechos": sus, "decisao_ideal_do_pipeline": ideal,
                                            "confianca": conf, "justificativa": j}, "papel_na_analise": list(papel)})


# ================= FAMILIA A - entidade herdada da pergunta
caso("A01", "A", "entidade (Gama) apenas na pergunta; nenhum trecho citado a menciona", Q_G,
     "As Deliberações devem nortear as gerências de regulação nos serviços do Gama.", [rc("neu", 101)], [cit("neu", sp("neu"))],
     "Gama", "COMPETENCIA", ["sem rótulo (inciso IX, texto corrido)"], "não associada (Gama só na pergunta)", "insuficiente_evidencia", "nao_verificavel", "nao_sustenta_a_localizacao", "bloquear", "alta",
     J("as deliberações norteiam gerências de regulação 'nos serviços do Gama'", "IX (cita normas e protocolos de regulação; não menciona Gama)", "não: nada liga o inciso IX ao Gama", "sim: 'Gama' vem só da pergunta",
       "o conteúdo vem do trecho, mas a localização 'no Gama' é eco da pergunta sem apoio; deveria ser bloqueada ou entregue sem a localização"), ["entidade_herdada_vs_sustentada"])
caso("A02", "A", "padrão val-087-A-r1: atributo do inciso IX (neutro) + entidade só num trecho de rótulo conflitante (Titular)", Q_G,
     "A Coordenação tem competência para nortear as gerências de regulação e implementar as normas e protocolos de regulação no Gama.", [rc("neu", 101), rc("mem_g", 102)],
     [cit("neu", sp("neu")), cit("mem_g", sp("mem_g"))], "Gama", "COMPETENCIA", ["IX: sem rótulo", "4 - Titular: (MEMBRO, conflita com COMPETENCIA)"],
     "atributo e entidade em trechos diferentes; o trecho da entidade é de membros, não de competência",
     "insuficiente_evidencia", "nao_verificavel", "nao_sustenta_a_localizacao", "bloquear", "media_alta",
     J("a competência de nortear/implementar normas existe 'no Gama'", "IX sustenta o conteúdo; o único trecho com 'Gama' é a designação de titular do HRG", "não: Gama aparece só como cargo do titular, não como alcance da competência", "parcialmente: 'Gama' está na pergunta e no trecho de membro",
       "o trecho que contém 'Gama' é de designação de membro e não sustenta competência; a localização é um eco da pergunta ancorado em citação de outro atributo"),
     ["B1_corrige_padrao_val087_A_r1", "citacao_literal_vs_sustentacao_semantica"])
caso("A03", "A", "entidade na pergunta e em trecho compatível (Compete)", Q_G,
     "Compete discutir e deliberar sobre os serviços regulados do Gama.", [rc("comp_g", 101)], [cit("comp_g", sp("comp_g"))], "Gama", "COMPETENCIA", ["IV - Compete (COMPETENCIA, compatível)"], "associada explicitamente no mesmo trecho",
     "correta", "correta", "sustenta", "entregar", "alta",
     J("compete discutir e deliberar sobre serviços regulados do Gama", "inciso IV: '...serviços regulados, inclusive os do Gama'", "sim", "não: o Gama também está no trecho", "paráfrase literal de trecho com rótulo compatível que cita a entidade"), ["controle_positivo"])
caso("A04", "A", "entidade na pergunta e em dois trechos com relações diferentes (competência compatível + membro conflitante)", Q_G,
     "Compete discutir e deliberar sobre os serviços regulados do Gama.", [rc("comp_g", 101), rc("mem_g", 102)], [cit("comp_g", sp("comp_g")), cit("mem_g", sp("mem_g"))], "Gama", "COMPETENCIA",
     ["IV - Compete (compatível)", "4 - Titular (MEMBRO, conflitante)"], "o trecho compatível associa; o trecho de membro é acessório", "correta", "correta", "sustenta", "entregar", "alta",
     J("compete discutir e deliberar sobre os serviços regulados do Gama", "inciso IV (compatível); o trecho de membros é citado mas não usado", "sim, pelo inciso IV", "não", "o conteúdo vem integralmente de trecho compatível; a citação conflitante é supérflua e não deve bloquear"), ["conflito_nao_necessario"])
caso("A05", "A", "resposta que só repete a pergunta, com trecho compatível citado", Q_G,
     "A Coordenação possui competências relacionadas aos serviços do Gama.", [rc("comp_g", 101)], [cit("comp_g", sp("comp_g"))], "Gama", "COMPETENCIA", ["IV - Compete (compatível)"], "associada no trecho",
     "correta_parcial", "correta", "sustenta", "entregar", "media",
     J("a Coordenação tem competências ligadas aos serviços do Gama", "inciso IV", "sim", "sim: a resposta é quase só eco da pergunta, porém o trecho a confirma", "verdadeira e sustentada, mas não informa quais competências; parcial"), ["repeticao_legitima_da_pergunta"])
caso("A06", "A", "padrão E6: atributo de trecho compatível sem Gama + trecho de membro com Gama; resposta ecoa 'no Gama'", Q_G,
     "Compete discutir e deliberar sobre os serviços regulados no Gama.", [rc("comp_ng", 101), rc("mem_g", 102)], [cit("comp_ng", sp("comp_ng")), cit("mem_g", sp("mem_g"))], "Gama", "COMPETENCIA",
     ["IV - Compete (compatível, sem Gama)", "4 - Titular (conflitante, com Gama)"], "competência regional; Gama só como cargo", "ambiguo", "nao_verificavel", "sustenta_o_conteudo_nao_a_localizacao", "indeterminado", "baixa",
     J("a competência de discutir/deliberar alcança os serviços do Gama", "inciso IV sustenta o conteúdo; 'Gama' só no trecho de membro", "parcial: depende de o Gama pertencer à Região Sul, que nenhum trecho afirma", "sim",
       "duas leituras plausíveis: (a) eco legítimo da pergunta sobre competência regional; (b) localização não sustentada. Não forçado"), ["B1_bloqueia_E6", "interpretacao_dupla"])
caso("A07", "A", "caso legítimo (mundo contratos): entidade (Planaltina) só na cláusula de Valor do mesmo extrato; resposta de Objeto repete a unidade da pergunta",
     "Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda para o Hospital Regional de Planaltina?",
     "O objeto é a manutenção preventiva de equipamentos de imagem, para o Hospital Regional de Planaltina.", [rc("opl", 101, C)], [cit("opl", sp("oa", C)), cit("opl", sp("vpl", C))],
     "Hospital Regional de Planaltina", "OBJETO", ["Objeto: (compatível)", "Valor: ... para o HRP (VALOR, conflitante)"],
     "mesmo extrato: a cláusula de Valor identifica a unidade do contrato; o Objeto é da mesma contratada", "correta", "correta", "sustenta", "entregar", "media_alta",
     J("o objeto do contrato da Alfa é a manutenção preventiva, para o HRP", "chunk único: 'Objeto: manutenção preventiva ...' e 'Valor: R$ 80.000,00, para o Hospital Regional de Planaltina'", "sim, por pertencerem ao mesmo extrato", "o nome Planaltina também está no trecho",
       "o extrato único liga contratada, objeto e unidade; citar a cláusula de Valor serve de âncora da unidade"), ["B1_bloqueia_legitimo", "perda_de_recall_regra_conservadora"])

# ================= FAMILIA B - conflito de rotulos
caso("B01", "B", "rótulo Titular citado e conteúdo exclusivo dele usado (padrão val-087-A-r2/r3)", Q_G,
     "A Coordenação tem competência para nortear as gerências e implementar as normas; o Diretor do HRG atua na regulação do Gama.", [rc("neu", 101), rc("mem_g", 102)], [cit("neu", sp("neu")), cit("mem_g", sp("mem_g"))], "Gama", "COMPETENCIA",
     ["IX: sem rótulo", "4 - Titular (MEMBRO, conflitante)"], "membro do HRG apresentado como se fosse competência", "incorreta", "incorreta", "nao_sustenta", "bloquear", "alta",
     J("o Diretor do HRG 'atua na regulação do Gama' (competência)", "trecho de membros: designa o Diretor do HRG como titular, sem dizer que regula", "não", "o Gama está na pergunta; 'HRG' não", "dado de membro tratado como competência; afirmação nova sem apoio"), ["controle_de_bloqueio_correto"])
caso("B02", "B", "rótulo Compete (compatível), pergunta sem entidade extra", Q_NG,
     "Compete discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados.", [rc("comp_ng", 101)], [cit("comp_ng", sp("comp_ng"))], "CRSSU", "COMPETENCIA", ["IV - Compete (compatível)"], "mesmo trecho",
     "correta", "correta", "sustenta", "entregar", "alta", J("competência de discutir e deliberar sobre direção/avaliação/monitoramento", "inciso IV", "sim", "não", "cópia fiel de trecho com rótulo compatível"), ["controle_positivo"])
caso("B03", "B", "trecho com rótulo desconhecido (texto corrido, art. 5º)", Q_NG,
     "Discute e delibera sobre os serviços regulados, em reuniões ordinárias mensais.", [rc("reuniao", 101)], [cit("reuniao", sp("reuniao"))], "CRSSU", "COMPETENCIA", ["sem rótulo reconhecido"], "mesmo trecho; atributo inferido do verbo, não do rótulo",
     "correta", "correta", "sustenta", "entregar", "media",
     J("a Coordenação discute e delibera sobre serviços regulados, em reuniões mensais", "art. 5º", "sim (verbos do próprio trecho)", "não", "sem rótulo não há como confirmar a família do atributo, mas o conteúdo está literalmente no trecho"), ["rotulo_desconhecido"])
caso("B04", "B", "rótulo conflitante (Titular) mas competência explícita no próprio trecho ('a quem compete')", Q_G,
     "Compete ao Diretor do HRG deliberar sobre os serviços do Gama.", [rc("cue", 101)], [cit("cue", sp("cue"))], "Gama", "COMPETENCIA", ["Titular (MEMBRO) com cue 'a quem compete'"], "associada no trecho: a competência é afirmada junto ao titular",
     "correta", "correta", "sustenta", "entregar", "media_alta",
     J("compete ao Diretor do HRG deliberar sobre os serviços regulados do Gama", "mesmo trecho: 'a quem compete deliberar sobre os serviços regulados do Gama'", "sim", "não: o Gama está no trecho", "o rótulo conflita, mas há evidência positiva explícita da competência"),
     ["conflito_de_rotulo_vs_evidencia_positiva", "perda_de_recall_regra_conservadora"])
caso("B05", "B", "trecho conflitante citado, mas o conteúdo da resposta vem de trecho compatível", Q_NG,
     "Compete discutir e deliberar sobre a direção e o monitoramento dos serviços regulados.", [rc("comp_ng", 101), rc("mem_g", 102)], [cit("comp_ng", sp("comp_ng")), cit("mem_g", sp("mem_g"))], "CRSSU", "COMPETENCIA",
     ["IV - Compete (compatível)", "4 - Titular (conflitante)"], "mesmo trecho compatível", "correta", "correta", "sustenta", "entregar", "alta",
     J("compete discutir e deliberar sobre direção e monitoramento", "inciso IV", "sim", "não", "o trecho de membros é citado sem ser usado"), ["conflito_nao_necessario"])
caso("B06", "B", "dois trechos conflitantes (GERSU e NOV) citados e usados numa resposta sobre competência", Q_NG,
     "As gerências de regulação seguem as normas; a GERSU e o NOV participam.", [rc("neu", 101), rc("mem2", 102)],
     [cit("neu", sp("neu")), cit("mem2", sp("mem2")), cit("mem2", "7 - Titular: Ouvidor do Núcleo de Ouvidoria (NOV)")], "CRSSU", "COMPETENCIA",
     ["IX: sem rótulo", "6/7 - Titular (MEMBRO, conflitante)"], "membros apresentados como competência", "incorreta", "incorreta", "nao_sustenta", "bloquear", "media_alta",
     J("a GERSU e o NOV 'participam' (como competência)", "a designação de titulares não é competência nem participação nas normas", "não", "não", "afirmação sobre membros respondendo a pergunta de competência"), ["multiplos_conflitos"])
caso("B07", "B", "dois trechos conflitantes para entidades diferentes (HRG e HRSM); resposta os mistura", Q_NG,
     "Compete ao HRG e ao HRSM deliberar sobre os serviços regulados.", [rc("mem_g", 101), rc("mem_ng", 102)], [cit("mem_g", sp("mem_g")), cit("mem_ng", sp("mem_ng"))], "CRSSU", "COMPETENCIA",
     ["Titular HRG (conflitante)", "Titular HRSM (conflitante)"], "membros tratados como detentores de competência", "incorreta", "incorreta", "nao_sustenta", "bloquear", "alta",
     J("compete ao HRG e ao HRSM deliberar", "ambos os trechos apenas designam titulares", "não", "não", "a competência não consta em nenhum trecho"), ["multiplos_conflitos", "controle_de_bloqueio_correto"])

# ================= FAMILIA C - relacao entidade-atributo
caso("C01", "C", "entidade e atributo no mesmo trecho", Q_A, "O objeto é a manutenção preventiva de equipamentos de imagem.", [rc("oa", 101, C)], [cit("oa", sp("oa", C))], "Alfa Serviços Ltda", "OBJETO", ["Objeto: (compatível)"], "mesmo trecho",
     "correta", "correta", "sustenta", "entregar", "alta", J("objeto = manutenção preventiva de equipamentos de imagem", "extrato 12/2025", "sim", "não", "cópia do campo Objeto do extrato da Alfa"), ["controle_positivo"])
caso("C02", "C", "entidade (Alfa) num trecho e atributo (Objeto) de OUTRA empresa em outro; ambos citados", Q_A, "O objeto é a reforma da rede de gases medicinais.",
     [rc("va", 101, C), rc("ob", 102, C)], [cit("va", sp("va", C)), cit("ob", sp("ob", C))], "Alfa Serviços Ltda", "OBJETO", ["Valor (da Alfa)", "Objeto: (da Beta, compatível com o atributo)"], "atributo pertence à Beta, entidade citada é a Alfa",
     "incorreta", "incorreta", "nao_sustenta", "bloquear", "alta",
     J("o objeto do contrato da Alfa é a reforma de gases", "extrato 13/2025 (Beta) traz esse objeto; extrato 12/2025 (Alfa) não", "não: atributo associado à Beta", "o nome Alfa vem da pergunta e consta num trecho citado", "combinação de entidade de um trecho com atributo de outro; resposta falsa"),
     ["entidade_x_atributo", "combinacao_de_trechos"])
caso("C03", "C", "dois contratos no contexto; resposta usa apenas o da entidade correta", Q_A, "O objeto é a manutenção preventiva de equipamentos de imagem.",
     [rc("oa", 101, C), rc("ob", 102, C)], [cit("oa", sp("oa", C)), cit("ob", sp("ob", C))], "Alfa Serviços Ltda", "OBJETO", ["Objeto (Alfa)", "Objeto (Beta)"], "atributo da Alfa associado explicitamente; trecho da Beta é distrator",
     "correta", "correta", "sustenta", "entregar", "alta", J("objeto da Alfa", "extrato 12/2025", "sim", "não", "conteúdo vem do trecho da entidade correta; o outro trecho é ruído citado"), ["distrator_citado"])
caso("C04", "C", "atributo associado a entidade diferente; só o trecho da Beta é citado", Q_A, "O objeto é a reforma da rede de gases medicinais.", [rc("ob", 101, C)], [cit("ob", sp("ob", C))], "Alfa Serviços Ltda", "OBJETO", ["Objeto (Beta)"],
     "atributo pertence à Beta; a Alfa não consta no trecho", "incorreta", "incorreta", "nao_sustenta", "bloquear", "alta",
     J("objeto da Alfa = reforma de gases", "extrato 13/2025 da Beta", "não", "não", "a entidade da pergunta não está na evidência"), ["entidade_x_atributo", "controle_de_bloqueio_correto"])
caso("C05", "C", "duas entidades, mesmo atributo", "Qual o objeto dos contratos nº 12/2025 e nº 13/2025 das empresas Alfa Serviços Ltda e Beta Engenharia Ltda?",
     "Alfa Serviços: manutenção preventiva de equipamentos de imagem; Beta Engenharia: reforma da rede de gases medicinais.", [rc("oa", 101, C), rc("ob", 102, C)], [cit("oa", sp("oa", C)), cit("ob", sp("ob", C))], "Alfa e Beta", "OBJETO",
     ["Objeto (Alfa)", "Objeto (Beta)"], "cada entidade com seu atributo", "correta", "correta", "sustenta", "entregar", "alta", J("objeto de cada contrato", "extratos 12 e 13/2025", "sim, ambas", "os nomes também estão nos trechos", "cada entidade associada ao seu objeto"), ["controle_positivo"])
caso("C06", "C", "duas entidades, atributos diferentes (objeto da Alfa, valor da Beta)", "Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda e o valor do contrato nº 13/2025 da empresa Beta Engenharia Ltda?",
     "Alfa Serviços: manutenção preventiva de equipamentos de imagem; Beta Engenharia: R$ 150.000,00.", [rc("oa", 101, C), rc("vb", 102, C)], [cit("oa", sp("oa", C)), cit("vb", sp("vb", C))], "Alfa e Beta", "OBJETO+VALOR",
     ["Objeto (Alfa)", "Objeto e Valor (Beta; o span citado contém ambos)"], "pergunta composta; cada entidade com o atributo pedido", "correta", "correta", "sustenta", "entregar", "media",
     J("objeto da Alfa e valor da Beta", "extratos 12 e 13/2025", "sim", "não", "a pergunta pede atributos distintos para entidades distintas (limitação: o mecanismo trata um atributo por pergunta)"), ["atributo_composto"])
caso("C07", "C", "relação ambígua: aditivo cita as duas empresas; pergunta é sobre 'contrato'", Q_A, "O objeto do contrato da Alfa é a prorrogação da vigência por mais 12 meses.", [rc("adit", 101, C)], [cit("adit", sp("adit", C))], "Alfa Serviços Ltda", "OBJETO",
     ["Objeto: (compatível)"], "termo aditivo, não contrato; duas partes", "ambiguo", "nao_verificavel", "sustenta_literalmente", "indeterminado", "baixa",
     J("o objeto do contrato da Alfa é a prorrogação", "termo aditivo 5/2025 (Alfa e Beta)", "ambígua: o objeto é do aditivo, não do contrato", "não", "duas leituras plausíveis (o aditivo é a resposta útil vs o objeto do contrato não foi informado)"), ["relacao_ambigua"])

# ================= FAMILIA D - afirmacoes novas e sustentacao
caso("D01", "D", "resposta que apenas repete a pergunta", Q_A, "O contrato da empresa Alfa Serviços Ltda tem um objeto descrito no extrato.", [rc("oa", 101, C)], [cit("oa", "Contratada: Alfa Serviços Ltda")], "Alfa Serviços Ltda", "OBJETO", ["sem rótulo"], "apenas a entidade citada",
     "correta_parcial", "correta", "sustenta_trivialmente", "indeterminado", "baixa", J("o contrato da Alfa tem um objeto descrito", "extrato 12/2025", "sim (trivial)", "sim: eco da pergunta", "verdadeira mas não responde; um sistema fail-closed poderia tratá-la como insuficiente"), ["repeticao_legitima_da_pergunta"])
caso("D02", "D", "acrescenta localização não sustentada (ausente da pergunta)", Q_A, "O objeto é a manutenção preventiva de equipamentos de imagem no Hospital Regional de Planaltina.", [rc("oa", 101, C)], [cit("oa", sp("oa", C))], "Alfa Serviços Ltda", "OBJETO",
     ["Objeto: (compatível)"], "entidade Alfa associada; localização nova", "incorreta", "nao_verificavel", "nao_sustenta_a_localizacao", "bloquear", "alta", J("a manutenção ocorre no HRP", "nenhum trecho cita Planaltina", "a localização não é associada", "não: Planaltina é nova", "afirmação nova não sustentada"), ["afirmacao_nova_nao_sustentada"])
caso("D03", "D", "localização na pergunta, ausente em toda a evidência", "Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda no Hospital Regional de Planaltina?",
     "O objeto é a manutenção preventiva de equipamentos de imagem no Hospital Regional de Planaltina.", [rc("oa", 101, C)], [cit("oa", sp("oa", C))], "Hospital Regional de Planaltina", "OBJETO", ["Objeto: (compatível)"], "localização não associada",
     "insuficiente_evidencia", "nao_verificavel", "nao_sustenta_a_localizacao", "bloquear", "alta", J("o objeto vale para o HRP", "extrato 12/2025 sem menção ao HRP", "não", "sim: eco da pergunta sem apoio", "eco de entidade da pergunta que a evidência não traz"), ["entidade_herdada_vs_sustentada"])
caso("D04", "D", "acrescenta entidade não sustentada", Q_A, "O objeto é a manutenção preventiva de equipamentos de imagem, contratada pela Secretaria de Obras.", [rc("oa", 101, C)], [cit("oa", sp("oa", C))], "Alfa Serviços Ltda", "OBJETO",
     ["Objeto: (compatível)"], "entidade extra sem apoio", "incorreta", "nao_verificavel", "nao_sustenta", "bloquear", "alta", J("contratante = Secretaria de Obras", "nenhum trecho cita contratante", "não", "não", "entidade inventada"), ["afirmacao_nova_nao_sustentada"])
caso("D05", "D", "fato sustentado + número inventado", Q_A, "O objeto é a manutenção preventiva de equipamentos de imagem, no valor de R$ 90.000,00.", [rc("oa", 101, C)], [cit("oa", sp("oa", C))], "Alfa Serviços Ltda", "OBJETO",
     ["Objeto: (compatível)"], "valor contradiz o trecho (R$ 80.000,00)", "incorreta", "incorreta", "contradiz", "bloquear", "alta", J("valor de R$ 90.000,00", "o extrato traz R$ 80.000,00", "não", "não", "número divergente do trecho"), ["afirmacao_nova_nao_sustentada"])
caso("D06", "D", "correta com paráfrase", Q_A, "A empresa Alfa Serviços foi contratada para realizar a manutenção preventiva dos equipamentos de imagem.", [rc("oa", 101, C)], [cit("oa", sp("oa", C))], "Alfa Serviços Ltda", "OBJETO",
     ["Objeto: (compatível)"], "mesmo trecho", "correta", "correta", "sustenta", "entregar", "alta", J("Alfa contratada para manutenção preventiva de equipamentos de imagem", "extrato 12/2025", "sim", "não", "paráfrase fiel"), ["perda_de_recall_regra_conservadora"])
caso("D07", "D", "parcialmente correta: responde só o objeto numa pergunta de objeto e valor", "Qual o objeto e o valor do contrato nº 12/2025 da empresa Alfa Serviços Ltda?", "O objeto é a manutenção preventiva de equipamentos de imagem.", [rc("oa", 101, C)], [cit("oa", sp("oa", C))],
     "Alfa Serviços Ltda", "OBJETO+VALOR", ["Objeto: (compatível)"], "mesmo trecho", "correta_parcial", "correta", "sustenta", "entregar", "alta", J("objeto do contrato", "extrato 12/2025", "sim", "não", "omite o valor, que está no trecho; parcial"), ["parcial"])
caso("D08", "D", "resposta curta", Q_A, "Manutenção preventiva de equipamentos de imagem.", [rc("oa", 101, C)], [cit("oa", sp("oa", C))], "Alfa Serviços Ltda", "OBJETO", ["Objeto: (compatível)"], "mesmo trecho",
     "correta", "correta", "sustenta", "entregar", "alta", J("objeto", "extrato 12/2025", "sim", "não", "trecho literal sem sujeito explícito"), ["resposta_curta"])
caso("D09", "D", "resposta genérica sem conteúdo", Q_A, "O contrato trata de serviços prestados pela empresa.", [rc("oa", 101, C)], [cit("oa", "Contratada: Alfa Serviços Ltda")], "Alfa Serviços Ltda", "OBJETO", ["sem rótulo"], "apenas a entidade",
     "insuficiente_evidencia", "correta", "sustenta_trivialmente", "bloquear", "media", J("o contrato trata de serviços", "extrato 12/2025", "sim", "sim: tudo é eco da pergunta", "não informa o objeto; deveria ser tratada como não respondida"), ["resposta_generica"])

assert len(CASOS) >= 24 and len({c["id"] for c in CASOS}) == len(CASOS)
out = {"versao": "casos_4d3/2", "natureza": "conjunto sintético diagnóstico, NÃO representativo do corpus real; rotulagem de referência escrita antes da execução, por quem também escreveu os casos (sem revisão independente)", "casos": CASOS}
(AQUI / "CASOS_DIAGNOSTICOS_4D3.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
L = ["# Rotulagem de referência — Fase 4D.3", "",
     "Escrita **antes** de executar qualquer função do pipeline. Autor dos casos = autor dos rótulos (sem segundo avaliador): são julgamentos de referência, não verdade independente. Casos sintéticos; não representativos do corpus real.", "",
     "Três avaliações separadas por caso: **correção semântica** (a resposta é verdadeira no mundo fictício descrito pelos trechos), **sustentação pelos trechos** (os trechos citados a sustentam) e **decisão ideal do pipeline** (entregar/bloquear/indeterminado). A aceitação *real* pelo pipeline é medida depois (RESULTADOS_BASELINE_4D3.csv).", ""]
for c in CASOS:
    j = c["julgamento_referencia"]
    z = j["justificativa"]
    L += [f"## {c['id']} — {c['descricao']}", f"- **Pergunta:** {c['pergunta']}", f"- **Resposta candidata:** {c['resposta']}",
          f"- **Entidade / atributo:** {c['entidade']} / {c['atributo']} — rótulos: {'; '.join(c['rotulo_do_trecho'])}", f"- **Relação entidade–atributo:** {c['relacao_entidade_atributo']}",
          f"- **Classe:** `{j['classe']}` | semântica: `{j['correcao_semantica']}` | sustentação: `{j['sustentacao_pelos_trechos']}` | decisão ideal: `{j['decisao_ideal_do_pipeline']}` | confiança: `{j['confianca']}`",
          f"  1. Afirmação avaliada: {z['afirmacao_avaliada']}", f"  2. Trecho: {z['trecho_que_sustenta_ou_contradiz']}", f"  3. Entidade associada ao atributo: {z['entidade_associada_ao_atributo']}",
          f"  4. Informação só da pergunta: {z['informacao_so_da_pergunta']}", f"  5. Por quê: {z['por_que']}", ""]
(AQUI / "ROTULAGEM_4D3.md").write_text("\n".join(L), encoding="utf-8")
h = {n: hashlib.sha256((AQUI / n).read_bytes()).hexdigest() for n in ("CASOS_DIAGNOSTICOS_4D3.json", "ROTULAGEM_4D3.md")}
(AQUI / "CONGELAMENTO_ROTULAGEM_4D3.json").write_text(json.dumps({"congelado_em": datetime.datetime.now().isoformat(timespec="seconds"), "sha256": h, "observacao": "gerado antes de importar/executar qualquer código do pipeline"}, indent=1), encoding="utf-8")
print(len(CASOS), Counter(c["familia"] for c in CASOS), Counter(c["julgamento_referencia"]["classe"] for c in CASOS), Counter(c["julgamento_referencia"]["decisao_ideal_do_pipeline"] for c in CASOS))
print(h)
