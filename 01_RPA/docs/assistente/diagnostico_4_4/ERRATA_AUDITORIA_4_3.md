# Errata da auditoria independente 4.3 (registrada na Etapa 4.4, Fase 1)

Os arquivos da auditoria (`auditoria_independente_4_3/`) **não foram editados**; as correções ficam aqui. As rodadas originais também não foram alteradas.

| Caso | O que a auditoria registrou | O que o diagnóstico 4.4 mostrou | Efeito |
|---|---|---|---|
| **val-050** | Heparina e metaraminol fora do período; midazolam "tampouco comprovadamente no período" | **Fato:** o doc 1307 declara "no período de 31/07/2025 a 22/08/2025", portanto o midazolam **está** no período. Heparina e metaraminol vêm do doc 196 ("no período de 31/01/2025 à 06/02/2025"), fora do período | Classificação *Incorreta* mantida; a resposta tinha **1 de 3 itens correto**, não 0 de 3 |
| **val-062** | Abstenção indevida com reprovação por `trecho_nao_literal`, tratada como possível falso positivo do verificador | **Fato:** o modelo **inventou** a citação "Valor do Contrato: R$ 1.105.500,00". O doc 1450 traz R$ 2.449.859,97 (contrato) e R$ 204.155,00 (empenho inicial) | A resposta existe no corpus (abstenção indevida mantida), mas o **bloqueio foi legítimo** (verdadeiro positivo do verificador). Sai do grupo "falsos positivos" |
| **val-097** | Grupo B (fonte esperada não enviada) | **Fato:** o replay de `montar_contexto` mostra que o chunk `dodf-105:est300o30:0000` **foi enviado** (a rodada marcou `enviado` por posição, supondo que o contexto é o prefixo do ranking) | Grupo real = **A**. Grupos da rodada 4.3: A = 77 e B = 73 (original 76/74); abstenções indevidas: A = 28 e B = 28 (original 27/29) |

Dados de apoio: `grupos_ab_corrigidos_20261114-130608.json` (recalculado, arquivo novo); `RELATORIO_DIAGNOSTICO_4_4.md` seções 1.3, 3 e 4.
Nenhum outro caso muda de grupo. Onze casos têm contexto enviado diferente do prefixo do ranking (val-020, 021, 024, 046, 050, 061, 078, 085, 090, 097, 117), mas só val-097 muda de grupo.
