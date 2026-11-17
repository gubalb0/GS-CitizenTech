# Relatório de avaliação consolidado — Gen AI CitizenTech

Organizado conforme o enunciado FIAP (`gsgenai.pdf`, §5 "Plano mínimo de testes" e §6 "Barema"). **Todos os números vêm dos relatórios originais indicados; nada foi recalculado ou executado para este documento**, exceto contagens simples por status feitas por leitura dos JSONL (indicadas). Casos individuais: `ANEXO_CASOS_AVALIACAO.md`. Segurança: `SEGURANCA_E_MITIGACOES.md`.

## 0. Tipos de evidência (leia antes)
| Tipo | O que é neste projeto | É validação independente? |
|---|---|---|
| **Desenvolvimento** | Experimentos usados para decidir chunking, retriever, prompt e políticas, sobre as **150 perguntas de validação** do dataset (e variantes lidas depois de ver resultados) | **Não** |
| **Avaliação isolada** | 48 casos (39 + 9 novos) × 2 repetições com contextos **montados pelo autor**, critérios em código (`avaliacao_geracao.py`) | **Não** (casos e critérios do autor) |
| **End-to-end** | Retriever congelado → gerador nas 150 perguntas, rodada única por versão (4.1, 4.2, 4.3), **diagnóstica** | **Não** (as 150 já foram usadas no retriever) |
| **Auditoria automática / por modelo** | Julgamentos feitos pelo agente de desenvolvimento ou por instância do mesmo modelo (auditoria 4.3, diagnóstico 4.4, avaliação cega 4B, reauditoria 4C) | **Não** (não é humana; o nome da pasta `auditoria_independente_4_3` é do projeto) |
| **Revisão humana** | **Nenhuma foi realizada.** Um pacote cego foi preparado (`fase4d4/PACOTE_REVISAO_HUMANA_4D4.md`) e não foi respondido | — |
O conjunto de teste (350) **nunca foi usado**. Os gabaritos do dataset são gerados por LLM e contêm erros conhecidos.

## 1. Avaliação de chunking (desenvolvimento) — `docs/assistente/02_associacao_e_chunking.md`
- **Estratégias:** `tamanho` (janela) e `estrutura` (Art./§/incisos/itens → frases → palavras), 300/500/700 tokens de superfície, com e sem overlap; metadados preservados (edição, data, seção, referência, tipo, número…).
- **Métricas medidas** (corpus inteiro; proxy de evidência em 94 perguntas não-MULTI com valores numéricos):

| Config | Chunks | Fronteiras limpas | Evidência no mesmo chunk |
|---|---:|---|---|
| tam300 (o0/o30) | 13.995 / 15.367 | 10,2% / 9,8% | 83,0% |
| tam500 (o0/o50) | 8.779 / 9.578 | 9,5% / 10,1% | 87,2% / 86,2% |
| est300 (o0/o30) | 15.686 / 16.584 | 95,5% / 95,8% | 84,0% |
| est500 (o0/o50) | 9.522 / 10.155 | 96,6% / 96,8% | 87,2% |
| est700 (o0/o70) | 6.983 / 7.452 | 97,3% / 97,5% | 88,3% |
- **Leitura do relatório:** a estrutura praticamente elimina cortes no meio de frase (≈96–98% × ≈10%), com ≈3× mais tempo de processamento; a integridade de evidência depende do **tamanho**, não da estratégia (83–88%).
- **Impacto na recuperação** (`03_retriever.md`, 150 perguntas, desenvolvimento): `est300o30` × `est500o50`: MRR BM25 0,434 × 0,419; "ao menos uma publicação correta" no mesmo orçamento de contexto (BM25) 0,613 × 0,520 a ≈ 2,3K tokens e 0,640 × 0,580 a ≈ 3K tokens; só 8,7% dos chunks de `est300o30` excedem 512 tokens do e5 (78,3% em `est500o50`). **Escolha: `est300o30`.**
- **Limitações:** só duas configurações passaram pelo teste de recuperação; o proxy cobre só valores numéricos de 94 perguntas; razão Qwen3/superfície medida em 12 chunks.

## 2. Avaliação do retriever (desenvolvimento) — `docs/assistente/03_retriever.md`
`est300o30`, 150 perguntas (109 não-MULTI + 41 MULTI), relevância no nível da publicação canônica:
| Modo | R@1 | R@5 | R@10 | MRR | ≥1 correta @10 |
|---|---|---|---|---|---|
| BM25 (**adotado**) | 0,246 | 0,491 | 0,578 | 0,434 | 0,687 |
| Vetorial `multilingual-e5-small` | 0,185 | 0,371 | 0,450 | 0,316 | 0,533 |
| Híbrido (RRF k=60) | 0,219 | 0,458 | 0,559 | 0,396 | 0,653 |
Variantes (exploratórias, lidas depois dos resultados): híbrido `rrf_k=20` R@10 0,599 / MRR 0,417; `max_por_doc=3`, sem documentos gigantes, sem deduplicação (diferenças pequenas, dentro do ruído com n=150); sensibilidade do BM25 (`k1`, `b`, radical leve): MRR 0,385–0,443 (padrão 0,434). **Evidência no mesmo conjunto de chunks (94 perguntas, 5 chunks):** `est300o30` BM25 55,3%, vetorial 40,4%, híbrido 52,1%. Custo: consulta BM25 ≈ 1,7 ms; indexação ≈ 34 min; e5 em CPU ≈ 1,4 GB de RAM.
**Não avaliados (declarado no relatório):** reranking, expansão de consulta, filtros por metadados (campos esparsos), outros modelos de embeddings. **Limitações:** n=150 (diferenças de ~0,03–0,04 estão no ruído); ≈ 31% das perguntas sem publicação correta no top-10; 6 perguntas não unívocas.

## 3. Avaliação isolada do generator — `docs/assistente/04_gerador.md` §3, `04_1_confiabilidade.md` §4 (avaliação isolada; não independente)
| Conjunto | Resultado documentado |
|---|---|
| Etapa 4, prompt v2 (39 casos × 2) | **69/74 aprovados, 0 falsas confianças** (v1 re-julgada: 56/74, 13 falsas confianças); JSON válido 76/76; 0 tokens de raciocínio; 0 vazamentos; mediana de prompt 2.470 tokens, latência mediana 12,7 s |
| 4.1, casos originais (78 execuções) | 70 aprovados, 0 falsa confiança (A3 rebaixada ×2; A5 `insuficiente`/`ambigua`; B1 `fora_do_escopo` ×2 por rótulo; H3 repetiu o comando na justificativa ×2) |
| 4.1, casos novos (18 execuções) | 18/18 aprovados, 0 falsa confiança |
Categorias: evidência suficiente, parcial/MULTI, sem evidência, conflito/pares não unívocos, ambígua, fora de escopo, injeção direta/em documento, revelar instruções, evidência cortada, induzir invenção. Critério de aderência às fontes e à abstenção: citação literal, número na evidência, status aceito (regras em código). **Limites (do próprio relatório):** contextos montados pelo autor; critério corrigido depois de ver a v1; os 3 pares não unívocos orientaram a v2 (melhora otimista); amostra pequena; a 4.1 não melhorou o conjunto original (70 × 73) e os casos novos foram escritos sabendo da política.

## 4. Avaliação end-to-end (desenvolvimento, diagnóstica) — rodadas únicas de 150 perguntas
Contagens por status lidas dos `geracao_e2e_41_*.jsonl` (rodadas preservadas; 0 erros técnicos nas três):
| Rodada | respondida | parcial | ambigua | insuficiente | fora_do_escopo | Abstenção |
|---|---:|---:|---:|---:|---:|---:|
| 4.1 (`20261113-173721`) | 2 | 41 | 58 | 35 | 14 | 107/150 (71,3%) |
| 4.2 (`20261114-014826`) | 10 | 24 | 67 | 35 | 14 | 116/150 (77,3%) |
| 4.3 (`20261114-130608`) | 8 | 23 | 71 | 33 | 15 | 119/150 (79,3%) |
Grupos da rodada (A = fonte correta entre os chunks enviados; B = não enviada; 76/74 nos arquivos, 77/73 após a errata `ERRATA_AUDITORIA_4_3.md`): 4.3 — A: 8 respondida, 12 parcial, 39 ambigua, 15 insuficiente, 2 fora_do_escopo; B: 0 respondida, 11 parcial, 32 ambigua, 18 insuficiente, 13 fora_do_escopo. Etapa 4 original (v2): 19 de 72 perguntas sem fonte correta receberam resposta confiante com dados de outra publicação (`04_gerador.md` §5) → motivou a política fail-closed.
**Perguntas e tipos:** o conjunto das 150 tem perguntas respondíveis, ambíguas (incluindo 6 não unívocas) e sem a publicação correta no contexto (grupo B); **não inclui perguntas fora de escopo ou adversariais** (estas estão na avaliação isolada, §3, e em `SEGURANCA_E_MITIGACOES.md`).
**Qualidade e fundamentação (auditoria 4.3, por modelo, não humana):** 31 respostas dadas = 7 corretas, 16 corretas mas parciais, **8 incorretas**; 119 abstenções = 53 ambíguas de fato, 10 corretas, **56 indevidas**. Todas as 8 incorretas passam na verificação técnica (citação literal ≠ resposta correta). Utilidade: 31/150 = 20,7%. **Consistência entre turnos: não avaliada** (assistente de turno único). Errata aplicada a val-050, val-062, val-097.
**Candidata atual (`fail-closed-4.4.4d1-cand`):** não houve nova rodada end-to-end. Avaliada por (a) replay offline das 150 saídas gravadas da 4.3 (30 respostas entregues; 0 diferenças nos 150 entre 4A e 4D.1), e (b) 21 gerações seletivas da Fase 4B (val-074 e val-087 com e sem a seleção de contexto S1; 3 controles): val-074 A 0/3 × B 3/3 e val-087 A 0/3 × B 3/3 na saída bruta, avaliação cega **feita pelo próprio agente** (reauditoria 4C discordou de 2 classificações). A S1 está **desligada por padrão**.

## 5. Testes de segurança
Ver `SEGURANCA_E_MITIGACOES.md`: 12 casos contra o modelo (injeção direta H1–H3, em documento I1–I3, revelar instruções J1–J3, induzir invenção L1–L3), 3 casos de verificador com saída simulada (N5–N7), 5 testes unitários e replays das proteções 4.4. Resultado agregado (4.1, 2 repetições): injeção direta 4/6 aprovadas (H3 reprovado por eco no campo interno `justificativa`), injeção em documento 6/6, revelar instruções 6/6, induzir invenção 6/6; sem falsa confiança nem vazamento. **Limite:** casos escritos pelo autor; sem atacante adaptativo.

## 6. Interpretação dos resultados
**O que os dados sustentam**
1. A cadeia chunking estrutural + BM25 supera a busca vetorial/híbrida **neste corpus e nestas 150 perguntas**; a recuperação é o gargalo: ≈ 31% das perguntas não têm publicação correta no top-10.
2. A política fail-closed evitou respostas completas de outra publicação (grupo B: 0 `respondida` na 4.3), ao custo de abstenção alta (79,3%) e de utilidade baixa (20,7%).
3. A verificação técnica garante literalidade e números, **não adequação semântica**: 8 de 31 respostas dadas estavam incorretas apesar de citações literais; períodos, localidades e tipo de informação exigiram proteções adicionais (4.4).
4. As proteções adicionais (M1–M5, A_DEST, A_LOC, normalização de rótulos) bloquearam padrões específicos em replay (val-130, val-149, val-083, val-087), mas parte dos bloqueios corresponde a abstenções consideradas indevidas pela auditoria (val-083) e val-087-A-r1 ainda é entregue.
5. Em testes adversariais controlados, o conjunto prompt + código se comportou como esperado em 11 de 12 casos contra o modelo, com uma falha parcial (H3).
**O que os dados não permitem concluir:** generalização para outros corpora ou perguntas reais de cidadãos; superioridade do modelo ou da quantização (nenhuma comparação); correção das respostas "dadas" (julgamento só por modelo); robustez a ataques adaptativos; desempenho integrado ao CitizenTech (não existe integração).
**Impacto para o cidadão e riscos:** ver `LIMITACOES_E_IMPACTO_CIDADAO.md`. Em resumo: respostas erradas apesar de citadas (25,8% das dadas na 4.3), abstenção excessiva, informação possivelmente desatualizada e ausência de turno múltiplo.

## 7. Índice de fontes
`docs/assistente/01…04_3`; `docs/assistente/auditoria_independente_4_3/` (+ `diagnostico_4_4/ERRATA_AUDITORIA_4_3.md`); `docs/assistente/diagnostico_4_4/` (fases 1–3, 4A–4D.7); `data_assistente/derivados/geracao_e2e_41_*.jsonl`, `geracao_isolada_*.jsonl`; `diagnostico_4_4/fase4/validacao_seletiva*.jsonl`; `docs/entrega_genai/*`.
