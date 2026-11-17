# Checklist de entrega — módulo Gen AI (Global Solution 2026.2)

Legenda: **[x]** concluído com evidência verificável nesta atividade (arquivo, listagem ou `verificar_hashes.py`); **[ ] PENDENTE** depende de execução ou confirmação humana ainda não realizada; **[~]** parcial. Nada foi marcado por suposição.

## Código
- [x] Código do Gen AI presente em `citizentech/assistente/` (listagem conferida).
- [x] Candidata identificada: `fail-closed-4.4.4d1-cand` (`geracao.py`, linha `VERSAO_POLITICA`).
- [x] Código de produção intacto: hashes de `geracao.py` (`c857b99f…`), `evidencias.py` (`12118192…`), `catalogo.py` (`8e44143b…`) conferem; `verificar_hashes.py` → TODOS CONFEREM.
- [x] Mecanismos experimentais fora de `citizentech/` (pastas `fase4d3…fase4d7`) e flag `priorizar_atributo=False` por padrão (leitura de `ConfigGeracao`).
- [x] Sem credenciais/chaves no código do Gen AI (busca textual por padrões comuns: nenhuma ocorrência relevante). O Gen AI não usa API paga.
- [ ] PENDENTE: repositório Git **sem commits** — decidir como empacotar (zip/pasta ou criar commit por um humano).
- [ ] PENDENTE: o código do Gen AI depende de `citizentech.texto.mascarar_pii` (RPA); empacotar o RPA junto.

## Documentação
- [x] `README_ENTREGA.md`, `ARQUITETURA.md`, `METODOLOGIA_E_EXPERIMENTOS.md`, `RESULTADOS_E_LIMITACOES.md`, `ESTADO_FINAL.md`, `CHECKLIST_ENTREGA.md` criados em `docs/entrega_genai/`.
- [x] Relatórios históricos das etapas 1–4.3 e 4.4/4A–4D.7 existem e não foram modificados.
- [ ] PENDENTE (humano): revisar os textos e conferir os nomes/matrículas da equipe (copiados do `README.md` raiz do RPA).
- [ ] PENDENTE (humano): confirmar o **enunciado da disciplina Gen AI**. O `docs/enunciado/` do repositório é o da disciplina *AI for RPA*; não foi encontrado enunciado específico do Gen AI, portanto os requisitos formais do módulo não puderam ser conferidos.

## Dependências
- [~] Pacotes importados pelo código identificados e versões do ambiente atual registradas no README (`pip list`, somente leitura).
- [ ] PENDENTE: **não existe arquivo de dependências do Gen AI** (`requirements.txt` cobre só o RPA); criar/validar em ambiente limpo.
- [ ] PENDENTE: `requirements-congelado.txt` (RPA) fixa `numpy==2.4.4`, mas o ambiente atual tem numpy 1.26.4; esclarecer qual interpretador foi usado em cada módulo.
- [ ] PENDENTE: confirmar licenças dos artefatos de terceiros (corpus CC BY 4.0 e e5 MIT estão nos relatórios; a licença do GGUF/Qwen3 não está documentada no repositório).

## Execução
- [x] Índice `est300o30` presente em `data_assistente/indices/` e dados originais com `MANIFESTO.json` (listagem conferida; integridade do corpus conferida por `verificar_hashes.py`).
- [ ] PENDENTE: executar uma consulta de ponta a ponta com LM Studio + `qwen3-8b` carregado (não executado: a atividade proíbe geração). O trecho do README foi montado a partir do código e não foi rodado.
- [ ] PENDENTE: reconstruir o índice em outra máquina (≈ 30 min por configuração; não testado nesta atividade).
- [ ] PENDENTE: confirmar a execução com 16 GB de RAM seguindo as orientações de memória (recarregar o modelo a cada ≈ 3 gerações).

## Testes
- [ ] PENDENTE: **reexecutar** `python -m pytest citizentech/assistente/tests -q` (último resultado registrado: 337 passando ao fim da 4D.1; não reexecutado aqui).
- [x] Testes existem para chunking, associação, retriever, gerador, verificador, M1–M5, 4A, 4B, 4D.1 e conferência de hashes (17 arquivos; contagem estática de 286 funções `test_`).
- [ ] PENDENTE (humano): explicar a diferença entre 286 funções e 337 testes (hipótese: parametrização, não verificada).

## Evidências
- [x] Rodadas históricas preservadas em `data_assistente/derivados/` (três `.jsonl` + `.meta.json` das rodadas 4.1/4.2/4.3).
- [x] Validação seletiva (21 gerações) e manifestos em `docs/assistente/diagnostico_4_4/fase4/`.
- [x] Hashes de referência (`hashes_referencia_44.json`) e manifesto 4D.7 conferem.
- [ ] PENDENTE: o prompt bruto enviado ao LM Studio não foi gravado (contexto reconstruído de forma determinística).

## Resultados
- [x] Resultados quantitativos consolidados por conjunto, sem misturar (`RESULTADOS_E_LIMITACOES.md`), com origem em cada relatório.
- [ ] PENDENTE: **validação independente** (segundo avaliador humano, conjunto externo/teste de 350): nunca realizada.
- [ ] PENDENTE: resultados das auditorias são de **modelo de linguagem**, não humanos; rotular assim na apresentação.

## Limitações
- [x] Limitações metodológicas, de gabarito, de memória, de utilidade e problemas sem solução registradas.
- [x] Ausência de integração com o Zelo registrada (nenhum documento a apresenta como concluída).

## Apresentação
- [ ] PENDENTE: roteiro/slides do **módulo Gen AI** (existe `docs/roteiro_apresentacao.md`, mas é do RPA: "CitizenTech RPA + IA").
- [ ] PENDENTE (humano): decidir o que será demonstrado ao vivo (a execução exige o modelo local e memória disponível; alternativa: mostrar os arquivos `.jsonl` das rodadas preservadas).
- [ ] PENDENTE (humano): preparar a mensagem de honestidade acadêmica: candidata experimental, não validada, fora do Zelo.

## Integridade desta atividade
- [x] Somente arquivos novos em `docs/entrega_genai/`; nenhuma alteração em código, dados, relatórios, snapshots ou hashes; nenhum teste, geração ou benchmark executado (ver `ESTADO_FINAL.md`).
