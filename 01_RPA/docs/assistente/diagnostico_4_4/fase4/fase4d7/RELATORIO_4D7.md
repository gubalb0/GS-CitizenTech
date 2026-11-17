# Fase 4D.7 — Correção pontual do analisador e fechamento do diagnóstico

Nenhum código de produção (`evidencias.py`, `geracao.py`, `catalogo.py`), a candidata `fail-closed-4.4.4d1-cand`, arquivos das Fases 4D.1–4D.6, casos, perguntas, documentos ou rótulos foram alterados; nenhuma geração, Qwen, LM Studio ou API; as políticas V0–V3 não foram implementadas. O trabalho está em `fase4/fase4d7/`.

## 1. Diagnóstico e correção
- **Errata lida** (RELATORIO_4D6 §1): a linha 122 de `prototipo_vinculo_4d5.py` deveria ignorar pontos de abreviatura.
- **Inspeção (bytes):** a linha lê `entre = re.sub(r"<0x08>(\w{1,3})\.", r"<0x01>", entre)`, isto é, o padrão começa com o byte **0x08** (backspace) e a substituição é o byte **0x01**. Causa: na edição da 4D.5 usei strings não-raw; `\b` virou 0x08 e `\1` virou 0x01. O padrão nunca casa, então a substituição foi um no-op e o ponto de "UI/G.," continuou a ser lido como fronteira de cláusula. Confirmei que a regex defeituosa tratava como fronteira **qualquer** ponto em `entre` (também decimais, datas, valores e CNPJ: ver `TESTES_REGEX_4D7.csv`, coluna "original DIVERGE").
- **Correção isolada:** `prototipo_vinculo_4d7.py` é cópia byte a byte do original com **apenas a linha 122** trocada por `entre = re.sub(r"\b(\w{1,3})\.", r"\1", entre)` (mesmo comentário). Zero bytes de controle na nova linha. Diff em `diff_analisador_4d5_4d7.patch` (1 linha removida, 1 adicionada, os bytes de controle do original aparecem como `<0x08>` e `<0x01>`). Nenhuma outra refatoração.

## 2. Testes pontuais (`TESTES_REGEX_4D7.csv`; 17 casos + 2 de integração)
- `UI/G.`, `U.I.`, `Dr.`, `Dra.`, `Sr.`, `Sra.`, `etc.`, `art.`, decimal (`5.883740%`), data (`07.05.2025`), valor (`R$ 1.147.963,68`) e CNPJ (`10.293.515/0001-80`): esperado "sem fronteira"; **corrigido OK em todos**; o original falhava em todos (tratava o ponto como fronteira).
- Ponto final após palavra longa (`assinado.`), ponto final após `2025.`, `;` e parênteses: esperado "fronteira"; **corrigido OK** (comportamento preservado).
- **Limitação registrada (R10):** ponto final de frase após palavra de até 3 caracteres (`…do hrt.`) é tratado como abreviatura pela regex pretendida; o resultado difere do esperado "fronteira". Nas unidades já segmentadas, o ponto final raramente fica em `entre`; não ampliei o escopo para tratá-lo.
- **Integração:** `_relacao` na unidade 33 do doc 495 (VITAMINA D): original → `coocorrencia: fronteira de clausula…`; corrigido → `explicita: 10 palavras entre a entidade e o atributo`.

## 3. Revalidação N1–N4 (`RESULTADOS_4D7.csv`, `COMPARACAO_4D5_4D7.md`)
Mesmos 26 casos sintéticos (27 alvos) e 5 casos reais (7 alvos), mesmos rótulos (congelamento verificado). O resultado original armazenado existia e foi **reproduzido exatamente** pela reexecução do protótipo original (controle), então a comparação não reconstruiu nada. **Um alvo mudou, em 34:** val-083 VITAMINA D, N1 e N2 de `coocorrencia`/`ausente` para **`explicita`** (aceita), conforme a leitura do texto: "VITAMINA D 400 UI/G., para atender as necessidades da Atenção Primária". Sem outras mudanças de estado, aceitação ou detalhe.
- **val-087, val-024, val-031, val-020:** sem alteração. val-087 Gama continua rejeitado por N1/N2 e aceito (falso vínculo) por N3/N4; val-031 e a CRSSU continuam só documentais; val-024 continua ausente em todos os níveis; val-020 continua só em N4.
- **val-083 CLORETO:** sem alteração (`ausente` / `adjacente_sem_vinculo` / N3 e N4 aceitam por proximidade); o destinatário do registro (Hospital Regional do Guará) continua distinto da entidade avaliada.
- Precisão e recall **não** foram calculados.

## 4. Regressões e limitações
Regressões: nenhuma observada. Limitações: rótulos de um só autor, sem segundo avaliador humano; os alvos reais são os mesmos que serviram ao ajuste do analisador; a regex corrigida trata como abreviatura qualquer palavra de até 3 caracteres antes de um ponto (R10); o inventário de entidades concorrentes e as heurísticas lexicais permanecem manuais; a 4D.6 não foi re-simulada (apenas a implicação foi registrada).

## 5. Integridade
- `verificar_hashes.py`: TODOS CONFEREM antes e depois.
- Antes do trabalho, registrei o hash de **56** arquivos (4D.1/4D.2 relatórios, tudo em `fase4d3`–`fase4d6`, e os três módulos de produção); depois, **todos idênticos**. `manifesto_hashes_4d7.json` guarda esses hashes antes/depois, o resultado da verificação e os hashes dos arquivos novos.
- Candidata confirmada: `VERSAO_POLITICA = "fail-closed-4.4.4d1-cand"`; `geracao.py` c857b99f49947e1a, `evidencias.py` 12118192b9529075, `catalogo.py` 8e44143ba1d092f5 (inalterados).
- Arquivos criados: os seis entregáveis pedidos e `prototipo_vinculo_4d7.py`, `criar_copia_corrigida_4d7.py`, `testes_regex_4d7.py`, `executar_4d7.py`, `gerar_resultados_4d7.py`. As saídas brutas intermediárias da reexecução ficaram fora do projeto.

## 6. Decisão final
1. **A regex foi corrigida?** Sim. A linha 122 agora é `\b(\w{1,3})\.` → `\1`, sem bytes de controle, e os testes pontuais passam (exceto a limitação R10, registrada).
2. **VITAMINA D mudou de classificação?** Sim: de `coocorrencia`/rejeitada para `explicita`/aceita em N1 e N2. CLORETO não mudou.
3. **Quais resultados mudaram?** Somente os de val-083 VITAMINA D em N1 e N2 (1 de 34 alvos). Nenhum sintético e nenhum outro real mudou.
4. **Houve regressões?** Não.
5. **Altera conclusão importante da 4D.5?** Não as principais. Permanecem: N3/N4 introduzem falsos vínculos (val-087 Gama, CLORETO e 7–8 sintéticos); N1/N2 não os introduzem; relações só documentais (CRSSU, HCB, val-020) continuam fora de N1/N2. Muda a afirmação de que N1/N2 perdiam uma relação legítima real por defeito do analisador (agora a recuperam) e a explicação dada para essa perda (errada, corrigida pela errata).
6. **A pendência técnica pode ser considerada encerrada?** Sim, para o defeito da regex: a correção está isolada, testada, revalidada e documentada. As limitações de método (rótulos de um só autor, inventário manual, heurísticas lexicais) permanecem registradas e não fazem parte desta pendência.

Parei aqui.
