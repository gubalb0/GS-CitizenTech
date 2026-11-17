# Rotulagem de referência — Fase 4D.3

Escrita **antes** de executar qualquer função do pipeline. Autor dos casos = autor dos rótulos (sem segundo avaliador): são julgamentos de referência, não verdade independente. Casos sintéticos; não representativos do corpus real.

Três avaliações separadas por caso: **correção semântica** (a resposta é verdadeira no mundo fictício descrito pelos trechos), **sustentação pelos trechos** (os trechos citados a sustentam) e **decisão ideal do pipeline** (entregar/bloquear/indeterminado). A aceitação *real* pelo pipeline é medida depois (RESULTADOS_BASELINE_4D3.csv).

## A01 — entidade (Gama) apenas na pergunta; nenhum trecho citado a menciona
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- **Resposta candidata:** As Deliberações devem nortear as gerências de regulação nos serviços do Gama.
- **Entidade / atributo:** Gama / COMPETENCIA — rótulos: sem rótulo (inciso IX, texto corrido)
- **Relação entidade–atributo:** não associada (Gama só na pergunta)
- **Classe:** `insuficiente_evidencia` | semântica: `nao_verificavel` | sustentação: `nao_sustenta_a_localizacao` | decisão ideal: `bloquear` | confiança: `alta`
  1. Afirmação avaliada: as deliberações norteiam gerências de regulação 'nos serviços do Gama'
  2. Trecho: IX (cita normas e protocolos de regulação; não menciona Gama)
  3. Entidade associada ao atributo: não: nada liga o inciso IX ao Gama
  4. Informação só da pergunta: sim: 'Gama' vem só da pergunta
  5. Por quê: o conteúdo vem do trecho, mas a localização 'no Gama' é eco da pergunta sem apoio; deveria ser bloqueada ou entregue sem a localização

## A02 — padrão val-087-A-r1: atributo do inciso IX (neutro) + entidade só num trecho de rótulo conflitante (Titular)
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- **Resposta candidata:** A Coordenação tem competência para nortear as gerências de regulação e implementar as normas e protocolos de regulação no Gama.
- **Entidade / atributo:** Gama / COMPETENCIA — rótulos: IX: sem rótulo; 4 - Titular: (MEMBRO, conflita com COMPETENCIA)
- **Relação entidade–atributo:** atributo e entidade em trechos diferentes; o trecho da entidade é de membros, não de competência
- **Classe:** `insuficiente_evidencia` | semântica: `nao_verificavel` | sustentação: `nao_sustenta_a_localizacao` | decisão ideal: `bloquear` | confiança: `media_alta`
  1. Afirmação avaliada: a competência de nortear/implementar normas existe 'no Gama'
  2. Trecho: IX sustenta o conteúdo; o único trecho com 'Gama' é a designação de titular do HRG
  3. Entidade associada ao atributo: não: Gama aparece só como cargo do titular, não como alcance da competência
  4. Informação só da pergunta: parcialmente: 'Gama' está na pergunta e no trecho de membro
  5. Por quê: o trecho que contém 'Gama' é de designação de membro e não sustenta competência; a localização é um eco da pergunta ancorado em citação de outro atributo

## A03 — entidade na pergunta e em trecho compatível (Compete)
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- **Resposta candidata:** Compete discutir e deliberar sobre os serviços regulados do Gama.
- **Entidade / atributo:** Gama / COMPETENCIA — rótulos: IV - Compete (COMPETENCIA, compatível)
- **Relação entidade–atributo:** associada explicitamente no mesmo trecho
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `alta`
  1. Afirmação avaliada: compete discutir e deliberar sobre serviços regulados do Gama
  2. Trecho: inciso IV: '...serviços regulados, inclusive os do Gama'
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: não: o Gama também está no trecho
  5. Por quê: paráfrase literal de trecho com rótulo compatível que cita a entidade

## A04 — entidade na pergunta e em dois trechos com relações diferentes (competência compatível + membro conflitante)
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- **Resposta candidata:** Compete discutir e deliberar sobre os serviços regulados do Gama.
- **Entidade / atributo:** Gama / COMPETENCIA — rótulos: IV - Compete (compatível); 4 - Titular (MEMBRO, conflitante)
- **Relação entidade–atributo:** o trecho compatível associa; o trecho de membro é acessório
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `alta`
  1. Afirmação avaliada: compete discutir e deliberar sobre os serviços regulados do Gama
  2. Trecho: inciso IV (compatível); o trecho de membros é citado mas não usado
  3. Entidade associada ao atributo: sim, pelo inciso IV
  4. Informação só da pergunta: não
  5. Por quê: o conteúdo vem integralmente de trecho compatível; a citação conflitante é supérflua e não deve bloquear

## A05 — resposta que só repete a pergunta, com trecho compatível citado
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- **Resposta candidata:** A Coordenação possui competências relacionadas aos serviços do Gama.
- **Entidade / atributo:** Gama / COMPETENCIA — rótulos: IV - Compete (compatível)
- **Relação entidade–atributo:** associada no trecho
- **Classe:** `correta_parcial` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `media`
  1. Afirmação avaliada: a Coordenação tem competências ligadas aos serviços do Gama
  2. Trecho: inciso IV
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: sim: a resposta é quase só eco da pergunta, porém o trecho a confirma
  5. Por quê: verdadeira e sustentada, mas não informa quais competências; parcial

## A06 — padrão E6: atributo de trecho compatível sem Gama + trecho de membro com Gama; resposta ecoa 'no Gama'
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- **Resposta candidata:** Compete discutir e deliberar sobre os serviços regulados no Gama.
- **Entidade / atributo:** Gama / COMPETENCIA — rótulos: IV - Compete (compatível, sem Gama); 4 - Titular (conflitante, com Gama)
- **Relação entidade–atributo:** competência regional; Gama só como cargo
- **Classe:** `ambiguo` | semântica: `nao_verificavel` | sustentação: `sustenta_o_conteudo_nao_a_localizacao` | decisão ideal: `indeterminado` | confiança: `baixa`
  1. Afirmação avaliada: a competência de discutir/deliberar alcança os serviços do Gama
  2. Trecho: inciso IV sustenta o conteúdo; 'Gama' só no trecho de membro
  3. Entidade associada ao atributo: parcial: depende de o Gama pertencer à Região Sul, que nenhum trecho afirma
  4. Informação só da pergunta: sim
  5. Por quê: duas leituras plausíveis: (a) eco legítimo da pergunta sobre competência regional; (b) localização não sustentada. Não forçado

## A07 — caso legítimo (mundo contratos): entidade (Planaltina) só na cláusula de Valor do mesmo extrato; resposta de Objeto repete a unidade da pergunta
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda para o Hospital Regional de Planaltina?
- **Resposta candidata:** O objeto é a manutenção preventiva de equipamentos de imagem, para o Hospital Regional de Planaltina.
- **Entidade / atributo:** Hospital Regional de Planaltina / OBJETO — rótulos: Objeto: (compatível); Valor: ... para o HRP (VALOR, conflitante)
- **Relação entidade–atributo:** mesmo extrato: a cláusula de Valor identifica a unidade do contrato; o Objeto é da mesma contratada
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `media_alta`
  1. Afirmação avaliada: o objeto do contrato da Alfa é a manutenção preventiva, para o HRP
  2. Trecho: chunk único: 'Objeto: manutenção preventiva ...' e 'Valor: R$ 80.000,00, para o Hospital Regional de Planaltina'
  3. Entidade associada ao atributo: sim, por pertencerem ao mesmo extrato
  4. Informação só da pergunta: o nome Planaltina também está no trecho
  5. Por quê: o extrato único liga contratada, objeto e unidade; citar a cláusula de Valor serve de âncora da unidade

## B01 — rótulo Titular citado e conteúdo exclusivo dele usado (padrão val-087-A-r2/r3)
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- **Resposta candidata:** A Coordenação tem competência para nortear as gerências e implementar as normas; o Diretor do HRG atua na regulação do Gama.
- **Entidade / atributo:** Gama / COMPETENCIA — rótulos: IX: sem rótulo; 4 - Titular (MEMBRO, conflitante)
- **Relação entidade–atributo:** membro do HRG apresentado como se fosse competência
- **Classe:** `incorreta` | semântica: `incorreta` | sustentação: `nao_sustenta` | decisão ideal: `bloquear` | confiança: `alta`
  1. Afirmação avaliada: o Diretor do HRG 'atua na regulação do Gama' (competência)
  2. Trecho: trecho de membros: designa o Diretor do HRG como titular, sem dizer que regula
  3. Entidade associada ao atributo: não
  4. Informação só da pergunta: o Gama está na pergunta; 'HRG' não
  5. Por quê: dado de membro tratado como competência; afirmação nova sem apoio

## B02 — rótulo Compete (compatível), pergunta sem entidade extra
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul?
- **Resposta candidata:** Compete discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados.
- **Entidade / atributo:** CRSSU / COMPETENCIA — rótulos: IV - Compete (compatível)
- **Relação entidade–atributo:** mesmo trecho
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `alta`
  1. Afirmação avaliada: competência de discutir e deliberar sobre direção/avaliação/monitoramento
  2. Trecho: inciso IV
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: não
  5. Por quê: cópia fiel de trecho com rótulo compatível

## B03 — trecho com rótulo desconhecido (texto corrido, art. 5º)
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul?
- **Resposta candidata:** Discute e delibera sobre os serviços regulados, em reuniões ordinárias mensais.
- **Entidade / atributo:** CRSSU / COMPETENCIA — rótulos: sem rótulo reconhecido
- **Relação entidade–atributo:** mesmo trecho; atributo inferido do verbo, não do rótulo
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `media`
  1. Afirmação avaliada: a Coordenação discute e delibera sobre serviços regulados, em reuniões mensais
  2. Trecho: art. 5º
  3. Entidade associada ao atributo: sim (verbos do próprio trecho)
  4. Informação só da pergunta: não
  5. Por quê: sem rótulo não há como confirmar a família do atributo, mas o conteúdo está literalmente no trecho

## B04 — rótulo conflitante (Titular) mas competência explícita no próprio trecho ('a quem compete')
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
- **Resposta candidata:** Compete ao Diretor do HRG deliberar sobre os serviços do Gama.
- **Entidade / atributo:** Gama / COMPETENCIA — rótulos: Titular (MEMBRO) com cue 'a quem compete'
- **Relação entidade–atributo:** associada no trecho: a competência é afirmada junto ao titular
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `media_alta`
  1. Afirmação avaliada: compete ao Diretor do HRG deliberar sobre os serviços regulados do Gama
  2. Trecho: mesmo trecho: 'a quem compete deliberar sobre os serviços regulados do Gama'
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: não: o Gama está no trecho
  5. Por quê: o rótulo conflita, mas há evidência positiva explícita da competência

## B05 — trecho conflitante citado, mas o conteúdo da resposta vem de trecho compatível
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul?
- **Resposta candidata:** Compete discutir e deliberar sobre a direção e o monitoramento dos serviços regulados.
- **Entidade / atributo:** CRSSU / COMPETENCIA — rótulos: IV - Compete (compatível); 4 - Titular (conflitante)
- **Relação entidade–atributo:** mesmo trecho compatível
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `alta`
  1. Afirmação avaliada: compete discutir e deliberar sobre direção e monitoramento
  2. Trecho: inciso IV
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: não
  5. Por quê: o trecho de membros é citado sem ser usado

## B06 — dois trechos conflitantes (GERSU e NOV) citados e usados numa resposta sobre competência
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul?
- **Resposta candidata:** As gerências de regulação seguem as normas; a GERSU e o NOV participam.
- **Entidade / atributo:** CRSSU / COMPETENCIA — rótulos: IX: sem rótulo; 6/7 - Titular (MEMBRO, conflitante)
- **Relação entidade–atributo:** membros apresentados como competência
- **Classe:** `incorreta` | semântica: `incorreta` | sustentação: `nao_sustenta` | decisão ideal: `bloquear` | confiança: `media_alta`
  1. Afirmação avaliada: a GERSU e o NOV 'participam' (como competência)
  2. Trecho: a designação de titulares não é competência nem participação nas normas
  3. Entidade associada ao atributo: não
  4. Informação só da pergunta: não
  5. Por quê: afirmação sobre membros respondendo a pergunta de competência

## B07 — dois trechos conflitantes para entidades diferentes (HRG e HRSM); resposta os mistura
- **Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul?
- **Resposta candidata:** Compete ao HRG e ao HRSM deliberar sobre os serviços regulados.
- **Entidade / atributo:** CRSSU / COMPETENCIA — rótulos: Titular HRG (conflitante); Titular HRSM (conflitante)
- **Relação entidade–atributo:** membros tratados como detentores de competência
- **Classe:** `incorreta` | semântica: `incorreta` | sustentação: `nao_sustenta` | decisão ideal: `bloquear` | confiança: `alta`
  1. Afirmação avaliada: compete ao HRG e ao HRSM deliberar
  2. Trecho: ambos os trechos apenas designam titulares
  3. Entidade associada ao atributo: não
  4. Informação só da pergunta: não
  5. Por quê: a competência não consta em nenhum trecho

## C01 — entidade e atributo no mesmo trecho
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O objeto é a manutenção preventiva de equipamentos de imagem.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: Objeto: (compatível)
- **Relação entidade–atributo:** mesmo trecho
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `alta`
  1. Afirmação avaliada: objeto = manutenção preventiva de equipamentos de imagem
  2. Trecho: extrato 12/2025
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: não
  5. Por quê: cópia do campo Objeto do extrato da Alfa

## C02 — entidade (Alfa) num trecho e atributo (Objeto) de OUTRA empresa em outro; ambos citados
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O objeto é a reforma da rede de gases medicinais.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: Valor (da Alfa); Objeto: (da Beta, compatível com o atributo)
- **Relação entidade–atributo:** atributo pertence à Beta, entidade citada é a Alfa
- **Classe:** `incorreta` | semântica: `incorreta` | sustentação: `nao_sustenta` | decisão ideal: `bloquear` | confiança: `alta`
  1. Afirmação avaliada: o objeto do contrato da Alfa é a reforma de gases
  2. Trecho: extrato 13/2025 (Beta) traz esse objeto; extrato 12/2025 (Alfa) não
  3. Entidade associada ao atributo: não: atributo associado à Beta
  4. Informação só da pergunta: o nome Alfa vem da pergunta e consta num trecho citado
  5. Por quê: combinação de entidade de um trecho com atributo de outro; resposta falsa

## C03 — dois contratos no contexto; resposta usa apenas o da entidade correta
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O objeto é a manutenção preventiva de equipamentos de imagem.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: Objeto (Alfa); Objeto (Beta)
- **Relação entidade–atributo:** atributo da Alfa associado explicitamente; trecho da Beta é distrator
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `alta`
  1. Afirmação avaliada: objeto da Alfa
  2. Trecho: extrato 12/2025
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: não
  5. Por quê: conteúdo vem do trecho da entidade correta; o outro trecho é ruído citado

## C04 — atributo associado a entidade diferente; só o trecho da Beta é citado
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O objeto é a reforma da rede de gases medicinais.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: Objeto (Beta)
- **Relação entidade–atributo:** atributo pertence à Beta; a Alfa não consta no trecho
- **Classe:** `incorreta` | semântica: `incorreta` | sustentação: `nao_sustenta` | decisão ideal: `bloquear` | confiança: `alta`
  1. Afirmação avaliada: objeto da Alfa = reforma de gases
  2. Trecho: extrato 13/2025 da Beta
  3. Entidade associada ao atributo: não
  4. Informação só da pergunta: não
  5. Por quê: a entidade da pergunta não está na evidência

## C05 — duas entidades, mesmo atributo
- **Pergunta:** Qual o objeto dos contratos nº 12/2025 e nº 13/2025 das empresas Alfa Serviços Ltda e Beta Engenharia Ltda?
- **Resposta candidata:** Alfa Serviços: manutenção preventiva de equipamentos de imagem; Beta Engenharia: reforma da rede de gases medicinais.
- **Entidade / atributo:** Alfa e Beta / OBJETO — rótulos: Objeto (Alfa); Objeto (Beta)
- **Relação entidade–atributo:** cada entidade com seu atributo
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `alta`
  1. Afirmação avaliada: objeto de cada contrato
  2. Trecho: extratos 12 e 13/2025
  3. Entidade associada ao atributo: sim, ambas
  4. Informação só da pergunta: os nomes também estão nos trechos
  5. Por quê: cada entidade associada ao seu objeto

## C06 — duas entidades, atributos diferentes (objeto da Alfa, valor da Beta)
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda e o valor do contrato nº 13/2025 da empresa Beta Engenharia Ltda?
- **Resposta candidata:** Alfa Serviços: manutenção preventiva de equipamentos de imagem; Beta Engenharia: R$ 150.000,00.
- **Entidade / atributo:** Alfa e Beta / OBJETO+VALOR — rótulos: Objeto (Alfa); Objeto e Valor (Beta; o span citado contém ambos)
- **Relação entidade–atributo:** pergunta composta; cada entidade com o atributo pedido
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `media`
  1. Afirmação avaliada: objeto da Alfa e valor da Beta
  2. Trecho: extratos 12 e 13/2025
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: não
  5. Por quê: a pergunta pede atributos distintos para entidades distintas (limitação: o mecanismo trata um atributo por pergunta)

## C07 — relação ambígua: aditivo cita as duas empresas; pergunta é sobre 'contrato'
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O objeto do contrato da Alfa é a prorrogação da vigência por mais 12 meses.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: Objeto: (compatível)
- **Relação entidade–atributo:** termo aditivo, não contrato; duas partes
- **Classe:** `ambiguo` | semântica: `nao_verificavel` | sustentação: `sustenta_literalmente` | decisão ideal: `indeterminado` | confiança: `baixa`
  1. Afirmação avaliada: o objeto do contrato da Alfa é a prorrogação
  2. Trecho: termo aditivo 5/2025 (Alfa e Beta)
  3. Entidade associada ao atributo: ambígua: o objeto é do aditivo, não do contrato
  4. Informação só da pergunta: não
  5. Por quê: duas leituras plausíveis (o aditivo é a resposta útil vs o objeto do contrato não foi informado)

## D01 — resposta que apenas repete a pergunta
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O contrato da empresa Alfa Serviços Ltda tem um objeto descrito no extrato.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: sem rótulo
- **Relação entidade–atributo:** apenas a entidade citada
- **Classe:** `correta_parcial` | semântica: `correta` | sustentação: `sustenta_trivialmente` | decisão ideal: `indeterminado` | confiança: `baixa`
  1. Afirmação avaliada: o contrato da Alfa tem um objeto descrito
  2. Trecho: extrato 12/2025
  3. Entidade associada ao atributo: sim (trivial)
  4. Informação só da pergunta: sim: eco da pergunta
  5. Por quê: verdadeira mas não responde; um sistema fail-closed poderia tratá-la como insuficiente

## D02 — acrescenta localização não sustentada (ausente da pergunta)
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O objeto é a manutenção preventiva de equipamentos de imagem no Hospital Regional de Planaltina.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: Objeto: (compatível)
- **Relação entidade–atributo:** entidade Alfa associada; localização nova
- **Classe:** `incorreta` | semântica: `nao_verificavel` | sustentação: `nao_sustenta_a_localizacao` | decisão ideal: `bloquear` | confiança: `alta`
  1. Afirmação avaliada: a manutenção ocorre no HRP
  2. Trecho: nenhum trecho cita Planaltina
  3. Entidade associada ao atributo: a localização não é associada
  4. Informação só da pergunta: não: Planaltina é nova
  5. Por quê: afirmação nova não sustentada

## D03 — localização na pergunta, ausente em toda a evidência
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda no Hospital Regional de Planaltina?
- **Resposta candidata:** O objeto é a manutenção preventiva de equipamentos de imagem no Hospital Regional de Planaltina.
- **Entidade / atributo:** Hospital Regional de Planaltina / OBJETO — rótulos: Objeto: (compatível)
- **Relação entidade–atributo:** localização não associada
- **Classe:** `insuficiente_evidencia` | semântica: `nao_verificavel` | sustentação: `nao_sustenta_a_localizacao` | decisão ideal: `bloquear` | confiança: `alta`
  1. Afirmação avaliada: o objeto vale para o HRP
  2. Trecho: extrato 12/2025 sem menção ao HRP
  3. Entidade associada ao atributo: não
  4. Informação só da pergunta: sim: eco da pergunta sem apoio
  5. Por quê: eco de entidade da pergunta que a evidência não traz

## D04 — acrescenta entidade não sustentada
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O objeto é a manutenção preventiva de equipamentos de imagem, contratada pela Secretaria de Obras.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: Objeto: (compatível)
- **Relação entidade–atributo:** entidade extra sem apoio
- **Classe:** `incorreta` | semântica: `nao_verificavel` | sustentação: `nao_sustenta` | decisão ideal: `bloquear` | confiança: `alta`
  1. Afirmação avaliada: contratante = Secretaria de Obras
  2. Trecho: nenhum trecho cita contratante
  3. Entidade associada ao atributo: não
  4. Informação só da pergunta: não
  5. Por quê: entidade inventada

## D05 — fato sustentado + número inventado
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O objeto é a manutenção preventiva de equipamentos de imagem, no valor de R$ 90.000,00.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: Objeto: (compatível)
- **Relação entidade–atributo:** valor contradiz o trecho (R$ 80.000,00)
- **Classe:** `incorreta` | semântica: `incorreta` | sustentação: `contradiz` | decisão ideal: `bloquear` | confiança: `alta`
  1. Afirmação avaliada: valor de R$ 90.000,00
  2. Trecho: o extrato traz R$ 80.000,00
  3. Entidade associada ao atributo: não
  4. Informação só da pergunta: não
  5. Por quê: número divergente do trecho

## D06 — correta com paráfrase
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** A empresa Alfa Serviços foi contratada para realizar a manutenção preventiva dos equipamentos de imagem.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: Objeto: (compatível)
- **Relação entidade–atributo:** mesmo trecho
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `alta`
  1. Afirmação avaliada: Alfa contratada para manutenção preventiva de equipamentos de imagem
  2. Trecho: extrato 12/2025
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: não
  5. Por quê: paráfrase fiel

## D07 — parcialmente correta: responde só o objeto numa pergunta de objeto e valor
- **Pergunta:** Qual o objeto e o valor do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O objeto é a manutenção preventiva de equipamentos de imagem.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO+VALOR — rótulos: Objeto: (compatível)
- **Relação entidade–atributo:** mesmo trecho
- **Classe:** `correta_parcial` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `alta`
  1. Afirmação avaliada: objeto do contrato
  2. Trecho: extrato 12/2025
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: não
  5. Por quê: omite o valor, que está no trecho; parcial

## D08 — resposta curta
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** Manutenção preventiva de equipamentos de imagem.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: Objeto: (compatível)
- **Relação entidade–atributo:** mesmo trecho
- **Classe:** `correta` | semântica: `correta` | sustentação: `sustenta` | decisão ideal: `entregar` | confiança: `alta`
  1. Afirmação avaliada: objeto
  2. Trecho: extrato 12/2025
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: não
  5. Por quê: trecho literal sem sujeito explícito

## D09 — resposta genérica sem conteúdo
- **Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda?
- **Resposta candidata:** O contrato trata de serviços prestados pela empresa.
- **Entidade / atributo:** Alfa Serviços Ltda / OBJETO — rótulos: sem rótulo
- **Relação entidade–atributo:** apenas a entidade
- **Classe:** `insuficiente_evidencia` | semântica: `correta` | sustentação: `sustenta_trivialmente` | decisão ideal: `bloquear` | confiança: `media`
  1. Afirmação avaliada: o contrato trata de serviços
  2. Trecho: extrato 12/2025
  3. Entidade associada ao atributo: sim
  4. Informação só da pergunta: sim: tudo é eco da pergunta
  5. Por quê: não informa o objeto; deveria ser tratada como não respondida
