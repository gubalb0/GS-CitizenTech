"""Avaliacao UNICA e sem ajuste do conjunto de validacao independente.

Fluxo (ver README.md desta pasta):
  1) Custodiante (NAO desenvolvedor) guarda o CSV rotulado FORA do repositorio de desenvolvimento.
  2) Custodiante lacra:   python validacao_independente/avaliar.py --lacrar  --conjunto CAMINHO.csv --custodiante "Nome"
  3) Custodiante avalia:  python validacao_independente/avaliar.py --avaliar --conjunto CAMINHO.csv
O script RECUSA avaliar se: o conjunto mudou desde o lacre; o modelo/regras mudaram desde o congelamento;
ou se ja houve uma avaliacao desse lacre (salvo --repetir com --justificativa, que fica registrada).
Este script nunca treina nem altera o modelo.
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import joblib
from sklearn.metrics import cohen_kappa_score, confusion_matrix, precision_recall_fscore_support

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
sys.path.insert(0, str(RAIZ))

from citizentech import classificador, config, regras  # noqa: E402

CLASSES = ["agendamento_consulta", "exames_resultados", "informacoes_gerais", "medicamentos",
           "reclamacao_atendimento", "sintomas_urgentes", "vacinacao", "visita_domiciliar"]
FORA = "fora_do_escopo"
OBRIGATORIAS = ["id_texto", "texto", "rotulo_final"]
# Tamanho minimo recomendado (abaixo disso o relatorio sai marcado como EXPLORATORIO)
MIN_POR_CLASSE, MIN_FORA, MIN_URGENTES = 30, 30, 40
LACRE = PASTA / "LACRE.json"
REGISTRO = PASTA / "registro_execucoes.jsonl"
CONGELADO = RAIZ / "docs" / "modelo_congelado.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hashes_codigo() -> dict:
    return {"modelo": sha(config.ARQ_MODELO),
            "classificador.py": sha(RAIZ / "citizentech" / "classificador.py"),
            "regras.py": sha(RAIZ / "citizentech" / "regras.py")}


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 3), round(min(1, c + h), 3)]


def ler_conjunto(p: Path):
    with p.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    faltam = [c for c in OBRIGATORIAS if not rows or c not in rows[0]]
    if faltam:
        raise SystemExit(f"Colunas obrigatorias ausentes: {faltam}")
    erros = []
    ids = set()
    for i, r in enumerate(rows, start=2):
        if r["id_texto"] in ids:
            erros.append(f"linha {i}: id duplicado {r['id_texto']}")
        ids.add(r["id_texto"])
        if r["rotulo_final"] not in CLASSES + [FORA]:
            erros.append(f"linha {i}: rotulo_final invalido '{r['rotulo_final']}'")
        if not (r["texto"] or "").strip():
            erros.append(f"linha {i}: texto vazio")
    if erros:
        raise SystemExit("Conjunto invalido:\n" + "\n".join(erros[:20]))
    return rows


def lacrar(args):
    if LACRE.exists():
        raise SystemExit("Ja existe LACRE.json. Um conjunto so pode ser lacrado uma vez.")
    if not CONGELADO.exists():
        raise SystemExit("Rode scripts/auditoria.py para gerar o congelamento antes de lacrar.")
    rows = ler_conjunto(args.conjunto)
    LACRE.write_text(json.dumps({
        "lacrado_em": datetime.now().isoformat(timespec="seconds"), "custodiante": args.custodiante,
        "n_textos": len(rows), "sha256_conjunto": sha(args.conjunto), "hashes_modelo_e_regras": hashes_codigo(),
        "declaracao": "O custodiante declara que o conjunto nao foi usado em treino, ajuste ou selecao de configuracao.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Lacrado: {len(rows)} textos. Nao altere conjunto, modelo nem regras antes da avaliacao.")


def avaliar(args):
    if not LACRE.exists():
        raise SystemExit("Sem LACRE.json: lacre o conjunto primeiro (--lacrar).")
    lacre = json.loads(LACRE.read_text(encoding="utf-8"))
    if sha(args.conjunto) != lacre["sha256_conjunto"]:
        raise SystemExit("RECUSADO: o conjunto mudou depois do lacre.")
    if hashes_codigo() != lacre["hashes_modelo_e_regras"]:
        raise SystemExit("RECUSADO: modelo/regras mudaram depois do lacre. Avalie a versao lacrada.")
    anteriores = [json.loads(l) for l in REGISTRO.read_text(encoding="utf-8").splitlines()] if REGISTRO.exists() else []
    if anteriores and not (args.repetir and args.justificativa):
        raise SystemExit("RECUSADO: este conjunto ja foi avaliado. Repeticao exige --repetir --justificativa '...' (fica registrada).")

    rows = ler_conjunto(args.conjunto)
    modelo = joblib.load(config.ARQ_MODELO)
    P = []
    for r in rows:
        cat, conf, _ = classificador.classificar(modelo, r["texto"])
        P.append((cat, conf, regras.decidir(cat, conf, r["texto"])))
    y = [r["rotulo_final"] for r in rows]
    yp = [p[0] for p in P]
    dentro = [i for i in range(len(rows)) if y[i] != FORA]
    fora = [i for i in range(len(rows)) if y[i] == FORA]
    auto = [i for i in dentro if P[i][2]["status"] == "encaminhado"]
    auto_err = [i for i in auto if yp[i] != y[i]]
    urg = [i for i in dentro if y[i] == "sintomas_urgentes"]
    # urgencia tambem por flag clinica independente da categoria (se o rotulador marcou)
    urg_flag = [i for i, r in enumerate(rows) if (r.get("urgencia_clinica") or "").lower() == "sim"]
    urg_all = sorted(set(urg) | set(urg_flag))
    prot = [i for i in urg_all if P[i][2]["prioridade"] == "alta" and P[i][2]["status"] == "revisao_humana"]
    acertos = sum(yp[i] == y[i] for i in dentro)
    cont = collections.Counter(y)
    exploratorio = (any(cont[c] < MIN_POR_CLASSE for c in CLASSES) or cont[FORA] < MIN_FORA or len(urg_all) < MIN_URGENTES)
    pr, rc, f1, sup = precision_recall_fscore_support([y[i] for i in dentro], [yp[i] for i in dentro], labels=CLASSES, zero_division=0)
    rel = {
        "executado_em": datetime.now().isoformat(timespec="seconds"), "lacre": lacre,
        "repeticao": bool(anteriores), "justificativa_repeticao": args.justificativa,
        "status_do_relatorio": "EXPLORATORIO (amostra abaixo do minimo)" if exploratorio else "CONFIRMATORIO",
        "n_total": len(rows), "n_por_rotulo": dict(cont), "minimos_exigidos": {"por_classe": MIN_POR_CLASSE, "fora_do_escopo": MIN_FORA, "urgencias": MIN_URGENTES},
        "acuracia_ia_no_escopo": {"acertos": acertos, "n": len(dentro), "taxa": round(acertos / len(dentro), 4), "ic95_wilson": wilson(acertos, len(dentro))},
        "automaticos": {"n": len(auto), "erros": len(auto_err),
                        "taxa_erro": round(len(auto_err) / len(auto), 4) if auto else None, "ic95_wilson": wilson(len(auto_err), len(auto))},
        "urgencias": {"n": len(urg_all), "protegidas_alta_e_humano": len(prot),
                      "NAO_protegidas": [{"id_texto": rows[i]["id_texto"], "obtido": yp[i], "status": P[i][2]["status"]} for i in urg_all if i not in prot],
                      "ic95_wilson_protecao": wilson(len(prot), len(urg_all))},
        "fora_do_escopo": {"n": len(fora), "enviados_a_humano": sum(P[i][2]["status"] == "revisao_humana" for i in fora),
                           "encaminhados_automaticamente_ERRO": [rows[i]["id_texto"] for i in fora if P[i][2]["status"] == "encaminhado"]},
        "revisao_humana_no_escopo": sum(P[i][2]["status"] == "revisao_humana" for i in dentro),
        "por_classe": {c: {"precisao": round(float(pr[k]), 3), "recall": round(float(rc[k]), 3), "f1": round(float(f1[k]), 3), "n": int(sup[k])} for k, c in enumerate(CLASSES)},
        "matriz_confusao": {"classes": CLASSES, "linhas": confusion_matrix([y[i] for i in dentro], [yp[i] for i in dentro], labels=CLASSES).tolist()},
        "erros_automaticos_ids": [rows[i]["id_texto"] for i in auto_err],
    }
    if "ambigua" in rows[0]:
        amb = [i for i in dentro if (rows[i].get("ambigua") or "").lower() == "sim"]
        rel["ambiguos"] = {"n": len(amb), "acertos": sum(yp[i] == y[i] for i in amb), "enviados_a_humano": sum(P[i][2]["status"] == "revisao_humana" for i in amb)}
    if "rotulo_1" in rows[0] and "rotulo_2" in rows[0]:
        pares = [(r["rotulo_1"], r["rotulo_2"]) for r in rows if r["rotulo_1"] and r["rotulo_2"]]
        if pares:
            rel["concordancia_rotuladores"] = {"n": len(pares), "kappa_cohen": round(float(cohen_kappa_score([a for a, _ in pares], [b for _, b in pares])), 3),
                                               "discordancias": sum(a != b for a, b in pares)}
    nome = f"relatorio_{lacre['sha256_conjunto'][:8]}_{datetime.now():%Y%m%d%H%M%S}.json"
    (PASTA / nome).write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
    with REGISTRO.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"em": rel["executado_em"], "relatorio": nome, "repeticao": rel["repeticao"], "justificativa": args.justificativa}, ensure_ascii=False) + "\n")
    print(json.dumps({k: rel[k] for k in ("status_do_relatorio", "acuracia_ia_no_escopo", "automaticos", "urgencias", "fora_do_escopo")}, ensure_ascii=False, indent=2))
    print("Relatorio completo:", PASTA / nome)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--lacrar", action="store_true")
    g.add_argument("--avaliar", action="store_true")
    ap.add_argument("--conjunto", type=Path, required=True)
    ap.add_argument("--custodiante", default="")
    ap.add_argument("--repetir", action="store_true")
    ap.add_argument("--justificativa", default="")
    a = ap.parse_args(argv)
    if a.lacrar and not a.custodiante:
        raise SystemExit("--custodiante e obrigatorio ao lacrar.")
    (lacrar if a.lacrar else avaliar)(a)


if __name__ == "__main__":
    main()
