"""Fase 4B - PROTOTIPO de S1 conservadora (somente analise offline; NAO faz parte do pacote `citizentech`, nao liga a flag, nao altera a implementacao).

Regra: o S1 atual (`montar_contexto` com priorizar_atributo=True) so vale se NENHUM chunk ja selecionado "cobre" o atributo para a entidade da pergunta.
Cobertura de um chunk (estrita: os nomes salientes precisam estar NO PROPRIO chunk, nao so na publicacao):
  - 'rotulo'       : rotulo forte em posicao de rotulo (`EV.rotulo_forte_no_chunk` com texto_entidade = o proprio chunk);
  - 'valor_tipado' : somente familia VALOR e somente se o atributo tem forma verificavel por estrutura: quantia monetaria 'R$ n' no chunk (cobre valor escrito em prosa).
Para as demais familias nao ha forma tipada confiavel: so o rotulo conta (limitacao documentada). Associacao com outra entidade => nao cobre.
"""
import re
import sys

sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import evidencias as EV
from citizentech.assistente.geracao import ConfigGeracao, montar_contexto

_RS = re.compile(r"R\$\s*\d")


def cobertura_do_chunk(texto: str, cab, fam, nomes) -> dict | None:
    if not fam or not nomes:
        return None
    if not all(n in EV._nf(texto) for n in nomes):
        return None                                                     # outra entidade (ou entidade nao identificavel no chunk): nao cobre
    r = EV.rotulo_forte_no_chunk(texto, cab, fam, nomes, texto)
    if r:
        return {"tipo": "rotulo", "detalhe": r["rotulo"]}
    if fam == "VALOR" and _RS.search(texto):
        return {"tipo": "valor_tipado", "detalhe": "R$"}
    return None


def montar_contexto_conservador(pergunta, resultados, cfg_off, cfg_on):
    """Retorna (contexto, info). `cfg_off`/`cfg_on` = ConfigGeracao sem/com priorizar_atributo."""
    base = montar_contexto(pergunta, resultados, cfg_off)
    atual = montar_contexto(pergunta, resultados, cfg_on)
    cab = EV.cabeca_do_atributo(pergunta)
    fam = EV.familia_do_atributo(cab)
    nomes = EV.termos_salientes(pergunta)["nomes"]
    por_id = {r.chunk_id: r for r in resultados}
    cob = {i.chunk_id: cobertura_do_chunk(por_id[i.chunk_id].texto, cab, fam, nomes) for i in base.itens}
    ids0, ids1 = [i.chunk_id for i in base.itens], [i.chunk_id for i in atual.itens]
    info = {"cobertura_selecionados": cob, "s1_atual_mudaria": ids0 != ids1}
    if ids0 == ids1:
        info["decisao"] = "sem_candidato"
        return base, info
    if any(cob.values()):
        info["decisao"] = "promocao_redundante_evitada"
        return base, info
    info["decisao"] = "promovido"
    return atual, info
