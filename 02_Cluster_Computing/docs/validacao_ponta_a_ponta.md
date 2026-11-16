# Validação ponta a ponta da reprodutibilidade (2026-11-12)

Fluxo completo (gerar → verificar → simular → comparar) executado **somente em uma cópia isolada nova**, com os scripts corrigidos, **sem alterar scripts, parâmetros, modelos, traces ou resultados**.
A raiz original foi apenas lida (cópia e hashes) e recebeu, além do que já existia, **somente este relatório**.

## 1. Resultado
**Aprovada neste ambiente:** todas as etapas foram concluídas com sucesso, os quatro tempos simulados coincidiram com os valores de referência e a raiz original permaneceu intacta.
O alcance da aprovação está limitado ao ambiente descrito abaixo (ver seção 8).

## 2. Ambiente e pré-requisitos
| Item | Valor |
|---|---|
| Sistema | Microsoft Windows 11 Pro 10.0.26200 |
| PowerShell | 5.1.26100.9818 |
| JDK | OpenJDK Temurin 17.0.21+9 (`javac 17.0.21`), informado por `ISPD_JDK_HOME` |
| iSPD | `ispd.Main -v` → "iSPD version 3.1"; pasta `D:\Downloads\ispd-main\ispd-main` (`ISPD_DIR`), compartilhada e só lida; commit **não registrado**; `build\classes` de 2026-11-12 16:28:26 |
| Gradle | wrapper 7.4 (`gradle-7.4-bin.zip`); jars (commons-cli 1.4, jfreechart 1.0.14, jcommon 1.0.17, itext 2.1.5, bcmail/bcprov-jdk14 138) achados pelo script no cache do Gradle do usuário |
| Python | 3.14.4 (só biblioteca padrão) |
| Cópia de teste | `C:\Users\henry\AppData\Local\Temp\claude\722b5e6b8057a6a1\347fe82f-5e08-45fd-8912-d044b4e3378e\scratchpad\e2e_copia` |

Preparação: manifesto SHA-256 da raiz original (76 arquivos); cópia completa com `robocopy /E`, verificada idêntica hash a hash (76 arquivos); presença conferida de `scripts\*`, `driver\*.java` e do trace.
A cópia já trazia resultados anteriores; por isso `-SobrescreverResultados` foi usado **só nela**.

## 3. Comandos executados (todos na cópia; `ISPD_DIR` e `ISPD_JDK_HOME` definidos; chamados com `powershell -NoProfile -ExecutionPolicy Bypass -File <COPIA>\scripts\…`)
```powershell
.\scripts\gerar_modelos.ps1 -Regenerar
.\scripts\executar.ps1 -Verificar -SobrescreverResultados
.\scripts\executar_sensibilidade.ps1 -Verificar -SobrescreverResultados
.\scripts\executar.ps1 -SobrescreverResultados
.\scripts\executar_sensibilidade.ps1 -SobrescreverResultados
python scripts\comparar.py
```
**Desvio em relação ao roteiro solicitado:** `executar.ps1 -Verificar` foi rodado **com** `-SobrescreverResultados` (e o equivalente para a sensibilidade), porque a cópia contém resultados e, sem a opção, os scripts **recusam por projeto** ("Resultados ja existem") — comportamento já validado antes e não repetido aqui.

## 4. Resultado de cada etapa
| # | Etapa | Resultado |
|---|---|---|
| 1 | Preparação (manifesto, cópia, ambiente) | **OK** |
| 2 | `gerar_modelos.ps1 -Regenerar` | **OK** — exit 0; 5 arquivos "REESCRITO" (trace + 4 modelos); 0 ocorrências de "MANTIDO"; data de modificação alterada nos 5 |
| 2a | Modelos apontam para o trace da própria cópia | **OK** — os 4 `file_path` iguais a `<COPIA>\trace\carga_citizentech_400.trace` |
| 2b | Trace | **OK** — 400 linhas de tarefa, 400 ids únicos, todas `arr="0.0" cpsz ="500.0" cmsz="4.0"` (500 MFLOP; 4 Mbit); SHA-256 `6636bdcbbf671fc4282b6e9714adeba3cc0b40932a4e7130a05c0d13b8aa3ee6` **igual ao original** |
| 2c | Modelos | **OK** — iguais aos originais exceto o `file_path`; parâmetros lidos dos XML: 1000 MFLOPS, 1 núcleo, `RoundRobin`, links 100 Mbps / 0,001 s / load 0; A: 4 links; B: 8 links; A'/B': cluster com `nodes` 2 e 4 + 2 links de tronco |
| 3a | `executar.ps1 -Verificar -SobrescreverResultados` | **OK** — "VERIFICACAO OK (Java 17)"; pré-requisitos e validação do caminho do trace aprovados |
| 3b | `executar_sensibilidade.ps1 -Verificar -SobrescreverResultados` | **OK** — idem |
| 3c | `executar.ps1 -SobrescreverResultados` (A e B) | **OK** — exit 0 |
| 3d | `executar_sensibilidade.ps1 -SobrescreverResultados` (A' e B') | **OK** — exit 0 |
| 3e | Artefatos | **OK** — por cenário: `result.html`, 7 imagens, `tarefas_por_worker.csv`, `console_ispd.txt`, `console_driver.txt`; HTMLs gerados nesta rodada (20:32), não copiados |
| 4 | `python scripts\comparar.py` | **OK** — exit 0; `comparacao.md` gerado na cópia |

Logs: nenhuma exceção (`Exception`/`at ispd.`) em nenhum `console_*.txt` dos 4 cenários. Em A' e B' o aviso de DTD ("Attribute "energy" must be declared for element type "cluster"") aparece, como já documentado; não foi corrigido e não impediu a simulação.
Tempo real de execução (~8 s e ~7 s de relógio por script) não foi comparado e não tem relação com o tempo simulado.

## 5. Comparação dos tempos simulados (HTML `Total Simulated Time`, cópia × referência)
| Cenário | Referência | Regenerado | Coincide |
|---|---:|---:|---|
| A — 2 workers | 100,042009765625 s | 100,042009765625 s | sim |
| B — 4 workers | 50,042009765625 s | 50,042009765625 s | sim |
| A' — 2 workers, switch compartilhado | 100,12501953125 s | 100,12501953125 s | sim |
| B' — 4 workers, switch compartilhado | 50,20701953125 s | 50,20701953125 s | sim |

Verificações adicionais (script de conferência que lê os arquivos regenerados):
- **Tarefas:** 400 por cenário (soma do CSV).
- **Distribuição:** A 200/200 e B 100×4 (CSV, direto); A' 200/200 e B' 100×4 **derivados** dos segundos de processamento do HTML ÷ 0,5 s (o CSV de A'/B' agrega `worker=400`).
- **Tamanho computacional (derivado):** segundos de processamento × 1000 MFLOPS ÷ tarefas = 500,000000 MFLOP nos 4 cenários.
- **Comunicação (derivada):** transmissão de ida por tarefa = 0,041000 s → (0,041 − 0,001) × 100 = 4,000000 Mbit; retorno por tarefa = 0,001009766 s (arquivo fixo de 0,0009765625 Mbit do simulador).
- **Redução e speedup (derivados dos tempos do HTML):** A→B **49,979 %**, **1,9992×**; A'→B' **49,856 %**, **1,9942×**.
- **Coerência HTML × CSV × `comparacao.md`:** os 4 tempos, as 2 reduções e os 2 speedups aparecem em `comparacao.md`; o arquivo regenerado é idêntico ao `comparacao.md` original.
- **Resultados regenerados × originais (informativo, não exigido):** `result.html`, CSV e as 7 imagens de cada cenário são **idênticos byte a byte** (SHA-256) aos da raiz original.

## 6. Diferenças encontradas
Nenhuma divergência numérica ou de conteúdo nos artefatos comparados. Ocorrências do processo de teste:
- **Falso alarme do meu código de teste (não do projeto):** na primeira tentativa da etapa 3, uma função auxiliar devolveu texto misturado ao exit code e interrompeu o fluxo indevidamente; o log da etapa mostrava "VERIFICACAO OK". Corrigi **apenas o código de teste** e **reexecutei a etapa 3 desde o início**; os resultados acima são dessa reexecução. Nenhum script do projeto foi alterado.
- Desvio de comando em `-Verificar` (seção 3).

## 7. Integridade da raiz original
- Manifesto SHA-256 antes e depois (76 arquivos, todos os arquivos, inclusive `driver\out`): **0 diferenças** antes de gravar este relatório; datas dos `.imsx`/trace inalteradas (A/B/trace 16:52:31; A'/B' 17:34:26).
- Modelos, trace, HTMLs, CSVs, logs e capturas originais: não modificados. Único acréscimo à raiz original: `docs/validacao_ponta_a_ponta.md`.

## 8. Limitações que permanecem
- Um único ambiente: Windows 11, PowerShell 5.1, JDK 17.0.21, o **mesmo** `build\classes` do iSPD e o **mesmo** cache do Gradle. **Não testado:** outro computador, Linux/macOS, PowerShell 7, outro JDK, build do iSPD do zero (internet), caminho relativo do trace.
- Os drivers dependem de classes internas do iSPD; versão/commit do iSPD não registrados.
- O hash dos `.imsx` depende da pasta onde são gerados (caminho absoluto do trace).
- Aviso de DTD em A'/B' mantido; A'/B' continuam **sem validação na GUI**; capturas da aba Resources pendentes; ordem de atribuição do RoundRobin só registrada no teste anterior (detalhe por tarefa), não nesta rodada.
- Logs `console_*.txt` não foram comparados byte a byte (contêm tempo real de execução).
