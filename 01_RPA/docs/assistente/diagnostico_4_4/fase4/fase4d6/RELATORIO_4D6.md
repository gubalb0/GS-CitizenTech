# Fase 4D.6 — Vínculo por frase como veto de falsos vínculos (candidata `fail-closed-4.4.4d1-cand`, não validada)

Convenção: **[OBS]** observado em documento/saída real; **[SIM]** simulação offline desta fase; **[JO]** julgamento de referência do autor (sem segundo avaliador humano); **[H]** hipótese. Nada foi implementado: nenhum código de produção, mecanismo B, alinhamento, catálogo, política de evidência positiva, S1 ou protótipo 4D.5 foi alterado; nenhuma geração; rótulos da 4D.5 intactos.

## 1. Integridade, versões e erratas
- `verificar_hashes.py` → TODOS CONFEREM antes e depois (ver §10). Candidata confirmada: `VERSAO_POLITICA = "fail-closed-4.4.4d1-cand"`; `geracao.py` c857b99f49947e1a, `evidencias.py` 12118192b9529075, `catalogo.py` 8e44143ba1d092f5.
- Relatórios 4D.4 e 4D.5 lidos. Hashes (16 car.) dos artefatos relevantes, registrados **no início desta fase** (os de 4D.4/4D.5 não tinham hash gravado antes; valem como referência a partir de agora):

| Arquivo | Hash |
|---|---|
| `fase4d4/RELATORIO_4D4.md` | a7f28c457a4903e7 |
| `fase4d4/CASOS_REAIS_4D4.md` | 6391f8a23b5dd8ab |
| `fase4d4/MATRIZ_AVALIACAO_4D4.csv` | ebca8ba1a81db64f |
| `fase4d5/RELATORIO_4D5.md` | b3fc640a9df4ea34 |
| `fase4d5/CASOS_REAIS_4D5.md` | e45b39caf493532d |
| `fase4d5/MODELO_RELACIONAL_4D5.md` | 25a23480c8e0cca1 |
| `fase4d5/ROTULAGEM_4D5.md` | dea66b5832807b7b |
| `fase4d5/CASOS_SINTETICOS_4D5.json` | 9a24350e98624ef4 |
| `fase4d5/ESPECIFICACAO_REAIS_4D5.json` | 988a9bfbb5fb16c4 |
| `fase4d5/CONGELAMENTO_ROTULAGEM_4D5.json` | 9ba4ad969581914d |
| `fase4d5/prototipo_vinculo_4d5.py` (v3, atual) | 01a60eb511cdced3 |
| `fase4d5/executar_4d5.py` | d11010dea0bfd1c3 |
| `fase4d5/resultados_4d5_detalhe.json` (v3) | 81ae2d7e84f85457 |
| `fase4d5/RESULTADOS_NIVEIS_4D5.csv` (v3) | ec4a24cfb85fcd82 |
| `fase4d5/execucao_v1/prototipo_vinculo_4d5.py` | 74c40509314ccad6 |
| `fase4d5/execucao_v1/RESULTADOS_NIVEIS_4D5.csv` | 17bef0c1e79cff66 |
| `fase4d5/execucao_v1/resultados_4d5_detalhe.json` | f55c374fc9ec5e1a |
| `fase4d5/execucao_v2/RESULTADOS_NIVEIS_4D5.csv` | 7d8be1a3fec94d9f |
| `fase4d5/execucao_v2/resultados_4d5_detalhe.json` | 0cf4130695c616c6 |
| `fase4d6/simular_veto_4d6.py` (versão única) | 2e0981fa8eb074ad |
- **Versões experimentais da 4D.5 preservadas:** v1 (código + resultados), v2 (**só resultados**; o código de v2 não foi salvo na época — registro a lacuna) e v3 (atual). Nada foi sobrescrito.
- **ERRATA da 4D.5 (descoberta nesta fase).** (i) A explicação dada na 4D.5 para a falha de val-083 VITAMINA D ("o termo 400 casou com R$ 20.400,00") **estava errada**: o único termo do item é "vitamina"; a causa é a linha 122 do protótipo (correção de pontos de abreviatura, "UI/G."), gravada com caracteres de controle (`\x08`, `\x01`) por escape não-raw, **que nunca casa**. (ii) Logo, a afirmação do §3 da 4D.5 de que a v3 corrigiu o tratamento de abreviatura é falsa; as demais correções da v3 (apelido entre parênteses, `, para`, `a quem`, papel só para localidades) funcionaram. (iii) Com a regex pretendida (cópia local, só diagnóstico) a relação de VITAMINA D vira `explicita`. O arquivo e os relatórios da 4D.5 **não foram modificados**; a correção está aqui. Aviso adicional: as métricas v3 da 4D.5 subestimam N1/N2 em pelo menos 1 alvo real.
- **Desvio metodológico:** o script de simulação desta fase tem **uma única versão**, sem reajuste após ver resultados.

## 2. Material
`POLITICAS_VETO_4D6.md`, `RESULTADOS_VETO_4D6.csv` (decisão por alvo × base × política), `RESUMO_VETO_4D6.csv` (agregados), `ANALISE_CASOS_REAIS_4D6.md`, `resultados_veto_4d6_detalhe.json` (inclui a sensibilidade), `simular_veto_4d6.py`.

## 3. Resultados [SIM] — sintéticos (27 alvos; positivos 9, negativos 11, documental 1, incertos 6) — base N3 / base N4
| Política | Falsos vínculos aceitos | Legítimas rejeitadas | Documental preservada | Conflitantes rejeitadas |
|---|---|---|---|---|
| V0 | 7 / 8 | 0 / 0 | 0 / 1 | 1/7 / 0/7 |
| V1 | 1 / 2 | 0 / 0 | 0 / 1 | 7/7 / 6/7 |
| V2 | 0 / 0 | 0 / 0 | 0 / 0 | 7/7 / 7/7 |
| V3 | 2 / 3 | 0 / 0 | 0 / 1 (encaminhada) | 6/7 / 5/7 |
Falsos vínculos residuais: V1 N3 = S07; V1 N4 = S07, S08 (entidade em frase ou chunk sem relação/outro papel: não há contradição, só proximidade); V3 acrescenta S26 em N3 e N4 (Gama como parte de outro nome; V3 não usa o componente c). S09 (documental em outro chunk) só é visível na base N4. Ambíguos/não verificáveis: V0 aceita 2+2, V1/V3 aceitam 1–2 deles; V2 os rejeita quase todos.

## 4. Resultados [SIM] — reais (7 alvos; esperados negativos 3, positivo 1, documental 2, ambíguo 1) — base N3 / N4
| Política | Falsos vínculos aceitos | Legítimas rejeitadas | Documentais preservadas | Conflitantes rejeitadas |
|---|---|---|---|---|
| V0 | 2 / 2 | 0 / 0 | 2 / 2 | 0/2 / 0/2 |
| V1 | 0 / 1 | 0 / 0 | 2 / 2 | 2/2 / 1/2 |
| V2 | 0 / 0 | **1 / 1** | 0 / 0 | 2/2 / 2/2 |
| V3 | 1 / 1 | 0 / 0 | 2 / 2 (HCB encaminhada) | 1/2 / 1/2 |
Sem precisão/recall: rótulos de um só autor e 7 alvos. Os 7 alvos são os mesmos usados para ajustar o analisador na 4D.5; não são validação independente.

## 5. Análise de sensibilidade [SIM]
- **Componentes de V1 (sintético, N4 / N3 falsos vínculos restantes):** só (a) 6 / 5; (a)+(b) 3 / 2; (a)+(b)+(c) 2 / 1; só (c) 7 / 6. Real (N3): (a) 2, (a)+(b) 1, (a)+(b)+(c) 0. (a) sozinho quase não ajuda; (b) e (c) carregam o efeito.
- **Dependência do inventário manual:** (a)/(b) só disparam para concorrentes que eu listei (HRS, Beta, HRG, HRAN/HRS/HRL/CRT). Fora desse inventário o veto não existe. É a principal limitação do veto por contradição.
- **Remover a exigência de entidade na mesma frase:** equivale ao componente (b) (veta pela presença de *outra* entidade na unidade do atributo, sem exigir a entidade avaliada). Funciona nos casos com inventário; risco [H]: vetar resposta legítima cujo trecho cita incidentalmente outra entidade (p.ex. órgão contratante) — **não observado** (0 legítimas rejeitadas), mas não há caso para testá-lo.
- **Permitir anáfora / frases adjacentes:** os dois únicos alvos aceitos só por N2 são S03 e S22, ambos por anáfora (nenhum por introdução com `:`); sem anáfora ou sem adjacência N2 perde os dois. Nos reais, N2 não aceita nada que N1 não aceitasse.
- **Aceitar relações documentais:** V3 com documental aceito eleva falsos vínculos (sintético N4: 3→3 mantido; real: 1 mantido) sem mudar legítimas, e preserva o documental. A busca de "relação explícita em outra unidade" **confundiu registros vizinhos** em S17 (o registro da máscara serviu de falso apoio por compartilhar o termo genérico "cirúrgica"); só não virou aceitação porque o veto (b) a precede. Nos reais, essa busca não achou nenhuma relação documental explícita (CRSSU e val-020 ficam `nao_verificavel`).
- **Registros vizinhos:** nenhum alvo esperado-negativo foi aceito por N1/N2; 5 casos com `adjacente_sem_vinculo` (S04, S11, S17, S21, val-083). 
- **Risco de bloquear respostas corretas que repetem nomes:** V0/V1/V3 não rejeitam nenhum positivo nem documental; V2 rejeita S09 (sintético) e, nos reais, VITAMINA D (por defeito do analisador), CRSSU e HCB.
- **Parser/papel:** a heurística de papel marcou "OUV-Gama" (unidade 26, fora do contexto) como menção direta, o que impede o veto (c) em base N4 para val-087; uma falha do detector, não da política.

## 6. Respostas às perguntas de encerramento
1. **Veto por contradição explícita é mais seguro que o veto por ausência?** Nesta amostra, sim em termos de **não rejeitar legítimas e documentais** (V1/V3: 0 e 0 em ambos os conjuntos; V2: rejeita S09, CRSSU, HCB e VITAMINA D). Em contrapartida V1/V3 **deixam passar** falsos vínculos sem contradição (S07, S08, S26, val-087 Gama em N4): aceitam proximidade. V2 zera falsos vínculos, mas por rejeitar tudo o que não é frase. "Mais seguro" vale apenas no sentido de preservar respostas; não é sinônimo de proteger contra falsos vínculos.
2. **É possível preservar relações documentais legítimas sem aceitar proximidade?** Parcialmente. V3 as encaminha em vez de aceitar, e o critério "sujeito da publicação" separou S09/val-031 de S07/S08 (menção sem relação). Mas só 2 dos 4 alvos documentais/ambíguos-documentais foram identificados (CRSSU e val-020 não); o critério é frágil (primeira unidade + inventário) e a busca de relação explícita em outras unidades falhou em reais e confundiu registros em S17.
3. **O vínculo por frase agrega informação nova ou reproduz as limitações de N1/N2?** Agrega informação no lado **negativo**: reconhece atribuição a outra entidade/atributo dentro da unidade do atributo (S02, S11, S15, S17, S21b, val-083 CLORETO), o que N3/N4 não veem; no lado de **aceitação** apenas reproduz as limitações de N1/N2 (V2). A informação nova depende do inventário manual de entidades e de heurísticas lexicais.
4. **Há evidência suficiente para um protótipo integrado futuro?** **Não.** 7 alvos reais ajustados ao analisador, rótulos de um só autor, dependência de inventário manual, um defeito de analisador descoberto só agora (errata), e a única proteção sem inventário (c) falha em N4 para val-087. A hipótese de veto é **plausível e merece teste independente**, mas não está sustentada o bastante para integração.

## 7. Distinção entre evidências
Observado em documentos reais: textos dos docs 174, 718, 1464, 361, 495, 1444 (ver `ANALISE_CASOS_REAIS_4D6.md`). Simulações: §3–§5. Julgamentos: rótulos da 4D.5 e leituras de "documental legítima" (val-031) e "resposta correta sem o elemento herdado". Hipóteses: risco de vetar legítimas por (b), uso de V1/V3 só como sinal de alerta, melhoria com inventário automático.

## 8. Limitações
Mesmo autor para casos, rótulos, protótipo e simulação; conjuntos pequenos; alvos reais reutilizados da 4D.5; inventário manual; heurísticas lexicais; defeito de analisador (errata) que afeta VITAMINA D; v2 sem código preservado; hashes de 4D.4/4D.5 registrados só agora; sem validação em outros textos do corpus.

## 9. Passos que dependem de autorização
Segunda avaliação humana dos rótulos 4D.5/4D.6; inventário automático de entidades (ou teste sem inventário); correção do analisador (linha 122) em nova versão preservada, com reexecução da 4D.5; mais casos reais com texto integral; qualquer protótipo integrado ou flag.

## 10. Integridade final
Ao encerrar: `verificar_hashes.py` → TODOS CONFEREM; `geracao.py`, `evidencias.py`, `catalogo.py` idênticos; protótipo 4D.5 (v3), v1, v2, resultados e relatórios 4D.4/4D.5 com os mesmos hashes da tabela do §1; nenhum arquivo fora de `fase4d6/` modificado depois do fim da 4D.5 (por data de modificação); sem geração, LM Studio ou API.
