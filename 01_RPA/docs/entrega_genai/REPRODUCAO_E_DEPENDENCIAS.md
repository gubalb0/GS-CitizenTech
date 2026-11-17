# Reprodução e dependências — módulo Gen AI

Levantamento feito em 2026-11-16 por **leitura** de arquivos e de metadados do ambiente (`importlib.metadata`, `pip`/`lms` só para consulta; nenhum pacote instalado, nenhum teste e nenhuma geração executados). Onde algo não é comprovável, está dito.

## 1. Versão do Python
- **Rodadas históricas do Gen AI:** a versão do Python **não foi registrada** nos arquivos `.meta.json` das rodadas (`geracao_e2e_41_*.meta.json` guardam modelo, runtime, parâmetros e hashes, mas não a versão do Python). **Não comprovada.**
- **Interpretador observado agora (e nas fases 4D recentes):** `C:\Python314\python.exe`, **Python 3.14.4** (MSC v.1944, 64 bit). O `README.md` do RPA cita 3.14.2 para os testes do RPA (10/11/2026). A sintaxe do código usa `from __future__ import annotations` e tipos `X | None` (exige ≥ 3.10).

## 2. Pacotes e versões identificados
Importados pelo código de `citizentech/assistente/` (inspeção das linhas `import`): `numpy`, `scipy` (BM25 em `scipy.sparse`), `pandas` (leitura do Parquet em `dados.py`), `requests` (cliente do LM Studio), `psutil` (`construir_indice.py`), `sentence_transformers` (importado tardiamente em `codificador.py`). `pyarrow` é necessário para `pandas.read_parquet` (inferido; não testado com outro motor). `pytest` para os testes. O Gen AI importa ainda `citizentech.texto.mascarar_pii` (módulo do RPA, que só usa `re` e `unicodedata`).

| Pacote | Versão instalada no interpretador acima | Observação |
|---|---|---|
| numpy | 1.26.4 | o `requirements-congelado.txt` do **RPA** fixa 2.4.4 |
| scipy | 1.17.1 | |
| pandas | 2.2.3 | |
| pyarrow | 24.0.0 | |
| requests | 2.34.2 | o congelado do RPA fixa 2.33.0 |
| psutil | 7.2.2 | |
| sentence-transformers | 5.5.1 | só para construir/avaliar índice vetorial |
| transformers / huggingface-hub / torch | 5.10.2 / 1.17.0 / 2.12.0 (CPU, segundo `03_retriever.md`: `2.12.0+cpu`) | só índice vetorial |
| pytest | 9.0.3 | |
| scikit-learn / joblib | 1.9.0 / 1.5.3 | usados pelo RPA, não pelo Gen AI; o congelado do RPA fixa 1.9.1 / 1.6.0 |
**Aviso:** estas são as versões **instaladas hoje**. Não há prova de que foram as mesmas das rodadas de 13–16/11, e há divergência já visível com os arquivos de versões do RPA. **Não existe ambiente limpo para validar** um arquivo de versões do Gen AI; por isso nenhum `requirements-genai.txt` com versões foi criado.

### Proposta de `requirements-genai.txt` (NÃO criada como arquivo; versões **não** verificadas)
```text
# PROPOSTA para o grupo validar em venv limpo antes de adotar. Sem versoes fixas porque nao ha ambiente limpo
# testado. Versoes observadas no ambiente de desenvolvimento (nao validadas): numpy 1.26.4, scipy 1.17.1, pandas 2.2.3,
# pyarrow 24.0.0, requests 2.34.2, psutil 7.2.2, pytest 9.0.3, sentence-transformers 5.5.1 (+ torch 2.12.0 CPU)
numpy
scipy
pandas
pyarrow
requests
psutil
pytest
# apenas para construir/avaliar o indice vetorial (consulta so com BM25 nao precisa):
sentence-transformers
torch
```
Passo pendente (humano): criar um venv novo, instalar, rodar `python -m pytest citizentech/assistente/tests -q` e registrar as versões resolvidas.

## 3. Configuração do LM Studio e do modelo
Fonte: `geracao_e2e_41_20261114-130608.meta.json`, `citizentech/assistente/geracao.py` (`ConfigGeracao`) e `docs/assistente/diagnostico_4_4/fase4/retomar_validacao_seletiva.py`.
| Item | Valor |
|---|---|
| LM Studio / runtime | **0.4.28**, llama.cpp **Vulkan 2.73.0**, GPU RX 6750 XT |
| Endereço local | `http://localhost:1234/v1/chat/completions` (verificação: `…/v1/models`) |
| Identificador do modelo no servidor | `qwen3-8b` (também havia carregados `qwen_qwen3-8b` e `text-embedding-nomic-embed-text-v1.5`; o embedding do LM Studio **não é usado** pelo pipeline) |
| Contexto do servidor | 8192 tokens |
| `parallel` | 1 nas rodadas end-to-end 4.1–4.3; 4 na avaliação isolada e na validação seletiva (Fase 4B) |
| Carga usada nos scripts (fases 4B) | `lms.exe load qwen_qwen3-8b --identifier qwen3-8b --context-length 8192 -y` (`C:\Users\henry\.lmstudio\bin\lms.exe`) |
| Parâmetros de geração | temperatura 0,3; `top_p` 0,8; `/no_think`; JSON Schema estrito; `max_tokens_saida` 1100; `max_chunks` 5 (limite 6); `orcamento_tokens` 3000; `max_tokens_chunk` 350; timeouts 5 s/180 s; sem *seed* |
| Prompt | `geracao.PROMPT_SISTEMA`, `VERSAO_PROMPT = "v3"` |

**Modelo e formato (verificado nesta máquina):** arquivo `C:\Users\henry\.lmstudio\models\bartowski\Qwen_Qwen3-8B-GGUF\Qwen_Qwen3-8B-Q4_K_M.gguf`, **5.027.784.224 bytes**, SHA-256 **`54fffa050078e984116639c83dfb64b5aa6d4cd474e018b076777c632bbccccd`** (calculado em 2026-11-16, somente leitura). Formato **GGUF**, quantização **Q4_K_M**, repositório `bartowski/Qwen_Qwen3-8B-GGUF` (URL: https://huggingface.co/bartowski/Qwen_Qwen3-8B-GGUF; página consultada em 2026-11-16: quantizado por bartowski com llama.cpp b5200 e opção imatrix; Q4_K_M listado com 5,03 GB, coerente com o arquivo local). O GGUF **não** faz parte do repositório.

## 4. Estrutura de diretórios necessária
Raiz do repositório = `D:\Downloads\GS\RPA` (`dados.RAIZ` é calculada a partir do arquivo).
```
citizentech/                       (pacote; assistente/ + texto.py do RPA, usado para mascarar PII)
data_assistente/dodf_original/     corpus-00000-of-00001.parquet, validation-00000-of-00001.parquet, MANIFESTO.json
data_assistente/indices/est300o30/ chunks.jsonl, vetores.npy, janela_inicio.npy, manifesto.json   (≈ 80 MB)
data_assistente/derivados/         saídas das rodadas (escrita ao rodar as avaliações)
D:\hf_cache                        cache do modelo e5 (padrão em codificador.py; só para vetores)
scripts/verificar_hashes.py        conferência de integridade (somente leitura)
```
O conjunto de teste (350) **não** existe localmente.

## 5. Comando de execução / trecho programático existente
Não há CLI de consulta. Com o LM Studio rodando e o modelo carregado como `qwen3-8b`:
```python
from citizentech.assistente import avaliacao_e2e as AE, geracao as G
from citizentech.assistente.catalogo import Catalogo
from citizentech.assistente.retriever import Indice
corpus, *_ = AE.preparar()
idx, cat = Indice.carregar(AE.IDX), Catalogo.de_corpus(corpus)
cfg = G.ConfigGeracao(); cli = G.ClienteLMStudio(cfg)
r = G.gerar_resposta("<pergunta>", idx.buscar("<pergunta>", k=cfg.max_chunks, modo="bm25"), cli, cfg, catalogo=cat)
print(r.status, r.resposta)
```
O trecho reproduz o uso de `citizentech/assistente/avaliacao_e2e.py` e das chamadas usadas nas fases 4D (replays), **mas não foi executado com o modelo nesta etapa**. Outros pontos de entrada existentes: `python -m citizentech.assistente.avaliacao_e2e` (rodada de 150 perguntas; cria novo `.jsonl`), `…avaliacao_geracao` (avaliação isolada), `…avaliar_retriever`, `…construir_indice` (≈ 30 min por configuração) e `python scripts/verificar_hashes.py` (integridade, sem modelo). Para testes: `python -m pytest citizentech/assistente/tests -q`.

## 6. Limitações de reprodução
1. Sem ambiente limpo validado; sem arquivo de dependências do Gen AI; versões instaladas diferem das fixadas pelo RPA.
2. Python das rodadas históricas não registrado.
3. A geração **não é determinística** (temperatura 0,3, sem *seed*); reexecutar a rodada de 150 não reproduzirá exatamente os mesmos textos. Os JSONL preservados são a evidência.
4. O prompt bruto enviado ao LM Studio não foi gravado; o contexto é reconstruído deterministicamente por `montar_contexto` e coincide com o registrado (hash).
5. Memória: com 16 GB de RAM, o `llama-server` cresce a cada requisição (≈ 4,5 GB na 1ª avaliação e até ≈ 8,2 GB nas rodadas 4.1–4.3, segundo `04_gerador.md` §6 e `04_1`/`04_3`), exigindo fechar aplicativos e recarregar o modelo a cada ≈ 3 gerações (Fase 4B).
6. Caminhos absolutos do ambiente (`D:\hf_cache`, `C:\Users\henry\.lmstudio`) precisam ser ajustados em outra máquina.
7. O repositório **não tem commits**; o pacote de entrega deve ser uma cópia da pasta.
8. O índice (≈ 200 MB com `est500o50`) e os Parquet não estão versionados; devem ser incluídos no pacote ou reconstruídos.
9. Os resultados das rodadas correspondem às versões de código registradas nos `.meta.json` (4.3: `geracao.py` `a5a6e2c472e34946`), **não** à candidata atual `fail-closed-4.4.4d1-cand`, que foi avaliada apenas por replay offline e por 21 gerações seletivas.
