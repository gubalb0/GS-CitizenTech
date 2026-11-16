"""Idempotencia: guarda hash de cada solicitacao processada (SQLite local) para evitar duplicidade."""
import hashlib
import sqlite3
from pathlib import Path

from .texto import normalizar


def hash_solicitacao(texto: str, cep: str) -> str:
    return hashlib.sha256((normalizar(texto) + "|" + cep.replace("-", "")).encode()).hexdigest()


class Estado:
    def __init__(self, caminho: Path):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(caminho)
        self.con.execute("CREATE TABLE IF NOT EXISTS processados (hash TEXT PRIMARY KEY, id TEXT, ts TEXT DEFAULT CURRENT_TIMESTAMP)")
        self.con.commit()

    def ja_processado(self, h: str) -> bool:
        return self.con.execute("SELECT 1 FROM processados WHERE hash=?", (h,)).fetchone() is not None

    def marcar(self, h: str, rid: str) -> None:
        self.con.execute("INSERT OR IGNORE INTO processados(hash,id) VALUES(?,?)", (h, rid))
        self.con.commit()

    def limpar(self) -> None:
        self.con.execute("DELETE FROM processados")
        self.con.commit()

    def fechar(self):
        self.con.close()
