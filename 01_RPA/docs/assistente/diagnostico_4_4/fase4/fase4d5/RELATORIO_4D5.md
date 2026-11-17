# Fase 4D.5 — Protótipo offline de vínculo entidade–atributo em nível de frase (candidata `fail-closed-4.4.4d1-cand`, não validada)

Convenção: **[DOC]** evidência documental real; **[SINT]** caso sintético; **[JO]** julgamento de referência do autor (não independente); **[EXEC]** resultado executado do protótipo; **[H]** hipótese. **Não há segundo avaliador humano**: todos os rótulos desta fase são do mesmo autor dos casos e do protótipo. Nenhum código de produção foi alterado; nenhuma geração; flags e S1 intactas; o protótipo **não** corrige o pipeline e não foi integrado a nada.

## 1. Integridade e referência
- **Antes:** `verificar_hashes.py` → TODOS CONFEREM. Candidata confirmada: `VERSAO_POLITICA = "fail-closed-4.4.4d1-cand"`; `geracao.py` c857b99f49947e1a, `evidencias.py` 12118192b9529075, `catalogo.py` 8e44143ba1d092f5. Relatórios 4D.1–4D.4 lidos/consultados (4D.1, 4D.3 e 4D.4 produzidos nesta sessão; 4D.2 relido no cabeçalho).
- **Depois:** ver §11.
- Tudo novo está em `fase4/fase4d5/`. Rotulagem congelada antes da execução (`CONGELAMENTO_ROTULAGEM_4D5.json`, verificada por asserção no executor).

## 2. Material criado
`MODELO_RELACIONAL_4D5.md`, `CASOS_SINTETICOS_4D5.json` (26 casos, 27 alvos), `ESPECIFICACAO_REAIS_4D5.json`, `ROTULAGEM_4D5.md`, `RESULTADOS_NIVEIS_4D5.csv`, `CASOS_REAIS_4D5.md`, `RELATORIO_4D5.md`; scripts `construir_casos_4d5.py`, `prototipo_vinculo_4d5.py`, `executar_4d5.py`; apoio `resultados_4d5_detalhe.json`, `execucao_v1/` e `execucao_v2/` (execuções anteriores preservadas).

## 3. Desvio de procedimento: o protótipo foi ajustado depois de ver resultados
A 1ª execução (v1) revelou defeitos do analisador (parênteses de apelido como "(HRT)", abreviatura "UI/G.", oração relativa "a quem compete", ", para…" de destinatário e verificação de papel aplicada a organizações). Corrigi em duas rodadas (v2, v3), **sem tocar nos rótulos**. Efeito no sintético (N1 recall / N2 recall): v1 0,33 / 0,56 → v2 0,44 / 0,67 → v3 **0,78 / 1,00**. Precisão de N1/N2 permaneceu 1,0 nas três. **Os números finais de N1/N2 no sintético foram obtidos depois de ajustar o analisador a esses casos e não são evidência de generalização.** Resultados v1 e v2 estão em `execucao_v1/` e `execucao_v2/`.

## 4. Resultados sintéticos [SINT][EXEC] (27 alvos; positivos 9, negativos 11, só-documental 1, incertos 6)
| Nível | TP | FP (falso vínculo) | FN (perda de recall) | TN | Precisão | Recall | Só-documental | Incertos aceitos/rejeitados |
|---|---:|---:|---:|---:|---:|---:|---|---|
| N1 mesma frase | 7 | 0 | 2 | 11 | 1,00 | 0,78 | rejeitado | 1 / 5 |
| N2 + adjacentes com vínculo | 9 | 0 | 0 | 11 | 1,00 | 1,00 | rejeitado | 1 / 5 |
| N3 mesmo chunk (ingênuo) | 9 | 7 | 0 | 4 | 0,56 | 1,00 | rejeitado | 4 / 2 |
| N4 mesma publicação (ingênuo) | 9 | 8 | 0 | 3 | 0,53 | 1,00 | aceito | 4 / 2 |
- Precisão/recall só foram calculados porque os rótulos permitem (positivo vs negativo); incertos (`nao_verificavel`/`ambiguo`) e `sustentado_documental` ficam fora, e a rotulagem não tem segundo avaliador.
- **Falsos vínculos do N3 (7):** S02 (coocorrência com contratante diferente), S07 (menção em frase não relacionada), S11 e S21b (atributo de outra entidade em frase adjacente), S15 (entidade só como titular), S17 (destinatário diferente), S26 (Gama como parte de "Conselhos de Saúde do Gama"). N4 acrescenta S08 (testemunha em outro chunk). Entidade só na pergunta (S06, S16) e em outra publicação (S10) são rejeitadas em todos os níveis.
- **Perdas de N1:** S03 e S22 (anáfora), recuperadas em N2. **S20** (relação cortada na fronteira de chunk; esperado `nao_verificavel`) é aceito em N1/N2 porque a **frase** inteira contém o HRT, embora o span citado só tenha o fim dela: o nível de frase "completa" a citação truncada — comportamento a decidir por humano.
- **Exigência de mais que coocorrência:** S02 (Alfa observa que a Beta contratará) é rejeitado em N1 por haver outra entidade mais perto do atributo; S19 (consórcio, "a primeira") também é rejeitado — esperado `ambiguo`.

## 5. Resultados reais [DOC][EXEC] (7 alvos em 5 casos; sem precisão/recall pooled)
| Alvo | Esperado [JO] | N1 | N2 | N3 | N4 |
|---|---|---|---|---|---|
| val-087 A-r1, Gama | não sustentado (outra entidade) | rejeita | rejeita | **aceita (falso vínculo)** | **aceita (falso vínculo)** |
| val-087 A-r1, CRSSU | só documental | rejeita | rejeita | aceita | aceita |
| val-024, Hosp. Reg. de Ceilândia | não sustentado (herdado) | rejeita | rejeita | rejeita | rejeita |
| val-031, HCB | só documental | rejeita | rejeita | aceita (proximidade, alias HCB) | aceita (sujeito da publicação) |
| val-020, Gama | ambíguo | rejeita | rejeita | rejeita | aceita |
| val-083, VITAMINA D (Atenção Primária) | sustentado | **rejeita (limitação do parser)** | rejeita | aceita | aceita |
| val-083, CLORETO (destinatário HRG) | outra entidade | rejeita | rejeita | **aceita (falso vínculo)** | **aceita (falso vínculo)** |
Contagem: falsos vínculos N1/N2 = 0, N3 = 2, N4 = 2; perdas de recall legítimas N1/N2 = 1 (VITAMINA D, defeito do parser, que casou o "400" de "R$ 20.400,00"); documentais rejeitadas em N1/N2 = 2 (CRSSU, HCB). Detalhes e textos em `CASOS_REAIS_4D5.md`.

## 6. Comparação com a referência atual (baseline e variantes 4D.3/4D.4)
1. **CRSSU–competência:** pelo texto citado (inciso IX) o protótipo **não** identifica a relação (IX não nomeia a CRSSU); só aparece em nível de chunk/publicação (Art. 1º/2º). É uma relação documental, não de frase.
2. **Gama em outra frase não vira evidência automática para o inciso IX:** sim em N1/N2 (rejeita); N3/N4 aceitam. As menções a Gama no contexto são partes de outros nomes (HRG, Conselhos, Ouvidoria); o vínculo "por chunk" da 4D.4 é, de fato, falso vínculo. Isto **não** mostra que o pipeline passaria a bloquear A-r1: o protótipo não está ligado a ele.
3. **Preserva respostas corretas que repetem nomes da pergunta?** Só quando o nome está na frase/adjacente (S01, S12, S25 etc.). Quando o nome só existe no documento (val-031) ou em outra parte do ato (val-020), N1/N2 rejeitam — **perda de recall documental**, igual ao problema da C simplificada em nível de chunk (4D.4). O protótipo não separa o "eco da pergunta" (qualificador) do conteúdo central da resposta.
4. **Destinatário em val-083:** distingue o destinatário do registro da entidade em registro vizinho (CLORETO rejeitado em N1/N2), mas não confirma o positivo (VITAMINA D) por defeito do parser.
5. **val-031:** N1/N2 não recuperam a relação; N4 a recupera como `sujeito_da_publicacao` (relação documental com base na primeira frase), N3 só por proximidade+alias. Distinguir proximidade de relação documental depende de regra "sujeito da publicação" e de inventário manual de concorrentes.
6. **Falsos vínculos vs. chunk:** N1/N2 0 vs N3 7 (sintético) e 0 vs 2 (real).
7. **Sem contexto humano não se decide:** val-020 (filial no Gama), val-083 (gabarito × texto), S05/S19/S24 (anáfora/ordem/eco ambíguos), se vínculo só documental basta (val-031), e o que fazer com o eco (qualificador) da pergunta.

## 7. Falsos vínculos e perdas de recall — síntese
Falsos vínculos: concentram-se nos níveis que usam proximidade (N3/N4); N1/N2 zero em ambos os conjuntos. Perdas de recall: N1/N2 perdem relações **só documentais** (CRSSU, val-031, val-020, S09) e dependem de anáfora/lexicon (S03/S22 só em N2); o analisador falha em casos reais com valores numéricos (VITAMINA D). O custo não é pequeno: nos reais, de 3 alvos com algum suporte (VITAMINA D, CRSSU, HCB) o N1/N2 aceita 0.

## 8. Casos que exigem interpretação humana
val-020, val-083 (gabarito), val-031 (suficiência da relação documental), S05, S19, S20, S24; e a decisão de política sobre qualificadores herdados da pergunta.

## 9. Limitações
Rótulos e casos do mesmo autor, sem segundo avaliador humano; protótipo ajustado depois de ver resultados (§3); 26 casos sintéticos escritos para estes mesmos contrastes e 5 reais; heurísticas lexicais, sem análise sintática; inventário de entidades concorrentes manual (influencia o `sujeito_da_publicacao` e o veto de "outra entidade"); termos numéricos casam fora da relação; verificação de papel só para localidades; segmentação ajustada a estes documentos; contexto enviado ao modelo reconstruído por replay e unidades fora do contexto contam em N4; confiança não é estimada pelo protótipo; não se usaram os 150 históricos como validação.

## 10. Recomendação técnica
Não implementar nem integrar. O protótipo demonstra, em nível experimental, que **vínculo em nível de frase/adjacência elimina os falsos vínculos que o nível de chunk/publicação introduz** (val-087 Gama, val-083 destinatário), mas **não resolve** a perda de relações só documentais e não decide casos ambíguos. Conclusão sustentada pelos dados: usar o vínculo de frase, se um dia for aproveitado, como **sinal de veto de um falso vínculo** (aceitar N3/N4 só se N1/N2 não indicam outra entidade/outro atributo) e não como condição de aceitação [H, não testada]; tratar o qualificador herdado da pergunta separadamente do conteúdo central também é hipótese. Antes de qualquer avanço: segunda avaliação humana dos rótulos; mais casos reais (hoje 5); decisão de política para vínculo só documental e para eco da pergunta. Tudo isso depende de autorização.

## 11. Integridade final
Ao encerrar: `verificar_hashes.py` → TODOS CONFEREM; `geracao.py`, `evidencias.py`, `catalogo.py` idênticos (c857b99f49947e1a / 12118192b9529075 / 8e44143ba1d092f5); arquivos da 4D.3 com os mesmos hashes de antes; nenhum arquivo fora de `fase4d5/` modificado desde o fim da 4D.4 (verificação por data de modificação); sem geração, sem LM Studio/API.
