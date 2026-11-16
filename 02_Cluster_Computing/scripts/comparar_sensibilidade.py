"""Compara A/B (links dedicados por worker) com A'/B' (switch compartilhado) lendo os HTMLs do iSPD.
Valores nativos vem dos HTMLs; derivados (reducao, speedup, reconciliacao) sao calculados aqui e rotulados."""
import re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
R = root / "resultados"


def ler(d):
    h = (R / d / "html" / "result.html").read_text(encoding="utf-8")
    t = float(re.search(r"Total Simulated Time\s*</strong>\s*=\s*([\d.]+)", h).group(1))
    rows = re.findall(r"<tr><td>([^<]*)</td><td>[^<]*</td><td>([\d.]+)</td><td>([\d.]+)</td></tr>", h)
    workers = [(n, float(p)) for n, p, c in rows if n.startswith("worker") and float(p) > 0]
    comm = [(n, float(c)) for n, p, c in rows if float(c) > 0]
    q = float(re.search(r"Queue average time:\s*([\d.]+)", h).group(1))  # 1a ocorrencia = fila de comunicacao
    idle = re.findall(r"Idleness of (processing|communication) resources\s*</strong>\s*=\s*([\d.]+)", h)
    return dict(t=t, workers=workers, comm=comm, q=q, idle=dict(idle))


D = {"A (2 w, links dedicados)": "A_2_workers", "B (4 w, links dedicados)": "B_4_workers",
     "A' (2 w, switch compartilhado)": "Ap_2_workers_switch", "B' (4 w, switch compartilhado)": "Bp_4_workers_switch"}
res = {k: ler(v) for k, v in D.items()}
ks = list(res)
L = ["# Sensibilidade: links dedicados (A/B) x switch compartilhado (A'/B')",
     "", "Valores nativos extraidos dos `result.html` do iSPD; reducao/speedup sao **derivados**.", "",
     "| Cenario | Tempo total simulado (s) | Fila media de comunicacao (s) | Ociosidade proc. (%) | Ociosidade comun. (%) | Proc. por worker (s) |",
     "|---|---|---|---|---|---|"]
for k in ks:
    r = res[k]
    L.append(f"| {k} | {r['t']} | {r['q']:.4f} | {r['idle'].get('processing')} | {r['idle'].get('communication')} | "
             f"{', '.join(str(p) for _, p in r['workers'])} |")
L += ["", "## Tempo de comunicacao por recurso (segundos de transmissao, HTML)", ""]
for k in ks:
    L.append(f"- {k}: " + "; ".join(f"{n} = {c:.6g}" for n, c in res[k]["comm"]))
L += ["", "## Derivados", ""]
for a, b, nome in [(ks[0], ks[1], "links dedicados (A -> B)"), (ks[2], ks[3], "switch compartilhado (A' -> B')")]:
    ta, tb = res[a]["t"], res[b]["t"]
    L.append(f"- {nome}: reducao = ({ta} - {tb}) / {ta} = **{(ta - tb) / ta * 100:.3f} %**; speedup = **{ta / tb:.4f}x**")
L += ["", "## Reconciliacao analitica (derivada, nao usada como resultado)",
      "- Links dedicados: T = 0,041 + 0,5 x 400/N + 0,001009765625.",
      "- Switch compartilhado (2 saltos em serie: link_ida + switch): primeira tarefa do ultimo worker chega em "
      "0,082 + (N-1) x 0,041 s; retorno = 2 x 0,001009765625 s; T = 0,082 + (N-1) x 0,041 + 0,5 x 400/N + 0,00201953125.",
      f"  - N=2: {0.082 + 1*0.041 + 100 + 0.00201953125:.11f}  (HTML: {res[ks[2]]['t']})",
      f"  - N=4: {0.082 + 3*0.041 + 50 + 0.00201953125:.11f}  (HTML: {res[ks[3]]['t']})"]
(R / "comparacao_sensibilidade.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
