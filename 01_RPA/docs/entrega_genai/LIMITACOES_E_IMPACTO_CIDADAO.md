# Limitações e impacto para o cidadão

As limitações abaixo são **resultados do projeto**, não funcionalidades. Os números vêm dos relatórios originais (indicados). Os julgamentos citados foram feitos por modelo de linguagem ou pelo autor; **não há avaliação humana independente**. Este é um protótipo acadêmico experimental (`fail-closed-4.4.4d1-cand`, não validado), **não aprovado para uso real**.

## 1. Risco de uma resposta incorreta em informação pública de saúde
**O que foi observado (rodada 4.3, 150 perguntas de validação; auditoria 4.3 por modelo de linguagem):** das 31 respostas dadas, **8 (25,8%) estavam incorretas**, 16 eram corretas mas parciais e 7 corretas. As 8 incorretas **passaram em toda a verificação técnica** (citações literais): o trecho citado existe, mas não responde ao que foi perguntado.
Exemplos reais (ver `ANEXO_CASOS_AVALIACAO.md`):
- **val-130:** pergunta sobre empresas credenciadas na Asa Sul; a resposta incluiu uma empresa cuja evidência é do prédio na Asa **Norte** (segundo a auditoria).
- **val-024:** a modificação contratual foi descrita corretamente, mas "no Hospital Regional de Ceilândia" repetia a pergunta e **não tinha apoio no texto citado**.
- **Grupo B da rodada 4.3** (fonte correta não enviada ao modelo): 11 respostas dadas, **0 totalmente corretas**, 5 parciais e 6 incorretas.
**Consequência para o cidadão:** um valor, um local ou uma unidade errados em informação oficial de saúde podem levar a procurar o serviço errado ou a confiar em dado inexistente. O sistema cita fontes, mas **citar não prova que a resposta esteja correta**. A candidata atual bloqueia alguns desses padrões (val-130, val-149, val-083), mas val-087-A-r1 **continua sendo entregue** com localização não sustentada (`RESULTADOS_E_LIMITACOES.md`, §I), e **nenhuma dessas melhorias foi validada com revisão humana nem com novas gerações em larga escala**.

## 2. Risco de abstenção excessiva
**Observado (4.3):** só 31 das 150 perguntas (20,7%) receberam resposta. Entre as 119 abstenções, a auditoria por modelo considerou **56 indevidas** (o corpus permitia ao menos resposta parcial), 53 ambíguas de fato e 10 corretas. O diagnóstico 4.4 atribuiu essas 56 a: 8 falsos positivos do verificador, 25 a recuperação/contexto e 19 a geração com o documento no contexto.
**Consequência:** a escolha deliberada de preferir "não responder" a "responder errado" (política *fail-closed*) reduz respostas erradas, mas deixa o cidadão sem resposta com frequência. Perguntas respondíveis podem terminar em abstenção (ex.: val-074 recebeu "Esta pergunta está fora do que as publicações oficiais consultadas permitem responder."; `ANEXO_CASOS_AVALIACAO.md`, caso 5). A mensagem de ambiguidade pede "a publicação, a data ou o contrato desejado", que um cidadão comum pode não conhecer.

## 3. Informações incompletas ou desatualizadas
- **Listas incompletas:** perguntas plurais ("Quais itens…") podem receber lista parcial; o sistema acrescenta aviso quando detecta cobertura incompleta, mas a detecção depende do catálogo e do contexto (≈ 3 chunks cabem por pergunta). Perguntas MULTI (várias publicações): o contexto enviado cobriu todas as publicações esperadas em apenas 4 de 41 (`04_gerador.md` §5).
- **Retificações e versões:** o Diário Oficial publica atos que depois são republicados ou corrigidos; o corpus é um **instantâneo** de edições (o dataset foi acessado em 2026-11-13). Há evidência no próprio corpus: um chunk usado nos testes diz "Republicado por ter sido encaminhado com incorreção no original". O sistema **não verifica se uma publicação foi posteriormente retificada ou revogada** nem a atualidade de vigências.
- **Publicações concorrentes:** o corpus tem publicações semelhantes com valores diferentes; o sistema tenta abster-se por ambiguidade, mas **a detecção é heurística** (regra de janela do catálogo; gera falsas ambiguidades, como em val-074 após correção de contexto).
- **Escopo do corpus:** são atos administrativos do DODF-DF (extratos, contratos, credenciamentos), **não** informação de serviço ao cidadão (horários, como agendar). Não responde a esse tipo de pergunta com base confiável.

## 4. Turno único
O assistente responde **uma pergunta por vez**, sem memória de conversa e sem perguntas de esclarecimento: nenhum teste de consistência entre turnos existe e o código não mantém histórico (`gerar_resposta` recebe uma pergunta e o contexto recuperado). O enunciado cita "consistência entre turnos" no plano de testes: **não foi avaliada**. Perguntas de seguimento ("e o valor?") não são resolvidas.

## 5. Ausência de integração com o protótipo CitizenTech
**Não há integração.** Nenhum código fora de `citizentech/assistente/` chama o Gen AI; não há interface, API ou frontend para o assistente. O RPA do repositório (triagem de solicitações à UBS) **não usa** o módulo Gen AI, e nada em `D:\Downloads\GS`, `D:\FIAP` ou `D:\Projetos` constitui um protótipo CitizenTech ou "Zelo" integrado (busca realizada na auditoria final). Os resultados descrevem o módulo **isolado**.

## 6. Ausência de avaliação humana independente
Todos os julgamentos de qualidade (auditoria 4.3, diagnóstico 4.4, avaliação cega da validação seletiva 4B, reauditoria 4C, rótulos sintéticos e reais das fases 4D) foram feitos pelo agente de desenvolvimento ou por instância do mesmo modelo, que conhecia o experimento. Os gabaritos do dataset foram gerados por LLM e têm erros conhecidos (ex.: val-024). Foi preparado um pacote cego de revisão humana (`diagnostico_4_4/fase4/fase4d4/PACOTE_REVISAO_HUMANA_4D4.md`) **que nunca foi respondido**. Os 150 casos de validação foram reutilizados em todas as decisões de projeto; **os resultados não medem generalização**. O conjunto de teste (350) nunca foi usado.

## 7. Hardware e execução local
- **Ambiente:** RX 6750 XT 12 GB, Ryzen 5 5500, 16 GB de RAM.
- **Memória:** o `llama-server` cresce a cada requisição (até ≈ 8,2 GB de RSS) e a RAM livre do sistema chegou a ≈ 45 MB; o servidor caiu em uma execução com `parallel` 4. Nas gerações da Fase 4B foi preciso fechar aplicativos e recarregar o modelo a cada ≈ 3 gerações.
- **Latência:** 12–21 s por pergunta (medianas); **tempo inadequado para atendimento interativo massivo**.
- **Reprodutibilidade:** sem *seed* (temperatura 0,3), Python das rodadas não registrado, sem arquivo de dependências validado em ambiente limpo (`REPRODUCAO_E_DEPENDENCIAS.md`).
- **Contexto curto:** o orçamento de ≈ 3 mil tokens e o prompt de ≈ 1,1 mil tokens deixam só ≈ 3 chunks por pergunta.

## 8. Outras limitações registradas
- Distinção `insuficiente` × `fora_do_escopo` não confiável; `ambigua` usado em excesso.
- Testes de segurança pequenos e escritos pelo autor (`SEGURANCA_E_MITIGACOES.md`); H3 teve falha parcial.
- Problemas conhecidos sem solução: premissa de "termo da pergunta não precisa de apoio" (val-087-A-r1), regra de janela do catálogo, associação entidade–localidade (val-024), política de evidência positiva (`ESTADO_FINAL.md`, `RESULTADOS_E_LIMITACOES.md`).

## 9. Uso responsável
O sistema **não deve ser usado para decisões reais** nem apresentado ao cidadão como fonte confiável. Em eventual piloto: modo sombra com conferência humana, exibição obrigatória das fontes, e validação independente prévia. Estas são recomendações; **nenhuma delas está implementada ou foi testada**.
