# Resultados da auditoria (gerado por `python scripts/auditoria.py`)

Retreino com os mesmos dados reproduz o modelo salvo: **True**

## teste1 (n=80)

Acuracia da IA: 87.5% · automaticos: 57 com 6 erros (10.5%) · revisao humana: 23 (ja corretos: 19) · urgencias protegidas: 10/10 · nao urgentes marcados alta: 1

Matriz de confusao (linhas=real, colunas=previsto):

| real \ prev | agendame | exames_r | informac | medicame | reclamac | sintomas | vacinaca | visita_d |
|---|---|---|---|---|---|---|---|---|
| agendamento_consulta | 8 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |
| exames_resultados | 1 | 8 | 0 | 1 | 0 | 0 | 0 | 0 |
| informacoes_gerais | 0 | 1 | 7 | 0 | 2 | 0 | 0 | 0 |
| medicamentos | 0 | 0 | 0 | 8 | 0 | 0 | 1 | 1 |
| reclamacao_atendimento | 0 | 0 | 0 | 1 | 9 | 0 | 0 | 0 |
| sintomas_urgentes | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 |
| vacinacao | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| visita_domiciliar | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 |

| Classe | Precisao | Recall | F1 | n |
|---|---|---|---|---|
| agendamento_consulta | 0.889 | 0.8 | 0.842 | 10 |
| exames_resultados | 0.889 | 0.8 | 0.842 | 10 |
| informacoes_gerais | 0.875 | 0.7 | 0.778 | 10 |
| medicamentos | 0.8 | 0.8 | 0.8 | 10 |
| reclamacao_atendimento | 0.818 | 0.9 | 0.857 | 10 |
| sintomas_urgentes | 0.909 | 1.0 | 0.952 | 10 |
| vacinacao | 0.909 | 1.0 | 0.952 | 10 |
| visita_domiciliar | 0.909 | 1.0 | 0.952 | 10 |

Erros automaticos (encaminhados sem humano e errados):

- conf 0.6: esperado `agendamento_consulta`, obtido `informacoes_gerais` — Como posso agendar um horário com a ginecologista do posto?
- conf 0.51: esperado `medicamentos`, obtido `vacinacao` — O antibiótico prescrito não está disponível na unidade.
- conf 0.93: esperado `exames_resultados`, obtido `agendamento_consulta` — Preciso marcar uma ultrassonografia pedida pelo médico.
- conf 0.51: esperado `exames_resultados`, obtido `medicamentos` — Como faço para buscar o laudo da mamografia?
- conf 0.45: esperado `informacoes_gerais`, obtido `reclamacao_atendimento` — Vocês atendem sem agendamento ou tenho que ir cedo?
- conf 0.77: esperado `informacoes_gerais`, obtido `reclamacao_atendimento` — A unidade tem atendimento de fisioterapia?

Urgencias NAO protegidas (sem prioridade alta + humano):

- (nenhuma)

## teste2 (n=40)

Acuracia da IA: 82.5% · automaticos: 27 com 3 erros (11.1%) · revisao humana: 13 (ja corretos: 9) · urgencias protegidas: 4/5 · nao urgentes marcados alta: 2

Matriz de confusao (linhas=real, colunas=previsto):

| real \ prev | agendame | exames_r | informac | medicame | reclamac | sintomas | vacinaca | visita_d |
|---|---|---|---|---|---|---|---|---|
| agendamento_consulta | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| exames_resultados | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| informacoes_gerais | 0 | 0 | 3 | 1 | 0 | 1 | 0 | 0 |
| medicamentos | 1 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| reclamacao_atendimento | 1 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| sintomas_urgentes | 0 | 0 | 0 | 0 | 0 | 4 | 1 | 0 |
| vacinacao | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 |
| visita_domiciliar | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 4 |

| Classe | Precisao | Recall | F1 | n |
|---|---|---|---|---|
| agendamento_consulta | 0.625 | 1.0 | 0.769 | 5 |
| exames_resultados | 1.0 | 0.8 | 0.889 | 5 |
| informacoes_gerais | 1.0 | 0.6 | 0.75 | 5 |
| medicamentos | 0.8 | 0.8 | 0.8 | 5 |
| reclamacao_atendimento | 1.0 | 0.8 | 0.889 | 5 |
| sintomas_urgentes | 0.667 | 0.8 | 0.727 | 5 |
| vacinacao | 0.833 | 1.0 | 0.909 | 5 |
| visita_domiciliar | 1.0 | 0.8 | 0.889 | 5 |

Erros automaticos (encaminhados sem humano e errados):

- conf 0.62: esperado `medicamentos`, obtido `agendamento_consulta` — Como consigo pegar o inalador para meu filho asmático?
- conf 0.52: esperado `reclamacao_atendimento`, obtido `agendamento_consulta` — O médico só olhou para o computador e não me examinou.
- conf 0.67: esperado `sintomas_urgentes`, obtido `vacinacao` — Meu filho bateu a cabeça, vomitou e está sonolento demais.

Urgencias NAO protegidas (sem prioridade alta + humano):

- `vacinacao` conf 0.67 status encaminhado — Meu filho bateu a cabeça, vomitou e está sonolento demais.

## combinado (n=120)

Acuracia da IA: 85.8% · automaticos: 84 com 9 erros (10.7%) · revisao humana: 36 (ja corretos: 28) · urgencias protegidas: 14/15 · nao urgentes marcados alta: 3

Matriz de confusao (linhas=real, colunas=previsto):

| real \ prev | agendame | exames_r | informac | medicame | reclamac | sintomas | vacinaca | visita_d |
|---|---|---|---|---|---|---|---|---|
| agendamento_consulta | 13 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |
| exames_resultados | 2 | 12 | 0 | 1 | 0 | 0 | 0 | 0 |
| informacoes_gerais | 0 | 1 | 10 | 1 | 2 | 1 | 0 | 0 |
| medicamentos | 1 | 0 | 0 | 12 | 0 | 0 | 1 | 1 |
| reclamacao_atendimento | 1 | 0 | 0 | 1 | 13 | 0 | 0 | 0 |
| sintomas_urgentes | 0 | 0 | 0 | 0 | 0 | 14 | 1 | 0 |
| vacinacao | 0 | 0 | 0 | 0 | 0 | 0 | 15 | 0 |
| visita_domiciliar | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 14 |

| Classe | Precisao | Recall | F1 | n |
|---|---|---|---|---|
| agendamento_consulta | 0.765 | 0.867 | 0.812 | 15 |
| exames_resultados | 0.923 | 0.8 | 0.857 | 15 |
| informacoes_gerais | 0.909 | 0.667 | 0.769 | 15 |
| medicamentos | 0.8 | 0.8 | 0.8 | 15 |
| reclamacao_atendimento | 0.867 | 0.867 | 0.867 | 15 |
| sintomas_urgentes | 0.824 | 0.933 | 0.875 | 15 |
| vacinacao | 0.882 | 1.0 | 0.938 | 15 |
| visita_domiciliar | 0.933 | 0.933 | 0.933 | 15 |

Erros automaticos (encaminhados sem humano e errados):

- conf 0.6: esperado `agendamento_consulta`, obtido `informacoes_gerais` — Como posso agendar um horário com a ginecologista do posto?
- conf 0.51: esperado `medicamentos`, obtido `vacinacao` — O antibiótico prescrito não está disponível na unidade.
- conf 0.93: esperado `exames_resultados`, obtido `agendamento_consulta` — Preciso marcar uma ultrassonografia pedida pelo médico.
- conf 0.51: esperado `exames_resultados`, obtido `medicamentos` — Como faço para buscar o laudo da mamografia?
- conf 0.45: esperado `informacoes_gerais`, obtido `reclamacao_atendimento` — Vocês atendem sem agendamento ou tenho que ir cedo?
- conf 0.77: esperado `informacoes_gerais`, obtido `reclamacao_atendimento` — A unidade tem atendimento de fisioterapia?
- conf 0.62: esperado `medicamentos`, obtido `agendamento_consulta` — Como consigo pegar o inalador para meu filho asmático?
- conf 0.52: esperado `reclamacao_atendimento`, obtido `agendamento_consulta` — O médico só olhou para o computador e não me examinou.
- conf 0.67: esperado `sintomas_urgentes`, obtido `vacinacao` — Meu filho bateu a cabeça, vomitou e está sonolento demais.

Urgencias NAO protegidas (sem prioridade alta + humano):

- `vacinacao` conf 0.67 status encaminhado — Meu filho bateu a cabeça, vomitou e está sonolento demais.

## Sondagem qualitativa da camada de urgencia (NAO e metrica)

| Frase | Categoria | Conf. | Prioridade | Status |
|---|---|---|---|---|
| meu pai nao esta respirando | sintomas_urgentes | 0.84 | alta | revisao_humana |
| acho que minha mae esta tendo um infarto | visita_domiciliar | 0.51 | normal | encaminhado |
| suspeita de avc, braco dormente | sintomas_urgentes | 0.67 | alta | revisao_humana |
| crianca engoliu um produto de limpeza | sintomas_urgentes | 0.72 | alta | revisao_humana |
| tentativa de suicidio de um familiar | visita_domiciliar | 0.57 | normal | encaminhado |
| nao tenho dor no peito, so quero marcar consulta | agendamento_consulta | 0.93 | alta | revisao_humana |
| estou me sentindo muito mal e sozinho, sem esperanca | sintomas_urgentes | 0.4 | alta | revisao_humana |
| gestante sem sentir o bebe mexer desde ontem | sintomas_urgentes | 0.58 | alta | revisao_humana |