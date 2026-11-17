# Etapa 4.4 — Diagnóstico das falhas da auditoria independente da 4.3

Escopo: investigação e plano. **Nenhum código, corpus, índice, dado original, arquivo congelado do RPA ou auditoria anterior foi alterado; nenhuma geração foi executada.** Tudo novo está em `docs/assistente/diagnostico_4_4/`.
Único procedimento "de execução": um *replay offline* da recuperação BM25 + `montar_contexto` (sem LLM, índice só lido) para reconstruir quais chunks foram realmente enviados ao modelo (`scripts/replay_contexto.py`, resultado em `replay_contexto.json`).
Quem diagnostica: o mesmo modelo que fez a auditoria (não é revisão humana). Fatos lidos nos documentos estão marcados como **fato**; o restante é **hipótese** ou **interpretação**.

## 0. Resumo e ordem de prioridade

Principais achados novos (além da auditoria):

1. **Os números do relatório da auditoria batem com o CSV**, mas três deles misturam denominadores e merecem ressalva (seção 1). Descobri ainda **três erros de atribuição na própria auditoria** (seção 1.3): val-050 (o midazolam *está* no período pedido), val-062 (o bloqueio foi legítimo: o modelo fabricou o valor) e val-097 (o grupo real é A, não B).
2. **O verificador atual valida o texto do trecho escolhido pelo modelo, não o conteúdo dos chunks/documentos citados.** É a causa comum dos falsos positivos (val-097, val-106, val-031) e, ao mesmo tempo, do que ele não pega: períodos, localidades e tipo de informação (val-050, val-130, val-136). As duas falhas são do mesmo desenho (seção 3 e 6C).
3. **Dos 56 casos de abstenção indevida, só 8 são falsos positivos do verificador** (eram o que o relatório da auditoria sugeria como o grosso). O maior bloco é recuperação/contexto (25 = 15 + 4 + 6) e geração/modelo com o documento no contexto (19 = 14 + 5) (seção 4).
4. **A medida "grupo A/B" da rodada tem um erro de método** (assume que os chunks enviados são o prefixo do ranking), com efeito pequeno (1 caso muda de grupo, 11 casos têm contexto não-prefixo).
5. **Integridade de `chunks_exemplos.json`:** não existe snapshot nem hash anterior; **não é possível provar igualdade byte a byte**. Há evidência parcial forte (4 de 7 chunks idênticos aos do índice de 13/11) e o arquivo já era gerado pelo mesmo script desde 13/11 (seção 5).
6. O conjunto de 350 **não está disponível localmente** e herda os problemas do benchmark (35% das perguntas da validação não têm resposta única). Não recomendo usá-lo como avaliação final sem uma etapa de qualificação do gabarito (seção 7).

**Fazer primeiro (baixo risco, alto ganho):** (1) verificador: checar valores/nomes contra o chunk e o documento citado e contra a candidata literal, normalizar datas e siglas; (2) verificador: checar período, localidade e entidade **em cada evidência**, não "em ao menos uma"; (3) relabel de `fora_do_escopo`; (4) corrigir o método de medição (`enviado`, grupo A/B, auditoria do gabarito). **Não implementar ainda:** limiar de score do BM25, juiz LLM, mudança do retriever/índices, mais contexto, mudança de modelo, relaxar a abstenção por ambiguidade (seção 8).

---

## 1. Conferência da auditoria

Arquivos conferidos: `RELATORIO_AUDITORIA_INDEPENDENTE_4_3.md`, `auditoria_independente_150.csv`, `auditoria_independente_21_multi.csv`, `metricas.json`. Recontagem direta no CSV (`150` linhas):

| Número no relatório | Reconferido no CSV | Denominador / observação |
|---|---|---|
| 31 respostas dadas: 7 corretas, 16 parciais, 8 incorretas | 7 + 16 + 8 = 31 ✔ | "16 parciais" = classe do auditor *Correta, mas parcial*. **Não é o mesmo conjunto que o status `parcial` do sistema (23)**: a classe inclui val-024, que o sistema marcou como `respondida`, e os 8 incorretos são todos de status `parcial` |
| 6 respostas com afirmação sem evidência | 6 ✔ (val-007, 024, 039, 130, 136, 149) | **Sobreposição:** 5 são das 8 incorretas; 1 (val-024) é "correta, mas parcial". Três incorretas (val-012, 050, 100) **não** têm a marca: erro de tipo de item/período, não de afirmação sem apoio |
| Parciais 15/23 | ✔ | 23 = status `parcial` do sistema; 15 = *Correta, mas parcial*; 8 = *Incorreta*. Nenhuma `parcial` foi "Correta" integral: o rótulo do auditor *Correta, mas parcial* é a única classe aceitável para parciais |
| Completas 7/8 estrita, 8/8 flexível | ✔ | 8 = status `respondida`. A diferença é val-024. **Reparo de leitura:** a versão "flexível" conta val-024 como correta mesmo com a afirmação sem evidência (local) |
| 119 abstenções = 53 + 10 + 56 | 119 ✔ | 119 = 150 − 31. 53 = *Ambígua de fato* (todas com status `ambigua`) |
| 56 abstenções indevidas | ✔ | Por status: 31 `insuficiente`, 15 `ambigua`, 10 `fora_do_escopo`. Por confiança do auditor: 14 alta, 23 média, 19 baixa |
| 71 classificações inadequadas | ✔ (71) | **Composição:** 56 indevidas + 8 incorretas + 1 (val-024) + 6 abstenções corretas com status mal rotulado (val-015, 025, 026, 034, 042, 127) = 71. É um **agregado de categorias de gravidade diferente**, não uma taxa de erro. Atenção: "71" coincide com o número de respostas `ambigua` (53 + 15 + 3), mera coincidência |

**Divergências e ressalvas (nada foi corrigido nos arquivos originais):**

- **1.1** *Taxa de abstenção adequada 63/119 (52,9%)* soma 53 *ambíguas de fato* + 10 *abstenções corretas*; em 6 das 63 o **status** está errado. Não é "taxa de abstenção correta" no sentido de rótulo.
- **1.2** *"Com publicações concorrentes" (56)* foi construído com o próprio julgamento do auditor (ver relatório) e é circular; não deve ser citado como desempenho.
- **1.3 Erros de atribuição que descobri na própria auditoria (errata; não editei o relatório original):**
  - **val-050:** o relatório diz que o midazolam "tampouco está comprovadamente no período". **Fato:** o doc 1307 declara "no período de 31/07/2025 a 22/08/2025"; o midazolam está no período. Dois dos três itens (heparina e metaraminol, doc 196, período 31/01–06/02/2025) estão fora. A classificação *Incorreta* se mantém, mas é **1 de 3 itens correto**.
  - **val-062:** a auditoria o trata como bloqueio por `trecho_nao_literal` sobre resposta existente. **Fato:** o modelo **inventou** a citação "Valor do Contrato: R$ 1.105.500,00" (o doc 1450 diz R$ 2.449.859,97 e empenho inicial R$ 204.155,00). O bloqueio foi legítimo (a resposta existe no corpus, mas o modelo não a produziu).
  - **val-097:** o relatório fala em grupo B. **Fato:** o replay mostra que o chunk do doc 105 foi enviado (a rodada marcou `enviado` por posição); o grupo real é A. Grupos corretos: A = 77, B = 73 (não 76/74); abstenções indevidas: A = 28, B = 28 (não 27/29).
- **1.4** Julgamentos de confiança baixa (27) devem ser lidos como inconclusivos; a sensibilidade (só alta/média) já está no `metricas.json`.

## 2. Diagnóstico das 8 respostas incorretas

Contexto de método: recuperação e `montar_contexto` foram reproduzidos exatamente (150/150 recuperações idênticas e mesmo número de chunks enviados). "Documento correto" = o que o auditor identificou (o gabarito do dataset é pista e, nestes casos, quase sempre inadequado).

| Caso | Pergunta (resumo) | O que o sistema fez | Doc recuperado | Doc que deveria sustentar | Trecho que comprova | Causa provável | Componente | Detectável automaticamente? |
|---|---|---|---|---|---|---|---|---|
| **val-050** | Insumos farmacêuticos p/ HRT de 31/07 a 22/08/2025 | Listou midazolam + heparina + metaraminol | 1307 (pos. 1, **período correto**) e chunk **0004** do doc 196 | 1307 (só ele) | doc 1307: "no período de 31/07/2025 a 22/08/2025"; doc 196: "no período de 31/01/2025 à 06/02/2025" | Os dois docs usam o mesmo modelo textual ("insumos e serviços de reparo ... PDPAS/HRT"), só muda o período; o BM25 os iguala. O chunk 0004 do doc 196 **não carrega o período** (ele está no 1º chunk). O modelo juntou itens de dois períodos | Chunking/contexto (período fica só no 1º chunk), retriever (empata documentos-modelo), **verificador** (aceita o período se aparecer em *alguma* fonte citada) | **Sim**: extrair o intervalo do documento ("no período de X a Y") e comparar com o da pergunta, por evidência |
| **val-130** | Empresas credenciadas p/ serviços na **Asa Sul** | "Biosphere Health Center (CNPJ ...0007-93)" e Visão Hospital de Olhos | 6, 920, 1645 | doc 6 (Oncoclínicas: Matriz + filiais; a filial 2 e a matriz estão na Asa Sul), 920 | doc 6: "Filial (3): ST SHL/NORTE ... ED. Biosphere Health Center – **Asa Norte** ... CNPJ 11.859.927/0007-93" | **Substituição de entidade**: tomou o nome de um edifício dentro do endereço da filial como se fosse a empresa e ignorou a localidade ("Asa Norte") dita no mesmo trecho | **Gerador** (extração de entidade) + **verificador** (localidade só é checada no chunk inteiro, onde "Asa Sul" aparece em outras filiais) | **Sim**: o *trecho* citado contém uma localidade (Asa Norte) diferente da da pergunta e não contém a pedida |
| **val-136** | Quais **especialidades** foram propostas pelo Hospital Home? | Respondeu com o objeto do edital ("serviços assistenciais clínicos e cirúrgicos...") | 94 (Termo 09/2025) | **Nenhum**: o doc 94 e o 72 dizem que as especialidades "estão elencadas na carta proposta doc. SEI nº 160711978" (não publicada). A resposta correta é "não consta" | doc 94: "interessada em se credenciar nas especialidades elencadas na carta proposta doc. sei n° 160711978" | O modelo **preencheu o tipo de informação pedido com outro** (objeto do edital) em vez de dizer que o dado não está publicado | **Gerador** (não respondeu ao atributo pedido; inferiu), **verificador** (não checa adequação do atributo) | **Parcial**: a evidência cita uma remissão a anexo ("elencadas na carta") e a resposta traz uma lista; regra "remissão a documento não publicado + resposta enumerativa → insuficiente". Dificilmente genérica |
| val-007 | Serviços de saúde implementados em Riacho Fundo II | Misturou eleição do Conselho de Saúde com "Hospital da Mulher" | 1236, 1449, 303 | 571/591 (Portaria conjunta 12/2025: UBS Tipo II e base SAMU em RFII), docs 1413 (Aviso 005/2025) | doc 1449: "Hospital da Mulher" é o de **São Paulo**, visitado por uma conselheira; a ata tem "Riacho Fundo II" só como local da reunião | Retrieval trouxe documentos que mencionam o termo-local por outro motivo; o modelo costurou itens sem relação | **Retriever** (docs relevantes não chegaram), **gerador** (agregou), **verificador** (entidade presente no chunk, não na frase evidência) | **Parcial**: a frase do trecho 3 não contém "Riacho Fundo" nem tema de saúde implementada |
| val-012 | **Equipamentos médicos** adquiridos p/ HRC | Álcool etílico e manutenção de macas | 238 e outros | docs 958, 1346 (aquisição de equipamentos) | doc 238: "ALCOOL ETILICO ABSOLUTO ... serviço de Manutenção Corretiva em Macas" | Casou o **local** (HRC) e perdeu o **tipo** (equipamento) | Retriever (não trouxe docs de equipamentos), gerador (categoria), verificador (sem checagem de tipo) | Parcial: léxico "equipamento" ausente dos itens; risco de falsos positivos |
| val-100 | **Aquisições de equipamentos** p/ HRC | Serviços de manutenção (hemodiálise, osmose) | 440, 1035, 322 | docs de aquisição de equipamentos | doc 440: "serviço na MÁQUINA DE HEMODIALISE" | Igual a val-012 | Idem | Idem |
| val-039 | Unidades de SSebastião que receberão equipamentos odontológicos | "Não foram especificadas as denominações" | 303 (chunk 0000, o 1º; as linhas de São Sebastião estão em outros chunks do mesmo doc de 32 mil caracteres) | doc 303 (grade com "UBS 1 SSB", "UBS 3 SSB", "UBS 9 SSB"...) | doc 303: "GSAP 1 SSB (UBS 1 SSB) ... SAO SEBASTIAO" | **Documento grande e tabular**: o chunk enviado era o cabeçalho da tabela; o dado estava em outro chunk. O modelo transformou "não vi no contexto" em afirmação sobre o documento | **Chunking/retriever** (tabela longa; sigla SSB), **gerador** (afirma ausência no doc a partir de contexto parcial) | **Sim (parcial)**: frase "não foram especificadas" + doc com muitos chunks não recuperados → deve ser `insuficiente`, não `parcial` |
| val-149 | Ações de atenção básica em Ceilândia em 2025 | Resposta genérica ("programas de promoção da saúde...") | 1365, 1611, 1052 | Nenhum doc claramente responde (o auditor não achou) | doc 1611: texto sobre o INAS, sem Ceilândia; doc 1052: decreto de cargos | **Evidência fraca** aceita como suficiente; o modelo sintetizou texto genérico de trechos sem relação | **Retriever** (sem doc relevante), **gerador** (devia abster-se), **verificador** (acha "Ceilândia" no chunk do decreto) | Parcial: nenhuma evidência traz a ação; pontuação BM25 **não** separa (ver abaixo) |

Observações transversais: (a) os 8 têm citações literais e `verificacao.ok`; (b) 6 dos 8 são do grupo B (a fonte esperada pelo dataset não foi enviada), mas o gabarito nesses casos é pouco confiável (val-007, 100, 149 têm "docs esperados" sem relação com a pergunta); (c) a pontuação BM25 do primeiro resultado **não separa** corretas de incorretas (incorretas: 16,8–35,3; corretas: 20,8–40,9; corretas-mas-parciais: 16,2–38,3), então um limiar simples de score não é suportado por evidência.

## 3. Falsos positivos do verificador (18 abstenções reprovadas)

### 3.1 val-097 — `5.250.814,42`
- **Fato:** o doc 105 traz "R$ 5.250.814,42" e "Construção da Unidade Básica de Saúde da Ponte Alta do Gama"; a candidata do modelo (`candidatas[].resposta_possivel = "R$ 5.250.814,42"`) foi marcada `literal=True`. A **citação (`trecho`)** escolhida pelo modelo termina em "...NATUREZA DA DESPESA FONTE VALOR 10.301" (cortada pelo limite de 300 caracteres) e **não inclui o valor**.
- **Causa:** `evidencias.afirmacoes_nao_sustentadas` valida os números/nomes da **resposta** apenas contra os **trechos** citados (+ metadados da edição); ignora o resto do chunk e a candidata literal. Não é problema de normalização de números: `5.250.814,42` seria encontrado se estivesse no texto comparado.
- **Componente:** verificador (granularidade da base de comparação) e gerador (citação truncada).

### 3.2 val-106 — "Hospital Lago Sul S/A (Hospital Daher)"
- **Fato:** o doc 994 contém "Hospital Lago Sul S/A, (Hospital Daher)" e "DATA DA ASSINATURA DO TERMO DE COMPROMISSO: 27/06/2025". A citação do modelo trouxe só o OBJETO e a data, não o trecho que nomeia o hospital.
- **Duas causas independentes:** (1) **nomes** `s/a` e `daher` da resposta só são procurados nos trechos; (2) **período:** `periodo_ausente` só reconhece o mês pelo **nome** ("junho") ou pela data da edição (2025-07-02 → julho); a data **numérica** "27/06/2025" no próprio trecho não é interpretada. Isso é um falso negativo de **normalização de datas** (não de números nem de entidades).
- **Componente:** verificador (comparação textual e extração de datas).

### 3.3 Tabela de todos os 18 casos reprovados pelo verificador

| Tipo | Casos | Causa | Reprovação legítima? |
|---|---|---|---|
| **A. Base de comparação estreita** (valor/nome está no chunk, não no trecho) | val-097, val-106 | Seção 3.1/3.2 | **Não** (falso positivo) |
| **B. Eco da pergunta / chunk vizinho** | val-031 (`2023`: o ano está na pergunta e no chunk C1 do mesmo doc 1464; o chunk citado C2 só tem os valores mensais) | `validar_saida` exige que cada número da resposta esteja nos chunks citados e **não isenta números da pergunta** (a outra regra, `afirmacoes_nao_sustentadas`, isenta) | **Não** (falso positivo de desenho) |
| **C. Entidade/sigla/morfologia** | val-087 (`nome=coordenacao`), val-141 (`programa, dados, periciais`) | `alinhamento` exige cada palavra capitalizada da pergunta literalmente no chunk citado: o documento usa sigla (CRSSU, PNIDPD) ou outra forma (`Perícias`) | **Não** (falso positivo) |
| **D. Citação com formato inválido, conteúdo correto** | val-032, val-045 (o modelo emendou duas linhas de tabela sem "..."), val-047 (vírgula virou hífen) | `trecho_literal` exige contiguidade e pontuação | **Em parte** (a regra é correta; o dado era recuperável da candidata/da janela) |
| **E. Bloqueio legítimo de geração ruim** | val-062 (valor inventado), val-108 (texto corrompido "超级" no fim da citação), val-126 (citação emendada de dois locais), val-033, 044, 058, 063, 083, 088, 089 (itens sem apoio) | Modelo | **Sim** |

Total: 8 falsos positivos reais (A–D, seção 4) e 10 bloqueios legítimos. **Normalização de números** não é a causa de nenhum caso; as causas são granularidade da base de comparação (A, B), regras de nomes sem siglas/morfologia (C) e datas (A: val-106).

## 4. As 56 abstenções indevidas por causa (causa primária)

Regra de atribuição: `scripts/causas.py`/`causas2.py` (documentos "que respondem" extraídos da justificativa do auditor e comparados com os chunks recuperados/enviados; **aproximação**, sujeita a erro do meu levantamento). Detalhe por caso: `causas_56_abstencoes_indevidas.csv`.

| # | Causa | N | Casos | Resolvível sem aumentar risco de erro? |
|---|---|---:|---|---|
| 1 | **Recuperação inadequada** (documento que responde não foi recuperado) | 15 | 019, 022, 029, 048, 055, 056, 058, 064, 067, 069, 089, 094, 112, 117, 134 | Só com mudança no retriever (alto custo/risco) — **não agora** |
| 2 | **Filtro de identificabilidade/relevância excessivo** (4.1–4.3 transforma em `ambigua` quando as publicações dão a mesma resposta/duplicadas) | 4 | 009, 054, 095, 135 | **Sim**, se a regra exigir respostas equivalentes verificadas por valor (já existe `respostas_equivalentes`); risco médio |
| 3 | **Verificador rejeitando evidência válida** | 8 | 031, 032, 045, 047, 087, 097, 106, 141 | **Sim**, mantendo a exigência de que o valor exista no documento citado: não abre brecha para o caso val-062 |
| 4 | **fora_do_escopo indevido** (causa secundária; sempre acompanha outra) | 10 | 019, 029, 046, 048, 060, 074, 086, 109, 119, 147 | **Sim**: reclassificar rótulo (não muda o conteúdo, só `insuficiente`/`ambigua`) |
| 5 | **Geração incapaz** (modelo com o doc no contexto) | 19 | 14: 004, 027, 028, 035, 036, 052, 053, 060, 061, 080, 105, 119, 121, 144 (sem reprovação; o modelo se absteve ou usou `ambigua`); 5: 033, 044, 062, 108, 126 (bloqueio legítimo) | Parcial: ajuste de prompt/estrutura da saída; risco médio; 5 são geração perigosa que o verificador deve continuar barrando |
| 6 | **Falta de contexto** (doc recuperado, mas descartado pelo orçamento de ~3K tokens) | 4 | 063, 074, 086, 147 | Só mudando orçamento/seleção; risco de latência/memória; **não agora** |
| 7 | **Pergunta aberta/plural sem documento único** (exige resposta `parcial` com cobertura) | 6 | 046, 076, 078, 083, 088, 109 | Depende de parcial seguro (ver 6D); risco médio |

Nota: 35 das 56 são perguntas do tipo lista ("quais..."), o que sobrepõe as causas 1, 5 e 7. Contagens por grupo corrigidas pelo replay: A = 28, B = 28.

## 5. Integridade de `data_assistente/derivados/chunks_exemplos.json`

**Fatos:**
- O arquivo foi reescrito em 2026-11-15 13:44:22 pelo script de conferência (`scratchpad/final_checks.py`), que contém o gravador `chunks_exemplos.json` (3 chamadas de `chunkear_documento`: doc 1647 `estrutura 500/50`, doc 1080 `estrutura 500/50` primeiros 3 chunks e `tamanho 500/0` primeiros 3; 7 entradas).
- **O mesmo código já havia sido executado em 2026-11-13 às 10:46 (horário local; 13:46 UTC na transcrição)**, antes da construção dos índices (11:26) (transcrição da sessão: "exemplos gravados: 7"; a listagem dos arquivos alterados naquele dia mostra `chunks_exemplos.json` com 26 KB). O arquivo atual tem 26.976 bytes (≈ 26 KB). Ou seja, o conteúdo anterior foi gerado pelo mesmo gravador (provavelmente o mesmo arquivo).
- **Não existe** snapshot, hash anterior ou commit: o repositório Git está sem nenhum commit (`git count-objects` = 0), `data_assistente/versoes/` não contém o arquivo e nenhum relatório registra seu hash. `citizentech/` não referencia o arquivo (foi gerado por script avulso).
- SHA-256 atual (referência daqui em diante): `8c9d583afde2423ce8ceda57d3f8f0b7df60e7fe140eabad076744d127c82f37`.
- **Verificação independente que consegui fazer:** comparei as 4 entradas `est500o50` (doc 1647:0000 e doc 1080:0000..0002) com os chunks do **índice construído em 13/11 às 11:26** (`indices/est500o50/chunks.jsonl`): **todos os campos são idênticos, inclusive o hash do chunk (4/4)**. As 3 entradas `tam500o0` não existem em nenhum índice e **não podem ser verificadas**. `chunking.py` não foi alterado desde 13/11 10:43 (data de modificação; sem hash de referência).

**Conclusão:** não é possível provar que o arquivo não mudou, e **a geração determinística não foi tratada como prova**. A evidência é: 4 de 7 entradas confirmadas por fonte independente; as outras 3 dependem apenas de `chunking.py` não ter mudado. O arquivo é um exemplo ilustrativo, não é entrada de nenhum pipeline (nenhum código o lê). **Não alterei nem sobrescrevi nada**; o arquivo não foi tocado nesta etapa. **Ação recomendada:** a partir de agora registrar o SHA-256 acima no manifesto do projeto e mover a rotina de conferência de hashes para um script que **não escreva em `data_assistente/`**.

## 6. Proposta técnica para a versão 4.4 (por componente)

Princípio: cada mudança só entra se existir teste que reproduza o erro com os casos atuais (regressão) e um teste de não-regressão para os casos que hoje funcionam.

### A. Retriever (congelado — **só propor**, sem implementar agora)
| Proposta | Arquivo/função | Problema que resolve | Risco | Teste necessário |
|---|---|---|---|---|
| A1. Carregar no chunk os campos do documento (`período`, localidade, ref.) — **no cabeçalho do contexto**, não no índice | `geracao._cabecalho`/`montar_contexto` (sem reconstruir índices) | val-050 (chunk 0004 sem período) | Baixo (só texto do prompt; +tokens) | Teste unitário com doc 196 (chunk 0004 deve exibir "período 31/01/2025 a 06/02/2025"); medir tokens |
| A2. Filtrar/rerankear por período, localidade e órgão extraídos da pergunta (antes de enviar) | novo módulo `consulta.py` + `Indice.buscar` (pós-filtro, sem alterar índice) | val-050, val-130, val-007 | Médio: filtro errado remove o doc certo | Avaliar recall@5 antes/depois no conjunto de **desenvolvimento** com a regra "nunca descartar, só reordenar" |
| A3. Reduzir falsos concorrentes: tratar `ids_equivalentes` e atos-modelo repetidos antes do teste de concorrência | `catalogo.relevantes/concorrentes`, `evidencias.publicacoes_concorrentes` | val-009, 054, 095, 135 | Médio (risco de responder ambíguo) | Reutilizar `test_multi_43.py` + casos de valores diferentes (val-005, 018, 023 devem continuar `ambigua`) |
| A4. **Não** alterar os índices nem usar o modo híbrido sem avaliação própria | — | R@5 do híbrido (0,458) vs BM25 não foi comparado no pipeline completo | — | Só com avaliação separada em desenvolvimento |

### B. Gerador
| Proposta | Arquivo/função | Problema | Risco | Teste |
|---|---|---|---|---|
| B1. Instrução e schema: responder **só ao atributo pedido**; se o atributo não consta, status `insuficiente` com "não consta na publicação" | `PROMPT_SISTEMA`, `CAMPOS_SAIDA` (versão do prompt) | val-136, 149 | Médio (mais abstenções) | Casos val-136 (esperado `insuficiente`), val-019/val-064 (esperado resposta) |
| B2. Campo `entidade_localidade` por evidência (o modelo declara qual entidade/localidade cada trecho sustenta) para o verificador conferir | `validar_saida` | val-130 | Baixo | val-130; entidades com siglas |
| B3. Não afirmar ausência a partir de contexto parcial ("não foram especificadas" → `insuficiente`) | prompt + regra em `_aplicar_politica` | val-039 | Baixo | val-039 |
| B4. Diferenciar completa x parcial por regra, não por escolha do modelo (já em `completude`); exigir aviso de cobertura em perguntas lista | `evidencias.compor/aviso_cobertura` | val-007, 012, 100 | Baixo | Testes 4.3 existentes |
| B5. Limitar o tamanho/ordem da citação (≤ N caracteres, **iniciar pelo trecho que contém o valor**), pedir candidatas literais como evidência | prompt | val-097, 032, 045, 047 | Baixo | Reprodução offline com `saida_bruta` salva |

### C. Verificador
| Proposta | Arquivo/função | Problema | Risco | Teste |
|---|---|---|---|---|
| C1. Base de comparação = **texto integral do(s) chunk(s) citado(s) + candidata literal + chunks vizinhos do mesmo documento**, mantendo "o valor tem de existir no documento" | `validar_saida`, `afirmacoes_nao_sustentadas` | val-097, 106, 031 | Baixo/médio: pode aceitar número de outra parte do mesmo doc; mitigar exigindo proximidade | Replay dos 18 reprovados: devem passar 097, 106, 031 e **continuar reprovados 062, 108, 126** |
| C2. Isentar números/anos presentes na **pergunta** também em `validar_saida` (já é feito na outra regra) | `validar_saida` | val-031 | Baixo | val-031 |
| C3. Normalizar datas: `dd/mm/aaaa` → mês; intervalos "no período de X a Y" extraídos do documento e comparados com o da pergunta, **por evidência** | `evidencias.periodo_ausente`, `alinhamento` | val-106, val-050 | Médio (formatos de data) | Casos val-050 (devem ser barrados itens do doc 196), val-106 |
| C4. Localidade e entidade **por evidência**: se a citação contém uma localidade conflitante e não contém a pedida → rejeitar | `alinhamento` (nova função `localidade_conflitante`) | val-130 | Médio | val-130 (esperado reprovado), val-017 (Asa Sul, esperado ok) |
| C5. Siglas e morfologia: dicionário de siglas **do corpus** (CRSSU, PNIDPD, HRT...) e radical para nomes; `nome=` só reprova se **nenhum** sinônimo/radical estiver no documento inteiro | `evidencias.alinhamento` | val-087, val-141 | Médio | val-087, val-141 devem passar; val-149 (Ceilândia só no decreto) deve continuar reprovado |
| C6. Citação literal **não é prova suficiente**: acrescentar checagem "a evidência responde ao atributo pedido" (período, localidade, entidade, tipo de item) | `_aplicar_politica` | 8 incorretas | Médio/alto (falsos bloqueios) | Medir **antes** quantas corretas hoje seriam bloqueadas (7 corretas e 16 parciais) |
| C7. Tolerância de `trecho_literal` a pontuação/hífen e "emendas" explícitas | `geracao.trecho_literal` | val-047 (e 032/045 só com cuidado) | Baixo | Testes com fabricação (val-062 deve continuar reprovado) |

### D. Classificação
| Proposta | Arquivo/função | Problema | Risco | Teste |
|---|---|---|---|---|
| D1. `fora_do_escopo` só se o tema não aparece no corpus (ex.: nenhum termo de conteúdo da pergunta tem cobertura no catálogo); caso contrário `insuficiente` ou `ambigua` | `geracao` (pós-modelo), `catalogo` | 10 casos | Baixo (só rótulo) | Casos val-019, 046, 060, 074, 119 → `insuficiente`; assuntos realmente fora (a criar em desenvolvimento) continuam `fora_do_escopo` |
| D2. Permitir `parcial` quando houver ≥1 evidência alinhada (período, localidade, entidade) e a pergunta for lista, com aviso de cobertura | `_aplicar_politica`, `evidencias.aviso_cobertura` | 6 casos abertos + parte dos 14 do bloco 5 | Médio | Casos val-033, 044, 058, 061, 063, 083 |
| D3. Preservar `ambigua` diante de conflito real: manter a rotina de valores diferentes (53 casos corretos) e só "desambiguar" se a resposta for equivalente por valor/documento | `classificar_divergencia` | — | — | Os 53 casos da auditoria devem continuar `ambigua` |

## 7. Estratégia de avaliação da 4.4

**Situação do conjunto de 350 (verificada, sem baixar nada):**
- `MANIFESTO.json`: `qa/test-00000-of-00001.parquet` "não baixado... reservado para avaliação final". Os docs 01 e 02 confirmam: nunca baixado nem usado. **Não está disponível localmente**; baixá-lo exige autorização (e deve ser feito uma vez, com hash registrado).
- **Independência:** mesma fonte (`gvic-unb/dodf-saude-qa`, mesma revisão), **mesmo corpus de 1.381 publicações**, mesmo processo de geração do gabarito. As decisões das etapas 4–4.3 foram tomadas olhando padrões de erro da validação, que compartilham modelos de pergunta e documentos com o teste (na validação, 175 documentos-gabarito distintos; 46 deles usados por mais de uma pergunta; os 5 tipos de documento mais frequentes concentram 88% das perguntas; os modelos "qual é o valor... / quem foi o responsável pela autorização..." se repetem). É provável que o teste tenha os mesmos modelos de pergunta, hospitais e documentos: **não é independente em desenho, só em amostra**.
- **Qualidade do gabarito (evidência nesta auditoria):** 53 de 150 perguntas (35%) não têm resposta única no corpus; 21 de 36 perguntas MULTI têm associação frouxa/indeterminada; gabaritos com erros de local (val-024) e de documentos esperados (val-007, 100, 149). Usar "acerto contra gabarito" como métrica final penaliza a abstenção correta e premia a resposta errada.

**Recomendação:** **não usar o teste de 350 como avaliação final sem antes qualificá-lo** (baixar uma vez, registrar hash, medir ambiguidade e erros de associação por amostra auditada, **sem rodar o sistema**). Se a qualificação mostrar a mesma taxa de ambiguidade, a métrica final deve ser por **auditoria independente com rótulo próprio**, não por gabarito.

**Divisão proposta (nenhum caso é reutilizado entre ajuste e medição):**
| Conjunto | Origem | Uso | Observação |
|---|---|---|---|
| **Desenvolvimento** | As 150 da validação (já "queimadas": viram regressão fixa) + os 8 incorretos e 56 indevidos como casos de teste | Corrigir bugs, testes unitários, ajuste de regras | Qualquer métrica aqui é diagnóstica; não reportar como desempenho |
| **Validação 4.4** | ~120 perguntas do teste de 350 (amostra estratificada por tipo, ambiguidade e localidade), **qualificadas antes** e acessadas só por métricas agregadas | Decidir entre alternativas e limiares | Congelar o conjunto antes (hash); proibir leitura caso a caso pelo desenvolvedor |
| **Teste final** | As ~230 restantes + 100 a 200 perguntas reais de cidadãos (coleta gov.br) com rótulo humano | **Uma única** execução da versão congelada | Auditoria humana independente, com dupla anotação em amostra para medir concordância |

Métricas obrigatórias: precisão das respostas dadas, **taxa de resposta incorreta**, abstenção indevida e correta, ambiguidade preservada, cobertura (respostas úteis / total), e por grupo (A/B corrigido pelo replay, MULTI, lista/singular). Nunca reportar só acurácia contra gabarito.

## 8. Recomendação final

**Fazer primeiro (ordem):**
1. **Corrigir a medição:** `enviado` e grupos A/B por replay de `montar_contexto` (sem LLM); registrar hashes de todos os artefatos; tirar a escrita em `data_assistente/` da rotina de conferência. Custo baixo; evita decisões com dados errados.
2. **Verificador, falsos positivos (C1, C2, C3 parcial, C5):** corrige 8 abstenções indevidas sem abrir porta para fabricação (val-062/108/126 continuam bloqueados).
3. **Verificador, falsos negativos (C3 período por evidência, C4 localidade por evidência):** corrige val-050 e val-130, que são erros que hoje chegam ao usuário. É a mudança que mais reduz risco de resposta incorreta.
4. **Reclassificar `fora_do_escopo` (D1):** só rótulo; zero risco de nova resposta incorreta.
5. **Gerador: B1/B3 (atributo ausente → `insuficiente`; ausência só com contexto completo):** corrige val-136 e val-039.
6. **Filtro de identificabilidade (A3/D3):** só com testes que preservem os 53 casos ambíguos.

**Não implementar agora (sem evidência suficiente):**
- **Limiar de score BM25** como critério de abstenção: os scores do primeiro resultado de corretas e incorretas se sobrepõem.
- **Juiz LLM de adequação** (C6 completo): não há avaliação de sua taxa de falso bloqueio; começar com regras determinísticas verificáveis.
- **Mudar retriever/índices, modo híbrido ou reconstruir chunks:** os ganhos esperados vêm do desenho de consulta e de cabeçalho; só reavaliar depois das correções acima, em desenvolvimento.
- **Aumentar o contexto/orçamento de tokens** (4 casos de falta de contexto): há risco de memória (a rodada chegou a 45 MB livres) e latência.
- **Relaxar a abstenção por ambiguidade em geral:** os 53 casos mostram que ela protege o usuário.
- **Responder mais por padrão em perguntas abertas** sem o aviso de cobertura e sem teste de "não afirmar ausência".
- **Usar o conjunto de 350 antes de qualificar o gabarito.**

## 9. Limitações

- Diagnóstico feito por modelo; atribuição de documentos "que respondem" na seção 4 vem do levantamento do auditor, não é verdade absoluta (27 julgamentos com confiança baixa).
- As causas dos 14 casos de "geração/modelo" não foram investigadas uma a uma (sem `saida_bruta` analisada); são hipótese.
- Sem execução do modelo, não foi possível testar o efeito das correções propostas.
- Integridade do arquivo de exemplos: parcial (seção 5).

## 10. Arquivos gerados

`RELATORIO_DIAGNOSTICO_4_4.md`, `causas_56_abstencoes_indevidas.csv`, `causas_abstencoes_indevidas.json`, `replay_contexto.json`, `scripts/causas.py`, `scripts/causas2.py`, `scripts/replay_contexto.py`.
