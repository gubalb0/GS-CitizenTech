"""
Registro de latência de cada etapa do pipeline.

Mede o tempo de STT, RAG, LLM, adaptação e TTS, além do tempo total da pergunta
até o início da resposta falada. Grava em logs/latencia.csv para o relatório.
"""
import csv
import time
from datetime import datetime

import config


class LatencyTracker:
    """Cronômetro simples por etapa. Use como context manager:

    >>> t = LatencyTracker()
    >>> with t.step("stt"):
    ...     texto = transcrever(audio)
    >>> t.total_desde_inicio()
    """

    def __init__(self):
        self._marks = {}
        self._inicio = time.perf_counter()

    def step(self, nome):
        return _StepTimer(self, nome)

    def _registrar(self, nome, segundos):
        self._marks[nome] = round(segundos, 3)

    def total_desde_inicio(self):
        total = round(time.perf_counter() - self._inicio, 3)
        self._marks["total"] = total
        return total

    @property
    def marcas(self):
        return dict(self._marks)

    def salvar_csv(self, caminho=None, extra=None):
        """Acrescenta uma linha ao CSV de latências."""
        caminho = caminho or (config.LOG_DIR / "latencia.csv")
        linha = {"timestamp": datetime.now().isoformat(timespec="seconds")}
        linha.update(self._marks)
        if extra:
            linha.update(extra)
        existe = caminho.exists()
        with open(caminho, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(linha.keys()))
            if not existe:
                writer.writeheader()
            writer.writerow(linha)
        return caminho


class _StepTimer:
    def __init__(self, tracker, nome):
        self.tracker = tracker
        self.nome = nome

    def __enter__(self):
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.tracker._registrar(self.nome, time.perf_counter() - self._t0)
        return False
