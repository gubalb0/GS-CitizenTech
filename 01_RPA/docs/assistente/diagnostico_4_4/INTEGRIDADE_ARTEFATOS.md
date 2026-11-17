# Integridade dos artefatos (Etapa 4.4, Fase 1)

## `data_assistente/derivados/chunks_exemplos.json`
- **SHA-256 atual (registrado em 2026-11-15):** `8c9d583afde2423ce8ceda57d3f8f0b7df60e7fe140eabad076744d127c82f37` (26.976 bytes). Registro: `hashes_referencia_44.json`.
- **Não é possível provar que o conteúdo é igual ao anterior.** Não existe snapshot, hash anterior nem commit (o repositório Git não tem nenhum commit). O arquivo foi reescrito em 2026-11-15 13:44 por uma rotina de conferência de hashes avulsa que continha o gravador do arquivo; essa mesma rotina já o tinha gravado em 2026-11-13 (~10:46, horário local).
- **Evidência parcial (não é prova):** 4 das 7 entradas (as `est500o50`) são idênticas, em todos os campos e no hash do chunk, aos chunks do índice construído em 13/11 às 11:26. As 3 entradas `tam500o0` não existem em nenhum índice e não são verificáveis; `chunking.py` não muda desde 13/11 10:43 (data de modificação).
- O arquivo é exemplo ilustrativo; nenhum código o lê.
- **A partir deste registro** qualquer mudança é detectável pela rotina abaixo. Antes dele, a igualdade histórica fica sem comprovação.

## Rotina de conferência
- Nova: `scripts/verificar_hashes.py` (somente leitura: abre arquivos só em modo `rb`; não grava, não regenera e não move nada; retorna 1 se algo diferir ou faltar).
- Confere `docs/modelo_congelado.json` (RPA congelado) e `hashes_referencia_44.json` (27 hashes: rodadas, `.meta.json`, auditorias, snapshots da versão 4.3, `chunking.py` e `chunks_exemplos.json`). Os arquivos vivos `geracao.py`, `evidencias.py` e `catalogo.py` **não** estão no manifesto porque mudarão na 4.4; a versão 4.3 fica fixada pelos snapshots `data_assistente/versoes/*_43_pre_execucao.py` (idênticos, em 2026-11-15, aos arquivos vivos) e por `avaliacao_e2e_etapa4_3.py` (estado do avaliador antes da correção de grupos).
- A rotina avulsa antiga (fora do repositório) foi substituída por um redirecionamento a este script.
- Testes: `citizentech/assistente/tests/test_verificar_hashes_44.py` (o verificador não altera mtime nem conteúdo, detecta alteração sem "consertar", reporta ausência sem criar arquivo, não contém chamadas de escrita; no repositório real, `chunks_exemplos.json` mantém hash e mtime).
