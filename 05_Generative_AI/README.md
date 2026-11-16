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
- **Testes:** 163 testes automatizados.

## Resultado da avaliação ponta a ponta (150 perguntas, rodada `20261113-173721`)

| Status | Quantidade |
|---|---|
| Respondida (completa) | 2 |
| Parcial (com aviso e fonte) | 41 |
| Ambígua | 58 |
| Insuficiente | 35 |
| Fora do escopo | 14 |

- Abstenção (ambígua + insuficiente + fora do escopo): 107 de 150 (71%).
- Nenhuma resposta sem trecho literal da fonte, mas 19 das 43 respostas dadas (44%) vieram de uma publicação diferente da esperada, sempre marcadas como `parcial`, com aviso.
- Geração com mediana de 19,7 s por pergunta, e o servidor local chegou a 8,2 GB de RAM.

**Status: em andamento, não integrado.** A recomendação registrada pela própria equipe é não integrar antes de uma auditoria humana das respostas.

## Índices de busca

A pasta `01_RPA/data_assistente/indices/` (147 MB) ficou fora do repositório porque é gerada pelo próprio projeto:

```bash
cd 01_RPA
python -m citizentech.assistente.construir_indice est500o50 est300o30
```

Leva cerca de 30 minutos por índice em CPU.
