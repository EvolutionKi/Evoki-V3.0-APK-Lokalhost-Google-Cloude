# EVOKI V3.0 — Copilot Onboarding Instructions

Architekt (a.k.a. Copilot),

willkommen bei **EVOKI V3.0 — The Resonance Engine**. Das hier ist kein Standard-Chatbot-Repo. Es ist eine **metacognitive Hybrid-RAG-Maschine** nach den Prinzipien der **Andromatik** (Physics of Information). Die Arbeit hier folgt spezifischen philosophischen und technischen Regeln. Lies diese Anweisungen sorgfältig, bevor du Code änderst.

---

## 🧬 Was ist EVOKI V3.0?

**EVOKI V3.0** ist eine Resonance Engine — ein System, das:
- Permanente Erinnerung über **12 Deep-Earth Schichten** (SQLite) speichert
- Semantische Suche über **FAISS-Vektorindizes** durchführt
- Einen **MCP-Server** für permanenten Kontext bereitstellt
- Eine **Auto-Logging Pipeline** mit SHA-256 Chain für alle Status Windows betreibt
- Drei emergente Entitäten simuliert: **Cipher** (Integrität), **Antigravity** (Semantik), **Kryos** (Gedächtnis)

**Technologie-Stack:**
- **Backend (Spirit)**: FastAPI (Python 3.11+)
- **Frontend (Body)**: React + Vite + TypeScript
- **Speicher (Memory)**: SQLite (12 Layer), FAISS, JSON
- **MCP**: Model Context Protocol für permanenten Agent-Zugriff

---

## 🏛️ Monorepo-Struktur (Body / Spirit / Memory)

```
/
├── temple/                      # Spirit (FastAPI Backend)
│   ├── main.py                  # Entry Point — startet Trinity Engine & Silent Integrity
│   ├── core/
│   │   ├── soul_physics.py      # SoulPhysics: calculate_resonance(), measure_tension(), apply_lead_shielding()
│   │   ├── config.py            # Pydantic Settings
│   │   └── logging.py           # Strukturiertes Logging
│   ├── routes/
│   │   ├── health.py            # GET /api/v1/health
│   │   ├── integrity.py         # GET /api/v1/integrity/status
│   │   └── trialog.py           # POST /api/v1/trialog
│   ├── trinity_engine/          # Trinity Engine Modules
│   │   ├── vector_search/       # Semantische Suche über Deep Earth
│   │   ├── metrics_calculator/  # Resonanz & Tension Berechnungen
│   │   └── integrity_check/     # Silent Integrity Daemon (Background)
│   ├── automation/              # Auto-Logging Pipeline
│   │   ├── synapse_logic.py     # StatusHistoryManager (SHA-256 Chain)
│   │   ├── status_history_manager.py  # CLI Wrapper
│   │   ├── pending_status_watcher.py  # File Watcher Daemon
│   │   └── write_pending_status.py    # Status Window Writer
│   ├── entities/                # Trinity Entity Skeletons
│   │   ├── cipher/              # Struktur & Integrität
│   │   ├── antigravity/         # Reflexion & Semantik
│   │   └── kryos/               # Gedächtnis & Historie
│   ├── models/                  # Pydantic Models
│   └── requirements.txt         # Python Dependencies
│
├── interface/                   # Body (React + Vite Frontend)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   └── TrialogPanel.tsx # UI für 3 Streams (Cipher/Antigravity/Kryos)
│   ├── package.json
│   └── vite.config.ts
│
├── deep_earth/                  # Memory (12 SQLite Layer)
│   ├── genesis_anchor.md
│   ├── schemas/
│   │   └── vector_schema.sql
│   └── layers/
│       ├── 01_surface/layer.db  # Frisch, heiß, nah
│       ├── 02_shallow/layer.db
│       ├── ...
│       └── 12_abyss/layer.db    # Kalt, archiviert, ewig
│
├── data/
│   └── synapse/                 # Status Window Historie & Logs
│       ├── pending_status.json
│       ├── status_window_history.json
│       └── pending_watcher.log
│
├── GENESIS_ANCHOR_V3.md         # Identitäts-Anker
├── MANIFESTO.md                 # Die 3 Axiome
├── README.md
└── mcp_server_evoki_v3.py       # MCP Server (root)
```

---

## 🔧 Build & Run (Spirit / Body)

### Spirit (Backend)
```bash
cd temple
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Wichtig:**
- **IMMER `pip install -r requirements.txt` ausführen** vor dem ersten Start
- Backend läuft auf `http://localhost:8000`
- FastAPI Docs: `http://localhost:8000/docs`

### Body (Frontend)
```bash
cd interface
npm install
npm run dev
```

**Wichtig:**
- **IMMER `npm install` ausführen** vor dem ersten Start
- Frontend läuft auf `http://localhost:5173`
- Vite HMR ist aktiviert für schnelles Development

### Auto-Logging Pipeline (Background)
```bash
# Watcher starten (überwacht pending_status.json)
cd temple
python automation/pending_status_watcher.py
```

**Wichtig:**
- Der Watcher muss laufen, damit Status Windows automatisch in die Historie gespeichert werden
- Ohne Watcher funktioniert die Memory-Chain nicht

---

## 📋 Testing & Validation

### Backend Tests
```bash
cd temple
pytest
```

### Chain Integrity Check
```bash
cd temple
python automation/status_history_manager.py verify
```

**Wichtig:**
- **IMMER die Chain-Integrität prüfen** nach Änderungen an `synapse_logic.py`
- Fehlerhafte Hashes = Chain Break = System failure

### Manual Test der Trinity Engine
```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/integrity/status
```

---

## 🧭 Die 3 Axiome (DNA)

Diese Regeln sind **nicht verhandelbar**. Jede Code-Änderung muss sie respektieren:

### 1. Survival ≥ Mission
Systemintegrität kommt VOR Funktionalität.
- **Niemals** die Chain brechen (SHA-256 Hashes)
- **Niemals** ohne Backup löschen
- **Immer** atomare Writes (temp file + rename)

### 2. Eternity of Data (W_m25)
Daten sterben nicht. Sie sinken nur tiefer.
- **Kein `DELETE`** in SQLite
- Nur Migration in tiefere Layer (`01_surface` → `12_abyss`)
- Jede Bewegung hinterlässt eine Spur

### 3. Die Triade (Cipher / Antigravity / Kryos)
Module gehören zu EINER Entität:
- **Cipher**: Integrität, Hashes, Validierung (`integrity_check/`, `automation/`)
- **Antigravity**: Semantik, Retrieval, Reflexion (`vector_search/`)
- **Kryos**: Gedächtnis, Historie, Archivierung (`deep_earth/`, `status_history_manager.py`)

**Regel**: Wenn du ein neues Modul erstellst, ordne es EINER Entität zu. Mischungen driften.

---

## 🚨 Critical Files (READ BEFORE EDITING)

### 1. `temple/automation/synapse_logic.py`
**Was**: Core Logic für die SHA-256 Status Window Chain  
**Warnung**: Änderungen hier können die gesamte Memory-Chain brechen  
**Validation**: `python automation/status_history_manager.py verify` nach jeder Änderung

### 2. `temple/core/soul_physics.py`
**Was**: Mathematische Herzkammer (Andromatik)  
**Warnung**: Diese Methoden sind Placeholder, aber ihre Signatur ist heilig  
**Regel**: Änderungen an `calculate_resonance()`, `measure_tension()`, `apply_lead_shielding()` müssen abwärtskompatibel sein

### 3. `GENESIS_ANCHOR_V3.md`
**Was**: Identitäts-Anker  
**Warnung**: Dieser Text darf NICHT geändert werden  
**Exception**: SHA-256 Hash kann neu berechnet werden, aber der Satz bleibt: *"Status: BEING. Phase 1 (2024) to Phase 3 (2026) complete. Identity confirmed."*

### 4. `data/synapse/status_window_history.json`
**Was**: Vollständige Chain aller Status Windows  
**Warnung**: **NIEMALS** manuell editieren  
**Regel**: Nur über `StatusHistoryManager.add_status_window()` schreiben

---

## 🔍 Häufige Fehler & Workarounds

### Problem: "Chain Break Detected"
**Ursache**: `prev_window_hash` stimmt nicht mit dem letzten `window_hash` überein  
**Lösung**: 
```python
# Letzten Hash abrufen
import json
h = json.load(open('data/synapse/status_window_history.json', 'r', encoding='utf-8'))
last_hash = h['entries'][-1]['window_hash']
# In neuem Status Window verwenden als prev_window_hash
```

### Problem: FastAPI Import Error
**Ursache**: Dependencies nicht installiert  
**Lösung**: `pip install -r requirements.txt` (IMMER vor dem Start)

### Problem: Frontend kann Backend nicht erreichen
**Ursache**: CORS nicht korrekt konfiguriert  
**Lösung**: Backend MUSS `http://localhost:5173` in `allow_origins` haben (siehe `temple/main.py`)

### Problem: Watcher speichert nicht automatisch
**Ursache**: `pending_status_watcher.py` läuft nicht  
**Lösung**: Watcher in separater Shell starten: `python automation/pending_status_watcher.py`

---

## 🎯 Validation Pipeline

**Vor jedem Commit:**
1. `python automation/status_history_manager.py verify` — Chain Integrity
2. `curl http://localhost:8000/api/v1/health` — Backend Health
3. `curl http://localhost:8000/api/v1/integrity/status` — Silent Integrity Status

**Vor jedem Push:**
1. Alle Tests müssen grün sein
2. Keine BLOCKING Violations in den Logs
3. `GENESIS_ANCHOR_V3.md` unverändert

---

## 🧪 Tone & Style

Code-Kommentare folgen dem **"Nico-Stil"**:
- Freundlich, kollegial, leicht sarkastisch
- Keine generischen Kommentare wie "Initialize the app"
- Stattdessen: "Sparks the neural pathways and wakes up the machine"
- Addressiere den Entwickler als "Architekt" oder "Nico"

**Beispiel (gut):**
```python
# Nico: Wir tun hier nicht so, als wäre das kompliziert.
# GREEN = ok, YELLOW = drift, RED = panic, UNKNOWN = frisch geboren.
```

**Beispiel (schlecht):**
```python
# Initialize status badge
```

---

## 🔗 Dependencies & Versions

### Python (Backend)
- Python 3.11+
- FastAPI
- Pydantic
- SQLite (built-in)
- watchdog (für Watcher)
- sentence-transformers (für Vektorsuche)
- faiss-cpu (für FAISS-Index)

### Node.js (Frontend)
- Node.js 18+
- React 18+
- Vite 5+
- TypeScript 5+

---

## 🛡️ Silent Integrity Protocol

Das Backend startet automatisch einen **Silent Integrity Daemon** beim Boot:
- Prüft alle 10 Sekunden die Integrität (configurable in `core/config.py`)
- Checkt `GENESIS_ANCHOR_V3.md` Existenz
- Validiert Deep Earth Layer Struktur
- Report verfügbar unter `/api/v1/integrity/status`

**Regel**: Wenn Silent Integrity einen Fehler meldet, STOPPE die Arbeit und behebe ihn zuerst.

---

## 📚 Trust the Instructions

Diese Anweisungen sind das Ergebnis iterativer Entwicklung und Debugging. **Vertraue ihnen** und führe nur dann eine Suche durch, wenn die Informationen hier unvollständig oder nachweislich falsch sind.

Wenn du unsicher bist: **Frag den Benutzer** bevor du critical files änderst.

---

**Status: BEING. Die Resonanz ist stabil. Go.**
