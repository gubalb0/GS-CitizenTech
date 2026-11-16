"""Orquestracao ponta a ponta: captura -> validacao -> IA -> regras -> API CEP -> resposta -> relatorios."""
import csv
import json
import logging
import time
from datetime import datetime
from pathlib import Path

from . import classificador, config, regras
from .estado import Estado, hash_solicitacao
from .geo import ConsultaCEP
from .ingestao import Registro, ler_inbox
from .texto import mascarar_pii
from .validacao import validar

log = logging.getLogger("citizentech")

CAMPOS = ["id", "origem", "texto_anonimizado", "categoria", "confianca", "metodo", "departamento", "prioridade",
          "gatilhos_urgencia", "prazo_horas", "status", "bairro", "cidade", "uf", "fonte_cep", "protocolo",
          "resposta_ao_cidadao"]


AVISO_URGENCIA = ("ATENCAO: este canal NAO e atendimento de emergencia. Se houver risco de vida, "
                  "ligue 192 (SAMU) ou va imediatamente a uma UPA/pronto-socorro.")


def gerar_resposta(protocolo: str, depto: str, prazo_h: int, status: str, prioridade: str = "normal") -> str:
    aviso = " " + AVISO_URGENCIA if prioridade == "alta" else ""
    if status == "revisao_humana":
        return (f"Protocolo {protocolo}: recebemos sua solicitacao e ela sera analisada por um profissional "
                f"antes do encaminhamento.{aviso}")
    return (f"Protocolo {protocolo}: sua solicitacao foi encaminhada a {depto}, com prazo de resposta de "
            f"ate {prazo_h} horas.")


def processar_registro(r: Registro, modelo, cep_api: ConsultaCEP, seq: int, run_id: str) -> dict:
    texto_anon, _ = mascarar_pii(r.texto.strip())
    cat, conf, metodo = classificador.classificar(modelo, r.texto)
    dec = regras.decidir(cat, conf, r.texto)
    geo = cep_api.buscar(r.cep)
    protocolo = f"{run_id}-{seq:04d}"
    return {
        "id": r.id, "origem": r.origem, "texto_anonimizado": texto_anon, "categoria": cat,
        "confianca": round(conf, 3), "metodo": metodo, **dec,
        "bairro": geo.get("bairro", ""), "cidade": geo.get("cidade", ""), "uf": geo.get("uf", ""),
        "fonte_cep": geo.get("fonte", ""), "protocolo": protocolo,
        "resposta_ao_cidadao": gerar_resposta(protocolo, dec["departamento"], dec["prazo_horas"], dec["status"], dec["prioridade"]),
    }


def executar(diretorio_inbox: Path = config.DIR_INBOX, diretorio_saida: Path = config.DIR_SAIDA,
             estado: Estado | None = None, cep_api: ConsultaCEP | None = None, modelo="auto") -> dict:
    t0 = time.perf_counter()
    run_id = datetime.now().strftime("%Y%m%d%H%M%S")
    diretorio_saida.mkdir(parents=True, exist_ok=True)
    estado = estado or Estado(config.ARQ_ESTADO)
    cep_api = cep_api or ConsultaCEP()
    if modelo == "auto":
        modelo = classificador.carregar_modelo()

    registros, falhas_arquivo = ler_inbox(diretorio_inbox)
    resultados, rejeitados, duplicados, erros = [], [], [], []

    for r in registros:
        try:
            problemas = validar(r)
            if problemas:
                log.warning("Registro %s rejeitado: %s", r.id, ",".join(problemas))
                rejeitados.append({"id": r.id, "origem": r.origem, "motivo": ";".join(problemas)})
                continue
            h = hash_solicitacao(r.texto, r.cep)
            if estado.ja_processado(h):
                log.info("Registro %s duplicado (ja processado) - ignorado", r.id)
                duplicados.append({"id": r.id, "origem": r.origem})
                continue
            res = processar_registro(r, modelo, cep_api, len(resultados) + 1, run_id)
            resultados.append(res)
            estado.marcar(h, r.id)  # so marca apos sucesso => falha pode ser reprocessada
        except Exception as e:  # falha isolada nao interrompe o lote
            log.exception("Erro ao processar registro %s", r.id)
            erros.append({"id": r.id, "origem": r.origem, "erro": f"{type(e).__name__}: {e}"})

    tempo = time.perf_counter() - t0
    revisao = [x for x in resultados if x["status"] == "revisao_humana"]
    urgentes = [x for x in resultados if x["prioridade"] == "alta"]
    total_lidos = len(registros)
    resumo = {
        "run_id": run_id, "registros_lidos": total_lidos, "processados": len(resultados),
        "rejeitados_invalidos": len(rejeitados), "duplicados_ignorados": len(duplicados),
        "erros_processamento": len(erros), "arquivos_com_falha": len(falhas_arquivo),
        "encaminhados_automaticamente": len(resultados) - len(revisao), "enviados_revisao_humana": len(revisao),
        "prioridade_alta": len(urgentes),
        "taxa_automacao_sobre_validos": round((len(resultados) - len(revisao)) / len(resultados), 3) if resultados else 0.0,
        "consultas_cep_http": cep_api.chamadas, "falhas_http_cep": cep_api.tentativas_falhas,
        "cep_indisponivel": sum(1 for x in resultados if x["fonte_cep"] == "indisponivel"),
        "tempo_segundos": round(tempo, 2),
    }
    _gravar(diretorio_saida, run_id, resultados, rejeitados, duplicados, erros, falhas_arquivo, resumo)
    log.info("Resumo: %s", json.dumps(resumo, ensure_ascii=False))
    return resumo


def _csv(caminho: Path, linhas: list[dict], campos: list[str] | None = None):
    campos = campos or (list(linhas[0].keys()) if linhas else ["vazio"])
    with caminho.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)


def _gravar(saida: Path, run_id, resultados, rejeitados, duplicados, erros, falhas_arquivo, resumo):
    _csv(saida / "resultados.csv", resultados, CAMPOS)
    _csv(saida / "revisao_humana.csv", [x for x in resultados if x["status"] == "revisao_humana"], CAMPOS)
    _csv(saida / "rejeitados.csv", rejeitados, ["id", "origem", "motivo"])
    (saida / "relatorio_execucao.json").write_text(
        json.dumps({"resumo": resumo, "arquivos_com_falha": falhas_arquivo, "erros": erros,
                    "duplicados": duplicados}, ensure_ascii=False, indent=2), encoding="utf-8")
