# Auditoria final de entrega — Global Solution 2026.2 (CitizenTech RPA + IA)

Data da auditoria: 11/11/2026. Tipo: **somente leitura e conferência**. Nenhum arquivo de implementação, dado, teste, modelo ou documento existente foi alterado; este é o único arquivo criado. Os problemas abaixo **não foram corrigidos** (primeiro o diagnóstico; a decisão de corrigir é do grupo).

> **Atualização de 11/11/2026 (rodada 3):** este documento passou a incorporar a análise do **PDF oficial da Global Solution 2026.2** (`2TIAP(F-Y)-2026 - GS 2026.2.pdf`, 17 páginas), que não estava disponível na auditoria original. As seções 1 a 7 preservam o diagnóstico original (a auditoria foi feita com o complemento de 2 páginas); onde o PDF ou as correções posteriores superam uma afirmação, há uma nota entre colchetes. **A análise do PDF está na seção 8 e o veredito atualizado, na seção 9.** Detalhes por requisito, com a página do PDF, em `docs/matriz_requisitos.md`. *[Rodada 7 (11/11/2026): registrados o escopo do manifesto (`docs/auditoria_ia.md`, seção 1), a explicação do título `EVID_xxxx` (checklist, seção 3.2), a situação do enunciado oficial (seção 8.1 e I-17) e a situação do modelo ilegível (I-16, ainda sem teste automatizado). As classificações dos requisitos não mudaram.]*

Classificação usada: **APROVADO** · **APROVADO COM RESSALVAS** · **PENDENTE** (depende de ação, geralmente do grupo) · **REPROVADO** (defeito que precisa ser corrigido antes da entrega).

---

## 1. Resumo executivo

**Veredito: a entrega NÃO está pronta. Estado: PENDENTE.** *[Atualizado em 11/11/2026 com o PDF oficial: continua NÃO PRONTA, e as exigências oficiais ampliam as pendências; ver seções 8 e 9.]*

- **O que está sólido:** a implementação, a integridade do modelo congelado e os testes estão íntegros e reproduzíveis; os números dos documentos batem com os resultados reais da auditoria; as limitações e a inaptidão para triagem clínica estão explícitas em vários documentos; as 10 capturas obrigatórias existem e são legíveis.
- **O que impede a entrega:** (1) o repositório Git não tem nenhum commit nem remoto, e o enunciado exige entrega por repositório Git, notebook Colab ou notebook Jupyter; (2) os nomes oficiais dos temas da disciplina não foram confirmados, e o critério "uso dos temas" vale 30% da nota; (3) a descrição da autoria dos dados e do código é contraditória entre os documentos (alguns dizem "escritos à mão/pela equipe", outros admitem auxílio de IA); (4) há defeitos de documentação corrigíveis, entre eles **um arquivo com caracteres de controle corrompidos** (`docs/checklist_entrega.md`) e **vários documentos que ainda dizem "integrantes em branco"** depois de o README ter sido preenchido.
- **[Atualização 11/11/2026 — PDF oficial]** O PDF separa três níveis de exigência. (a) **Desafio geral CitizenTech** (p. 1–6): atendido em parte; **acessibilidade, sustentabilidade, viabilidade e escuta de usuários não estão tratadas** nos documentos. (b) **Disciplina 01** (p. 11): ponta a ponta, resiliência, evidências, proteção de dados e ética atendidos; os **três temas** (tratamento de arquivos e dados, integração com APIs, banco de dados SQL) estão **atendidos** pela lista de exemplos do PDF, com ressalvas de profundidade *[reavaliado na rodada 4: antes "2 plenos, 1 parcial"; Pandas não é exigido]*; o quadro de temas declara o SQLite desde a rodada 5 (uso mínimo), com nomes **não confrontados com o plano de ensino** e **sem confirmação do professor**. (c) **Disciplina integradora 06** (p. 14) e **prêmio** (p. 11): **vídeo de até 7 min, documentação ABNT, GitHub e integração de todos os módulos não existem**. O prazo é **19/11/2026 às 23h55**, pelo Portal do Aluno, e nenhum envio foi feito.
- **Nenhum problema novo foi encontrado nos números nem no modelo.** Os problemas são de consistência entre documentos, evidências arquivadas e pendências do grupo.

| Área | Classificação |
|---|---|
| Integridade técnica (hashes, testes, manifesto) | **APROVADO** |
| Consistência numérica entre documentos e auditoria | **APROVADO COM RESSALVAS** |
| Limitações e inaptidão para triagem clínica explícitas | **APROVADO** |
| Diferenciação entre dados sintéticos e validação independente | **APROVADO** |
| Recursos futuros marcados como não implementados | **APROVADO** |
| Evidências visuais | **APROVADO COM RESSALVAS** |
| Cobertura dos requisitos da Global Solution | **PENDENTE** *[atualizado 11/11/2026: antes "aprovado com ressalvas", com base só no complemento. Com o PDF oficial: 18 atendidos, 11 parciais, 10 não atendidos e 3 não comprovados, de 42 requisitos avaliáveis (mais 1 N/A, F25); reclassificação da rodada 4, antes 17/12/11/3 de 43; ver seção 8]* |
| Roteiro de apresentação | **APROVADO COM RESSALVAS** |
| Perguntas da banca | **APROVADO COM RESSALVAS** |
| Qualidade/consistência da documentação | **REPROVADO** em 1 item (checklist corrompido); demais com ressalvas |
| Entrega por Git | **PENDENTE** |
| Pendências do grupo | **PENDENTE** |

---

## 2. Resultado de cada verificação

### 2.1 Integridade técnica — APROVADO
| Verificação | Resultado |
|---|---|
| Hash do modelo congelado | `data/modelo/classificador.joblib` = `c9a89d199558beee523093f46d9297d2ad8bc4a17ad407284a5bbc873e71a5c2`, **igual** ao manifesto |
| Arquivos protegidos | treino, teste 1, teste 2, modelo, `classificador.py` e `regras.py`: **6 de 6 idênticos** ao manifesto (conferido por leitura direta, sem executar `auditoria.py` para não reescrever os arquivos derivados) |
| Testes automatizados | `python -m pytest -q` → **21 passed** |
| Manifesto × implementação | Classes, `C=10`, `max_iter=1000`, TF-IDF de palavras (1–2, 1.651 termos) e de caracteres (`char_wb` 3–5, 3.998 termos), 20 termos de urgência, SLA (1 h/72 h), limiar 0,45: **idênticos** ao que o código carrega |
| Alterações inesperadas | Nenhuma nos arquivos protegidos. Alterados desde a fase anterior (todos documentos/derivados): `README.md` (preenchimento dos integrantes e a linha das capturas), `docs/checklist_entrega.md`, `docs/evidencias_visuais/*`, `docs/auditoria_resultados.*` (regenerados, conteúdo estável) |
| Segredos e dados pessoais | Varredura de padrões de chave/senha/token: **nenhuma ocorrência**; `.env` não existe; CPF/e-mail/telefone nos dados são **fictícios** (S010 e S018, mascarados na saída) |
| Estado do Git | Branch `main`, **0 commits**, **0 remotos**, 71 arquivos versionáveis, 13 entradas não rastreadas; ignorados: `.pytest_cache`, `__pycache__`, `data/estado.db`, `logs/`, `saida/`; `.env` e `validacao_independente/conjunto/` cobertos pelo `.gitignore` |

Ressalvas técnicas menores (não bloqueiam): ver I-13 e I-16.

### 2.2 Consistência das informações
| Pergunta | Resultado |
|---|---|
| Os números dos documentos correspondem aos da auditoria? | **Sim.** Conferidos contra `docs/auditoria_resultados.json` e `docs/evidencias_resultados.json`: 87,5% (70/80), 82,5% (33/40), 85,8% combinado; erros entre automáticos 6/57, 3/27, 9/84 (10,7%); revisão humana 23/13/36 (28 já corretos); urgências 10/10, 4/5, 14/15; falso alarme 1/70, 2/35, 3/105; baseline 58,8%, 50,0%, 55,8% combinado; F1 por classe e faixas de confiança. IC95% de Wilson de 9/84: calculado 5,7–19,1%, o documento diz ≈ 5,7–19% ✓ |
| As métricas estão descritas corretamente? | **Com ressalvas:** coexistem **duas definições de "automático"** (por confiança ≥ 0,45 e por status `encaminhado`) e dois cenários de falha de API com contagens diferentes (6 e 9 falhas) sem explicação. Ver I-06 e I-07 |
| Limitações do classificador explícitas? | **Sim** (README, auditoria, evidências, roteiro, perguntas): treino sintético, testes não independentes, contaminação parcial, erro de alta confiança, limiar não calibrado, sem "fora do escopo", sem categoria de saúde mental |
| Sintético × validação independente? | **Sim, bem diferenciados.** README, `auditoria_ia.md` e `validacao_independente/README.md` dizem que a validação independente **não foi executada** e que nenhum resultado independente existe |
| Deixa claro que não está apta para triagem clínica autônoma? | **Sim**: banner no topo de README e `auditoria_ia.md`, `evidencias.md`, `etica_ods.md`, matriz (seção E), roteiro (seção 11) e perguntas (18) |
| Futuro marcado como não implementado? | **Sim**: perguntas (20) usa `[NÃO IMPLEMENTADO]`; README e auditoria tratam as recomendações como recomendações; `validacao_independente/` descrita como estrutura apenas |

### 2.3 Evidências visuais (`docs/evidencias_visuais/`)
| Verificação | Resultado |
|---|---|
| Todas as obrigatórias existem? | **Sim.** As 10 do checklist (1–10) estão presentes, mais 3 outras: `01b`, `04b` e `11` (total de 13 arquivos) |
| Nomes correspondem ao conteúdo? | **Sim.** Cada imagem foi aberta e conferida |
| Duplicadas/desnecessárias? | Nenhuma duplicata binária (SHA-256 distintos). Redundância de conteúdo: `01b` repete o `pytest` de `01` em painel estreito (opcional); `03` e `11` têm logs parecidos (cenários diferentes) |
| Legíveis? | **Sim**, todas (texto monoespaçado em 1458 px de largura; `01b` mais estreita) |
| Inconsistências entre capturas e documentos? | **Sim, uma:** a captura `07` mostra `falhas_http_cep: 9`, enquanto `evidencias.md` e `evidencias_resultados.md` dizem 6 (ver I-06) |
| Extras identificados como extras? | **Parcialmente.** Só a `11` é marcada "(extra)" no checklist; `01b` e `04b` não são marcadas (ver I-14) |
| Observação | As capturas exibem o título de janela `EVID_xxxxxxxx` (artefato do método de captura) e o caminho com o nome de usuário do Windows. O método e as limitações estão descritos no checklist; o título `EVID_…` não |

### 2.4 Requisitos da Global Solution (complemento de 2 páginas; histórico — o PDF oficial é analisado na seção 8)
Cada requisito × evidência verificada nesta auditoria:

| Requisito do enunciado | Evidência conferida | Classificação |
|---|---|---|
| Robô que automatiza uma tarefa de ponta a ponta | `main.py` + capturas 03, 04a, 05, 06; `evidencias_resultados.md` (esperado = obtido) | **APROVADO** |
| IA onde agrega | Classificador com baseline comparável; captura 08; `auditoria_ia.md` | **APROVADO COM RESSALVAS** (qualidade e segurança limitadas, declaradas) |
| ≥ 3 temas com função real e justificativa de escolha | `docs/temas.md` (5 linhas: as 4 técnicas originais e o SQLite, acrescentado na rodada 5; código executado). **Nomes oficiais não confirmados** *[PDF p. 11 e inspeção da implementação (rodada 4): 3 temas da lista do PDF com função real (tratamento de arquivos e dados; integração com APIs; banco de dados SQL); Pandas não é exigido; ver 8.3]* | **APROVADO COM RESSALVAS** (implementação com 3 temas; o quadro de temas declara o SQLite desde a rodada 5, com uso mínimo; nomes do plano de ensino **não confrontados** e **sem confirmação do professor**) |
| LLM opcional | Não usado | **APROVADO** (N/A) |
| Falhas tratadas com log e caminho seguro, sem interromper | Capturas 03, 07, 11; 21 testes | **APROVADO** |
| Ferramentas gratuitas; dados sintéticos/públicos; sem PII real | Varredura e dados conferidos | **APROVADO** |
| Chaves fora do código e do repositório | Varredura sem ocorrências; `.env.example`; `.gitignore` | **APROVADO** |
| Ponto de entrada claro e README que permite rodar | `main.py`; README. Reprodução em cópia limpa foi feita em fase anterior, **mas não há log/captura arquivado** dessa verificação | **APROVADO COM RESSALVAS** (ver I-11b) |
| Grupo de até 5 integrantes | README:8 lista 3 integrantes com RM *[o PDF oficial, p. 11, diz "trio, dupla ou individualmente": 3 integrantes atendem às duas redações]* | **APROVADO** |
| Entregável: repositório Git, notebook Colab ou Jupyter | Git sem commits e sem remoto; a matriz de requisitos **não tem linha** para este requisito | **PENDENTE** (ver I-09) |
| Entregável: quadro de temas | `docs/temas.md` | **APROVADO COM RESSALVAS** *[atualizado na rodada 6: antes **PENDENTE** (nomes). O quadro declara o SQLite desde a rodada 5, com arquivos, operações, evidências e uso mínimo. Ressalva mantida: os nomes **não foram confrontados com o plano de ensino**]* |
| Entregável: evidências (execução, resultado medido em amostra, ≥ 1 falha tratada) | Seções do `evidencias*.md`, capturas | **APROVADO COM RESSALVAS** |
| Entregável: parágrafo de dados, ética e ODS | `docs/etica_ods.md` (longo, mas coerente) | **APROVADO** |
| Prazo conforme o calendário | Não informado *[atualizado 11/11/2026: o PDF oficial, p. 11, informa entrega até **19/11/2026 às 23h55**, pelo Portal do Aluno; nenhum envio comprovado]* | **PENDENTE** (grupo) |

Barema (peso): temas 30% → **PENDENTE** (nomes) · ponta a ponta/reprodutibilidade 25% → **APROVADO COM RESSALVAS** · resiliência e segurança 20% → **APROVADO COM RESSALVAS** (robô sólido; segurança clínica da classificação inadequada, declarada) · evidências 15% → **APROVADO COM RESSALVAS** · dados/ética/ODS/organização 10% → **APROVADO COM RESSALVAS** (defeitos de organização dos documentos).

**A matriz de requisitos é coerente com o que foi implementado?** Sim, nos requisitos que ela lista, mas está **desatualizada** em dois pontos (integrantes; falta a linha de entrega via Git) e não cita as capturas de tela como evidência. *[Resolvido em 11/11/2026: a matriz foi corrigida e depois reescrita com o PDF oficial; ver `docs/matriz_requisitos.md`.]*

**Afirmações do README que não podem ser comprovadas pelo código ou por evidência arquivada:**
- "testado ... inclusive em ambiente virtual novo" e "Em ambiente novo foi verificado que `numpy 2.5.4` também funciona" (README:36 e :54): verdade na sessão, mas **sem log, captura ou script arquivado** no repositório.
- "Versão anterior do modelo: 73,8% e 67,5%" (README:99) e "só palavras → 64/80 e 29/40" (perguntas Q3; `evidencias.md:38`): os resultados vieram de scripts temporários que **não foram versionados**; o repositório não permite reproduzi-los.
- Todas as demais afirmações numéricas e de comportamento foram conferidas.

### 2.5 Apresentação
| Verificação | Resultado |
|---|---|
| Roteiro em sequência lógica? | **Sim.** As 12 etapas pedidas, nessa ordem, com ~12,75 min somados (o texto diz "~12 min"). Conferir o tempo real disponível com a banca |
| Demonstração executável só com as instruções documentadas? | **Sim, na máquina testada** (Windows, PowerShell, Python 3.14.2): os comandos do roteiro foram executados e geraram as saídas citadas (capturas 03, 07, 11). **Não testado** em macOS/Linux (só a falha tem equivalente em bash) nem em outras versões de Python |
| Perguntas da banca sustentadas pela implementação? | **Sim.** As respostas foram conferidas contra o código (timeout 4 s, 3 tentativas, circuit breaker após 3 falhas, 20 termos, 72 h/1 h, fallback com confiança ≤ 0,4). Exceção: Q3 depende dos números não reprodutíveis (I-11) |
| Pontos que a equipe provavelmente não saberá explicar | Ver seção 5 |

---

## 3. Inconsistências encontradas (arquivo e localização)

Gravidade: **Alta** = precisa ser corrigida antes da entrega · **Média** = confunde a banca ou o leitor · **Baixa** = cosmético/rastreabilidade. *[Esta tabela é o registro da auditoria original. A **situação atual** de cada item, após as rodadas de correção documental, está na seção 8.5.]*

| ID | Gravidade | Arquivo e localização | Problema | Classificação | Recomendação |
|---|---|---|---|---|---|
| I-01 | **Alta** | `docs/checklist_entrega.md` linhas 54, 56, 57, 58, 59 | Os comandos aparecem **corrompidos** (`saidaesultados.csv`, `saidaevisao_humana.csv`, `saidaejeitados.csv`, `saidaalha`, `docsuditoria_resultados.md`) e há **caracteres de controle** (CR solto nas linhas 54, 56, 57; FF na 58; BEL na 59): as sequências `\r`, `\f`, `\a` do caminho do Windows viraram caracteres de controle ao gerar o arquivo. Pode quebrar a renderização da tabela | **REPROVADO** | Reescrever as 5 linhas com as barras invertidas corretas (ex.: `saida\resultados.csv`) |
| I-02 | **Alta** | `docs/checklist_entrega.md:8` ("Integrantes … **Em branco**") e `:79`; `docs/matriz_requisitos.md:16` ("**não informados**", status Pendente) e `:23` ("integrantes em branco", Parcial); `docs/roteiro_apresentacao.md:3`; `docs/perguntas_banca.md:4`; `docs/diagnostico.md:9` | O README foi preenchido (`README.md:8`: Henry Gimenez – 563217; Gustavo Balbo – 561711; Vinícius Araújo – 564504), mas 5 documentos ainda dizem que está em branco | **REPROVADO** (desatualizado) | Atualizar os documentos; a matriz e o checklist passam a "Atendido". **Turma** continua pendente |
| I-03 | **Alta** (integridade acadêmica) | Autoria: `README.md:4,89,105`, `docs/evidencias.md:16-17` ("escritos à mão"), `docs/auditoria_ia.md:4,61`, `docs/roteiro_apresentacao.md:75,102` **×** `docs/checklist_entrega.md:13` e `docs/perguntas_banca.md:23` | Os documentos descrevem os testes e o treino como "escritos à mão/pela própria equipe", enquanto o checklist e a Q5 informam que foram produzidos **com auxílio de assistente de IA**. O README não traz nenhuma declaração de uso de IA | **PENDENTE** (decisão do grupo) | O grupo deve conferir a regra de declaração da FIAP/disciplina e decidir uma redação **única** em todos os documentos. Esta auditoria não altera a autoria declarada |
| I-04 | Média | `README.md:29` | Texto "`saida/o*.csv`" no diagrama (deveria ser `saida/*.csv`) | **APROVADO COM RESSALVAS** | Corrigir o texto |
| I-05 | Média | `README.md:82` | Diz "(11 imagens)"; a pasta tem **13** arquivos (10 itens obrigatórios + `01b`, `04b`, `11`) | **APROVADO COM RESSALVAS** | Ajustar para 13, ou "11 capturas + 2 variantes" |
| I-06 | Média | `docs/evidencias.md:28`, `docs/evidencias_resultados.md:72-74` **×** captura `07`, `docs/roteiro_apresentacao.md:71`, `docs/perguntas_banca.md` Q10 | Os documentos dizem **6** falhas HTTP no cenário de API fora do ar; a captura 07 mostra **9** (`falhas_http_cep: 9`). Causa: `scripts/validar.py` usa 2 tentativas; a demonstração ao vivo usa o padrão (3). Nada no texto explica a diferença | **APROVADO COM RESSALVAS** | Explicar nos dois documentos que são dois cenários (2 e 3 tentativas), ou citar só um |
| I-07 | Média | `docs/evidencias.md:36-37,49`; `docs/evidencias_resultados.md:7,29` **×** `README.md:91-96`, `docs/auditoria_ia.md:21-28` | Duas definições de "encaminhado automaticamente": por **confiança ≥ 0,45** (67/80, 89,6%; "7 erros passaram", "13/80 a humano") e por **status** do robô (57; 6/57; 23 a humano). O banner de `evidencias.md:3` corrige só em parte, e a tabela e a análise mantêm a definição antiga | **APROVADO COM RESSALVAS** | Deixar a tabela de `evidencias.md` e os cabeçalhos de `evidencias_resultados.md` explícitos sobre qual definição usam |
| I-08 | Média | `docs/auditoria_ia.md:30` **×** `:18` (item b) e `scripts/validar.py` atual | A linha 30 diz que o `validar.py` "continua mostrando a métrica de urgência apenas do teste 1"; a linha 18 e o script/`evidencias_resultados.md:32-44` mostram teste 1, teste 2 e combinado | **APROVADO COM RESSALVAS** | Remover ou corrigir a frase da linha 30 |
| I-09 | Média | `docs/matriz_requisitos.md` (seção A/B) | Falta a linha do requisito do enunciado **"Entrega por repositório Git, notebook Colab ou Jupyter"** (status real: Pendente, 0 commits). A matriz também não cita as capturas de tela (11/11) como evidência | **PENDENTE** | Incluir a linha com status Pendente e referenciar `docs/evidencias_visuais/` |
| I-10 | Baixa | `docs/auditoria_ia.md:16` | "`modelo_congelado.json` foi criado **uma única vez**": na prática foi criado em `docs/congelamento/`, removido e recriado em `docs/` (hashes iguais). Também `:7` ("nenhuma configuração foi escolhida consultando resultados", válido só para aquela etapa) parece contradizer `:58`; `:10` traz `vocabulário incluído no próprio manifesto` formatado como código e omite `joblib` na lista de versões | **APROVADO COM RESSALVAS** | Reescrever as três frases para refletir o histórico |
| I-11 | Média | `docs/perguntas_banca.md` Q3; `docs/evidencias.md:38`; `README.md:99` | Números "só palavras: 64/80 e 29/40" e "versão anterior: 73,8% e 67,5%" não são reproduzíveis a partir do repositório (scripts temporários não versionados; o modelo de 360 textos não foi preservado) | **APROVADO COM RESSALVAS** | Indicar nesses trechos que são resultados históricos não reproduzíveis, ou omiti-los |
| I-11b | Média | `README.md:36,54`, `docs/matriz_requisitos.md:15,32,40`, `docs/checklist_entrega.md:84` | "Verificado em cópia limpa/venv novo" não tem log nem captura arquivados | **APROVADO COM RESSALVAS** | Repetir e arquivar a evidência (log ou captura) antes da entrega |
| I-12 | Baixa | `docs/diagnostico.md` (documento histórico da Fase 1) | Contém "integrantes não informados" e descreve decisões iniciais; está fora da lista de documentos e não indica que é histórico | **APROVADO COM RESSALVAS** | Marcar como histórico ou atualizar |
| I-13 | Baixa | `docs/modelo_congelado.json` (`sha256`) | O manifesto protege 6 arquivos. Os módulos que também afetam o comportamento (`texto.py`, que normaliza o texto de entrada do modelo; `pipeline.py`; `config.py`; `geo.py`; `ingestao.py`; `estado.py`; `validacao.py`; `main.py`) **não** são conferidos: uma alteração neles não seria detectada. `main.py` mudou depois da criação do manifesto (documentado em `auditoria_ia.md:18`) | **APROVADO COM RESSALVAS** | Registrar a limitação do escopo do congelamento; uma ampliação exigiria novo congelamento (decisão do grupo) |
| I-14 | Baixa | `docs/checklist_entrega.md:51,55,62` | Apenas a captura 11 é marcada como "(extra)". `01b` e `04b` não são identificadas como extras. O título de janela `EVID_xxxxxxxx` visível nas capturas não é explicado | **APROVADO COM RESSALVAS** | Marcar `01b` e `04b` como extras e acrescentar uma nota sobre o título |
| I-15 | Baixa | `docs/roteiro_apresentacao.md` ("Plano B") | O Plano B cita `docs/exemplo_saida/` e `evidencias_resultados.md`, mas não as capturas de `docs/evidencias_visuais/`, que são o melhor apoio se a demonstração falhar | **APROVADO COM RESSALVAS** | Incluir as capturas no Plano B |
| I-16 | Baixa | `main.py` (`_modelo_congelado`) | O caminho de segurança "modelo salvo ilegível → re-treina só em memória" não tem teste automatizado (os 21 testes não o cobrem) | **APROVADO COM RESSALVAS** | Registrar como limitação ou testar numa etapa futura |
| I-17 | Baixa | `docs/enunciado/p1.png`, `p2.png` | Material oficial da FIAP será versionado (e publicado, se o repositório for público) | **APROVADO COM RESSALVAS** | Decidir se mantém no repositório |

---

## 4. Evidências ausentes ou insuficientes

| Item | Situação |
|---|---|
| Capturas obrigatórias (10) | **Todas presentes** |
| Verificação em ambiente limpo (venv novo, `requirements.txt`) | **Insuficiente:** citada em 5 lugares, mas sem log/captura arquivado (I-11b) |
| Reprodutibilidade dos números "só palavras" e "versão anterior" | **Ausente:** não há script versionado (I-11) |
| Validação independente | **Ausente por decisão:** estrutura pronta, nenhum conjunto coletado, nenhum resultado; qualquer menção a "validado" além de "avaliado em testes internos" seria indevida |
| Revisão por profissional de saúde das categorias e dos termos de urgência | **Ausente** |
| Ganho de tempo do robô em relação à triagem manual | **Nunca medido** (o benefício social descrito é potencial) |
| Documentos Markdown **renderizados** (capturas 8, 9, 10 são texto bruto) | Opcional; declarado no checklist |
| Execução em outra máquina/plataforma | Ausente; declarado |
| Declaração de uso de assistente de IA na entrega | **Ausente** no README/entrega (ver I-03) |
| Entrega publicada (commit/remoto, ou notebook) | **Ausente** |
| *[PDF oficial, 11/11/2026]* Vídeo de até 7 minutos (disciplina 06) e vídeo pitch (prêmio) | **Ausentes**: não existe nenhum vídeo (o roteiro de ~12,75 min não é um vídeo e excede 7 min) |
| *[PDF oficial]* Documentação em formato ABNT (disciplina 06) | **Ausente**: os documentos são Markdown |
| *[PDF oficial]* GitHub do projeto (disciplina 06) | **Ausente**: Git sem commits e sem remoto |
| *[PDF oficial]* Módulos das demais disciplinas e sua integração (disciplina 06) | **Não encontrados** neste repositório; existência fora dele **não comprovada** |
| *[PDF oficial]* Tratamento de acessibilidade, sustentabilidade, viabilidade e escuta de usuários (desafio geral) | **Ausente** na documentação e na implementação (acessibilidade e sustentabilidade: 0 ocorrências no código e em README, `etica_ods.md` e `temas.md`). *[Modelo de negócio: **não exigido explicitamente**; ver F25 na matriz]* |
| *[PDF oficial]* Envio pelo Portal do Aluno até 19/11/2026 às 23h55 | **Não comprovado** (nenhum envio) |

---

## 5. Riscos para a apresentação

| Risco | Probabilidade/impacto | Mitigação |
|---|---|---|
| **Banca pergunta quem escreveu o código/dados** e a resposta do grupo contradiz os documentos (I-03) | Alta / alto | Alinhar a declaração antes; ensaiar a resposta |
| **Grupo não consegue explicar a implementação** (o código foi produzido com auxílio de IA) | Alta / alto | Ler `perguntas_banca.md` e abrir o código de cada módulo; tópicos de maior risco: (1) TF-IDF de palavras × `char_wb` 3–5 e por que ajuda com erros de digitação; (2) por que a Regressão Logística e o que significa `C=10`; (3) probabilidade × confiança e por que não é calibrada; (4) idempotência por hash do texto normalizado + CEP; (5) retry com espera exponencial e circuit breaker; (6) por que S014 virou "urgente"; (7) congelamento por SHA-256 e IC de Wilson; (8) limites do mascaramento por regex |
| **Perguntas não cobertas** por `perguntas_banca.md` | Média / médio | Preparar respostas a: "por que o limiar 0,45?" (não foi justificado, é um valor inicial sem calibração); "como as 8 categorias foram definidas e por quem?" (pelo desenvolvimento, sem validação de profissional); "qual o ganho de tempo?" (não medido); "por que não usar dados reais?" |
| Demonstração depende de **internet** (ViaCEP) | Média / baixo | Sem rede o fluxo continua (cidades vazias, 3 tentativas + timeout alongam a execução); tenha as capturas e `docs/exemplo_saida/` à mão (I-15) |
| **Máquina da apresentação diferente** (outra versão de Python, macOS/Linux, sem venv) | Média / médio | Testar antes; só uma configuração foi testada. Comandos PowerShell do roteiro não funcionam em bash (há equivalente só para a falha) |
| Terminal estreito quebra os logs ilegíveis | Média / baixo | Maximizar o terminal; usar as capturas como apoio |
| **Tempo:** o roteiro soma ~12,75 min | Desconhecida | Confirmar o tempo disponível; cortar a idempotência e a etapa 12 se necessário |
| Rodar `--treinar` ou `gerar_treino.py` ao vivo | Baixa / alto | Já alertado no roteiro e no checklist: invalida o congelamento |
| Confusão entre números por definições diferentes (I-06, I-07) | Média / médio | Corrigir os documentos ou padronizar a fala: "automático = encaminhado sem humano, 6/57 e 3/27" |
| Falha da banca em ver o pior caso como falha de rigor | Baixa | A transparência (trauma craniano, infarto, saúde mental) é um ponto forte se apresentada **antes** da pergunta |
| *[PDF oficial]* **Prazo de 19/11/2026 às 23h55** com envio pelo Portal ainda não feito; restam 8 dias a partir de 11/11/2026 | Alta / alto | Definir quem envia e o que será enviado (repositório, link, arquivos) com antecedência; não deixar para a última hora, como o próprio PDF alerta |
| *[PDF oficial]* **Disciplina 06 e prêmio sem entrega**: vídeo, ABNT, GitHub e módulos integrados inexistentes | Alta / alto | Decidir se o grupo fará a disciplina 06 e o prêmio; se sim, o trabalho restante é grande e **está fora do escopo do repositório atual** |
| *[PDF oficial; reavaliado na rodada 4]* **Temas:** e-mail, scraping e RPA desktop ausentes (Pandas não é exigido), mas **3 temas da lista do PDF atendidos** (arquivos e dados, APIs, SQL). Pontos contestáveis: API **acessória**, SQL de **uso mínimo**, transformações de dados simples; o quadro de temas **declara o SQLite desde a rodada 5**, mas com nomes **não confrontados com o plano de ensino** | Baixa a média / médio (30% da nota no complemento) | O SQL já está declarado no quadro (rodada 5); mostrar a função de cada tema com as evidências; confirmar os nomes do plano de ensino, se o grupo o obtiver; **não** apresentar tecnologia ausente como implementada |
| *[PDF oficial]* **Desafio geral**: acessibilidade, sustentabilidade, viabilidade e escuta de usuários não documentadas | Média / médio | Decidir se serão documentadas (somente o que for verdadeiro); a banca pode perguntar |
| *[PDF oficial]* **Duração**: o roteiro (~12,75 min) excede o vídeo de 7 min exigido pela disciplina 06 e pelo pitch | Média / médio | Um vídeo exigiria roteiro próprio e mais curto; o roteiro atual serve à banca, não ao vídeo |

---

## 6. Pendências que dependem dos integrantes do grupo

| # | Pendência | Observação |
|---|---|---|
| G-1 | **Nomes oficiais dos temas da disciplina** | Bloqueia o critério de 30%; confrontar `docs/temas.md` com o plano de ensino e ajustar README, temas e matriz |
| G-2 | **Turma** | Não consta em nenhum documento |
| G-3 | **Prazo/data de entrega e de apresentação** | Não informado *[atualizado: entrega até **19/11/2026 às 23h55**, PDF p. 11; a data da apresentação **não consta** no PDF]* |
| G-4 | **Forma de entrega e publicação** (Git com commit e remoto, ou notebook) | O Git está inicializado e vazio; **commit e publicação só com autorização do grupo** |
| G-5 | **Declaração de uso de assistente de IA** e redação única da autoria dos dados/testes | I-03 |
| G-6 | **Confirmar o tema** (triagem de pedidos à UBS) como o problema do grupo | Proposto com auxílio do assistente e escolhido entre opções |
| G-7 | **Decidir sobre a validação independente** | Opcional para o enunciado; sem ela, nada pode ser chamado de "validado" |
| G-8 | **Revisão por profissional de saúde** das categorias e termos de urgência | Necessária para qualquer uso além do acadêmico |
| G-9 | **Corrigir as inconsistências I-01 a I-17** que o grupo decidir tratar | Esta auditoria não corrigiu nenhuma |
| G-10 | **Arquivar a evidência de ambiente limpo** (I-11b) e **ensaiar** a apresentação | |
| G-11 | *[PDF oficial]* **Enviar a entrega da disciplina 01 pelo Portal do Aluno** até 19/11/2026 às 23h55 | Depende da equipe; nenhum envio comprovado |
| G-12 | *[PDF oficial; reavaliado na rodada 4]* **Opcional:** confirmar com o professor da disciplina 01 que os 3 temas implementados (arquivos e dados, APIs, SQL) são aceitos, e confrontar os nomes do quadro de temas com o plano de ensino, se o obtiverem | O quadro de temas **já declara o SQLite desde a rodada 5**. O PDF dá exemplos ("como") e **não exige Pandas**; o plano de ensino não está disponível; **nenhuma confirmação do professor foi obtida** |
| G-13 | *[PDF oficial]* **Decidir sobre a disciplina integradora 06**: vídeo ≤ 7 min, documentação ABNT, GitHub, módulos integrados | Nada disso existe; exige decisão e trabalho da equipe |
| G-14 | *[PDF oficial]* **Decidir sobre o prêmio**: vídeo pitch ≤ 7 min com solução integradora, enviado "na disciplina indicada" | Opcional; o PDF não identifica a disciplina |
| G-15 | *[PDF oficial]* **Decidir se documentam** acessibilidade, sustentabilidade, viabilidade, escuta de usuários e ecossistema | Só o que for verdadeiro; nenhum desses pontos está tratado hoje |

---

## 7. Veredito final (auditoria original; **superado pelo veredito atualizado da seção 9**)

**NÃO DECLARO A ENTREGA PRONTA.**

1. **Tecnicamente:** **APROVADO.** Modelo, dados, testes e manifesto íntegros; 21 testes passando; sem segredos; números dos documentos conferem com a auditoria; limitações e inaptidão para triagem clínica explícitas.
2. **Documentação e evidências:** **APROVADO COM RESSALVAS**, com **um item REPROVADO** (`docs/checklist_entrega.md` corrompido, I-01) e outro desatualizado (integrantes, I-02). Nenhum exige mudança de código.
3. **Entrega:** **PENDENTE.** Sem commit/remoto (ou notebook), sem confirmação dos temas, sem turma/prazo e com a questão da declaração de autoria em aberto.

**Para considerar a entrega pronta** (ordem sugerida): (1) G-5/I-03, redação única de autoria; (2) G-1, nomes dos temas; (3) I-01 e I-02, correções de documentação; (4) G-4, decisão e execução da entrega via Git com autorização; (5) I-04 a I-09, ajustes menores de consistência; (6) G-10, arquivar evidência de ambiente limpo e ensaiar.

**Resumo para a banca, se nada mais mudar:** protótipo funcional e bem documentado, honesto sobre seus limites, **inapto para triagem clínica**, avaliado apenas em testes internos sintéticos, sem validação independente.

---

## 8. Análise do enunciado oficial (PDF GS 2026.2) — adicionada em 11/11/2026

### 8.1 Fontes e método
- **PDF oficial:** `2TIAP(F-Y)-2026 - GS 2026.2.pdf`, 17 páginas de slides (2 por página), 04/11/2026, 2.021.801 bytes (SHA-256 `b9af6e4e…c215`). **Foi consultado na revisão documental; a cópia utilizada está fora do repositório, em `Downloads`, e o arquivo não está versionado junto ao projeto** (o repositório tem 0 PDFs); a preservação da referência no repositório é **decisão pendente** (I-17). O texto das 17 páginas foi extraído e lido; o conteúdo visual foi conferido nas páginas 5, 6, 7–9, 11 e 14. Nada do conteúdo foi presumido: onde o PDF é omisso (por exemplo, a "disciplina indicada" do prêmio), isso foi registrado.
- **Complemento da disciplina 01:** `docs/enunciado/p1.png` e `p2.png` (somente as imagens estão no repositório; o PDF de origem, `gsrpa.pdf`, também está em `Downloads`, e **não é uma cópia duplicada** do PDF oficial).
- **Os três níveis do PDF foram mantidos separados:** desafio geral CitizenTech (p. 1–6); atividade específica da disciplina 01 (p. 11); disciplina integradora 06 (p. 14); e o vídeo pitch para concorrer ao prêmio (p. 11).
- Pontos do PDF usados: p. 4 (desafio), p. 6 (case integrado e as seis perguntas de uma boa proposta), p. 10–11 (calendário e regras de entrega), p. 11 (disciplina 01), p. 14 (disciplina 06), p. 12–15 (demais disciplinas). Referências por requisito, em `docs/matriz_requisitos.md`.

### 8.2 Inventário e resultado
Requisitos identificados no PDF, por nível (IDs da matriz). **PENDENTE conta como NÃO ATENDIDO** até haver ação da equipe.

| Nível (PDF) | Requisitos | ATENDIDO | PARCIALMENTE | NÃO ATENDIDO | NÃO COMPROVADO |
|---|---|---|---|---|---|
| Desafio geral CitizenTech (p. 1–6) — F01 a F25 | 25 (24 avaliáveis + 1 N/A: F25) | 11 | 9 | 3 | 1 |
| Disciplina 01 (p. 11) — G01 a G09 | 9 | 7 | 1 | 1 | 0 |
| Disciplina integradora 06 (p. 14) — H01 a H06 | 6 | 0 | 1 | 5 | 0 |
| Entrega geral e premiação (p. 10–11) — I01 a I03 | 3 | 0 | 0 | 1 | 2 |
| **Total** | **43** (42 avaliáveis + 1 N/A) | **18** | **11** | **10** | **3** |

*[Reclassificação da rodada 4 (11/11/2026): G01 passou de PARCIALMENTE ATENDIDO para ATENDIDO (os três temas do PDF têm função real; Pandas não é exigido); F25 passou de NÃO ATENDIDO para N/A (reflexão de contexto, não exigência explícita); F05 e F06 mantidos como NÃO ATENDIDO. Antes: 17 · 12 · 11 · 3, de 43.]*

- **Atendidos (18):** F01, F08, F09, F12, F15, F17, F18, F20, F21, F22, F23; G01, G02, G03, G04, G05, G06, G09.
- **Parcialmente atendidos (11):** F02, F04, F07, F10, F11, F13, F16, F19, F24; G07; H05.
- **Não atendidos (10):** F05 (acessibilidade), F06 (sustentabilidade), F14 (viabilidade); G08 (envio ao Portal, **pendente**); H01 (vídeo), H02 (ABNT), H03 (GitHub), H04 (módulos integrados), H06 (envio, **pendente**); I01 (vídeo pitch do prêmio).
- **N/A (1):** F25 (modelos de negócio): o PDF menciona o termo na **reflexão** do case (p. 6) e em um dos 15 exemplos de propostas (p. 9), mas **não o inclui entre os pontos que cada proposta deve considerar** nem em nenhuma disciplina; o projeto **não desenvolve modelo de negócio**, o que fica registrado como observação.
- **Não comprovados (3):** F03 (escuta de quem convive com o problema), I02 ("disciplina indicada" não identificada no PDF), I03 (Challenge Sprint, não descrito no PDF).
- **Adicionalmente:** dos 6 exemplos de temas do PDF, **3 ATENDIDOS** (tratamento de arquivos e dados; integração com APIs; banco de dados SQL), 0 PARCIAL e 3 NÃO ATENDIDOS (web scraping, e-mail automatizado, RPA desktop); os 3 temas próprios do projeto (NLP/ML, regras de negócio, resiliência) estão NÃO COMPROVADOS como "tema da disciplina" e **não são necessários** para o mínimo de 3; os 7 módulos das outras disciplinas estão NÃO COMPROVADOS.
- Afirmações como "atendido" exigem evidência arquivada ou executável; várias dependem de ressalvas (seção 8.6). Onde só havia uma menção na documentação (inclusão, qualidade de vida, benefício esperado), o status é **parcial**, e não atendido.

### 8.3 Temas da disciplina 01: função real e demonstrável
| Tema (exemplos do PDF, p. 11) | Função efetiva no fluxo | Evidência | Situação |
|---|---|---|---|
| Tratamento de arquivos e dados (o PDF cita Pandas como exemplo) | **Função real e necessária:** leitura de CSV e TXT com isolamento de falha por arquivo (`ingestao.py:19–61`), validação de 4 regras (`validacao.py:9–20`), normalização e mascaramento de CPF/e-mail/telefone (`texto.py:10–23`) e geração de `resultados.csv` (17 colunas), `revisao_humana.csv`, `rejeitados.csv` e `relatorio_execucao.json` (`pipeline.py:103–116`); 4 arquivos de entrada → 25 lidos, 21 processados, 3 rejeitados, 1 duplicado, 2 arquivos defeituosos tratados. Biblioteca padrão; transformações simples | Capturas `03`–`06`; 5 testes (validação, mascaramento, pasta ausente, arquivo corrompido) | **ATENDIDO** *[rodada 4: antes "parcial" pela ausência de Pandas, que o PDF não exige]* |
| Web scraping | Não existe | — | **NÃO ATENDIDO** |
| E-mail automatizado | Não existe (a resposta ao cidadão é gerada e gravada, **não enviada**) | — | **NÃO ATENDIDO** |
| RPA desktop | Não existe | — | **NÃO ATENDIDO** |
| Integração com APIs | ViaCEP em `geo.py:14–63` (HTTP, timeout, retry, cache, circuit breaker); enriquece 4 colunas das saídas (**16 dos 21 registros** enriquecidos na execução registrada); função **acessória** (não decide o roteamento) | Capturas `03`, `04a`, `07`; 4 testes | **ATENDIDO** |
| Banco de dados SQL | SQLite em `estado.py:9–32` (`CREATE`, `SELECT`, `INSERT OR IGNORE`, `DELETE`); o fluxo **decide com base nela** (duplicado ignorado; hash gravado só após o sucesso; `pipeline.py:71–78`); uso **mínimo**; **declarado em `docs/temas.md` desde a rodada 5** (linha "Banco de dados SQL (SQLite)") | Captura `11`; `test_pipeline_duplicado_invalido_e_idempotencia` | **ATENDIDO** |
| NLP/ML, regras de negócio, resiliência (próprios) | Funções reais, mas **fora da lista de exemplos** do PDF | Capturas `04a`, `05`, `07` | **NÃO COMPROVADO** como "tema da disciplina" |

**Conclusão (reavaliada na rodada 4):** **tratamento de arquivos e dados, integração com APIs e banco de dados SQL são três temas distintos** (módulos e funções diferentes no fluxo: preparar entradas e saídas; enriquecer o endereço; impedir o reprocessamento), **cada um com função real e evidência arquivada**. O mínimo de 3 é atingido **pela própria lista do PDF**, sem depender de NLP/ML ou regras de negócio e sem exigir Pandas (o PDF o cita só como exemplo). **Ressalvas mantidas:** API acessória; SQL de uso mínimo; transformações de dados simples (biblioteca padrão); o quadro `docs/temas.md` **declara o SQLite desde a rodada 5**, mas seus nomes **não foram confrontados com o plano de ensino**. Nenhuma funcionalidade foi presumida para completar o número. **Esta é uma avaliação do projeto, não uma aprovação do professor.**

**Acessibilidade e sustentabilidade (F05 e F06): lacunas mantidas.** O desafio pede promovê-las (p. 4) e a proposta deve considerar a acessibilidade (p. 6). Não há funcionalidade nem documento: 0 arquivos de código e 0 ocorrências em `README.md`, `docs/etica_ods.md` e `docs/temas.md`. A relação com os ODS (3, 10 e 16) é qualitativa e não substitui essas dimensões. Continuam **NÃO ATENDIDOS**.

**Modelos de negócio (F25): N/A.** O PDF cita "novos modelos de negócio" na frase de **reflexão** que abre o case (p. 6) e em um dos 15 cartões de exemplos (p. 9, slide 17). O que cada proposta deve fazer (demonstrar funcionamento e benefício, considerando viabilidade, inclusão, acessibilidade, proteção de dados e responsabilidade no uso da IA, e relacionar o impacto aos ODS) **não inclui modelo de negócio**, e nenhuma disciplina o pede. O projeto não o desenvolve; isso é uma observação, não um descumprimento.

### 8.4 Divergências entre as fontes
| Ponto | Complemento (`docs/enunciado`) | PDF oficial | Efeito |
|---|---|---|---|
| Tamanho do grupo | "até 5 integrantes" | "trio, dupla ou individualmente" (p. 11) | O grupo tem 3: atende às duas |
| Prazo | "segue o calendário da GS" | **19/11/2026 às 23h55**, Portal do Aluno (p. 11) | Prazo conhecido; envio pendente |
| Canal de entrega | "repositório Git, notebook Colab ou Jupyter" | Portal do Aluno, em Trabalhos (p. 11); **GitHub** para a disciplina 06 (p. 14) | O repositório é o conteúdo; o Portal é o canal; Git sem commits |
| Temas | "a escolha é do grupo" | Lista de exemplos "como…" (p. 11) | Interpretação em aberto (8.3) |
| Pesos do barema | 30/25/20/15/10% | **Não informa pesos** | Os pesos vêm só do complemento |

### 8.5 Situação atual dos itens I-01 a I-17 (após as rodadas de correção documental)
| Item | Situação | Observação |
|---|---|---|
| I-01 (checklist corrompido) | **Resolvido** | Rodada 1 |
| I-02 (integrantes) | **Resolvido** | Integrantes atualizados; turma continua pendente |
| I-03 (autoria e uso de IA) | **PENDENTE (grupo)** | Bloqueado por instrução; a divergência permanece |
| I-04, I-05 (README) | **Resolvidos** | Rodada 1 |
| I-06, I-07 (números) | **Esclarecidos** | `docs/evidencias.md`, "Esclarecimentos sobre contagens" |
| I-08, I-10 (`auditoria_ia.md`) | **Resolvidos** | Rodada 2 |
| I-09 (matriz) | **Resolvido** | Matriz corrigida e depois reescrita com o PDF |
| I-11, I-11b (não reproduzível; sem log) | **Marcados** | Decisão do grupo sobre manter ou remover; log de ambiente limpo não existe |
| I-12 (`diagnostico.md`) | **Resolvido** | Nota de atualização |
| I-13 (escopo do manifesto) | **Resolvido** *[rodada 7]* | Documentado em `docs/auditoria_ia.md`, seção 1: os **seis arquivos** protegidos, o que a verificação comprova e o que não comprova, o que está fora do manifesto, a recriação automática e o significado da data. `scripts/auditoria.py` **não foi alterado**. Também consta na Q26 e na matriz (J) |
| I-14 (extras e título `EVID_`) | **Resolvido** *[rodada 7]* | Extras marcados no checklist; o título `EVID_xxxx` é explicado no checklist (seção 3.2: janela de captura, 12 das 13 imagens, não é do CitizenTech; identificadores reais: `run_id` e `protocolo`) e no Plano B do roteiro |
| I-15 (Plano B) | **Resolvido** | Rodada 2 |
| I-16 (modelo ilegível sem teste) | **Aberto** (pendente) | Limitação registrada. O cenário de modelo ilegível **foi simulado em memória** em 11/11/2026 (`joblib.load` e `treinar` substituídos, sem escrever arquivos nem treinar; **script de uso único, não versionado**), mas **não possui teste automatizado específico**. A decisão de implementar esse teste **fica pendente de autorização técnica separada**; nenhum teste ou código foi alterado |
| I-17 (enunciado oficial no repositório) | **Aberto** (decisão do grupo pendente) | O enunciado oficial (`2TIAP(F-Y)-2026 - GS 2026.2.pdf`, 2.021.801 bytes, SHA-256 `b9af6e4e…c215`) **foi consultado** na revisão documental e seu conteúdo foi **analisado**; a cópia usada está **fora do repositório, em `Downloads`**, e **não está versionada** junto ao projeto (0 PDFs no repositório). A incorporação a `docs/enunciado/` foi avaliada e **não é claramente recomendável** (material oficial da FIAP; repositório possivelmente público; sem necessidade técnica); **recomendação registrada, sem cópia**: manter a referência (nome, data, tamanho e SHA-256) e, se o grupo quiser guardar o arquivo, fazê-lo em local privado ou após confirmar com o professor. A **preservação da referência no repositório continua sendo decisão pendente** |

### 8.6 Ressalvas técnicas preservadas
1. Dados **sintéticos**. 2. **Validação independente não realizada.** 3. Métricas **não comprovam desempenho em solicitações reais.** 4. Modelo **não validado para triagem clínica**; solução inapta para encaminhamento clínico autônomo. 5. **Falha grave** na classificação de um caso de possível urgência (trauma craniano), além de infarto e tentativa de suicídio sem prioridade alta. 6. Classificação é **apoio administrativo, com revisão humana**. 7. Limiar **0,45 sem calibração formal**. 8. **Métricas históricas não reproduzíveis** (já marcadas). 9. Manifesto SHA-256 protege **só seis arquivos**. 10. `auditoria.py` **recria o manifesto se ele estiver ausente**. 11. Git **sem commits e sem remoto**. 12. Ambiente limpo **relatado, sem log**.

---

## 9. Veredito atualizado (11/11/2026)

**A ENTREGA NÃO ESTÁ PRONTA. Estado: PENDENTE.** O PDF oficial não muda o veredito: ele amplia o que falta.

| Nível | Classificação | Síntese |
|---|---|---|
| Atividade da **disciplina 01** (p. 11) | **PARCIALMENTE ATENDIDA** | Tecnicamente sólida (ponta a ponta, resiliência, evidências, proteção de dados e ética), com ressalvas graves de qualidade. Pendentes: **nomes do quadro de temas não confrontados com o plano de ensino** (os 3 temas do PDF estão implementados e o quadro declara o SQLite desde a rodada 5; sem confirmação do professor), **Git sem commits**, **envio pelo Portal até 19/11/2026 às 23h55**, declaração de autoria e uso de IA |
| **Desafio geral** CitizenTech (p. 1–6) | **PARCIALMENTE ATENDIDO** | Problema, público, funcionamento, proteção de dados e ODS cobertos. **Sem tratamento** de acessibilidade, sustentabilidade, viabilidade e escuta de usuários; benefício e impacto não medidos |
| **Disciplina integradora 06** (p. 14) | **NÃO ATENDIDA** | Sem vídeo, ABNT, GitHub e módulos das demais disciplinas |
| **Prêmio** (p. 11, opcional) | **NÃO ATENDIDO** | Sem vídeo pitch; "disciplina indicada" não identificada no PDF |
| Qualidade técnica e integridade | **APROVADO COM RESSALVAS** | Hashes, testes e números conferem; ressalvas da seção 8.6 |

**Para considerar a entrega da disciplina 01 pronta**, a equipe precisa: (1) definir uma declaração única de autoria e uso de IA; (2) se quiserem, confirmar com o professor que os três temas são aceitos e confrontar os nomes do quadro de temas com o plano de ensino (o quadro já declara o SQLite desde a rodada 5); (3) decidir e autorizar o commit e a publicação; (4) **enviar pelo Portal até 19/11/2026 às 23h55**; (5) decidir sobre disciplina 06, prêmio e a documentação do desafio geral. **Nada disso foi feito por esta documentação, e nenhuma entrega incompleta foi apresentada como completa.**
