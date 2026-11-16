# Roteiro de apresentação — CitizenTech RPA + IA (Global Solution 2026.2)

> **Campos que dependem do grupo (preencher antes de apresentar):** Integrantes: Henry Gimenez - 563217; Gustavo Balbo - 561711; Vinícius Araújo - 564504 (conforme `README.md:8`; o grupo deve confirmar) · Turma: `____________` · Nomes oficiais dos temas da disciplina: `____________` · Prazo/data da apresentação: `____________`.
> Tempo estimado: ~12 min (4 min de execução ao vivo). Todos os comandos e saídas abaixo foram **executados** em 10/11/2026 (Windows 11, Python 3.14.2); o tempo depende da rede (a API de CEP é pública e externa).

## 0. Preparação (fazer antes, fora da apresentação)
Na pasta do projeto, com o ambiente virtual ativo e `pip install -r requirements.txt` já feito:
```bash
python -m pytest -q
python scripts/auditoria.py
```
Esperado: `21 passed` e `Integridade OK: todos os hashes conferem com docs/modelo_congelado.json`. Deixe abertos: `README.md`, `docs/auditoria_resultados.md` (matriz de confusão), `docs/matriz_requisitos.md` e uma pasta com os arquivos de saída. **Dica:** abra o `.csv` no editor de texto, ou no Excel com codificação UTF-8 (os arquivos usam UTF-8 com BOM).

## Sequência da apresentação

### 1. Problema (1 min)
Nas UBS, pedidos chegam por telefone, formulário e app (consulta, vacina, remédio, exame, visita, reclamação…) e, misturados, relatos de possível emergência. A triagem é manual: lenta, sujeita a encaminhamento errado e a um caso grave ficar parado na fila. *(README → "Problema")*

### 2. Público beneficiado (30 s)
Usuários do SUS (idosos, gestantes, famílias com crianças, pessoas acamadas) e as equipes da UBS (recepção, farmácia, vacina, agentes comunitários). *(README → "Público afetado")*

### 3. Proposta da solução (45 s)
Um robô que lê a caixa de entrada sozinho, valida, classifica por IA, define setor e prioridade, enriquece o endereço via API pública, gera protocolo e resposta e **separa o que não deve decidir sozinho para um profissional**. Ele **não** faz diagnóstico nem orientação clínica. Dados 100% sintéticos.

### 4. Arquitetura técnica (1 min)
Mostre o diagrama do README (7 etapas): captura → validação → idempotência → IA → regras → API de CEP → saída. Módulos em `citizentech/`; ponto de entrada único `main.py`. Temas da disciplina aplicados (confirmar os nomes oficiais): RPA de arquivos e orquestração; IA/NLP de classificação de texto; regras de negócio; integração com API e resiliência. *(docs/temas.md)*

### 5. Funcionamento da automação RPA (1 min)
Explique, mostrando `data/inbox/`: 4 arquivos de entrada — `solicitacoes_lote1.csv` (24 pedidos), `solicitacao_E100.txt` (1 pedido), `lote_sem_coluna.csv` e `lote_corrompido.csv` (arquivos defeituosos de propósito). O robô lê tudo, trata cada registro de forma isolada, não duplica protocolos (hash + SQLite) e gera relatórios.

### 6. Aplicação da IA (1 min)
TF-IDF de palavras (1–2-gramas) + de caracteres (3–5-gramas) → Regressão Logística, 8 categorias, treinada em 640 textos **sintéticos**. A probabilidade vira a "confiança": abaixo de 0,45 o caso vai a humano. Mostre `docs/modelo_congelado.json` (hashes, parâmetros) para evidenciar que o modelo está congelado.

### 7. Demonstração do processamento (1,5 min) — **ao vivo**
```bash
python main.py --reset
```
Saída esperada (resumo; as linhas de log aparecem antes):
```
... | ERROR   | Falha ao ler lote_corrompido.csv: UnicodeDecodeError: ...
... | ERROR   | Falha ao ler lote_sem_coluna.csv: ValueError: coluna obrigatoria 'texto' ausente
... | INFO    | Lido solicitacao_E100.txt: 1 registro(s)
... | INFO    | Lido solicitacoes_lote1.csv: 24 registro(s)
... | WARNING | Registro S015 rejeitado: cep_invalido
... | WARNING | Registro S016 rejeitado: texto_vazio
... | WARNING | Registro S017 rejeitado: texto_curto_demais
... | INFO    | Registro S019 duplicado (ja processado) - ignorado
OK: 21 processados, 4 para revisao humana, 3 rejeitados, 1 duplicados. Saidas em ...\saida
```
O que mostrar:
- `saida/resultados.csv`: **S001** ("Quero marcar uma consulta…") → `agendamento_consulta`, `encaminhado`, prazo 72 h, cidade preenchida pela API de CEP. **S010** e **S018** → o e-mail, o CPF e o telefone fictícios aparecem como `[EMAIL]`, `[CPF]`, `[TEL]` na coluna `texto_anonimizado` (mascaramento).
- `saida/rejeitados.csv`: S015 (CEP inválido), S016 (vazio), S017 (curto demais).
- `saida/relatorio_execucao.json`: totais da execução (lidos, processados, rejeitados, duplicados, revisão humana, tempo).
- **Idempotência** (opcional, 20 s): `python main.py` (sem `--reset`) → `OK: 0 processados, 0 para revisao humana, 3 rejeitados, 22 duplicados`.

### 8. Demonstração de encaminhamento para revisão humana (1,5 min)
Abra `saida/revisao_humana.csv`. Devem aparecer 4 casos (todos `prioridade = alta`, prazo `1 h`, setor "Classificacao de Risco (profissional de saude)" (grafia sem acento, como está no arquivo)):
- **S008** "dor forte no peito e falta de ar" (confiança 0,978), **S009** "bebê… febre alta… respira com dificuldade" (0,989) e **S022** "meu pai desmaiou… boca torta" (0,986): urgências reais, enviadas a humano.
- **S014** "Preciso de ajuda com um problema, podem verificar?" (confiança 0,37): texto vago; o modelo o colocou em `sintomas_urgentes` e o robô o enviou a humano. **Fale com franqueza:** é um caso de excesso de cautela, não de acerto.
- Leia a coluna `resposta_ao_cidadao`: protocolo + "será analisada por um profissional" + **aviso de que o canal não é de emergência (SAMU 192 / UPA)**.
- Regra: prioridade alta (termos de risco ou categoria urgente) **sempre** vai a humano; confiança < 0,45 também. O robô nunca "resolve" urgência sozinho. *(citizentech/regras.py)*

### 9. Demonstração de tratamento de falha (1,5 min) — **ao vivo**
Simule a API de CEP fora do ar (PowerShell; mantém a `saida/` normal intacta):
```powershell
$env:CEP_API_URL="http://127.0.0.1:9/{cep}"; $env:CEP_TIMEOUT_S="1"; $env:CEP_BACKOFF_S="0.3"
python main.py --reset --saida saida\falha
Remove-Item Env:CEP_API_URL,Env:CEP_TIMEOUT_S,Env:CEP_BACKOFF_S
```
Em bash: `CEP_API_URL="http://127.0.0.1:9/{cep}" CEP_TIMEOUT_S=1 CEP_BACKOFF_S=0.3 python main.py --reset --saida saida/falha`.
Mostre no log: para cada um dos 3 primeiros CEPs, `tentativa 1/3 falhou (ConnectTimeout)`, `2/3`, `3/3` com espera crescente (backoff exponencial) e, **depois dos 3 CEPs, nenhuma nova tentativa** (circuit breaker aberto). Resultado: o mesmo `OK: 21 processados, 4 para revisao humana, 3 rejeitados, 1 duplicados` — o lote **não parou**; a coluna `fonte_cep` fica `indisponivel` (20 casos) ou `sem_cep` (1). Em seguida restaure o estado normal: `python main.py --reset`.
Também já demonstrados na mesma execução: arquivo corrompido, arquivo sem coluna, texto vazio/curto, CEP inválido e duplicado.

### 10. Resultados dos testes (1 min)
Mostre `docs/auditoria_resultados.md` e a tabela do README (números **medidos**, em 2 testes escritos pela própria equipe):

| | Teste 1 (n=80) | Teste 2 (n=40) | Combinado (n=120) |
|---|---|---|---|
| Acurácia da IA | 87,5% | 82,5% | 85,8% |
| Erros entre os encaminhados automaticamente | 6/57 (10,5%) | 3/27 (11,1%) | **9/84 (10,7%)** |
| Enviados a humano | 23 | 13 | 36 |
| Urgências protegidas (prioridade alta + humano) | 10/10 | **4/5** | **14/15** |

Baseline de palavras-chave: 58,8% e 50,0%. Matriz de confusão combinada (linhas = real, colunas = previsto; ordem: agendamento, exames, informações, medicamentos, reclamação, sintomas urgentes, vacinação, visita):
```
agendamento_consulta   [13,  0,  1,  0,  0,  1,  0,  0]
exames_resultados      [ 2, 12,  0,  1,  0,  0,  0,  0]
informacoes_gerais     [ 0,  1, 10,  1,  2,  1,  0,  0]
medicamentos           [ 1,  0,  0, 12,  0,  0,  1,  1]
reclamacao_atendimento [ 1,  0,  0,  1, 13,  0,  0,  0]
sintomas_urgentes      [ 0,  0,  0,  0,  0, 14,  1,  0]
vacinacao              [ 0,  0,  0,  0,  0,  0, 15,  0]
visita_domiciliar      [ 0,  0,  0,  0,  0,  1,  0, 14]
```
Também: 21 testes automatizados (`python -m pytest -q`) e `python scripts/validar.py` (ponta a ponta: esperado = obtido).

### 11. Limitações e segurança (1,5 min) — **não pule**
Diga com clareza (README → banner "Aptidão de uso"):
- **A solução NÃO está apta para triagem clínica nem para encaminhamento autônomo de solicitações reais.**
- No teste 2, "meu filho **bateu a cabeça, vomitou e está sonolento**" foi classificado como vacinação e encaminhado **sem** revisão humana. Uma sondagem qualitativa também mostrou que "**infarto**" e "**tentativa de suicídio**" não disparam prioridade alta, e **não há categoria de saúde mental**. Nada disso foi corrigido: modelo, treino, testes e regras estão congelados desde a auditoria; corrigir é uma etapa futura, com critérios revisados por profissionais de saúde.
- Cerca de 1 em 9 encaminhamentos automáticos errou. Um erro chegou a confiança 0,93 e nenhum limiar o pegaria.
- Treino sintético por template; testes escritos e vistos pela equipe (não independentes), com contaminação parcial. A validação independente **não foi executada**; a estrutura está em `validacao_independente/`.
- O texto "S024 — parar de fumar" (fora do escopo) foi encaminhado automaticamente como agendamento: o robô não tem classe "fora do escopo".

### 12. Impacto social e ODS (30 s)
Reduz o tempo de triagem e prioriza quem pode estar em risco, beneficiando quem depende do SUS. **ODS 3** (saúde e bem-estar), **ODS 10** (redução das desigualdades), **ODS 16** (instituições eficazes e transparentes). O impacto real **não foi medido**. *(docs/etica_ods.md)*

## Plano B (se algo falhar na hora)
- **Sem internet:** a demonstração principal continua funcionando; as cidades ficam vazias e `fonte_cep = indisponivel`. Aproveite: é a própria demonstração de resiliência (a execução demora mais por causa do timeout e dos retries).
- **Saída desatualizada ou ambiente quebrado:** use as **capturas de tela** de `docs/evidencias_visuais/` (mapa etapa → imagem logo abaixo), além de `docs/exemplo_saida/` (amostra real de uma execução anterior, de 10/11/2026) e `docs/evidencias_resultados.md`. Diga com clareza que são **capturas e arquivos pré-gerados** de execuções reais, **não** uma execução ao vivo.
- **`.csv` com acentos estranhos:** é só a codificação do visualizador; abra como UTF-8.
- **Não rode** `python main.py --treinar` nem `python scripts/gerar_treino.py` durante a apresentação: alteram treino/modelo e invalidam o congelamento (`python scripts/auditoria.py` passaria a abortar).

### Plano B: mapa etapa do roteiro → captura (`docs/evidencias_visuais/`)
Se a demonstração ao vivo falhar em uma etapa, mostre a imagem correspondente. Todas existem na pasta; as marcadas **(extra)** não eram obrigatórias.

| Etapa do roteiro | Captura | O que ela mostra | Observação |
|---|---|---|---|
| §0 Preparação (testes) | `01_testes_pytest_21_passed.png` · `01b_testes_pytest_painel_terminal_do_app.png` **(extra)** | `python -m pytest -q` → `21 passed` | A `01b` é o painel de Terminal do app (estreito) |
| §0 Preparação (integridade) e §6 modelo congelado | `02_auditoria_integridade_ok.png` | `python scripts/auditoria.py` → `Integridade OK` e os SHA-256 dos 6 arquivos protegidos | **Não mostra** os parâmetros do modelo: abra `docs/modelo_congelado.json` |
| §5 Automação RPA | `03_execucao_normal_main_reset.png` | Os logs da leitura da caixa de entrada: 2 arquivos defeituosos e a leitura de `solicitacao_E100.txt` (1) e `solicitacoes_lote1.csv` (24) | **Não há captura** da listagem da pasta `data/inbox/` |
| §7 Processamento | `03_execucao_normal_main_reset.png` · `04a_resultados_csv_tabela.png` | Execução `python main.py --reset` (21 processados, 4 para revisão humana, 3 rejeitados, 1 duplicado) e o resultado por registro | A `04a` é uma **visão tabular** do `resultados.csv`, não o CSV cru |
| §7 Mascaramento de dados pessoais | `04b_resultados_csv_mascaramento_pii.png` **(extra)** | S001 encaminhado; S010 e S018 com `[EMAIL]`, `[CPF]`, `[TEL]` | Visão com `Format-List` |
| §7 Rejeitados e relatório | `06_rejeitados_e_relatorio_execucao.png` | Motivos das 3 rejeições e o `resumo` do `relatorio_execucao.json` | O JSON aparece **cortado em 19 linhas**, como indica o comando na imagem |
| §7 Idempotência (opcional) | `11_idempotencia_segunda_execucao.png` **(extra)** | `python main.py` sem `--reset` → 0 processados, 22 duplicados | |
| §8 Revisão humana | `05_revisao_humana_csv.png` | S008, S009, S014 e S022 com prioridade alta, prazo de 1 h e a resposta com o aviso 192 | Visão com `Format-List` |
| §9 Tratamento de falha | `07_falha_api_cep_retry_circuit_breaker.png` | API de CEP fora do ar: 3 tentativas por CEP em 3 CEPs, sem novas tentativas depois, `falhas_http_cep: 9` e `OK: 21 processados…` | Os 9 vêm do padrão de 3 tentativas; o `evidencias_resultados.md` mostra 6 (2 tentativas); ver `docs/evidencias.md`, "Esclarecimentos sobre contagens" |
| §10 Resultados dos testes | `08_matriz_confusao_combinada.png` (e `01`) | Matriz de confusão do conjunto combinado (n=120), com 85,8% de acurácia, 9 erros em 84 encaminhados sem humano e urgências 14/15 | A tabela comparativa teste 1 × teste 2 × combinado do README **não tem captura**; abra o `README.md` |
| §11 Limitações e segurança | `09_readme_aptidao_de_uso.png` | O início do README, com o banner de que a solução não está apta para triagem clínica | Texto bruto (Markdown não renderizado) |
| Apoio (requisitos do enunciado) | `10_matriz_de_requisitos.png` | O início de `docs/matriz_requisitos.md` | Texto bruto; é só o início da matriz |

**Etapas sem captura:** §1 (problema), §2 (público), §3 (proposta), §4 (arquitetura, o diagrama está no `README.md`), §6 (parâmetros do modelo, ver `docs/modelo_congelado.json`) e §12 (impacto e ODS, ver `docs/etica_ods.md`). Para elas, use o próprio documento.

**Cuidados ao usar as capturas:**
- São de execuções reais feitas em **11/11/2026** na máquina de desenvolvimento (Windows, Python 3.14.2); os horários e os `run_id` diferem dos de uma execução ao vivo, e os totais (21 processados, 4 para revisão humana…) são os mesmos. As capturas `03`, `04a`, `04b`, `05` e `06` vêm da mesma execução; a `07` e a `11` vêm de execuções posteriores.
- O título de janela `EVID_xxxxxxxx`, visível na maioria das imagens, é um artefato do método de captura (cada comando foi executado em uma janela de console própria), sem relação com o projeto. O método e as limitações estão em `docs/checklist_entrega.md`, seção 3.2.
- Não há capturas de documentos Markdown renderizados nem de uma execução em outra máquina.
