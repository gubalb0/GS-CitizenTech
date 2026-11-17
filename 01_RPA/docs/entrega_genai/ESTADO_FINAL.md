# Estado final do módulo Gen AI

Registro de 2026-11-16, conferido contra os arquivos do repositório (`D:\Downloads\GS\RPA`). Fonte dos números: relatórios originais (ver `RESULTADOS_E_LIMITACOES.md`).

## 1. Versão candidata
`geracao.VERSAO_POLITICA = "fail-closed-4.4.4d1-cand"` — **candidata, não validada, não aprovada para integração ao Zelo.** Prompt v3. Retriever congelado: `est300o30`, BM25, top-5. Flag `priorizar_atributo` = `False` (padrão do código). Hashes SHA-256 (16 primeiros caracteres) conferidos nesta atividade e por `scripts/verificar_hashes.py` (**TODOS CONFEREM: True**):

| Arquivo | Hash |
|---|---|
| `citizentech/assistente/geracao.py` | `c857b99f49947e1a` (= snapshot `data_assistente/versoes/geracao_44_fase4d1.py`) |
| `citizentech/assistente/evidencias.py` | `12118192b9529075` (= `evidencias_44_fase4d1.py`) |
| `citizentech/assistente/catalogo.py` | `8e44143ba1d092f5` (inalterado desde 4A) |
Versões anteriores preservadas como snapshots em `data_assistente/versoes/` (4.1, 4.2, 4.3, 4.4 fases 2/3/4A/4B-prep/4B-cand/4D.1, com variantes `_pre`).

## 2. Funcionalidades implementadas (no código da candidata)
Ingestão e integridade do corpus; deduplicação; associação QA→publicação (avaliação); chunking `est300o30`; indexação BM25 (e vetorial e5, disponível mas não usada na consulta); recuperação BM25; montagem de contexto com orçamento ≈ 3K tokens; geração local via LM Studio (Qwen3-8B Q4_K_M, JSON Schema, `/no_think`, T=0,3); verificação independente do modelo (citação literal, números, alinhamento, afirmações sem apoio); abstenção por conflito/identificabilidade (4.2/4.3); proteções 4.4 M1–M5, A_DEST, A_LOC; registro auditável `relacoes/3` com mecanismo B (necessidade do trecho); normalização de índice de lista em rótulos (4D.1); mascaramento de PII; conferência de integridade. **Todas estão em código testado por testes automatizados (cliente simulado), mas a candidata como um todo não foi validada com revisão humana independente.**

## 3. Funcionalidades experimentais (fora da candidata)
- **S1** (seleção de contexto por rótulo do atributo, "forte" e "conservadora"): implementada atrás da flag `priorizar_atributo`, **desligada por padrão**; validada só em 21 gerações de 2 casos.
- **RRF/híbrido e índice vetorial:** avaliados no retriever (Etapa 3); não usados na consulta.
- **4D.2–4D.7:** diagnóstico do mecanismo B; conjunto sintético (30 casos); casos reais; protótipo de vínculo entidade–atributo por frase (N1–N4); políticas de veto V0–V3; protótipo corrigido `prototipo_vinculo_4d7.py`. Vivem em `docs/assistente/diagnostico_4_4/fase4/fase4d3…fase4d7/`, **fora de `citizentech/`**.

## 4. Alterações realizadas até a 4D.7
| Fase | Alteração no código da candidata? | Resumo |
|---|---|---|
| Etapas 1–3 | — | corpus, chunking, retriever |
| Etapa 4, 4.1, 4.2, 4.3 | sim | gerador, fail-closed, identificabilidade, janela MULTI |
| 4.4 Fases 1–3 | sim | medição e hashes; verificador; M1–M5 |
| 4A | sim | `relacoes/2→3`, mecanismo B, A_DEST, A_LOC |
| 4B | sim | S1 atrás de flag (desligada) |
| 4C | **não** | reauditoria das 21 gerações |
| 4D.1 | **sim (única mudança de código desde 4B)** | normalização de índice de lista; versão `4.4.4d1-cand` |
| 4D.2–4D.7 | **não** | diagnósticos e protótipos isolados |
**A correção da Fase 4D.7 pertence ao protótipo diagnóstico `prototipo_vinculo_4d7.py` (cópia isolada do protótipo da 4D.5, uma linha de regex alterada) e não foi integrada à candidata nem a qualquer módulo de execução.** Ela não altera nenhum resultado do pipeline.

## 5. Mecanismos que permaneceram fora da produção
Vínculo entidade–atributo por frase (N1–N4); políticas de veto V0–V3; correções B1/B2/C/D da exclusão de termos da pergunta; qualquer integração com o Zelo; e a própria candidata (não aprovada).

## 6. Arquivos de referência
- Relatórios por etapa: `docs/assistente/01…04_3`, `docs/assistente/auditoria_independente_4_3/` (**auditoria por modelo de linguagem, não humana**), `docs/assistente/diagnostico_4_4/` (`RELATORIO_DIAGNOSTICO_4_4.md`, `FASE1…3_REGISTRO`, `fase3/`, `fase4/FASE4A…FASE4D1/2`, `fase4d3…fase4d7/`).
- Integridade: `docs/assistente/diagnostico_4_4/hashes_referencia_44.json` (`f9502ecb9a5f52ce`), `INTEGRIDADE_ARTEFATOS.md`, `fase4/fase4d7/manifesto_hashes_4d7.json` (`0501b6a3831b7042`), `docs/modelo_congelado.json` (RPA, `56c31c8e6f02d991`).
- Dados brutos de rodadas: `data_assistente/derivados/geracao_e2e_41_{20261113-173721,20261114-014826,20261114-130608}.jsonl` e `.meta.json`; validação seletiva em `diagnostico_4_4/fase4/validacao_seletiva*.jsonl` (hashes `cbb8482916d55050`, `c198f0893d40121f`; manifesto `43fb09685404714c`).
- Relatórios chave: `FASE4D1_NORMALIZACAO_ROTULOS.md` (`388ea4f094bae2d0`), `FASE4D2_DIAGNOSTICO_MECANISMO_B.md` (`343d067c2ad1dc00`), `fase4d7/RELATORIO_4D7.md` (`79114ea4a043fbc5`).

## 7. Situação dos testes
Suíte `citizentech/assistente/tests/`: **337 passando ao fim da 4D.1** (último resultado registrado). **Não reexecutada nesta atividade** (restrição); a reconfirmação é item pendente do `CHECKLIST_ENTREGA.md`. `verificar_hashes.py` (somente leitura) foi executado e conferiu: TODOS CONFEREM. Os testes do RPA estão em `tests/` e não fazem parte deste módulo.

## 8. Limitações (resumo; ver `RESULTADOS_E_LIMITACOES.md`)
Sem revisão humana independente; 150 casos de desenvolvimento; gabaritos por LLM; utilidade ≈ 20% (31/150 respondidas na 4.3) com 8 respostas dadas incorretas; val-087-A-r1 continua sendo entregue; memória limita a execução; sem integração com o Zelo; sem arquivo de dependências do Gen AI; repositório sem commits.

## 9. Decisão de congelamento
**Congelar em `fail-closed-4.4.4d1-cand`.** Nenhuma nova alteração de código, nenhum novo protótipo e nenhuma nova rodada de benchmark fazem parte desta entrega. A candidata **não é promovida** a versão aprovada: permanece "experimental, não validada, fora do Zelo". Qualquer evolução (p.ex. revisão humana dos rótulos, correção do caso val-087-A-r1, política para eco da pergunta, integração com o Zelo) exige **autorização explícita e nova fase**; está registrada como melhoria futura, não como parte desta entrega.
