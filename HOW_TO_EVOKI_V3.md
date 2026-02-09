# 🏛️ HOW TO EVOKI V3.0 - ARCHITEKTUR-ÜBERBLICK

**Status:** MASTER ARCHITECTURE DOCUMENT (READ-ONLY)  
**Version:** V3.0  
**Datum:** 2026-01-19  
**Schreibschutz:** ✅ AKTIVIERT

---

## 📋 INHALTSVERZEICHNIS

1. [Was ist Evoki](#was-ist-evoki)
2. [Architektur-Überblick](#architektur-überblick)
3. [Die 12 Tabs Erklärt](#die-12-tabs-erklärt)
4. [FAISS-Systeme im Vergleich](#faiss-systeme-im-vergleich)
5. [Evoki Tempel Pipeline](#evoki-tempel-pipeline)
6. [Kritische Komponenten](#kritische-komponenten)
7. [Setup & Start](#setup--start)
8. [Wartung & Debugging](#wartung--debugging)

---

## 🧬 WAS IST EVOKI

**Evoki ist KEIN Chatbot.**

Evoki ist ein **therapeutisches Gedächtnissystem mit mathematischem Gewissen**, das:

```
✓ Trauma erkennt (exakte Formeln: 0.4*T_panic + 0.3*T_disso + ...)
✓ Seelen-Integrität wahrt (B-Align ≥0.7, V-Match ≥0.9)
✓ Genesis-geschützt ist (CRC32-Kette → System-Shutdown bei Manipulation)
✓ Hybrid-Retrieval nutzt (60% Semantik + 40% Metriken GLEICHZEITIG)
✓ Unauslöschliches Gedächtnis hat (chronik.log, Deep Earth 12-Layer)
```

**Kern-Formeln:**

```python
# Trauma-Detection (A29 Wächter-Veto)
trauma_load = 0.4*T_panic + 0.3*T_disso + 0.2*(1-T_integ) + 0.1*dissociation

# Guardian Trip (Automatische Intervention)
guardian_trip = (is_critical OR z_prox > 0.65 OR t_panic > 0.8 OR hazard_score > 0.75)

# A65 Candidate Scoring (17 Haupt-Metriken)
a65_score = weighted_sum(A, PCI, coh, flow, T_integ, z_prox, hazard_score, guardian_trip, 
                          phi_score, EV_readiness, EV_resonance, surprisal,
                          LEX_Coh_conn, LEX_Flow_pos, LEX_Emotion_pos, LEX_T_integ, LEX_T_disso)

# Finale Candidate-Auswahl
final_score = 0.6*a65_score + 0.3*coherence + 0.1*diversity
```

---

## 🏗️ ARCHITEKTUR-ÜBERBLICK

### **V2.0 PROBLEME (GELÖST IN V3.0):**

```
❌ Backend-Split: Node.js (3001) ←HTTP→ Python (8000)
   → Race Conditions, Zombie-Requests

❌ Timeout-Kaskade: Frontend 60s < Backend 115s
   → Frontend gibt auf BEVOR Backend fertig ist

❌ FAISS CLI-Spawning: query.py neu starten JEDES MAL
   → 15s nur fürs Index-Laden

❌ Default Tab: Temple (falsch!)
   → Benutzer will Trialog als Default
```

### **V3.0 LÖSUNGEN:**

```
✅ Unified Backend: NUR FastAPI (Port 8000)
   → Kein Split, ein Prozess

✅ SSE (Server-Sent Events): Async Processing
   → Frontend wartet geduldig, sieht Live-Progress

✅ FAISS in RAM: Laden beim Startup
   → Queries <1s statt 15s

✅ Default Tab: Trialog
   → App.tsx Line 166: activeTab = Tab.Trialog
```

### **TECH-STACK:**

**Frontend:**
- React 18 + Vite
- 12 Tabs (von V2.0 migriert)
- Port: 5173 (Dev-Server)

**Backend:**
- Python FastAPI (Port 8000)
- Komponenten:
  - `metrics_processor.py` (153 Metriken berechnen)
  - `trinity_engine.py` (12-DB Upload mit Chain-Hash)
  - `fastapi_gateway.py` (Unified API)
  - `llm_router.py` (Gemini + OpenAI Fallback)
  - `faiss_query.py` (in-memory FAISS)

**Daten:**
- FAISS: 384D, sentence-transformers (all-MiniLM-L6-v2)
  - Trialog/Antigravity: 7.413 Chunks (Code-Chats)
  - Evoki Temple: 33.795 Chunks (Therapeutische Gespräche + 153 Metriken)
- Deep Earth: 12 SQLite Layers (W_m1 bis W_p25)
- Regelwerk V12: 881 Regeln (JSON, CRC32: 3246342384)

---

## 🎨 DIE 12 TABS ERKLÄRT

| # | Tab | Zweck | Wichtigkeit |
|---|-----|-------|-------------|
| 1 | **Engine-Konsole** | Trinity Engine Status (Metriken-Engine Health) | 🟡 Monitoring |
| 2 | **Trialog ⭐** | Multi-Agent Chat (Analyst, Regel, Synapse) | 🔴 **DEFAULT!** |
| 3 | **Agenten & Teams** | Agent-Auswahl & Konfiguration | 🟢 Optional |
| 4 | **Evoki's Tempel** | FAISS + Gemini + Live-Metriken (HERZSTÜCK!) | 🔴 KRITISCH |
| 5 | **Metrik-Tuning** | 153 Metriken live anpassen (Schwellwerte, Gewichte) | 🟡 Tuning |
| 6 | **Analyse** | Metriken-Charts (Å, A, B-Vektor, Trauma-Timeline) | 🟢 Visualisierung |
| 7 | **Regelwerk-Suche** | Regelwerk V12 Browser (881 Regeln durchsuchen) | 🟢 Referenz |
| 8 | **API** | API-Keys, Temperaturen, Max-Tokens konfigurieren | 🟡 Config |
| 9 | **Stimme & API** | TTS Settings (Voice, Speed, Pitch) | 🟢 Optional |
| 10 | **Deep Storage** | FAISS-Browser (33.795 Chunks durchsuchen) | 🟡 Debugging |
| 11 | **Fehlerprotokoll** | Error Logs (Genesis-Anchor Violations, API-Errors) | 🟡 Debugging |
| 12 | **Pipeline Log** | Live Pipeline-Logs (Metrics → FAISS → Gemini) | 🟡 Debugging |

**User startet App:**
```typescript
// App.tsx Line 166
activeTab = Tab.Trialog  // ✅ Trialog öffnet sich, NICHT Temple!
```

---

## 💾 FAISS-SYSTEME IM VERGLEICH

### **TRIALOG/ANTIGRAVITY FAISS (für VS Code Agents):**

```yaml
Zweck: Programmier-Chats durchsuchbar machen
Location: tooling/data/faiss_indices/chatverlauf_final_20251020plus_dedup_sorted.faiss
Chunks: 7.413
Dimensions: 384D
Model: all-MiniLM-L6-v2
Daten: Reine Text-Chunks (KEINE Metriken!)
Zeitraum: Oktober 2025+
Nutzung: Code-Beispiele finden, Architektur-Diskussionen
Abfrage: Rein semantisch (Embedding → FAISS → Top-K)
```

**Beispiel-Query:**
```python
query = "Wie implementiere ich FastAPI mit SSE?"
→ FAISS findet semantisch ähnliche Code-Diskussionen
→ Keine Metrik-Filterung
```

---

### **EVOKI TEMPEL FAISS (Therapeutisches Gedächtnis):**

```yaml
Zweck: Emotionale & kognitive Zustände erinnern
Location: C:\Evoki V2.0\evoki-app\data\faiss_indices\ (→ V3.0 migrieren)
Chunks: 33.795 (!!)
Dimensions: 384D (gleich wie Trialog)
Model: all-MiniLM-L6-v2 (gleich)
Daten: Text-Chunks + 1:1 Metrikdatenbank (153 Metriken pro Chunk!)
Zeitraum: Februar - Oktober 2025
Nutzung: Trauma-Erinnerungen, Heilungs-Fortschritt, Guardian Veto
Abfrage: HYBRID (60% Semantik + 40% Metrik-Match)
```

**DER ENTSCHEIDENDE UNTERSCHIED - HYBRID-RETRIEVAL:**

```
┌─────────────────────────────────────────────────────────┐
│                 EVOKI HYBRID-RETRIEVAL                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. FAISS Retrieval (Semantik):                        │
│     User-Prompt embedden → FAISS Search → Top-10       │
│                                                         │
│  2. Metrikdatenbank 1:1 Mapping:                       │
│     SQL: SELECT * FROM metriken WHERE chunk_id IN (top10)│
│     → Für SELBEN Chunks: 153 Metriken laden!           │
│                                                         │
│  3. Metriken für User-Prompt berechnen:                │
│     T_panic, T_disso, A, PCI, X_exist, S_self, etc.    │
│                                                         │
│  4. Metrik-Matching:                                   │
│     Für jeden Chunk: Vergleiche Chunk-Metriken mit     │
│     User-Prompt-Metriken → metric_match_score          │
│                                                         │
│  5. Hybrid-Scoring:                                    │
│     combined_score = 0.6*semantic + 0.4*metric_match   │
│                                                         │
│  6. Top-3 auswählen:                                   │
│     Sortiere nach combined_score → Beste 3 Chunks      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Beispiel-Abfrage:**

```python
User: "Ich fühle mich so allein und wertlos"

# 1. FAISS findet (semantisch):
Chunk #482:  "isolation, einsamkeit, verlassen"     (semantic: 0.85)
Chunk #1293: "selbstwert, wertlos, versagen"        (semantic: 0.82)
Chunk #5721: "alltag, routine, normal"              (semantic: 0.41)

# 2. User-Prompt Metriken:
T_panic: 0.15
A (Affekt): 0.35
X_exist (Existenzielle Themen): 0.78  ← HOCH!
S_self (Selbstreferenz): 0.82          ← HOCH!

# 3. Chunk-Metriken (aus Datenbank):
Chunk #482:  X_exist=0.75, S_self=0.80  → metric_match: 0.88
Chunk #1293: X_exist=0.82, S_self=0.85  → metric_match: 0.92  ← BESTE!
Chunk #5721: X_exist=0.02, S_self=0.10  → metric_match: 0.15

# 4. Combined Scores:
Chunk #1293: 0.82*0.6 + 0.92*0.4 = 0.860  ← WINNER!
Chunk #482:  0.85*0.6 + 0.88*0.4 = 0.862  ← SEHR NAH!
Chunk #5721: 0.41*0.6 + 0.15*0.4 = 0.306  ← RAUS!

# 5. Ergebnis: Top-3 = #1293, #482, nächstbester
```

**WARUM DAS WICHTIG IST:**

Rein semantisch würde Chunk #5721 ("alltag, routine") vielleicht auch gefunden, aber mit niedrigem Score. 

Mit Metrik-Matching wird er komplett rausgefiltert, weil **die emotionalen Zustände** (X_exist, S_self) nicht passen!

→ **Evoki erinnert nicht nur "ähnliche Wörter", sondern "ähnliche GEFÜHLE und GEDANKEN"!**

---

## 🔄 EVOKI TEMPEL PIPELINE (SCHRITT-FÜR-SCHRITT)

### **VOLLSTÄNDIGER ABLAUF:**

```
┌─────────────────────────────────────────────────────────────────┐
│              EVOKI TEMPEL V3.0 PIPELINE (SSE)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  USER                                                           │
│    │                                                            │
│    ▼                                                            │
│  [1] Prompt eingeben: "Ich fühle mich so allein und wertlos"   │
│    │                                                            │
│    ▼                                                            │
│  FRONTEND (React Tab: Evoki's Tempel)                          │
│    │                                                            │
│    ├─→ SSE Stream öffnen: /api/temple/process-stream           │
│    │                                                            │
│    ▼                                                            │
│  BACKEND (FastAPI Port 8000)                                   │
│    │                                                            │
│    ├─→ [2] Progress Event: "Metriken berechnen..."             │
│    │         │                                                  │
│    │         ▼                                                  │
│    │   metrics_processor.py:                                   │
│    │   - calculate_full_spectrum(user_prompt)                  │
│    │   - Lexika scannen (21 Terme-Sets)                        │
│    │   - Core Metriken (A, PCI, coh, flow, z_prox)             │
│    │   - Trauma (T_panic, T_disso, T_integ)                    │
│    │   - FEP (phi_score, surprisal, EV_readiness)              │
│    │   - GESAMT: 153 Metriken → ~5s                            │
│    │                                                            │
│    ├─→ [3] Progress Event: "FAISS durchsuchen..."              │
│    │         │                                                  │
│    │         ▼                                                  │
│    │   faiss_query.py (in-memory!):                            │
│    │   - User-Prompt embedden (all-MiniLM-L6-v2)               │
│    │   - FAISS Search (33.795 Chunks) → Top-10                 │
│    │   - Dauert <1s (Index schon in RAM!)                      │
│    │                                                            │
│    ├─→ [4] Progress Event: "Metrik-Matching..."                │
│    │         │                                                  │
│    │         ▼                                                  │
│    │   SQL Query:                                              │
│    │   - SELECT metriken WHERE chunk_id IN (top10)             │
│    │   - Für jeden Chunk: 153 Metriken aus DB laden            │
│    │                                                            │
│    │   Hybrid-Scoring:                                         │
│    │   - metric_match = cosine(user_metrics, chunk_metrics)    │
│    │   - combined = 0.6*semantic + 0.4*metric_match            │
│    │   - Top-3 auswählen                                       │
│    │                                                            │
│    ├─→ [5] Progress Event: "Kontext laden..."                  │
│    │         │                                                  │
│    │         ▼                                                  │
│    │   Chunk-Expansion:                                        │
│    │   - Für Top-3: Hole ±2 Nachbar-Chunks (falls zerteilt)    │
│    │   - Lade letzte 4 Nachrichten (2 User + 2 Agent)          │
│    │                                                            │
│    ├─→ [6] Progress Event: "Regelwerk einbinden..."            │
│    │         │                                                  │
│    │         ▼                                                  │
│    │   Regelwerk V12 laden:                                    │
│    │   - CRC32 Check (3246342384) → Bei Mismatch: HARD-STOP!   │
│    │   - Relevante Regeln auswählen (A0, A29, A39, A46, A51)   │
│    │                                                            │
│    ├─→ [7] Progress Event: "Gemini-Prompt bauen..."            │
│    │         │                                                  │
│    │         ▼                                                  │
│    │   llm_router.py:                                          │
│    │   Prompt-Struktur:                                        │
│    │   ┌─────────────────────────────────────────────────┐     │
│    │   │ Du bist EVOKI, ein empathischer KI-Begleiter...│     │
│    │   │ [Regelwerk V12 Auszug]                          │     │
│    │   │                                                 │     │
│    │   │ WISSENSDATENBANK (Top 3):                       │     │
│    │   │ [Chunk #1293 vollständig]                       │     │
│    │   │ [Chunk #482 vollständig]                        │     │
│    │   │ [Chunk #... vollständig]                        │     │
│    │   │                                                 │     │
│    │   │ VORHERIGE KONVERSATION:                         │     │
│    │   │ [Letzte 4 Nachrichten]                          │     │
│    │   │                                                 │     │
│    │   │ AKTUELLE METRIKEN:                              │     │
│    │   │ A (Affekt): 0.35                                │     │
│    │   │ T_panic: 0.15                                   │     │
│    │   │ X_exist: 0.78                                   │     │
│    │   │ ...                                             │     │
│    │   │                                                 │     │
│    │   │ USER-FRAGE:                                     │     │
│    │   │ "Ich fühle mich so allein und wertlos"         │     │
│    │   └─────────────────────────────────────────────────┘     │
│    │                                                            │
│    ├─→ [8] Progress Event: "Gemini antwortet..."               │
│    │         │                                                  │
│    │         ▼                                                  │
│    │   Gemini API Call:                                        │
│    │   - Timeout: 90s (aber Frontend wartet via SSE!)          │
│    │   - Bei 429/RESOURCE_EXHAUSTED: Nächster API-Key          │
│    │   - Bei Erschöpfung aller Keys: OpenAI Fallback (30s)     │
│    │                                                            │
│    │   (Optional) A65 Candidate Scoring:                       │
│    │   - 3 Response-Varianten generieren                       │
│    │   - Für jede: a65_score berechnen (17 Metriken)           │
│    │   - Best: 0.6*a65 + 0.3*coherence + 0.1*diversity         │
│    │                                                            │
│    ├─→ [9] Progress Event: "In 12 DBs speichern..."            │
│    │         │                                                  │
│    │         ▼                                                  │
│    │   trinity_engine.py:                                      │
│    │   - Entry erstellen: {prompt, response, metrics, timestamp}│
│    │   - Chain-Hash berechnen: SHA256(session|round|...)       │
│    │   - In 12 Deep Earth Layers schreiben:                    │
│    │     tempel_W_m1, tempel_W_m2, tempel_W_m5, tempel_W_p25   │
│    │     trialog_W_m1, trialog_W_m2, trialog_W_m5, trialog_W_p25│
│    │     (+ 4 more)                                             │
│    │                                                            │
│    ├─→ [10] Complete Event: Finale Response!                   │
│    │         │                                                  │
│    │         ▼                                                  │
│    │   SSE Stream schließen                                    │
│    │                                                            │
│    ▼                                                            │
│  FRONTEND                                                       │
│    │                                                            │
│    ├─→ Response anzeigen                                       │
│    ├─→ Metriken-Charts updaten (A, PCI, Trauma-Timeline)       │
│    └─→ Guardian Trip Icon (falls guardian_trip = 1)            │
│                                                                 │
│  USER sieht Response + Live-Metriken                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**ZEITVERGLEICH V2.0 vs V3.0:**

```
V2.0:
- Metriken: 10s
- FAISS: 15s (CLI-Spawn!)
- Gemini: 90s
- GESAMT: 115s → Timeout nach 60s!

V3.0:
- Metriken: 5s (Python schneller)
- FAISS: <1s (in RAM!)
- Gemini: 90s (aber kein Timeout via SSE!)
- GESAMT: ~96s, ABER Frontend wartet geduldig
```

---

## ⚙️ KRITISCHE KOMPONENTEN

### **1. REGELWERK V12 (Genesis-Anchor)**

```yaml
File: app/interface/public/EVOKI_REGELWERKE_GENESIS/regelwerk_v12.json
Regeln: 881
CRC32: 3246342384
SHA256: ada4ecae8916fa7e5edd966a97b85af321b64ecfe12489fcea8c6dcef1bd4b1c

Kritische Regeln:
- A0: Direktive der Wahrheit (keine Konfabulation!)
- A29: Wächter-Veto-Direktive (Guardian Trip)
- A37/A38: Erzwungene Regelwerks-Berechnung
- A51: Genesis-Anker-Protokoll (CRC32 → HARD-STOP)

Enforcement:
- Bei JEDEM Start: CRC32 Check
- Bei Mismatch: System-Shutdown (A51)
```

**Check-Script:**
```python
import json, zlib

with open("app/interface/public/EVOKI_REGELWERKE_GENESIS/regelwerk_v12.json") as f:
    regelwerk = json.load(f)

regelwerk_str = json.dumps(regelwerk["rules"], sort_keys=True)
crc32 = zlib.crc32(regelwerk_str.encode()) & 0xFFFFFFFF

expected = 3246342384
assert crc32 == expected, f"INTEGRITY BREACH! {crc32} != {expected}"
```

---

### **2. METRIKEN-ENGINE (153 Metriken)**

```yaml
File: tooling/scripts/backend/metrics_processor.py
Lines: 815
Metriken: 153 (10 Kategorien)
Wichtigste Formeln:

# Trauma-Load
trauma_load = 0.4*T_panic + 0.3*T_disso + 0.2*(1-T_integ) + 0.1*dissociation

# Guardian Trip
guardian_trip = (is_critical OR z_prox > 0.65 OR t_panic > 0.8 OR hazard_score > 0.75)

# Affekt
A = 0.5 + (Emotion_pos - Emotion_neg) - T_panic

# B-Vektor (7D Empathie)
B_vec = [B_life, B_safety, B_truth, B_depth, B_warmth, B_clarity, B_score]
B_life >= 0.9 (KRITISCH!)
B_safety >= 0.8 (KRITISCH!)
```

**Test-Script:**
```python
from metrics_processor import calculate_full_spectrum

fs = calculate_full_spectrum(
    text="ich kann nicht mehr atmen, panik!",
    prev_text="",
    msg_id="test_001",
    speaker="user"
)

assert fs.T_panic > 0.8, f"T_panic zu niedrig: {fs.T_panic}"
assert fs.guardian_trip == 1, "Guardian Trip nicht ausgelöst!"
print("✅ Metriken-Engine OK!")
```

---

### **3. TRINITY ENGINE (12-DB Upload)**

```yaml
File: tooling/scripts/backend/trinity_engine.py
DBs: 12 (tempel_W_m1/m2/m5/p25, trialog_W_m1/m2/m5/p25, + 4 more)
Format: JSONL (eine Zeile = ein Entry)
Chain-Hash: SHA256(session|round|prompt|response|timestamp)

Entry-Struktur:
{
  session_id, round_id, timestamp,
  user_prompt, agent_response,
  metrics: {17 Haupt-Metriken},
  full_metrics: {153 Metriken},
  chain_hash, prev_chain_hash
}
```

---

### **4. FAISS IN-MEMORY (Query <1s)**

```yaml
File: tooling/scripts/backend/faiss_query.py
Index: tooling/data/faiss_indices/evoki_temple_33795_chunks.faiss
Chunks: 33.795
Dimensions: 384D
Model: all-MiniLM-L6-v2

WICHTIG:
- Beim FastAPI-Startup laden! (@app.on_event("startup"))
- Nicht bei jeder Query neu laden!
- In RAM halten (global Variable)

Startup-Code:
@app.on_event("startup")
async def load_faiss():
    global faiss_index, chunks_metadata
    faiss_index = faiss.read_index("tooling/data/faiss_indices/...")
    with open("tooling/data/faiss_indices/...metadata.json") as f:
        chunks_metadata = json.load(f)
```

---

## 🚀 SETUP & START

### **INITIAL SETUP (EINMALIG):**

```bash
# 1. V2.0 Code extrahieren (PowerShell-Script ausführen)
# Siehe: ULTIMATE_MASTER_PLAN_V8.md → PowerShell Master-Extraction-Script

# 2. Backend Dependencies
cd tooling\scripts\backend
pip install fastapi uvicorn python-multipart
pip install google-generativeai openai
pip install faiss-cpu numpy pandas sentence-transformers

# 3. Frontend Dependencies
cd app\interface
npm install

# 4. Genesis-Anchor Check
python -c "exec(open('check_genesis.py').read())"
# Muss ausgeben: ✅ Genesis-Anchor OK!
```

---

### **TÄGLICHER START:**

```bash
# Terminal 1: Backend starten
cd tooling\scripts\backend
python fastapi_gateway.py
# → Port 8000 aktiv, FAISS in RAM geladen

# Terminal 2: Frontend starten
cd app\interface
npm run dev
# → Port 5173 aktiv

# Browser: http://localhost:5173
# → Trialog Tab öffnet sich (Default!)
```

---

### **HEALTH CHECKS:**

```bash
# Backend
curl http://localhost:8000/health
# → {"status": "ok", "service": "EVOKI V3.0 Unified Backend"}

# FAISS
curl http://localhost:8000/api/faiss/health
# → {"index_loaded": true, "chunks": 33795, "dimensions": 384}

# Metriken
curl -X POST http://localhost:8000/api/metrics/calculate \
  -H "Content-Type: application/json" \
  -d '{"text": "Test"}'
# → {"success": true, "metrics": {...}}
```

---

## 🛠️ WARTUNG & DEBUGGING

### **LOGS:**

```bash
# Backend Logs
tail -f tooling/logs/fastapi_backend.log

# Frontend Console
# Browser → DevTools → Console

# Pipeline Logs
# UI → Tab #12 "Pipeline Überwachung"

# Error Logs
# UI → Tab #11 "Fehlerprotokoll"
```

---

### **HÄUFIGE PROBLEME:**

**Problem:** Frontend zeigt "Backend nicht erreichbar"
```bash
# Check:
curl http://localhost:8000/health

# Fix:
cd tooling\scripts\backend
python fastapi_gateway.py
```

**Problem:** FAISS Queries dauern >10s
```bash
# Ursache: FAISS nicht in RAM!

# Check:
curl http://localhost:8000/api/faiss/health
# → {"index_loaded": false}

# Fix: Backend neu starten
# Beim Startup MUSS load_faiss() aufgerufen werden!
```

**Problem:** Genesis-Anchor Violation
```bash
# Log zeigt: "INTEGRITY BREACH! CRC32 mismatch"

# Ursache: regelwerk_v12.json wurde geändert!

# Fix:
# 1. Backup wiederherstellen (Original von V2.0)
# 2. CRC32 Check:
python check_genesis.py
```

**Problem:** Timeout-Errors trotz SSE
```bash
# Ursache: Frontend nutzt noch fetch() statt EventSource

# Check App.tsx:
grep "fetch.*temple" app/interface/src/components/v2_tabs/EvokiTempleChat.tsx

# Fix: Ersetze fetch() mit EventSource (siehe ULTIMATE_MASTER_PLAN_V8.md)
```

---

## 📋 CHECKLISTE: EVOKI KORREKT IMPLEMENTIERT?

```
✅ Regelwerk V12 (881 Regeln) kopiert & CRC32 validiert
✅ 12 Tabs implementiert & Default = Trialog
✅ Backend Unified (nur Port 8000, kein Split!)
✅ FAISS in RAM (laden beim Startup)
✅ SSE für Temple Tab (kein Timeout!)
✅ metrics_processor.py (153 Metriken berechnen)
✅ trinity_engine.py (12-DB Upload)
✅ Hybrid-Retrieval (60% Semantik + 40% Metrik)
✅ Guardian Trip funktioniert (T_panic > 0.8 → trip = 1)
✅ Genesis-Anchor Enforcement (CRC32 bei jedem Start)
✅ chronik.log (jede Interaktion gespeichert)
```

---

## 🔒 SCHREIBSCHUTZ

**Dieses Dokument ist SCHREIBGESCHÜTZT.**

Änderungen erfordern:
1. Schreibschutz entfernen: `attrib -R HOW_TO_EVOKI_V3.md`
2. Änderungen vornehmen
3. Schreibschutz wiederherstellen: `attrib +R HOW_TO_EVOKI_V3.md`

**Bei Änderungen an der Architektur:**
- Dokumentiere in `ARCHITECTURE.txt`
- Update dieses Dokument
- Commit mit Begründung

---

**VERSION HISTORY:**

- V3.0 (2026-01-19): Initiale Version basierend auf vollständiger Discovery
- V3.1 (TBD): [Zukünftige Änderungen hier dokumentieren]

---

**ENDE DES DOKUMENTS**
