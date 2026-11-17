"""Auditoria de encerramento da 4A - Mecanismo B (apoio exclusivo): busca em dados reais e cenarios sinteticos (somente leitura; sem LLM)."""
import json, sys
sys.path.insert(0, r"D:\Downloads\GS\RPA\citizentech\assistente\tests")
sys.path.insert(0, r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\scripts")
from test_fase4a import chunk, rodar, saida, rels
from citizentech.assistente import evidencias as EV
from replay_verificador import replay, AE
novo = replay()
orig = {json.loads(l)["qid"]: json.loads(l) for l in open(AE.SAIDA / "geracao_e2e_41_20261114-130608.jsonl", encoding="utf-8")}
sem_termos, conflitos = [], []
for k, v in novo.items():
    b = json.loads(orig[k]["saida"]["telemetria"]["saida_bruta"])
    if orig[k]["saida"]["status"] not in ("respondida", "parcial") and k not in ("val-031","val-032","val-044","val-047","val-083","val-087","val-141"): continue
    t = EV.termos_de_conteudo(b["resposta"], orig[k]["pergunta"])
    pr = (v["verificacao"].get("evidencia") or {}).get("protecao", {})
    rr = pr.get("relacoes", [])
    if not t and rr: sem_termos.append((k, len(rr)))
    if any(r["estado"] == "conflito" for r in rr): conflitos.append((k, v["status"], len(t), [(r["fonte"], r["necessaria"], r["bloqueia"]) for r in rr if r["estado"] == "conflito"]))
print("respostas que chegaram ao helper SEM termos de conteudo mensuraveis:", sem_termos)
print("respostas com rotulo conflitante registrado:", conflitos)
out = {}
def run(nome, pergunta, chunks, obj):
    r = rodar(pergunta, chunks, obj)
    out[nome] = {"status": r.status, "problemas": r.verificacao.get("problemas"), "termos": EV.termos_de_conteudo(obj["resposta"], pergunta),
                 "relacoes": [(x["fonte"], x["estado"], x["necessaria"], x["bloqueia"]) for x in rels(r)]}
    print(nome, out[nome])
def o(resp, spans, fontes):
    return saida(resposta=resp, fontes=list(fontes), cand=[{"fonte": f, "resposta_possivel": s} for f, s in spans], evid=[{"fonte": f, "trecho": s} for f, s in spans])
Q = "Qual é o prazo do contrato da empresa Alfa em 2025?"
cA = chunk(1, "Contrato da empresa Alfa em 2025. Vigência: 12 meses.", 301, ordem=0, n=2)
cB = chunk(2, "Anexo do contrato da empresa Alfa em 2025. Objeto: reforma do prédio.", 301, ordem=1, n=2)
spans = [("C1", "Vigência: 12 meses"), ("C2", "Objeto: reforma do prédio")]
run("S1_sem_termos_mensuraveis_rotulo_conflitante_citado_e_nao_usado", Q, [cA, cB], o("O prazo é de 12 meses.", spans, ("C1", "C2")))
run("S1b_controle_mesma_resposta_com_um_termo_mensuravel", "Qual é o prazo do contrato da empresa Alfa em 2025?", [cA, cB], o("O prazo é de 12 meses de vigência contratual.", spans, ("C1", "C2")))
cA3 = chunk(1, "Contrato da empresa Alfa em 2025. Vigência: 12 meses. Reajuste anual conforme índice oficial.", 301, ordem=0, n=2)
cB3 = chunk(2, "Anexo do contrato da empresa Alfa em 2025. Objeto: reforma de serviços cirúrgicos do prédio.", 301, ordem=1, n=2)
run("S3_termo_coincidente_so_no_trecho_conflitante", Q, [cA3, cB3], o("O prazo é de 12 meses; há reajuste anual e a obra cirúrgica não altera o prazo.", [("C1", "Vigência: 12 meses"), ("C2", "Objeto: reforma de serviços cirúrgicos do prédio")], ("C1", "C2")))
cX = chunk(1, "Contrato da empresa Alfa em 2025. Vigência: 12 meses. Objeto: reforma do prédio Santos.", 303)
run("S2_conflitante_e_o_proprio_apoio_da_afirmacao_com_termo_compartilhado", "Qual é o prazo do contrato da empresa Alfa em 2025?", [cX], o("O prazo é de 12 meses para o prédio Santos.", [("C1", "Vigência: 12 meses"), ("C1", "Objeto: reforma do prédio Santos")], ("C1",)))
json.dump({"sem_termos": sem_termos, "conflitos": conflitos, "sinteticos": out}, open(r"D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase4\auditoria_4a_apoio_exclusivo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
