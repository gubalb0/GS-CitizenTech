"""Conferencia de integridade por SHA-256 - SOMENTE LEITURA.

Compara arquivos com (a) docs/modelo_congelado.json (RPA congelado) e (b) docs/assistente/diagnostico_4_4/hashes_referencia_44.json
(artefatos do Gen AI: rodadas, auditorias, versao 4.3, chunks_exemplos.json). NUNCA escreve, move nem regenera arquivos
(a versao anterior desta rotina, avulsa, regravava data_assistente/derivados/chunks_exemplos.json a cada conferencia).
Uso: python scripts/verificar_hashes.py [raiz]      (codigo de saida 0 = tudo confere; 1 = diferenca ou arquivo ausente)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

MANIFESTOS = (("docs/modelo_congelado.json", "sha256"), ("docs/assistente/diagnostico_4_4/hashes_referencia_44.json", "arquivos"))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def verificar(raiz: Path) -> list[tuple[str, str, str]]:
    """[(manifesto, caminho, 'OK'|'DIFERENTE'|'AUSENTE')]. Le arquivos; nao cria nem altera nada."""
    out = []
    for mf, chave in MANIFESTOS:
        arq = raiz / mf
        if not arq.exists():
            out.append((mf, "(manifesto)", "AUSENTE"))
            continue
        hashes = json.loads(arq.read_text(encoding="utf-8")).get(chave) or {}
        for rel, esperado in hashes.items():
            p = raiz / rel
            out.append((mf, rel, "AUSENTE" if not p.exists() else ("OK" if sha256(p) == esperado else "DIFERENTE")))
    return out


def main(argv: list[str]) -> int:
    raiz = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[1]
    res = verificar(raiz)
    for mf, rel, st in res:
        print(f"[{st:9}] {rel}   ({Path(mf).name})")
    ok = bool(res) and all(st == "OK" for _, _, st in res)
    print("TODOS CONFEREM:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
