# Fase 4B — Preparação offline (NÃO VALIDADA)

Data: 2026-11-15. Escopo: alterações offline no mecanismo B, no esquema de relações e na seleção de contexto (S1 forte). **Nenhuma geração com modelo foi executada.** Rótulo da versão em código: `fail-closed-4.4.4b-prep` (preparação; não promovida a validada). A referência imutável continua sendo `fail-closed-4.4.4a` (snapshots `*_44_fase4a.py`).

## 1. Hashes e snapshots (SHA-256, 16 primeiros caracteres)

| Arquivo | 4A (referência) | 4B-pre (antes das mudanças) | 4B-prep (depois) |
|---|---|---|---|
| `geracao.py` | `bbd28166f0db19c3` | `bbd28166f0db19c3` | `0891e70c01600054` |
| `evidencias.py` | `be8ac1dd9a2bdde6` | `be8ac1dd9a2bdde6` | `93363fab9f1a7f37` |
| `catalogo.py` | `8e44143ba1d092f5` | `8e44143ba1d092f5` | `8e44143ba1d092f5` (inalterado) |

Snapshots em `data_assistente/versoes/`: `*_44_fase4b_pre.py` (estado 4A, criado antes de qualquer edição) e `geracao_44_fase4b.py` / `evidencias_44_fase4b.py` (estado atual). Todos incluídos em `hashes_referencia_44.json`; `scripts/verificar_hashes.py` → **TODOS CONFEREM: True** (inclui o manifesto do RPA congelado). Baseline de comportamento da 4A: `fase4/replay_baseline_fase4a_comportamento.json`.

## 2. Arquivos alterados e justificativa

- `citizentech/assistente/evidencias.py` (apenas acréscimos + `SCHEMA_RELACOES = "relacoes/3"`): `PALAVRAS_FUNCIONAIS`, `tokens_de_uso`, `termos_de_uso`, `suporte_por_unidade` (mecanismo B v2); `dimensoes_da_relacao`, `ESTADOS_DIM` (relacoes/3); `rotulos_fortes`, `rotulo_forte_no_chunk` (S1 forte).
- `citizentech/assistente/geracao.py`: `VERSAO_POLITICA`; `_relacoes_44` reescrita em duas passadas (mecanismo B v2 + dimensões); `ConfigGeracao.priorizar_atributo` (**False por padrão**); `Contexto.selecao` (log); `montar_contexto` virou *wrapper* de `_montar_contexto` (corpo original intacto).
- Testes: novos `test_fase4b.py` (8), `test_fase4b_relacoes.py` (10), `test_fase4b_selecao.py` (8). Ajustes de asserção em testes antigos, só de rótulo/redação: `VERSAO_POLITICA`, `relacoes/2→relacoes/3` e a redação da justificativa em `test_fase4a.py` ("nao bloqueia"). Nenhuma decisão esperada foi alterada.
- Não tocados: BM25/embeddings/RRF/índices/corpus/chunking/gabaritos, orçamento (3.000), arquivos congelados do RPA, rodadas, auditorias e snapshots anteriores.

## 3. Mecanismo B v2 — regra e testes T1–T6

**Causa investigada:** em `termos_de_conteudo` só palavras com ≥6 letras contavam; resposta sem tais termos (números, siglas, uma palavra) caía em "todos os trechos necessários" → bloqueio por trecho conflitante não usado.

**Nova regra (sem limiar de caracteres, sem depender de palavra longa):** termos de uso = tokens da resposta que não são palavras funcionais (lista fechada do português), nem genéricos, nem da pergunta (inclui flexão por radical). Números (`12`) e siglas (`HRG`) contam. Um trecho conflitante só é *necessário* se algum termo da resposta tiver **todos** os seus apoios em trechos com a mesma causa de conflito. Se nenhum termo da resposta é apoiado por trecho algum (`medida_de_uso = nao_mensuravel`), todos os trechos continuam necessários (**fail-closed**).

| Teste | Cenário | Resultado |
|---|---|---|
| T1 | span correto + secundário conflitante não usado | entregue; conflito registrado, `bloqueia=False` ✔ |
| T2 | resposta de uma palavra ("Sim.") | com span conflitante: bloqueia (fail-closed); sem conflito: entrega ✔ |
| T3 | só números pequenos (`12`, `30`) | medidos; secundário não necessário → entrega ✔ |
| T4 | termo em dois spans, um conflitante | entrega (o outro apoia) ✔ |
| T5 | siglas | `HRG` só no span conflitante → bloqueia; `CRSSU` apoiada pelo correto → entrega ✔ |
| T6 | único span conflitante + resposta não mensurável | continua bloqueando ✔ |

Replay offline dos 150 contra a baseline 4A: **0 diferenças** (status, resposta, problemas) — nenhuma decisão mudou. Limitação: "Sim." é tratado como palavra funcional; respostas só de palavras funcionais ficam em fail-closed.

## 4. Relações — esquema `relacoes/3`

Aditivo: todos os campos de `relacoes/2` permanecem (`entidade`, `atributo`, `estado`, `estado_associacao`, …). Novos: `dimensoes` {`entidade`, `destinatario`, `atributo`, `localidade`}, cada uma com `estado` (`confirmada|conflitante|nao_verificavel|nao_aplicavel`), valor pedido/encontrado, `justificativa` e `origem`; `estado_geral` (conflitante se qualquer dimensão conflita; confirmada só se **todas** as aplicáveis confirmam; senão não verificável); `medida_de_uso`. Confirmar o destinatário não confirma o atributo. Testes: destinatário correto + atributo incorreto → `conflitante`; destinatário conflitante + atributo correto → `conflitante`; localidade confirmada + atributo não verificável → `nao_verificavel`; todas confirmadas → `confirmada`; ausência de informação → `nao_verificavel` (não confirmação); mais três integrados (val-083 mantém bloqueio). As dimensões **não influenciam** nenhuma decisão do pipeline (replay: 0 diferenças).

## 5. Seleção de contexto — S1 forte (flag `priorizar_atributo`, desligada por padrão)

Regra: um chunk é prioritário se (a) contém um rótulo que **repete o atributo pedido** (mesma família e mesmo radical da cabeça: `competencias` → `competencia`/`compete`) **em posição de rótulo** (primeira palavra de cláusula/item, já sem enumerador "Art. 4º", "IV –", "§", ou palavra seguida de `:`), e (b) está associado à entidade da pergunta (todos os nomes salientes presentes no chunk ou nos chunks recuperados da mesma publicação; sem nome saliente → não prioriza). Família ampla ("atribuições", etc.) e ocorrência no meio de frase não contam. Só atua se esse chunk foi **descartado** pelo orçamento na seleção original; então passa à frente, a ordem relativa dos demais é preservada, o orçamento (3.000) é o mesmo e `Contexto.selecao` registra por chunk priorizado/mantido/descartado e o motivo. Flag desligada ⇒ caminho de código original, `selecao == []`.

Comparação offline (150 perguntas, `fase4b_selecao_comparacao.py/.json`):

- Contextos alterados: **6** (val-011, 074, 080, 087, 125, 133); **144 inalterados**.
- Respostas entregues na 4.3 afetadas: **0** (os 6 eram ambigua/fora_do_escopo/insuficiente).
- Orçamento: nenhum estouro (máx. 2.985); tokens antes→depois: 011 2886→2882, 074 2916→2985, 080 2716→2712, 087 2948→2928, 125 2790→2741, 133 2801→2802.
- Ordem relativa dos demais preservada em todos. Grupos: val-074 B→A e val-080 B→A (o documento esperado passa a entrar no contexto).
- **val-087:** passa a incluir `dodf-174:0003` (frase "IV – Compete à CRSSU…") e `0002` ("Art. 4º Competência e Disposições…"); saem `0000` e `0001` (lista de membros).
- **val-130:** contexto **inalterado** (a regra estrita não o prioriza; na simulação frouxa anterior mudava); o replay mantém o bloqueio esperado (`insuficiente`, problemas idênticos à 4A).
- **Mudanças não esperadas a revisar:** val-011, val-125 e val-133 trocam um chunk por outro de documento **que não é o esperado** (rótulo "Endereço:"/"Valor:" + nomes da entidade presentes). Atendem à regra, mas o benefício não é demonstrável sem modelo; val-065 deixou de mudar ao exigir nome saliente. Recomenda-se decidir se esses três são aceitos antes de qualquer regeneração.

## 6. Impactos colaterais e limitações

- Suíte completa: **311 testes passando** (285 da 4A + 26 novos). Replay 150 vs 4A: 0 diferenças com a flag desligada.
- O efeito do S1 sobre as respostas **não foi medido** (sem modelo): só sabemos qual contexto muda. Mais contexto de "competência" não garante resposta correta.
- A associação com a entidade é por nomes salientes (nível de publicação), podendo aproximar publicações homônimas (ex.: val-125/133).
- Rótulos fortes só existem para famílias com `FAM_ROTULO`; perguntas sem atributo de família conhecida nunca são afetadas.
- val-007 (modalidade) e val-012/100 (tipo de item) seguem fora do alcance.

## 7. Confirmações

- **Nenhuma geração foi executada**; LM Studio/API de modelo não foram chamados; nenhuma rodada end-to-end; as 11 perguntas **não** foram regeneradas; sem set de 350.
- RPA congelado, corpus, índices, BM25/embeddings/RRF/chunking, gabaritos, rodadas, auditorias e snapshots anteriores: **intactos** (`verificar_hashes.py` → TODOS CONFEREM).
- Versão `fail-closed-4.4.4b-prep` **não está validada**; `fail-closed-4.4.4a` permanece como referência. A flag `priorizar_atributo` permanece desligada por padrão; regeneração seletiva depende de autorização explícita.
