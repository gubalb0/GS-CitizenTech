"""Etapa 4.4 / Fase 4D.1 (candidata, nao validada) - normalizacao do indice de lista antes do reconhecimento do rotulo (`EV.rotulo_do_valor`).
Causa raiz: val-087-A-r1 citou '4 - Titular: Diretor do HRG...' e o parser, que espera o rotulo no inicio do valor, nao o reconheceu (estado 'desconhecido')."""
import glob
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_fase4a import MEMB, Q87, chunk, entregue, o87, rels, rodar  # noqa: E402

from citizentech.assistente import evidencias as EV  # noqa: E402

TXT = ("Suplente: Substituto legal do cargo; 4 - Titular: Diretor do Hospital Regional do Gama, da Diretoria do HRG (HRG); Suplente: Substituto; "
       "5. Titular: Maria; 6) Titular: Joao; IV - Titular: Pedro; objeto: aquisicao de itens; Valor: R$ 1.234,56; Processo 00060-00173080/2025-64.")
TIT = {"rotulo": "titular", "familia": "MEMBRO"}


def test_1_rotulo_sem_indice():
    assert EV.rotulo_do_valor(TXT, "Titular: Diretor do Hospital Regional do Gama") == TIT


def test_2_indice_numerico_com_hifen():
    assert EV.rotulo_do_valor(TXT, "4 - Titular: Diretor do Hospital Regional do Gama") == TIT
    assert EV.rotulo_do_valor(TXT, "4 – Titular: Diretor do Hospital Regional do Gama") == TIT         # meia-risca
    assert EV.sem_indice_de_lista("4 - Titular: X") == "Titular: X"


def test_3_indice_numerico_com_ponto():
    assert EV.rotulo_do_valor(TXT, "5. Titular: Maria") == TIT


def test_4_indice_numerico_com_parentese():
    assert EV.rotulo_do_valor(TXT, "6) Titular: Joao") == TIT


def test_5_romano_maiusculo_canonico_e_equivalente():
    assert EV.rotulo_do_valor(TXT, "IV - Titular: Pedro") == TIT
    assert EV.sem_indice_de_lista("CIVIL - Titular: x") == "CIVIL - Titular: x"                         # palavra, nao algarismo
    assert EV.sem_indice_de_lista("MIX - Titular: x") == "MIX - Titular: x"


def test_6_texto_sem_rotulo_apos_o_indice_nao_muda():
    v = "4 - Diretor do Hospital Regional do Gama sem rotulo"
    assert EV.sem_indice_de_lista(v) == v and EV.rotulo_do_valor(TXT, v) is None


def test_7_numeros_do_conteudo_datas_ids_cnpj_e_valores_nao_sao_removidos():
    for v in ("14/03/2025: Objeto aquisicao", "2025 - Objeto: x", "12.345.678/0001-90 Titular: y", "00060-00173080/2025-64: Objeto x", "R$ 10 - Objeto: x",
              "1.234,56 - Valor: x", "10.5 Objeto: x", "123456 - Titular: y"):
        assert EV.sem_indice_de_lista(v) == v, v
    assert EV.rotulo_do_valor(TXT, "2025 - Objeto: x") is None                                          # 4 digitos nao e indice


def test_8_rotulo_em_posicao_intermediaria_continua_pela_busca_antes_do_valor():
    assert EV.rotulo_do_valor(TXT, "aquisicao de itens") == {"rotulo": "objeto", "familia": "OBJETO"}    # (b): 'objeto:' imediatamente antes
    assert EV.rotulo_do_valor(TXT, "R$ 1.234,56") == {"rotulo": "valor", "familia": "VALOR"}


def test_9_comportamento_anterior_preservado():
    for v, esperado in (("Titular: Diretor", TIT), ("Objeto: servico", {"rotulo": "objeto", "familia": "OBJETO"}), ("sem rotulo nenhum", None)):
        assert EV.rotulo_do_valor(f"x; {v}; y", v) == esperado


# ----------------------------------------------------------------------------- cenarios sinteticos integrados
C1 = chunk(1, "Art. 2º Designar membros da Coordenação de Regulação da Região Sul (CRSSU) em 2025: " + MEMB + " 4 - Titular: Diretor do Hospital Regional do Gama (HRG); Suplente: substituto.", 174)


def test_membro_com_indice_e_bloqueado_como_sem_indice():
    for sp in ("Titular: Diretor do Hospital Regional do Gama (HRG)", "4 - Titular: Diretor do Hospital Regional do Gama (HRG)", "4. Titular: Diretor do Hospital Regional do Gama (HRG)"):
        r = rodar(Q87, [C1], o87("A Coordenação é composta pelo Diretor do HRG.", [("C1", sp)]))
        assert r.status == "insuficiente" and r.verificacao["problemas"] == ["rotulo_incompativel_com_atributo"], sp


def test_competencia_explicita_com_indice_nao_e_bloqueada():
    c = chunk(1, "Coordenação de Regulação da Região Sul, 2025. 4 - Competência: discutir e deliberar sobre os serviços regulados da Região Sul. 5 - Compete à CRSSU fixar fluxos.", 174)
    casos = (("4 - Competência: discutir e deliberar sobre os serviços regulados da Região Sul", "Compete discutir e deliberar sobre os serviços regulados."),
             ("Competência: discutir e deliberar sobre os serviços regulados da Região Sul", "Compete discutir e deliberar sobre os serviços regulados."),
             ("5 - Compete à CRSSU fixar fluxos", "Compete à CRSSU fixar fluxos."))
    for sp, resp in casos:
        r = rodar(Q87, [c], o87(resp, [("C1", sp)]))
        assert entregue(r), (sp, r.verificacao)
        assert not any(x["bloqueia"] for x in rels(r))


# ----------------------------------------------------------------------------- reproducao dos casos da validacao seletiva (replay offline, sem modelo)
RAIZ = Path(__file__).resolve().parents[3]
FASE4 = RAIZ / "docs" / "assistente" / "diagnostico_4_4" / "fase4"
IDX = RAIZ / "data_assistente" / "indices" / "est300o30"
ARQ = sorted(glob.glob(str(FASE4 / "validacao_seletiva*.jsonl")))


@pytest.mark.skipif(not (IDX.exists() and len(ARQ) >= 2), reason="indice/JSONL indisponiveis")
def test_replay_21_rotulo_de_val_087_a_r1_e_reconhecido_e_nenhuma_decisao_muda():
    """RESULTADO REAL da 4D.1: o rotulo `titular`/MEMBRO de '4 - Titular: ...' passa a ser reconhecido em val-087-A-r1, mas a decisao NAO muda: a resposta de r1 ('...no Gama')
    so usa termos exclusivos de C1 (a palavra 'Gama' vem da pergunta e e excluida de `termos_de_uso`), logo C2 nao e 'necessaria' (mecanismo B v2) e nao bloqueia.
    r2/r3 (citam 'HRG', termo exclusivo de C2) continuam bloqueados. A liberacao indevida de r1 depende do mecanismo B, fora do escopo autorizado."""
    from citizentech.assistente import avaliacao_e2e as AE
    from citizentech.assistente import geracao as G
    from citizentech.assistente.catalogo import Catalogo
    from citizentech.assistente.retriever import Indice

    class Falso:
        def __init__(self, bruto): self.bruto = bruto
        def completar(self, msgs, temperatura=None):
            return {"conteudo": self.bruto, "finish": "stop", "tokens_prompt": 0, "tokens_saida": 0, "tokens_raciocinio": 0, "latencia_s": 0.0}

    corpus, *_ = AE.preparar()
    cat, idx = Catalogo.de_corpus(corpus), Indice.carregar(IDX)
    regs = {json.loads(l)["run_id"]: json.loads(l) for f in ARQ for l in open(f, encoding="utf-8")}
    novos = {}
    for rid, r in regs.items():
        cfg = G.ConfigGeracao(priorizar_atributo=bool(r["flag_priorizar_atributo"]))
        p = r["saida"]["pergunta"]
        n = G.gerar_resposta(p, idx.buscar(p, k=cfg.max_chunks, modo="bm25"), Falso(r["saida"]["telemetria"]["saida_bruta"]), cfg, catalogo=cat)
        assert (n.status, n.resposta, (n.verificacao or {}).get("problemas")) == (r["saida"]["status"], r["saida"]["resposta"], (r["saida"]["verificacao"] or {}).get("problemas")), rid
        novos[rid] = n
    r1 = [x for x in rels(novos["val-087-A-r1"]) if x["fonte"] == "C2"]
    assert r1 and all(x["rotulo"] == TIT and x["estado"] == "conflito" and x["causas_do_conflito"] == ["rotulo"] and x["necessaria"] is False and x["bloqueia"] is False for x in r1)
    for rid in ("val-087-A-r2", "val-087-A-r3"):
        assert novos[rid].status == "insuficiente" and novos[rid].verificacao["problemas"] == ["rotulo_incompativel_com_atributo"]
