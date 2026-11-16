# Validação de reprodutibilidade dos scripts atualizados (2026-11-12)

Todos os testes de geração e execução foram feitos **somente em uma cópia isolada** do projeto. A raiz original (`D:\Downloads\GS\CLUSTER`) foi apenas **lida** (cópia e comparações) e,
ao final, recebeu apenas este relatório. Valores abaixo vêm de arquivos e saídas reais desta sessão; "derivado" indica cálculo próprio.

## 1. Resultado em uma linha
- **Critérios de aprovação:** (a) os 4 tempos simulados coincidiram — **atendido**; (b) o trace manteve o mesmo hash — **atendido**; (c) originais intactos — **atendido**.
- **Falha encontrada (não corrigida, conforme instrução):** `scripts\gerar_modelos.ps1 -Regenerar` **não regenera** (item 4.1). Para prosseguir com isolamento, a regeneração foi feita por
  **contorno** (chamada direta ao gerador Java). Portanto a validação "ponta a ponta apenas pelos scripts" **não está completa**; a decisão sobre aprovar fica com você.

## 2. Ambiente
| Item | Valor identificado |
|---|---|
| Sistema | Windows 11 Pro 10.0.26200 |
| PowerShell | 5.1.26100.9818 (Windows PowerShell) |
| Java / javac | OpenJDK Temurin 17.0.21+9 / javac 17.0.21 (`ISPD_JDK_HOME` = `C:\Users\henry\AppData\Local\Programs\Eclipse Adoptium\jdk-17.0.21.9-hotspot`) |
| iSPD | `D:\Downloads\ispd-main\ispd-main` (compartilhado, somente leitura); `ispd.Main -v` imprime "iSPD version 3.1"; commit **não registrado** (sem git) |
| Build do iSPD | Gradle wrapper 7.4 (`gradle-7.4-bin.zip`); `build\classes` de 2026-11-12 16:28:26, posterior ao fonte mais recente (16:09:08); `build.gradle` sem toolchain |
| Dependências | 6 jars achados no cache do Gradle do usuário: commons-cli 1.4, jfreechart 1.0.14, jcommon 1.0.17, itext 2.1.5, bcmail-jdk14 138, bcprov-jdk14 138 |
| Python | 3.14.4 (só biblioteca padrão) |
| Cópia isolada | `C:\Users\henry\AppData\Local\Temp\claude\722b5e6b8057a6a1\347fe82f-5e08-45fd-8912-d044b4e3378e\scratchpad\copia_cluster` (75 arquivos, SHA-256 idêntico à origem no momento da cópia) |

## 3. Proteção dos originais
- Manifesto SHA-256 da raiz original antes de começar: 75 arquivos. Cópia completa feita com `robocopy /E`; verificada idêntica (hash a hash).
- Na cópia, `resultados\` foi renomeada para `resultados_originais_copiados\` e recriada vazia, para que os scripts partissem de resultados inexistentes (o padrão sem sobrescrita foi testado antes dessa troca).
- `-SobrescreverResultados` foi usado **somente na cópia**.

## 4. Testes e resultados
Variáveis de ambiente usadas nos testes: `ISPD_DIR=D:\Downloads\ispd-main\ispd-main`, `ISPD_JDK_HOME=<JDK 17 acima>`. Scripts chamados com `powershell -NoProfile -ExecutionPolicy Bypass -File <COPIA>\scripts\...`.

| # | Teste | Comando (na cópia) | Resultado |
|---|---|---|---|
| 1 | Recusa de sobrescrita com resultados existentes | `executar.ps1 -Verificar` | **OK** — recusou: "Resultados ja existem: …\resultados\A_2_workers. Nada foi executado." |
| 2 | Pré-requisitos | `executar.ps1 -Verificar` e `executar_sensibilidade.ps1 -Verificar` (sem resultados) | **OK** — "VERIFICACAO OK (Java 17)" nos dois; JDK 17, pasta do iSPD, `build\classes` e os 6 jars resolvidos |
| 3a | Geração sem `-Regenerar` | `gerar_modelos.ps1` | **OK** — os 5 arquivos (trace + 4 modelos) "MANTIDO"; hashes inalterados |
| 3b | Geração com `-Regenerar` | `gerar_modelos.ps1 -Regenerar` | **FALHA** — todos os arquivos "MANTIDO" (nada reescrito); ver 5.1 |
| 3c | Geração por contorno | `java -cp driver\out;<classpath iSPD> GerarModelos <COPIA> --regenerar` e `GerarModelosCluster <COPIA> --regenerar` | **OK** — 5 arquivos "REESCRITO" |
| 3d | Conteúdo do que foi gerado (3c) | script de verificação em Python (leitura) | **OK** — ver abaixo |
| 4a | Executar A e B | `executar.ps1` | **OK** — exit 0 |
| 4b | Executar A' e B' | `executar_sensibilidade.ps1` | **OK** — exit 0 (avisos de DTD esperados, ver 5.3) |
| 5 | Comparação com os originais | `compara_resultados.py`; `comparar.py`; `comparar_sensibilidade.py` | **OK** — ver abaixo |
| 6 | Detalhe por tarefa | `executar.ps1 -DetalheTarefas -SobrescreverResultados` e `executar_sensibilidade.ps1 -DetalheTarefas -SobrescreverResultados` | **OK** — arquivos produzidos; ver seção 6 |

### 4.1 Verificação da geração (3d, após o contorno)
- **Trace:** 400 linhas de tarefa, 400 ids únicos (1–400), todas exatamente `arr="0.0" sts="1" cpsz ="500.0" cmsz="4.0" usr="user1"` (500 MFLOP; 4 Mbit = 0,5 MB).
  SHA-256 da cópia = `6636bdcbbf671fc4282b6e9714adeba3cc0b40932a4e7130a05c0d13b8aa3ee6` = hash do original (**IGUAL**).
- **Modelos:** os 4 são **idênticos aos originais exceto o atributo `file_path`**, que agora aponta para o trace **da cópia** (verificado nos 4).
- **Parâmetros lidos dos XMLs:** A: mestre + 2 workers, 4 links; B: mestre + 4 workers, 8 links; mestre e workers 1000 MFLOPS, 1 núcleo; `RoundRobin` no mestre; todos os links 100 Mbps, latência 0,001, load 0.
  A'/B': mestre `RoundRobin` + 1 cluster (`nodes`=2 / 4, 1000 MFLOPS, 100 Mbps, 0,001) e 2 links de tronco (100 Mbps, 0,001); `<trace tasks="400" format="iSPD">` em todos.

### 4.2 Comparação dos tempos simulados (HTML `Total Simulated Time`)
| Cenário | Esperado | Reproduzido (cópia) | Original (HTML) | Coincide |
|---|---:|---:|---:|---|
| A | 100,042009765625 s | 100,042009765625 s | 100,042009765625 s | sim |
| B | 50,042009765625 s | 50,042009765625 s | 50,042009765625 s | sim |
| A' | 100,12501953125 s | 100,12501953125 s | 100,12501953125 s | sim |
| B' | 50,20701953125 s | 50,20701953125 s | 50,20701953125 s | sim |

Além do tempo, nos 4 cenários: `result.html` **byte a byte idêntico** (SHA-256) ao original; `tarefas_por_worker.csv` idêntico; as 7 imagens da pasta `html` de cada cenário idênticas;
linhas globais do console (Total Simulated Time, Idleness…, Efficiency, Satisfaction) iguais; `comparacao.md` e `comparacao_sensibilidade.md` regenerados na cópia são idênticos aos originais.
Contagens (CSV): A 200/200; B 100×4; A' e B' `worker=400` (agregado, limitação conhecida). Tempo de processamento por worker no HTML: 100,0 s (A, A') e 50,0 s (B, B').
**Não** foi comparado o tempo real de execução (a execução levou ~9 s e ~7 s de relógio; irrelevante para o tempo simulado).

## 5. Problemas encontrados
1. **`gerar_modelos.ps1 -Regenerar` não funciona (defeito do script, não corrigido).** Causa confirmada com teste isolado: `$extra = if ($Regenerar) { @('--regenerar') } else { @() }` faz o PowerShell 5.1
   desenrolar o array de 1 elemento para **string**; ao fazer `@extra` na chamada nativa, a string é dividida em caracteres e o Java recebe `-`, `-`, `r`, `e`… em vez de `--regenerar`, então `args[1]` não é reconhecido e tudo é "MANTIDO".
   Efeito: sem erro e sem aviso, nada é regenerado; o README orienta justamente `-Regenerar` para outro computador. O caminho **sem** `-Regenerar` está correto.
2. **`-Verificar` não detecta modelo apontando para trace de outro projeto.** Na cópia recém-feita os `.imsx` referenciavam o trace da **raiz original** (`D:\Downloads\GS\CLUSTER\trace\…`), e `-Verificar` deu OK porque o arquivo existe nesta máquina.
   Rodar as simulações nesse estado leria o trace da pasta original (somente leitura). Isso foi evitado regenerando os modelos na cópia (contorno 3c) antes de simular. O README já avisa que o `.imsx` guarda caminho absoluto, mas o script não compara com a raiz atual.
3. **Avisos de DTD em A'/B'** (stderr): "Attribute "energy" must be declared for element type "cluster"" — conhecido, não impede a simulação; aparece nos logs e na saída do script.
4. **`worker_num` e `worker_id` no detalhe:** em A/B `worker_num` é sempre 0 (o `worker_id` distingue os workers); em A'/B' `worker_id` é sempre `worker` e `worker_num` (1..N) distingue.

## 6. Detalhe por tarefa (3º argumento de `SimularModelo`)
Produzido em `resultados\<cenário>\tarefas_detalhe.csv` pela cópia: 400 linhas + cabeçalho nos 4 cenários, 400 ids únicos, as 400 tarefas com estado concluído (4).
Os tempos e os HTMLs continuaram idênticos aos originais depois dessas execuções (`-DetalheTarefas` não altera o resultado). Rodando duas vezes, os 4 arquivos de detalhe saíram **idênticos** (hash).

O que os dados **demonstram**:
- **Distribuição por worker:** A 200/200; B 100×4; A' 200/200 (`worker_num` 1–2); B' 100×4 (`worker_num` 1–4) — contagem direta por tarefa, o que também confirma a divisão por segundos de processamento usada antes para A'/B'.
- **A atribuição não segue a ordem dos ids:** por exemplo, em A, a tarefa 2 foi para `worker1`, a 3 e a 4 para `worker2`, a 5 e a 6 para `worker1`. Ids com worker igual a `(id−1) mod N`: A 354/400, B 153/400, A' 8/400, B' 4/400 (derivado). Isso é compatível com o apontado no README: o motor não garante a ordem entre eventos empatados em t=0.
- **Ordem de despacho (apenas inferência, em A/B):** a espera em fila de comunicação de cada tarefa é múltipla de 0,041 s e, dentro de cada worker, os postos (espera ÷ 0,041) são únicos de 0 a n−1 (verificado). **Sob a suposição** de que o RoundRobin alterna os workers na ordem do modelo, isso reconstrói
  uma ordem de despacho que é permutação dos 400 ids (início inferido: 1, 400, 399, 398, 2, 4…). É uma **inferência**, não um log de decisões do escalonador.

O que **não** se pode afirmar: uma ordem determinística garantida pelo motor. O que foi observado é **reprodutível nesta máquina/JDK/iSPD** (duas execuções idênticas); reprodutibilidade em outra versão do Java, do iSPD ou outro sistema **não foi verificada**.

## 7. Integridade da raiz original
- Manifesto SHA-256 (todos os arquivos, incluindo `driver\out`) antes e depois dos testes: **75 arquivos, 0 diferenças**; datas de modificação dos `.imsx` e do trace inalteradas
  (A/B/trace 16:52:31; A'/B' 17:34:26). Hashes dos modelos e do trace: iguais aos registrados no README.
- Único arquivo acrescentado à raiz original: este `docs/validacao_reprodutibilidade.md` (conferido em verificação posterior à gravação do relatório; ver mensagem final da sessão).

## 8. Limitações que permaneceram (não testadas / não resolvidas)
- Apenas Windows 11, PowerShell 5.1, JDK 17.0.21, `build\classes` do Gradle 7.4 e a **mesma** pasta do iSPD e cache do Gradle. **Não testado:** outro computador, Linux/macOS, PowerShell 7, outro JDK (inclusive o teste negativo com JDK 8 real),
  build do iSPD do zero (internet/Gradle), caminho relativo no `file_path`.
- Os drivers dependem de classes internas do iSPD; a descoberta dos jars depende do layout do cache do Gradle; versão/commit do iSPD não registrados.
- `-Regenerar` via script está quebrado (5.1); `-Verificar` não valida a localização do trace (5.2).
- A'/B' continuam **não validados na GUI**; capturas da aba Resources continuam pendentes.
- Os logs `console_*.txt` contêm tempo real e dependem de codificação; só o tempo simulado e o HTML foram comparados.

## 9. Conclusão
Os quatro tempos simulados, o hash do trace, os HTMLs, os CSVs e as imagens foram **reproduzidos exatamente** na cópia, usando `executar.ps1` e `executar_sensibilidade.ps1`, sem alterar os originais.
A etapa de **geração** só foi concluída com um contorno, por causa do defeito em `gerar_modelos.ps1 -Regenerar`. Nenhuma correção foi aplicada; aguardo sua avaliação.
