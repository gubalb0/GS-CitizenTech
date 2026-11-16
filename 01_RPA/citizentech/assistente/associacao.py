"""Associacao pergunta (QA) -> publicacao(oes) de origem no corpus.

Regras (sem similaridade lexical): o `texto_publicacao` do QA e composto por blocos
    "Edicao N — AAAA-MM-DD — Secao X — <referencia>\\n<texto>"
e a chave estrutural (edicao, data_edicao, secao, referencia) mais a COMPARACAO TEXTUAL EXATA do corpo com
`texto_completo` decide o vinculo. Perguntas MULTI trazem varios blocos (cada um e associado separadamente).

Status por bloco:
  exata_unica        -> 1 documento do corpus com mesma chave e texto igual
  exata_duplicatas   -> varios documentos (ids distintos) com mesma chave e texto IDENTICO (duplicata no corpus)
  exata_normalizada  -> igual apenas apos remover acentos/caixa (nivel 2), 1 ou mais documentos
  texto_divergente   -> chave bate, texto nao bate (nao comprovado)
  ambigua            -> varios documentos com a mesma chave e textos DIFERENTES e nenhum igual ao bloco
  sem_correspondencia-> nenhuma chave encontrada
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from .dados import norm_espacos, norm_forte

CABECALHO = re.compile(r"^Edição (\d+) — (\d{4}-\d{2}-\d{2}) — (Seção [IVX]+) — (.*)$")
SEPARADOR = re.compile(r"(?m)^(?=Edição \d+ — \d{4}-\d{2}-\d{2} — Seção [IVX]+ — )")

RESOLVIDOS = {"exata_unica", "exata_duplicatas", "exata_normalizada"}


def dividir_blocos(texto_publicacao: str) -> list[dict]:
    """Quebra o texto_publicacao em blocos com cabecalho. Blocos sem cabecalho valido viram `cabecalho=None`."""
    partes = [p for p in SEPARADOR.split(texto_publicacao or "") if p.strip()]
    blocos = []
    for p in partes:
        linha, _, corpo = p.partition("\n")
        m = CABECALHO.match(linha)
        if not m:
            blocos.append({"cabecalho": None, "corpo": p.strip()})
            continue
        ed, data, sec, ref = m.groups()
        blocos.append({"cabecalho": {"edicao": int(ed), "data_edicao": data, "secao": sec, "referencia": ref},
                       "corpo": corpo.strip()})
    return blocos


def indexar_corpus(corpus: list[dict]) -> dict[tuple, list[dict]]:
    idx: dict[tuple, list[dict]] = defaultdict(list)
    for d in corpus:
        idx[(d["edicao"], d["data_edicao"], d["secao"], d["referencia"] or "")].append(d)
    return idx


def associar_bloco(bloco: dict, idx: dict) -> dict:
    cab = bloco["cabecalho"]
    if cab is None:
        return {"status": "sem_correspondencia", "motivo": "bloco_sem_cabecalho_valido", "doc_ids": []}
    cands = idx.get((cab["edicao"], cab["data_edicao"], cab["secao"], cab["referencia"]), [])
    if not cands:
        return {"status": "sem_correspondencia", "motivo": "chave_nao_encontrada", "doc_ids": [], "cabecalho": cab}
    corpo = norm_espacos(bloco["corpo"])
    iguais = [d for d in cands if norm_espacos(d["texto_completo"]) == corpo]
    if iguais:
        ids = sorted(d["id"] for d in iguais)
        return {"status": "exata_unica" if len(ids) == 1 else "exata_duplicatas", "doc_ids": ids,
                "n_candidatos_chave": len(cands), "cabecalho": cab}
    fortes = [d for d in cands if norm_forte(d["texto_completo"]) == norm_forte(bloco["corpo"])]
    if fortes:
        return {"status": "exata_normalizada", "doc_ids": sorted(d["id"] for d in fortes),
                "n_candidatos_chave": len(cands), "cabecalho": cab}
    return {"status": "texto_divergente" if len(cands) == 1 else "ambigua", "doc_ids": [],
            "candidatos_chave": sorted(d["id"] for d in cands), "cabecalho": cab}


def associar_pergunta(qa: dict, idx: dict) -> dict:
    blocos = dividir_blocos(qa["texto_publicacao"])
    res = [associar_bloco(b, idx) for b in blocos]
    multi = qa.get("fonte") == "MULTI"
    st = [r["status"] for r in res]
    if st and all(s in RESOLVIDOS for s in st):
        estado = "resolvida"
    elif any(s in RESOLVIDOS for s in st):
        estado = "parcial"
    else:
        estado = "nao_resolvida"
    return {"qid": qa["qid"], "multi": multi, "n_blocos": len(blocos), "estado": estado, "blocos": res,
            "doc_ids": sorted({i for r in res for i in r["doc_ids"]})}


def associar_todas(corpus: list[dict], perguntas: list[dict]) -> list[dict]:
    idx = indexar_corpus(corpus)
    return [associar_pergunta(q, idx) for q in perguntas]


def resumo(assoc: list[dict]) -> dict:
    por_estado = Counter(a["estado"] for a in assoc)
    por_bloco = Counter(b["status"] for a in assoc for b in a["blocos"])
    return {"perguntas": len(assoc), "por_estado": dict(por_estado), "blocos_total": sum(por_bloco.values()),
            "por_status_bloco": dict(por_bloco),
            "multi": {"perguntas": sum(a["multi"] for a in assoc),
                      "por_estado": dict(Counter(a["estado"] for a in assoc if a["multi"])),
                      "blocos_por_pergunta": dict(Counter(a["n_blocos"] for a in assoc if a["multi"]))},
            "nao_multi": {"perguntas": sum(not a["multi"] for a in assoc),
                          "por_estado": dict(Counter(a["estado"] for a in assoc if not a["multi"]))}}


def _tokens(t: str) -> set[str]:
    return {w for w in re.findall(r"\w+", norm_forte(t)) if len(w) > 3}


def perguntas_nao_univocas(perguntas: list[dict], assoc: list[dict], limiar_jaccard: float = 0.8) -> list[dict]:
    """Diagnostico (nao e associacao): pares de perguntas identicas ou quase identicas (Jaccard de tokens) cuja
    resposta ou documento de origem difere. Serve para sinalizar perguntas que o texto sozinho nao desambigua."""
    por_q = {a["qid"]: a for a in assoc}
    achados = []
    for i in range(len(perguntas)):
        for j in range(i + 1, len(perguntas)):
            a, b = perguntas[i], perguntas[j]
            ta, tb = _tokens(a["pergunta"]), _tokens(b["pergunta"])
            if not ta or not tb:
                continue
            jac = len(ta & tb) / len(ta | tb)
            igual = norm_forte(a["pergunta"]) == norm_forte(b["pergunta"])
            if igual or jac >= limiar_jaccard:
                da, db = por_q[a["qid"]]["doc_ids"], por_q[b["qid"]]["doc_ids"]
                achados.append({"q1": a["qid"], "q2": b["qid"], "jaccard": round(jac, 3), "pergunta_identica": igual,
                                "mesmos_docs": da == db and bool(da), "respostas_iguais": norm_forte(a["resposta"]) == norm_forte(b["resposta"]),
                                "pergunta_1": a["pergunta"], "docs_1": da, "docs_2": db})
    return achados
