# Etapa 2 — Associação QA→documento e chunking (DODF, validação)

Gerado por: `python -m citizentech.assistente.relatorio_associacao`, `python -m citizentech.assistente.avaliar_chunking`
Dados derivados: `data_assistente/derivados/` · Testes: `python -m pytest citizentech/assistente/tests -q` (51 passaram)
O conjunto de TESTE (350) **não foi baixado nem usado**.

## A. Integridade
| Arquivo | Bytes | SHA-256 | Confere com o `oid` LFS do HF |
|---|---|---|---|
| `corpus-00000-of-00001.parquet` | 7.523.363 | `94104e51…c79c9` | sim |
| `validation-00000-of-00001.parquet` | 1.579.818 | `f40aff3a…49b6` | sim |
Revisão HF `ef52e3fe…`; licença CC BY 4.0; acesso em 2026-11-13; URLs no `MANIFESTO.json`. Originais marcados como somente leitura.
Corpus: 1.381 documentos, 220 datas, 219 edições, nenhum texto vazio, 4.008.970 tokens de superfície (mediana 295 por documento; p90 4.098; máx. 458.610). **Nenhum texto tem quebra de linha** (estrutura só por marcadores). 76 documentos são duplicatas exatas (mesma chave e texto, ids diferentes).

## B. Associação pergunta → publicação (150 perguntas de validação)
Método: o `texto_publicacao` é formado por blocos `Edição N — data — Seção — referência` + texto. A chave (edição, data, seção, referência) localiza candidatos e a **igualdade exata do texto** decide. Sem similaridade lexical.
| Resultado | Perguntas | Blocos (252 no total) |
|---|---|---|
| Resolvidas | **150 / 150** | exata única 213 · exata com duplicatas 39 |
| Parciais / não resolvidas / ambíguas / sem correspondência | 0 | 0 |
- MULTI: 41 perguntas, todas resolvidas bloco a bloco (1 bloco: 4; 2: 8; 3: 9; 4: 4; 5: 16 perguntas). A soma dos documentos por pergunta MULTI tem mediana de 81.976 caracteres (máx. 273.649), muito além do limite de ~3K tokens do gerador.
- Blocos com duplicatas (39; grupos de 2 e de 3 ids de texto idêntico): 23 perguntas (11 não-MULTI). O gabarito é o **conjunto** de ids equivalentes.
- 197 documentos distintos são referenciados pelas 150 perguntas (de 1.381).
- Perguntas não unívocas (diagnóstico por texto idêntico ou Jaccard≥0,8): 3 pares reais — val-005/val-018 (mesma pergunta, valores e datas diferentes), val-023/val-120 e val-122/val-146 (perguntas **idênticas** com respostas e documentos diferentes). O 4º par sinalizado (val-059/val-099) são hospitais diferentes (Brazlândia × Ceilândia): falso positivo do diagnóstico. Para essas perguntas, um documento específico não é identificável só pelo texto da pergunta.

## C. Chunking (`citizentech/assistente/chunking.py`)
- Estratégias: `tamanho` (janela de tokens, overlap exato) e `estrutura` (unidades Art./§/Considerando/Cláusula/incisos/itens → frases → palavras, empacotadas até o limite; overlap só com unidades inteiras). Não corta o numerador de item ("1.6.2.3.2.") do seu título nem referências "Art. 49, § 1º".
- IDs: documento `dodf-<id>`, chunk `dodf-<id>:<config>:<ordem>`; hash do texto; offsets de caracteres.
- Metadados preservados em cada chunk: edicao, data_edicao, secao, referencia, tipo_documento, numero_documento, data, topicos, localidades, tipo_unidade, programas. `texto_indexacao` = cabeçalho contextual + texto.
- Unidade de tamanho: **token de superfície** (palavra ou pontuação). Calibração com o Qwen3 (12 chunks `est500o50`, servidor local): razão Qwen3/superfície mediana 1,60 (1,31–2,04). **Um chunk de 500 tokens de superfície ≈ 800 tokens do Qwen3.**

| Config | Chunks | Tokens (total) | Média | p10 | p90 | Fronteiras limpas | Evidência no mesmo chunk* |
|---|---|---|---|---|---|---|---|
| tam300o0 / o30 | 13.995 / 15.367 | 4,01 M / 4,43 M | 286 / 288 | 300 | 300 | 10,2% / 9,8% | 83,0% |
| tam500o0 / o50 | 8.779 / 9.578 | 4,01 M / 4,42 M | 457 / 461 | 236 / 273 | 500 | 9,5% / 10,1% | 87,2% / 86,2% |
| tam700o0 / o70 | 6.566 / 7.111 | 4,01 M / 4,41 M | 611 / 620 | 200 / 233 | 700 | 10,1% / 10,2% | 88,3% |
| est300o0 / o30 | 15.686 / 16.584 | 4,01 M / 4,17 M | 256 / 252 | 171 / 166 | 299 | 95,5% / 95,8% | 84,0% |
| est500o0 / o50 | 9.522 / 10.155 | 4,01 M / 4,21 M | 421 / 415 | 225 / 195 | 499 | 96,6% / 96,8% | 87,2% |
| est700o0 / o70 | 6.983 / 7.452 | 4,01 M / 4,24 M | 574 / 569 | 205 / 187 | 699 | 97,3% / 97,5% | 88,3% |
\* Proxy retriever-independente: em 94 perguntas não-MULTI avaliáveis (resposta com valores R$/CNPJ/processo/número presentes no documento), fração em que **todos** esses valores ficam num só chunk. Valores vêm da resposta e do documento exato; não é gabarito novo.

Leitura (somente do que foi medido): a estrutura praticamente elimina cortes no meio de frase (≈96–98% de fronteiras limpas contra ≈10% por tamanho) com custo de ~3× mais tempo de processamento (≈10 s vs ≈3 s para o corpus todo) e chunks mais variáveis em tamanho. A integridade de evidência **depende do tamanho, não da estratégia** (83–84% a 300; 87% a 500; 88% a 700); overlap não mudou esse proxy. As 11 falhas do `est700o70` são todas perguntas de lista ("Quais itens foram adquiridos…") cujos valores se espalham por uma publicação com vários itens: exigem recuperar vários chunks.
Chunks por documento: 24 documentos geram mais de 100 chunks em `est500o50` (o maior, Portaria 544, 348 chunks); documentos gigantes (tabelas de CNPJ, regimentos) dominam o total de chunks.

## D. Testes (`citizentech/assistente/tests/`)
51 testes passaram em 0,21 s: documentos curtos, longos, vazios/None, caracteres especiais (acentos, aspas, emoji, R$, nº), texto sem pontuação, overlap exato, progresso com overlap alto, não cortar referência a artigo, valores monetários e numeradores de itens, determinismo/IDs, validação de configuração, e a associação (exata, duplicatas, mesma chave decidida por texto, ambígua, texto divergente, sem correspondência, normalização de espaços/acentos, MULTI parcial, perguntas não unívocas). Não testei contra o corpus real em teste automatizado (os scripts de relatório fazem isso).

## E. Limitações
- Associação 150/150 é por construção do dataset (o `texto_publicacao` reproduz o `texto_completo`); não valida a qualidade das perguntas nem que a resposta seja correta.
- O proxy de evidência cobre só 94 perguntas não-MULTI e só valores numéricos; não mede perguntas qualitativas nem MULTI.
- A fração de fronteiras limpas conta fim em `.`, `;` ou `:`; não verifica sentido semântico (ex.: tabelas de CNPJ separadas por `;`).
- Razão Qwen3/superfície medida em 12 chunks (1,31–2,04): o orçamento de contexto (~3K tokens Qwen3) deve ser conferido com o tokenizador real na etapa do gerador. Tokenizador do modelo de embeddings ainda não definido (D5).
- Duplicatas do corpus (76) não foram removidas; podem consumir posições no top-k.
- Textos gigantes (até 458 mil tokens) inflam o índice; não decidi corte nem filtro.
- Validação apenas (150). Nada foi avaliado no teste (350).
