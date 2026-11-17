# Fase 4D.1 — Normalização de rótulos com índice de lista (versão CANDIDATA `fail-closed-4.4.4d1-cand`, não validada)

Escopo: apenas a normalização de prefixos de enumeração antes do reconhecimento de rótulo em `rotulo_do_valor`. Não foram tocados: regra de relevância do catálogo, associação de entidades, política de evidência positiva, mecanismo B, S1 conservadora. Flag `priorizar_atributo` desligada; **nenhuma geração, LM Studio ou API**; JSONL da validação, manifesto e snapshots históricos intactos.

## 1. Causa raiz

`EV.rotulo_do_valor(texto, valor)` procura (a) um prefixo `rótulo:` no próprio valor, com `^\s*([a-z][a-z ]{1,38}?)\s*:`, que **exige que o valor comece por letra**, e (b) um rótulo imediatamente antes do valor no texto. Em `val-087-A-r1` a citação foi `4 - Titular: Diretor do Hospital Regional do Gama…` (com o índice do item): (a) falhou (começa por "4") e (b) encontrou "…Suplente: Substituto legal do cargo; " (sem rótulo conhecido) ⇒ `estado = desconhecido`, `rotulo = None`. Em A-r2/A-r3, sem o prefixo "4 - ", o mesmo trecho foi reconhecido como `titular`/MEMBRO e bloqueado.

## 2. Implementação (`citizentech/assistente/evidencias.py`, único ponto de uso: `geracao._relacoes_44`)

- Nova função `sem_indice_de_lista(valor)` e constantes `_INDICE_LISTA`, `_APOS_INDICE_E_ROTULO`; `rotulo_do_valor` passa a aplicar `sem_indice_de_lista` ao valor antes do fold/regex.
- O índice é removido **somente se** o que vem depois tem forma de rótulo (`letra… :` em até 38 caracteres). Formas aceitas: `4 -`, `4 –`, `4 —`, `4)`, `4. ` (ponto seguido de espaço), todas com 1–3 dígitos; algarismos romanos **maiúsculos canônicos** (I…XXXIX) com `- – — ) .`. Não casam (ficam intactos): datas (`14/03/2025:`), anos (`2025 - Objeto:`, 4 dígitos), CNPJ (`12.345.678/0001-90 …`), números de processo/ids, valores (`R$ 10 - Objeto:`, `1.234,56 - Valor:`), decimais (`10.5 Objeto:`), números longos, palavras maiúsculas parecidas com romanos (`CIVIL -`, `MIX -`) e índice seguido de texto sem rótulo (`4 - Diretor do HRG`).
- `VERSAO_POLITICA = "fail-closed-4.4.4d1-cand"` (única outra mudança em `geracao.py`; asserção correspondente atualizada em `test_politica_evidencias.py`).

## 3. Testes (`tests/test_fase4d1.py`, 12 testes)

Rótulo sem índice; com índice numérico+hífen (e meia-risca); numérico+ponto; numérico+parêntese; romano canônico (e não-romanos `CIVIL`/`MIX`); texto sem rótulo após o índice; números do conteúdo/datas/ids/CNPJ/valores não removidos; rótulo em posição intermediária (busca antes do valor); comportamento anterior preservado; cenários integrados — membro com `4 - `, `4. ` e sem índice **bloqueado igualmente**; **competência explícita** com e sem índice (`4 - Competência:`, `Competência:`, `5 - Compete à CRSSU…`) **não bloqueada**; replay offline dos 21 registros da validação seletiva.

Suíte completa: **337 testes passando** (325 + 12). Um erro de fixture meu foi corrigido durante o desenvolvimento (a resposta sintética mencionava "CRSSU", ausente do trecho citado, bloqueando por `afirmacoes_nao_sustentadas`, sem relação com rótulo).

## 4. Resultados dos replays (sem modelo)

Referências gravadas antes da mudança: `replay_4d1_pre_*.json`; depois: `replay_4d1_pos_*.json` (novos arquivos).

| Replay | Itens | Diferenças (status/resposta/problemas) pré→pós |
|---|---:|---|
| Rodada 4.3 (150, saídas brutas gravadas) | 150 | **0** (também 0 contra a baseline 4A) |
| Validação seletiva (21, saídas brutas e contextos de cada slot) | 21 | **0** (e replay pré = registro gravado em 21/21, validando o harness) |

Spans em que o índice foi efetivamente removido: **0** nos 150; **1** na validação seletiva (a citação `4 - Titular: Diretor do HRG…` de val-087-A-r1). Logo, a mudança afeta no máximo esse caso observado.

- Respostas anteriormente corretas bloqueadas: **nenhuma**. Respostas incorretas que passaram a ser entregues: **nenhuma**. Mudanças de status/resposta/problemas: **nenhuma**.

## 5. Resultado específico: val-087-A-r1 — o rótulo é reconhecido, mas a decisão não muda

- r1: o relacionamento da citação C2 passa a `rotulo = titular/MEMBRO`, `estado = conflito`, `causas = [rotulo]` (antes: `desconhecido`, sem causas). **O rótulo agora é reconhecido, como pedido.**
- Mesmo assim, r1 **continua entregue como `parcial`**: o conflito não é *necessário* segundo o mecanismo B v2. A resposta de r1 diz "…implementação das normas e protocolos de regulação de internação hospitalar **no Gama**"; seus termos de uso (nortear, gerências, implementação, normas, protocolos, internação, hospitalar…) têm suporte em C1; "Gama" vem da **pergunta** e é excluído de `termos_de_uso`. Em r2/r3 a resposta usa "**HRG**" (termo exclusivo de C2), portanto C2 é necessária e o bloqueio dispara.
- r2 e r3: **bloqueio preservado** (`insuficiente`, `rotulo_incompativel_com_atributo`).
- Conclusão: a correção do parser é correta e necessária (o registro auditável de r1 passou a refletir o conflito de rótulo), mas é **insuficiente** para impedir a liberação de r1. Essa parte depende do mecanismo B (necessidade do trecho) e da política de evidência positiva, **fora do escopo autorizado**; nada foi alterado ali.

## 6. Diferenças em relação à candidata anterior (`4.4.4b-cand`)

| Item | Antes | Depois |
|---|---|---|
| `rotulo_do_valor('…4 - Titular: X')` | `None` | `titular`/MEMBRO |
| Decisões do pipeline nos 150 e nos 21 | — | idênticas |
| Registro (relacoes/3) de val-087-A-r1, C2 | `desconhecido`, sem causa | `conflito`, causa `rotulo`, `necessaria=False`, `bloqueia=False` |
| `VERSAO_POLITICA` | `fail-closed-4.4.4b-cand` | `fail-closed-4.4.4d1-cand` |

## 7. Integridade e hashes (16 primeiros caracteres)

| Arquivo | 4B-cand (preservado) | 4D.1-pre | 4D.1 (novo) |
|---|---|---|---|
| `geracao.py` | `46862831592d09fc` | `46862831592d09fc` | `c857b99f49947e1a` |
| `evidencias.py` | `742031bb9934a3d9` | `742031bb9934a3d9` | `12118192b9529075` |
| `catalogo.py` | `8e44143ba1d092f5` | `8e44143ba1d092f5` | `8e44143ba1d092f5` (inalterado) |

Snapshots criados: `*_44_fase4d1_pre.py` (antes) e `geracao/evidencias_44_fase4d1.py` (depois); `*_44_fase4b_cand.py` e demais históricos não foram modificados. JSONL da validação (`cbb8482916d55050`, `c198f0893d40121f`) e manifesto (`43fb09685404714c`) inalterados. Novos hashes adicionados ao registro de referência; `verificar_hashes.py` → TODOS CONFEREM.

## 8. Limitações restantes

- A liberação indevida de val-087-A-r1 **persiste** (depende de mecanismo B/evidência positiva): resposta que localiza o conteúdo por um termo vindo da pergunta ("Gama") não torna o trecho conflitante "necessário". Requer decisão e testes próprios antes de qualquer alteração.
- Cobertura do parser limitada às formas listadas; índices alfabéticos (`a)`), duplos (`4.1 -`) e parênteses (`(4)`) não foram normalizados (fora da lista autorizada).
- Só um caso real exercita a mudança; não há estimativa de efeito em outros corpora.
- Pendentes, sem autorização: regra de relevância do catálogo (P1), associação de entidade por localidade (P4), evidência positiva (P3), taxonomia de status (P5).

Parei aqui; não avancei para catálogo ou associação de entidades.
