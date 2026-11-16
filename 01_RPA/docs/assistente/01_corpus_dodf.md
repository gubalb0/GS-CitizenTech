# Etapa 1 — Corpus: amostra do DODF Public Health QA

## Origem e licença
- Dataset: `gvic-unb/dodf-saude-qa` — https://huggingface.co/datasets/gvic-unb/dodf-saude-qa
- Licença declarada no cartão: **CC BY 4.0** (exige atribuição). Idioma: pt-BR. Acesso público, sem gate.
- Citação indicada pelo cartão: Freire, A. S. M. et al. "Evaluating Location-Aware RAG Approaches for Question Answering over Public Health–Related Content in Brazilian Official Gazettes." BRACIS 2026 (to appear, Springer).
- Data de acesso: **2026-11-13**, via `datasets-server.huggingface.co/rows` (somente amostra).
- Tamanho total (metadados do servidor): corpus 1.381 linhas / 7,5 MB parquet; QA 500 linhas (350 teste + 150 validação) / 6,4 MB.

## Amostra baixada (local: `data_assistente/dodf_amostra/`)
- `corpus_amostra_100.jsonl`: as 100 primeiras linhas do corpus (**NÃO aleatórias**: são de 20 edições de janeiro/2025).
- `qa_validacao_amostra_30.jsonl`: as 30 primeiras linhas da validação. Teste (350) não foi tocado.
- `schema_e_acesso.json`: esquema e metadados de acesso.

## Estrutura
- Corpus (13 campos): `id`, `edicao`, `data_edicao`, `referencia`, `secao`, `tipo_documento`, `numero_documento`, `texto_completo`, `data`, `topicos`, `localidades`, `tipo_unidade`, `programas`.
- QA (6 campos): `pergunta`, `resposta`, `secao`, `fonte` (data da edição ou `MULTI`), `tipo_documento`, `texto_publicacao` (cabeçalho "Edição N — data — Seção — título" + texto).
- **O QA não traz o `id` do documento do corpus.** A ligação pergunta→documento precisa ser reconstruída casando `texto_publicacao` com `texto_completo`.

## Achados na amostra (medidos)
- Corpus (100 docs): texto de 594 a 134.796 caracteres; mediana 1.183, média 6.837, p90 14.605. Nenhum texto vazio. Seção III em 89 e Seção I em 11. 13 tipos de documento (mais comuns: Extrato 32, Ineditorial 20, Reconhecimento de dívida 20, Autorização 10).
- Metadados enriquecidos são esparsos nesta amostra: `topicos` vazio em 84/100, `localidades` vazio em 55/100, `programas` vazio em 97/100; `tipo_unidade` = "hospital" em 84/100. Não servem como filtro confiável.
- QA (30 perguntas): pergunta mediana 97 caracteres; resposta mediana 357. 25/30 perguntas citam um hospital, unidade ou região. 7/30 são `MULTI` (agregam até 5 publicações; `texto_publicacao` de 24 mil a 185 mil caracteres, muito acima do limite de ~3K tokens). Nos demais 23, `texto_publicacao` tem mediana de ~1.400 caracteres (~420 tokens, estimativa chars/3,3).
- Respondibilidade (leitura manual de 6 itens: QA 0, 2, 5, 18, 23 e 6 parcialmente): a resposta está sustentada pelo `texto_publicacao` em todos. Uma heurística automática de "tokens-chave da resposta presentes na fonte" deu média 0,76, mas **subestima** porque as respostas escrevem valores por extenso, datas em outro formato e nomes sem acento; não usar essa heurística como métrica.
- **Perguntas não unívocas:** QA 5 e QA 18 são praticamente a mesma pergunta ("valor autorizado para pagamento ao Hospital das Clínicas e Pronto Socorro de Fraturas") com respostas e documentos diferentes (R$ 69.281,56 em 24/02/2025 vs R$ 169.905,44 em 26/05/2025). Isso limita Recall@k/MRR por documento exato, e é um bom caso de ambiguidade para testes.
- Publicações agrupadas ("Ineditorial") podem trazer vários avisos; no QA 2 o cabeçalho cita o Chamamento 259/2025, mas a resposta é do 270/2025, que também está no texto. O chunking deve respeitar esse agrupamento.

## Natureza do corpus (limitação de escopo)
Quase todo o conteúdo é administrativo (Seção III: extratos, reconhecimentos de dívida, contratos, credenciamentos, avisos de chamamento). **Não é informação de serviço ao cidadão** (horários, vacinas, como agendar). O benchmark mede RAG sobre documentos oficiais; para as oito categorias do CitizenTech será preciso um corpus complementar (gov.br/SUS), ainda não aprovado (D4). As perguntas foram geradas por LLM (Claude Haiku 4.5, segundo o cartão), com filtros automáticos; não são perguntas reais de cidadãos.

## NÃO verificado (falha de infraestrutura, não conclusão)
Tentei casar cada pergunta de validação com seu documento no corpus consultando só as edições citadas pelo endpoint `/filter`. O serviço do Hugging Face devolveu erros 500/502 e timeouts; o resultado "1/30 casados" **é inválido e não deve ser citado**. Casamento local só foi possível para as 3 perguntas cujas edições estão na amostra: QA 6 → 1 documento; QA 19 → 2 candidatos; QA 25 → 2 candidatos (documentos de texto idêntico ou quase). Por isso a taxa de casamento (necessária para medir Recall@k e MRR) segue **desconhecida**.

## Pendência para a decisão
O corpus completo tem 7,5 MB (mais 2,2 MB de QA de validação, 1,6 MB). Para validar o casamento QA→documento e prosseguir para chunking e retriever é preciso baixá-lo. Aguardando aprovação.
