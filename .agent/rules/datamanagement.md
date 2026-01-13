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
- Tooling Python-Root (`tooling/scripts/`): `__init__.py`, `main.py`, `pyproject.toml`, `requirements.txt`

Regel: Trennung von App-Code und Tools
Niemals:** Tool-Scripts in `app/` ablegen (auÃŸer sie sind Teil der Core-API)

Automatische Durchsetzung

Der Agent MUSS bei jedem Datei-Schreibvorgang prÃ¼fen:
1. Zielverzeichnis existiert bereits?
2. EnthÃ¤lt es nur Dateien ODER nur Ordner?
3. Passt der neue Inhalt zum Typ?
4. GehÃ¶rt die Datei zu `app/` (Core) oder `tooling/` (Tools)?

Bei VerstoÃŸ: Korrekten Ordner erstellen und dort ablegen.

Regel 4: copilot-instructions.md aktuell halten

Pflicht:** Bei jeder strukturellen Ã„nderung MUSS `.github/copilot-instructions.md` aktualisiert werden.

Nicht lÃ¶schen, nur aktualisieren!**

