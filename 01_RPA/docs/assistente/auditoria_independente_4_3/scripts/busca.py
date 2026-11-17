import sys, re
from ctx import C, fold, ctx
F = {i: fold(d["texto_completo"] or "") for i, d in C.items()}
def busca(*t, n=14):
    k = [fold(x) for x in t]
    r = [i for i, f in F.items() if all(x in f for x in k)]
    print(f"## {t}: {len(r)} docs")
    for i in r[:n]:
        d = C[i]; print("  ", i, d["tipo_documento"], d["referencia"], "ed", d["edicao"], d["data_edicao"])
if __name__ == "__main__":
    for a in sys.argv[1:]:
        busca(*a.split("&"))
