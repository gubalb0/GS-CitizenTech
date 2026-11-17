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
