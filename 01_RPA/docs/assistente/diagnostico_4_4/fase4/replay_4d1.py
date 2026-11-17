"""Fase 4D.1 - replays OFFLINE (sem modelo): reexecuta gerar_resposta com ClienteFalso que devolve a saida bruta ja gravada.
Uso: python replay_4d1.py <rotulo>   -> grava replay_4d1_<rotulo>_150.json e replay_4d1_<rotulo>_21.json (arquivos novos; nao sobrescreve)."""
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import avaliacao_e2e as AE
from citizentech.assistente import geracao as G
from citizentech.assistente.catalogo import Catalogo
from citizentech.assistente.retriever import Indice

AQUI = Path(__file__).parent
rot = sys.argv[1]


class Falso:
    def __init__(self, bruto): self.bruto = bruto
    def completar(self, msgs, temperatura=None):
        return {"conteudo": self.bruto, "finish": "stop", "tokens_prompt": 0, "tokens_saida": 0, "tokens_raciocinio": 0, "latencia_s": 0.0}


def resumo(r):
    return {"status": r.status, "resposta": r.resposta, "problemas": (r.verificacao or {}).get("problemas")}


corpus, val, *_ = AE.preparar()
cat, idx = Catalogo.de_corpus(corpus), Indice.carregar(AE.IDX)
cfg = G.ConfigGeracao()
orig = {json.loads(l)["qid"]: json.loads(l) for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8")}
out150 = {q["qid"]: resumo(G.gerar_resposta(q["pergunta"], idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25"), Falso(orig[q["qid"]]["saida"]["telemetria"]["saida_bruta"]), cfg, catalogo=cat)) for q in val}
regs = [json.loads(l) for f in sorted(glob.glob(str(AQUI / "validacao_seletiva*.jsonl"))) for l in open(f, encoding="utf-8")]
out21 = {}
for r in regs:
    c = G.ConfigGeracao(priorizar_atributo=bool(r["flag_priorizar_atributo"]))
    p = r["saida"]["pergunta"]
    out21[r["run_id"]] = {"gravado": resumo(type("R", (), {"status": r["saida"]["status"], "resposta": r["saida"]["resposta"], "verificacao": r["saida"]["verificacao"]})),
                          "replay": resumo(G.gerar_resposta(p, idx.buscar(p, k=c.max_chunks, modo="bm25"), Falso(r["saida"]["telemetria"]["saida_bruta"]), c, catalogo=cat))}
for nome, d in (("150", out150), ("21", out21)):
    dest = AQUI / f"replay_4d1_{rot}_{nome}.json"
    assert not dest.exists(), f"{dest} ja existe"
    dest.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("21: replay == gravado:", sum(v["gravado"] == v["replay"] for v in out21.values()), "/ 21")
print("150 salvo; versao:", G.VERSAO_POLITICA)
