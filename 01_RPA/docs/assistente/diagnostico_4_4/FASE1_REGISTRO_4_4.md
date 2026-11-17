# Versão 4.4 — Fase 1 (integridade e medição)

A versão 4.3 permanece como referência: `geracao.py`, `evidencias.py` e `catalogo.py` **não foram alterados** (idênticos aos snapshots `*_43_pre_execucao.py`). Resultados das rodadas anteriores intactos (hashes em `hashes_referencia_44.json`, conferidos).

| # | Problema original | Correção aplicada | Testes adicionados | Resultado | Risco de regressão |
|---|---|---|---|---|---|
| 1 | Erros de atribuição na auditoria (val-050, 062, 097) | `ERRATA_AUDITORIA_4_3.md`; auditoria original não editada | — (documento; dado de apoio reproduzível por `scripts/recalcular_grupos.py`) | — | Nenhum |
| 2 | `enviado`/grupo A/B calculados como prefixo do ranking (`res[:n_env]`, `posicao <= n_env`); `montar_contexto` pula chunks que estouram o orçamento | Novo `citizentech/assistente/grupos.py` (`itens_enviados`, `grupo_ab`, `marcar_enviados`); `avaliacao_e2e.main` passa a usá-lo, falha se a reconstrução divergir da telemetria e grava `metodo_envio` | `tests/test_grupos_44.py` (9): contexto não-prefixo; falso A e falso B do método antigo; flag por `chunk_id`; duplicatas equivalentes; contagem de esperadas; divergência com a telemetria falha; `avaliacao_e2e` não contém mais o prefixo; regressão real val-097 (rodada original preservada como B, recalculada como A) | Passam | Baixo: só a medição muda; o gerador não. Novas rodadas gravam 1 campo extra |
| 3 | Sem teste contra esse erro | Item acima | Item acima | — | — |
| 4 | Rotina de hashes reescrevia `chunks_exemplos.json` | `scripts/verificar_hashes.py` somente leitura (modo `rb`, nunca grava); rotina avulsa substituída por redirecionamento | `tests/test_verificar_hashes_44.py` (5) | Passam | Baixo; manifesto novo pode acusar diferença legítima se artefatos mudarem (por desenho) |
| 5 | Sem hash/snapshot de `chunks_exemplos.json` | SHA-256 `8c9d583a…2f37` em `hashes_referencia_44.json` + `INTEGRIDADE_ARTEFATOS.md` (limitação documentada) | coberto em `test_verificar_hashes_44.py` | Passam | Nenhum |

Resultado da recalculagem (arquivo novo `grupos_ab_corrigidos_20261114-130608.json`): grupos 76/74 → **77/73**; só val-097 muda; 11 casos com contexto não-prefixo.
Suíte do Gen AI: **199 passam** (185 anteriores + 14 novos). Hash do RPA congelado e dos 27 artefatos: confere.
Snapshot do avaliador pré-correção: `data_assistente/versoes/avaliacao_e2e_etapa4_3.py`.
