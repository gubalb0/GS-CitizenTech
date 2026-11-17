"""Fase 4D.5 - casos sinteticos (26) e especificacao/expectativas dos 5 casos reais, ESCRITOS E CONGELADOS ANTES de executar o prototipo.
Este script nao importa o pipeline nem o prototipo. Saidas: CASOS_SINTETICOS_4D5.json, ESPECIFICACAO_REAIS_4D5.json, ROTULAGEM_4D5.md, CONGELAMENTO_ROTULAGEM_4D5.json.
Vocabulario de 'vinculo esperado': sustentado | sustentado_documental (so na publicacao/cabecalho, nao na citacao) | nao_sustentado_herdado | nao_sustentado_outra_entidade |
nao_sustentado_outro_atributo | nao_verificavel | ambiguo. 'sustentado' = relacao entidade-atributo expressa no texto da citacao (mesma frase, ou frase adjacente com vinculo textual)."""
import datetime
import hashlib
import json
import pathlib

AQUI = pathlib.Path(__file__).parent
S = []


def E(nome, formas, tipo="organizacao", parciais=()):
    return {"nome": nome, "formas": list(formas), "tipo": tipo, "parciais": list(parciais)}


HRT = E("Hospital Regional de Taguatinga", ["hospital regional de taguatinga", "hrt"])
HRS = E("Hospital Regional de Sobradinho", ["hospital regional de sobradinho", "hrs"])
ALFA = E("Alfa Serviços Ltda", ["alfa servicos ltda", "alfa servicos", "alfa"])
CEIL = E("Ceilândia", ["ceilandia"], "localidade")
GAMA = E("Gama", ["gama"], "localidade")
CRSSU = E("Coordenação de Regulação (CRSSU)", ["crssu", "coordenacao de regulacao"])
AP = E("Atenção Primária", ["atencao primaria"])


def caso(id, tema, perg, resp, pubs, cits, ent, fam, alvos, just, conf, outras=()):
    S.append({"id": id, "tema": tema, "pergunta": perg, "resposta": resp, "publicacoes": pubs, "citacoes": cits, "entidade": ent, "outras_entidades": list(outras),
              "atributo_familia": fam, "alvos": alvos, "justificativa": just, "confianca": conf})


def al(trecho_resposta, vinculo, citacao, documental, relacao):
    return {"trecho_da_resposta": trecho_resposta, "vinculo_esperado": vinculo, "sustentacao_da_citacao": citacao, "sustentacao_documental": documental, "relacao_esperada": relacao}


QOBJ = "Qual o objeto do contrato do Hospital Regional de Taguatinga (HRT)?"
caso("S01", "mesma frase, relação explícita", "Qual o objeto do contrato da empresa Alfa Serviços Ltda?", "A Alfa Serviços Ltda foi contratada para a manutenção de tomógrafos.",
     {"P1": ["Contrato nº 15/2025. A Alfa Serviços Ltda foi contratada para a manutenção de tomógrafos do hospital."]}, [{"pub": "P1", "texto": "A Alfa Serviços Ltda foi contratada para a manutenção de tomógrafos do hospital"}], ALFA, "OBJETO",
     [al("Alfa", "sustentado", "sim", "sim", "explícita")], "entidade e atributo na mesma frase, ligados por 'foi contratada para'", "alta")
caso("S02", "mesma frase, coocorrência sem relação com a entidade", "Qual o objeto do contrato da empresa Alfa Serviços Ltda?", "A Alfa Serviços Ltda contratou a manutenção de tomógrafos.",
     {"P1": ["Ata nº 3/2025. Na reunião, a Alfa Serviços Ltda observou que a manutenção de tomógrafos será contratada pela Beta Engenharia Ltda."]}, [{"pub": "P1", "texto": "Na reunião, a Alfa Serviços Ltda observou que a manutenção de tomógrafos será contratada pela Beta Engenharia Ltda"}], ALFA, "OBJETO",
     [al("Alfa", "nao_sustentado_outra_entidade", "nao", "nao", "coocorrência; o contratante é a Beta")], "a Alfa só aparece como quem observou; quem contrata é a Beta", "alta", ["beta engenharia ltda", "beta"])
caso("S03", "frases adjacentes com anáfora", "Quais exames o Hospital Regional de Taguatinga (HRT) passou a oferecer?", "O HRT passou a oferecer exames de tomografia.",
     {"P1": ["Nota nº 4/2025. O Hospital Regional de Taguatinga (HRT) recebeu o novo equipamento em março. A unidade passou a oferecer exames de tomografia."]}, [{"pub": "P1", "texto": "A unidade passou a oferecer exames de tomografia"}], HRT, "OBJETO",
     [al("HRT", "sustentado", "sim", "sim", "adjacente com anáfora ('A unidade' retoma o HRT)")], "a frase citada retoma o HRT por 'A unidade' (referente único na frase anterior)", "media_alta")
caso("S04", "frases adjacentes sem vínculo textual", "O que o contrato prevê para o Hospital Regional de Taguatinga (HRT)?", "O contrato prevê a aquisição de monitores multiparâmetros para o HRT.",
     {"P1": ["Extrato nº 9/2025. O Hospital Regional de Taguatinga (HRT) foi visitado pelo Secretário. O contrato prevê a aquisição de monitores multiparâmetros."]}, [{"pub": "P1", "texto": "O contrato prevê a aquisição de monitores multiparâmetros"}], HRT, "OBJETO",
     [al("HRT", "nao_verificavel", "nao", "nao", "só proximidade")], "a frase anterior menciona o HRT por outro motivo (visita); nada liga o contrato ao HRT", "media")
caso("S05", "anáfora ambígua", "Quais exames o Hospital Regional de Taguatinga (HRT) passou a oferecer?", "O HRT passou a oferecer exames de tomografia.",
     {"P1": ["Nota nº 5/2025. O Hospital Regional de Taguatinga (HRT) recebeu o equipamento. O Hospital Regional de Sobradinho (HRS) ampliou o atendimento. A unidade passou a oferecer exames de tomografia."]}, [{"pub": "P1", "texto": "A unidade passou a oferecer exames de tomografia"}], HRT, "OBJETO",
     [al("HRT", "ambiguo", "nao", "nao", "'A unidade' pode ser o HRT ou o HRS")], "dois referentes possíveis para 'A unidade'", "media", ["hospital regional de sobradinho", "hrs"])
caso("S06", "entidade só na pergunta (organização)", QOBJ, "O objeto é a manutenção de tomógrafos do HRT.",
     {"P1": ["Contrato nº 12/2025. Objeto: manutenção de tomógrafos. Vigência: 12 meses."]}, [{"pub": "P1", "texto": "Objeto: manutenção de tomógrafos"}], HRT, "OBJETO",
     [al("HRT", "nao_sustentado_herdado", "nao", "nao", "ausente")], "o HRT não consta em nenhum ponto da publicação", "alta")
caso("S07", "entidade em outra frase não relacionada do mesmo chunk", QOBJ, "O objeto é a manutenção de tomógrafos do HRT.",
     {"P1": ["Contrato nº 12/2025. Objeto: manutenção de tomógrafos. A empresa executará os serviços em 12 meses. O HRT realizou a reunião de abertura no dia 3 de março."]}, [{"pub": "P1", "texto": "Objeto: manutenção de tomógrafos"}], HRT, "OBJETO",
     [al("HRT", "nao_sustentado_herdado", "nao", "nao", "menção em frase sem relação com o objeto")], "o HRT só aparece numa frase sobre reunião", "media_alta")
caso("S08", "entidade em outro chunk, outro papel", QOBJ, "O objeto é a manutenção de tomógrafos do HRT.",
     {"P1": ["Contrato nº 12/2025. Objeto: manutenção de tomógrafos. Vigência: 12 meses.", "Testemunha: Diretor do HRT. Data de assinatura: 07/05/2025."]}, [{"pub": "P1", "texto": "Objeto: manutenção de tomógrafos"}], HRT, "OBJETO",
     [al("HRT", "nao_sustentado_outro_atributo", "nao", "nao", "o HRT aparece como testemunha, outro papel")], "o HRT é mencionado no outro chunk como testemunha, não como destinatário do objeto", "alta")
caso("S09", "entidade em outro chunk, sujeito da publicação", "Qual a taxa de ocupação do Hospital Regional de Taguatinga (HRT) no trimestre?", "A taxa de ocupação do HRT foi de 82%.",
     {"P1": ["Relatório assistencial do Hospital Regional de Taguatinga (HRT), terceiro trimestre de 2024. O relatório analisa os indicadores de desempenho.", "Indicadores: taxa de ocupação de leitos 82%; tempo médio de permanência 5 dias."]},
     [{"pub": "P1", "texto": "Indicadores: taxa de ocupação de leitos 82%"}], HRT, "INDICADOR",
     [al("HRT", "sustentado_documental", "nao", "sim", "sujeito da publicação (cabeçalho), em outro chunk")], "o relatório inteiro é do HRT, definido na primeira frase", "media_alta")
caso("S10", "entidade em publicação diferente", QOBJ, "O objeto é a manutenção de tomógrafos do HRT.",
     {"P1": ["Contrato nº 12/2025. Objeto: manutenção de tomógrafos. Vigência: 12 meses."], "P2": ["Portaria nº 7/2025. O Hospital Regional de Taguatinga (HRT) foi incluído na rede de urgência."]}, [{"pub": "P1", "texto": "Objeto: manutenção de tomógrafos"}], HRT, "OBJETO",
     [al("HRT", "nao_sustentado_herdado", "nao", "nao", "o HRT está em outra publicação")], "proximidade entre documentos não cria relação", "alta")
caso("S11", "atributo associado a outra entidade", "Qual o objeto do contrato do Hospital Regional de Taguatinga (HRT)?", "O HRT contratou manutenção de tomógrafos.",
     {"P1": ["Extrato nº 20/2025. O Hospital Regional de Sobradinho (HRS) contratou manutenção de tomógrafos. O Hospital Regional de Taguatinga (HRT) contratou aquisição de monitores."]},
     [{"pub": "P1", "texto": "O Hospital Regional de Sobradinho (HRS) contratou manutenção de tomógrafos"}, {"pub": "P1", "texto": "O Hospital Regional de Taguatinga (HRT) contratou aquisição de monitores"}], HRT, "OBJETO",
     [al("HRT", "nao_sustentado_outra_entidade", "nao", "nao", "a manutenção é do HRS")], "frases adjacentes com entidades e objetos trocados", "alta", ["hospital regional de sobradinho", "hrs"])
caso("S12", "dois atributos para uma entidade", "Qual o objeto e o valor do contrato do Hospital Regional de Taguatinga (HRT)?", "O HRT contratou manutenção de tomógrafos, no valor de R$ 50.000,00.",
     {"P1": ["Extrato nº 21/2025. O Hospital Regional de Taguatinga (HRT) contratou manutenção de tomógrafos, no valor de R$ 50.000,00."]}, [{"pub": "P1", "texto": "O Hospital Regional de Taguatinga (HRT) contratou manutenção de tomógrafos, no valor de R$ 50.000,00"}], HRT, "OBJETO",
     [al("HRT", "sustentado", "sim", "sim", "explícita (objeto e valor)")], "ambos os atributos na mesma frase com o HRT como sujeito", "alta")
caso("S13", "mesmo atributo para duas entidades", "Qual o objeto do contrato do Hospital Regional de Sobradinho (HRS)?", "O HRS contratou manutenção de tomógrafos.",
     {"P1": ["Extrato nº 22/2025. O Hospital Regional de Taguatinga (HRT) e o Hospital Regional de Sobradinho (HRS) contrataram manutenção de tomógrafos."]}, [{"pub": "P1", "texto": "O Hospital Regional de Taguatinga (HRT) e o Hospital Regional de Sobradinho (HRS) contrataram manutenção de tomógrafos"}], HRS, "OBJETO",
     [al("HRS", "sustentado", "sim", "sim", "explícita, sujeito composto")], "o HRS é um dos sujeitos da mesma frase", "alta")
caso("S14", "conflito de rótulo com competência explícita", "Quais as competências do Diretor do Hospital Regional de Taguatinga (HRT)?", "Compete ao Diretor do HRT deliberar sobre o transporte de pacientes.",
     {"P1": ["Portaria nº 8/2025. Titular: o Diretor do HRT, a quem compete deliberar sobre o transporte de pacientes."]}, [{"pub": "P1", "texto": "Titular: o Diretor do HRT, a quem compete deliberar sobre o transporte de pacientes"}], HRT, "COMPETENCIA",
     [al("HRT", "sustentado", "sim", "sim", "explícita ('a quem compete')")], "o rótulo é Titular, mas a frase atribui expressamente a competência ao Diretor do HRT", "alta")
caso("S15", "conflito de rótulo sem competência explícita", "Quais as competências do Hospital Regional de Taguatinga (HRT)?", "O Diretor do HRT integra a comissão e delibera sobre o transporte de pacientes.",
     {"P1": ["Portaria nº 8/2025. Art. 2º Designar membros: 4 - Titular: Diretor do Hospital Regional de Taguatinga (HRT); Suplente: substituto legal do cargo."]}, [{"pub": "P1", "texto": "4 - Titular: Diretor do Hospital Regional de Taguatinga (HRT)"}], HRT, "COMPETENCIA",
     [al("HRT", "nao_sustentado_outro_atributo", "nao", "nao", "o HRT aparece como cargo de titular; nada sobre competência")], "só a designação de membro; 'delibera sobre transporte' não está no texto", "alta")
caso("S16", "localização herdada da pergunta", "Qual a aquisição de ambulâncias prevista para Ceilândia?", "O contrato prevê a aquisição de ambulâncias para Ceilândia.",
     {"P1": ["Extrato nº 8/2025. Objeto: aquisição de ambulâncias para a rede de urgência do Distrito Federal."]}, [{"pub": "P1", "texto": "Objeto: aquisição de ambulâncias para a rede de urgência do Distrito Federal"}], CEIL, "OBJETO",
     [al("Ceilândia", "nao_sustentado_herdado", "nao", "nao", "ausente")], "a localidade só está na pergunta", "alta")
caso("S17", "destinatário diferente da entidade perguntada", "Quais itens foram adquiridos para a Atenção Primária?", "Foi adquirida luva cirúrgica para a Atenção Primária.",
     {"P1": ["RATIFICO a aquisição do item Código SES 1 - LUVA CIRÚRGICA, para atender as necessidades do Hospital Regional do Guará, no valor global de R$ 300,00. RATIFICO a aquisição do item Código SES 2 - MÁSCARA CIRÚRGICA, para atender as necessidades da Atenção Primária, no valor global de R$ 120,00."]},
     [{"pub": "P1", "texto": "LUVA CIRÚRGICA, para atender as necessidades do Hospital Regional do Guará"}], AP, "OBJETO",
     [al("Atenção Primária", "nao_sustentado_outra_entidade", "nao", "nao", "o destinatário do registro da luva é outro")], "o destinatário da luva é o Hospital Regional do Guará; a Atenção Primária aparece em outro registro", "alta", ["hospital regional do guara"])
caso("S18", "destinatário correto, destinatário diferente em outro registro", "Quais itens foram adquiridos para a Atenção Primária?", "Foi adquirida máscara cirúrgica para a Atenção Primária.",
     {"P1": ["RATIFICO a aquisição do item Código SES 1 - LUVA CIRÚRGICA, para atender as necessidades do Hospital Regional do Guará, no valor global de R$ 300,00. RATIFICO a aquisição do item Código SES 2 - MÁSCARA CIRÚRGICA, para atender as necessidades da Atenção Primária, no valor global de R$ 120,00."]},
     [{"pub": "P1", "texto": "MÁSCARA CIRÚRGICA, para atender as necessidades da Atenção Primária"}], AP, "OBJETO",
     [al("Atenção Primária", "sustentado", "sim", "sim", "explícita no registro")], "o registro da máscara nomeia a Atenção Primária como destinatária", "alta", ["hospital regional do guara"])
caso("S19", "relação ambígua (consórcio)", "Qual a obra executada pela empresa Alfa Serviços Ltda?", "A Alfa executará a parte elétrica da obra de reforma da UPA.",
     {"P1": ["Extrato nº 30/2025. A Alfa Serviços Ltda e a Beta Engenharia Ltda, em consórcio, executarão a obra de reforma da UPA, cabendo à primeira a parte elétrica."]}, [{"pub": "P1", "texto": "A Alfa Serviços Ltda e a Beta Engenharia Ltda, em consórcio, executarão a obra de reforma da UPA, cabendo à primeira a parte elétrica"}], ALFA, "OBJETO",
     [al("Alfa", "ambiguo", "sim", "sim", "'a primeira' = Alfa, mas exige resolver a ordem de menção")], "a relação depende de resolver 'a primeira'; plausível, mas exige leitura da ordem", "media", ["beta engenharia ltda", "beta"])
caso("S20", "evidência incompleta (relação cortada na fronteira do chunk)", "O que o Hospital Regional de Taguatinga (HRT) passará a oferecer?", "O HRT passará a oferecer exames de tomografia.",
     {"P1": ["Nota nº 6/2025. O Hospital Regional de Taguatinga (HRT) passará a oferecer", "exames de tomografia a partir de maio."]}, [{"pub": "P1", "texto": "exames de tomografia a partir de maio"}], HRT, "OBJETO",
     [al("HRT", "nao_verificavel", "nao", "sim", "a frase atravessa a fronteira de chunk; o trecho citado não contém a entidade")], "o vínculo existe no documento, mas a citação isola o atributo; exige leitura da frase inteira", "media")
caso("S21", "resposta que mistura correto e incorreto", "O que o Hospital Regional de Taguatinga (HRT) contratou?", "O HRT contratou manutenção de tomógrafos. O HRT contratou aquisição de ambulâncias.",
     {"P1": ["Extrato nº 31/2025. O Hospital Regional de Taguatinga (HRT) contratou manutenção de tomógrafos. A Secretaria de Saúde contratou aquisição de ambulâncias."]},
     [{"pub": "P1", "texto": "O Hospital Regional de Taguatinga (HRT) contratou manutenção de tomógrafos"}, {"pub": "P1", "texto": "A Secretaria de Saúde contratou aquisição de ambulâncias"}], HRT, "OBJETO",
     [al("manutenção de tomógrafos", "sustentado", "sim", "sim", "explícita"), al("aquisição de ambulâncias", "nao_sustentado_outra_entidade", "nao", "nao", "a contratante é a Secretaria")],
     "primeira afirmação sustentada; segunda atribui ao HRT o que é da Secretaria", "alta", ["secretaria de saude"])
caso("S22", "anáfora por pronome", "O que a empresa Alfa Serviços Ltda fornecerá?", "A Alfa fornecerá os tomógrafos.",
     {"P1": ["Extrato nº 32/2025. A Alfa Serviços Ltda assinou o contrato. Ela fornecerá os tomógrafos."]}, [{"pub": "P1", "texto": "Ela fornecerá os tomógrafos"}], ALFA, "OBJETO",
     [al("Alfa", "sustentado", "sim", "sim", "adjacente com anáfora ('Ela')")], "referente único na frase anterior", "media_alta")
caso("S23", "resposta que apenas repete a pergunta", QOBJ, "O contrato do HRT tem um objeto.",
     {"P1": ["Contrato nº 12/2025. Objeto: manutenção de tomógrafos. Testemunha: Diretor do HRT."]}, [{"pub": "P1", "texto": "Objeto: manutenção de tomógrafos"}], HRT, "OBJETO",
     [al("HRT", "nao_verificavel", "nao", "nao", "a resposta não afirma conteúdo novo")], "sem afirmação nova não há relação a verificar", "media")
caso("S24", "eco da pergunta ambíguo (padrão A06)", "Quais as competências da Coordenação de Regulação da Região Sul em relação aos serviços do Gama?", "Compete discutir e deliberar sobre os serviços regulados no Gama.",
     {"P1": ["Ordem nº 1/2025. Coordenação de Regulação da Região Sul (CRSSU). IV - Compete à CRSSU discutir e deliberar sobre os serviços regulados em toda a Região Sul."]}, [{"pub": "P1", "texto": "IV - Compete à CRSSU discutir e deliberar sobre os serviços regulados em toda a Região Sul"}], GAMA, "COMPETENCIA",
     [al("Gama", "ambiguo", "nao", "nao", "a competência é regional; o Gama pode estar incluído")], "duas leituras plausíveis (eco legítimo ou localização sem apoio)", "baixa")
caso("S25", "localidade na mesma frase da competência", "Quais as competências da Coordenação de Regulação da Região Sul em relação aos serviços do Gama?", "Compete deliberar sobre os serviços regulados, inclusive os do Gama.",
     {"P1": ["Ordem nº 1/2025. Coordenação de Regulação da Região Sul (CRSSU). IV - Compete à CRSSU deliberar sobre os serviços regulados, inclusive os do Gama."]}, [{"pub": "P1", "texto": "IV - Compete à CRSSU deliberar sobre os serviços regulados, inclusive os do Gama"}], GAMA, "COMPETENCIA",
     [al("Gama", "sustentado", "sim", "sim", "explícita ('inclusive os do Gama')")], "a frase estende a competência ao Gama", "alta")
caso("S26", "localidade como parte de outra entidade em frase não adjacente (padrão val-087)", "Quais as competências da Coordenação de Regulação da Região Sul em relação aos serviços do Gama?", "A Coordenação norteia as gerências de regulação no Gama.",
     {"P1": ["Ordem nº 1/2025. Coordenação de Regulação da Região Sul (CRSSU). IX - As Deliberações deverão nortear as gerências de regulação no cumprimento das atribuições regimentais. X - A Coordenação reunir-se-á mensalmente. XI - Poderão se manifestar os presidentes dos Conselhos de Saúde do Gama e de Santa Maria."]},
     [{"pub": "P1", "texto": "As Deliberações deverão nortear as gerências de regulação no cumprimento das atribuições regimentais"}], GAMA, "COMPETENCIA",
     [al("Gama", "nao_sustentado_outra_entidade", "nao", "nao", "o Gama aparece como parte do nome de outro órgão (Conselhos de Saúde do Gama)")], "o único 'Gama' do texto pertence ao nome de um conselho, em frase não relacionada à competência", "media_alta")

# ---------- especificacao dos 5 casos reais (expectativas congeladas ANTES da execucao)
REAIS = {
 "val-087-A-r1": {"descricao": "val-087, resposta A-r1 (flag desligada), doc 174", "doc": 174, "chunks_do_contexto": ["dodf-174:est300o30:0004", "dodf-174:est300o30:0001", "dodf-174:est300o30:0000"],
                  "entidades": [E("Gama", ["gama"], "localidade"), E("CRSSU", ["crssu", "coordenacao de regulacao da regiao de saude sul"])], "atributo_familia": "COMPETENCIA", "outras_entidades": [],
                  "esperado": {"Gama": {"vinculo": "nao_sustentado_outra_entidade", "citacao": "nao", "documental": "nao", "nota": "no texto, 'Gama' é endereço/nome de outros órgãos (HRG, Conselhos de Saúde do Gama), em incisos distintos do IX"},
                               "CRSSU": {"vinculo": "sustentado_documental", "citacao": "nao", "documental": "sim", "nota": "Art. 1º/Art. 4º definem a CRSSU e suas competências; o inciso IX citado não nomeia a CRSSU"}}},
 "val-024": {"descricao": "val-024, doc 718", "doc": 718, "chunks_do_contexto": ["dodf-718:est300o30:0000"], "entidades": [E("Hospital Regional de Ceilândia", ["hospital regional de ceilandia", "hrc"], "organizacao", ["ceilandia"])],
             "atributo_familia": "OBJETO", "outras_entidades": ["hran", "hrs", "hrl", "crt"], "esperado": {"Hospital Regional de Ceilândia": {"vinculo": "nao_sustentado_herdado", "citacao": "nao", "documental": "nao",
             "nota": "o doc lista HRAN, CRT, CEO UBS 11 - Ceilândia, HRS, HRL; 'Ceilândia' é a localidade da UBS 11, não o Hospital Regional de Ceilândia"}}},
 "val-031": {"descricao": "val-031, doc 1464", "doc": 1464, "chunks_do_contexto": ["dodf-1464:est300o30:0000", "dodf-1464:est300o30:0004"], "entidades": [E("Hospital da Criança de Brasília José Alencar", ["hospital da crianca de brasilia jose alencar", "hcb"])],
             "atributo_familia": "INDICADOR", "outras_entidades": [], "esperado": {"Hospital da Criança de Brasília José Alencar": {"vinculo": "sustentado_documental", "citacao": "nao", "documental": "sim",
             "nota": "a primeira frase do relatório define o HCB como o hospital objeto de todo o relatório; o span citado está em outro chunk"}}},
 "val-020": {"descricao": "val-020, doc 361", "doc": 361, "chunks_do_contexto": ["dodf-361:est300o30:0001"], "entidades": [E("Gama", ["gama"], "localidade")], "atributo_familia": "OBJETO", "outras_entidades": [],
             "esperado": {"Gama": {"vinculo": "ambiguo", "citacao": "nao", "documental": "parcial", "nota": "o Gama é endereço de uma filial da empresa credenciada, no fim do mesmo ato; a resposta omite que é filial; exige leitura humana"}}},
 "val-083": {"descricao": "val-083, doc 495 (C1) e doc 1444 (C2)", "doc": [495, 1444], "chunks_do_contexto": ["dodf-495:est300o30:0015", "dodf-1444:est300o30:0014"], "entidades": [E("Atenção Primária", ["atencao primaria"])],
             "atributo_familia": "OBJETO", "outras_entidades": ["hospital regional do guara"], "itens": {"VITAMINA D": "sustentado", "CLORETO DE SODIO": "nao_sustentado_outra_entidade"},
             "esperado": {"Atenção Primária": {"vinculo": "por_item", "citacao": "ver itens", "documental": "ver itens", "nota": "destinatário literal do registro; o gabarito do dataset trata os itens do Hospital Regional do Guará como parte da resposta (interpretação humana)"}}},
}
(AQUI / "CASOS_SINTETICOS_4D5.json").write_text(json.dumps({"versao": "casos_4d5/1", "natureza": "sintético; rotulagem de referência do autor, sem segundo avaliador humano", "casos": S}, ensure_ascii=False, indent=1), encoding="utf-8")
(AQUI / "ESPECIFICACAO_REAIS_4D5.json").write_text(json.dumps(REAIS, ensure_ascii=False, indent=1), encoding="utf-8")
L = ["# Rotulagem — Fase 4D.5 (congelada antes da execução do protótipo)", "", "Autor dos casos = autor dos rótulos; **não há segundo avaliador humano**. Vocabulário de `vínculo esperado`: sustentado (relação expressa no texto da citação: mesma frase ou frase adjacente com vínculo textual), sustentado_documental (só na publicação/cabeçalho), nao_sustentado_herdado, nao_sustentado_outra_entidade, nao_sustentado_outro_atributo, nao_verificavel, ambiguo.", "", "## Casos sintéticos", ""]
for c in S:
    L += [f"### {c['id']} — {c['tema']}", f"- Pergunta: {c['pergunta']}", f"- Resposta: {c['resposta']}", f"- Publicações/chunks: {json.dumps(c['publicacoes'], ensure_ascii=False)}", f"- Citação: {json.dumps(c['citacoes'], ensure_ascii=False)}",
          f"- Entidade: {c['entidade']['nome']} ({c['entidade']['tipo']}); atributo: {c['atributo_familia']}"]
    for a in c["alvos"]:
        L.append(f"- Alvo '{a['trecho_da_resposta']}': **{a['vinculo_esperado']}** (citação: {a['sustentacao_da_citacao']}; documental: {a['sustentacao_documental']}; relação: {a['relacao_esperada']})")
    L += [f"- Justificativa: {c['justificativa']} — confiança: {c['confianca']}", ""]
L += ["## Casos reais (expectativas congeladas antes de executar o protótipo)", ""]
for k, v in REAIS.items():
    L.append(f"### {k} — {v['descricao']}")
    for e, x in v["esperado"].items():
        L.append(f"- {e}: **{x['vinculo']}** (citação: {x['citacao']}; documental: {x['documental']}) — {x['nota']}")
    if "itens" in v:
        L.append(f"- Itens: {v['itens']}")
    L.append("")
(AQUI / "ROTULAGEM_4D5.md").write_text("\n".join(L), encoding="utf-8")
h = {n: hashlib.sha256((AQUI / n).read_bytes()).hexdigest() for n in ("CASOS_SINTETICOS_4D5.json", "ESPECIFICACAO_REAIS_4D5.json", "ROTULAGEM_4D5.md")}
(AQUI / "CONGELAMENTO_ROTULAGEM_4D5.json").write_text(json.dumps({"congelado_em": datetime.datetime.now().isoformat(timespec="seconds"), "sha256": h, "observacao": "gerado antes de escrever/executar o protótipo"}, indent=1), encoding="utf-8")
from collections import Counter  # noqa: E402
print(len(S), Counter(a["vinculo_esperado"] for c in S for a in c["alvos"]))
