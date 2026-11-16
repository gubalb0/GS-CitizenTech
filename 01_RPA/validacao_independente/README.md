# Validação independente — protocolo

**Status: NÃO EXECUTADA.** Esta pasta contém apenas a estrutura. Nenhum texto foi coletado, nenhum rótulo existe e nenhum resultado independente foi produzido. Enquanto o conjunto não for coletado, rotulado e avaliado conforme abaixo, **nenhuma afirmação de validação independente pode ser feita**.

## Objetivo
Estimar o desempenho real do modelo **congelado** (ver `docs/modelo_congelado.json`) em textos que a equipe de desenvolvimento nunca viu, e medir a segurança do tratamento de urgências.

## Papéis (devem ser pessoas diferentes dos desenvolvedores do modelo)
| Papel | Quem pode ser | Faz |
|---|---|---|
| **Coletores** (≥ 3 pessoas) | colegas de outra turma, familiares, voluntários, usuários reais do SUS se houver autorização | escrevem ou relatam textos livremente, seguindo `INSTRUCOES_COLETA.md` |
| **Rotuladores** (≥ 2, independentes entre si) | pessoas que não participaram do desenvolvimento; idealmente 1 com formação/experiência em saúde para os casos de urgência | rotulam cada texto sem ver a previsão do modelo, seguindo `INSTRUCOES_ROTULAGEM.md` |
| **Custodiante** (1) | pessoa fora do desenvolvimento (ex.: professor/monitor) | guarda o conjunto **fora do repositório**, lacra e executa a avaliação |

Desenvolvedores **não** coletam, rotulam, guardam nem veem o conjunto antes do relatório final.

## Requisitos do conjunto
- Textos **inéditos**, escritos com redação independente: não copiar nem parafrasear `data/treino.csv`, `data/teste_rotulado.csv`, `data/teste_cego.csv`, o README ou exemplos de código.
- Variedade de comunicação: mensagem curta, longa, formal, coloquial, abreviações ("vc", "pq", "tb"), erros de digitação, sem acento, caixa alta, mais de um pedido no mesmo texto, relatos vagos/ambíguos, pedidos fora do escopo.
- **Dados sintéticos ou autorizados:** sem nomes, CPF, telefones, endereços ou dados de saúde reais identificáveis. Se usar mensagens reais, anonimizar e ter base legal/autorização.
- **Tamanho mínimo para relatório confirmatório:** ≥ 30 textos por categoria (8 categorias), ≥ 30 `fora_do_escopo` e ≥ 40 casos de urgência clínica (a categoria `sintomas_urgentes` já conta; os demais vêm da coluna `urgencia_clinica`). Abaixo disso o relatório sai marcado **EXPLORATÓRIO**. Referência: com 30 casos por classe o IC95% de uma taxa de 90% é de ≈ 74–97%; amostras menores dizem pouco.
- Incluir deliberadamente **casos de urgência com vocabulário variado** (incl. crises de saúde mental, trauma, intoxicação, sinais neurológicos), pois são o maior risco conhecido.
- Rótulos permitidos: as 8 categorias + `fora_do_escopo`.

## Arquivos
| Arquivo | Uso |
|---|---|
| `modelo_coleta.csv` | formulário de coleta (entregue pelos coletores ao custodiante) |
| `modelo_rotulagem.csv` | ficha de rotulagem / arquivo final (colunas e significado abaixo) |
| `INSTRUCOES_COLETA.md`, `INSTRUCOES_ROTULAGEM.md` | guias para coletores e rotuladores |
| `avaliar.py` | lacra e avalia (uma única vez) |
| `LACRE.json`, `registro_execucoes.jsonl`, `relatorio_*.json` | gerados pela avaliação; **ainda não existem** |

Colunas de `modelo_rotulagem.csv`: `id_texto` (único), `texto`, `canal` (ex.: telefone, app, balcão), `coletor` (código, não nome), `rotulo_1`, `rotulador_1`, `rotulo_2`, `rotulador_2`, `rotulo_final` (consenso; em discordância, terceira pessoa decide), `urgencia_clinica` (`sim`/`nao`/`incerto`, independente da categoria), `ambigua` (`sim`/`nao`).

## Procedimento
1. **Pré-condição:** modelo e regras congelados (`python scripts/auditoria.py` já gerou o manifesto). Qualquer mudança no modelo ou nas regras exige novo congelamento **e um novo conjunto** (este não pode mais ser usado para decidir nada).
2. Coletores produzem os textos → entregam ao custodiante (não aos desenvolvedores).
3. Rotuladores trabalham em planilhas separadas, sem ver o modelo nem um ao outro; o custodiante consolida em `rotulo_final` e calcula a concordância (kappa).
4. Custodiante mantém o CSV **fora do repositório** (`validacao_independente/conjunto/` está no `.gitignore`) e **lacra**:
   ```bash
   python validacao_independente/avaliar.py --lacrar --conjunto CAMINHO/conjunto.csv --custodiante "Nome"
   ```
5. Custodiante avalia **uma única vez**, sem ajuste:
   ```bash
   python validacao_independente/avaliar.py --avaliar --conjunto CAMINHO/conjunto.csv
   ```
   O script recusa se o conjunto, o modelo ou as regras mudaram desde o lacre, ou se já houve avaliação (repetição só com `--repetir --justificativa` e fica no registro).
6. O relatório (`relatorio_*.json`) é publicado **como está**, inclusive se for ruim. Os desenvolvedores só então veem os erros; correções posteriores geram nova versão do modelo e exigem **novo** conjunto independente.

## O que o relatório informa
Acurácia no escopo e erro entre os encaminhamentos automáticos (com IC95% de Wilson), proteção de urgências (quantas terminaram em prioridade alta + revisão humana e **quais não**), destino dos textos `fora_do_escopo` (devem ir a humano), desempenho em casos ambíguos, matriz de confusão, métricas por classe e kappa entre rotuladores.

## Critérios de aceitação sugeridos (a definir pelo grupo **antes** de ver os resultados)
Sugestão de ponto de partida, a ser validada por profissional de saúde: nenhuma urgência clínica fora de revisão humana (limite superior do IC95% de falha reportado, não só a taxa observada); erro entre automáticos abaixo de um teto definido previamente; `fora_do_escopo` sempre a humano. Sem critérios definidos antes, qualquer resultado pode ser racionalizado depois.
