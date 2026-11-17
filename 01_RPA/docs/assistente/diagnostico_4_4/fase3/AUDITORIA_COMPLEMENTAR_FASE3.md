# Auditoria complementar da Fase 3 — Gen AI `fail-closed-4.4.3`

Etapa **somente diagnóstica**: nenhuma correção, nenhuma alteração do pipeline, nenhuma geração com o modelo, Fase 4 não iniciada. Auditor: modelo de linguagem (não é revisão humana). **Fato** = lido nos documentos/saídas gravadas ou reproduzido offline; **hipótese** = inferência não comprovada.
Método: replay offline (saídas brutas da rodada 4.3 + recuperação BM25 + `montar_contexto`), buscas no corpus e execuções sintéticas do código atual. Arquivos auxiliares (só em `fase3/`): `auditoria_complementar_coleta.py`, `auditoria_complementar_dados.json`, `auditoria_complementar_cenarios_087.py/.json`.

## 1. Integridade e preservação

| Verificação | Resultado |
|---|---|
| `scripts/verificar_hashes.py` (RPA congelado via `modelo_congelado.json`, rodadas, auditorias, snapshots da 4.3/Fase 2/Fase 3, `chunking.py`, `chunks_exemplos.json`) | **todos conferem** (antes e depois da auditoria) |
| `geracao.py`, `evidencias.py`, `catalogo.py` vivos x `*_44_fase3.py` | idênticos (`cmp`) |
| `*_44_fase2.py` x `*_44_fase2_final.py` | idênticos entre si (estado da Fase 2 preservado) |
| Snapshots da 4.3 (`*_43_pre_execucao.py`, `avaliacao_e2e_etapa4_3.py`) | no manifesto, conferem |
| `chunks_exemplos.json` | SHA-256 `8c9d583a…2f37` (inalterado) |
| Código/testes/corpus/índices/gabaritos/rodadas/relatórios | não alterados; esta etapa só criou os arquivos auxiliares acima em `fase3/` |
Observação: para comparar recuperação lexical e híbrida carreguei o codificador e5 (leitura; sem LLM, sem gravar índice). Nenhuma divergência de integridade foi encontrada.

## 2. Diagnóstico individual dos quatro erros restantes

Em todos: recuperação e contexto reproduzidos exatamente (BM25 est300o30, 5 recuperados, 3 enviados), citações `literal`, Fase 3 sem efeito (nenhum mecanismo decidiu).

### val-007 — "Quais serviços de saúde estão sendo implementados em Riacho Fundo II?"
1. **Recuperados:** doc 1236 (Resolução CSDF, eleição do Conselho Regional de Saúde RFII) pos. 1–2; doc 1449 (Ata do CDM-DF) pos. 3; doc 303 pos. 4–5 (não enviados). **Enviados:** C1 1236 (Art. 12, composição), C2 1236 (Art. 16, eleição), C3 1449 (Ata).
2. **Saída bruta:** lista conselho + eleições + "Hospital da Mulher"; quotes literais dos três.
3. **Fase 2:** aceita (nomes `riacho`/`fundo` presentes nos chunks). **Fase 3:** M2 `servicos`→OBJETO, valores sem rótulo (`desconhecido`); M1/M3/M4/M5 não se aplicam. Entregue como `parcial`.
4. **Fato:** o doc 1449 só tem "Riacho Fundo II" como local da reunião; o "Hospital da Mulher" é o de São Paulo. Nenhum dos três trechos descreve serviço de saúde sendo implementado em RFII.
5. **Documentos relevantes** (auditoria anterior): Portaria Conjunta 12/2025 (docs 571 e 591: UBS Tipo II e base do SAMU em RFII) e Aviso 005/2025 (doc 1413). **Posição:** BM25 591→14, 571→21, 1413→83; híbrido 571→6, 591→12, 1413→24. **Nenhum entra no top-5 em nenhum dos dois modos.**
6. **Gabarito do dataset:** cita 571/591, mas a associação lista 5 docs (3 sem relação: 474, 488, 621).
- **Causa principal (confirmada):** o BM25 prioriza documentos que repetem "Riacho Fundo II"/"implementados" (governança do conselho) e os documentos relevantes ficam fora do top-5.
- **Secundárias (confirmadas):** o trecho C3 é atribuído ao local errado; o atributo (serviços de saúde) não é sustentado por nenhum trecho (composição de conselho e eleição são governança); o verificador (Fase 2) une trechos de publicações diferentes numa lista sem ligar cada trecho ao atributo. **Hipótese:** pergunta vaga ("serviços ... implementados") favorece geração genérica.
- **Categorias:** recuperação encontrou-mas-não-priorizou; evidência atribuída ao local errado; atributo incorreto; resposta genérica; erro de geração; falha do verificador; limitação do gabarito.

### val-012 — "Quais equipamentos médicos foram adquiridos para o Hospital Regional de Ceilândia?"
1. **Recuperados:** 238 (pos. 1), 560 (2), 807 (3), 956, 1455. **Enviados:** C1 238, C2 560, C3 807.
2. **Saída:** "álcool etílico absoluto 99,5GL e o serviço de manutenção corretiva em macas".
3. **Fase 2:** aceita. **Fase 3:** `equipamentos` não tem família (M2 `desconhecido`).
4. **Fato:** só C1 (doc 238) é do HRC. C2 (560) é reparo de processador de tecidos do Hospital Regional de **Taguatinga**; C3 (807) é compra do IGESDF para HBDF/HRSM. Os itens de C1 são um insumo (Código SES **numérico** 95046) e um **serviço** de manutenção.
5. **Equipamentos do HRC existem:** doc 1346 (mesa de necropsia, Código SES **P**42003), 958 (lavadora ultrassônica, **P**08301), 1680 (balança antropométrica, **P**08002171). **Posição:** BM25 1346→7, 1680→10, 958→24; híbrido 1680→16, 1346→18, 958→28. BM25 empata 238 e 560 em 16,77: o termo "equipamentos médicos" casa **nomes de empresas** ("DS MEDICAL ... EQUIPAMENTOS MÉDICOS HOSPITALARES").
- **Causa principal (confirmada):** recuperação encontrou mas não priorizou (equipamentos reais estão nas posições 7–28, só 3 chunks cabem no contexto). **Secundárias (confirmadas):** o gerador tratou qualquer item como "equipamento"; o verificador não tem noção de tipo de item. **Hipótese (com indício):** o código SES com prefixo **P** marca bem permanente. Amostra no corpus: 488 itens com código P (ar-condicionado, armário, cadeira, instrumental) x 2.937 com código numérico (medicamentos, material de consumo), 14+14 amostrados sem exceção; não validado exaustivamente.
- **Categorias:** não priorizou; atributo incorreto (tipo de item); erro de interpretação; falha do verificador; gabarito (aponta um único doc, 1680, para pergunta plural).

### val-100 — "Quais aquisições de equipamentos hospitalares foram realizadas para o Hospital Regional de Ceilândia?"
1. **Recuperados:** 440 (pos. 1), 1035 (2), 322 (3), 434, 238. **Enviados:** C1 440, C2 1035 (Ata de comitê de drogas), C3 322 (decisão do TCDF).
2. **Saída:** "serviço na máquina de hemodiálise (R$ 1.254,67) e serviço na osmose reversa (R$ 2.724,32)".
3. **Fase 2:** aceita. **Fase 3:** nenhum mecanismo (rótulos desconhecidos).
4. **Fato:** o doc 440 diz "cujo objeto é o **serviço** na MÁQUINA DE HEMODIALISE", adjudicado a "SH BIOMEDICA **SERVICOS DE MANUTENCAO EM EQUIPAMENTOS HOSPITALARES** LTDA": o termo da pergunta casa o **nome da empresa de manutenção**. O doc diz serviço, não aquisição de equipamento; o modelo reformulou como "aquisições".
5. **Relevantes:** 1346→9 (BM25)/19 (híbrido), 958→59/15, 1680→38/50. **Gabarito:** as 5 publicações esperadas (1413, 1418, 1453, 1460, 1478) tratam de outro assunto.
- **Causa principal (confirmada):** colisão lexical + equipamentos reais fora do top-5. **Secundárias (confirmadas):** reformulação de "serviço" como "aquisição" (erro de geração); sem verificação de tipo; gabarito incorreto. 
- **Categorias:** não priorizou; atributo incorreto; erro de geração; falha do verificador; limitação do gabarito.

### val-149 — "Quais ações de atenção básica e primária em saúde serão executadas em Ceilândia durante 2025?"
1. **Recuperados:** 1365 (pos. 1 e 4), 1611 (2), 1052 (3), 1008 (5). **Enviados:** C1 1365 (alteração de grade de equipamentos), C2 1611 (texto sobre o INAS), C3 1052 (decreto de cargos).
2. **Saída:** "programas de promoção da saúde, prevenção de doenças, atenção primária... A Gerência de Serviços de Atenção Primária nº 07 da Ceilândia também está envolvida".
3. **Fase 2:** aceita (Ceilândia e 2025 presentes em algum chunk citado). **Fase 3:** nenhum mecanismo.
4. **Fato:** C2 (doc 1611) **não menciona Ceilândia**; a lista genérica vem do estatuto do INAS ("poderá desenvolver programas..."). C3 é um decreto que cria o cargo de gerente da Gerência nº 07 da Ceilândia (não é execução de ação). C1 é uma grade de equipamentos.
5. **Evidência parcial real no corpus:** doc 1154 (manutenção em UBS 11 de Ceilândia, "Atenção Primária da Região Oeste"), grade do doc 1365 (UBS de Ceilândia). **Gabarito:** Plano Anual de Publicidade (campanha), BM25 99→46 e híbrido 99→88; 87 não recuperado.
- **Causa principal (confirmada):** geração genérica sobre evidências sem relação com o atributo, aceita por um verificador que valida **a união** dos chunks citados. **Secundárias:** pergunta vaga e prospectiva ("serão executadas") (hipótese); gabarito e corpus não trazem uma publicação que responda diretamente (limitação, não provada ausência).
- **Categorias:** resposta genérica; evidência de outra entidade/local (C2); erro de interpretação (hipótese); falha do verificador; limitação do corpus/gabarito.

## 3. val-087 em profundidade

**Fatos.** Todos os 5 chunks recuperados são do doc 174 (Ordem de Serviço 396/2022, que institui a CRSSU), em ordem: ord.4 (pos. 1), ord.1 (2), ord.0 (3), ord.2 (4), ord.3 (5). Foram enviados só os três primeiros.
- C1 (ord.4) é o Art. 4º, item IX: "As Deliberações deverão nortear as respectivas gerências de regulação..." (efeito das deliberações; não é a competência em si).
- C2 (ord.1) é a lista de membros do Art. 2º ("Titular: Diretor do Hospital Regional do Gama (HRG)...").
- A competência real, "**IV – Compete à CRSSU discutir e deliberar sobre a direção, avaliação, monitoramento, organização, funcionamento e aperfeiçoamento dos serviços regulados na Região de Saúde Sul...**", está no chunk ord.3, **recuperado em 5º e não enviado** por orçamento (confirmado no índice).
- O modelo juntou C1 (nortear as gerências) com C2 (membros) e concluiu "competência ... no Hospital Regional do Gama". O "HRG" só tem apoio na lista de membros (que não diz competência). Esse é o nexo que a Fase 3 barrou.

**A relação rótulo–entidade é real?** A lista de membros pertence à própria CRSSU (Art. 2º: "membros para compor a CRSSU"). Portanto a associação **existe no documento**, mas foi **estabelecida por mim**, não pelo sistema: o registro `relacoes` grava `entidade = ['coordenacao','regulacao','sul','gama']` (os nomes da **pergunta**, inclusive uma localidade), não a entidade do registro do trecho. Também: valor truncado em 90 caracteres, sem identificador do registro nem posição no chunk, e trecho de competência explícita (candidata de C1 e a frase "Compete à CRSSU") sai como `desconhecido` porque a candidata não começa com "rótulo:". Origem (`candidata_literal`/`citacao`) e `chunk_id` estão corretos. **Conclusão:** o registro prova o conflito, mas **não prova a associação com a entidade perguntada**.

**Cenários (código atual, entrada sintética, sem LLM; `auditoria_complementar_cenarios_087.json`):**
| Cenário | Entrada | Resultado atual | Esperado | Veredicto |
|---|---|---|---|---|
| **A1** — `titular` existe na publicação; resposta usa só o trecho de competência | chunk com "IV – Compete à CRSSU..." + lista "Titular:" | `parcial` | entregue | **OK** (rótulo não citado não bloqueia) |
| **A2** — resposta cita também um trecho "Titular:" de **outra entidade** (outro comitê), sem usá-lo em nenhum termo | competência da CRSSU + "Titular: Maria da Silva (Comitê da Região Norte)" | **insuficiente** (`rotulo_incompativel_com_atributo`) | entregue | **FALHA**: bloqueio por rótulo independente de outra entidade |
| **B1** — resposta usa a lista de membros da própria entidade como competência (val-087) | "A Coordenação tem competência no HRG" sustentado só por "Titular: Diretor do HRG" | insuficiente | bloqueado | **OK** |
| **B2** — só há lista de membros da entidade | | insuficiente | bloqueado | **OK** |
| **C** — o trecho abre com "Titular:" mas contém "a quem compete deliberar sobre os serviços do Gama" | | **insuficiente** | entregue (a competência está no trecho) | **FALHA**: rótulo por prefixo ignora o conteúdo |
**Conclusão sobre o bloqueio de val-087:** correto para a *evidência efetivamente usada* (associação de membro a competência), mas a regra é grossa: (i) bloqueia a resposta inteira quando **qualquer** trecho citado tem rótulo conflitante, mesmo que nenhum termo da resposta dependa dele (A2); (ii) olha só o prefixo do trecho (C); (iii) não verifica a qual entidade o trecho pertence. O resultado desejável para val-087 não era bloquear, e sim **`insuficiente` por contexto sem a frase de competência** ou `parcial` com o item IV (o chunk existia no top-5).
**Propostas de teste (não implementadas):** manter A1, B1, B2; transformar A2 e C em testes que **devem passar a entregar**: A2 (bloqueio só se o trecho conflitante for o **único apoio** de ≥1 termo específico da resposta E pertencer ao registro da entidade perguntada) e C (rótulo reconhecido também no conteúdo: "compete", "a quem compete"). Teste adicional D: mesma entidade, lista de membros e competência em seções diferentes, resposta usando ambas apenas para termos distintos → bloquear só o termo apoiado pelo trecho de membros. Teste de registro: `relacoes` deve conter `entidade_do_registro`, `registro` (início/fim no chunk), `termos_suportados` e valor sem truncamento.

## 4. Matriz de qualidade (classificação desta auditoria; não pelo status)

| Caso | Status Fase 2 | Aud. anterior | Fase 3 | Classificação desta auditoria | O que realmente mudou |
|---|---|---|---|---|---|
| val-007 | parcial | Incorreta | parcial | **Incorreta** | nada |
| val-012 | parcial | Incorreta | parcial | **Incorreta** | nada |
| val-100 | parcial | Incorreta | parcial | **Incorreta** | nada |
| val-149 | parcial | Incorreta | parcial | **Incorreta (genérica)** | nada |
| val-039 | parcial | Incorreta | insuficiente | **Abstenção indevida** (a informação existe em chunks não enviados) | erro eliminado; sem ganho informativo |
| val-050 | parcial | Incorreta | insuficiente | **Abstenção indevida** (o midazolam, no período, era resposta parcial correta) | erro eliminado; perdeu 1 item correto |
| val-130 | parcial | Incorreta | insuficiente | **Abstenção indevida** (Visão Hospital de Olhos, Asa Sul, era item correto) | erro eliminado; perdeu 1 item correto |
| val-136 | parcial | Incorreta | insuficiente + mensagem de remissão | **Abstenção correta** (informa a verdade: especialidades constam da carta SEI 160711978, não publicada) | **melhoria real** |
| val-087 | parcial | (não auditado) | insuficiente | **Abstenção indevida** (competência existe, em chunk não enviado) | resposta parcialmente sustentada → abstenção |
| val-141 | parcial | (não auditado) | insuficiente | **Abstenção defensável** (hipótese: ausência não comprovável com 3 de 28 trechos) | negativa não afirmada |
| val-047 | parcial | (4.3: abstenção) | parcial reescrito | **Parcialmente sustentada** (linha de candidato aprovado ≠ "programa disponível", mas sem exclusividade) | texto menos conclusivo |
| val-031, val-032 | parcial | (4.3: abstenção) | parcial | **Correta, mas parcial** (justificados no diagnóstico) | — |
| val-044 | parcial | (4.3: abstenção) | parcial | **Parcialmente sustentada** (objeto genérico do edital como "serviços") | — |
| val-083 | parcial | (4.3: abstenção) | parcial | **Parcialmente sustentada, com erro de entidade**: o trecho que sustenta o cloreto de sódio diz "para atender as necessidades do **Hospital Regional do Guará**", não da Atenção Primária; vitamina D e lençol dizem "Atenção Primária" | **problema não visto antes; a Fase 3 não o cobre** |

**A Fase 3 corrigiu os erros identificados?** Dos 8 incorretos: 1 virou informação correta (val-136), 3 viraram abstenções seguras que descartam informação correta ou disponível (039, 050, 130), **4 permanecem errados**. A melhoria é de **segurança** (menos respostas incorretas entregues: 8→4 entre as 31 originais), não de **utilidade**. O estado de 23 respostas boas (7 + 16) se manteve. As 5 respostas que passaram a `parcial` na Fase 2 e não foram auditadas antes têm qualidade mista (2 corretas-parciais, 2 parcialmente sustentadas, 1 com erro de entidade).

## 5. Causas confirmadas x hipóteses

| Causa | Casos | Situação |
|---|---|---|
| Documentos relevantes fora do top-5 em **BM25 e híbrido** (posições 6–88) | 007, 012, 100 | **Confirmada**. Não indica por si que mudar BM25/RRF resolveria: nenhum modo os traz ao top-5 |
| Colisão lexical com nomes de empresas ("equipamentos hospitalares/médicos") | 012, 100 | **Confirmada** (texto dos docs 440, 560) |
| Chunk com a competência recuperado, mas não enviado (orçamento) | 087 (+063, 074, 086, 147 do diagnóstico anterior) | **Confirmada** |
| Verificador valida a **união** dos trechos citados (não cada trecho x entidade/local/atributo) | 007, 149, 083 | **Confirmada** (origens do alinhamento = `chunk_citado` de outro trecho) |
| Tipo de item (equipamento x serviço x consumível) sem verificação | 012, 100 | **Confirmada** como lacuna; o sinal "Código SES P" é **hipótese** (amostra) |
| Rótulo conflitante de outra entidade bloqueia indevidamente | (sintético A2, C) | **Confirmada em teste sintético**; frequência real: 1 caso (087) nas 150, 0 falsos bloqueios conhecidos |
| Pergunta vaga/prospectiva favorece resposta genérica | 007, 149 | **Hipótese** |
| Corpus sem publicação que responda diretamente | 149 | **Hipótese** (há evidências parciais em 1154/1365) |
| Gabarito inadequado | 007, 100, 149 (e 012 incompleto) | **Confirmada** |

## 6. Intervenções possíveis, priorizadas

| # | Intervenção | Evidência | Arquivo/função | Risco | Teste sem o modelo | Comparabilidade |
|---|---|---|---|---|---|---|
| 1 | **Verificador por uso e por registro**: bloquear conflito de rótulo só se o trecho for apoio único de um termo específico e pertencer ao registro da entidade; reconhecer "compete"/"a quem compete" no conteúdo; vincular **cada** trecho à entidade/local/destinatário perguntado (HR Guará x Atenção Primária) e gravar entidade/registro/termos nas `relacoes` | A2, C, val-083, val-007 (C3), val-149 (C2), registro incompleto | `evidencias.rotulo_do_valor`, `conflito_atributo_rotulo`, `_protecao_resposta` (M2), `classificar_niveis` | Médio: pode liberar respostas hoje bloqueadas (087) e bloquear outras; cobertura baixa já observada | testes sintéticos A1/A2/B1/B2/C/D + replay das 150 comparando com a Fase 3 | `PROTECOES_44` permite replay lado a lado |
| 2 | **Montagem de contexto guiada pelo atributo, dentro do top-5**: priorizar, entre os 5 chunks já recuperados, o que contém o rótulo/família do atributo antes do orçamento | 087 (chunk 3 era o 5º) + 4 casos "recuperado não enviado" | `geracao.montar_contexto` | Médio/alto: muda o contexto de todas as perguntas; sem aumentar tokens | Seleção determinística testável offline (quais chunks entram); **o efeito nas respostas não é testável sem o modelo** | Quebra a comparabilidade de contexto com a 4.3; exigiria rodada nova autorizada |
| 3 | **Tipo de item (equipamento)** por estrutura do próprio corpus (Código SES P x numérico; "aquisição do item" x "serviço") | 012, 100; 488 x 2.937 itens | nova função em `evidencias.py` + M2 | Médio; vale só para extratos de dispensa SES; **precisa validar** a hipótese em amostra maior antes | auditoria offline do corpus (precisão do sinal) + testes sintéticos | independente do modelo |
| 4 | Política para respostas genéricas (007, 149) | 2 casos; sem sinal confiável sem semântica | `_protecao_resposta` | Alto risco de bloquear respostas boas | — | **Sem evidência suficiente para propor regra** |
| 5 | **Mudança no retriever (BM25, embeddings, RRF)** | relevantes em 7–88 nos dois modos; nenhum teste mostrou ganho | `retriever.py` | Alto (congelado) | — | **Não recomendada** |
| 6 | Documentar limites do corpus/gabarito | 007, 100, 149 | relatórios | Nenhum | — | — |

## 7. Riscos e limitações desta auditoria
- Julgamento de modelo, sem dupla revisão humana; casos 031, 032, 044, 047 e 083 avaliados por mim pela primeira vez.
- Cenários A2/C são **sintéticos**: mostram o comportamento do código, não a frequência real.
- A hipótese do código SES "P" vem de amostra de 28 itens e de um regex; não é validação.
- Os resultados de recuperação híbrida usaram o codificador e5 local (leitura), uma única configuração.
- Replay usa as saídas do modelo da 4.3; nova geração mudaria as saídas.
- As 150 perguntas já serviram para projetar as fases; nada aqui estima generalização.

## 8. Recomendação sobre a Fase 4

- **Retrieval: não há evidência para alterar BM25, embeddings ou RRF.** Os documentos relevantes ficam fora do top-5 em ambos os modos e, mesmo que subissem, o orçamento deixa passar só 3 chunks.
- **Prioridade 1 — verificação (escopo definido):** vínculo de cada evidência com a entidade/local/destinatário perguntado, conflito de rótulo "por uso" (corrigir A2 e C) e registro completo das relações. Há evidência direta (val-083, 007, 149, 087 e os cenários) e é testável sem o modelo.
- **Prioridade 2 — montagem de contexto:** há evidência (087 e quatro casos "recuperado e não enviado"), mas **só pode ser avaliada com nova geração**; deve ser etapa separada e autorizada, com comparabilidade explícita.
- **Prioridade 3 — tipo de item (equipamentos):** validar primeiro o sinal estrutural do corpus; só então implementar.
- **Geração/política contra respostas genéricas:** ainda **sem evidência suficiente** para decidir; documentar.
- Registrar, independentemente da Fase 4, as limitações de gabarito (val-007, 100, 149) e que val-083 contém um erro de entidade não detectado.
