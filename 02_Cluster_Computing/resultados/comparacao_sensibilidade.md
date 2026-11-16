# Sensibilidade: links dedicados (A/B) x switch compartilhado (A'/B')

Valores nativos extraidos dos `result.html` do iSPD; reducao/speedup sao **derivados**.

| Cenario | Tempo total simulado (s) | Fila media de comunicacao (s) | Ociosidade proc. (%) | Ociosidade comun. (%) | Proc. por worker (s) |
|---|---|---|---|---|---|
| A (2 w, links dedicados) | 100.042009765625 | 4.0795 | 0.04199212483177369 | 95.80078751682225 | 100.0, 100.0 |
| B (4 w, links dedicados) | 50.042009765625 | 2.0295 | 0.08394899769564 | 95.80255011521766 | 50.0, 50.0, 50.0, 50.0 |
| A' (2 w, switch compartilhado) | 100.12501953125 | 8.2197 | 0.1248634275781431 | 88.81138378887381 | 100.0, 100.0 |
| B' (4 w, switch compartilhado) | 50.20701953125 | 8.2698 | 0.41233184758387004 | 77.68717547614246 | 50.0, 50.0, 50.0, 50.0 |

## Tempo de comunicacao por recurso (segundos de transmissao, HTML)

- A (2 w, links dedicados): link_ida_w2 = 8.2; link_ida_w1 = 8.2; link_volta_w2 = 0.201953; link_volta_w1 = 0.201953
- B (4 w, links dedicados): link_ida_w4 = 4.1; link_ida_w3 = 4.1; link_ida_w2 = 4.1; link_ida_w1 = 4.1; link_volta_w2 = 0.100977; link_volta_w1 = 0.100977; link_volta_w4 = 0.100977; link_volta_w3 = 0.100977
- A' (2 w, switch compartilhado): link_ida = 16.4; link_volta = 0.403906; worker = 16.8039
- B' (4 w, switch compartilhado): link_ida = 16.4; link_volta = 0.403906; worker = 16.8039

## Derivados

- links dedicados (A -> B): reducao = (100.042009765625 - 50.042009765625) / 100.042009765625 = **49.979 %**; speedup = **1.9992x**
- switch compartilhado (A' -> B'): reducao = (100.12501953125 - 50.20701953125) / 100.12501953125 = **49.856 %**; speedup = **1.9942x**

## Reconciliacao analitica (derivada, nao usada como resultado)
- Links dedicados: T = 0,041 + 0,5 x 400/N + 0,001009765625.
- Switch compartilhado (2 saltos em serie: link_ida + switch): primeira tarefa do ultimo worker chega em 0,082 + (N-1) x 0,041 s; retorno = 2 x 0,001009765625 s; T = 0,082 + (N-1) x 0,041 + 0,5 x 400/N + 0,00201953125.
  - N=2: 100.12501953125  (HTML: 100.12501953125)
  - N=4: 50.20701953125  (HTML: 50.20701953125)
