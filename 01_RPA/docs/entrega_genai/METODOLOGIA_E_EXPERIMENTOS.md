# Metodologia e experimentos

Todos os números abaixo foram copiados dos relatórios originais indicados (nenhum foi recalculado nesta atividade). **Todos os experimentos usaram o conjunto de validação (150 perguntas) como conjunto de desenvolvimento**; o conjunto de teste de 350 perguntas nunca foi baixado nem usado. Portanto **nada aqui é validação independente** (ver §9).

## 1. Corpus (`docs/assistente/01_corpus_dodf.md`, `02_...`)
- **Fonte:** `gvic-unb/dodf-saude-qa` (Hugging Face), **CC BY 4.0** (atribuição exigida), revisão `ef52e3fe…`, acesso em 2026-11-13. Citação do cartão: Freire, A. S. M. et al., *Evaluating Location-Aware RAG Approaches for Question Answering over Public Health–Related Content in Brazilian Official Gazettes* (BRACIS 2026, *to appear*).
- **Tamanho:** corpus 1.381 documentos (4.008.970 tokens de superfície; mediana 295; máx. 458.610); QA de validação 150 perguntas (41 `MULTI`), teste 350 (não usado). Integridade conferida por SHA-256 contra o `oid` do HF (`MANIFESTO.json`); originais marcados como somente leitura.
- **Natureza:** quase todo administrativo (Seção III: extratos, reconhecimentos de dívida, contratos, credenciamentos, avisos). **Não é informação de serviço ao cidadão.** As perguntas e as respostas de referência foram **geradas por LLM** (Claude Haiku 4.5, segundo o cartão), com filtros automáticos; não são perguntas reais de cidadãos e os gabaritos têm erros (ex.: val-024).
- **Perguntas não unívocas:** 6 (val-005/018, val-023/120, val-122/146) têm perguntas idênticas ou quase idênticas com documentos diferentes; 16 de 36 perguntas MULTI têm associação frouxa com o rótulo MULTI (4.3).

## 2. Pré-processamento
- **Deduplicação:** 76 duplicatas exatas → 1.305 documentos canônicos; qualquer id do grupo vale como fonte correta.
- **Associação QA→publicação** (150/150, por igualdade exata do `texto_publicacao`; 252 blocos); isto valida o encaixe do dataset, não a qualidade das perguntas nem das respostas.
- **Normalização de busca:** minúsculas, sem acentos, tokens `\w+`, sem stopwords nem stemmer.

## 3. Estratégia de chunking (Etapa 2)
Comparação de `tamanho` e `estrutura` em 300/500/700 tokens, com e sem sobreposição (seis configurações × duas). A estrutura eleva as fronteiras limpas de ≈10% para ≈96–98% com ~3× mais tempo de processamento; a integridade de evidência depende do **tamanho** (83–84% a 300; 87% a 500; 88% a 700 — proxy sobre 94 perguntas com valores numéricos), não da estratégia. **Escolha final:** `est300o30` (Etapa 3), por MRR melhor, mais "ao menos uma publicação correta" no mesmo orçamento de contexto (0,613 vs 0,520 a ≈2,3K tokens; 0,640 vs 0,580 a ≈3K, BM25), e só 8,7% dos chunks acima do limite de 512 tokens do e5 (contra 78,3%).

## 4. Recuperação: BM25, embeddings e RRF (Etapa 3)
- **BM25** Okapi próprio (`k1=1,5`, `b=0,75`, definidos antes de avaliar). **Embeddings:** `intfloat/multilingual-e5-small` (MIT; 384-d; CPU; ≈1,4 GB de RAM; indexação ≈ 31–34 min por configuração). **RRF:** `Σ 1/(60+posição)`, 100 candidatos por recuperador.
- **Resultados (150 validação; `est300o30`)**

| Modo | R@1 | R@5 | R@10 | MRR | Ao menos 1 correta @10 |
|---|---|---|---|---|---|
| BM25 | 0,246 | 0,491 | 0,578 | 0,434 | 0,687 |
| Vetorial | 0,185 | 0,371 | 0,450 | 0,316 | 0,533 |
| Híbrido (RRF k=60) | 0,219 | 0,458 | 0,559 | 0,396 | 0,653 |
(`est500o50`: BM25 0,593 / 0,419 / 0,700; híbrido 0,529 / 0,336 / 0,620 para R@10 / MRR / Hit@10.)
- **Leitura:** o vetorial é fraco neste corpus; o híbrido de pesos iguais **não superou o BM25** em MRR e Recall. Em variantes **exploratórias** (lidas depois de ver os resultados, nas mesmas 150 perguntas) `rrf_k=20` elevou o Recall@10 do híbrido a 0,599 (est300o30), acima do BM25 (0,578), mas com MRR inferior (0,417 vs 0,434); nenhum padrão foi alterado com base nelas. **Decisão do projeto:** BM25 em `est300o30` (melhor MRR, ≈1,7 ms por consulta, dispensa os embeddings na consulta). Diferenças de ~0,03–0,04 com n=150 ficam dentro do ruído.
- **Lacuna:** ≈31% das perguntas não têm nenhuma publicação correta nos 10 primeiros documentos com BM25; só um modelo de embeddings foi avaliado; reranking, expansão de consulta e filtros por metadados não foram avaliados.

## 5. Modelo local e parâmetros de geração
Qwen3-8B Q4_K_M (GGUF, bartowski) em LM Studio 0.4.28 / llama.cpp Vulkan 2.73.0, RX 6750 XT; contexto 8192; `/no_think` (0 tokens de raciocínio em todas as chamadas medidas); JSON Schema estrito; temperatura 0,3; `top_p` 0,8; sem *seed*; `max_tokens_saida` 1100 (700 truncava o JSON em 7/150); orçamento de prompt ≈ 3.000 tokens do Qwen3 (≈ 1,76 × tokens de superfície, razão medida 1,6 + margem); top-5 chunks (limite 6). Sem *seed*, repetições do mesmo caso podem divergir (observado nas 21 gerações da validação seletiva).

## 6. Metodologia de avaliação
1. **Isolada (Etapa 4):** 39 casos × 2 repetições com contextos reais montados pelo autor (categorias: evidência suficiente, parcial, sem evidência, conflito, ambígua, fora do escopo, injeção de instrução, etc.). Critério corrigido após ver a v1; os 3 pares não unívocos orientaram a v2 (melhora nesses pares é otimista).
2. **End-to-end diagnóstica:** retriever congelado → gerador, nas 150 perguntas, em **rodadas únicas identificadas** por `run_id` (`20261113-173721` = 4.1; `20261114-014826` = 4.2; `20261114-130608` = 4.3), preservadas em `data_assistente/derivados/`. Grupos por haver ou não publicação correta **entre os chunks efetivamente enviados** (A/B; reconstruídos com `grupos.py`).
3. **Auditorias por modelo de linguagem:** auditoria da 4.3 (150 perguntas), diagnóstico 4.4 e auditoria das 21 gerações (4C), todas feitas pelo **agente de desenvolvimento ou por instância do mesmo modelo, sem revisão humana**.
4. **Replays offline** (sem modelo): as 150 saídas brutas gravadas são reprocessadas pelo verificador de cada versão para medir o efeito de mudanças sem nova geração.

## 7. Evolução das fases de confiabilidade
| Fase | O que mudou | Resultado documentado |
|---|---|---|
| Etapa 4 | Gerador, prompt v2, verificador, injeção/abstenção | Isolada: 69/74 sem falsas confianças; e2e: 19 de 72 perguntas sem fonte correta receberam resposta confiante de outras publicações → **não aprovado** |
| 4.1 | Política fail-closed (`parcial`, prompt v3), 163 testes | 0 respostas "completas" sem fonte correta; 19 respostas de outra instância ainda entregues como `parcial` |
| 4.2 | Abstenção por **identificabilidade** da publicação (`catalogo.py`), 174 testes | Completas 2→10, parciais 41→24, ambíguas 58→67, abstenção 71,3%→77,3%; grupo B 19→13 |
| 4.3 | Relevância por janela (1.500 caracteres, ≥ 3 termos) para MULTI no singular | Abstenção 79,3%; nenhuma resposta completa de outra publicação |
| Auditoria 4.3 (modelo) | Julgamento de 150 respostas | Ver `RESULTADOS_E_LIMITACOES.md`; recomendação: não integrar ao Zelo |
| 4.4 Fase 1 | Erros de atribuição da auditoria (val-050/062/097), medição de grupos A/B, `verificar_hashes.py` | Errata; `grupos.py` (9 testes) |
| 4.4 Fase 2 | Verificador: casamento de citação por tokens, atribuição, alinhamento por publicação | 26 testes; replay sem diferença antes de editar |
| 4.4 Fase 3 | M1–M5 (ausência/remissão, rótulo×atributo, item de lista, período, localidade) | `fail-closed-4.4.3`; suíte do Gen AI: 262 testes |
| 4A | Registro auditável das relações; mecanismo B (conflito de rótulo só bloqueia se necessário), A_DEST, A_LOC | `fail-closed-4.4.4a`; 23 testes novos |
| 4B | Seleção de contexto S1 (forte → conservadora), flag `priorizar_atributo` **desligada por padrão** | `fail-closed-4.4.4b-cand`; replay: só val-074 e val-087 mudam de contexto |
| Validação seletiva 4B | **21 gerações** reais (val-074 e val-087, A = sem S1, B = com S1, + 3 controles) com avaliação cega **pelo próprio agente** | val-074 A 0/3 × B 3/3 corretas; val-087 A 0/3 × B 3/3 (saída bruta); controles estáveis; pipeline ainda marca `ambigua` em val-074-B |
| 4C | Reauditoria das 21 (mesmo agente, cegamento procedimental) | Discordou de 2 classificações; recomendou revisão humana; achados P1–P5 |
| 4D.1 | Normalização de índice de lista (`4 - Titular:`) no reconhecimento de rótulo | `fail-closed-4.4.4d1-cand` (**atual**); 337 testes; replay: 0 diferenças nos 150 e nos 21 |
| 4D.2–4D.7 | **Diagnósticos** (não integrados): por que val-087-A-r1 escapa; conjunto sintético; casos reais; protótipo de vínculo por frase; políticas de veto V0–V3; correção do protótipo | Ver §8 e `ESTADO_FINAL.md` |

## 8. Fases 4D.2–4D.7 (diagnóstico; nada foi integrado)
- **4D.2:** val-087-A-r1 escapa porque o termo "Gama" vem da **pergunta** e é excluído de `termos_de_uso`, de modo que o trecho conflitante não é "necessário". A mesma premissa ("o que vem da pergunta não precisa de apoio") aparece também em `alinhamento` e `afirmacoes_nao_sustentadas`.
- **4D.3 (30 casos sintéticos, rotulagem do próprio autor):** variantes B1/B2 (tratar nomes da pergunta como termos de uso) corrigem o padrão de val-087-A-r1 mas bloqueiam um caso legítimo; a "C simplificada" corrigia o mesmo caso no sintético. **Esses resultados sintéticos não são representativos do corpus.**
- **4D.4 (casos reais):** a C simplificada em nível de chunk **não** corrige val-087-A-r1 (o chunk neutro cita "Gama" em outro inciso) e removeria 2 de 30 entregas reais; B1/B2 corrigem val-087-A-r1 e não mudam nenhum dos 150 outros. Preparado, **sem realizar**, um pacote de revisão humana cego.
- **4D.5 (protótipo de vínculo por frase, 26 sintéticos + 5 reais):** vínculo por frase/adjacência não introduz falsos vínculos que o nível de chunk/publicação introduz, mas perde relações só documentais; o protótipo foi ajustado depois de ver resultados (v1→v3, preservadas).
- **4D.6 (políticas de veto V0–V3):** veto por contradição explícita preserva mais respostas legítimas que o veto por ausência, porém deixa passar falsos vínculos sem contradição e depende de um inventário manual de entidades; **não há evidência suficiente para integração**. Errata: a explicação anterior do "400 × R$ 20.400,00" estava errada; a causa era uma regex defeituosa.
- **4D.7:** corrigida **somente** a linha da regex de abreviaturas **em uma cópia isolada do protótipo diagnóstico** (`prototipo_vinculo_4d7.py`); um alvo em 34 mudou (val-083 VITAMINA D); sem regressões. **A candidata e o código de produção não foram alterados.**

## 9. Desenvolvimento × validação independente
- **Desenvolvimento (usado para decidir):** as 150 perguntas de validação (chunking, retriever, prompt, políticas, mecanismos, replays); os 39 casos isolados; os 30 + 26 casos sintéticos das fases 4D; as 21 gerações de val-074/val-087 (esses dois casos foram escolhidos **por terem sido diagnosticados**).
- **Validação independente: não existe.** Não houve conjunto externo, nem o teste de 350, nem **segundo avaliador humano** (a revisão humana das 21 gerações e dos rótulos das 4D foi preparada e permanece pendente). Os rótulos sintéticos foram escritos por quem construiu os casos e os protótipos.

## 10. Limitações metodológicas
Rótulos e gabaritos de origem LLM; 150 casos reusados em todas as decisões (risco de ajuste ao conjunto); auditorias feitas por modelo de linguagem; contextos controlados construídos pelo autor na avaliação isolada; amostras pequenas (21 gerações; 5 casos reais nas 4D.5–4D.7); parte dos mecanismos foi desenhada olhando casos específicos (val-083, val-087, val-130, val-149); temperatura 0,3 sem *seed*; latências medidas em máquina em uso; a ausência de comparação com outros modelos de embeddings e outros LLMs.
