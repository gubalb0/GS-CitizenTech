# Pacote de revisão — versão de REFERÊNCIA (com julgamentos originais) — NÃO entregar ao avaliador antes da avaliação

Mapeamento entre a versão cega e os casos da Fase 4D.3, com o julgamento original (de quem escreveu os casos; **não** independente) e a justificativa original, copiados sem alteração.

## Caso 1 = A07
- Descrição original do caso: caso legítimo (mundo contratos): entidade (Planaltina) só na cláusula de Valor do mesmo extrato; resposta de Objeto repete a unidade da pergunta
- Pergunta: Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda para o Hospital Regional de Planaltina?
- Resposta: O objeto é a manutenção preventiva de equipamentos de imagem, para o Hospital Regional de Planaltina.
- Entidade / atributo: Hospital Regional de Planaltina / OBJETO
- Rótulos (anotação original): Objeto: (compatível); Valor: ... para o HRP (VALOR, conflitante)
- Relação alegada entre entidade e atributo: mesmo extrato: a cláusula de Valor identifica a unidade do contrato; o Objeto é da mesma contratada
- **Julgamento atual:** classe `correta`, semântica `correta`, sustentação `sustenta`, decisão ideal `entregar`, confiança `media_alta`
- Justificativa original: afirmação: o objeto do contrato da Alfa é a manutenção preventiva, para o HRP | trecho: chunk único: 'Objeto: manutenção preventiva ...' e 'Valor: R$ 80.000,00, para o Hospital Regional de Planaltina' | entidade associada: sim, por pertencerem ao mesmo extrato | só da pergunta: o nome Planaltina também está no trecho | por quê: o extrato único liga contratada, objeto e unidade; citar a cláusula de Valor serve de âncora da unidade
- Papel na análise (tags originais): B1_bloqueia_legitimo, perda_de_recall_regra_conservadora

## Caso 2 = B04
- Descrição original do caso: rótulo conflitante (Titular) mas competência explícita no próprio trecho ('a quem compete')
- Pergunta: Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- Resposta: Compete ao Diretor do HRG deliberar sobre os serviços do Gama.
- Entidade / atributo: Gama / COMPETENCIA
- Rótulos (anotação original): Titular (MEMBRO) com cue 'a quem compete'
- Relação alegada entre entidade e atributo: associada no trecho: a competência é afirmada junto ao titular
- **Julgamento atual:** classe `correta`, semântica `correta`, sustentação `sustenta`, decisão ideal `entregar`, confiança `media_alta`
- Justificativa original: afirmação: compete ao Diretor do HRG deliberar sobre os serviços regulados do Gama | trecho: mesmo trecho: 'a quem compete deliberar sobre os serviços regulados do Gama' | entidade associada: sim | só da pergunta: não: o Gama está no trecho | por quê: o rótulo conflita, mas há evidência positiva explícita da competência
- Papel na análise (tags originais): conflito_de_rotulo_vs_evidencia_positiva, perda_de_recall_regra_conservadora

## Caso 3 = A02
- Descrição original do caso: padrão val-087-A-r1: atributo do inciso IX (neutro) + entidade só num trecho de rótulo conflitante (Titular)
- Pergunta: Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- Resposta: A Coordenação tem competência para nortear as gerências de regulação e implementar as normas e protocolos de regulação no Gama.
- Entidade / atributo: Gama / COMPETENCIA
- Rótulos (anotação original): IX: sem rótulo; 4 - Titular: (MEMBRO, conflita com COMPETENCIA)
- Relação alegada entre entidade e atributo: atributo e entidade em trechos diferentes; o trecho da entidade é de membros, não de competência
- **Julgamento atual:** classe `insuficiente_evidencia`, semântica `nao_verificavel`, sustentação `nao_sustenta_a_localizacao`, decisão ideal `bloquear`, confiança `media_alta`
- Justificativa original: afirmação: a competência de nortear/implementar normas existe 'no Gama' | trecho: IX sustenta o conteúdo; o único trecho com 'Gama' é a designação de titular do HRG | entidade associada: não: Gama aparece só como cargo do titular, não como alcance da competência | só da pergunta: parcialmente: 'Gama' está na pergunta e no trecho de membro | por quê: o trecho que contém 'Gama' é de designação de membro e não sustenta competência; a localização é um eco da pergunta ancorado em citação de outro atributo
- Papel na análise (tags originais): B1_corrige_padrao_val087_A_r1, citacao_literal_vs_sustentacao_semantica

## Caso 4 = A06
- Descrição original do caso: padrão E6: atributo de trecho compatível sem Gama + trecho de membro com Gama; resposta ecoa 'no Gama'
- Pergunta: Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- Resposta: Compete discutir e deliberar sobre os serviços regulados no Gama.
- Entidade / atributo: Gama / COMPETENCIA
- Rótulos (anotação original): IV - Compete (compatível, sem Gama); 4 - Titular (conflitante, com Gama)
- Relação alegada entre entidade e atributo: competência regional; Gama só como cargo
- **Julgamento atual:** classe `ambiguo`, semântica `nao_verificavel`, sustentação `sustenta_o_conteudo_nao_a_localizacao`, decisão ideal `indeterminado`, confiança `baixa`
- Justificativa original: afirmação: a competência de discutir/deliberar alcança os serviços do Gama | trecho: inciso IV sustenta o conteúdo; 'Gama' só no trecho de membro | entidade associada: parcial: depende de o Gama pertencer à Região Sul, que nenhum trecho afirma | só da pergunta: sim | por quê: duas leituras plausíveis: (a) eco legítimo da pergunta sobre competência regional; (b) localização não sustentada. Não forçado
- Papel na análise (tags originais): B1_bloqueia_E6, interpretacao_dupla
