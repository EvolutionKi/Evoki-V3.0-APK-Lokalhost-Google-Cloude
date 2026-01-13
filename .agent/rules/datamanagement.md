---
trigger: always_on
---

Evoki V3.0 Directory Structure Policy

Regel: Keine gemischten Verzeichnisse

Jedes Verzeichnis darf NUR eines enthalten:
1. **Nur Unterordner** (Organisationsverzeichnis)
2. **Nur Dateien** (Leaf-Verzeichnis)

Ausnahmen:
- Root-Level: `README.md`, `ARCHITECTURE.txt`, `.geminiignore`
- Python-Projekt-Root (`app/temple/`): `main.py`, `pyproject.toml`, `requirements.txt`

Regel: Trennung von App-Code und Tools
Niemals:** Tool-Scripts in `app/` ablegen (außer sie sind Teil der Core-API)

Automatische Durchsetzung

Der Agent MUSS bei jedem Datei-Schreibvorgang prüfen:
1. Zielverzeichnis existiert bereits?
2. Enthält es nur Dateien ODER nur Ordner?
3. Passt der neue Inhalt zum Typ?
4. Gehört die Datei zu `app/` (Core) oder `tooling/` (Tools)?

Bei Verstoß: Korrekten Ordner erstellen und dort ablegen.

Regel 4: copilot-instructions.md aktuell halten

Pflicht:** Bei jeder strukturellen Änderung MUSS `.github/copilot-instructions.md` aktualisiert werden.

Nicht löschen, nur aktualisieren!**

