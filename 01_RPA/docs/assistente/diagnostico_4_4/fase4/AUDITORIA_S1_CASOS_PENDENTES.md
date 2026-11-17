# Auditoria complementar — S1 forte: casos val-011, val-125 e val-133

Somente leitura: nenhum código, teste, corpus, índice, snapshot ou resultado foi alterado; nenhuma geração, LM Studio ou rodada end-to-end. A flag `priorizar_atributo` continua desligada. Fonte: ranking BM25 (k=5) + `montar_contexto` com a flag desligada (contexto anterior) e ligada (novo), comparados com o gabarito (`esperado`) e o texto completo dos chunks.

## Resumo

| Caso | Atributo | Gabarito no contexto antes / depois | Saiu → entrou | Classificação |
|---|---|---|---|---|
| val-011 | endereço | ausente / ausente (doc 1329 nem foi recuperado) | doc 859 (pos 3) → doc 1438 (pos 4) | **Neutro** |
| val-125 | valor | presente (655) / presente | doc 938 (pos 4) → doc 945 (pos 5) | **Neutro** |
| val-133 | valor | presente (734) / presente | doc 1109 (pos 4) → doc 1516 (pos 5) | **Neutro** |
| val-087 (referência) | competências | gabarito 174 presente, **mas sem a frase de competência** / frase presente | 174:0000 e 0001 (listas de membros) → 174:0002 e 0003 | Aceitável (evidência direta) |

Nenhum dos três é **Aceitável** nem **Rejeitar**. Em todos, o chunk que entra é da mesma entidade e traz o atributo pedido, mas troca um chunk equivalente por outro, sem benefício demonstrável. Nenhum teve resposta entregue na 4.3 (todos `ambigua`).

## val-011 — "Qual é o endereço do hospital credenciado no Gama que teve alterações em seus procedimentos?"

1. **Atributo:** endereço; nome saliente da pergunta: apenas `gama` (uma localidade, não um nome de hospital).
2. **Antes:** 1611:0002 (pos 1; regulamento do plano de saúde, irrelevante), 856:0128 (pos 2; lei do Comércio Local Sul, irrelevante), 859:0000 (pos 3; Termo de Credenciamento nº 90/2025, Hospital de Olhos do Gama, 09/06/2025). Descartados: 1438 (pos 4), 162 (pos 5).
3. **Depois:** 1438:0000, 1611:0002, 856:0128.
4. **Saiu 859; entrou 1438.**
5. **Rótulo:** `ENDEREÇO:` em "CNPJ…, ENDEREÇO: ST QUADRA 1 CONJUNTO G LOTE 1 - GAMA/DF". O 859 tem o mesmo rótulo; ele só não foi "promovido" porque já estava selecionado. O S1 deslocou um chunk igualmente forte.
6. **Entidade:** 859 e 1438 são o mesmo Termo de Credenciamento nº 90/2025 (Clínica Sul de Oftalmologia / Hospital de Olhos do Gama, mesmo CNPJ, mesmo endereço), em duas edições (09/06 e 22/09/2025). Textos praticamente idênticos; muda o signatário (Waldeci Ramalho → Sinésio Silva Souza) e "Edital … nº 01/2024" → "01/2024".
7. **Atributo:** ambos trazem o endereço do mesmo hospital. A pergunta, porém, pede o hospital "que teve alterações em seus procedimentos" e o gabarito é o doc 1329 (Hospital Maria Auxiliadora, no Gama), que **não foi recuperado em nenhum contexto**. Nada no texto do 1438 mostra "alterações em procedimentos"; pode tratar-se de republicação, mas isso não é demonstrável pelo texto.
8. **Evidência útil perdida:** nenhuma — o conteúdo de endereço é o mesmo.
9. **Classificação: Neutro.** Troca de quase-duplicata por quase-duplicata; nenhum dos dois leva ao hospital esperado. Não prejudica (mesma entidade) nem beneficia (o gabarito segue fora).

## val-125 — "Qual foi o valor da dívida reconhecida pelo Hospital Santa Marta?"

1. **Atributo:** valor; nomes: `santa`, `marta`.
2. **Antes:** 1203:0000 (pos 1; considerandos, sem valor/entidade explícitos), 655:0000 (pos 2; **gabarito**, R$ 64,10), 812:0000 (pos 3; Hospital Santa Marta, reconhecimento de dívida), 938:0000 (pos 4; Hospital Santa Marta, R$ 78.213,91). Descartado: 945 (pos 5).
3. **Depois:** 945, 1203, 655, 812.
4. **Saiu 938; entrou 945.**
5. **Rótulo:** `Valor:` ("Valor: R$413.596,67").
6. **Entidade:** 945 → "HOSPITAL SANTA MARTA LTDA", CNPJ 00.610.980/0001-44 — o mesmo CNPJ dos docs 655, 812 e 938. Entidade correta.
7. **Atributo:** responde (R$ 413.596,67 de dívida reconhecida), mas é **mais uma** dívida do mesmo hospital, não a do gabarito (655). O 938 também responde ("RECONHEÇO A DÍVIDA, no valor de R$ 78.213,91…"), só que em prosa, sem o rótulo `Valor:`. A priorização favorece o **formato do rótulo**, não maior relevância.
8. **Evidência útil perdida:** nenhuma específica — o 938 era outra dívida do mesmo hospital; o gabarito (655) permanece. Reduz a diversidade em um sentido e aumenta em outro (troca uma dívida por outra).
9. **Classificação: Neutro.** A pergunta é intrinsecamente ambígua (várias dívidas do mesmo hospital); trocar uma candidata válida por outra não melhora nem piora a cobertura do gabarito.

## val-133 — "Qual é o valor autorizado para pagamento ao Hospital Lago Sul?"

1. **Atributo:** valor autorizado; nomes: `lago`, `sul`.
2. **Antes:** 944:0000 (pos 1; R$ 80.065,57), 1067:0087 (pos 2; debate legislativo, irrelevante), 734:0000 (pos 3; **gabarito**, R$ 23.505,72), 1109:0000 (pos 4; R$ 45.751,71). Descartado: 1516 (pos 5).
3. **Depois:** 1516, 944, 1067, 734.
4. **Saiu 1109; entrou 1516.**
5. **Rótulo:** `Valor:`. O 1109 **também** tem `Valor:` — foi deslocado por ter ranking mais baixo, não por falta de rótulo.
6. **Entidade:** 1516 → Hospital Lago Sul S/A, CNPJ 00.382.069/0001-27, processo 04001-00000796/2024-36 (o mesmo de 734, 944 e 1109). Entidade correta.
7. **Atributo:** responde com o mesmo tipo de ato (R$ 323.859,26, autorização de pagamento do Termo nº 07/2020), mas é mais um pagamento do mesmo processo — não é o do gabarito.
8. **Evidência útil perdida:** nenhuma distinta: 1109 e 1516 têm a mesma estrutura e entidade, valores diferentes; 734 (gabarito) permanece.
9. **Classificação: Neutro.** Inversão de posição entre dois chunks igualmente "fortes"; não há critério do S1 que justifique 1516 sobre 1109.

## Comparação com val-087

| | val-087 | val-011 / 125 / 133 |
|---|---|---|
| Contexto anterior continha evidência do atributo? | **Não**: só listas de membros e artigos de instituição; a frase "IV – Compete à CRSSU discutir e deliberar…" estava no chunk descartado | **Sim**: o contexto anterior já tinha chunk(s) com o atributo da mesma entidade (859; 655/812/938; 944/734/1109) |
| Chunk que entra | traz a evidência única do atributo ("Compete à CRSSU discutir e deliberar sobre a direção, avaliação, monitoramento…") e o título "Art. 4° Competência e Disposições Gerais…" | traz mais uma ocorrência do mesmo tipo de dado (outro endereço-duplicata ou outro valor) |
| Chunk que sai | listas de membros (não respondem à pergunta) | chunks equivalentes que também respondem |
| Efeito na cobertura | de zero para presente | inalterada |
| Rótulo | repete o atributo ("compete"/"Competência") **e** a frase é a resposta | repete o atributo (`ENDEREÇO:`, `Valor:`), mas só indica formato; não distingue qual registro é o pedido |

Em val-087 o rótulo coincide com a resposta; nos três casos pendentes, o rótulo é um campo de formulário que existe também nos chunks já presentes. A literalidade do rótulo, isolada, não demonstra benefício.

## Conclusões e observações (sem alteração de código)

- **Aceitável: 0; Neutro: 3 (val-011, 125, 133); Rejeitar: 0.** Nenhuma substituição introduz entidade ou atributo de outra natureza, nem remove evidência distinta; tampouco algum deles tem benefício demonstrável.
- Padrão observado: o S1 promove o chunk descartado **mesmo quando o contexto já contém chunk igualmente forte** (val-011 e val-133). Nesses casos o efeito é apenas inversão de ranking. A regra se justifica em val-087 porque nenhum chunk selecionado trazia o atributo. Uma variante conservadora (promover só se nenhum chunk selecionado do mesmo documento/entidade tiver rótulo forte) reverteria val-011 e val-133 para o contexto original e manteria val-087, val-074 e val-080; val-125 seguiria mudando (938 sem `Valor:` literal). Esta variante **não foi implementada** nem testada; fica como decisão para o responsável.
- Limitação: o rótulo forte vale para formulários com campo explícito (`Valor:`, `ENDEREÇO:`); documentos em prosa ("no valor de") ficam em desvantagem arbitrária.
- Estas conclusões são sobre o contexto, não sobre respostas: sem modelo, o efeito na geração permanece não medido.

Confirmação: nenhuma alteração em código/testes/corpus/índices/snapshots/resultados; flag `priorizar_atributo` desligada; nenhum modelo chamado.
