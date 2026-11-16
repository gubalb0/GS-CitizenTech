# Plano de entrega final — Global Solution 2026.2 | CitizenTech (RPA + IA)

Data da análise: **11/11/2026**. Prazo oficial das atividades das disciplinas: **19/11/2026 às 23h55**, pelo Portal do Aluno (PDF oficial, p. 11), ou seja, **8 dias** a partir da data desta análise.

**Natureza deste documento:** análise de preparação, **somente leitura**. Nada foi executado além de leituras e de uma conferência de hashes; não houve treinamento, nem alteração de código, modelo, dados, testes, scripts, dependências ou documentos existentes, nem operação Git, nem publicação. **Este é o único arquivo criado nesta etapa.** As ações propostas **dependem de autorização** antes de qualquer execução.

**Fontes:** estrutura real do repositório; `docs/matriz_requisitos.md` (requisitos do PDF oficial `2TIAP(F-Y)-2026 - GS 2026.2.pdf`, que está **fora do repositório**, em `Downloads`, e do complemento `docs/enunciado/p1.png` e `p2.png`); `docs/checklist_entrega.md`; `docs/roteiro_apresentacao.md`; `docs/auditoria_final_entrega.md`; `docs/relatorio_correcao_documental.md`. Onde um número vem de uma execução anterior, isso está dito.

---

## 1. Resumo executivo

- **O que está pronto para a disciplina 01:** um protótipo executável (`main.py`), com RPA, IA, resiliência, idempotência, evidências de validação com dados sintéticos, três temas com função real no fluxo (tratamento de arquivos e dados, integração com APIs, banco de dados SQL), documentação de ética/ODS e 13 capturas de tela reais. Os 6 arquivos protegidos pelo manifesto seguem idênticos; o último resultado dos testes registrado é **21 passed** (rodada 7; **não reexecutados** nesta etapa).
- **O que impede considerar a entrega concluída:** (1) **nenhum envio foi feito pelo Portal** (prazo 19/11/2026 às 23h55); (2) o **Git não tem commits nem remoto**; (3) a **declaração de autoria e uso de IA** está divergente entre documentos e depende da equipe; (4) **turma** não informada; (5) o plano de ensino não foi consultado (nomes dos temas não confrontados).
- **Segurança para publicação:** **nenhum problema CRÍTICO ou ALTO** encontrado (não há `.env`, chaves, tokens ou credenciais; nenhuma chave é necessária). Há **4 pontos MÉDIOS** (zipar a pasta de trabalho; nomes e RM dos integrantes em 8 documentos; identidade Git global; material oficial da FIAP em `docs/enunciado/`) e itens BAIXOS (seção 4).
- **Apresentação:** o roteiro cobre 11 dos 12 elementos pedidos, e **um parcialmente**: **os "três temas da disciplina" não são apresentados com os nomes e a função dos três temas atendidos** (o roteiro lista 4 técnicas; o SQLite só aparece de passagem na etapa 5). A demonstração principal **funciona sem internet**, mas **fica mais lenta e sem as cidades** (seção 6).
- **A entrega da disciplina 01 não depende da disciplina 06 nem da premiação.** Vídeo de até 7 minutos, documentação ABNT, GitHub e integração de todos os módulos são exigências da **disciplina 06** (p. 14) e/ou do **prêmio** (p. 11), e **nenhum deles existe** (seção 8, grupos B e C). Se o grupo decidir cumpri-los, o trabalho restante é grande e foge do repositório atual.
- **Veredito desta análise:** o projeto **não está pronto para ser dado como entregue**, mas está **tecnicamente pronto para ser organizado e enviado** assim que a equipe tomar as decisões listadas na seção 9. As limitações técnicas conhecidas **continuam valendo** (dados sintéticos; sem validação independente; sem prova de desempenho real; **inapto para triagem clínica**; falha grave de urgência; limiar 0,45 sem calibração; manifesto de 6 arquivos; recriação do manifesto quando ausente; Git sem commits).

---

## 2. Estado atual do projeto

| Aspecto | Estado | Evidência |
|---|---|---|
| Execução | Ponto de entrada `python main.py --reset`; saída conhecida: 25 lidos, 21 processados, 4 para revisão humana, 3 rejeitados, 1 duplicado, 2 arquivos defeituosos tratados | `main.py`; captura `docs/evidencias_visuais/03_execucao_normal_main_reset.png`; `docs/exemplo_saida/` |
| Testes | **21 passed** na última execução registrada (rodada 7), com `-p no:cacheprovider`; **não reexecutados nesta etapa** | `tests/test_citizentech.py`, `tests/test_avaliacao_independente.py`; captura `01_testes_pytest_21_passed.png` |
| Integridade | **6 de 6** arquivos protegidos idênticos ao manifesto (conferido agora, por leitura) | `docs/modelo_congelado.json` |
| IA | TF-IDF (palavras + caracteres) + Regressão Logística; 87,5% (teste 1, n=80) e 82,5% (teste 2, n=40); 9 erros em 84 encaminhados sem humano; urgências protegidas 14/15 | `docs/auditoria_ia.md`, `docs/auditoria_resultados.md`, captura `08` |
| Validação independente | **Não realizada** (só a estrutura existe) | `validacao_independente/README.md` |
| Git | Branch `main`, **0 commits, 0 remotos**; 73 arquivos entrariam num primeiro `git add .` | `git ls-files -co --exclude-standard` (leitura) |
| Documentação | README, 16 documentos em `docs/`, 13 capturas, 4 arquivos de exemplo de saída | seção 3 |
| Requisitos oficiais | 43 identificados no PDF: 18 atendidos, 11 parciais, 10 não atendidos, 3 não comprovados, 1 N/A | `docs/matriz_requisitos.md` (seções F a J) |

**O que a documentação não prova:** a existência de um documento não comprova o funcionamento. Funcionamento comprovado por **execução e captura**: ponta a ponta, rejeições, mascaramento, revisão humana, falha de API, idempotência (capturas `03` a `07` e `11`). Comprovado **apenas por relato**, sem log: a execução em ambiente limpo (venv novo).

---

## 3. Inventário dos arquivos (sem remover, mover ou renomear nada)

Total no disco (sem `.git`): **139 arquivos, ~3,0 MiB**. Entrariam no Git: **73 arquivos**. O restante é gerado ou ignorado.

| Categoria | Caminhos | Arquivos | Tamanho | Versionar? |
|---|---|---|---|---|
| **Código-fonte necessário** | `main.py`; `citizentech/` (`__init__`, `classificador`, `config`, `estado`, `geo`, `ingestao`, `logs`, `pipeline`, `regras`, `texto`, `validacao`) | 12 | 23 KiB | **Sim** |
| **Scripts** | `scripts/auditoria.py`, `scripts/gerar_treino.py`, `scripts/validar.py` | 3 | 27 KiB | **Sim** |
| **Testes** | `tests/test_citizentech.py`, `tests/test_avaliacao_independente.py` | 2 | 9 KiB | **Sim** |
| **Configuração** | `.env.example`, `.gitignore`, `.gitattributes` | 3 | 1 KiB | **Sim** |
| **Dependências** | `requirements.txt`, `requirements-congelado.txt` | 2 | <1 KiB | **Sim** |
| **Datasets** | `data/treino.csv` (640 sintéticos), `data/teste_rotulado.csv` (80), `data/teste_cego.csv` (40) | 3 | 83 KiB | **Sim** |
| **Caixa de entrada da demonstração** | `data/inbox/` (4 arquivos, 2 deliberadamente defeituosos) | 4 | 2 KiB | **Sim** |
| **Modelo congelado** | `data/modelo/classificador.joblib` (hash em `docs/modelo_congelado.json`) | 1 | 465 KiB | **Sim, de propósito** (o `.gitignore` o permite) |
| **Documentação** | `README.md`; `docs/` (16: matriz, checklist, roteiro, perguntas, auditorias, evidências, ética/ODS, temas, relatórios, manifesto, resultados `.json`) | 17 | 389 KiB | **Sim** |
| **Evidências visuais** | `docs/evidencias_visuais/` (13 PNG) | 13 | 772 KiB | **Sim** |
| **Exemplo de saída** | `docs/exemplo_saida/` | 4 | 12 KiB | **Sim** |
| **Enunciado (imagens do complemento)** | `docs/enunciado/p1.png`, `p2.png` | 2 | 432 KiB | **A decidir** (ver M4) |
| **Validação independente (estrutura)** | `validacao_independente/` (protocolo, instruções, `avaliar.py`, modelos de planilha) | 7 | 19 KiB | **Sim** (o conjunto real, quando existir, fica ignorado) |
| **Gerados em execução (ignorados)** | `logs/execucao.log` (29 KiB), `saida/` (4 arquivos), `data/estado.db` | 6 | ~53 KiB | **Não** (reproduzíveis com `python main.py`) |
| **Temporários/caches (ignorados)** | `.pytest_cache/`, `*/__pycache__/` | 20 | 104 KiB | **Não** |
| **Backups (ignorados)** | `_backup_docs_pre_correcao_2026-11-11/` (cópias de documentos de 7 rodadas) | 40 | 643 KiB | **Não** (ver M1) |

**Arquivos desnecessários para a entrega** (não precisam ir ao Portal nem ao GitHub): `_backup_docs_pre_correcao_2026-11-11/`, `.pytest_cache/`, `__pycache__/`, `logs/`, `saida/`, `data/estado.db`. **Nada foi removido.** Fora do repositório: o PDF oficial e `gsrpa.pdf` (em `Downloads`).

---

## 4. Resultado da revisão de segurança para publicação

Escopo: leitura dos arquivos; **nenhum valor sensível foi copiado para este documento**. Padrões de segredo foram procurados nos **73 arquivos versionáveis** (as imagens e o `.joblib` não foram varridos por texto, exceto uma busca por caminhos locais no `.joblib`).

### CRÍTICO e ALTO
**Nenhum encontrado.**
- **`.env`:** não existe; só `.env.example`, que contém apenas **nomes** de variáveis (`CEP_API_URL`, `CEP_TIMEOUT_S`, `CEP_MAX_RETRIES`, `CEP_BACKOFF_S`, `CONFIANCA_MINIMA`) e uma linha comentada de chave **vazia**.
- **Chaves, tokens e credenciais:** 7 padrões de busca (chaves `sk-`, AWS, GitHub, Slack, `Bearer`, chaves privadas e atribuições `api_key/secret/password/token`), **0 ocorrências**. Nenhuma API do projeto exige chave (a ViaCEP é pública).
- **Arquivos de segredo** (`.pem`, `.key`, `credentials*`, `secrets*`…): nenhum.

### MÉDIO
| ID | Problema | Onde | Recomendação (não aplicada) |
|---|---|---|---|
| **M1** | **Zipar a pasta de trabalho** para o Portal incluiria `.git`, `logs/`, `saida/`, `data/estado.db`, caches e `_backup_docs_pre_correcao_2026-11-11/` (40 documentos antigos, com caminhos locais e versões superadas) | Raiz do projeto | Enviar somente arquivos versionados (por exemplo, um `git archive` depois do commit) ou uma cópia limpa; **não** zipar a pasta de trabalho |
| **M2** | **Nomes e RM dos 3 integrantes** em 8 arquivos versionáveis (README e 7 documentos de `docs/`) | `README.md:8`, `docs/` | Publicar só com **ciência de cada integrante**; se o repositório for público, decidir se o RM fica visível |
| **M3** | **Identidade Git global configurada** (nome e e-mail; valores **não exibidos**): o primeiro commit usará essa identidade, que ficará visível no GitHub | Configuração do Git | Conferir antes do commit qual identidade será usada (por exemplo, o e-mail "noreply" do GitHub) |
| **M4** | **Material oficial da FIAP** (`docs/enunciado/p1.png` e `p2.png`, 432 KiB) seria publicado | `docs/enunciado/` | Decidir antes do commit (I-17); o PDF oficial já está fora do repositório |

### BAIXO
| ID | Problema | Onde | Observação |
|---|---|---|---|
| B1 | **Caminho local e usuário do Windows** nas **13 capturas** (prompt `C:\Users\…\Projetos\…`) e em 2 documentos (`docs/matriz_requisitos.md`, `docs/relatorio_correcao_documental.md`) | `docs/evidencias_visuais/`, 2 `.md` | Sem credencial; revela apenas o nome de usuário local |
| B2 | **Dados pessoais fictícios** (1 e-mail, 1 CPF e 1 telefone sintéticos) em `data/inbox/solicitacoes_lote1.csv` (S010 e S018) e nos testes | `data/inbox/`, `tests/test_citizentech.py` | Sintéticos e usados para testar o mascaramento; **nenhum dado pessoal real** foi encontrado |
| B3 | O **`.joblib` é um arquivo pickle**: carregar pickle de origem não confiável executa código | `data/modelo/classificador.joblib` | O arquivo é próprio e seu hash está no manifesto; 0 caminhos locais embutidos. A conferência só ocorre quando `scripts/auditoria.py` é executado (o `main.py` não a faz) |
| B4 | `validacao_independente/LACRE.json` e os relatórios **não estão ignorados** | `validacao_independente/` | Ainda não existem; quando forem gerados conterão o nome do custodiante |
| B5 | O `.gitignore` não cobre `.idea/`, `.vscode/`, `*.zip`, `.DS_Store` | `.gitignore` | Nenhum desses arquivos existe hoje; cobertura opcional |
| B6 | `logs/execucao.log`, `saida/` e `data/estado.db` contêm dados da execução | `logs/`, `saida/`, `data/` | **Ignorados pelo Git** (confirmado); o log tem 267 linhas e **0 caminhos locais**; as saídas têm PII mascarado; o estado guarda só hashes |

**Informações de ambiente:** os documentos citam Windows 11 e Python 3.14.2 (útil e sem risco); não há nome de máquina. **Datasets:** sintéticos; **sem dados pessoais reais**.

---

## 5. Checklist da disciplina 01 (AI for Robotic Process Automation)

Legenda: **PRONTO** (há evidência) · **ORGANIZAR** (existe, mas precisa de arrumação) · **DOCUMENTAR** · **PENDENTE** · **EQUIPE** (depende de confirmação ou decisão da equipe).

| # | Item | Estado | Caminho ou evidência |
|---|---|---|---|
| 1 | Protótipo executável com ponto de entrada claro | **PRONTO** | `main.py`; captura `03`; `docs/matriz_requisitos.md` (A, G02) |
| 2 | Funcionamento ponta a ponta, sem intervenção | **PRONTO** | capturas `03`, `04a`, `05`, `06`; `docs/exemplo_saida/` |
| 3 | **Três temas** com função real: tratamento de arquivos e dados; integração com APIs; banco de dados SQL | **PRONTO**, com ressalvas de profundidade (biblioteca padrão; API acessória; SQL de uso mínimo) | `docs/matriz_requisitos.md` (G.2); `docs/temas.md`; `citizentech/ingestao.py`, `validacao.py`, `texto.py`, `pipeline.py`, `geo.py`, `estado.py` |
| 4 | Resiliência (arquivo ausente/corrompido, dado inválido, API fora do ar, erro isolado) | **PRONTO** | capturas `03`, `07`, `11`; `tests/test_citizentech.py` |
| 5 | Evidências de validação com dados de teste | **PRONTO**, com ressalvas (sintéticos; não independentes) | `docs/auditoria_ia.md`, `docs/evidencias.md`, `docs/evidencias_resultados.md`, capturas `01`, `08` |
| 6 | Proteção de dados e ética | **PRONTO** | `docs/etica_ods.md`; mascaramento (captura `04b`) |
| 7 | README com problema, execução e chaves | **PRONTO** | `README.md` (turma ausente) |
| 8 | Quadro de temas | **PRONTO**, com a ressalva de que os nomes **não foram confrontados com o plano de ensino** | `docs/temas.md` |
| 9 | Grupo em trio, dupla ou individual | **PRONTO** (3 integrantes) | `README.md:8`; **EQUIPE**: conferir os dados |
| 10 | **Envio pelo Portal do Aluno** (Trabalhos), direto ao professor, **até 19/11/2026 às 23h55** | **PENDENTE** | PDF p. 11 (slide 21) |
| 11 | **Forma do envio**: o complemento aceita repositório Git, notebook Colab ou Jupyter; o PDF define o Portal como canal | **EQUIPE** + **ORGANIZAR** | Decidir o que se anexa ou o link; Git sem commits |
| 12 | Regras específicas da disciplina no portal ("verifique no portal ... ou com o professor") | **EQUIPE** | Não conferido (sem acesso ao portal) |
| 13 | **Declaração única de autoria e uso de IA** | **EQUIPE** (divergência mantida) | `docs/checklist_entrega.md` (seção 1) |
| 14 | Turma | **EQUIPE** | Não consta em nenhum documento |
| 15 | Nomes oficiais dos temas (plano de ensino) | **EQUIPE** (opcional) | O PDF só dá exemplos; plano de ensino indisponível |
| 16 | Roteiro com os três temas | **DOCUMENTAR** | `docs/roteiro_apresentacao.md` (§4); ver seção 6 |
| 17 | Aviso no README de que, num clone, `scripts/validar.py` pode regravar o modelo (via `carregar_modelo`) e fazer a auditoria abortar | **DOCUMENTAR** | `docs/relatorio_correcao_documental.md` (8.6); **não aplicado** |
| 18 | Evidência de ambiente limpo (log) | **PENDENTE** (hoje só relato) | `docs/matriz_requisitos.md`; sem log |
| 19 | Limpar a seleção do que será enviado (sem backups, logs, caches) | **ORGANIZAR** | seção 3 e M1 |

**Fora do que a disciplina 01 exige:** validação independente, correção de urgências, revisão por profissional de saúde (recomendações do projeto, não exigências do PDF).

---

## 6. Checklist da apresentação

Avaliação do `docs/roteiro_apresentacao.md` (12 etapas, **~12,75 min** somados) contra os 12 elementos pedidos. **Nada foi executado** nesta análise; a coluna "Risco" usa o que já foi medido (execuções de 10 e 11/11) ou calculado a partir dos parâmetros, e indica quando é estimativa.

| # | Elemento a demonstrar | Cobertura no roteiro | Evidência de apoio | Risco |
|---|---|---|---|---|
| 1 | Problema e público-alvo | **Sim** (§1 e §2) | `README.md` (Problema, Público afetado) | — |
| 2 | Proposta CitizenTech | **Sim** (§3) | `README.md` (Objetivo) | — |
| 3 | Arquitetura | **Sim** (§4) | diagrama do `README.md` (**sem captura**) | Exibir o README no computador da apresentação |
| 4 | **Três temas da disciplina** | **Parcial**: o §4 lista 4 técnicas (RPA de arquivos, NLP/ML, regras, API+resiliência) e o SQLite aparece só de passagem no §5; **não apresenta os três temas como tais** (arquivos e dados; APIs; SQL) | `docs/temas.md`; `docs/matriz_requisitos.md` (G.2) | **Alto para a banca**: arriscado não mostrar o SQL e a função de cada tema; ajustar o roteiro (**DOCUMENTAR**) |
| 5 | Funcionamento ponta a ponta | **Sim** (§7, ao vivo) | `python main.py --reset`; capturas `03`, `04a`, `06` | **Internet** (ViaCEP): sem rede, cidades vazias e execução mais lenta |
| 6 | Classificação por IA | **Sim** (§6) | `docs/modelo_congelado.json`; captura `02` | A captura `02` não mostra parâmetros; abrir o manifesto |
| 7 | Encaminhamento e revisão humana | **Sim** (§8) | `saida/revisao_humana.csv`; captura `05` | Casos S008, S009, S014, S022; **S014 é excesso de cautela** (dizer isso) |
| 8 | Resiliência | **Sim** (§9, ao vivo) | captura `07`; testes | **Offline**: a simulação usa `127.0.0.1:9`, **não depende de internet**; comando em PowerShell (em bash há equivalente) |
| 9 | Idempotência | **Sim, opcional** (§7) | captura `11` | Esquecer o `--reset` mostra "0 processados" (é a própria demonstração; avisar) |
| 10 | Evidências e métricas | **Sim** (§10) | captura `08`; `docs/auditoria_resultados.md` | Duas definições de "automático"; usar a **por status** (6/57, 3/27, 9/84) |
| 11 | Limitações e responsabilidade no uso da IA | **Sim** (§11, "não pule") | captura `09`; `docs/etica_ods.md` | Dizer, **antes** de perguntarem: dados sintéticos, falha do trauma craniano, inapta para triagem clínica |
| 12 | Benefício esperado para o cidadão | **Parcial** (§12): descreve o benefício **potencial**; o ganho de tempo **nunca foi medido** | `docs/etica_ods.md` | Não afirmar impacto real |

**Demonstrações que podem falhar ou depender de internet:**
- **ViaCEP** (§7, ao vivo): 24 registros com CEP, **6 CEPs distintos** (5 em formato válido). Sem internet, as cidades ficam vazias; **estimativa (não medida):** até **~45 s adicionais** se cada tentativa estourar o timeout de 4 s (3 tentativas, espera de 1 e 2 s, circuit breaker após 3 CEPs), bem menos se a falha for imediata. Com internet, a execução registrada levou **11 a 16 s**.
- **Ambiente da máquina da apresentação:** só foi testado Windows + Python 3.14.2; o roteiro usa PowerShell; o `pip install` exige internet (fazer antes). Um modelo `.joblib` que não carregue por versão de biblioteca é re-treinado **em memória** pelo `main.py` (caminho **sem teste automatizado**, I-16).
- **Arquivos reescritos pelas demonstrações e versionados:** `python scripts/auditoria.py` reescreve `docs/auditoria_resultados.md/.json` (conteúdo estável) e `python scripts/validar.py` reescreve `docs/evidencias_resultados.md/.json` (com novos tempos); rodá-los **suja a árvore do Git**. O `validar.py` **não** consta no roteiro.
- **Largura do terminal:** os logs quebram em terminal estreito; maximizar a janela.
- **Duração:** ~12,75 min; o tempo disponível da banca **não é conhecido** (o vídeo das disciplinas 06/prêmio é de no máximo 7 min).
- **Plano B:** `docs/roteiro_apresentacao.md` (mapa etapa → captura) e `docs/exemplo_saida/`; **não há captura** da listagem de `data/inbox/`, do diagrama do README nem da tabela comparativa de resultados.

---

## 7. Checklist do GitHub / repositório

### 7.1 Estado atual do Git (somente leitura)
Branch `main`; **0 commits; 0 remotos**; **73 arquivos** no primeiro `git add .`; ignorados presentes: `.pytest_cache/`, `__pycache__/`, `data/estado.db`, `logs/`, `saida/`, `_backup_docs_pre_correcao_2026-11-11/`; `core.autocrlf=true` global, mas o `.gitattributes` (`* -text`) preserva os bytes (os hashes do manifesto dependem disso). O PDF da disciplina 06 exige o **GitHub do projeto**; para a disciplina 01 o complemento aceita Git, Colab ou Jupyter.

### 7.2 O que versionar, o que ignorar
| Grupo | Itens | Evidência |
|---|---|---|
| **Versionar (73 arquivos)** | `main.py`; `citizentech/` (11); `scripts/` (3); `tests/` (2); `data/treino.csv`, `data/teste_*.csv`, `data/inbox/` (4), `data/modelo/classificador.joblib`; `requirements*.txt`; `.env.example`, `.gitignore`, `.gitattributes`; `README.md`; `docs/` (16 + 13 PNG + `exemplo_saida/` 4 + `enunciado/` 2); `validacao_independente/` (7) | `git ls-files -co --exclude-standard` |
| **Já ignorados (conferido com `git check-ignore`)** | `.env`, `logs/`, `saida/`, `data/estado.db`, `.pytest_cache/`, `__pycache__/`, `_backup_docs_pre_correcao_*/`, `validacao_independente/conjunto/`, `.venv/`, `*.key`, `*.pem`, `*.sav` | `.gitignore` |
| **Opcionalmente ignorar** (nenhum existe hoje) | `.idea/`, `.vscode/`, `*.zip`, `.DS_Store`, `Thumbs.db` | B5 |
| **Sensíveis a decidir** | nomes/RM (M2), identidade Git (M3), `docs/enunciado/` (M4) | seção 4 |

### 7.3 Estrutura recomendada (a atual já serve; **não mover nada**)
```
README.md  main.py  requirements.txt  requirements-congelado.txt  .env.example  .gitignore  .gitattributes
citizentech/  scripts/  tests/  data/ (treino, testes, inbox, modelo)  validacao_independente/
docs/ (documentação, evidencias_visuais/, exemplo_saida/, modelo_congelado.json)
```

### 7.4 Documentação necessária para reprodução (estado)
| Item | Estado | Evidência |
|---|---|---|
| Instalação, configuração, execução e testes | **Existe** | `README.md` ("Instalação e configuração", "Como executar", "Como executar os testes…") |
| Dependências e versões exatas | **Existe** | `requirements.txt`, `requirements-congelado.txt` |
| Chaves | **Não há** (nenhuma necessária) | `.env.example` |
| Modelo e hashes | **Existe** | `docs/modelo_congelado.json` |
| Aviso do risco de `validar.py` num clone | **Falta** (DOCUMENTAR) | seção 5, item 17 |
| Licença (`LICENSE`) | **Não existe**; decisão da equipe | — |
| Ambiente limpo comprovado | **Falta** log | seção 5, item 18 |

### 7.5 Pendências antes do primeiro commit (nenhuma executada)
1. **Equipe:** visibilidade do repositório (privado ou público) e consentimento dos 3 integrantes quanto a nome e RM (M2).
2. **Equipe:** confirmar a identidade Git que aparecerá no commit (M3).
3. **Equipe:** decidir sobre `docs/enunciado/` (M4) e sobre incluir os documentos internos de processo (`docs/relatorio_correcao_documental.md`, `docs/auditoria_final_entrega.md`).
4. **Equipe:** resolver a declaração de autoria e uso de IA antes de publicar o README.
5. **Antes do commit:** reconferir `git status`, os hashes dos 6 arquivos e os testes (**exige autorização**).
6. **Depois do commit:** **conferir um clone limpo** (venv novo, `pip install -r requirements.txt`, `python scripts/auditoria.py`, `python main.py --reset`, `python -m pytest -q`) e **arquivar o log**, o que também fecha a pendência de ambiente limpo. Atenção: **no clone, rodar `scripts/auditoria.py` antes de `scripts/validar.py`**.

---

## 8. Entregáveis e decisões

Os quatro grupos **não são uma única entrega**. A disciplina 06 e o prêmio **não são obrigatórios para entregar a disciplina 01**.

### A. Obrigatórios para a disciplina 01 (PDF p. 11; complemento)
Ver a seção 5. Resumo: envio pelo Portal até 19/11/2026 às 23h55 (**pendente**); protótipo, README, quadro de temas, evidências e parágrafo de ética/ODS (**prontos**, com as ressalvas listadas); três temas (**prontos**); declaração de autoria e uso de IA, turma e forma do envio (**equipe**).

### B. Obrigatórios para a disciplina 06 — Governança em IA & Business Analytics (PDF p. 14)
| Item | Estado | Evidência |
|---|---|---|
| Vídeo de até 7 minutos | **Não existe** | o roteiro (~12,75 min) é para a banca, não é um vídeo |
| Documentação em formato ABNT | **Não existe** | os documentos são Markdown |
| GitHub do projeto | **Não existe** | Git sem commits e sem remoto |
| Demonstrar a integração de **todos** os módulos da GS | **Não existe neste repositório**; os módulos das disciplinas 02–05 e 07–09 **não foram encontrados** (existência fora dele: **não comprovada**) | `docs/matriz_requisitos.md` (H.2) |
| Aplicar ao contexto de Governança em IA e Business Analytics | **Parcial**: há material de governança de IA; não há Business Analytics | `docs/etica_ods.md`, `docs/auditoria_ia.md`, `docs/modelo_congelado.json` |
| Envio pelo Portal até 19/11/2026 às 23h55 | **Pendente** | PDF p. 11 |

### C. Obrigatórios para concorrer à premiação (opcional; PDF p. 11)
| Item | Estado | Evidência |
|---|---|---|
| Vídeo pitch de até 7 minutos com **solução integradora** | **Não existe** | — |
| Envio pelo Portal "na disciplina indicada" | **Não comprovado**: o PDF não identifica qual é | PDF p. 11 |
| Se é o mesmo vídeo da disciplina 06 | **Não informado** no PDF | — |
| "Challenge Sprint" em 30/11/2026 | **Não descrito** no PDF; fora deste plano | PDF p. 10 |

### D. Recomendações que melhoram a apresentação (**não são exigências comprovadas**)
1. Atualizar o roteiro para apresentar os **três temas** pelos nomes do PDF, com a função e a evidência de cada um (`docs/roteiro_apresentacao.md`, §4).
2. Ensaiar **offline e online**, cronometrando; confirmar o tempo disponível.
3. Abrir antes `README.md` (diagrama), `docs/auditoria_resultados.md`, `docs/modelo_congelado.json` e `saida/`; deixar o terminal maximizado.
4. Preparar o Plano B (capturas e `docs/exemplo_saida/`) e dizer que são pré-gerados.
5. Avisar no README o risco do `validar.py` num clone; considerar uma `LICENSE`.
6. Se o grupo optar por vídeo (disciplina 06 ou prêmio), escrever um **roteiro próprio de até 7 min**.
7. Documentar (ou declarar como limitação) acessibilidade, sustentabilidade, viabilidade e escuta de usuários, **só o que for verdadeiro**.
8. Teste automatizado do cenário de modelo ilegível (I-16): **requer autorização técnica separada**.

---

## 9. Pendências da equipe (nenhuma pode ser resolvida pela documentação)

| # | Pendência | Prazo/observação |
|---|---|---|
| 1 | **Enviar a atividade pelo Portal** (o que e por quem) | **19/11/2026 às 23h55** |
| 2 | **Declaração única de autoria e uso de IA**, conforme as regras da FIAP | antes do envio e de publicar |
| 3 | **Decidir sobre a disciplina 06 e o prêmio** (fazer ou não; vídeo, ABNT, GitHub, módulos) | decide o escopo restante |
| 4 | **Autorizar commit e publicação**; escolher a visibilidade; confirmar identidade Git e consentimento (nome/RM) | antes do primeiro commit |
| 5 | **Turma** e **data da apresentação** (não constam no PDF) | — |
| 6 | **Confirmar os dados dos integrantes** copiados do README | — |
| 7 | **Conferir no portal** as regras específicas da disciplina 01 e o que é o Challenge Sprint | — |
| 8 | **Confrontar os nomes dos temas com o plano de ensino** e, se quiserem, confirmar com o professor | opcional |
| 9 | **Decidir sobre `docs/enunciado/`** (I-17) e sobre os documentos internos de processo | antes do commit |
| 10 | **Autorizar** os ajustes documentais da seção 8-D (roteiro, aviso do README, licença) | — |
| 11 | **Decidir sobre o teste do modelo ilegível** (I-16) | autorização técnica separada |
| 12 | Documentar acessibilidade, sustentabilidade, viabilidade e escuta de usuários (ou declarar como limitação) | opcional |

---

## 10. Ordem recomendada de execução (**todas as etapas aguardam autorização**)

| Etapa | Quando | Ação | Quem | Depende de |
|---|---|---|---|---|
| 1 | 11–12/11 | Decidir: autoria/IA; visibilidade; disciplina 06 e prêmio (sim/não); forma de envio; consultar o portal e o professor | Equipe | — |
| 2 | 12–13/11 | Resolver M2, M3 e M4 (nomes/RM, identidade Git, enunciado) | Equipe | Etapa 1 |
| 3 | 13/11 | Ajustes documentais autorizados: roteiro (três temas), aviso do `validar.py`, turma, licença | Assistente, com autorização | Etapas 1–2 |
| 4 | 13–14/11 | Reconferir hashes e rodar os 21 testes, sem cache | Assistente, com autorização | Etapa 3 |
| 5 | 14/11 | Primeiro commit e, se decidido, publicação no GitHub | Equipe/Assistente, com autorização | Etapas 1–4 |
| 6 | 14–15/11 | **Verificar um clone limpo** e **arquivar o log** (ambiente limpo) | Assistente, com autorização | Etapa 5 |
| 7 | 15–17/11 | Ensaiar a apresentação **offline e online**; cronometrar | Equipe | Etapas 3 e 6 |
| 8 | até 18/11 | **Enviar pelo Portal** a partir de arquivos versionados (não zipar a pasta de trabalho), com folga de pelo menos um dia | Equipe | Etapas 5–6 |
| 9 | opcional | Disciplina 06 e prêmio (roteiro de vídeo ≤ 7 min, ABNT, GitHub, módulos) | Equipe | Decisão da etapa 1 |

---

## 11. Critérios para considerar a entrega pronta

**Disciplina 01 (mínimo):**
1. ☐ Atividade enviada pelo Portal **antes de 19/11/2026 às 23h55**, com comprovante de envio.
2. ☐ O que foi enviado vem de arquivos **versionados** (não da pasta de trabalho) e não inclui `.git`, `logs/`, `saida/`, `data/estado.db`, caches nem backups.
3. ☐ Declaração única de autoria e uso de IA, igual em todos os documentos.
4. ☐ Repositório com commit e, se for o canal escolhido, publicado, com a visibilidade decidida e M2, M3 e M4 resolvidos.
5. ☐ `python scripts/auditoria.py`: **Integridade OK**; `python -m pytest -q`: **21 passed**; `python main.py --reset`: `21 processados, 4 para revisao humana, 3 rejeitados, 1 duplicados`, **em um clone limpo**, com log arquivado.
6. ☐ Três temas apresentados pelos nomes do PDF, com função e evidência (roteiro atualizado).
7. ☐ Turma informada; dados dos integrantes confirmados.
8. ☐ Ressalvas técnicas visíveis (dados sintéticos; sem validação independente; sem prova de desempenho real; inapta para triagem clínica; falha grave de urgência; limiar 0,45 sem calibração; manifesto de 6 arquivos; Git/ambiente limpo conforme o estado real).
9. ☐ Nenhuma credencial, dado pessoal real ou caminho local sensível nos arquivos publicados.

**Disciplina 06** (somente se o grupo decidir cumpri-la): vídeo ≤ 7 min, documentação ABNT, GitHub publicado, integração de todos os módulos demonstrada.
**Prêmio** (opcional): vídeo pitch ≤ 7 min com solução integradora, enviado pelo Portal na disciplina indicada.

**Não são critérios de prontidão da disciplina 01:** a disciplina 06, o prêmio, a validação independente e a correção das falhas de urgência (estas continuam sendo limitações declaradas).
