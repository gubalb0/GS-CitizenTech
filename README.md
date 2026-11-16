# CitizenTech: Global Solution 2026/2 (FIAP)

Repositório da entrega de **Governança em IA e Business Analytics**, que reúne os módulos das nove disciplinas da Global Solution 2026/2 (tema CitizenTech) e mostra o que foi e o que não foi integrado.

**Curso:** Tecnólogo em Inteligência Artificial · Turma 2TIAPY

| Integrante | RM |
|---|---|
| Gustavo Balbo Saraiva | 561711 |
| Henry Gimenez | 563217 |
| Vinicius Araujo | 564504 |

**Links**
- 🎬 Vídeo da GBA: ✏️ _https://youtu.be/..._
- 🌐 Zelo publicado: https://zelo-web.onrender.com
- 📦 Repositório original do Zelo: https://github.com/gubalb0/GS-FRONT
- 📄 Relatório da GBA: [`06_Governanca_GBA/`](06_Governanca_GBA/)

## Módulos

| Pasta | Disciplina | Projeto | Problema / público |
|---|---|---|---|
| [`01_RPA`](01_RPA/) | AI for Robotic Process Automation | Robô de triagem de solicitações para UBS | Pedidos ao SUS chegam misturados e são triados à mão |
| [`02_Cluster_Computing`](02_Cluster_Computing/) | Cluster Computing, Computação Neuromórfica e Supercomputadores | Simulação no iSPD de 2 e 4 workers | Fila de classificação das solicitações em horário de pico |
| [`03_Computacao_Quantica`](03_Computacao_Quantica/) | Computação Quântica & IA | Identidade digital + criptografia pós-quântica (conceitual) | Dados vitalícios do cidadão expostos ao algoritmo de Shor |
| [`04_Front_End_Zelo`](04_Front_End_Zelo/) | Front End & Mobile Development | **Zelo**: zeladoria urbana com IA (Streamlit + FastAPI + LLM) | Morador não sabe classificar nem a quem recorrer |
| [`05_Generative_AI`](05_Generative_AI/) | Generative AI & Advanced Nets | Assistente RAG sobre o Diário Oficial do DF (saúde) | Informação pública dispersa em documentos oficiais |
| [`06_Governanca_GBA`](06_Governanca_GBA/) | Governança em IA e Business Analytics | Relatório de integração e roteiro do vídeo | Integração e governança dos módulos |
| [`07_IoT_OuviAi`](07_IoT_OuviAi/) | Physical Computing, Embedded AI, Robotics & Cognitive IoT | **OuviAí**: sons domésticos para pessoas surdas (Edge Impulse) | Pessoa surda não percebe campainha e batida na porta |
| [`08_PLN_Assistente_de_Voz`](08_PLN_Assistente_de_Voz/) | Processamento de Linguagem Natural, Chatbots & Virtual Agents | Assistente de voz sobre direitos do consumidor | Idosos e pessoas com baixa alfabetização sem acesso a orientação |
| [`09_Visao_Computacional`](09_Visao_Computacional/) | Visão Computacional | Detecção de fissuras em concreto (MobileNetV2) | Triagem de locais para inspeção na manutenção urbana |

## Quadro de integração

| Módulo | Nível | Como se relaciona com o resto |
|---|---|---|
| Front-end (Zelo) | **Integrado (técnico)** | Front Streamlit → API FastAPI → LLM (Groq) e dados abertos (ViaCEP, Open-Meteo), em produção no Render |
| RPA | **Integrado por dados** com o Cluster | A carga simulada no Cluster representa a classificação das solicitações do robô |
| Cluster Computing | **Integrado por dados** com o RPA | Mede quanto o tempo de esvaziar a fila cai de 2 para 4 workers (speedup simulado de 1,9992×) |
| Visão Computacional | **Integrado por tema** com o Zelo | Mesmo domínio (manutenção urbana); a foto do problema poderia ser classificada no relato do Zelo |
| Generative AI | **Não integrado** | Em andamento; a própria avaliação recomenda auditoria humana antes de integrar |
| PLN | **Não integrado** | Outro problema (direitos do consumidor); a voz poderia virar um canal de entrada do Zelo |
| IoT (OuviAí) | **Não integrado** | Outro problema (acessibilidade doméstica); roda no celular, sem servidor |
| Computação Quântica | **Conceitual** | Trabalho sem implementação; o roadmap de criptografia pós-quântica se aplica à proteção dos dados de todos os módulos |

Os critérios e a justificativa de cada nível estão no relatório da GBA.

## Como executar cada módulo

Cada pasta tem o próprio README com instalação, execução e testes. Resumo:

| Módulo | Comando principal | Testes |
|---|---|---|
| RPA | `python main.py --reset` | `python -m pytest -q` (21 testes) |
| Cluster | `scripts/executar.ps1` (JDK 17 + iSPD 3.1) | resultados em `resultados/comparacao.md` |
| Zelo | `docker compose up --build`, ou ver o README da pasta | `cd backend && pytest -q` (28 testes) |
| Generative AI | ver `05_Generative_AI/README.md` (LM Studio + Qwen3-8B) | `python -m pytest citizentech/assistente/tests -q` (163 testes) |
| PLN | `python app.py` (Ollama + Qwen2.5-3B) | scripts em `tests/` |
| Visão Computacional | `python app.py` (Gradio) | `scripts/03_avaliar.py` |
| IoT | Edge Impulse → Deployment → Run this model | relatório em PDF |

## O que ficou fora do repositório

- Arquivos `.env` e chaves de API (só os `.env.example` estão aqui).
- Artefatos gerados que cada projeto recria sozinho: índices de busca do Gen AI (147 MB), logs, saídas de execução e caches.
- A amostra de 2.000 imagens da Visão Computacional **está incluída** (`09_Visao_Computacional/data/`, 16 MB), para que a avaliação possa ser repetida.
