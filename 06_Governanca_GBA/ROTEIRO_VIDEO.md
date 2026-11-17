# Roteiro do vídeo da GBA (alvo: 6 min · limite 5 a 7 min)

> Só tópicos, de propósito: fale com as suas palavras. O barema corta a nota do vídeo pela metade se houver leitura massiva de documento.
> Grave cada bloco separado e junte na edição. Os tempos são acumulados.

## Antes de gravar
- Abrir e "acordar" https://zelo-web.onrender.com (o servidor gratuito dorme).
- Gravar à parte o clipe da aba "Publicações oficiais" no Zelo local, com o LM Studio aberto (passo a passo em `04_Front_End_Zelo/docs/INTEGRACAO_GENAI.md`). Corte a espera de cada resposta na edição.
- Deixar prontos os materiais já gravados de cada módulo:
  - vídeo anotado da Visão: `09_Visao_Computacional/exemplos/video_demo_anotado.mp4`;
  - gravação de tela do OuviAí ao vivo, feita no celular;
  - prints do RPA: `01_RPA/docs/evidencias_visuais/`;
  - resultados do Cluster: `02_Cluster_Computing/resultados/`.
- Abrir o repositório GS-CitizenTech no GitHub e o relatório da GBA em PDF.

## Roteiro

| Tempo | Tela | Tópicos para falar |
|---|---|---|
| **0:00 → 0:30** | README do repositório (topo) | Quem é o grupo · tema CitizenTech · 9 disciplinas, 8 módulos + GBA · Zelo como eixo |
| **0:30 → 1:00** | README, tabela de módulos | 3 frentes: cidade (Zelo, Visão) · saúde (RPA, Cluster, Gen AI) · acesso do cidadão (IoT, PLN, Quântica) |
| **1:00 → 2:15** | Zelo no Render | Relato com telefone no texto → dado apagado · classificação + urgência · cidadão corrige · protocolo + canal oficial · **por que o canal vem de tabela:** IA inventou "0800-xxxx" no teste |
| **2:15 → 2:45** | Prints do RPA (execução, revisão humana) | Triagem de pedidos de UBS · 8 categorias · urgência → humano · 85,8% · **não apto para uso real** (trauma, infarto, saúde mental) |
| **2:45 → 3:05** | `comparacao.md` ou HTML do iSPD | Simula a fila do RPA · 2 → 4 workers · 100 s → 50 s · speedup ≈ 2× · é simulação, não hardware real |
| **3:05 → 3:35** | Zelo **local**, aba "Publicações oficiais" (gravar antes, com o LM Studio) | Integração real: Zelo → serviço isolado → RAG do DODF · uma pergunta respondida com publicação e trecho · "capital da França" → fora do escopo · protótipo não validado (8 de 31 incorretas) |
| **3:25 → 3:45** | Vídeo anotado da Visão | Fissura em concreto · acurácia 0,997 · triagem para inspeção, não avalia estrutura · ligação com o Zelo (foto do relato) |
| **3:45 → 4:05** | Gravação do OuviAí no celular | Surdos · campainha / batida / ambiente · 15/15 ao vivo · roda no celular, áudio não sai do aparelho |
| **4:05 → 4:25** | Arquitetura do PLN (`relatorio/arquitetura.png`) | Voz → texto → CDC → resposta falada · idosos e baixa alfabetização · WER 18,9% · poderia ser canal de voz do Zelo |
| **4:25 → 4:40** | `03_Computacao_Quantica/roadmap.png` | Identidade digital · Shor quebra RSA · criptografia pós-quântica (NIST 2024) · roadmap até 2032 |
| **4:40 → 5:30** | Relatório, Quadro 1 (integração) | 4 níveis · integrado: Zelo + Gen AI · por dados: RPA + Cluster · por tema: Visão · não integrados (IoT, PLN) e **por quê** · conceitual: Quântica |
| **5:30 → 5:55** | Relatório, Quadro 3 (riscos) | Humano no circuito em todos · LGPD: mascaramento, áudio apagado/local · aprendizado: regra no prompt não é garantia |
| **5:55 → 6:10** | README, links | Repositório, Zelo publicado e relatório · agradecimento |

**Total: cerca de 6 min 20 s**, com folga de 1 minuto para o limite de 7.

## Dicas
- Na parte da Governança (4:40 → 5:55), fale olhando o quadro e explique; não leia as linhas.
- Se passar de 7 min, encurte primeiro os blocos de Gen AI e Quântica.
- Publique no YouTube como **Não listado** e coloque o link no README e na seção 4 do relatório.
