# Rotulagem — Fase 4D.5 (congelada antes da execução do protótipo)

Autor dos casos = autor dos rótulos; **não há segundo avaliador humano**. Vocabulário de `vínculo esperado`: sustentado (relação expressa no texto da citação: mesma frase ou frase adjacente com vínculo textual), sustentado_documental (só na publicação/cabeçalho), nao_sustentado_herdado, nao_sustentado_outra_entidade, nao_sustentado_outro_atributo, nao_verificavel, ambiguo.

## Casos sintéticos

### S01 — mesma frase, relação explícita
- Pergunta: Qual o objeto do contrato da empresa Alfa Serviços Ltda?
- Resposta: A Alfa Serviços Ltda foi contratada para a manutenção de tomógrafos.
- Publicações/chunks: {"P1": ["Contrato nº 15/2025. A Alfa Serviços Ltda foi contratada para a manutenção de tomógrafos do hospital."]}
- Citação: [{"pub": "P1", "texto": "A Alfa Serviços Ltda foi contratada para a manutenção de tomógrafos do hospital"}]
- Entidade: Alfa Serviços Ltda (organizacao); atributo: OBJETO
- Alvo 'Alfa': **sustentado** (citação: sim; documental: sim; relação: explícita)
- Justificativa: entidade e atributo na mesma frase, ligados por 'foi contratada para' — confiança: alta

### S02 — mesma frase, coocorrência sem relação com a entidade
- Pergunta: Qual o objeto do contrato da empresa Alfa Serviços Ltda?
- Resposta: A Alfa Serviços Ltda contratou a manutenção de tomógrafos.
- Publicações/chunks: {"P1": ["Ata nº 3/2025. Na reunião, a Alfa Serviços Ltda observou que a manutenção de tomógrafos será contratada pela Beta Engenharia Ltda."]}
- Citação: [{"pub": "P1", "texto": "Na reunião, a Alfa Serviços Ltda observou que a manutenção de tomógrafos será contratada pela Beta Engenharia Ltda"}]
- Entidade: Alfa Serviços Ltda (organizacao); atributo: OBJETO
- Alvo 'Alfa': **nao_sustentado_outra_entidade** (citação: nao; documental: nao; relação: coocorrência; o contratante é a Beta)
- Justificativa: a Alfa só aparece como quem observou; quem contrata é a Beta — confiança: alta

### S03 — frases adjacentes com anáfora
- Pergunta: Quais exames o Hospital Regional de Taguatinga (HRT) passou a oferecer?
- Resposta: O HRT passou a oferecer exames de tomografia.
- Publicações/chunks: {"P1": ["Nota nº 4/2025. O Hospital Regional de Taguatinga (HRT) recebeu o novo equipamento em março. A unidade passou a oferecer exames de tomografia."]}
- Citação: [{"pub": "P1", "texto": "A unidade passou a oferecer exames de tomografia"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **sustentado** (citação: sim; documental: sim; relação: adjacente com anáfora ('A unidade' retoma o HRT))
- Justificativa: a frase citada retoma o HRT por 'A unidade' (referente único na frase anterior) — confiança: media_alta

### S04 — frases adjacentes sem vínculo textual
- Pergunta: O que o contrato prevê para o Hospital Regional de Taguatinga (HRT)?
- Resposta: O contrato prevê a aquisição de monitores multiparâmetros para o HRT.
- Publicações/chunks: {"P1": ["Extrato nº 9/2025. O Hospital Regional de Taguatinga (HRT) foi visitado pelo Secretário. O contrato prevê a aquisição de monitores multiparâmetros."]}
- Citação: [{"pub": "P1", "texto": "O contrato prevê a aquisição de monitores multiparâmetros"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **nao_verificavel** (citação: nao; documental: nao; relação: só proximidade)
- Justificativa: a frase anterior menciona o HRT por outro motivo (visita); nada liga o contrato ao HRT — confiança: media

### S05 — anáfora ambígua
- Pergunta: Quais exames o Hospital Regional de Taguatinga (HRT) passou a oferecer?
- Resposta: O HRT passou a oferecer exames de tomografia.
- Publicações/chunks: {"P1": ["Nota nº 5/2025. O Hospital Regional de Taguatinga (HRT) recebeu o equipamento. O Hospital Regional de Sobradinho (HRS) ampliou o atendimento. A unidade passou a oferecer exames de tomografia."]}
- Citação: [{"pub": "P1", "texto": "A unidade passou a oferecer exames de tomografia"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **ambiguo** (citação: nao; documental: nao; relação: 'A unidade' pode ser o HRT ou o HRS)
- Justificativa: dois referentes possíveis para 'A unidade' — confiança: media

### S06 — entidade só na pergunta (organização)
- Pergunta: Qual o objeto do contrato do Hospital Regional de Taguatinga (HRT)?
- Resposta: O objeto é a manutenção de tomógrafos do HRT.
- Publicações/chunks: {"P1": ["Contrato nº 12/2025. Objeto: manutenção de tomógrafos. Vigência: 12 meses."]}
- Citação: [{"pub": "P1", "texto": "Objeto: manutenção de tomógrafos"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **nao_sustentado_herdado** (citação: nao; documental: nao; relação: ausente)
- Justificativa: o HRT não consta em nenhum ponto da publicação — confiança: alta

### S07 — entidade em outra frase não relacionada do mesmo chunk
- Pergunta: Qual o objeto do contrato do Hospital Regional de Taguatinga (HRT)?
- Resposta: O objeto é a manutenção de tomógrafos do HRT.
- Publicações/chunks: {"P1": ["Contrato nº 12/2025. Objeto: manutenção de tomógrafos. A empresa executará os serviços em 12 meses. O HRT realizou a reunião de abertura no dia 3 de março."]}
- Citação: [{"pub": "P1", "texto": "Objeto: manutenção de tomógrafos"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **nao_sustentado_herdado** (citação: nao; documental: nao; relação: menção em frase sem relação com o objeto)
- Justificativa: o HRT só aparece numa frase sobre reunião — confiança: media_alta

### S08 — entidade em outro chunk, outro papel
- Pergunta: Qual o objeto do contrato do Hospital Regional de Taguatinga (HRT)?
- Resposta: O objeto é a manutenção de tomógrafos do HRT.
- Publicações/chunks: {"P1": ["Contrato nº 12/2025. Objeto: manutenção de tomógrafos. Vigência: 12 meses.", "Testemunha: Diretor do HRT. Data de assinatura: 07/05/2025."]}
- Citação: [{"pub": "P1", "texto": "Objeto: manutenção de tomógrafos"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **nao_sustentado_outro_atributo** (citação: nao; documental: nao; relação: o HRT aparece como testemunha, outro papel)
- Justificativa: o HRT é mencionado no outro chunk como testemunha, não como destinatário do objeto — confiança: alta

### S09 — entidade em outro chunk, sujeito da publicação
- Pergunta: Qual a taxa de ocupação do Hospital Regional de Taguatinga (HRT) no trimestre?
- Resposta: A taxa de ocupação do HRT foi de 82%.
- Publicações/chunks: {"P1": ["Relatório assistencial do Hospital Regional de Taguatinga (HRT), terceiro trimestre de 2024. O relatório analisa os indicadores de desempenho.", "Indicadores: taxa de ocupação de leitos 82%; tempo médio de permanência 5 dias."]}
- Citação: [{"pub": "P1", "texto": "Indicadores: taxa de ocupação de leitos 82%"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: INDICADOR
- Alvo 'HRT': **sustentado_documental** (citação: nao; documental: sim; relação: sujeito da publicação (cabeçalho), em outro chunk)
- Justificativa: o relatório inteiro é do HRT, definido na primeira frase — confiança: media_alta

### S10 — entidade em publicação diferente
- Pergunta: Qual o objeto do contrato do Hospital Regional de Taguatinga (HRT)?
- Resposta: O objeto é a manutenção de tomógrafos do HRT.
- Publicações/chunks: {"P1": ["Contrato nº 12/2025. Objeto: manutenção de tomógrafos. Vigência: 12 meses."], "P2": ["Portaria nº 7/2025. O Hospital Regional de Taguatinga (HRT) foi incluído na rede de urgência."]}
- Citação: [{"pub": "P1", "texto": "Objeto: manutenção de tomógrafos"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **nao_sustentado_herdado** (citação: nao; documental: nao; relação: o HRT está em outra publicação)
- Justificativa: proximidade entre documentos não cria relação — confiança: alta

### S11 — atributo associado a outra entidade
- Pergunta: Qual o objeto do contrato do Hospital Regional de Taguatinga (HRT)?
- Resposta: O HRT contratou manutenção de tomógrafos.
- Publicações/chunks: {"P1": ["Extrato nº 20/2025. O Hospital Regional de Sobradinho (HRS) contratou manutenção de tomógrafos. O Hospital Regional de Taguatinga (HRT) contratou aquisição de monitores."]}
- Citação: [{"pub": "P1", "texto": "O Hospital Regional de Sobradinho (HRS) contratou manutenção de tomógrafos"}, {"pub": "P1", "texto": "O Hospital Regional de Taguatinga (HRT) contratou aquisição de monitores"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **nao_sustentado_outra_entidade** (citação: nao; documental: nao; relação: a manutenção é do HRS)
- Justificativa: frases adjacentes com entidades e objetos trocados — confiança: alta

### S12 — dois atributos para uma entidade
- Pergunta: Qual o objeto e o valor do contrato do Hospital Regional de Taguatinga (HRT)?
- Resposta: O HRT contratou manutenção de tomógrafos, no valor de R$ 50.000,00.
- Publicações/chunks: {"P1": ["Extrato nº 21/2025. O Hospital Regional de Taguatinga (HRT) contratou manutenção de tomógrafos, no valor de R$ 50.000,00."]}
- Citação: [{"pub": "P1", "texto": "O Hospital Regional de Taguatinga (HRT) contratou manutenção de tomógrafos, no valor de R$ 50.000,00"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **sustentado** (citação: sim; documental: sim; relação: explícita (objeto e valor))
- Justificativa: ambos os atributos na mesma frase com o HRT como sujeito — confiança: alta

### S13 — mesmo atributo para duas entidades
- Pergunta: Qual o objeto do contrato do Hospital Regional de Sobradinho (HRS)?
- Resposta: O HRS contratou manutenção de tomógrafos.
- Publicações/chunks: {"P1": ["Extrato nº 22/2025. O Hospital Regional de Taguatinga (HRT) e o Hospital Regional de Sobradinho (HRS) contrataram manutenção de tomógrafos."]}
- Citação: [{"pub": "P1", "texto": "O Hospital Regional de Taguatinga (HRT) e o Hospital Regional de Sobradinho (HRS) contrataram manutenção de tomógrafos"}]
- Entidade: Hospital Regional de Sobradinho (organizacao); atributo: OBJETO
- Alvo 'HRS': **sustentado** (citação: sim; documental: sim; relação: explícita, sujeito composto)
- Justificativa: o HRS é um dos sujeitos da mesma frase — confiança: alta

### S14 — conflito de rótulo com competência explícita
- Pergunta: Quais as competências do Diretor do Hospital Regional de Taguatinga (HRT)?
- Resposta: Compete ao Diretor do HRT deliberar sobre o transporte de pacientes.
- Publicações/chunks: {"P1": ["Portaria nº 8/2025. Titular: o Diretor do HRT, a quem compete deliberar sobre o transporte de pacientes."]}
- Citação: [{"pub": "P1", "texto": "Titular: o Diretor do HRT, a quem compete deliberar sobre o transporte de pacientes"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: COMPETENCIA
- Alvo 'HRT': **sustentado** (citação: sim; documental: sim; relação: explícita ('a quem compete'))
- Justificativa: o rótulo é Titular, mas a frase atribui expressamente a competência ao Diretor do HRT — confiança: alta

### S15 — conflito de rótulo sem competência explícita
- Pergunta: Quais as competências do Hospital Regional de Taguatinga (HRT)?
- Resposta: O Diretor do HRT integra a comissão e delibera sobre o transporte de pacientes.
- Publicações/chunks: {"P1": ["Portaria nº 8/2025. Art. 2º Designar membros: 4 - Titular: Diretor do Hospital Regional de Taguatinga (HRT); Suplente: substituto legal do cargo."]}
- Citação: [{"pub": "P1", "texto": "4 - Titular: Diretor do Hospital Regional de Taguatinga (HRT)"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: COMPETENCIA
- Alvo 'HRT': **nao_sustentado_outro_atributo** (citação: nao; documental: nao; relação: o HRT aparece como cargo de titular; nada sobre competência)
- Justificativa: só a designação de membro; 'delibera sobre transporte' não está no texto — confiança: alta

### S16 — localização herdada da pergunta
- Pergunta: Qual a aquisição de ambulâncias prevista para Ceilândia?
- Resposta: O contrato prevê a aquisição de ambulâncias para Ceilândia.
- Publicações/chunks: {"P1": ["Extrato nº 8/2025. Objeto: aquisição de ambulâncias para a rede de urgência do Distrito Federal."]}
- Citação: [{"pub": "P1", "texto": "Objeto: aquisição de ambulâncias para a rede de urgência do Distrito Federal"}]
- Entidade: Ceilândia (localidade); atributo: OBJETO
- Alvo 'Ceilândia': **nao_sustentado_herdado** (citação: nao; documental: nao; relação: ausente)
- Justificativa: a localidade só está na pergunta — confiança: alta

### S17 — destinatário diferente da entidade perguntada
- Pergunta: Quais itens foram adquiridos para a Atenção Primária?
- Resposta: Foi adquirida luva cirúrgica para a Atenção Primária.
- Publicações/chunks: {"P1": ["RATIFICO a aquisição do item Código SES 1 - LUVA CIRÚRGICA, para atender as necessidades do Hospital Regional do Guará, no valor global de R$ 300,00. RATIFICO a aquisição do item Código SES 2 - MÁSCARA CIRÚRGICA, para atender as necessidades da Atenção Primária, no valor global de R$ 120,00."]}
- Citação: [{"pub": "P1", "texto": "LUVA CIRÚRGICA, para atender as necessidades do Hospital Regional do Guará"}]
- Entidade: Atenção Primária (organizacao); atributo: OBJETO
- Alvo 'Atenção Primária': **nao_sustentado_outra_entidade** (citação: nao; documental: nao; relação: o destinatário do registro da luva é outro)
- Justificativa: o destinatário da luva é o Hospital Regional do Guará; a Atenção Primária aparece em outro registro — confiança: alta

### S18 — destinatário correto, destinatário diferente em outro registro
- Pergunta: Quais itens foram adquiridos para a Atenção Primária?
- Resposta: Foi adquirida máscara cirúrgica para a Atenção Primária.
- Publicações/chunks: {"P1": ["RATIFICO a aquisição do item Código SES 1 - LUVA CIRÚRGICA, para atender as necessidades do Hospital Regional do Guará, no valor global de R$ 300,00. RATIFICO a aquisição do item Código SES 2 - MÁSCARA CIRÚRGICA, para atender as necessidades da Atenção Primária, no valor global de R$ 120,00."]}
- Citação: [{"pub": "P1", "texto": "MÁSCARA CIRÚRGICA, para atender as necessidades da Atenção Primária"}]
- Entidade: Atenção Primária (organizacao); atributo: OBJETO
- Alvo 'Atenção Primária': **sustentado** (citação: sim; documental: sim; relação: explícita no registro)
- Justificativa: o registro da máscara nomeia a Atenção Primária como destinatária — confiança: alta

### S19 — relação ambígua (consórcio)
- Pergunta: Qual a obra executada pela empresa Alfa Serviços Ltda?
- Resposta: A Alfa executará a parte elétrica da obra de reforma da UPA.
- Publicações/chunks: {"P1": ["Extrato nº 30/2025. A Alfa Serviços Ltda e a Beta Engenharia Ltda, em consórcio, executarão a obra de reforma da UPA, cabendo à primeira a parte elétrica."]}
- Citação: [{"pub": "P1", "texto": "A Alfa Serviços Ltda e a Beta Engenharia Ltda, em consórcio, executarão a obra de reforma da UPA, cabendo à primeira a parte elétrica"}]
- Entidade: Alfa Serviços Ltda (organizacao); atributo: OBJETO
- Alvo 'Alfa': **ambiguo** (citação: sim; documental: sim; relação: 'a primeira' = Alfa, mas exige resolver a ordem de menção)
- Justificativa: a relação depende de resolver 'a primeira'; plausível, mas exige leitura da ordem — confiança: media

### S20 — evidência incompleta (relação cortada na fronteira do chunk)
- Pergunta: O que o Hospital Regional de Taguatinga (HRT) passará a oferecer?
- Resposta: O HRT passará a oferecer exames de tomografia.
- Publicações/chunks: {"P1": ["Nota nº 6/2025. O Hospital Regional de Taguatinga (HRT) passará a oferecer", "exames de tomografia a partir de maio."]}
- Citação: [{"pub": "P1", "texto": "exames de tomografia a partir de maio"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **nao_verificavel** (citação: nao; documental: sim; relação: a frase atravessa a fronteira de chunk; o trecho citado não contém a entidade)
- Justificativa: o vínculo existe no documento, mas a citação isola o atributo; exige leitura da frase inteira — confiança: media

### S21 — resposta que mistura correto e incorreto
- Pergunta: O que o Hospital Regional de Taguatinga (HRT) contratou?
- Resposta: O HRT contratou manutenção de tomógrafos. O HRT contratou aquisição de ambulâncias.
- Publicações/chunks: {"P1": ["Extrato nº 31/2025. O Hospital Regional de Taguatinga (HRT) contratou manutenção de tomógrafos. A Secretaria de Saúde contratou aquisição de ambulâncias."]}
- Citação: [{"pub": "P1", "texto": "O Hospital Regional de Taguatinga (HRT) contratou manutenção de tomógrafos"}, {"pub": "P1", "texto": "A Secretaria de Saúde contratou aquisição de ambulâncias"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'manutenção de tomógrafos': **sustentado** (citação: sim; documental: sim; relação: explícita)
- Alvo 'aquisição de ambulâncias': **nao_sustentado_outra_entidade** (citação: nao; documental: nao; relação: a contratante é a Secretaria)
- Justificativa: primeira afirmação sustentada; segunda atribui ao HRT o que é da Secretaria — confiança: alta

### S22 — anáfora por pronome
- Pergunta: O que a empresa Alfa Serviços Ltda fornecerá?
- Resposta: A Alfa fornecerá os tomógrafos.
- Publicações/chunks: {"P1": ["Extrato nº 32/2025. A Alfa Serviços Ltda assinou o contrato. Ela fornecerá os tomógrafos."]}
- Citação: [{"pub": "P1", "texto": "Ela fornecerá os tomógrafos"}]
- Entidade: Alfa Serviços Ltda (organizacao); atributo: OBJETO
- Alvo 'Alfa': **sustentado** (citação: sim; documental: sim; relação: adjacente com anáfora ('Ela'))
- Justificativa: referente único na frase anterior — confiança: media_alta

### S23 — resposta que apenas repete a pergunta
- Pergunta: Qual o objeto do contrato do Hospital Regional de Taguatinga (HRT)?
- Resposta: O contrato do HRT tem um objeto.
- Publicações/chunks: {"P1": ["Contrato nº 12/2025. Objeto: manutenção de tomógrafos. Testemunha: Diretor do HRT."]}
- Citação: [{"pub": "P1", "texto": "Objeto: manutenção de tomógrafos"}]
- Entidade: Hospital Regional de Taguatinga (organizacao); atributo: OBJETO
- Alvo 'HRT': **nao_verificavel** (citação: nao; documental: nao; relação: a resposta não afirma conteúdo novo)
- Justificativa: sem afirmação nova não há relação a verificar — confiança: media

### S24 — eco da pergunta ambíguo (padrão A06)
- Pergunta: Quais as competências da Coordenação de Regulação da Região Sul em relação aos serviços do Gama?
- Resposta: Compete discutir e deliberar sobre os serviços regulados no Gama.
- Publicações/chunks: {"P1": ["Ordem nº 1/2025. Coordenação de Regulação da Região Sul (CRSSU). IV - Compete à CRSSU discutir e deliberar sobre os serviços regulados em toda a Região Sul."]}
- Citação: [{"pub": "P1", "texto": "IV - Compete à CRSSU discutir e deliberar sobre os serviços regulados em toda a Região Sul"}]
- Entidade: Gama (localidade); atributo: COMPETENCIA
- Alvo 'Gama': **ambiguo** (citação: nao; documental: nao; relação: a competência é regional; o Gama pode estar incluído)
- Justificativa: duas leituras plausíveis (eco legítimo ou localização sem apoio) — confiança: baixa

### S25 — localidade na mesma frase da competência
- Pergunta: Quais as competências da Coordenação de Regulação da Região Sul em relação aos serviços do Gama?
- Resposta: Compete deliberar sobre os serviços regulados, inclusive os do Gama.
- Publicações/chunks: {"P1": ["Ordem nº 1/2025. Coordenação de Regulação da Região Sul (CRSSU). IV - Compete à CRSSU deliberar sobre os serviços regulados, inclusive os do Gama."]}
- Citação: [{"pub": "P1", "texto": "IV - Compete à CRSSU deliberar sobre os serviços regulados, inclusive os do Gama"}]
- Entidade: Gama (localidade); atributo: COMPETENCIA
- Alvo 'Gama': **sustentado** (citação: sim; documental: sim; relação: explícita ('inclusive os do Gama'))
- Justificativa: a frase estende a competência ao Gama — confiança: alta

### S26 — localidade como parte de outra entidade em frase não adjacente (padrão val-087)
- Pergunta: Quais as competências da Coordenação de Regulação da Região Sul em relação aos serviços do Gama?
- Resposta: A Coordenação norteia as gerências de regulação no Gama.
- Publicações/chunks: {"P1": ["Ordem nº 1/2025. Coordenação de Regulação da Região Sul (CRSSU). IX - As Deliberações deverão nortear as gerências de regulação no cumprimento das atribuições regimentais. X - A Coordenação reunir-se-á mensalmente. XI - Poderão se manifestar os presidentes dos Conselhos de Saúde do Gama e de Santa Maria."]}
- Citação: [{"pub": "P1", "texto": "As Deliberações deverão nortear as gerências de regulação no cumprimento das atribuições regimentais"}]
- Entidade: Gama (localidade); atributo: COMPETENCIA
- Alvo 'Gama': **nao_sustentado_outra_entidade** (citação: nao; documental: nao; relação: o Gama aparece como parte do nome de outro órgão (Conselhos de Saúde do Gama))
- Justificativa: o único 'Gama' do texto pertence ao nome de um conselho, em frase não relacionada à competência — confiança: media_alta

## Casos reais (expectativas congeladas antes de executar o protótipo)

### val-087-A-r1 — val-087, resposta A-r1 (flag desligada), doc 174
- Gama: **nao_sustentado_outra_entidade** (citação: nao; documental: nao) — no texto, 'Gama' é endereço/nome de outros órgãos (HRG, Conselhos de Saúde do Gama), em incisos distintos do IX
- CRSSU: **sustentado_documental** (citação: nao; documental: sim) — Art. 1º/Art. 4º definem a CRSSU e suas competências; o inciso IX citado não nomeia a CRSSU

### val-024 — val-024, doc 718
- Hospital Regional de Ceilândia: **nao_sustentado_herdado** (citação: nao; documental: nao) — o doc lista HRAN, CRT, CEO UBS 11 - Ceilândia, HRS, HRL; 'Ceilândia' é a localidade da UBS 11, não o Hospital Regional de Ceilândia

### val-031 — val-031, doc 1464
- Hospital da Criança de Brasília José Alencar: **sustentado_documental** (citação: nao; documental: sim) — a primeira frase do relatório define o HCB como o hospital objeto de todo o relatório; o span citado está em outro chunk

### val-020 — val-020, doc 361
- Gama: **ambiguo** (citação: nao; documental: parcial) — o Gama é endereço de uma filial da empresa credenciada, no fim do mesmo ato; a resposta omite que é filial; exige leitura humana

### val-083 — val-083, doc 495 (C1) e doc 1444 (C2)
- Atenção Primária: **por_item** (citação: ver itens; documental: ver itens) — destinatário literal do registro; o gabarito do dataset trata os itens do Hospital Regional do Guará como parte da resposta (interpretação humana)
- Itens: {'VITAMINA D': 'sustentado', 'CLORETO DE SODIO': 'nao_sustentado_outra_entidade'}
