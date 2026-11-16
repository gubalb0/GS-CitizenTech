# CitizenTech – Simulação de cluster no iSPD (Global Solution 2026.2, FIAP)

Todos os parâmetros abaixo são **hipóteses de simulação**, não medições. O modelo **não mede** o desempenho
real do classificador Python; apenas simula fila, processamento e rede com valores plausíveis.
"Tempo" = **tempo simulado** do iSPD (segundos simulados), distinto do tempo real de execução do programa.

## Estrutura
| Caminho | Conteúdo |
|---|---|
| `modelos/cenario_A_2_workers.imsx`, `cenario_B_4_workers.imsx` | Modelos Grid gerados pelo escritor oficial `IconicoXML` |
| `trace/carga_citizentech_400.trace` | Trace único e compartilhado (400 tarefas) |
| `driver/GerarModelos.java` | Gera trace + modelos (única variável: nº de workers); **não sobrescreve** sem `--regenerar` |
| `driver/SimularModelo.java` | Executor complementar (mesmo motor) que lista tarefas por worker; 3º argumento opcional grava detalhe por tarefa (ver "RoundRobin") |
| `scripts/_comum.ps1` | Funções comuns (resolve JDK/iSPD/classpath, pré-requisitos, execução); não é chamado diretamente |
| `scripts/gerar_modelos.ps1` | **Gera** trace e modelos (não simula); `-Regenerar` para sobrescrever |
| `scripts/executar.ps1` | **Executa** A e B nos modelos existentes (não gera nada); recusa sobrescrever resultados sem `-SobrescreverResultados` |
| `scripts/comparar.py` | Monta `resultados/comparacao.md` a partir dos HTMLs/CSVs existentes (Python 3, só biblioteca padrão) |
| `resultados/*/html/result.html` | HTML oficial exportado pelo iSPD (`ispd.Main -in … -o …`) |
| `resultados/*/console_*.txt`, `tarefas_por_worker.csv` | Logs e contagem de tarefas |
| `resultados/comparacao.md` | Comparação A/B e A'/B' (fontes HTML × CSV × derivado indicadas no próprio arquivo) |
| `modelos/cenario_Ap_2_workers_switch.imsx`, `cenario_Bp_4_workers_switch.imsx` | Sensibilidade A'/B' (switch compartilhado) |
| `driver/GerarModelosCluster.java`, `scripts/executar_sensibilidade.ps1`, `scripts/comparar_sensibilidade.py` | Geram, executam e comparam A'/B' |
| `resultados/Ap_2_workers_switch/`, `resultados/Bp_4_workers_switch/`, `resultados/comparacao_sensibilidade.md` | Resultados de A'/B' e comparação A/B × A'/B' |
| `resultados/tentativa_descartada_cluster_mestre/` | Primeira tentativa de A'/B' (cluster como mestre), rejeitada pelo validador do iSPD; mantida como registro |
| `docs/auditoria_metodologica.md` | Auditoria metodológica (somente leitura) e seu registro posterior |

## Parâmetros (idênticos nos dois cenários, exceto o nº de workers e a consequência direta na rede)
400 tarefas, todas com `arr=0.0` · 500 MFLOP (`cpsz`) · entrada 0,5 MB = 4,0 Mbit (`cmsz`) · workers 1000 MFLOPS,
1 núcleo · mestre 1000 MFLOPS · links 100 Mbps **por link**, latência 0,001 s · escalonador RoundRobin · usuário `user1` · carga ociosa 0.
**Atenção (rede):** em A/B cada worker tem seu par de links; a banda **por link** é constante, mas a capacidade **agregada** de envio do mestre
cresce com o nº de workers (200 Mbps em A, 400 Mbps em B). A seção "Sensibilidade A'/B'" mantém a capacidade agregada constante.

## Validações técnicas no código-fonte (iSPD)
1. **Trace** (`TraceFileWorkloadGenerator`, `TraceTaskInfo`, `TraceTaskBuilder`): pula 5 linhas de cabeçalho; cada linha é
   separada por aspas e lida por posição: id=campo 1, `arr`=3 (s), `sts`=5, `cpsz`=7 (MFlops), `cmsz`=9 (**MBits**), `usr`=11.
   `arr="0.0"` coloca as 400 tarefas em t=0; os tempos são lidos do arquivo, sem aleatoriedade. Os dois modelos apontam para o mesmo arquivo.
   Ao contrário da carga `node`, que usa exponencial com semente `currentTimeMillis`.
   *Limitação encontrada*: toda linha depois do cabeçalho vira tarefa; por isso o trace **não pode** ter `</trace></system>` no fim
   (causa `ArrayIndexOutOfBoundsException: Index 11`). O arquivo foi gerado sem essas linhas.
2. **RoundRobin** (`RoundRobin.java`): fila de tarefas (`escalonarTarefa` = `remove(0)`) e lista circular de escravos. Confirmado na execução:
   A = 200/200 tarefas; B = 100/100/100/100 (`tarefas_por_worker.csv`). O HTML não traz contagem de tarefas por worker;
   ela foi lida do estado final das `Tarefa` do motor pelo `SimularModelo`. No HTML, segundos de processamento ÷ 0,5 s/tarefa dá o mesmo valor.
   **A ordem de atribuição (qual tarefa vai a qual worker) não está registrada**; ver a seção "RoundRobin: o que está comprovado".
3. **Comunicação** (`TaskBuilder`, `CS_Link`): a tarefa envia `cmsz` (4 Mbit) ao worker e o worker devolve ao mestre um arquivo fixo de
   0,0009765625 Mbit (`FILE_MASTER_RECEIVE_SIZE`), que não é configurável pelo trace. Tempo por transmissão = Mbit/banda + latência
   (latência em segundos). Ida: 4/100+0,001 = 0,041 s; volta ≈ 0,00101 s. O iSPD contabiliza as duas direções (colunas "Communication performed" dos links).
4. **Mestre** (`CS_Mestre`): o escalonador só recebe os escravos como destinos (`addEscravo`). O mestre só poderia processar se fosse
   listado como escravo; não foi, e o HTML mostra `mestre` com 0,0 s de processamento.
5. **Campos do HTML** (`SalvarResultadosHTML`): tempo total = "Total Simulated Time" em *Global metrics*; processamento por worker =
   coluna "Processing performed" da *Table of Resource* (segundos). O HTML e a tabela de recursos **não trazem utilização por worker**
   (a GUI tem gráficos "Use of computing power…"; o que plotam **não foi verificado**). A fração 99,958 % (A) e 99,916 % (B) é **derivada
   por nós** = processamento ÷ tempo total simulado = 100 % − ociosidade nativa de processamento (com `load` = 0); deve ser lida como
   "fração do tempo simulado em processamento", não como métrica nativa de utilização.
6. **Equivalência**: o diff dos `.imsx` mostra apenas workers/slaves e links adicionais (4→8 links; 2 por worker, mesmos 100 Mbps/1 ms, load 0).
   Máquinas: mesmo `power`, `number`=1, owner, load; mesmo `<trace>`, mesmo escalonador. **Ressalva:** os links adicionais elevam a capacidade
   agregada de rede de A para B (fila média de comunicação: 4,0795 s em A × 2,0295 s em B); ver "Auditoria" e "Sensibilidade A'/B'".

## Limitações / observações
- **Links direcionados**: o motor só segue conexões de saída (`CS_Processamento.getMenorCaminho`). Com um único link mestre→worker a execução falha
  em `CS_Maquina.determinarCaminhos` (NPE). Por isso há **2 links por worker** (ida e volta) com parâmetros idênticos.
  Cada worker tem link dedicado, então a rede cresce com o número de workers e **não há gargalo compartilhado**: isso favorece o speedup quase ideal.
- Chegada simultânea em t=0, tarefas homogêneas e RoundRobin tornam o resultado quase perfeitamente linear; não representa carga real.
- **"Efficiency" (4 %) não deve ser usada como eficiência do cluster.** Pelo código (`MetricasTarefa.calcEficiencia`), é a média por tarefa de
  capacidade ÷ (tamanho × tempo de processamento) = 1000 ÷ (500 × 0,5) = 4; não é normalizada e é igual em todos os cenários. "Satisfaction = 100 %"
  é constante no código. "Idleness of communication" é a média sobre todos os links e depende do nº de links.
- **"Processing average time = 0.0" do HTML (seção Tasks) não deve ser usado**: pelo código (`Metricas.java`, linhas ~518 e 596-597) parece defeito do
  simulador (atribui em vez de acumular); não confirmado por experimento. Os tempos de comunicação (fila e transmissão) são coerentes.
- Foram exportados 4 gráficos (não 7); a causa **não foi verificada**.
- Ressalvas de modelagem: a latência ocupa o servidor do link (sem pipeline); o arquivo de retorno é fixo (0,0009765625 Mbit) e não configurável;
  0,5 MB = 4 Mbit assume 1 MB = 8 Mbit decimais.
- Os `.imsx` foram escritos com o escritor oficial e validados pelo leitor oficial (DTD); a abertura e a execução na GUI estão
  registradas na seção "Execução pela interface gráfica" abaixo.
- Execução única por cenário (a carga é determinística); executar de novo deve repetir os números.

## Como reproduzir em outro computador (Windows PowerShell 5.1)
**Pré-requisitos**
1. **JDK 17** (testado: Eclipse Temurin 17.0.21). O código do iSPD usa recursos de Java ≥ 16; outras versões **não foram testadas** (o script avisa se for > 17 e recusa < 17).
   O `java` do PATH desta máquina era o 1.8; por isso o JDK é sempre informado explicitamente.
2. **iSPD compilado** (mesma versão usada aqui; sem git, o commit **não foi registrado**): na pasta do iSPD, com JDK 17, `.\gradlew build`
   (gera `build\classes\java\main`; o 1º build baixa o Gradle 7.4 e as dependências, o que exige internet — não reverificado aqui). Alternativa: `.\gradlew shadowJar` e usar `-IspdJar`.
3. **Python 3** para `scripts\comparar.py` (usa só a biblioteca padrão; testado com 3.14).

**Configuração** (parâmetros `-IspdDir`, `-JdkHome`, `-GradleCache`, `-IspdJar` ou variáveis `ISPD_DIR`, `ISPD_JDK_HOME`/`JAVA_HOME`, `GRADLE_USER_HOME`, `ISPD_JAR`):
```powershell
$env:ISPD_DIR      = 'C:\caminho\ispd'                        # contém build.gradle e src\
$env:ISPD_JDK_HOME = 'C:\caminho\jdk-17'                      # contém bin\java e bin\javac
```
**Passos**
```powershell
# 0) Verificar pré-requisitos (não compila, não simula)
.\scripts\executar.ps1 -Verificar
# 1) GERAR modelos/trace (não simula). Padrão: NÃO sobrescreve. Em outro computador, o .imsx guarda o caminho ABSOLUTO do trace, então regenere:
.\scripts\gerar_modelos.ps1 -Regenerar
# 2) EXECUTAR (não gera nada). Recusa se resultados\ já existirem; use outra cópia do projeto (-Raiz) ou -SobrescreverResultados
.\scripts\executar.ps1
.\scripts\executar_sensibilidade.ps1
# 3) Comparar (só lê resultados; reescreve resultados\comparacao.md)
python scripts\comparar.py
python scripts\comparar_sensibilidade.py
```
**Como saber se reproduziu:** `trace\carga_citizentech_400.trace` deve ter SHA-256 `6636bdcbbf671fc4282b6e9714adeba3cc0b40932a4e7130a05c0d13b8aa3ee6` (ver "Hashes registrados"); o **tempo simulado** deve ser 100,042009765625 (A),
50,042009765625 (B), 100,12501953125 (A') e 50,20701953125 (B'). O hash do `.imsx` **muda** em outra pasta (caminho absoluto do trace); o conteúdo é igual exceto esse atributo
(verificado gerando os quatro modelos numa pasta temporária: iguais aos atuais após normalizar `file_path`). Logs de console contêm tempo **real** de execução e variam.

**O que foi e o que NÃO foi testado após esta revisão dos scripts** (sem executar simulações, por restrição desta etapa):
- Testado: sintaxe dos 4 scripts; `-Verificar` com parâmetros e com variáveis de ambiente; recusa de JDK/iSPD inexistentes; recusa de sobrescrita de resultados; `gerar_modelos.ps1`
  no padrão (manteve todos os arquivos) e geração dos 4 modelos + trace numa pasta temporária (idênticos aos atuais exceto o caminho absoluto).
- **NÃO testado:** o caminho de execução das simulações dos scripts reescritos (`Invoke-Cenarios`: compilação dos drivers, chamadas ao motor, gravação dos logs em UTF-8); a versão da
  checagem de Java < 17 com um JDK 8 real; outro computador, outro sistema operacional ou outra versão do PowerShell.
- **Atualização posterior:** o caminho de execução, a geração com `-Regenerar` (após corrigir dois defeitos) e a comparação foram depois exercitados numa cópia isolada — ver `docs/validacao_reprodutibilidade.md` e `docs/validacao_ponta_a_ponta.md` (o teste com JDK 8 real e outros ambientes continuam **não feitos**).

**Dependências/limitações que permanecem (a parametrização não elimina)**
- Só testado em Windows com PowerShell 5.1 e `build\classes` produzidos pelo Gradle 7.4 sob JDK 17.
- Os drivers (`driver/*.java`) compilam contra **classes internas** do iSPD (`IconicoXML`, `SimulacaoSequencial`, `Tarefa`…); outra versão do iSPD pode quebrar a compilação.
- A descoberta dos jars depende do layout do cache do Gradle (`modules-2\files-2.1`) e dos nomes/versões exatos das dependências.
- O `.imsx` embute o caminho absoluto do trace; mover o projeto exige `gerar_modelos.ps1 -Regenerar` (ou editar o `file_path`). Caminho relativo **não foi testado**.
- Versão/commit do iSPD não registrados; `driver\out\` é artefato de compilação regravado a cada execução dos scripts.

## RoundRobin: o que está comprovado e o que não está
**Comprovado pelo código e pelas contagens existentes**
- `RoundRobin.escalonarRecurso` percorre a lista de escravos de forma circular e `escalonarTarefa` retira sempre a 1ª tarefa da fila; com 400 tarefas e N workers
  **cada worker recebe 400/N tarefas, independentemente da ordem de chegada**. Isso confere com os dados: A = 200/200 e B = 100×4 (`tarefas_por_worker.csv`);
  em A'/B' (CSV agregado) a divisão vem dos segundos de processamento do HTML (100,0 s e 50,0 s ÷ 0,5 s = 200 e 100 tarefas por worker).
- A ordem dos workers no ciclo é a ordem dos `<slave>` no modelo (A/B) ou o índice do nó dentro do cluster (A'/B').

**Não comprovado: quais tarefas (ids) foram para cada worker e em que ordem**
- Todas as tarefas têm `arr=0.0`. A fila de eventos do motor (`SimulacaoSequencial`) é um `java.util.PriorityQueue` e `FutureEvent.compareTo` compara **só o tempo de criação**;
  portanto a ordem entre eventos empatados em t=0 **não é garantida pelo código** como a ordem de id/arquivo. Não se deve afirmar "tarefa 1 → worker1, tarefa 2 → worker2…" sem registro.
- Os resultados existentes (HTML e CSV de contagens) **não contêm** o mapeamento id → worker nem a ordem de despacho.

**Procedimento para registrar sem modificar o motor (preparado, NÃO executado nesta etapa)**
*(Atualização posterior: o 3º argumento foi exercitado numa cópia isolada — ver `docs/validacao_reprodutibilidade.md`, seção 6 — e não por este trecho original.)*
`driver/SimularModelo.java` aceita um 3º argumento opcional; ele grava, apenas lendo getters públicos de `Tarefa` após a simulação, `indice_na_lista;id;estado;worker_id;worker_num;criacao_s;espera_comunicacao_s;comunicacao_s;inicio_processamento_s;fim_processamento_s`.
A mudança foi só compilada. Para usá-lo **sem sobrescrever os resultados existentes**, rode manualmente em uma pasta nova (com `$cp` = `driver\out` + classpath do iSPD, como em `scripts\_comum.ps1`):
```powershell
& "$env:ISPD_JDK_HOME\bin\java.exe" -cp $cp SimularModelo modelos\cenario_A_2_workers.imsx saida\tarefas_por_worker.csv saida\tarefas_detalhe.csv
```
Limites mesmo após executar: o arquivo mostra o **estado final** (worker de cada tarefa, tempos), não um log de decisões do escalonador; a ordem de despacho só pode ser **inferida**
(p.ex., pela espera na fila do link, que em A/B é múltipla de 0,041 s). Um log direto exigiria instrumentar `RoundRobin`/`CS_Mestre`, o que alteraria o código do iSPD e **não foi feito**.

## Execução pela interface gráfica (GUI) do iSPD
Os quatro modelos (A, B, A' e B') foram **abertos e simulados (botão Simulate) na interface gráfica do iSPD pelo usuário**. As capturas foram tiradas pelo usuário e copiadas
para `evidencias/` sem sobrescrever nada. Nenhum modelo foi salvo pela GUI (hashes dos `.imsx` inalterados) e nenhum resultado oficial foi substituído.

| Cenário | Tempo total simulado na GUI | Tempo no HTML exportado pelo terminal | Ociosidade de processamento (GUI) |
|---|---|---|---|
| A (2 workers) | 100.042 s | 100,042 s | 0,0419921 % |
| B (4 workers) | 50.0420 s | 50,042 s | 0,0839490 % |

Os tempos de A e B na GUI **coincidem** com os dos HTMLs do terminal (100,042 s e 50,042 s); a ociosidade das capturas é a mesma impressa no console do terminal.
Para **A' e B' o tempo total na GUI não foi capturado** (a aba Global não foi fotografada): só a aba **Resources** foi registrada, e seus valores coincidem com o HTML oficial (ver abaixo).
Nas capturas de A/B, o painel do mestre mostra Label `mestre`, 1000,0 MFLOPS, 1 núcleo, Master marcado e Scheduling algorithm RoundRobin (texto cortado como "RoundRo…").
O X vermelho ao lado do ícone 0 é um aviso visual da GUI (política de alocação de VMs `vm_alloc` igual a "---", conforme `Machine.checkConfiguration`) e não impediu a simulação.

### Inventário das 13 evidências em `evidencias/`
| Grupo | Arquivo | Cenário | Conteúdo efetivamente visível | Conferência |
|---|---|---|---|---|
| 1. Modelo A/B aberto na GUI | `A_diagrama.png` | A | Diagrama: mestre (0) e 2 workers (1, 2) com links | visual |
| | `A_mestre_config.png` | A | Painel do mestre: `mestre`, 1000.0, 1 núcleo, Master, RoundRobin, Slave Nodes | visual |
| | `A_gui_sem_selecao.png` | A | Janela com `cenario_A_2_workers.imsx` aberto; título com `[modified]`; nenhum ícone selecionado | visual |
| | `B_diagrama_mestre_config.png` | B | Diagrama: mestre e 4 workers + painel do mestre (mesmos parâmetros) | visual |
| 2. Aba Global A/B | `A_global.png` | A | Total Simulated Time 100.042; ociosidade de processamento 0,0419921 %; Efficiency 4 % (não usada) | coincide com o HTML |
| | `B_global.png` | B | Total Simulated Time 50.0420; ociosidade de processamento 0,0839490 % | coincide com o HTML |
| 3. Aba Resources A/B | `A_resources_gui.png` | A | `worker1`/`worker2` 100.0 s; `mestre` 0.0; `link_ida_w1/w2` 8.200000000000033; `link_volta_w1/w2` 0.2019531249999997 | texto conferido com o HTML oficial |
| | `B_resources_gui.png` | B | `worker1`–`worker4` 50.0 s; `mestre` 0.0; `link_ida_w1–w4` 4.099999999999996; `link_volta_w1–w4` 0.10097656250000019 | texto conferido com o HTML oficial |
| 4. Cluster de A'/B' | `Ap_diagrama_mestre_selecionado.png` | A' | Título `cenario_Ap_2_workers_switch.imsx`; mestre selecionado (`[id: 1 worker]` em Slave Nodes); mestre (0) ligado ao ícone de cluster (1) | visual |
| | `Ap_cluster_config_nodes2.png` | A' | Cluster `worker`: **Number of nodes 2**, 1000.0, 1 núcleo, Bandwidth 100.0, Latency 0.001, Master desmarcado, scheduler `---`; Properties: 2 slaves; título com `[modified]` | visual |
| | `Bp_cluster_config_nodes4.png` | B' | Cluster `worker`: **Number of nodes 4**, mesmos parâmetros; Properties: 4 slaves; sem barra de título (o arquivo é identificado pelo valor 4) | visual |
| 5. Aba Resources A'/B' | `Ap_resources_gui.png` | A' | `worker node 1/2` 100.0 s; `link_ida` 16.400000000000105; `link_volta` 0.40390624999999813; `worker` (switch) 16.803906249999976 | texto conferido com o HTML oficial |
| | `Bp_resources_gui.png` | B' | `worker node 1–4` 50.0 s; mesmos links/switch (16.400000000000105; 0.40390624999999813; 16.803906249999983) | texto conferido com o HTML oficial |

O que o conjunto **demonstra:** os quatro modelos abrem na GUI; os parâmetros do mestre (A/B) e do cluster (A'/B': nodes, potência, núcleos, banda, latência) são os do modelo; os tempos de A/B e os recursos de
processamento e comunicação de A, B, A' e B' coincidem com os HTMLs oficiais.
O que **não** está capturado ou comprovado visualmente:
- **Aba Global, Tasks e Users de A' e B'** (portanto os tempos 100,125 s e 50,207 s **não** foram vistos na GUI); Tasks e Users também não de A/B.
- O erro do parser exibido ao simular A' (abaixo) **não tem captura**; em B' não se sabe se ocorreu.
- A'/B' mostram **um único ícone de cluster**: os workers individuais e o switch só aparecem como linhas da tabela Resources (`worker node k`, `worker`); os dois links (ida/volta) aparecem sobrepostos no desenho.
- As janelas de Resources não têm título; o cenário é identificado pelo conteúdo (nº de workers e nomes dos links) e pelo registro do usuário.
- Os parâmetros do cluster (potência, banda, latência) de A'/B' foram vistos no painel; o *Scheduling algorithm* do cluster aparece como `---`.

### Observações da GUI para A'/B' (investigação no código-fonte do iSPD; detalhes em `docs/auditoria_metodologica.md`, seção 6.5)
- **Erro do parser ao simular A'** ("Erros Encontrados durante o parser do Modelo Simulavel: Erro semantico … linha 8, coluna 19 / coluna 25 / coluna 25"): a GUI converte o modelo para um texto
  "simulável" (`modelosimulavel`) e o valida com um parser antigo. Para um cluster **não mestre** o conversor escreve o algoritmo como `---` (padrão de `Cluster.schedulingAlgorithm`), mas a gramática exige ali um nome
  (token começando por letra); a linha 8 gerada foi `CS_1 worker 2 2 --- FILAS …` e as colunas 19 e 25 são o fim de `---` e de `FILAS`.
  A simulação continuou porque o resultado desse parser é **descartado**: `SimulationDialog` monta a rede a partir do XML (`IconicoXML.newRedeDeFilas`), o mesmo caminho do terminal.
  Leitura: **incompatibilidade do conversor/validador da GUI com clusters não mestres**, não problema de configuração segundo o motor; os recursos simulados coincidem com os do HTML oficial.
  Não verificado: se B' gera o mesmo aviso (mesmo código) e se A/B não geram aviso (não reportado, não capturado).
- **`[modified]`:** `MainWindow.modificar()` marca o modelo como alterado em memória e é chamado, entre outros, ao adicionar um ícone (`DesenhoGrade.adicionarVertice`). As capturas de A' e B' mostram a notificação
  "Cluster icon added.", compatível com um clique na área de desenho com a ferramenta Cluster ativa. As propriedades do ícone selecionado (id 1, x 300, y 400, nodes 2/4, 1000, 100, 0.001) e a aba Resources
  coincidem com o modelo/HTML oficial, e os `.imsx` em disco permanecem inalterados (não foram salvos). **Não se pode excluir** um ícone adicional em memória que não apareça nas capturas. Em A, `[modified]` aparece em
  `A_gui_sem_selecao.png` sem a notificação de ícone adicionado (causa não identificada).

## Sensibilidade A'/B' (capacidade de rede agregada constante)
Motivo: em A/B a capacidade agregada de rede dobra junto com os workers (ver "Auditoria"). A'/B' usa o **mesmo trace** e os mesmos parâmetros, mas os
workers ficam atrás de **um único switch compartilhado** (ícone `cluster` não-mestre, `CS_Switch`, um servidor FIFO único) ligado ao mestre por
**um par de links de tronco**; variando só `nodes` (2 e 4), a capacidade de comunicação não depende de N.
Um cluster com `master=true` foi tentado primeiro e **rejeitado** por `IconicoXML.validarModelo` ("One or more parameters have not been configured",
pois só `<machine>` com `<master>` conta como mestre); por isso o mestre é uma `<machine>` (registro em `resultados/tentativa_descartada_cluster_mestre/`).

| Cenário | Tempo total simulado (HTML, s) | Redução A→B / A'→B' (derivada) |
|---|---|---|
| A (2 workers, links dedicados) | 100,042009765625 | 49,979 % (speedup 1,9992×) |
| B (4 workers, links dedicados) | 50,042009765625 | |
| A' (2 workers, switch compartilhado) | 100,12501953125 | 49,856 % (speedup 1,9942×) |
| B' (4 workers, switch compartilhado) | 50,20701953125 | |

Com rede compartilhada, a transmissão total é igual nos dois cenários (link de ida 16,4 s; switch 16,8039 s) e a fila média de comunicação fica quase
igual (8,22 s × 8,27 s), em vez de cair de 4,08 s para 2,03 s. A conclusão qualitativa se mantém; a diferença na redução é de 0,12 ponto percentual.
Diferenças de desenho de A'/B' em relação a A/B: dois saltos em série (link de ida + switch) e 2 ms de latência por sentido; o trecho extra de ~0,08 s e o
escalonamento da chegada da primeira tarefa de cada worker explicam os +0,083 s (A') e +0,165 s (B') sobre A/B. Os tempos de A'/B' são reproduzidos por
T = 0,082 + (N−1)·0,041 + 0,5·400/N + 0,00201953125 (derivada; ver `resultados/comparacao_sensibilidade.md`). O CSV de tarefas por worker de A'/B' mostra
`worker=400` porque o cluster nomeia todos os workers igual; a distribuição (200 por worker em A', 100 em B') foi obtida pelos segundos de processamento do
HTML (100,0 s e 50,0 s ÷ 0,5 s/tarefa). O iSPD imprime um aviso do DTD (`energy` não declarado para `cluster`) que não impede a simulação.
A'/B' foram **abertos e simulados na GUI pelo usuário** (ver seção "Execução pela interface gráfica"); só a aba Resources foi capturada e coincide com o HTML oficial; Global/Tasks/Users de A'/B' **não** foram capturados.

## Auditoria metodológica (resumo; detalhes em `docs/auditoria_metodologica.md`)
- Os tempos de A/B são exatamente reproduzidos por 0,042009765625 + 0,5·400/N (ida 0,041 s da 1ª tarefa + retorno 0,001009765625 s da última); a
  coincidência GUI × terminal usa o mesmo motor e não é validação independente da modelagem.
- **Problema de controle:** a capacidade agregada de rede dobra de A para B; efeito pequeno no tempo total (rede < 8,2 % de ocupação por link), mas a premissa
  "só os workers mudam" exige ressalva. A'/B' foi simulado para quantificar isso (acima).
- **Não usar** `Efficiency`, `Satisfaction` e `Processing average time` (ver Limitações).
- Reprodutibilidade (achados da auditoria): os scripts originais tinham caminhos absolutos (iSPD, JDK 17, jars do cache Gradle), exigiam o iSPD já compilado e **regeravam**
  `modelos/` e `trace/` a cada execução; `scripts/comparar.py` exige Python 3. **Tratado na etapa de correções** (seção "Como reproduzir em outro computador"): caminhos por
  parâmetro/variável de ambiente, geração separada da execução, sem sobrescrita por padrão. Permanecem as dependências listadas naquela seção. O código do iSPD usa recursos
  de Java ≥ 16; sem git, versão/commit do iSPD não registrados. Logs de console contêm tempo **real** de execução (não reprodutível bit a bit); só o tempo **simulado** é determinístico.

### Hashes registrados (SHA-256, calculados em 2026-11-12)
| Arquivo | SHA-256 |
|---|---|
| `trace/carga_citizentech_400.trace` | `6636bdcbbf671fc4282b6e9714adeba3cc0b40932a4e7130a05c0d13b8aa3ee6` |
| `modelos/cenario_A_2_workers.imsx` | `ffc8a175fb25e88dfa6a994dd5cd9c5178c1c7fc9e9a253b6efd93368cc88f1a` |
| `modelos/cenario_B_4_workers.imsx` | `e02b451ac6481c18469b31d3b838b979cf2104e93fa0e968de7037e51dd875eb` |
| `modelos/cenario_Ap_2_workers_switch.imsx` | `4b84688985b2eeb17cc04b0e4b37c6d24e14e506bf521b77a807fcc9e875c1e6` |
| `modelos/cenario_Bp_4_workers_switch.imsx` | `9d5dbcc43f3626fec034e03129a416aec290974aa337014b6a713acb6bb27e43` |

Os hashes de A, B e do trace foram conferidos como iguais aos calculados **antes** da rodada A'/B' (após a abertura na GUI), o que mostra que essa rodada não os alterou.
Não existe hash anterior à abertura dos modelos na GUI.

### Pendências
- **Capturas já feitas:** aba Resources de A, B, A' e B' (ver inventário das 13 evidências). **Ainda sem captura:** aba Global/Tasks/Users de A' e B'; o erro do parser em A'; qualquer aviso em B'.
- `[modified]` nas capturas de A e A' (e a notificação "Cluster icon added." em A' e B'): os `.imsx` em disco estão inalterados (hash), mas uma alteração **em memória** na GUI não pode ser totalmente excluída (ver "Observações da GUI").
- **Validação de reprodutibilidade (concluída em ambiente único):** `docs/validacao_reprodutibilidade.md` (testes isolados e defeitos encontrados) e `docs/validacao_ponta_a_ponta.md` (gerar → verificar → simular → comparar numa cópia isolada,
  reproduzindo os 4 tempos). Após esses testes, o texto "NÃO testado: o caminho de execução…" na seção "Como reproduzir" e "preparado, NÃO executado" na seção "RoundRobin" **estão desatualizados**: ambos foram exercitados
  na cópia (o detalhe por tarefa foi gerado e repetiu-se idêntico em duas execuções). Os registros desses testes estão nos documentos citados.
- **Ainda pendente:** teste em outro computador/SO/JDK/PowerShell; registro de versão/commit do iSPD; ordem de despacho do RoundRobin só **inferida** (não há log do escalonador).
- **Esta documentação não deve ser considerada final**, nem a entrega, até que as pendências acima sejam resolvidas ou aceitas como limitações.
