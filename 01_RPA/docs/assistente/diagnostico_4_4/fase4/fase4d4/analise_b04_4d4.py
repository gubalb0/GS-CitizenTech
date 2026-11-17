"""Fase 4D.4 - analise diagnostica do falso bloqueio B04 e da fragilidade do 'cue' textual. SOMENTE LEITURA dos casos 4D.3 (nao os altera, nao sobrescreve nada da 4D.3).
Replica o harness da 4D.3 (chunks injetados, resposta fixa, sem modelo). Acrescenta 2 SONDAS SINTETICAS (P1, P2), claramente marcadas, so para mostrar a fragilidade do cue."""
import json
import pathlib
import sys

RAIZ = pathlib.Path(r"D:\Downloads\GS\RPA")
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "citizentech" / "assistente" / "tests"))
from test_fase4a import chunk, o87, rodar  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402

AQUI = pathlib.Path(__file__).parent
D43 = AQUI.parent / "fase4d3"
CASOS = json.loads((D43 / "CASOS_DIAGNOSTICOS_4D3.json").read_text(encoding="utf-8"))["casos"]
det43 = json.loads((D43 / "resultados_4d3_detalhe.json").read_text(encoding="utf-8"))["por_caso"]

HEAD = "Ordem de Serviço nº 93/2025. Coordenação de Regulação da Região de Saúde Sul (CRSSU). "
Q_G = "Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?"
SONDAS = [
    {"id": "P1_sintetica", "descricao": "SONDA SINTÉTICA: span de membro com a palavra 'competência' incidental (nome de órgão), sem atribuir competência; resposta usa conteúdo só desse span",
     "pergunta": Q_G, "resposta": "O Diretor do HRG integra a Câmara de Competência Técnica.", "chunks": [{"chave": "m", "doc": 101, "ordem": 0, "n_chunks_doc": 1,
     "texto": HEAD + "Art. 2º Designar membros: 4 - Titular: Diretor do Hospital Regional do Gama (HRG), da Câmara de Competência Técnica; Suplente: substituto."}],
     "citacoes": [{"chunk": "m", "span": "4 - Titular: Diretor do Hospital Regional do Gama (HRG), da Câmara de Competência Técnica"}]},
    {"id": "P2_sintetica", "descricao": "SONDA SINTÉTICA: span de membro que afirma a atribuição com palavra fora da lista de rótulos ('incumbe'); resposta usa esse conteúdo",
     "pergunta": Q_G, "resposta": "Incumbe ao Diretor do HRG deliberar sobre os serviços do Gama.", "chunks": [{"chave": "m", "doc": 101, "ordem": 0, "n_chunks_doc": 1,
     "texto": HEAD + "Titular: o Diretor do HRG do Gama, a quem incumbe deliberar sobre os serviços regulados do Gama."}],
     "citacoes": [{"chunk": "m", "span": "Titular: o Diretor do HRG do Gama, a quem incumbe deliberar sobre os serviços regulados do Gama"}]},
]


def executar(c):
    chunks = [chunk(k + 1, ch["texto"], ch["doc"], ordem=ch["ordem"], n=ch["n_chunks_doc"]) for k, ch in enumerate(c["chunks"])]
    chave = {ch["chave"]: f"C{k + 1}" for k, ch in enumerate(c["chunks"])}
    spans = [(chave[x["chunk"]], x["span"]) for x in c["citacoes"]]
    r = rodar(c["pergunta"], chunks, o87(c["resposta"], spans, fontes=tuple(sorted({f for f, _ in spans}))))
    rl = [x for x in ((r.verificacao or {}).get("evidencia") or {}).get("protecao", {}).get("relacoes", []) if x["origem"] == "citacao"]
    textos = {chave[ch["chave"]]: ch["texto"] for ch in c["chunks"]}
    return r, rl, textos


def filtro_C(c, r, rl, textos, modo):
    if r.status not in ("respondida", "parcial"):
        return "ja_bloqueado"
    nomes = [n for n in EV.termos_salientes(c["pergunta"])["nomes"] if n in EV._nf(c["resposta"])]
    for n in nomes:
        ruim = (lambda x: x["estado"] == "conflito") if modo == "estado" else (lambda x: bool(x["causas_do_conflito"]))
        if not any(n in EV._nf(textos[x["fonte"]]) and not ruim(x) for x in rl):
            return "BLOQUEIA"
    return "libera"


out = {}
for c in CASOS + SONDAS:
    r, rl, tx = executar(c)
    j = c.get("julgamento_referencia", {})
    out[c["id"]] = {"decisao_ideal_4d3": j.get("decisao_ideal_do_pipeline"), "status_baseline": r.status, "problemas": (r.verificacao or {}).get("problemas"),
                    "C_estado": filtro_C(c, r, rl, tx, "estado"), "C_causas": filtro_C(c, r, rl, tx, "causas"),
                    "citacoes": [{"fonte": x["fonte"], "rotulo": (x["rotulo"] or {}).get("rotulo"), "estado": x["estado"], "causas": x["causas_do_conflito"], "necessaria": x["necessaria"], "bloqueia": x["bloqueia"],
                                  "cue": EV.cue_de_atributo(x["valor"], "COMPETENCIA"), "justificativa": x["justificativa"]} for x in rl]}
    if c["id"].startswith("P"):
        out[c["id"]]["descricao"] = c["descricao"]
# conferencia de consistencia com a 4D.3 (estado) - nao sobrescreve nada
dif = [k for k in out if k in det43 and out[k]["status_baseline"] != det43[k]["baseline"]["status"]]
out["_conferencia_baseline_vs_4d3_divergencias"] = dif
(AQUI / "b04_c_causas_4d4.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("divergencias vs 4D.3:", dif)
for k in ("B04", "A07", "A02", "A06", "B05", "P1_sintetica", "P2_sintetica"):
    v = out[k]
    print(k, v["status_baseline"], v["problemas"], "C_estado:", v["C_estado"], "C_causas:", v["C_causas"], [(x["rotulo"], x["estado"], x["causas"], x["cue"], x["bloqueia"]) for x in v["citacoes"]])
print("C_estado bloqueia:", [k for k, v in out.items() if k[0] in "ABCD" and v["C_estado"] == "BLOQUEIA"])
print("C_causas bloqueia:", [k for k, v in out.items() if k[0] in "ABCD" and v["C_causas"] == "BLOQUEIA"])
