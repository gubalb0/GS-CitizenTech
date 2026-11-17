"""Fase 4D.5 - PROTOTIPO EXPERIMENTAL OFFLINE de vinculo entidade-atributo em nivel de frase. Nao integrado ao pipeline; deterministico; sem modelo.
Usa de `citizentech.assistente.evidencias` apenas funcoes puras de LEITURA (_fold1, termos_de_uso, cue_de_atributo, FAM_ROTULO, COMPATIVEL, _radical). Nada e alterado.

Modelo (ver MODELO_RELACIONAL_4D5.md): Publicacao -> Chunks -> Unidades (frases/registros); Afirmacao (clausula da resposta) com termos de atributo; Entidade (formas, tipo);
Relacao avaliada em quatro niveis: N1 mesma frase (exige relacao, nao so coocorrencia), N2 frases adjacentes com vinculo textual (anafora/introducao), N3 mesmo chunk (ingenuo),
N4 mesma publicacao (ingenuo). N3/N4 sao propositalmente ingenuos (qualquer ocorrencia) para medir falsos vinculos por proximidade."""
import math
import re
import sys

sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import evidencias as EV  # noqa: E402

F = EV._fold1
ABREV = {"art", "arts", "n", "inc", "par", "ltda", "dr", "dra", "sr", "sra", "ed", "cnpj", "proc", "fl", "fls", "av", "prof", "etc", "ex", "p", "pp", "s", "sei", "gdf", "df"}
_BORDA = re.compile(r"(?<=[.;])\s+(?=[A-ZÀ-Ú0-9\"“(])|(?<=[:;.])\s+(?=\d{1,3}\s*-\s*[A-ZÀ-Ú])|(?<=[:;.])\s+(?=[IVX]{1,5}\s*-\s+[A-ZÀ-Ú])|\s+(?=RATIFICO\b)|,\s+(?=CNPJ\b)")
CONECT_PROIBIDO = {"que", "observou", "afirmou", "disse", "informou", "declarou", "segundo"}
ANAFORA = re.compile(r"^(?:(?:a|o|essa|esse|esta|este)\s+(?:unidade|orgao|entidade|empresa|instituicao|coordenacao|comissao|contratada|regiao|localidade|hospital|policlinica)\b|(?:ela|ele|esta|este|essa|esse)\b)")
CONTINUACAO = re.compile(r"^(?:para (?:tanto|isso|esse fim)|ainda|alem disso|nesse sentido|no mesmo ato)\b")
PREP_ANTES = re.compile(r"(?:\b(?:d[oa]s?|n[oa]s?|em|de)\b)\s*$")
_ROT = re.compile(r"^\s*(?:\d{1,3}\s*[-–)]\s*|[IVX]{1,5}\s*[-–)]\s*)?([^\W\d_][^:\n]{0,38}):")


def segmentar(texto):
    cortes = [0]
    for m in _BORDA.finditer(texto):
        ant = re.search(r"([^\W_]+)\W*$", texto[:m.start() + 1].rstrip(".; "))
        palavra = (ant.group(1) if ant else "").lower()
        if texto[m.start() - 1:m.start()] == "." and (palavra in ABREV or len(palavra) == 1):
            continue
        cortes.append(m.end())
    cortes.append(len(texto) + 1)
    return [(a, b - 1) for a, b in zip(cortes, cortes[1:]) if texto[a:b - 1].strip()]


class Publicacao:
    def __init__(self, pid, texto, chunks):
        """chunks: dict chunk_id -> texto (substring do texto da publicacao). Unidades fora de qualquer chunk conhecido ficam com chunk=None (nao enviadas ao modelo)."""
        self.pid, self.texto, self.f = pid, texto, F(texto)
        self.ch = {}
        for cid, ct in chunks.items():
            i = texto.find(ct)
            if i >= 0:
                self.ch[cid] = (i, i + len(ct))
        self.un = []
        for k, (a, b) in enumerate(segmentar(texto)):
            self.un.append({"i": k, "ini": a, "fim": b, "txt": texto[a:b], "f": self.f[a:b], "chunks": [c for c, (x, y) in self.ch.items() if a < y and b > x]})

    def unidades_do_trecho(self, trecho):
        n = re.sub(r"\s+", " ", F(trecho)).strip()
        base = re.sub(r"\s+", " ", self.f)
        if not n:
            return []
        i = self.f.find(F(trecho))
        if i < 0:   # tolera diferenca de espacos: aproxima por unidades que contem metade das palavras do trecho
            pal = set(n.split())
            return [u for u in self.un if len(pal & set(u["f"].split())) >= max(2, len(pal) // 2)]
        j = i + len(F(trecho))
        return [u for u in self.un if u["ini"] < j and u["fim"] > i]


def _mencoes(unid, formas, tipo="organizacao"):
    """[(pos, forma, papel)]; papel 'parte_de_outra_entidade' quando a forma e precedida por preposicao + nome proprio capitalizado (ex.: 'Conselhos de Saude do Gama')."""
    out = []
    for fm in formas:
        for m in re.finditer(r"\b" + re.escape(fm) + r"\b", unid["f"]):
            orig_antes = unid["txt"][:m.start()]
            papel = "direta"
            mm = PREP_ANTES.search(F(orig_antes)) if tipo == "localidade" else None
            if mm:
                resto = orig_antes[:mm.start()].rstrip()
                pal = resto.split()[-1] if resto.split() else ""
                if pal[:1].isupper() and not resto.endswith(('.', ':', ';')):
                    papel = "parte_de_outra_entidade"
            out.append((m.start(), fm, papel))
    return sorted(out)


def _radicais(termos):
    return {t: EV._radical(t) if len(t) >= 6 and not t.isdigit() else t for t in termos}


def _termos_na_unidade(unid, termos):
    toks = set(EV.tokens_de_uso(unid["txt"]))
    rad = {EV._radical(t) if len(t) >= 6 and not t.isdigit() else t for t in toks}
    return [t for t, r in _radicais(termos).items() if t in toks or r in rad]


def _familia_unidade(txt, fam_req):
    m = _ROT.match(txt)
    fam_rot = EV.FAM_ROTULO.get(F(m.group(1)).split()[0]) if m else None
    cue = EV.cue_de_atributo(txt, fam_req)
    ok = EV.COMPATIVEL.get(fam_req, {fam_req})
    conflito = bool(fam_rot and fam_rot not in ok and not cue)
    return {"rotulo_familia": fam_rot, "cue": cue, "conflito": conflito}


def _relacao(unid, ments, termos_unid, outras, ent_formas):
    """'explicita' | 'coocorrencia' | 'outra_entidade'. Exige: mencao nao parte de outra entidade, mesma clausula (sem ; . ( ) nem ',' fora de conectores), sem discurso reportado,
    1..12 palavras entre a mencao e o termo mais proximo, e nenhuma outra entidade da mesma classe mais perto do termo do que a entidade avaliada."""
    f = unid["f"]
    pos_t = []
    for t in termos_unid:
        for m in re.finditer(r"\b" + re.escape(F(t)[:6] if len(t) >= 6 else F(t)), f):
            pos_t.append(m.start())
    if not pos_t:
        return "coocorrencia", "sem termo do atributo na unidade"
    melhor = None
    for (p, fm, papel) in ments:
        if papel != "direta":
            continue
        d = min(abs(p - q) for q in pos_t)
        if melhor is None or d < melhor[0]:
            melhor = (d, p, fm)
    if melhor is None:
        return "coocorrencia", "mencao so como parte de outra entidade"
    d, p, fm = melhor
    q = min(pos_t, key=lambda x: abs(x - p))
    a, b = sorted((p, q))
    entre = re.sub(r"\([^)]*\)", " ", f[a:b])   # apelidos entre parenteses ('(HRT)') nao quebram a relacao
    entre = re.sub(r"[()]", " ", entre)           # parentese solto (a mencao e o proprio apelido)
    entre = re.sub(r"\b(\w{1,3})\.", r"\1", entre)   # ponto de abreviatura ('UI/G.') nao e fronteira
    for o in outras:
        for m in re.finditer(r"\b" + re.escape(o) + r"\b", f):
            if min(abs(m.start() - x) for x in pos_t) < d:
                return "outra_entidade", f"'{o}' esta mais perto do atributo"
    if re.search(r"[;.()]", entre) or re.search(r",(?!\s*(?:inclusive|incluindo|bem como|e|ou|especialmente|para|a quem|cujo|cuja|onde))", entre):
        return "coocorrencia", "fronteira de clausula entre entidade e atributo"
    pal = re.findall(r"\w+", entre)
    if any(w in CONECT_PROIBIDO for w in pal):
        return "coocorrencia", "discurso reportado"
    if len(pal) > 14:
        return "coocorrencia", "distancia > 12 palavras"
    return "explicita", f"{len(pal)} palavras entre a entidade e o atributo"


def _entidades_em(unid, formas_por_nome):
    return {n for n, fs in formas_por_nome.items() if any(re.search(r"\b" + re.escape(x) + r"\b", unid["f"]) for x in fs)}


def avaliar(pub, trechos_citados, termos, ent, fam_req, outras, outras_pubs=()):
    """Avalia UM par (entidade, afirmacao). Retorna estados por nivel, aceitacao por estrategia N1..N4 e diagnostico."""
    formas = ent["formas"]
    u_cit = []
    for t in trechos_citados:
        for u in pub.unidades_do_trecho(t):
            if u not in u_cit:
                u_cit.append(u)
    thr = max(1, math.ceil(0.4 * len(termos))) if termos else 0
    u_attr = [u for u in u_cit if len(_termos_na_unidade(u, termos)) >= thr] if termos else []
    nota = ""
    if termos and not u_attr:
        u_attr, nota = u_cit, "nenhuma unidade citada reune os termos; usando unidades citadas"
    out = {"unidades_citadas": [u["i"] for u in u_cit], "unidades_atributo": [u["i"] for u in u_attr], "nota": nota, "niveis": {}, "aceita": {}, "detalhes": []}
    if not termos:
        out["niveis"] = {"N1": "sem_conteudo", "N2": "sem_conteudo", "N3": "sem_conteudo", "N4": "sem_conteudo"}
        out["aceita"] = {k: False for k in ("N1", "N2", "N3", "N4")}
        return out
    todos = {"alvo": formas, **{o: [o] for o in outras}}
    # ---- N1: mesma frase
    n1, d1 = "ausente", []
    for u in u_attr:
        ments = _mencoes(u, formas, ent.get("tipo"))
        fam = _familia_unidade(u["txt"], fam_req)
        if ments:
            rel, why = _relacao(u, ments, _termos_na_unidade(u, termos), outras, formas)
            if fam["conflito"]:
                rel, why = "outro_atributo", f"unidade com rotulo da familia {fam['rotulo_familia']} incompativel com {fam_req}"
            if all(m[2] != "direta" for m in ments):
                rel, why = "outra_entidade", "a mencao e parte do nome de outra entidade"
            d1.append((u["i"], rel, why))
            rank = {"explicita": 3, "coocorrencia": 2, "outro_atributo": 1, "outra_entidade": 1}
            if n1 == "ausente" or rank.get(rel, 0) > rank.get(n1, 0):
                n1 = rel
        else:
            ents = _entidades_em(u, {o: [o] for o in outras})
            d1.append((u["i"], "sem_mencao", f"outras entidades na unidade: {sorted(ents)}"))
    # ---- N2: frases adjacentes com vinculo textual
    n2, d2 = "ausente", []
    for u in u_attr:
        for v in (x for x in (pub.un[u["i"] - 1] if u["i"] > 0 else None, pub.un[u["i"] + 1] if u["i"] + 1 < len(pub.un) else None) if x):
            if not (set(u["chunks"]) & set(v["chunks"])) and (u["chunks"] or v["chunks"]):
                continue
            ments = [m for m in _mencoes(v, formas, ent.get("tipo")) if m[2] == "direta"]
            if not ments:
                continue
            anaf = bool(ANAFORA.match(u["f"].strip()) or CONTINUACAO.match(u["f"].strip())) and v["i"] < u["i"]
            intro = v["txt"].rstrip().endswith(":") and v["i"] < u["i"]
            if anaf:
                anterior = [x for x in pub.un[:u["i"]][::-1] if _entidades_em(x, todos)]
                ref = _entidades_em(anterior[0], todos) if anterior else set()
                if ref == {"alvo"}:
                    n2, d2 = "adjacente_com_vinculo", d2 + [(v["i"], "anafora com referente unico")]
                else:
                    d2.append((v["i"], f"anafora ambigua/outro referente: {sorted(ref)}"))
                    n2 = n2 if n2 != "ausente" else "anafora_ambigua"
            elif intro:
                n2, d2 = "adjacente_com_vinculo", d2 + [(v["i"], "unidade anterior introduz com ':'")]
            elif n2 in ("ausente",):
                n2, d2 = "adjacente_sem_vinculo", d2 + [(v["i"], "so proximidade")]
    # ---- N3: mesmo chunk (ingenuo)
    chs = {c for u in u_cit for c in u["chunks"]}
    n3, d3 = "ausente", []
    for u in pub.un:
        if chs & set(u["chunks"]):
            for (p, fm, papel) in _mencoes(u, formas, ent.get("tipo")):
                d3.append((u["i"], papel))
                n3 = "mesmo_chunk"
    # ---- N4: mesma publicacao (ingenuo)
    n4, d4 = "ausente", []
    for u in pub.un:
        for (p, fm, papel) in _mencoes(u, formas, ent.get("tipo")):
            d4.append((u["i"], papel, "no_contexto_enviado" if u["chunks"] else "FORA_do_contexto_enviado"))
            n4 = "mesma_publicacao"
    if n4 != "ausente" and pub.un and any(d[0] == 0 for d in d4) and not any(re.search(r"\b" + re.escape(o) + r"\b", pub.f) for o in outras):
        n4 = "sujeito_da_publicacao"
    # ---- em outra publicacao (nunca aceito)
    outra = [pid for pid, tx in outras_pubs if any(re.search(r"\b" + re.escape(x) + r"\b", F(tx)) for x in formas)]
    out["niveis"] = {"N1": n1, "N2": n2 if n2 != "ausente" or n1 != "explicita" else n1, "N3": n3, "N4": n4}
    if n1 == "explicita":
        out["niveis"]["N2"] = "explicita"
    out["aceita"] = {"N1": n1 == "explicita", "N2": n1 == "explicita" or n2 == "adjacente_com_vinculo", "N3": n3 == "mesmo_chunk", "N4": n4 in ("mesma_publicacao", "sujeito_da_publicacao")}
    out["detalhes"] = {"N1": d1, "N2": d2, "N3": d3, "N4": d4, "em_outra_publicacao": outra}
    # parciais (ex.: localidade da entidade sem a entidade)
    if ent.get("parciais"):
        pp = [(u["i"], u["txt"][:90]) for u in pub.un if _mencoes(u, ent["parciais"])]
        out["detalhes"]["parciais_na_publicacao"] = pp[:4]
    return out


def afirmacoes(resposta, pergunta):
    """Clausulas da resposta (sem o AVISO), cada uma com seus termos de atributo (termos de uso de producao, leitura)."""
    r = re.split(r"\n\s*\n?\s*AVISO\b", resposta)[0]
    cl = []
    for s in segmentar(r):
        t = r[s[0]:s[1]]
        for p in re.split(r";|,\s+(?=incluindo|inclusive|bem como|resultando|sendo)|\s+bem como\s+", t):
            if p.strip():
                cl.append({"texto": p.strip(), "termos": EV.termos_de_uso(p, pergunta)})
    return cl
