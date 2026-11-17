"""Fase 4D.4 - gera MATRIZ_AVALIACAO_4D4.csv (30 sinteticos da 4D.3 + casos reais). Somente leitura das entradas; escreve so em fase4d4/.
Segunda avaliacao humana: 'pendente' em todas as linhas (nao ha avaliacao humana independente; nada foi inferido)."""
import csv
import glob
import json
import pathlib

AQUI = pathlib.Path(__file__).parent
D43 = AQUI.parent / "fase4d3"
CASOS = json.loads((D43 / "CASOS_DIAGNOSTICOS_4D3.json").read_text(encoding="utf-8"))["casos"]
det = json.loads((D43 / "resultados_4d3_detalhe.json").read_text(encoding="utf-8"))["por_caso"]
b04 = json.loads((AQUI / "b04_c_causas_4d4.json").read_text(encoding="utf-8"))
real = json.loads((AQUI / "real_4d4.json").read_text(encoding="utf-8"))
r150 = json.loads((AQUI / "replay_150_status_4d4.json").read_text(encoding="utf-8"))
regs = {json.loads(ln)["run_id"]: json.loads(ln) for f in sorted(glob.glob(str(AQUI.parent / "validacao_seletiva*.jsonl"))) for ln in open(f, encoding="utf-8")}
ent150 = {x["id"]: x for x in real["res150_entregues"]}
ent21 = {x["id"]: x for x in real["res21_entregues"]}
f = lambda e: "entrega" if e else "bloqueia"  # noqa: E731

COLS = ["id", "origem", "pergunta", "entidade", "atributo", "evidencia", "relacao_entidade_atributo", "conflito", "julgamento_original", "tipo_do_julgamento_original", "segunda_avaliacao_humana",
        "resultado_baseline", "resultado_B1_B2", "resultado_C_estado(4D.3)", "resultado_C_causas(4D.4,diagnostico)", "confianca", "observacoes"]
linhas = []
for c in CASOS:
    j = c["julgamento_referencia"]
    d = det[c["id"]]
    b = b04[c["id"]]
    linhas.append([c["id"], "SINTETICA", c["pergunta"], c["entidade"], c["atributo"], " || ".join(x["span"] for x in c["citacoes"]), c["relacao_entidade_atributo"], "; ".join(c["rotulo_do_trecho"]),
                   f"{j['classe']} / decisão ideal: {j['decisao_ideal_do_pipeline']}", "julgamento de referência do autor dos casos (não independente)", "pendente",
                   f"{f(d['baseline']['entregue'])} ({d['baseline']['status']})", f(d["B1"]["entregue"]) + ("" if d["B1"]["entregue"] == d["B2"]["entregue"] else " / B2 difere"),
                   f(d["C_simplificada"]["entregue"]), "bloqueia" if b["C_causas"] == "BLOQUEIA" else ("entrega" if b["C_causas"] == "libera" else "bloqueia (já bloqueado pela baseline)"), j["confianca"], "; ".join(c["papel_na_analise"])])


def status150(k):
    return r150[k]["status"], r150[k]["problemas"]


def c_de(k, tabela, chave):
    x = tabela.get(k)
    if x is None:
        return "n/a (baseline já bloqueia/abstém)"
    return f"bloqueia (nome '{x[chave]}' ausente do chunk citado não conflitante)" if x[chave] else "entrega"


R = [  # (id, fonte, pergunta, entidade, atributo, evidencia, relacao, conflito, julgamento original, tipo, confianca, observacoes)
    ("val-087-A-r1", "21", "Quais são as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?", "Gama / CRSSU", "COMPETENCIA",
     "C1 doc174 chunk 0004 (inciso IX; o mesmo chunk traz o inciso XI com 'Conselhos de Saúde do Gama') || C2 doc174 chunk 0001 '4 - Titular: Diretor do Hospital Regional do Gama (HRG)' || C3 Art. 1º",
     "implícita/separada: conteúdo (inciso IX) em C1; 'Gama' como cargo de titular em C2", "rótulo 'titular' (MEMBRO) em C2, reconhecido após a 4D.1; não necessário segundo o mecanismo B",
     "validação seletiva: val-087 braço A 0/3 corretas (avaliação cega/auditoria 4C)", "avaliação do projeto (não revisão humana independente)", "media", "único positivo real: B1/B2 corrigem; C chunk-level NÃO corrige porque 'Gama' consta do chunk C1 (inciso XI)"),
    ("val-087-A-r2", "21", "(idem)", "Gama / CRSSU", "COMPETENCIA", "C1 (inciso IX) || C2 'Titular: Diretor do HRG ...'", "separada", "rótulo titular; 'HRG' exclusivo de C2", "abstenção (correta)", "avaliação do projeto", "alta", "controle de bloqueio correto"),
    ("val-087-A-r3", "21", "(idem)", "Gama / CRSSU", "COMPETENCIA", "C1 || C2", "separada", "rótulo titular; 'HRG' exclusivo de C2", "abstenção (correta)", "avaliação do projeto", "alta", "controle de bloqueio correto"),
    ("val-087-B-r1", "21", "(idem)", "Gama / CRSSU", "COMPETENCIA", "C2 'IV - Compete à CRSSU...' || C3 inciso IX (flag S1 ligada)", "explícita (inciso IV, competência regional; sem menção ao Gama)", "nenhum", "correta/parcial (validação seletiva: B 3/3)", "avaliação do projeto", "media", "resposta não repete 'Gama'; o gabarito do dataset diz 'incluindo o Gama'"),
    ("val-024", "150", "Qual foi a modificação contratual realizada para equipamentos de radiologia no Hospital Regional de Ceilândia?", "Hospital Regional de Ceilândia", "OBJETO/modificação", "C1: 'supressão de 5 (cinco) equipamentos de Raio X Panorâmico' (doc 718, ed. 97; lista HRAN, CRT, CEO, UBS 11 - Ceilândia, HRS, HRL)",
     "implícita/ausente: HRC não é citado", "nenhum", "Correta, mas parcial (auditoria 4.3: 'no HRC' repete a premissa da pergunta)", "auditoria 4.3 do projeto (não revisão humana independente)", "media", "localização herdada da pergunta, entregue; gabarito do dataset também a repete"),
    ("val-020", "150", "Quais estabelecimentos de saúde foram credenciados para prestar serviços de radiologia e medicina nuclear no Gama?", "Gama", "ESTABELECIMENTOS credenciados", "C1 doc361 chunk 0001 (Edital 3/2024): credenciamento do Instituto de Medicina Nuclear (CNPJ ...); 'Gama' não consta do chunk citado",
     "implícita: Gama é endereço de filial no documento, fora do chunk citado", "nenhum", "Correta, mas parcial (4.3)", "auditoria 4.3 do projeto", "media", "C bloqueia (perda de recall real); Gama aparece em chunks de outros documentos (C2/C3)"),
    ("val-031", "150", "Quais foram os indicadores de satisfação dos pacientes no Hospital da Criança de Brasília José Alencar durante o terceiro trimestre de 2023?", "Hospital da Criança de Brasília José Alencar", "INDICADORES", "C2 doc1464: 'Satisfação dos Pacientes — ... julho 94,2%, agosto 96,6%, setembro 97,6%'; nome do hospital em outro chunk (C1) do mesmo documento",
     "explícita no documento; entidade em chunk vizinho não citado", "nenhum", "Abstenção indevida na rodada original (4.3: falso positivo de verificação); replay da candidata entrega 'parcial'", "auditoria 4.3 do projeto", "media", "C bloqueia por granularidade de chunk (perda de recall real)"),
    ("val-006", "150", "Qual é o serviço de alimentação hospitalar contratado para as unidades de saúde em Ceilândia?", "Ceilândia", "OBJETO", "C2 doc28 (Contrato 1025/2024): 'fornecimento ininterrupto de alimentação hospitalar ...'; UPAs 24H de Ceilândia no documento", "implícita: localização em outro ponto do mesmo documento", "nenhum",
     "Correta (4.3)", "auditoria 4.3 do projeto", "media", "resposta correta que combina localização da pergunta e documento"),
    ("val-041", "150", "Qual instituição de saúde em Ceilândia teve seu crédito orçamentário descentralizado para pagamento de despesas de exercícios anteriores?", "Ceilândia", "INSTITUIÇÃO beneficiária", "C1–C3 (docs 468/469/398): 'HOSPITAL DAS CLÍNICAS E PRONTO SOCORRO DE FRATURAS DE CEILÂNDIA LTDA'", "explícita (nome contém Ceilândia)", "nenhum", "Correta (4.3)", "auditoria 4.3 do projeto", "alta", "controle positivo real"),
    ("val-130", "150", "Quais empresas foram credenciadas para prestar serviços assistenciais clínicos e cirúrgicos na Asa Sul?", "Asa Sul", "EMPRESAS credenciadas", "C2 doc6: 'Filial (3): ST SHL/NORTE ... ED. Biosphere Health Center – Asa Norte' || C3 doc920: 'VISÃO HOSPITAL DE OLHOS ... Asa Sul'", "conflitante para C2 (Asa Norte)", "localidade_conflitante_no_registro (candidata atual bloqueia)",
     "Incorreta (4.3: Biosphere está na Asa Norte)", "auditoria 4.3 do projeto", "media_alta", "localização herdada da pergunta aplicada a evidência de outra localidade; mecanismo A_LOC, não B"),
    ("val-149", "150", "Quais ações de atenção básica e primária em saúde serão executadas em Ceilândia durante 2025?", "Ceilândia", "AÇÕES", "C2 doc1611 (INAS, Art. 23), C3 gerência nº 07 da Ceilândia...", "não verificável/ausente: nenhuma publicação cita ações em Ceilândia 2025", "publicacao_sem_vinculo_com_a_localidade (candidata atual bloqueia)",
     "Incorreta (4.3)", "auditoria 4.3 do projeto", "media_alta", "mecanismo A_LOC, não B"),
    ("val-083", "150", "Quais itens foram adquiridos para atender as necessidades da Atenção Primária no Guará?", "Atenção Primária / Guará", "ITENS adquiridos", "C1/C2 doc de ratificações: itens com destinatário 'Atenção Primária' e itens com destinatário 'Hospital Regional do Guará' no mesmo chunk",
     "conflitante para itens do 'Hospital Regional do Guará' segundo A_DEST; o gabarito os trata como resposta", "destinatário (A_DEST)", "Abstenção indevida (4.3)", "auditoria 4.3 do projeto", "media", "atributo associado a destinatário diferente; divergência mecanismo×gabarito; não é B"),
    ("val-001", "150", "Qual serviço de manutenção foi contratado para a Policlínica do Núcleo Bandeirante?", "Policlínica do Núcleo Bandeirante", "SERVIÇO", "docs 349 (ed. 48) e 719 (ed. 97): duas autoclaves distintas", "conflito entre duas publicações", "ambiguidade entre publicações",
     "Ambígua de fato (4.3)", "auditoria 4.3 do projeto", "media_alta", "conflito entre publicações; abstenção/ambígua correta"),
]
for (k, fonte, perg, ent, atr, ev, rel, conf, jo, tj, cf, obs) in R:
    if fonte == "21":
        s = regs[k]["saida"]["status"]
        base = f"{f(s in ('respondida', 'parcial'))} ({s})"
        c_est = c_de(k, ent21, "C_estado_bloqueia")
        c_cau = c_de(k, ent21, "C_causas_bloqueia")
        b12 = "bloqueia (B1 e B2)" if k == "val-087-A-r1" else "sem mudança"
    else:
        s, p = status150(k)
        base = f"{f(s in ('respondida', 'parcial'))} ({s}{'; ' + ','.join(p) if p else ''})"
        c_est = c_de(k, ent150, "C_estado_bloqueia")
        c_cau = c_de(k, ent150, "C_causas_bloqueia")
        b12 = "sem mudança (B1/B2 não alteram nenhum dos 150)"
    linhas.append([k, "REAL (" + ("validação seletiva 21" if fonte == "21" else "rodada 4.3, 150") + ")", perg, ent, atr, ev, rel, conf, jo, tj, "pendente", base, b12, c_est, c_cau, cf, obs])
with open(AQUI / "MATRIZ_AVALIACAO_4D4.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(COLS)
    w.writerows(linhas)
print(len(linhas), "linhas")
for L in linhas[30:]:
    print(L[0], "|", L[11], "|", L[12], "|", L[13], "|", L[14])
