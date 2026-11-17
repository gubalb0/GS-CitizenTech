# PACOTE_BALBO — transferência técnica do módulo Gen AI (CitizenTech, Global Solution 2026.2)

Para: **Gustavo Balbo (RM 561711)**. Preparado em 2026-11-16 a partir de `D:\Downloads\GS\RPA` (o repositório original **não foi modificado**; este pacote é uma cópia).

## Sua tarefa
Realizar a **integração** do assistente Gen AI com o protótipo CitizenTech por meio de uma camada **isolada**. **A integração NÃO foi feita** e **nada neste pacote a declara concluída**. Também faz parte da entrega acadêmica gravar o vídeo de até 5 minutos (ver `ENTREGA_FIAP_GENAI/ROTEIRO_VIDEO.md`, no pacote da FIAP).

## Leia nesta ordem
1. `TRANSFERENCIA_BALBO.md` — arquitetura, fluxo RAG, pontos de entrada, formatos de entrada e saída, abstenção, limitações e como projetar a camada de integração.
2. `projeto/docs/entrega_genai/REPRODUCAO_E_DEPENDENCIAS.md` e `README_ENTREGA.md` — ambiente, dependências, LM Studio, modelo.
3. `projeto/docs/entrega_genai/LIMITACOES_E_IMPACTO_CIDADAO.md` e `RESULTADOS_E_LIMITACOES.md` — o que o sistema **não** faz bem.
4. `INVENTARIO_PACOTE_BALBO.md` — o que está (e o que não está) no pacote.

## Conteúdo
```
PACOTE_BALBO/
├─ README_BALBO.md  TRANSFERENCIA_BALBO.md  INVENTARIO_PACOTE_BALBO.md
└─ projeto/                       cópia da estrutura do repositório (rodar os comandos a partir daqui)
   ├─ citizentech/assistente/     código do Gen AI (+ tests/)
   ├─ citizentech/*.py, main.py   módulo RPA (congelado; o Gen AI reutiliza citizentech/texto.py)
   ├─ data_assistente/            corpus (Parquet + MANIFESTO), índice est300o30, rodadas (JSONL), snapshots
   ├─ docs/                       documentação do RPA, docs/assistente/ (relatórios) e docs/entrega_genai/ (12 documentos)
   ├─ scripts/verificar_hashes.py conferência de integridade (somente leitura)
   └─ tests/, data/, requirements*.txt (RPA), .env.example (sem segredos)
```

## Primeiros passos (todos por sua conta; nada foi executado com o modelo)
```bash
cd PACOTE_BALBO/projeto
python scripts/verificar_hashes.py .          # esperado: TODOS CONFEREM: True (já verificado nesta cópia)
python -m pytest citizentech/assistente/tests -q   # testes sem modelo; último registro: 337 passando (4D.1); não reexecutado ao montar o pacote
```
Para gerar respostas é preciso o **LM Studio com o modelo Qwen3-8B Q4_K_M** carregado como `qwen3-8b` (o arquivo GGUF de ≈ 5 GB **não está no pacote**; instruções e SHA-256 em `TRANSFERENCIA_BALBO.md` §9). Sem o modelo, a recuperação e a montagem de contexto funcionam (verificado), e a geração devolve `insuficiente` com erro técnico.

## Avisos
- **Candidata não validada:** `fail-closed-4.4.4d1-cand`. Não altere `geracao.py`, `evidencias.py` e `catalogo.py`; os hashes de referência estão nos manifestos.
- **Não há integração com o CitizenTech** hoje; o RPA do repositório não chama o Gen AI. **[CONFIRMAR]** com o grupo qual é o protótipo e o "Zelo".
- Nenhuma revisão humana dos resultados foi feita; as auditorias existentes são de modelo de linguagem.
- Não há arquivo de dependências validado do Gen AI.
- Segredos: nenhum arquivo `.env` ou chave foi incluído (verificação em `INVENTARIO_PACOTE_BALBO.md`).
