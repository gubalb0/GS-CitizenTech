import sys, json, re, csv
sys.path.insert(0, r"D:\Downloads\GS\RPA")
from facts import fold, termos, melhor, valores
from ctx import C
F = json.load(open(r"D:\Downloads\GS\RPA\docs\assistente\auditoria_independente_4_3\fatos_por_pergunta.json", encoding="utf-8"))
FQ = {f["qid"]: f for f in F}
from citizentech.assistente.auditoria_multi import preparar
corpus, val, assoc, dup, esperados, docs = preparar()
R = {q["qid"]: (q, esp) for q, esp in zip(val, esperados)}
alvo = "val-007 val-017 val-020 val-021 val-022 val-024 val-032 val-048 val-052 val-053 val-058 val-059 val-060 val-079 val-087 val-095 val-099 val-116 val-119 val-121 val-139".split()
for qid in alvo:
    q, esp = R[qid]; T = termos(q["pergunta"]); kv = valores(q["resposta"])
    print("==", qid, "|", q["pergunta"][:150], "| termos:", len(T))
    for g in esp:
        i = sorted(g)[0]; d = C[i]; f = fold(d["texto_completo"] or ""); ns = re.sub(r"\s+", "", f)
        b, p = melhor(f, ns, T)
        pres = [x for x in kv if fold(x) in f or re.sub(r"\s+", "", fold(x)) in ns]
        print(f"   assoc {i} {d['tipo_documento'][:14]} {str(d['referencia'])[:22]} ed{d['edicao']} cob{b}/{len(T)} vals{len(pres)}/{len(kv)} | {re.sub(chr(10),' ',(d['texto_completo'] or '')[max(0,p-30):p+170])}")
