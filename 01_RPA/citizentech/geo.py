"""Integracao com API publica gratuita (ViaCEP) com timeout, retry com espera e circuit breaker.
Apenas o CEP (dado publico) sai da maquina; o texto da solicitacao nunca e enviado."""
import logging
import time

import requests

from . import config

log = logging.getLogger("citizentech")


class ConsultaCEP:
    LIMITE_FALHAS_SEGUIDAS = 3

    def __init__(self, url=None, timeout=None, retries=None, backoff=None, sessao=None):
        self.url = url or config.CEP_API_URL
        self.timeout = timeout if timeout is not None else config.CEP_TIMEOUT_S
        self.retries = retries if retries is not None else config.CEP_MAX_RETRIES
        self.backoff = backoff if backoff is not None else config.CEP_BACKOFF_S
        self.http = sessao or requests
        self.cache: dict[str, dict] = {}
        self.falhas_seguidas = 0
        self.chamadas = 0
        self.tentativas_falhas = 0

    def buscar(self, cep: str) -> dict:
        """Retorna dict com 'fonte' ('viacep', 'indisponivel' ou 'sem_cep'). Nunca levanta excecao."""
        cep = cep.replace("-", "")
        if not cep:
            return {"fonte": "sem_cep"}
        if cep in self.cache:
            return self.cache[cep]
        if self.falhas_seguidas >= self.LIMITE_FALHAS_SEGUIDAS:
            return {"fonte": "indisponivel", "motivo": "circuit_breaker_aberto"}
        res = self._com_retry(cep)
        if res.get("fonte") == "viacep":
            self.cache[cep] = res
            self.falhas_seguidas = 0
        elif res.get("motivo") != "cep_nao_encontrado":
            self.falhas_seguidas += 1
        return res

    def _com_retry(self, cep: str) -> dict:
        ultimo = ""
        for tent in range(1, self.retries + 1):
            self.chamadas += 1
            try:
                r = self.http.get(self.url.format(cep=cep), timeout=self.timeout)
                r.raise_for_status()
                d = r.json()
                if not isinstance(d, dict):
                    raise ValueError("resposta inesperada")
                if d.get("erro"):
                    return {"fonte": "indisponivel", "motivo": "cep_nao_encontrado"}
                return {"bairro": d.get("bairro", ""), "cidade": d.get("localidade", ""),
                        "uf": d.get("uf", ""), "fonte": "viacep"}
            except (requests.RequestException, ValueError) as e:
                ultimo = type(e).__name__
                self.tentativas_falhas += 1
                log.warning("CEP %s: tentativa %d/%d falhou (%s)", cep, tent, self.retries, ultimo)
                if tent < self.retries:
                    time.sleep(self.backoff * 2 ** (tent - 1))  # backoff exponencial
        return {"fonte": "indisponivel", "motivo": ultimo}
