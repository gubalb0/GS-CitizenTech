# Resultados da validacao (gerado por `python scripts/validar.py`)

## 1. IA - conjunto de teste rotulado (n=80, escrito a mao, fora do treino)

| Metodo | Acuracia | Acertos | Acuracia nos encaminhados automaticamente | % enviado a revisao humana |
|---|---|---|---|---|
| TF-IDF palavras+caracteres + Reg. Logistica | 0.875 | 70/80 | 0.896 | 0.162 |
| Baseline palavras-chave | 0.588 | 47/80 | None | 1.0 |

### Erros do modelo ML

| Texto | Esperado | Obtido | Confianca |
|---|---|---|---|
| Como posso agendar um horário com a ginecologista do posto? | agendamento_consulta | informacoes_gerais | 0.6 |
| Preciso de um horário com o clínico, estou com a pressão descontrolada há semanas. | agendamento_consulta | sintomas_urgentes | 0.54 |
| O antibiótico prescrito não está disponível na unidade. | medicamentos | vacinacao | 0.51 |
| Onde pego os comprimidos da minha mãe hipertensa? | medicamentos | visita_domiciliar | 0.42 |
| Preciso marcar uma ultrassonografia pedida pelo médico. | exames_resultados | agendamento_consulta | 0.93 |
| Como faço para buscar o laudo da mamografia? | exames_resultados | medicamentos | 0.51 |
| Reclamação: o banheiro da unidade está sujo e interditado. | reclamacao_atendimento | medicamentos | 0.3 |
| Vocês atendem sem agendamento ou tenho que ir cedo? | informacoes_gerais | reclamacao_atendimento | 0.45 |
| A unidade tem atendimento de fisioterapia? | informacoes_gerais | reclamacao_atendimento | 0.77 |
| Onde fica a unidade de saúde mais próxima do meu CEP? | informacoes_gerais | exames_resultados | 0.19 |

## 1b. IA - segundo conjunto de teste (n=40, escrito ANTES da ampliacao do treino)

| Metodo | Acuracia | Acertos | Acuracia nos automaticos | % revisao humana |
|---|---|---|---|---|
| TF-IDF palavras+caracteres + Reg. Logistica | 0.825 | 33/40 | 0.9 | 0.25 |
| Baseline palavras-chave | 0.5 | 20/40 | None | 1.0 |

### Seguranca: urgencia clinica no fluxo completo (IA + regras)

**ATENCAO:** o resultado '10/10' vale SOMENTE para o teste 1. No teste 2 e no conjunto combinado ha urgencia nao protegida.

| Conjunto | Urgencias com prioridade alta + revisao humana | Nao urgentes marcados alta (falso alarme) |
|---|---|---|
| Teste 1 | 10/10 | 1/70 |
| Teste 2 | 4/5 | 2/35 |
| **Combinado** | **14/15** | 3/105 |

Urgencias NAO protegidas (encaminhadas sem revisao humana):

- (teste 2) classificada como `vacinacao`: "Meu filho bateu a cabeça, vomitou e está sonolento demais."

Referencia atual dos numeros: `docs/auditoria_ia.md` e `docs/auditoria_resultados.md` (`python scripts/auditoria.py`).
Esta pagina e GERADA por `python scripts/validar.py`; os numeros de IA e de ponta a ponta nao foram alterados, apenas a apresentacao da metrica de seguranca foi ampliada para os dois testes.

## 2. Ponta a ponta (data/inbox)

| Metrica | Esperado | Obtido |
|---|---|---|
| registros_lidos | 25 | 25 |
| processados | 21 | 21 |
| rejeitados_invalidos | 3 | 3 |
| duplicados_ignorados | 1 | 1 |
| arquivos_com_falha | 2 | 2 |
| erros_processamento | 0 | 0 |

Confere: **True**. Tempo: 16.34 s.

## 3. Idempotencia

{"processados": 0, "duplicados_ignorados": 22, "confere": true}

## 4. Falha tratada: API de CEP fora do ar

```json
{
  "processados": 21,
  "erros_processamento": 0,
  "falhas_http_cep": 6,
  "consultas_cep_http": 6,
  "cep_indisponivel_nos_resultados": 20,
  "lote_completo_apesar_da_falha": true
}
```