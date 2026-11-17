# Etapa 4.3 — Perguntas MULTI formuladas no singular

**Status do Gen AI: experimental / em andamento.** Não aprovado para integração ao Zelo (falta revisão humana independente e validação de integração). Nenhum julgamento humano foi preenchido.

Rodada única: `20261114-130608` (150 perguntas de validação, 150/150, 0 erros técnicos, JSON válido 150/150, política `fail-closed-4.3`). Mesmo modelo (Qwen3-8B Q4_K_M), LM Studio 0.4.28 / llama.cpp Vulkan 2.73.0, `parallel` 1, ctx 8192, T 0,3, prompt v3, mesmo retriever (est300o30, BM25, top-5) e orçamento de contexto da 4.2. Rodadas `20261113-173721` (4.1) e `20261114-014826` (4.2) preservadas. Retriever, índices, datasets, teste de 350 e arquivos congelados do RPA não foram tocados (hashes conferidos). Snapshots pré-execução em `data_assistente/versoes/*_43_pre_execucao.py`.

## 1. O que mudou

1. **Relevância por janela com cobertura parcial** (`Catalogo.relevantes`): conta, em **todo o corpus**, publicações independentes cuja melhor janela de 1.500 caracteres cobre ao menos tantos termos distintos da pergunta quanto a publicação citada (mínimo 3 termos). Diferença para a 4.2: a 4.2 exigia cobrir *todos* os termos que a citada cobre; agora basta equivalência de cobertura. Uma única publicação recuperada não é tomada como prova de que só existe uma relevante.
2. **Duplicatas, republicações e atos-modelo** (mesmo texto de evidência ou mesmos valores específicos) são "concordantes" e não contam como publicações independentes.
3. **Singular com publicação relevante concorrente** → `ambigua`, nenhum valor entregue, lista das publicações e pedido de data/número/documento.
4. **Lista com cobertura incompleta** → `parcial`, com aviso explícito do que foi analisado e do que não pode ser confirmado: "o corpus contém ao menos N outra(s) publicação(ões) potencialmente relevante(s) que não foram analisadas…" (`telemetria.cobertura_lista`). Sem catálogo, mantém o aviso genérico anterior.
5. **Perguntas gerais** com uma publicação relevante e sem concorrente continuam `respondida`; compostas continuam avaliadas por parte.
6. Parâmetros fixados antes da avaliação: janela 1.500, mínimo 3 termos, piso 1,0 (nenhum limiar foi ajustado após ver resultados).

Testes: **183 passam na rodada** (185 após os testes de regressão da §2) (174 + 9 novos em `test_multi_43.py`: val-024-like com concorrente parcial, uma única relevante, singular com valores diferentes, equivalentes, plural incompleto, pergunta geral, duplicatas/republicações, composta, mínimo de termos).

## 2. O caso val-024 (resultado negativo, a ler com atenção)

O val-024 **continua `respondida`** na 4.3. A investigação no texto do corpus mostra por quê:

- O dataset marca a pergunta como MULTI com 5 publicações esperadas (docs 616, 621, 684, 688, 718). Apenas a **718** (Primeiro Termo Aditivo ao Contrato nº 051462/2024, supressão de 5 equipamentos de Raio X no HRC) trata da modificação contratual de radiologia. As outras 4 só mencionam "Ceilândia": dispensas de licitação de itens não relacionados (616, 688), diretório de agências do trabalhador (621) e pauta do TCDF com uma administração regional (684).
- Melhor janela de termos: a 718 cobre 5 dos 6 termos; nenhuma outra publicação do corpus passa de 3. Não há segunda publicação relevante.
- A resposta dada coincide com a referência do dataset (supressão de 5 equipamentos de Raio X).

Conclusão: as "5 publicações esperadas" do val-024 vêm de uma associação QA→documento frouxa, não de múltiplas publicações com informações distintas. O critério de conclusão ("não pode sair completa quando a cobertura for insuficiente **e houver indícios de múltiplas publicações independentes**") não se aplica a este caso com base no texto do corpus, e eu não conseguiria bloqueá-lo sem uma regra que também bloquearia respostas corretas (val-006 e val-041 têm a mesma forma: singular, só nome de local como âncora, sem número). Registro isso como discordância com a premissa da etapa, para decisão sua. Em produção o sistema também não sabe se a pergunta é MULTI; uma regra "singular sem discriminador léxico → sempre ambígua" seria possível, mas custaria as respostas corretas citadas.

O mecanismo, porém, funciona quando o concorrente existe: val-082 (resposta de outra publicação, antes completa) e val-054 passaram a `ambigua`; o teste sintético val-024-like (`test_multi_no_singular_com_outra_publicacao_relevante_nao_sai_completa`) comprova o bloqueio.

### Decisão (registrada após a apresentação dos resultados)
A decisão do responsável é **manter o val-024 como `respondida`** e **não** adotar regra universal "sem número/data/ano → `ambigua`". A política consolidada considera a intenção da pergunta e as evidências reais do corpus:

| Situação | Status |
|---|---|
| Singular, uma única publicação claramente relevante, evidência suficiente | `respondida` |
| Singular, publicações concorrentes com informações divergentes | `ambigua` |
| Lista/múltiplas publicações, recuperação incompleta | `parcial`, com aviso de cobertura |
| Ausência de identificadores, isoladamente | **não** provoca abstenção |

Nenhuma alteração de código foi feita nesta decisão: a política `fail-closed-4.3` já se comporta assim (a ausência de identificadores só importa quando existe concorrente real no corpus). Não houve nova rodada de 150.

### MULTI declarado pelo dataset × multiplicidade real de evidências
O rótulo MULTI vem da associação QA→publicação da Etapa 2 (a resposta de referência foi gerada a partir de vários blocos/fontes do dataset) e **não mede** quantas publicações do corpus realmente respondem à pergunta. No val-024, 5 publicações estão associadas, mas só 1 (718) é efetivamente relevante.

Verificação nos demais casos (`python -m citizentech.assistente.auditoria_multi`, somente leitura, sem modelo; saída em `auditoria_multi_dataset.csv`). Critério fixado antes de ler os resultados: uma publicação associada é efetivamente relevante se a melhor janela de 1.500 caracteres cobre ≥ max(3, 0,75 × a melhor cobertura entre as associadas) termos distintos da pergunta. Das 41 perguntas MULTI, 36 têm ≥ 2 publicações associadas distintas após deduplicação (as demais colapsam em 1):

| Classificação | N | Perguntas |
|---|---:|---|
| Multiplicidade real (≥ 2 relevantes) | 15 | val-013, 035, 039, 044, 055, 069, 070, 074, 094, 100, 108, 112, 114, 130, 149 |
| Associação frouxa (1 relevante), como o val-024 | 16 | val-017, 020, 021, 022, 024, 032, 052, 053, 060, 079, 087, 095, 116, 119, 121, 139 |
| Indeterminado (nenhuma associada cobre ≥ 3 termos) | 5 | val-007, 048, 058, 059, 099 |

Leitura: cerca de metade das perguntas MULTI do dataset (16 de 36) tem associação frouxa, e em 5 a cobertura lexical é baixa demais para afirmar algo. Isso é uma **limitação do benchmark**: métricas "MULTI" (recall de todas as publicações esperadas, completude) tendem a penalizar o sistema por não recuperar publicações que não são relevantes de fato. A medida é lexical (mesma limitação da relevância por janela) e **não** substitui revisão humana; os dados originais não foram alterados. Recomendação: tratar a lista de 16 como candidatos a revisão humana de gabarito, não corrigir o dataset automaticamente.

Teste de regressão: `test_regressao_val_024_continua_respondida_com_o_corpus_real` (usa o corpus real; pula se indisponível) garante `respondida` com 0 publicações concorrentes relevantes, e `test_auditoria_do_rotulo_multi_classifica_val_024_como_associacao_frouxa` fixa a classificação. Suíte total: **185 testes passam**.

## 3. Comparação 4.1 × 4.2 × 4.3 (mesmo script, mesmos campos)

| Métrica | 4.1 | 4.2 | 4.3 |
|---|---:|---:|---:|
| respondida / parcial | 2 / 41 | 10 / 24 | 8 / 23 |
| ambigua / insuficiente / fora | 58 / 35 / 14 | 67 / 35 / 14 | 71 / 33 / 15 |
| Abstenção total | 107 (71,3%) | 116 (77,3%) | 119 (79,3%) |
| Respostas dadas | 43 | 34 | 31 |
| Dadas sem a fonte correta citada | 19 | 14 | 11 |
| Completas indevidas (grupo B `respondida`) | 0 | 1 (val-082) | **0** |
| MULTI `respondida` | 0 | 1 (val-024) | 1 (val-024) |
| Completas com só fontes corretas | 2 | 7 | 7 |
| Latência mediana / p95 | 19,7 / 29,5 s | 21,0 / 31,8 s | 17,1 / 26,3 s |

(Obs.: a contagem de "dadas sem fonte correta" da 4.2 neste script é 14; o relatório 4.2 citava 13 por critério ligeiramente diferente. Aqui as três colunas usam o mesmo critério.)

- **Efeito atribuível à regra nova (confirmado por replay determinístico das saídas brutas da 4.2):** val-082 (resposta de outra publicação) e val-054 (resposta correta) `respondida → ambigua`. Resultado líquido: uma resposta errada bloqueada e uma correta perdida.
- **Respostas corretas preservadas:** as 7 completas com só fontes corretas da 4.2 (val-000, 002, 003, 006, 024, 049, 090) continuam as mesmas na 4.3; val-041 (completa correta) também foi mantida e val-054 foi perdida. Dos 16 casos: grupo A, 6 de 9 preservados como `respondida`, 3 em abstenção (val-009, 054, 128); grupo B, 7 de 7 bloqueados (val-082 agora incluído).
- **Mudanças não atribuíveis à regra:** 12 perguntas trocaram entre `insuficiente`↔`parcial`/`ambigua`/`fora_do_escopo` (ex.: val-026, 044, 047, 108, 112, 007, 020, 021, 119, 121, 139, 149). A regra nova só age sobre `respondida`/`parcial` singulares e listas via aviso; essas trocas vêm da variação do modelo (T 0,3), como já ocorrera da 4.1 para a 4.2. A diferença de abstenção de 77,3% para 79,3% **não deve ser creditada integralmente à política**.
- **Parciais com cobertura incompleta:** 23 parciais; 17 trazem contagem de outras publicações relevantes no corpus (mediana 10), 6 usam o aviso genérico (publicação citada sem termos suficientes para avaliar, ou nenhuma outra relevante encontrada).
- **Perguntas não unívocas (6):** todas `ambigua`. **MULTI:** 14 parciais, 14 insuficientes, 7 ambíguas, 5 fora do escopo, 1 respondida (val-024); em 4 de 41 MULTI o contexto enviado tinha todas as publicações esperadas.
- **Regressões em perguntas gerais:** nenhuma resposta correta de pergunta geral foi bloqueada além de val-054; val-000, 002, 003, 006, 041, 049, 090 continuam respondidas.

## 4. Limitações e riscos

- val-024 não é detectado (ver §2). O gabarito MULTI do dataset é pouco confiável como "verdade de múltiplas publicações".
- Relevância é lexical (radicais, nomes, números) em janela de 1.500 caracteres: sinônimos e siglas podem gerar falsos concorrentes (val-054: 22 publicações do mesmo hospital passaram o piso; a resposta correta foi sacrificada) ou falsos "únicos". O contador "ao menos N publicações" nas listas é uma estimativa, não uma contagem verificada.
- A política exige acesso ao texto completo do corpus em produção (catálogo em memória, ~1.305 documentos canônicos).
- Memória: `llama-server` até 7,8 GB de RSS e RAM livre mínima do sistema de **45 MB** durante a rodada (a 4.2 chegou a ~196 MB). Sem erros técnicos, mas o ambiente está no limite; manter outros programas fechados.
- Avaliação diagnóstica: as 150 perguntas já foram usadas no desenvolvimento do retriever; sem juiz humano independente; correção das respostas por leitura minha e pelo gabarito gerado por LLM.
- Não foi usado o teste de 350; não houve integração com o RPA.

## 5. Arquivos

- Código: `catalogo.py` (`melhor_janela`, `relevantes`), `geracao.py` (`_identificabilidade`, cobertura de lista), `evidencias.py` (`aviso_cobertura`, `compor`), `auditoria.py` (nova coluna de indicadores), `avaliacao_e2e.py` (meta 4.3).
- Dados: `data_assistente/derivados/geracao_e2e_41_20261114-130608.jsonl` + `.meta.json` (prefixo `41` mantido por compatibilidade).
- Auditoria do rótulo MULTI: `citizentech/assistente/auditoria_multi.py` → `docs/assistente/auditoria_multi_dataset.csv`.
- Auditoria: `docs/assistente/auditoria_e2e_20261114-130608.csv` e `.md` (campos de julgamento humano em branco; revisar todas as 31 respostas dadas e as 71 ambíguas).

## 6. Pendências

1. ~~Decisão sobre val-024~~: resolvida (manter `respondida`, §2).
2. Revisão humana do gabarito dos 16 casos de associação frouxa e dos 5 indeterminados antes de novas medições MULTI.
3. Auditoria humana independente e coleta de perguntas reais de cidadãos (gov.br) continuam pendentes.
