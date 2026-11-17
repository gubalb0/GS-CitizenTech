# Etapa 4.2 — Política conservadora de abstenção (identificabilidade da publicação)

**Status do Gen AI: experimental / em andamento.** Não está aprovado para integração ao Zelo/CitizenTech: falta revisão humana independente e validação de integração. A avaliação é **diagnóstica** (as 150 perguntas já foram usadas no retriever), a correção das respostas é por leitura minha e os campos de julgamento humano do CSV de auditoria estão **em branco**.

Código novo/alterado: `catalogo.py` (novo), `evidencias.py` (`tokens_especificos`), `geracao.py` (`_identificabilidade`, parâmetro `catalogo`), `avaliacao_e2e.py` · testes: `python -m pytest citizentech/assistente/tests -q` → **174 passam** (163 da 4.1 − 1 teste substituído + 12 novos em `test_abstencao_42.py`; mais 5 testes antigos ajustados de propósito) · retriever, índices, datasets originais, arquivos congelados do RPA **inalterados** (hashes conferidos) · conjunto de teste (350) **não usado** · prompt, modelo, runtime, parâmetros e orçamento de contexto iguais aos da 4.1.
Preservado sem sobrescrever: rodada `20261113-173721` (4.1), seu CSV de auditoria e relatórios, e snapshots em `data_assistente/versoes/` (código 4.1, `*_42_pre_execucao.py`).

## 1. Conferência da tabela de referência (4.1)
Antes de usar os números da 4.1, conferi o CSV `auditoria_e2e_20261113-173721.csv` e o `.jsonl`: 150 linhas; 2 respondida, 41 parcial, 58 ambigua, 35 insuficiente, 14 fora_do_escopo; grupo B: 0 completas e 19 parciais; abstenção 107/150 = 71,3%; latência de geração mediana 19,7 s e p95 29,5 s; 0 respostas sem evidência literal. **Os totais conferem.**

## 2. O que mudou e por quê
A 4.1 transformava "pergunta de resposta única sem número/data/documento" em `parcial` com aviso. A 4.2 **troca isso por um teste de identificabilidade**, que não olha só se a pergunta tem número ou data:
- **Catálogo do corpus** (`Catalogo`, somente leitura, 1.305 documentos canônicos, ~5 s para montar): dada a publicação citada pelo modelo, procura **outra** publicação (não duplicata) que (a) cubra todos os termos da pergunta que a citada cobre — nomes, números, ano, mês, palavras de conteúdo — **juntos numa janela de 1.500 caracteres** (documentos enormes com as palavras dispersas não contam) e (b) **não sustente o mesmo fato**: ficam de fora publicações que contêm os trechos de evidência citados (republicações, atos-modelo repetidos) ou todos os valores/ids/nomes específicos da resposta.
- **Se existe concorrente divergente** ⇒ `ambigua`, a mensagem lista a publicação e até 3 outras e pede data, número ou documento; **nenhum valor é entregue** (a informação encontrada fica só na telemetria como `resposta_modelo_descartada`). O mesmo vale para publicações concorrentes no contexto (a 4.1 mostrava "Na publicação X consta: …"; isso foi removido).
- **Se nenhuma concorrente** ⇒ resposta **completa** com `Fonte:` identificada, mesmo sem número ou data (pergunta geral/publicação única).
- **Sem catálogo** (ou publicação não avaliável): heurística conservadora — exige número, ano ou mês; sem isso, `ambigua`.
- **Preservado:** lista/MULTI continua `parcial` com aviso; perguntas compostas continuam sendo respondidas por partes independentes (`gerar_resposta_composta` repassa o catálogo); alinhamento, sustentação, rastreabilidade e verificação da 4.1 seguem valendo (nada é "completo" sem evidência literal e fonte identificada).

## 3. Testes obrigatórios (12 novos)
Pergunta específica sem identificadores suficientes → abstenção (sem entregar valor); com publicação identificável (inclusive por número) → resposta; duas publicações concorrentes no contexto → ambiguidade; pergunta geral com evidência → resposta (inclusive com republicação do mesmo ato); documento gigante com termos dispersos não é concorrente; concorrente que sustenta o mesmo fato não gera ambiguidade; MULTI/lista → `parcial` com aviso; composta → partes independentes; publicação errada com valor semelhante → bloqueio (alinhamento) ou abstenção; ausência da fonte correta → nenhuma resposta completa indevida; sem catálogo → heurística conservadora; unidades do catálogo. **Suíte completa: 174 passam.**

## 4. Os 16 casos reavaliados (rodada 4.2)
Casos que a 4.1 entregava como `parcial` por "escopo não especificado" (7 do grupo B e 9 do grupo A). "Correta" = minha leitura contra a referência do dataset, não auditoria independente.

| Pergunta | Grupo | Status 4.1 | Status 4.2 | Abstenção | Justificativa da decisão | Resposta correta deixou de ser entregue? |
|---|---|---|---|---|---|---|
| val-000 | A | parcial | **respondida** | não | publicação identificável: nenhuma concorrente divergente (1 concordante) | não |
| val-003 | A | parcial | **respondida** | não | publicação identificável (0 concorrentes) | não |
| val-006 | A | parcial | **respondida** | não | publicação identificável (0 concorrentes) | não |
| val-009 | A | parcial | ambigua | **sim** | 1 publicação do corpus cobre os termos sem sustentar o mesmo fato | **sim (perda potencial)** — a resposta (60 dias) estava correta |
| val-024 | A | parcial | **respondida** | não | publicação identificável (0 concorrentes) | não (ver §6: é MULTI) |
| val-041 | A | parcial | **respondida** | não | 0 divergentes; 46 concordantes (mesmo fato) | não |
| val-049 | A | parcial | **respondida** | não | 0 concorrentes | não |
| val-054 | A | parcial | **respondida** | não | 0 divergentes; 136 concordantes | não |
| val-128 | A | parcial | ambigua | **sim** | 1 publicação concorrente (outro chamamento do mesmo hospital) | **sim (perda potencial)** — R$ 2.550,00 estava correto |
| val-008 | B | parcial | ambigua | sim | 12 publicações concorrentes (Prontonorte) | n/a (a anterior era de outra publicação) |
| val-011 | B | parcial | ambigua | sim | 8 concorrentes | n/a |
| val-057 | B | parcial | ambigua | sim | 11 concorrentes | n/a |
| val-073 | B | parcial | ambigua | sim | 2 concorrentes | n/a |
| val-075 | B | parcial | ambigua | sim | 46 concorrentes | n/a |
| val-107 | B | parcial | ambigua | sim | 206 concorrentes (pergunta genérica) | n/a |
| val-082 | B | parcial | **respondida** | **não** | nenhuma concorrente encontrada pelo catálogo | n/a — **resposta de outra publicação entregue e, pior, como completa** |

- **Respostas corretas preservadas:** 7 de 9 do grupo A (agora completas, com fonte).
- **Potencialmente corretas perdidas:** 2 (val-009 e val-128), por haver outra publicação do corpus que cobre os termos sem conter o mesmo fato.
- **Incorretas de publicações concorrentes bloqueadas:** 6 de 7 do grupo B (val-008, 011, 057, 073, 075, 107).
- **Regressão:** val-082 (B) escapou do bloqueio e passou de `parcial` com aviso para `respondida` completa. O catálogo não achou outra publicação com os mesmos termos próximos; a referência lista vários motivos de cancelamento e a resposta citou um só. É um exemplo de falsa confiança que a regra **não** impede.
Detalhe em `data_assistente/derivados/casos16_42.json`.

## 5. Nova avaliação end-to-end (rodada única `20261114-014826`)
150/150 numa só rodada, sem retomar nem misturar execuções; 0 erros técnicos; JSON válido 150/150; 0 tokens de raciocínio; mesmo modelo/quantização (Qwen3-8B Q4_K_M), LM Studio 0.4.28 / llama.cpp Vulkan 2.73.0, `parallel` 1, contexto 8192, T 0,3, prompt v3, mesmo retriever (est300o30, BM25, top-5) e orçamento (~3K tokens; prompt real mediana 2.540, máx. 3.052). Política `fail-closed-4.2`; parâmetros, hashes dos arquivos e catálogo em `geracao_e2e_41_20261114-014826.meta.json`. O grupo (A/B) de cada pergunta é idêntico ao da 4.1 (0 mudanças), pois o contexto enviado foi o mesmo.

| Métrica | Etapa 4.1 | Etapa 4.2 |
|---|---:|---:|
| Respostas completas | 2 | **10** |
| Respostas parciais | 41 | **24** |
| Ambíguas | 58 | **67** |
| Insuficientes | 35 | 35 |
| Fora do escopo | 14 | 14 |
| Respostas do grupo B | 0 completas, 19 parciais | **1 completa, 12 parciais** |
| Abstenção total (ambigua+insuficiente+fora) | 71,3% (107) | **77,3% (116)** |
| Respostas dadas (completas+parciais) | 43 | 34 |
| Respostas sem evidência verificável | 0 | 0 |
| Latência de geração, mediana | 19,7 s | 21,0 s |
| Latência de geração, p95 | 29,5 s | 31,8 s |
Grupo A (fonte correta enviada, 76): 9 respondida, 12 parcial, 36 ambigua, 18 insuficiente, 1 fora_do_escopo. Grupo B (74): 1 respondida, 12 parcial, 31 ambigua, 17 insuficiente, 13 fora_do_escopo. Por que a latência subiu: o teste de identificabilidade (catálogo) roda em cada resposta dada. Memória: `llama-server` até 8,4 GB de RSS, RAM livre do sistema mínima ~196 MB, VRAM do adaptador 7,2–7,6 GB.

## 6. MULTI e perguntas compostas
- **MULTI (41):** 17 insuficiente, 14 parcial (todas com aviso), 5 ambigua, 4 fora_do_escopo e **1 respondida** (val-024). O contexto enviado cobre todas as publicações esperadas em só 4 das 41.
- **Regra 5 não é atendida por inteiro:** val-024 tem 5 publicações esperadas e só 1 no contexto, mas a pergunta foi redigida como resposta única ("Qual foi a modificação contratual…") e a publicação citada é identificável; saiu **completa**. Em produção o assistente não sabe se a pergunta é "MULTI" (isso é um rótulo do dataset), e a 4.1 só a marcava `parcial` pelo aviso de escopo que a 4.2 removeu. Perguntas de lista ("Quais…") continuam `parcial`.
- **Compostas:** cobertas por testes (partes independentes, sem falso conflito); nenhuma das 150 é composta.

## 7. Comparação detalhada e regressões
- Transições 4.1→4.2: ambigua→ambigua 58; insuficiente→insuficiente 32; parcial→parcial 21; fora→fora 14; **parcial→ambigua 9**; **parcial→respondida 8** (7 corretas do A e val-082); parcial→insuficiente 3; insuficiente→parcial 3; respondida→respondida 2 (val-002 e val-090, ambas corretas).
- **Regressões (abstenção→resposta dada):** 3 perguntas (val-026, val-047, val-112) passaram de `insuficiente` para `parcial`. Não vêm da regra nova (que só abstém): vêm de variação do modelo (T 0,3) e dos filtros de verificação. Val-026 é do grupo B (nova resposta dada sem a fonte correta, `parcial`).
- **A abstenção aumentou** de 71,3% para 77,3% (+9 perguntas), principalmente pelas 9 conversões `parcial→ambigua` (8 dos 16 casos + 1 fora deles). As respostas dadas caíram de 43 para 34 e, no grupo B, de 19 para 13.
- Taxa de respostas dadas sem fonte correta: 13 de 34 (38%) contra 19 de 43 (44%).

## 8. Limitações e riscos restantes
1. **1 resposta de outra publicação ainda sai como completa** (val-082) e outras 12 do grupo B saem como lista `parcial`; a regra só vê o que existe no corpus, não o que o gabarito espera.
2. **2 respostas potencialmente corretas foram perdidas** (val-009, val-128) e o assistente passa a pedir esclarecimento mesmo quando o cidadão não tem como informar data ou número.
3. Val-024 mostra que MULTI redigido como pergunta única pode sair completo.
4. As heurísticas são lexicais: termos salientes, palavras de conteúdo (prefixo de 6 letras), janela de 1.500 caracteres, "elementos específicos" da resposta. Sinônimos, siglas e documentos com redação diferente podem gerar falsos concorrentes ou falsos "únicos". Exige acesso ao texto do corpus em produção.
5. Variação entre rodadas: com T 0,3 o mesmo conjunto pode produzir respostas diferentes (as 3 regressões); uma rodada não é uma distribuição.
6. As 150 perguntas já foram usadas no retriever; o julgamento de correção é meu; os gabaritos vêm de um dataset gerado por LLM; nenhuma auditoria independente foi feita.
7. Consumo de RAM alto para 16 GB; urgência clínica continua fora do gerador (RPA).

## 9. Material de auditoria
`docs/assistente/auditoria_e2e_20261114-014826.csv` (+ guia `auditoria_e2e_20261114-014826.md`): 150 linhas por prioridade, com as **34 respostas dadas** e as **67 ambíguas** para revisão obrigatória e 49 abstenções para amostragem; colunas de julgamento humano **vazias**. A auditoria da 4.1 (`auditoria_e2e_20261113-173721.*`) foi preservada.

## 10. Próximos passos sugeridos (dependem de você)
Revisão humana independente das 101 linhas de prioridade 1 e 2; decidir se o assistente deve fazer pergunta de esclarecimento estruturada (data/número/documento) quando devolve `ambigua`; decidir como tratar perguntas MULTI redigidas como única (por exemplo, marcar `parcial` quando o catálogo achar várias publicações sobre o mesmo assunto); coletar perguntas reais fora do conjunto de validação.
