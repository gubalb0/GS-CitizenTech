# Etapa 3 — Retriever (BM25 + vetorial + RRF)

Reprodução: `python -m citizentech.assistente.construir_indice est500o50 est300o30` (≈30 min cada, CPU) ·
`python -m citizentech.assistente.avaliar_retriever est500o50 est300o30` · `... --orcamento` · `... --sensibilidade-bm25` ·
testes: `python -m pytest citizentech/assistente/tests -q` (84 passaram) · resultados brutos em `data_assistente/derivados/retriever_*.json`.
Avaliado **somente** nas 150 perguntas de validação. O conjunto de teste (350) não foi baixado nem usado. Nenhum LLM foi chamado.

## 1. Arquitetura e decisões técnicas (registradas antes da avaliação)

```
corpus (1.381 docs) → dedup (1.305 canônicos; 76 cópias exatas mapeadas) → chunking (est500o50 | est300o30)
   ├─ BM25 (scipy.sparse; texto = cabeçalho contextual + chunk)        ─┐
   └─ e5-small: janelas ≤512 tokens → vetores 384-d; chunk = máx(janelas) ─┴→ RRF (k=60, 100 candidatos) → top-k chunks
```
Módulos novos em `citizentech/assistente/`: `texto_busca.py`, `dedup.py`, `bm25.py`, `codificador.py`, `retriever.py`, `metricas.py`, `construir_indice.py`, `avaliar_retriever.py`. A interface `Indice.construir(corpus, ConfigChunk, codificador)` aceita qualquer configuração de chunking; `salvar/carregar` persistem chunks, vetores e manifesto (o BM25 é reconstruído de forma determinística).

### Modelo de embeddings
- **`intfloat/multilingual-e5-small`**, MIT, revisão `614241f622f53c4eeff9890bdc4f31cfecc418b3`, baixado em 2026-11-13 para `D:\hf_cache` (~493 MB: `model.safetensors` 470.641.600 bytes + tokenizador). SHA-256 do `model.safetensors` conferido com o `oid` do HF: `1a55775f…c98477`.
- 12 camadas, 384 dimensões, vocabulário 250.037, entrada máxima 512 tokens, prefixos `query: ` / `passage: `. PyTorch instalado é CPU (`2.12.0+cpu`); a RX 6750 XT não é usada para embeddings.
- Por que este: multilíngue, cabe na CPU e na RAM do hardware validado, sem API externa, licença permissiva. `multilingual-e5-base` e `bge-m3` **não foram avaliados** (custo de CPU/RAM e prazo): é uma limitação, não um resultado.
- Requisitos medidos: processo com o modelo ≈1,4 GB de RAM; throughput de indexação ≈10 janelas/s; codificar uma consulta ≈28 ms (mediana; p95 ≈31 ms).

### Tokenizador e limite — achado que mudou o desenho
O tokenizador do e5 gera ≈1,47× (est500o50) e ≈1,54× (est300o30) os tokens de superfície do chunking. Em 600 chunks sorteados: `est500o50` mediana 630 tokens do e5, p90 825, máx. 929, **78,3% acima de 512**; `est300o30` mediana 380, p90 503, 8,7% acima de 512. Para não truncar em silêncio, chunks maiores que o limite viram **janelas** de ≤512 tokens (sobreposição de 64, cabeçalho repetido) e o score do chunk é o **máximo** entre as janelas. Resultado: 17.613 janelas para 9.913 chunks (est500o50) e 17.566 para 16.199 (est300o30).

### Normalização, parâmetros
- BM25: minúsculas, sem acentos (NFKD), tokens `\w+`, números separados; sem stopwords nem stemmer. Okapi `k1=1,5`, `b=0,75` (definidos antes de avaliar). Implementação própria em `scipy.sparse` (nenhuma dependência nova).
- Vetorial: produto interno de vetores normalizados, busca exata.
- RRF: `Σ 1/(60 + posição)`, 100 candidatos por recuperador, desempate pelo menor índice de chunk (ordem do corpus).

### Duplicatas e documentos gigantes
- 76 documentos redundantes (mesma chave estrutural e texto idêntico); 1.305 documentos canônicos são indexados; `ids_equivalentes` fica em cada chunk e resultado; na avaliação qualquer id do grupo é fonte válida.
- Nenhum documento foi cortado. Gigante = mais de 20 mil tokens de superfície (definição desta avaliação): **40 documentos**, que concentram 57,2% (est500o50) e 58,2% (est300o30) dos chunks. O controle de dominância é feito no resultado (`max_por_doc`).

## 2. Configurações comparadas e método de avaliação
- Chunking: `est500o50` (9.913 chunks) e `est300o30` (16.199 chunks), ambos por estrutura.
- Relevância: associação QA→publicação comprovada (`associacao.py`), no nível de **publicação canônica**. Cada documento aparece no ranking na posição do seu melhor chunk (100 candidatos). Perguntas MULTI têm de 1 a 5 publicações esperadas (grupos únicos); Recall@k = fração das publicações esperadas encontradas nas k primeiras. "Tem ao menos uma correta" = Hit@10. MULTI "cobertura total" = todas as publicações esperadas nos 10 primeiros documentos.
- Variantes avaliadas: BM25, vetorial, híbrido (RRF), vetorial/híbrido só com a 1ª janela (simula truncamento), `max_por_doc=3`, `rrf_k` 20/100, sem documentos gigantes (filtro no resultado), sem deduplicação.
- **Exploratório:** as variantes (rrf_k, truncamento, k1/b/radical) foram lidas nas 150 perguntas de validação. Nenhum parâmetro padrão foi alterado com base nelas.

## 3. Métricas (150 perguntas de validação; 109 não-MULTI + 41 MULTI)

### Principais (padrão: `k1=1,5`, `b=0,75`, RRF k=60)
| Config | Modo | R@1 | R@3 | R@5 | R@10 | MRR | Ao menos 1 correta @10 | MULTI cobertura total @10 |
|---|---|---|---|---|---|---|---|---|
| est500o50 | BM25 | 0,219 | 0,416 | 0,499 | 0,593 | 0,419 | 0,700 | 0,146 |
| est500o50 | vetorial | 0,100 | 0,226 | 0,262 | 0,366 | 0,231 | 0,440 | 0,098 |
| est500o50 | híbrido | 0,170 | 0,322 | 0,412 | 0,529 | 0,336 | 0,620 | 0,171 |
| est300o30 | BM25 | 0,246 | 0,429 | 0,491 | 0,578 | 0,434 | 0,687 | 0,122 |
| est300o30 | vetorial | 0,185 | 0,292 | 0,371 | 0,450 | 0,316 | 0,533 | 0,146 |
| est300o30 | híbrido | 0,219 | 0,397 | 0,458 | 0,559 | 0,396 | 0,653 | 0,146 |
Com n=150, uma diferença de ~0,03–0,04 equivale a poucas perguntas e fica dentro do ruído; leio apenas as diferenças grandes.

### Por subconjunto (Recall@10 / MRR / Hit@10)
| | Não-MULTI (109) | MULTI (41) | Sem os 6 não unívocos (144) | Só os 6 não unívocos |
|---|---|---|---|---|
| est500o50 BM25 | 0,670 / 0,382 / 0,670 | 0,390 / 0,518 / 0,781 | 0,583 / 0,425 / 0,694 | 0,833 / 0,277 / 0,833 |
| est500o50 vetorial | 0,413 / 0,211 / 0,413 | 0,242 / 0,283 / 0,512 | 0,354 / 0,220 / 0,431 | 0,667 / 0,482 / 0,667 |
| est500o50 híbrido | 0,596 / 0,315 / 0,596 | 0,350 / 0,394 / 0,683 | 0,523 / 0,333 / 0,618 | 0,667 / 0,413 / 0,667 |
| est300o30 BM25 | 0,651 / 0,406 / 0,651 | 0,381 / 0,508 / 0,781 | 0,567 / 0,436 / 0,681 | 0,833 / 0,388 / 0,833 |
| est300o30 vetorial | 0,505 / 0,296 / 0,505 | 0,305 / 0,369 / 0,610 | 0,441 / 0,309 / 0,528 | 0,667 / 0,481 / 0,667 |
| est300o30 híbrido | 0,633 / 0,381 / 0,633 | 0,361 / 0,435 / 0,707 | 0,554 / 0,395 / 0,653 | 0,667 / 0,413 / 0,667 |
(Nos não-MULTI, Recall@10 = Hit@10 por definição.)

### Variantes (Recall@10 / MRR / Hit@10)
| Variante | est500o50 | est300o30 |
|---|---|---|
| vetorial, só 1ª janela (≈truncamento) | 0,421 / 0,245 / 0,487 | 0,450 / 0,316 / 0,533 (igual: 1 janela na maioria) |
| híbrido, só 1ª janela | 0,557 / 0,372 / 0,653 | 0,559 / 0,397 / 0,653 |
| híbrido `max_por_doc=3` | 0,529 / 0,336 / 0,620 | 0,559 / 0,396 / 0,653 |
| híbrido `rrf_k=20` | 0,562 / 0,356 / 0,667 | 0,599 / 0,417 / 0,707 |
| híbrido `rrf_k=100` | 0,521 / 0,336 / 0,607 | 0,550 / 0,390 / 0,647 |
| híbrido sem documentos gigantes (filtro) | 0,536 / 0,331 / 0,633 | 0,557 / 0,390 / 0,647 |
| híbrido sem deduplicação | 0,545 / 0,332 / 0,640 | 0,562 / 0,396 / 0,653 |

### Sensibilidade do BM25 (somente lexical; 4 valores de `k1` × 3 de `b` × radical leve sim/não)
- est500o50: MRR de 0,363 a 0,447 (padrão 0,419; melhor `radical=1, k1=1,5, b=0,9`: 0,447). est300o30: MRR de 0,385 a 0,443 (padrão 0,434; melhor `k1=1,2, b=0,9`: 0,443). Radical leve eleva Hit@10 de 0,70→0,73 (est500o50) e 0,69→0,72 (est300o30), mas a MRR varia nos dois sentidos. As diferenças entre as melhores combinações são pequenas para n=150; os padrões foram mantidos.

### Latência, memória e tamanho do índice
| | est500o50 | est300o30 |
|---|---|---|
| Chunking / BM25 / tokenização em janelas / embeddings | 11,3 s / 4,6 s / 19,4 s / 1.801,8 s | 11,8 s / 4,7 s / 19,1 s / 1.983,8 s |
| **Indexação total** | **1.837,6 s (≈31 min)** | **2.021,7 s (≈34 min)** |
| Tamanho em disco (chunks.jsonl + vetores) | 74,4 MB | 79,2 MB |
| RAM extra ao carregar o índice | ≈160 MB | ≈81 MB |
| Consulta BM25 (mediana / p95) | 1,2 / 1,6 ms | 1,7 / 2,8 ms |
| Consulta vetorial (mediana / p95), sem codificar a pergunta | 7,3 / 7,8 ms | 7,2 / 7,7 ms |
| Consulta híbrida (mediana / p95), sem codificar a pergunta | 8,8 / 9,4 ms | 8,6 / 9,4 ms |
Soma-se, nas buscas vetoriais/híbridas, a codificação da pergunta pelo e5 em CPU: ≈28 ms (mediana). Latência total de uma consulta híbrida ≈ 37 ms. O processo com o modelo ocupa ≈1,4 GB de RAM. Medições em uma máquina em uso normal (uma sessão).

### Diversidade e dominância no top-10 de chunks (média das 150 consultas)
| | Docs distintos | Slots de docs gigantes | Slots de docs irrelevantes |
|---|---|---|---|
| est500o50 BM25 / vetorial / híbrido | 8,8 / 8,6 / 8,8 | 10,4% / 14,6% / 8,1% | 89% / 94% / 91% |
| est300o30 BM25 / vetorial / híbrido | 8,7 / 8,5 / 8,7 | 12,5% / 8,3% / 5,4% | 90% / 92% / 90% |
Os gigantes têm ≈57% dos chunks do índice mas ocupam só 5–15% do top-10: não dominam o resultado. Filtrá-los não melhora a recuperação (tabela de variantes) e **piora** a cobertura total de MULTI (0,171→0,146 no est500o50), pois publicações esperadas de MULTI incluem documentos grandes.

### Duplicatas
Sem deduplicar, cópias de uma publicação já presente aparecem no top-10 de chunks em 66 das 150 consultas (86 documentos-cópia no total) no est500o50 e em 59 (80) no est300o30. O efeito sobre Recall/MRR não é mensurável com n=150 (diferenças ≤0,02, sinais mistos). O benefício é de espaço no top-k e ausência de repetição; o custo é nulo (ids preservados).

### Evidência no mesmo conjunto de chunks (94 perguntas não-MULTI com valores verificáveis)
Fração em que **todos** os valores-chave da resposta (R$, CNPJ, processo, número/ano) aparecem no texto concatenado dos primeiros chunks:
| | 5 chunks | 10 chunks |
|---|---|---|
| est500o50 BM25 / vetorial / híbrido | 59,6% / 31,9% / 51,1% | 68,1% / 40,4% / 62,8% |
| est300o30 BM25 / vetorial / híbrido | 55,3% / 40,4% / 52,1% | 61,7% / 48,9% / 61,7% |

### Mesmo orçamento de contexto (chunks, não documentos)
O gerador aceita ≈3K tokens do Qwen3. Convertendo o tamanho dos chunks recuperados com a razão 1,6 medida na Etapa 2:
| Orçamento ≈ | Config / modo / k | Hit (≥1 pub. correta) | Recall das publicações | Evidência completa |
|---|---|---|---|---|
| 2,2–2,3 K tokens | est500o50 BM25, k=4 | 0,520 | 0,440 | 54,3% |
| | est300o30 BM25, k=6 | **0,613** | 0,508 | 56,4% |
| | est500o50 híbrido, k=4 | 0,407 | 0,348 | 46,8% |
| | est300o30 híbrido, k=6 | 0,540 | 0,470 | 53,2% |
| 2,9–3,0 K tokens | est500o50 BM25, k=5 | 0,580 | 0,485 | 59,6% |
| | est300o30 BM25, k=8 | 0,640 | 0,536 | 59,6% |
| | est500o50 híbrido, k=5 | 0,453 | 0,396 | 51,1% |
| | est300o30 híbrido, k=8 | 0,600 | 0,512 | 56,4% |

## 4. Análise qualitativa
**Exemplos reais (est300o30).**
- *Sucesso:* val-000 "Qual empresa foi inabilitada no credenciamento … cirurgia oftalmológica …?" — BM25 e híbrido trazem em 1º lugar `dodf-1647:est300o30:0000` (Extrato, Edital nº 03/2025, 2025-11-10, 192 tokens, score BM25 40,9 contra 33,6 do 2º). O 2º e o 3º do BM25 são outros extratos de inabilitação (Hospital Santa Marta), irrelevantes mas do mesmo tipo.
- *MULTI parcial:* val-013 "aquisições … Hospital Regional de Taguatinga … Sudoeste" — esperadas 4 publicações distintas; BM25 acha uma (`dodf-242`) na posição 3; o híbrido a rebaixa para a posição 15 porque o vetorial prefere trechos de aquisições de outras unidades.
- *Falha:* val-014 "Até quando será possível enviar propostas para o chamamento no Hospital da Criança de Brasília José Alencar?" — esperado: Chamamento nº 246/2025 (2025-10-20). Os três primeiros do BM25 e do híbrido são outros chamamentos/avisos do mesmo hospital. Nenhum recuperador traz o esperado nos 100 candidatos.

**Perguntas sem nenhuma publicação correta nos 100 candidatos (híbrido):** 8 no est500o50 (val-014, 025, 034, 064, 104, 107, 145, 148) e 11 no est300o30 (acrescenta val-042, 048, 061, 093; val-048 é MULTI). O padrão dominante é **pergunta subespecificada** ("o hospital", "a dívida reconhecida pelo INAS", "o chamamento no HCB") diante de dezenas de publicações quase idênticas do mesmo tipo; o retriever acha o tipo certo, não a instância. Não é possível separar aqui o que é falha do retriever do que é ambiguidade da pergunta.

**Correta só em posições baixas:** com o híbrido, 85 perguntas (est500o50) e 70 (est300o30) têm a publicação correta apenas após a posição 3 (por exemplo val-010: posição 39 no est500o50; val-043: 55–69).

**Dominância:** 9 perguntas (est500o50) e 8 (est300o30) têm ≥5 dos 10 primeiros chunks do mesmo documento. Não classifiquei a relevância desses documentos um a um.

**BM25 × vetorial × híbrido (est500o50; publicação correta entre os 10 primeiros documentos):** BM25 105/150, vetorial 66, híbrido 93. 49 perguntas só o BM25 acerta, 10 só o vetorial, 1 só o híbrido. O híbrido perde 23 perguntas que BM25 ou vetorial achariam sozinhos. Primeiro lugar: BM25 43, vetorial 19, híbrido 32. No est300o30: 103 / 80 / 98; só BM25 36, só vetorial 13, só híbrido 4; primeiro lugar 45 / 33 / 40. O BM25 vence onde a pergunta traz nomes e números exatos (por exemplo "Chamamento nº 270/2025"); o vetorial (e5-small, CPU) acerta mais perguntas de redação livre, mas pior com textos administrativos cheios de siglas e valores. Com um recuperador bem mais fraco, o RRF de pesos iguais arrasta o BM25 para baixo.

**Efeito das janelas:** para o est500o50 a variante "só 1ª janela" saiu **melhor** que o máximo entre janelas (vetorial R@10 0,421 vs 0,366; híbrido 0,557 vs 0,529). Não investiguei a causa; uma hipótese não testada é que janelas finais de tabelas ou listas geram similaridades altas espúrias. Isso contraria a decisão de design (não truncar) e fica registrado como achado.

**MULTI:** só 7 das 41 perguntas (est500o50) e 6 (est300o30) têm todas as publicações esperadas nos 10 primeiros documentos. Recall@10 médio ≈0,35–0,36, e cai com o número de publicações esperadas (1: 1,0 / 2: 0,5 / 3: 0,11 / 4: 0,17 / 5: 0,29 no est500o50; poucas perguntas por faixa). Os exemplos inspecionados (val-007 "serviços de saúde … Riacho Fundo II") indicam que a pergunta agregada tem relação fraca com o texto das publicações-gabarito; a qualidade dessas perguntas LLM-geradas limita o que qualquer retriever consegue.

**Valor encontrado mas evidência incompleta:** 4 perguntas (est500o50) e 9 (est300o30) têm a publicação correta nos 5 primeiros documentos mas não reúnem todos os valores-chave nos 5 primeiros chunks; são quase todas perguntas de lista ("Quais equipamentos foram adquiridos …").

**Não unívocos (híbrido, est500o50):** val-005/val-018 (posições 2 e 1), val-023/val-120 (18 e 2), val-122/val-146 (3 e 11). Em cada par o 1º resultado de uma pergunta é justamente a publicação esperada da outra (ex.: docs 704, 408 e 822). Para perguntas **idênticas** (023/120 e 122/146) é impossível acertar as duas no 1º lugar: o teto de R@1 do par é 50%. Por isso reportei os números com e sem esses 6 casos (BM25 R@10: 0,583 sem eles e 0,833 neles; não são representativos).

## 5. Qual configuração
Não escolhi pela média de uma métrica. Pontos considerados:
- **Qualidade:** est300o30 supera est500o50 em MRR (BM25 0,434 vs 0,419; híbrido 0,396 vs 0,336) e em R@1; R@10 é equivalente ou ligeiramente melhor no est500o50 só para o BM25 (0,593 vs 0,578), dentro do ruído.
- **Mesmo orçamento de contexto:** est300o30 leva vantagem clara em "ao menos uma publicação correta" (0,613 contra 0,520 a ≈2,3K tokens com BM25; 0,640 contra 0,580 a ≈3K), com evidência completa equivalente.
- **MULTI:** diferença de 1 pergunta na cobertura total (0,171 vs 0,146 no híbrido) — não conclusiva.
- **Custo:** latência de consulta e tempo de indexação equivalentes; est300o30 gera mais chunks (16,2 mil contra 9,9 mil) e menos RAM por janelas; tamanho do índice similar (≈75–80 MB).
- **Compatibilidade com o limite do e5:** est300o30 tem só 8,7% dos chunks acima de 512 tokens (contra 78,3%), evitando o problema das janelas.

## 6. Falhas e limitações
- O recuperador vetorial é fraco neste corpus (Hit@10 0,44–0,53) e o híbrido de pesos iguais **não supera o BM25** em MRR e Recall; o ganho do híbrido aparece em parte de MULTI e, para `rrf_k=20`, em Recall@10 (explorado depois de ver os resultados, nas 150 perguntas).
- 30% (est500o50) e 31% (est300o30) das perguntas não têm nenhuma publicação correta entre os 10 primeiros documentos com o BM25 (Hit@10 0,70 e 0,69).
- Parte relevante dos erros decorre de perguntas subespecificadas (inclusive 6 não unívocas) e de MULTI de gabarito frágil. O teto real do retriever sobre esse conjunto não é conhecido.
- Só um modelo de embeddings foi avaliado; e5-small em CPU. Não avaliei reranking, expansão de consulta, filtros por metadados (os campos `localidades`/`tipo_unidade` são esparsos) nem pesos diferentes no RRF.
- O número de documentos gigantes (40) usa um limite de 20 mil tokens definido por mim.
- A evidência é verificada só por valores numéricos (94 perguntas), não por sentido.
- Latências medidas em uma sessão, com o computador em uso. A tabela de diversidade e os testes não classificam a relevância de cada documento dominante.
- Os dados são do Diário Oficial do DF (atos administrativos), não de informação ao cidadão sobre as oito categorias do CitizenTech; o corpus complementar (gov.br/SUS) continua não coletado.

## 7. Testes
84 testes em `citizentech/assistente/tests/` (51 das etapas anteriores + 33 novos, com codificador falso, sem rede e sem baixar o modelo): normalização; BM25 (ordem, termo desconhecido, consulta vazia, parâmetros inválidos, desempate determinístico); deduplicação (ids preservados, mesmo texto com chave diferente não é duplicata, sem duplicata no top-k, variante sem dedup); busca lexical, vetorial e híbrida (origem de cada resultado, fórmula do RRF, ordem exata com listas conhecidas, determinismo); consultas vazias/sem resultado; `max_por_doc`; documento gigante indexado até o fim; metadados e rastreabilidade (offsets reconstroem o texto); troca de configuração; várias janelas por chunk; salvar/carregar com resultados idênticos; checkpoint de embeddings retomado; índice inválido/incompleto/de outro modelo; parâmetros e entradas inválidas; corpus vazio; métricas com MULTI e ids equivalentes. Os testes **não** exercitam o e5 real (a avaliação o faz).

## 8. Recomendação para a próxima etapa (gerador)
1. Usar **`est300o30` como configuração principal** e manter `est500o50` apenas como referência.
2. Como recuperador do gerador, **BM25 como base**, com o vetorial como apoio opcional. O híbrido só deve entrar se um teste com dados novos (nenhum foi preservado além do conjunto de teste) confirmar `rrf_k=20` ou outro peso; hoje o BM25 sozinho tem a melhor MRR, o menor custo (≈1,7 ms) e dispensa o modelo de embeddings (1,4 GB de RAM) na consulta.
3. Contexto do gerador: **k=5 a 6 chunks** do est300o30 (≈1,9–2,3 K tokens do Qwen3), mantendo folga para instruções e saída dentro do limite de ~3K.
4. Como ≈31% das perguntas não têm a publicação correta nos 10 primeiros documentos e muitas são subespecificadas, a **abstenção e o pedido de esclarecimento** passam a ser o ponto central do gerador; sugiro avaliá-lo separadamente nas perguntas com recuperação correta e nas sem.
5. Antes de qualquer melhoria do retriever (modelo de embeddings maior, RRF ponderado, filtros por entidade), decidir se vale o custo (cada reindexação ≈30 min) frente ao objetivo de demonstrar o RAG; não implementei nenhuma delas.
6. MULTI continua sendo um caso à parte (cobertura total ≈15%): tratá-lo como limitação documentada ou desenhar consultas em várias passagens.
