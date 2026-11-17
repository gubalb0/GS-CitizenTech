# Auditoria de encerramento da Fase 4A — preparação da Fase 4B

Etapa **somente de leitura**: nenhum arquivo do pipeline, teste, corpus, índice, gabarito ou rodada foi alterado; sem chamadas ao modelo; `fail-closed-4.4.4a` inalterada. Auditor: modelo de linguagem (não é revisão humana). **Fato** = reproduzido offline ou lido nos documentos; **hipótese** = inferência. Auxiliares (só em `fase4/`): `auditoria_4a_simulacao.py/.json`, `auditoria_4a_apoio_exclusivo.py/.json`, `auditoria_4a_contexto.py/.json`, `auditoria_4a_contexto_S1forte.json`.

## 1. Integridade
`scripts/verificar_hashes.py`: **todos conferem** (RPA congelado, rodadas, auditorias, snapshots da 4.3, Fase 2, 3 e 4A). `geracao.py`, `evidencias.py` e `catalogo.py` vivos são idênticos aos `*_44_fase4a.py`; `VERSAO_POLITICA = "fail-closed-4.4.4a"`. Sem divergências.

## 2. val-007 — por que continua sendo entregue

**Afirmação geográfica produzida (fato):** "A implementação de serviços de saúde em Riacho Fundo II inclui ações relacionadas ao Conselho Regional de Saúde, eleições para membros conselheiros e programas voltados à saúde da mulher, como o Hospital da Mulher."
**O que sustenta cada parte:**
| Parte da afirmação | Trecho (doc, chunk) | O que o trecho realmente diz |
|---|---|---|
| "Conselho Regional de Saúde ... eleições para membros" | C1/C2 (doc 1236, Resolução CSDF) | Composição e eleição do **Conselho Regional de Saúde do Riacho Fundo II** (governança/controle social). É sobre RFII, mas **não é um serviço de saúde implementado**. |
| "programas voltados à saúde da mulher, como o Hospital da Mulher" | C3 (doc 1449, Ata do CDM-DF) | "Giselle Ferreira compartilha sobre sua visita à **São Paulo**... conheceu o **Hospital da Mulher** onde todos os equipamentos e rede funcionam 24 horas". O Hospital da Mulher é o de São Paulo. |
**Contexto do mesmo chunk C3 (fato):** a frase seguinte é "A senhora Ana Maria ressalta que em sua gestão apoia muito as mulheres do Riacho Fundo e **solicita o CEAM do Riacho Fundo II**" (um **pedido**, não um serviço implementado) e, antes, "relata sobre o **sonho** de em Brasília ter um hospital referência para a Mulher". RFII aparece na ata também como **local da reunião** ("sede da Escola de Samba Acadêmicos do Riacho Fundo II"). Ou seja, o chunk menciona RFII (por isso Fases 2/4A não veem falta de localidade), mas **nenhuma menção liga RFII a um serviço implementado**. Não assumi que a localidade da reunião seja a do serviço.
**Evidência independente de serviço implementado em RFII?** *Nos trechos enviados: nenhuma.* No corpus (não recuperado, BM25 14/21/83, híbrido 6/12/24): Portaria Conjunta 12/2025 (docs 571 e 591: crédito para a **construção** de base do SAMU no Posto de Saúde da Família QN 7B de RFII e **continuidade de licitação** da UBS Tipo II em RFII) e Aviso 005/2025 (doc 1413: licitação da UBS Tipo II). São serviços **em implantação/planejados**; ainda assim seriam resposta parcial legítima, que o contexto não contém.
**Por que continua entregue (fato):** M2 só decide em famílias conhecidas e `servicos` (OBJETO) não tem rótulo no trecho; M5 exige CNPJ; M4 não há período; as relações de C1/C2/C3 ficaram `nao_verificavel` (`necessaria=True` só para C3 e um grupo de C1/C2) e o estado `nao_verificavel` não bloqueia por desenho.
**Classificação adequada com o contexto enviado:** **`insuficiente`** (não há trecho que sustente um serviço implementado em RFII; o único candidato a "serviço" é de outra cidade). Uma resposta `parcial` só seria defensável se o contexto contivesse a Portaria 12/2025 ou o Aviso 005/2025, e mesmo então deveria dizer "em implantação". A diferença entre o que está sendo entregue e o que deveria ser é de **atributo** (governança e pedido x serviço implementado) e de **ato de fala** (solicitação/aspiração x realização), e não de localização textual. **Hipótese:** detectar isso exigiria interpretar modalidade ("solicita", "sonho") — não há estrutura para verificá-la sem lista lexical, e não há dados suficientes para validar tal lista.

## 3. Simulação: bloquear relações `nao_verificavel` (não aplicada)
Base: 30 respostas entregues no replay da 4A (8 `respondida` + 22 `parcial`), classificadas por auditoria anterior/complementar: 7 Corretas, 18 Corretas-mas-parciais, 2 Parcialmente sustentadas (val-044, 047), 3 Incorretas (val-007, 012, 100). Um item pode ter 2 relações (candidata e citação); contei por relação e por trecho.
| Política simulada | Respostas afetadas | Corretas / corretas-parciais | Parc. sustentadas | Incorretas |
|---|---:|---:|---:|---:|
| P1: qualquer relação `nao_verificavel` | 15 | 12 (5 + 7) | 2 | 1 (val-007) |
| P2: alguma relação `nao_verificavel` **necessária** | 12 | 9 (4 + 5) | 2 | 1 (val-007) |
| P3: nenhuma relação necessária `confirmada` | 10 | 8 (4 + 4) | 1 | 1 (val-007) |
| P4: todas as relações necessárias `nao_verificavel` | 10 | 8 | 1 | 1 (val-007) |
**Leitura:** a política mais seletiva (P3/P4) removeria **8 respostas boas para barrar 1 incorreta** (val-007). val-012 e val-100, também incorretas, **não** seriam barradas por nenhuma política. Afetadas boas em P3/P4: val-000, 003, 017, 021, 024, 031, 049, 090 (respostas simples cujo trecho não tem rótulo/destinatário reconhecível). Em val-007, das 6 relações `nao_verificavel` só as de C3 são necessárias (C1/C2 são secundárias).
**Descoberta importante sobre o registro:** em val-012 e val-100, as relações aparecem como **`confirmada`** (4 de 4) porque o **destinatário** coincide ("Hospital Regional de Ceilândia"), embora o **atributo** esteja incorreto (`equipamentos`: sem família; val-100: a cabeça extraída foi `aquisicoes`, e o rótulo do trecho é "objeto"/ausente). `estado_associacao` mistura dimensões (entidade/destinatário x atributo): `confirmada` **não** significa "a evidência responde ao atributo". Isso é uma limitação do esquema `relacoes/2` que pode induzir a erro em auditorias.
**Conclusão:** uma política "bloquear não verificável" custa muito mais que rende; não recomendada.

## 4. Mecanismo B — regra "sem termos mensuráveis ⇒ todos os trechos necessários"
**Dados reais:** nas 150 saídas, **nenhuma** resposta que chegou ao verificador estava sem termos de conteúdo, e o único rótulo conflitante registrado foi o de val-087 (bloqueio correto). Portanto a regra não causou falso bloqueio observado; o risco é teórico, mas reproduzível:
| Cenário sintético (código atual) | Resultado | Avaliação |
|---|---|---|
| **S1** "O prazo é de 12 meses." (sem termos mensuráveis); trecho "Vigência: 12 meses" correto e trecho "Objeto: reforma do prédio" (mesma publicação, rótulo incompatível) citado e **não usado** | `insuficiente` (`rotulo_incompativel_com_atributo`) | **falso bloqueio**: o trecho conflitante é desnecessário, mas todos contam como necessários |
| **S1b** controle: mesma resposta com uma palavra mensurável ("vigência contratual") | `respondida` | mostra que o resultado depende de a resposta ter um termo ≥ 6 letras |
| **S3** resposta que menciona "cirúrgica" (palavra só do trecho conflitante) | `insuficiente` | discutível: a resposta usa conteúdo de um trecho de atributo errado; pode ser bloqueio legítimo ou ruído |
| **S2** o próprio apoio de uma parte da resposta ("prédio Santos") é o trecho de objeto | `insuficiente` | consistente com a regra: parte da resposta vem de trecho de outro atributo |
**Testes sintéticos adicionais propostos (não implementados):** (T1) S1 deve entregar, pois o trecho conflitante não sustenta nada; para isso a regra de apoio deve usar um limiar menor (ex.: palavras ≥ 4 letras e números ≥ 2 dígitos) **ou**, sem termos, considerar necessários só os trechos que contêm o **valor/candidata principal** da resposta; (T2) resposta de uma palavra ("Sim.") com um trecho conflitante e um de apoio: definir o comportamento esperado (bloquear é aceitável, mas deve ser explícito); (T3) resposta só com números < 3 dígitos ("12 meses") em duas publicações; (T4) termo presente em dois trechos (nenhum exclusivo) e um deles conflitante: o conflitante não é necessário, o outro sustenta; (T5) termos só em maiúsculas (siglas) em trecho conflitante e trecho correto; (T6) o conflito de rótulo em trecho sem termo exclusivo em resposta com `termos` vazios e uma única unidade (deve continuar bloqueando).

## 5. Preparação da Fase 4B — montagem de contexto (diagnóstico)
**Quadro geral (150 perguntas):** 5 chunks recuperados em todas; enviados: 3 em 102, 4 em 34, 5 em 9, 2 em 5. Em **141/150 há chunk descartado**, sempre por **orçamento** (3.000 tokens; o limite `max_chunks` nunca é o motivo). Cada chunk custa 164–634 tokens (mediana 530); o prompt base custa ~1.244; sobram ~1.750 tokens ⇒ 3 chunks.
**val-087 (fatos, espelho do `montar_contexto` com tokens por chunk):**
| Pos. | Chunk (ord.) | Tokens | Enviado | Motivo | Contém atributo |
|---|---|---:|---|---|---|
| 1 | ord.4 (Art. 4º IX) | 504 | sim | — | `atribuições` (incidental) |
| 2 | ord.1 (lista de membros) | 613 | sim | — | não |
| 3 | ord.0 (cabeçalho, Art. 1º/2º) | 580 | sim | — | `atribuições` (incidental) |
| 4 | ord.2 | 604 | **não** | acumulado 2.948 + 604 > 3.000 | cabeçalho "Art. 4º **Competência** e Disposições" |
| 5 | **ord.3** | 569 | **não** | acumulado 2.948 + 569 > 3.000 | **"IV – Compete à CRSSU discutir e deliberar..."** (a competência) |
**Outros casos "recuperado e não enviado"** (val-063, 074, 086, 147): o chunk descartado foi o 4º/5º por orçamento (acumulado 2.862–2.983). Em nenhum deles o atributo pedido tem rótulo de família (063 `insumos`, 086 `novas`, 147 `procedimentos`); em 074 (`objeto`) todos os chunks têm "objeto". Esses quatro **não** são resolvidos por priorização de atributo (nota: a coluna "contém atributo" por palavra-família é um sinal fraco; "atribuições" aparece em muitos chunks, incidentalmente).
**Estratégias que preservam o orçamento (simuladas só na seleção; o efeito nas respostas não é testável sem o modelo):**
| Estratégia | Regra | Perguntas com contexto diferente (de 150) | Respostas dadas na 4.3 afetadas | Efeito em val-087 | Grupos A/B (gabarito imperfeito) |
|---|---|---:|---|---|---|
| **S1 forte** | priorizar, na ordem estável, chunks que contêm o **rótulo que repete o atributo pedido** (`compete`/`competência` para "competências"; só quando o atributo tem família) | **11** | **1** (val-130, já bloqueada) | envia ord.2, **ord.3** (a competência) e ord.4 | B→A em val-080 e val-130 |
| S1 fraco | idem, com qualquer rótulo da família (inclui "atribuições") | 17 | — | muda, mas pode manter o chunk certo de fora (cue incidental) | B→A em 040, 044, 080, 130 |
| **S2** | priorizar o chunk que cobre mais **nomes da pergunta** | 36 | **9** (021, 059, 070, 099, 100, 111, 130, 131, 149) | muda (cobertura quase uniforme: 3/3/3/4/3) | B→A em 040, 044, 074, 086, 147 (alcança 3 dos 4 "recuperado e não enviado") |
Outras ideias (não simuladas): remover duplicação textual/sobreposição entre chunks vizinhos do mesmo documento; truncar chunks mais longos que a mediana (já há corte em 350 tokens de superfície); enviar apenas o trecho do chunk em torno dos termos da pergunta. Todas mudam o texto que o modelo vê e exigem avaliação com o modelo.
**Observação:** S2 alcança mais casos, mas altera 9 respostas hoje entregues (várias corretas-mas-parciais) sem como saber o efeito; S1 forte é a mais estreita e tem evidência concreta (val-087).

## 6. Limitações
- Rótulos "corretas/incorretas" vêm das auditorias anteriores e da complementar (modelo); val-031/032/044/047 avaliados por mim. 
- O sinal "contém atributo" por palavra é fraco; só val-087 tem prova direta (a frase "Compete à CRSSU" no chunk descartado).
- A simulação de contexto só altera a **seleção**; não há como prever a resposta sem o modelo.
- Grupos A/B dependem de gabarito imperfeito. As 150 perguntas já serviram para projetar as fases.

## 7. Recomendação objetiva sobre a Fase 4B
1. **Pode-se iniciar a 4B, com escopo mínimo: S1 forte** (priorização por rótulo que repete o atributo, dentro dos 5 recuperados, sem mudar orçamento, retriever ou prompt). Evidência: val-087 (e só ele entre os casos analisados) e impacto limitado a **11 perguntas, 1 resposta entregue**; as outras 139 mantêm contexto idêntico (comparabilidade preservada).
2. **Condição:** a 4B só pode ser validada com o modelo. Exigir autorização explícita para regenerar **apenas as 11 perguntas afetadas** (mais controles), nunca a rodada completa; os testes offline cobrem apenas a seleção determinística.
3. **Não incluir S2** nesta primeira etapa (36 perguntas, 9 respostas entregues afetadas, sem evidência de ganho).
4. **Antes ou junto com a 4B (verificação, sem modelo):** (a) separar no esquema `relacoes` as dimensões (`entidade/destinatario`, `atributo`, `localidade`) para que `confirmada` não seja lida como "responde ao atributo" (val-012/100); (b) ajustar a regra de apoio exclusivo para não bloquear no S1 (testes T1–T6); (c) decidir a política de val-007: não há solução estrutural (ato de fala); manter como limitação documentada ou aceitar, explicitamente, um custo de 8 respostas boas por uma incorreta (não recomendado).
5. **Sem evidência suficiente:** mudanças no retriever (relevantes ficam em 6–88 nos dois modos), regra geral contra respostas genéricas, bloqueio de `nao_verificavel`.
