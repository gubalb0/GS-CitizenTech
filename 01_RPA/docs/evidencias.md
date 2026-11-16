# Evidências de validação

> **Atualização da auditoria:** os números de urgência e de acerto automático desta página foram revistos em [`auditoria_ia.md`](auditoria_ia.md). Em especial: urgências protegidas são **14/15** (não 10/10; o 10/10 valia só para o teste 1) e o erro entre encaminhamentos automáticos, contado como o robô decide, é **9/84 (10,7%)**, não ~10% por faixa de confiança. A validação independente **não foi executada**. Falhas de segurança conhecidas e não corrigidas: trauma craniano encaminhado como vacinação sem revisão humana (teste 2); "infarto" e "tentativa de suicídio" não disparam prioridade alta (sondagem qualitativa); sem categoria para crise de saúde mental. A solução **não está apta** para triagem clínica nem encaminhamento autônomo.

Números de execuções reais em 10/11/2026, reproduzíveis com:
```bash
python -m pytest -q          # 21 passed
python scripts/validar.py    # gera evidencias_resultados.md e .json (tabelas completas e listas de erros)
python main.py --reset       # execução ponta a ponta; ver saida/ e logs/execucao.log
```

## Conjuntos de dados
| Arquivo | Conteúdo | Uso |
|---|---|---|
| `data/treino.csv` | 640 textos sintéticos (templates + ruído, seed fixa), 8 classes | treino |
| `data/teste_rotulado.csv` | 80 textos escritos à mão (10 por classe), redação diferente do treino | teste 1 da IA |
| `data/teste_cego.csv` | 40 textos escritos à mão (5 por classe), criados antes da ampliação do treino | teste 2 da IA |
| `data/inbox/` | 24 solicitações CSV + 1 TXT + 2 arquivos defeituosos | ponta a ponta |

## Casos cobertos
- **Sucesso:** 21 registros classificados, encaminhados ou enviados a humano, com protocolo.
- **Dados inválidos:** texto vazio (S016), curto (S017), CEP inválido (S015) → `rejeitados.csv`.
- **Duplicado:** S019 = S003 → ignorado.
- **Arquivos ruins:** `lote_corrompido.csv` e `lote_sem_coluna.csv` → logados, lote segue.
- **PII:** S010 e S018 têm e-mail, CPF e telefone fictícios → mascarados.
- **Urgência:** S008, S009, S022 (+ S014 vago, tratado por cautela) → prioridade alta + revisão humana + aviso 192.
- **Fora do escopo (limitação observada):** S024 ("apoio para parar de fumar", sem categoria correspondente) foi classificado como `agendamento_consulta` com confiança 0,53 e **encaminhado automaticamente**; o robô não tem classe "fora do escopo". Só S014 (vago, conf. 0,37) foi a humano por baixa confiança, e S008, S009, S014 e S022 por prioridade alta.
- **Falha tratada:** API de CEP inacessível → circuit breaker aberto, **21/21 processados**, endereço `indisponivel`. Falhas HTTP: **6** no cenário automatizado de `scripts/validar.py` (2 tentativas por CEP × 3 CEPs) e **9** na demonstração ao vivo com o padrão de 3 tentativas (captura `07`); são dois cenários, ver "Esclarecimentos sobre contagens" abaixo.
- **Falha de modelo:** testes unitários cobrem fallback por palavras-chave e erro isolado em um registro.

## Métricas
| Medida | Teste 1 (n=80) | Teste 2 (n=40) |
|---|---|---|
| Acurácia ML (palavras+caracteres) | 87,5% (70/80); macro-F1 0,87 | 82,5% (33/40); macro-F1 0,83 |
| Acurácia baseline palavras-chave | 58,8% (47/80) | 50,0% (20/40) |
| Casos com confiança ≥ 0,45 (**contagem por confiança**; não é o "automático" do README, ver "Esclarecimentos") | 67/80, 89,6% de acerto (60/67) | 30/40, 90% de acerto (27/30) |
| Enviados a humano por baixa confiança | 13/80 (16%) | 10/40 (25%) |
| Versão anterior (360 textos, só palavras) — **não reproduzível a partir do repositório** (ver "Esclarecimentos") | 73,8% | 67,5% |

| Outras medidas | Resultado |
|---|---|
| Urgências com prioridade alta + humano (IA + regras) | teste 1: 10/10; teste 2: 4/5; combinado 14/15 |
| Falso alarme de urgência | 1/70 |
| Ponta a ponta esperado × obtido | 6/6 métricas conferem |
| Idempotência | 2ª execução: 0 processados, 22 duplicados |
| Tempo (execução normal) | 10–22 s conforme a rede, quase todo em chamadas à API de CEP |

## Análise dos erros e limites
No teste 1, dos 10 erros, 3 tiveram confiança < 0,45 e foram para humano; **7 tinham confiança ≥ 0,45** (pelo status do robô, 6 foram encaminhados sem humano; ver "Esclarecimentos") (ex.: "exames_resultados → agendamento_consulta" com confiança 0,93; informações ↔ reclamação). Os erros se concentram em categorias administrativas vizinhas. A melhoria veio de (1) ampliar o treino com frases de vocabulário geral de UBS e (2) adicionar n-gramas de caracteres ao TF-IDF. **Cuidado com a interpretação:** o teste 1 já havia sido analisado antes da ampliação, então ele é parcialmente contaminado; as frases novas não copiam os testes, mas o vocabulário se sobrepõe, e a configuração do modelo foi escolhida entre 4 opções olhando esses testes. O teste 2 é mais confiável, mas também pequeno e escrito pela equipe. Dados reais devem dar resultado pior. A regra de urgência continua sendo a rede de segurança. Ver limitações no README.

## Esclarecimentos sobre contagens (11/11/2026)
Esta seção **não altera nenhuma métrica histórica**: explica por que números aparentemente diferentes representam conceitos diferentes e marca o que não pode ser comprovado.

### 1. Duas definições de "encaminhado automaticamente"
- **Por confiança** (usada em `docs/evidencias_resultados.md`, gerado por `scripts/validar.py`, e nas linhas "confiança ≥ 0,45" acima): conta os casos cuja probabilidade máxima do modelo é ≥ 0,45.
- **Por status do robô** (usada em `README.md` e `docs/auditoria_ia.md`, gerados por `scripts/auditoria.py`): conta os casos com `status = encaminhado` em `regras.decidir()`, que **também** manda a humano os casos de prioridade alta ou da categoria `sintomas_urgentes`, mesmo com confiança alta.

A diferença é exatamente o conjunto de casos que as regras de urgência desviaram para humano apesar de confiança ≥ 0,45. Conciliação conferida em 11/11/2026 por leitura (modelo salvo e `regras.decidir`, **sem treino**; conferência feita com um script de uso único **não versionado**, então esta tabela é um registro e não um artefato reproduzível por comando do repositório):

| | Teste 1 (n=80) | Teste 2 (n=40) |
|---|---|---|
| Casos com confiança ≥ 0,45 (por confiança) | 67 (7 erros) | 30 (3 erros) |
| − desviados a humano pelas regras de urgência apesar da confiança | 10 (9 urgências corretas + 1 erro) | 3 (urgências corretas) |
| **= Encaminhados sem humano (status `encaminhado`)** | **57 (6 erros; 10,5%)** | **27 (3 erros; 11,1%)** |
| Enviados a humano por confiança < 0,45 | 13 | 10 |
| + enviados a humano pelas regras de urgência | 10 | 3 |
| **= Enviados a humano (status `revisao_humana`)** | **23** | **13** |

O erro a mais na contagem por confiança do teste 1 (7 contra 6) é "Preciso de um horário com o clínico, estou com a pressão descontrolada há semanas", classificado como `sintomas_urgentes` com confiança 0,54: errou a categoria, mas as regras o mandaram a humano. Ao falar em público, diga sempre qual definição está usando; a de referência para "automático" é a **por status** (6/57, 3/27 e 9/84 no combinado).

### 2. Falhas HTTP: 6 nos documentos e 9 na captura 07
São dois cenários distintos, não uma contradição:
- **Cenário automatizado** (`scripts/validar.py:99`): `ConsultaCEP(..., timeout=0.5, retries=2, backoff=0.05)` → 3 CEPs × 2 tentativas = **6** consultas e **6** falhas até o circuit breaker abrir (`LIMITE_FALHAS_SEGUIDAS = 3` em `citizentech/geo.py`). Resultado em `docs/evidencias_resultados.md` (seção 4): `falhas_http_cep: 6`, `consultas_cep_http: 6`.
- **Demonstração ao vivo e captura `07`**: usa o padrão `CEP_MAX_RETRIES = 3` (`citizentech/config.py`), com `CEP_TIMEOUT_S=1` e `CEP_BACKOFF_S=0.3` definidos por variável de ambiente → 3 CEPs × 3 tentativas = **9** (`falhas_http_cep: 9`, `consultas_cep_http: 9`).
- Em ambos, **20 dos 21** registros ficam com `fonte_cep = indisponivel` (`cep_indisponivel: 20` no resumo da captura `07` e em `evidencias_resultados.md`) e os 21 são processados. O registro restante é o S011, que **não tem CEP** e portanto não consulta a API (`fonte_cep = sem_cep`, visível na captura `04a`); para o cenário automatizado isso é **inferido** (21 − 20), porque `evidencias_resultados.md` guarda só a contagem de indisponíveis.

| | Cenário automatizado (`scripts/validar.py`) | Demonstração ao vivo (captura `07`) |
|---|---|---|
| URL | `http://127.0.0.1:9/{cep}` (endereço sem serviço) | a mesma |
| Timeout | 0,5 s (`validar.py:99`) | 1 s (`CEP_TIMEOUT_S=1`, variável de ambiente) |
| Tentativas por CEP | **2** (`retries=2`) | **3** (padrão `CEP_MAX_RETRIES`) |
| Espera inicial entre tentativas | 0,05 s | 0,3 s (`CEP_BACKOFF_S=0.3`) |
| CEPs consultados antes de o circuit breaker abrir | 3 | 3 |
| `consultas_cep_http` / `falhas_http_cep` | **6 / 6** | **9 / 9** |
| `cep_indisponivel` | 20 | 20 |
| Onde está registrado | `docs/evidencias_resultados.md`, seção 4 (arquivo gerado, mantido como original) | `docs/evidencias_visuais/07_falha_api_cep_retry_circuit_breaker.png` |

`docs/evidencias_resultados.md` é gerado por `scripts/validar.py` e não foi editado manualmente; por isso o **esclarecimento** de que o `6` ali se refere ao cenário automatizado (2 tentativas) está **somente nesta página**.

### 3. Resultados que não podem ser reproduzidos a partir do repositório
| Resultado | Onde aparece | Situação |
|---|---|---|
| 73,8% e 67,5% ("versão anterior": 360 textos de treino, só palavras) | `README.md` (resultados), tabela de métricas desta página | **Não reproduzível:** o `treino.csv` de 360 textos e o modelo daquela versão não foram preservados (foram substituídos pela versão de 640 textos) e não há script ou log. Valor relatado em sessão de desenvolvimento. Recomendação: manter apenas como histórico rotulado ou remover |
| "só palavras": 64/80 (80%) e 29/40 (72,5%), com o treino de 640 | `docs/perguntas_banca.md` (Q3) | **Não reproduzível:** veio de um script temporário não versionado; reproduzir exigiria treinar um modelo só de palavras, o que **não foi feito** (treinamento fora do escopo desta correção). Recomendação: manter apenas como resultado relatado ou remover |
| Comparação entre 4 configurações do TF-IDF/classificador | `docs/perguntas_banca.md` (Q1 e Q3), `README.md` (limitações), `docs/auditoria_ia.md` (ressalvas) | **Não reproduzível:** foi relatada; os resultados individuais das 4 configurações não foram preservados. O fato de a escolha ter sido feita olhando os testes permanece como **ressalva metodológica** registrada |
| Atribuição causal "a melhoria veio de ampliar o treino e de adicionar n-gramas de caracteres" | parágrafo "Análise dos erros e limites" desta página | **Hipótese**, pois depende dos dois resultados acima, que não podem ser reproduzidos |

**São reproduzíveis** (por `scripts/validar.py` e `scripts/auditoria.py`, com o modelo congelado): a acurácia do baseline de palavras-chave (58,8% e 50,0%), a acurácia final de 87,5% e 82,5%, a matriz de confusão e todas as contagens por status.

### 4. Ambiente limpo
A execução do projeto em cópia limpa com venv novo foi **relatada** em 10/11/2026 (integridade OK, `main.py` OK, 21 testes), mas **não possui log, captura ou script preservado**; não há evidência documental dela neste repositório. As capturas `01` e `03` comprovam `pytest` e `main.py` na máquina de desenvolvimento, não em ambiente limpo.
