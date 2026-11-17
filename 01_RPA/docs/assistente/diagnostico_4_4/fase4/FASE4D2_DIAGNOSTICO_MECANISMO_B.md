# Fase 4D.2 — Diagnóstico do mecanismo B (somente investigação)

**Natureza:** investigação técnica baseada nos artefatos e no código do próprio projeto; **não é uma auditoria independente**. Nenhum código, teste, fixture, prompt, índice, corpus, JSONL, manifesto, hash de referência ou snapshot foi alterado; nenhuma geração, LM Studio ou API. Scripts de análise ficaram em diretório temporário da sessão (fora do projeto). Convenção de rótulos: **[Fato]** observado nos artefatos/código; **[Execução]** resultado de rodar funções existentes sem persistir mudanças; **[Interpretação]**; **[Hipótese]**; **[Recomendação]**.

## 1. Resumo executivo

- [Fato] `val-087-A-r1` escapa do bloqueio porque, em `_relacoes_44`, o trecho conflitante C2 (`4 - Titular: Diretor do HRG…`, agora reconhecido como `titular`/MEMBRO) só é *necessário* se **algum termo de uso da resposta tiver todos os seus apoios em trechos conflitantes**. Os termos de uso de r1 são todos apoiados também por C1 (item IX, sem rótulo conhecido); o único elemento da resposta que depende de C2 é a palavra **"Gama"** ("…internação hospitalar no Gama"), mas "Gama" está na pergunta e é **removida de `termos_de_uso`** (`evidencias.py:948`, `t in q`). Em r2/r3 a resposta traz **"HRG"**, que não está na pergunta e só existe em C2 → C2 passa a ser necessária → bloqueio.
- [Fato] A mesma premissa — "o que veio da pergunta não precisa de sustentação" — aparece em **três** pontos independentes: `termos_de_uso` (`evidencias.py:944–948`), `afirmacoes_nao_sustentadas` (`evidencias.py:193`, `n not in q`) e `alinhamento` (`evidencias.py:136–142`, que aceita o nome se estiver em qualquer chunk citado ou na publicação). Nenhum deles exige que **o span citado** sustente a localização "no Gama".
- [Execução] Replicação sintética do padrão de r1 (E3) e uma variante com atributo compatível (E6) reproduzem a liberação. Duas variantes diagnósticas da exclusão (B1: nomes salientes passam a contar; B2: nada da pergunta é excluído) bloqueiam r1 e **não alteram nenhuma outra decisão** nos 150 e nos 21 — mas isso é pouco informativo: nos 150 só **1** caso tem rótulo conflitante (o próprio val-087).
- [Interpretação] B1/B2 não distinguem *eco da pergunta* de *afirmação nova de localização* (E6 vs E3 ficam iguais); a evidência histórica não mede o risco de falso bloqueio. Rótulos como base de "evidência positiva" têm cobertura baixíssima (28 de 30 respostas entregues não têm nenhum rótulo compatível).
- [Recomendação] Não corrigir ainda; antes, construir casos de teste de conflito de rótulo (hoje há 1) e decidir qual princípio (B, C ou D) adotar. Detalhes nos §9–§12.

## 2. Integridade dos artefatos

`verificar_hashes.py` → **TODOS CONFEREM: True** (sem reparar nem atualizar hashes). SHA-256 (16 primeiros caracteres):

| Artefato | Hash |
|---|---|
| `citizentech/assistente/geracao.py` = `data_assistente/versoes/geracao_44_fase4d1.py` | `c857b99f49947e1a` |
| `citizentech/assistente/evidencias.py` = `…/evidencias_44_fase4d1.py` | `12118192b9529075` |
| `citizentech/assistente/catalogo.py` (= `catalogo_44_fase4d1_pre.py`) | `8e44143ba1d092f5` |
| `geracao_44_fase4d1_pre.py` / `evidencias_44_fase4d1_pre.py` (= 4B-cand) | `46862831592d09fc` / `742031bb9934a3d9` |
| `validacao_seletiva_20261116-155046.jsonl` | `cbb8482916d55050` |
| `validacao_seletiva_retomada_20261116-161042.jsonl` | `c198f0893d40121f` |
| `protocolo_validacao_manifestos.json` | `43fb09685404714c` |
| `FASE4D1_NORMALIZACAO_ROTULOS.md` (relatório de referência) | `388ea4f094bae2d0` |

Implementação investigada: **`fail-closed-4.4.4d1-cand`** (arquivos vivos idênticos ao snapshot `*_44_fase4d1.py`; `cmp` sem diferença). Caminhos: `D:\Downloads\GS\RPA\citizentech\assistente\{geracao,evidencias,catalogo}.py`, `D:\Downloads\GS\RPA\data_assistente\versoes\*_44_fase4d1*.py`, `D:\Downloads\GS\RPA\docs\assistente\diagnostico_4_4\fase4\`.

## 3. Referência de código do mecanismo B

| Etapa | Arquivo:linhas | Função |
|---|---|---|
| Termos de uso da resposta | `evidencias.py:941–951` | `termos_de_uso`: descarta palavras funcionais (`PALAVRAS_FUNCIONAIS`, 927–929), genéricas (`GENERICAS`, 14), tokens da pergunta (`q`, 944) e flexões por radical de 6 letras (945, 948) |
| Tokenização | `evidencias.py:930–938` | `tokens_de_uso` (sem acento/caixa; números só dígitos) |
| Apoio por unidade | `evidencias.py:954–965` | `suporte_por_unidade`: unidade apoia o termo por token exato ou radical (6 letras); sem termo apoiado ⇒ `nao_mensuravel` |
| Agrupamento de spans | `evidencias.py:904–921` | `grupos_de_trechos`: candidata literal + citação sobrepostas no chunk = 1 unidade |
| Montagem das unidades | `geracao.py:589–602` | `_relacoes_44` |
| Rótulo e estado | `geracao.py:608–610`; `evidencias.py:569–588` (`rotulo_do_valor`), `590+` (`conflito_atributo_rotulo`) | `desconhecido` se rótulo ausente/família desconhecida; `conflito` só com famílias conhecidas incompatíveis |
| Causa do conflito | `geracao.py:615–621` | `rotulo` só se `estado==conflito` **e** sem `cue` de competência no próprio span |
| Necessidade | `geracao.py:627–630, 639–640` | `necessaria_para`: `nao_mensuravel` ⇒ `True`; senão `any(gid in us and all(causa in unit_causas[v] for v in us) for us in suporte.values())` |
| Bloqueio | `geracao.py:668–673` | bloqueia se necessária e mecanismo ligado |
| Alinhamento (Fase 2) | `evidencias.py:115–158`; `geracao.py:811–813` | nomes salientes da pergunta devem aparecer em **qualquer** chunk citado ou na publicação |
| Sustentação de afirmações | `evidencias.py:161–200`; `geracao.py:808–810` | nomes/números da resposta devem estar nos trechos citados **ou na pergunta** (linha 193) |

## 4. Rastreamento de `val-087-A-r1` (item a item)

1. **Pergunta:** "Quais são as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?" — atributo `competencias` (família COMPETENCIA); nomes salientes: coordenacao, regulacao, sul, gama.
2. **Resposta bruta (r1):** "A Coordenação de Regulação da Região de Saúde Sul tem competência para nortear as gerências de regulação, incluindo a implementação das normas e protocolos de regulação de internação hospitalar no Gama." (status do modelo `parcial`).
3. **Chunks enviados** (hash de contexto `ec5eaddd50…`, condição A): C1 = `dodf-174:0004` (itens VIII–XI), C2 = `dodf-174:0001` (lista de membros 2–11), C3 = `dodf-174:0000` (preâmbulo, Art. 1º e 2º).
4. **Citações:** C1 "As Deliberações deverão nortear as respectivas gerências de regulação…" (item IX); **C2 `4 - Titular: Diretor do Hospital Regional do Gama, da Diretoria do Hospital Regional do Gama (HRG);`** (literal no chunk); C3 "Art. 1º Instituir a Coordenação de Regulação da Região de Saúde Sul (CRSSU)…".
5. **`rotulo_do_valor` na citação C2:** antes da 4D.1 (`*_fase4d1_pre`): `None`; depois: `{rotulo: titular, familia: MEMBRO}`.
6. **Tokens da pergunta (q):** quais, sao, as, competencias, da, coordenacao, de, regulacao, regiao, saude, sul, em, relacao, aos, servicos, do, gama.
7. **Termos da resposta e descartes:** descartados por funcional: a, de, da, tem, para, as, das, e, no; por **pergunta**: coordenacao, regulacao, sul, **gama**; genéricos: regiao, saude; radical da pergunta: competencia.
8. **Termos de uso (B):** nortear, gerencias, incluindo, implementacao, normas, protocolos, internacao, hospitalar.
9. **Suporte por unidade:** nortear, gerencias, implementacao, normas, protocolos, internacao → só `C1#0`; `hospitalar` → `C1#0` e `C2#0` ([Fato] C2 "apoia" `hospitalar` só por coincidência de radical de 6 letras com "Hospital"). **Nenhum termo tem C2 como único apoio.** `incluindo` não é apoiado por nenhuma unidade (fora de `suporte`).
10. **Estados:** C1 `desconhecido`; **C2 `conflito`, causa `rotulo`, `necessaria=False`, `bloqueia=False`**; C3 `desconhecido`. `medida_de_uso = termos_apoiados`.
11. **Condição exata do escape:** `necessaria_para('rotulo', C2#0)` = `any(C2#0 ∈ us ∧ ∀v∈us: 'rotulo'∈causas(v))`. Para `hospitalar`, `us = {C1#0, C2#0}` e C1 não tem causa ⇒ falso; nos demais termos C2 nem pertence a `us` ⇒ falso. O único elemento da resposta que só C2 sustenta é "Gama", que `termos_de_uso` removeu (linha 948) **antes** de `suporte_por_unidade` ser chamada (geracao.py:601). Logo, a perda acontece na **entrada** de B, não no cálculo de necessidade.
12. **Decisão final:** `parcial` (pergunta de lista: `eh_lista` ⇒ `completude: lista_nao_exaustiva`) com aviso de cobertura; nenhum problema. `alinhamento` passou porque "gama" existe nos chunks citados (C1 item XI "Conselhos de Saúde do Gama", C2) e `afirmacoes_nao_sustentadas` passou porque "Gama" é da pergunta e consta no span de C2.

Distinções: **evidência citada** = C1, C2, C3. **Evidência que sustenta semanticamente** o conteúdo central ("nortear gerências… protocolos de internação hospitalar") = C1 (item IX, que trata de GIR e GEREG, e fala em "Região de Saúde Sul", não "Gama"). **Termos herdados da pergunta** = coordenação, regulação, sul, gama, competência. **Termos usados por B** = os oito do item 8. **Trechos que B considera necessários** = C1 (candidata e citação); C2 e C3 não. A localização "no Gama" não é sustentada por nenhum span como competência (só C2 menciona o Gama, como sede de um membro). [Interpretação] o ganho de r1 para o usuário é uma frase com localização não demonstrada.

## 5. Comparação A-r1, A-r2, A-r3 [Execução, a partir dos registros gravados]

| Dimensão | A-r1 | A-r2 | A-r3 |
|---|---|---|---|
| Resposta | "…nortear as gerências… implementação das normas e protocolos de regulação de internação hospitalar **no Gama**." | "…nortear as gerências… implementação de normas e protocolos de internação hospitalar **no Hospital Regional do Gama (HRG)**." | idem r2 |
| Citações | C1 (IX), C2 `4 - Titular…`, C3 (Art. 1º) | C1 (IX), C2 `Titular: Diretor do HRG…` | idem r2 |
| Termos só da pergunta | coordenacao, regulacao, sul, **gama**, competencia | coordenacao, regulacao, sul, gama, competencia | idem |
| Termos de uso | nortear, gerencias, incluindo, implementacao, normas, protocolos, internacao, hospitalar | os mesmos **+ `hrg`** (e `hospital`/`regional` são genéricos) | idem r2 |
| Rótulo reconhecido (4D.1) | C2: `titular`/MEMBRO | C2: `titular`/MEMBRO | idem |
| Trecho conflitante | C2 | C2 | C2 |
| Termo que o apoia só nele | **nenhum** ("gama" excluído) | **`hrg`** (só C2) | `hrg` |
| `necessaria` de C2 | **False** | **True** | **True** |
| Mecanismo B | não bloqueia | bloqueia | bloqueia |
| Decisão final | `parcial` (entregue, incorreta segundo a auditoria 4C) | `insuficiente` (`rotulo_incompativel_com_atributo`) | idem |

**Diferença lógica:** em r2/r3 existe um termo da resposta **fora da pergunta** (`hrg`) cujo único apoio é a unidade conflitante; em r1 o equivalente semântico ("no Gama" ≈ HRG) é um termo **da pergunta**. A diferença não é superficial: o conteúdo conflitante é o mesmo, mas a *forma lexical* de referi-lo decide o resultado.

## 6. Lógica atual do mecanismo B

- **Extração de termos (`evidencias.py:941–951`):** tokens da resposta menos funcionais, genéricos e tudo o que aparece na pergunta (por token ou radical de 6 letras). [Fato] a exclusão cobre **todos** os tokens da pergunta, não só entidades.
- **Apoio (954–965):** o termo é apoiado por unidades cujo texto (citação + candidata sobreposta) contém o token ou o radical de 6 letras. [Fato] o radical gera apoios espúrios (`hospitalar`↔`Hospital`).
- **Necessidade (627–630):** necessária ⇔ existe termo cujos apoios são todos unidades com a mesma causa de conflito; `nao_mensuravel` ⇒ tudo necessário.
- **Conflito de rótulo (609–621):** só com rótulo de família conhecida incompatível com a do atributo e sem `cue` de competência no próprio span.
- **Resposta só com termos genéricos/funcionais ou curta (E1/E2):** nenhum termo apoiado ⇒ `nao_mensuravel` ⇒ conflitante bloqueia (fail-closed).
- **Entidade só na pergunta:** excluída de B; se nenhum chunk citado a contém, o `alinhamento` bloqueia (`nome=gama`) antes de B (S1, S7, E4).
- **Entidade na pergunta e no trecho:** excluída de B igualmente (S2, S4, S8); a presença no trecho só importa ao `alinhamento`.
- **Trecho conflitante e resposta que não repete o rótulo:** irrelevante para B; o rótulo só entra no estado/causa do trecho.
- **Evidência positiva em outro trecho:** unidades sem causa não entram no cálculo; se o termo é apoiado também por unidade sem causa, a unidade conflitante deixa de ser necessária (S8).
- **Testes existentes** (`test_fase4a.py`, `test_fase4b.py`) cobrem A1/A2/B1/B2, T1–T6; nenhum cobre "termo da pergunta apoiado só pelo trecho conflitante". [Interpretação] o fato de os testes passarem não demonstra que a regra é correta nesse ponto.

## 7. Matriz sintética [Execução; **diagnóstica, não representa dados reais**]

Pergunta de referência: "Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do **Gama**?" (a variante "sem Gama" em S3). Chunks sintéticos com cabeçalho da Coordenação; "Compatível" = trecho com "IV - Compete à CRSSU…" (a regra reconhece `compete` só por cue, `estado=desconhecido`); "Conflitante" = `Titular:` (MEMBRO). *Avaliação* é minha, separada da saída do código.

| # | Cenário (pergunta / trecho / rótulo / resposta usa entidade) | Termos de uso | Descartados (principais) | Necessários | Decisão do código | Avaliação (separada) |
|---|---|---|---|---|---|---|
| S1 | Sim / Não / conflitante / Sim | abrange | gama (pergunta) | — | `insuficiente` por `alinhamento` (`nome=gama`), B não chega a atuar | correto: o trecho não sustenta nada |
| S2 | Sim / Sim / conflitante / Sim (só o conflitante citado) | abrange | gama | todos (`nao_mensuravel`) | `insuficiente` (rótulo) | correto (membros ≠ competência) |
| S3 | **Não** / Sim / conflitante / Sim | abrange, **gama** | — | C1 (exclusivo `gama`) | `insuficiente` (rótulo) | correto |
| S4 | Sim / Sim / compatível / Sim | discutir, deliberar | gama, compete, regulados | C1 | `parcial` (entregue) | correto |
| S5 | Sim / Sim / conflitante / **Não** (cita competência + membros) | crssu, discutir, deliberar, direcao | — | C1; C2 **não** | `parcial` | correto (conflito citado e não usado) |
| S6 | Sim / Sim / conflitante **com competência explícita** / Sim | diretor, hrg, deliberar | gama, compete | C1 (`causas=[]`) | `parcial` | inconclusivo: o span afirma competência do Diretor, não da Coordenação |
| S7 | Sim / Não / **sem rótulo** / Sim | deliberacoes, norteiam, gerencias | gama, regulacao | — | `insuficiente` por `alinhamento` | correto |
| S8 | Sim / Sim em **outro** trecho / um conflitante + um compatível / Sim | discutir, deliberar | gama | C1; C2 **não** | `parcial` | correto (tudo sustentado pelo compatível) |
| E1 | resposta curta "Sim." + conflitante | — | sim (funcional) | todos | `insuficiente` (fail-closed) | conservador; inconclusivo |
| E2 | resposta genérica (só palavras da pergunta) + neutro + conflitante | existem | quase tudo | conflitante necessário | `insuficiente` | conservador; resposta sem conteúdo |
| **E3** | entidade só na citação conflitante; atributo do neutro; resposta usa a entidade (**padrão r1**) | nortear, gerencias, implementar, normas, protocolos | gama | C1; C2 **não** | **`parcial` (entregue)** | **liberação duvidosa**: "no Gama" não é sustentado pelo trecho de competência; [Interpretação] provável liberação indevida |
| E4 | entidade só na pergunta (nenhuma citação a contém) | idem E3 | gama | — | `insuficiente` por `alinhamento` | correto |
| E5 | atributo no compatível + termo exclusivo do conflitante (HRG) | discutir, deliberar, **hrg** | compete, regulados | C1; **C2** | `insuficiente` (rótulo) | correto (HRG vem do trecho de membros) |
| **E6** | atributo no compatível + entidade só no conflitante (variante com atributo compatível) | discutir, deliberar | gama | C1; C2 **não** | **`parcial`** | inconclusivo/provavelmente aceitável: o conteúdo central é sustentado e "no Gama" ecoa a pergunta |
| E7 | dois conflitos de rótulo (sem "Gama" nos chunks) | gerencias, seguem, normas, gersu, nov, participam | regulacao | — | `insuficiente` por `alinhamento` | cenário **não isola B** (limitação) |
| E7b | dois conflitos de rótulo, ambos com "Gama" no chunk, resposta usa termos dos dois | gerencias, normas, gersu, ouv… | — | C2 (`gersu`) e C3 (`ouv`) | `insuficiente` (ambos `bloqueia`) | correto |
| E7c | dois conflitos, resposta usa termo de **um** | gerencias, normas, gersu, participa | — | C2; C3 **não** | `insuficiente` (por C2) | correto |

Sensibilidade às variantes diagnósticas da exclusão (monkeypatch em memória, nenhum arquivo alterado): **B1** (nomes salientes contam) e **B2** (nada da pergunta é excluído) mudam apenas **E3** e **E6**, que passam de `parcial` para `insuficiente`; S1–S8, E1, E2, E4, E5, E7 permanecem iguais. [Interpretação] B1/B2 tratam do mesmo modo o padrão problemático (E3) e o caso provavelmente legítimo (E6); não há como distinguir "eco da pergunta" de "localização nova" por léxico.

## 8. Impacto nos 150 casos históricos [Execução; offline; os 150 participaram do desenvolvimento — não generalizam]

Replay com saídas brutas gravadas (versão `4d1-cand`, 0 diferenças contra 4A):

| Categoria | N | IDs / observação |
|---|---:|---|
| Respostas entregues (`respondida`/`parcial`) | 30 | classe 4.3: 7 Correta, 16 Correta-parcial, 3 Incorreta, 4 Abstenção indevida |
| Casos que chegam à análise de relações (M2/B) | 35 | val-000, 002, 003, 006, 007, 012, 013, 017, 020, 021, 024, 031, 032, 041, 044, 047, 049, 050, 059, 066, 070, 083, 087, 090, 091, 099, 100, 102, 111, 114, 118, 130, 131 … |
| Relações de citação: `desconhecido` / `compativel` / `conflito` | 69 / 2 / 1 | **96 % sem rótulo conhecido** |
| Citações com **rótulo conflitante** | **1** | **val-087** (único) |
| Conflitos com causa (qualquer tipo) | 3 | val-083 (destinatário), val-087 (rótulo), val-149 (localidade da publicação) |
| Respostas que repetem termo da pergunta (não funcional/genérico) | 136 | 30 de 30 entre as entregues |
| Respostas que repetem **nome saliente** da pergunta | 114 | 25 de 30 entre as entregues |
| **Potencial escape** (conflito não bloqueante + termo herdado só no trecho conflitante) | **0** | critério: ver abaixo |
| Conflito com compatível citado no mesmo caso | 0 | — |
| Conflito real *entre* trechos distintos | não verificável | só 1 conflito de rótulo na base |

Critérios: "herdado" = token da resposta, não funcional/genérico, presente na pergunta (token ou radical de 6 letras); "potencial escape" = relação com causa de conflito, `bloqueia=False`, e termo herdado usado na resposta que ocorre no span conflitante e em nenhum span sem conflito.

Simulações (monkeypatch em memória de `termos_de_uso`, replay offline):

| Variante | Mudanças nos 150 | Mudanças nos 21 da validação | Resposta correta bloqueada? | Incorreta que passou a ser entregue? |
|---|---:|---|---|---|
| B1 — nomes salientes contam | 0 | `val-087-A-r1` → `insuficiente` (`rotulo_incompativel_com_atributo`) | nenhuma | nenhuma |
| B2 — nada da pergunta excluído | 0 | idem | nenhuma | nenhuma |

**Limitações [importantes]:** (1) só **1** de 150 casos tem rótulo conflitante; a ausência de falsos bloqueios nas simulações mostra **insensibilidade**, não segurança; o risco de falso bloqueio das alternativas B é **não verificável** com estes dados. (2) A categoria "potencial escape = 0" vale só para a definição acima. (3) A exposição da alternativa D por rótulo: **28 de 30** entregues não têm nenhum rótulo compatível (6 Correta, 15 Correta-parcial, 3 Incorreta, 4 Abstenção indevida) — exigir rótulo compatível bloquearia quase tudo, inclusive respostas corretas. (4) Nenhuma regra nova foi criada para produzir os números; categorias sem evidência estão marcadas como não verificáveis.

Exemplos representativos: **val-087** (único conflito de rótulo na rodada 4.3; bloqueado por outra causa na época); **val-083** e **val-149** (conflitos de destinatário/localidade — outros mecanismos, não afetados pela exclusão de termos da pergunta).

## 9. Alternativas (sem implementação)

| | A — manter exclusão | B — entidade/nome da pergunta como termo de uso | C — vínculo entidade–atributo–trecho | D — evidência positiva do atributo |
|---|---|---|---|---|
| Princípio | o que está na pergunta não revela qual trecho foi usado | tornar o trecho que traz a entidade "necessário" | verificar que o atributo pedido e a entidade estão ligados **no mesmo span** | exigir cue/rótulo compatível em pelo menos um span citado |
| Benefício | evita falsos bloqueios por eco da pergunta (S4/S8/E6) | bloqueia r1 e E3 | trata a causa: "no Gama" não é sustentado pelo span de competência | bloqueia respostas sustentadas só por spans sem relação com o atributo |
| Risco | mantém r1/E3 | não separa eco de localização nova (E6 também bloqueia); depende da forma lexical | exige extração/associação robustas (relações entre entidade, atributo e valor) | rótulo é raro (96 % `desconhecido`); cue de competência cobre pouco |
| Falsos positivos (bloqueios indevidos) esperados | baixos | possíveis em respostas que ecoam a pergunta (E6) | possíveis se a entidade está só no título/cabeçalho | **altos** se baseada em rótulo (28/30 entregues sem rótulo compatível) |
| Falsos negativos (liberações indevidas) | r1/E3 persistem | caem para os casos com entidade só no trecho conflitante | menos, se bem extraído | menos, no limite |
| Complexidade | nenhuma | baixa (alterar a lista de exclusão) | alta | média/alta |
| Testes necessários | E3 vs E6 documentando o limite | pares E3/E6, eco vs localização, respostas curtas, listas | cenários com entidade no cabeçalho, em outro registro, em tabela | casos corretos sem rótulo; medir recall nos 23 corretos/parciais da 4.3 |
| Impacto histórico mensurável | nenhum (baseline) | 0 mudanças nos 150; 1 nos 21 (r1) — **insensível** | não mensurável | exposição de 28/30 entregues (por rótulo) — inviável por rótulo |

Nenhuma alternativa é recomendada com base só em val-087; os números acima mostram apenas o que é e o que não é mensurável.

## 10. Limitações

- Base histórica com **um** conflito de rótulo; cenários sintéticos são diagnósticos, não evidência de comportamento em dados reais.
- A matriz usa uma pergunta/entidade; E7 não isolou B (o `alinhamento` interveio), tratado em E7b/E7c.
- `termos_de_uso` e `suporte_por_unidade` usam radical de 6 letras (apoios espúrios, ex.: hospitalar/Hospital); não medi o alcance desse efeito.
- Avaliação de correção dos cenários é minha e não foi revista por terceiros.
- Simulações B1/B2 por monkeypatch em memória; não há implementação testada.

## 11. Recomendação técnica

1. [Recomendação] Não alterar a regra ainda. O defeito é real, reproduzível (r1, E3, E6) e localizado na **entrada** de B (exclusão de termos da pergunta) combinada com a isenção equivalente em `afirmacoes_nao_sustentadas` e `alinhamento`.
2. [Recomendação] Antes de escolher B, C ou D, construir um conjunto de **casos de conflito de rótulo** (hoje há 1 em 150): listas de membros/titulares, itens com índice, entidades só na pergunta, ecos legítimos (E6) — para medir falsos bloqueios.
3. [Recomendação] Tratar B1 como a opção de menor custo a investigar, **com** testes que separem E3 de E6 e uma decisão explícita sobre o aceite de bloquear ecos; C como solução de princípio, de custo maior; D baseada em rótulo é inviável (rótulo ausente em 96 %).
4. [Hipótese] Parte do risco poderia ser reduzida exigindo que o termo da pergunta usado na resposta tenha apoio em span **sem** conflito (não só presença no chunk), mas isso depende da distinção entre eco e afirmação, não testada aqui.

## 12. Decisões que dependem de autorização

1. Implementar qualquer correção em `termos_de_uso`, `_relacoes_44`, `alinhamento` ou `afirmacoes_nao_sustentadas`.
2. Construir/rotular novos casos de teste de conflito de rótulo e, se necessário, ampliar a base de validação.
3. Definir se bloquear ecos da pergunta (E6) é aceitável em troca de bloquear E3/r1.
4. Qualquer nova rodada com modelo.

Nenhuma geração foi executada; nenhum código alterado; hashes conferem.
