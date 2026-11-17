# Justificativa da escolha do modelo — Qwen3-8B Q4_K_M

Este documento registra **apenas o que é confirmável** em arquivos do repositório, medições existentes ou consulta feita em 2026-11-16. O que não é confirmável está marcado **PENDENTE**. Não há benchmark comparativo entre LLMs neste projeto; nenhum foi inventado.

## 1. Decisão e escopo
O gerador usa **Qwen3-8B, quantização Q4_K_M, formato GGUF**, servido localmente pelo **LM Studio 0.4.28** (llama.cpp Vulkan 2.73.0), com parâmetros fixos (`ConfigGeracao`: temperatura 0,3; `top_p` 0,8; `/no_think`; JSON Schema estrito). **Só este modelo foi avaliado**; nenhuma outra LLM ou quantização foi comparada.
- **Origem da decisão:** a escolha do modelo local foi aprovada durante o desenvolvimento (decisão registrada como "D2" na memória de sessão do assistente de desenvolvimento: LM Studio + Qwen3-8B Q4_K_M, runtime Vulkan, limite de ≈ 3 mil tokens de contexto). **Não existe arquivo do repositório com o racional original** da decisão. **PENDENTE:** o grupo deve confirmar a decisão e o racional.

## 2. Fatores sustentados por evidência
| Fator | Evidência |
|---|---|
| **Execução local** | Todas as rodadas usam `http://localhost:1234` (`.meta.json`, `ConfigGeracao.url`); nenhuma chamada a API externa de LLM no código do Gen AI e nenhuma chave de API (busca textual). O enunciado da disciplina de RPA (`docs/enunciado/p1.png`) fixa a regra de usar ferramentas gratuitas e de não enviar dados pessoais reais a APIs; o enunciado do Gen AI (`gsgenai.pdf`) não impõe restrição equivalente nos trechos lidos. |
| **Hardware** | AMD RX 6750 XT 12 GB, Ryzen 5 5500, 16 GB de RAM (`.meta.json`: "RX 6750 XT"; configuração informada pelo grupo e repetida nos relatórios). |
| **Tamanho do arquivo** | GGUF Q4_K_M = **5.027.784.224 bytes** (verificado localmente) ≈ 5,03 GB, coerente com o listado na página de bartowski (consulta de 2026-11-16). |
| **Limite de memória (medido)** | `04_gerador.md` §6: `llama-server` até **4,5 GB** de RSS, RAM livre do sistema até **~200 MB**, VRAM total até **11,8 GB de 12 GB** (inclui desktop). Nas rodadas 4.1–4.3: RSS até **8,2 GB** (`04_1`) e **7,8 GB** com RAM livre mínima de **45 MB** (`04_3`). Em uma execução com `parallel` 4 e outro programa aberto, o servidor **caiu** (`04_gerador.md` §6). |
| **Contexto ≈ 3 mil tokens** | `ConfigGeracao.orcamento_tokens = 3000` (prompt total estimado, tokens do Qwen3); o contexto do servidor é 8192. O prompt de sistema ocupa ≈ 1,1 mil tokens, de modo que só ≈ 3 chunks cabem (`04_gerador.md` §8). A razão **por que** o orçamento foi fixado em 3 mil (memória, latência ou ambos) **não está documentada além da restrição de memória observada; PENDENTE de confirmação**. |
| **Latência** | Mediana de geração 12,7 s (avaliação isolada) e 17–21 s nas rodadas end-to-end 4.1–4.3 (medianas calculadas dos JSONL: 19,8 s, 21,1 s e 17,2 s); p95 30,9 s na 1ª avaliação end-to-end (`04_gerador.md` §6). |
| **Comportamento com `/no_think`** | `reasoning_tokens = 0` em todas as chamadas medidas; JSON válido 150/150 nas rodadas 4.1–4.3 e 76/76 na avaliação isolada. `max_tokens_saida` 700 truncava o JSON em 7/150; foi para 1100. |
| **Aderência às regras** | Sem falsa confiança nos 78+18 casos controlados da avaliação isolada e instruções embutidas não obedecidas (`SEGURANCA_E_MITIGACOES.md`). Isto vale para esse modelo e prompt; não é comparação com outros. |

## 3. Origem, formato e licença
- **Origem do arquivo:** `bartowski/Qwen_Qwen3-8B-GGUF` (https://huggingface.co/bartowski/Qwen_Qwen3-8B-GGUF), arquivo `Qwen_Qwen3-8B-Q4_K_M.gguf`, em `C:\Users\henry\.lmstudio\models\bartowski\Qwen_Qwen3-8B-GGUF\`, SHA-256 `54fffa050078e984116639c83dfb64b5aa6d4cd474e018b076777c632bbccccd` (calculado em 2026-11-16). Data de download do arquivo: o carimbo do arquivo local é de 2026-11-13.
- **Licença declarada:** a página do repositório de bartowski declara **apache-2.0**, e a página do modelo original `Qwen/Qwen3-8B` (https://huggingface.co/Qwen/Qwen3-8B) declara **Apache 2.0**; ambas **consultadas em 2026-11-16** por leitura automatizada das páginas (o resumo foi produzido por uma ferramenta de busca de páginas; **o grupo deve conferir o texto original das licenças antes de citá-las formalmente**).
- **Quantização:** feita por bartowski com llama.cpp b5200 e opção imatrix (segundo a página, mesma consulta).
- **Modelo original:** Qwen3-8B, modelo de linguagem causal, 8,2 B de parâmetros totais (segundo a página do modelo original).

## 4. Alternativas
Nenhuma alternativa (outro LLM, outra quantização, API em nuvem) foi **testada ou documentada** no repositório. Portanto **não há evidência** para afirmar por que o Qwen3-8B Q4_K_M é melhor que outras opções. O que se pode dizer é que ele **coube** no hardware com margem pequena (§2) e atendeu aos requisitos de formato (JSON, `/no_think`).

## 5. Limitações da escolha
- Um único modelo; sem comparação de qualidade entre quantizações (Q4_K_M foi a única) nem entre modelos.
- Memória: com 16 GB de RAM, execuções longas exigem recarregar o modelo e fechar aplicativos (ver `REPRODUCAO_E_DEPENDENCIAS.md` §6).
- Sem *seed*; resultados variam entre execuções.
- O orçamento de ≈ 3 mil tokens reduz a revocação do contexto (só ≈ 3 chunks por pergunta na maioria dos casos).
- Licença e origem: leitura automatizada, pendente de conferência humana.

## 6. Pendências de confirmação pelo grupo
1. Racional da decisão D2 (por que Qwen3-8B Q4_K_M e por que ≈ 3 mil tokens).
2. Conferência das licenças nas páginas originais.
3. Data em que o GGUF foi baixado (o carimbo do arquivo é 2026-11-13).
