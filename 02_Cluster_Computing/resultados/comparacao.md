# Comparação dos cenários A/B e análise de sensibilidade A'/B'

## Fontes dos dados
- **HTML** (`resultados/<cenario>/html/result.html`, exportado pelo iSPD): tempo total simulado, processamento por worker (segundos) e ociosidade de processamento nativa.
- **CSV** (`resultados/<cenario>/tarefas_por_worker.csv`, gerado por `driver/SimularModelo.java`, mesmo motor do iSPD): tarefas concluídas por recurso. **Não vem do HTML.** Em A'/B' o cluster nomeia todos os workers igual e o CSV agrega as 400 tarefas em `worker`.
- **Derivado**: calculado por este script a partir do HTML/CSV (redução percentual, speedup, fração do tempo em processamento, tarefas ÷ 0,5 s).
- Tempos são **tempo simulado** (segundos simulados), não tempo real de execução. Todos os parâmetros são hipóteses de simulação.

## Cenários A e B — links dedicados por worker (comparação principal)

| Cenário | Tempo total simulado (s) — HTML |
|---|---|
| A (2 workers) | 100.042009765625 |
| B (4 workers) | 50.042009765625 |

- Redução do tempo simulado (derivada): (100.042009765625 − 50.042009765625) / 100.042009765625 = **49.979 %**; speedup = **1.9992×**

## Cenários A' e B' — ANÁLISE DE SENSIBILIDADE (topologia de rede diferente)

A'/B' usa o **mesmo trace e os mesmos parâmetros**, mas a **topologia de rede é outra**: um par de links de tronco + **um switch compartilhado** (capacidade agregada de comunicação constante), com dois saltos em série e 2 ms de latência por sentido. **Não é uma repetição de A/B**; serve para quantificar o efeito de a capacidade agregada de rede dobrar em A/B. Na interface gráfica, A'/B' foram abertos e simulados pelo usuário; **só a aba Resources foi capturada** e coincide com o HTML oficial (Global/Tasks/Users de A'/B' não foram capturados). A GUI exibiu avisos do parser do "modelo simulável" para o cluster não mestre (`---`), sem efeito sobre a simulação (ver `docs/auditoria_metodologica.md`, 6.5).

| Cenário | Tempo total simulado (s) — HTML |
|---|---|
| A' (2 workers, switch compartilhado) | 100.12501953125 |
| B' (4 workers, switch compartilhado) | 50.20701953125 |

- Redução do tempo simulado (derivada): (100.12501953125 − 50.20701953125) / 100.12501953125 = **49.856 %**; speedup = **1.9942×**

## Por worker

A coluna final **não é uma métrica nativa do iSPD por worker**: é a **fração do tempo simulado em processamento (derivada)** = segundos de processamento do worker (HTML) ÷ tempo total simulado (HTML). Com `load` = 0, a média sobre os workers é igual a 100 % − *Idleness of processing resources* nativa (global). Não deve ser chamada de "utilização nativa".

| Cenário | Worker (HTML) | Tarefas concluídas (CSV) | Processamento (s) — HTML | Processamento ÷ 0,5 s (derivada) | Fração do tempo simulado em processamento (derivada, %) |
|---|---|---|---|---|---|
| A (2 workers) | worker1 | 200 | 100.0 | 200 | 99.958 |
| A (2 workers) | worker2 | 200 | 100.0 | 200 | 99.958 |
| B (4 workers) | worker1 | 100 | 50.0 | 100 | 99.916 |
| B (4 workers) | worker2 | 100 | 50.0 | 100 | 99.916 |
| B (4 workers) | worker3 | 100 | 50.0 | 100 | 99.916 |
| B (4 workers) | worker4 | 100 | 50.0 | 100 | 99.916 |
| A' (2 workers) | worker node 1 | agregado em `worker`: 400 | 100.0 | 200 | 99.875 |
| A' (2 workers) | worker node 2 | agregado em `worker`: 400 | 100.0 | 200 | 99.875 |
| B' (4 workers) | worker node 1 | agregado em `worker`: 400 | 50.0 | 100 | 99.588 |
| B' (4 workers) | worker node 2 | agregado em `worker`: 400 | 50.0 | 100 | 99.588 |
| B' (4 workers) | worker node 3 | agregado em `worker`: 400 | 50.0 | 100 | 99.588 |
| B' (4 workers) | worker node 4 | agregado em `worker`: 400 | 50.0 | 100 | 99.588 |

Ociosidade de processamento **nativa** (HTML, média sobre os workers): A (2 workers) = 0.04199212483177369 %; B (4 workers) = 0.08394899769564 %; A' (2 workers) = 0.1248634275781431 %; B' (4 workers) = 0.41233184758387004 %.

## Indicadores do iSPD que NÃO são usados como medida de desempenho
- **Efficiency**: pelo código (`MetricasTarefa.calcEficiencia`) é capacidade ÷ (tamanho × tempo de processamento) por tarefa, não normalizada e igual em todos os cenários; não mede a eficiência do cluster.
- **Satisfaction**: valor constante (100) no código; não carrega informação.
- **Processing average time** (seção Tasks do HTML): aparece como 0,0 s; pelo código parece defeito do simulador (não confirmado por experimento).
Detalhes e referências no código em `docs/auditoria_metodologica.md`.

