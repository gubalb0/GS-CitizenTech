# Avaliação da S1 conservadora (Fase 4B) — análise e simulação offline

Sem modelo, LM Studio, API ou geração; flag `priorizar_atributo` desligada; implementação do pacote **não alterada** (`geracao.py` `0891e70c…`, `evidencias.py` `93363fab…`, iguais ao snapshot 4B-prep; `verificar_hashes.py` → TODOS CONFEREM). O protótipo vive fora do pacote, em `fase4/s1_conservadora_proto.py`, com a simulação em `avaliacao_s1_conservadora.py/.json` e os testes em `test_s1_conservadora_proto.py`. `fail-closed-4.4.4a` e `4.4.4b-prep` preservados.

## 1. Hipótese e como distinguir as situações

Hipótese: só promover o chunk de rótulo explícito se nenhum chunk **já selecionado** cobrir o atributo para a entidade da pergunta.

| Situação | Mecanismo disponível | Confiável? |
|---|---|---|
| Atributo já sustentado, **com rótulo** em posição de rótulo | `rotulo_forte_no_chunk` + nomes da entidade **no próprio chunk** | Sim |
| Atributo já sustentado, **sem rótulo**, em prosa | Só para a família **VALOR**, que tem forma tipada verificável (`R$ n`) com os nomes da entidade no chunk | Sim, para valor |
| Atributo já sustentado em prosa nas demais famílias (endereço, objeto, competência…) | Não existe forma tipada confiável | **Não** — sem verificação, não declaro cobertura |
| Atributo ausente do contexto | Nenhum selecionado satisfaz os dois itens acima | Sim (ausência de cobertura *reconhecível*) |
| Atributo mencionado incidentalmente | Palavra fora de posição de rótulo não conta; `R$` sem a entidade no chunk não conta | Parcial: um `R$` incidental no chunk da própria entidade (ex.: multa) seria contado como cobertura |
| Atributo de outra entidade | Exige todos os nomes salientes da pergunta no chunk (mais estrito que o S1, que aceita a publicação) | Parcial: nomes salientes parecidos entre entidades homônimas passam |

**Limitação central:** a regra decide *cobertura reconhecível*, não *cobertura semântica*. Ela não verifica que o `R$` ou o rótulo respondem à pergunta, nem resolve conflito entre valores; só evita trocar um chunk que já tem o tipo de dado por outro igual. Em famílias sem forma tipada, a ausência do rótulo é lida como "não coberto" (o risco é promover redundante, nunca esconder cobertura — direção conservadora quanto a *contexto*, não quanto a respostas).

## 2. Os seis casos

| Caso | Contexto original | S1 atual | Cobertura nos selecionados | Candidato | Variante conservadora |
|---|---|---|---|---|---|
| val-011 (endereço) | 1611, 856, **859** | 1438, 1611, 856 (sai 859) | 859: rótulo `ENDEREÇO:` + Gama | 1438: mesmo termo (reedição), mesmo endereço | **não promove** (contexto original) |
| val-074 (objeto) | 338:16, 1722:24, 442:15 | 28:0, 338, 1722 (sai 442) | nenhuma: só "cujo objeto é a aquisição do item…" em prosa (incidental, outros itens) | 28:0 `Objeto: FORNECIMENTO … ALIMENTAÇÃO HOSPITALAR…` | **promove** (= S1 atual) |
| val-080 (valor) | 479, 1487, 1289, 1390 | 407, 479, 1487, 1289 (sai 1390) | 479 (R$ em errata), 1289 e 1390 (`Valor:`), todos da entidade | 407 `Valor: R$127.547,08` (doc do gabarito, processo 04001-00001199/2025-18) | **não promove** |
| val-087 (competências) | 174:4, :1, :0 | 174:2, :3, :4 | nenhuma (listas de membros, instituição) | 174:3 "IV – Compete à CRSSU discutir e deliberar…" + 174:2 "Art. 4° Competência e Disposições" | **promove** (= S1 atual) |
| val-125 (valor) | 1203, 655, 812, 938 | 945, 1203, 655, 812 (sai 938) | 1203, 655, 812, 938: `R$` em prosa, Hospital Santa Marta | 945 `Valor: R$413.596,67` | **não promove** |
| val-133 (valor) | 944, 1067, 734, 1109 | 1516, 944, 1067, 734 (sai 1109) | 944, 734, 1109: `Valor:` + Lago Sul | 1516 `Valor: R$323.859,26` | **não promove** |

Critérios específicos:
- **val-011:** o endereço já está representado (859). Evitado. ✔
- **val-125:** o valor em prosa é reconhecido como evidência (`valor_tipado`) nos quatro chunks. Evitado. ✔
- **val-133:** há outros dois chunks equivalentes com o mesmo atributo e entidade. Evitado. ✔
- **val-087:** nenhum selecionado cobre competência; a promoção da frase explícita é preservada. ✔
- **val-074:** a mudança B→A é **ganho real de cobertura**: os três selecionados originais só têm o termo "objeto" incidental, em listas de aquisições de itens; o chunk 28 traz o objeto (fornecimento de alimentação hospitalar) do contrato pedido, e o doc 28 está no gabarito.
- **val-080:** a mudança B→A é **ganho de gabarito, não de cobertura de atributo**. O contexto original já tinha três registros de valor da mesma entidade (e uma errata); o 407 é um quarto registro do mesmo tipo, que por acaso é o do gabarito. Nenhuma regra baseada em estrutura distingue o 407 dos demais sem conhecer o gabarito; a conservadora o perde de propósito. Observação: o 407 e o 1390 compartilham o processo 04001-00001199/2025-18, e o 479 é uma errata ("ONDE SE LÊ R$127.547,08, LEIA-SE R$125.582,46") — a pergunta tem várias respostas candidatas e é inerentemente ambígua.

## 3. Testes sintéticos (8, passando)

| Cenário | Esperado | Resultado |
|---|---|---|
| 1 sem evidência do atributo + candidato com rótulo | promove | ✔ |
| 2 evidência equivalente em prosa (`no valor de R$…`), sem rótulo | não promove (cobertura `valor_tipado`) | ✔ |
| 3 rótulo `Valor:` mas de **outra entidade** | não conta como cobertura; promove | ✔ |
| 4 atributo incidental ("competência do plenário… compete a outro órgão") | não conta; promove | ✔ |
| 5 duas evidências equivalentes já no contexto | não promove | ✔ |
| 6 evidência conflitante (R$ 1,00 × R$ 500,00, mesma entidade) | não promove; o **conflito não é resolvido** pela seleção | ✔ (limitação registrada) |
| unitário: rótulo sem entidade; família sem forma tipada; `R$` fora da família VALOR | não cobre | ✔ |
| flag padrão desligada | `False` | ✔ |

Os testes mostram que presença de rótulo ≠ cobertura (cenários 3 e unitário) e que cobertura ≠ rótulo (cenário 2).

## 4. Simulação nos 150 (baseline 4A × S1 atual × S1 conservadora)

| | Baseline 4A | S1 atual | S1 conservadora |
|---|---|---|---|
| Contextos alterados | — | 6 (011, 074, 080, 087, 125, 133) | **2 (074, 087)** |
| Promoções redundantes evitadas | — | — | 4 (011, 080, 125, 133) |
| Casos com cobertura nova de atributo | — | 074, 087 (+ 080 só por gabarito) | **074, 087** |
| Orçamento máximo (tokens) | 2.998 | 2.998 | 2.998 (sem estouro, ≤ 3.000) |
| Respostas entregues na 4.3 afetadas | — | 0 | 0 |
| Diferenças da conservadora fora dos 6 | — | — | nenhuma |
| Grupos A/B | — | 074 B→A, 080 B→A | 074 B→A (080 permanece B) |

Tokens por caso (baseline / atual / conservadora): 011 2886/2882/2886; 074 2916/2985/2985; 080 2716/2712/2716; 087 2948/2928/2928; 125 2790/2741/2790; 133 2801/2802/2801. Os 144 demais contextos ficam idênticos à baseline.

## 5. Limitações

- A cobertura é *reconhecível por estrutura*, só com rótulo ou, para VALOR, `R$`. Nas outras famílias (endereço, objeto, competência em prosa) uma cobertura sem rótulo não é detectada; nesse caso a regra pode promover redundância (é o comportamento do S1 atual, não pior).
- `R$` em chunk da entidade que não seja o valor pedido (multa, valor global × valor autorizado) conta como cobertura.
- Não resolve conflito entre evidências nem escolhe entre candidatas equivalentes (val-080).
- Comprovação apenas de **contexto**; efeito nas respostas não medido (sem modelo). Só 150 perguntas e 6 casos tocados: pouca base para generalizar.
- O protótipo reutiliza `rotulo_forte_no_chunk`, que aceita só rótulos que repetem o atributo; é preciso manter essa restrição.

## 6. Recomendação

1. A variante conservadora é **implementável e testável** e elimina as 4 promoções redundantes, mantendo os dois ganhos com evidência direta (val-087, val-074). Recomendo adotá-la **em vez** do S1 atual, caso a S1 seja ativada.
2. Perde-se, de propósito, o ganho de gabarito de val-080 (B→A), que não decorre de cobertura de atributo e não pode ser justificado sem conhecer o gabarito. Se o responsável preferir recuperá-lo, só seria possível com uma regra que escolhesse entre registros equivalentes (por exemplo, data/ordem), o que **não há evidência para propor**.
3. Para integrar: mover `cobertura_do_chunk` para `evidencias.py`, aplicá-la em `montar_contexto` antes de promover, registrar em `Contexto.selecao` o motivo "promoção redundante evitada" e portar os 8 testes para a suíte do pacote. Isso exige autorização explícita (a implementação não foi tocada).
4. Antes de qualquer regeneração, a mudança prevista seria apenas val-074 e val-087 (contexto), sem efeito sobre respostas entregues na 4.3.

Confirmação: nenhuma geração; sem LM Studio/API; flag desligada; implementação, corpus, índices, gabaritos, RPA congelado e snapshots intactos.
