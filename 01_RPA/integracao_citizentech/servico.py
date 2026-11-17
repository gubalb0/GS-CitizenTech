"""Camada de integração ISOLADA entre o assistente Gen AI (RAG sobre o DODF) e o protótipo CitizenTech (Zelo).

Só IMPORTA o Gen AI: nenhum arquivo de `citizentech/assistente/` é alterado (ver TRANSFERENCIA_BALBO.md, §1 e §8).
Contrato público: `AssistenteDODF.perguntar(texto) -> dict` na versão `VERSAO_CONTRATO`.
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field

from citizentech.assistente import geracao as G

logger = logging.getLogger("integracao_citizentech")

VERSAO_CONTRATO = "1.0"

# Status do Gen AI + "indisponivel" (criado aqui: o servidor do modelo não respondeu, nada foi gerado).
ROTULOS = {
    "respondida": "Resposta encontrada",
    "parcial": "Resposta parcial",
    "ambigua": "Mais de uma publicação possível",
    "insuficiente": "Sem resposta confirmada",
    "fora_do_escopo": "Fora do escopo",
    "indisponivel": "Assistente indisponível",
}
AVISOS = {
    "parcial": "A resposta pode estar incompleta: confira as publicações citadas.",
    "ambigua": "Encontramos mais de uma publicação que pode responder. Refaça a pergunta indicando a publicação, "
               "a data ou o número do contrato.",
    "insuficiente": "As publicações recuperadas não sustentam uma resposta. Isso não quer dizer que a informação não exista.",
    "fora_do_escopo": "O assistente só consulta publicações de saúde do Diário Oficial do Distrito Federal.",
    "indisponivel": "O modelo de linguagem não está ligado neste computador. A consulta funciona só na demonstração local, "
                    "com o LM Studio aberto.",
}
MSG_INDISPONIVEL = "O assistente de publicações oficiais está indisponível agora. Tente novamente mais tarde."
MSG_ERRO_TECNICO = "Não foi possível consultar o assistente agora por uma falha técnica. Tente novamente em instantes."
CAMPOS_FONTE = ("referencia", "tipo_documento", "numero_documento", "edicao", "data_edicao", "secao")


@dataclass
class _Recursos:
    corpus: list = field(default_factory=list)
    indice: object = None
    catalogo: object = None
    segundos_inicializacao: float = 0.0


class AssistenteDODF:
    """Carrega corpus, índice e catálogo UMA vez (~12 s) e serializa as chamadas ao modelo (LM Studio com parallel=1)."""

    def __init__(self, cfg: G.ConfigGeracao | None = None, sessao=None, carregar_recursos=None):
        self.cfg = cfg or G.ConfigGeracao()
        self.cliente = G.ClienteLMStudio(self.cfg, sessao)
        self._carregar_recursos = carregar_recursos or _carregar_recursos_reais
        self._recursos: _Recursos | None = None
        self._lock_init = threading.Lock()
        self._lock_modelo = threading.Lock()   # uma pergunta por vez

    # ------------------------------------------------------------- recursos
    @property
    def recursos(self) -> _Recursos:
        if self._recursos is None:
            with self._lock_init:
                if self._recursos is None:
                    t0 = time.perf_counter()
                    self._recursos = self._carregar_recursos()
                    self._recursos.segundos_inicializacao = round(time.perf_counter() - t0, 1)
                    logger.info("Corpus, índice e catálogo carregados em %.1f s", self._recursos.segundos_inicializacao)
        return self._recursos

    def saude(self) -> dict:
        return {
            "versao_contrato": VERSAO_CONTRATO,
            "versao_politica": G.VERSAO_POLITICA,
            "modelo": self.cfg.modelo,
            "modelo_disponivel": self.cliente.disponivel(),
            "recursos_carregados": self._recursos is not None,
        }

    # ------------------------------------------------------------- consulta
    def perguntar(self, texto: str) -> dict:
        if not isinstance(texto, str):
            raise TypeError("texto deve ser str")
        texto = texto.strip()
        if not self.cliente.disponivel():        # recomendação §8.4: checar antes de gerar
            return _saida("indisponivel", MSG_INDISPONIVEL, erro_tecnico="servidor_indisponivel")
        rec = self.recursos
        with self._lock_modelo:
            t0 = time.perf_counter()
            resultados = rec.indice.buscar(texto, k=self.cfg.max_chunks, modo="bm25") if texto else []
            r = G.gerar_resposta(texto, resultados, self.cliente, self.cfg, catalogo=rec.catalogo)
            latencia = round(time.perf_counter() - t0, 1)
        return converter(r.para_dict(), latencia)


def converter(d: dict, latencia_s: float | None = None) -> dict:
    """Converte `RespostaGerada.para_dict()` no contrato público. Não reescreve o texto do modelo."""
    tel = d.get("telemetria") or {}
    erro = tel.get("erro_tecnico")
    status = d.get("status") if d.get("status") in ROTULOS else "insuficiente"
    resposta = d.get("resposta") or ""
    if erro in ("servidor_indisponivel", "timeout", "resposta_invalida_do_servidor"):
        resposta = MSG_ERRO_TECNICO       # falha técnica não é "sem resposta": avisa para tentar de novo
    trechos = {}
    for e in d.get("evidencias") or []:
        trechos.setdefault(e.get("fonte"), []).append(e.get("trecho", ""))
    fontes = [{**{k: f.get(k) for k in CAMPOS_FONTE}, "trechos": trechos.get(f.get("id"), [])}
              for f in d.get("fontes") or []]
    return _saida(status, resposta, fontes=fontes, erro_tecnico=erro, latencia_s=latencia_s,
                  versao_politica=tel.get("versao_politica") or G.VERSAO_POLITICA)


def _saida(status, resposta, fontes=None, erro_tecnico=None, latencia_s=None, versao_politica=None) -> dict:
    return {
        "versao_contrato": VERSAO_CONTRATO,
        "versao_politica": versao_politica or G.VERSAO_POLITICA,
        "status": status,
        "rotulo_status": ROTULOS[status],
        "resposta": resposta,
        "aviso": AVISOS.get(status),
        "fontes": fontes or [],
        "erro_tecnico": erro_tecnico,
        "latencia_s": latencia_s,
    }


def _carregar_recursos_reais() -> _Recursos:
    from citizentech.assistente import dados as D
    from citizentech.assistente.avaliacao_e2e import IDX
    from citizentech.assistente.catalogo import Catalogo
    from citizentech.assistente.retriever import Indice

    corpus = D.carregar_corpus()
    return _Recursos(corpus=corpus, indice=Indice.carregar(IDX), catalogo=Catalogo.de_corpus(corpus))
