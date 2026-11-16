import logging
import sys

from . import config


def configurar_log() -> logging.Logger:
    config.DIR_LOGS.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("citizentech")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")
    fh = logging.FileHandler(config.DIR_LOGS / "execucao.log", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(sh)
    return log
