# Modelo relacional experimental — Fase 4D.5

Protótipo **offline, determinístico, sem modelo**, em `prototipo_vinculo_4d5.py`. Não integrado ao pipeline. Usa de `evidencias.py` só funções puras de leitura (`_fold1`, `termos_de_uso`, `tokens_de_uso`, `cue_de_atributo`, `FAM_ROTULO`, `COMPATIVEL`, `_radical`); nada foi alterado.

## 1. Objetos
| Objeto | Representação |
|---|---|
| Publicação | texto completo do documento + chunks conhecidos (somente os que entraram no contexto do modelo; o resto é "fora do contexto enviado") |
| Chunk | trecho da publicação; as unidades herdam a lista de chunks que as contêm |
| Unidade (frase) | segmento por `.`/`;` com guarda de abreviaturas, itens de lista (`4 - `, `IV - `), registros `RATIFICO …` e `, CNPJ …`; guarda posição, chunks, texto |
| Pergunta / resposta | texto; a resposta é dividida em **afirmações atômicas** (cláusulas: `;`, `, incluindo/inclusive/bem como/resultando/sendo`) |
| Afirmação | cláusula + **termos de atributo** (`termos_de_uso(cláusula, pergunta)` menos as palavras da entidade) |
| Entidade | `{nome, formas, tipo (organização|localidade), parciais}`; as **entidades concorrentes** (`outras_entidades`) são informadas por quem monta o caso (inventário manual, não descoberto) |
| Atributo | família (`COMPETENCIA`, `OBJETO`, …) usada para checar o rótulo/cue da unidade |
| Origem da evidência | citação (spans do modelo) → unidades citadas; depois frase vizinha, mesmo chunk, mesma publicação, outra publicação |
| Relação | estado por nível (abaixo) + diagnóstico (unidade, motivo) |
| Confiança | **não estimada** pelo protótipo (ver limitações); o campo existe só nos rótulos de referência |

## 2. Estados de relação (por afirmação × entidade)
1. **Coocorrência**: a entidade e o atributo estão na mesma frase, mas sem relação (fronteira de cláusula, discurso reportado, >12 palavras, ou sem termo).
2. **Relação explícita** (N1): mesma frase, mesma cláusula (parênteses de apelido e abreviaturas não quebram; vírgula só antes de `inclusive/incluindo/bem como/e/ou/para/a quem/cujo/onde`), 1–12 palavras entre a entidade e o termo mais próximo, nenhuma outra entidade concorrente mais perto do atributo, unidade sem rótulo de família incompatível (sem `cue`), e menção que não seja só parte do nome de outra entidade (verificação de papel **apenas para localidades**: `…do Gama` precedido de nome próprio capitalizado, como "Conselhos de Saúde do Gama", é `parte_de_outra_entidade`).
3. **Frases adjacentes** (N2): a unidade com o atributo é vizinha (±1, mesmo chunk) da unidade com a entidade **e** há vínculo textual: anáfora ("A unidade", "O órgão", "Ela"…) resolvida só se a unidade anterior mais próxima com entidade contém exclusivamente a entidade avaliada; ou continuação ("Para tanto", "Além disso"); ou introdução por `:`. Adjacência sem vínculo é só proximidade.
4. **Anafórica ambígua**: o referente mais próximo é outra entidade ou há mais de uma → não vincula.
5. **Entre chunks** (N3, ingênuo): qualquer menção no(s) chunk(s) das unidades citadas, independentemente de papel/relação. Existe para medir falsos vínculos por proximidade.
6. **Entre publicações**: menção em outra publicação é registrada (`em_outra_publicacao`) e **nunca** aceita.
7. **Herdada da pergunta**: a entidade não consta de nenhuma unidade da publicação citada (estado `ausente` em todos os níveis).
8. **Contraditória/outro atributo**: unidade com a entidade e rótulo de família incompatível sem `cue` (`outro_atributo`), ou outra entidade mais próxima do atributo (`outra_entidade`).
9. **Mesma publicação** (N4, ingênuo): qualquer menção na publicação; sub-estado `sujeito_da_publicacao` quando a menção está na primeira unidade e nenhuma entidade concorrente informada aparece no documento.

## 3. Estratégias avaliadas
| Nível | Aceita o vínculo quando |
|---|---|
| N1 mesma frase | N1 = `explicita` |
| N2 frases adjacentes | N1 `explicita` ou N2 `adjacente_com_vinculo` |
| N3 mesmo chunk | qualquer menção no chunk das unidades citadas (ingênuo) |
| N4 mesma publicação | qualquer menção na publicação (ingênuo) |
Nenhum nível é tratado como correto; todos são comparados com os rótulos congelados.

## 4. Heurísticas e limitações do modelo
Regras lexicais (listas de conectores, anáforas, abreviaturas), não análise sintática: não resolve sujeito/objeto, não trata pronome oblíquo, nem referência por ordem ("a primeira"). O inventário de entidades concorrentes é manual. Termos numéricos podem casar fora da relação (ex.: "400" em "R$ 20.400,00"). O segmentador foi dimensionado com os documentos destes casos e **não** foi validado em outros textos do corpus.
