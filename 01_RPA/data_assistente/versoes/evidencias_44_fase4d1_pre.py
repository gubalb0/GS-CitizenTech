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


_DATA_NUM = re.compile(r"(?<!\d)(\d{1,2})/(\d{1,2})/(\d{4})(?!\d)")


def meses_em_datas_numericas(texto_nf: str) -> set[int]:
    """Meses (1-12) de datas numericas dd/mm/aaaa presentes no texto ('27/06/2025' -> 6). Etapa 4.4 (val-106)."""
    return {int(m.group(2)) for m in _DATA_NUM.finditer(texto_nf) if 1 <= int(m.group(2)) <= 12}


def periodo_ausente(sal: dict, texto: str, data_edicao: str | None) -> list[str]:
    """Anos/meses citados na pergunta que nao constam no texto citado nem na data da edicao. O mes vale pelo nome ou por data numerica
    dd/mm/aaaa no proprio texto (4.4)."""
    t = _nf(texto)
    d = str(data_edicao or "")
    m = re.fullmatch(r"(\d{4})-(\d{2})-\d{2}", d)
    nums = meses_em_datas_numericas(t)
    falt = []
    for y in sal["anos"]:
        if y not in t and not (m and m.group(1) == y):
            falt.append(y)
    for mes in sal["meses"]:
        if mes not in t and MESES[mes] not in nums and not (m and int(m.group(2)) == MESES[mes]):
            falt.append(mes)
    return falt


def alinhamento(pergunta: str, textos_citados: list[tuple[str, str | None]], textos_publicacao: list[tuple[str, str]] | None = None) -> dict:
    """Todos os termos salientes (nomes, numeros) e o periodo da pergunta devem aparecer na evidencia citada (texto do chunk +
    cabecalho). Retorna {'ok': bool, 'ausentes': [...], 'origens': {termo: origem}}.
    Etapa 4.4: `textos_publicacao` = [(texto, origem)] de OUTROS trechos da MESMA publicacao citada (chunks vizinhos do contexto, documento
    completo do catalogo). Um nome/numero/periodo que nao esta no chunk citado, mas esta na mesma publicacao, e aceito com a origem registrada
    ('chunk_citado' | 'chunk_vizinho' | 'documento_completo'). Nunca recebe textos de publicacoes diferentes (responsabilidade de quem chama)."""
    sal = termos_salientes(pergunta)
    alvo = _nf(" ".join(t for t, _ in textos_citados))
    extra = [(_nf(t), o) for t, o in (textos_publicacao or [])]
    origens: dict[str, str] = {}

    def achou(termo: str, eh_numero: bool = False) -> bool:
        if eh_numero:
            if _sem_esp(termo) in _sem_esp(alvo):
                origens[termo] = "chunk_citado"
                return True
            for t, o in extra:
                if _sem_esp(termo) in _sem_esp(t):
                    origens[termo] = o
                    return True
            return False
        if termo in alvo:
            origens[termo] = "chunk_citado"
            return True
        for t, o in extra:
            if termo in t:
                origens[termo] = o
                return True
        return False

    aus = [("nome", n) for n in sal["nomes"] if not achou(n)] + [("numero", n) for n in sal["numeros"] if not achou(n, True)]
    # periodo: precisa constar em ao menos uma das fontes citadas (ou na mesma publicacao)
    for tipo, lista in (("ano", sal["anos"]), ("mes", sal["meses"])):
        for v in lista:
            args = lambda t, d: periodo_ausente({"anos": [v] if tipo == "ano" else [], "meses": [v] if tipo == "mes" else []}, t, d)   # noqa: E731
            if all(args(t, d) for t, d in textos_citados):
                prov = next((o for t, o in (textos_publicacao or []) if not args(t, textos_citados[0][1] if textos_citados else None)), None)
                if prov is None:
                    aus.append((tipo, v))
                else:
                    origens[v] = prov
            else:
                origens[v] = "chunk_citado"
    return {"ok": not aus, "ausentes": aus, "origens": origens}


def afirmacoes_nao_sustentadas(resposta: str, trechos: list[str], pergunta: str, extras: str = "", adicionais: list[tuple[str, str]] | None = None,
                               origens: dict | None = None) -> list[str]:
    """Numeros e nomes da RESPOSTA que nao aparecem nos trechos de evidencia citados (nem na pergunta). `extras` = metadados
    confiaveis das publicacoes citadas (data da edicao, referencia, numero) que tambem podem sustentar identificacoes."""
    ev = _nf(" ".join(trechos) + " " + extras)
    ev_sem = _sem_esp(ev)
    q = _nf(pergunta)
    # 4.4: evidencias ADICIONAIS atribuiveis a mesma publicacao citada, com origem registrada (ex.: candidata literal verificada no chunk citado)
    adic = [(_nf(t), o) for t, o in (adicionais or [])]
    adic_sem = [(_sem_esp(t), o) for t, o in adic]

    def origem(k: str, kind: str) -> str | None:
        if kind == "n" and k in ev_sem:
            return "citacao_verificada"
        for (ts, o), (tn, _) in zip(adic_sem, adic):
            if (k in ts) if kind == "n" else (k in tn):
                return o
        return None
    falt = []
    for n in _NUM.findall(resposta):
        k = _sem_esp(_nf(n)).rstrip(".,-/")
        if k and k not in ev_sem and k not in _sem_esp(q):
            o = origem(k, "n")
            if o is None:
                falt.append(k)
            elif origens is not None:
                origens[k] = o
    toks = _tokens(resposta)
    ini = True
    for t in toks:
        n = _nf(t).strip(".-/,;:")
        eh_nome = bool(n) and len(n) >= 3 and not any(c.isdigit() for c in n) and n not in GENERICAS and (t[0].isupper() or t.isupper()) and not ini
        if eh_nome and n not in ev and n not in q:
            o = origem(n, "t")
            if o is None:
                falt.append(n)
            elif origens is not None:
                origens[n] = o
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


# ------------------------------------------------------------------ Etapa 4.4 (Fase 2): citacao, atribuicao e niveis de evidencia
_TOK = re.compile(r"\d[\d.,/\-]*\d|\d|[^\W\d_]+", re.UNICODE)
_ALFABETO_ESTRANHO = re.compile("[Ͱ-ϿЀ-ԯ֐-ۿऀ-෿฀-໿ᄀ-ᇿ぀-ヿ㐀-鿿가-힯]")
MAX_SPAN_TOKENS = 120          # regiao compacta do chunk em que os fragmentos de uma citacao reparada precisam estar
MIN_COBERTURA = 0.6            # fracao dos tokens da citacao que precisa casar literalmente
MIN_FRAGMENTO = 2              # tokens para um fragmento contar


def tem_alfabeto_estranho(texto: str) -> bool:
    """Caracteres de outros alfabetos (CJK, cirilico, arabe...) em texto em portugues: sinal de geracao corrompida."""
    return bool(_ALFABETO_ESTRANHO.search(texto or ""))


def _toks(t: str) -> list[str]:
    t = (t or "").replace("°", "º")
    t = re.sub(r"\bn\s*\.\s*º", "nº", t, flags=re.I)          # 'n.º' == 'nº'
    return _TOK.findall(norm_forte(t))


def _contido(parte: list[str], texto: list[str]) -> int | None:
    n = len(parte)
    if not n:
        return None
    for i in range(len(texto) - n + 1):
        if texto[i:i + n] == parte:
            return i
    return None


def casar_citacao(trecho: str, texto: str) -> dict:
    """Compara a citacao do modelo com o chunk citado, por TOKENS (numeros inteiros e palavras; pontuacao fora dos numeros e ignorada;
    acentos/caixa ignorados; digitos exatos). Retorna {'status', 'verificado': texto efetivamente casado, 'fragmentos', 'fabricados'}:
      literal     - cada parte (separada por '...') aparece contigua no chunk;
      reparada    - a citacao emenda trechos nao contiguos do MESMO chunk sem marcar '...': so os fragmentos literais valem como evidencia
                    (em ordem, em regiao compacta, cobrindo >= 60% da citacao e sem numero ausente do chunk);
      fabricada   - algum numero da citacao nao existe no chunk (valor inventado);
      nao_literal - o restante (inclui citacao copiada de OUTRO chunk, mesmo que da mesma publicacao: a citacao precisa estar no chunk citado).
    """
    tx = _toks(texto)
    partes = [_toks(p) for p in re.split(r"\.\.\.|…", trecho or "")]
    partes = [p for p in partes if p]
    if not partes:
        return {"status": "nao_literal", "verificado": "", "fragmentos": [], "fabricados": []}
    if all(_contido(p, tx) is not None for p in partes) and any(len(" ".join(p)) >= 4 for p in partes):
        return {"status": "literal", "verificado": " ... ".join(" ".join(p) for p in partes), "fragmentos": [], "fabricados": []}
    q = [t for p in partes for t in p]
    vocab = set(tx)
    fabr = [t for t in q if any(c.isdigit() for c in t) and t not in vocab]
    truncada = False
    if fabr == [q[-1]] and any(v.startswith(q[-1]) and v != q[-1] for v in vocab if any(c.isdigit() for c in v)):
        q, truncada, fabr = q[:-1], True, []          # numero cortado no fim da citacao (limite de caracteres): prefixo de numero do chunk, nao e valor inventado
        partes[-1] = partes[-1][:-1]
        partes = [p for p in partes if p]
        if partes and all(_contido(p, tx) is not None for p in partes):
            return {"status": "reparada", "verificado": " ... ".join(" ".join(p) for p in partes), "fragmentos": [], "fabricados": [], "truncada": True}
    if fabr:
        return {"status": "fabricada", "verificado": "", "fragmentos": [], "fabricados": fabr}
    pos: dict[str, list[int]] = {}
    for i, t in enumerate(tx):
        pos.setdefault(t, []).append(i)
    frags, i, ult = [], 0, -1
    while i < len(q):
        melhor = (0, -1)
        for j in pos.get(q[i], []):
            if j < ult:
                continue
            k = 0
            while i + k < len(q) and j + k < len(tx) and q[i + k] == tx[j + k]:
                k += 1
            if k > melhor[0]:
                melhor = (k, j)
        if melhor[0] >= MIN_FRAGMENTO:
            frags.append((melhor[1], melhor[1] + melhor[0]))
            ult = melhor[1] + melhor[0]
            i += melhor[0]
        else:
            i += 1
    cobertos = sum(b - a for a, b in frags)
    if frags and cobertos / len(q) >= MIN_COBERTURA and frags[-1][1] - frags[0][0] <= MAX_SPAN_TOKENS:
        return {"status": "reparada", "verificado": " ... ".join(" ".join(tx[a:b]) for a, b in frags), "fragmentos": [(a, b) for a, b in frags], "fabricados": []}
    return {"status": "nao_literal", "verificado": "", "fragmentos": [], "fabricados": []}


def termos_especificos_da_resposta(resposta: str, pergunta: str) -> list[str]:
    """Numeros e nomes proprios da resposta que nao estao na pergunta (os termos que precisam de evidencia)."""
    q = _nf(pergunta)
    out = []
    for n in _NUM.findall(resposta):
        k = _sem_esp(_nf(n)).rstrip(".,-/")
        if k and k not in _sem_esp(q):
            out.append(k)
    ini = True
    for t in _tokens(resposta):
        n = _nf(t).strip(".-/,;:")
        if bool(n) and len(n) >= 3 and not any(c.isdigit() for c in n) and n not in GENERICAS and (t[0].isupper() or t.isupper()) and not ini and n not in q:
            out.append(n)
        ini = t.endswith((".", ":", "?", "!"))
    return list(dict.fromkeys(out))


def classificar_niveis(resposta: str, pergunta: str, por_publicacao: dict[str, list[tuple[str, str]]], contexto_geral: list[str], lista: bool) -> dict:
    """Niveis de evidencia por termo especifico da resposta (Etapa 4.4):
      encontrada  - o termo aparece em algum trecho do contexto enviado (qualquer publicacao);
      atribuivel  - o termo aparece na evidencia (citacao verificada / candidata literal) de uma publicacao CITADA, com origem registrada;
      suficiente  - (decisao final, calculada com o alinhamento) todos os termos atribuiveis e, em resposta que NAO e lista, a mesma publicacao
                    sustenta todos eles: evidencias de publicacoes diferentes nunca se combinam para aprovar uma resposta unica.
    `por_publicacao`: {chave_da_publicacao: [(origem, texto)]}. Retorna {'termos', 'encontrada_so_em_outra_publicacao', 'sem_evidencia',
    'publicacao_unica', 'atribuicao': {termo: [(publicacao, origem)]}}."""
    termos = termos_especificos_da_resposta(resposta, pergunta)
    ctx = _sem_esp(_nf(" ".join(contexto_geral)))
    atrib: dict[str, list[tuple[str, str]]] = {}
    for t in termos:
        for pub, fontes in por_publicacao.items():
            for origem, texto in fontes:
                alvo = _sem_esp(_nf(texto)) if any(c.isdigit() for c in t) else _nf(texto)
                if t in alvo:
                    atrib.setdefault(t, []).append((pub, origem))
                    break
    sem = [t for t in termos if t not in atrib]
    so_outra = [t for t in sem if t in ctx]
    unica = True
    if termos and not lista and not sem:
        unica = any(all(any(p == pub for p, _ in atrib[t]) for t in termos) for pub in por_publicacao)
    return {"termos": termos, "sem_evidencia": sem, "encontrada_so_em_outra_publicacao": so_outra, "publicacao_unica": unica, "atribuicao": atrib}


# ------------------------------------------------------------------ Etapa 4.4 (Fase 3) - M1: ausencia, remissao e cobertura
_NEG = re.compile(r"\bn[aã]o (?:foi|foram|h[aá]|consta\w*|especific\w*|mencion\w*|informa\w*|identific\w*|dispon\w*|existe\w*)\b|\bsem (?:informa|especifica|men)", re.I)
_ATRIB_HEAD = re.compile(r"^\s*(?:at[eé]\s+)?(qual|quais|quanto|quantos|quantas)\b(?:\s+(?:[eé]|s[aã]o|era|eram|foi|foram|ser[aá]|ser[aã]o))?(?:\s+(?:o|a|os|as|um|uma))?\s+([\wÀ-ÿ]+)", re.I)


def afirmacao_negativa(resposta: str) -> str | None:
    """Trecho da resposta que afirma ausencia/omissao de informacao ('nao foram especificadas', 'nao consta', 'nao especifica'...) segundo uma
    gramatica fechada; None se nao houver."""
    m = _NEG.search(resposta or "")
    return m.group(0) if m else None


def cabeca_do_atributo(pergunta: str) -> str | None:
    """Substantivo-cabeca do atributo pedido, sem acento e em minusculas ('Quais especialidades medicas...' -> 'especialidades';
    'Qual e o valor autorizado...' -> 'valor'; 'Quem...' -> 'quem'; 'Quando/Ate quando...' -> 'quando'). None se a pergunta nao segue o molde."""
    if re.match(r"^\s*quem\b", pergunta or "", re.I):
        return "quem"
    if re.match(r"^\s*(?:at[eé]\s+)?quando\b", pergunta or "", re.I):
        return "quando"
    m = _ATRIB_HEAD.match(pergunta or "")
    return _nf(m.group(2)) if m else None


_REMISSAO = re.compile(r"(?:elencad|listad|relacionad|descrit|constant|indicad|previst)\w*\s+(?:na|no|nos|nas|em)\s+(?:\w+\s+){0,2}?"
                       r"(?P<doc>carta|anexo|proposta|tabela|planilha|documento|doc)(?P<ref>[^.;]{0,50})")
_SEI = re.compile(r"sei\s*(?:n[ºo°]?\s*)?(\d{6,})")


def remissao_a_anexo(texto: str, cabeca: str | None) -> dict | None:
    """O atributo pedido (`cabeca`) aparece no texto apenas por REMISSAO a documento/anexo ('especialidades elencadas na carta proposta doc. SEI n 160...').
    Retorna {'atributo', 'documento', 'sei'} ou None. Nao decide se o valor esta publicado em outro lugar: so que ESTA publicacao remete a outro documento."""
    if not cabeca:
        return None
    t = _nf(texto)
    rad = cabeca[:7]
    for m in _REMISSAO.finditer(t):
        antes = re.findall(r"\w+", t[max(0, m.start() - 60):m.start()])[-3:]          # o atributo vem logo antes do verbo ('especialidades elencadas na ...')
        if any(w.startswith(rad) for w in antes):
            s = _SEI.search(t[m.end("doc"):m.end("doc") + 90])
            return {"atributo": cabeca, "documento": m.group("doc"), "sei": s.group(1) if s else None}
    return None


def cobertura_da_publicacao(grupos: dict[str, list[dict]]) -> dict[str, dict]:
    """`grupos`: {publicacao: [{'ordem': int|None, 'n_chunks_doc': int|None, 'chunk_id': str}, ...]} (chunks da publicacao presentes no CONTEXTO).
    Retorna por publicacao {'total', 'analisados', 'completa'}; 'completa' so e True quando o total e conhecido e todos os trechos foram analisados."""
    out = {}
    for pub, its in grupos.items():
        tot = max([i["n_chunks_doc"] for i in its if i.get("n_chunks_doc")] or [0]) or None
        ordens = {i.get("ordem") if i.get("ordem") is not None else i["chunk_id"] for i in its}
        out[pub] = {"total": tot, "analisados": len(ordens), "completa": bool(tot) and len(ordens) >= tot}
    return out


# ------------------------------------------------------------------ Etapa 4.4 (Fase 3) - M2: atributo pedido x rotulo do valor
# Familias fechadas e auditaveis. Os rotulos vem da frequencia de '<rotulo>:' no corpus (compete 1.200, empresa 459, valor 464, objeto 361, partes 267,
# vigencia 233, responsavel 160, endereco 133, ...). So um CONFLITO entre familias CONHECIDAS bloqueia; rotulo ou atributo desconhecido nunca bloqueia.
FAM_ATRIBUTO = {
    "objeto": "OBJETO", "finalidade": "OBJETO", "servico": "OBJETO", "servicos": "OBJETO", "aquisicao": "OBJETO", "fornecimento": "OBJETO",
    "especialidade": "ESPECIALIDADE", "especialidades": "ESPECIALIDADE",
    "valor": "VALOR", "preco": "VALOR", "custo": "VALOR", "montante": "VALOR",
    "prazo": "PRAZO", "vigencia": "PRAZO", "validade": "PRAZO", "duracao": "PRAZO",
    "competencia": "COMPETENCIA", "competencias": "COMPETENCIA", "atribuicao": "COMPETENCIA", "atribuicoes": "COMPETENCIA", "funcao": "COMPETENCIA", "funcoes": "COMPETENCIA",
    "empresa": "PARTE", "empresas": "PARTE", "fornecedor": "PARTE", "contratada": "PARTE", "instituicao": "PARTE", "vencedora": "PARTE", "proponente": "PARTE",
    "membro": "MEMBRO", "membros": "MEMBRO", "integrante": "MEMBRO", "integrantes": "MEMBRO", "composicao": "MEMBRO",
    "responsavel": "RESPONSAVEL", "responsaveis": "RESPONSAVEL",
    "motivo": "MOTIVO", "razao": "MOTIVO", "causa": "MOTIVO", "fundamento": "MOTIVO",
    "endereco": "ENDERECO", "localizacao": "ENDERECO",
}
FAM_ROTULO = {
    "objeto": "OBJETO", "finalidade": "OBJETO",
    "especialidade": "ESPECIALIDADE", "especialidades": "ESPECIALIDADE",
    "valor": "VALOR", "preco": "VALOR",
    "vigencia": "PRAZO", "prazo": "PRAZO", "validade": "PRAZO",
    "compete": "COMPETENCIA", "competencia": "COMPETENCIA", "atribuicoes": "COMPETENCIA", "atribuicao": "COMPETENCIA", "cabe": "COMPETENCIA",
    "empresa": "PARTE", "interessado": "PARTE", "vencedora": "PARTE", "contratada": "PARTE", "proponente": "PARTE", "firma": "PARTE", "partes": "PARTE", "credenciada": "PARTE",
    "titular": "MEMBRO", "suplente": "MEMBRO", "membro": "MEMBRO", "membros": "MEMBRO", "integrantes": "MEMBRO", "composicao": "MEMBRO",
    "responsavel": "RESPONSAVEL", "responsaveis": "RESPONSAVEL", "signatarios": "RESPONSAVEL", "relator": "RESPONSAVEL",
    "motivo": "MOTIVO", "fundamento": "MOTIVO",
    "endereco": "ENDERECO",
}
# familias do rotulo que podem legitimamente responder a cada familia de atributo
COMPATIVEL = {
    "OBJETO": {"OBJETO", "ESPECIALIDADE"}, "ESPECIALIDADE": {"ESPECIALIDADE"}, "VALOR": {"VALOR"}, "PRAZO": {"PRAZO"}, "COMPETENCIA": {"COMPETENCIA"},
    "PARTE": {"PARTE"}, "MEMBRO": {"MEMBRO", "RESPONSAVEL"}, "RESPONSAVEL": {"RESPONSAVEL", "MEMBRO", "PARTE"}, "MOTIVO": {"MOTIVO", "OBJETO"}, "ENDERECO": {"ENDERECO"},
}


def _fold1(t: str) -> str:
    """Normalizacao que PRESERVA o comprimento (acento/caixa), para indexar o texto original."""
    import unicodedata
    return "".join((unicodedata.normalize("NFKD", c)[:1] or c).lower() for c in unicodedata.normalize("NFC", t or ""))


def familia_do_atributo(cabeca: str | None) -> str | None:
    return FAM_ATRIBUTO.get(cabeca or "")


def rotulo_do_valor(texto: str, valor: str) -> dict | None:
    """Rotulo que o proprio texto da ao `valor` ('cujo objeto E <valor>', 'Valor do Contrato: <valor>', 'Titular: <valor>').
    Procura (a) um prefixo 'rotulo:' no proprio valor e (b) 'rotulo e|:|-' imediatamente antes dele no texto. Retorna {'rotulo','familia'} ou None
    (rotulo desconhecido)."""
    ft, fv = _fold1(texto), _fold1(valor).strip()
    cands = []
    m = re.match(r"\s*([a-z][a-z ]{1,38}?)\s*:", fv)
    if m:
        cands.append(m.group(1))
    i = ft.find(fv[:40]) if fv else -1
    if i >= 0:
        m2 = re.search(r"([a-z]+(?:\s+(?:de|do|da|dos|das)\s+[a-z]+)?(?:\s+[a-z]+){0,1})\s*(?:\be\b|:|-|–|=)\s*$", ft[max(0, i - 60):i])
        if m2:
            cands.append(m2.group(1))
    for c in cands:
        for w in reversed(re.findall(r"[a-z]+", c)):
            if w in FAM_ROTULO:
                return {"rotulo": w, "familia": FAM_ROTULO[w]}
    return None


def conflito_atributo_rotulo(cabeca: str | None, rotulo: dict | None) -> bool:
    """True so quando atributo e rotulo sao de familias CONHECIDAS e incompativeis."""
    fa = familia_do_atributo(cabeca)
    return bool(fa and rotulo and rotulo["familia"] not in COMPATIVEL.get(fa, {fa}))


# ------------------------------------------------------------------ Etapa 4.4 (Fase 3) - M3: item de lista x resposta conclusiva
_SEG = re.compile(r"\s*(?:\s[-–]\s|[;,])\s*")


def _segmentos(valor: str) -> list[str]:
    return [s.strip() for s in _SEG.split((valor or "").strip()) if s.strip()]


def item_do_registro(valor: str, n: int = 3) -> str:
    """Chave do registro: os `n` primeiros segmentos do valor ('402 - Anestesiologia - Hospital Regional do Gama (HRG)'), sem o restante (dados pessoais, notas...).
    E sempre um PREFIXO literal do valor verificado."""
    seg = _segmentos(valor)[:n]
    return " - ".join(seg)


def molde_do_registro(valor: str) -> re.Pattern | None:
    """Molde (regex) da abertura do registro, a partir dos 3 primeiros segmentos do valor: numeros -> \\d+, palavras -> ate 4 palavras.
    So existe se o registro abre com um segmento numerico (codigo/numero de ordem) e tem >= 2 segmentos."""
    seg = _segmentos(valor)[:3]
    if len(seg) < 2 or not re.fullmatch(r"[\d.]+", seg[0]):
        return None
    partes = [r"\d+" if re.fullmatch(r"[\d.]+", s) else r"[^\W\d_]+(?:\s[^\W\d_]+){0,4}" for s in seg]
    return re.compile(r"\s*[-–;,]\s*".join(partes))


def estrutura_de_lista(texto: str, valor: str, minimo: int = 3) -> dict | None:
    """O `valor` e UM registro de uma enumeracao: o mesmo molde de abertura (numero - termo - termo) se repete >= `minimo` vezes, com conteudos DIFERENTES, no chunk.
    Retorna {'registros', 'amostra'} ou None. Valor sem molde numerico (texto corrido) nunca e tratado como lista."""
    mol = molde_do_registro(valor)
    if mol is None:
        return None
    achados = {m.group(0).strip().lower() for m in mol.finditer(texto or "")}
    return {"registros": len(achados), "amostra": sorted(achados)[:3]} if len(achados) >= minimo else None


def exclusividade(resposta: str, cabeca: str | None) -> bool:
    """A resposta apresenta UM item como a resposta ('O programa ... e Anestesiologia') para uma pergunta cujo atributo e plural: a cabeca da pergunta aparece
    no singular, ligada por 'e/foi' ao item, sem marcador de enumeracao parcial (inclui, entre, dentre, alem de...)."""
    if not cabeca or not cabeca.endswith("s") or len(cabeca) < 5:
        return False
    t = _nf(resposta)
    if re.search(r"\b(?:entre|dentre|inclui|incluem|alem de|como|tais como|por exemplo)\b", t):
        return False
    return bool(re.search(rf"\b{cabeca[:-1]}\w*\b[^.]{{0,110}}?\b(?:e|foi|sao|foram)\b\s", t))


# ------------------------------------------------------------------ Etapa 4.4 (Fase 3) - M4: periodos semanticamente equivalentes
_D_NUM = r"\d{1,2}/\d{1,2}/\d{4}"
_D_EXT = r"\d{1,2}\s*(?:o|º)?\s+de\s+(?:" + "|".join(MESES) + r")(?:\s+de\s+\d{4})?"
_D_ANY = rf"(?:{_D_NUM}|{_D_EXT})"
_PAR_DATAS = re.compile(rf"(?P<d1>{_D_ANY})\s+(?:a|ate|e)\s+(?P<d2>{_D_ANY})")


def _para_data(s: str, ano_padrao: int | None = None) -> tuple[int, int, int] | None:
    s = _nf(s)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return int(m.group(3)), int(m.group(2)), int(m.group(1))
    m = re.fullmatch(r"(\d{1,2})\s*(?:o|º)?\s+de\s+(\w+)(?:\s+de\s+(\d{4}))?", s)
    if m and m.group(2) in MESES:
        ano = int(m.group(3)) if m.group(3) else ano_padrao
        return (ano, MESES[m.group(2)], int(m.group(1))) if ano else None
    return None


def _tipo_do_contexto(antes: str, padrao: str) -> str:
    a = _nf(antes)
    if re.search(r"vig[eê]nc|vigent", a):
        return "vigencia"
    if re.search(r"execu", a):
        return "execucao"
    if re.search(r"publica", a):
        return "publicacao"
    return padrao


def periodo_da_pergunta(pergunta: str) -> dict | None:
    """Intervalo de datas pedido ('no periodo de 31 de julho a 22 de agosto de 2025', 'entre 01/07/2025 e 31/07/2025') e seu TIPO:
    vigencia | execucao | publicacao | generico (periodo de referencia/execucao dos atos). None se a pergunta nao traz intervalo."""
    n = _nf(pergunta)
    m = _PAR_DATAS.search(n)
    if not m:
        return None
    d2 = _para_data(m.group("d2"))
    d1 = _para_data(m.group("d1"), d2[0] if d2 else None)
    if not (d1 and d2):
        return None
    return {"inicio": d1, "fim": d2, "tipo": _tipo_do_contexto(n[max(0, m.start() - 60):m.start()], "generico")}


_DECL = re.compile(rf"(?P<rot>vigencia|periodo)\b[^.;]{{0,60}}?(?:\bde\s+)?(?P<d1>{_D_NUM})\s+(?:a|ate)\s+(?P<d2>{_D_NUM})")


def periodos_declarados(texto: str) -> list[dict]:
    """Periodos que a PUBLICACAO declara para si, com o tipo: 'vigencia ... de d1 a d2' -> vigencia; 'no periodo de d1 a d2' -> referencia (ou execucao,
    se 'execucao' vier logo antes). Datas de assinatura/ratificacao/edicao NAO sao periodos."""
    t = _nf(texto)
    out = []
    for m in _DECL.finditer(t):
        d1, d2 = _para_data(m.group("d1")), _para_data(m.group("d2"))
        if not (d1 and d2):
            continue
        tipo = "vigencia" if m.group("rot") == "vigencia" else ("execucao" if re.search(r"execu", t[max(0, m.start() - 40):m.start()]) else "referencia")
        out.append({"tipo": tipo, "inicio": d1, "fim": d2, "trecho": t[max(0, m.start() - 20):m.end()]})
    return out


COMPATIVEL_PERIODO = {"generico": {"referencia", "execucao"}, "execucao": {"execucao", "referencia"}, "vigencia": {"vigencia"}}


def periodos_incompativeis(pedido: dict | None, declarados: list[dict], data_edicao: str | None = None) -> list[dict]:
    """Periodos da publicacao que NAO se sobrepoem ao pedido, comparando apenas periodos do MESMO sentido (vigencia x vigencia; periodo de referencia/execucao dos atos x
    periodo generico ou de execucao). 'publicacao' compara com a data da edicao. Periodos de outro sentido sao ignorados (nao ha bloqueio)."""
    if not pedido:
        return []
    out = []
    if pedido["tipo"] == "publicacao":
        m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(data_edicao or ""))
        if m:
            d = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if not (pedido["inicio"] <= d <= pedido["fim"]):
                out.append({"tipo": "publicacao", "inicio": d, "fim": d, "trecho": f"data da edicao {data_edicao}"})
        return out
    ok = COMPATIVEL_PERIODO.get(pedido["tipo"], set())
    for d in declarados:
        if d["tipo"] in ok and (d["fim"] < pedido["inicio"] or d["inicio"] > pedido["fim"]):
            out.append(d)
    return out


# ------------------------------------------------------------------ Etapa 4.4 (Fase 3) - M5: identificador x localidade por ASSOCIACAO ESTRUTURAL
# So decide quando o identificador (CNPJ) esta ligado a localidade por estrutura: (a) o mesmo REGISTRO numerado ('Matriz:', 'Filial (3):', 'Unidade 2:') ou
# (b) o mesmo campo rotulado ('CNPJ: x, ENDERECO: ...' / 'ENDERECO: ... CNPJ: x'). Proximidade textual sozinha NAO e associacao.
REGIOES = {"sudoeste", "sudeste", "norte", "sul", "leste", "oeste", "centro-sul", "centro sul", "centro-norte"}      # regioes de saude: contem cidades, nunca entram em conflito
_CNPJ = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")
_CAB_REGISTRO = re.compile(r"(?:matriz|filial\s*\(\d+\)|filial\s*\d+|unidade\s*\(\d+\)|unidade\s+\d+)\s*[:\-–]")


def cnpjs(texto: str) -> list[str]:
    return list(dict.fromkeys(_CNPJ.findall(texto or "")))


def _localidades_em(trecho_folded: str, gazetario: list[str]) -> list[str]:
    achadas = [g for g in gazetario if re.search(rf"(?<![a-z]){re.escape(g)}(?![a-z])", trecho_folded)]
    return [g for g in achadas if not any(g != h and g in h for h in achadas)]          # 'riacho fundo' dentro de 'riacho fundo ii' nao conta


def associacao_estrutural(texto: str, ident: str, gazetario: list[str], nomes: list[str] | None = None) -> dict | None:
    """Associacao ESTRUTURAL entre o identificador e (i) localidades e (ii) nomes de entidades. Retorna
    {'via': 'registro_numerado'|'rotulo_endereco', 'localidades': [...], 'nomes_no_registro': [...], 'nomes_em_outros_registros': [...]} ou None quando
    o identificador nao esta no texto ou nao ha estrutura confiavel (nesse caso NAO ha decisao)."""
    ft = _fold1(texto)
    i = ft.find(ident.lower())
    if i < 0:
        return None
    cab = [m.start() for m in _CAB_REGISTRO.finditer(ft)]
    nomes = [n for n in (nomes or [])]
    if len(cab) >= 2 and any(c <= i for c in cab):
        limites = list(zip(cab, cab[1:] + [len(ft)]))
        ini = max(c for c in cab if c <= i)
        fim = min([c for c in cab if c > i] or [len(ft)])
        reg = ft[ini:fim]
        registros = [ft[a:b] for a, b in limites]
        # nomes DISCRIMINATIVOS: aparecem em exatamente um registro do chunk (nomes presentes em todos, como 'cnpj', nao identificam a entidade)
        discr = {n: [k for k, r in enumerate(registros) if n in r] for n in nomes}
        discr = {n: ks for n, ks in discr.items() if len(ks) == 1}
        k_reg = next(k for k, (a, b) in enumerate(limites) if a == ini)
        no_reg = [n for n, ks in discr.items() if ks[0] == k_reg]
        outros = [n for n, ks in discr.items() if ks[0] != k_reg]
        return {"via": "registro_numerado", "localidades": _localidades_em(reg, gazetario), "nomes_no_registro": no_reg,
                "nomes_em_outros_registros": outros if not no_reg else []}
    m = (re.search(rf"cnpj\W{{0,6}}{re.escape(ident.lower())}[^;]{{0,40}}?endereco\s*:\s*(?P<a>[^;]{{0,200}})", ft)
         or re.search(rf"endereco\s*:\s*(?P<a>[^;]{{0,200}}?)[,;.]?\s*cnpj\W{{0,6}}{re.escape(ident.lower())}", ft))
    if m:
        end = re.split(r"telefone|e-?mail|\bcep\b|cnpj", m.group("a"))[0]
        return {"via": "rotulo_endereco", "localidades": _localidades_em(end, gazetario), "nomes_no_registro": [], "nomes_em_outros_registros": []}
    return None


# ------------------------------------------------------------------ Etapa 4.4 / Fase 4A - Mecanismo C: registro auditavel das relacoes (esquema relacoes/2)
SCHEMA_RELACOES = "relacoes/3"
_RE_RATIFICO = re.compile(r"\bratifico\b")
_RE_SEI = re.compile(r"processo sei n[.ºo°]*\s*([\d./-]{8,})")


def registro_do_trecho(texto: str, valor: str) -> dict | None:
    """Registro ESTRUTURAL do chunk que contem o `valor`: (a) registro numerado ('Matriz:', 'Filial (n):'; id = o proprio cabecalho) ou (b) segmento de
    ratificacao (de um 'RATIFICO' ao proximo; id = 'Processo SEI n' do segmento, quando existe). Retorna {'tipo','id','inicio','fim'} (posicoes no texto
    normalizado de mesmo comprimento) ou None. NUNCA inventa identificador: sem estrutura reconhecivel, nao ha registro."""
    ft, fv = _fold1(texto), _fold1(valor).strip()
    i = ft.find(fv[:40]) if fv else -1
    if i < 0:
        return None
    cab = [m.start() for m in _CAB_REGISTRO.finditer(ft)]
    if len(cab) >= 2 and any(c <= i for c in cab):
        ini, fim = max(c for c in cab if c <= i), min([c for c in cab if c > i] or [len(ft)])
        return {"tipo": "numerado", "id": re.split(r"[:\-–]", ft[ini:fim], maxsplit=1)[0].strip(), "inicio": ini, "fim": fim}
    rat = [m.start() for m in _RE_RATIFICO.finditer(ft)]
    if len(rat) >= 2:
        ini, fim = max([r for r in rat if r <= i] or [0]), min([r for r in rat if r > i] or [len(ft)])
        sei = _RE_SEI.search(ft[ini:fim])
        return {"tipo": "ratificacao", "id": f"SEI {sei.group(1).strip('.,;')}" if sei else None, "inicio": ini, "fim": fim}
    return None


# ------------------------------------------------------------------ Etapa 4.4 / Fase 4A - Mecanismo B: conflito de rotulos so quando o trecho SUSTENTA um termo da resposta
def termos_de_conteudo(resposta: str, pergunta: str) -> list[str]:
    """Termos da resposta que carregam o seu conteudo e que NAO vieram da pergunta: palavras de >= 6 letras (radical de 6), siglas/nomes em maiusculas com >= 3 letras
    e numeros com >= 3 digitos. Palavras genericas e palavras da pergunta ficam de fora."""
    q = _nf(pergunta)
    qrad = {_radical(w) for w in re.findall(r"[\w]+", q) if len(w) >= 6}
    out = []
    for t in _tokens(resposta):
        n = _nf(t).strip(".-/,;:()")
        if not n or n in GENERICAS or n in q.split():
            continue
        dig = re.sub(r"\D", "", n)
        if dig and len(dig) >= 3:
            out.append("#" + dig)
        elif not any(c.isdigit() for c in n) and ((len(n) >= 6 and _radical(n) not in qrad) or (t.strip(".-/,;:()").isupper() and len(n) >= 3 and n not in q.split())):
            out.append(n)
    return list(dict.fromkeys(out))


def apoio_exclusivo(unidades: dict[str, str], termos: list[str]) -> dict[str, list[str]]:
    """Para cada unidade de evidencia (um chunk citado: seus trechos), os termos que SO ela sustenta. Sem termos, nao ha como medir: todas as unidades
    contam como necessarias (comportamento conservador da Fase 3)."""
    nf = {u: _nf(t) for u, t in unidades.items()}
    sem = {u: _sem_esp(t) for u, t in nf.items()}

    def apoia(u: str, t: str) -> bool:
        return (t[1:] in sem[u]) if t.startswith("#") else ((_radical(t) in nf[u]) if len(t) >= 6 else bool(re.search(rf"\b{re.escape(t)}\b", nf[u])))
    if not termos:
        return {u: ["(sem termos de conteudo: unidade tratada como necessaria)"] for u in unidades}
    return {u: [t for t in termos if apoia(u, t) and not any(apoia(v, t) for v in unidades if v != u)] for u in unidades}


def cue_de_atributo(texto: str, familia_atributo: str | None) -> str | None:
    """Palavra do PROPRIO trecho que pertence a uma familia de rotulo compativel com o atributo pedido ('compete', 'competencia', 'atribuicoes'...).
    Se existe, um rotulo conflitante no inicio do trecho ('Titular: ...') nao basta para bloquear: a relacao e semantica e fica 'nao verificavel'."""
    if not familia_atributo:
        return None
    ok = COMPATIVEL.get(familia_atributo, {familia_atributo})
    for w in re.findall(r"[a-z]+", _nf(texto)):
        if FAM_ROTULO.get(w) in ok:
            return w
    return None


# ------------------------------------------------------------------ Etapa 4.4 / Fase 4A - Mecanismo A: associacao evidencia x destinatario x localidade da publicacao
_RE_DEST = re.compile(r"necessidades\s+(?:da|do|de|dos|das)\s+(?P<d>[^,;.]{3,90})")
_CORTE_DEST = re.compile(r"\s+(?:em|no|na|nos|nas|durante|conforme|entre|desde|ate)\s+(?:\d|janeiro|fevereiro|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro|periodo)|\s+(?:no|na)\s+(?!periodo)")
_STOP_DEST = {"para", "atender", "necessidades", "unidade", "unidades"}


def destinatario_da_pergunta(pergunta: str) -> str | None:
    """Destinatario pedido: 'para atender as necessidades da Atencao Primaria no Guara?' -> 'atencao primaria'; 'adquiridos para o Hospital Regional de Taguatinga?' ->
    'hospital regional de taguatinga'. A localidade que vem depois de 'no/na' e tratada a parte (nao e o destinatario). None se a pergunta nao traz destinatario."""
    n = _nf(pergunta).rstrip("?. ")
    m = _RE_DEST.search(n) or re.search(r"\bpara\s+(?:o|a|os|as)\s+(?P<d>[^?.,;]{3,90})", n)
    if not m:
        return None
    d = m.group("d")
    cut = _CORTE_DEST.search(d)
    return (d[:cut.start()] if cut else d).strip() or None


def destinatario_no_registro(texto: str, valor: str) -> dict | None:
    """Destinatario DECLARADO pelo registro do valor: a clausula 'para atender as necessidades d[ao] X' que vem depois do item, dentro do mesmo registro
    (limitado pelo proximo 'RATIFICO' ou 'cujo objeto' e por 300 caracteres). Retorna {'destinatario','posicao'} ou None: a mera presenca de uma localidade no
    documento NAO e destinatario."""
    ft, fv = _fold1(texto), _fold1(valor).strip()
    i = ft.find(fv[:40]) if fv else -1
    if i < 0:
        return None
    ini_busca = i
    fim = min(len(ft), i + len(fv) + 300)
    for marca in ("ratifico", "cujo objeto"):
        j = ft.find(marca, i + max(10, len(fv) // 2))
        if j != -1:
            fim = min(fim, j)
    m = _RE_DEST.search(ft, ini_busca, fim)
    return {"destinatario": m.group("d").strip(), "posicao": m.start()} if m else None


def _tokens_dest(d: str, gaz: list[str]) -> tuple[set[str], set[str]]:
    loc = {g for g in gaz if re.search(rf"(?<![a-z]){re.escape(g)}(?![a-z])", d)}
    loc_tokens = {w for g in loc for w in g.split()}
    toks = {w for w in re.findall(r"[a-z]{4,}", d) if w not in _STOP_DEST}
    return toks - loc_tokens, loc


def comparar_destinatarios(dq: str | None, dt: str | None, gaz: list[str]) -> dict:
    """Estado da associacao com o destinatario: confirmada (mesmo destinatario; localidades, se ambas existem, coincidem), conflitante (destinatario declarado diferente
    do pedido, ou mesma unidade generica em localidade diferente) ou nao_verificavel (um dos lados sem destinatario)."""
    if not dq or not dt:
        return {"estado": "nao_verificavel", "justificativa": "destinatario ausente na pergunta ou no registro do trecho"}
    tq, lq = _tokens_dest(dq, gaz)
    tt, lt = _tokens_dest(dt, gaz)
    if tq & tt:
        if lq and lt and not (lq & lt):
            return {"estado": "conflitante", "justificativa": f"mesma unidade ('{', '.join(sorted(tq & tt))}'), mas localidade do registro ({', '.join(sorted(lt))}) difere da pedida ({', '.join(sorted(lq))})"}
        return {"estado": "confirmada", "justificativa": f"destinatario do registro ('{dt}') coincide com o pedido ('{dq}')"}
    if tq and tt:
        return {"estado": "conflitante", "justificativa": f"o registro destina o item a '{dt}', e a pergunta trata de '{dq}'"}
    return {"estado": "nao_verificavel", "justificativa": "destinatarios sem termos comparaveis"}


def grupos_de_trechos(texto: str, spans: list[str]) -> list[list[int]]:
    """Agrupa trechos (candidata literal e citacao do MESMO item) que se sobrepoem no chunk: um item = um grupo. Trechos nao localizados formam grupo proprio."""
    ft = _fold1(texto)
    pos = []
    for k, s in enumerate(spans):
        fs = _fold1(s).strip()
        i = ft.find(fs[:40]) if fs else -1
        pos.append((i, i + len(fs), k) if i >= 0 else (-1 - k, -1 - k, k))
    grupos: list[list[int]] = []
    atual_fim = None
    for ini, fim, k in sorted(pos):
        if grupos and atual_fim is not None and ini < atual_fim and ini >= 0:
            grupos[-1].append(k)
            atual_fim = max(atual_fim, fim)
        else:
            grupos.append([k])
            atual_fim = fim
    return grupos


# ------------------------------------------------------------------ Etapa 4.4 / Fase 4B (preparacao) - Mecanismo B v2: uso do trecho sem limiar de comprimento
# Classe fechada de palavras funcionais do portugues (artigos, preposicoes, conjuncoes, pronomes, verbos de ligacao). Nao e um limiar de caracteres: "12" e "HRG" contam;
# "de", "o", "que" nao. Um termo so e de USO quando nao vem da pergunta, nao e funcional/generico e e apoiado por algum trecho citado.
PALAVRAS_FUNCIONAIS = frozenset("""a o as os um uma uns umas de do da dos das em no na nos nas por pelo pela pelos pelas para pra com sem sob sobre entre ate ao aos
a e ou mas que se como quando onde qual quais quem quanto quantos quantas foi foram eh e sao era eram sera serao ser sendo tem teve ha haver ter ja nao mais muito
sim nem este esta esse essa isto isso aquele aquela seu sua seus suas lhe me te nos vos eu tu ele ela eles elas meu minha""".split())
_TOK_USO = re.compile(r"\d+(?:[.,/]\d+)*|[^\W\d_]+", re.UNICODE)


def tokens_de_uso(texto: str) -> list[str]:
    """Tokens normalizados (sem acento/caixa); numeros viram so digitos ('12,00' -> '1200')."""
    out = []
    for t in _TOK_USO.findall(_nf(texto)):
        out.append(re.sub(r"\D", "", t) if t[0].isdigit() else t)
    return out


def termos_de_uso(resposta: str, pergunta: str) -> list[str]:
    """Termos da RESPOSTA que podem mostrar qual trecho a sustenta: tudo que nao e palavra funcional, generica ou da pergunta (inclusive por flexao: mesmo radical
    de 6 letras). Sem limiar de tamanho para decidir relevancia."""
    q = set(tokens_de_uso(pergunta))
    qrad = {_radical(w) for w in q if len(w) >= 6 and not w.isdigit()}
    out = []
    for t in tokens_de_uso(resposta):
        if not t or t in PALAVRAS_FUNCIONAIS or t in GENERICAS or t in q or (len(t) >= 6 and not t.isdigit() and _radical(t) in qrad):
            continue
        out.append(t)
    return list(dict.fromkeys(out))


def suporte_por_unidade(unidades: dict[str, str], termos: list[str]) -> dict:
    """Quais unidades (grupos de trechos) apoiam cada termo. Retorna {'medida': 'termos_apoiados'|'nao_mensuravel', 'suporte': {termo: [unidades]}}.
    So termos apoiados por ao menos uma unidade medem uso; se nenhum termo e apoiado (ex.: 'Sim.'), o uso NAO e mensuravel e quem decide mantem o comportamento
    fail-closed."""
    toks = {u: set(tokens_de_uso(t)) for u, t in unidades.items()}
    rad = {u: {_radical(w) for w in s if len(w) >= 6 and not w.isdigit()} for u, s in toks.items()}
    sup: dict[str, list[str]] = {}
    for t in termos:
        us = [u for u in unidades if t in toks[u] or (len(t) >= 6 and not t.isdigit() and _radical(t) in rad[u])]
        if us:
            sup[t] = us
    return {"medida": "termos_apoiados" if sup else "nao_mensuravel", "suporte": sup}


# ------------------------------------------------------------------ Etapa 4.4 / Fase 4B (preparacao) - relacoes/3: dimensoes separadas
ESTADOS_DIM = ("confirmada", "conflitante", "nao_verificavel", "nao_aplicavel")


def dimensoes_da_relacao(*, nomes_q, nomes_no_trecho, cab, fam, rot, estado_rotulo, cue, dq, dt, cmp, lq, loc_registro, loc_pub) -> dict:
    """Uma associacao por DIMENSAO (entidade, destinatario, atributo, localidade), cada uma com estado, justificativa e origem. Confirmar uma dimensao NUNCA confirma outra:
    `estado_geral` so e 'confirmada' se todas as dimensoes aplicaveis estiverem confirmadas; qualquer conflito -> 'conflitante'; senao 'nao_verificavel'.
    Os campos de relacoes/2 permanecem na relacao (compatibilidade); estas dimensoes sao ADITIVAS e nao alteram nenhuma decisao do pipeline."""
    d = {}
    # entidade (nomes da pergunta presentes no registro do trecho)
    if not nomes_q:
        d["entidade"] = {"estado": "nao_aplicavel", "pedida": [], "encontrada": [], "justificativa": "a pergunta nao traz nome de entidade", "origem": "pergunta"}
    elif set(nomes_q) <= set(nomes_no_trecho):
        d["entidade"] = {"estado": "confirmada", "pedida": list(nomes_q), "encontrada": list(nomes_no_trecho), "justificativa": "todos os nomes da pergunta aparecem no registro do trecho", "origem": "registro"}
    else:
        d["entidade"] = {"estado": "nao_verificavel", "pedida": list(nomes_q), "encontrada": list(nomes_no_trecho), "justificativa": "nem todos os nomes da pergunta aparecem no registro do trecho (a entidade pode estar so no titulo/cabecalho)", "origem": "registro"}
    # destinatario
    if not dq:
        d["destinatario"] = {"estado": "nao_aplicavel", "pedido": None, "encontrado": dt, "justificativa": "a pergunta nao indica destinatario", "origem": "pergunta"}
    else:
        d["destinatario"] = {"estado": cmp["estado"], "pedido": dq, "encontrado": dt, "justificativa": cmp["justificativa"], "origem": "registro"}
    # atributo (rotulo do valor x atributo pedido)
    if fam is None:
        d["atributo"] = {"estado": "nao_aplicavel", "pedido": {"cabeca": cab, "familia": None}, "encontrado": rot, "justificativa": "a pergunta nao pede atributo de familia conhecida", "origem": "pergunta"}
    elif estado_rotulo == "compativel":
        d["atributo"] = {"estado": "confirmada", "pedido": {"cabeca": cab, "familia": fam}, "encontrado": rot, "justificativa": f"rotulo '{rot['rotulo']}' ({rot['familia']}) compativel com '{cab}'", "origem": "rotulo_do_valor"}
    elif estado_rotulo == "conflito" and cue is None:
        d["atributo"] = {"estado": "conflitante", "pedido": {"cabeca": cab, "familia": fam}, "encontrado": rot, "justificativa": f"rotulo '{rot['rotulo']}' ({rot['familia']}) incompativel com '{cab}'", "origem": "rotulo_do_valor"}
    elif estado_rotulo == "conflito":
        d["atributo"] = {"estado": "nao_verificavel", "pedido": {"cabeca": cab, "familia": fam}, "encontrado": rot, "justificativa": f"rotulo incompativel, mas o trecho contem '{cue}': relacao semantica nao verificada", "origem": "rotulo_do_valor"}
    else:
        d["atributo"] = {"estado": "nao_verificavel", "pedido": {"cabeca": cab, "familia": fam}, "encontrado": rot, "justificativa": "o trecho nao tem rotulo identificavel para o valor", "origem": "rotulo_do_valor"}
    # localidade
    if not lq:
        d["localidade"] = {"estado": "nao_aplicavel", "pedida": [], "encontrada": loc_registro, "justificativa": "a pergunta nao indica localidade", "origem": "pergunta"}
    elif loc_pub is False:
        d["localidade"] = {"estado": "conflitante", "pedida": list(lq), "encontrada": loc_registro, "justificativa": "a publicacao nao menciona a localidade perguntada", "origem": "publicacao"}
    elif loc_registro and set(lq) <= set(loc_registro):
        d["localidade"] = {"estado": "confirmada", "pedida": list(lq), "encontrada": loc_registro, "justificativa": "a localidade perguntada aparece no registro do trecho", "origem": "registro"}
    elif loc_pub is True:
        d["localidade"] = {"estado": "confirmada", "pedida": list(lq), "encontrada": loc_registro, "justificativa": "a publicacao menciona a localidade (vinculo da publicacao, nao do registro)", "origem": "publicacao"}
    else:
        d["localidade"] = {"estado": "nao_verificavel", "pedida": list(lq), "encontrada": loc_registro, "justificativa": "sem como verificar a localidade no registro nem na publicacao", "origem": "registro"}
    ap = [v["estado"] for v in d.values() if v["estado"] != "nao_aplicavel"]
    geral = "conflitante" if "conflitante" in ap else ("confirmada" if ap and all(x == "confirmada" for x in ap) else "nao_verificavel")
    return {"dimensoes": d, "estado_geral": geral}


# ------------------------------------------------------------------ Etapa 4.4 / Fase 4B (preparacao) - S1 forte: priorizacao de chunk por rotulo EXPLICITO do atributo pedido
_ENUM_INICIAL = re.compile(r"^\s*(?:(?:art|§)\.?\s*\d+\s*[ºo°]?|\d+\s*[ºo°]|\([a-z0-9]+\)|[ivxlcdm]+|\d+|[a-z])\s*(?:[-–—.):]\s*|(?=\s))", re.IGNORECASE)
_FRONT_CLAUSULA = re.compile(r"(?:(?<=[.;:!?])\s+|\n+)")


def rotulos_fortes(cab: str | None, fam: str | None) -> set[str]:
    """Rotulos que REPETEM o proprio atributo pedido (mesma familia e mesmo radical da cabeca: 'competencias' -> compete/competencia/competencias).
    Familias amplas de rotulos ('atribuicoes', 'finalidade' ...) nao entram: so a repeticao do atributo."""
    if not cab or not fam or len(cab) < 5:
        return set()
    return {w for w, f in FAM_ROTULO.items() if f == fam and w[:5] == cab[:5]}


def rotulo_forte_no_chunk(texto: str, cab: str | None, fam: str | None, nomes: list[str], texto_entidade: str | None = None) -> dict | None:
    """Procura, no texto de um chunk, um rotulo forte em POSICAO DE ROTULO (primeira palavra de uma clausula/item, ja sem enumerador 'IV -', 'Art. 4º', '1)', ou palavra
    seguida de ':') e exige associacao com a entidade da pergunta: todos os nomes salientes da pergunta aparecem no chunk OU na publicacao a que ele pertence
    (sem nome saliente na pergunta nao ha como associar a entidade: nao prioriza; `texto_entidade` = textos dos chunks recuperados do MESMO documento; um chunk de uma publicacao que trata da entidade herda a associacao). Ocorrencia incidental (a palavra no meio de uma
    frase) nao conta. Retorna {'rotulo', 'clausula'} ou None."""
    fortes = rotulos_fortes(cab, fam)
    if not fortes:
        return None
    ft = _nf(texto_entidade if texto_entidade is not None else texto)
    if not nomes or not all(n in ft for n in nomes):
        return None                                                                      # nem o chunk nem a publicacao estao associados a entidade da pergunta
    for cl in _FRONT_CLAUSULA.split(re.sub(r"(?i)(art|arts|inc|par)\.", r"", texto)):
        c = cl.strip()
        for _ in range(3):                                                               # ate 3 enumeradores empilhados ('Art. 4º IV - ...')
            m = _ENUM_INICIAL.match(c)
            if not m:
                break
            c = c[m.end():]
        ws = re.findall(r"[^\W\d_]+", _nf(c))
        if ws and ws[0] in fortes:
            return {"rotulo": ws[0], "clausula": c[:120]}
        m2 = re.match(r"\s*([^\W\d_]+)\s*:", _nf(c))
        if m2 and m2.group(1) in fortes:
            return {"rotulo": m2.group(1), "clausula": c[:120]}
    return None


# ------------------------------------------------------------------ Etapa 4.4 / Fase 4B (candidata) - S1 conservadora: cobertura ESTRUTURAL do atributo por um chunk
_QUANTIA = re.compile(r"R\$\s*\d")


def cobertura_do_chunk(texto: str, cab: str | None, fam: str | None, nomes: list[str]) -> dict | None:
    """Criterio ESTRUTURAL (nao semantico) de que um chunk ja selecionado cobre o atributo pedido para a entidade da pergunta. Cobre se:
    (a) todos os nomes salientes da pergunta estao NO PROPRIO chunk (outra entidade ou entidade nao identificavel => nao cobre) e
    (b) ha rotulo forte em posicao de rotulo (`rotulo_forte_no_chunk` com o proprio chunk como texto de entidade), ou
    (c) so para a familia VALOR: quantia monetaria em prosa ('R$ n').
    Nao ha forma tipada confiavel para as demais familias: sem rotulo explicito, nao presume cobertura. Nao garante que a evidencia responda a pergunta."""
    if not fam or not nomes:
        return None
    if not all(n in _nf(texto) for n in nomes):
        return None
    r = rotulo_forte_no_chunk(texto, cab, fam, nomes, texto)
    if r:
        return {"tipo": "rotulo", "detalhe": r["rotulo"]}
    if fam == "VALOR" and _QUANTIA.search(texto):
        return {"tipo": "valor_tipado", "detalhe": "R$"}
    return None
