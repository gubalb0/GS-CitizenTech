# Perguntas prováveis da banca — respostas fundamentadas na implementação real

> Regra do documento: tudo que está nas respostas **existe no repositório** ou foi **medido**. O que seria evolução futura aparece marcado como **[NÃO IMPLEMENTADO]**. Números: `docs/auditoria_resultados.md` e `docs/evidencias_resultados.md`.
> Campos do grupo: Integrantes: Henry Gimenez - 563217; Gustavo Balbo - 561711; Vinícius Araújo - 564504 (conforme `README.md:8`; o grupo deve confirmar) · Turma `____` · Temas (nomes oficiais) `____` · Prazo `____`.

---

## A. Escolhas de IA

**1. Por que foi escolhido TF-IDF?**
O problema é classificar textos curtos em 8 categorias com pouquíssimos dados (640 textos sintéticos de treino). TF-IDF (`citizentech/classificador.py`) é uma representação clássica, rápida, gratuita, roda em CPU e não exige pré-treinamento externo; dá peso às palavras que distinguem categorias ("insulina", "vacina") e reduz o peso das comuns. **O que não fizemos:** não comparamos com embeddings, redes neurais ou outros classificadores; a escolha foi pragmática. Só comparamos o TF-IDF com um baseline de palavras-chave (58,8% e 50,0% de acurácia contra 87,5% e 82,5%) e com 4 configurações do próprio TF-IDF (ver pergunta 3; essa comparação foi **relatada e não é reproduzível** a partir do repositório).

**2. Por que utilizar regressão logística?**
Porque produz probabilidades por classe (`predict_proba`), e o projeto usa a maior probabilidade como **confiança** para decidir se o robô encaminha ou passa a um humano (limiar 0,45, em `config.py`/`regras.py`). É simples, treina em segundos e é regularizada (`C=10`). **Ressalva:** as probabilidades não foram calibradas formalmente, e há um erro de classificação com confiança 0,93 (exame de ultrassonografia → agendamento). Portanto a confiança é um indicador útil, não uma garantia.

**3. Qual a função dos n-gramas de caracteres?**
Além do TF-IDF de palavras (1–2-gramas), há um TF-IDF de **caracteres** (`char_wb`, 3 a 5 caracteres dentro de cada palavra). Isso aproxima formas parecidas e erros de digitação ("vacinas"/"vacinação", "remedio"/"remédios") sem precisar de dicionário. Resultados com o treino já ampliado para 640 textos: palavras + caracteres → 70/80 (87,5%) no teste 1 e 33/40 (82,5%) no teste 2 (**reproduzíveis** com `scripts/validar.py`); só palavras → 64/80 (80%) e 29/40 (72,5%) (**não reproduzíveis a partir do repositório**: foram relatados a partir de um script temporário não versionado; não os apresente como evidência verificável). Por isso o efeito isolado dos n-gramas de caracteres neste projeto é uma **hipótese relatada**, não um resultado comprovado. **Ressalva:** essa configuração foi escolhida entre 4 olhando esses mesmos testes, então o ganho é provavelmente otimista.

**4. Por que não usar um LLM?**
O enunciado o torna opcional, e aqui ele traria custo, dependência de chave/serviço e risco de resposta inventada em um contexto de saúde. A IA usada é um classificador que só escolhe entre 8 rótulos. Nenhum LLM está implementado.

**5. Como são os dados de treino? A acurácia é real?**
Os 640 textos de treino são **sintéticos**, gerados por templates com variação e ruído e seed fixa (`scripts/gerar_treino.py`, reprodutível: o arquivo regenerado tem o mesmo hash). Os testes (80 e 40 textos) foram escritos à mão pela equipe de desenvolvimento, **com auxílio de um assistente de IA** `[o grupo deve confirmar e declarar o uso conforme as regras da FIAP]`. Logo, **a acurácia não representa mensagens reais de cidadãos**; mensagens reais devem render números piores.

---

## B. Automação e encaminhamento

**6. Como funciona a automação?**
`main.py` → `citizentech/pipeline.py`: (1) `ingestao.py` lê todos os `.csv`/`.txt` de `data/inbox/`; (2) `validacao.py` rejeita texto vazio/curto/longo e CEP inválido; (3) `estado.py` calcula um hash do texto normalizado + CEP e ignora o que já foi processado (SQLite); (4) o classificador define a categoria e a confiança; (5) `regras.py` define setor, prioridade e status; (6) `geo.py` consulta a ViaCEP; (7) gera protocolo, resposta ao cidadão e os arquivos em `saida/`. Roda sem intervenção humana em um único comando.

**7. Isso é mesmo RPA? Não há automação de interface (UiPath, Selenium)?**
Não há automação de interface gráfica. É um robô de *back-office* orientado a arquivos e API: captura (arquivos), processamento em lote, aplicação de regras, integração com serviço externo e geração de saídas — o conjunto "ler, decidir e agir" do fluxo manual de um atendente. Não alegamos usar ferramentas de RPA comerciais.

**8. Como ocorre o encaminhamento?**
`regras.decidir()` mapeia a categoria a um setor (ex.: `medicamentos` → "Farmacia da UBS") e define prioridade e prazo: **normal = 72 h; alta = 1 h**. O status é `encaminhado` **ou** `revisao_humana`. Vai a humano quando: confiança < 0,45; categoria indefinida; categoria `sintomas_urgentes`; ou a prioridade é alta (20 termos de risco, como "dor no peito", "falta de ar", "convulsao", "sangramento"). Nenhuma mensagem é realmente enviada ao cidadão: a resposta é um texto gerado e gravado em `resposta_ao_cidadao`.

**9. Um mesmo pedido enviado duas vezes por pessoas diferentes é duplicado?**
Sim, é tratado como duplicado se o texto normalizado e o CEP forem idênticos (a duplicidade é por conteúdo, não por pessoa). É uma limitação: dois cidadãos diferentes com texto igual e mesmo CEP seriam um só.

---

## C. Erros, resiliência e segurança operacional

**10. Como o sistema trata erros?**
- **Arquivo corrompido/sem coluna/ausente:** log de erro e o lote continua (demonstrado: `lote_corrompido.csv`, `lote_sem_coluna.csv`; pasta de entrada ausente coberta em teste).
- **Dado inválido:** vai para `rejeitados.csv` com o motivo.
- **Duplicado:** ignorado e registrado.
- **API de CEP fora do ar:** timeout de 4 s por padrão, até 3 tentativas com espera exponencial e **circuit breaker** após 3 falhas seguidas; o registro segue com `fonte_cep = indisponivel` (demonstrado: 21/21 processados).
- **Falha no modelo:** fallback por palavras-chave, com confiança limitada a 0,4 — logo sempre vai a revisão humana.
- **Erro em um registro:** `try/except` por registro; o erro é logado e o lote prossegue.
- Tudo em `logs/execucao.log`. Credenciais: nenhuma necessária; `.env` fora do Git.

**11. E quando a API responde "CEP não encontrado"?**
Isso não é falha de rede: o resultado é `indisponivel`, sem acionar nova tentativa nem contar para o circuit breaker. Alguns CEPs de exemplo (como o de S018) caem nesse caso.

**12. Como vocês protegem dados pessoais?**
Só dados sintéticos. CPF, e-mail e telefone no texto são mascarados (`[CPF]`, `[EMAIL]`, `[TEL]`) antes de gerar saídas; **apenas o CEP** (dado público) é enviado à API externa, nunca o texto. Em produção seriam necessários base legal, retenção, criptografia e controle de acesso, **que não estão implementados**. O mascaramento por expressões regulares não pega nomes, endereços ou dados de saúde.

---

## D. Validação

**13. Como foi feita a validação?**
(a) 21 testes automatizados (`pytest`): validação, mascaramento, arquivos defeituosos, fallback de IA, retry/circuit breaker, idempotência, falha isolada; (b) dois conjuntos de teste rotulados à mão (80 e 40 textos) com métricas por classe e matriz de confusão; (c) execução ponta a ponta com esperado × obtido; (d) cenário de falha da API; (e) auditoria somente leitura com hashes (`scripts/auditoria.py`, `docs/modelo_congelado.json`); (f) uma execução em cópia limpa com venv novo foi **relatada, mas não possui log preservado**; não a apresente como evidência arquivada.

**14. A validação é independente? Os testes são confiáveis?**
**Não são independentes.** O teste 1 foi analisado (erros vistos) antes de ampliarmos o treino, o teste 2 foi escrito e visto pela mesma equipe, e escolhemos a configuração do modelo entre 4 opções olhando esses testes. As amostras são pequenas (5 a 15 casos por classe). A validação independente (coleta e rotulagem por terceiros, avaliação única) tem protocolo pronto em `validacao_independente/` e **não foi executada**; não há nenhum resultado independente.

**15. Qual a taxa de erro real?**
Nos 120 textos: acurácia da IA 85,8%; mas o que importa operacionalmente é que dos 84 encaminhados automaticamente, **9 estavam errados (10,7%)**, ou seja, cerca de 1 em 9 (“automaticamente” = status `encaminhado` do robô; `docs/evidencias.md` também mostra uma contagem por confiança ≥ 0,45, que é outro conceito — ver “Esclarecimentos sobre contagens”). Dos 36 enviados a humano, 28 já estavam corretos (carga de revisão desnecessária, preço da cautela).

**16. Houve correção de números durante o projeto?**
Sim, e está documentado: "10/10 urgências" valia só para o teste 1 (no combinado são 14/15), e o "~90% de acerto nos automáticos" contava só pela confiança. A auditoria (`docs/auditoria_ia.md`) corrige essas afirmações.

---

## E. Limitações, segurança e evolução

**17. Quais são as limitações?**
Treino sintético; testes não independentes e pequenos; limiar 0,45 não calibrado; erros de alta confiança; só 8 categorias e nenhuma classe "fora do escopo" (o pedido S024, "parar de fumar", foi encaminhado como agendamento); sem tratamento de negação, abreviações ou múltiplos pedidos no mesmo texto; urgência por lista fixa de termos; categorias e termos **não validados por profissional de saúde**; resposta ao cidadão apenas gerada, não enviada; SQLite local. Lista completa: README → "Limitações conhecidas".

**18. Por que a solução não está apta para triagem clínica?**
Porque falhou nos próprios testes em casos graves: o relato "meu filho **bateu a cabeça, vomitou e está sonolento**" foi classificado como vacinação e encaminhado **sem revisão humana** (urgências protegidas: 14/15); uma sondagem qualitativa mostrou que "**infarto**" e "**tentativa de suicídio**" não disparam prioridade alta, e não existe categoria de saúde mental. Além disso, nenhum profissional de saúde revisou categorias e termos, e não há validação independente. **Nenhuma classificação automática substitui triagem clínica.** O uso responsável seria, no máximo, apoio ao atendente em **modo sombra** (o humano decide tudo).

**19. Por que não corrigiram essas falhas?**
Por decisão consciente: ao detectá-las na auditoria, congelamos modelo, dados, testes e regras para preservar a rastreabilidade (hashes em `docs/modelo_congelado.json`) e evitar "melhorar" os números ajustando regras sobre os próprios testes. Qualquer nova regra de urgência exige critérios revisados por profissionais de saúde e um **novo** conjunto independente.

**20. Como a solução poderia evoluir? (nada disto está implementado)**
- **[NÃO IMPLEMENTADO]** Rodar a validação independente e calibrar o limiar de confiança com dados independentes.
- **[NÃO IMPLEMENTADO]** Revisão das regras de urgência por profissionais de saúde, nova categoria de crise de saúde mental, tratamento de negação e regra mais conservadora (qualquer menção a sintoma vai a humano).
- **[NÃO IMPLEMENTADO]** Classe "fora do escopo"; confirmação humana obrigatória para medicamentos e exames.
- **[NÃO IMPLEMENTADO]** Dados reais anonimizados e autorizados; comparação com outros modelos; envio real de respostas e integração com o sistema da UBS; piloto em modo sombra.

**21. Qual o impacto social e a relação com os ODS?**
O ganho potencial é reduzir o tempo de triagem e priorizar casos de risco para quem depende do SUS: **ODS 3** (saúde e bem-estar), **ODS 10** (desigualdades) e **ODS 16** (instituições eficazes e transparentes, com protocolo e prazo rastreáveis). O impacto real **não foi medido**; os resultados vêm de um protótipo com dados sintéticos (`docs/etica_ods.md`).

---

## F. Aprofundamento técnico (adicionado em 11/11/2026)

> Cada resposta separa **o que está documentado ou no código** do **que não possui justificativa formal**. Não há justificativas retrospectivas.

**22. Como funciona o TF-IDF com n-gramas de caracteres, tecnicamente?**
O texto passa por `texto.normalizar` (minúsculas, remoção de acentos, símbolos viram espaço) e depois por dois vetorizadores concatenados em um `FeatureUnion` (`citizentech/classificador.py`): (a) **palavras**, 1 a 2-gramas, com 1.651 termos; (b) **caracteres**, `analyzer="char_wb"`, 3 a 5-gramas, com 3.998 termos. Ambos usam `sublinear_tf=True` (1 + log da frequência), IDF suavizado e normalização L2, com `min_df=1` (parâmetros no manifesto `docs/modelo_congelado.json`). No modo `char_wb` os n-gramas são formados **dentro dos limites de cada palavra**, o que faz "vacina", "vacinas" e "vacinação" compartilharem pedaços como "vac", "aci" e "cin", e um erro de digitação alterar só alguns desses pedaços. **Limites:** com 640 textos de treino, 5.649 atributos no total aumentam o risco de ajuste excessivo; não há ablação preservada que isole o efeito dos n-gramas de caracteres neste projeto (ver Q3: o efeito é uma hipótese relatada).

**23. A confiança do modelo é calibrada?**
**Não foi calibrada.** A "confiança" é a maior probabilidade de `predict_proba` da Regressão Logística (`classificador.classificar`); não há etapa de calibração (por exemplo, calibração isotônica ou de Platt) e não foram calculados diagrama de confiabilidade, ECE ou Brier. O que existe é a acurácia por faixa nos 120 textos de teste (`docs/auditoria_resultados.json`): [0, 0,3): 50% (n=4); [0,3, 0,45): 74% (n=19); [0,45, 0,6): 71% (n=17); [0,6, 0,8): 80% (n=20); [0,8, 1,0]: 98% (n=60). Há um erro com confiança 0,93 (ultrassonografia → agendamento). As faixas têm amostras pequenas e não são monotônicas entre 0,3 e 0,6. Portanto a confiança funciona como um **sinal** para mandar casos a humano, não como probabilidade de acerto; e as regras de urgência independem dela. (Em geral, regressão logística com regularização fraca, `C=10`, em poucos dados tende a ser confiante demais; isso é uma propriedade geral, **não medida aqui**.)

**24. Como funciona a idempotência por hash?**
`citizentech/estado.py` calcula `SHA-256(texto normalizado + "|" + CEP sem hífen)` e guarda o hash em uma tabela SQLite (`processados`, hash como chave primária; `data/estado.db`). Em `pipeline.py`, o registro cujo hash já existe é ignorado e registrado como duplicado; o hash só é gravado **depois** do processamento bem-sucedido (`estado.marcar`), de modo que uma falha pode ser reprocessada. `python main.py --reset` limpa a tabela. Evidência: captura `11` (2ª execução: 0 processados, 22 duplicados) e testes automatizados. **Limites:** a duplicidade é por **conteúdo** (mesmo texto e CEP), não por pessoa; mudar uma palavra gera outro hash; o estado é local (SQLite), sem prazo de validade.

**25. Como funciona o circuit breaker?**
`citizentech/geo.py`: cada consulta de CEP tem timeout (4 s por padrão) e até 3 tentativas com espera exponencial. Se **3 CEPs seguidos** falham (`LIMITE_FALHAS_SEGUIDAS = 3`, contados depois de esgotar as tentativas), o robô para de chamar a API e devolve `indisponivel` imediatamente para os demais; um sucesso zera o contador e CEPs já consultados ficam em cache. "CEP não encontrado" não conta como falha. Evidência: captura `07` (3 CEPs × 3 tentativas = 9 falhas, depois nenhuma nova tentativa) e testes automatizados. **Limites:** o disjuntor não tem estado "meio aberto": uma vez aberto, permanece aberto até o fim da execução (a cada execução um novo objeto é criado).

**26. Como funciona o congelamento por SHA-256 e o que ele garante?**
`docs/modelo_congelado.json` guarda o SHA-256 de 6 arquivos (`data/treino.csv`, `data/teste_rotulado.csv`, `data/teste_cego.csv`, `data/modelo/classificador.joblib`, `citizentech/classificador.py`, `citizentech/regras.py`), além de parâmetros, classes, vocabulário e versões das bibliotecas. `python scripts/auditoria.py` **não sobrescreve** o manifesto: só confere os hashes e **aborta** se algum divergir. `.gitattributes` (`* -text`) evita que a conversão de fim de linha altere os bytes. **O que garante:** que esses 6 arquivos são idênticos aos de 10/11/2026. **O que não garante:** os módulos `texto.py` (normalização do texto de entrada), `pipeline.py`, `config.py`, `geo.py`, `ingestao.py`, `estado.py`, `validacao.py` e `main.py` **não estão** no manifesto; uma alteração neles não seria detectada. Re-treinar com os mesmos dados reproduz as probabilidades, mas não os bytes do `.joblib` (por isso o `main.py` usa o modelo salvo e não o sobrescreve).

**27. Por que o limiar de confiança é 0,45?**
- **Documentado:** o valor é o padrão de `CONFIANCA_MINIMA` em `citizentech/config.py`, aparece em `.env.example` (pode ser alterado por variável de ambiente), na regra descrita no README, em `docs/modelo_congelado.json` (`limiar_confianca_revisao`) e em `docs/auditoria_ia.md`, que registra que **não foi calibrado**. Há uma relação documentada no código: o fallback por palavras-chave limita a confiança a 0,4 para ficar sempre abaixo do limiar (comentário em `classificador.py`).
- **Sem justificativa formal:** **não existe justificativa registrada** para o valor 0,45 (sem curva cobertura × erro, sem conjunto de validação independente, sem custo de revisão). Não se deve inventar uma justificativa; a resposta honesta é "valor inicial, não calibrado".
- **Observação a posteriori (não é justificativa):** nos 120 testes, a acurácia em [0,3, 0,45) foi 74% (n=19) e em [0,45, 0,6) foi 71% (n=17): **não há degrau de acerto em 0,45** nessas amostras pequenas, ou seja, o limiar não separa de forma nítida casos mais e menos confiáveis.

**28. Como foram definidas as oito categorias?**
- **Documentado:** a lista está no README e nos dados (`scripts/gerar_treino.py`, `data/teste_*.csv`); o mapeamento categoria → setor está em `citizentech/regras.py` (`DEPARTAMENTO`, com nomes genéricos); as definições operacionais de cada rótulo estão em `validacao_independente/INSTRUCOES_ROTULAGEM.md` (criadas para a validação independente, **não executada**; descrevem o significado dos rótulos, não justificam a escolha das oito); a escolha do tema "triagem de pedidos à UBS" entre opções está em `docs/diagnostico.md`.
- **Sem justificativa formal:** **não há registro** de critério para escolher exatamente estas oito categorias, nem de levantamento de demandas reais de uma UBS, normas ou protocolos do SUS, entrevistas com atendentes ou revisão por profissional de saúde. Os nomes dos setores também não têm fonte documentada de organograma. A lista foi definida no desenho do protótipo, sem validação formal; não crie uma justificativa retrospectiva. Consequências já registradas como limitações: não existe classe "fora do escopo" nem categoria de saúde mental, e as categorias não foram validadas por profissional de saúde.
