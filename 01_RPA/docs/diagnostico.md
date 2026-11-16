# Diagnóstico inicial (Fase 1) e decisões

**Estado encontrado:** repositório `GS/RPA` vazio. Único insumo: enunciado (`docs/enunciado/p1.png`, `p2.png`, extraído do PDF, que só continha imagem). Não havia problema definido, código, modelos ou plano de ensino. As pastas vizinhas (`forzy-pln-sprints-3-4`, `jogo-pln`) não foram usadas.

**Implementado antes:** nada. **Reaproveitado:** nada.

**Decisão:** a pedido do grupo, o problema foi proposto e, depois, ajustado por escolha do usuário: triagem automática de pedidos de cidadãos à UBS (atenção básica de saúde). A primeira versão (156 municipal) foi substituída. Ele pede RPA real (arquivos → decisão → saída), IA útil (classificar texto livre) e tem limite natural para IA: urgência clínica exige humano.

**Riscos:** (1) sem dados reais, métricas vêm de dados sintéticos e são otimistas; (2) nomes dos temas da disciplina não confirmados; (3) dependência de API externa (mitigada por retry/fallback); (4) integrantes não informados. *[Atualização de 11/11/2026: os integrantes passaram a constar em `README.md:8` — Henry Gimenez - 563217; Gustavo Balbo - 561711; Vinícius Araújo - 564504; conforme o README, não verificado fora dele. Os demais riscos desta lista permanecem como registrados na Fase 1.]*

**Cobertura do barema:** temas 30% → `docs/temas.md` com código executado; ponta a ponta 25% → `main.py` único + README + pytest; resiliência 20% → try/except por registro, retry/timeout/circuit breaker, idempotência, logs, `.env`, revisão humana; evidências 15% → `scripts/validar.py`, teste rotulado separado do treino, erros analisados; ética/organização 10% → `docs/etica_ods.md`, repositório modular.
