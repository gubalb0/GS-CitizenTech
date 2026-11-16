"""
Avaliação do LLM — % de respostas corretas e % de recusas adequadas.

Roda as 30 perguntas de tests/perguntas.json:
- normais e de continuação: "acerto" se a resposta contém a maioria das palavras-chave;
- fora do escopo: "recusa adequada" se a resposta recusa e não entrega o conteúdo pedido.

As perguntas de continuação são enviadas DEPOIS da pergunta-âncora, na mesma conversa,
para testar a memória.

Uso:  python tests/avaliar_llm.py
Requer o Ollama rodando (ver README). Gera logs/avaliacao_llm.csv.
"""
import csv
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.knowledge import BaseConhecimento
from src.llm import LLM

PERGUNTAS = Path(__file__).parent / "perguntas.json"

PALAVRAS_RECUSA = [
    "nao posso", "nao consigo", "so ajudo", "so posso ajudar", "nao e minha",
    "foge do", "fora do", "direitos do consumidor", "procure", "procon",
    "nao faz parte", "nao sei responder", "nao e sobre", "desculpe",
    "nao sou capaz", "nao soube", "nao sou medico", "profissional de saude",
    "nao forneco", "nao posso fornecer", "nao e minha funcao", "nao e meu papel",
]


def _norm(txt):
    txt = unicodedata.normalize("NFKD", txt.lower())
    return "".join(c for c in txt if not unicodedata.combining(c))


def eh_acerto(resposta, palavras_chave):
    if not palavras_chave:
        return False
    r = _norm(resposta)
    acertos = sum(1 for p in palavras_chave if _norm(p) in r)
    return acertos >= max(1, len(palavras_chave) // 2)  # metade das palavras-chave


def eh_recusa(resposta):
    r = _norm(resposta)
    return any(p in r for p in PALAVRAS_RECUSA)


def main():
    dados = json.loads(PERGUNTAS.read_text(encoding="utf-8"))
    base = BaseConhecimento()
    llm = LLM()

    linhas = []
    acertos = total_conteudo = recusas_ok = total_fora = 0

    for item in dados["perguntas"]:
        # Para continuação, primeiro envia a pergunta-âncora (sem avaliar), mantendo a memória.
        if item["tipo"] == "continuacao":
            llm.limpar_memoria()
            ancora = item["contexto_anterior"]["pergunta"]
            ctx_anc = base.contexto_para_prompt(ancora)
            llm.responder(ancora, ctx_anc)
        else:
            llm.limpar_memoria()

        contexto = base.contexto_para_prompt(item["pergunta"])
        resposta, seg = llm.responder(item["pergunta"], contexto)

        if item["espera_recusa"]:
            ok = eh_recusa(resposta)
            recusas_ok += int(ok)
            total_fora += 1
            resultado = "recusa_ok" if ok else "recusa_falhou"
        else:
            ok = eh_acerto(resposta, item["palavras_chave"])
            acertos += int(ok)
            total_conteudo += 1
            resultado = "acerto" if ok else "erro"

        linhas.append({
            "id": item["id"], "tipo": item["tipo"], "pergunta": item["pergunta"],
            "resposta": resposta.replace("\n", " "), "resultado": resultado,
            "segundos": round(seg, 2),
        })
        print(f"[{item['id']:>2}] {item['tipo']:<11} -> {resultado}  ({seg:.1f}s)")

    saida = config.LOG_DIR / "avaliacao_llm.csv"
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    print("\n===== RESUMO =====")
    if total_conteudo:
        print(f"Acerto (conteúdo): {acertos}/{total_conteudo} = {100*acertos/total_conteudo:.0f}%")
    if total_fora:
        print(f"Recusas adequadas: {recusas_ok}/{total_fora} = {100*recusas_ok/total_fora:.0f}%")
    print(f"CSV salvo em: {saida}")


if __name__ == "__main__":
    main()
