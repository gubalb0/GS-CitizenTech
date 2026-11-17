"""Replay OFFLINE do verificador/politica com as saidas BRUTAS do modelo ja gravadas na rodada 4.3 (nenhuma chamada ao LLM).
Reexecuta citizentech.assistente.geracao.gerar_resposta com um cliente falso que devolve `saida_bruta`. Uso: importar `replay(run)` ou executar."""
import json, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import avaliacao_e2e as AE
from citizentech.assistente.catalogo import Catalogo
from citizentech.assistente.geracao import ConfigGeracao, gerar_resposta
from citizentech.assistente.retriever import Indice
RUN = "20261114-130608"

class ClienteFalso:
    def __init__(self, bruto, cfg): self.bruto, self.cfg = bruto, cfg
    def completar(self, msgs, temperatura=None):
        return {"conteudo": self.bruto, "finish": "stop", "tokens_prompt": 0, "tokens_saida": 0, "tokens_raciocinio": 0, "latencia_s": 0.0}

def replay(run=RUN, qids=None):
    corpus, val, assoc, dup, esperados, docs = AE.preparar()
    idx = Indice.carregar(AE.IDX); cat = Catalogo.de_corpus(corpus); cfg = ConfigGeracao()
    orig = {}
    for l in open(AE.SAIDA / f"geracao_e2e_41_{run}.jsonl", encoding="utf-8"):
        o = json.loads(l); orig[o["qid"]] = o
    out = {}
    for q in val:
        if qids and q["qid"] not in qids: continue
        o = orig[q["qid"]]; bruto = o["saida"]["telemetria"].get("saida_bruta")
        if bruto is None: continue
        res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25")
        r = gerar_resposta(q["pergunta"], res, ClienteFalso(bruto, cfg), cfg, catalogo=cat).para_dict()
        out[q["qid"]] = {"status_orig": o["saida"]["status"], "status": r["status"], "problemas": r["verificacao"].get("problemas"), "verificacao": r["verificacao"], "resposta": r["resposta"], "evidencias": r["evidencias"]}
    return out

if __name__ == "__main__":
    from collections import Counter
    out = replay()
    dif = {k: (v["status_orig"], v["status"]) for k, v in out.items() if v["status_orig"] != v["status"]}
    print(len(out), "casos; diferentes da rodada original:", len(dif), dif)
    print(Counter(v["status"] for v in out.values()))
