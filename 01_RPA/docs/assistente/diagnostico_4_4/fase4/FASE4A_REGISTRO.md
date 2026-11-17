# Fase 4A — Integridade das relações entre evidência e entidade (`fail-closed-4.4.4a`)

Escopo: **somente verificação** (`evidencias.py`, `geracao.py`, uma linha em `catalogo.py`). Não foram alterados: retriever, BM25, embeddings, RRF, índices, corpus, montagem/orçamento de contexto, prompts, parâmetros, modelo, política de abstinência, RPA, saídas históricas e relatórios anteriores. Nenhuma chamada ao modelo; validação por replay offline das 150 saídas brutas da rodada 4.3.
`fail-closed-4.4.3` (Fase 3) permanece como referência imutável nos snapshots `*_44_fase3.py` (idênticos a `*_44_fase4a_pre.py`, criados antes da edição).

## 1. Diagnóstico (confirmado na auditoria complementar e reconfirmado nesta fase)
| Falha | Causa técnica |
|---|---|
| val-083 | O item "cloreto de sódio" estava num registro de ratificação cujo destinatário é "o Hospital Regional do Guará"; a pergunta é sobre a Atenção Primária. A existência da localidade "Guará" e do produto no documento não prova o destinatário. |
| val-149 | A evidência do estatuto do INAS (doc 1611) vinha de uma publicação que **não menciona Ceilândia**; a Fase 2 aceitava porque outro trecho citado (o decreto) trazia a localidade. |
| val-087 / A2 / C | O bloqueio por rótulo (`titular`) olhava só o trecho em si, não se ele sustentava algum termo da resposta; rótulo no prefixo ignorava competência explícita no mesmo trecho. |
| val-007 | O trecho sobre o "Hospital da Mulher" (São Paulo) não tem vínculo estrutural com Riacho Fundo II, mas **não há como provar isso por estrutura** (a localidade só aparece como local da reunião). |
| Registro | `relacoes` trazia só os nomes da **pergunta** como "entidade", valor truncado em 90 caracteres e nenhuma informação de registro/destinatário. |

## 2. Implementação (etapas pequenas; testes após cada uma)
**Etapa 1 — Mecanismo C: registro auditável (esquema `relacoes/2`).** `verificacao.evidencia.protecao.esquema_relacoes = "relacoes/2"`; cada relação por trecho usado (candidata literal e citação verificada). Comportamento idêntico ao da Fase 3 (replay: 0 diferenças).
**Etapa 2 — Mecanismo B: conflito de rótulos por uso.** Um conflito só bloqueia se (i) o trecho (grupo de trechos do mesmo item: candidata + citação que se sobrepõem) sustenta um termo de conteúdo da resposta que nenhum outro grupo sustenta e (ii) o próprio trecho não traz um indício explícito do atributo (`compete`, `atribuições`...); com indício, fica `nao_verificavel`. Termos de conteúdo: palavras ≥ 6 letras, siglas/nomes em maiúsculas e números ≥ 3 dígitos, fora a pergunta e os genéricos; sem termos, todos os trechos contam como necessários (conservador). Replay: 0 diferenças (val-087 continua bloqueado: `hrg` só existe na lista de membros).
**Etapa 3 — Mecanismo A: destinatário e localidade da publicação.** (a) *Destinatário*: a cláusula estrutural "para atender as necessidades d[ao] X" do **mesmo registro** (delimitado pelo próximo `RATIFICO`/`cujo objeto`), comparada com o destinatário da pergunta ("Atenção Primária" ≠ "Hospital Regional do Guará"; a localidade que vem depois de "no/na" não é destinatário). Estados: confirmada (termos não-geográficos em comum; localidades, se ambas existem, coincidem), conflitante (sem termo em comum ou mesma unidade em outra localidade), não verificável (um dos lados sem destinatário). (b) *Localidade da publicação*: se a pergunta tem localidade (gazetário do corpus, sem regiões de saúde) e a publicação inteira (catálogo) **e** seus metadados não a citam, o trecho dessa publicação não pode ser associado a ela. Ambos só bloqueiam quando o trecho é necessário (como na Etapa 2).

## 3. Arquivos e funções
- `evidencias.py` (novas): `registro_do_trecho`, `termos_de_conteudo`, `apoio_exclusivo`, `cue_de_atributo`, `destinatario_da_pergunta`, `destinatario_no_registro`, `comparar_destinatarios`, `grupos_de_trechos`, `SCHEMA_RELACOES`; ajuste de `maxsplit` em `registro_do_trecho`.
- `geracao.py`: `_relacoes_44` (nova; substitui o bloco M2 de `_protecao_resposta`), `_publicacao_menciona_localidade` (nova), `_protecao_resposta` (chama `_relacoes_44`), mensagens `MSG_DESTINATARIO`/`MSG_LOC_PUB`, flags `A_DEST`/`A_LOC` em `PROTECOES_44`, `VERSAO_POLITICA = "fail-closed-4.4.4a"`.
- `catalogo.py`: `meta` passa a incluir `localidades` (leitura).
- Testes: `tests/test_fase4a.py` (novo, 23 testes). Ajustes de isolamento: `test_protecao_44.py::test_replay_150_fase3_...` roda com `A_DEST`/`A_LOC` desligados (Fase 3 isolada); `test_politica_evidencias.py` (constante da versão).

## 4. Esquema das relações antes/depois
| Campo | Fase 3 (`relacoes`, sem versão) | Fase 4A (`relacoes/2`) |
|---|---|---|
| `entidade` | nomes da pergunta | **mantido** (continua sendo os nomes da pergunta) |
| `atributo`, `familia_atributo`, `rotulo`, `origem`, `chunk_id`, `estado` | sim (`estado` ∈ compativel/conflito/desconhecido) | **mantidos** (`estado` continua descrevendo só o rótulo) |
| `valor` | truncado em 90 caracteres | **completo** |
| `esquema`, `publicacao`, `doc_id`, `fonte` | — | novos |
| `entidade_pergunta` / `entidade_no_trecho` | — | novos (nomes da pergunta presentes no registro/trecho) |
| `atributo_pedido` / `atributo_encontrado` | — | novos (`{cabeca, familia}` / rótulo) |
| `destinatario_pergunta` / `destinatario_no_trecho` | — | novos (só da cláusula estrutural; nunca de localidade solta) |
| `localidades_no_registro`, `publicacao_menciona_localidade` | — | novos |
| `registro` | — | `{tipo, id}` ou `null` (id só se existir na fonte: cabeçalho numerado ou `Processo SEI`) |
| `estado_associacao` | — | `confirmada` / `conflitante` / `nao_verificavel` |
| `causas_do_conflito`, `justificativa`, `necessaria`, `termos_exclusivos`, `bloqueia` | — | novos |
Consumidores do esquema antigo continuam lendo os mesmos campos. A versão está em `protecao.esquema_relacoes`.

## 5. Testes e resultados
`tests/test_fase4a.py` (23): **C** (esquema e campos históricos, valor extenso sem truncamento, identificador do registro só se existe, entidade/atributo pedido x encontrado, evidência sem associação verificável); **B** (unidades; **A1, A2, B1, B2, C exatamente como na auditoria**; conflito real com duas unidades); **A** (unidades; entidade e destinatário corretos; produto destinado a outra unidade, val-083; item conflitante não usado; mesma unidade em outra localidade; localidade mencionada sem destinatário; registros independentes sem herdar destinatário por proximidade; publicação sem a localidade, val-149; val-007 não verificável; cada mecanismo é necessário) e **replay dos 150**.
| Cenário | Resultado obtido | Esperado |
|---|---|---|
| A1 | entregue | permitir ✓ |
| A2 | entregue; relação registrada como `conflitante`, `necessaria=False`, `bloqueia=False` | não bloquear ✓ |
| B1, B2 | `insuficiente` (`rotulo_incompativel_com_atributo`) | bloquear ✓ |
| C | entregue; `nao_verificavel` com a justificativa citando `compete` | não bloquear automaticamente ✓ |
**Suíte completa do Gen AI: 285 passam** (262 + 23).

## 6. Replay offline das 150 (Fase 4A x comportamento da Fase 3; baseline gravado antes das alterações)
Mudam **2** casos; os outros 148 idênticos em status e texto (`replay_fase4a_mudancas.json`).
| Caso | Fase 3 | Fase 4A | Evidência nova que justifica | Texto depois |
|---|---|---|---|---|
| val-083 | `parcial` (5 itens "para a Atenção Primária no Guará") | `insuficiente` (`destinatario_conflitante`) | o registro SEI do cloreto de sódio declara "para atender as necessidades do Hospital Regional do Guará" | "No registro de Extrato 00375749/2025 (...), o item 'CLORETO DE SODIO ...' é destinado a hospital regional do guara, e a pergunta trata de atencao primaria; por isso o item não responde à pergunta." |
| val-149 | `parcial` (generica) | `insuficiente` (`publicacao_sem_vinculo_com_a_localidade`) | o texto completo da Portaria 03/2006 (doc 1611) e seus metadados não citam Ceilândia, e o trecho dessa publicação sustenta termos exclusivos da resposta | "Portaria numerada 03/2006 (...) não menciona a localidade perguntada (ceilandia); o trecho dessa publicação não pode ser associado a ela." |
Sem mudança (comportamento verificado): val-007 (`parcial`; relações `nao_verificavel`), val-012, val-100 (`parcial`), val-087 (continua `insuficiente`; a relação do trecho de membros é `conflitante`, `necessaria`, `bloqueia`), val-044, val-047 (`parcial`, texto inalterado), val-062, val-108, val-126 (continuam bloqueados pelos mesmos motivos) e as 23 respostas corretas/corretas-mas-parciais. Nenhuma promoção de status em nenhum dos 150.
Estados das relações nas 30 respostas entregues: 80 confirmadas, 33 não verificáveis, 0 conflitantes bloqueantes.

## 7. Mudanças de comportamento
Apenas as duas acima, ambas **rebaixamentos** (`parcial` → `insuficiente`). Nenhum bloqueio da Fase 3 foi removido; nenhuma resposta foi promovida.

## 8. Riscos e limitações
- **val-007 não é resolvido.** O trecho do Hospital da Mulher (São Paulo) fica `nao_verificavel` e a resposta continua sendo entregue: provar a atribuição exigiria inferência semântica que não existe por estrutura (Riacho Fundo II aparece só como local da reunião). Interpretei "comportamento conservador" como não afrouxar nem endurecer sem prova; uma política que bloqueasse todo `nao_verificavel` removeria 33 relações de respostas entregues, entre elas as das corretas (não testada como regra).
- val-012 e val-100 (tipo de item) não pertencem ao mecanismo A e seguem entregues.
- O destinatário só é reconhecido na cláusula "para atender as necessidades d[ao] X" de extratos de ratificação; fora disso é `nao_verificavel`. Variações de redação do destinatário ("HCB" x "Hospital da Criança de Brasília") podem gerar falso conflito (0 observado nas 150).
- A regra de localidade da publicação pode bloquear publicações que servem à localidade só por sigla (ex.: "HRC"); mitigada por texto completo + metadados; 0 ocorrências nas 150, mas a cobertura é pequena.
- A associação por necessidade depende de termos de conteúdo; respostas sem termos mensuráveis tratam todos os trechos como necessários (como na Fase 3).
- Mensagens trazem destinatário/localidade normalizados (minúsculas, sem acento): estético.
- As 150 perguntas foram usadas no projeto; o replay é regressão, não estimativa de desempenho, e usa as saídas do modelo da 4.3.

## 9. Integridade
`scripts/verificar_hashes.py`: **todos conferem** (RPA congelado, rodadas, auditorias, snapshots da 4.3, Fase 2, Fase 3 e Fase 4A; manifesto ampliado). Snapshots criados: `geracao/evidencias/catalogo_44_fase4a_pre.py` (= Fase 3, idênticos aos `_44_fase3.py`) e `_44_fase4a.py` (estado final). `chunks_exemplos.json`: SHA-256 inalterado. Corpus, índices, chunks, gabaritos, rodadas e relatórios anteriores não foram tocados. Nenhuma chamada ao modelo.

## 10. Critérios de conclusão
Associação evidência–entidade coberta por testes ✓; cenários A1, A2, B1, B2, C com os resultados esperados ✓; relações auditáveis (`relacoes/2`) ✓; nenhum bloqueio legítimo da Fase 3 removido (replay e testes) ✓; suíte completa passa (285) ✓; replay reproduzível (`fase4/replay_fase4a.py`, baseline em `fase4/replay_baseline_fase3_comportamento.json`) ✓; hashes e snapshots íntegros ✓.
