# Inventário do PACOTE_BALBO

Gerado em 2026-11-16 pela preparação do pacote (cópias; o repositório original `D:\Downloads\GS\RPA` não foi modificado). A lista completa de arquivos com SHA-256 está em `manifesto_sha256.csv` (todos os arquivos, exceto este inventário e o próprio manifesto).

## Totais
377 arquivos de manifesto (105.4 MB descompactados). **375** idênticos ao original (SHA-256 igual), **2** novos (documentos do pacote), **0** alterados ou divergentes.

## Conteúdo de `projeto/`
| Item | Arquivos | Tamanho (KB) |
|---|---:|---:|
| `.env.example` | 1 | 0 |
| `.gitattributes` | 1 | 0 |
| `.gitignore` | 1 | 1 |
| `README.md` | 1 | 13 |
| `citizentech/` | 50 | 490 |
| `data/` | 9 | 562 |
| `data_assistente/` | 81 | 99,932 |
| `docs/` | 222 | 6,906 |
| `main.py` | 1 | 2 |
| `requirements-congelado.txt` | 1 | 0 |
| `requirements.txt` | 1 | 0 |
| `scripts/` | 4 | 29 |
| `tests/` | 2 | 9 |

### `projeto/data_assistente/`
| Item | Arquivos | Tamanho (KB) |
|---|---:|---:|
| `derivados/` | 24 | 10,614 |
| `dodf_amostra/` | 3 | 1,576 |
| `dodf_original/` | 3 | 8,891 |
| `indices/` | 4 | 77,320 |
| `versoes/` | 47 | 1,530 |
(`indices/` contém apenas `est300o30/`: `chunks.jsonl`, `vetores.npy`, `janela_inicio.npy`, `manifesto.json`.)

## Documentos novos na raiz do pacote
`README_BALBO.md`, `TRANSFERENCIA_BALBO.md`, `INVENTARIO_PACOTE_BALBO.md`, `manifesto_sha256.csv`. Os 12 documentos de entrega estão em `projeto/docs/entrega_genai/` (idênticos aos originais).

## O que NÃO foi copiado (e por quê)
| Item do original | Motivo |
|---|---|
| Modelo `Qwen_Qwen3-8B-Q4_K_M.gguf` (≈ 5 GB, em `C:\Users\henry\.lmstudio\models\bartowski\`) | pedido explícito; obter conforme `TRANSFERENCIA_BALBO.md` §9 (SHA-256 `54fffa05…cccd`) |
| `data_assistente/indices/_ckpt/` (≈ 52 MB) | checkpoints temporários de embeddings |
| `data_assistente/indices/est500o50/` (≈ 71 MB) | configuração de referência, não usada na consulta; reconstruível |
| `.git/` | repositório sem commits |
| `logs/`, `saida/`, `.pytest_cache/`, `__pycache__/`, `*.pyc` | temporários e gerados em execução |
| `_backup_docs_pre_correcao_2026-11-11/` | cópia de backup do RPA (duplicata) |
| `validacao_independente/` | estrutura do RPA, não executada, sem relação com o Gen AI |
| `D:\hf_cache` (modelo e5) | cache externo ao repositório (só para reconstruir vetores) |
| Ambientes virtuais | não existem no repositório |

## Verificações
- `verificar_hashes.py` na cópia (`projeto/`): **TODOS CONFEREM: True**.
- Hashes (16 car.) de `geracao.py`, `evidencias.py`, `catalogo.py` idênticos ao original: c857b99f49947e1a, 12118192b9529075, 8e44143ba1d092f5. Candidata: `fail-closed-4.4.4d1-cand` (presente em `geracao.py`).
- Varredura de segredos: nenhum `.env`, chave privada, token ou credencial (ver `ENTREGA_FIAP_GENAI/INTEGRIDADE.md` §4 para o detalhe; os mesmos arquivos de dados e código).
- Segurança: `.env.example` não contém chaves; o código do Gen AI não usa API externa.
