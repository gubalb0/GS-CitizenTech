"""Auditoria independente 4.3 - passo 1: levantamento de FATOS por pergunta (somente leitura; sem modelo, sem retriever, sem gerador).
Candidatos sao localizados por busca propria (cobertura de termos em janela de 1500 caracteres) sobre o corpus ORIGINAL; nao usa o ranking do sistema."""
import json, re, sys, unicodedata
sys.path.insert(0, r"D:\Downloads\GS\RPA")
from pathlib import Path
from citizentech.assistente import dados as D
RUN = r"D:\Downloads\GS\RPA\data_assistente\derivados\geracao_e2e_41_20261114-130608.jsonl"
OUT = Path(r"D:\Downloads\GS\RPA\docs\assistente\auditoria_independente_4_3")
STOP = set("qual quais quem quando onde como segundo conforme publicado publicada publicacao edicao distrito federal secretaria estado diario oficial dodf sobre acerca foram sendo ainda esta esse essa desse deste pelo pela entre contra cujo cuja valor numero processo".split())
def fold(t): return "".join((unicodedata.normalize("NFKD", c)[:1] or c).lower() for c in unicodedata.normalize("NFC", t))
def termos(q):
    ws = re.findall(r"[\w./-]+", q)
    out = []
    for w in ws:
        f = fold(w).strip(".-/")
        if any(c.isdigit() for c in f):
            out.append(("#", re.sub(r"\s+", "", f)))
        elif len(f) >= 5 and f not in STOP:
            out.append(("w", f[:6]))
    return list(dict.fromkeys(out))
def melhor(doc_f, doc_nospace, T, J=1500):
    ev = []
    for k, (tp, x) in enumerate(T):
        alvo = doc_nospace if tp == "#" else doc_f
        i, c = alvo.find(x), 0
        while i != -1 and c < 200:
            ev.append((i, k)); i = alvo.find(x, i + 1); c += 1
    ev.sort(); best, bp, cnt, e = 0, 0, {}, 0
    for p, k in ev:
        cnt[k] = cnt.get(k, 0) + 1
        while ev[e][0] < p - J:
            cnt[ev[e][1]] -= 1
            if not cnt[ev[e][1]]: del cnt[ev[e][1]]
            e += 1
        if len(cnt) > best: best, bp = len(cnt), ev[e][0]
    return best, bp
def valores(ref):
    v = set(re.findall(r"\d[\d./-]*\d", ref))
    v |= {m for m in re.findall(r"\b[A-ZÀ-Ý][A-ZÀ-Ý0-9]{3,}\b", ref)}
    return sorted(v)
def main():
    C = D.carregar_corpus(); V = D.carregar_validacao()
    docs = {d["id"]: d for d in C}
    F = {i: fold(d["texto_completo"] or "") for i, d in docs.items()}
    NS = {i: re.sub(r"\s+", "", t) for i, t in F.items()}
    R = {}
    for l in open(RUN, encoding="utf-8"):
        o = json.loads(l); R[o["qid"]] = o
    out = []
    for q in V:
        o = R[q["qid"]]; s = o["saida"]; T = termos(q["pergunta"])
        sc = []
        for i in docs:
            b, p = melhor(F[i], NS[i], T)
            if b: sc.append((b, i, p))
        sc.sort(key=lambda x: (-x[0], x[1]))
        top = sc[:6]
        kv = valores(q["resposta"])
        cand = []
        for b, i, p in top:
            d = docs[i]; txt = d["texto_completo"] or ""
            cand.append({"doc_id": i, "cobertura": b, "n_termos": len(T), "ref": f'{d["tipo_documento"]} {d["referencia"]} ed.{d["edicao"]} {d["data_edicao"]}',
                         "chars": len(txt), "valores_ref_presentes": [x for x in kv if fold(x) in F[i] or re.sub(r"\s+", "", fold(x)) in NS[i]],
                         "trecho": re.sub(r"\s+", " ", txt[max(0, p - 80): p + 420])})
        ev = []
        for e in s["evidencias"]:
            did = int(e["chunk_id"].split(":")[0].split("-")[1])
            ids = [f["ids_equivalentes"] for f in s["fontes"] if f["chunk_id"] == e["chunk_id"]]
            ids = ids[0] if ids else [did]
            tf = fold(re.sub(r"\s+", " ", e["trecho"]).strip(" .,;:")); tfs = re.sub(r"\s+", "", tf)
            ev.append({"trecho": e["trecho"], "doc_id": did, "literal_no_doc_citado": any(tfs in NS[i] for i in ids if i in NS)})
        ans = s.get("resposta") or ""
        numA = sorted(set(re.findall(r"\d[\d./-]*\d", ans)))
        cited = {int(f["doc_id"]) for f in s["fontes"]}
        cit_ids = set(); [cit_ids.update(f["ids_equivalentes"]) for f in s["fontes"]]
        sem = [n for n in numA if not any(re.sub(r"\s+", "", fold(n)) in NS[i] for i in cit_ids if i in NS)]
        out.append({"qid": q["qid"], "pergunta": q["pergunta"], "grupo": o["grupo"], "multi": o["multi"], "nao_univoca": o["nao_univoca"], "status": s["status"],
                    "resposta": ans, "evidencias": ev, "docs_citados": sorted(cited), "numeros_da_resposta_ausentes_no_doc_citado": sem,
                    "resposta_dataset(LLM,nao e verdade)": q["resposta"], "valores_ref": kv, "fonte_dataset_data": q["fonte"], "n_termos_pergunta": len(T),
                    "candidatos_independentes": cand, "justificativa_sistema": s.get("justificativa", ""), "identificabilidade": {k: v for k, v in s["telemetria"].get("identificabilidade", {}).items() if k != "concorrentes"},
                    "concorrentes_sistema": [c.get("id") for c in s["telemetria"].get("identificabilidade", {}).get("concorrentes", [])]})
    (OUT / "fatos_por_pergunta.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(out))
if __name__ == "__main__": main()
