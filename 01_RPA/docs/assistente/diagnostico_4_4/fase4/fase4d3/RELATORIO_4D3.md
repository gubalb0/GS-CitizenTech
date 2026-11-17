# Fase 4D.3 — Conjunto diagnóstico de conflitos de evidência (candidata `fail-closed-4.4.4d1-cand`, não validada)

Conjunto **sintético** de 30 casos para examinar a premissa "termo da pergunta não precisa de sustentação" e o mecanismo B. **Não é um benchmark representativo do corpus real e não permite generalizar.** Nenhum código de produção, prompt, parâmetro, retriever, índice, corpus, JSONL, manifesto, snapshot ou relatório anterior foi alterado; nenhuma geração, LM Studio ou API; flag `priorizar_atributo` desligada. Convenção: **[F]** fato observado, **[E]** resultado executado, **[J]** julgamento de referência (meu), **[H]** hipótese.

## 1. Integridade dos artefatos
- `verificar_hashes.py` → **TODOS CONFEREM** (antes e depois). Candidata investigada = `VERSAO_POLITICA = "fail-closed-4.4.4d1-cand"` [F].
- Hashes (16 car.): `geracao.py` c857b99f49947e1a (= snapshot `geracao_44_fase4d1.py`), `evidencias.py` 12118192b9529075 (= `evidencias_44_fase4d1.py`), `catalogo.py` 8e44143ba1d092f5; `FASE4D1_NORMALIZACAO_ROTULOS.md` 388ea4f094bae2d0; `FASE4D2_DIAGNOSTICO_MECANISMO_B.md` 343d067c2ad1dc00; JSONL da validação cbb8482916d55050 e c198f0893d40121f; manifesto 43fb09685404714c. Todos idênticos aos de antes da fase.
- Tudo o que esta fase criou está em `docs/assistente/diagnostico_4_4/fase4/fase4d3/`. Nada foi integrado à suíte oficial.

## 2. Quantidade e distribuição dos casos
30 casos: família A (entidade herdada) 7, B (conflito de rótulos) 7, C (entidade–atributo) 7, D (afirmações novas) 9. Dois "mundos": regulação (vocabulário de val-087, para comparabilidade) e contratos (para não depender de uma palavra específica).
- Classe de referência [J]: correta 13, incorreta 8, insuficiente_evidencia 4, correta_parcial 3, ambiguo 2. A classe `nao_verificavel` foi usada **só** nos campos de correção semântica/sustentação; nenhum caso recebeu essa classe como rótulo principal.
- Decisão ideal [J]: entregar 15, bloquear 12, indeterminado 3. Confiança: alta 19, média-alta 4, média 4, baixa 3.

## 3. Critérios de construção e rotulagem
- Rotulagem escrita **antes** de importar o pipeline (`construir_casos_4d3.py` não o importa); hash congelado em `CONGELAMENTO_ROTULAGEM_4D3.json`, verificado por asserção no executor. Três campos separados: correção semântica (verdade no mundo fictício dos trechos), sustentação pelos trechos e decisão ideal; a aceitação real pelo pipeline é um quarto dado, medido depois.
- **Desvio de procedimento (registrado):** na 1ª execução (v1), os 17 casos do mundo contratos foram todos para `ambigua` por falta de discriminador na pergunta (heurística sem catálogo exige número/ano/mês), o que mascarava os mecanismos estudados. Corrigi **só o texto da pergunta** (acrescentei "nº 12/2025", "nº 13/2025"), sem tocar em julgamentos, e reexecutei. Verifiquei por diff que, entre v1 e v2, **somente o campo `pergunta` mudou** (17 casos). Os artefatos v1 estão preservados em `primeira_execucao_descartada_v1/`. Como vi os resultados de v1 antes de v2, o congelamento é anterior a *cada* execução, mas não anterior a *toda* observação.
- Autor dos casos = autor dos rótulos; sem revisão independente. Os rótulos de A02, A06, A07 e B04 (os que discriminam as variantes) têm confiança média/baixa e são contestáveis (§8).

## 4. Resultados da implementação atual [E]
Tabela por caso (decisão do pipeline em replay offline com resposta candidata fixa; colunas das variantes na §5):

| caso | classe ref. | ideal | baseline | B1 | B2 | C simpl. | D | causa do bloqueio na baseline |
|---|---|---|---|---|---|---|---|---|
| A01 | insuficiente_evidencia | bloquear | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | evidencia_nao_corresponde_a_pergunta:nome=gama |
| A02 | insuficiente_evidencia | bloquear | parcial | bloqueia | bloqueia | bloqueia | bloqueia |  |
| A03 | correta | entregar | parcial | entrega | entrega | entrega | bloqueia |  |
| A04 | correta | entregar | parcial | entrega | entrega | entrega | bloqueia |  |
| A05 | correta_parcial | entregar | parcial | entrega | entrega | entrega | bloqueia |  |
| A06 | ambiguo | indeterminado | parcial | bloqueia | bloqueia | bloqueia | bloqueia |  |
| A07 | correta | entregar | respondida | bloqueia | bloqueia | entrega | entrega |  |
| B01 | incorreta | bloquear | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | rotulo_incompativel_com_atributo |
| B02 | correta | entregar | parcial | entrega | entrega | entrega | bloqueia |  |
| B03 | correta | entregar | parcial | entrega | entrega | entrega | bloqueia |  |
| B04 | correta | entregar | parcial | entrega | entrega | bloqueia | bloqueia |  |
| B05 | correta | entregar | parcial | entrega | entrega | entrega | bloqueia |  |
| B06 | incorreta | bloquear | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | rotulo_incompativel_com_atributo |
| B07 | incorreta | bloquear | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | rotulo_incompativel_com_atributo |
| C01 | correta | entregar | respondida | entrega | entrega | entrega | entrega |  |
| C02 | incorreta | bloquear | ambigua | bloqueia | bloqueia | bloqueia | bloqueia | — |
| C03 | correta | entregar | ambigua | bloqueia | bloqueia | bloqueia | bloqueia | — |
| C04 | incorreta | bloquear | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | evidencia_nao_corresponde_a_pergunta:nome=alfa,numero=12/2025 |
| C05 | correta | entregar | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | evidencias_de_publicacoes_distintas_combinadas |
| C06 | correta | entregar | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | evidencias_de_publicacoes_distintas_combinadas |
| C07 | ambiguo | indeterminado | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | evidencia_nao_corresponde_a_pergunta:numero=12/2025 |
| D01 | correta_parcial | indeterminado | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | rotulo_incompativel_com_atributo |
| D02 | incorreta | bloquear | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | afirmacoes_nao_sustentadas_pela_evidencia:planaltina |
| D03 | insuficiente_evidencia | bloquear | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | evidencia_nao_corresponde_a_pergunta:nome=planaltina |
| D04 | incorreta | bloquear | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | afirmacoes_nao_sustentadas_pela_evidencia:obras |
| D05 | incorreta | bloquear | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | valores_nao_sustentados:90.000,00 |
| D06 | correta | entregar | respondida | entrega | entrega | entrega | entrega |  |
| D07 | correta_parcial | entregar | respondida | entrega | entrega | entrega | entrega |  |
| D08 | correta | entregar | respondida | entrega | entrega | entrega | entrega |  |
| D09 | insuficiente_evidencia | bloquear | insuficiente | bloqueia | bloqueia | bloqueia | bloqueia | rotulo_incompativel_com_atributo |

Detalhe de termos, termos descartados por origem na pergunta, citações (rótulo, estado, causas, necessária, bloqueia, termos exclusivos) e causa de bloqueio: `RESULTADOS_BASELINE_4D3.csv`.
- **Falsa liberação (1): A02** — reproduz o padrão de val-087-A-r1: "Gama" é descartado como termo da pergunta (`da_pergunta`), os termos de uso (nortear, gerências, implementar, normas, protocolos) só dependem do inciso IX; o trecho de membros fica `conflito`, `necessaria=False`, `bloqueia=False`. Entregue como `parcial`.
- **Falsos bloqueios (3): C03, C05, C06** — **não** causados por B nem pelas isenções da pergunta: C03 vira `ambigua` (duas candidatas divergentes de publicações diferentes citadas); C05/C06 caem em `evidencias_de_publicacoes_distintas_combinadas`. São efeitos de outras regras (ambiguidade/combinação de publicações), fora do escopo desta fase.
- **Bloqueios corretos:** A01, D03 (entidade só na pergunta, ausente em todo trecho citado → `evidencia_nao_corresponde_a_pergunta`, alinhamento); D02, D04, D05 (`afirmacoes_nao_sustentadas`/`valores_nao_sustentados`); B01, B06, B07 (`rotulo_incompativel_com_atributo`, mecanismo B); C04 (alinhamento); C02 (`ambigua`, não por B).
- **Observação importante [F]:** a isenção de termos da pergunta em `alinhamento`/`afirmacoes_nao_sustentadas` **não produziu liberação indevida quando a entidade falta em todos os trechos citados** (A01, D03, C04 bloqueados); o problema surge quando a entidade existe em **algum** trecho citado de outro atributo (A02).

## 5. Resultados por variante [E]
Variantes só em memória/pós-hoc (B1/B2: monkeypatch de `EV.termos_de_uso` restaurado, com asserção; C simplificada e D: filtros sobre a baseline que só podem bloquear). **C simplificada** = cada nome saliente da pergunta repetido na resposta precisa constar no chunk de ao menos uma citação cujo estado não seja `conflito`. **D** = exige ao menos uma citação com estado `compativel`. Essas definições são minhas e arbitrárias.

| Variante | Falsas liberações | Falsos bloqueios (ideal=entregar) | Corretas preservadas (de 13) | Corretas parciais bloqueadas | Mudou vs baseline |
|---|---|---|---|---|---|
| Baseline | A02 | C03, C05, C06 | 10 | 0 | — |
| B1 | — | A07, C03, C05, C06 | 9 | 0 | A02 (corrigido), A06, A07 |
| B2 | — | A07, C03, C05, C06 | 9 | 0 | idem B1 |
| C simplificada | — | B04, C03, C05, C06 | 9 | 0 | A02 (corrigido), A06, B04 |
| D | — | A03, A04, A05, B02, B03, B04, B05, C03, C05, C06 | 4 | 1 (A05) | 9 casos |

- B1 e B2 são **indistinguíveis neste conjunto**; nenhum caso separa nome saliente de qualquer palavra da pergunta.
- Os 3 falsos bloqueios C03/C05/C06 são herdados por todas as variantes (não dependem delas).

## 6. Falsos bloqueios e falsas liberações (resumo)
- **B1/B2 corrigem A02** (padrão r1) [E], **mas bloqueiam A07** (legítimo, [J] media_alta) e **A06** (ambíguo). Confirma, em duas famílias de texto, que B1 não separa "eco da pergunta" de "localização nova" [F/E].
- **C simplificada corrige A02 e preserva A07**, porque o nome "Planaltina" consta no mesmo chunk da citação `Objeto` (compatível); em compensação **bloqueia B04**, em que a única citação tem rótulo conflitante mas competência explícita no próprio trecho. Isso mostra a diferença entre conflito de rótulo e evidência positiva [E].
- **D** corrige A02, mas bloqueia 7 casos corretos adicionais; o custo aqui decorre em parte de o parser **não reconhecer** rótulo em "IV - Compete à CRSSU…" (sem dois-pontos → `desconhecido`), logo "compatível" quase nunca aparece no mundo regulação. Coerente com a Fase 4D.2 (28 de 30 respostas entregues sem rótulo compatível nos dados reais) [F/E]; inviável como regra isolada.

## 7. Casos inconclusivos
A06 (baseline entrega; B1/B2/C bloqueiam), C07 (bloqueado por `alinhamento`, número 12/2025 ausente do aditivo — **não** isola a ambiguidade que se queria testar) e D01 (bloqueado por `rotulo_incompativel_com_atributo` porque "Contratada:" é rótulo PARTE ≠ OBJETO). Não há gabarito defensável para o "melhor" resultado; não foram contados como erro. Quatro casos de baixa confiança/ambíguos concentram a divergência entre variantes.

## 8. Limitações da simulação offline
- Conjunto pequeno (30), sintético, escrito e rotulado pela mesma pessoa; não representa frequência nem diversidade do corpus (que, na 4D.2, tinha 1 caso de conflito de rótulo em 150).
- A resposta do modelo é fixa e escrita por mim; não se avalia como o Qwen produziria r1-like. Contexto injetado diretamente (sem retrieval/montagem real) e **sem catálogo** (usa a heurística de identificabilidade sem catálogo; a regra de janela do catálogo, P1, não foi exercida) — **não executável offline**: comportamento real do modelo, catálogo, retrieval.
- A07 e B04 dependem de julgamento: se A07 fosse tratado como ambíguo, o falso bloqueio de B1 desapareceria; se B04 fosse tratado como bloqueável, o de C simplificada também. A conclusão "B1 bloqueia legítimo" repousa nesses rótulos [H sobre sensibilidade].
- C simplificada e D são interpretações minhas; outras formulações dariam outros números. B1/B2 foram aplicados em `termos_de_uso` apenas, não em `alinhamento`/`afirmacoes_nao_sustentadas`, portanto não testam a premissa compartilhada nesses dois pontos.
- Cobertura de rótulos limitada: "IV - Compete…" sem dois-pontos não é reconhecido; "Contratada:" (PARTE) gera conflito com OBJETO em respostas vazias.
- Casos C03/C05/C06/C02/C07 são decididos por mecanismos externos ao estudado; isolam mal o objeto da fase.

## 9. Recomendação técnica
1. **Não implementar B1/B2 como regra única**: trocam 1 falsa liberação (A02) por ao menos 1 falso bloqueio de caso legítimo (A07) e passam a bloquear o ambíguo A06 [E]; a evidência é de 1 padrão real (val-087) + sintéticos.
2. **C simplificada é a direção mais seletiva observada** (corrige A02, preserva A07), mas precisa distinguir conflito de rótulo com evidência positiva explícita (B04) [H: tratar `estado=conflito` sem causa — cue explícito — como não conflitante; **não testado**, para não ajustar a 30 casos].
3. **Descartar D como regra isolada**; no máximo, sinal auxiliar.
4. Antes de qualquer mudança: segundo avaliador independente para A02, A06, A07, B04; mais casos derivados de publicações reais (hoje só val-087); decidir a política sobre ecos da pergunta (A06) — se "bloquear ou entregar sem a localização".
5. Os falsos bloqueios C03/C05/C06 sugerem revisar separadamente as regras de ambiguidade/combinação de publicações (relacionadas a P1/P5).

## 10. Mudanças que ainda dependem de autorização
Qualquer alteração em `termos_de_uso`, `_relacoes_44`, `alinhamento` ou `afirmacoes_nao_sustentadas`; integração dos casos à suíte oficial; segunda rotulagem humana; novos casos com publicações reais; revisão das regras de ambiguidade/combinação; qualquer geração com modelo. Parei aqui.

## Arquivos
`CASOS_DIAGNOSTICOS_4D3.json`, `ROTULAGEM_4D3.md`, `RESULTADOS_BASELINE_4D3.csv`, `COMPARACAO_VARIANTES_4D3.csv`, `RELATORIO_4D3.md`; apoio: `construir_casos_4d3.py`, `executar_4d3.py`, `CONGELAMENTO_ROTULAGEM_4D3.json`, `resultados_4d3_detalhe.json`, `primeira_execucao_descartada_v1/`.
