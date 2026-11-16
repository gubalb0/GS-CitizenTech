"""Testa a MECANICA do avaliador independente com um CSV minusculo gerado no teste.
NAO e validacao do modelo: os textos abaixo existem so para exercitar lacre, recusas e relatorio."""
import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from citizentech import config  # noqa: E402
from validacao_independente import avaliar as av  # noqa: E402

pytestmark = pytest.mark.skipif(not config.ARQ_MODELO.exists(), reason="rode main.py/auditoria antes (modelo salvo)")


@pytest.fixture
def amb(tmp_path, monkeypatch):
    monkeypatch.setattr(av, "LACRE", tmp_path / "LACRE.json")
    monkeypatch.setattr(av, "REGISTRO", tmp_path / "reg.jsonl")
    monkeypatch.setattr(av, "PASTA", tmp_path)
    csvp = tmp_path / "c.csv"
    with csvp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id_texto", "texto", "rotulo_final", "urgencia_clinica", "ambigua"])
        w.writerow(["a1", "quero marcar consulta", "agendamento_consulta", "nao", "nao"])
        w.writerow(["a2", "estou com dor forte no peito", "sintomas_urgentes", "sim", "nao"])
        w.writerow(["a3", "assunto de outro orgao qualquer", "fora_do_escopo", "nao", "sim"])
    return csvp


def test_fluxo_lacre_avaliacao_e_recusas(amb, tmp_path):
    av.main(["--lacrar", "--conjunto", str(amb), "--custodiante", "teste"])
    with pytest.raises(SystemExit):  # nao pode lacrar duas vezes
        av.main(["--lacrar", "--conjunto", str(amb), "--custodiante", "teste"])
    av.main(["--avaliar", "--conjunto", str(amb)])
    rel = json.loads(next(tmp_path.glob("relatorio_*.json")).read_text(encoding="utf-8"))
    assert rel["status_do_relatorio"].startswith("EXPLORATORIO")  # amostra minuscula
    assert rel["n_total"] == 3
    with pytest.raises(SystemExit):  # segunda avaliacao recusada
        av.main(["--avaliar", "--conjunto", str(amb)])
    av.main(["--avaliar", "--conjunto", str(amb), "--repetir", "--justificativa", "teste da mecanica"])


def test_recusa_se_conjunto_mudou(amb):
    av.main(["--lacrar", "--conjunto", str(amb), "--custodiante", "t"])
    amb.write_text(amb.read_text(encoding="utf-8") + "a4,texto novo qualquer,vacinacao,nao,nao\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        av.main(["--avaliar", "--conjunto", str(amb)])


def test_rotulo_invalido_rejeitado(amb):
    amb.write_text(amb.read_text(encoding="utf-8").replace("vacinacao", "x").replace("agendamento_consulta", "inventado"), encoding="utf-8")
    with pytest.raises(SystemExit):
        av.main(["--lacrar", "--conjunto", str(amb), "--custodiante", "t"])
