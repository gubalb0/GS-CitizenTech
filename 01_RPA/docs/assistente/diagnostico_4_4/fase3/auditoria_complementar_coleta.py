"""Auditoria complementar da Fase 3 - COLETA SOMENTE LEITURA (sem LLM; replay offline com saidas brutas gravadas). Grava apenas em fase3/."""
import csv, json, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\scripts")
from replay_verificador import ClienteFalso, AE
from citizentech.assistente import grupos as GR
from citizentech.assistente.catalogo import Catalogo
from citizentech.assistente.geracao import ConfigGeracao, gerar_resposta, montar_contexto
from citizentech.assistente.retriever import Indice
CASOS = ["val-007", "val-012", "val-100", "val-149", "val-087"]
corpus, val, assoc, dup, esp, docs = AE.preparar(); idx = Indice.carregar(AE.IDX); cat = Catalogo.de_corpus(corpus); cfg = ConfigGeracao()
orig = {json.loads(l)["qid"]: json.loads(l) for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8")}
aud = {r["qid"]: r for r in csv.DictReader(open(r"D:\Downloads\GS\RPA\docs\assistente\auditoria_independente_4_3\auditoria_independente_150.csv", encoding="utf-8-sig"), delimiter=";")}
out = {}
for q, e, a in zip(val, esp, assoc):
    k = q["qid"]
    if k not in CASOS: continue
    o = orig[k]; res = idx.buscar(q["pergunta"], k=cfg.max_chunks, modo="bm25")
    ctx = montar_contexto(q["pergunta"], res, cfg); itens = ctx.itens
    bruto = json.loads(o["saida"]["telemetria"]["saida_bruta"])
    r = gerar_resposta(q["pergunta"], res, ClienteFalso(o["saida"]["telemetria"]["saida_bruta"], cfg), cfg, catalogo=cat).para_dict()
    out[k] = {"pergunta": q["pergunta"], "gabarito_dataset": q["resposta"], "docs_esperados_dataset": [sorted(g) for g in e],
              "auditoria_anterior": {"classe": aud[k]["classificacao_independente"], "justificativa": aud[k]["justificativa_e_referencias_documentais"]},
              "recuperados": [{"pos": x.posicao, "chunk_id": x.chunk_id, "doc": x.doc_id, "score": round(x.score, 2), "ref": f"{x.metadados.get('tipo_documento')} {x.metadados.get('referencia')} ed.{x.metadados.get('edicao')}",
                               "enviado": x.chunk_id in {i.chunk_id for i in itens}, "n_chunks_doc": x.metadados.get("n_chunks_doc"), "ordem": x.metadados.get("ordem")} for x in res],
              "contexto": {i.id: {"chunk_id": i.chunk_id, "doc": i.doc_id, "texto": i.texto_original} for i in itens},
              "tokens_contexto": ctx.tokens_estimados, "grupo_real": GR.grupo_ab(e, itens),
              "saida_bruta": bruto, "fase3_status": r["status"], "fase3_resposta": r["resposta"], "fase3_problemas": r["verificacao"].get("problemas"),
              "evidencia_registro": r["verificacao"].get("evidencia"), "citacoes": [{"fonte": x["fonte"], "citacao": x.get("citacao"), "trecho_verificado": x.get("trecho_verificado", "")[:160]} for x in r["evidencias"]]}
json.dump(out, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase3\auditoria_complementar_dados.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
for k, v in out.items(): print(k, v["fase3_status"], v["grupo_real"], [(x["pos"], x["doc"], x["enviado"]) for x in v["recuperados"]], "esperados", v["docs_esperados_dataset"])
