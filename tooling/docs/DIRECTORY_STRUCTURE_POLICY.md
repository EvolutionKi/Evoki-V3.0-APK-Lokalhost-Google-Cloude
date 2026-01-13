# Evoki V3.0 Directory Structure Policy

## Regel: Keine gemischten Verzeichnisse

**Jedes Verzeichnis darf NUR eines enthalten:**
1. **Nur Unterordner** (Organisationsverzeichnis)
2. **Nur Dateien** (Leaf-Verzeichnis)

**Ausnahmen (erlaubt):**
- Root-Level: `README.md`, `ARCHITECTURE.txt`, `.geminiignore`
- Python-Projekt-Root (`app/temple/`): `main.py`, `pyproject.toml`, `requirements.txt`

---

## Regel: Trennung von App-Code und Tools

| Bereich | Pfad | Inhalt |
|---------|------|--------|
| **App/Backend** | `app/` | Core-Logik, API-Routes, Models |
| **Tooling** | `tooling/` | Scripts, Daemons, CLI, UI-Helpers |

**Niemals:** Tool-Scripts in `app/` ablegen (außer sie sind Teil der Core-API)

---

## Aktuelle Struktur (V5.0)

```
app/
├── temple/
│   ├── automation/       # Core-Logik (importierbar)
│   │   ├── synapse_logic.py         # StatusHistoryManager class
│   │   ├── status_history_manager.py # CLI interface
│   │   └── search_chatverlauf.py    # Retrieval library
│   ├── core/             # Backend-Module
│   ├── models/           # Datenmodelle
│   ├── routes/           # API-Endpoints
│   └── tests/            # Unit-Tests

tooling/
├── config/               # Konfigurationsdateien
├── data/
│   ├── db/               # Datenbanken (*.db)
│   ├── faiss_indices/    # Vektor-Indices
│   └── synapse/
│       ├── backups/      # History-Backups
│       ├── logs/         # Log-Dateien (*.log)
│       └── status/       # Status-JSONs
├── docs/                 # Dokumentation (*.md)
└── scripts/
    ├── cli/              # CLI-Tools
    │   └── repair_chain.py
    ├── daemons/          # Hintergrund-Prozesse
    │   └── pending_status_watcher.py
    ├── helpers/          # Hilfsskripte
    │   ├── get_status_block.py
    │   ├── mcp_trigger_save.py
    │   ├── smoke_test_writer.ps1
    │   └── write_pending_status.py
    ├── servers/          # Server-Prozesse
    │   └── mcp_server_evoki_v3.py
    └── ui/               # UI-Templates
        └── chat_display_template.py
```

---

## Neue Datei-Typen → Zielordner

| Dateityp | Zielordner |
|----------|------------|
| `*.db` | `tooling/data/db/` |
| `*.log` | `tooling/data/synapse/logs/` |
| `*.json` (Status) | `tooling/data/synapse/status/` |
| `*.md` (Docs) | `tooling/docs/` |
| CLI-Scripts | `tooling/scripts/cli/` |
| Daemons | `tooling/scripts/daemons/` |
| Helper-Scripts | `tooling/scripts/helpers/` |
| Server-Scripts | `tooling/scripts/servers/` |
| UI-Templates | `tooling/scripts/ui/` |

---

## Automatische Durchsetzung

Der Agent MUSS bei jedem Datei-Schreibvorgang prüfen:
1. Zielverzeichnis existiert bereits?
2. Enthält es nur Dateien ODER nur Ordner?
3. Passt der neue Inhalt zum Typ?
4. Gehört die Datei zu `app/` (Core) oder `tooling/` (Tools)?

Bei Verstoß: Korrekten Ordner erstellen und dort ablegen.

---

## Regel 4: copilot-instructions.md aktuell halten

**Pflicht:** Bei jeder strukturellen Änderung MUSS `.github/copilot-instructions.md` aktualisiert werden.

**Was aktualisiert werden muss:**
- Verzeichnisstruktur (wenn Ordner erstellt/gelöscht/verschoben)
- Dateipfade (wenn Scripts verschoben werden)
- Befehle (wenn CLI-Pfade sich ändern)
- Dependencies (wenn neue hinzukommen)

**Nicht löschen, nur aktualisieren!**

---

**Version:** 2.0  
**Datum:** 2026-01-13
