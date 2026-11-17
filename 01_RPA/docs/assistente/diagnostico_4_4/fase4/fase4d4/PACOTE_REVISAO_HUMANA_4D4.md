# Pacote de revisão humana — Fase 4D.4 (VERSÃO CEGA)

**Material preparado para uma segunda avaliação humana. Nenhuma avaliação foi feita nem simulada: os campos de resposta estão em branco.**

Todos os documentos abaixo são **fictícios (sintéticos)**: foram escritos para o diagnóstico, não vêm do DODF. Esta versão não traz julgamentos anteriores, justificativas, saídas do sistema nem resultados de variantes, de propósito. Por favor, **não consulte** o relatório da Fase 4D.3 nem a versão de referência antes de preencher.

## Como avaliar
Para cada caso, responda com base **apenas** nos trechos mostrados:
1. **Correção semântica** da resposta no mundo descrito pelos trechos: `correta` | `parcialmente correta` | `incorreta` | `não verificável`.
2. **Sustentação pelos trechos citados**: a resposta (inclusive a entidade/localização mencionada) é sustentada pelos trechos citados? `sim` | `parcial` | `não` | `não verificável`.
3. **Decisão desejável para um assistente que prefere abster-se a errar**: `entregar` | `bloquear` | `indeterminado`.
4. Se a resposta menciona uma entidade/localidade que também está na pergunta: ela é sustentada pelos trechos, ou apenas repete a pergunta?
5. Confiança (`alta`/`média`/`baixa`) e comentário livre. Se houver mais de uma interpretação plausível, marque `não verificável`/`indeterminado` em vez de forçar.

---
## Caso 1
**Pergunta:** Qual o objeto do contrato nº 12/2025 da empresa Alfa Serviços Ltda para o Hospital Regional de Planaltina?
**Resposta candidata:** O objeto é a manutenção preventiva de equipamentos de imagem, para o Hospital Regional de Planaltina.
**Entidade de interesse:** Hospital Regional de Planaltina  |  **Atributo perguntado:** OBJETO

**Trechos disponíveis (texto integral do trecho):**
- **T1** — origem: Extrato de Contrato nº 12/2025 (documento FICTÍCIO (sintético)), documento nº 101, trecho 1 de 1.  
  > Extrato de Contrato nº 12/2025. Contratada: Alfa Serviços Ltda. Objeto: manutenção preventiva de equipamentos de imagem. Valor: R$ 80.000,00, para o Hospital Regional de Planaltina (HRP).

**Trechos efetivamente citados como evidência na resposta:**
- de T1: “Objeto: manutenção preventiva de equipamentos de imagem” — rótulo textual: “Objeto:”
- de T1: “Valor: R$ 80.000,00, para o Hospital Regional de Planaltina (HRP)” — rótulo textual: “Valor:”

| Pergunta | Sua resposta |
|---|---|
| 1. Correção semântica |  |
| 2. Sustentação pelos trechos |  |
| 3. Decisão desejável |  |
| 4. Entidade/localização: sustentada ou só eco da pergunta? |  |
| 5. Confiança / comentário |  |

---
## Caso 2
**Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
**Resposta candidata:** Compete ao Diretor do HRG deliberar sobre os serviços do Gama.
**Entidade de interesse:** Gama  |  **Atributo perguntado:** COMPETENCIA

**Trechos disponíveis (texto integral do trecho):**
- **T1** — origem: Ordem de Serviço nº 93/2025 (documento FICTÍCIO (sintético)), documento nº 101, trecho 1 de 1.  
  > Ordem de Serviço nº 93/2025. Coordenação de Regulação da Região de Saúde Sul (CRSSU). Titular: o Diretor do HRG do Gama, a quem compete deliberar sobre os serviços regulados do Gama.

**Trechos efetivamente citados como evidência na resposta:**
- de T1: “Titular: o Diretor do HRG do Gama, a quem compete deliberar sobre os serviços regulados do Gama” — rótulo textual: “Titular:”

| Pergunta | Sua resposta |
|---|---|
| 1. Correção semântica |  |
| 2. Sustentação pelos trechos |  |
| 3. Decisão desejável |  |
| 4. Entidade/localização: sustentada ou só eco da pergunta? |  |
| 5. Confiança / comentário |  |

---
## Caso 3
**Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
**Resposta candidata:** A Coordenação tem competência para nortear as gerências de regulação e implementar as normas e protocolos de regulação no Gama.
**Entidade de interesse:** Gama  |  **Atributo perguntado:** COMPETENCIA

**Trechos disponíveis (texto integral do trecho):**
- **T1** — origem: Ordem de Serviço nº 93/2025 (documento FICTÍCIO (sintético)), documento nº 101, trecho 1 de 1.  
  > Ordem de Serviço nº 93/2025. Coordenação de Regulação da Região de Saúde Sul (CRSSU). IX - As Deliberações deverão nortear as gerências de regulação no cumprimento das atribuições regimentais de implementar as normas e protocolos de regulação.
- **T2** — origem: Ordem de Serviço nº 93/2025 (documento FICTÍCIO (sintético)), documento nº 102, trecho 1 de 1.  
  > Ordem de Serviço nº 93/2025. Coordenação de Regulação da Região de Saúde Sul (CRSSU). Art. 2º Designar membros: 4 - Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: substituto.

**Trechos efetivamente citados como evidência na resposta:**
- de T1: “As Deliberações deverão nortear as gerências de regulação no cumprimento das atribuições regimentais de implementar as normas e protocolos de regulação” — rótulo textual: sem rótulo com dois-pontos no início do trecho citado
- de T2: “4 - Titular: Diretor do Hospital Regional do Gama (HRG)” — rótulo textual: “Titular:”

| Pergunta | Sua resposta |
|---|---|
| 1. Correção semântica |  |
| 2. Sustentação pelos trechos |  |
| 3. Decisão desejável |  |
| 4. Entidade/localização: sustentada ou só eco da pergunta? |  |
| 5. Confiança / comentário |  |

---
## Caso 4
**Pergunta:** Quais as competências da Coordenação de Regulação da Região de Saúde Sul em relação aos serviços do Gama?
**Resposta candidata:** Compete discutir e deliberar sobre os serviços regulados no Gama.
**Entidade de interesse:** Gama  |  **Atributo perguntado:** COMPETENCIA

**Trechos disponíveis (texto integral do trecho):**
- **T1** — origem: Ordem de Serviço nº 93/2025 (documento FICTÍCIO (sintético)), documento nº 101, trecho 1 de 1.  
  > Ordem de Serviço nº 93/2025. Coordenação de Regulação da Região de Saúde Sul (CRSSU). IV - Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados.
- **T2** — origem: Ordem de Serviço nº 93/2025 (documento FICTÍCIO (sintético)), documento nº 102, trecho 1 de 1.  
  > Ordem de Serviço nº 93/2025. Coordenação de Regulação da Região de Saúde Sul (CRSSU). Art. 2º Designar membros: 4 - Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: substituto.

**Trechos efetivamente citados como evidência na resposta:**
- de T1: “IV - Compete à CRSSU discutir e deliberar sobre a direção, avaliação e monitoramento dos serviços regulados” — rótulo textual: sem rótulo com dois-pontos no início do trecho citado
- de T2: “4 - Titular: Diretor do Hospital Regional do Gama (HRG)” — rótulo textual: “Titular:”

| Pergunta | Sua resposta |
|---|---|
| 1. Correção semântica |  |
| 2. Sustentação pelos trechos |  |
| 3. Decisão desejável |  |
| 4. Entidade/localização: sustentada ou só eco da pergunta? |  |
| 5. Confiança / comentário |  |

---
Avaliador(a): ____________  Data: ________  (preencher; não preencher por inferência da equipe)