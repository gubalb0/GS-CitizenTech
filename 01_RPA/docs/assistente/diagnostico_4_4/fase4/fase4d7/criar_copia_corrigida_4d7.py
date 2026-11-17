"""Fase 4D.7 - cria prototipo_vinculo_4d7.py a partir de prototipo_vinculo_4d5.py (somente leitura do original), trocando APENAS a linha da regex de abreviatura,
e gera o diff. Usa literais bytes RAW (rb'...') para nao repetir o erro de escape da 4D.5."""
import difflib
import pathlib

AQUI = pathlib.Path(__file__).parent
ORIG = AQUI.parent / "fase4d5" / "prototipo_vinculo_4d5.py"
src = ORIG.read_bytes()
old = b'    entre = re.sub(r"\x08(\\w{1,3})\\.", r"\x01", entre)'   # \x08 e \x01 aqui sao ESCAPES de byte (nao raw) de proposito: reproduzem os bytes de controle do original
new = rb'    entre = re.sub(r"\b(\w{1,3})\.", r"\1", entre)'
assert src.count(old) == 1, "linha original nao encontrada exatamente uma vez"
assert new.count(b"\x08") == 0 and new.count(b"\x01") == 0, "a linha nova nao pode conter bytes de controle"
out = src.replace(old, new)
(AQUI / "prototipo_vinculo_4d7.py").write_bytes(out)
a = src.decode("utf-8").splitlines(keepends=True)
b = out.decode("utf-8").splitlines(keepends=True)
d = "".join(difflib.unified_diff(a, b, "fase4d5/prototipo_vinculo_4d5.py", "fase4d7/prototipo_vinculo_4d7.py", n=2))
d = d.replace("\x08", "<0x08>").replace("\x01", "<0x01>")   # torna visiveis os bytes de controle do original
(AQUI / "diff_analisador_4d5_4d7.patch").write_text(d, encoding="utf-8", newline="")
linhas_dif = [i + 1 for i, (x, y) in enumerate(zip(src.splitlines(), out.splitlines())) if x != y]
print("linhas diferentes:", linhas_dif, "| bytes de controle na nova:", sum(1 for x in out if x < 32 and x not in (9, 10, 13)))
print(d)
