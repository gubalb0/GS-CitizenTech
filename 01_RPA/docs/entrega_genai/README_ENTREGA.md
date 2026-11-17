# CitizenTech — módulo Gen AI (assistente de consulta ao DODF-Saúde) — Global Solution 2026.2

> **Estado: protótipo acadêmico experimental.** A candidata atual é `fail-closed-4.4.4d1-cand`, **não validada** e **não integrada ao Zelo**. Não use para decisões reais. Resultados e limitações: [`RESULTADOS_E_LIMITACOES.md`](RESULTADOS_E_LIMITACOES.md). Estado final e congelamento: [`ESTADO_FINAL.md`](ESTADO_FINAL.md).

Documentação consolidada em 2026-11-16 a partir dos arquivos reais do projeto. Esta pasta (`docs/entrega_genai/`) é **nova**; nenhum documento, código ou dado anterior foi movido, alterado ou excluído. Onde algo não pôde ser confirmado, o texto diz.

## 1. Onde o Gen AI está
O código do Gen AI está no pacote `citizentech/assistente/` do repositório `D:\Downloads\GS\RPA`, que também hospeda o módulo **RPA** (`main.py`, `citizentech/*.py`, `README.md` da raiz). Os documentos do Gen AI estão em `docs/assistente/`. A pasta de trabalho `D:\Downloads\GS\GENAI` está vazia; este pacote de documentação foi criado dentro do repositório, ao lado de `docs/assistente/`. O módulo **Cluster** (`D:\Downloads\GS\CLUSTER`) é independente e não foi tocado.

## 2. Problema e objetivo
Informações de saúde pública em Diários Oficiais (DODF) são extensas, administrativas e difíceis de consultar. O objetivo do Gen AI é um **assistente de perguntas e respostas sobre publicações do DODF relacionadas à saúde**, que responda **só com base nos trechos recuperados**, cite a fonte com trecho literal e **se abstenha** (ambígua / insuficiente / fora do escopo) quando a evidência não sustenta uma resposta única. A prioridade de projeto é **não responder errado** (política *fail-closed*), mesmo ao custo de responder pouco.

Não é um assistente clínico: não orienta diagnóstico nem conduta, e o corpus é administrativo (extratos, contratos, credenciamentos, reconhecimentos de dívida), não "informação de serviço ao cidadão".

## 3. Funcionalidades disponíveis (implementadas no código atual)
Somente o que existe em código e é exercitado por testes automatizados do repositório (ver `ARQUITETURA.md` e `ESTADO_FINAL.md`):
- **Ingestão e preparação** do corpus DODF Public Health QA (leitura do Parquet, integridade por hash, deduplicação).
- **Associação pergunta→publicação** nas 150 perguntas de validação (para avaliação).
- **Chunking** estrutural/por tamanho (configuração escolhida: `est300o30`).
- **Índice** BM25 (usado) e vetorial `multilingual-e5-small` (construído e avaliado, **não usado** na consulta final) + RRF (avaliado; **não usado**).
- **Recuperação** BM25 top-5.
- **Geração** via LM Studio (Qwen3-8B Q4_K_M local), saída JSON estrita, `/no_think`, temperatura 0,3.
- **Verificação independente do LLM** e **abstenção** (política `fail-closed`), com status `respondida`, `parcial`, `ambigua`, `insuficiente`, `fora_do_escopo`.
- **Mascaramento de PII** na pergunta (reuso de `citizentech.texto.mascarar_pii`, do módulo RPA, somente leitura).
**Não há interface de usuário final nem comando único de consulta** (ver §8): o uso é programático (Python) mais scripts de avaliação.

## 4. O que NÃO é funcionalidade (protótipos/experimentos)
Mecanismos experimentais e simulações das fases 4D.2–4D.7 (vínculo por frase, políticas de veto V0–V3, protótipo corrigido da 4D.7) e a seleção de contexto "S1 conservadora" (flag `priorizar_atributo`, **desligada por padrão**) **não são funcionalidades disponíveis ao usuário** nem fazem parte do comportamento padrão. Ver `ESTADO_FINAL.md`.

## 5. Tecnologias
Python 3.14.4 no ambiente em que esta documentação foi conferida (o README do RPA cita 3.14.2 para os testes do RPA; qual versão foi usada em cada fase do Gen AI não está registrada de forma verificável), `numpy`, `scipy` (BM25 próprio em `scipy.sparse`), `pandas` + `pyarrow` (Parquet), `requests` (cliente do LM Studio), `psutil` (monitoramento nos scripts de construção do índice), `sentence-transformers` + `torch` (somente para construir/avaliar o índice vetorial), `pytest`. Modelo gerador: **Qwen3-8B Q4_K_M (GGUF, bartowski)** em **LM Studio 0.4.28** (llama.cpp Vulkan 2.73.0). Embeddings: `intfloat/multilingual-e5-small` (MIT). Corpus: `gvic-unb/dodf-saude-qa` (**CC BY 4.0**; atribuição exigida).
Ambiente de testes: AMD RX 6750 XT 12 GB, Ryzen 5 5500, 16 GB de RAM.

## 6. Arquitetura resumida
```
pergunta → mascarar PII → BM25 (est300o30, top-5) → montar contexto (≤ ~3K tokens, ≤ 6 chunks)
        → LM Studio (Qwen3-8B, JSON Schema, /no_think) → verificação (citações literais, números,
          alinhamento, abstenção por identificabilidade, proteções M1–M5/A_DEST/A_LOC) → RespostaGerada
```
Detalhes e diagrama em [`ARQUITETURA.md`](ARQUITETURA.md).

## 7. Instalação (baseada nos arquivos reais)
Não há `requirements` específico do Gen AI no repositório. Os arquivos existentes (`requirements.txt`, `requirements-congelado.txt`) cobrem o **RPA** (`scikit-learn`, `joblib`, `requests`, `pytest`). O código do Gen AI importa também `numpy`, `scipy`, `pandas`, `pyarrow` (via `pandas.read_parquet`, inferido), `psutil` e, para o índice vetorial, `sentence_transformers`/`torch`. Versões presentes no ambiente conferido (`pip list`, somente leitura): numpy 1.26.4, scipy 1.17.1, pandas 2.2.3, pyarrow 24.0.0, psutil 7.2.2, requests 2.34.2, pytest 9.0.3, torch 2.12.0. **Isso é um registro do ambiente atual, não um arquivo de dependências verificado em ambiente limpo (pendência).** O `requirements-congelado.txt` do RPA fixa `numpy==2.4.4`, versão diferente da instalada aqui: o ambiente do Gen AI e o do RPA podem não ser o mesmo interpretador; não foi investigado (pendência).
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt      # RPA; o Gen AI exige ainda os pacotes listados acima (sem arquivo oficial)
```
**Dados e índices (não estão versionados no Git — o repositório não tem nenhum commit):** `data_assistente/dodf_original/` (Parquet do corpus e da validação, com `MANIFESTO.json` e SHA-256) e `data_assistente/indices/est300o30/` (índice pronto, ≈ 80 MB; `est500o50` também existe). O modelo e5 foi baixado para `D:\hf_cache` (fora do repositório; só necessário para reconstruir/avaliar vetores). O conjunto de teste de 350 perguntas **nunca foi baixado**.
**LM Studio:** instalar o LM Studio e baixar o GGUF Qwen3-8B Q4_K_M; carregar com identificador **`qwen3-8b`**, contexto 8192, servidor local em `http://localhost:1234` (valores padrão de `ConfigGeracao`). Nas fases documentadas foi usado `parallel` 1 (rodadas completas) ou 4 (validação seletiva). **Aviso de memória:** o processo `llama-server` cresce a cada requisição (cache de prompt); com 16 GB de RAM foi necessário descarregar/recarregar o modelo a cada ≈ 3 gerações e fechar outros aplicativos.

## 8. Execução
Não existe CLI de consulta. As formas de executar, conforme o código:
- **Consulta programática** (exige LM Studio com o modelo carregado):
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
Este trecho foi montado a partir das assinaturas e do uso em `avaliacao_e2e.py`; **não foi executado nesta etapa** (a atividade proíbe novas gerações).
- **Rodada diagnóstica de 150 perguntas** (gera novo `.jsonl`; exige LM Studio): `python -m citizentech.assistente.avaliacao_e2e`.
- **Avaliação isolada do gerador:** `python -m citizentech.assistente.avaliacao_geracao`. **Retriever:** `python -m citizentech.assistente.avaliar_retriever est500o50 est300o30`. **Construir índice** (~30 min por configuração, CPU): `python -m citizentech.assistente.construir_indice est300o30`.
- **Conferência de integridade (somente leitura, sem modelo):** `python scripts/verificar_hashes.py` (resultado na última conferência: `TODOS CONFEREM: True`).
**Não repita rodadas de benchmark ao avaliar a entrega**: as rodadas históricas estão preservadas em `data_assistente/derivados/` e os relatórios citam seus identificadores.

## 9. Testes
```bash
python -m pytest citizentech/assistente/tests -q
```
Todos usam cliente simulado (sem rede e sem modelo). **Esta atividade não executou os testes** (restrição de não executar nada novo). Último resultado registrado: **337 testes passando ao fim da Fase 4D.1** (relatório `docs/assistente/diagnostico_4_4/fase4/FASE4D1_NORMALIZACAO_ROTULOS.md`); as fases 4D.2–4D.7 não alteraram a suíte oficial nem o código de produção, então o esperado é o mesmo número, **mas isso precisa ser reconfirmado por execução humana** (pendência no checklist). Contagem estática por inspeção: 286 funções `test_` em 17 arquivos de `citizentech/assistente/tests/` (a diferença para 337 provavelmente vem de parametrização; hipótese não verificada). Os testes da pasta `tests/` da raiz pertencem ao RPA (o README do RPA cita 21).

## 10. Estrutura de pastas relevante
```
citizentech/assistente/        código do Gen AI (chunking, bm25, retriever, geracao, evidencias, catalogo, avaliações) + tests/
data_assistente/               dodf_original (corpus/validação + MANIFESTO), indices, derivados (rodadas), versoes (snapshots)
docs/assistente/               relatórios 01–04.3, auditoria 4.3 (por modelo de linguagem), diagnostico_4_4/ (fases 1–3, 4A–4D.7)
docs/entrega_genai/            ESTA documentação de entrega
scripts/verificar_hashes.py    conferência de integridade (somente leitura)
```
Fora do escopo do Gen AI: `main.py`, `citizentech/*.py` (RPA congelado), `data/`, `validacao_independente/`.

## 11. Limitações principais (resumo)
Rodada diagnóstica de 150 casos usada no desenvolvimento (não mede generalização); **sem revisão humana independente**; as auditorias existentes foram feitas pelo próprio agente de desenvolvimento (modelo de linguagem); utilidade baixa por desenho fail-closed (≈ 20% das 150 perguntas recebem resposta, segundo a auditoria da 4.3); **val-087-A-r1** (resposta entregue com localização não sustentada) permanece sem correção; sem integração com o Zelo; ambiente de 16 GB limita a execução. Ver `RESULTADOS_E_LIMITACOES.md`.

## 12. Estado atual
Congelado em `fail-closed-4.4.4d1-cand` (candidata, não validada). A correção da Fase 4D.7 pertence a um **protótipo diagnóstico**, não à candidata. Ver `ESTADO_FINAL.md` e `CHECKLIST_ENTREGA.md`.

**Equipe do projeto (conforme README raiz do repositório):** Henry Gimenez - 563217; Gustavo Balbo - 561711; Vinícius Araújo - 564504. FIAP · Tecnólogo em Inteligência Artificial.
