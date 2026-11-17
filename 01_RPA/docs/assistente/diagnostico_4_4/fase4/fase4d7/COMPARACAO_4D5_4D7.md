# Comparação 4D.5 (original) × 4D.7 (corrigido)

Mesmos casos, mesmas perguntas, mesmos documentos e **mesmos rótulos** (`CONGELAMENTO_ROTULAGEM_4D5.json` verificado por asserção no executor; hashes dos casos/rotulagem inalterados). Única diferença entre as execuções: a linha 122 do analisador (ver `diff_analisador_4d5_4d7.patch`). Dados alvo a alvo: `RESULTADOS_4D7.csv`. Não se calculam precisão nem recall: os rótulos não tiveram segundo avaliador humano; "concordância" abaixo é só a comparação de cada alvo com o rótulo congelado.

## Controle de reprodutibilidade
O artefato original (`fase4d5/resultados_4d5_detalhe.json`, hash 81ae2d7e84f85457) existe e **não foi tocado**. Para garantir que a comparação não depende de reconstrução silenciosa, reexecutei o protótipo **original** (4D.5) em um script fora do projeto: os 34 alvos (27 sintéticos + 7 reais) reproduziram **exatamente** (estados, aceitações e rótulos) o resultado armazenado. A diferença abaixo, portanto, vem só da correção.

## O que mudou
Um alvo de 34 mudou; nenhum dos 27 sintéticos mudou.

| Alvo | Rótulo 4D.5 | N1 orig → corr | N2 orig → corr | N3 | N4 |
|---|---|---|---|---|---|
| val-083 **VITAMINA D** | sustentado | `coocorrencia` → **`explicita`** (rejeita → aceita) | `ausente` → **`explicita`** (rejeita → aceita) | `mesmo_chunk` (sem mudança) | `mesma_publicacao` (sem mudança) |
Concordância com o rótulo para esse alvo: N1/N2 de "perda de recall" para "acerto".

## O que não mudou (casos reais)
| Alvo | N1 | N2 | N3 | N4 |
|---|---|---|---|---|
| val-087 Gama (esperado: outra entidade) | ausente | ausente | aceita (falso vínculo) | aceita (falso vínculo) |
| val-087 CRSSU (esperado: só documental) | ausente | ausente | aceita | aceita |
| val-024 Hospital Regional de Ceilândia (herdado) | ausente | ausente | ausente | ausente |
| val-031 HCB (só documental) | ausente | ausente | aceita (proximidade/sigla) | aceita (sujeito da publicação) |
| val-020 Gama (ambíguo) | ausente | ausente | ausente | aceita |
| val-083 CLORETO (outra entidade: Hospital Regional do Guará) | ausente | `adjacente_sem_vinculo` | aceita (falso vínculo) | aceita (falso vínculo) |
As ocorrências e os motivos (campo `detalhes`) são idênticos aos originais em todos os 34 alvos, inclusive o registro do CLORETO: o vínculo do CLORETO **não** foi alterado.

## Sintéticos (27 alvos)
Estados, aceitações e classes idênticos nos quatro níveis. Os resultados sintéticos de N1 e N2 da 4D.5 permanecem válidos como foram relatados (com a ressalva já feita lá: o analisador foi ajustado a esses casos).

## Regressões
Nenhuma: não há alvo cuja aceitação em N1/N2 tenha passado de correta para incorreta, e nenhum alvo esperado-negativo passou a ser aceito por N1 ou N2.

## Efeito sobre afirmações da 4D.5 (sem reescrever os relatórios anteriores)
- "Perda de recall legítima em N1/N2 = 1 (VITAMINA D)" → **0** nos reais. O motivo atribuído na 4D.5 ("400 casou com R$ 20.400,00") continua **incorreto**; a causa foi a regex defeituosa (errata da 4D.6).
- "De 3 alvos com algum suporte (VITAMINA D, CRSSU, HCB), N1/N2 aceitam 0" → N1/N2 aceitam **1** (VITAMINA D); CRSSU e HCB (relações só documentais) continuam rejeitados por N1/N2.
- Falsos vínculos: N1/N2 = 0, N3 = 2, N4 = 2 nos reais e 0/7/8 nos sintéticos — inalterados.
- Implicação para a 4D.6 (**não re-simulada**): com N1 = `explicita`, a categoria derivada de VITAMINA D seria `citada` e V2 deixaria de rejeitá-la; os números da 4D.6 que dependem desse alvo (legítima rejeitada por V2) estão superados por esta correção.
