"""Catalogo do corpus para o teste de IDENTIFICABILIDADE da publicacao (Etapa 4.2).

Pergunta: dada a publicacao que o modelo citou, existe OUTRA publicacao do corpus (nao duplicata) que cobre todos os termos da pergunta
que a citada cobre? Se existe, a pergunta nao identifica uma publicacao especifica e o assistente nao pode escolher entre elas.

Somente leitura: usa o texto do corpus ja carregado; nao toca no retriever, nos indices nem nos dados originais. Numeros, anos e meses
tambem sao termos (um ano so discrimina se nao aparecer em publicacoes concorrentes, como acontece com 2025 em quase todo o corpus).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import evidencias as EV
from .dados import norm_forte


@dataclass
class DocCat:
    id: int
    ids_equivalentes: list[int]
    texto_nf: str
    texto_sem_esp: str
    data_edicao: str
    meta: dict


class Catalogo:
    def __init__(self, docs: list[dict]):
        """`docs`: documentos CANONICOS (um por grupo de duplicatas), cada um com `ids_equivalentes`."""
        self.docs: dict[int, DocCat] = {}
        for d in docs:
            t = norm_forte(" ".join([d.get("texto_completo") or "", str(d.get("referencia") or ""), str(d.get("numero_documento") or ""),
                                     " ".join(d.get("localidades") or []), " ".join(d.get("tipo_unidade") or [])]))
            self.docs[int(d["id"])] = DocCat(int(d["id"]), [int(x) for x in d.get("ids_equivalentes", [d["id"]])], t, re.sub(r"\s+", "", t),
                                             str(d.get("data_edicao") or ""),
                                             {k: d.get(k) for k in ("edicao", "data_edicao", "secao", "referencia", "tipo_documento", "numero_documento")})
        self._por_equiv = {i: dc.id for dc in self.docs.values() for i in dc.ids_equivalentes}
        self.localidades = sorted({norm_forte(x) for d in docs for x in (d.get("localidades") or []) if x}, key=len, reverse=True)      # gazetario do proprio corpus (4.4)

    @classmethod
    def de_corpus(cls, corpus: list[dict]) -> "Catalogo":
        from .dedup import agrupar_duplicatas, documentos_canonicos
        return cls(documentos_canonicos(corpus, agrupar_duplicatas(corpus)))

    def __len__(self) -> int:
        return len(self.docs)

    def canonico(self, doc_id: int) -> int | None:
        return self._por_equiv.get(int(doc_id))

    def _termos(self, pergunta: str) -> dict:
        s = EV.termos_salientes(pergunta)
        s["conteudo"] = EV.palavras_de_conteudo(pergunta)
        return s

    @staticmethod
    def _cobre(dc: DocCat, s: dict) -> set[str]:
        c = set()
        for n in s["nomes"]:
            if n in dc.texto_nf:
                c.add("n:" + n)
        for n in s["numeros"]:
            if re.sub(r"\s+", "", n) in dc.texto_sem_esp:
                c.add("#:" + n)
        m = re.fullmatch(r"(\d{4})-(\d{2})-\d{2}", dc.data_edicao)
        for y in s["anos"]:
            if y in dc.texto_nf or (m and m.group(1) == y):
                c.add("a:" + y)
        for mes in s["meses"]:
            if mes in dc.texto_nf or (m and int(m.group(2)) == EV.MESES[mes]):
                c.add("m:" + mes)
        for w in s["conteudo"]:
            if EV._radical(w) in dc.texto_nf:
                c.add("c:" + w)
        return c

    JANELA = 1500      # caracteres (~um chunk): os termos da pergunta precisam aparecer JUNTOS, nao espalhados por um documento enorme

    def _proximos(self, dc: DocCat, s: dict, cov: set[str]) -> bool:
        """Todos os termos cobertos (nomes, numeros, palavras de conteudo) aparecem dentro de uma mesma janela do documento."""
        from bisect import bisect_left
        pos_por_termo: list[list[int]] = []
        for k in cov:
            tipo, t = k.split(":", 1)
            if tipo in ("a", "m"):
                continue                      # ano/mes podem vir so do cabecalho (data da edicao): nao entram na proximidade
            alvo = dc.texto_sem_esp if tipo == "#" else dc.texto_nf
            t = re.sub(r"\s+", "", t) if tipo == "#" else (EV._radical(t) if tipo == "c" else t)
            ps, i = [], alvo.find(t)
            while i != -1 and len(ps) < 400:
                ps.append(i)
                i = alvo.find(t, i + 1)
            if not ps:
                return False
            pos_por_termo.append(ps)
        if len(pos_por_termo) <= 1:
            return True
        pos_por_termo.sort(key=len)
        for a in pos_por_termo[0]:
            if all((lambda ps: (j := bisect_left(ps, a - self.JANELA)) < len(ps) and ps[j] <= a + self.JANELA)(ps) for ps in pos_por_termo[1:]):
                return True
        return False

    @staticmethod
    def _contem_trechos(dc: DocCat, trechos: list[str]) -> bool:
        partes = [norm_forte(p.strip(" .,;:!?-–—\"'()[]")) for t in trechos for p in re.split(r"\.\.\.|…", t)]
        partes = [p for p in partes if len(p) >= 8]
        return bool(partes) and all(p in dc.texto_nf for p in partes)

    @staticmethod
    def _contem_afirmacao(dc: DocCat, tokens: list[str]) -> bool:
        """A publicacao contem TODOS os elementos especificos (valores, ids, nomes) da resposta: sustenta o mesmo fato."""
        return bool(tokens) and all((t in dc.texto_sem_esp) if any(c.isdigit() for c in t) else (t in dc.texto_nf) for t in tokens)

    # ---- Etapa 4.3: relevancia por janela (cobertura PARCIAL dos termos) -------------------------------------------------
    @staticmethod
    def _lista_termos(s: dict) -> list[tuple[str, str]]:
        nomes = list(s["nomes"])
        return ([("n", n) for n in nomes] + [("c", w) for w in s["conteudo"] if w not in nomes] + [("#", x) for x in s["numeros"]])

    def melhor_janela(self, dc: DocCat, s: dict) -> int:
        """Maior numero de termos DISTINTOS da pergunta que aparecem juntos numa janela de JANELA caracteres do documento."""
        ev = []
        for k, (tp, x) in enumerate(self._lista_termos(s)):
            alvo = dc.texto_sem_esp if tp == "#" else dc.texto_nf
            x = re.sub(r"\s+", "", x) if tp == "#" else (EV._radical(x) if tp == "c" else x)
            i, c = alvo.find(x), 0
            while i != -1 and c < 300:
                ev.append((i, k))
                i, c = alvo.find(x, i + 1), c + 1
        ev.sort()
        best, cnt, esq = 0, {}, 0
        for p, k in ev:
            cnt[k] = cnt.get(k, 0) + 1
            while ev[esq][0] < p - self.JANELA:
                kk = ev[esq][1]
                cnt[kk] -= 1
                if not cnt[kk]:
                    del cnt[kk]
                esq += 1
            best = max(best, len(cnt))
        return best

    MIN_TERMOS = 3          # abaixo disso a coincidencia de termos nao distingue publicacoes (fixado antes da avaliacao 4.3)

    def relevantes(self, pergunta: str, doc_ids_citados: list[int], trechos_citados: list[str] | None = None,
                   afirmacoes: list[str] | None = None, piso: float = 1.0) -> dict:
        """Publicacoes INDEPENDENTES do corpus tao relevantes quanto as citadas: janela de termos >= piso * (melhor janela entre as citadas),
        com no minimo MIN_TERMOS termos. Duplicatas, republicacoes e atos-modelo que contem as mesmas evidencias ('concordantes') nao contam.
        Uma unica publicacao recuperada NAO e prova de que so existe uma relevante: a contagem e feita sobre todo o corpus."""
        cids = {c for c in (self.canonico(d) for d in doc_ids_citados) if c is not None}
        if not cids:
            return {"avaliavel": False, "melhor_citada": 0, "relevantes": [], "concordantes": 0}
        s = self._termos(pergunta)
        mc = max(self.melhor_janela(self.docs[c], s) for c in cids)
        if mc < self.MIN_TERMOS:
            return {"avaliavel": False, "melhor_citada": mc, "relevantes": [], "concordantes": 0}
        lim = max(self.MIN_TERMOS, int(piso * mc + 0.999))
        trechos = trechos_citados or []
        rel, concord = [], 0
        for i, dc in self.docs.items():
            if i in cids or self.melhor_janela(dc, s) < lim:
                continue
            if (trechos and self._contem_trechos(dc, trechos)) or self._contem_afirmacao(dc, afirmacoes or []):
                concord += 1
            else:
                rel.append({"id": dc.id, **dc.meta})
        return {"avaliavel": True, "melhor_citada": mc, "relevantes": rel, "concordantes": concord}

    def concorrentes(self, pergunta: str, doc_id_citado: int, trechos_citados: list[str] | None = None,
                     afirmacoes: list[str] | None = None) -> dict:
        """Publicacoes do corpus que (a) cobrem todos os termos da pergunta que a citada cobre e (b) NAO contem os trechos de
        evidencia citados. As que contem os mesmos trechos (republicacoes, modelos de ato repetidos) dizem a mesma coisa e nao
        tornam a pergunta ambigua; as demais podem dar outra resposta.
        Retorna {'avaliavel', 'cobertura_citada', 'concorrentes': [meta...], 'concordantes': n}.
        `avaliavel` e False se a publicacao citada nao existe no catalogo ou nao cobre nenhum termo da pergunta."""
        cid = self.canonico(doc_id_citado)
        if cid is None:
            return {"avaliavel": False, "cobertura_citada": 0, "concorrentes": [], "concordantes": 0}
        s = self._termos(pergunta)
        cov = self._cobre(self.docs[cid], s)
        if not cov:
            return {"avaliavel": False, "cobertura_citada": 0, "concorrentes": [], "concordantes": 0}
        cobrem = [dc for i, dc in self.docs.items() if i != cid and self._cobre(dc, s) >= cov and self._proximos(dc, s, cov)]
        trechos = trechos_citados or []
        concord = [dc for dc in cobrem if (trechos and self._contem_trechos(dc, trechos)) or self._contem_afirmacao(dc, afirmacoes or [])]
        div = [dc for dc in cobrem if dc not in concord]
        return {"avaliavel": True, "cobertura_citada": len(cov), "concorrentes": [{"id": dc.id, **dc.meta} for dc in div], "concordantes": len(concord)}
