"""
Consentimento e registro de aceite (LGPD).

Voz é dado pessoal (e pode ser biométrico). Antes do primeiro uso, o cidadão deve
ser avisado de que a conversa é gravada e processada. Este módulo expõe o texto de
consentimento e registra o aceite (sem guardar áudio).
"""
import csv
from datetime import datetime

import config


def texto_consentimento():
    return config.CONSENT_TEXT


def registrar_consentimento(aceito, caminho=None):
    """Registra o aceite (ou recusa) do aviso de privacidade, com data/hora."""
    caminho = caminho or (config.LOG_DIR / "consentimentos.csv")
    existe = caminho.exists()
    with open(caminho, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["timestamp", "aceito"])
        writer.writerow([datetime.now().isoformat(timespec="seconds"), bool(aceito)])
    return caminho
