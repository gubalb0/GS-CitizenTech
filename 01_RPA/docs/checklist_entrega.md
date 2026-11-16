# Checklist de entrega — Global Solution 2026.2 (CitizenTech RPA + IA)

Legenda: ✅ verificado (executado/conferido em 10/11/2026) · ⬜ a fazer · ⛔ pendência **do grupo** (não pode ser resolvida pelo código).

## 1. ⛔ Pendências que dependem do grupo (destacadas)
| Campo | Onde preencher | Situação |
|---|---|---|
| ✅ **Integrantes** (nome e RM; complemento: até 5; PDF oficial p. 11: trio, dupla ou individual) | `README.md:8` · capa/slides | **Preenchido no README** (3 integrantes: Henry Gimenez - 563217; Gustavo Balbo - 561711; Vinícius Araújo - 564504), conforme o README; **não foi verificado fora dele**. O grupo deve confirmar a exatidão e levar os nomes à capa/slides |
| ⛔ **Turma** | `README.md`, slides | **Não informada** |
| ⛔ **Nomes oficiais dos temas da disciplina** | `docs/temas.md`, `README.md` (tabela de temas), `docs/matriz_requisitos.md` | Os nomes atuais descrevem o que foi implementado (RPA de arquivos, NLP/ML, regras de negócio, API+resiliência); **não foram confrontados com o plano de ensino**. *[Rodada 5: o quadro agora também declara o SQLite; o PDF (p. 11) dá, como exemplos, os nomes "tratamento de arquivos e dados", "integração com APIs" e "banco de dados SQL", que os três temas atendidos usam; o plano de ensino segue indisponível.]* |
| ⛔ **Prazo/data de entrega e de apresentação** | PDF oficial, p. 10–11 | **Entrega até 19/11/2026 às 23h55**, pelo Portal do Aluno (Trabalhos), direto ao professor. **Envio não realizado.** A **data da apresentação não consta** no PDF; o grupo deve obtê-la. Ver a seção 6 |
| ⛔ **Confirmar o tema** | grupo | O problema (triagem de pedidos à UBS) foi proposto com auxílio do assistente de IA e escolhido entre opções; o grupo deve confirmar que quer defendê-lo |
| ⛔ **Declarar o uso de assistente de IA** | README / entrega, conforme regras da FIAP e da disciplina | O código, os dados sintéticos e os textos de teste foram produzidos com auxílio de um assistente de IA; o grupo deve verificar a regra de declaração e **entender e saber explicar** tudo (ver `docs/perguntas_banca.md`) |
| ⛔ **Forma de entrega e publicação** | grupo | O complemento aceita repositório Git, notebook Colab ou Jupyter; o PDF oficial define o **Portal do Aluno** como canal (p. 11) e exige o **GitHub** na disciplina 06 (p. 14). O Git local está **inicializado e sem commits**, sem remoto; **commit e publicação só com autorização do grupo** |

## 2. Auditoria final desta etapa (nenhum código, treino, modelo ou regra foi alterado)
| Verificação | Resultado |
|---|---|
| Testes automatizados (`python -m pytest -q`) | ✅ 21 passed |
| Integridade (`python scripts/auditoria.py`) | ✅ "Integridade OK: todos os hashes conferem com docs/modelo_congelado.json" |
| Modelo congelado intacto | ✅ SHA-256 de `data/modelo/classificador.joblib` = `c9a89d19…71a5c2` (igual ao manifesto) |
| Git sem commits | ✅ `main` sem commits (`git rev-parse HEAD` falha), 0 remotos |
| Demonstração ponta a ponta executada | ✅ `python main.py --reset` → `21 processados, 4 para revisao humana, 3 rejeitados, 1 duplicados` |
| Demonstração de falha executada (bash e PowerShell) | ✅ API de CEP fora do ar → mesmo resultado, `fonte_cep = indisponivel` |
| Idempotência executada | ✅ 2ª execução sem `--reset` → `0 processados, 22 duplicados` |

Nesta etapa só foram **criados** documentos em `docs/` e regenerados `saida/` e `logs/` (arquivos de execução, ignorados pelo Git) ao rodar a demonstração.

## 3. Evidências disponíveis
### 3.1 Arquivos que já existem
| Evidência | Arquivo | Observação |
|---|---|---|
| Saídas do robô (amostra pré-gerada) | `docs/exemplo_saida/` (`resultados.csv`, `revisao_humana.csv`, `rejeitados.csv`, `relatorio_execucao.json`) | Execução anterior; `saida/` é regenerada a cada `python main.py` e **não** é versionada |
| Logs | `logs/execucao.log` | Gerado na execução; **ignorado pelo Git**. Conteúdo atual = execuções da demonstração (normal, falha, idempotência) |
| Resultados da validação (gerado) | `docs/evidencias_resultados.md`, `.json` | `python scripts/validar.py` |
| Matriz de confusão e métricas por classe | `docs/auditoria_resultados.md`, `.json`; resumo em `docs/roteiro_apresentacao.md` (seção 10) | `python scripts/auditoria.py` |
| Auditoria, erros e riscos | `docs/auditoria_ia.md` | |
| Modelo congelado (hashes, parâmetros, vocabulário) | `docs/modelo_congelado.json` | |
| Matriz de requisitos do enunciado | `docs/matriz_requisitos.md` | |
| Demonstração de resiliência (cenário "API fora do ar") | `docs/evidencias_resultados.md` (seção 4) + comando ao vivo em `docs/roteiro_apresentacao.md` (seção 9) | |
| Ética, dados e ODS | `docs/etica_ods.md` | |
| Quadro de temas | `docs/temas.md` | Atualizado na rodada 5 (inclui o SQLite); nomes do plano de ensino a confirmar |
| Protocolo da validação independente | `validacao_independente/README.md` | **Estrutura apenas; não executada** |

### 3.2 Capturas de tela — ✅ **realizadas em 11/11/2026** (`docs/evidencias_visuais/`)
Todas as imagens são **capturas reais** de janelas de console onde os comandos foram **de fato executados** nesta etapa (nenhum resultado foi digitado, simulado ou editado; as imagens não têm nenhum retoque). Nenhum código, treino, modelo, dado ou regra foi alterado e **nenhum comando de treinamento foi executado**; após as capturas, `python scripts/auditoria.py` continua informando "Integridade OK".

| # | Captura | Arquivo | Comando exibido na imagem | O que mostra | Feito |
|---|---|---|---|---|---|
| 1 | Testes | [`01_testes_pytest_21_passed.png`](evidencias_visuais/01_testes_pytest_21_passed.png) | `python -m pytest -q` | `21 passed` | ✅ |
| 1b | Testes (painel de Terminal do app, interativo) — **extra** | [`01b_testes_pytest_painel_terminal_do_app.png`](evidencias_visuais/01b_testes_pytest_painel_terminal_do_app.png) | `python -m pytest -q` | `21 passed` (recorte só do painel; estreito, por isso as linhas quebram) | ✅ |
| 2 | Integridade | [`02_auditoria_integridade_ok.png`](evidencias_visuais/02_auditoria_integridade_ok.png) | `python scripts/auditoria.py` | `Integridade OK…` e os SHA-256 de treino, testes, modelo e regras | ✅ |
| 3 | Execução normal | [`03_execucao_normal_main_reset.png`](evidencias_visuais/03_execucao_normal_main_reset.png) | `python main.py --reset` | 2 arquivos ruins (corrompido e sem coluna), S015/S016/S017 rejeitados, S019 duplicado, `OK: 21 processados, 4 para revisao humana, 3 rejeitados, 1 duplicados` | ✅ |
| 4a | Resultados (tabela) | [`04a_resultados_csv_tabela.png`](evidencias_visuais/04a_resultados_csv_tabela.png) | `Import-Csv saida\resultados.csv … \| Format-Table` | categoria, confiança, prioridade, status, cidade e `fonte_cep` de cada registro (*visão tabular do arquivo real*) | ✅ |
| 4b | Resultados (mascaramento) — **extra** | [`04b_resultados_csv_mascaramento_pii.png`](evidencias_visuais/04b_resultados_csv_mascaramento_pii.png) | `Import-Csv … \| Where-Object … \| Format-List` | S001 encaminhado; S010 e S018 com `[EMAIL]`, `[CPF]`, `[TEL]` | ✅ |
| 5 | Revisão humana | [`05_revisao_humana_csv.png`](evidencias_visuais/05_revisao_humana_csv.png) | `Import-Csv saida\revisao_humana.csv … \| Format-List` | S008, S009, S014, S022: prioridade alta, prazo 1 h, resposta com aviso 192 | ✅ |
| 6 | Rejeitados e relatório | [`06_rejeitados_e_relatorio_execucao.png`](evidencias_visuais/06_rejeitados_e_relatorio_execucao.png) | `Get-Content saida\rejeitados.csv; Get-Content saida\relatorio_execucao.json -TotalCount 19` | motivos das rejeições e o `resumo` da execução (o JSON aparece cortado em 19 linhas, como indicado no comando) | ✅ |
| 7 | Falha tratada | [`07_falha_api_cep_retry_circuit_breaker.png`](evidencias_visuais/07_falha_api_cep_retry_circuit_breaker.png) | variáveis `CEP_*` + `python main.py --reset --saida saida\falha` | `tentativa 1/3 … 3/3 falhou (ConnectTimeout)` para 3 CEPs e nenhuma nova tentativa depois (circuit breaker); `falhas_http_cep: 9`, `cep_indisponivel: 20`; resultado final igual: `OK: 21 processados…` | ✅ |
| 8 | Matriz de confusão | [`08_matriz_confusao_combinada.png`](evidencias_visuais/08_matriz_confusao_combinada.png) | `Get-Content docs\auditoria_resultados.md … \| Select-Object -Skip 83 -First 16` | conjunto combinado (n=120): 85,8% de acurácia, 9 erros em 84 automáticos, urgências 14/15 | ✅ |
| 9 | Aptidão de uso | [`09_readme_aptidao_de_uso.png`](evidencias_visuais/09_readme_aptidao_de_uso.png) | `Get-Content README.md -TotalCount 4` | banner: "NÃO está apta para triagem clínica", trauma craniano, infarto, saúde mental | ✅ |
| 10 | Matriz de requisitos | [`10_matriz_de_requisitos.png`](evidencias_visuais/10_matriz_de_requisitos.png) | `Get-Content docs\matriz_requisitos.md -TotalCount 12` | início da matriz e primeiras linhas com status (texto bruto, não renderizado) | ✅ |
| 11 | Idempotência (extra) | [`11_idempotencia_segunda_execucao.png`](evidencias_visuais/11_idempotencia_segunda_execucao.png) | `python main.py` (sem `--reset`) | `OK: 0 processados, 0 para revisao humana, 3 rejeitados, 22 duplicados` | ✅ |

**Como foram feitas (para não haver dúvida sobre autenticidade).** Cada comando rodou em uma janela de console real (`conhost`, 160 colunas) aberta na hora; a janela foi capturada com a API do Windows `PrintWindow`, sem capturar a tela inteira (outros programas abertos não aparecem). A linha amarela com o comando é impressa pelo script de captura antes de executá-lo (equivale ao comando digitado); o restante é a saída real. A captura 1b é do painel de Terminal do próprio app, onde o comando foi digitado de fato.

**Sobre o título `EVID_xxxx` nas imagens (explicação da rodada 7).** `EVID_xxxx` (por exemplo, `EVID_f3670f1d`) é o **título da janela de console**, gerado pelo **procedimento de captura de evidências** para localizar cada janela; é um código aleatório que **muda a cada imagem**. Aparece em **12 das 13 imagens** (todas, exceto a `01b`, que é do painel de Terminal do app). **Não é um identificador produzido pelo CitizenTech**: não é gravado em nenhum arquivo de saída, log ou código do projeto. Os **identificadores reais do sistema** são o **`run_id`** (14 dígitos de data e hora, por exemplo `20261111075622`) e o **`protocolo`** (o `run_id` mais uma sequência, por exemplo `20261111075622-0002`). As imagens registram **execuções reais do protótipo**; a linha amarela do comando, como explicado acima, é impressa pelo script de captura. Esta explicação é coerente com o Plano B de `docs/roteiro_apresentacao.md`, que também trata o título como artefato do método de captura.

**Limitações das capturas (leia antes de usar nos slides):**
- Foram capturadas **só saídas de terminal e texto de arquivos**. Não há captura de interface gráfica do projeto (ele não tem uma) nem de documentos Markdown **renderizados**: as capturas 8, 9 e 10 mostram o texto bruto (tabelas Markdown em `|`).
- As capturas 4a, 4b e 5 mostram o **conteúdo real dos CSV em visão tabular** (`Import-Csv` + `Format-Table/Format-List`), não o CSV cru, porque as linhas do arquivo são largas demais para uma imagem legível.
- O console exibe os textos exatamente como estão nos arquivos; nomes de setor aparecem sem acento ("Classificacao de Risco") porque assim estão gravados.
- Os horários e o `run_id` nas imagens são de 11/11/2026 e mudam a cada execução; os totais (21 processados, 4 revisão humana, etc.) são estáveis.
- As capturas refletem o estado deste computador (Windows 11, Python 3.14.2) e não substituem a demonstração ao vivo.

**Ainda não existe (opcional, não exigido pelo checklist):** captura de documentos renderizados (Markdown) e de uma execução em outra máquina. Alternativa: abrir os `.md` em um visualizador e tirar a captura com a ferramenta de recorte do Windows (`Win + Shift + S`).

## 4. Checklist técnico da entrega
| Item | Status |
|---|---|
| Código executável com ponto de entrada único (`main.py`) | ✅ |
| `README.md` com problema, público, objetivo, arquitetura, instalação, execução, chaves, testes, resultados e limitações | ✅ (integrantes preenchidos; turma ainda não informada ⛔) |
| Quadro de temas (≥ 3) | ✅ 5 linhas no quadro (inclui o SQLite desde a rodada 5); **3 temas do PDF atendidos**; nomes do plano de ensino a confirmar ⛔ |
| Evidências: execução com dados de teste, resultado medido, ≥ 1 falha tratada | ✅ |
| Parágrafo de dados, ética e ODS | ✅ `docs/etica_ods.md` |
| Sem dados pessoais reais; sem chaves no repositório; `.env.example`; `.env` ignorado | ✅ (varredura de segredos sem ocorrências; `.env` inexistente) |
| Reprodutível em ambiente limpo (venv novo, apenas `requirements.txt`) | ⬜ **execução relatada, sem log preservado**: em 10/11/2026 foi relatada uma execução em cópia limpa com venv novo (Windows + Python 3.14.2), mas **não há log, captura ou script arquivado** que a comprove. As capturas `01` e `03` comprovam `pytest` e `main.py` na máquina de desenvolvimento, não em ambiente limpo. **Outras plataformas/versões não testadas** |
| Dados reservados da validação independente fora do Git | ✅ `validacao_independente/conjunto/` no `.gitignore` |
| Bytes preservados (hashes) no Git | ✅ `.gitattributes` com `* -text`; modelo versionado |
| Validação independente | ⬜ **pendente** (não exigida pelo enunciado; exigida pelo grupo para qualquer afirmação de validação) |
| Segurança clínica (trauma craniano, infarto, saúde mental) | ⛔ **não corrigida**; solução **inapta** para triagem clínica |

## 5. Pontos a não esquecer na apresentação
1. Dizer logo no início que os dados são sintéticos e que a solução **não** está apta para uso clínico.
2. Mostrar a falha do trauma craniano e as lacunas de infarto/saúde mental **antes** que a banca pergunte.
3. Chamar os testes pelo que são: escritos pela equipe, não independentes. Não dizer "validado"; dizer "avaliado em testes internos".
4. Não rodar `python main.py --treinar` nem `python scripts/gerar_treino.py` na apresentação (invalidam o congelamento).
5. Ter o Plano B pronto (`docs/exemplo_saida/`) caso a rede falhe.

## 6. Requisitos oficiais do PDF GS 2026.2 — conferência pela equipe (adicionada em 11/11/2026)
Fonte: `2TIAP(F-Y)-2026 - GS 2026.2.pdf` (17 páginas; **fora do repositório**; cada página tem 2 slides). Detalhe por requisito, com a página de origem e as evidências: `docs/matriz_requisitos.md`, seções F a J. As exigências abaixo estão **separadas por origem**, porque **não são uma única entrega**.

Legenda: ✅ **evidenciado no projeto** (há arquivo ou captura; não exige ação) · ⬜ **a fazer ou a conferir pela equipe** · ⛔ **depende de decisão ou ação da equipe**. **Nenhum item que dependa da equipe está marcado como concluído.**

### 6.1 Exigência da disciplina 01 — AI for Robotic Process Automation (PDF p. 11 e complemento)
| Item | Origem | Estado | Ação da equipe |
|---|---|---|---|
| Enviar a atividade pelo **Portal do Aluno** (Trabalhos), direto ao professor, **até 19/11/2026 às 23h55** | p. 11 (slide 21) | ⛔ **Não enviada** | Definir o que será enviado (link do repositório e/ou arquivos) e quem envia; **não deixar para a última hora** (alerta do próprio PDF) |
| Conferir no portal as **regras específicas da disciplina** ("verifique no portal ... ou diretamente com ele") | p. 11 (slide 22) | ⛔ **Não conferido** (sem acesso ao portal) | Verificar se há regras além do PDF e do complemento |
| **Pelo menos 3 temas**, cada um com função real no fluxo | p. 11 (slide 22) | ✅ **Atendido pelos exemplos do PDF: três temas distintos, cada um com função real e evidência** (reclassificado nas rodadas 4 e 5): **(1) tratamento de arquivos e dados** (`ingestao.py`, `validacao.py`, `texto.py`, `pipeline.py`), **(2) integração com APIs** (`geo.py`) e **(3) banco de dados SQL** (`estado.py`, `pipeline.py`). **Pandas é um exemplo citado no PDF, não uma exigência explícita.** **Ressalvas de profundidade mantidas:** (1) usa a biblioteca padrão, com transformações simples; (2) a API é **acessória** (não decide o roteamento); (3) o SQL tem **uso mínimo** (uma tabela). Evidências: `docs/matriz_requisitos.md`, seção G.2; capturas `03`–`07` e `11` | Opcional: confirmar com o professor que os três temas são aceitos (o plano de ensino não está disponível). Os temas próprios (NLP/ML, regras de negócio) são adicionais e **não são necessários** para o mínimo |
| Quadro de temas coerente com o que existe (declarar o SQL/SQLite; deixar claro o que **não** é usado: Pandas, web scraping, e-mail e RPA desktop) | p. 11 + complemento | ✅ `docs/temas.md` **declara o SQLite desde a rodada 5**, com os arquivos, as operações, as evidências e o uso mínimo. O que **não** é usado (Pandas, web scraping, e-mail automatizado, RPA desktop) está registrado na matriz (seção G.2), **não no quadro**. ⬜ Os nomes do plano de ensino continuam **não confrontados** | **Não apresentar tecnologia ausente como implementada**; confirmar os nomes oficiais do plano de ensino, se o grupo o obtiver |
| Funcionamento ponta a ponta | p. 11 (slide 22) | ✅ Capturas `03`–`06`; `docs/evidencias_resultados.md` | — |
| Resiliência | p. 11 (slide 22) | ✅ Capturas `03`, `07`, `11`; 21 testes | — |
| Evidências de validação com dados de teste | p. 11 (slide 22) | ✅ **Com ressalvas:** dados sintéticos, sem validação independente, sem prova de desempenho real | Não dizer "validado"; dizer "avaliado em testes internos" |
| Proteção de dados e ética | p. 11 (slide 22) | ✅ `docs/etica_ods.md` | — |
| Organização da entrega | p. 11 (slide 22) | ⬜ **Parcial:** Git sem commits; turma pendente; quadro de temas atualizado, com os nomes do plano de ensino ainda não confirmados | Ver a seção 1 deste checklist |
| Trio, dupla ou individual | p. 11 (slide 21) | ✅ 3 integrantes (`README.md:8`); ⛔ **confirmar a exatidão dos dados** | Conferir nomes e RM |
| **Declaração única de autoria e uso de IA** | regras da FIAP/disciplina (verificar) | ⛔ **Divergência mantida** (ver item da seção 1) | Decidir a redação conforme as regras da FIAP |

### 6.2 Exigência da disciplina integradora 06 — Governança em IA & Business Analytics (PDF p. 14)
Estas exigências **não são da disciplina 01** e **nenhuma está atendida**.
| Item | Origem | Estado | Ação da equipe |
|---|---|---|---|
| **Vídeo de até 7 minutos** | p. 14 (slide 27) | ⛔ **Não existe** (o `docs/roteiro_apresentacao.md` tem ~12,75 min e é para a banca) | Decidir se fará; exigiria um roteiro próprio e mais curto |
| **Documentação em formato ABNT** | p. 14 (slide 27) | ⛔ **Não existe** (os documentos são Markdown) | Decidir se fará |
| **GitHub do projeto** | p. 14 (slide 27) | ⛔ **Git sem commits e sem remoto** | Autorizar commit e publicação, se o grupo decidir |
| **Demonstrar a integração e o funcionamento de todos os módulos da GS** | p. 14 (slide 27) | ⛔ **Só o módulo da disciplina 01 existe neste repositório**; os das disciplinas 02–05 e 07–09 (p. 12–15) **não foram encontrados** (existência fora dele: não comprovada) | Informar o estado real dos demais módulos |
| Aplicar ao contexto de Governança em IA e Business Analytics | p. 14 (slide 27) | ⬜ **Parcial:** há material de governança (`docs/etica_ods.md`, `docs/auditoria_ia.md`, `docs/modelo_congelado.json`); **não há Business Analytics** | Decidir se adaptará |
| Entrega pelo Portal até 19/11/2026 às 23h55 | p. 11 (slide 21) | ⛔ **Não enviada** | — |

### 6.3 Exigência da GS integradora e do prêmio (PDF p. 5, 10 e 11) — o prêmio é opcional
| Item | Origem | Estado | Ação da equipe |
|---|---|---|---|
| **Vídeo pitch de até 7 minutos** com **solução integradora**, para concorrer ao prêmio | p. 11 (slide 21) | ⛔ **Não existe** | Decidir se o grupo concorre |
| Enviar o vídeo pelo Portal "**na disciplina indicada**" | p. 11 (slide 21) | ⛔ **O PDF não identifica qual é** | Perguntar ao professor ou ao portal; o PDF **não diz** se este vídeo é o mesmo da disciplina 06 |
| **Challenge Sprint** em 30/11/2026 | p. 10 (slide 19) | ⛔ **Não descrito no PDF**; fora deste mapeamento | Verificar no portal o que é e se se aplica |
| Calendário: 04 a 19/11 desenvolvimento; 23 a 27/11 resultado e vista de provas | p. 10 (slide 19) | ℹ️ Informativo | — |
| **Data da apresentação** | — | ⛔ **Não consta** no PDF | Obter com o professor |

### 6.4 Desafio geral CitizenTech (PDF p. 1–6) — pontos a conferir na documentação
O PDF pede que a proposta considere os pontos abaixo. Hoje a documentação **não os trata** ou só os menciona. **Documentar somente o que for verdadeiro; não inventar pesquisa, entrevistas ou resultados.**
| Ponto (origem) | Estado no projeto | Ação da equipe (opcional) |
|---|---|---|
| **Acessibilidade** (p. 4, p. 6) | ⛔ **Não tratada**; nenhum recurso implementado | Decidir se será documentada (ou declarada como limitação) |
| **Sustentabilidade** (p. 4) | ⛔ **Não tratada** (ODS escolhidos: 3, 10 e 16) | Idem |
| **Inclusão** (p. 4, p. 6) | ⬜ **Parcial:** só o público-alvo vulnerável; sem recurso implementado | Idem |
| **Viabilidade** (p. 6) | ⛔ **Não tratada** | Idem |
| **Escuta de quem convive com o problema** (p. 6) | ⛔ **Não comprovada**; nenhum levantamento registrado | Informar se houve; se não houve, declará-lo |
| **Quem participa do ecossistema** (p. 5–6) | ⬜ **Parcial:** só cidadãos e equipes das UBS | Idem |
| **Resultados e impacto esperados** (p. 6) | ⬜ **Parcial:** só resultados de teste sintético; impacto real **não medido** | Não afirmar impacto real |
| **Modelos de negócio** (p. 6, texto do case) | ⛔ **Não tratados** (não está claro se é exigência) | Perguntar ao professor |

### 6.5 Ressalvas que devem aparecer na apresentação e na entrega
Dados **sintéticos**; **sem validação independente**; métricas **sem prova de desempenho real**; **inapta para triagem clínica** (apoio administrativo, com revisão humana); **falha grave** (trauma craniano); limiar **0,45 sem calibração**; métricas históricas **não reproduzíveis**; manifesto SHA-256 protege **só seis arquivos** e `auditoria.py` **recria o manifesto se ele estiver ausente**; **Git sem commits e sem remoto**; ambiente limpo **relatado, sem log**.
