# Versão 4.4 — Fase 2 (verificador)

Política: `fail-closed-4.4.2` (prompt v3 inalterado). Snapshots da 4.3 preservados (`data_assistente/versoes/*_43_pre_execucao.py`, idênticos aos arquivos vivos antes desta fase). Estado pós-Fase 2 guardado em `geracao_44_fase2.py` e `evidencias_44_fase2.py`. Nenhuma geração com o modelo foi executada: a validação usa **replay offline** das saídas brutas gravadas na rodada 4.3 (`scripts/replay_verificador.py`; antes das alterações reproduziu os 150 resultados originais sem nenhuma diferença).

## Arquivos alterados
- `citizentech/assistente/evidencias.py`: `periodo_ausente`, `alinhamento`, `afirmacoes_nao_sustentadas` (alteradas); `casar_citacao`, `meses_em_datas_numericas`, `tem_alfabeto_estranho`, `termos_especificos_da_resposta`, `classificar_niveis` (novas).
- `citizentech/assistente/geracao.py`: `trecho_literal`, `validar_saida`, `_aplicar_politica`, `VERSAO_POLITICA` (alteradas); `_chave_pub`, `_irmaos`, `_textos_publicacao`, `_tv` (novas).
- Testes: `tests/test_verificador_44.py` (novo, 26 testes); `tests/test_politica_evidencias.py` (apenas a constante de versão da política).
- Não alterados: retriever, índices, corpus, `catalogo.py`, RPA congelado, rodadas e auditorias anteriores.

## Correções de diagnóstico (descobertas nesta fase, com evidência)
1. **val-087 e val-141:** a causa **não** era sigla ou morfologia. Os nomes da pergunta (`coordenação`; `programa`, `dados`, `periciais`) estão na **mesma publicação**, em chunk vizinho que também foi enviado ao modelo, mas não no chunk citado. Por isso não relaxei o casamento de nomes (não criei regra de sigla/radical).
2. **val-126:** a citação **existe literalmente** no chunk C1 do doc 1014, mas o modelo a atribuiu ao C2. Não é texto inventado nem emendado: é **erro de rastreabilidade (chunk errado)**. O bloqueio foi mantido, como pedido, e agora diz isso (`citacao_em_outro_chunk:C2->C1`). A resposta em si estava correta; ver "Decisão pendente".
3. **val-097:** a citação foi cortada no meio de um número (`10.301`, prefixo de `10.301.6202.3135.0003`).
4. **val-033/089:** continuam bloqueados, mas pelo motivo certo: itens afirmados sem citação verificada da própria fonte.

## Lógica implementada (evidência encontrada x atribuível x suficiente)
- **Citação (`casar_citacao`):** compara por tokens (números inteiros e palavras; pontuação fora de números ignorada; dígitos exatos). Estados: `literal`; `reparada` (emenda de trechos não contíguos **do mesmo chunk**, em ordem, em região de até 120 tokens, cobrindo ≥ 60%; só os fragmentos literais valem como evidência e a parte emendada é descartada; um número cortado no fim da citação, prefixo de número do chunk, também é `reparada`); `fabricada` (algum número não existe no chunk); `nao_literal`.
- **Atribuível:** um termo específico da resposta (número ou nome) é atribuível se está na citação verificada, na **candidata literal** (verificada no chunk citado, e só para fontes que também têm citação verificada) ou nos metadados; a origem fica em `verificacao["evidencia"]`. **Nada de outra publicação conta.**
- **Encontrada:** termo presente em algum chunk do contexto. Se só estiver em outra publicação, é registrado em `encontrada_so_em_outra_publicacao` e não sustenta a resposta.
- **Suficiente (parcial nesta fase):** alinhamento com a pergunta (nomes, números, ano, mês) no chunk citado **ou na mesma publicação** (chunks vizinhos do contexto e documento completo do catálogo, com origem registrada); mês também por data numérica `dd/mm/aaaa`; em pergunta de **um fato** com mais de uma publicação citada, **uma única** publicação precisa conter os termos da pergunta e sustentar todos os termos da resposta (`evidencias_de_publicacoes_distintas_combinadas`). Adequação do atributo pedido (período por evidência, localidade, tipo de informação) fica para a Fase 3.
- **Texto corrompido:** caracteres de outros alfabetos na resposta, citações ou candidatas bloqueiam (`caracteres_fora_do_alfabeto`, val-108).
- A citação continua precisando ser literal **no chunk citado**: ser literal em outro chunk não a legitima (só vale como suporte auxiliar de ano/nome).

## Resultado do replay (150 casos, saídas brutas da 4.3)
Só **10** casos mudam; os outros 140 permanecem idênticos, e as 31 respostas dadas na 4.3 mantêm status e texto.

| Caso | 4.3 | 4.4 Fase 2 | Evidência/origem registrada | Observação |
|---|---|---|---|---|
| val-031 | insuficiente | **parcial** | ano e nomes no chunk vizinho `dodf-1464` | mesma publicação |
| val-032 | insuficiente | **parcial** | citação `reparada` (linha pulada descartada) | |
| val-047 | insuficiente | **parcial** | citação `literal` (vírgula x hífen) | resposta diz "é Anestesiologia" numa lista de programas: Fase 3 |
| val-087 | insuficiente | **parcial** | `coordenação` em chunk vizinho `dodf-174` | |
| val-141 | insuficiente | **parcial** | nomes em chunk vizinho `dodf-1035` | resposta é negativa ("não especifica"): Fase 3 |
| val-045 | insuficiente | **ambigua** | citação `reparada`; verificador aprova | a política de identificabilidade (inalterada) a converte em `ambigua` |
| val-097 | insuficiente | **ambigua** | citação `reparada` (número cortado) + candidata literal | idem |
| val-106 | insuficiente | **ambigua** | candidata literal + mês por data numérica | idem |
| val-044 | insuficiente | **parcial** | candidata literal na fonte C3 (que tem citação verificada) | **não estava na lista**: mesma família de falso positivo; responde com o objeto do edital (tipo val-136): Fase 3 |
| val-083 | insuficiente | **parcial** | candidata literal em C2 (que tem citação verificada) | **não estava na lista**; mesma família |
| val-062 | insuficiente | insuficiente | `citacao_fabricada:1.105.500,00` | preservado |
| val-108 | insuficiente | insuficiente | `caracteres_fora_do_alfabeto` | preservado |
| val-126 | insuficiente | insuficiente | `citacao_em_outro_chunk:C2->C1` | preservado |
| val-033, val-089 | insuficiente | insuficiente | itens da candidata de fontes sem citação verificada | preservados |

Contagem de status da 4.3 (original → replay): `insuficiente` 33 → 23; `parcial` 23 → 30 (+7 incluindo 044 e 083); `ambigua` 71 → 74; `respondida` 8 → 8; `fora_do_escopo` 15 → 15. Isto **não mede acerto**: 3 dos 7 novos `parcial` (val-044, 047, 141) são exatamente os tipos de erro que a Fase 3 deve impedir.

## Testes
`test_verificador_44.py` (26): casar_citacao (pontuação, dígitos exatos, separadores, `n.º`, emenda reparada x fora de ordem x dispersa x baixa cobertura, número fabricado, número cortado x número diferente, outro chunk, alfabeto), período por data numérica (positivo e mês errado), alinhamento (mesma publicação com origem x ausente x outra publicação), candidata literal (positivo e negativo), integração para val-097, 106, 031, 087, 032, 062, 108, 126, 033, publicação única, níveis de evidência e **replay real dos 150** (só 10 casos mudam, bloqueios preservados, 31 respostas da 4.3 inalteradas).
Suíte do Gen AI: **225 passam** (199 + 26). Hashes do RPA e dos 27 artefatos conferem (`scripts/verificar_hashes.py`).

## Riscos de regressão
- Número cortado no fim da citação vira `reparada` (sem o valor): risco baixo; o valor continua exigindo candidata literal ou citação.
- Candidata literal como evidência: só em fonte com citação verificada e só para termos que existem no chunk citado; pode aprovar itens que o modelo não citou (val-083). Mitigação: origem registrada em `verificacao.evidencia`.
- Documento completo do catálogo para nomes/anos: pode aceitar um nome que está na publicação certa mas em outra parte (a adequação entidade→atributo é a Fase 3).
- Regra de publicação única só atua em pergunta de um fato com mais de uma publicação citada; pode bloquear respostas legítimas montadas com duas publicações (nenhuma das 150 mudou por ela).
- A política de ambiguidade (4.2/4.3) foi mantida: val-045, 097 e 106 continuam sem resposta.

## Decisão pendente
**val-126:** a resposta ("instalação de 11 tendas ...") está certa e a evidência pertence à publicação correta, mas a citação aponta o chunk errado. Mantive o bloqueio conforme a instrução. Se quiser, uma regra futura pode **reatribuir** a citação ao chunk irmão onde ela é literal (registrando a origem), mas isso não foi implementado.
