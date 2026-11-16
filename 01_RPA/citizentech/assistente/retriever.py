"""Retriever hibrido (BM25 + vetorial + RRF) sobre chunks do DODF, com troca de configuracao de chunking.

    idx = Indice.construir(corpus, ConfigChunk("estrutura", 500, 50), CodificadorE5())
    idx.salvar(pasta); idx = Indice.carregar(pasta, codificador)
    r = idx.buscar("qual o valor autorizado ...", k=10, modo="hibrido")

- Duplicatas exatas: indexa-se apenas o documento canonico; `ids_equivalentes` fica em cada chunk e resultado.
- Ranking deterministico: empates desfeitos pelo menor indice de chunk (ordem do corpus).
- Nenhum documento e cortado por tamanho; documentos gigantes sao indexados normalmente. O controle de dominancia e feito
  no RESULTADO (`max_por_doc`), nao no indice.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .bm25 import BM25, top_k_deterministico
from .chunking import ConfigChunk, chunkear_documento
from .codificador import Codificador
from .dedup import agrupar_duplicatas, documentos_canonicos

MODOS = ("bm25", "vetorial", "hibrido")
RRF_K_PADRAO = 60
CANDIDATOS_PADRAO = 100


@dataclass
class Resultado:
    posicao: int
    chunk_id: str
    doc_id: int                      # id canonico do documento no corpus original
    score: float
    texto: str
    ids_equivalentes: list[int]
    ranks: dict[str, int] = field(default_factory=dict)   # posicao (1-based) em cada recuperador que o trouxe
    metadados: dict = field(default_factory=dict)


@dataclass
class Indice:
    config: ConfigChunk
    chunks: list[dict]
    bm25: BM25
    vetores: np.ndarray
    janela_inicio: np.ndarray        # len = n_chunks + 1; janelas de cada chunk sao contiguas
    doc_de_chunk: np.ndarray
    manifesto: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ construcao
    @classmethod
    def construir(cls, corpus: list[dict], config: ConfigChunk, codificador: Codificador, dedup: bool = True,
                  bm25_k1: float = 1.5, bm25_b: float = 0.75, radical_leve: bool = False,
                  checkpoint: Path | None = None, progresso=None) -> "Indice":
        t0 = time.perf_counter()
        dup = agrupar_duplicatas(corpus)
        docs = documentos_canonicos(corpus, dup) if dedup else [{**d, "ids_equivalentes": [int(d["id"])]} for d in corpus]
        chunks: list[dict] = []
        for d in docs:
            for c in chunkear_documento(d, config):
                c["ids_equivalentes"] = list(d["ids_equivalentes"])
                c["doc_numerico"] = int(d["id"])
                chunks.append(c)
        t_chunk = time.perf_counter() - t0
        if not chunks:
            raise ValueError("nenhum chunk gerado (corpus vazio?)")

        t1 = time.perf_counter()
        bm25 = BM25(bm25_k1, bm25_b, radical_leve).ajustar([c["texto_indexacao"] for c in chunks])
        t_bm25 = time.perf_counter() - t1

        t2 = time.perf_counter()
        textos, inicio = [], [0]
        for c in chunks:
            js = codificador.janelas(c)
            textos.extend(js)
            inicio.append(len(textos))
        t_janelas = time.perf_counter() - t2
        t3 = time.perf_counter()
        vetores = _codificar_com_checkpoint(textos, codificador, checkpoint, progresso)
        t_emb = time.perf_counter() - t3
        if len(vetores) != len(textos):
            raise RuntimeError("numero de vetores difere do numero de janelas")
        manifesto = {"config": config.nome, "estrategia": config.estrategia, "max_tokens": config.max_tokens,
                     "overlap_tokens": config.overlap_tokens, "codificador": codificador.nome, "dimensao": int(codificador.dimensao),
                     "dedup": dedup, "documentos_originais": len(corpus), "documentos_indexados": len(docs),
                     "duplicatas_redundantes": dup.n_documentos_redundantes, "n_chunks": len(chunks), "n_janelas": len(textos),
                     "bm25": {"k1": bm25_k1, "b": bm25_b, "radical_leve": radical_leve},
                     "tempos_s": {"chunking": round(t_chunk, 2), "bm25": round(t_bm25, 2), "janelas": round(t_janelas, 2),
                                  "embeddings": round(t_emb, 2)}}
        return cls(config, chunks, bm25, vetores, np.asarray(inicio, dtype=np.int64),
                   np.asarray([c["doc_numerico"] for c in chunks], dtype=np.int64), manifesto)

    # ------------------------------------------------------------------ persistencia
    def salvar(self, pasta: Path) -> None:
        pasta.mkdir(parents=True, exist_ok=True)
        with (pasta / "chunks.jsonl").open("w", encoding="utf-8") as fh:
            for c in self.chunks:
                fh.write(json.dumps(c, ensure_ascii=False) + "\n")
        np.save(pasta / "vetores.npy", self.vetores)
        np.save(pasta / "janela_inicio.npy", self.janela_inicio)
        (pasta / "manifesto.json").write_text(json.dumps(self.manifesto, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def carregar(cls, pasta: Path, codificador_nome: str | None = None) -> "Indice":
        """Recarrega chunks e vetores; o BM25 e reconstruido de forma deterministica a partir dos chunks."""
        pasta = Path(pasta)
        for f in ("chunks.jsonl", "vetores.npy", "janela_inicio.npy", "manifesto.json"):
            if not (pasta / f).exists():
                raise FileNotFoundError(f"indice incompleto: falta {f} em {pasta}")
        man = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
        if codificador_nome and man.get("codificador") != codificador_nome:
            raise ValueError(f"indice gerado com {man.get('codificador')}, nao com {codificador_nome}")
        chunks = [json.loads(l) for l in (pasta / "chunks.jsonl").open(encoding="utf-8")]
        vetores = np.load(pasta / "vetores.npy")
        ji = np.load(pasta / "janela_inicio.npy")
        if len(ji) != len(chunks) + 1 or ji[-1] != len(vetores):
            raise ValueError("indice inconsistente (janelas x chunks)")
        b = man["bm25"]
        bm = BM25(b["k1"], b["b"], b["radical_leve"]).ajustar([c["texto_indexacao"] for c in chunks])
        cfg = ConfigChunk(man["estrategia"], man["max_tokens"], man["overlap_tokens"])
        return cls(cfg, chunks, bm, vetores, ji, np.asarray([c["doc_numerico"] for c in chunks], dtype=np.int64), man)

    def tamanho_em_disco(self, pasta: Path) -> int:
        return sum(p.stat().st_size for p in Path(pasta).iterdir() if p.is_file())

    # ------------------------------------------------------------------ busca
    def _pontuar_vetorial(self, q: np.ndarray, janela: str) -> np.ndarray:
        s = self.vetores @ q
        ini = self.janela_inicio[:-1]
        return s[ini] if janela == "primeira" else np.maximum.reduceat(s, ini)

    def _rank_lexical(self, consulta: str, n: int) -> list[int]:
        idx, _ = self.bm25.buscar(consulta, n)
        return [int(i) for i in idx]

    def _rank_vetorial(self, q: np.ndarray, n: int, janela: str) -> tuple[list[int], np.ndarray]:
        s = self._pontuar_vetorial(q, janela)
        return [int(i) for i in top_k_deterministico(s, n)], s

    def buscar(self, consulta: str, k: int = 10, modo: str = "hibrido", k_candidatos: int = CANDIDATOS_PADRAO,
               rrf_k: int = RRF_K_PADRAO, max_por_doc: int | None = None, janela: str = "max",
               codificador: Codificador | None = None, vetor_consulta: np.ndarray | None = None) -> list[Resultado]:
        if not isinstance(consulta, str):
            raise TypeError("consulta deve ser str")
        if not isinstance(k, int) or isinstance(k, bool) or k < 1:
            raise ValueError("k deve ser inteiro >= 1")
        if modo not in MODOS:
            raise ValueError(f"modo invalido: {modo!r} (use {MODOS})")
        if janela not in ("max", "primeira"):
            raise ValueError("janela deve ser 'max' ou 'primeira'")
        if rrf_k < 1 or k_candidatos < 1 or (max_por_doc is not None and max_por_doc < 1):
            raise ValueError("parametros invalidos")
        if not consulta.strip():
            return []
        n = max(k_candidatos, k)
        listas: dict[str, list[int]] = {}
        score_bm25: dict[int, float] = {}
        if modo in ("bm25", "hibrido"):
            idx_b, sc_b = self.bm25.buscar(consulta, n)
            listas["bm25"] = [int(i) for i in idx_b]
            score_bm25 = {int(i): float(s) for i, s in zip(idx_b, sc_b)}
        if modo in ("vetorial", "hibrido"):
            if vetor_consulta is None:
                if codificador is None:
                    raise ValueError("busca vetorial exige `codificador` ou `vetor_consulta`")
                vetor_consulta = codificador.codificar_consultas([consulta])[0]
            listas["vetorial"], sv = self._rank_vetorial(vetor_consulta, n, janela)
        if modo == "hibrido":
            pont: dict[int, float] = {}
            for lista in listas.values():
                for pos, i in enumerate(lista, start=1):
                    pont[i] = pont.get(i, 0.0) + 1.0 / (rrf_k + pos)
            ordem = sorted(pont, key=lambda i: (-pont[i], i))
            score = pont
        else:
            ordem = listas[modo]
            if modo == "vetorial":
                score = {i: float(sv[i]) for i in ordem}
            else:
                score = score_bm25
        ranks = {m: {i: p for p, i in enumerate(l, start=1)} for m, l in listas.items()}
        out, por_doc = [], {}
        for i in ordem:
            d = int(self.doc_de_chunk[i])
            if max_por_doc is not None and por_doc.get(d, 0) >= max_por_doc:
                continue
            por_doc[d] = por_doc.get(d, 0) + 1
            c = self.chunks[i]
            out.append(Resultado(len(out) + 1, c["chunk_id"], d, float(score[i]), c["texto"], c["ids_equivalentes"],
                                 {m: r[i] for m, r in ranks.items() if i in r},
                                 {k_: c.get(k_) for k_ in ("edicao", "data_edicao", "secao", "referencia", "tipo_documento",
                                                         "numero_documento", "char_inicio", "char_fim", "n_tokens", "ordem",
                                                         "n_chunks_doc", "localidades", "tipo_unidade")}))
            if len(out) == k:
                break
        return out


def _codificar_com_checkpoint(textos: list[str], cod: Codificador, pasta: Path | None, progresso, bloco: int = 1024) -> np.ndarray:
    if not textos:
        return np.zeros((0, cod.dimensao), dtype=np.float32)
    h = hashlib.sha1("\x00".join(textos).encode("utf-8")).hexdigest()[:16]
    partes = []
    if pasta is not None:
        pasta = Path(pasta) / f"ckpt_{cod.nome.replace('/', '_')}_{h}"
        pasta.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    for n, ini in enumerate(range(0, len(textos), bloco)):
        arq = pasta / f"parte_{n:05d}.npy" if pasta is not None else None
        if arq is not None and arq.exists():
            partes.append(np.load(arq))
        else:
            v = cod.codificar_janelas(textos[ini:ini + bloco])
            if arq is not None:
                np.save(arq, v)
            partes.append(v)
        if progresso:
            feito = min(ini + bloco, len(textos))
            progresso(feito, len(textos), time.perf_counter() - t0)
    return np.concatenate(partes, axis=0).astype(np.float32)
