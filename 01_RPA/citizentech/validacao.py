"""Regras de validacao de dados de entrada."""
import re

from .ingestao import Registro

_CEP = re.compile(r"^\d{5}-?\d{3}$")


def validar(r: Registro) -> list[str]:
    erros = []
    t = (r.texto or "").strip()
    if not t:
        erros.append("texto_vazio")
    elif len(t) < 15:
        erros.append("texto_curto_demais")
    elif len(t) > 2000:
        erros.append("texto_longo_demais")
    if r.cep and not _CEP.match(r.cep):
        erros.append("cep_invalido")
    return erros
