# Auditoria independente de qualidade — Gen AI CitizenTech 4.3

Rodada auditada: `geracao_e2e_41_20261114-130608` (política `fail-closed-4.3`, validação, 150 perguntas).
Auditor: modelo de linguagem (Claude) atuando como revisor, **não** como desenvolvedor, sem usar o status do sistema como referência. **Não é revisão humana**: ela continua pendente e não é substituída por este documento.
Nada do Gen AI, do corpus, dos índices, do retriever, do RPA ou das auditorias anteriores foi alterado; nenhuma geração foi executada. Todos os artefatos novos estão nesta pasta.

## Resumo executivo

**A pergunta: a 4.3 está realmente respondendo corretamente ou apenas apresentando resultados tecnicamente válidos?**

**Resposta curta: as duas coisas, em proporções preocupantes. O que o sistema entrega com status de resposta é, em geral, verdadeiro e citado, mas a verificação técnica passa respostas erradas, e o sistema deixa de responder quase metade das vezes em que o corpus permitia.**

| Indicador (150 perguntas, julgamento do auditor) | Resultado |
|---|---|
| Perguntas avaliadas | **150 de 150** (confiança do auditor: alta 69, média 54, baixa 27; 0 "não avaliável") |
| Respostas dadas (`respondida` + `parcial`) | 31 |
| ... corretas | 7 (22,6%) |
| ... corretas, mas parciais | 16 (51,6%) |
| ... **incorretas** | **8 (25,8%)** |
| ... com afirmação sem evidência | 6 |
| Respostas completas (`respondida`, 8): precisão | 7/8 estrita (87,5%); 8/8 flexível |
| Respostas parciais (`parcial`, 23): corretas ou parciais corretas | 15/23 (65,2%) |
| Abstenções (119): ambíguas de fato | 53 (44,5%) |
| ... abstenções corretas (sem resposta única ou ausente) | 10 (8,4%) |
| ... **abstenções indevidas** (o corpus permitia responder) | **56 (47,1%)**; só alta/média confiança: 37 de 92 (40,2%) |
| Taxa de abstenção adequada (ambígua de fato + abstenção correta) | 63/119 = 52,9% |
| Classificações inadequadas (status do sistema) | 71 de 150 |

Três achados que o relatório automático anterior não mostrava:

1. **As 8 respostas incorretas passam em toda a verificação técnica.** Todas têm citações literais (29 de 31 respostas dadas têm todas as citações literais no documento citado), todas têm fonte e `verificacao.ok`. O erro é de **adequação semântica**: o trecho é real, mas não responde à pergunta (ex.: val-050 pediu o período 31/07–22/08 e dois dos três itens são de fevereiro; val-130 trouxe `Biosphere Health Center`, que é o nome de um edifício na Asa **Norte**; val-136 respondeu "especialidades" com o objeto do edital). Fidelidade literal não implica correção.
2. **Quando a fonte correta não foi enviada (grupo B) o sistema acerta pouco**: 11 respostas dadas, 0 totalmente corretas, 5 corretas-mas-parciais e 6 incorretas. No grupo A: 20 dadas, 7 corretas, 11 parciais corretas, 2 incorretas.
3. **A 4.3 é conservadora demais.** Entre as 119 abstenções, 56 tinham resposta sustentável no corpus (ou ao menos uma resposta parcial suportada), incluindo 10 `fora_do_escopo` para temas que estão no corpus e 18 casos barrados pelo verificador por motivos que, na minha leitura, eram falsos positivos ou geração ruim (ex.: val-097: o valor `5.250.814,42` está no doc 105 e foi reprovado como "não sustentado"; val-106 reprovado por `s/a,daher` com o doc 994 contendo "Hospital Lago Sul S/A (Hospital Daher)").

**Recomendação:** a 4.3 é adequada para continuar como experimento. Não é confiável para uso em produção e **não deve ser integrada ao Zelo**: precisão de resposta dada de 74% (completa e parcial aceitáveis), um quarto das respostas dadas incorretas, e utilidade (respostas efetivas) de 31/150 = 20,7%. Nada aqui altera o status: Gen AI experimental, sem aprovação para integração.

---

## 1. Metodologia

1. **Dados disponíveis (confirmados):** corpus original (parquet, 1.381 publicações), validação (150 perguntas com gabarito gerado por LLM), rodada 4.3 (`.jsonl`, 150 registros, com saída completa, fontes e telemetria), auditorias anteriores, `auditoria_multi_dataset.csv`. Nada ausente para as 150 perguntas.
2. **Candidatos independentes** (`scripts/facts.py`): para cada pergunta busquei, no corpus original, as publicações com maior cobertura de termos da pergunta numa janela de 1.500 caracteres, com código próprio (não usa o ranking do retriever nem o catálogo do gerador). Para cada candidato registrei se contém os valores do gabarito do dataset. O gabarito é **pista**, não verdade (foi gerado por LLM; achei erros nele, ex.: val-024).
3. **Conferência das respostas dadas (31):** leitura do texto do documento citado (`scripts/ctx.py`) para verificar: citação literal, nomes, números, datas, local/período pedidos, afirmações sem evidência. Julgamento manual caso a caso (`scripts/julgamentos_dadas.py`).
4. **Abstenções (119):** para cada uma, determinei no corpus (a) se existe resposta única e estável; (b) se há publicações independentes concorrentes com respostas diferentes (valores, signatários, datas); (c) se a pergunta é aberta/plural (resposta parcial suportada possível). Busca por termos (`scripts/busca.py`) e leitura dos trechos (`scripts/julgamentos_abst_1..5.py`).
5. **21 casos MULTI:** revisão individual dos documentos associados pelo dataset (`scripts/multi_view.py`, `scripts/julgamentos_multi.py`).
6. **Métricas:** `scripts/build.py` → `auditoria_independente_150.csv`, `auditoria_independente_21_multi.csv`, `metricas.json`.

**Vocabulário das classes.** Respostas dadas: *Correta*; *Correta, mas parcial* (o que afirma é suportado, mas a pergunta pedia mais ou a lista é incompleta); *Incorreta* (afirma algo contrário/estranho ao documento, ou não responde ao pedido). Abstenções: *Ambígua de fato* (há publicações independentes concorrentes com respostas diferentes: o sistema acertou em se abster); *Abstenção correta* (não há resposta única ou a informação não existe; pode haver status mal rotulado); *Abstenção indevida* (o corpus permitia responder, ao menos parcialmente; **não significa que o verificador errou**: em vários casos a geração do modelo continha afirmações sem apoio e o bloqueio protegeu o usuário; significa que o usuário ficou sem resposta existente).
Em cada linha há **confiança do auditor** (alta/média/baixa) e a separação entre **fato comprovado** (lido no documento), **interpretação** (julgamento do auditor, assinalado) e **inconclusivo** (confiança baixa).

## 2. Quantidade avaliada

150 de 150 receberam classificação. 27 têm confiança baixa (principalmente abstenções de perguntas abertas e perguntas ambíguas em que não confrontei todos os valores). Nenhuma foi marcada "não avaliável": na pior hipótese são **inconclusivas** e foram mantidas na tabela com essa marca. A coluna de sensibilidade em `metricas.json` recalcula tudo só com confiança alta/média (123 casos).

## 3. Resultados e métricas

Totais gerais: ver tabela do resumo. Detalhe por grupo (fonte: `metricas.json`):

| Grupo | n | Dadas | Corretas | Corretas, mas parciais | Incorretas | Ambíguas de fato | Abst. corretas | Abst. indevidas | Status inadequado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Geral | 150 | 31 | 7 | 16 | 8 | 53 | 10 | 56 | 71 |
| Grupo A (fonte correta enviada) | 76 | 20 | 7 | 11 | 2 | 29 | 0 | 27 | 30 |
| Grupo B (fonte correta não enviada) | 74 | 11 | 0 | 5 | 6 | 24 | 10 | 29 | 41 |
| MULTI declarado pelo dataset | 41 | 15 | 0 | 10 | 5 | 2 | 1 | 23 | 29 |
| Não MULTI | 109 | 16 | 7 | 6 | 3 | 51 | 9 | 33 | 42 |
| Com publicações concorrentes* | 56 | 0 | 0 | 0 | 0 | 53 | 1 | 2 | 2 |

\* Grupo construído a partir do julgamento do auditor ("ambígua de fato") ou de concorrentes apontados pelo sistema; por isso **não é independente** e a taxa de 54/56 (96,4%) não deve ser lida como desempenho: apenas mostra que, quando há concorrência real, o sistema não responde (o que é o desejado). Os grupos A/B vêm da associação do dataset, que também é imperfeita (ver seção 7).

Precisões: respostas completas 7/8 estrita, 8/8 flexível; parciais 15/23 (grupo A 10/12; grupo B 5/11); taxa de abstenção adequada 63/119 (52,9%).

Resultados individuais, com justificativa e referência documental (id do documento no corpus original): `auditoria_independente_150.csv` (e tabela resumida no fim deste relatório).

## 4. Principais erros encontrados

**Respostas dadas incorretas (8, todas `parcial`, 6 do grupo B):**

| Caso | Erro | Evidência documental |
|---|---|---|
| val-007 | Une eleição do Conselho de Saúde com "Hospital da Mulher" como se fosse serviço implementado em Riacho Fundo II | O Hospital da Mulher da Ata (doc 1449) é de São Paulo |
| val-012 | "Equipamentos adquiridos": lista álcool etílico (insumo) e manutenção de macas (serviço) | doc 238 |
| val-039 | Diz que as unidades não têm denominação | doc 303 traz grade com UBS de São Sebastião |
| val-050 | Período 31/07–22/08/2025: heparina e metaraminol de 10/02/2025 | doc 196 (ed.28) |
| val-100 | "Equipamentos adquiridos": serviços de hemodiálise e osmose | doc 440 |
| val-130 | Empresa `Biosphere Health Center` na Asa Sul | doc 6: filial da Asa Norte; Biosphere é o nome do edifício |
| val-136 | Especialidades propostas = objeto do edital | doc 94: especialidades "elencadas na carta proposta" não publicada |
| val-149 | Ações de atenção primária em Ceilândia em 2025 a partir de texto genérico do INAS | docs 1611, 1365, 1052 não descrevem ações em Ceilândia |

**Resposta completa com imprecisão:** val-024 afirma "no Hospital Regional de Ceilândia"; o doc 718 cita HRAN, CRT, CEO UBS 11 Ceilândia, HRS e HRL e **não** o HRC. O fato central (supressão de 5 equipamentos de Raio X Panorâmico, redução de valor) está correto. A premissa vem do gabarito do dataset, que o sistema repetiu.

**Correções menores** (classificadas como corretas-mas-parciais): `Fonte:` citando o rótulo do documento e não o aviso respondido (val-002: aviso 270/2025 dentro do doc rotulado 259/2025); item fora do tema (val-066: fita para impressora como "material médico"); datas de homologação x ratificação (val-143).

## 5. Exemplos de respostas corretas e incorretas

- **Correta:** val-049 (membros efetivos da Comissão de Ética Médica da UPA Riacho Fundo II, doc 698, nomes e CRM conferidos); val-090 (motivo do cancelamento do Chamamento 202/2025: Art. 6º do Decreto 33.390/11, doc 1348); val-041.
- **Correta, mas parcial:** val-118 (PFF2 para o HR de Brazlândia, doc 441, aviso de que há ao menos 2 outras publicações); val-070.
- **Incorreta (literal e fora de contexto):** val-130, val-050, val-136 (seção 4).

## 6. Problemas de recuperação

- 29 das 56 abstenções indevidas são do grupo B: a fonte existe no corpus e não chegou ao modelo (ex.: val-056, medicamentos do HRC em maio/2025, doc 688; val-069, Hospital Regional de Samambaia; val-064, CAPS em Ceilândia, doc 894; val-109, enxoval hospitalar do HRC). No grupo A também há falhas de recuperação parcial (val-094, val-112). Em alguns, o contexto era de outro hospital e o modelo disse "não menciona" (comportamento correto dado o contexto, resultado inútil).
- Perguntas com identificador exato foram resolvidas quando a fonte chegou (val-126, Convênio 026202/2024 existe só no doc 1014).
- Consistência: val-006 (Ceilândia) foi respondida a partir do doc 28, enquanto val-022 (Santa Maria) e val-074 (Samambaia) foram barradas apesar de o mesmo doc listar essas unidades; val-041 respondida e val-029 (pergunta muito semelhante) barrada.

## 7. Problemas de geração e fidelidade

- **Falsos positivos do verificador** (18 abstenções reprovadas, todas julgadas indevidas, ver ressalva da seção 1): valor presente no documento reprovado como não sustentado (val-097), ano da pergunta reprovado (val-031), `nome=coordenacao`/`nome=programa` (val-087, val-141), `trecho_nao_literal` em docs com resposta única (val-032, val-045, val-062, val-126). Em ~8 casos de perguntas abertas o modelo gerou itens sem apoio e o bloqueio protegeu o usuário de afirmações sem evidência (val-033, 044, 058, 063, 083, 088, 089, 108); o prejuízo ali é a ausência de uma resposta parcial suportada.
- **Verificação não detecta adequação semântica:** os 8 erros da seção 4 têm citações literais. Faltam checagens de período, localidade e tipo de item pedido (ex.: val-050, val-130).
- **O sistema às vezes escreve a resposta e rotula como `ambigua`** (val-028, val-134, val-052): o conteúdo útil existe na saída, mas o status contradiz.
- **Gabarito do dataset falha:** val-024 atribui ao HRC um fato que o doc 718 não atribui; val-012 e val-099 têm referências que listam itens de outras publicações; os 5 documentos "esperados" de val-007, val-024 e val-099 incluem publicações sem relação com a pergunta. As métricas do benchmark herdam esses erros.

## 8. Problemas de abstinência e ambiguidade

- **Acertos:** em 53 casos o sistema se absteve corretamente por ambiguidade real (mesmo hospital com valores/signatários diferentes: Hospital das Clínicas e PS de Fraturas, Prontonorte, Maria Auxiliadora, Santa Lúcia, Pacini, Anchieta; chamamentos do HCB sem número).
- **Rótulos errados:** 15 `fora_do_escopo`, dos quais 10 sobre assuntos presentes no corpus (ex.: val-019 análise de água, val-046 Hospital de Sobradinho) e 5 que eram, na verdade, perguntas ambíguas (val-015, 025, 034) ou sem resposta (val-042, 116). `fora_do_escopo` deveria ser reservado a assuntos fora do corpus.
- **Perguntas abertas** (plural escrito no singular ou "quais ... foram adquiridos") foram em geral barradas (das 33 `insuficiente`, 31 foram julgadas indevidas); uma resposta `parcial` com aviso de cobertura seria a saída desejada pela política 4.3, mas o verificador exige que cada afirmação tenha evidência, e a geração costuma errar nisso.
- **Política 4.3 com os casos val-054 e val-082:** val-054 (natureza dos serviços do Prontonorte: "serviços médicos", resposta idêntica nos docs 545/549/550) virou `ambigua` por concorrência que não altera a resposta (julgado indevida, confiança média); val-082 (motivos de cancelamento do HRT) é ambígua de fato (motivos diferentes nos docs 196 e 1352).

### 8.1 Os 21 casos MULTI (revisão independente)

Arquivo: `auditoria_independente_21_multi.csv`.

| Classificação anterior (automática) | Classificação independente | Decisão | Casos |
|---|---|---|---|
| associação frouxa (16) | associação frouxa (1 publicação relevante) | mantida (12) | val-017, 020, 021, 022, 024, 032, 053, 060, 087, 116, 119, 121 |
| associação frouxa | multiplicidade real no corpus | corrigida (4) | val-052, 079, 095, 139 |
| indeterminado (5) | multiplicidade real no corpus | corrigida (4) | val-048, 058, 059, 099 |
| indeterminado | associação frouxa | corrigida (1) | val-007 |

Resultado: **13 associação frouxa e 8 multiplicidade real**. A classificação lexical anterior estava certa em 12 de 21 casos (57%). Nos 9 corrigidos, o critério lexical estava errado em ambos os sentidos: (a) 5 "indeterminados" eram, na verdade, multiplicidade real (val-048, 058, 059, 099) ou associação frouxa (val-007) porque o texto contém os termos de forma diferente da pergunta; (b) 4 "frouxos" têm multiplicidade real no corpus porque o dataset associou o documento errado/incompleto mas existem outras publicações relevantes (val-052 dezenas de dispensas do HRT; val-079 dois credenciamentos em Taguatinga; val-095 duas publicações concordantes sobre a mesma UBS; val-139 rescisão e sanção do mesmo contrato). Para val-024: confirmada associação frouxa (só o doc 718 é relevante), e o doc 718 não nomeia o HRC.

## 9. Limitações desta auditoria

- **O auditor é um modelo de linguagem**, não um revisor humano independente. Pode errar e não substitui a revisão humana pendente.
- **Candidatos por busca léxica**: pode haver publicações relevantes não encontradas; o julgamento "uma única publicação responde" é por evidência encontrada, não prova de ausência.
- **Não li integralmente os documentos longos** (alguns passam de 50 mil caracteres); li os trechos em torno dos termos e comparei valores e signatários em amostras (docs de reconhecimento de dívida). Em abstenções "ambígua de fato" com confiança média/baixa não confrontei todos os valores.
- **Julgamento de perguntas abertas** (plural no singular) tem componente interpretativo: se uma resposta parcial suportada era obrigatória é decisão de política. 27 casos têm confiança baixa.
- **Conjunto de validação (150)** já foi usado para ajustar a política 4.1–4.3: os números são diagnósticos, não estimativa de generalização. O conjunto de teste de 350 não foi usado.
- **Gabarito e grupos A/B vêm do dataset gerado por LLM**; há erros (val-024, val-136). Os grupos A/B refletem a associação, que também é imperfeita.
- **Uma rodada só**: a variação por temperatura (T=0,3) faz alguns casos mudarem entre rodadas.
- Perguntas "Com publicações concorrentes" dependem do próprio julgamento do auditor (ver nota da tabela).

## 10. Recomendação sobre a confiabilidade da versão 4.3

1. **Não integrar ao Zelo.** Respostas dadas: 74% aceitáveis e 26% incorretas; 6 com afirmação sem evidência. Utilidade: 20,7% das perguntas receberam alguma resposta.
2. **Tratar `respondida` como mais confiável que `parcial`:** 8 completas, 7 totalmente corretas e 1 com imprecisão de local; 23 parciais, 8 incorretas (35%). Em produção, parciais exigiriam revisão.
3. **Antes de nova versão:** (a) adicionar verificação de adequação semântica (período, localidade, tipo de item) além de literalidade; (b) tratar os falsos positivos do verificador (valores presentes, nomes próprios); (c) restringir `fora_do_escopo` a temas fora do corpus; (d) melhorar recuperação do grupo B; (e) permitir `parcial` com aviso de cobertura para perguntas abertas; (f) corrigir o gabarito nos casos apontados e revisar humanamente os 21 casos MULTI (resultado em `auditoria_independente_21_multi.csv`).
4. **Pendências abertas:** revisão humana independente (ainda não feita, campos em branco nos CSVs antigos), perguntas reais de cidadãos e corpus gov.br, e qualquer decisão de integração, que depende de revisão humana e de validação em ambiente de integração.

---

## Anexo: resultado individual (resumo)

Coluna "Conf." = confiança do auditor. Justificativas e referências em `auditoria_independente_150.csv`.

| qid | grupo | MULTI | status do sistema | classificação independente | status adequado | sem evid. | conf. |
|---|---|---|---|---|---|---|---|
| val-000 | A | - | respondida | Correta | sim | - | alta |
| val-001 | A | - | ambigua | Ambigua de fato | sim | - | media |
| val-002 | A | - | respondida | Correta | sim | - | alta |
| val-003 | A | - | respondida | Correta | sim | - | alta |
| val-004 | B | - | ambigua | Abstencao indevida | não | - | media |
| val-005 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-006 | A | - | respondida | Correta | sim | - | alta |
| val-007 | B | sim | parcial | Incorreta | não | sim | alta |
| val-008 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-009 | A | - | ambigua | Abstencao indevida | não | - | alta |
| val-010 | B | - | ambigua | Ambigua de fato | sim | - | media |
| val-011 | B | - | ambigua | Ambigua de fato | sim | - | baixa |
| val-012 | B | - | parcial | Incorreta | não | - | media |
| val-013 | A | sim | parcial | Correta, mas parcial | sim | - | media |
| val-014 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-015 | B | - | fora_do_escopo | Abstencao correta | não | - | alta |
| val-016 | A | - | ambigua | Ambigua de fato | sim | - | baixa |
| val-017 | A | sim | parcial | Correta, mas parcial | sim | - | alta |
| val-018 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-019 | B | - | fora_do_escopo | Abstencao indevida | não | - | media |
| val-020 | A | sim | parcial | Correta, mas parcial | sim | - | media |
| val-021 | A | sim | parcial | Correta, mas parcial | sim | - | alta |
| val-022 | B | sim | insuficiente | Abstencao indevida | não | - | alta |
| val-023 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-024 | A | sim | respondida | Correta, mas parcial | não | sim | media |
| val-025 | B | - | fora_do_escopo | Abstencao correta | não | - | media |
| val-026 | B | - | insuficiente | Abstencao correta | não | - | baixa |
| val-027 | A | - | ambigua | Abstencao indevida | não | - | media |
| val-028 | A | - | ambigua | Abstencao indevida | não | - | alta |
| val-029 | B | - | fora_do_escopo | Abstencao indevida | não | - | media |
| val-030 | A | - | ambigua | Ambigua de fato | sim | - | media |
| val-031 | A | - | insuficiente | Abstencao indevida | não | - | alta |
| val-032 | A | sim | insuficiente | Abstencao indevida | não | - | alta |
| val-033 | B | - | insuficiente | Abstencao indevida | não | - | baixa |
| val-034 | B | - | fora_do_escopo | Abstencao correta | não | - | alta |
| val-035 | A | sim | insuficiente | Abstencao indevida | não | - | media |
| val-036 | A | - | ambigua | Abstencao indevida | não | - | media |
| val-037 | A | - | ambigua | Ambigua de fato | sim | - | media |
| val-038 | A | - | ambigua | Ambigua de fato | sim | - | media |
| val-039 | A | sim | parcial | Incorreta | não | sim | media |
| val-040 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-041 | A | - | respondida | Correta | sim | - | alta |
| val-042 | B | - | fora_do_escopo | Abstencao correta | não | - | media |
| val-043 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-044 | B | sim | insuficiente | Abstencao indevida | não | - | baixa |
| val-045 | A | - | insuficiente | Abstencao indevida | não | - | alta |
| val-046 | B | - | fora_do_escopo | Abstencao indevida | não | - | media |
| val-047 | A | sim | insuficiente | Abstencao indevida | não | - | media |
| val-048 | B | sim | fora_do_escopo | Abstencao indevida | não | - | media |
| val-049 | A | - | respondida | Correta | sim | - | alta |
| val-050 | A | - | parcial | Incorreta | não | - | alta |
| val-051 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-052 | B | sim | ambigua | Abstencao indevida | não | - | baixa |
| val-053 | A | sim | insuficiente | Abstencao indevida | não | - | alta |
| val-054 | A | - | ambigua | Abstencao indevida | não | - | media |
| val-055 | B | sim | insuficiente | Abstencao indevida | não | - | media |
| val-056 | B | - | insuficiente | Abstencao indevida | não | - | media |
| val-057 | B | - | ambigua | Ambigua de fato | sim | - | media |
| val-058 | A | sim | insuficiente | Abstencao indevida | não | - | baixa |
| val-059 | B | sim | parcial | Correta, mas parcial | sim | - | alta |
| val-060 | A | sim | fora_do_escopo | Abstencao indevida | não | - | media |
| val-061 | B | - | insuficiente | Abstencao indevida | não | - | baixa |
| val-062 | A | - | insuficiente | Abstencao indevida | não | - | alta |
| val-063 | B | - | insuficiente | Abstencao indevida | não | - | baixa |
| val-064 | B | - | insuficiente | Abstencao indevida | não | - | media |
| val-065 | A | - | ambigua | Ambigua de fato | sim | - | media |
| val-066 | B | - | parcial | Correta, mas parcial | sim | - | media |
| val-067 | B | - | insuficiente | Abstencao indevida | não | - | baixa |
| val-068 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-069 | B | sim | ambigua | Abstencao indevida | não | - | media |
| val-070 | A | sim | parcial | Correta, mas parcial | sim | - | alta |
| val-071 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-072 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-073 | B | - | ambigua | Ambigua de fato | sim | - | baixa |
| val-074 | B | sim | fora_do_escopo | Abstencao indevida | não | - | alta |
| val-075 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-076 | B | - | insuficiente | Abstencao indevida | não | - | baixa |
| val-077 | A | - | ambigua | Ambigua de fato | sim | - | media |
| val-078 | B | - | insuficiente | Abstencao indevida | não | - | baixa |
| val-079 | B | sim | ambigua | Ambigua de fato | sim | - | media |
| val-080 | B | - | ambigua | Abstencao indevida | não | - | baixa |
| val-081 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-082 | B | - | ambigua | Ambigua de fato | sim | - | media |
| val-083 | B | - | insuficiente | Abstencao indevida | não | - | baixa |
| val-084 | A | - | ambigua | Ambigua de fato | sim | - | media |
| val-085 | A | - | ambigua | Ambigua de fato | sim | - | media |
| val-086 | B | - | fora_do_escopo | Abstencao indevida | não | - | media |
| val-087 | A | sim | insuficiente | Abstencao indevida | não | - | alta |
| val-088 | B | sim | insuficiente | Abstencao indevida | não | - | baixa |
| val-089 | B | - | insuficiente | Abstencao indevida | não | - | baixa |
| val-090 | A | - | respondida | Correta | sim | - | alta |
| val-091 | B | - | parcial | Correta, mas parcial | sim | - | media |
| val-092 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-093 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-094 | A | sim | ambigua | Abstencao indevida | não | - | media |
| val-095 | A | sim | ambigua | Abstencao indevida | não | - | baixa |
| val-096 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-097 | B | - | insuficiente | Abstencao indevida | não | - | alta |
| val-098 | A | - | ambigua | Ambigua de fato | sim | - | baixa |
| val-099 | B | sim | parcial | Correta, mas parcial | sim | - | media |
| val-100 | B | sim | parcial | Incorreta | não | - | media |
| val-101 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-102 | B | - | parcial | Correta, mas parcial | sim | - | alta |
| val-103 | A | - | ambigua | Ambigua de fato | sim | - | media |
| val-104 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-105 | A | - | insuficiente | Abstencao indevida | não | - | media |
| val-106 | A | - | insuficiente | Abstencao indevida | não | - | alta |
| val-107 | B | - | ambigua | Abstencao correta | sim | - | alta |
| val-108 | B | sim | insuficiente | Abstencao indevida | não | - | baixa |
| val-109 | B | - | fora_do_escopo | Abstencao indevida | não | - | media |
| val-110 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-111 | A | - | parcial | Correta, mas parcial | sim | - | media |
| val-112 | A | sim | insuficiente | Abstencao indevida | não | - | baixa |
| val-113 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-114 | A | sim | parcial | Correta, mas parcial | sim | - | media |
| val-115 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-116 | B | sim | fora_do_escopo | Abstencao correta | sim | - | media |
| val-117 | B | - | ambigua | Abstencao indevida | não | - | baixa |
| val-118 | A | - | parcial | Correta, mas parcial | sim | - | alta |
| val-119 | A | sim | fora_do_escopo | Abstencao indevida | não | - | alta |
| val-120 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-121 | A | sim | ambigua | Abstencao indevida | não | - | baixa |
| val-122 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-123 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-124 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-125 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-126 | A | sim | insuficiente | Abstencao indevida | não | - | alta |
| val-127 | B | - | insuficiente | Abstencao correta | não | - | baixa |
| val-128 | A | - | ambigua | Ambigua de fato | sim | - | baixa |
| val-129 | B | - | ambigua | Abstencao correta | sim | - | alta |
| val-130 | B | sim | parcial | Incorreta | não | sim | alta |
| val-131 | A | sim | parcial | Correta, mas parcial | sim | - | alta |
| val-132 | A | - | ambigua | Ambigua de fato | sim | - | baixa |
| val-133 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-134 | A | - | ambigua | Abstencao indevida | não | - | media |
| val-135 | A | - | ambigua | Abstencao indevida | não | - | media |
| val-136 | B | - | parcial | Incorreta | não | sim | alta |
| val-137 | A | - | ambigua | Ambigua de fato | sim | - | alta |
| val-138 | B | - | ambigua | Ambigua de fato | sim | - | media |
| val-139 | A | sim | ambigua | Ambigua de fato | sim | - | media |
| val-140 | A | - | ambigua | Ambigua de fato | sim | - | media |
| val-141 | A | - | insuficiente | Abstencao indevida | não | - | media |
| val-142 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-143 | A | - | parcial | Correta, mas parcial | sim | - | media |
| val-144 | A | sim | insuficiente | Abstencao indevida | não | - | baixa |
| val-145 | B | - | ambigua | Abstencao correta | sim | - | alta |
| val-146 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-147 | B | - | fora_do_escopo | Abstencao indevida | não | - | media |
| val-148 | B | - | ambigua | Ambigua de fato | sim | - | alta |
| val-149 | B | sim | parcial | Incorreta | não | sim | alta |
