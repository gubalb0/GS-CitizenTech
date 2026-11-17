# Transferência técnica — módulo Gen AI do CitizenTech (para Gustavo Balbo)

Escrito em 2026-11-16 a partir dos arquivos reais do repositório `D:\Downloads\GS\RPA` (cópia em `projeto/`). **A integração com o protótipo CitizenTech não foi feita nem iniciada** e é a sua tarefa. Todas as afirmações abaixo vêm de leitura do código, dos relatórios ou de uma verificação de leitura feita ao preparar este pacote (indicada como "verificado"). Nada aqui foi executado com o modelo de linguagem. Os pontos que o grupo precisa confirmar estão marcados **[CONFIRMAR]**.

## 1. Escopo e regras
- **Objetivo da sua parte:** criar uma camada de integração **isolada** que receba uma solicitação do cidadão no protótipo CitizenTech, chame o assistente Gen AI e exiba **resposta, status e fontes** (item "Implementação e integração" do barema FIAP e requisito do vídeo).
- **Não alterar** `citizentech/assistente/geracao.py`, `evidencias.py`, `catalogo.py`, o retriever, os índices, os snapshots, os manifestos nem o RPA congelado (`data/`, `citizentech/classificador.py`, `regras.py`). Os hashes estão em `projeto/docs/modelo_congelado.json` e `projeto/docs/assistente/diagnostico_4_4/hashes_referencia_44.json`; `python projeto/scripts/verificar_hashes.py projeto` deve continuar retornando `TODOS CONFEREM: True` (verificado nesta cópia).
- **Candidata:** `geracao.VERSAO_POLITICA = "fail-closed-4.4.4d1-cand"`. É uma candidata **não validada**; o Gen AI **não está aprovado** para uso real.
- **[CONFIRMAR]** Qual é exatamente o "protótipo CitizenTech" e o "Zelo" (onde está, em que linguagem, como recebe solicitações). Não encontrei nenhum protótipo, frontend ou API fora do RPA (triagem de pedidos à UBS) e da simulação de cluster; nenhum arquivo fora de `citizentech/assistente/` chama o Gen AI.

## 2. O que é o Gen AI (RAG sobre o DODF)
Assistente de perguntas e respostas sobre **publicações do Diário Oficial do DF relacionadas à saúde** (dataset `gvic-unb/dodf-saude-qa`, CC BY 4.0): 1.381 documentos (1.305 após remover 76 duplicatas exatas) e 150 perguntas de validação. Responde **somente com base nos trechos recuperados**, cita a fonte com trecho literal e **se abstém** quando a evidência não sustenta uma resposta única (*fail-closed*). É um protótipo acadêmico; o corpus é administrativo (extratos, contratos, credenciamentos), não "informação de serviço ao cidadão".

## 3. Fluxo RAG (consulta)
```
pergunta (str, ≤ 500 caracteres)
  → mascarar_pii (citizentech.texto, do RPA)                      [CPF/telefone viram marcadores]
  → Indice.buscar(modo="bm25", k=5)  — chunking est300o30, BM25 próprio (scipy)
  → montar_contexto (≤ ~3.000 tokens do Qwen3, ≤ 6 chunks; texto neutralizado como "não confiável")
  → LM Studio /v1/chat/completions (Qwen3-8B Q4_K_M, JSON Schema, /no_think, T=0,3, top_p=0,8)
  → verificação independente do LLM (citação literal, números, alinhamento, identificabilidade, proteções M1–M5/A_DEST/A_LOC)
  → RespostaGerada (status, resposta, fontes, evidencias, justificativa, verificacao, telemetria, candidatas)
```
Preparação offline (já feita; os índices estão no pacote): deduplicação → chunking `est300o30` (16.199 chunks canônicos) → BM25 + vetores e5 (os vetores existem no índice, mas a consulta usa só BM25).

## 4. Pontos de entrada (Python; não há CLI de consulta)
| Função | Onde | Função |
|---|---|---|
| `dados.carregar_corpus()` | `citizentech/assistente/dados.py` | lê o Parquet do corpus (1.381 docs) |
| `Indice.carregar(pasta)` | `retriever.py` | carrega o índice (`AE.IDX` = `data_assistente/indices/est300o30`) |
| `Catalogo.de_corpus(corpus)` | `catalogo.py` | catálogo para a abstenção por identificabilidade |
| `idx.buscar(pergunta, k=5, modo="bm25")` | `retriever.py` | devolve `list[Resultado]` (`posicao, chunk_id, doc_id, score, texto, ids_equivalentes, metadados`) |
| `ConfigGeracao()` | `geracao.py` | parâmetros (URL `http://localhost:1234/v1/chat/completions`, modelo `qwen3-8b`, `max_chunks=5`, `orcamento_tokens=3000`, `temperatura=0.3`, `top_p=0.8`, `max_tokens_saida=1100`, timeouts 5 s/180 s) |
| `ClienteLMStudio(cfg, sessao=None).disponivel()` | `geracao.py` | verifica se o servidor responde e o modelo está carregado (`sessao` permite injetar um cliente HTTP simulado em testes) |
| `gerar_resposta(pergunta, resultados, cliente, cfg, catalogo=catalogo)` | `geracao.py` | **ponto principal**; nunca levanta exceção de comunicação |
| `gerar_resposta_composta(pergunta, recuperar, cliente, cfg, catalogo)` | `geracao.py` | variante para pergunta composta (recebe uma função `recuperar`) |
Trecho (montado do código; **não executado com o modelo**):
```python
from citizentech.assistente import dados as D, geracao as G
from citizentech.assistente.catalogo import Catalogo
from citizentech.assistente.retriever import Indice
from citizentech.assistente.avaliacao_e2e import IDX
corpus = D.carregar_corpus(); idx = Indice.carregar(IDX); cat = Catalogo.de_corpus(corpus)   # inicialização: ≈ 12 s (verificado)
cfg = G.ConfigGeracao(); cli = G.ClienteLMStudio(cfg)
if cli.disponivel():
    r = G.gerar_resposta(pergunta, idx.buscar(pergunta, k=cfg.max_chunks, modo="bm25"), cli, cfg, catalogo=cat)
    saida = r.para_dict()
```
**Verificado nesta preparação (sem modelo):** com a pasta original, a inicialização acima levou ≈ 12 s, `buscar` devolveu 5 chunks para uma pergunta de teste, `montar_contexto` enviou 3 deles (≈ 2.537 tokens estimados) e `disponivel()` retornou `False` (LM Studio desligado). **Execute `python` a partir da raiz do projeto (`projeto/`)** para que `import citizentech` funcione.

## 5. Formatos
**Entrada:** uma `str` (a pergunta). Truncada em 500 caracteres; CPF e telefone são mascarados antes do prompt. Pergunta vazia ou sem trechos → `insuficiente` sem chamar o modelo. Não há histórico de conversa (turno único).
**Saída:** `RespostaGerada.para_dict()` (ou os atributos). Campos:
| Campo | Conteúdo |
|---|---|
| `pergunta` | pergunta (já mascarada) |
| `status` | `respondida`, `parcial`, `ambigua`, `insuficiente`, `fora_do_escopo` |
| `resposta` | texto para o cidadão. Em `insuficiente`/`fora_do_escopo` é **mensagem fixa** do código (ex.: "Não foi possível confirmar uma resposta nas publicações recuperadas."; "Esta pergunta está fora do que as publicações oficiais consultadas permitem responder."). Em `parcial` o texto inclui um aviso de cobertura incompleta |
| `fontes` | lista de `{id, chunk_id, doc_id, ids_equivalentes, posicao_ranking, score, edicao, data_edicao, secao, referencia, tipo_documento, numero_documento}` |
| `evidencias` | lista de `{fonte, trecho}` com o **trecho literal** do chunk citado |
| `justificativa` | motivo da abstenção (texto interno; não é mostrado ao cidadão nas abstenções) |
| `verificacao` | `{ok, problemas[], evidencia{...}}`; `problemas` traz o motivo técnico do rebaixamento (p.ex. `rotulo_incompativel_com_atributo`); `evidencia.protecao.relacoes` é o registro auditável |
| `telemetria` | modelo, temperatura, `chunks_enviados`, tokens, `latencia_s`, `erro_tecnico` (`servidor_indisponivel`, `timeout`, `resposta_invalida_do_servidor`, `vazamento_do_prompt` ou `None`), etc. |
| `candidatas` | respostas possíveis por fonte (usadas na detecção de conflito) |
Exemplos reais de saída estão em `projeto/docs/entrega_genai/ANEXO_CASOS_AVALIACAO.md` (15 casos) e nos JSONL de `projeto/data_assistente/derivados/`.

## 6. Tratamento de abstenção (o que a sua camada deve mostrar)
| Status | Significado | Sugestão de exibição |
|---|---|---|
| `respondida` | resposta completa, com fonte e trecho literal verificados | resposta + fontes + trecho |
| `parcial` | resposta incompleta ou com cobertura limitada (lista, MULTI) | resposta + aviso (já está no texto) + fontes |
| `ambigua` | mais de uma publicação plausível; o texto pede "a publicação, a data ou o contrato desejado" | mostrar o pedido de esclarecimento e as publicações candidatas (`fontes`). **Não há turno seguinte no assistente**: a camada de integração teria de reenviar uma pergunta nova |
| `insuficiente` | evidência não sustenta resposta (ou falha técnica) | mensagem fixa; se `telemetria.erro_tecnico` existir, tratar como indisponibilidade |
| `fora_do_escopo` | pergunta fora do que o corpus permite | mensagem fixa |
A distinção `insuficiente` × `fora_do_escopo` **não é confiável** (rótulo impreciso; o comportamento de abster-se está correto). Em 4.3, só 31 de 150 perguntas receberam resposta (20,7%); a abstenção alta é intencional (*fail-closed*).

## 7. Limitações que afetam a integração
- **Turno único**, sem memória de conversa e sem esclarecimento interativo.
- **Latência:** 12–21 s por pergunta (medianas); 30 s ou mais no p95. LM Studio foi usado com `parallel` 1 nas rodadas completas → serializar as chamadas.
- **Memória:** 16 GB de RAM; o `llama-server` cresce a cada requisição (até ≈ 8,2 GB de RSS) e o servidor já caiu em uma execução; o tratamento de falha devolve `insuficiente` com `erro_tecnico`.
- **Escopo do corpus:** atos administrativos do DODF-DF. O RPA do repositório classifica pedidos à UBS (agendamento, vacina, medicamentos…) — **a maior parte desses pedidos não é respondível por este corpus**. **[CONFIRMAR]** quais solicitações do protótipo vão para o Gen AI (por exemplo, a categoria `informacoes_gerais`).
- **Qualidade:** na rodada 4.3 (auditoria por modelo, sem revisão humana), das 31 respostas dadas 8 estavam incorretas apesar de citações literais; ver `projeto/docs/entrega_genai/RESULTADOS_E_LIMITACOES.md` e `LIMITACOES_E_IMPACTO_CIDADAO.md`. Problema conhecido sem correção: val-087-A-r1.
- **Sem seed**, temperatura 0,3: respostas variam entre execuções.
- **Candidata não validada**; flag `priorizar_atributo` deve ficar **`False`** (padrão).
- **Dependências:** não há arquivo de dependências validado do Gen AI (ver `projeto/docs/entrega_genai/REPRODUCAO_E_DEPENDENCIAS.md`).

## 8. Como implementar a camada de integração isolada (recomendações; **não implementado**)
1. **Onde:** um módulo/pasta **fora** de `citizentech/assistente/` (p.ex. `integracao_citizentech/`), que apenas **importa** o Gen AI. Nenhuma edição em arquivos congelados.
2. **Contrato:** função `perguntar(texto: str) -> dict` que retorne `{status, resposta, fontes[], evidencias[], aviso, erro_tecnico}`, derivada de `RespostaGerada.para_dict()`; versionar o contrato (campo `versao`) e incluir `VERSAO_POLITICA` na saída.
3. **Inicialização única:** carregar `corpus`, `Indice` e `Catalogo` uma vez (≈ 12 s) e reutilizar.
4. **Verificação de saúde:** chamar `ClienteLMStudio.disponivel()` antes; se falso, devolver mensagem clara de indisponibilidade sem tentar gerar.
5. **Concorrência e tempo:** serializar chamadas; usar fila/assíncrono se a interface do CitizenTech for interativa; timeout de leitura padrão 180 s.
6. **Exibição:** sempre mostrar o `status`, as `fontes` (referência, edição, data) e o trecho literal em `evidencias`; para `ambigua`, listar as publicações. Não reescrever o texto do modelo.
7. **Privacidade:** o Gen AI mascara CPF/telefone da pergunta, mas a camada deve evitar enviar dados pessoais desnecessários; não registrar solicitações em logs sem necessidade.
8. **Testes sem modelo:** `ClienteLMStudio(cfg, sessao)` aceita uma sessão HTTP simulada; ver `citizentech/assistente/tests/test_geracao.py` (funções `cli`/`ok`) para o padrão. Testar o mapeamento de cada status.
9. **Teste manual para o vídeo:** uma solicitação do protótipo → pergunta ao Gen AI → resposta com fontes, um caso de abstenção, e o `verificar_hashes.py` inalterado.
10. **Critério de aceite sugerido:** `TODOS CONFEREM: True` após a integração; nenhuma alteração em `geracao.py`, `evidencias.py`, `catalogo.py`; documentação do que foi integrado e do que ficou de fora; nada declarado como "validado".

## 9. Execução e preparação do ambiente
Passos (todos **pendentes de execução por você**; só a leitura foi verificada aqui):
1. Python 3.14.x (observado: 3.14.4). Dependências: `numpy`, `scipy`, `pandas`, `pyarrow`, `requests`, `psutil`, `pytest`; `sentence-transformers` + `torch` só para reconstruir o índice vetorial. **Sem arquivo de versões validado** — ver `REPRODUCAO_E_DEPENDENCIAS.md`.
2. LM Studio 0.4.28 (runtime llama.cpp Vulkan 2.73.0), modelo `Qwen_Qwen3-8B-Q4_K_M.gguf` (`bartowski/Qwen_Qwen3-8B-GGUF`, 5.027.784.224 bytes, SHA-256 `54fffa050078e984116639c83dfb64b5aa6d4cd474e018b076777c632bbccccd`). **O GGUF não está neste pacote**: baixar do repositório do Hugging Face acima e conferir o SHA-256. Carregar com identificador `qwen3-8b`, contexto 8192 (nas fases anteriores: `lms load qwen_qwen3-8b --identifier qwen3-8b --context-length 8192 -y`), servidor em `http://localhost:1234`.
3. Memória livre: feche aplicativos pesados (o `llama-server` chegou a ≈ 8 GB).
4. Verificar integridade: `python projeto/scripts/verificar_hashes.py projeto`.
5. Testes (sem modelo): `python -m pytest citizentech/assistente/tests -q`, a partir de `projeto/`. Último resultado registrado: 337 passando (fim da Fase 4D.1); **não reexecutado ao preparar este pacote**.

## 10. Mapa de arquivos
Ver `INVENTARIO_PACOTE_BALBO.md`. Principais: `projeto/citizentech/assistente/` (código), `projeto/docs/entrega_genai/` (12 documentos de entrega), `projeto/docs/assistente/` (relatórios 01–04.3 e `diagnostico_4_4/`), `projeto/data_assistente/` (corpus, índice `est300o30`, rodadas e snapshots).

## 11. Pendências para você e para o grupo
- Integração com o protótipo CitizenTech (sua tarefa) e definição do que será mostrado no vídeo.
- **[CONFIRMAR]** protótipo/Zelo, quais solicitações vão ao Gen AI, nomes completos dos integrantes.
- Validar dependências em ambiente limpo e executar os testes.
- Revisão humana dos julgamentos (nenhuma foi feita).
