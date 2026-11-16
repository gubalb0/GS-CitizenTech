"""Gera resultados/comparacao.md a partir de arquivos de resultado JA existentes. Nao executa simulacao.

Requisitos: Python 3 (somente biblioteca padrao). Uso, a partir da raiz do projeto:
    python scripts/comparar.py

Fontes (declaradas no proprio relatorio):
  - HTML  : resultados/<cenario>/html/result.html  (tempo total simulado, processamento por worker, ociosidade nativa)
  - CSV   : resultados/<cenario>/tarefas_por_worker.csv (tarefas concluidas por recurso; gerado por driver/SimularModelo)
  - DERIVADO: calculado aqui a partir dos dois (rotulado como tal)
"""
import re, csv, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
R = root / "resultados"

CEN = [  # (rotulo, pasta, grupo)
    ("A (2 workers)", "A_2_workers", "AB"),
    ("B (4 workers)", "B_4_workers", "AB"),
    ("A' (2 workers)", "Ap_2_workers_switch", "ApBp"),
    ("B' (4 workers)", "Bp_4_workers_switch", "ApBp"),
]
TEMPO_POR_TAREFA = 0.5  # s = 500 MFLOP / 1000 MFLOPS (hipotese de simulacao)


def ler(pasta):
    h = (R / pasta / "html" / "result.html").read_text(encoding="utf-8")
    t = float(re.search(r"Total Simulated Time\s*</strong>\s*=\s*([\d.]+)", h).group(1))
    idle = float(re.search(r"Idleness of processing resources\s*</strong>\s*=\s*([\d.]+)", h).group(1))
    rows = re.findall(r"<tr><td>([^<]*)</td><td>[^<]*</td><td>([\d.]+)</td><td>[\d.]+</td></tr>", h)
    workers = sorted((n, float(p)) for n, p in rows if n.startswith("worker") and float(p) > 0)
    cnt = {}
    with open(R / pasta / "tarefas_por_worker.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            cnt[r["recurso"]] = int(r["tarefas_concluidas"])
    return dict(t=t, idle=idle, workers=workers, cnt=cnt)


res = {rot: ler(p) for rot, p, _ in CEN}
rA, rB, rAp, rBp = (res[c[0]] for c in CEN)


def red(a, b):
    return (a["t"] - b["t"]) / a["t"] * 100, a["t"] / b["t"]


L = []
L += ["# Comparação dos cenários A/B e análise de sensibilidade A'/B'", "",
      "## Fontes dos dados",
      "- **HTML** (`resultados/<cenario>/html/result.html`, exportado pelo iSPD): tempo total simulado, processamento por worker (segundos) e "
      "ociosidade de processamento nativa.",
      "- **CSV** (`resultados/<cenario>/tarefas_por_worker.csv`, gerado por `driver/SimularModelo.java`, mesmo motor do iSPD): tarefas concluídas por recurso. "
      "**Não vem do HTML.** Em A'/B' o cluster nomeia todos os workers igual e o CSV agrega as 400 tarefas em `worker`.",
      "- **Derivado**: calculado por este script a partir do HTML/CSV (redução percentual, speedup, fração do tempo em processamento, tarefas ÷ 0,5 s).",
      "- Tempos são **tempo simulado** (segundos simulados), não tempo real de execução. Todos os parâmetros são hipóteses de simulação.", ""]

L += ["## Cenários A e B — links dedicados por worker (comparação principal)", "",
      "| Cenário | Tempo total simulado (s) — HTML |", "|---|---|",
      f"| A (2 workers) | {rA['t']} |", f"| B (4 workers) | {rB['t']} |", ""]
r, s = red(rA, rB)
L += [f"- Redução do tempo simulado (derivada): ({rA['t']} − {rB['t']}) / {rA['t']} = **{r:.3f} %**; speedup = **{s:.4f}×**", ""]

L += ["## Cenários A' e B' — ANÁLISE DE SENSIBILIDADE (topologia de rede diferente)", "",
      "A'/B' usa o **mesmo trace e os mesmos parâmetros**, mas a **topologia de rede é outra**: um par de links de tronco + **um switch compartilhado** "
      "(capacidade agregada de comunicação constante), com dois saltos em série e 2 ms de latência por sentido. **Não é uma repetição de A/B**; serve para "
      "quantificar o efeito de a capacidade agregada de rede dobrar em A/B. Na interface gráfica, A'/B' foram abertos e simulados pelo usuário; **só a aba Resources foi capturada** e coincide com o HTML oficial (Global/Tasks/Users de A'/B' não foram capturados). A GUI exibiu avisos do parser do \"modelo simulável\" para o cluster não mestre (`---`), sem efeito sobre a simulação (ver `docs/auditoria_metodologica.md`, 6.5).", "",
      "| Cenário | Tempo total simulado (s) — HTML |", "|---|---|",
      f"| A' (2 workers, switch compartilhado) | {rAp['t']} |", f"| B' (4 workers, switch compartilhado) | {rBp['t']} |", ""]
r, s = red(rAp, rBp)
L += [f"- Redução do tempo simulado (derivada): ({rAp['t']} − {rBp['t']}) / {rAp['t']} = **{r:.3f} %**; speedup = **{s:.4f}×**", ""]

L += ["## Por worker", "",
      "A coluna final **não é uma métrica nativa do iSPD por worker**: é a **fração do tempo simulado em processamento (derivada)** = segundos de "
      "processamento do worker (HTML) ÷ tempo total simulado (HTML). Com `load` = 0, a média sobre os workers é igual a 100 % − *Idleness of processing "
      "resources* nativa (global). Não deve ser chamada de \"utilização nativa\".", "",
      "| Cenário | Worker (HTML) | Tarefas concluídas (CSV) | Processamento (s) — HTML | Processamento ÷ 0,5 s (derivada) | Fração do tempo simulado em processamento (derivada, %) |",
      "|---|---|---|---|---|---|"]
for rot, _, _ in CEN:
    x = res[rot]
    for n, p in x["workers"]:
        csv_v = x["cnt"].get(n)
        csv_txt = str(csv_v) if csv_v is not None else f"agregado em `worker`: {x['cnt'].get('worker', 'n/d')}"
        L.append(f"| {rot} | {n} | {csv_txt} | {p} | {p / TEMPO_POR_TAREFA:.0f} | {p / x['t'] * 100:.3f} |")
L += ["", "Ociosidade de processamento **nativa** (HTML, média sobre os workers): " +
      "; ".join(f"{rot} = {res[rot]['idle']} %" for rot, _, _ in CEN) + ".", ""]

L += ["## Indicadores do iSPD que NÃO são usados como medida de desempenho",
      "- **Efficiency**: pelo código (`MetricasTarefa.calcEficiencia`) é capacidade ÷ (tamanho × tempo de processamento) por tarefa, não normalizada e igual em todos os "
      "cenários; não mede a eficiência do cluster.",
      "- **Satisfaction**: valor constante (100) no código; não carrega informação.",
      "- **Processing average time** (seção Tasks do HTML): aparece como 0,0 s; pelo código parece defeito do simulador (não confirmado por experimento).",
      "Detalhes e referências no código em `docs/auditoria_metodologica.md`.", ""]
(R / "comparacao.md").write_text("\n".join(L) + "\n", encoding="utf-8")
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consoles cp1252 nao codificam "−" e "÷"
print("\n".join(L))
