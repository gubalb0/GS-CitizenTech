# Versão 4.4 — Fase 3 (proteção contra respostas incorretas)

Política: `fail-closed-4.4.3`. Nenhuma geração com o modelo; validação por **replay offline** das 150 saídas brutas da rodada 4.3 (`scripts/replay_fase3.py`; a linha de base da Fase 2 é o mesmo código com `PROTECOES_44` vazio e foi validada contra a rodada 4.3 + os 10 casos liberados na Fase 2, com asserts de status e texto).

## Arquivos e funções alterados
- `citizentech/assistente/evidencias.py` (novas): M1 `afirmacao_negativa`, `cabeca_do_atributo`, `remissao_a_anexo`, `cobertura_da_publicacao`; M2 `FAM_ATRIBUTO`, `FAM_ROTULO`, `COMPATIVEL`, `familia_do_atributo`, `rotulo_do_valor`, `conflito_atributo_rotulo`, `_fold1`; M3 `item_do_registro`, `molde_do_registro`, `estrutura_de_lista`, `exclusividade`; M4 `periodo_da_pergunta`, `periodos_declarados`, `periodos_incompativeis`; M5 `cnpjs`, `associacao_estrutural`, `REGIOES`.
- `citizentech/assistente/geracao.py`: nova `_protecao_resposta` (M1→M2→M4→M5→M3, nessa ordem) chamada em `_aplicar_politica` **depois** das conversões em `ambigua` (as abstenções da 4.3 não mudam); `compor` passa a receber o texto recomposto (M3); mensagens `MSG_NAO_ENCONTRADA`, `MSG_AUSENTE_ANALISE_INTEGRAL`, `MSG_REMISSAO`, `MSG_ROTULO`, `MSG_PERIODO`, `MSG_LOCALIDADE`, `MSG_ENTIDADE`; `VERSAO_POLITICA`; constante `PROTECOES_44` (permite o replay comparativo e os testes de necessidade de cada mecanismo).
- `citizentech/assistente/catalogo.py`: só um atributo de leitura, `Catalogo.localidades` (gazetário vindo dos metadados do corpus; 55 valores).
- Testes: `tests/test_protecao_44.py` (novo, 37 testes). `tests/test_politica_evidencias.py` (constante de versão) e `tests/test_verificador_44.py` (o teste de replay da Fase 2 agora roda com `PROTECOES_44` vazio, isolando a Fase 2; o efeito combinado é verificado em `test_protecao_44.py`).
- Não alterados: retriever, embeddings, BM25, RRF, índices, corpus, orçamento de contexto, modelo, RPA congelado. Sem juiz LLM nem chamadas adicionais.

## Mecanismos (todos só rebaixam para `insuficiente` ou reescrevem o texto de uma `parcial`)
- **M1 — ausência, remissão e cobertura.** Três situações, três mensagens, nenhuma afirma ausência não comprovada: (a) *remissão a documento não publicado* (o atributo pedido aparece só como "especialidades elencadas na carta proposta, doc. SEI n° ...") → "a publicação remete o atributo a documento não publicado (Doc. SEI nº ...)"; (b) *afirmação negativa com contexto parcial* (`n_chunks_doc` > trechos analisados) → "não encontrei nos trechos analisados (X de Y); isso não significa que não conste"; (c) *negativa após análise integral* (todos os trechos da publicação no contexto) → "analisei integralmente a publicação e não identifiquei nela esta informação".
- **M2 — atributo x rótulo do valor.** Famílias fechadas, derivadas da frequência de rótulos no corpus (compete 1.200, valor 464, empresa 459, objeto 361, partes 267, vigência 233, responsável 160, endereço 133). Só **conflito entre famílias conhecidas** bloqueia; rótulo ou atributo desconhecido nunca bloqueia. A relação entidade–atributo–valor é registrada em `verificacao.evidencia.protecao.relacoes` (estado `compativel`/`conflito`/`desconhecido`).
- **M3 — item de lista.** Só quando a pergunta é lista, a resposta é exclusiva ("o programa ... é X"), o item é um registro de uma enumeração (≥3 registros do mesmo molde no chunk) e há **um único** item verificado. O texto vira "Entre os itens encontrados em {publicação}, consta: {prefixo literal do registro}. Este é apenas um dos itens...", sem dados pessoais do restante da linha; o status segue `parcial` e o aviso de lista não exaustiva é mantido.
- **M4 — períodos.** Interpreta o intervalo da pergunta e seu sentido (genérico, execução, vigência, publicação) e o confronta só com períodos do **mesmo sentido** declarados pela publicação ("no período de ..." = referência/execução; "vigência de ... a ..." = vigência; data da edição = publicação). Datas de assinatura/ratificação não são períodos. Sem período declarado: registrado, sem bloqueio.
- **M5 — localidade/entidade por associação estrutural.** Só decide quando o CNPJ está ligado à localidade por **registro numerado** ("Matriz:", "Filial (n):") ou por **campo rotulado** ("CNPJ: x, ENDEREÇO: ..."). Proximidade textual não conta. Regiões de saúde (sudoeste, sul...) nunca conflitam com cidades. Entidade em outro registro só vale com nomes discriminativos (que aparecem em um único registro).

## Testes adicionados (37) e resultado
Unidades de cada mecanismo; positivo/negativo/regressão para M1–M5 (inclui: entidade correta com atributo errado; atributo correto com entidade de outro registro; valor correto com período errado; localidade no documento mas não associada à entidade; item de lista sem confirmação; negativa com contexto incompleto; não encontrada x ausente após análise integral; remissão); `test_cada_mecanismo_e_necessario_remover_um_reabre_o_erro` (5, parametrizado: com o mecanismo removido, o cenário volta a ser entregue); `test_nenhum_mecanismo_promove_status_nem_cria_resposta`; replay dos 150 (`test_replay_150_fase3_...`).
**Suíte do Gen AI completa: 262 passam** (225 anteriores + 37). Hashes e RPA: ver abaixo.

## Replay dos 150: diferenças Fase 3 x Fase 2 (7 casos; os outros 143 idênticos em status e texto)
| Caso | Fase 2 | Fase 3 | Mecanismo / motivo | Texto |
|---|---|---|---|---|
| val-039 | parcial ("não foram especificadas as denominações") | insuficiente | M1 (negativa, contexto parcial: 1 de 28 trechos) | "Não encontrei esta informação nos trechos ... (1 de 28 trechos de Extrato Contrato nº 051690/2024 ...). Isso não significa que ela não conste da publicação." |
| val-047 | parcial ("O programa ... é Anestesiologia") | **parcial** | M3 | "Entre os itens encontrados em Aviso 1/2024 (...), consta: 402 - Anestesiologia - Hospital Regional do Gama (HRG). Este é apenas um dos itens da lista; ... não é exaustiva." + AVISO de lista |
| val-050 | parcial (heparina + metaraminol fora do período) | insuficiente | M4 (período declarado 31/01–06/02/2025 x pedido 31/07–22/08/2025) | "Extrato 01/2025 (...) refere-se ao período de 31/01/2025 a 06/02/2025 (referencia), que não coincide com o período solicitado ..." |
| val-087 | parcial | insuficiente | M2 (rótulo 'titular', família MEMBRO, x atributo 'competências') | "A evidência encontrada em Ordem de serviço 396/2022 ... trata de outro atributo ('titular') e não de competencias..." |
| val-130 | parcial (Biosphere como empresa da Asa Sul) | insuficiente | M5 (registro "Filial (3)" do CNPJ ...0007-93 = Asa Norte; pedido Asa Sul) | "No registro de Autorização 133/2021 ... a localidade informada é asa norte, e não asa sul..." |
| val-136 | parcial (objeto do edital como "especialidades") | insuficiente | M1 (remissão a Doc. SEI 160711978); M2 também bloquearia | "Extrato 09/2025 ... remete o atributo solicitado (especialidades) a documento não publicado ... (Doc. SEI nº 160711978)..." |
| val-141 | parcial (negativa sobre a Região Norte) | insuficiente | M1 (negativa, 3 de 28 trechos) | mensagem de contexto parcial |
Arquivo completo: `fase3/replay_fase3_mudancas.json`. Casos que ficam `parcial` sem alteração: val-044, 031, 032 (justificados no diagnóstico), e as 23 respostas julgadas Correta/Correta-mas-parcial pela auditoria.

## Critérios de conclusão (verificados literalmente por `fase3/verificacao_criterios.py`)
1. val-039, 050, 130, 136 e 141 não são entregues como `respondida`/`parcial` — **PASS** (todos `insuficiente`).
2. val-047 continua `parcial`, sem texto exclusivo — **PASS**.
3. val-087 deixa de ser `parcial` com a frase atual — **PASS**.
4. val-044, 031 e 032 permanecem `parcial`, mesmo texto — **PASS**.
5. As 23 respostas dadas julgadas Correta/Correta-mas-parcial (7 + 16) mantêm status e texto — **PASS**.
6. Nenhuma promoção; todas as mudanças são rebaixamentos ou reescrita de `parcial` — **PASS**.
7. val-062, 108 e 126 seguem bloqueados pelos mesmos motivos — **PASS**.
8. Cada mecanismo tem teste positivo, negativo e de regressão, e teste de necessidade — **PASS**.
9. Hashes, snapshots e RPA — **PASS** (abaixo). Extra: nenhuma abstenção da 4.3 (fora os 10 casos da Fase 2) mudou — **PASS**. **Nenhum critério falhou.**

## Preservação
Snapshots da 4.3 (`*_43_pre_execucao.py`, `avaliacao_e2e_etapa4_3.py`) e da Fase 2 (`*_44_fase2.py`, `*_44_fase2_final.py`; idênticos entre si) intactos; criados `geracao/evidencias/catalogo_44_fase3.py`. `scripts/verificar_hashes.py`: todos os hashes conferem (RPA congelado, rodadas, auditorias, snapshots; manifesto ampliado com os snapshots da Fase 2 e 3). `chunks_exemplos.json` mantém o SHA-256 registrado. Rodadas e auditorias anteriores não foram alteradas.

## Limitações e riscos que permanecem
- **Cobertura baixa dos verificadores relacionais.** Entre as 38 respostas dadas da Fase 2: M2 chegou a uma relação conhecida (compatível ou conflito) em só 4; M4 teve período na pergunta em 1; M5 encontrou associação estrutural em 1 (val-130); M3 detectou lista em 1. Fora desses casos, os mecanismos não decidem (por desenho), então a proteção real é estreita. Ela não generaliza por si só: depende de testar com perguntas novas.
- **As 8 respostas incorretas da auditoria:** 4 deixam de ser entregues (val-039, 050, 130, 136). **val-007, 012, 100 e 149 continuam sendo entregues** (recuperação ruim, tipo de item e evidência genérica): fora do escopo acordado; nenhum mecanismo da Fase 3 as cobre.
- **val-136:** é bloqueado por M1 e por M2 (defesa em profundidade); por isso o teste de necessidade de M1 usa o cenário de negativa (val-039/141).
- **val-087:** foi bloqueado pelo conflito de família (`titular`, de uma lista de membros), não por ausência do rótulo "compete" (rótulo desconhecido não bloqueia, conforme o ajuste 3). Se a evidência tivesse a mesma frase sem a lista de membros, passaria.
- **val-141 e val-039** viram `insuficiente` com mensagem de contexto parcial: a informação pode existir nos trechos não analisados; o sistema não afirma ausência.
- **val-044** continua `parcial` com o objeto do edital como "serviços credenciados": é genérico mas compatível (rótulo `objeto` ∈ família de `serviços`); fica como risco de resposta pouco informativa.
- **M4:** só reconhece intervalos com duas datas e períodos declarados com "período de ... a ..." ou "vigência ... a ..."; atos sem período declarado não são verificados. Uma resposta com um item fora do período bloqueia a resposta inteira (não filtra só o item).
- **M5:** só CNPJ; só registros "Matriz/Filial/Unidade" ou "CNPJ ... ENDEREÇO"; as localidades nas mensagens saem em minúsculas sem acento.
- **M3:** só para registros que abrem com número (molde `numero - termo - termo`); outras enumerações (itens em prosa) não são reconhecidas.
- **Medição em desenvolvimento:** as 150 perguntas foram usadas para projetar os mecanismos; os resultados acima são regressão, não estimativa de desempenho. O replay usa as saídas do modelo da 4.3; uma nova geração pode produzir respostas diferentes.
