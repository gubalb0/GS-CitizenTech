"""Fase 4D.4 - gera o pacote de revisao humana (versao CEGA) e a versao de REFERENCIA (com julgamentos originais) a partir dos casos 4D.3 (somente leitura).
A versao cega NAO contem: julgamento original, justificativa, relacao alegada, descricao/papel dos casos, saida do pipeline, resultado de variantes, nem os IDs originais."""
import hashlib
import json
import pathlib
import re

AQUI = pathlib.Path(__file__).parent
D43 = AQUI.parent / "fase4d3"
CASOS = {c["id"]: c for c in json.loads((D43 / "CASOS_DIAGNOSTICOS_4D3.json").read_text(encoding="utf-8"))["casos"]}
ORDEM = [("Caso 1", "A07"), ("Caso 2", "B04"), ("Caso 3", "A02"), ("Caso 4", "A06")]   # ordem embaralhada; mapeamento so na versao de referencia
DOCS = {"Ordem de Serviço nº 93/2025": "documento FICTÍCIO (sintético)", "Extrato de Contrato nº 12/2025": "documento FICTÍCIO (sintético)"}


def rotulo_textual(span):
    m = re.match(r"\s*(?:\d{1,3}\s*[-–)]\s*|[IVX]+\s*[-–)]\s*)?([^\W\d_][^:\n]{0,38}):", span)
    return f"“{m.group(1).strip()}:”" if m else "sem rótulo com dois-pontos no início do trecho citado"


def origem(texto):
    return next((k for k in DOCS if texto.startswith(k) or k in texto[:80]), "documento fictício")


cega = ["# Pacote de revisão humana — Fase 4D.4 (VERSÃO CEGA)", "",
        "**Material preparado para uma segunda avaliação humana. Nenhuma avaliação foi feita nem simulada: os campos de resposta estão em branco.**", "",
        "Todos os documentos abaixo são **fictícios (sintéticos)**: foram escritos para o diagnóstico, não vêm do DODF. Esta versão não traz julgamentos anteriores, justificativas, saídas do sistema nem resultados de variantes, de propósito. Por favor, **não consulte** o relatório da Fase 4D.3 nem a versão de referência antes de preencher.", "",
        "## Como avaliar",
        "Para cada caso, responda com base **apenas** nos trechos mostrados:",
        "1. **Correção semântica** da resposta no mundo descrito pelos trechos: `correta` | `parcialmente correta` | `incorreta` | `não verificável`.",
        "2. **Sustentação pelos trechos citados**: a resposta (inclusive a entidade/localização mencionada) é sustentada pelos trechos citados? `sim` | `parcial` | `não` | `não verificável`.",
        "3. **Decisão desejável para um assistente que prefere abster-se a errar**: `entregar` | `bloquear` | `indeterminado`.",
        "4. Se a resposta menciona uma entidade/localidade que também está na pergunta: ela é sustentada pelos trechos, ou apenas repete a pergunta?",
        "5. Confiança (`alta`/`média`/`baixa`) e comentário livre. Se houver mais de uma interpretação plausível, marque `não verificável`/`indeterminado` em vez de forçar.", ""]
for nome, cid in ORDEM:
    c = CASOS[cid]
    cega += [f"---", f"## {nome}", f"**Pergunta:** {c['pergunta']}", f"**Resposta candidata:** {c['resposta']}", f"**Entidade de interesse:** {c['entidade']}  |  **Atributo perguntado:** {c['atributo']}", "", "**Trechos disponíveis (texto integral do trecho):**"]
    for i, ch in enumerate(c["chunks"], 1):
        cega.append(f"- **T{i}** — origem: {origem(ch['texto'])} ({DOCS.get(origem(ch['texto']), 'fictício')}), documento nº {ch['doc']}, trecho {ch['ordem'] + 1} de {ch['n_chunks_doc']}.  \n  > {ch['texto']}")
    cega += ["", "**Trechos efetivamente citados como evidência na resposta:**"]
    for x in c["citacoes"]:
        k = [ch["chave"] for ch in c["chunks"]].index(x["chunk"]) + 1
        cega.append(f"- de T{k}: “{x['span']}” — rótulo textual: {rotulo_textual(x['span'])}")
    cega += ["", "| Pergunta | Sua resposta |", "|---|---|", "| 1. Correção semântica |  |", "| 2. Sustentação pelos trechos |  |", "| 3. Decisão desejável |  |", "| 4. Entidade/localização: sustentada ou só eco da pergunta? |  |", "| 5. Confiança / comentário |  |", ""]
cega += ["---", "Avaliador(a): ____________  Data: ________  (preencher; não preencher por inferência da equipe)"]
(AQUI / "PACOTE_REVISAO_HUMANA_4D4.md").write_text("\n".join(cega), encoding="utf-8")

ref = ["# Pacote de revisão — versão de REFERÊNCIA (com julgamentos originais) — NÃO entregar ao avaliador antes da avaliação", "",
       "Mapeamento entre a versão cega e os casos da Fase 4D.3, com o julgamento original (de quem escreveu os casos; **não** independente) e a justificativa original, copiados sem alteração.", ""]
for nome, cid in ORDEM:
    c = CASOS[cid]
    j = c["julgamento_referencia"]
    z = j["justificativa"]
    ref += [f"## {nome} = {cid}", f"- Descrição original do caso: {c['descricao']}", f"- Pergunta: {c['pergunta']}", f"- Resposta: {c['resposta']}", f"- Entidade / atributo: {c['entidade']} / {c['atributo']}",
            f"- Rótulos (anotação original): {'; '.join(c['rotulo_do_trecho'])}", f"- Relação alegada entre entidade e atributo: {c['relacao_entidade_atributo']}",
            f"- **Julgamento atual:** classe `{j['classe']}`, semântica `{j['correcao_semantica']}`, sustentação `{j['sustentacao_pelos_trechos']}`, decisão ideal `{j['decisao_ideal_do_pipeline']}`, confiança `{j['confianca']}`",
            f"- Justificativa original: afirmação: {z['afirmacao_avaliada']} | trecho: {z['trecho_que_sustenta_ou_contradiz']} | entidade associada: {z['entidade_associada_ao_atributo']} | só da pergunta: {z['informacao_so_da_pergunta']} | por quê: {z['por_que']}",
            f"- Papel na análise (tags originais): {', '.join(c['papel_na_analise'])}", ""]
(AQUI / "PACOTE_REVISAO_HUMANA_4D4_REFERENCIA.md").write_text("\n".join(ref), encoding="utf-8")
print({n: hashlib.sha256((AQUI / n).read_bytes()).hexdigest()[:16] for n in ("PACOTE_REVISAO_HUMANA_4D4.md", "PACOTE_REVISAO_HUMANA_4D4_REFERENCIA.md")})
