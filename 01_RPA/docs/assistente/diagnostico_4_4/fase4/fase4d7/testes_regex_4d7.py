"""Fase 4D.7 - testes pontuais da regex de abreviatura (original 4D.5 vs corrigida 4D.7). Nao e uma suite extensa.
Metrica: apos aplicar a substituicao, a regra de fronteira de _relacao (`[;.()]`) ainda encontra pontuacao? (True = fronteira de clausula)."""
import csv
import importlib.util
import pathlib
import re
import sys

AQUI = pathlib.Path(__file__).parent
D5 = AQUI.parent / "fase4d5"
sys.path.insert(0, r"D:\Downloads\GS\RPA")
raw5 = (D5 / "prototipo_vinculo_4d5.py").read_bytes()
assert b'r"\x08(\\w{1,3})\\.", r"\x01"' in raw5, "a linha defeituosa da 4D.5 nao esta como documentado"
ORIG_PAT, ORIG_REP = "\x08(\\w{1,3})\\.", "\x01"        # exatamente os bytes do arquivo 4D.5 (string NAO raw)
NEW_PAT, NEW_REP = r"\b(\w{1,3})\.", r"\1"


def carregar(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


P5 = carregar("p5", D5 / "prototipo_vinculo_4d5.py")
P7 = carregar("p7", AQUI / "prototipo_vinculo_4d7.py")


def fronteira(s, pat, rep):
    return bool(re.search(r"[;.()]", re.sub(pat, rep, s)))


T = [  # (id, descricao, entrada, esperado_fronteira, nota)
    ("R01", "UI/G. (caso da val-083)", "vitamina d 400 ui/g., para atender as necessidades da ", False, ""),
    ("R02", "U.I.", "dose de 400 u.i. por dia", False, ""),
    ("R03", "Dr.", "o dr. silva assinou", False, ""),
    ("R04", "Dra.", "a dra. maria assinou", False, ""),
    ("R05", "Sr.", "o sr. jose assinou", False, ""),
    ("R06", "Sra.", "a sra. ana assinou", False, ""),
    ("R07", "etc.", "contratos, licitacoes etc. e outros", False, ""),
    ("R08", "art.", "conforme art. 30 da lei", False, ""),
    ("R09", "ponto final apos palavra longa", "o contrato foi assinado. o hrt recebeu", True, ""),
    ("R10", "ponto final apos palavra curta (<=3 letras)", "o contrato e do hrt. o hospital", True, "LIMITACAO conhecida: palavra de ate 3 caracteres antes do ponto e tratada como abreviatura; nas unidades segmentadas o ponto final raramente fica em `entre`"),
    ("R11", "decimal", "reducao de 5.883740% do valor", False, ""),
    ("R12", "data com pontos", "assinado em 07.05.2025 pelo diretor", False, ""),
    ("R13", "data com barras e ponto final", "assinado em 07/05/2025. proximo", True, "o ponto final vem apos '2025' (4 caracteres): continua fronteira"),
    ("R14", "valor monetario", "no valor de r$ 1.147.963,68 para o hospital", False, ""),
    ("R15", "CNPJ", "cnpj 10.293.515/0001-80 ltda", False, ""),
    ("R16", "ponto e virgula", "item um; item dois", True, "inalterado pela correcao"),
    ("R17", "parenteses", "hospital (hrt) contratou", True, "inalterado (parenteses sao tratados antes, em outra linha de _relacao)"),
]
rows = []
for tid, desc, ent, esp, nota in T:
    o = fronteira(ent, ORIG_PAT, ORIG_REP)
    n = fronteira(ent, NEW_PAT, NEW_REP)
    res = "OK" if n == esp else ("LIMITACAO" if tid == "R10" else "FALHA")
    rows.append([tid, desc, ent, esp, o, n, res, "original ok" if o == esp else "original DIVERGE do esperado", nota])
# integracao: _relacao do modulo original (4D.5) vs corrigido (4D.7) na unidade real da val-083 (VITAMINA D) - texto da propria publicacao
from citizentech.assistente import avaliacao_e2e as AE  # noqa: E402

corpus, *_ = AE.preparar()
doc495 = next(d for d in corpus if d["id"] == 495)["texto_completo"]
seg = P5.segmentar(doc495)
u = doc495[seg[33][0]:seg[33][1]]
for nome, P in (("4D.5", P5), ("4D.7", P7)):
    unid = {"txt": u, "f": P.F(u), "i": 33, "chunks": []}
    r = P._relacao(unid, P._mencoes(unid, ["atencao primaria"], "organizacao"), ["vitamina"], [], ["atencao primaria"])
    rows.append([f"I-{nome}", "integracao: _relacao na unidade 33 do doc 495 (VITAMINA D)", u, "explicita", "", "", "OK" if r[0] == "explicita" else "ESPERADO_NAO_ATINGIDO" if nome == "4D.7" else "ESTADO_ORIGINAL", f"{r[0]}: {r[1]}", ""])
with open(AQUI / "TESTES_REGEX_4D7.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["id", "descricao", "entrada", "esperado_fronteira(ou relacao)", "observado_original_4D5", "observado_corrigido_4D7", "resultado", "comentario_original", "nota"])
    w.writerows(rows)
for r in rows:
    print(r[0], r[1][:40], "| esp", r[3], "| orig", r[4], "| novo", r[5], "|", r[6], "|", r[7][:60])
