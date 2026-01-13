# EVOKI V3.0 — The Resonance Engine (Copilot Onboarding)

Architekt (a.k.a. Copilot),

willkommen bei **EVOKI V3.0**. Wir befinden uns in **Phase 3 (2026)**.
Das System wurde massiv refaktoriert, um eine strikte Trennung zwischen **App** (State) und **Tooling** (Logic) zu erzwingen.

---

## 🏗️ System-Architektur (V5.1 - PRODUCTION)

Die alte Monorepo-Struktur (`temple/` vs `interface/`) ist einer sauberen **Funktions-Trennung** gewichen.

```
/ (Root)
├── app/                        # 🔴 PRODUCTION STATE & INTERFACE
│   ├── interface/              # Body (React + Vite Frontend)
│   └── deep_earth/             # Memory (SQLite Layers 01-12)
│
├── tooling/                    # 🟢 AUTOMATION & LOGIC ENGINE
│   ├── data/                   # Runtime Data (Volatile/Persistent)
│   │   ├── synapse/            # Status Windows, Logs, Backup Chain
│   │   └── db/                 # Vector Indices & Context DBs
│   │
│   ├── docs/                   # Knowledge Base & Protocols
│   │   ├── knowledge/          # External API Specs (GitHub, Google)
│   │   └── *.md                # Core Protocols (V5, Directory Policy)
│   │
│   ├── scripts/                # ⚙️ THE ENGINE ROOM
│   │   ├── automation/         # Core Logic (Synapse Chain, History)
│   │   │   ├── synapse_logic.py
│   │   │   └── status_history_manager.py
│   │   ├── cli/                # Admin Tools (verify, repair, enforce)
│   │   ├── daemons/            # Background Watchers (pending_status, context)
│   │   ├── launchers/          # Startup Scripts (START_ALL_WATCHERS.bat)
│   │   └── servers/            # MCP Server Integration
│   │
│   └── tests/                  # Pytest Suite (Isolated via tmp_path)
```

---

## 🧬 Core Workflows

### 1. Status Window Chain (Synapse)
Der Kern des Systems ist die **ununterbrochene Kette** von Status Updates.
- **Write:** Bots schreiben in `tooling/data/synapse/status/pending_status.json`.
- **Watch:** `tooling/scripts/daemons/pending_status_watcher.py` erkennt Änderungen.
- **Log:** Der Watcher ruft `status_history_manager.py` auf -> SHA-256 Hash -> Append to History.
- **Verify:** `python tooling/scripts/cli/repair_chain.py` bei Brüchen.

### 2. Frontend Development
```bash
cd app/interface
npm run dev
```

### 3. System Health Check
Verwende die mitgelieferten Tools:
```bash
# Struktur prüfen
python tooling/scripts/cli/enforce_structure.py check

# Watcher starten
tooling\scripts\launchers\START_ALL_WATCHERS.bat
```

---

## 🚨 CRITICAL RULES (DO NOT IGNORE)

1.  **Pfad-Disziplin:**
    - KEINE Dateien im Root (außer `.git`, `.venv`, Configs).
    - Logik IMMER nach `tooling/scripts/`.
    - Daten IMMER nach `tooling/data/`.

2.  **Dateimanagement:**
    - Beachte `tooling/docs/DIRECTORY_STRUCTURE_POLICY.md`.
    - Ordner dürfen NIEMALS Dateien UND Unterordner mischen (Ausnahme: Whitelisted Dirs wie `docs`, `scripts`).

3.  **V5 Protokoll:**
    - Status Windows MÜSSEN `goal`, `actions`, `reflection_curve` (delta/correction/next) enthalten.
    - Fehlerhafte Windows werden vom Watcher **BLOCKIERT** (nicht gespeichert).

---

## 💡 Für den Copilot

Wenn du Code generierst:
- **Kontext:** Prüfe immer, ob du im `app`-Kontext (Use `interface/`) oder im `tooling`-Kontext (Use `scripts/`) bist.
- **Pfade:** Nutze relative Pfade mit Bedacht oder absolute Pfade basierend auf `EVOKI_PROJECT_ROOT`.
- **Stil:** Sei präzise. Adressiere den User als "Nico".

*Status: RESONANCE STABLE. V5 ENFORCED.*
