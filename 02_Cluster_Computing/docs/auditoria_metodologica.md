# Auditoria metodológica – Simulação Cluster Computing CitizenTech (iSPD)

Auditoria **somente de leitura**: nenhum modelo, script, resultado, README ou evidência foi alterado e nenhuma simulação foi reexecutada.
Este arquivo é o único artefato criado. Todo número abaixo foi lido de arquivos já existentes ou calculado a partir deles e do código;
cálculos próprios estão rotulados como **derivados**. Itens que não foi possível confirmar estão marcados **NÃO VERIFICADO**.

Legenda: **CORRETO** (sem alteração) · **RESSALVA** (pode ficar, mas exige explicação) · **PROBLEMA** (compromete validade ou interpretação).

## 1. Escopo e arquivos analisados
- Projeto: `README.md`, `resultados/comparacao.md`, `modelos/*.imsx`, `trace/carga_citizentech_400.trace`, `driver/*.java`,
  `scripts/executar.ps1`, `scripts/comparar.py`, `resultados/*/html/result.html`, `resultados/*/tarefas_por_worker.csv`, `resultados/*/console_*.txt`, `evidencias/*`.
- Código-fonte do iSPD (somente leitura, `D:\Downloads\ispd-main\ispd-main\src\ispd`): `motor/metricas/MetricasGlobais.java`, `Metricas.java`,
  `MetricasTarefa.java`; `motor/filas/servidores/CS_Comunicacao.java`, `CS_Processamento.java`, `implementacao/CS_Link.java`, `CS_Switch.java`,
  `CS_Internet.java`, `CS_Mestre.java`, `CS_Maquina.java`; `motor/workload/impl/TraceFileWorkloadGenerator.java`, `task/TaskBuilder.java`, `TraceTaskInfo.java`;
  `arquivo/xml/models/builders/QueueNetworkBuilder.java`, `arquivo/xml/utils/SwitchConnection.java`; `policy/scheduling/grid/impl/RoundRobin.java`;
  `gui/results/*`.

## 2. Diagnóstico por tópico

### 2.1 Comparabilidade da rede — **PROBLEMA de controle experimental** (impacto numérico limitado no tempo total)
**Configuração nos modelos** (`modelos/cenario_A_2_workers.imsx`, `cenario_B_4_workers.imsx`): mestre ligado a cada worker por **dois links
direcionados dedicados** (`link_ida_wK`: mestre→worker; `link_volta_wK`: worker→mestre), todos 100 Mbps, latência 0,001 s, load 0.
A: 2 workers, 4 links. B: 4 workers, 8 links (contagem de `<link` nos arquivos). O gerador é `driver/GerarModelos.java` (`buildModel`).

**Por que dois links:** o roteamento percorre apenas conexões de saída (`CS_Processamento.getMenorCaminho`, ~linha 245); sem o link worker→mestre ocorre
`NullPointerException` em `CS_Maquina.determinarCaminhos` (reproduzido na execução anterior).

**Largura de banda por link vs. agregada (distinção pedida):**
| | Por link | Nº links de ida | Capacidade agregada de envio do mestre (derivada) |
|---|---|---|---|
| A | 100 Mbps | 2 | 2 × 100 = 200 Mbps |
| B | 100 Mbps | 4 | 4 × 100 = 400 Mbps |

A banda **por link** é constante; a **agregada dobra** de A para B. Cada `CS_Link` é um servidor FIFO independente (`CS_Link.chegadaDeCliente`:
fila `filaPacotes`); o mestre despacha as 400 tarefas em t=0 e cada link atende só as suas.

**Evidência nativa do efeito (HTML, seção Tasks, `resultados/*/html/result.html`):** tempo médio de **fila de comunicação** = 4,0795 s (A) vs 2,0295 s (B).
Reproduzido analiticamente (derivado): 0,041 × 99,5 = 4,0795; 0,041 × 49,5 = 2,0295. Ou seja, a fila de rede por tarefa cai pela metade só porque há
mais links. O total de segundos de transmissão de ida é igual nos dois (16,4 s: 2×8,2 vs 4×4,1), apenas repartido em mais servidores.

**Favorece artificialmente o B?** Em termos de *desenho*, sim: a capacidade de comunicação agregada é uma segunda variável que muda junto com o número de
workers, contrariando "somente a quantidade de workers deve mudar". Em termos de *tempo total*, o efeito é pequeno: nenhum link passa de ~8,2 % de ocupação
(8,2 s em 100,042 s; 4,1 s em 50,042 s) e a simulação é limitada por computação (derivado: 0,5 s de CPU por tarefa × 200 ou 100 tarefas por worker ≫ tempo de rede).
O efeito aparece em métricas de rede (fila, ociosidade de comunicação) e na fração de 0,042 s de sobrecarga, não nos ~100 s / ~50 s.

**Como manter a capacidade agregada constante dentro do iSPD (verificado no código, NÃO simulado):**
- **Opção recomendada – ícone `cluster` (switch único).** `QueueNetworkBuilder.processClusterElement` cria 1 mestre + N máquinas ligados por **um `CS_Switch`**
  (`SwitchConnection.toMaster` / `toMachine`). `CS_Switch` é **um único servidor FIFO** (`filaPacotes`, `linkDisponivel`) compartilhado por todas as transferências
  (ida e volta), com `bandwidth`/`latency` do ícone. Variando só `nodes` (2 vs 4), a capacidade de comunicação fica constante (um meio compartilhado de 100 Mbps).
- **`internet` NÃO serve:** `CS_Internet` não tem fila (`chegadaDeCliente` agenda atendimento imediato), logo não limita a capacidade agregada.
- **Não verificado:** se o ícone cluster aceita exatamente os mesmos parâmetros (RoundRobin, 1 núcleo por máquina, potência do mestre) e como o mestre do cluster é
  contabilizado (`aMasterWithNoLoad` usa a mesma `power` do ícone). Exige teste.
- **[Superado pelo Adendo ao final: A'/B' foi simulado; a estimativa abaixo estava abaixo do valor real e o cluster como mestre foi rejeitado pelo validador.]**
  **Estimativa analítica, NÃO verificada por simulação (texto original da auditoria):** com um switch compartilhado, a demanda total de rede seria 400 × (0,041 + 0,001009765625) ≈ 16,8 s, menor que
  o tempo de computação nos dois cenários; o efeito sobre o tempo total deveria ser da ordem de décimos de segundo (chegada escalonada da primeira tarefa de cada worker:
  k × 0,041 s). A ordem de grandeza sugere que a conclusão qualitativa se mantém, mas isso precisa ser confirmado por simulação.

### 2.2 Métrica de utilização e ociosidade
**Origem dos valores no README (0,0419921 % e 0,0839490 %):** campo nativo `Idleness of processing resources`, impresso pelo console do terminal e pela aba Global da GUI
(`evidencias/A_global.png`, `B_global.png`).

**Fórmula nativa** (`MetricasGlobais.getOciosidadeComputacao`): média, sobre `redeDeFilas.getMaquinas()`, de `[(T − segundosDeProcessamento) − ocupacao × (T − segundosDeProcessamento)]`,
dividida por T e multiplicada por 100, onde T = tempo simulado. Com `load` = 0, equivale a `100 × (1 − proc/T)`. `getMaquinas()` contém apenas máquinas **não mestre**
(`QueueNetworkBuilder.makeAndAddMachine` coloca o mestre em outra lista), portanto a média é sobre os workers.
Conferência (derivado): 1 − 100/100,042009765625 = 0,0419921 %; 1 − 50/50,042009765625 = 0,0839490 % — idênticos aos valores nativos.

**`proc/T` como "utilização":** é a fração do **tempo simulado total** em que o worker esteve processando (segundos de processamento da `Table of Resource` ÷ tempo total).
Valores derivados: A = 99,958 %, B = 99,916 % (= 100 % − ociosidade nativa; relação exata aqui porque `load` = 0). **RESSALVA:** pode ser apresentada, mas descrita como
"fração do tempo simulado em processamento (derivada, = 100 % − ociosidade nativa de processamento)", e não como métrica nativa de utilização por worker. O denominador inclui
os 0,042 s de sobrecarga de rede (início e fim), por isso fica um pouco abaixo de 100 %. Não é mérito do paralelismo: é consequência das hipóteses (carga homogênea, sem contenção).
Nota: o README afirma "O iSPD não exibe utilização por worker"; isso vale para o HTML/tabela de recursos. A GUI tem a aba "Use of computing power through time" com gráficos
"Per machine/Per user/Per task" (`ResultsComputingPowerPane`); **NÃO VERIFICADO** o que esses gráficos plotam. A afirmação do README deve ser qualificada.

**Ociosidade de comunicação (95,8008 % A; 95,8026 % B)** — **RESSALVA:** `getOciosidadeComunicacao` é a média da ociosidade sobre **todos os links** (4 em A, 8 em B), então
depende do número de links; os valores por link são iguais (8,2 %/0,2 % de ocupação), por isso saem quase idênticos. Não é comparável como medida de "uso da rede".
Derivado: A 95,80079 %, B 95,80255 % (confere com a fórmula).

**`Efficiency` = 4 % — PROBLEMA se interpretada.** Fórmula nativa: média, por tarefa, de `capacidadeRecebida / (tamanhoTarefa × tempoProcessamento)`
(`MetricasTarefa.java:82-84`; `capacidadeRecebida` = `getPoderComputacional()` da máquina, chamada em `CS_Maquina.java:274`). Aqui: 1000 / (500 × 0,5) = **4,0**
(derivado; 0,5 s = 500/1000 é o tempo de processamento esperado; o valor por tarefa não foi impresso, mas 4,0 só é consistente com 0,5 s). A expressão **não é normalizada** (MFLOPS ÷ (MFLOP × s))
e dá 4,0 por ser (capacidade/tamanho)² — não mede eficiência paralela nem o impacto do número de workers; é igual nos dois cenários. O rótulo "BAD" vem de limiares fixos
(>70 GOOD, >40 MEDIA; `MetricasGlobais.toString`). **Não deve ser usada nem citada como eficiência do cluster.** Também `Satisfaction = 100 %` é constante no código
(`MetricasGlobais`: `satisfacaoMedia = 100`) e não carrega informação.

**Defeito no simulador (seção Tasks do HTML) — PROBLEMA do simulador, NÃO VERIFICADO por experimento:** o HTML mostra `Processing average time = 0.0 s` e `Queue average time (processamento) = 0.0 s`
nos dois cenários, apesar de haver 0,5 s de processamento por tarefa. No código, `Metricas.java:596-597` **atribui** (`=`) em vez de acumular (`+=`) e `Metricas.java:518` faz
`tempoMedioProcessamento = tempoMedioFilaProcessamento / numeroDeSimulacoes`. Esses campos **não devem ser usados**. (Os campos de **comunicação** usam `+=` e são coerentes.)

### 2.3 Tempos de comunicação — **CORRETO** (com ressalvas de modelagem)
Fórmula (`CS_Comunicacao.tempoTransmitir`, linhas ~93-95): `Mbits / larguraBandaDisponivel + latencia`, com `larguraBandaDisponivel = banda × (1 − ocupacao)` (ocupação 0).
- **Ida:** 4 Mbit / 100 Mbps + 0,001 s = **0,041 s** por tarefa (40 ms de transmissão + 1 ms de latência).
- **Retorno:** o arquivo de retorno é fixo, `FILE_MASTER_RECEIVE_SIZE = 0,0009765625` Mbit (`TaskBuilder`), não configurável pelo trace: 0,0009765625/100 + 0,001 = **0,001009765625 s**.
- **Os 0,042 s extras (derivado, exato):** 0,041 (ida da primeira tarefa, antes de o worker poder começar) + 0,001009765625 (retorno da última) = **0,042009765625 s**.
  Logo T(N) = 0,042009765625 + 400 × 0,5 / N reproduz exatamente 100,042009765625 (N=2) e 50,042009765625 (N=4).
- **Conferência com os totais de link do HTML:** ida 200 × 0,041 = 8,2 (A) e 100 × 0,041 = 4,1 (B); volta 200 × 0,001009765625 = 0,2019531 (A) e 0,1009766 (B) — idênticos
  à coluna "Communication performed".
- **Coerência com o simulador:** sim; a GUI e o terminal usam o mesmo motor, então a coincidência 100,042/50,042 **não** é validação independente da modelagem — a validação é a
  reconciliação analítica acima, que depende apenas do código lido.
- **Ressalvas de modelagem:** (a) a latência ocupa o servidor do link (o evento de saída usa `tempoTransmitir` completo, sem pipeline), de modo que cada tarefa ocupa o link por 0,041 s;
  (b) 0,5 MB = 4 Mbit assume 1 MB = 8 Mbit decimais; (c) o retorno é um valor fixo do simulador, não uma hipótese nossa.
- **Interpretação do speedup:** 49,979 % de redução e speedup 1,99916× decorrem da sobrecarga fixa de 0,042 s (Amdahl simples). Isso confirma as hipóteses do modelo, não "desempenho de cluster real".

### 2.4 Carga de trabalho — **CORRETO**
- Mesmo arquivo nos dois modelos: `<trace file_path="D:\Downloads\GS\CLUSTER\trace\carga_citizentech_400.trace" … tasks="400"/>`; SHA-256 do trace:
  `6636bdcbbf671fc4282b6e9714adeba3cc0b40932a4e7130a05c0d13b8aa3ee6`.
- Conteúdo verificado por leitura: 400 linhas de tarefa, todas `arr="0.0" sts="1" cpsz ="500.0" cmsz="4.0" usr="user1"`, ids únicos 1–400.
  `cmsz` é em **MBits** (`TraceTaskInfo`), logo 4,0 Mbit = 0,5 MB. `arr` é o instante de criação em segundos.
- RoundRobin (`RoundRobin.java`): lista circular de escravos, FIFO de tarefas. **Verificado:** contagens 200/200 (A) e 100/100/100/100 (B) em `tarefas_por_worker.csv`.
  **NÃO VERIFICADO diretamente:** a *ordem* de atribuição por tarefa (só as contagens foram registradas); a ordem decorre da leitura do código.
- Diferenças entre os cenários além do nº de workers: **nº de links e capacidade agregada de rede (ver 2.1)**; ids/posições de ícones (sem efeito). Potência, núcleos, load, owner,
  escalonador, trace e parâmetros de link são iguais.
- Mestre: não está na lista de escravos, não processa (HTML: `mestre` 0,0 s) — **CORRETO**.

### 2.5 Reprodutibilidade — **RESSALVA**
Pontos verificados em `scripts/executar.ps1` (leitura; não executado de novo):
- **Caminhos absolutos fixos:** `$Ispd = D:\Downloads\ispd-main\ispd-main`; `$Jdk = C:\Users\henry\…\jdk-17.0.21.9-hotspot\bin`; jars do Gradle por **caminho com hash** no cache do usuário.
  Em outro computador falha sem edição.
- **Pré-requisito não documentado:** exige `build\classes\java\main` do iSPD já compilado (pelo Gradle). O README não instrui como compilar. Versão/commit do iSPD **não registrados**
  (não há git; `-v` imprime "3.1"). Se `build\classes` corresponde ao código atual: **NÃO VERIFICADO**.
- **Versão do Java:** o `java` padrão do PATH é 1.8; o script usa o JDK 17 absoluto. O código usa recursos de Java ≥ 16 (text blocks, `switch ->`, `instanceof` com padrão, `Stream.toList`);
  `build.gradle` não declara toolchain. Compatibilidade com outras versões: **NÃO VERIFICADO**.
- **Regenera os modelos e o trace a cada execução** (`GerarModelos`), sobrescrevendo `modelos/*.imsx` e `trace/*.trace`. Isso não é "reproduzir a partir dos arquivos presentes".
  Se o projeto for movido, os `.imsx` mantêm o caminho absoluto antigo do trace (`C:\…`/`D:\Downloads\GS\CLUSTER\trace\…`) até serem regerados.
- **Dependência externa não documentada:** `scripts/comparar.py` exige Python 3 e **não é chamado** por `executar.ps1`; o README cita o script mas não o passo nem a dependência.
  `comparacao.md` diz "valores extraídos dos HTMLs", mas a contagem de tarefas vem do CSV do driver (`SimularModelo`), não do HTML.
- O comentário do script ("o motor escreve arquivos temporários no diretório corrente") **não foi confirmado**: o caminho usado (`TerminalApplication`) só chama `validarInicioSimulacao`
  e nenhum arquivo temporário apareceu em `resultados/*/`.
- **Logs não idênticos bit a bit:** `console_ispd.txt` contém "Simulation Execution Time" (tempo **real**, ~0,1 s) e códigos ANSI; só o tempo **simulado** é determinístico
  (trace fixo, sem sorteio; GUI e terminal deram os mesmos valores).
- **Integridade dos `.imsx` após a GUI:** a captura A mostra `[modified]`. As datas de gravação dos `.imsx` (16:52:31) são anteriores aos HTMLs (16:52:33), o que sugere que a GUI
  não os regravou, mas **hash anterior não foi guardado** — NÃO VERIFICADO.
- **Outra pessoa seguindo apenas o README:** hoje **não conseguiria** sem ajustes (caminhos, pré-requisito de build, Python).

**Inconsistências documentação × arquivos/código (para corrigir depois, não alteradas):**
1. `README.md`, limitações: "Efficiency … não foi investigada sua definição" — agora é conhecida (item 2.2).
2. `README.md` ponto 5: "O iSPD não exibe utilização por worker" — qualificar (HTML vs. gráficos da GUI).
3. `README.md`: "Foram exportados 4 gráficos (não 7)… neste modo" — causa **NÃO VERIFICADA**.
4. `README.md`: "rede de 100 Mbps" / "só muda a quantidade de workers" — omite que a capacidade agregada de rede dobra (2.1).
5. `resultados/comparacao.md`: título "extraídos dos HTMLs" vs. contagens vindas do CSV; coluna "Utilização derivada" deve ser renomeada conforme 2.2.
6. `README.md` e `comparacao.md` não citam que `Processing average time = 0.0` do HTML é defeito do simulador.

## 3. Resumo de classificação
| # | Achado | Classe |
|---|---|---|
| 1 | Capacidade agregada de rede dobra de A para B (links dedicados) | **PROBLEMA** (controle); impacto no tempo total pequeno |
| 2 | Banda por link constante (100 Mbps) | CORRETO |
| 3 | `proc/T` como "utilização" | RESSALVA (renomear; derivada) |
| 4 | Ociosidade de processamento nativa | CORRETO (fórmula conferida) |
| 5 | Ociosidade de comunicação (média sobre nº de links) | RESSALVA |
| 6 | `Efficiency` = 4 % | PROBLEMA se usada/interpretada; não usar |
| 7 | `Processing average time = 0.0` no HTML | PROBLEMA do simulador (não usar) |
| 8 | Tempos de comunicação e os 0,042 s | CORRETO (reconciliação exata) |
| 9 | Latência ocupa o link; retorno fixo 1 Kbit | RESSALVA (documentar) |
| 10 | Carga idêntica, 400 × 500 MFLOP, t=0, 4 Mbit | CORRETO |
| 11 | RoundRobin (contagens) | CORRETO; ordem não verificada |
| 12 | Reprodutibilidade/portabilidade | RESSALVA |
| 13 | Inconsistências do README/comparacao.md | RESSALVA (corrigir) |

## 4. Recomendações (NÃO implementadas; aguardam aprovação)
1. **Simulação de sensibilidade com capacidade agregada constante:** gerar A'/B' com o ícone `cluster` (um `CS_Switch` compartilhado, mesmos 100 Mbps/1 ms, `nodes` = 2 e 4, RoundRobin,
   mesmo trace). Registrar A/B (links dedicados) e A'/B' (meio compartilhado) lado a lado, explicando a diferença de desenho. Antes, confirmar que o ícone cluster mantém potência,
   núcleos e escalonador equivalentes.
2. Reescrever no README a descrição da rede: "um par de links de 100 Mbps por worker" e declarar que a capacidade agregada varia no desenho atual.
3. Renomear a coluna para "fração do tempo simulado em processamento (derivada)", citar a relação com a ociosidade nativa e qualificar a frase sobre utilização por worker.
4. Declarar `Efficiency`, `Satisfaction` e `Processing average time` como não usadas, com a justificativa do código.
5. Reprodutibilidade: parametrizar caminhos (iSPD, JDK), documentar pré-requisitos (build do iSPD, JDK 17, Python), separar "gerar modelos" de "executar", chamar `comparar.py` ou
   documentar sua execução, registrar hash/commit do iSPD e o SHA-256 dos `.imsx`/trace, e não regerar `modelos/` por padrão.
6. Registrar a ordem de atribuição do RoundRobin se for necessário defendê-la (não só as contagens).

## 5. Conclusão
- **Os valores 100,042 s e 50,042 s estão corretos como saída do modelo atual:** são exatamente explicados pela fórmula 0,042009765625 + 200/N × 0,5 e coincidem em GUI e terminal.
  **Não precisam ser recalculados** para o modelo "links dedicados por worker".
- **A comparação, porém, não está totalmente controlada**: a capacidade agregada de rede dobra junto com os workers. Com a rede longe da saturação, o efeito sobre o tempo total deve ser pequeno
  (estimativa analítica, não verificada), mas a premissa "somente os workers mudam" **não pode ser afirmada** sem ressalva.
- **Defensabilidade acadêmica:** a comparação pode ser defendida **desde que** o texto declare a topologia (links dedicados), descreva corretamente as métricas (item 2.2) e não use
  `Efficiency`/`Processing average time`. Para uma defesa sem ressalvas sobre a rede, recomenda-se **uma rodada adicional** (A'/B') com meio compartilhado.
- O resultado é sobre um modelo de hipóteses (carga homogênea, t=0, sem contenção forte); **não mede o desempenho real do classificador Python**.

## 6. Adendo (2026-11-12) – execução de A'/B' e atualização da documentação
O corpo da auditoria acima foi escrito em modo somente leitura e **não foi reescrito**; este adendo registra o que foi feito depois, com aprovação.

### 6.1 Simulação de sensibilidade A'/B' (switch compartilhado) — executada no motor oficial
- Primeira tentativa (cluster com `master="true"`): **rejeitada** por `IconicoXML.validarModelo` ("One or more parameters have not been configured"),
  porque `WrappedDocument.hasNoMasters` só considera `<machine>` com `<master>`. Os arquivos foram preservados em
  `resultados/tentativa_descartada_cluster_mestre/`. Isso corrige a recomendação 1 do item 4, que supunha o cluster como mestre (caveat então registrado como NÃO VERIFICADO).
- Topologia usada: mestre (`<machine>`) → `link_ida` → cluster não-mestre (um `CS_Switch` + N workers) → `link_volta` → mestre; capacidade de comunicação independente de N.
- Resultados (HTML): **A' = 100,12501953125 s; B' = 50,20701953125 s** (redução 49,856 %, speedup 1,9942×) contra A/B = 100,042009765625 / 50,042009765625 s (49,979 %, 1,9992×).
  Transmissão total igual nos dois (link de ida 16,4 s; switch 16,8039 s); fila média de comunicação 8,22 s × 8,27 s (em A/B: 4,08 s × 2,03 s).
- Reconciliação (derivada): T = 0,082 + (N−1)·0,041 + 0,5·400/N + 0,00201953125 reproduz exatamente A' e B'.
- A estimativa da seção 2.1 (≈100,083 / 50,165 s) **supunha um único salto** e ficou abaixo do real (dois saltos em série: tronco + switch).
- Limitações de A'/B': dois saltos e 2 ms de latência por sentido (diferença de desenho em relação a A/B); CSV de tarefas por worker agrega `worker=400`
  (distribuição obtida pelos segundos de processamento do HTML); aviso de DTD (`energy` não declarado para `cluster`); **não aberto na GUI**.
- Reclassificação do achado 1 (rede): continua **PROBLEMA de controle** para A/B tomados isoladamente, agora **quantificado**: com capacidade agregada constante a redução
  muda 0,12 ponto percentual. A comparação A/B pode ser defendida **desde que** A'/B' seja apresentada junto e a topologia declarada.

### 6.2 Atualizações do `README.md` feitas a partir da auditoria
Itens 1 (Efficiency), 2 (utilização por worker), 3 (gráficos, causa não verificada) e 4 (descrição da rede) da lista de inconsistências foram corrigidos no README;
foram adicionadas as seções "Sensibilidade A'/B'", "Auditoria metodológica (resumo)" e "Hashes registrados" e a lista de pendências.

### 6.3 Ainda não implementado
- Item 5 da lista de inconsistências (`resultados/comparacao.md`: título "extraídos dos HTMLs" e coluna "Utilização derivada") — **arquivo não alterado**.
- Recomendações de reprodutibilidade (item 4.5): parametrizar caminhos, documentar pré-requisitos, separar geração de execução, chamar/documentar `comparar.py`.
- Registro da ordem de atribuição do RoundRobin; capturas da aba Resources; abertura de A'/B' na GUI.
- `scripts/executar.ps1` e `scripts/executar_sensibilidade.ps1` **não foram reexecutados** após esta atualização; `executar.ps1` continua regerando `modelos/` e `trace/`.

### 6.4 Etapa de correções documentais e de reprodutibilidade (sem executar simulações)
Executada após o adendo 6.1–6.3, **sem** rodar nem regenerar simulações e **sem** alterar modelos, trace, HTMLs, CSVs ou tempos registrados (verificado por manifesto SHA-256 antes/depois).
- **Item 5 da lista de inconsistências (comparacao.md) — tratado:** `scripts/comparar.py` reescrito e `resultados/comparacao.md` regenerado a partir dos HTMLs/CSVs existentes: fontes
  separadas (HTML × CSV × derivado), coluna "Fração do tempo simulado em processamento (derivada)" com a ressalva de que não é métrica nativa por worker, A/B separado de A'/B'
  (topologia diferente, sem validação na GUI) e `Efficiency`/`Satisfaction`/`Processing average time` declarados como não usados.
- **Reprodutibilidade (item 4.5) — tratado em parte:** `scripts/_comum.ps1`, `gerar_modelos.ps1`, `executar.ps1`, `executar_sensibilidade.ps1` sem caminhos de computador embutidos
  (parâmetros/variáveis de ambiente), geração separada da execução, sem sobrescrita por padrão (`-Regenerar`, `-SobrescreverResultados`), checagem de JDK ≥ 17 e de pré-requisitos
  (`-Verificar`). **Permanecem** as dependências documentadas no README (JDK 17, build do iSPD, layout do cache Gradle, classes internas do iSPD, caminho absoluto do trace no `.imsx`).
  O caminho de execução das simulações dos scripts reescritos **não foi testado**.
- **RoundRobin — esclarecido, não registrado:** o código garante só a divisão 400/N; a ordem entre eventos empatados em t=0 **não é garantida** (`PriorityQueue` com `FutureEvent.compareTo` só por tempo).
  Há um procedimento preparado (3º argumento opcional de `SimularModelo`), compilado e **não executado**.
- Continuam abertos: executar os scripts reescritos numa cópia; registrar a ordem do RoundRobin; capturas Resources; validação de A'/B' na GUI; versão do iSPD; teste em outro computador.

### 6.5 Evidências visuais adicionais, validação visual de A'/B' e investigação do parser da GUI (2026-11-12)
**Evidências.** `evidencias/` passou de 6 para 13 imagens (nenhuma sobrescrita): Resources de A, B, A' e B' (4); configuração do cluster de A' e B' (`Ap_cluster_config_nodes2.png`, `Bp_cluster_config_nodes4.png`) e o diagrama de A' com o mestre selecionado
(`Ap_diagrama_mestre_selecionado.png`). O inventário arquivo a arquivo, com o conteúdo efetivamente visível, está no `README.md` ("Inventário das 13 evidências").
Todas as imagens existem e abrem (verificação de assinatura PNG, CRC e descompressão); o texto das quatro tabelas Resources foi conferido com a tabela "Table of Resource" dos HTMLs oficiais (valores idênticos, inclusive casas decimais).

**O que passou a estar comprovado visualmente (A'/B'):** `nodes` = 2 (A') e 4 (B'); cluster com 1000 MFLOPS, 1 núcleo, banda 100,0, latência 0,001, Master desmarcado, scheduler `---`; mestre com `Slave Nodes [id: 1 worker]`; processamento por worker (100,0 s e 50,0 s) e
transmissão por link/switch (16,4 s; 0,4039 s; 16,8039 s) iguais aos HTMLs oficiais.
**O que NÃO está comprovado visualmente:** aba Global/Tasks/Users de A' e B' (os tempos 100,125 s e 50,207 s não foram vistos na GUI); o erro do parser (sem captura); qualquer aviso em B'; os workers individuais como ícones (a GUI mostra um único ícone de cluster).
Isto **substitui** as afirmações anteriores deste documento e do README de que A'/B' "não foram abertos na GUI" (os registros históricos 6.1–6.4 e os relatórios de validação mantêm o texto da época).

**Erros semânticos do parser ao simular A' (investigação no código-fonte, sem modificar o modelo).**
- *Origem:* `SimulationDialog` chama `ProgressoSimulacao.AnalisarModelos` (`motor/ProgressoSimulacao.java:72`), que grava `modeloiconico`/`modelosimulavel` na pasta de trabalho do iSPD e roda `InterpretadorSimulavel.leArquivo` (parser JavaCC, `arquivo/interpretador/internal/simulable/Interpretador.jj`). A mensagem "Erros Encontrados durante o parser do Modelo Simulavel:" é montada nesse parser; `resuladoParser()` abre a janela "Found Errors".
- *Linha 8 / `---`:* o conversor (`internal/iconic/Interpretador.java:107`) escreve para clusters `CS_1 <nome> 2 <nº escravos> <algoritmo> FILAS …`; para cluster **não mestre** `<algoritmo>` é o padrão `---` (`gui/iconico/grade/Cluster.java:106`). A gramática (`Interpretador.jj:395`) exige ali um token `nome` (começa com letra); `---` é o token `VAZIO`. O arquivo gerado (`modelosimulavel`, gravado às 22:17:25) tem na linha 8:
  `CS_1 worker 2 2 --- FILAS fila_0_worker fila_1_worker SERVIDORES serv_worker 0 1000.000000 100.000000 0.001000`. As colunas informadas (19 e 25) são o fim de `---` e de `FILAS` nessa linha (derivado; o parser reporta o fim do token). O 1º erro decorre de `---`; a repetição no `FILAS` vem da recuperação de erro (`consomeTokens` para em `FILAS`); o **caminho exato da repetição não foi rastreado**.
- *Por que a simulação continuou:* o resultado do parser é descartado (`interpretSimulationModel` ignora o retorno; `resuladoParser` só mostra a janela). A rede e a carga são criadas a partir do XML (`SimulationDialog.java` ~152-180: `IconicoXML.newRedeDeFilas(this.model)` e `newGerarCarga(this.model)`), o mesmo caminho do terminal.
- *Classificação:* **RESSALVA** — incompatibilidade entre o conversor/validador da GUI e clusters não mestres com algoritmo `---` (padrão da GUI), isto é, validação auxiliar incompleta. Não indica problema de configuração segundo o motor: o caminho XML aceita o cluster (`QueueNetworkBuilder.processClusterElement`) e os recursos simulados coincidem com os do HTML oficial. **Não verificado:** se B' gera o mesmo aviso (a linha é gerada pelo mesmo código, mas não foi capturada) e se A/B não geram aviso (não reportado).
  Não se conclui que o aviso é "inofensivo" por coincidência de resultados: a conclusão se apoia na leitura do código (resultado do parser não usado) **e** na igualdade dos recursos simulados.

**`[modified]`.** `MainWindow.modificar()` (`gui/MainWindow.java:863`) define o título "… [modified] …" e `currentFileHasUnsavedChanges`; é chamada, entre outros, por `DesenhoGrade.adicionarVertice` (`gui/iconico/grade/DesenhoGrade.java:352-381`) ao adicionar um ícone com a ferramenta ativa (que emite a notificação "Cluster icon added.", linha 367). Essa notificação aparece nas capturas de A' e B', o que é **compatível** com um clique na área de desenho com a ferramenta Cluster ativa. Evidências: o ícone selecionado tem as propriedades do arquivo (id 1, x 300, y 400, nodes 2/4, 1000, 100, 0,001); a aba Resources coincide com o HTML oficial; os `.imsx` em disco permanecem com o mesmo hash (não foram salvos).
Não há evidência de que a simulação rodou um modelo diferente, mas **não é possível excluir** um ícone extra em memória que não apareça nas capturas (não foi verificado se um cluster recém-adicionado e não configurado produziria linha extra na tabela). Em A, `[modified]` aparece em `A_gui_sem_selecao.png` sem a notificação de ícone adicionado; a causa **não foi identificada**. Classificação: **RESSALVA**.

**Atualização de `resultados/comparacao.md`:** a seção A'/B' dizia que A'/B' "não foram validados na interface gráfica"; o texto foi corrigido (gerado por `scripts/comparar.py`, sem alterar números). Os relatórios `docs/validacao_*.md` registram a igualdade do `comparacao.md` regenerado **na época**; após esta correção de texto os dois arquivos diferem apenas nessa frase.

**Pendências restantes:** aba Global/Tasks/Users de A' e B' na GUI; captura do aviso do parser (se desejado); teste em outro ambiente; versão/commit do iSPD.
