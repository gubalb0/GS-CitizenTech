"""
Passo 5 (opcional) — converte o relatório Markdown em PDF (markdown -> HTML -> PDF).

Uso:  python scripts/05_gerar_pdf.py
"""
import sys
from pathlib import Path

import markdown
from xhtml2pdf import pisa

RAIZ = Path(__file__).resolve().parents[1]
MD = RAIZ / "relatorio" / "relatorio.md"
PDF = RAIZ / "relatorio" / "relatorio.pdf"

ESTILO = """
<style>
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; color: #222; }
h1 { font-size: 17pt; border-bottom: 2px solid #333; padding-bottom: 4px; }
h2 { font-size: 13pt; color: #1a3b6e; margin-top: 14px; }
h3 { font-size: 11pt; color: #333; }
table { border-collapse: collapse; margin: 6px 0; }
th, td { border: 1px solid #888; padding: 3px 7px; font-size: 9.5pt; }
th { background: #e8eef7; }
code { background: #f0f0f0; font-family: Courier; font-size: 9pt; }
pre { background: #f5f5f5; border: 1px solid #ddd; padding: 6px; font-size: 8.5pt; }
hr { border: none; border-top: 1px solid #bbb; }
</style>
"""


def main():
    md = MD.read_text(encoding="utf-8")
    corpo = markdown.markdown(md, extensions=["tables", "fenced_code"])
    html = "<html><head><meta charset='utf-8'>" + ESTILO + "</head><body>" + corpo + "</body></html>"
    with open(PDF, "wb") as f:
        status = pisa.CreatePDF(html, dest=f)
    if status.err:
        print("Erro ao gerar PDF")
        sys.exit(1)
    print(f"PDF gerado: {PDF}")


if __name__ == "__main__":
    main()
