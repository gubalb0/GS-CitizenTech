# Fase 4B — Integração da S1 conservadora (versão CANDIDATA, não validada)

Escopo autorizado: implementação e validação **offline**. Versão em código: `fail-closed-4.4.4b-cand` (candidata). **Nenhuma geração foi executada; LM Studio e APIs de modelo não foram usados; a flag `priorizar_atributo` permanece `False` por padrão; nenhuma pergunta foi regenerada; nenhuma rodada end-to-end.**

## 1. Preservação e hashes (SHA-256, 16 primeiros caracteres)

Antes de alterar: `verificar_hashes.py` → TODOS CONFEREM; arquivos vivos idênticos aos snapshots `*_44_fase4b.py` (4B-prep).

| Arquivo | 4A (`*_44_fase4a.py`) | 4B-prep (`*_44_fase4b.py`, preservado) | 4B-cand (novo: `*_44_fase4b_cand.py`) |
|---|---|---|---|
| `geracao.py` | `bbd28166f0db19c3` | `0891e70c01600054` | `46862831592d09fc` |
| `evidencias.py` | `be8ac1dd9a2bdde6` | `93363fab9f1a7f37` | `742031bb9934a3d9` |
| `catalogo.py` | `8e44143ba1d092f5` | `8e44143ba1d092f5` | `8e44143ba1d092f5` (inalterado) |

Nenhum snapshot histórico foi sobrescrito. Incluídos no manifesto `hashes_referencia_44.json`: os dois snapshots `_cand` e os documentos/protótipo (`s1_conservadora_proto.py` `d3232f79…`, `AVALIACAO_S1_CONSERVADORA.md` `eea79e6c…`, `AUDITORIA_S1_CASOS_PENDENTES.md` `aa4da57c…`, `FASE4B_PREPARACAO.md` `16ae9196…`). Pós-integração: `verificar_hashes.py` → **TODOS CONFEREM: True** (inclui o RPA congelado).

## 2. Arquivos alterados

- `evidencias.py`: acréscimo de `cobertura_do_chunk(texto, cab, fam, nomes)` e `_QUANTIA` (lógica idêntica ao protótipo).
- `geracao.py`: em `montar_contexto`, antes de promover, calcula a cobertura dos chunks já selecionados (`EV.cobertura_do_chunk` sobre o texto original do resultado); se algum cobre, devolve a seleção original e registra em `Contexto.selecao` "promocao redundante evitada: o contexto ja cobre o atributo (chunk:tipo)". Caso contrário, mantém o comportamento da S1 já existente (promove à frente os chunks de rótulo forte descartados; orçamento e ordem relativa dos demais preservados). `VERSAO_POLITICA = "fail-closed-4.4.4b-cand"`.
- Testes: novo `test_fase4b_s1_conservadora.py`; ajustes só de expectativa intencional: `test_politica_evidencias.py` (rótulo da versão) e `test_fase4b_selecao.py` (a S1 pura mudava 6 contextos; a integrada muda 2 — registrado no próprio teste e na avaliação anterior, não é adaptação para esconder divergência: o resultado coincide exatamente com o do protótipo).
- Não tocados: BM25/embeddings/RRF/índices/corpus/chunking, gabaritos, RPA congelado, rodadas/auditorias/snapshots/protótipos/relatórios anteriores.

## 3. Lógica integrada (exatamente a validada no protótipo)

Um chunk **cobre** o atributo se (a) todos os nomes salientes da pergunta estão no próprio chunk e (b) há rótulo forte em posição de rótulo, ou (c) somente para a família VALOR, `R$ n` em prosa. Sem forma tipada confiável, as demais famílias não presumem cobertura sem rótulo. A função só recebe `texto, cab, fam, nomes` (nada do gabarito; teste verifica a assinatura e o código-fonte). **Critério estrutural, não garantia semântica.**

## 4. Testes

- **Suíte completa: 325 passando** (311 anteriores + 14 novos). Inclui T1–T6 do mecanismo B v2, `relacoes/3`, o replay 4A da suíte.
- Novos (`test_fase4b_s1_conservadora.py`): os 6 cenários sintéticos + unitário de cobertura estrutural + teste de flag desligada/não uso de gabarito (os 8 do protótipo); regressões nos 150: val-011, val-080, val-125, val-133 (promoção redundante evitada, contexto idêntico), val-074 (promove `dodf-28:0000`), val-087 (inclui `174:0002` e `174:0003`), e o conjunto: só val-074 e val-087 mudam, 148 idênticos, orçamento ≤ 3.000, ordem relativa preservada, `selecao == []` com flag desligada.
- Flag desligada por padrão: `ConfigGeracao().priorizar_atributo is False`; comportamento anterior preservado (replay e `selecao == []`).

## 5. Validação offline dos 150

**Replay contra a baseline 4A** (flag desligada, saídas gravadas do modelo; sem modelo): **0 diferenças** em status, resposta e problemas.

**Seleção — baseline 4A × S1 atual (4B-prep) × S1 conservadora integrada** (`fase4b_integracao_comparacao.py/.json`):

| | S1 atual | S1 conservadora |
|---|---|---|
| Contextos alterados | 6 (011, 074, 080, 087, 125, 133) | **2 (074, 087)** |
| Inalterados | 144 | **148** |
| Chunks promovidos | — | 074: `dodf-28:0000`; 087: `dodf-174:0002`, `dodf-174:0003` |
| Promoções redundantes evitadas | — | 011, 080, 125, 133 |
| Orçamento máximo (tokens) | 2.998 | 2.998 (observado; ≤ 3.000) |
| Respostas entregues na 4.3 afetadas | 0 | 0 |
| Grupos A/B | 074 B→A; 080 B→A | 074 B→A; **080 permanece B** |
| Divergência do protótipo | — | **nenhuma** |

Tokens (baseline / atual / conservadora): 074 2916/2985/2985; 087 2948/2928/2928; os demais coincidem com a baseline na conservadora. val-080 segue sem resolução: o chunk do gabarito (407) é um quarto registro equivalente e não é promovido de propósito.

## 6. Limitações da cobertura estrutural

- Não é cobertura semântica: não verifica que o rótulo ou o `R$` respondem à pergunta; um `R$` incidental no chunk da entidade (multa, valor global) conta como cobertura de VALOR.
- Sem rótulo explícito, endereço/objeto/competência etc. em prosa não são reconhecidos como cobertos (pode manter promoção redundante, como no S1 anterior).
- A associação à entidade usa nomes salientes da pergunta; entidades homônimas podem passar.
- Não resolve conflito entre evidências nem escolhe entre registros equivalentes (val-080); não usa gabarito.
- Efeito sobre as respostas **não medido** (sem modelo); evidência de contexto apenas em 150 perguntas e 2 casos alterados.

## 7. Estado e confirmações

- Versão **candidata `fail-closed-4.4.4b-cand`**, não validada. `fail-closed-4.4.4a` e `4.4.4b-prep` preservadas nos snapshots.
- Flag `priorizar_atributo` **desligada por padrão**; nenhuma geração executada; nenhuma pergunta regenerada; nenhuma rodada end-to-end. A validação com modelo depende de autorização explícita posterior.
