# CitizenTech RPA + IA — Triagem automática de solicitações à UBS

> ## ⛔ Aptidão de uso
> **A solução NÃO está apta para triagem clínica nem para encaminhamento autônomo de solicitações reais.** É um protótipo acadêmico, avaliado só com dados sintéticos e testes escritos pela própria equipe. Falhas de segurança conhecidas e **não corrigidas**: (1) um caso de **trauma craniano** ("bateu a cabeça, vomitou e está sonolento") foi classificado como vacinação e encaminhado sem revisão humana; (2) uma sondagem qualitativa mostrou que **infarto** não dispara prioridade alta (caiu em visita domiciliar, encaminhado); (3) **crise de saúde mental / tentativa de suicídio** não é reconhecida: não há categoria nem regra, e o caso foi encaminhado automaticamente. Cerca de 1 em 9 encaminhamentos automáticos nos testes estava errado. Qualquer regra de urgência futura deve ser uma **etapa separada**, com critérios revisados por profissionais de saúde.

FIAP · Tecnólogo em Inteligência Artificial · Global Solution 2026.2 · AI for Robotic Process Automation

**Integrantes:** Henry Gimenez - 563217; Gustavo Balbo - 561711; Vinícius Araújo - 564504

## Problema
Nas Unidades Básicas de Saúde (UBS), pedidos chegam por telefone, formulário e app: marcar consulta, vacina, medicamento em falta, resultado de exame, visita domiciliar, reclamações, dúvidas… e, misturados a eles, **relatos de possível emergência** ("dor no peito", "bebê com febre e respirando mal"). A triagem é manual: cada mensagem é lida e encaminhada. O resultado é **demora, encaminhamento errado e risco de um caso grave ficar parado na fila**.

## Público afetado
- **Usuários do SUS**, em especial idosos, gestantes, famílias com crianças e pessoas acamadas, que dependem da UBS e têm pouco acesso a alternativas privadas.
- **Equipes das UBS** (recepção, farmácia, vacina, agentes comunitários), sobrecarregadas com triagem repetitiva.

## Objetivo da solução
Um robô que, sem intervenção, lê a caixa de entrada de solicitações, **valida, classifica por IA, define o setor responsável e a prioridade, enriquece o endereço via API pública, gera protocolo e resposta ao cidadão**. O robô **não faz diagnóstico nem orientação clínica**: quando há sinal de urgência ou a IA não tem confiança, ele **passa o caso a um profissional** e informa o cidadão (aviso padrão: SAMU 192 / UPA).

## Arquitetura e funcionamento
```
data/inbox (CSV/TXT)
  └─► [1 Captura RPA] ingestao.py ── arquivo ausente/corrompido → log, segue
        └─► [2 Validação] validacao.py ── texto vazio/curto, CEP inválido → rejeitados.csv
              └─► [3 Idempotência] estado.py (SQLite, hash) ── duplicado → ignorado
                    └─► [4 IA] classificador.py  TF-IDF palavras+caracteres + Regressão Logística (fallback: palavras-chave)
                          └─► [5 Regras] regras.py  setor, urgência clínica, revisão humana
                                └─► [6 API] geo.py  ViaCEP: timeout + retry exponencial + circuit breaker
                                      └─► [7 Saída] resposta ao cidadão + saida/*.csv + relatorio_execucao.json
```
**Regras de segurança:** prioridade alta (termos de risco ou categoria `sintomas_urgentes`) ⇒ **sempre** revisão humana, meta de 1 h; confiança < 0,45 ⇒ revisão humana. Cada registro roda em `try/except`; uma falha isolada é logada e o lote continua. CPF/e-mail/telefone são mascarados antes de qualquer saída. Só o **CEP** (dado público) vai à API externa, nunca o texto.

Categorias (8): agendamento_consulta, vacinacao, medicamentos, exames_resultados, visita_domiciliar, reclamacao_atendimento, informacoes_gerais, sintomas_urgentes.

## Tecnologias
Python (sintaxe exige ≥ 3.10; **testado apenas com Python 3.14.2 no Windows 11**; uma execução em ambiente virtual novo foi relatada, mas **não há log preservado**) · scikit-learn · requests · SQLite (stdlib) · pytest. Tudo gratuito, **sem chaves obrigatórias**, sem LLM.

## Temas da disciplina aplicados
Resumo (detalhes e justificativas em [`docs/temas.md`](docs/temas.md)):

| Tema | Onde no fluxo | O que resolve |
|---|---|---|
| Automação de processos com RPA (captura, leitura de arquivos, orquestração) | `ingestao.py`, `pipeline.py` | Lê a caixa de entrada e executa a triagem sem humano |
| IA/NLP — classificação de texto com ML | `texto.py`, `classificador.py` | Decide o setor a partir de texto livre |
| Regras de negócio / regras inteligentes | `regras.py` | Urgência clínica, SLA e quando exigir revisão humana |
| Integração com API e resiliência (retry, timeout, logs, idempotência) | `geo.py`, `estado.py`, `logs.py` | Enriquece endereço e sobrevive a falhas |

## Instalação e configuração
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```
`requirements.txt` aceita versões recentes. As versões **exatas** da auditoria estão em `requirements-congelado.txt` (scikit-learn 1.9.1, numpy 2.4.4, joblib 1.6.0); use-as se o modelo salvo não carregar. Foi relatado que, em ambiente novo, `numpy 2.5.4` também funcionou (**sem log preservado**; não é uma evidência arquivada).

**Chaves:** nenhuma é necessária. Para ajustar parâmetros (timeout, retries, limiar), copie `.env.example` para `.env` (ignorado pelo Git). Se algum dia integrar uma API paga ou LLM, a chave deve ficar **apenas** no `.env`. A API de CEP (ViaCEP) é pública e gratuita; sem internet o robô continua e marca o endereço como `indisponivel`.

## Como executar
```bash
python main.py --reset
```
Lê `data/inbox/` (dados **sintéticos**: 24 solicitações em CSV, 1 TXT, 1 CSV com colunas erradas e 1 corrompido) e grava em `saida/`: `resultados.csv`, `revisao_humana.csv`, `rejeitados.csv`, `relatorio_execucao.json`; logs em `logs/execucao.log`. Uma amostra dessas saídas está em [`docs/exemplo_saida/`](docs/exemplo_saida/). Rodar de novo **sem** `--reset` demonstra a idempotência (0 processados, tudo duplicado). Esperado: `21 processados, 4 para revisao humana, 3 rejeitados, 1 duplicados` (o tempo, 10–22 s, depende da rede).

**Modelo congelado.** O modelo (`data/modelo/classificador.joblib`) é **versionado** e usado como está; o `main.py` não o sobrescreve (se o arquivo não carregar por versão de biblioteca, re-treina só em memória). `python main.py --treinar` ou `python scripts/gerar_treino.py` **alteram** treino/modelo e invalidam o congelamento (a auditoria passará a abortar). Use apenas se a intenção for criar uma nova versão.

## Como executar os testes, a validação e a auditoria
```bash
python -m pytest -q             # 21 testes automatizados
python scripts/validar.py       # métricas -> docs/evidencias_resultados.md/.json
python scripts/auditoria.py     # confere hashes do congelamento e gera docs/auditoria_resultados.md/.json
```
Em um clone novo, rode `python scripts/auditoria.py` primeiro: ele confere se treino, testes, modelo e regras são idênticos aos de `docs/modelo_congelado.json` e aborta se não forem.

## Onde estão as evidências
| O que | Arquivo |
|---|---|
| Resultados da validação (gerado) | [`docs/evidencias_resultados.md`](docs/evidencias_resultados.md) |
| Evidências comentadas e casos de teste | [`docs/evidencias.md`](docs/evidencias.md) |
| Auditoria da IA, erros e riscos | [`docs/auditoria_ia.md`](docs/auditoria_ia.md), [`docs/auditoria_resultados.md`](docs/auditoria_resultados.md) |
| Modelo congelado (parâmetros, hashes, vocabulário) | [`docs/modelo_congelado.json`](docs/modelo_congelado.json) |
| Exemplo de saída do robô | [`docs/exemplo_saida/`](docs/exemplo_saida/) |
| Capturas de tela reais da execução (13 arquivos: 10 evidências obrigatórias + 3 extras: `01b`, `04b` e `11`) | [`docs/evidencias_visuais/`](docs/evidencias_visuais/) · índice em [`docs/checklist_entrega.md`](docs/checklist_entrega.md) |
| Requisitos do enunciado × projeto | [`docs/matriz_requisitos.md`](docs/matriz_requisitos.md) |
| Quadro de temas · Ética, dados e ODS | [`docs/temas.md`](docs/temas.md) · [`docs/etica_ods.md`](docs/etica_ods.md) |

## Resultados da validação
> **Leia antes:** o protótipo **não está validado para uso real**. Auditoria completa em [`docs/auditoria_ia.md`](docs/auditoria_ia.md); modelo congelado em `docs/modelo_congelado.json`.

Medidos com `python scripts/validar.py` e `python scripts/auditoria.py` (pipeline completo: IA + regras), em dois testes escritos pela própria equipe (nenhum é independente):

| | Teste 1 (n=80) | Teste 2 (n=40) | Combinado (n=120) |
|---|---|---|---|
| Acurácia da IA | 87,5% | 82,5% | 85,8% |
| Erros entre encaminhados automaticamente | 6/57 (10,5%) | 3/27 (11,1%) | **9/84 (10,7%)** |
| Enviados a humano | 23 | 13 | 36 |
| Urgências protegidas (prioridade alta + humano) | 10/10 | **4/5** | **14/15** |

*“Encaminhado automaticamente” = status `encaminhado` do robô (sem humano), que já desconta os casos mandados a humano pelas regras de urgência. Em `docs/evidencias.md` e `docs/evidencias_resultados.md` aparece também uma contagem “por confiança ≥ 0,45” (67/80 e 30/40), que é **outro conceito**; a conciliação está em `docs/evidencias.md`, seção “Esclarecimentos sobre contagens”.*

- **Falha de segurança conhecida:** no teste 2, "meu filho bateu a cabeça, vomitou e está sonolento" foi classificado como vacinação e encaminhado sem revisão humana. Uma sondagem qualitativa também mostrou que "infarto" e "tentativa de suicídio" não disparam prioridade alta, e não há categoria para saúde mental. **Não foram corrigidos**: modelo, treino, dados, testes e regras permanecem congelados desde a auditoria.
- Baseline de palavras-chave: 58,8% e 50,0%. Versão anterior do modelo (360 textos, só palavras): 73,8% e 67,5% — **não reproduzível a partir do repositório** (relatado em sessão de desenvolvimento, sem script nem log preservados; o treino e o modelo daquela versão não foram guardados).
- **Ponta a ponta** — 25 registros lidos: 21 processados, 3 rejeitados, 1 duplicado, 2 arquivos ruins tratados, 0 erros; esperado = obtido (10–22 s conforme a rede).
- **Falha tratada** — com a API de CEP fora do ar, os 21 registros foram processados (retry + circuit breaker). **Idempotência** — segunda execução: 0 reprocessados.
- **Validação independente:** estrutura pronta em [`validacao_independente/`](validacao_independente/README.md), **não executada**. Nenhum resultado independente existe.

## Limitações conhecidas
- Treino de 640 textos **sintéticos por template**; testes pequenos (80 e 40) escritos e vistos pela equipe de desenvolvimento, com contaminação parcial (o teste 1 foi analisado antes da ampliação do treino; a configuração foi escolhida entre 4 opções olhando os testes). Os números **não representam mensagens reais**.
- Erros de alta confiança (ex.: 0,93) não são detectáveis pelo limiar de 0,45, que não foi calibrado. Cerca de 1 em 9 encaminhamentos automáticos errou nos testes.
- Urgência por palavras-chave **não substitui classificação de risco clínica**; já falhou em um caso medido. Sem categoria de saúde mental, sem tratamento de negação, abreviações ou múltiplos pedidos no mesmo texto.
- Categorias e termos de urgência **não foram validados por profissional de saúde**.
- Só 8 categorias; textos fora do escopo tendem a cair em alguma delas.
- A resposta ao cidadão é um template; nada é enviado. Alguns CEPs de exemplo não existem na ViaCEP (`indisponivel`). O estado de idempotência é SQLite local.

## Recomendações de uso seguro
Resumo (detalhes em [`docs/auditoria_ia.md`](docs/auditoria_ia.md)): não usar em produção; se piloto, **modo sombra** com decisão humana em tudo; qualquer menção a sintoma vai a humano; confirmação humana em medicamentos e exames; validação clínica e nova validação independente antes de qualquer mudança de regra.

## Proteção de dados, ética e ODS
Ver [`docs/etica_ods.md`](docs/etica_ods.md). Resumo: dados de saúde são sensíveis (LGPD) — aqui só há dados sintéticos, com mascaramento de PII, envio externo restrito ao CEP, sem diagnóstico automatizado, **revisão humana obrigatória** em urgência e baixa confiança. ODS 3 (saúde e bem-estar), 10 (redução das desigualdades) e 16 (instituições eficazes).

## Estrutura
```
main.py              ponto de entrada único
citizentech/         módulos (ingestão, validação, IA, regras, API, pipeline)
data/                inbox sintética, treino sintético, 2 testes rotulados, modelo congelado
scripts/             gerar_treino.py, validar.py, auditoria.py
tests/               pytest
docs/                diagnóstico, temas, evidências, auditoria da IA, modelo_congelado.json, matriz de requisitos, ética/ODS, enunciado, exemplo_saida
requirements*.txt    dependências (faixa) e versões exatas da auditoria
.gitignore, .gitattributes   segredos fora do Git; bytes preservados (hashes do congelamento)
validacao_independente/  protocolo e avaliador único do conjunto independente (não executado)
```
