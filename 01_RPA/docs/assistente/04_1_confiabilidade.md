# Etapa 4.1 — Correções de confiabilidade do gerador

Código: `citizentech/assistente/evidencias.py` (novo), `geracao.py`, `avaliacao_geracao.py`, `avaliacao_e2e.py`, `auditoria.py` · testes: `python -m pytest citizentech/assistente/tests -q` (**163 passam**: 137 anteriores + 26 novos) · retriever, índices, dados e arquivos congelados do RPA **inalterados** (hashes conferidos); conjunto de teste (350) **não usado**; nenhum modelo novo, nenhuma API paga.
Versões anteriores preservadas em `data_assistente/versoes/` (código e relatório da Etapa 4, snapshot do código e dos critérios **antes** da execução 4.1) e em `data_assistente/derivados/` (`geracao_isolada_v1.jsonl`, `geracao_isolada_etapa4_v2.jsonl`, `geracao_e2e_etapa4_final.jsonl` e as execuções parciais da Etapa 4).

> **Resumo honesto.** A etiqueta "resposta completa sem fonte correta" **foi eliminada** (0 de 74 perguntas do grupo B; eram 19). Mas **19 respostas de outra instância da pergunta continuam sendo entregues** no grupo B — agora sempre como `parcial`, com a publicação identificada e um aviso explícito. **Isso não é a mesma coisa que não responder**, e 44% das respostas dadas (19/43) vêm de perguntas sem a fonte correta. Dos 150 casos, só 2 saem como `respondida` (completa). O sistema ficou muito mais conservador, não necessariamente mais certo.
> A avaliação end-to-end é **diagnóstica** (as 150 perguntas já foram usadas no retriever). Julgamento de correção por leitura minha, sem auditoria de terceiros.

## 1. Diagnóstico das 19 falsas respostas (antes de editar)
- Releitura de `04_gerador.md`, `geracao.py` (verificador, prompt, testes) e dos dados da execução final da Etapa 4.
- **Em todas as 19 respostas, a evidência citada continha todos os termos salientes da pergunta** (nomes próprios, números, período). O modelo não "inventou": **escolheu uma publicação real, do mesmo hospital e do mesmo tipo, que não era a esperada**. Em 7 delas a pergunta era de resposta única ("Quem foi responsável…", "Qual o valor da dívida do Hospital Prontonorte?", "Qual a vigência…") e em 12, de lista ("Quais…").
- **Como o modelo escolhe:** com 3–5 chunks de publicações semelhantes (reconhecimentos de dívida, chamamentos, extratos do mesmo hospital), ele cita o trecho que melhor casa com as palavras da pergunta; a posição do chunk citado foi variada (posições 1 a 4). Nada na pergunta (sem número, data ou documento) distingue uma publicação da outra, e o gabarito exige **uma** instância específica.
- **Por que o verificador da Etapa 4 não pegou:** ele só garantia (a) que o trecho citado existe literalmente no chunk e (b) que números da resposta existem em algum chunk citado. Ambas as condições eram satisfeitas. Não havia verificação de que a evidência correspondesse à pergunta (alinhamento), nem de que nomes da resposta estivessem na evidência, nem de que **outra** publicação igualmente relevante estivesse presente, nem aviso de escopo ou de completude.
- **Limite do que o código consegue saber:** nos casos em que a publicação esperada nem foi recuperada, nada no contexto revela a existência dela. Só é possível (i) exigir que a resposta identifique a publicação, (ii) declarar que a pergunta não a especifica e (iii) abster-se quando há concorrentes no contexto.

## 2. Alterações implementadas (todas no código, depois da geração)
| Regra | Onde | O que faz |
|---|---|---|
| Rastreabilidade | `metadados_completos` | Fonte citada sem `doc_id`, edição, data, seção ou referência/número → resposta reprovada. |
| Sustentação das afirmações | `afirmacoes_nao_sustentadas` | Números e nomes da **resposta** precisam estar nos **trechos de evidência citados** (ou nos metadados confiáveis da publicação), não apenas em algum lugar do chunk. |
| Alinhamento pergunta × evidência | `alinhamento` | Todos os nomes próprios, números/ids, anos e meses da pergunta precisam constar na publicação citada (texto, cabeçalho, localidades). Falha ⇒ `insuficiente` (ex.: pede "Chamamento nº 270/2025" e a fonte é o nº 259/2025; valor correto de outro hospital; data de outro período). |
| Publicação concorrente | `publicacoes_concorrentes` | Em pergunta de resposta única: outra publicação (doc diferente, não duplicata) no contexto que cobre **todos os termos que a citada cobre** ⇒ `ambigua`, listando as publicações; a resposta do modelo aparece só como "Na publicação X consta…". |
| Divergências | `classificar_divergencia` | Distingue `duplicadas` (não é conflito), `respostas_equivalentes`, `periodos_diferentes` (apresentadas com as datas), `divergentes_mesmo_periodo` (conflito sobre o mesmo fato) e `sem_divergencia`. |
| Perguntas compostas | `dividir_pergunta_composta`, `gerar_resposta_composta` | Cada parte é recuperada e respondida **separadamente**; fontes de partes diferentes nunca são tratadas como conflito (corrige o erro do G1). |
| Taxonomia | status `parcial` | Lista/MULTI ("Quais…") é **sempre** `parcial` com aviso fixo (completude não verificável); pergunta de resposta única **sem número, data ou documento** também é `parcial`, com aviso de escopo ("refere-se apenas à publicação abaixo; podem existir outras semelhantes"). `respondida` (completa) só com discriminador. |
| Identificação da publicação | `compor` | Toda resposta dada traz `Fonte:` com tipo, referência, edição, data e seção, montada **dos metadados**, não do texto do modelo. |
| Prompt v3 | `PROMPT_SISTEMA` | Acrescenta `parcial` e a regra de usar `respondida` só se todos os pontos forem sustentados. |
| Telemetria | `gerar_resposta` | Versões do prompt e da política, `scores_recebidos`, `divergencia`, `publicacoes_concorrentes`. |
Efeito colateral aceito: o contexto passou a trazer metadados `localidades`/`tipo_unidade` no alinhamento; e quando as publicações citadas são rebaixadas por política, o texto do modelo fica só em `justificativa`.

### Limiar BM25 (investigado, **não adotado**)
Calculei, sobre as 150 perguntas, o score do 1º chunk, a diferença para o 2º e um score relativo (top-1 ÷ limite superior dado pelos pesos IDF dos termos da consulta). AUC para "há fonte correta nos 5 chunks": top-1 0,76; relativo 0,70; diferença 0,68; para "fonte correta em 1º": 0,83 / 0,67 / 0,73. Limiares **relativos fixados antes de olhar os dados** (0,3 / 0,5 / 0,7): com 0,3 descartam-se 22 consultas (16 sem fonte, 6 com) e **45 das 61 sem fonte continuam passando**; 0,5 corta 129 de 150; 0,7 corta 149. Mediana do score top-1: 27,7 (fonte correta enviada) contra 20,2 (sem). **Conclusão:** o score separa moderadamente, mas não o bastante para servir de portão (perderia respostas corretas e deixaria passar a maioria das erradas), e uma pontuação alta não prova correção. Ele fica **registrado na telemetria** (`scores_recebidos`) e no arquivo de auditoria, sem decidir nada.

## 3. Testes novos (26, `tests/test_politica_evidencias.py`)
Tipo da pergunta; termos salientes e período; divisão de pergunta composta; classificação de divergências (5 tipos); **publicação semelhante com valor diferente**; **publicação correta ausente**; **valor correto associado à publicação errada**; **data de outro período**; **citação existente que não sustenta a afirmação** (nome e valor); rastreabilidade incompleta; identificação da publicação na resposta; conflito no mesmo período; períodos diferentes com datas; duplicadas sem conflito; concorrente igualmente relevante; número da pergunta distingue a publicação; publicação que não cobre os termos não é concorrente; lista nunca completa; `parcial` do modelo mantido e verificado; composta independente (não é conflito), composta com parte sem evidência, composta simples delega; escopo explícito sem discriminador; taxonomia e telemetria. Ajustei 4 testes antigos cujo comportamento mudou de propósito (por exemplo, "Quais valores…" agora é `parcial`).

## 4. Avaliação controlada (isolada)
48 casos (39 da Etapa 4 + 9 novos) × 2 repetições; 86 chamadas ao modelo + 10 saídas simuladas. **Critérios dos casos novos fixados no código antes da execução** (snapshot em `data_assistente/versoes/avaliacao_geracao_41_criterios_pre_execucao.py`). Única alteração dos critérios antigos, registrada: nos casos originais, `parcial` conta como `respondida` (alias), pois o status não existia. Não ajustei nenhum critério depois.

| Conjunto | Aprovados | Falsa confiança | Observações |
|---|---|---|---|
| Etapa 4 v2 (mesmo julgador, casos originais, 78 exec.) | 73 | 0 | resultado anterior |
| **4.1, casos originais (78 exec.)** | **70** | **0** | A3 rebaixada ×2; A5 `insuficiente`/`ambigua`; B1 `fora_do_escopo` ×2 (rótulo); H3 repetiu o comando na justificativa ×2 |
| **4.1, casos novos (18 exec.)** | **18** | **0** | ver abaixo |
Novos: publicação semelhante com valor diferente (2/2 `insuficiente`); publicação correta ausente (2/2 abstenção); duas publicações, perguntas independentes (2/2 `respondida` com os dois valores, sem conflito); MULTI com parte das fontes (2 `parcial` com aviso, 2 `insuficiente`; nunca `respondida`); citação existente que não sustenta (simulada, 2/2 `insuficiente`); valor correto da publicação errada (simulada, 2/2); valor de outro período (simulada, 2/2); evidência contraditória no mesmo período (2/2 `ambigua`).
**Leitura:** a política bloqueou todos os cenários adversariais, mas **não melhorou** o conjunto original (70 contra 73) — a diferença vem de rótulos (`fora_do_escopo` em vez de `insuficiente`) e do conservadorismo. Os cenários simulados testam o verificador, não o modelo. Os casos novos foram escritos por mim sabendo da política.

## 5. Avaliação end-to-end reproduzível (rodada única `20261113-173721`)
- **Identificação:** prompt v3, política `fail-closed-4.1`, Qwen3-8B Q4_K_M, LM Studio 0.4.28/llama.cpp Vulkan 2.73.0, `parallel` 1, contexto 8192, T 0,3, `max_tokens_saida` 1100; sha256 de `geracao.py`/`evidencias.py`/`avaliacao_e2e.py` e parâmetros em `geracao_e2e_41_20261113-173721.meta.json`. Retriever: est300o30, BM25, top-5 (congelado). **150/150 em uma só rodada, sem retomar nem misturar execuções, 0 erros técnicos, JSON válido 150/150, 0 tokens de raciocínio.**
- Prompt real mediana 2.540 tokens (p95 2.854, máx. 3.052); chunks enviados: 3 em 102, 4 em 34, 5 em 9 e 2 em 5 das perguntas.

| Grupo | n | respondida | parcial | ambigua | insuficiente | fora_do_escopo |
|---|---|---|---|---|---|---|
| **A** — fonte correta enviada | 76 | 2 | 22 | 33 | 18 | 1 |
| **B** — sem fonte correta | 74 | **0** | 19 | 25 | 17 | 13 |
| MULTI (41) | 41 | 0 | 16 | 5 | 16 | 4 |
Total: 2 respondida, 41 parcial, 58 ambigua, 35 insuficiente, 14 fora_do_escopo.

- **As 19 falsas respostas da Etapa 4:** 14 viraram `parcial` (com publicação identificada e aviso) e 5 `insuficiente` (afirmações não sustentadas pela evidência). **As 7 de resposta única (val-008, 011, 057, 073, 075, 082, 107) continuam sendo entregues com informação de outra publicação** — por exemplo val-057: R$ 5.205.150,00 contra R$ 153.720,63 na referência; val-107: 12 meses contra 60. Agora vêm com "ATENÇÃO: a pergunta não informa data, número ou documento; esta resposta refere-se apenas à publicação identificada…".
- **Respostas sem evidência verificável:** 0 de 43 (todas as dadas têm trecho literal e `Fonte:` identificada). **Respostas dadas sem a fonte correta:** 19 de 43 (44%); no grupo B, 19 de 74 (26%), todas `parcial`.
- **Taxa de abstenção** (ambigua + insuficiente + fora_do_escopo): 107/150 (71%). Rebaixadas pela política: 17. `ambigua` convertida por regra: 2 (publicações semelhantes). Problemas de verificação mais frequentes: afirmações não sustentadas pela evidência (10), trecho não literal (7), alinhamento (2).
- **Grupo A (fonte correta enviada, 76):** só 24 respostas dadas; pela minha leitura, 13 são respostas únicas corretas (como val-000, 002, 009, 024, 041, 049, 090, 128) e 11 são listas parciais; 33 `ambigua`. **O sistema abstém-se ou qualifica muito, inclusive quando tem a fonte.**
- **MULTI (41):** o contexto enviado cobre todas as publicações esperadas em **só 4**; o gerador deu 16 respostas, **todas `parcial` com aviso** (0 completas), e nenhuma foi apresentada como completa. Não inventa o número de fontes: a mensagem diz que a lista não é exaustiva.
- **Pares não unívocos:** as 6 perguntas saíram `ambigua`.
- **Latência/memória:** geração mediana 19,7 s (p95 29,5 s, máx. 37,6 s). `llama-server` chegou a **8,2 GB de RSS** e a RAM livre do sistema a **~180 MB**; VRAM do adaptador 7,6–7,8 GB (jogo fechado). O servidor não caiu desta vez.

## 6. Tratamento de MULTI e respostas parciais
Taxonomia implementada: **completa** (`respondida`, só com discriminador e sem lista), **parcial** (lista/MULTI ou escopo não especificado), **insuficiente**, **ambígua**, **fora do escopo**. O código não tenta saber quantas publicações a pergunta exige: toda lista é tratada como não exaustiva. Deterministicamente (metadados) só é possível checar identificação, período e nomes; não é possível provar completude.

## 7. Limitações e riscos restantes
1. **Respostas de outra instância ainda saem como `parcial`** (7 de resposta única no grupo B e 12 listas). Uma política mais dura seria abster-se em pergunta de resposta única sem discriminador (`escopo_nao_especificado`: 16 casos, 7 no grupo B e 9 no A). **Não adotei sem sua decisão** porque aumentaria a abstenção para ~82% e descartaria 9 respostas corretas do grupo A.
2. Só 2 respostas `respondida`: "completa" praticamente depende de a pergunta citar número/data/documento, o que perguntas de cidadãos raramente fazem.
3. Os cenários simulados e os casos novos foram escritos por mim; o conjunto de 150 já foi usado no retriever; os gabaritos são de um dataset gerado por LLM.
4. Mais um desvio: a regra de concorrentes e o alinhamento usam heurísticas lexicais (nomes próprios, números, prefixos de 6 letras) e podem errar com siglas, sinônimos e perguntas sem nomes.
5. O rótulo `insuficiente` × `fora_do_escopo` continua inconsistente; o modelo ainda ecoa comandos do usuário na `justificativa` (interna).
6. O consumo de RAM é alto para 16 GB; a urgência clínica continua fora do gerador (RPA).
7. A correção de cada resposta ainda **não foi auditada por terceiros**.

## 8. Material para auditoria independente
`docs/assistente/auditoria_e2e_20261113-173721.csv` (+ guia `.md`): 150 linhas (`;`, UTF-8 com BOM) ordenadas por prioridade — **43 respostas dadas** e **58 ambíguas** destacadas para revisão obrigatória, 49 abstenções para amostragem. Colunas: pergunta, fontes recuperadas (enviadas marcadas), resposta, status, evidências, fontes citadas, verificação automática, justificativa, referência do dataset (marcada como gerada por LLM) e campos **em branco** para julgamento humano (correta/incorreta/parcial/ambígua adequada…, "sustentada na fonte citada?", "publicação certa?", observações, revisor). Nenhum dado pessoal.

## 9. Recomendação
**Não integrar.** Decisões pendentes (suas): (1) tornar `escopo_nao_especificado` abstenção em vez de `parcial` (mais seguro, menos útil); (2) a auditoria humana das 101 linhas de revisão obrigatória antes de qualquer afirmação de correção; (3) decidir se o assistente deve incentivar o cidadão a informar data/número/documento (pergunta de esclarecimento) — hoje a resposta já pede isso nos casos `ambigua`; (4) corpus gov.br/SUS e perguntas reais de cidadãos para uma avaliação independente.
