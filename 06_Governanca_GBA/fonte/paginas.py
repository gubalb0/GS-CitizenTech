"""Lê o PDF renderizado e devolve a página (numeração ABNT) de cada título, figura e quadro.
Uso: python paginas.py relatorio.pdf relatorio.chaves.json paginas.json"""
import json, re, subprocess, sys

pdf, chaves_json, saida = sys.argv[1:4]
chaves = json.load(open(chaves_json))
n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
norm = lambda t: re.sub(r"\s+", " ", t).strip()
textos = {p: norm(subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", pdf, "-"],
                                 capture_output=True, text=True).stdout) for p in range(1, n + 1)}
PRIMEIRA_TEXTUAL = 5  # capa, rosto, listas, sumário
res, faltando = {}, []
for chave in chaves["titulos"] + chaves["figuras"] + chaves["quadros"]:
    alvo = norm(chave)[:60]
    pag = next((p for p in range(PRIMEIRA_TEXTUAL, n + 1) if alvo in textos[p]), None)
    if pag is None:
        faltando.append(chave)
    else:
        res[chave] = pag - 1  # a capa não é contada
json.dump(res, open(saida, "w"), ensure_ascii=False, indent=1)
print(f"{len(res)} encontrados, {n} páginas no PDF", "| faltando:", faltando)
