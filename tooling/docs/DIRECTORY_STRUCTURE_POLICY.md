# Evoki V3.0 Directory Structure Policy

## Regel: Keine gemischten Verzeichnisse

**Jedes Verzeichnis darf NUR eines enthalten:**
1. **Nur Unterordner** (Organisationsverzeichnis)
2. **Nur Dateien** (Leaf-Verzeichnis)

**Ausnahmen (erlaubt):**
- Root-Level: `README.md`, `ARCHITECTURE.txt`, `.geminiignore`
- Whitelisted Folders (siehe `tooling/scripts/cli/enforce_structure.py`)

---

## Regel: Trennung von App-Code und Tools

| Bereich | Pfad | Inhalt |
|---------|------|--------|
| **App** | `app/` | Production Artifacts (State/UI/Memory) |
| **Tooling** | `tooling/` | Development Logic, Automation, Scripts |

**Niemals:** Tool-Scripts in `app/` ablegen.

---

## Aktuelle Struktur (V5.1)

```
app/
├── interface/            # Frontend (React/Vite)
└── deep_earth/           # Memory (SQLite Layers)

tooling/
├── data/                 # Runtime State
│   ├── synapse/          # Status/Logs
│   └── db/               # Context DBs
│
├── docs/                 # Documentation
│   └── knowledge/
│
├── scripts/              # Logic Engine
│   ├── automation/       # Core Logic (Synapse Chain)
│   ├── cli/              # Admin Tools
│   ├── daemons/          # Watchers
│   ├── helpers/          # Utilities
│   ├── launchers/        # .bat Files
│   └── servers/          # MCP Server
│
└── tests/                # Pytest Suite
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
| Launchers | `tooling/scripts/launchers/` |
| Core-Logik | `tooling/scripts/automation/` |
| UI-Templates | `tooling/scripts/ui/` |

---

## Automatische Durchsetzung

Verwende das Tool `enforce_structure.py` zur Prüfung:
`python tooling/scripts/cli/enforce_structure.py check`

---

## Regel 4: copilot-instructions.md aktuell halten

**Pflicht:** Bei jeder strukturellen Änderung MUSS `.github/copilot-instructions.md` aktualisiert werden.

**Version:** 3.0 (V5.1 Refactor)
**Datum:** 2026-01-13 (Phase 3)
