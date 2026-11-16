# Auditoria da IA de classificação (modelo congelado)

> ## ⛔ Aptidão de uso
> **A solução NÃO está apta para triagem clínica nem para encaminhamento autônomo de solicitações reais.** É um protótipo acadêmico, avaliado só com dados sintéticos e testes escritos pela própria equipe. Falhas de segurança conhecidas e **não corrigidas**: (1) um caso de **trauma craniano** ("bateu a cabeça, vomitou e está sonolento") foi classificado como vacinação e encaminhado sem revisão humana; (2) uma sondagem qualitativa mostrou que **infarto** não dispara prioridade alta (caiu em visita domiciliar, encaminhado); (3) **crise de saúde mental / tentativa de suicídio** não é reconhecida: não há categoria nem regra, e o caso foi encaminhado automaticamente. Cerca de 1 em 9 encaminhamentos automáticos nos testes estava errado. Qualquer regra de urgência futura deve ser uma **etapa separada**, com critérios revisados por profissionais de saúde.


Auditoria somente leitura, reproduzível com `python scripts/auditoria.py` (tabelas completas em `docs/auditoria_resultados.md/.json`). Nenhum dado, teste, regra ou modelo foi alterado nesta etapa de auditoria, e nenhuma configuração foi escolhida nela consultando resultados. (A configuração do modelo foi escolhida **antes** do congelamento, entre 4 opções, olhando os testes; ver a seção 5.)

## 1. Estado atual do modelo
- **Versão congelada** registrada em `docs/modelo_congelado.json` (hashes SHA-256 de treino, testes, modelo e regras; versões de Python, scikit-learn, numpy e joblib), com o vocabulário dos dois TF-IDF incluído no próprio manifesto. Re-treinar com os mesmos dados reproduz as probabilidades do modelo salvo (verificado).
- **Features:** TF-IDF de palavras (1–2-gramas, `sublinear_tf`, 1.651 termos) + TF-IDF de caracteres (`char_wb`, 3–5-gramas, `sublinear_tf`, 3.998 termos), texto sem acentos e em minúsculas.
- **Classificador:** Regressão Logística (`C=10`, `lbfgs`, `max_iter=1000`), 8 classes, treinada em 640 textos **sintéticos** de template (80/classe).
- **Decisão:** vai a humano se confiança < 0,45, categoria indefinida, categoria `sintomas_urgentes` ou termo de urgência (lista fixa em `regras.py`). O limiar 0,45 **não foi calibrado**.

### Integridade e rastreabilidade
`docs/modelo_congelado.json` foi criado em 10/11/2026 às 21:05:38 (campo `data_auditoria`, igual à data de modificação do arquivo) a partir dos arquivos originais, sem modificação. Antes disso, uma versão anterior do manifesto havia sido gerada em `docs/congelamento/` e foi removida quando o arquivo passou para o caminho atual; segundo o relato da sessão, os hashes eram os mesmos, mas **essa versão anterior não foi preservada**, então a coincidência **não pode ser comprovada**. Desde a criação do manifesto atual, `scripts/auditoria.py` não o sobrescreve: nas execuções seguintes só confere os hashes e **aborta** se treino, testes, modelo ou regras divergirem. Nesta etapa não foram alterados modelo, treinamento, dados, testes existentes, regras de classificação nem regras de encaminhamento. (Observação de rastreabilidade: o treino e o modelo foram modificados em etapas anteriores, antes do congelamento, quando o treino foi ampliado de 360 para 640 textos e foram adicionados n-gramas de caracteres; ver `docs/evidencias.md`.)

### Escopo e limites do manifesto SHA-256 (pendência I-13; documentado na rodada 7, 11/11/2026)
**O que o manifesto protege.** Exatamente **seis arquivos** (`scripts/auditoria.py:41–48`), cujo SHA-256 está registrado no campo `sha256` de `docs/modelo_congelado.json`:
1. `data/treino.csv`
2. `data/teste_rotulado.csv`
3. `data/teste_cego.csv`
4. `data/modelo/classificador.joblib`
5. `citizentech/classificador.py`
6. `citizentech/regras.py`

**O que a verificação comprova.** Somente que, no momento em que `python scripts/auditoria.py` é executado, cada um desses seis arquivos tem o **mesmo SHA-256 registrado no manifesto**; se algum divergir, o script aborta com "INTEGRIDADE VIOLADA" (`scripts/auditoria.py:57–62`).

**O que ela não comprova.**
- **Não comprova a integridade de todos os arquivos do projeto.**
- **Não estão protegidos por este manifesto:** o **próprio script de auditoria** (`scripts/auditoria.py`); os **demais módulos** (`citizentech/texto.py`, `pipeline.py`, `config.py`, `geo.py`, `estado.py`, `ingestao.py`, `validacao.py`, `logs.py` e `main.py`); os scripts `scripts/validar.py` e `scripts/gerar_treino.py`; os **testes** (`tests/`); as **dependências** (`requirements.txt` e `requirements-congelado.txt`); `data/inbox/`, `validacao_independente/` e a **documentação**; e **o próprio manifesto**, que não tem assinatura nem carimbo de tempo externo. Em particular, `texto.py` normaliza o texto antes de ele chegar ao modelo: uma alteração ali mudaria as previsões **sem ser detectada**.
- Também não comprova a qualidade ou a segurança do modelo, a independência dos testes nem a ausência de vazamento de dados.

**Recriação automática do manifesto.** Se `docs/modelo_congelado.json` **não existe**, `scripts/auditoria.py` **o cria** com os hashes dos arquivos naquele momento (`scripts/auditoria.py:55–93`), e a conferência passa a comparar o estado atual com um manifesto novo. Portanto, **a ausência do manifesto não deve ser tratada como uma verificação válida de integridade histórica**: a conferência só tem sentido quando o manifesto **original** está presente e preservado (uma referência independente são os seis hashes exibidos na captura `docs/evidencias_visuais/02_auditoria_integridade_ok.png`).

**Data do manifesto.** O campo `data_auditoria` (`2026-11-10T21:05:38`) indica **quando os hashes foram registrados**, não uma garantia independente de que os arquivos estavam íntegros antes dessa data (o treino e o modelo foram alterados em etapas anteriores, como descrito acima) nem de que o manifesto não possa ser recriado depois.

*Esta descrição foi feita sem alterar `scripts/auditoria.py` nem o funcionamento da auditoria.*

**Fechamento (fase final, 10/11/2026).** Após o congelamento foram feitas apenas mudanças que **não afetam modelo, treino, dados, testes existentes nem regras** (hashes conferidos antes e depois): (a) `main.py` passou a usar o modelo salvo sem sobrescrevê-lo (antes, um clone poderia retreinar e gravar um `.joblib` com hash diferente, pois o retreino reproduz as probabilidades mas não os bytes); (b) `scripts/validar.py` passou a **relatar** a métrica de urgência também para o teste 2 e o conjunto combinado e a listar a urgência não protegida (apenas apresentação; as métricas de IA e de ponta a ponta não mudaram); (c) `.gitignore`, `.gitattributes` (`* -text`, para preservar bytes e hashes) e `requirements-congelado.txt`; (d) `docs/exemplo_saida/` e `docs/matriz_requisitos.md`.

## 2. Resultados nos testes existentes (pipeline completo: IA + regras)
| | Teste 1 (n=80) | Teste 2 (n=40) | Combinado (n=120) |
|---|---|---|---|
| Acurácia só da IA | 87,5% | 82,5% | 85,8% |
| Encaminhados automaticamente | 57 | 27 | 84 |
| **Erros entre os automáticos** | 6 (10,5%) | 3 (11,1%) | **9 (10,7%)** |
| Enviados a humano | 23 (19 já corretos) | 13 (9 já corretos) | 36 (28 já corretos) |
| Urgências protegidas (prioridade alta + humano) | 10/10 | **4/5** | **14/15 (93,3%)** |
| Não urgentes marcados prioridade alta | 1/70 | 2/35 | 3/105 |

**Correção de afirmações anteriores.** (a) "10/10 urgências" valia só para o teste 1; no teste 2 uma urgência não foi protegida. (b) "~90% de acerto nos automáticos" contava só pela confiança; contando como o robô decide (também mandando prioridade alta a humano), cerca de **1 em cada 9 encaminhamentos automáticos está errado**. Na versão original do `scripts/validar.py`, a métrica de urgência cobria apenas o teste 1; depois do fechamento descrito acima (item b), ele também relata o teste 2 e o conjunto combinado (14/15, o mesmo valor de `scripts/auditoria.py`) e lista a urgência não protegida. A medida de referência continua sendo a de `scripts/auditoria.py`.

## 3. Análise dos erros
**Por classe (combinado, n=15 cada)**
| Classe | Precisão | Recall | F1 |
|---|---|---|---|
| vacinacao | 0,88 | 1,00 | 0,94 |
| visita_domiciliar | 0,93 | 0,93 | 0,93 |
| sintomas_urgentes | 0,82 | 0,93 | 0,88 |
| reclamacao_atendimento | 0,87 | 0,87 | 0,87 |
| exames_resultados | 0,92 | 0,80 | 0,86 |
| agendamento_consulta | 0,76 | 0,87 | 0,81 |
| medicamentos | 0,80 | 0,80 | 0,80 |
| informacoes_gerais | 0,91 | 0,67 | 0,77 |

- **Confusões mais frequentes:** exames → agendamento (2) e informações → reclamação (2). `agendamento_consulta` funciona como "ralo" (recebe 3 dos 9 erros automáticos).
- **Erros automáticos (9):** ultrassonografia → agendamento (conf 0,93); laudo de mamografia → medicamentos; antibiótico em falta → vacinação; inalador → agendamento; informações sobre fisioterapia e sobre atendimento sem agendamento → reclamação; ginecologista → informações; "médico só olhou o computador" → agendamento; **trauma craniano com vômito e sonolência → vacinação**.
- **Confiança:** acima de 0,8, 98% de acerto (n=60); entre 0,45 e 0,6, 71% (n=17); abaixo de 0,3, 50% (n=4). Há erros de **alta confiança** (0,93) que nenhum limiar captura; o limiar só separa o que é fraco, não o que é arriscado.
- **Revisão humana:** 28 dos 36 casos enviados já estavam corretos (carga de trabalho desnecessária de ~78%), preço aceitável pela segurança, mas a ser acompanhado.

## 4. Risco operacional por categoria
1. **sintomas_urgentes — crítico.** Falso negativo clínico real (trauma craniano → vacinação, encaminhado). Sondagem qualitativa (8 frases do auditor, **não é métrica**): "infarto" → visita domiciliar e "tentativa de suicídio" → visita domiciliar, ambos prioridade normal e encaminhados automaticamente; não há categoria nem regra para crise de saúde mental; não há tratamento de negação ("não tenho dor no peito…" → alta; erra para o lado seguro).
2. **medicamentos — alto.** F1 0,80; interrupção de tratamento contínuo (insulina etc.) pode passar despercebida.
3. **exames_resultados — médio-alto.** Erro com confiança 0,93.
4. **informacoes_gerais — médio.** Recall 0,67; perguntas viram "reclamação".
5. **agendamento_consulta / reclamacao_atendimento — médio-baixo.**

## 5. Ressalvas metodológicas
- Os dois testes **não são independentes**: o teste 1 foi analisado (erros vistos) antes da ampliação do treino e o teste 2 foi escrito e visto pela equipe de desenvolvimento; a configuração do modelo (palavras+caracteres, `C=10`) foi escolhida entre 4 opções olhando esses testes. As frases adicionadas ao treino não copiam os testes, mas o vocabulário do domínio se sobrepõe.
- **Amostras pequenas:** 5 a 15 casos por classe; um erro muda uma métrica de classe em 7 a 20 pontos. Não há intervalos de confiança nos testes existentes; o IC95% de Wilson para 9/84 de erro automático (~10,7%) é ≈ 5,7–19%.
- Treino sintético por templates; textos reais tendem a ser mais difíceis (abreviações, gírias, relatos longos, múltiplos pedidos).
- Rótulos escritos pelos próprios desenvolvedores; **nenhuma revisão por profissional de saúde**; lista de termos de urgência não validada clinicamente.

## 6. Limitações (ainda não resolvidas)
- Possível urgência clínica pode ser encaminhada sem revisão (1 caso medido em 15 e 2 em 8 sondagens qualitativas).
- Sem categoria/regra para saúde mental; sem tratamento de negação, abreviações ou múltiplas demandas.
- Limiar de confiança não calibrado; erros de alta confiança não detectáveis por confiança.
- Só 8 categorias; textos fora do escopo tendem a cair em alguma categoria (não medido).
- Nenhuma validação independente foi executada.

## 7. Protocolo de validação independente
Estrutura pronta em `validacao_independente/` (papéis, requisitos do conjunto, instruções de coleta e rotulagem, lacre e avaliador único). **Status: não executada; nenhum conjunto foi coletado e nenhum resultado independente existe.** O avaliador recusa rodar se conjunto, modelo ou regras mudaram desde o lacre. A mecânica foi testada com um CSV minúsculo gerado nos testes automatizados (`tests/test_avaliacao_independente.py`), o que **não** constitui validação do modelo.

## 8. Recomendações para uso seguro
1. **Não usar em produção.** O resultado atual é de protótipo acadêmico com dados sintéticos.
2. Se piloto: **modo sombra** (o robô sugere, humano decide tudo) e coleta dos desacordos.
3. **Nenhuma classificação substitui triagem clínica.** Todo texto que mencione sintoma, estado de saúde ou risco deve ir a humano, independentemente da categoria.
4. **Antes de qualquer piloto**, resolver com validação clínica: falsos negativos de urgência (trauma, infarto, saúde mental), nova categoria/regra de crise de saúde mental e tratamento de negação. Qualquer mudança exige novo congelamento **e novo conjunto independente**.
5. Exigir confirmação humana para `medicamentos` e `exames_resultados`; reservar encaminhamento automático a categorias administrativas de baixo risco.
6. Calibrar o limiar com dados independentes e reportar IC95%.
7. Exibir sempre o aviso de emergência (SAMU 192/UPA) ao cidadão e registrar toda decisão para auditoria.
8. Monitorar erro por categoria, perfil e bairro; revisar periodicamente por amostragem.
