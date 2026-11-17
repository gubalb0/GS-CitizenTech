# Auditoria independente das 21 gerações (Fase 4C) — somente leitura

Nenhum arquivo técnico, prompt, retriever, índice, manifesto, snapshot ou resultado foi alterado; nenhuma geração, flag ou integração com o Zelo. Arquivos auxiliares: apenas em diretório temporário da sessão (embaralhamento, mapa e avaliação independente); nenhum arquivo novo no projeto além deste relatório.

## 1. Integridade dos dados

- Dois JSONL localizados por inspeção do diretório: `validacao_seletiva_20261116-155046.jsonl` (ordens 1–7, SHA `cbb8482916d55050`) e `validacao_seletiva_retomada_20261116-161042.jsonl` (ordens 8–21, SHA `c198f0893d40121f`). Existem também três `.resumo.json` de retomada (duas paradas sem geração e a execução completa).
- Combinados: **21 registros, 21 `run_id` únicos, ordens 1–21 sem lacuna, 7 slots × 3 repetições**; hash de contexto, de parâmetros e lista de chunks de cada registro = manifesto (SHA `43fb09685404714c`); `verificar_hashes.py` → TODOS CONFEREM; `geracao.py`/`evidencias.py`/`catalogo.py` com os hashes registrados.
- Os contextos foram **reconstruídos** a partir do índice (somente leitura) e o hash do conteúdo enviado ao modelo bateu com o do registro em todos os 7 contextos distintos — as avaliações abaixo usam o texto efetivamente enviado.
- Limitação: o LM Studio não gravou o prompt bruto; a reconstrução é determinística (mesmo código, hash idêntico), não uma captura da requisição.

## 2. Metodologia

1. As 21 saídas foram embaralhadas com **semente nova** em códigos Q01–Q21, sem condição, slot, ordem ou resultado esperado; cada saída ficou associada apenas ao contexto de origem (X1–X7, textos integrais dos chunks).
2. Cada resposta foi avaliada contra o texto dos chunks (não contra o status do pipeline) nas 10 dimensões pedidas; a citação foi conferida por **busca literal programática** (após normalizar espaços) dentro do chunk indicado.
3. A avaliação independente foi **gravada antes de abrir o mapeamento** (temp); só então as condições A/B foram reveladas.
4. Classes: Correta · Correta, mas parcial · Incorreta · Não verificável com as evidências disponíveis (usada para abstenções em que o contexto não contém a evidência — não equivale a "abstenção correta/indevida", que é julgamento sobre o corpus).

**Vieses e limites da própria auditoria:** o mesmo agente (modelo) conduziu a execução, a avaliação cega da fase anterior e esta auditoria, e já conhecia o experimento; o cegamento é procedimental, não pleno. Reclassifiquei sem reaproveitar as classes anteriores e **discordei de duas** (§3). Recomenda-se revisão humana das 21 saídas. Os contextos revelam inevitavelmente a pergunta, e o chunk `dodf-28:0000` denuncia a condição B.

## 3. Resultado individual das 21 respostas (após a revelação)

Citações: **todas literais** nos chunks indicados (13/13 saídas com citação; 8 abstenções sem citação).

| Execução | Cod. | Classe independente | Pipeline | Evidência / observação |
|---|---|---|---|---|
| val-074-A-r1 | Q10 | Não verificável | fora_do_escopo (`abstencao_sem_justificativa`) | contexto sem o objeto; motivo declarado ("não relacionada") impreciso |
| val-074-A-r2 | Q04 | Não verificável | fora_do_escopo | idem |
| val-074-A-r3 | Q05 | Não verificável | fora_do_escopo | idem |
| val-074-B-r1 | Q17 | **Correta** | **ambigua** | `Objeto: FORNECIMENTO ININTERRUPTO…` literal em `dodf-28:0000`; UPA 24H SAMAMBAIA listada |
| val-074-B-r2 | Q15 | **Correta** | ambigua | idem |
| val-074-B-r3 | Q07 | **Correta** | ambigua | idem |
| val-087-A-r1 | Q09 | **Incorreta** | **parcial (entregue)** | só o item IX ("Deliberações deverão nortear as gerências…"); localiza "no Gama" sem suporte; C2 = `4 - Titular: …HRG` (membro) |
| val-087-A-r2 | Q01 | Incorreta | insuficiente (`rotulo_incompativel_com_atributo`) | idem; HRG como local da implementação |
| val-087-A-r3 | Q21 | Incorreta | insuficiente (`rotulo_incompativel_com_atributo`) | idem |
| val-087-B-r1 | Q13 | Correta, mas parcial | parcial | item IV literal + "nortear gerências" (IX) sustentado; não liga ao Gama |
| val-087-B-r2 | Q03 | Correta, mas parcial | parcial | IV literal; "bem como a implementação das normas e protocolos" mistura IV (orientar) e IX (gerências implementam) |
| val-087-B-r3 | Q14 | Correta, mas parcial | parcial | idem Q13 |
| val-006-C-r1/r2/r3 | Q12/Q08/Q19 | Correta ×3 | respondida ×3 | serviço = fornecimento ininterrupto de alimentação hospitalar; UPA Ceilândia I e II no trecho |
| val-024-C-r1/r2/r3 | Q02/Q16/Q18 | **Correta, mas parcial ×3, com ressalva de atribuição** | respondida ×3 | contrato 051462/2024 e supressão de 5 equipamentos confere; **"Hospital Regional de Ceilândia" não consta do trecho** (locais: HRAN, CRT, CEO UBS 11 – Ceilândia, HRS, HRL); omite valores |
| val-025-C-r1/r2/r3 | Q06/Q11/Q20 | Não verificável ×3 | fora_do_escopo ×3 | contexto = 3 chunks do mesmo edital de ensino médio; abstenção adequada; pergunta subespecificada |

**Divergências em relação à avaliação anterior (fase 4B):** (i) val-087-B passou de "Correta" para "Correta, mas parcial" (a pergunta é "em relação aos serviços do Gama" e nenhuma resposta liga a competência ao Gama; Q03 ainda mistura IV e IX); (ii) val-024-C: antes "Correta, mas parcial" sem ressalva, agora com a ressalva de que a atribuição ao Hospital Regional de Ceilândia não é sustentada. A classe das abstenções passou de "Abstenção indevida/correta" para "Não verificável", por ser julgamento sobre o contexto.

## 4. Comparação A × B (independente)

| Caso | A (baseline) | B (S1 conservadora) |
|---|---|---|
| val-074 | 0/3 respostas; 3 abstenções (Não verificável) | **3/3 Corretas** (saída bruta) |
| val-087 | **0/3 corretas** (3 Incorretas) | **3/3 Corretas, mas parciais** |
| Entregue ao usuário (pipeline) val-074 | 0/3 (fora_do_escopo) | **0/3** (ambigua) |
| Entregue ao usuário val-087 | 1/3 (**incorreta**) + 2 bloqueios corretos | 3/3 (parciais, adequadas) |

- **Respostas corretas bloqueadas pelo pipeline (falsos bloqueios): 3** — val-074-B ×3.
- **Respostas incorretas entregues (falsas liberações): 1** — val-087-A-r1; mais **3 entregues com ressalva de atribuição** — val-024-C ×3 (controle).
- **Bloqueios corretos: 2** — val-087-A-r2/r3.
- O ganho da S1 conservadora é real no nível do contexto/saída bruta (6/6 B adequadas vs 0/6 A), mas ainda **não chega ao usuário** em val-074.

## 5. Controles

Variação entre repetições: **nenhuma factual**; val-006 e val-024 idênticos em conteúdo (diferenças de uma palavra em val-024: "redução do valor total do contrato" vs "…contratual"); citações idênticas e literais; sem afirmações sem suporte além da atribuição de val-024; sem abstenções indevidas em val-006/024; abstenção de val-025 estável. **O verificador comportou-se de forma idêntica nas 3 repetições de cada controle.** val-024 merece atenção: o status `respondida` está correto quanto ao contrato, mas a associação ao Hospital Regional de Ceilândia não é demonstrada (item P3).

## 6. val-074 em detalhe

- **A frase aparece literalmente?** Sim: `dodf-28:0000`, "Objeto: FORNECIMENTO ININTERRUPTO DE ALIMENTAÇÃO HOSPITALAR ESPECIALMENTE PREPARADA PARA PACIENTES, RESPECTIVOS ACOMPANHANTES … DAS UNIDADE DE SAÚDE DO IGESDF – … 13 (TREZE) UNIDADES DE PRONTO ATENDIMENTO (UPA 24H – … SAMAMBAIA …)". Citações das 3 respostas B conferem literalmente.
- **Publicação/entidade corretas?** Extrato do Contrato nº 1025/2024 (DODF ed. 5, 08/01/2025), IGESDF × Máxima Facility, vigência até 30/07/2025; a UPA 24H Samambaia é uma das 13 unidades. A resposta B é fiel. Omissões menores (empresa, valor, vigência) não alteram o atributo pedido.
- **Concorrência real?** **Não.** Termos da pergunta (7): samambaia, objeto, fornecimento, alimentacao, hospitalar, unidades, atendem. Termos presentes no documento (melhor janela de 1.500 caracteres):

| Doc | Termos presentes | Janela | Contém "alimentação"? |
|---|---|---:|---|
| 28 (citado) | samambaia, objeto, fornecimento, **alimentacao**, hospitalar, unidades | 6 | sim |
| 473 (Extrato 03/2025) | samambaia, objeto, fornecimento, hospitalar, unidades, atendem | 6 | **não** |
| 877 (Extrato 06/2025) | idem | 6 | **não** |
| 1722 (Extrato 11/2025) | idem | 6 | **não** |
| 596 (Extrato 00078353/2025) | objeto, fornecimento, alimentacao, hospitalar, unidades, atendem | 6 | só "fonte de alimentação" de balança (sentido distinto) |

  Os três primeiros são dispensas de licitação para **itens de compra** (dexametasona, compressas, touca…) do Hospital Regional de Samambaia; nenhuma trata de alimentação hospitalar. Apenas o doc 28 contém "fornecimento ininterrupto de alimentação" (verificado em todo o catálogo). `concorrentes` estritos = 0 (`n_concorrentes: 0`, `tem_discriminador_lexical: False`).
- **Regra que produz o bloqueio:** `geracao._identificabilidade` (`geracao.py:908–933`) une `Catalogo.concorrentes` (`catalogo.py:171–189`, vazio aqui) a `Catalogo.relevantes` (`catalogo.py:147–169`): é "relevante" todo documento cuja melhor janela de 1.500 caracteres (`melhor_janela`, `catalogo.py:122–143`) cubra ≥ `max(MIN_TERMOS=3, ceil(piso·melhor_citada))` termos distintos (piso 1,0). Todos os termos pesam igual. A cobertura de 6/7 se obtém por palavras genéricas ("objeto", "fornecimento", "hospitalar", "unidades", "atendem") + a localidade; **o único termo discriminante ("alimentação") vale 1/7**. As publicações listadas na mensagem de ambiguidade são "relevantes" por similaridade textual, não por competirem pela resposta.
- **Bloqueio correto ou excessivo?** **Excessivamente conservador (falso bloqueio)** nesta evidência: a publicação pedida está identificada de forma única por conteúdo; o bloqueio contradiz o objetivo da regra (identificar *qual publicação responde*). A ambiguidade genuína exigiria outra publicação que também descreva fornecimento de alimentação hospitalar (nenhuma existe no corpus nessa janela).
- **O que resolveria com segurança** (sem implementar): (1) peso/discriminância dos termos (um termo de conteúdo raro no corpus, como "alimentação", precisa estar presente na publicação concorrente para ela ser considerada relevante); (2) exigir que o concorrente cubra o **predicado/atributo** da pergunta (objeto + "alimentação") e não só a janela de palavras; (3) dar peso à evidência literal citada (a resposta do modelo, "fornecimento ininterrupto de alimentação…", só ocorre no doc 28 — `_contem_afirmacao` já existe mas só serve para classificar concordantes, não para descartar relevantes sem o termo); (4) não contar verbos/palavras de ligação ("atendem") como termo de conteúdo.
- **Escala do problema:** na rodada 4.3, 10 respostas foram convertidas por "publicação não identificável"; **só 2** (val-054, val-082) por força exclusiva da regra de janela (`n_concorrentes=0`, `n_relevantes_janela>0`), uma delas classificada "Abstenção indevida" pela auditoria 4.3. Com a S1, val-074 vira um terceiro caso. Base pequena: não permite estimar o efeito de uma correção sobre o conjunto.
- **Observação sobre gabarito:** o benchmark registra `multi=True` e 4 fontes esperadas para val-074 (docs 28, 42, 51, 62); os docs 42, 51 e 62 (instrução normativa de Comunicação, aditivo BetaniaMed, dispensa SRSSO) **não contêm** "alimenta*"; apenas o doc 28 sustenta o objeto. Não foi possível confirmar a origem das demais; recomenda-se revisão do gabarito (não alterado aqui).

## 7. val-087 em detalhe

- **B cita a competência literalmente?** Sim: C2 = `IV - Compete à CRSSU discutir e deliberar sobre a direção, avaliação, monitoramento, organização, funcionamento e aperfeiçoamento dos serviços regulados na Região de Saúde Sul, …` (`dodf-174:0003`); atribuída à CRSSU (Coordenação de Regulação da Região de Saúde Sul), entidade correta; responde ao atributo (competência). Q03 acrescenta "bem como a implementação das normas e protocolos de regulação", que combina IV ("orientando a forma de implementação dos protocolos") e IX (as **gerências** implementam): imprecisão leve.
- **Escopo "Gama":** nenhuma resposta B conecta a competência ao Gama (as respostas reconhecem na justificativa "não especificam detalhes exclusivos ao Gama"); o texto só fala em Região de Saúde Sul. Por isso "Correta, mas parcial".
- **`parcial` do pipeline é adequado?** Em B, coincide com a classe, **mas por outra razão**: `parcial` é rótulo estrutural de pergunta de lista ("Quais são as competências…" → `eh_lista`; `completude: lista_nao_exaustiva`, aviso "baseada apenas nas 1 publicação(ões)"); não mede correção. O mesmo rótulo foi aplicado à resposta **incorreta** de A-r1.
- **A-r1 entregue como `parcial`: causa exata.** As três repetições de A produziram a mesma estrutura (item IX + `Titular: Diretor do Hospital Regional do Gama` como evidência de competência). Em r2 e r3 a citação foi `Titular: Diretor do HRG…` → `rotulo_do_valor` identificou o rótulo `titular` (família MEMBRO) → `rotulo_incompativel_com_atributo` (M2). Em r1 a citação foi **`4 - Titular: Diretor do HRG…`** (com o índice da lista): `EV.rotulo_do_valor` (`evidencias.py`) só reconhece o prefixo `rotulo:` quando o valor começa por letra (regex `^\s*([a-z][a-z ]{1,38}?)\s*:`) e a busca do rótulo *antes* do valor encontra "…Suplente: Substituto legal do cargo; " (sem rótulo conhecido). Resultado: `estado = desconhecido`, `rotulo = None`, `causas = []`, `bloqueia = False`. Reproduzido isoladamente: o mesmo trecho dá `None` com o prefixo "4 - " e `{rotulo: titular, família: MEMBRO}` sem ele.
- **Confusão membros × competência?** O verificador **não confundiu** nada em r1: **não identificou** o rótulo, porque o índice numérico da lista mascarou "Titular:". A política trata `desconhecido` como não conflitante (fail-open dentro de uma política fail-closed). A evidência C1 (item IX) tem estado `desconhecido` e é tratada como `nao_verificavel`; nada exige evidência positiva do atributo "competência".

## 8. Falhas do verificador e diagnóstico técnico

| # | Problema | Arquivo/função | Regra | Evidência | Casos | Risco de correção | Regressões possíveis | Testes sintéticos (antes de implementar) |
|---|---|---|---|---|---|---|---|---|
| P1 | Falso bloqueio por "publicação não identificável" | `geracao._identificabilidade` (908–933); `Catalogo.relevantes/melhor_janela` (`catalogo.py`) | janela de ≥N termos com peso igual; palavras genéricas contam; "relevante" ≠ concorre pela resposta | tabela do §6: 3 docs sem "alimentação" classificados como relevantes (6/7); concorrentes estritos = 0 | val-074-B ×3; na 4.3: val-054, val-082 | Afrouxar demais deixaria passar perguntas ambíguas reais (7/10 conversões da 4.3 eram "Ambígua de fato") | Perda de ambiguidade genuína; mudança do equilíbrio medido na 4.3 | (a) concorrente sem o termo raro não é relevante; (b) concorrente que também contém o predicado continua bloqueando; (c) verbo de ligação não conta; (d) pergunta genuinamente ambígua (dois contratos de alimentação) continua `ambigua`; (e) estabilidade nos 10 casos da 4.3 |
| P2 | M2 não reconhece rótulo quando o valor começa por índice de lista | `EV.rotulo_do_valor` (`evidencias.py`), consumida por `_relacoes_44`/M2 | exige prefixo `rotulo:` começando por letra; antes do valor, regex curta | `4 - Titular:` → `None`; `Titular:` → `titular/MEMBRO` | val-087-A-r1 (liberação indevida) | Aceitar numeração pode transformar itens legítimos em conflito (ex.: "1 - Objeto:"); depende do que é "índice" | Falsos bloqueios em listas numeradas legítimas | spans `4 - Titular:`, `(4) Titular:`, `IV – Titular:`, `item 4. Titular:` ≡ sem prefixo; negativos: `1 - Objeto:` com atributo OBJETO continua compatível; teste com membro dentro de lista numerada de competências |
| P3 | `desconhecido` tratado como não conflitante; ausência de evidência positiva do atributo | `_relacoes_44` / `_protecao_resposta` (M2) | só bloqueia com rótulo **conhecido incompatível** | r1: C1 e C2 `desconhecido`; resposta entregue | val-087-A-r1 | Exigir cue positivo pode bloquear respostas corretas sem cue (muitas perguntas) | Aumento de abstenções (perda de recall) | pergunta de competência com evidência sem cue de competência (membros, designação, instituição) → deve bloquear; evidência com "compete" → liberar; medir efeito nos 23 corretos/parciais da 4.3 |
| P4 | Associação de entidade por token de localidade único | `termos_salientes`; `_relacoes_44` (dimensão `entidade` de `relacoes/3`); A_LOC | "Hospital Regional de Ceilândia" reduz-se a `['ceilandia']`; `CEO UBS 11 – CEILÂNDIA` satisfaz | `relacoes/3` marca entidade/localidade `confirmada` e `estado_geral: confirmada` | val-024-C ×3 (e potencialmente qualquer pergunta "Hospital X em Local Y") | Exigir o tipo de unidade pode derrubar respostas legítimas | Falsos bloqueios quando o texto cita a unidade por sigla | trecho com lista de unidades contendo a localidade mas não o hospital pedido → `nao_verificavel`, não `confirmada`; trecho com o hospital pedido → `confirmada`; sigla (HRC) |
| P5 | `status` mistura sentidos | `gerar_resposta` (política de status) | `parcial` = lista não exaustiva; `fora_do_escopo` usado para abstenção de pergunta pertinente | A-r1 `parcial` incorreta; val-074-A `fora_do_escopo` com `abstencao_sem_justificativa` entregue | val-087-A-r1, val-074-A ×3, val-025 ×3 | Alterar taxonomia afeta relatórios e UI | Métricas históricas deixam de ser comparáveis | testes que separem completude da lista × sustentação da resposta × motivo da abstenção |

**Observação sobre relacoes/3 (Fase 4B):** a dimensão `entidade` confirmada apenas por token de localidade (P4) é uma limitação introduzida/exposta pela implementação 4B e não deve ser lida como confirmação semântica.

## 9. Limitações e vieses

- Auditor único e não independente da execução; 2 casos-alvo e 3 repetições por condição; os controles representam três perfis. A reconstrução de contexto é verificada por hash, não por captura da requisição.
- Texto integral do corpus e dos chunks lido em modo somente leitura; `localidades` do catálogo são derivadas do corpus (não auditadas).
- Contagem de "concorrentes" depende de `palavras_de_conteudo`; não foi testada a sensibilidade a outras listas de stop-words.
- A comparação 2/150 de P1 é descritiva.

## 10. Recomendações priorizadas para a próxima fase

1. **P2 (alta, baixo risco):** normalizar o índice de lista em `rotulo_do_valor` com testes simétricos (com/sem prefixo) — corrige a única liberação indevida observada.
2. **P1 (alta):** tornar a relevância da janela sensível à discriminância dos termos e ao predicado da pergunta, mantendo os casos genuinamente ambíguos da 4.3; criar antes o conjunto sintético (a–e) e medir nos 10 casos da 4.3 e nos 150.
3. **P4 (média):** não confirmar entidade apenas por localidade; propagar para `relacoes/3` como `nao_verificavel`.
4. **P3 (média, decisão de política):** avaliar a exigência de evidência positiva do atributo (alto impacto em recall) antes de qualquer implementação.
5. **P5 (baixa):** separar na saída o rótulo de completude da lista do estado de sustentação.
6. Revisar o gabarito de val-074 e revisar humanamente as 21 saídas.

Nenhuma correção foi implementada; a próxima decisão aguarda a revisão desta auditoria.
