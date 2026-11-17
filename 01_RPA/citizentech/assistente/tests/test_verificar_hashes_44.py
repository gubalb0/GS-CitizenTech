"""Etapa 4.4 / Fase 1: a conferencia de hashes e SOMENTE LEITURA e nunca reescreve artefatos."""
import ast
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "scripts"))
import verificar_hashes as VH  # noqa: E402


def _estado(raiz: Path) -> dict:
    return {p.relative_to(raiz).as_posix(): (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest()) for p in raiz.rglob("*") if p.is_file()}


def _mini_repo(tmp_path, alterar=False):
    (tmp_path / "docs" / "assistente" / "diagnostico_4_4").mkdir(parents=True)
    (tmp_path / "data_assistente" / "derivados").mkdir(parents=True)
    ex = tmp_path / "data_assistente" / "derivados" / "chunks_exemplos.json"
    ex.write_text('{"a": 1}', encoding="utf-8")
    h = hashlib.sha256(ex.read_bytes()).hexdigest()
    (tmp_path / "docs" / "modelo_congelado.json").write_text(json.dumps({"sha256": {}}), encoding="utf-8")
    (tmp_path / "docs" / "assistente" / "diagnostico_4_4" / "hashes_referencia_44.json").write_text(
        json.dumps({"arquivos": {"data_assistente/derivados/chunks_exemplos.json": h}}), encoding="utf-8")
    if alterar:
        ex.write_text('{"a": 2}', encoding="utf-8")
    return tmp_path


def test_verificacao_nao_escreve_nada_e_aponta_arquivo_ok(tmp_path):
    raiz = _mini_repo(tmp_path)
    antes = _estado(raiz)
    assert VH.main(["x", str(raiz)]) == 0
    assert _estado(raiz) == antes                           # nenhum arquivo criado, alterado (mtime) ou removido


def test_verificacao_detecta_alteracao_sem_corrigir_o_arquivo(tmp_path):
    raiz = _mini_repo(tmp_path, alterar=True)
    antes = _estado(raiz)
    assert [st for _, _, st in VH.verificar(raiz)] == ["DIFERENTE"]
    assert VH.main(["x", str(raiz)]) == 1
    assert _estado(raiz) == antes                           # nao "conserta" o arquivo divergente


def test_arquivo_ausente_e_reportado_e_nao_criado(tmp_path):
    raiz = _mini_repo(tmp_path)
    (raiz / "data_assistente" / "derivados" / "chunks_exemplos.json").unlink()
    assert [st for _, _, st in VH.verificar(raiz)] == ["AUSENTE"]
    assert not (raiz / "data_assistente" / "derivados" / "chunks_exemplos.json").exists()


def test_codigo_do_verificador_nao_contem_operacoes_de_escrita():
    src = (RAIZ / "scripts" / "verificar_hashes.py").read_text(encoding="utf-8")
    proibidos = {"write_text", "write_bytes", "unlink", "rename", "replace", "rmtree", "copy", "copyfile", "move", "mkdir", "touch", "remove", "dump"}
    chamadas = {n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "") for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call)}
    assert not (chamadas & proibidos)
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "open" or (isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "open"):
            modo = [a.value for a in list(n.args[1:2]) + [k.value for k in n.keywords if k.arg == "mode"] if isinstance(a, ast.Constant)]
            assert all(set(str(m)) <= {"r", "b"} for m in modo)
    assert "chunks_exemplos" not in src.replace("chunks_exemplos.json\n", "") or "write" not in src.lower().replace("somente leitura", "")


@pytest.mark.skipif(not (RAIZ / "docs" / "assistente" / "diagnostico_4_4" / "hashes_referencia_44.json").exists(), reason="manifesto 4.4 ausente")
def test_repositorio_real_confere_e_chunks_exemplos_continua_com_o_hash_registrado():
    alvo = RAIZ / "data_assistente" / "derivados" / "chunks_exemplos.json"
    antes = (alvo.stat().st_mtime_ns, hashlib.sha256(alvo.read_bytes()).hexdigest())
    assert VH.main(["x"]) == 0
    assert (alvo.stat().st_mtime_ns, hashlib.sha256(alvo.read_bytes()).hexdigest()) == antes
    ref = json.loads((RAIZ / "docs" / "assistente" / "diagnostico_4_4" / "hashes_referencia_44.json").read_text(encoding="utf-8"))
    assert ref["arquivos"]["data_assistente/derivados/chunks_exemplos.json"] == antes[1]
