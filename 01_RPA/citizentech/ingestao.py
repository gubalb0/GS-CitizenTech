"""RPA - captura: le a caixa de entrada (CSV e TXT) e devolve registros brutos.
Falhas de arquivo (ausente, corrompido, colunas faltando) sao registradas e nao derrubam o lote."""
import csv
import logging
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("citizentech")


@dataclass
class Registro:
    id: str
    texto: str
    cep: str
    origem: str


def ler_inbox(diretorio: Path) -> tuple[list[Registro], list[dict]]:
    regs: list[Registro] = []
    falhas: list[dict] = []
    if not diretorio.exists() or not diretorio.is_dir():
        log.error("Diretorio de entrada ausente: %s", diretorio)
        falhas.append({"arquivo": str(diretorio), "motivo": "diretorio_ausente"})
        return regs, falhas
    arquivos = sorted(p for p in diretorio.iterdir() if p.suffix.lower() in (".csv", ".txt"))
    if not arquivos:
        log.warning("Nenhum arquivo .csv/.txt em %s", diretorio)
    for arq in arquivos:
        try:
            novos = _ler_csv(arq) if arq.suffix.lower() == ".csv" else _ler_txt(arq)
            log.info("Lido %s: %d registro(s)", arq.name, len(novos))
            regs.extend(novos)
        except Exception as e:  # arquivo ruim nao interrompe os demais
            log.error("Falha ao ler %s: %s: %s", arq.name, type(e).__name__, e)
            falhas.append({"arquivo": arq.name, "motivo": f"{type(e).__name__}: {e}"})
    return regs, falhas


def _ler_csv(arq: Path) -> list[Registro]:
    with arq.open(newline="", encoding="utf-8") as fh:  # UnicodeDecodeError se corrompido
        rd = csv.DictReader(fh)
        if not rd.fieldnames or "texto" not in rd.fieldnames:
            raise ValueError("coluna obrigatoria 'texto' ausente")
        out = []
        for i, row in enumerate(rd, start=2):
            rid = (row.get("id") or "").strip() or f"{arq.stem}-L{i}"
            out.append(Registro(rid, row.get("texto") or "", (row.get("cep") or "").strip(), arq.name))
        return out


def _ler_txt(arq: Path) -> list[Registro]:
    linhas = arq.read_text(encoding="utf-8").splitlines()
    cep = ""
    corpo = []
    for l in linhas:
        if l.upper().startswith("CEP:"):
            cep = l.split(":", 1)[1].strip()
        else:
            corpo.append(l)
    return [Registro(arq.stem, "\n".join(corpo).strip(), cep, arq.name)]
