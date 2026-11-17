# Protocolo de validação seletiva — Fase 4B (versão candidata `fail-closed-4.4.4b-cand`)

Status: **planejamento e preparação; nenhuma geração foi executada** (sem LM Studio, sem Qwen, sem APIs, sem rodada, sem regenerar os 150). Os manifestos foram montados offline (recuperação BM25 + montagem de contexto/mensagens; nada foi enviado a modelo). Pipeline, corpus, índices, gabaritos e snapshots não foram alterados; a flag `priorizar_atributo` continua `False` por padrão (a condição B a liga **somente** numa instância de configuração em memória, nunca no código).

## 1. Desenho experimental

Pergunta: a S1 conservadora melhora a resposta nos dois casos cujo contexto muda (**val-074** objeto do contrato; **val-087** competência da CRSSU)?

Desenho **pareado e intra-caso**: para cada caso-alvo, mesma pergunta, mesmo prompt de sistema, mesmo modelo/parâmetros/orçamento; a **única** diferença é o contexto selecionado. Como a geração é estocástica (temperatura 0,3, top_p 0,8, sem seed), cada condição é executada **3 vezes** e a unidade de análise é a distribuição das 3 repetições, não uma única resposta. Três **controles** executam **somente a condição C** (flag desligada), 3 repetições por caso; medem a variabilidade da geração sem mudança de contexto.

**Contagem aprovada: 21 gerações.**

| Grupo | Cálculo | Gerações |
|---|---|---:|
| Alvos | 2 casos × 2 condições (A, B) × 3 repetições | 12 |
| Controles | 3 casos × 1 condição (C) × 3 repetições | 9 |
| **Total** | | **21** |

**Esclarecimento técnico:** a afirmação de que o contexto dos controles é idêntico com e sem a flag descreve uma **propriedade verificada offline** (testes e manifesto: `contexto_identico_com_flag_ligada = true` nos 3), **não** duas condições de execução. A flag S1 só altera a seleção de chunks do contexto e **não é enviada ao modelo**; como o conteúdo enviado é idêntico nos dois estados, executar ambos duplicaria amostras da mesma condição sem medir efeito adicional da S1. Por isso **não existem slots `-A` ou `-B` para controles** (só `val-006-C`, `val-024-C`, `val-025-C`), e não se acrescentam gerações redundantes.

| Papel | Slot | Contexto | Reps |
|---|---|---|---|
| Alvo, A (baseline 4A) | val-074-A, val-087-A | flag desligada | 3 cada |
| Alvo, B (candidata) | val-074-B, val-087-B | flag ligada (S1 conservadora) | 3 cada |
| Controle (condição única C) | val-006-C, val-024-C, val-025-C | flag desligada (condição C; sem slots A/B) | 3 cada |

## 2. Condições A e B

**A — baseline 4A:** contexto reconstruído com `ConfigGeracao()` (flag off). Verificado: reproduz exatamente o contexto da rodada 4.3 nos 150 (chunks, quantidade, scores e tokens) e, para os 5 casos do protocolo, `contexto_reproduz_rodada_4_3 = true`. O código de montagem do prompt é idêntico ao da rodada 4.3 (comparação AST de `PROMPT_SISTEMA`, `ESQUEMA_SAIDA`, `VERSAO_PROMPT`, `ConfigGeracao` sem o campo novo, `_cabecalho`, `neutralizar`, `estimar_tokens`: **todos iguais**).

**B — candidata 4B:** `ConfigGeracao(priorizar_atributo=True)`.

| Caso | Contexto A (ordem enviada) | Contexto B (ordem enviada) | Tokens A → B |
|---|---|---|---|
| val-074 | 338:0016, 1722:0024, 442:0015 | **28:0000**, 338:0016, 1722:0024 | 2916 → 2985 |
| val-087 | 174:0004, 174:0001, 174:0000 | **174:0002, 174:0003**, 174:0004 | 2948 → 2928 |

**Confirmação:** para ambos os casos, `hash_prompt_sistema`, `hash_parametros` e `versao_prompt` são **iguais** entre A e B; apenas `hash_contexto` difere (`so_o_contexto_difere = true`). Ambas as condições serão processadas pelo **mesmo código** (hash do código vivo = snapshot `*_44_fase4b_cand.py`); a flag off reproduz as decisões da 4A (replay dos 150 = 0 diferenças).

**Diferenças em relação à rodada 4.3 original (documentadas):** (i) a rodada usou `versao_politica = fail-closed-4.3`; a política só atua *depois* da geração, não altera a requisição ao modelo; (ii) sessão/estado do LM Studio, cache de prompt e a ausência de seed tornam a saída da 4.3 **não reproduzível bit a bit**. Por isso a condição A **será re-executada** (não se reaproveita a saída histórica como se fosse A); a saída 4.3 fica registrada como referência histórica, fora das contagens.

## 3. Controles e justificativa

| Controle | Classe (auditoria 4.3) | Contexto (tokens / chunks) | Por quê |
|---|---|---|---|
| **val-006** | Correta (respondida) | 2910 / 3 (inclui `dodf-28:0000`) | Resposta correta entregue; mesmo tema de val-074 (alimentação hospitalar, contrato 1025/2024) e contém o mesmo chunk promovido em val-074-B — mostra o comportamento do modelo com esse chunk sem o efeito da seleção |
| **val-024** | Correta, mas parcial (respondida) | 2969 / 3 (perto do orçamento) | Parcial entregue, contexto grande: sensível a instabilidade de formato/completude |
| **val-025** | Abstenção correta (fora_do_escopo) | 2604 / 3 | Comportamento de abstenção; geração curta (≈4 s) — checa se a abstenção é estável |

Critérios: contexto idêntico com e sem a flag (propriedade verificada offline; execução só em C); contexto 4A reproduzido; custo baixo; cobertura de resposta correta, correta parcial e abstenção. Alternativas descartadas por custo (5 chunks / geração longa): val-026.

## 4. Congelamento das entradas

Arquivo: `docs/assistente/diagnostico_4_4/fase4/protocolo_validacao_manifestos.json` (SHA-256 `43fb09685404714c…`), gerado por `preparar_manifestos_validacao.py` (recusa sobrescrever). Para cada slot: caso, versão do pipeline, hash do código (`geracao.py 46862831592d09fc`, `evidencias.py 742031bb9934a3d9`, `catalogo.py 8e44143ba1d092f5`), hash do prompt de sistema, das mensagens, do contexto, dos parâmetros e do corpo da requisição, chunks ordenados com SHA-256 do texto e tokens, modelo, parâmetros, condição (A/B/C) e a referência histórica da 4.3. Hashes de contexto (10 primeiros): 074-A `3d99b28a62`, 074-B `ce5937a934`, 087-A `ec5eaddd50`, 087-B `05602bf6c3`, 006 `854dc51beb`, 024 `0e82d9e678`, 025 `165c090e51`; hash de parâmetros **comum a todos**: `da69521dce`.

**Parâmetros congelados** (`ClienteLMStudio.completar`, sem alteração): modelo `qwen3-8b` (Qwen3-8B Q4_K_M bartowski; LM Studio 0.4.28, llama.cpp Vulkan 2.73.0, contexto 8192 — registro do projeto), `temperature 0,3`, `top_p 0,8`, `max_tokens 1100`, `stream false`, `response_format json_schema strict (resposta_cidadao)`, `/no_think` no prompt, orçamento 3.000 tokens, `max_chunks 5`, `razao_qwen 1,76`, `max_tokens_chunk 350`, retentativa de JSON inválido com temperatura 0 (`tentativas_json = 2`). **Seed: não definida** (o pipeline original não envia seed; adicioná-la seria alterar a configuração). A capturar, sem alterar, no início da execução: id do modelo carregado (`/v1/models`), versão do LM Studio/runtime, GPU offload, flash attention, batch size, threads, RAM livre.

## 5. Rubrica (aplicada por resposta; independente do status do pipeline)

Cada dimensão: **OK / Parcial / Falha / N/A**, com citação do trecho que justifica.

1. **Correção factual** vs. a referência (corpus).  2. **Aderência à pergunta.**  3. **Entidade e destinatário** corretos.  4. **Atributo** correto (objeto ≠ aquisição; competência ≠ composição/membros).  5. **Localidade** (quando aplicável).  6. **Fidelidade** aos trechos enviados.  7. **Citações/rastreabilidade** (fonte existe no contexto; trecho literal).  8. **Afirmações não sustentadas** (qualquer fato fora dos trechos enviados).  9. **Abstenção** correta ou indevida.  10. **Completude** (elementos exigidos presentes).

**Classe final:** Correta · Correta parcial · Incorreta · Abstenção correta · Abstenção indevida.

**Elementos exigidos, fixados agora (antes de qualquer execução):**
- **val-074:** E1 (obrigatório) objeto = *fornecimento ininterrupto de alimentação hospitalar* preparada para pacientes, acompanhantes e colaboradores; E2 (desejável) unidades de saúde do IGESDF incl. UPA 24H Samambaia; E3 (desejável) Contrato/Extrato do doc 28 como fonte. **Falhas:** apresentar como objeto a aquisição de itens (ex.: dexametasona, compressas), confundir com unidades de outra região, abstenção.
- **val-087:** E1 (obrigatório) compete à CRSSU discutir e deliberar sobre direção, avaliação, monitoramento, organização, funcionamento e aperfeiçoamento dos serviços regulados na Região de Saúde Sul; E2 (desejável) fluxos existentes e protocolos de regulação; E3 (desejável) menção ao Gama apenas como parte da Região Sul (não inventar competência específica do Gama). **Falhas:** listar membros/titulares (ex.: HRG) como competência, atribuir competência ao Superintendente/outra entidade, abstenção.
- Controles: referência = `resposta_referencia` do benchmark e a classe da auditoria 4.3.

**Aplicação cega:** as saídas (texto, citações, status) serão embaralhadas e identificadas só por código; condição e repetição ocultas até o fim da avaliação. Recomenda-se que o responsável humano reveja uma amostra (idealmente todas as 12 de alvo). O resultado do pipeline (`respondida`, `parcial`, `insuficiente`…) é registrado à parte e **não** define a classe.

## 6. Critérios de sucesso e regressão (definidos antes)

Por caso-alvo, 3 repetições por condição:
- **Melhora real:** em B, ≥ 2 de 3 repetições Correta/Correta parcial **com E1 presente, citação válida e nenhuma afirmação não sustentada**; em A, ≤ 1 de 3; nenhum controle regride (abaixo).
- **Neutro:** distribuições de classe de A e B diferem em ≤ 1 repetição, ou ambas igualmente corretas/incorretas.
- **Regressão:** B produz resposta Incorreta ou com afirmação não sustentada em ≥ 2 repetições onde A não produziu; **ou** qualquer resposta de B que atribua o atributo à entidade errada (ex.: membros como competência, aquisição como objeto) — registra-se como regressão qualitativa mesmo em 1 repetição; ou piora em controle.
- **Inconclusivo:** demais padrões, ou quando a variabilidade nos controles (mesmo contexto) for do mesmo tamanho que a diferença A×B.
- **Controles:** classe estável nas 3 repetições = base de comparação; se um controle varia de classe, essa variação é o piso de ruído; mudança de classe em controle com contexto idêntico **não** é atribuída à S1.
- **Divergência entre repetições:** relatar todas as saídas e a distribuição (ex.: 2 Corretas, 1 Incorreta); **proibido** escolher a melhor; a síntese usa a classe majoritária *e* a faixa.
- **Respostas com palavras diferentes:** equivalência por **elementos exigidos** (E1…), não por texto; sinônimos aceitos se preservam atributo, entidade e números exatos; números/CNPJ/datas exigem igualdade.
- **Corretas-parciais:** E1 presente mas elementos desejáveis ausentes ⇒ Correta parcial (conta como sucesso apenas se não houver afirmação não sustentada); registra-se o elemento faltante.
- Uma única resposta favorável **não** prova melhoria; com n = 3 por condição o resultado é **descritivo**, sem significância estatística, e cobre só dois casos — não generaliza para os 150.
- Mudança de status (insuficiente → respondida) **nunca** é critério por si; vale a classe da rubrica.

## 7. Sequência operacional (uma geração por vez)

21 execuções em ordem fixa no manifesto (`sequencia`): por repetição, bloco alvo (A/B alternando a ordem entre repetições: r1 A→B, r2 B→A, r3 A→B, e alternando val-074/val-087) seguido dos 3 controles (ordem invertida nas repetições pares). 
Pré-voo (antes de cada sessão): fechar navegador/Discord e cargas pesadas; conferir hashes (`verificar_hashes.py`) e que o código vivo = snapshot `_cand`; checar RAM livre (referência hoje: ≈5,0 GB livres de 16 GB com o sistema aberto) — **só iniciar** com ≥ 3 GB livres **com o modelo já carregado e ocioso**; carregar o modelo **uma vez** (não recarregar entre execuções; sem instância paralela); capturar a configuração ativa.
Por execução: verificar RAM livre antes; enviar **uma** requisição; amostrar RAM a cada ≈2 s durante a geração (psutil); gravar entrada/saída bruta, tokens, latência, tentativas, `finish`, erros e pico de RAM em arquivo **novo** (`validacao_seletiva_<timestamp>.jsonl`; nunca sobrescrever); aguardar o fim antes da próxima. 
**Interrupção segura:** parar o lote (sem nova requisição) se RAM livre < 1,5 GB, uso de memória comprometida > 90 %, swap em crescimento sustentado, timeout/erro de servidor repetido (2×) ou LM Studio sem resposta; registrar a causa e retomar apenas após novo pré-voo. Sem aumentar contexto, batch ou limite de tokens para "melhorar" resultados. Retentativa de JSON inválido é a do pipeline (já prevista); qualquer outra repetição manual é proibida.

## 8. Número de gerações e arquivos

**Desenho recomendado: 21 gerações** (alvos: 2 casos × 2 condições A/B × 3 repetições = 12; controles: 3 casos × 1 condição C × 3 repetições = 9). Podem ocorrer retentativas automáticas de JSON inválido pelo pipeline (1/150 na 4.3), contadas à parte. Tempo estimado ≈ 21 × (4–25 s) ≈ 5–9 min de geração + carga do modelo. Alternativas (não recomendadas): **12** (só alvos, sem piso de ruído) ou **15** (alvos + 1 controle × 3; cobre um só perfil de resposta).

Arquivos que serão utilizados: `citizentech/assistente/{geracao,evidencias,catalogo}.py` (inalterados); `data_assistente/versoes/*_44_fase4b_cand.py` (referência); índice `data_assistente/indices/est300o30`; corpus/benchmark via `avaliacao_e2e.preparar()`; rodada histórica `data_assistente/derivados/geracao_e2e_41_20261114-130608.jsonl` (só leitura); `docs/assistente/auditoria_independente_4_3/auditoria_independente_150.csv` (só leitura); `protocolo_validacao_manifestos.json`; `preparar_manifestos_validacao.py`. Novos na execução (não existem ainda): um `validacao_seletiva_<timestamp>.jsonl` de saída e o script executor (a ser escrito e revisado só após autorização, com trava que exige o hash do manifesto).

## 9. Limitações e riscos

- n = 3 por condição, 2 alvos: **evidência descritiva, não estatística**; não generaliza.
- Sem seed: não há reprodução bit a bit; cache de prompt do llama.cpp (prefixo do sistema) pode introduzir pequena dependência de ordem — mitigada pela alternância de ordem.
- A referência para a rubrica é a do benchmark; julgamento é humano/assistido e pode divergir — por isso a aplicação cega e a revisão pelo responsável.
- val-087-B muda o contexto, mas o **verificador** pode continuar bloqueando (4.3: `evidencia_nao_corresponde_a_pergunta:nome=coordenacao`); a rubrica avalia a **saída bruta do modelo** além do status final, para separar efeito de contexto do efeito do verificador.
- val-074-A: a 4.3 respondeu `fora_do_escopo`; a melhoria esperada depende de o modelo usar o chunk 28.
- Pressão de memória (16 GB, DDR4-2400; ≈5 GB livres no momento da preparação): risco de swap/travamento; mitigado por execução sequencial, pré-voo e limites de interrupção.
- A configuração real do LM Studio só pode ser capturada na execução; divergências em relação ao registro D2 serão documentadas antes de comparar.

## 10. Auditoria final de consistência

- Código vivo = snapshot `*_44_fase4b_cand.py` (asserção no gerador); `verificar_hashes.py` confere; flag padrão `False`.
- A×B: prompt, parâmetros e versão de prompt idênticos; só o contexto difere (2/2 casos).
- Contextos A reproduzem a rodada 4.3 (150/150; 5/5 no protocolo); controles têm contexto idêntico com a flag ligada (3/3).
- Nenhum modelo foi carregado/chamado; nenhum arquivo histórico foi sobrescrito.
