# Generative AI & Advanced Nets: assistente RAG sobre o Diário Oficial do DF (saúde)

**Integrantes:** Henry Gimenez (RM 563217), Gustavo Balbo (RM 561711), Vinicius Araujo (RM 564504)

O código deste módulo fica **dentro da pasta `01_RPA/`**, porque compartilha o pacote Python `citizentech` com o robô de RPA. Separar os arquivos quebraria os imports.

| O que | Onde |
|---|---|
| Código do assistente (chunking, BM25, embeddings, geração, verificação de evidências, avaliação) | [`../01_RPA/citizentech/assistente/`](../01_RPA/citizentech/assistente/) |
| Relatórios por etapa (corpus, chunking, retriever, gerador, confiabilidade) | [`../01_RPA/docs/assistente/`](../01_RPA/docs/assistente/) |
| Amostras do corpus, dataset original e resultados das avaliações | [`../01_RPA/data_assistente/`](../01_RPA/data_assistente/) |
| Planilha para auditoria humana das 150 respostas | [`../01_RPA/docs/assistente/auditoria_e2e_20261113-173721.csv`](../01_RPA/docs/assistente/auditoria_e2e_20261113-173721.csv) |

## Resumo

- **Problema:** responder perguntas sobre publicações de saúde do Diário Oficial do Distrito Federal (DODF) com a fonte identificada, ou abster-se quando não houver evidência.
- **Dados:** dataset público `gvic-unb/dodf-saude-qa` (CC BY 4.0): corpus de 1.381 publicações e 150 perguntas de validação. O conjunto de teste (350) não foi usado.
- **Pipeline:** recuperação lexical BM25 (top-5) → modelo local Qwen3-8B (LM Studio) → verificação de evidências no código (rastreabilidade, alinhamento pergunta × fonte, publicações concorrentes) → resposta com a fonte ou abstenção.
- **Testes:** 337 testes automatizados do módulo, mais 11 da camada de integração.

## Resultado da avaliação ponta a ponta (rodada 4.3, 150 perguntas de validação)

Fonte: `01_RPA/docs/entrega_genai/RESULTADOS_E_LIMITACOES.md`. Julgamento feito por modelo de linguagem, sem revisão humana.

| Indicador | Valor |
|---|---|
| Respostas dadas (respondida + parcial) | 31 de 150 (20,7%) |
| ... corretas / corretas, mas parciais / incorretas | 7 / 16 / 8 |
| Abstenções | 119 (79,3%); 56 delas consideradas indevidas pela auditoria |
| Recuperação BM25 (R@5 / MRR) | 0,491 / 0,434 |
| Latência de geração | 12 a 21 s (medianas), 30 s ou mais no p95 |

As 8 respostas incorretas passaram em toda a verificação técnica: citação literal não garante resposta correta. A versão atual (`fail-closed-4.4.4d1-cand`) entrega 30 das 150 no replay offline.

**Status: protótipo não validado, integrado ao Zelo por uma camada isolada (só na demonstração local).** O módulo continua sem revisão humana das respostas; a integração não muda isso.

## Integração com o Zelo

```
Zelo (aba "Publicações oficiais") → API do Zelo /publicacoes → integracao_citizentech (porta 8100) → Gen AI → LM Studio (Qwen3-8B)
```

| O que | Onde |
|---|---|
| Camada isolada (`perguntar(texto) -> dict`, contrato 1.0, carga única do índice, chamadas em série) | [`../01_RPA/integracao_citizentech/servico.py`](../01_RPA/integracao_citizentech/servico.py) |
| Serviço HTTP local (`/saude`, `/perguntar`) | [`../01_RPA/integracao_citizentech/api.py`](../01_RPA/integracao_citizentech/api.py) |
| Testes sem modelo (11) | [`../01_RPA/integracao_citizentech/tests/`](../01_RPA/integracao_citizentech/tests/) |
| Lado do Zelo (rota e aba) | [`../04_Front_End_Zelo/backend/app/routers/publicacoes.py`](../04_Front_End_Zelo/backend/app/routers/publicacoes.py), [`../04_Front_End_Zelo/frontend/features/publicacoes.py`](../04_Front_End_Zelo/frontend/features/publicacoes.py) |
| Passo a passo para rodar (Windows) | [`../04_Front_End_Zelo/docs/INTEGRACAO_GENAI.md`](../04_Front_End_Zelo/docs/INTEGRACAO_GENAI.md) |
| Material de transferência preparado pelo Henry | [`transferencia/`](transferencia/) |

- Nenhum arquivo congelado do Gen AI foi alterado: `python scripts/verificar_hashes.py .` continua `TODOS CONFEREM: True`, e os 337 testes do módulo seguem passando.
- O cidadão vê sempre o status, a publicação citada (edição e data do DODF) e o trecho literal. CPF e telefone saem da pergunta no Zelo, antes de chegar ao serviço.
- O modelo precisa de ~8 GB de RAM, por isso a aba fica desligada no Zelo publicado no Render.

## Índices de busca

O índice usado nas consultas (`01_RPA/data_assistente/indices/est300o30`, 75 MB) está no repositório. Os demais índices de teste ficaram de fora e podem ser gerados com:

```bash
cd 01_RPA
python -m citizentech.assistente.construir_indice est500o50 est300o30
```

Leva cerca de 30 minutos por índice em CPU.
