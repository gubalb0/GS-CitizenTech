"""Recalcula os grupos A/B de uma rodada pelo contexto REAL (citizentech.assistente.grupos). Sem LLM; NAO altera a rodada original;
grava um arquivo NOVO em docs/assistente/diagnostico_4_4/."""
import json, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA")
from collections import Counter
from citizentech.assistente import avaliacao_e2e as AE, grupos as GR
from citizentech.assistente.geracao import ConfigGeracao
from citizentech.assistente.retriever import Indice
RUN = sys.argv[1] if len(sys.argv) > 1 else "20261114-130608"
corpus, val, assoc, dup, esperados, docs = AE.preparar(); idx = Indice.carregar(AE.IDX); cfg = ConfigGeracao()
orig = {}
for l in open(AE.SAIDA / f"geracao_e2e_41_{RUN}.jsonl", encoding="utf-8"):
    o = json.loads(l); orig[o["qid"]] = o
out = {}
for q, esp in zip(val, esperados):
    o = orig[q["qid"]]; res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25")
    itens = GR.itens_enviados(q["pergunta"], res, cfg, n_esperado=o["saida"]["telemetria"]["chunks_enviados"])
    g, n = GR.grupo_ab(esp, itens)
    out[q["qid"]] = {"grupo_original": o["grupo"], "grupo_corrigido": g, "n_esperadas_enviadas_corrigido": n, "n_esperadas_enviadas_original": o["n_esperadas_enviadas"],
                     "enviados_eh_prefixo": [i.chunk_id for i in itens] == [r.chunk_id for r in res[:len(itens)]]}
dest = AE.D.RAIZ / "docs" / "assistente" / "diagnostico_4_4" / f"grupos_ab_corrigidos_{RUN}.json"
if dest.exists(): raise SystemExit("arquivo ja existe; nao sobrescrevo")
dest.write_text(json.dumps(out, indent=1), encoding="utf-8")
print("grupo original:", Counter(v["grupo_original"] for v in out.values()), "| corrigido:", Counter(v["grupo_corrigido"] for v in out.values()))
print("mudam:", [(k, v["grupo_original"], v["grupo_corrigido"]) for k, v in out.items() if v["grupo_original"] != v["grupo_corrigido"]])
print("n_esperadas_enviadas diferente:", [k for k, v in out.items() if v["n_esperadas_enviadas_original"] != v["n_esperadas_enviadas_corrigido"]])
print("contexto nao-prefixo:", [k for k, v in out.items() if not v["enviados_eh_prefixo"]])
