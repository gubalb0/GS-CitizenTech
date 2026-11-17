"""Gera o material de AUDITORIA INDEPENDENTE (para uma segunda pessoa) a partir de uma rodada end-to-end.

Uso: python -m citizentech.assistente.auditoria <caminho do geracao_e2e_41_<run_id>.jsonl>
Saidas (docs/assistente/): auditoria_e2e_<run_id>.csv (UTF-8 com BOM, abre no Excel) e auditoria_e2e_<run_id>.md (guia).
A classificacao automatica NAO e verdade definitiva: os campos de julgamento humano ficam em branco.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from . import dados as D

CAMPOS = ["prioridade_de_revisao", "qid", "grupo_automatico(A=fonte correta enviada;B=nao)", "multi", "pergunta", "fontes_recuperadas(enviadas marcadas com *)",
          "resposta_produzida", "status_atribuido", "evidencias_citadas", "fontes_citadas", "verificacao_automatica", "identificabilidade_e_cobertura(4.2/4.3)", "justificativa_do_sistema",
          "referencia_do_dataset(gerada por LLM; nao e verdade definitiva)",
          "JULGAMENTO_HUMANO(correta/incorreta/parcial/ambigua_adequada/ambigua_inadequada/abstencao_adequada/abstencao_inadequada)",
          "a_resposta_esta_sustentada_na_fonte_citada?(sim/nao)", "a_fonte_citada_e_a_publicacao_certa?(sim/nao/indeterminado)", "observacoes", "revisor"]


def prioridade(o: dict) -> str:
    st = o["saida"]["status"]
    if st in ("respondida", "parcial"):
        return "1-REVISAR (resposta dada)"
    if st == "ambigua":
        return "2-REVISAR (ambigua)"
    if o["saida"]["telemetria"].get("erro_tecnico"):
        return "4-erro tecnico"
    return "3-abstencao (amostra)"


def linha(o: dict) -> list:
    s = o["saida"]
    fr = "\n".join(f"{'*' if f['enviado'] else ' '}{f['posicao']}. {f['chunk_id']} | {f['tipo_documento']} {f['referencia']} | DODF ed.{f['edicao']} {f['data_edicao']}"
                   f" | score {f['score']} | {f['trecho_inicial'][:160]!r}" for f in o["fontes_recuperadas"])
    ev = "\n".join(f"[{e['fonte']}] literal={e['literal']}: {e['trecho']}" for e in s["evidencias"])
    fc = "\n".join(f"{f['id']} {f['chunk_id']} (doc {f['doc_id']}; {f['tipo_documento']} {f['referencia']}; {f['data_edicao']})" for f in s["fontes"])
    ver = json.dumps(s["verificacao"], ensure_ascii=False)
    t = s["telemetria"]
    ind = json.dumps({k: (({a: b for a, b in t[k].items() if a != "concorrentes"}) if isinstance(t[k], dict) else t[k]) for k in ("identificabilidade", "cobertura_lista") if t.get(k)}, ensure_ascii=False)
    return [prioridade(o), o["qid"], o["grupo"], "sim" if o["multi"] else "nao", o["pergunta"], fr, s["resposta"], s["status"], ev, fc, ver, ind, s["justificativa"],
            o["resposta_referencia"], "", "", "", "", ""]


def main(arq: Path) -> tuple[Path, Path]:
    L = [json.loads(l) for l in arq.open(encoding="utf-8")]
    run_id = L[0]["run_id"]
    L.sort(key=lambda o: (prioridade(o), o["qid"]))
    csv_p = D.RAIZ / "docs" / "assistente" / f"auditoria_e2e_{run_id}.csv"
    with csv_p.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(CAMPOS)
        w.writerows(linha(o) for o in L)
    n1 = sum(1 for o in L if o["saida"]["status"] in ("respondida", "parcial"))
    n2 = sum(1 for o in L if o["saida"]["status"] == "ambigua")
    md = f"""# Auditoria independente — rodada end-to-end `{run_id}`

Arquivo: `{csv_p.name}` ({len(L)} perguntas; separador `;`, UTF-8 com BOM). Ordenado por prioridade de revisão.

## Como revisar
1. Revisar **todas** as linhas de prioridade 1 (**{n1}** respostas dadas: status `respondida` ou `parcial`) e 2 (**{n2}** `ambigua`). As abstenções (prioridade 3) podem ser amostradas (sugestão: 30 linhas sorteadas, mais todas as do grupo A).
2. Para cada linha, ler a pergunta, as fontes recuperadas (as enviadas ao modelo estão marcadas com `*`), a resposta e as evidências citadas.
3. Preencher `JULGAMENTO_HUMANO`, as duas perguntas sim/não e as observações. **Não** usar o status automático nem a coluna de referência como verdade: a referência vem do dataset DODF Public Health QA, gerada por LLM, e pode estar incompleta ou ser uma entre várias publicações semelhantes.
4. Casos de especial atenção: respostas dadas em perguntas de grupo B (a fonte correta não estava no contexto enviado), perguntas `MULTI` e as 6 perguntas não unívocas (val-005/018/023/120/122/146).
5. Devolver o CSV preenchido; a concordância entre o status automático e o julgamento humano deve ser reportada separadamente.

## Observações
- `grupo_automatico` vem da associação QA→publicação da Etapa 2 (igualdade exata de texto) e dos chunks efetivamente enviados; ele não julga a resposta.
- `verificacao_automatica` lista os problemas que o código encontrou (trecho não literal, valor não sustentado, publicação concorrente etc.).
- Nenhum dado pessoal real consta nos arquivos: o corpus é público (DODF, CC BY 4.0).
"""
    md_p = D.RAIZ / "docs" / "assistente" / f"auditoria_e2e_{run_id}.md"
    md_p.write_text(md, encoding="utf-8")
    return csv_p, md_p


if __name__ == "__main__":
    print(main(Path(sys.argv[1])))
