# Relatório de correção documental — pós-auditoria final

Data: 11/11/2026. Escopo: correções documentais autorizadas após `docs/auditoria_final_entrega.md`. **Nenhum arquivo de implementação, dado, teste, modelo ou regra foi alterado.** A redação sobre **autoria e uso de IA não foi alterada**. **Nenhuma operação de Git que modifique o repositório foi feita.** Aguardo nova autorização antes de qualquer outra alteração.

## 0. Resumo executivo (atualizado na rodada 3, 11/11/2026)
- **Três rodadas de correção documental** foram feitas, todas somente em documentos: (1) correção do checklist corrompido, dos integrantes, do README, da matriz, das divergências numéricas, do ambiente limpo e das perguntas da banca (seções 1 a 6); (2) correção de `docs/auditoria_ia.md`, do Plano B do roteiro e da explicação das falhas HTTP (seção 7); (3) **revisão com o PDF oficial da Global Solution 2026.2**, que não estava disponível antes (seção 8).
- **Estado da documentação:** coerente entre si e fiel às duas fontes oficiais (PDF e complemento), conforme as verificações das seções 5, 7.4 e 8.8. Código, modelo, dados, regras, testes e scripts permaneceram intactos (6 de 6 hashes; 21 testes passando).
- **Estado da entrega: NÃO PRONTA (PENDENTE).** O PDF oficial identifica **43 requisitos**: **17 atendidos, 12 parcialmente atendidos, 11 não atendidos e 3 não comprovados** *[reclassificado na rodada 4: **18 · 11 · 10 · 3** de 42 requisitos avaliáveis, mais 1 N/A (F25); ver a seção 9]*. A atividade da disciplina 01 está parcialmente atendida; a **disciplina integradora 06** (vídeo ≤ 7 min, ABNT, GitHub, módulos integrados) e o **prêmio** (vídeo pitch) **não estão atendidos**. O **prazo é 19/11/2026 às 23h55** (Portal do Aluno) e nenhum envio foi feito.
- **O que depende da equipe:** declaração única de autoria e uso de IA; temas oficiais (confirmar com o professor o que conta como tema); turma; data da apresentação; commit e publicação; envio ao Portal; decisão sobre disciplina 06, prêmio e a documentação de acessibilidade, sustentabilidade, viabilidade e escuta de usuários (seção 8.5).

## 1. Arquivos
### 1.1 Backups (criados antes de qualquer edição)
Pasta `_backup_docs_pre_correcao_2026-11-11/` (na raiz; incluída no `.gitignore`, para não ser versionada), com cópia, preservando datas, de: `README.md`, `.gitignore`, `docs/checklist_entrega.md`, `docs/matriz_requisitos.md`, `docs/roteiro_apresentacao.md`, `docs/perguntas_banca.md`, `docs/diagnostico.md`, `docs/evidencias.md`, `docs/auditoria_ia.md`, `docs/etica_ods.md`, `docs/temas.md`. O arquivo `_SHA256_originais.txt` registra o hash (16 primeiros caracteres) de cada cópia. A pasta pode ser apagada pelo grupo depois da revisão.

### 1.2 Modificados
| Arquivo | O que mudou |
|---|---|
| `docs/checklist_entrega.md` | Linhas 54–59 recuperadas (item A); integrantes (item B); linha de ambiente limpo (item F); rótulo "extra" nas capturas `1b` e `4b` (consistência com o README) |
| `README.md` | `saida/o*.csv` → `saida/*.csv`; "11 imagens" → 13 arquivos (10 obrigatórias + 3 extras); afirmações de ambiente limpo contextualizadas; "versão anterior" marcada como não reproduzível; nota sobre a definição de "automático" |
| `docs/matriz_requisitos.md` | Linha do requisito de entrega por Git (**PENDENTE**), com implementado × evidenciado × pendente; integrantes; ambiente limpo contextualizado |
| `docs/roteiro_apresentacao.md` | Campo Integrantes (linha 3) |
| `docs/perguntas_banca.md` | Campo Integrantes (linha 4); Q1, Q3, Q13 e Q15 contextualizadas; nova seção **F** (Q22–Q28) |
| `docs/diagnostico.md` | Nota de atualização de 11/11/2026 no risco "(4) integrantes não informados" (o texto original foi preservado) |
| `docs/evidencias.md` | Contexto nas linhas de falhas HTTP, "versão anterior", "confiança ≥ 0,45" e "7 tinham confiança ≥ 0,45"; nova seção **"Esclarecimentos sobre contagens"** |
| `.gitignore` | Uma linha: `_backup_docs_pre_correcao_*/` |

### 1.3 Criados
`docs/relatorio_correcao_documental.md` (este relatório) e a pasta de backup.

### 1.4 Deliberadamente não modificados
`data/modelo/classificador.joblib`, `data/treino.csv`, `data/teste_rotulado.csv`, `data/teste_cego.csv`, `citizentech/*`, `scripts/*`, `tests/*`, `main.py`, `validacao_independente/*`, `docs/modelo_congelado.json`, `docs/auditoria_ia.md`, `docs/etica_ods.md`, `docs/temas.md`, `docs/evidencias_resultados.md/.json` e `docs/auditoria_resultados.md/.json` (os dois últimos são gerados por `scripts/validar.py` e `scripts/auditoria.py` e foram mantidos como originais; ver 3.4).

## 2. Problemas corrigidos
| Item | Problema | Correção |
|---|---|---|
| A | `docs/checklist_entrega.md`: 6 caracteres de controle (4 CR, 1 FF, 1 BEL) nas linhas 54, 56–59 | Causa: as sequências `\r`, `\f` e `\a` dos caminhos do Windows (`saida\resultados.csv`, `saida\falha`, `docs\auditoria_resultados.md`) foram interpretadas como caracteres de controle ao gerar o arquivo. **Todas foram recuperadas sem ambiguidade** (cada caractere de controle correspondia a exatamente uma sequência) e os caminhos agora coincidem com os comandos exibidos nas capturas. Não houve trecho irrecuperável. Nota de transparência: a primeira tentativa de correção falhou pelo mesmo problema de escape no meu comando e foi refeita |
| B | Integrantes "em branco/não informados" em 5 documentos | Preenchidos com os nomes do `README.md:8` (a mesma cadeia nos 6 documentos): Henry Gimenez - 563217; Gustavo Balbo - 561711; Vinícius Araújo - 564504. **Não foram conferidos fora do README**; o grupo deve confirmar. Turma, temas oficiais e prazo continuam como pendência |
| C | `saida/o*.csv`; "11 imagens"; outros caminhos | Corrigidos no README. A busca por outros caminhos incorretos (31 links relativos e todos os caminhos entre crases) não encontrou novos defeitos |
| D | Matriz sem o requisito de entrega por Git | Linha adicionada com **Implementado** (repositório local, `.gitignore`, `.gitattributes`), **Evidenciado** (0 commits e 0 remotos, conferidos em 10 e 11/11/2026) e **Pendente** (commit, publicação ou notebook). Status **PENDENTE**; não é declarado atendido |
| F | Afirmações de teste em ambiente limpo | Contextualizadas em 8 pontos (README ×2, checklist, matriz ×4, perguntas Q13): **"relatada, sem log preservado"**. Nenhum log foi criado |
| G | Preparação para a banca | Q22–Q28 em `docs/perguntas_banca.md` (seção F), fundamentadas no código e no manifesto, com "documentado" separado de "sem justificativa formal" |

## 3. Divergências esclarecidas
Nenhuma métrica histórica foi alterada.

### 3.1 Duas definições de "automático" (esclarecida)
- **Por confiança ≥ 0,45** (`evidencias_resultados.md`, gerado por `validar.py`): 67/80 e 30/40.
- **Por status `encaminhado`** (README e `auditoria_ia.md`): 57/80 e 27/40.
- A diferença é exatamente o conjunto de casos que as regras de urgência desviaram a humano apesar da confiança ≥ 0,45: **10** no teste 1 (9 urgências corretas + 1 erro) e **3** no teste 2 (todas corretas). Os erros, por consequência, são 7 contra 6 no teste 1 e 3 contra 3 no teste 2. A conciliação fecha (67 − 10 = 57; 30 − 3 = 27; revisão humana 13 + 10 = 23 e 10 + 3 = 13). Ela foi conferida por leitura (modelo salvo e `regras.decidir`, sem treino) com um **script de uso único não versionado**; por isso a tabela em `docs/evidencias.md` é um registro e não um artefato reproduzível por comando do repositório. A definição de referência para fala pública é a **por status**.

### 3.2 Falhas HTTP: 6 e 9 (esclarecida)
Dois cenários distintos: `scripts/validar.py:99` usa `retries=2` → 3 CEPs × 2 = **6**; a demonstração ao vivo (captura `07`) usa o padrão `CEP_MAX_RETRIES = 3` → 3 × 3 = **9**. Em ambos, o circuit breaker abre após 3 CEPs falhos e os 21 registros são processados.

### 3.3 Resultados que não podem ser reproduzidos (marcados, não removidos)
| Resultado | Situação | Recomendação |
|---|---|---|
| 73,8% e 67,5% (versão anterior: 360 textos, só palavras) | Não reproduzível: treino e modelo daquela versão não foram preservados; sem script nem log | Manter apenas como histórico rotulado ou **remover** |
| "só palavras": 64/80 e 29/40 (treino de 640) | Não reproduzível: script temporário não versionado; reproduzir exigiria treinar (fora do escopo) | Manter só como relatado ou **remover** |
| Comparação entre 4 configurações | Não reproduzível; a ressalva metodológica ("escolhida olhando os testes") permanece | Manter a ressalva |
| Atribuição "a melhoria veio de mais dados + n-gramas" | Hipótese, pois depende dos itens acima | Tratar como hipótese |

Reproduzíveis: baseline de palavras-chave (58,8% e 50,0%), 87,5% e 82,5%, matriz de confusão e as contagens por status.

### 3.4 Ambiente limpo
A execução em cópia limpa com venv novo foi **relatada** em 10/11/2026 e **não tem log, captura ou script preservado**. Os documentos agora dizem isso e **não** a tratam como evidência arquivada.

## 4. Problemas que não puderam ser resolvidos
| Item | Motivo |
|---|---|
| **Autoria e uso de IA** (I-03) | **Bloqueado por instrução.** A divergência permanece: `README.md`, `docs/evidencias.md`, `docs/auditoria_ia.md`, `docs/roteiro_apresentacao.md` (e `docs/perguntas_banca.md`/`docs/checklist_entrega.md`) descrevem os dados e testes como "escritos à mão/pela equipe", enquanto o checklist (item "Declarar o uso de assistente de IA") e a Q5 informam auxílio de IA. Conferi que as 35 passagens de autoria/IA dos 5 arquivos bloqueados são idênticas às dos backups |
| Git (entrega) | **Bloqueado por instrução.** 0 commits, 0 remotos; requisito de entrega **PENDENTE** |
| Números não reproduzíveis | Só podem ser **marcados**, não comprovados |
| Ambiente limpo | Sem log; só pode ser **refeito e arquivado** pelo grupo |
| `docs/evidencias_resultados.md` | Gerado por `validar.py`; continua mostrando `falhas_http_cep: 6` sem nota (a explicação está em `docs/evidencias.md`). Editá-lo à mão seria sobrescrito na próxima execução |
| Itens da auditoria **fora da lista de correções autorizadas** (não tratados) | I-08 (`auditoria_ia.md:30` ainda diz que o `validar.py` mostra a urgência só do teste 1, contradizendo a linha 18); I-10 (`auditoria_ia.md:7, 10, 16`); I-13 (a limitação do escopo do manifesto agora consta na Q26, mas não em `auditoria_ia.md`); I-15 (Plano B do roteiro sem as capturas); título `EVID_xxxx` das capturas; I-16 e I-17. Aguardam autorização |

> *[Atualização de 11/11/2026: I-08, I-10 e I-15 foram **tratados na rodada 2** (seção 7.2), e a lacuna do enunciado geral foi resolvida com a análise do PDF oficial na rodada 3 (seção 8). Continuam abertos I-13 (parcial), a explicação do título `EVID_xxxx` no checklist (parcial), I-16 e I-17; ver as seções 7.5 e 8.5.]*

## 5. Verificação posterior
| Verificação | Resultado |
|---|---|
| Caracteres de controle em todos os `.md` | **Nenhum** (CR soltos: 0) |
| Links relativos | **31 conferidos, 0 quebrados** |
| Caminhos entre crases | Nenhum inexistente, exceto atalhos esperados (`docs/auditoria_resultados.md/.json`) e a pasta reservada `validacao_independente/conjunto` (ignorada de propósito) |
| Tabelas Markdown | Nenhuma linha com número de colunas diferente do cabeçalho |
| Consistência entre documentos | Integrantes iguais nos 6 documentos; afirmações de ambiente limpo e de números históricos consistentes entre si; o que ainda mostra "____" é Turma, temas e prazo (pendências do grupo) |
| Autoria e uso de IA intocados | **35 passagens conferidas, 0 alteradas** (a única diferença de contagem é "descrita", falso positivo de "escrit") |
| Hashes dos 6 arquivos protegidos | **6 de 6 idênticos** ao manifesto; datas de modificação inalteradas (dados e modelo em 10/11 17:11–17:21; manifesto 21:05) |
| Código e dados alterados nesta tarefa | **Nenhum**: só `.gitignore` e documentos foram modificados |
| Testes automatizados | **21 passed** (11,3 s). Os testes `pytest` já treinam um modelo **em memória** (`salvar_em=None`) para avaliar a mecânica; nada é gravado, o `.joblib` não foi tocado e nenhum comando de treino ou de regeneração de dados foi executado |
| Git | `main`, **0 commits, 0 remotos**; nenhuma operação de escrita no Git (apenas leitura). A pasta de backup é ignorada pelo `.gitignore` |

## 6. Pendências restantes do grupo (posição da 1ª rodada; atualizada nas seções 7.5 e 8.5)
Nenhuma foi marcada como concluída.
1. **Declaração única de autoria e uso de IA** (conforme as regras da FIAP) e alinhamento dos documentos.
2. **Nomes oficiais dos temas da disciplina**; **turma**; **prazo/data**.
3. **Confirmar os dados dos integrantes** copiados do README.
4. **Entrega**: decidir e autorizar commit e publicação (ou notebook).
5. **Confirmar o tema** (UBS).
6. **Arquivar evidência de ambiente limpo** (log), se quiserem afirmá-lo.
7. **Decidir** se mantêm ou removem os resultados não reproduzíveis (3.3) e se autorizam as correções restantes da seção 4.
8. Validação independente e revisão por profissional de saúde (opcionais para o enunciado; necessárias para qualquer afirmação além de "avaliado em testes internos").

---

## 7. Rodada 2 (11/11/2026) — pendências documentais da seção 4

Escopo autorizado: `docs/auditoria_ia.md`, o Plano B de `docs/roteiro_apresentacao.md` e a explicação das falhas HTTP em `docs/evidencias.md`. **Nenhum** código, modelo, dado, regra, teste, arquivo protegido ou `docs/evidencias_resultados.md` foi alterado; nenhuma operação de escrita no Git; nenhum log retrospectivo foi criado; nenhuma informação acadêmica foi inventada. Backup desta rodada: `_backup_docs_pre_correcao_2026-11-11/rodada2_antes/` (com `_SHA256_antes_rodada2.txt`).

### 7.1 Arquivos modificados nesta rodada
Somente `docs/auditoria_ia.md`, `docs/roteiro_apresentacao.md`, `docs/evidencias.md` e este relatório. Conferido por data de modificação: nenhum outro arquivo do projeto foi alterado depois do início da rodada.

### 7.2 O que foi corrigido
| Documento | Problema | Correção (somente conteúdo factual e técnico) |
|---|---|---|
| `docs/auditoria_ia.md`, linha 30 | Dizia que o `validar.py` "continua mostrando a métrica de urgência apenas do teste 1", contradizendo a linha 18 | Reescrita: a versão original cobria só o teste 1; depois do fechamento (item b da linha 18) ele também relata teste 2 e combinado (14/15, igual ao de `auditoria.py`). Conferido contra `docs/evidencias_resultados.md`. A medida de referência continua sendo a de `auditoria.py` |
| `docs/auditoria_ia.md`, linha 7 | "Nenhuma configuração foi escolhida consultando resultados" parecia contradizer a seção 5 (a configuração foi escolhida olhando os testes) | Delimitada à etapa de auditoria, com remissão: a configuração foi escolhida **antes** do congelamento, entre 4 opções, olhando os testes (seção 5) |
| `docs/auditoria_ia.md`, linha 10 | Trecho `vocabulário incluído no próprio manifesto` formatado como código (artefato) e lista de versões sem `joblib` | Frase refeita; versões: Python, scikit-learn, numpy e joblib (conferido no manifesto) |
| `docs/auditoria_ia.md`, linha 16 | "Foi criado **uma única vez**" era impreciso: o manifesto foi gerado antes em `docs/congelamento/`, removido e recriado no caminho atual | Corrigido: criado em 10/11/2026 às 21:05:38 (igual ao `data_auditoria` e à data do arquivo). A versão anterior **não foi preservada**, e a coincidência dos hashes **é um relato que não pode ser comprovado** |
| `docs/roteiro_apresentacao.md`, Plano B | Plano B citava só `exemplo_saida/` e `evidencias_resultados.md` | Nova tabela etapa do roteiro → captura, para as 13 imagens existentes (todas conferidas: existem e todas são citadas), com o que cada uma mostra e suas limitações; etapas **sem captura** declaradas (§1–§4, §6 e §12; também a listagem de `data/inbox/` e a tabela comparativa do README); cuidados (execução real de 11/11, não ao vivo; título `EVID_xxxx` é artefato; visões tabulares; texto bruto) |
| `docs/evidencias.md`, "Esclarecimentos" §2 | Avaliada: a explicação 6 × 9 estava **correta, mas incompleta** | Complementada com tabela lado a lado dos dois cenários (timeout 0,5 s × 1 s; tentativas 2 × 3; espera 0,05 s × 0,3 s; consultas/falhas 6/6 × 9/9; `cep_indisponivel` 20 em ambos) e com a precisão de que o registro restante é o S011, sem CEP (`sem_cep`, visível na captura `04a`), **inferido** para o cenário automatizado. Declarado que o esclarecimento vive só nesta página porque `evidencias_resultados.md` é gerado e não foi editado |

### 7.3 Avaliação do item 3 (`evidencias_resultados.md`)
A explicação existente em `docs/evidencias.md` **não era suficiente** por si só: explicava a causa (2 × 3 tentativas), mas não comparava os parâmetros nem registrava que o `6` do arquivo gerado se refere ao cenário automatizado. Foi **apenas complementada**; o arquivo gerado e os scripts permanecem como estavam. Limitação que permanece: quem lê só `evidencias_resultados.md` não encontra a nota ali (o arquivo é regenerado a cada execução do `validar.py`).

### 7.4 Verificação final desta rodada
| Verificação | Resultado |
|---|---|
| Autoria e uso de IA × backups originais | **38 passagens conferidas** em 6 documentos (README, `evidencias.md`, `auditoria_ia.md`, `checklist_entrega.md`, `perguntas_banca.md`, `roteiro_apresentacao.md`): **0 alteradas**. Uma ocorrência nova da expressão "à mão" (a frase "não foi editado à mão", sobre a edição de um arquivo gerado) foi reescrita como "editado manualmente" para não se confundir com a redação de autoria |
| Markdown | Nenhum caractere de controle; **31 links relativos, 0 quebrados**; nenhuma linha de tabela com número de colunas diferente do cabeçalho nos 3 documentos editados |
| Capturas citadas no roteiro | As 13 existem em `docs/evidencias_visuais/` e todas aparecem no Plano B |
| Hashes dos 6 arquivos protegidos | **6 de 6 idênticos** ao manifesto |
| Testes automatizados | **21 passed** (11,3 s). Os testes treinam um modelo **em memória** (`salvar_em=None`), como antes; nada foi gravado e nenhum treino ou regeneração de dados foi executado |
| Git | `main`, **0 commits, 0 remotos**; nenhuma operação de escrita |

### 7.5 Pendências que continuam
**Dependem do grupo** (nenhuma foi marcada como concluída):
1. Declaração única de autoria e uso de IA (conforme as regras da FIAP) e alinhamento dos documentos; a divergência permanece registrada.
2. Nomes oficiais dos temas da disciplina, turma e prazo/data.
3. Confirmar os dados dos integrantes copiados do README.
4. Entrega: decidir e autorizar commit e publicação (ou notebook); requisito **PENDENTE** na matriz.
5. Confirmar o tema (UBS).
6. Arquivar um log de execução em ambiente limpo, se quiserem afirmá-lo (hoje: relatado, sem log).
7. Decidir se mantêm ou removem os resultados não reproduzíveis (73,8%/67,5%; "só palavras" 64/80 e 29/40; comparação de 4 configurações).
8. Validação independente e revisão por profissional de saúde.

**Documentais ainda sem tratar** (não incluídos nas autorizações das duas rodadas; aguardam decisão): I-13 (a limitação do escopo do manifesto consta na Q26 de `perguntas_banca.md`, mas não em `auditoria_ia.md`), explicação do título `EVID_xxxx` também no checklist (hoje só no Plano B do roteiro), I-16 (o caminho "modelo ilegível → re-treina em memória" de `main.py` não tem teste automatizado) e I-17 (material oficial `docs/enunciado/p1.png` e `p2.png` seria versionado).

---

## 8. Rodada 3 (11/11/2026) — revisão documental com o PDF oficial da Global Solution 2026.2

### 8.1 Escopo e restrições
Autorizado: atualizar **somente** `docs/matriz_requisitos.md`, `docs/auditoria_final_entrega.md`, `docs/checklist_entrega.md` e este relatório, usando como referência o **PDF oficial** `2TIAP(F-Y)-2026 - GS 2026.2.pdf` (17 páginas de slides; cada página traz 2 slides; **permanece fora do repositório**, em `Downloads`; **não foi copiado nem enviado**) e o complemento da disciplina 01 (`docs/enunciado/`). Respeitadas as restrições: nenhum código Python, modelo, dataset/CSV, regra, script, teste ou dependência foi tocado; nenhum treinamento foi executado; nenhum comando Git que altere o repositório; nenhum commit, publicação ou envio; **nenhuma declaração de autoria ou de uso de IA foi alterada**; nenhuma evidência, funcionalidade ou resultado foi inventado.

### 8.2 Backups criados
`_backup_docs_pre_correcao_2026-11-11/rodada3_antes/` com cópia (datas preservadas) de `docs/matriz_requisitos.md`, `docs/auditoria_final_entrega.md`, `docs/checklist_entrega.md` e `docs/relatorio_correcao_documental.md`, mais `_SHA256_antes_rodada3.txt`. A pasta é ignorada pelo Git.

### 8.3 Documentos alterados
| Arquivo | O que mudou |
|---|---|
| `docs/matriz_requisitos.md` | **Reescrita** com as duas fontes: seções A–E do complemento preservadas (linhas de prazo, integrantes/trio, Git e temas atualizadas) e novas seções **F** (desafio geral, p. 1–6, 25 requisitos), **G** (disciplina 01, p. 11, 9 requisitos + tabela de 6 temas de exemplo e 3 próprios), **H** (disciplina 06, p. 14, 6 requisitos + 7 módulos das outras disciplinas), **I** (entrega geral, prazos e prêmio, 3 requisitos) e **J** (12 ressalvas técnicas). Todo requisito traz a **página do PDF** de origem |
| `docs/auditoria_final_entrega.md` | Histórico preservado, com notas entre colchetes onde o PDF supera o diagnóstico; novas linhas de evidências ausentes, riscos e pendências (G-11 a G-15); novas seções **8** (análise do PDF) e **9** (veredito atualizado); `Cobertura dos requisitos da GS` passou de "aprovado com ressalvas" para **PENDENTE** |
| `docs/checklist_entrega.md` | Linhas de prazo (19/11/2026 às 23h55), canal de entrega (Portal; GitHub para a disciplina 06) e grupo (trio) atualizadas; nova seção **6**, separando exigências da disciplina 01, da disciplina 06 e da GS/prêmio, com o desafio geral |
| `docs/relatorio_correcao_documental.md` | Este resumo executivo (seção 0), notas nas seções 4 e 6 e esta seção 8 |

### 8.4 Requisitos oficiais identificados e resultado
**43 requisitos** do PDF (todos com página de origem, conferido na matriz): desafio geral (25), disciplina 01 (9), disciplina integradora 06 (6) e entrega/premiação (3). Contagem lida das próprias tabelas da matriz e igual nos três documentos.

| Nível | ATENDIDO | PARCIALMENTE | NÃO ATENDIDO* | NÃO COMPROVADO |
|---|---|---|---|---|
| Desafio geral (F01–F25) | 11 | 9 | 4 | 1 |
| Disciplina 01 (G01–G09) | 6 | 2 | 1 | 0 |
| Disciplina 06 (H01–H06) | 0 | 1 | 5 | 0 |
| Entrega geral e prêmio (I01–I03) | 0 | 0 | 1 | 2 |
| **Total (43)** | **17** | **12** | **11** | **3** |

\* inclui os dois itens **PENDENTES** de envio ao Portal (G08 e H06), que contam como não atendidos até haver ação da equipe.

- **Atendidos (17):** F01, F08, F09, F12, F15, F17, F18, F20–F23; G02–G06, G09.
- **Parcialmente atendidos (12):** F02, F04, F07, F10, F11, F13, F16, F19, F24; G01, G07; H05.
- **Não atendidos (11):** F05 (acessibilidade), F06 (sustentabilidade), F14 (viabilidade), F25 (modelos de negócio, se for exigência); G08 e H06 (envio, pendentes); H01 (vídeo), H02 (ABNT), H03 (GitHub), H04 (módulos integrados); I01 (vídeo pitch).
- **Não comprovados (3):** F03 (escuta de usuários), I02 ("disciplina indicada" não identificada no PDF), I03 (Challenge Sprint, não descrito no PDF).
- **Temas da disciplina 01 (6 exemplos do PDF):** ATENDIDOS 2 (integração com APIs; banco de dados SQL), PARCIAL 1 (arquivos e dados, **sem Pandas**), NÃO ATENDIDOS 3 (web scraping, e-mail automatizado, RPA desktop). Os 3 temas próprios do projeto (NLP/ML, regras, resiliência) ficam **NÃO COMPROVADOS** como "tema da disciplina". **Os 7 módulos das demais disciplinas** estão NÃO COMPROVADOS (não encontrados no repositório).
- **Divergências entre as fontes registradas:** grupo "até 5" (complemento) × "trio, dupla ou individual" (PDF); prazo; canal de entrega (Portal × Git); pesos do barema (só no complemento).

> *[Atualização da rodada 4: as contagens e as listas desta seção 8.4 refletem a classificação da rodada 3. Foram reclassificados G01 e o tema "arquivos e dados" (para ATENDIDO) e F25 (para N/A). A contagem vigente é **18 · 11 · 10 · 3 + 1 N/A**; ver a seção 9.]*

### 8.5 Pendências que dependem da equipe (nenhuma marcada como concluída)
1. **Enviar a entrega pelo Portal do Aluno até 19/11/2026 às 23h55** (restam 8 dias a partir de 11/11/2026).
2. **Declaração única de autoria e uso de IA** (conforme as regras da FIAP); divergência mantida.
3. **Confirmar com o professor o que conta como tema** (Pandas é exigido? NLP/ML e regras valem?); nomes oficiais dos temas; decidir a declaração do SQL no quadro. *[Rodada 4: a confirmação passou a ser **opcional**, porque os três temas implementados (arquivos e dados, APIs, SQL) atendem ao mínimo pela lista do PDF e Pandas não é exigido; continua pendente **atualizar o quadro de temas** para nomear o SQL; ver a seção 9.]*
4. **Decidir sobre a disciplina 06** (vídeo ≤ 7 min, documentação ABNT, GitHub, módulos integrados) e sobre o **prêmio** (vídeo pitch; qual é a "disciplina indicada"; se é o mesmo vídeo da disciplina 06).
5. **Commit e publicação** (Git sem commits e sem remoto), com autorização.
6. **Turma** e **data da apresentação** (não constam no PDF); confirmar os dados dos integrantes.
7. **Decidir se documentam** acessibilidade, sustentabilidade, viabilidade, escuta de usuários, ecossistema e modelo de negócio (somente o que for verdadeiro); confirmar o tema (UBS).
8. Verificar no **portal do aluno** as regras específicas da disciplina e o que é o **Challenge Sprint** (30/11/2026).
9. Arquivar um **log de ambiente limpo**, se quiserem afirmá-lo; decidir sobre os resultados não reproduzíveis; validação independente e revisão por profissional de saúde.

**Resolvido ou atualizado nesta rodada:** a lacuna "enunciado geral ausente" (agora analisado; o PDF segue fora do repositório, ver I-17); o prazo (era "não informado", agora 19/11/2026 às 23h55); o tamanho do grupo (3 integrantes atendem ao PDF e ao complemento); a separação entre exigências da disciplina 01, da disciplina 06 e da GS/prêmio.

### 8.6 Recomendações para outros arquivos (**não aplicadas**: fora do escopo autorizado)
- `README.md`: citar o PDF oficial como fonte; se for verdade, declarar como limitações a ausência de recursos de **acessibilidade**, de análise de **sustentabilidade**, de **viabilidade** e de **escuta de usuários**; alinhar a referência ao tamanho do grupo (trio); acrescentar o aviso de que, **num clone, `scripts/validar.py` pode regravar o modelo** (via `carregar_modelo`, se o `treino.csv` for mais novo que o `.joblib`) e fazer o `auditoria.py` abortar.
- `docs/temas.md`: **declarar o banco de dados SQL (SQLite)** como tema, esclarecer que **Pandas, web scraping, e-mail automatizado e RPA desktop não são usados** e que NLP/ML e regras de negócio **não constam** na lista de exemplos do PDF.
- `docs/etica_ods.md`: registrar como limitação a ausência de acessibilidade e de dimensão de sustentabilidade, e que a relação com os ODS é qualitativa.
- `docs/roteiro_apresentacao.md`: observar que ~12,75 min **excedem** os 7 min do vídeo; se o grupo optar por vídeo, será necessário um roteiro próprio.
- `docs/perguntas_banca.md`: acrescentar perguntas sobre a ausência de Pandas, sobre o uso mínimo de SQL e sobre o que falta para a disciplina 06.
- `docs/checklist_entrega.md` (seção 3.2): explicar o título `EVID_xxxx`; `docs/auditoria_ia.md`: registrar o escopo do manifesto e a recriação quando ausente (I-13).
- `docs/enunciado/`: decidir se o PDF oficial entra no repositório (I-17).

### 8.7 Ressalvas técnicas preservadas
Conferido que **as 12 ressalvas** (dados sintéticos; validação independente não realizada; métricas sem prova de desempenho real; inaptidão para triagem clínica; falha grave de urgência; apoio administrativo com revisão humana; limiar 0,45 sem calibração; métricas históricas não reproduzíveis; manifesto com só seis arquivos; recriação do manifesto quando ausente; Git sem commits e sem remoto; ambiente limpo sem log) **constam** na seção J da matriz e na seção 8.6 da auditoria, e as principais também no checklist (seção 6.5). Nenhuma foi removida ou suavizada. **Nenhuma entrega incompleta foi apresentada como completa.**

### 8.8 Verificação final da rodada 3
| Verificação | Resultado |
|---|---|
| Requisitos oficiais com página do PDF | **43 de 43** com referência (páginas citadas: 1, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15; todas dentro de 1–17) |
| Contagem 17/12/11/3 | Lida das tabelas da matriz e **igual** na matriz, na auditoria e neste relatório |
| Coerência matriz × checklist × auditoria | Prazo (19/11/2026 às 23h55), trio, ausência de vídeo/ABNT/GitHub/módulos e as 12 ressalvas aparecem nos três; nenhuma contradição encontrada. A matriz marca G08 e H06 como PENDENTES, e o checklist os lista como ⛔ não enviados |
| Caracteres de controle, links e tabelas | Nenhum caractere de controle; links relativos do checklist **13, 0 quebrados**; nenhuma tabela com número de colunas incorreto nos 4 documentos |
| Caminhos entre crases | Nenhum inexistente, exceto `validacao_independente/conjunto` (pasta reservada, ignorada de propósito) e `docs/congelamento` (pasta antiga, citada apenas como histórico) |
| Autoria e uso de IA × backups originais | **38 passagens conferidas, 0 alteradas** (6 documentos) |
| Testes automatizados | **21 passed** (31,1 s), com `-p no:cacheprovider` e sem bytecode: **nenhum arquivo de cache foi criado ou alterado no projeto**; os testes treinam um modelo só em memória, e nenhum treino persistido ou regeneração de dados foi executado |
| Hashes dos 6 arquivos protegidos | **6 de 6 idênticos** ao manifesto |
| Arquivos fora do escopo documental | **Nenhum modificado**: código, modelo, dados, regras, testes, scripts e dependências não têm data posterior ao início da rodada |
| Git | `main`, **0 commits, 0 remotos**; nenhuma operação de escrita |

---

## 9. Rodada 4 (11/11/2026) — revisão pontual das classificações: temas da disciplina 01, modelos de negócio, acessibilidade e sustentabilidade

### 9.1 Escopo e restrições
Autorizado: reavaliar três questões e atualizar **somente** as classificações e justificativas necessárias em `docs/matriz_requisitos.md` e `docs/auditoria_final_entrega.md`, registrando as mudanças neste relatório. Respeitadas as restrições: **nenhum** código, modelo, dado, regra, teste ou script foi alterado; nenhum treinamento; nenhum comando Git de escrita; nenhuma funcionalidade foi inventada; as lacunas de acessibilidade e sustentabilidade **foram mantidas**. **O `docs/checklist_entrega.md` não foi alterado** (fora do escopo autorizado; ver 9.6).

### 9.2 Backup e documentos alterados
- **Backup:** `_backup_docs_pre_correcao_2026-11-11/rodada4_antes/` (`docs/matriz_requisitos.md`, `docs/auditoria_final_entrega.md`, `docs/relatorio_correcao_documental.md` e `_SHA256_antes_rodada4.txt`).
- **Alterados:** `docs/matriz_requisitos.md`, `docs/auditoria_final_entrega.md` e este relatório.

### 9.3 Reclassificações e evidências

| Item | Antes | Depois | Base da decisão |
|---|---|---|---|
| **G01** — ≥ 3 temas da disciplina 01 com função real (PDF p. 11) | PARCIALMENTE ATENDIDO | **ATENDIDO** (com ressalvas de profundidade) | Os três temas abaixo existem, são distintos e têm função real |
| Tema **tratamento de arquivos e dados** | PARCIALMENTE ATENDIDO (por não usar Pandas) | **ATENDIDO** | O PDF cita Pandas **entre parênteses, como exemplo**, após "como"; não o exige. A função real está comprovada no código, nas saídas, nos testes e nas capturas |
| **F25** — modelos de negócio | NÃO ATENDIDO (se for exigência) | **N/A** (não exigido explicitamente; observação registrada) | O termo aparece na frase de **reflexão** do case (p. 6) e em um de 15 cartões de exemplos (p. 9); **não** está entre os pontos que cada proposta deve considerar (p. 6) nem em nenhuma disciplina (p. 11 a 15) |
| **F05** — acessibilidade | NÃO ATENDIDO | **NÃO ATENDIDO** (mantido) | O desafio pede promovê-la (p. 4) e a proposta deve considerá-la (p. 6); **0 arquivos de código e 0 ocorrências** em README, `etica_ods.md` e `temas.md`; sem interface |
| **F06** — sustentabilidade | NÃO ATENDIDO | **NÃO ATENDIDO** (mantido) | O desafio pede promovê-la (p. 4); **0 arquivos de código e 0 ocorrências** nos documentos; a relação com os ODS 3, 10 e 16 é qualitativa e não equivale a promover sustentabilidade |

**Evidências dos três temas distintos (inspeção do código, saídas reais, testes e capturas):**

| Tema (PDF p. 11) | Módulos e linhas | Função no fluxo | Evidência |
|---|---|---|---|
| **Tratamento de arquivos e dados** | `ingestao.py:19–61`, `validacao.py:9–20`, `texto.py:10–23`, `pipeline.py:103–116` | Ler CSV e TXT (com falha isolada por arquivo), validar (4 regras), normalizar e **mascarar CPF/e-mail/telefone**, e gerar 3 CSV (UTF-8 com BOM) e 1 JSON. Execução registrada: 4 arquivos → 25 registros lidos, 21 processados (21 linhas em `resultados.csv`), 4 em `revisao_humana.csv`, 3 rejeitados, 1 duplicado, 2 arquivos defeituosos tratados | Capturas `03`, `04a`, `04b`, `05`, `06`; 5 testes (validação ×2, mascaramento, pasta ausente, arquivo corrompido) |
| **Integração com APIs** | `geo.py:14–63` | Requisição HTTP à ViaCEP com timeout, retry, cache e circuit breaker; preenche `bairro`, `cidade`, `uf` e `fonte_cep`: **16 dos 21 registros enriquecidos**, 4 `indisponivel`, 1 `sem_cep`. **Acessória:** não decide o roteamento | Capturas `03`, `04a`, `07`; 4 testes (retry, falha total, resposta inesperada, circuit breaker) |
| **Banco de dados SQL** | `estado.py:9–32`, `pipeline.py:71–78` | SQLite: `CREATE TABLE IF NOT EXISTS`, `SELECT`, `INSERT OR IGNORE`, `DELETE`; o fluxo **decide com base na tabela** (duplicado ignorado; hash gravado só após o sucesso). Na 2ª execução, os 22 registros válidos são ignorados. **Uso mínimo** (uma tabela) | Captura `11`; `test_pipeline_duplicado_invalido_e_idempotencia` |

**São temas distintos** porque cada um está em módulos diferentes, usa recursos diferentes (arquivos e texto; HTTP; SQL) e cumpre uma função diferente (preparar entradas e saídas; enriquecer o endereço; impedir o reprocessamento), e nenhum é só uma camada do outro.

**Ressalvas de profundidade mantidas (não rebaixam o tema, mas ficam registradas):** o tema de arquivos usa a biblioteca padrão, com transformações simples e sem DataFrames; a API é **acessória**; o SQL é de **uso mínimo**. O `docs/temas.md` **não nomeia o SQL** (pendência documental, não de implementação). O plano de ensino não está disponível.

### 9.4 Efeito na contagem dos requisitos oficiais
| | ATENDIDO | PARCIALMENTE | NÃO ATENDIDO | NÃO COMPROVADO | N/A | Avaliáveis |
|---|---|---|---|---|---|---|
| Antes (rodada 3) | 17 | 12 | 11 | 3 | 0 | 43 |
| **Depois (rodada 4)** | **18** | **11** | **10** | **3** | **1** | **42** |

Mudanças: G01 (PARCIAL → ATENDIDO: +1 / −1) e F25 (NÃO ATENDIDO → N/A: −1 e saída das avaliáveis). A contagem foi **relida das próprias tabelas da matriz** e confere com a auditoria. Nas tabelas de temas: **3 ATENDIDOS**, 0 PARCIAL, 3 NÃO ATENDIDOS (web scraping, e-mail, RPA desktop).

### 9.5 Ressalvas técnicas preservadas
Conferido que as **12 ressalvas** (dados sintéticos; validação independente não realizada; métricas sem prova de desempenho real; inaptidão para triagem clínica; falha grave de urgência; apoio administrativo com revisão humana; limiar 0,45 sem calibração; métricas históricas não reproduzíveis; manifesto com só seis arquivos; recriação do manifesto quando ausente; Git sem commits e sem remoto; ambiente limpo sem log) **continuam** na seção J da matriz e na seção 8.6 da auditoria. **Nenhuma foi removida ou suavizada.** A solução continua **inapta para triagem clínica**, e as demais lacunas oficiais (F14 viabilidade, F03 escuta de usuários, disciplina 06, prêmio, envio ao Portal) **não mudaram**.

### 9.6 Inconsistência conhecida e pendências (nada foi alterado fora do escopo)
- **`docs/checklist_entrega.md`, seção 6.1**, ainda reflete a classificação anterior nas linhas "Pelo menos 3 temas" (diz "2 plenos e 1 parcial, sem Pandas" e "confirmar com o professor... Pandas é exigido?") e "Quadro de temas coerente". **Aguarda autorização** para ser atualizado. *[**Resolvido na rodada 5** (seção 10): a seção 6.1 do checklist foi corrigida e agora concorda com a matriz e a auditoria quanto aos três temas.]*
- **Seções 0, 8.4 e 8.5 deste relatório** são o registro da rodada 3 e ganharam notas apontando para esta seção.
- **`docs/temas.md`**: continua sem nomear o SQL e sem os nomes dos temas do PDF (recomendação das rodadas anteriores; **não aplicada**). *[**Resolvido na rodada 5 quanto ao SQL**: a linha "Banco de dados SQL (SQLite)" foi acrescentada. Os nomes do plano de ensino seguem não confrontados.]*
- **Pendências da equipe**, inalteradas: declaração única de autoria e uso de IA; envio pelo Portal até 19/11/2026 às 23h55; decisão sobre disciplina 06 e prêmio; commit e publicação; turma e data da apresentação; documentar (ou declarar como limitação) acessibilidade, sustentabilidade, viabilidade e escuta de usuários.

### 9.7 Verificação final da rodada 4
| Verificação | Resultado |
|---|---|
| Contagem 18 · 11 · 10 · 3 + 1 N/A | Lida das tabelas F–I da matriz e **igual** na auditoria; todos os 43 requisitos com página do PDF; F05 e F06 = NÃO ATENDIDO; F25 = N/A; G01 = ATENDIDO |
| Resquícios da classificação antiga | Só a nota histórica entre colchetes na auditoria ("antes 2 plenos, 1 parcial") |
| Markdown | Sem caracteres de controle e sem tabelas com número de colunas incorreto nos documentos alterados |
| Ressalvas técnicas | As 12 presentes na matriz (J) e na auditoria (8.6) |
| Autoria e uso de IA × backups originais | **38 passagens conferidas, 0 alteradas** |
| Testes automatizados | **21 passed** (5,2 s), com `-p no:cacheprovider` e sem bytecode; **nenhum cache criado**; os testes treinam só em memória, e nenhum treino persistido foi executado |
| Hashes dos 6 arquivos protegidos | **6 de 6 idênticos** ao manifesto |
| Arquivos fora do escopo documental | **Nenhum modificado** (código, modelo, dados, regras, testes, scripts e dependências sem data posterior ao início da rodada; só a matriz e a auditoria mudaram, além deste relatório) |
| Git | `main`, **0 commits, 0 remotos**; nenhuma operação de escrita |

---

## 10. Rodada 5 (11/11/2026) — checklist 6.1 e quadro de temas

### 10.1 Escopo e restrições
Autorizado: corrigir a seção 6.1 do `docs/checklist_entrega.md`, acrescentar o tema banco de dados SQL em `docs/temas.md` e registrar esta rodada. Respeitadas as restrições: **nenhum** código, modelo, dado, regra, teste, script ou dependência foi alterado; nenhum treinamento; nenhuma operação Git; nenhuma declaração de autoria ou de uso de IA foi modificada; nada foi atribuído ao SQL que o código não faça. **`docs/matriz_requisitos.md` e `docs/auditoria_final_entrega.md` não foram alterados** (fora do escopo desta rodada; ver 10.5).

### 10.2 Backup e arquivos alterados
- **Backup:** `_backup_docs_pre_correcao_2026-11-11/rodada5_antes/` (`docs/checklist_entrega.md`, `docs/temas.md`, `docs/relatorio_correcao_documental.md` e `_SHA256_antes_rodada5.txt`).
- **Alterados:** `docs/checklist_entrega.md`, `docs/temas.md` e este relatório.

### 10.3 O que foi alterado
| Arquivo | Alteração |
|---|---|
| `docs/checklist_entrega.md`, seção 6.1 | A linha "Pelo menos 3 temas" deixou de dizer "2 plenos e 1 parcial, sem Pandas" e passou a **✅ atendido pelos exemplos do PDF, com três temas distintos**: tratamento de arquivos e dados, integração com APIs e banco de dados SQL, com os arquivos de cada um. A pergunta **"Pandas é exigido?" foi removida**; o texto registra que **Pandas é um exemplo citado no PDF, não uma exigência explícita**. Ação passou a **opcional** (confirmar com o professor que os três temas são aceitos). As **ressalvas de profundidade foram preservadas**: biblioteca padrão com transformações simples; API acessória; SQL de uso mínimo (uma tabela) |
| `docs/checklist_entrega.md`, outras linhas | A linha "Quadro de temas coerente" passou a ✅ (o quadro declara o SQLite) e a registrar que o que **não** é usado (Pandas, web scraping, e-mail, RPA desktop) está na matriz (G.2), **não** no quadro; ⬜ os nomes do plano de ensino continuam não confrontados. Ajustadas, por coerência, as linhas de "Organização da entrega", "Nomes oficiais dos temas" (seção 1), "Quadro de temas" (seção 3.1) e "Quadro de temas (≥ 3)" (seção 4) |
| `docs/temas.md` | **Nova linha "Banco de dados SQL (SQLite)"**: arquivos `estado.py` e `pipeline.py` (`pipeline.py:71–78`); tabela única `processados` (`hash` chave primária, `id`, `ts`); operações **implementadas** `CREATE TABLE IF NOT EXISTS` (`estado.py:17`), `SELECT` (`:21`), `INSERT OR IGNORE` (`:24`) e `DELETE` (`:28`, usado por `--reset`), com `commit` após cada escrita; função de **persistência de estado e controle de idempotência**; evidências: **captura `11`** (0 processados, 22 duplicados) e o teste **`test_pipeline_duplicado_invalido_e_idempotencia`**; transparência: **uso mínimo** (uma tabela, sem relacionamentos, sem outros índices além da chave primária, sem tratamento de concorrência; guarda só hash, id e data, não o texto nem os resultados; duplicidade por conteúdo, não por pessoa). Uma remissão foi acrescentada na linha de integração com API (que já citava `estado.py`) e uma **nota** com a correspondência entre os exemplos do PDF e as linhas do quadro. As demais linhas e o aviso sobre o plano de ensino **não foram alterados** |

### 10.4 Verificação final da rodada 5
| Verificação | Resultado |
|---|---|
| Três temas descritos de forma consistente | Os nomes "tratamento de arquivos e dados", "integração com APIs" e "banco de dados SQL" aparecem nos quatro documentos (matriz, auditoria, checklist e `temas.md`); os arquivos citados (`ingestao.py`, `validacao.py`, `texto.py`, `geo.py`, `estado.py`, `pipeline.py`), a captura `11` e o teste de idempotência coincidem; as **três ressalvas de profundidade** (biblioteca padrão; API acessória; SQL mínimo) estão nos quatro |
| Referências de linha do SQL | `estado.py:17`, `:21`, `:24`, `:28` e `pipeline.py:71`, `:72`, `:78` conferidas contra o código |
| Resquícios da classificação antiga no checklist | **Nenhum** ("2 plenos", "1 parcial", "Pandas é exigido?" e "ainda não declara o SQL" não aparecem) |
| Markdown | Sem caracteres de controle e sem tabelas com número de colunas incorreto nos quatro documentos |
| Ressalvas técnicas | Conferidas na seção J da matriz, na 8.6 da auditoria e na 6.5 do checklist (dados sintéticos; validação independente não realizada; sem prova de desempenho real; inaptidão para triagem clínica; falha grave; revisão humana; limiar 0,45; métricas não reproduzíveis; seis arquivos; recriação do manifesto; Git sem commits; ambiente limpo sem log). **Nenhuma foi removida** |
| Autoria e uso de IA × backups originais | **38 passagens conferidas, 0 alteradas** |
| Testes automatizados | **21 passed** (26,6 s), com `-p no:cacheprovider` e sem bytecode: **nenhum cache criado**; os testes treinam só em memória, e nenhum treino persistido foi executado |
| Hashes dos 6 arquivos protegidos | **6 de 6 idênticos** ao manifesto |
| Arquivos fora do escopo documental | **Nenhum modificado**: código, modelo, dados, regras, testes, scripts, dependências e caches sem data posterior ao início da rodada; só `docs/checklist_entrega.md` e `docs/temas.md` mudaram (mais este relatório) |
| Git | `main`, **0 commits, 0 remotos**; nenhuma operação de escrita |

**Inconsistência anterior resolvida:** a divergência entre o checklist (seção 6.1) e a matriz/auditoria quanto aos três temas, registrada em 9.6, **foi resolvida**: os quatro documentos agora concordam que há **três temas atendidos** (tratamento de arquivos e dados; integração com APIs; banco de dados SQL), com as mesmas ressalvas de profundidade.

### 10.5 Afirmações que ficaram desatualizadas pela rodada 5 (fora do escopo; **aguardam autorização**)
A matriz e a auditoria ainda dizem, em alguns pontos, que o `docs/temas.md` **não declara o SQL**, o que deixou de ser verdade. O restante dessas linhas (classificação e ressalvas) continua correto.
- **`docs/matriz_requisitos.md`:** linha 26 (complemento: "o quadro de temas ainda não nomeia o SQL"); linha 40 (entregável "Quadro de temas": "O quadro não declara explicitamente o banco de dados SQL ... **Parcial**"); linha 48 (barema "Uso dos temas": "`docs/temas.md` ainda não nomeia o SQL"); linha 60 (pontos de atenção: "Pendência documental: nomear o SQL no quadro"); linha 117 (G07: "quadro de temas a atualizar (não nomeia o SQL)"); linha 133 (tema SQL: "`docs/temas.md` não o declara como tema"); linha 138 (conclusão de G01: "o quadro ... não nomeia o SQL").
- **`docs/auditoria_final_entrega.md`:** linha 80 ("Nomes oficiais não confirmados ... o quadro ... deve ser atualizado para nomear o SQL"); linha 88 ("Entregável: quadro de temas ... **PENDENTE** (nomes)"); linha 178 ("quadro de temas **sem o SQL**"); linha 199 (G-12: "atualizar o quadro de temas para nomear o SQL"); linhas 257 e 260 ("não declarado em `docs/temas.md`" e "quadro ... sem o SQL"); linha 304 ("quadro de temas (nomear o SQL)"); linha 310 ("(2) atualizar o quadro de temas (declarar o SQL...)").
- **Efeito provável:** o entregável "Quadro de temas" (matriz B e auditoria 2.4) ainda pode permanecer parcial apenas pelos **nomes do plano de ensino**, que continuam indisponíveis; a reclassificação desses itens fica a critério do grupo. *[**Resolvido na rodada 6** (seção 11): todas as linhas listadas acima foram corrigidas, mais uma ocorrência adicional encontrada na varredura (auditoria, linha 17).]*

### 10.6 Pendências restantes
- **Dependem da equipe (inalteradas):** declaração única de autoria e uso de IA; envio pelo Portal até 19/11/2026 às 23h55; decisão sobre disciplina 06 e prêmio; commit e publicação; turma e data da apresentação; documentar (ou declarar como limitação) acessibilidade, sustentabilidade, viabilidade e escuta de usuários; confirmar os nomes do plano de ensino, se o obtiverem; arquivar um log de ambiente limpo.
- **Documentais:** as afirmações listadas em 10.5 foram atualizadas na rodada 6 (seção 11); continuam abertos I-13 (escopo do manifesto em `auditoria_ia.md`), a explicação do título `EVID_xxxx` no checklist, I-16 e I-17 (ver 7.5 e 8.6).

---

## 11. Rodada 6 (11/11/2026) — correção das inconsistências residuais da rodada 5 (quadro de temas)

### 11.1 Escopo e restrições
Autorizado: corrigir, em `docs/matriz_requisitos.md`, `docs/auditoria_final_entrega.md` e neste relatório, as afirmações de que o `docs/temas.md` **não declara o SQL**, que deixaram de ser verdadeiras na rodada 5. Cada ocorrência foi lida **no contexto completo** e reescrita individualmente (sem substituição automática). Respeitadas as restrições: **nenhum** código, modelo, dado, regra, teste, script ou dependência foi alterado; nenhum treinamento; nenhuma operação Git; nenhuma declaração de autoria ou de uso de IA foi modificada. `docs/checklist_entrega.md` e `docs/temas.md` **não foram alterados** nesta rodada.

### 11.2 Backup e arquivos alterados
- **Backup:** `_backup_docs_pre_correcao_2026-11-11/rodada6_antes/` (`docs/matriz_requisitos.md`, `docs/auditoria_final_entrega.md`, `docs/relatorio_correcao_documental.md` e `_SHA256_antes_rodada6.txt`).
- **Alterados:** `docs/matriz_requisitos.md`, `docs/auditoria_final_entrega.md` e este relatório.

### 11.3 Correções realizadas
| Documento e linha (numeração anterior) | O que dizia | Como ficou |
|---|---|---|
| Matriz 26 (complemento, "≥ 3 temas") | "o quadro de temas ainda não nomeia o SQL" | O quadro **declara o SQLite desde a rodada 5**; os nomes **não foram confrontados com o plano de ensino**; confirmar com o professor **não equivale a aprovação docente já obtida** |
| Matriz 40 (entregável "Quadro de temas") | "O quadro não declara explicitamente o banco de dados SQL ... **Parcial**" | Quadro de **5 linhas**, com a linha "Banco de dados SQL (SQLite)" (arquivos, operações, evidências, uso mínimo) e a nota de correspondência com o PDF; o que não é usado dos exemplos do PDF está na seção G.2, **não no quadro**. Status: **Atendido (com ressalvas)**: nomes não confrontados com o plano de ensino e SQL de implementação mínima |
| Matriz 48 (barema "Uso dos temas") | "`docs/temas.md` ainda não nomeia o SQL ... justificativa incompleta" | **Atendido** na implementação e no quadro; ressalvas: nomes não confrontados com o plano de ensino, denominações do projeto (correspondência em nota do `temas.md`), **nenhuma confirmação do professor** |
| Matriz 60 (pontos de atenção) | "4 técnicas no quadro atual. Pendência documental: nomear o SQL" | "5 linhas no quadro atual (as 4 originais e o SQLite, rodada 5)"; ressalva dos nomes mantida |
| Matriz 117 (G07) | "quadro de temas a atualizar (não nomeia o SQL)" | "quadro de temas atualizado na rodada 5 (inclui o SQLite), com os nomes do plano de ensino ainda não confrontados". G07 **continua PARCIALMENTE ATENDIDO** (Git sem commits, turma) |
| Matriz 133 (tema SQL) | "`docs/temas.md` não o declara como tema" e "declarar no quadro de temas" | "o declara desde a rodada 5" (linha, arquivos, operações, evidências, uso mínimo); status **ATENDIDO (uso mínimo, declarado na rodada 5)** |
| Matriz 138 (conclusão de G01) | "o quadro `docs/temas.md` **não nomeia o SQL**" | "passou a declarar o SQLite na rodada 5, mas seus nomes **não foram confrontados com o plano de ensino**"; acrescentado: **a classificação é do projeto, não uma aprovação do professor** |
| Matriz 15 (parágrafo de reclassificações) | — | Nota de **histórico**: SQLite acrescentado na rodada 5; referências atualizadas na rodada 6; SQL mínimo e nomes não confrontados |
| Auditoria 80 (2.4, "≥ 3 temas") | "4 técnicas"; "o quadro deve ser atualizado para nomear o SQL" | "5 linhas ... SQLite acrescentado na rodada 5"; "declara o SQLite desde a rodada 5, com uso mínimo; nomes **não confrontados** e **sem confirmação do professor**" |
| Auditoria 88 (2.4, "Entregável: quadro de temas") | **PENDENTE** (nomes) | **APROVADO COM RESSALVAS** (nota de histórico: antes PENDENTE; ressalva dos nomes mantida) |
| Auditoria 178 (riscos) | "quadro de temas **sem o SQL**"; mitigação "Declarar o SQL e nomear os 3 temas" | "declara o SQLite desde a rodada 5, mas com nomes não confrontados"; mitigação: "O SQL já está declarado ... confirmar os nomes do plano de ensino, se o grupo o obtiver". Probabilidade **mantida** |
| Auditoria 199 (G-12) | "atualizar o quadro de temas para nomear o SQL" | Ação reduzida a: confirmar com o professor (opcional) e confrontar os nomes com o plano de ensino; "nenhuma confirmação do professor foi obtida" |
| Auditoria 257 (tema SQL em 8.3) | "**não declarado** em `docs/temas.md`" | "**declarado em `docs/temas.md` desde a rodada 5**" |
| Auditoria 260 (conclusão de 8.3) | "quadro `docs/temas.md` sem o SQL" | "declara o SQLite desde a rodada 5, mas seus nomes não foram confrontados"; acrescentado: **avaliação do projeto, não aprovação do professor** |
| Auditoria 304 (veredito, disciplina 01) | "Pendentes: **quadro de temas** (nomear o SQL ...)" | "Pendentes: **nomes do quadro não confrontados com o plano de ensino** ... sem confirmação do professor"; a disciplina 01 **continua PARCIALMENTE ATENDIDA** |
| Auditoria 310 (condições para considerar pronta) | "(2) atualizar o quadro de temas (declarar o SQL ...)" | "(2) se quiserem, confirmar com o professor ... e confrontar os nomes com o plano de ensino (o quadro já declara o SQLite)" |
| **Auditoria 17** (*ocorrência adicional*, não listada) | "a pendência é documental (o quadro de temas não nomeia o SQL)" | "o quadro de temas declara o SQLite desde a rodada 5 (uso mínimo), com nomes **não confrontados com o plano de ensino** e **sem confirmação do professor**" |

**Preservado:** a ressalva de que o SQL tem **implementação mínima** (uma tabela, sem armazenar resultados); a **ausência de confronto com os nomes oficiais do plano de ensino**; o **histórico** de que o SQLite foi acrescentado ao quadro na **rodada 5**; as limitações técnicas e as pendências ainda verdadeiras. **Nada foi transformado em declaração de aprovação pelo professor.**

**Efeito nas classificações:** só duas linhas de status mudaram, ambas no **entregável "Quadro de temas"** (matriz B: Parcial → Atendido com ressalvas; auditoria 2.4: PENDENTE → APROVADO COM RESSALVAS), porque a única pendência era o SQL fora do quadro. **A contagem dos 43 requisitos oficiais não mudou** (18 · 11 · 10 · 3 e 1 N/A); G01 permanece ATENDIDO e G07 permanece PARCIALMENTE ATENDIDO.

### 11.4 Varredura de ocorrências antigas
Nos quatro documentos (matriz, auditoria, checklist e `temas.md`), **não resta nenhuma** afirmação de que o quadro de temas "não nomeia", "não declara" ou "deve passar a declarar" o SQL. Restam apenas, **de propósito**, o rótulo do item do checklist ("declarar o SQL/SQLite", que descreve o requisito, já marcado ✅), os textos novos que dizem "passou a declarar" e as notas de histórico.

### 11.5 Verificação final da rodada 6
| Verificação | Resultado |
|---|---|
| Coerência matriz × auditoria × checklist × `temas.md` | Os quatro dizem que o quadro de temas declara o SQLite (rodada 5), que o SQL tem uso mínimo e que os nomes não foram confrontados com o plano de ensino; os três temas usam os mesmos nomes, arquivos, captura `11` e teste de idempotência |
| Ressalvas técnicas | As 12 presentes na seção J da matriz, na 8.6 da auditoria e na 6.5 do checklist; **nenhuma removida** |
| Aprovação do professor | Nenhum documento a declara (apenas negações) |
| Markdown | Sem caracteres de controle e sem tabelas com número de colunas incorreto nos quatro documentos |
| Contagem oficial | Relida das tabelas F–I da matriz: **18 · 11 · 10 · 3 + 1 N/A**, inalterada; F05 e F06 seguem NÃO ATENDIDOS |
| Autoria e uso de IA | 38 passagens dos documentos de referência **sem alteração**; os termos de autoria/IA da matriz (0) e da auditoria (19) têm a mesma contagem antes e depois |
| Testes automatizados | **21 passed** (24,4 s), com `-p no:cacheprovider` e sem bytecode: **nenhum cache criado**; os testes treinam só em memória, e nenhum treino persistido foi executado |
| Hashes dos 6 arquivos protegidos | **6 de 6 idênticos** ao manifesto |
| Arquivos modificados | **Somente os três documentos autorizados** (matriz, auditoria e este relatório); `docs/checklist_entrega.md`, `docs/temas.md`, código, modelo, dados, regras, testes, scripts, dependências e caches **sem data posterior** ao início da rodada |
| Git | `main`, **0 commits, 0 remotos**; nenhuma operação de escrita |

### 11.6 Pendências restantes
- **Dependem da equipe (inalteradas):** declaração única de autoria e uso de IA; envio pelo Portal até 19/11/2026 às 23h55; decisão sobre disciplina 06 e prêmio; commit e publicação; turma e data da apresentação; documentar (ou declarar como limitação) acessibilidade, sustentabilidade, viabilidade e escuta de usuários; confrontar os nomes do quadro com o plano de ensino, se o obtiverem, e, se quiserem, confirmar com o professor; arquivar um log de ambiente limpo.
- **Documentais ainda abertas:** I-13 (escopo do manifesto em `auditoria_ia.md`), explicação do título `EVID_xxxx` no checklist, I-16 e I-17. *[Rodada 7 (seção 12): I-13 e `EVID_xxxx` foram **documentados**; I-17 teve a situação do PDF **registrada** (decisão do grupo pendente); **I-16 permanece pendente**, sem teste automatizado.]*

---

## 12. Rodada 7 (11/11/2026) — encerramento das pendências documentais: I-13, `EVID_xxxx`, I-17 e I-16

### 12.1 Escopo e restrições
Autorizado: documentar o escopo do manifesto (I-13) em `docs/auditoria_ia.md`; explicar o título `EVID_xxxx` em `docs/checklist_entrega.md`; verificar o PDF oficial e registrar a situação do enunciado (I-17) na matriz e na auditoria; registrar a situação do modelo ilegível (I-16, **fora do escopo de implementação**); e registrar a rodada neste relatório. Respeitadas as restrições: **nenhum** código de produção, teste, modelo, dado, regra de classificação ou script foi alterado (**`scripts/auditoria.py` não foi alterado**); nenhum treinamento; nenhuma operação Git; **nenhum arquivo foi copiado ou movido** (inclusive o PDF oficial); nenhuma declaração de autoria ou de uso de IA foi modificada. **Não foram feitas novas melhorias ou auditorias além das três pendências.**

### 12.2 Backup e documentos alterados
- **Backup:** `_backup_docs_pre_correcao_2026-11-11/rodada7_antes/` (`docs/matriz_requisitos.md`, `docs/auditoria_final_entrega.md`, `docs/checklist_entrega.md`, `docs/auditoria_ia.md`, `docs/relatorio_correcao_documental.md` e `_SHA256_antes_rodada7.txt`).
- **Alterados:** os cinco documentos acima.

### 12.3 Correções realizadas
| Pendência | Documento | O que foi registrado |
|---|---|---|
| **I-13** — escopo do manifesto | `docs/auditoria_ia.md` (nova subseção na seção 1) | O manifesto protege **exatamente seis arquivos** (`data/treino.csv`, `data/teste_rotulado.csv`, `data/teste_cego.csv`, `data/modelo/classificador.joblib`, `citizentech/classificador.py`, `citizentech/regras.py`; `scripts/auditoria.py:41–48`). A verificação comprova **só** a correspondência desses seis com os hashes do manifesto (`:57–62`) e **não** a integridade de todo o projeto. **Fora do manifesto:** o próprio script de auditoria, os demais módulos (inclusive `texto.py`, cuja alteração mudaria as previsões sem ser detectada), `validar.py`, `gerar_treino.py`, os testes, as dependências, `data/inbox/`, `validacao_independente/`, a documentação e o próprio manifesto (sem assinatura nem carimbo externo). **Recriação:** o script cria o manifesto se ele não existe (`:55–93`); a ausência **não** é verificação válida de integridade histórica. **Data:** `data_auditoria` indica quando os hashes foram **registrados**, não uma garantia independente de integridade anterior. A matriz (J, itens 9 e 10) foi alinhada e aponta para essa subseção |
| **`EVID_xxxx`** — artefato de captura | `docs/checklist_entrega.md` (seção 3.2) | `EVID_xxxx` é o **título da janela de console** gerado pelo procedimento de captura; aparece em **12 das 13 imagens** (todas, exceto a `01b`); **não é um identificador produzido pelo CitizenTech** (não está em nenhum arquivo de saída, log ou código); os **identificadores reais** são `run_id` e `protocolo`; as imagens registram **execuções reais** do protótipo. Coerente com o Plano B de `docs/roteiro_apresentacao.md` (que diz "visível na maioria das imagens", compatível com 12 de 13; o roteiro **não foi alterado**, por estar fora do escopo autorizado) |
| **I-17** — enunciado oficial | `docs/matriz_requisitos.md` (tabela de fontes e novo parágrafo) e `docs/auditoria_final_entrega.md` (8.1 e 8.5) | **Verificado:** o PDF está disponível em `C:\Users\henry.costa\Downloads\`; nome exato `2TIAP(F-Y)-2026 - GS 2026.2.pdf`, 2.021.801 bytes, SHA-256 `b9af6e4e647ce87531d043668b60c882574f37f39ce4c61fcf08184dfd61c215`. O repositório tem **0 PDFs**. Registrado que o enunciado foi **consultado** na revisão documental, que a cópia usada está **fora do repositório, em `Downloads`**, que o conteúdo foi **analisado, mas não está versionado**, e que a **preservação da referência no repositório continua sendo decisão pendente**. **Avaliação:** a incorporação a `docs/enunciado/` **não é claramente recomendável** (material oficial da FIAP; repositório possivelmente público, já que a disciplina 06 exige o GitHub; sem necessidade técnica). **Recomendação registrada, sem cópia:** manter a referência (nome, data, tamanho e SHA-256) e, se o grupo quiser guardar o arquivo, fazê-lo em local privado ou após confirmar com o professor. **Sem duplicatas:** `gsrpa.pdf` (570.387 bytes, também em `Downloads`) é outro documento, o complemento da disciplina 01, de que o repositório guarda só as imagens `p1.png` e `p2.png` |
| **I-16** — modelo ilegível (fora do escopo) | `docs/auditoria_final_entrega.md` (8.5) | O cenário foi **simulado em memória** em 11/11/2026 (`joblib.load` e `treinar` substituídos, sem escrever arquivos nem treinar; script de uso único, **não versionado**), mas **não possui teste automatizado específico**. A decisão de implementar o teste **fica pendente de autorização técnica separada**. **Nenhum teste ou código foi alterado** |

**Histórico atualizado:** a matriz (parágrafo de reclassificações) e a auditoria (nota inicial e 8.5) receberam notas da rodada 7; as rodadas 1 a 6 foram preservadas. As **classificações dos requisitos não mudaram** (18 · 11 · 10 · 3 + 1 N/A).

### 12.4 Verificação final da rodada 7
| Verificação | Resultado |
|---|---|
| Coerência entre os cinco documentos | A lista dos seis arquivos é idêntica na subseção da `auditoria_ia.md` e na seção J da matriz e coincide com o manifesto real; auditoria e checklist falam em "seis arquivos" sem divergência; as linhas de `scripts/auditoria.py` citadas (41–48, 55–93, 57–62) conferem com o código; as notas sobre o PDF e sobre I-16/I-17 são as mesmas na matriz, na auditoria e neste relatório |
| Explicação de `EVID_xxxx` | Presente no checklist, com os oito elementos pedidos, e coerente com o Plano B do roteiro |
| Enunciado oficial | **Nenhum documento o declara versionado**; matriz, auditoria e checklist dizem "fora do repositório"; o repositório tem 0 PDFs |
| I-16 | **Continua registrado como pendência** (sem teste automatizado; decisão técnica separada) |
| Ressalvas técnicas | Conferidas as 12 (seção J da matriz, 8.6 da auditoria e 6.5 do checklist); **nenhuma removida** |
| Markdown | Sem caracteres de controle e sem tabelas com número de colunas incorreto nos quatro documentos verificados antes deste relatório (este é verificado em seguida) |
| Autoria e uso de IA | Passagens dos documentos de referência **sem alteração** (conferência com os backups originais) |
| Testes automatizados | **21 passed** (5,2 s), com `-p no:cacheprovider` e sem bytecode: **nenhum cache criado**; os testes treinam só em memória, e nenhum treino persistido foi executado |
| Hashes dos 6 arquivos protegidos | **6 de 6 idênticos** ao manifesto |
| Arquivos modificados | **Somente os cinco documentos autorizados**; código, testes, modelo, dados, regras, scripts, dependências, caches, README, roteiro, `temas.md` e `docs/enunciado/` **sem data posterior** ao início da rodada |
| Git | `main`, **0 commits, 0 remotos**; nenhuma operação de escrita |

### 12.5 Pendências restantes
- **I-16:** teste automatizado do cenário de modelo ilegível, **pendente de autorização técnica separada** (exige alterar `tests/`).
- **I-17:** decisão do grupo sobre preservar a referência do enunciado oficial no repositório (ver a recomendação em 12.3).
- **Dependem da equipe (inalteradas):** declaração única de autoria e uso de IA; envio pelo Portal até 19/11/2026 às 23h55; decisão sobre disciplina 06 e prêmio; commit e publicação; turma e data da apresentação; documentar (ou declarar como limitação) acessibilidade, sustentabilidade, viabilidade e escuta de usuários; confrontar os nomes do quadro de temas com o plano de ensino e, se quiserem, confirmar com o professor; arquivar um log de ambiente limpo.
- **Encerramento:** **esta é a última rodada de correções documentais gerais**; novas alterações dependem de autorização específica.
