# Casos reais — Fase 4D.4

Somente documentos, chunks e saídas **já existentes** (corpus de 1.381 documentos, rodada 4.3 com 150 perguntas, validação seletiva de 21 gerações, auditoria 4.3 do projeto). Nenhuma pergunta ou relação foi inventada; nenhuma geração foi feita. Rótulos de classe vêm da **auditoria 4.3 do projeto**, que **não é uma revisão humana independente**. "Candidata atual" = `fail-closed-4.4.4d1-cand`, em replay offline das saídas brutas gravadas. Resultados por caso e por variante: `MATRIZ_AVALIACAO_4D4.csv`; scripts e saídas de apoio: `diagnostico_real_4d4.py`, `real_4d4.json`.

Legenda da relação entidade–atributo: **explícita** (no mesmo trecho), **implícita** (inferível só por outro ponto do documento/chunk), **conflitante**, **não verificável**.

## Cobertura das categorias pedidas

| Categoria | Casos reais encontrados |
|---|---|
| Titularidade × competência | val-087 (A-r1, A-r2, A-r3) |
| Entidade e atributo em trechos separados | val-087-A-r1; val-031 |
| Competência explícita em texto com rótulo conflitante | **nenhum caso real** (ver R-13) |
| Localização herdada da pergunta | val-024, val-020, val-087-A-r1, val-130 |
| Atributo associado a destinatário diferente | val-083 |
| Conflito entre duas publicações | val-001 (ambiguidade real entre docs 349 e 719) |
| Resposta correta que combina pergunta e documento | val-006, val-041 |

## R-01 val-087 (21 gerações, flag desligada = braço A; ligada = braço B)
1. **Pergunta:** "Quais são as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?"
2. **Respostas existentes.** Gabarito do dataset: "…compete à CRSSU discutir e deliberar sobre a direção, avaliação, monitoramento, organização, funcionamento e aperfeiçoamento dos serviços regulados na Região de Saúde Sul, **incluindo o Gama**…". A-r1 (entregue como `parcial`): "…competência para nortear as gerências de regulação, incluindo a implementação das normas e protocolos de regulação de internação hospitalar **no Gama**." A-r2/A-r3: abstenção por rótulo incompatível ("trata de outro atributo ('titular')"). B-r1/B-r2/B-r3: competências do inciso IV e inciso IX, sem mencionar o Gama.
3. **Documentos/chunks:** doc 174 (duplicata do doc 180), Ordem de Serviço (ed. 26/2025). Contexto de A-r1: C1 = chunk `dodf-174:est300o30:0004` (inciso IX, e também inciso XI), C2 = chunk `…0001` (`4 - Titular: Diretor do Hospital Regional do Gama, da Diretoria do Hospital Regional do Gama (HRG)`), C3 = chunk `…0000` (Art. 1º). Nos braços B o contexto traz o inciso IV.
4. **Entidade/atributo:** Gama (e CRSSU) / COMPETENCIA.
5. **Relação:** o texto do inciso IV diz "no âmbito de toda a Região de Saúde Sul", **sem citar o Gama**; o Gama aparece (a) como cargo de titular em C2 (item de membros, **rótulo conflitante**), (b) no inciso XI, que trata da manifestação dos presidentes dos Conselhos de Saúde do Gama e de Santa Maria nas Deliberações. Para A-r1, a relação entre "competência" e "Gama" é **implícita no melhor caso e conflitante/não verificável no trecho citado para a localização**; o gabarito do dataset a trata como incluída.
6. **Limitações do contexto:** o orçamento de 3.000 tokens e o retrieval BM25 decidem se o inciso IV chega ao modelo; em A-r1 ele não chegou ao contexto (chunks 0004, 0001 e 0000). **Fato relevante para a hipótese de vínculo:** o chunk C1 de A-r1 **contém "Gama" (inciso XI)**, em frase diferente do trecho citado (inciso IX).

## R-02 val-024 — localização herdada entregue
Pergunta: "Qual foi a modificação contratual realizada para equipamentos de radiologia no Hospital Regional de Ceilândia?" Resposta existente: "…supressão de 5 (cinco) equipamentos de Raio X Panorâmico, resultando na redução do valor total do contrato" (`respondida`; o gabarito acrescenta "localizados no Hospital Regional de Ceilândia"). Fonte: doc 718 (Extrato de Primeiro Termo Aditivo ao Contrato 051462/2024, ed. 97), cujo texto lista "HRAN, CRT, CEO UBS 11 - CEILÂNDIA, HRS, HRL" e **não cita o HRC** (auditoria 4.3). Entidade/atributo: Hospital Regional de Ceilândia / modificação contratual. Relação: **implícita/ausente** (a unidade da pergunta não está no texto). Limitação: a auditoria considera o fato central correto e a atribuição ao HRC não sustentada, e o próprio gabarito a repete.

## R-03 val-020 — "no Gama" fora do chunk citado
Pergunta: "Quais estabelecimentos de saúde foram credenciados para prestar serviços de radiologia e medicina nuclear no Gama?" Resposta (`parcial`): o Instituto de Medicina Nuclear e Endocrinologia de Brasília Ltda (CNPJ 24.942.732/0001-69). Fonte: doc 361, Edital 3/2024 (ed. 51), chunk `dodf-361:est300o30:0001`, **sem "Gama"**; segundo a auditoria 4.3 o Gama é endereço de uma **filial** no documento. Os chunks C2/C3 (docs 1009 e 1054) mencionam Gama, mas não são o citado. Relação: **implícita** (localidade em outro ponto do mesmo documento). Auditoria 4.3: "Correta, mas parcial".

## R-04 val-031 — entidade em chunk vizinho do mesmo documento
Pergunta sobre indicadores de satisfação no "Hospital da Criança de Brasília José Alencar" no terceiro trimestre de 2023. Citação: C2 (doc 1464, chunk com "Satisfação dos Pacientes — … julho 94,2%, agosto 96,6%, setembro 97,6%"); o nome do hospital está em outro chunk do mesmo documento (C1). Rodada original: `insuficiente` por `valores_nao_sustentados:2023`, classificada na auditoria 4.3 como **abstenção indevida** (falso positivo de verificação); a candidata atual entrega `parcial`. Relação: **explícita no documento**, entidade no chunk não citado.

## R-05 val-130 — atributo/localidade de outra região
Pergunta: empresas credenciadas na **Asa Sul**. Resposta da rodada original (`parcial`): Biosphere Health Center e Visão Hospital de Olhos. A citação de Biosphere é "Filial (3): ST SHL/NORTE … ED. Biosphere Health Center – **Asa Norte**" (doc 6), isto é, outra localidade; Visão Hospital de Olhos (doc 920) está na Asa Sul. Auditoria 4.3: "Incorreta". A candidata atual bloqueia (`localidade_conflitante_no_registro`, mecanismo A_LOC). Relação: **conflitante** para Biosphere. É um exemplo real de localização da pergunta aplicada a evidência de outra localidade, resolvido por mecanismo diferente do B.

## R-06 val-149 — publicação sem vínculo com a localidade
Pergunta sobre ações de atenção primária em **Ceilândia** em 2025. Resposta original `parcial`, genérica (doc 1611, texto do INAS, sem citar Ceilândia). Auditoria 4.3: "Incorreta"; candidata atual bloqueia (`publicacao_sem_vinculo_com_a_localidade`). Relação: **não verificável/ausente**.

## R-07 val-083 — destinatário diferente
Pergunta: itens adquiridos para "Atenção Primária no Guará". O chunk de ratificações mistura itens com destinatário "Atenção Primária" e itens com destinatário "Hospital Regional do Guará"; o mecanismo A_DEST marca estes últimos como `conflitante`, e a candidata atual abstém (`destinatario_conflitante`). O gabarito do dataset trata os itens do Hospital Regional do Guará como parte da resposta; a auditoria 4.3 classifica a abstenção como indevida. Relação: **conflitante segundo o mecanismo; divergência com o gabarito**. Não é mecanismo B.

## R-08 val-001 — conflito entre duas publicações
Pergunta: "Qual serviço de manutenção foi contratado para a Policlínica do Núcleo Bandeirante?". Há ao menos duas publicações (doc 349, ed. 48, e doc 719, ed. 97), cada uma sobre uma autoclave diferente (auditoria 4.3). Candidata atual: `ambigua`. Classe 4.3: "Ambígua de fato". Relação: **conflito entre publicações** (resposta correta = abstenção/esclarecimento).

## R-09 val-006 e R-10 val-041 — respostas corretas que combinam pergunta e documento
val-006 ("serviço de alimentação hospitalar … em Ceilândia"): resposta `respondida` com o objeto do Contrato 1025/2024 (doc 28); "Ceilândia" não está no span citado, mas o documento trata das UPAs 24H de Ceilândia (auditoria 4.3: "Correta"). val-041 ("instituição de saúde em Ceilândia … crédito descentralizado"): "Hospital das Clínicas e Pronto Socorro de Fraturas de **Ceilândia** Ltda", nome já contendo a localidade (docs 468/469/398; 4.3: "Correta"). Relação: implícita (val-006) e explícita (val-041). Servem de controles de recall.

## R-11 Entregas reais com nome da pergunta ausente do span citado
Entre as 30 respostas entregues na replay dos 150, 12 repetem um nome saliente da pergunta que **não consta do span citado** (val-003, 006, 012, 020, 021, 049, 059, 090, 099, 111, 114, 143); 11 delas são "Correta" (4) ou "Correta, mas parcial" (7) e 1 (val-012) "Incorreta" na auditoria 4.3. Isso mostra que o eco de nome da pergunta é **frequente nas entregas reais e, na maioria, não corresponde a erro** — contrasta com a premissa do cenário sintético A02. (Contagem direta no span citado; não verifiquei caso a caso se o nome está no chunk.)

## R-12 Impacto offline das variantes nos dados reais
- **B1 e B2:** nenhuma mudança nos 150; nos 21, só val-087-A-r1 passa a bloquear.
- **C simplificada (nome da pergunta repetido na resposta deve constar no chunk de citação não conflitante; definição da 4D.3):** nos 150, bloqueia val-020 e val-031 (ambos plausivelmente corretos); nos 21, **não bloqueia val-087-A-r1** (o chunk C1 contém "Gama"). Resultado idêntico quando "conflito" é definido por `causas_do_conflito` em vez de `estado`.
- Capturas de erros reais pela C: **0**; por B1/B2: **1** (val-087-A-r1). Entregas reais removidas: C **2/30**; B1/B2 **0/30** nos 150.

## R-13 Competência explícita em texto com rótulo conflitante: não encontrado
Varredura do corpus: 13 documentos contêm "Titular"; itens do tipo "N - Titular:" aparecem apenas nos docs 174/180 (duplicatas, 12 itens únicos), nenhum com atribuição de competência dentro do próprio item. Dois acertos do detector de "cue" resultaram de captura excessiva do meu regex (invadiu o "Art. 3º" seguinte), não de item real. **Não há caso real análogo a B04.** B04 existe só como caso sintético.

## Limites
Poucos positivos reais (1: val-087-A-r1); gabaritos do dataset e auditoria 4.3 não são revisão humana independente; contexto efetivo reconstruído por replay offline, não por nova geração; não foi verificado caso a caso se os nomes de R-11 estão no chunk.
