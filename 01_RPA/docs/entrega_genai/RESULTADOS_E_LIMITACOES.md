# Resultados e limitações

Cada tabela abaixo pertence a **um** conjunto/rodada e não deve ser somada ou comparada com outra. Números copiados dos relatórios originais (indicados); nenhuma rodada, geração ou teste foi executado nesta atividade. **Nenhum resultado aqui é validação independente.** "Auditoria" abaixo = julgamento feito por modelo de linguagem (o agente de desenvolvimento ou instância do mesmo modelo), **não** revisão humana.

## A. Recuperação (150 perguntas de validação; `03_retriever.md`) — desenvolvimento
| `est300o30` | R@1 | R@5 | R@10 | MRR | ≥1 pub. correta @10 |
|---|---|---|---|---|---|
| BM25 (usado) | 0,246 | 0,491 | 0,578 | 0,434 | 0,687 |
| Vetorial (e5-small) | 0,185 | 0,371 | 0,450 | 0,316 | 0,533 |
| Híbrido RRF k=60 | 0,219 | 0,458 | 0,559 | 0,396 | 0,653 |
≈31% das perguntas não têm publicação correta nos 10 primeiros documentos (BM25). Cobertura total de perguntas MULTI ≈ 10–17% conforme a configuração. Latência: consulta BM25 ≈ 1,7 ms (mediana); indexação ≈ 34 min por configuração (CPU).

## B. Gerador, avaliação isolada (39 casos × 2 repetições; contextos montados pelo autor) — desenvolvimento
Prompt v2 (Etapa 4): **69/74 critérios aprovados, 0 falsas confianças** (v1 re-julgada: 56/74 e 13 falsas confianças); JSON válido em 76/76; 0 tokens de raciocínio; 0 vazamentos do prompt; injeções de instrução em documentos não obedecidas. Critério corrigido após a v1 e os 3 pares não unívocos orientaram a v2 → resultado otimista.

## C. Rodadas end-to-end históricas (150 perguntas de validação, rodada única cada) — diagnóstico, não generalização
| Rodada (`run_id`) | Política | Resultado documentado |
|---|---|---|
| Etapa 4 | v2 | 19 de 72 perguntas sem fonte correta receberam resposta confiante com dados de outras publicações → não aprovado |
| 4.1 (`20261113-173721`) | `fail-closed-4.1` | 0 respostas "completas" sem fonte correta; 19 respostas de outra instância entregues como `parcial` (com aviso) |
| 4.2 (`20261114-014826`) | `fail-closed-4.2` | completas 2→10; parciais 41→24; ambíguas 58→67; abstenção 71,3%→77,3%; respostas do grupo B 19→13 |
| 4.3 (`20261114-130608`) | `fail-closed-4.3` | abstenção 79,3% (119 de 150); nenhuma resposta completa de outra publicação |
Estas contagens são **status do sistema**, não correção semântica.

## D. Auditoria da rodada 4.3 (150 perguntas; julgamento do agente, não humano) — `auditoria_independente_4_3/`
| Indicador | Valor |
|---|---|
| Respostas dadas (`respondida` + `parcial`) | 31 de 150 (20,7%) |
| ... corretas / corretas, mas parciais / incorretas | 7 / 16 / **8** |
| Abstenções | 119: 53 ambíguas de fato; 10 corretas; **56 indevidas** (o corpus permitia ao menos resposta parcial) |
| Grupo A (fonte correta enviada) | 20 dadas: 7 corretas, 11 parciais, 2 incorretas |
| Grupo B (fonte correta não enviada) | 11 dadas: 0 corretas, 5 parciais, 6 incorretas |
Achados: as 8 incorretas passam em toda a verificação técnica (citação literal ≠ resposta correta); o sistema é conservador demais. A auditoria recomendou **não integrar ao Zelo**. A **errata** (`diagnostico_4_4/ERRATA_AUDITORIA_4_3.md`) corrige três atribuições (val-050, val-062, val-097); 27 casos têm "confiança baixa" do auditor.
Diagnóstico 4.4 dos 56 abstenções indevidas: 8 falsos positivos do verificador; 25 por recuperação/contexto; 19 por geração com o documento no contexto.

## E. Candidata atual — replays offline das 150 saídas gravadas da 4.3 (sem modelo)
- Com a candidata `fail-closed-4.4.4d1-cand`, o replay **entrega 30** das 150 (a rodada 4.3 original entregou 31). Nas 4D.1: **0 diferenças** de status/resposta/problemas entre a versão anterior e a atual nos 150 e nos 21 registros.
- Casos bloqueados por mecanismos novos: val-087 (rótulo `titular` incompatível), val-130 (localidade), val-149 (publicação sem vínculo com a localidade), val-083 (destinatário). Isso **não** foi validado por revisão humana: val-083 é abstenção considerada indevida pela auditoria da 4.3.

## F. Validação seletiva da Fase 4B (21 gerações reais; só val-074, val-087 e 3 controles) — dev
Avaliação cega **procedimental** feita pelo mesmo agente; sem humano. Resultados na saída bruta: val-074 **A (sem S1) 0/3** corretas × **B (com S1) 3/3**; val-087 **A 0/3 × B 3/3**; controles estáveis. Pipeline: val-074-B continua `ambigua` (regra de janela do catálogo); val-087-A-r1 foi **entregue como `parcial` com "no Gama" não sustentado** e **continua assim** na candidata (4D.2). A reauditoria 4C discordou de 2 classificações e recomendou revisão humana. A flag S1 (`priorizar_atributo`) **permanece desligada por padrão**; os resultados B só valem com ela ligada.

## G. Testes automatizados
`python -m pytest citizentech/assistente/tests -q`: **337 passaram ao fim da 4D.1** (relatório FASE4D1; contagens citadas nos relatórios: 137 (Etapa 4), 163 (4.1), 174 (4.2), 183–185 (4.3; o relatório cita os dois valores), 262 (Fase 3 da 4.4), 337 (4D.1)). Fases 4D.2–4D.7 não alteraram a suíte. **Não reexecutado nesta atividade; reconfirmação pendente.** Todos usam cliente simulado (sem modelo). Os testes verificam comportamento do código e replays de casos conhecidos; **não** medem qualidade em dados novos.

## H. Diagnósticos 4D.3–4D.7 — protótipos, **não** parte da candidata
Cada conjunto é separado; rótulos de um só autor, sem segundo avaliador.
- **Sintéticos 4D.5 (26 casos / 27 alvos):** falsos vínculos aceitos — mesma frase (N1) 0, frases adjacentes (N2) 0, mesmo chunk (N3) 7, mesma publicação (N4) 8. **Reais 4D.5 (5 casos / 7 alvos):** N1/N2 0 falsos vínculos; N3 2; N4 2. Ajustados a esses mesmos casos; **não generalizam**.
- **4D.6, políticas de veto (sintéticos 27 / reais 7):** V1 (veto por contradição explícita) aceita 1–2 falsos vínculos sintéticos e 0–1 reais, sem rejeitar legítimas; V2 (veto por ausência) rejeita relações legítimas/documentais. Depende de um inventário manual de entidades.
- **4D.7:** após corrigir a regex do protótipo, 1 de 34 alvos mudou (val-083 VITAMINA D, N1/N2 de `coocorrencia` para `explicita`); sem regressões.

## I. Limitações
- **Gabaritos:** respostas de referência geradas por LLM; erros conhecidos (ex.: val-024); 6 perguntas não unívocas; 16 de 36 MULTI com associação frouxa.
- **150 casos de desenvolvimento:** reusados em todas as decisões (chunking, retriever, prompts, políticas, mecanismos, replays); não medem generalização. O conjunto de teste de 350 não foi usado.
- **Sem segundo avaliador humano:** auditoria 4.3, diagnóstico 4.4, avaliação cega 4B, reauditoria 4C e rótulos sintéticos/reais 4D foram feitos pelo agente de desenvolvimento. Um pacote cego de revisão humana (4D.4) foi **preparado e nunca respondido**.
- **Utilidade baixa por desenho:** ≈ 20% das perguntas recebem resposta; ≈ 47% das abstenções (56/119) foram indevidas segundo a auditoria; respostas dadas incorretas: 8 de 31 (25,8%).
- **Problemas que permanecem sem solução:** (1) val-087-A-r1 entregue com localização herdada da pergunta e não sustentada (a premissa "termo da pergunta não precisa de apoio" é compartilhada por `termos_de_uso`, `alinhamento` e `afirmacoes_nao_sustentadas`); (2) regra de janela do catálogo gera falsa `ambigua` (val-074-B); (3) associação entidade–localidade (val-024: "no Hospital Regional de Ceilândia" entregue sem apoio); (4) política de evidência positiva e taxonomia de status (`insuficiente` × `fora_do_escopo` não confiável); (5) respostas "corretas, mas parciais" que repetem nomes da pergunta.
- **Ambiente:** 16 GB de RAM; `llama-server` cresce a cada requisição (≈ 5,4→7,6 GB), exigindo recarregar o modelo a cada ≈ 3 gerações e fechar outros aplicativos; execuções de modelo não são determinísticas (sem *seed*).
- **Zelo:** **nenhuma integração foi realizada**; o módulo está **explicitamente não aprovado** para o Zelo (auditoria 4.3 e relatórios 4.1–4.3).
- **Dados:** corpus administrativo do DODF-DF, não informação ao cidadão; corpus complementar (gov.br/SUS) não coletado.
- **Reprodutibilidade:** não há arquivo de dependências do Gen AI; o repositório não tem commits; o prompt bruto enviado ao LM Studio não foi gravado (contextos reconstruídos deterministicamente, com hash idêntico).
