"""Politica fail-closed de evidencias (Etapa 4.1): regras DETERMINISTICAS aplicadas depois da geracao.

Nada aqui depende do LLM para decidir: tipo da pergunta, termos salientes, alinhamento pergunta x evidencia, periodo,
sustentacao das afirmacoes, publicacoes concorrentes, classificacao de divergencias e composicao da mensagem final.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .dados import norm_forte

# palavras genericas (sem acento): nao identificam uma publicacao especifica
GENERICAS = {"distrito", "federal", "dodf", "brasilia", "hospital", "saude", "servicos", "servico", "publicacoes", "publicacao", "unidade", "regional",
             "regiao", "secretaria", "estado", "conforme", "qual", "quais", "quem", "quando", "onde", "quanto", "quantos", "como", "porque", "foram",
             "para", "pelo", "pela", "pelos", "com", "das", "dos", "uma", "nos", "nas", "ate", "entre", "esta", "estao", "sendo", "esse", "essa",
             "foi", "sao", "tem", "teve", "tinha", "nao", "mais", "alem", "isso", "assim", "dentro", "sobre", "pode", "podem", "deve", "devem"}
MESES = {"janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
         "novembro": 11, "dezembro": 12}
_LISTA = re.compile(r"^\s*(?:quais|quantos|quantas|liste|cite|enumere)\b|\bconforme\s+as\s+publica[cç][oõ]es\b|\bquais\s+s[aã]o\b", re.I)
_SINGULAR = re.compile(r"^\s*(?:qual|quem|quando|at[eé]\s+quando|onde|quanto|em\s+que|de\s+quem|a\s+quem)\b", re.I)
_NUM = re.compile(r"\d[\d.,/\-]*\d|\d")


def _nf(t: str) -> str:
    return norm_forte(t)


def _sem_esp(t: str) -> str:
    return re.sub(r"\s+", "", t)


def eh_lista(pergunta: str) -> bool:
    return bool(_LISTA.search(pergunta))


def eh_singular(pergunta: str) -> bool:
    return bool(_SINGULAR.match(pergunta)) and not eh_lista(pergunta)


def dividir_pergunta_composta(pergunta: str) -> list[str]:
    """Divide uma pergunta composta em subperguntas independentes ('...? E tambem: ...?'). Retorna [pergunta] se simples."""
    partes = re.split(r"(?<=\?)\s+|\s+E\s+tamb[eé]m[:,]?\s+|;\s+e\s+", pergunta.strip())
    partes = [re.sub(r"^E\s+tamb[eé]m[:,]?\s+", "", p.strip()) for p in partes if p]
    partes = [p for p in partes if len(p.split()) >= 3]
    return partes if len(partes) >= 2 else [pergunta.strip()]


def _tokens(texto: str) -> list[str]:
    return re.findall(r"[\wÀ-ÿ][\wÀ-ÿ/\-\.]*", texto)


def termos_salientes(pergunta: str) -> dict:
    """Termos que identificam a publicacao pedida: nomes proprios (maiusculas fora do inicio), numeros/ids, anos e meses."""
    nomes, numeros, anos, meses = [], [], [], []
    for i, t in enumerate(_tokens(pergunta)):
        n = _nf(t).strip(".-/")
        if not n:
            continue
        if any(c.isdigit() for c in n):
            (anos if re.fullmatch(r"20\d\d", n) else numeros).append(n)
        elif n in MESES:
            meses.append(n)
        elif i > 0 and t[0].isupper() and len(n) >= 3 and n not in GENERICAS:
            nomes.append(n)
    return {"nomes": list(dict.fromkeys(nomes)), "numeros": list(dict.fromkeys(numeros)), "anos": list(dict.fromkeys(anos)), "meses": list(dict.fromkeys(meses))}


def palavras_de_conteudo(pergunta: str) -> list[str]:
    out = []
    for t in _tokens(pergunta):
        n = _nf(t).strip(".-/")
        if len(n) >= 5 and n not in GENERICAS and not any(c.isdigit() for c in n) and n not in MESES:
            out.append(n)
    return list(dict.fromkeys(out))


def _radical(w: str) -> str:
    return w[:6]


def _contem(texto_nf: str, termo: str) -> bool:
    return termo in texto_nf


def _contem_radical(texto_nf: str, termo: str) -> bool:
    return _radical(termo) in texto_nf


def periodo_ausente(sal: dict, texto: str, data_edicao: str | None) -> list[str]:
    """Anos/meses citados na pergunta que nao constam no texto citado nem na data da edicao."""
    t = _nf(texto)
    d = str(data_edicao or "")
    m = re.fullmatch(r"(\d{4})-(\d{2})-\d{2}", d)
    falt = []
    for y in sal["anos"]:
        if y not in t and not (m and m.group(1) == y):
            falt.append(y)
    for mes in sal["meses"]:
        if mes not in t and not (m and int(m.group(2)) == MESES[mes]):
            falt.append(mes)
    return falt


def alinhamento(pergunta: str, textos_citados: list[tuple[str, str | None]]) -> dict:
    """Todos os termos salientes (nomes, numeros) e o periodo da pergunta devem aparecer na evidencia citada (texto do chunk +
    cabecalho). Retorna {'ok': bool, 'ausentes': [...]}."""
    sal = termos_salientes(pergunta)
    alvo = _nf(" ".join(t for t, _ in textos_citados))
    aus = [("nome", n) for n in sal["nomes"] if n not in alvo] + [("numero", n) for n in sal["numeros"] if _sem_esp(n) not in _sem_esp(alvo)]
    # periodo: precisa constar em ao menos uma das fontes citadas
    for tipo, lista in (("ano", sal["anos"]), ("mes", sal["meses"])):
        for v in lista:
            if all(periodo_ausente({"anos": [v] if tipo == "ano" else [], "meses": [v] if tipo == "mes" else []}, t, d) for t, d in textos_citados):
                aus.append((tipo, v))
    return {"ok": not aus, "ausentes": aus}


def afirmacoes_nao_sustentadas(resposta: str, trechos: list[str], pergunta: str, extras: str = "") -> list[str]:
    """Numeros e nomes da RESPOSTA que nao aparecem nos trechos de evidencia citados (nem na pergunta). `extras` = metadados
    confiaveis das publicacoes citadas (data da edicao, referencia, numero) que tambem podem sustentar identificacoes."""
    ev = _nf(" ".join(trechos) + " " + extras)
    ev_sem = _sem_esp(ev)
    q = _nf(pergunta)
    falt = []
    for n in _NUM.findall(resposta):
        k = _sem_esp(_nf(n)).rstrip(".,-/")
        if k and k not in ev_sem and k not in _sem_esp(q):
            falt.append(k)
    toks = _tokens(resposta)
    ini = True
    for t in toks:
        n = _nf(t).strip(".-/,;:")
        eh_nome = bool(n) and len(n) >= 3 and not any(c.isdigit() for c in n) and n not in GENERICAS and (t[0].isupper() or t.isupper()) and not ini
        if eh_nome and n not in ev and n not in q:
            falt.append(n)
        ini = t.endswith((".", ":", "?", "!"))
    return list(dict.fromkeys(falt))


def tokens_especificos(resposta: str, pergunta: str) -> list[str]:
    """Elementos da resposta que identificam o FATO de forma especifica: valores monetarios, numeros/ids com 4+ digitos (exceto anos)
    e nomes proprios com 6+ letras que nao estao na pergunta. Numeros pequenos ('12 meses') sao fracos e ficam de fora."""
    q = _nf(pergunta)
    out = []
    for m in re.findall(r"R\$\s?\d[\d.,]*\d", resposta):
        out.append(_sem_esp(_nf(m)).rstrip(".,"))
    for n in _NUM.findall(resposta):
        k = re.sub(r"\D", "", n)
        if len(k) >= 4 and not re.fullmatch(r"20\d\d", k) and not any(k in re.sub(r"\D", "", o) for o in out):
            out.append(_sem_esp(_nf(n)).rstrip(".,-/"))
    ini = True
    for t in _tokens(resposta):
        n = _nf(t).strip(".-/,;:")
        if not ini and len(n) >= 6 and not any(c.isdigit() for c in n) and n not in GENERICAS and (t[0].isupper() or t.isupper()) and n not in q:
            out.append(n)
        ini = t.endswith((".", ":", "?", "!"))
    return list(dict.fromkeys(out))


def publicacoes_concorrentes(pergunta: str, itens: list, citados: list) -> list:
    """Publicacoes (docs diferentes e nao equivalentes) presentes no contexto enviado que cobrem TODOS os termos da pergunta que a
    publicacao citada cobre (nomes, numeros, anos, palavras de conteudo): sao tao relevantes quanto a citada."""
    sal = termos_salientes(pergunta)
    termos = sal["nomes"] + sal["numeros"] + sal["anos"] + sal["meses"] + palavras_de_conteudo(pergunta)
    if not termos or not citados:
        return []

    def cobre(it) -> set[str]:
        t = _nf(it.texto_original + " " + str(it.metadados.get("data_edicao") or ""))
        return {x for x in termos if (_contem(t, x) if x in sal["nomes"] + sal["numeros"] + sal["anos"] + sal["meses"] else _contem_radical(t, x))}
    ids_cit = set().union(*[set(c.ids_equivalentes) | {c.doc_id} for c in citados])
    cob_cit = set().union(*[cobre(c) for c in citados])
    out = []
    for it in itens:
        if it in citados or (set(it.ids_equivalentes) | {it.doc_id}) & ids_cit:
            continue
        if cob_cit and cobre(it) >= cob_cit:
            out.append(it)
    return out


def identificar_publicacao(m: dict) -> str:
    titulo = " ".join(x for x in (str(m.get("tipo_documento") or "").strip(), str(m.get("referencia") or m.get("numero_documento") or "").strip()) if x)
    return f"{titulo or 'publicação'} (DODF edição {m.get('edicao', '?')}, {m.get('data_edicao', '?')}, {m.get('secao', '?')})"


def metadados_completos(meta: dict, doc_id) -> list[str]:
    """Rastreabilidade: id do documento e metadados minimos."""
    falt = []
    if doc_id in (None, ""):
        falt.append("doc_id")
    for k in ("edicao", "data_edicao", "secao"):
        if meta.get(k) in (None, ""):
            falt.append(k)
    if not (meta.get("referencia") or meta.get("numero_documento")):
        falt.append("referencia/numero_documento")
    return falt


def _chave(t: str) -> str:
    return re.sub(r"[^0-9a-z]+", "", _nf(t))


def classificar_divergencia(candidatas: list[dict], datas: dict[str, str | None]) -> dict:
    """Classifica candidatas literais a uma pergunta de resposta unica:
    'duplicadas' (mesma publicacao ou copias), 'respostas_equivalentes', 'periodos_diferentes' (datas de edicao diferentes),
    'divergentes_mesmo_periodo' (conflito sobre o mesmo fato) ou 'sem_divergencia'. `datas`: id da fonte -> data_edicao."""
    lit = [c for c in candidatas if c.get("literal") and _chave(c["resposta_possivel"])]
    distintas: list[dict] = []
    for c in lit:
        k = _chave(c["resposta_possivel"])
        if any(k in _chave(d["resposta_possivel"]) or _chave(d["resposta_possivel"]) in k for d in distintas):
            continue
        distintas.append(c)
    if len(distintas) < 2:
        return {"tipo": "respostas_equivalentes" if len(lit) > 1 else "sem_divergencia", "candidatas": distintas}
    docs = [set(d["ids_equivalentes"]) for d in distintas]
    if all(docs[0] & d for d in docs[1:]):
        return {"tipo": "duplicadas", "candidatas": distintas}
    ds = {datas.get(d["fonte"]) for d in distintas}
    return {"tipo": "periodos_diferentes" if len(ds) > 1 else "divergentes_mesmo_periodo", "candidatas": distintas}


@dataclass
class Decisao:
    status: str
    resposta: str | None = None            # None => manter a do modelo
    fontes_ids: list[str] = field(default_factory=list)
    motivos: list[str] = field(default_factory=list)
    tipo: str | None = None


def aviso_parcial(n_publicacoes: int) -> str:
    return (f"AVISO: resposta parcial, baseada apenas nas {n_publicacoes} publicação(ões) recuperada(s); pode haver outras publicações "
            "com informações adicionais que não foram verificadas.")


AVISO_ESCOPO = ("ATENÇÃO: a pergunta não informa data, número ou documento; esta resposta refere-se apenas à publicação identificada abaixo, "
                "e podem existir outras publicações semelhantes com informações diferentes.")


def sem_discriminador(pergunta: str) -> bool:
    """A pergunta nao traz numero/id, ano ou mes: nada a distingue entre publicacoes semelhantes do mesmo assunto."""
    s = termos_salientes(pergunta)
    return not (s["numeros"] or s["anos"] or s["meses"])


def aviso_cobertura(n_pub: int, n_outras: int | None) -> str:
    """Etapa 4.3: lista com cobertura incompleta — o que foi encontrado e o que NAO pode ser confirmado."""
    base = f"AVISO: resposta parcial. Foram analisadas apenas {n_pub} publicação(ões)"
    if n_outras:
        return (base + f"; o corpus contém ao menos {n_outras} outra(s) publicação(ões) potencialmente relevante(s) que não foram analisadas, "
                "portanto não é possível confirmar que a lista está completa.")
    return base + "; não é possível confirmar que a lista está completa, pois podem existir outras publicações com informações adicionais."


def compor(resposta: str, publicacoes: list[str], parcial: bool, n_pub: int, escopo: bool = False, aviso: str | None = None) -> str:
    partes = [resposta.strip()]
    if escopo:
        partes.append(AVISO_ESCOPO)
    elif parcial:
        partes.append(aviso or aviso_parcial(n_pub))
    partes.append("Fonte: " + "; ".join(publicacoes) + ".")
    return "\n\n".join(partes)
