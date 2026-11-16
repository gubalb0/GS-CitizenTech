"""Auditoria SOMENTE LEITURA do modelo congelado. Uso: python scripts/auditoria.py
NAO treina para uso, NAO altera dados, testes nem modelo, NAO escolhe configuracao.
Gera:
  docs/modelo_congelado.json                  parametros, classes, vocabulario, hashes, versoes, data
  docs/auditoria_resultados.md / .json        matriz de confusao, P/R/F1, erros, seguranca
O manifesto de congelamento e criado UMA vez e NUNCA sobrescrito: nas execucoes seguintes o script apenas
confere os hashes atuais contra ele e ABORTA se treino, testes, modelo ou regras tiverem mudado.
"""
import collections
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from citizentech import classificador, config, regras  # noqa: E402

DOCS = RAIZ / "docs"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ler(p: Path):
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


ARQ_CONGELADO = DOCS / "modelo_congelado.json"
ARQUIVOS_CONGELADOS = {
    "data/treino.csv": config.ARQ_TREINO,
    "data/teste_rotulado.csv": config.ARQ_TESTE,
    "data/teste_cego.csv": config.ARQ_TESTE_CEGO,
    "data/modelo/classificador.joblib": config.ARQ_MODELO,
    "citizentech/classificador.py": RAIZ / "citizentech" / "classificador.py",
    "citizentech/regras.py": RAIZ / "citizentech" / "regras.py",
}


def hashes_atuais() -> dict:
    return {k: sha256(v) for k, v in ARQUIVOS_CONGELADOS.items()}


def congelar(modelo) -> dict:
    """Cria o manifesto se nao existir; se existir, SO verifica (aborta em qualquer divergencia)."""
    if ARQ_CONGELADO.exists():
        info = json.loads(ARQ_CONGELADO.read_text(encoding="utf-8"))
        diverge = [k for k, v in hashes_atuais().items() if info["sha256"].get(k) != v]
        if diverge:
            raise SystemExit(f"INTEGRIDADE VIOLADA: arquivos diferem do congelamento: {diverge}. Auditoria abortada.")
        print("Integridade OK: todos os hashes conferem com docs/modelo_congelado.json")
        return info
    fu, clf = modelo.named_steps["tfidf"], modelo.named_steps["clf"]
    vocab, cfg = {}, {}
    for nome, v in fu.transformer_list:
        p = v.get_params()
        cfg[nome] = {k: list(p[k]) if isinstance(p[k], tuple) else p[k]
                     for k in ("analyzer", "ngram_range", "sublinear_tf", "min_df", "lowercase", "norm", "use_idf", "smooth_idf")}
        cfg[nome]["tamanho_vocabulario"] = len(v.vocabulary_)
        vocab[nome] = sorted(v.vocabulary_.keys())
    # reprodutibilidade: re-treinar com os MESMOS dados (em memoria) e comparar com o modelo salvo
    novo = classificador.treinar(salvar_em=None)
    X = [classificador.normalizar(r["texto"]) for r in ler(config.ARQ_TESTE) + ler(config.ARQ_TESTE_CEGO)]
    iguais = bool(np.allclose(modelo.predict_proba(X), novo.predict_proba(X), atol=1e-9))
    info = {
        "descricao": "Modelo congelado para auditoria. Nao alterar treino/testes/modelo/regras sem nova versao.",
        "data_auditoria": datetime.now().isoformat(timespec="seconds"),
        "hashes_calculados_sobre": "arquivos originais, sem modificacao, no momento do congelamento",
        "sha256": hashes_atuais(),
        "tfidf": cfg,
        "classificador": {k: str(v) for k, v in clf.get_params().items()},
        "classes": [str(c) for c in modelo.classes_],
        "limiar_confianca_revisao": config.CONFIANCA_MINIMA,
        "regras_urgencia_termos": regras.URGENTES,
        "sla_horas": regras.SLA_H,
        "n_treino": len(ler(config.ARQ_TREINO)),
        "versoes": {"python": platform.python_version(), "scikit-learn": sklearn.__version__,
                    "numpy": np.__version__, "joblib": joblib.__version__},
        "retreino_com_mesmos_dados_reproduz_probabilidades": iguais,
        "vocabulario": vocab,
    }
    ARQ_CONGELADO.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def avaliar(nome, rows, modelo):
    CL = [str(c) for c in modelo.classes_]
    y = [r["categoria"] for r in rows]
    P = []
    for r in rows:
        cat, conf, _ = classificador.classificar(modelo, r["texto"])
        P.append((cat, conf, regras.decidir(cat, conf, r["texto"])))
    yp = [p[0] for p in P]
    cm = confusion_matrix(y, yp, labels=CL)
    pr, rc, f1, sup = precision_recall_fscore_support(y, yp, labels=CL, zero_division=0)
    auto = [i for i, p in enumerate(P) if p[2]["status"] == "encaminhado"]
    rev = [i for i, p in enumerate(P) if p[2]["status"] == "revisao_humana"]
    auto_err = [i for i in auto if yp[i] != y[i]]
    urg = [i for i, c in enumerate(y) if c == "sintomas_urgentes"]
    return {
        "nome": nome, "n": len(rows), "classes": CL,
        "acuracia_ia": round(sum(a == b for a, b in zip(y, yp)) / len(y), 4),
        "matriz_confusao": cm.tolist(),
        "por_classe": {c: {"precisao": round(float(pr[i]), 3), "recall": round(float(rc[i]), 3),
                           "f1": round(float(f1[i]), 3), "n": int(sup[i])} for i, c in enumerate(CL)},
        "pares_confundidos": [[a, b, n] for (a, b), n in collections.Counter(
            (y[i], yp[i]) for i in range(len(y)) if y[i] != yp[i]).most_common()],
        "automaticos": len(auto), "erros_automaticos": len(auto_err),
        "taxa_erro_automatico": round(len(auto_err) / len(auto), 4) if auto else None,
        "revisao_humana": len(rev), "revisao_humana_ja_corretos": sum(yp[i] == y[i] for i in rev),
        "erros_automaticos_detalhe": [{"texto": rows[i]["texto"], "esperado": y[i], "obtido": yp[i],
                                       "confianca": round(P[i][1], 2)} for i in auto_err],
        "urgencias": len(urg),
        "urgencias_com_alta_e_humano": sum(P[i][2]["prioridade"] == "alta" and P[i][2]["status"] == "revisao_humana" for i in urg),
        "urgencias_NAO_protegidas": [{"texto": rows[i]["texto"], "obtido": yp[i], "confianca": round(P[i][1], 2),
                                      "status": P[i][2]["status"]} for i in urg
                                     if not (P[i][2]["prioridade"] == "alta" and P[i][2]["status"] == "revisao_humana")],
        "nao_urgentes_marcados_alta": sum(P[i][2]["prioridade"] == "alta" for i in range(len(y)) if y[i] != "sintomas_urgentes"),
        "faixas_confianca": {f"[{lo},{hi})": {"n": sum(lo <= p[1] < hi for p in P),
                                              "acuracia": round(sum(P[i][0] == y[i] for i in range(len(y)) if lo <= P[i][1] < hi)
                                                                / max(1, sum(lo <= p[1] < hi for p in P)), 2)}
                             for lo, hi in [(0, .3), (.3, .45), (.45, .6), (.6, .8), (.8, 1.01)]},
    }


# Sondagem QUALITATIVA da camada de urgencia: frases do auditor, NAO sao conjunto de teste, NAO geram metrica.
SONDAGEM = ["meu pai nao esta respirando", "acho que minha mae esta tendo um infarto", "suspeita de avc, braco dormente",
            "crianca engoliu um produto de limpeza", "tentativa de suicidio de um familiar",
            "nao tenho dor no peito, so quero marcar consulta", "estou me sentindo muito mal e sozinho, sem esperanca",
            "gestante sem sentir o bebe mexer desde ontem"]


def main():
    modelo = joblib.load(config.ARQ_MODELO)
    info = congelar(modelo)
    t1, t2 = ler(config.ARQ_TESTE), ler(config.ARQ_TESTE_CEGO)
    res = [avaliar("teste1", t1, modelo), avaliar("teste2", t2, modelo), avaliar("combinado", t1 + t2, modelo)]
    sond = []
    for t in SONDAGEM:
        c, cf, _ = classificador.classificar(modelo, t)
        d = regras.decidir(c, cf, t)
        sond.append({"texto": t, "categoria": c, "confianca": round(cf, 2), "prioridade": d["prioridade"], "status": d["status"]})
    (DOCS / "auditoria_resultados.json").write_text(
        json.dumps({"congelamento_ok": info["retreino_com_mesmos_dados_reproduz_probabilidades"],
                    "resultados": res, "sondagem_qualitativa": sond}, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# Resultados da auditoria (gerado por `python scripts/auditoria.py`)", "",
          f"Retreino com os mesmos dados reproduz o modelo salvo: **{info['retreino_com_mesmos_dados_reproduz_probabilidades']}**", ""]
    for r in res:
        md += [f"## {r['nome']} (n={r['n']})", "",
               f"Acuracia da IA: {r['acuracia_ia']:.1%} · automaticos: {r['automaticos']} com {r['erros_automaticos']} erros "
               f"({r['taxa_erro_automatico']:.1%}) · revisao humana: {r['revisao_humana']} (ja corretos: {r['revisao_humana_ja_corretos']}) · "
               f"urgencias protegidas: {r['urgencias_com_alta_e_humano']}/{r['urgencias']} · nao urgentes marcados alta: {r['nao_urgentes_marcados_alta']}", "",
               "Matriz de confusao (linhas=real, colunas=previsto):", "", "| real \\ prev | " + " | ".join(c[:8] for c in r["classes"]) + " |",
               "|---|" + "---|" * len(r["classes"])]
        md += [f"| {c} | " + " | ".join(map(str, row)) + " |" for c, row in zip(r["classes"], r["matriz_confusao"])]
        md += ["", "| Classe | Precisao | Recall | F1 | n |", "|---|---|---|---|---|"]
        md += [f"| {c} | {m['precisao']} | {m['recall']} | {m['f1']} | {m['n']} |" for c, m in r["por_classe"].items()]
        md += ["", "Erros automaticos (encaminhados sem humano e errados):", ""]
        md += [f"- conf {e['confianca']}: esperado `{e['esperado']}`, obtido `{e['obtido']}` — {e['texto']}" for e in r["erros_automaticos_detalhe"]] or ["- (nenhum)"]
        md += ["", "Urgencias NAO protegidas (sem prioridade alta + humano):", ""]
        md += [f"- `{u['obtido']}` conf {u['confianca']} status {u['status']} — {u['texto']}" for u in r["urgencias_NAO_protegidas"]] or ["- (nenhuma)"]
        md += [""]
    md += ["## Sondagem qualitativa da camada de urgencia (NAO e metrica)", "",
           "| Frase | Categoria | Conf. | Prioridade | Status |", "|---|---|---|---|---|"]
    md += [f"| {s['texto']} | {s['categoria']} | {s['confianca']} | {s['prioridade']} | {s['status']} |" for s in sond]
    (DOCS / "auditoria_resultados.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md[:6]))
    print("sha256:", json.dumps(info["sha256"], indent=1))
    # releitura final: nada foi alterado durante a auditoria
    assert hashes_atuais() == info["sha256"], "arquivos mudaram durante a auditoria"


if __name__ == "__main__":
    main()
