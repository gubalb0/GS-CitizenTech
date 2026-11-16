# Physical Computing, Embedded AI, Robotics & Cognitive IoT: OuviAí

**Integrantes:** Gustavo Balbo Saraiva (RM 561711), Henry Gimenez (RM 563217), Vinicius Araujo (RM 564504)

Assistente sonoro para pessoas surdas ou com deficiência auditiva: o microfone do celular capta o som, um modelo treinado no **Edge Impulse** reconhece **campainha**, **batida na porta** ou **ambiente**, e a tela mostra o evento.

- Relatório completo com as 12 capturas de tela: [`relatorio_ouviai.pdf`](relatorio_ouviai.pdf)
- Vídeo da validação ao vivo no celular (55 s, 15 tentativas): [`video_validacao_ao_vivo.mp4`](video_validacao_ao_vivo.mp4). A gravação de tela do iPhone não captura o som enquanto o microfone está em uso; o relatório (seção 6) traz o tempo de cada tentativa no vídeo.

## Arquitetura

```
som → microfone do celular → janelas de 1 s (16 kHz) → MFE (espectrograma Mel) → CNN 1D → classe na tela
```

O modelo roda no navegador do celular (Edge Impulse → Deployment → Run this model), sem aplicativo próprio e sem enviar o áudio para a nuvem.

## Dados e resultados

- 60 gravações de 5 s feitas pelo grupo (20 por classe), divididas em 45 para treino e 15 para teste.

| Avaliação | O que mede | Resultado |
|---|---|---|
| Validação do treinamento | aprendizado (20% das janelas de treino, modelo int8) | 98,8% |
| Teste com áudios inéditos | generalização (15 arquivos, 135 janelas, modelo float32) | 97,78% |
| Tempo real no celular | funcionamento real (15 tentativas ao vivo) | 15/15 (100%) |

- Modelo embarcável: inferência em 7 ms, 14,7 KB de RAM e 40,9 KB de flash.
- Único tipo de erro: falso positivo de campainha em um áudio de ambiente com ruído de elevador e movimento de cadeira.
- **ODS:** 10 (redução das desigualdades) e 11 (cidades e comunidades sustentáveis).
