"""Regras de negocio: departamento, prioridade/SLA e decisao de revisao humana."""
from . import config
from .texto import normalizar

DEPARTAMENTO = {
    "agendamento_consulta": "Recepcao e Agendamento da UBS",
    "vacinacao": "Sala de Vacina",
    "medicamentos": "Farmacia da UBS",
    "exames_resultados": "Regulacao de Exames",
    "visita_domiciliar": "Equipe de Saude da Familia - Visita Domiciliar",
    "reclamacao_atendimento": "Ouvidoria da Saude",
    "informacoes_gerais": "Acolhimento e Informacoes",
    "sintomas_urgentes": "Classificacao de Risco (profissional de saude)",
    "indefinida": "Triagem Manual",
}
# Termos de possivel urgencia clinica -> prioridade alta => SEMPRE avaliacao humana imediata.
# O robo nao faz diagnostico nem orientacao clinica; so sinaliza e entrega aviso padrao (192/UPA).
URGENTES = ["dor no peito", "falta de ar", "respira com dificuldade", "dificuldade para respirar",
            "dificuldade respiratoria", "desmaio", "desmaiou", "desmaiada", "convulsao", "sangramento",
            "sangrar", "febre alta", "boca torta", "confuso", "confusao", "engasgada", "engasgado",
            "roxa", "roxo", "dor forte no peito"]
SLA_H = {"alta": 1, "normal": 72}


def prioridade(texto: str) -> tuple[str, list[str]]:
    t = " " + normalizar(texto) + " "
    achados = [k for k in URGENTES if f" {k} " in t]
    return ("alta" if achados else "normal"), achados


def decidir(categoria: str, confianca: float, texto: str) -> dict:
    prio, gatilhos = prioridade(texto)
    # urgencia clinica nunca e resolvida sozinha pelo robo: vai para humano
    revisao = confianca < config.CONFIANCA_MINIMA or categoria == "indefinida" or prio == "alta"         or categoria == "sintomas_urgentes"
    if categoria == "sintomas_urgentes":
        prio = "alta"
    return {
        "departamento": DEPARTAMENTO.get(categoria, DEPARTAMENTO["indefinida"]),
        "prioridade": prio,
        "gatilhos_urgencia": ";".join(gatilhos),
        "prazo_horas": SLA_H[prio],
        "status": "revisao_humana" if revisao else "encaminhado",
    }
