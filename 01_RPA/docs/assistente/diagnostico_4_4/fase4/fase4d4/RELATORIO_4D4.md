# Fase 4D.4 — Validação dos julgamentos e casos com evidências reais (candidata `fail-closed-4.4.4d1-cand`, não validada)

Convenção: **[DOC]** evidência documental real (corpus, rodada 4.3, validação seletiva); **[SINT]** caso sintético da 4D.3 ou sonda desta fase; **[JO]** julgamento original (de quem escreveu os casos; não independente); **[AUD]** classe da auditoria 4.3 do projeto (também não é revisão humana independente); **[HUM]** julgamento humano independente — **nenhum existe ainda**; **[H]** hipótese não validada. Nenhum código de produção, caso/rótulo da 4D.3, JSONL, manifesto, snapshot ou hash foi alterado; nenhuma geração foi feita; a flag `priorizar_atributo` permanece desligada; C simplificada **não** foi implementada (só filtros pós-hoc em scripts de diagnóstico).

## 1. Integridade
- **Antes:** `verificar_hashes.py` → TODOS CONFEREM. Referência 4D.3 (16 car.): `CASOS_DIAGNOSTICOS_4D3.json` cafc0eb529e71c4a; `ROTULAGEM_4D3.md` 4e4168ec93fba89d; `RESULTADOS_BASELINE_4D3.csv` b62b52bd57595a3b; `COMPARACAO_VARIANTES_4D3.csv` 60589254c37d5361; `RELATORIO_4D3.md` 0dccce031e1f39a4; `CONGELAMENTO_ROTULAGEM_4D3.json` c04229279cbafceb; `resultados_4d3_detalhe.json` c51d47e50f79429f. Produção: `geracao.py` c857b99f49947e1a, `evidencias.py` 12118192b9529075, `catalogo.py` 8e44143ba1d092f5.
- **Depois:** ver §10 (verificado ao fim).
- Tudo novo está em `fase4/fase4d4/`. Os scripts só leem os insumos; as variantes B1/B2 são monkeypatch em memória restaurado com asserção.

## 2. Material de revisão humana (não realizada)
`PACOTE_REVISAO_HUMANA_4D4.md` (versão **cega**: pergunta, resposta, trechos integrais, origem, entidade, atributo, rótulo textual, formulário em branco; IDs reordenados e sem julgamento, justificativa, relação alegada, saída do pipeline ou variantes; documentos marcados como fictícios). `PACOTE_REVISAO_HUMANA_4D4_REFERENCIA.md` guarda o mapeamento (Caso 1=A07, 2=B04, 3=A02, 4=A06) e os julgamentos originais — **não deve ser entregue ao avaliador**. Nenhuma segunda avaliação foi feita ou simulada: o campo está `pendente` em todas as 43 linhas da matriz. Enquanto uma segunda pessoa não avaliar, isto **não** é revisão independente.

## 3. Evidências reais encontradas [DOC]
Detalhes e fontes em `CASOS_REAIS_4D4.md`. Resumo: titularidade×competência (val-087); entidade e atributo separados (val-087-A-r1, val-031); localização herdada (val-024, val-020, val-087-A-r1, val-130); destinatário diferente (val-083); conflito entre publicações (val-001); resposta correta combinando pergunta e documento (val-006, val-041). **Competência explícita em texto com rótulo conflitante (B04): nenhum caso real.**
Fatos novos relevantes:
1. O gabarito do dataset para val-087 diz "**incluindo o Gama**", mas o inciso IV do documento fala em "toda a Região de Saúde Sul" sem citar o Gama; as respostas corretas do braço B não o mencionam. O eco da pergunta existe até no gabarito.
2. Em val-087-A-r1, o chunk neutro C1 **contém "Gama"** (inciso XI, sobre os Conselhos de Saúde do Gama e de Santa Maria), em frase diferente do trecho citado (inciso IX).
3. 12 das 30 entregas reais repetem um nome da pergunta que não está no span citado; 11 são "Correta"/"Correta, mas parcial" e 1 "Incorreta" [AUD]. O eco é comum e, na maioria, inofensivo nos dados reais.

## 4. O falso bloqueio B04 (investigação, sem alterar código)
Resultados em `b04_c_causas_4d4.json` [SINT].
1. **Por que o rótulo conflitante "prevalece"?** Na baseline **não prevalece**: o span tem rótulo `titular` (`estado=conflito`), mas `cue_de_atributo` encontra "compete" no próprio trecho, então `causas_do_conflito = []` e `bloqueia = False`; B04 é entregue. O "falso bloqueio" da 4D.3 foi **artefato da definição do meu filtro C**, que testava `estado == conflito` (classificação do rótulo) em vez de `causas_do_conflito`.
2. **Classificação do rótulo?** O rótulo é classificado corretamente (titular → MEMBRO); o erro estava no uso do `estado` bruto.
3. **Falta de associação rótulo–atributo?** Só existe associação por **família de rótulo** (rótulo→família→compatível com o atributo). Não há associação entre o span, a frase em que a entidade aparece e o atributo; esse vínculo é justamente o que a hipótese C exigiria e **não existe** hoje.
4. **Necessidade dos trechos?** B04: `necessaria=True`, porém sem causa de conflito, portanto não bloqueia. Não é problema da necessidade.
5. **C simplificada distingue competência explícita de titularidade sem exceção textual frágil?** Reescrevendo o filtro por `causas` (diagnóstico pós-hoc, **não** proposta), B04 passa e A02/A06 continuam bloqueados. Mas isso só funciona porque herda o `cue_de_atributo`, que é **lexical** e frágil [SINT, sondas desta fase]: **P1** (membro cujo nome de órgão contém "Competência", sem atribuir competência) é **entregue** (falsa liberação: o cue aceita a palavra incidental); **P2** ("a quem *incumbe* deliberar…", competência explícita com palavra fora da lista) é **bloqueado** (falso bloqueio). Distinguir "competência explícita" de "titularidade" sem lista de palavras exigiria análise sintática/semântica da relação ao nível da frase [H]. Em dados reais não há instância de cue em span de rótulo conflitante (varredura do corpus), logo a fragilidade é demonstrada, não medida.

## 5. Hipótese da C simplificada diante dos dados reais
| Medida | Resultado |
|---|---|
| Corrige o único positivo real (val-087-A-r1)? [DOC] | **Não**: "Gama" consta do chunk C1 (inciso XI), então o vínculo no nível do chunk é satisfeito. Em nível de publicação, também passaria (o doc 174 cita o Gama) |
| Entregas reais removidas | **2/30** nos 150 (val-020, val-031), ambas plausivelmente corretas [AUD: "Correta, mas parcial" e "Abstenção indevida" na rodada original]; 0/10 nos 21 |
| Erros reais capturados | **0** |
| B1/B2 | corrigem val-087-A-r1 (1/21); 0 mudanças nos 150 |
No sintético, C (por `causas`) corrige A02, preserva A07 e B04 e bloqueia A06 [SINT]; esse bom desempenho **não se sustenta nos dados reais** porque o cenário sintético A02 foi montado com o nome ausente do chunk neutro, o que o caso real não reproduz. A única hipótese ainda aberta é o vínculo em **nível de span/frase** (o "Gama" do inciso XI não se liga ao inciso IX): não testada, sem implementação.

## 6. Matriz
`MATRIZ_AVALIACAO_4D4.csv`: 43 linhas (30 sintéticas, 13 reais) com origem, pergunta, entidade, atributo, evidência, relação, conflito, julgamento original e seu tipo, segunda avaliação (`pendente`), resultado baseline, B1/B2, C(estado, 4D.3), C(causas, 4D.4), confiança e observações. Os resultados das variantes sobre dados reais são replays offline com a candidata atual.

## 7. Respostas às perguntas de decisão
1. **A C simplificada tem sustentação suficiente para um protótipo?** **Não.** A evidência a favor é sintética e a favor de rótulos não validados; os dados reais mostram 0 acertos e 2 perdas em 30 entregas, e não corrigem o caso motivador.
2. **B04 é corrigível sem exceção frágil?** B04 **não é uma falha da baseline**; o falso bloqueio era do filtro C. O comportamento correto de B04 depende de um cue lexical frágil (P1/P2). Corrigir isso sem lista de palavras exigiria relação ao nível da frase [H].
3. **Os casos reais confirmam o vínculo entidade–atributo–trecho?** **Não de forma conclusiva.** Confirmam que a localização herdada existe (val-024, val-020, val-087), mas o vínculo em nível de chunk/publicação não separa o caso crítico. A hipótese em nível de span permanece não testada.
4. **O que continua sem solução:** eco legítimo da pergunta vs localização nova (o próprio gabarito de val-087 ecoa); entidade em chunk vizinho do mesmo documento (val-031, val-020); competência explícita vs titularidade sem léxico; divergência mecanismo×gabarito em destinatário (val-083); regra de janela do catálogo (P1) e taxonomia de status (P5), fora do escopo.
5. **Risco de perda de recall:** C (chunk-level): 2/30 das entregas reais (≈7%) e 0 detecções [DOC]. B1/B2: 0/30 nos 150 e 0 outras mudanças nos 21, mas a base é quase insensível (um único caso de conflito de rótulo), então **o risco não é estimável**; no sintético B1/B2 bloqueiam A07 [SINT, julgamento contestável].
6. **Precisam de julgamento humano:** A02, A06, A07, B04 (pacote preparado); val-087-A-r1 (a menção "no Gama" é aceitável?), val-024 e val-020 (aceitar eco de localização?), val-031 (entidade em chunk vizinho), val-083 (destinatário vs gabarito).

## 8. Recomendação
**Não implementar B1, B2, C ou D.** A evidência continua concentrada em quatro casos sintéticos e em um único positivo real. Os dados reais não sustentam C chunk-level e mostram que o eco da pergunta é comum e, na maioria, correto. Passos que dependem de autorização: (a) coletar a segunda avaliação humana do pacote; (b) decidir a política para ecos da pergunta (bloquear, entregar sem a localização ou aceitar); (c) se autorizado, protótipo **offline** de vínculo em nível de frase/span, com avaliação apenas contra os 43 casos e sem alterar produção; (d) revisão separada das regras de ambiguidade/combinação de publicações (P1/P5).

## 9. Limitações
Um positivo real; B04 sem análogo real; gabaritos e auditoria 4.3 não são revisão humana independente; as sondas P1/P2 são sintéticas; contagem R-11 feita no span citado (não verifiquei o chunk caso a caso); replays offline com respostas gravadas, sem novas gerações; C testado só como filtro pós-hoc com definição minha.

## 10. Integridade final
Ao encerrar: `verificar_hashes.py` → TODOS CONFEREM; os 7 arquivos da 4D.3 conferem com os hashes do §1; `geracao.py`, `evidencias.py` e `catalogo.py` idênticos (c857b99f49947e1a / 12118192b9529075 / 8e44143ba1d092f5). Nenhum código de produção, JSONL, manifesto ou snapshot foi tocado.
