# Políticas de veto — definições (Fase 4D.6, experimentais; não integradas)

Tudo é simulação offline sobre as saídas da 4D.5 (`resultados_4d5_detalhe.json`), por `simular_veto_4d6.py` (versão única, sem reajustes). Rótulos da 4D.5 intactos. Nenhuma regra de produção foi criada.

## 1. Categorias da relação entidade–atributo (derivadas pelo script, em ordem de prioridade)
| Categoria | Critério derivado (não vem dos rótulos) |
|---|---|
| `conflitante` | N1 = `outra_entidade`/`outro_atributo` **ou** a unidade que sustenta o atributo cita outra entidade do inventário e não a avaliada (componente b) |
| `citada` | N1 = `explicita` (relação na mesma frase do trecho citado) |
| `complementar` | N2 = `adjacente_com_vinculo` (anáfora/introdução) |
| `nao_relacionada` | N1 = `coocorrencia` **ou** N2 = `adjacente_sem_vinculo` — evidência *positiva* de mera proximidade; **ausência em N1/N2 não entra aqui** |
| `documental` | só no nível amplo, e (i) há relação explícita em outra unidade **não citada** da mesma publicação, ou (ii) a menção está na primeira unidade da publicação sem entidade concorrente informada (`sujeito_da_publicacao`) |
| `nao_verificavel` | aceito só pelo nível amplo, sem relação demonstrada (ou resposta sem conteúdo novo) |
| `sem_vinculo_amplo` | nenhuma menção na publicação (informação herdada da pergunta); nada a vetar |
`documental` nunca é convertido em `citada`; ausência em N1/N2 nunca é convertida em `nao_relacionada`.

## 2. Componentes de contradição
- **(a)** N1 = `outra_entidade` (outra entidade do inventário mais perto do atributo) ou `outro_atributo` (rótulo de família incompatível, sem `cue`).
- **(b)** a unidade do atributo cita outra entidade do inventário e não a avaliada (ex.: registro cujo destinatário é outro).
- **(c)** identidade: todas as menções do nível amplo têm papel `parte_de_outra_entidade` (ex.: "Conselhos de Saúde do **Gama**"). Vale só para localidades; depende da heurística de papel.
O inventário de entidades concorrentes é **manual** (informado por quem montou o caso); (a) e (b) só disparam para concorrentes listados.

## 3. Políticas (decisão ∈ ACEITA | REJEITA | ENCAMINHA), com base N3 (mesmo chunk) ou N4 (mesma publicação)
| Política | Regra |
|---|---|
| V0 sem veto | ACEITA se o nível amplo acha menção; senão REJEITA |
| V1 veto por contradição explícita | REJEITA se o nível amplo aceita **e** (a) ou (b) ou (c); ausência em N1/N2 não veta |
| V2 veto por ausência | ACEITA só se N1 explícita ou N2 adjacente com vínculo (controle excessivamente conservador; = N2 da 4D.5) |
| V3 veto condicionado | REJEITA se (a) ou (b) (evidência positiva de outra entidade/atributo; sem (c)); `citada`/`complementar` → ACEITA; `documental` → **ENCAMINHA** (nem aceita nem rejeita, vai a julgamento humano); demais casos do nível amplo mantêm V0 |
`ENCAMINHA` conta como "preservada", nunca como "aceita".

## 4. Medidas (separadas para sintéticos e reais; sem precisão/recall)
Falsos vínculos aceitos (esperado `nao_sustentado_*` e decisão ACEITA), negativos encaminhados, legítimas aceitas/encaminhadas/rejeitadas (esperado `sustentado`), documentais preservadas/rejeitadas (esperado `sustentado_documental`), conflitantes rejeitadas (esperado `outra_entidade`/`outro_atributo`), ambíguos e não verificáveis (distribuição das decisões). Não se calcula precisão/recall: a rotulagem é do mesmo autor, sem segundo avaliador, e os conjuntos são pequenos (27 alvos sintéticos; 7 reais).
