"""Fase 4D.7 - monta RESULTADOS_4D7.csv comparando, alvo a alvo, o resultado ORIGINAL armazenado da 4D.5 (v3, somente leitura) com o resultado CORRIGIDO (reexecucao com prototipo_vinculo_4d7).
Nao calcula precisao nem recall: a coluna de concordancia compara cada alvo com o rotulo congelado da 4D.5 (sem segundo avaliador humano)."""
import csv
import json
import pathlib

AQUI = pathlib.Path(__file__).parent
SCR = pathlib.Path(r"C:/Users/henry/AppData/Local/Temp/claude/1d1f73d24e18fb6a/619b1d2d-4dd6-4445-ba09-b40d8dcd3ae8/scratchpad")
orig = json.loads((AQUI.parent / "fase4d5" / "resultados_4d5_detalhe.json").read_text(encoding="utf-8"))
nova = json.loads((SCR / "resultados_4d7_detalhe.json").read_text(encoding="utf-8"))
NIV = ["N1", "N2", "N3", "N4"]
cols = (["origem", "id", "alvo", "esperado_rotulo_4D5"] + [f"{n}_original" for n in NIV] + [f"{n}_corrigido" for n in NIV] + [f"{n}_aceita_orig>corr" for n in NIV]
        + [f"{n}_concordancia_orig>corr" for n in NIV] + ["mudou", "detalhes_mudaram", "nota"])
n_mudou = 0
with open(AQUI / "RESULTADOS_4D7.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(cols)
    for x, y in zip(orig, nova):
        assert (x["origem"], x["id"], x["alvo"], x["esperado"]) == (y["origem"], y["id"], y["alvo"], y["esperado"]), "casos/rotulos divergem entre original e corrigido"
        mudou = x["estados"] != y["estados"] or x["aceita"] != y["aceita"]
        n_mudou += mudou
        w.writerow([x["origem"], x["id"], x["alvo"], x["esperado"]] + [x["estados"][n] for n in NIV] + [y["estados"][n] for n in NIV]
                   + [f"{int(x['aceita'][n])}>{int(y['aceita'][n])}" for n in NIV] + [f"{x['classe'][n]}>{y['classe'][n]}" for n in NIV]
                   + ["SIM" if mudou else "nao", "SIM" if x["detalhes"] != y["detalhes"] else "nao", y["nota"][:140]])
print(len(orig), "alvos;", n_mudou, "mudaram")
