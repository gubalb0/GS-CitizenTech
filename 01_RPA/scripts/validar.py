"""Validacao reproduzivel. Uso: python scripts/validar.py
Gera docs/evidencias_resultados.json e docs/evidencias_resultados.md com numeros reais da execucao.
 1) Qualidade da IA em conjunto de teste ROTULADO escrito a mao (80 textos, nao usado no treino)
 2) Baseline de palavras-chave (caminho alternativo) para comparacao
 3) Execucao ponta a ponta com resultado esperado x obtido
 4) Cenario de falha: API de CEP fora do ar (timeout/retry/circuit breaker) sem interromper o lote
 5) Idempotencia: segunda execucao nao reprocessa"""
import csv
import json
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from sklearn.metrics import accuracy_score, classification_report  # noqa: E402

from citizentech import classificador, config, regras  # noqa: E402
from citizentech.estado import Estado  # noqa: E402
from citizentech.geo import ConsultaCEP  # noqa: E402
from citizentech.logs import configurar_log  # noqa: E402
from citizentech.pipeline import executar  # noqa: E402

configurar_log()


def avaliar_ia(arquivo=config.ARQ_TESTE, seguranca=True):
    with arquivo.open(encoding="utf-8") as fh:
        teste = list(csv.DictReader(fh))
    y = [r["categoria"] for r in teste]
    modelo = classificador.treinar(salvar_em=None)  # treina so com data/treino.csv
    out = {"n_teste": len(teste)}
    for nome, m in (("ml_tfidf_logreg", modelo), ("baseline_palavras_chave", None)):
        pred = [classificador.classificar(m, r["texto"]) for r in teste]
        yp = [p[0] for p in pred]
        conf = [p[1] for p in pred]
        auto = [i for i, c in enumerate(conf) if c >= config.CONFIANCA_MINIMA]
        out[nome] = {
            "acuracia": round(accuracy_score(y, yp), 3),
            "acertos": sum(a == b for a, b in zip(y, yp)),
            "acuracia_nos_encaminhados_automaticamente": round(
                sum(y[i] == yp[i] for i in auto) / len(auto), 3) if auto else None,
            "taxa_enviada_revisao_humana": round(1 - len(auto) / len(teste), 3),
            "relatorio_por_classe": classification_report(y, yp, output_dict=True, zero_division=0),
            "erros": [{"texto": teste[i]["texto"], "esperado": y[i], "obtido": yp[i], "confianca": round(conf[i], 2)}
                      for i in range(len(teste)) if y[i] != yp[i]],
        }
    if not seguranca:
        return out
    # Metrica de seguranca: fluxo completo IA + regras. Urgencia clinica deve acabar com humano.
    urg = [i for i, c in enumerate(y) if c == "sintomas_urgentes"]
    nao = [i for i in range(len(y)) if i not in urg]
    def humano_alta(i):
        c, cf, _ = classificador.classificar(modelo, teste[i]["texto"])
        d = regras.decidir(c, cf, teste[i]["texto"])
        return d["prioridade"] == "alta" and d["status"] == "revisao_humana"
    out["seguranca_urgencia_clinica"] = {
        "urgentes_no_teste": len(urg),
        "urgentes_com_alta_e_revisao_humana": sum(humano_alta(i) for i in urg),
        "nao_urgentes_marcados_alta": sum(
            regras.decidir(*classificador.classificar(modelo, teste[i]["texto"])[:2], teste[i]["texto"])["prioridade"] == "alta"
            for i in nao),
        "nao_urgentes_no_teste": len(nao),
        "urgentes_NAO_protegidos": [{"texto": teste[i]["texto"], "categoria_obtida": classificador.classificar(modelo, teste[i]["texto"])[0]}
                                    for i in urg if not humano_alta(i)],
    }
    return out


def _copiar_inbox(destino: Path) -> Path:
    inbox = destino / "inbox"
    shutil.copytree(config.DIR_INBOX, inbox)
    return inbox


def ponta_a_ponta_e_falha():
    res = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        inbox = _copiar_inbox(tmp)
        # --- cenario normal (API real; se a rede cair, o proprio fluxo trata) ---
        estado = Estado(tmp / "e1.db")
        r1 = executar(inbox, tmp / "s1", estado=estado)
        r1b = executar(inbox, tmp / "s1b", estado=estado)  # idempotencia
        esperado = {"registros_lidos": 25, "processados": 21, "rejeitados_invalidos": 3,
                    "duplicados_ignorados": 1, "arquivos_com_falha": 2, "erros_processamento": 0}
        res["execucao_normal"] = {"esperado": esperado,
                                  "obtido": {k: r1[k] for k in esperado},
                                  "confere": all(r1[k] == v for k, v in esperado.items()),
                                  "resumo": r1}
        res["idempotencia_segunda_execucao"] = {
            "processados": r1b["processados"], "duplicados_ignorados": r1b["duplicados_ignorados"],
            "confere": r1b["processados"] == 0 and r1b["duplicados_ignorados"] == 21 + 1}
        # --- cenario de falha: API de CEP inacessivel ---
        estado2 = Estado(tmp / "e2.db")
        api_fora = ConsultaCEP(url="http://127.0.0.1:9/{cep}", timeout=0.5, retries=2, backoff=0.05)
        r2 = executar(inbox, tmp / "s2", estado=estado2, cep_api=api_fora)
        res["falha_api_cep_fora_do_ar"] = {
            "processados": r2["processados"], "erros_processamento": r2["erros_processamento"],
            "falhas_http_cep": r2["falhas_http_cep"], "consultas_cep_http": r2["consultas_cep_http"],
            "cep_indisponivel_nos_resultados": r2["cep_indisponivel"],
            "lote_completo_apesar_da_falha": r2["processados"] == r1["processados"],
        }
        estado.fechar(); estado2.fechar()
    return res


def main():
    resultado = {"ia": avaliar_ia(), "ia_teste_cego": avaliar_ia(config.ARQ_TESTE_CEGO, True), **ponta_a_ponta_e_falha()}
    (RAIZ / "docs").mkdir(exist_ok=True)
    (RAIZ / "docs" / "evidencias_resultados.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    ia = resultado["ia"]
    ml, bl = ia["ml_tfidf_logreg"], ia["baseline_palavras_chave"]
    md = [
        "# Resultados da validacao (gerado por `python scripts/validar.py`)", "",
        f"## 1. IA - conjunto de teste rotulado (n={ia['n_teste']}, escrito a mao, fora do treino)", "",
        "| Metodo | Acuracia | Acertos | Acuracia nos encaminhados automaticamente | % enviado a revisao humana |",
        "|---|---|---|---|---|",
        f"| TF-IDF palavras+caracteres + Reg. Logistica | {ml['acuracia']} | {ml['acertos']}/{ia['n_teste']} | {ml['acuracia_nos_encaminhados_automaticamente']} | {ml['taxa_enviada_revisao_humana']} |",
        f"| Baseline palavras-chave | {bl['acuracia']} | {bl['acertos']}/{ia['n_teste']} | {bl['acuracia_nos_encaminhados_automaticamente']} | {bl['taxa_enviada_revisao_humana']} |",
        "", "### Erros do modelo ML", "", "| Texto | Esperado | Obtido | Confianca |", "|---|---|---|---|",
    ]
    md += [f"| {e['texto']} | {e['esperado']} | {e['obtido']} | {e['confianca']} |" for e in ml["erros"]] or ["| (nenhum) | | | |"]
    cg = resultado["ia_teste_cego"]
    mc, bc = cg["ml_tfidf_logreg"], cg["baseline_palavras_chave"]
    md += ["", f"## 1b. IA - segundo conjunto de teste (n={cg['n_teste']}, escrito ANTES da ampliacao do treino)", "",
           "| Metodo | Acuracia | Acertos | Acuracia nos automaticos | % revisao humana |", "|---|---|---|---|---|",
           f"| TF-IDF palavras+caracteres + Reg. Logistica | {mc['acuracia']} | {mc['acertos']}/{cg['n_teste']} | {mc['acuracia_nos_encaminhados_automaticamente']} | {mc['taxa_enviada_revisao_humana']} |",
           f"| Baseline palavras-chave | {bc['acuracia']} | {bc['acertos']}/{cg['n_teste']} | {bc['acuracia_nos_encaminhados_automaticamente']} | {bc['taxa_enviada_revisao_humana']} |"]
    s1, s2 = ia["seguranca_urgencia_clinica"], cg["seguranca_urgencia_clinica"]
    comb_u = s1["urgentes_no_teste"] + s2["urgentes_no_teste"]
    comb_p = s1["urgentes_com_alta_e_revisao_humana"] + s2["urgentes_com_alta_e_revisao_humana"]
    comb_fa = s1["nao_urgentes_marcados_alta"] + s2["nao_urgentes_marcados_alta"]
    comb_n = s1["nao_urgentes_no_teste"] + s2["nao_urgentes_no_teste"]
    md += ["", "### Seguranca: urgencia clinica no fluxo completo (IA + regras)", "",
           "**ATENCAO:** o resultado '10/10' vale SOMENTE para o teste 1. No teste 2 e no conjunto combinado ha urgencia nao protegida.", "",
           "| Conjunto | Urgencias com prioridade alta + revisao humana | Nao urgentes marcados alta (falso alarme) |", "|---|---|---|",
           f"| Teste 1 | {s1['urgentes_com_alta_e_revisao_humana']}/{s1['urgentes_no_teste']} | {s1['nao_urgentes_marcados_alta']}/{s1['nao_urgentes_no_teste']} |",
           f"| Teste 2 | {s2['urgentes_com_alta_e_revisao_humana']}/{s2['urgentes_no_teste']} | {s2['nao_urgentes_marcados_alta']}/{s2['nao_urgentes_no_teste']} |",
           f"| **Combinado** | **{comb_p}/{comb_u}** | {comb_fa}/{comb_n} |", "",
           "Urgencias NAO protegidas (encaminhadas sem revisao humana):", ""]
    md += [f"- (teste 2) classificada como `{u['categoria_obtida']}`: \"{u['texto']}\"" for u in s2["urgentes_NAO_protegidos"]]
    md += [f"- (teste 1) classificada como `{u['categoria_obtida']}`: \"{u['texto']}\"" for u in s1["urgentes_NAO_protegidos"]]
    md += ["", "Referencia atual dos numeros: `docs/auditoria_ia.md` e `docs/auditoria_resultados.md` (`python scripts/auditoria.py`).",
           "Esta pagina e GERADA por `python scripts/validar.py`; os numeros de IA e de ponta a ponta nao foram alterados, apenas a apresentacao da metrica de seguranca foi ampliada para os dois testes."]
    n = resultado["execucao_normal"]
    md += ["", "## 2. Ponta a ponta (data/inbox)", "", "| Metrica | Esperado | Obtido |", "|---|---|---|"]
    md += [f"| {k} | {v} | {n['obtido'][k]} |" for k, v in n["esperado"].items()]
    md += [f"", f"Confere: **{n['confere']}**. Tempo: {n['resumo']['tempo_segundos']} s.",
           "", "## 3. Idempotencia", "", json.dumps(resultado["idempotencia_segunda_execucao"]),
           "", "## 4. Falha tratada: API de CEP fora do ar", "", "```json",
           json.dumps(resultado["falha_api_cep_fora_do_ar"], indent=2), "```"]
    (RAIZ / "docs" / "evidencias_resultados.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
