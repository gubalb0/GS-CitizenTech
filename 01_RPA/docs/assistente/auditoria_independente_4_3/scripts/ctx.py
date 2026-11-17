import sys, re
sys.path.insert(0, r"D:\Downloads\GS\RPA")
from citizentech.assistente import dados as D
from facts import fold
C = {d["id"]: d for d in D.carregar_corpus()}
def ctx(doc, term, w=300, n=2):
    t = re.sub(r"\s+", " ", C[doc]["texto_completo"] or ""); f = fold(t); k = fold(term); i = 0; c = 0
    print(f"--- doc {doc} [{C[doc]['tipo_documento']} {C[doc]['referencia']} ed.{C[doc]['edicao']} {C[doc]['data_edicao']}] len={len(t)} termo={term!r}")
    while c < n:
        i = f.find(k, i)
        if i < 0:
            if c == 0: print("   (nao encontrado)")
            break
        print("   ...", t[max(0, i - w): i + w], "..."); i += len(k); c += 1
if __name__ == "__main__":
    a = sys.argv[1:]
    for j in range(0, len(a), 2): ctx(int(a[j]), a[j + 1], 300 if len(a) > 2 else 500)
