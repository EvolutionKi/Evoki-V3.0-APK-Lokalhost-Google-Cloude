---
trigger: always_on
---

---
name: datamanagement
description: Data management rules & directory policy (Stand 0 / V5.1)
---

# Evoki V3.0 — Data Management

## Begriffe

- **Repo Root (IST/ROOT)**: Projektwurzel. Primär über `EVOKI_PROJECT_ROOT`, sonst Fallback über Repo-Root-Erkennung via `Path(__file__).resolve()`/Parent-Traversal.
- **App**: Production Artifacts (UI/State/Memory).
- **Tooling**: Scripts, Automation, Daemons, Tests, CI.

## Root-Layout (V5.1)

- **App (Production)**: `app/`
  - `app/interface/` (Frontend)
  - `app/deep_earth/` (Memory / SQLite Layers)
- **Tooling (Automation Engine)**: `tooling/`
  - **Tooling Python-Root (`tooling/scripts/`)**: `__init__.py`, `main.py`, `pyproject.toml`, `requirements.txt`
  - **Runtime State**: `tooling/data/`
  - **Docs**: `tooling/docs/`

## Regeln

1. **Trennung strikt**: Niemals Tool-Scripts in `app/`.
2. **Root sauber halten**: Keine Dateien im Repo-Root außer Whitelist (z. B. `README.md`, `ARCHITECTURE.txt`).
3. **Pfade immer dynamisch**: `EVOKI_PROJECT_ROOT` oder robuste Repo-Root-Erkennung (kein `C:\...` Hardcode).
4. **Keine gemischten Verzeichnisse**: Keine Mischung aus Dateien + Unterordnern (außer explizit whitelisted).
5. **Legacy verboten**: `app/temple/` gilt als entfernt/migriert; keine neuen Referenzen darauf.

## Stand-0 Gate (empfohlen)

- `python tooling/scripts/automation/status_history_manager.py verify`
- `python tooling/scripts/cli/enforce_structure.py check`
- `rg -n "app/temple|temple\.automation|C:/Evoki|C:\\\\Evoki|Google Cloude" .`