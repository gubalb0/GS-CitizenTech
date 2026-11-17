# Validação seletiva da Fase 4B — resultados (candidata `fail-closed-4.4.4b-cand`, NÃO validada)

Escopo: 21 gerações autorizadas (7 slots × 3 repetições), `val-074` e `val-087` (A = baseline 4A, B = S1 conservadora) e 3 controles (C). **Não é validação geral nem prova de prontidão para produção**; o Gen AI continua experimental e fora do Zelo.

## 1. Execução

- **21 de 21 gerações concluídas**, sem lacunas nem duplicações; nenhuma retentativa de JSON; nenhum erro técnico.
- Primeira etapa: 7 gerações (ordens 1–7), interrompida pelo critério de memória (RAM livre mínima 1.137 MB < 1.500 MB, causada pelo crescimento do `llama-server` de 5,4 → 7,6 GB — cache de prompt). Retomada autorizada, ordens 8–21 em 5 blocos (3+3+3+3+2), com descarregar/recarregar do modelo entre blocos. Parada intermediária registrada: dois tentativas de retomada pararam **antes de qualquer geração** porque a RAM livre pós-carga (3.026 e 3.053 MiB) ficou abaixo do limite de 3.072 MiB; por decisão do responsável o limite pós-carga passou a **3.000 MB** (só essa constante do script de retomada).
- Configuração efetiva conferida em cada carga: `qwen3-8b`, Qwen3-8B Q4_K_M, contexto 8192, `parallel 4`; temperatura 0,3; sem seed; mesmo prompt/parâmetros (hash de parâmetros idêntico em todos os slots).
- `tokens_prompt` (sem truncamento): 074-A 2748, 074-B 2865, 087-A 2493, 087-B 2479, 006 2649, 024 2643, 025 2093 — constante nas 3 repetições.
- Tempo total de geração 342 s (≈ 5,7 min); por geração 8–20 s. RAM livre mínima durante a retomada: 2.255 MB; memória comprometida máxima global 64,4 %.
- Verificações de integridade (`validacao_seletiva_integridade.json`): 21 `run_id` únicos e iguais ao manifesto, 3 repetições nos 7 slots, hash do contexto/parâmetros/chunks de cada execução = manifesto, flag ligada somente nos slots B, controles com flag desligada.

## 2. Avaliação cega

Procedimento: as 21 saídas foram embaralhadas (semente fixa) e identificadas só por código S01–S21 (`validacao_seletiva_CEGO.json`). A classe de cada uma foi **registrada antes de abrir o mapeamento** (`validacao_seletiva_AVALIACAO_CEGA.json`, SHA `3f36670a269e2927`), com a rubrica e os elementos exigidos do protocolo, sobre a saída bruta do modelo, independentemente do status do pipeline. Rubrica não ajustada depois. Limitações: um único avaliador (modelo); o conteúdo das respostas pode sugerir a condição; as dimensões de fidelidade/citação foram completadas depois, com a verificação literal do pipeline.

### 2.1 Alvos

| Caso | Condição | r1 | r2 | r3 | Classe (saída bruta) | Status do pipeline |
|---|---|---|---|---|---|---|
| val-074 | **A** (baseline) | Abstenção indevida | Abstenção indevida | Abstenção indevida | 0/3 corretas | fora_do_escopo ×3 |
| val-074 | **B** (S1 conservadora) | Correta | Correta | Correta | **3/3 corretas** | **ambigua ×3** |
| val-087 | **A** | Incorreta | Incorreta | Incorreta | 0/3 corretas | parcial, insuficiente, insuficiente |
| val-087 | **B** | Correta | Correta | Correta | **3/3 corretas** | parcial ×3 |

- **val-074:** em B, o modelo cita `Objeto: FORNECIMENTO ININTERRUPTO DE ALIMENTAÇÃO HOSPITALAR ESPECIALMENTE PREPARADA…` (chunk `dodf-28:0000`, E1 presente, citação literal). Em A, sem esse chunk, abstém-se nas 3. **Atenção:** o pipeline converte as 3 respostas B em `ambigua` (teste de identificabilidade: há outras publicações semelhantes — CONTRATO 1025/2024, Extrato 03/2025 etc.). Ou seja, a **saída bruta melhora, mas o cidadão ainda não recebe o objeto**; o resultado final do pipeline é "não identificada a publicação" nos dois casos.
- **val-087:** em B, as 3 respostas trazem a frase de competência (compete à CRSSU discutir e deliberar sobre direção, avaliação, monitoramento, organização, funcionamento e aperfeiçoamento dos serviços regulados), com citações literais de `C2`/`C3`. Em A, as 3 falham do mesmo modo que na 4.3: competência = "nortear gerências" e Titular HRG como evidência (membros como competência). O verificador bloqueia 2/3 (`rotulo_incompativel_com_atributo`), mas **a repetição r1 de A foi entregue como `parcial` com resposta incorreta** — falha do verificador existente, não da S1; em B isso não ocorre.

### 2.2 Controles (contexto idêntico; condição C)

| Controle | Classe r1/r2/r3 | Pipeline |
|---|---|---|
| val-006 | Correta ×3 | respondida ×3 |
| val-024 | Correta parcial ×3 | respondida ×3 |
| val-025 | Abstenção correta ×3 | fora_do_escopo ×3 |

Os três controles ficaram **estáveis na classe** (e, em val-006/024, com o mesmo conteúdo) nas 3 repetições: o piso de ruído observado é zero em mudança de classe. Isso sustenta, nesta amostra, que as diferenças A×B em val-074/087 vêm do contexto, não de variação da geração.

## 3. Aplicação dos critérios pré-definidos

| Caso | Critério | Resultado |
|---|---|---|
| val-074 | B ≥ 2/3 corretas com E1, citação válida, sem afirmação não sustentada; A ≤ 1/3 | B 3/3, A 0/3 → **melhora real na saída bruta** (ressalva: status final do pipeline = ambigua em ambas as condições) |
| val-087 | idem | B 3/3, A 0/3 → **melhora real** (também no status final: de bloqueio/entrega errada para entrega correta parcial) |
| Controles | sem piso de ruído relevante | estáveis; **sem regressão** |
| Regressão | B Incorreta ou com afirmação não sustentada | **nenhuma** em B |

Conclusão objetiva: nos dois casos-alvo, a S1 conservadora produziu contexto que levou o modelo a respostas corretas em 6/6 gerações B contra 0/6 em A, sem regressão nos controles.

## 4. Limitações

- **2 casos e 3 repetições por condição:** resultado descritivo, sem significância estatística; **não generaliza** para os 150 (a S1 conservadora altera só esses 2 contextos).
- val-074-B não chega ao cidadão: a política de identificabilidade (`ambigua`) intercepta. Melhorar o status final exigiria tratar a publicação não identificável, fora do escopo desta fase.
- val-087-A r1 mostra que o verificador atual pode entregar resposta de competência baseada em lista de membros; B contorna ao fornecer a evidência certa, mas a fragilidade do verificador persiste.
- Avaliação por um único avaliador (modelo); recomenda-se revisão humana das 21 saídas e do arquivo de mapeamento.
- Sem seed e com temperatura 0,3, as repetições foram bastante estáveis aqui (mesma classe em 21/21 grupos de 3); isso não garante estabilidade em outros casos.
- Consumo de memória: o modelo exige recarga a cada ~3 gerações (cache de prompt) e ≥ 3 GB de RAM livre pós-carga; o limite pós-carga foi reinterpretado para 3.000 MB por decisão do responsável.

## 5. Artefatos e hashes (SHA-256, 16 primeiros caracteres)

| Arquivo (em `docs/assistente/diagnostico_4_4/fase4/`) | Hash |
|---|---|
| `validacao_seletiva_20261116-155046.jsonl` (ordens 1–7, inalterado) | `cbb8482916d55050` |
| `validacao_seletiva_retomada_20261116-161042.jsonl` (ordens 8–21) | `c198f0893d40121f` |
| `protocolo_validacao_manifestos.json` (manifesto, inalterado) | `43fb09685404714c` |
| `validacao_seletiva_integridade.json` | `1d77f31a0a34564b` |
| `validacao_seletiva_CEGO.json` / `..._MAPA_nao_abrir_antes_da_avaliacao.json` | `9d71cca105629c5e` / `1d59b9bfe6cdce09` |
| `validacao_seletiva_AVALIACAO_CEGA.json` | `3f36670a269e2927` |
| Scripts: `executar_validacao_seletiva.py`, `retomar_validacao_seletiva.py`, `integridade_e_cegamento.py` | novos |
| Código técnico: `geracao.py` / `evidencias.py` / `catalogo.py` | `46862831592d09fc` / `742031bb9934a3d9` / `8e44143ba1d092f5` (inalterados) |

`verificar_hashes.py` → TODOS CONFEREM. Resumos das paradas: `validacao_seletiva_20261116-155046.resumo.json`, `validacao_seletiva_retomada_20261116-155541.resumo.json`, `..._160031.resumo.json`, `..._161042.resumo.json`.

## 6. Estado final

Modelo descarregado e servidor LM Studio encerrado. Nenhuma alteração em pipeline, prompts, parâmetros, índice, manifesto, hashes de referência, snapshots ou resultados históricos. Nenhuma rodada além dos 21 slots. Versão `fail-closed-4.4.4b-cand` permanece **candidata, não validada**; novas rodadas ou mudanças no pipeline dependem de nova autorização.
