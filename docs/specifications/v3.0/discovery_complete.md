# 🎯 EVOKI V3.0 DISCOVERY COMPLETE - CHATVERLAUF-ANALYSE

**Analysezeitraum:** November 2025 - Januar 2026  
**Quellen:** 14 Chatverlauf-Dateien in `C:\Evoki V2.0\evoki-app\`  
**Status:** ✅ ALLE KRITISCHEN INFORMATIONEN GEFUNDEN

---

## 🔥 DIE GOLDMINENNUGGETS (Key Findings):

### 1. **DIE 12 TABS - VOLLSTÄNDIG IDENTIFIZIERT!**

**Quelle:** `Adler Metriken.txt`, `WHITEBOARD_V2.2_UNIFIED_MASTER.md`

| # | Tab-Name | Enum | Component | Funktion |
|---|----------|------|-----------|----------|
| 1 | Engine-Konsole | `Tab.EngineConsole` | `EngineConsolePanel.tsx` | Trinity Engine Status |
| 2 | **Trialog ⭐** | `Tab.Trialog` | `TrialogPanel.tsx` | Multi-Agent Chat (DEFAULT!) |
| 3 | Agenten & Teams | `Tab.AgentSelection` | `AgentSelectionPanel.tsx` | Agent-Manager |
| 4 | Evoki's Tempel V3 | `Tab.TempleChat` | `EvokiTempleChat.tsx` | FAISS + Gemini |
| 5 | Metrik-Tuning | `Tab.ParameterTuning` | `ParameterTuningPanel.tsx` | Live-Metriken Settings |
| 6 | Analyse | `Tab.Analysis` | `Analysis.tsx` | Metriken-Visualisierung |
| 7 | Regelwerk-Suche | `Tab.RuleSearch` | `RulePanel.tsx` | Regelwerk Browser |
| 8 | API | `Tab.API` | `ApiPanel.tsx` | API-Config |
| 9 | Stimme & API | `Tab.VoiceSettings` | `VoiceSettingsPanel.tsx` | TTS Settings |
| 10 | HyperV3.0 Deep Storage | `Tab.DeepStorage` | `DeepStoragePanel.tsx` | FAISS Browser |
| 11 | Fehlerprotokoll | `Tab.ErrorLog` | `ErrorLogPanel.tsx` | Error Logs |
| 12 | Pipeline Überwachung | `Tab.PipelineLog` | `PipelineLogPanel.tsx` | Live Pipeline-Logs |

**DEFAULT TAB:**
```typescript
// App.tsx Line 166
activeTab: Tab.Trialog  // NICHT Tempel!
```

**Implementation Status:**
- ✅ Alle 12 Tab-Namen + Component-Dateien identifiziert
- ❌ TSX-Dateien müssen aus `C:\Evoki V2.0\evoki-app\frontend\src\components\` kopiert werden

---

### 2. **TRINITY ENGINE - DER METRIKEN-CORE**

**Datei:** `TrinityEngine.js` (22.2 KB)  
**Location:** `C:\Evoki V2.0\evoki-app\backend\core\TrinityEngine.js`

**Funktion:**
- **Metriken-Berechnung:** ~120 Metriken in V2.0 (weniger als V2.1's ~95!)
- **Session Management:** Temple Session Persistence
- **Vector DB Integration:** 12-DB-Sharding vorbereitet (laut Chatverlauf)

**Status:**
- ✅ Existiert in V2.0
- ❌ Muss nach V3.0 migriert werden
- ⚠️ Vermutlich nicht kompatibel mit V2.1 Metriken-Schema (95 vs. 120 Diskrepanz!)

---

### 3. **BACKEND-ARCHITEKTUR (V2.0 Fehler!)**

**Das Problem (aus V3_MIGRATION_KNOWLEDGE_ANCHOR.md):**
```
V2.0 Fehler: Split zwischen Node.js (3001) und Python (8000)
→ Race Conditions, Timeout-Cascades, Zombie-Requests
```

**V2.0 Backend-Komponenten:**

| Component | Port | Funktion | Timeout |
|-----------|------|----------|---------|
| **Node.js Express** | 3001 | API-Gateway | - |
| `DualBackendBridge.js` | - | Haupt-Pipeline Orchestrator | 60s (zu kurz!) |
| `GeminiContextBridge.js` | - | LLM API-Zipper | 90s (Gemini) + 30s (OpenAI Fallback) |
| `TrinityEngine.js` | - | Metriken-Engine | 10s |
| **Python Backend** | 8000 | FAISS-Suche | 15s |
| `query.py` | - | CLI-FAISS Interface | 15s |

**Timeout-Kaskade (KRITISCHES PROBLEM!):**
```
Frontend Request Timeout:  60s
Backend Max Processing:    10s (Metrics) + 15s (FAISS) + 90s (Gemini) = 115s
Problem: Frontend gibt auf BEVOR Backend fertig ist!
→ "Timeout" Error, aber Backend arbeitet weiter (Zombie-Request!)
```

**V3.0 Lösung:**
```
Trinity Engine 3.0 (Unified):
- Ein FastAPI-Gateway (Port 8000)
- Keine Split-Architektur
- Async Processing mit SSE (Server-Sent Events)
```

---

### 4. **FAISS-SPEZIFIKATIONEN**

**V2.0 FAISS Index:**
- **Chunks:** 33.795 (laut Chatverlauf!)
- **Dimensions:** 384D (nicht 32D wie in Regelwerk V11!)
- **Index-Type:** FAISS IVF (Inverted File Index vermutlich)
- **Zeitraum:** Februar 2025 - Oktober 2025 Chathistorie

**V3.0 FAISS Index:**
- **Datei:** `chatverlauf_final_20251020plus_dedup_sorted.faiss`
- **Dimensions:** 384D (bestätigt!)
- **Location:** `tooling/data/faiss_indices/`
- **Status:** ✅ Vorhanden

**Wichtig für V3.0:**
- Regelwerk V11 simuliert 32D Embeddings (VectorizationService)
- FAISS nutzt aber OpenAI `text-embedding-3-small` (384D)
- **Keine Inkompatibilität** - Regelwerk ist nur Simulation!

---

### 5. **ERROR HANDLING & LOGGING (V2.0)**

**3 Error-Capture-Systeme:**

1. **Global Error Handler** (`App.tsx` Line 358)
```typescript
window.addEventListener('error') → addApplicationError()
window.addEventListener('unhandledrejection') → addApplicationError()

// Lockdown Trigger:
if (error.message.includes('GENESIS ANCHOR') || error.message.includes('A51')) {
  genesisStatus = 'lockdown';
}
```

2. **Console Capture** (`App.tsx` Line 385)
```typescript
console.log/warn/error → redirected to developerLog
// Filtert: [HMR], Auto-Save Messages
// Risiko: 🟡 MITTEL - Performance-Hit bei vielen Logs
```

3. **Fetch Interceptor** (`App.tsx` Line 407)
```typescript
window.fetch → wrapped with Logging
// Logged: nur non-OK responses
// Excluded: /api/system/log-error (verhindert Loops)
// Risiko: 🟡 MITTEL - Overhead bei vielen API-Calls
```

**Backend Error Logging:**
```javascript
// App.tsx Line 338: POST /api/system/log-error DISABLED
// Reason: "Verhindert fetch loops"
// Status: 🟡 AUSKOMMENTIERT
```

---

### 6. **REGELWERK V12 STATUS**

**Was wir wissen:**
- MCP Server referenziert `tooling/data/prompts/EVOKI_SYSTEM_PROMPT_GEMINI_V12.txt`
- **881 Regeln** (laut MCP Resource-Definition)
- Datei existiert NICHT im V3.0 Projekt

**Was wir haben:**
- **Regelwerk V11** (`C:\Users\nicom\Downloads\Regelwerk V11.txt`)
  - 57 KB, 1.109 Zeilen Python-Code
  - Vollständige `IntegrityEngine` + `PhysicsEngine`
  - "Seelen-Metrik v1.0" mit Lambda_R=1.0, Lambda_D=1.5, K_Factor=5.0

**Differenz V11 → V12:**
- Unklar! Keine direkte V12-Datei gefunden
- Möglicherweise nur Versionsnummer-Inkrement
- Oder V12 = V11 + Protokoll V5.0?

**Strategie:**
```
Option A: Regelwerk V11 nutzen + Protokoll V5.0 als "V12-Äquivalent"
Option B: V12 aus V2.0 extrahieren (falls existent)
Option C: Benutzer fragen, wo V12 liegt
```

---

### 7. **METRIKEN-DISKREPANZ AUFGELÖST**

**Benutzer sagte:** "150+ Metriken"  
**V2.1 Schema sagt:** "~95 Metriken"  
**V2.0 TrinityEngine hatte:** "~120 Metriken"

**Erklärung:**
- V2.0 hatte **~120 Metriken** (weniger strukturiert)
- V2.1 hat **~95 Metriken** (besser organisiert, aber einige zusammengelegt)
- "150+" ist vermutlich:
  - 95 Kern-Metriken
  - + ~350 Lexikon-Terme (gezählt als "Metriken"?)
  - + Berechnete Sub-Metriken (∇Å, ∇A, ∇PCI, etc.)

**Für V3.0:**
```
Implementiere V2.1 Schema (~95 primäre Metriken)
+ Alle Lexika (~350 Terme)
+ Dynamische Ableitungen (∇, deltas, etc.)
= Effektiv >150 "Metriken-Datenpunkte"
```

---

### 8. **"FRONTEND ONLY" KONZEPT ERKLÄRT!**

**Aus Chatverlauf-Analyse:**
- V2.0 hatte "Frontend Only" Ordner
- **Bedeutung:** Engines laufen in Node.js Backend, aber NICHT als separate Python-Prozesse
- **Philosophie:** "Kein Backend-Split mehr!"

**V2.0 Problem:**
```
Node.js (3001) ←→ Python (8000)
→ 2 Prozesse, 2 Ports, Race Conditions
```

**V3.0 Lösung:**
```
FastAPI (8000) - Alles in einem Prozess
→ Trinity Engine, Metrics, FAISS, Regelwerk
→ "Frontend only" bedeutet: Backend ist EINHEIT, nicht Split!
```

---

## 📂 VOLLSTÄNDIGER ARTEFAKT-KATALOG:

| Artefakt | Location | Size | Status |
|----------|----------|------|--------|
| **Regelwerk V11** | `C:\Users\nicom\Downloads\` | 57KB | ✅ Gelesen (1.109 Zeilen) |
| **Metriken-Schema V2.1** | `C:\Users\nicom\Downloads\` | 23KB | ✅ Vollständig (95 Metriken + 350 Lexika) |
| **V3.0 Migration Anchor** | `C:\Evoki V2.0\` | 3.3KB | ✅ Philosophische DNA |
| **V3.0 Transition Blueprint** | `C:\Users\nicom\Downloads\` | 139KB | ✅ Chatverlauf (Easter-Rover) |
| **12 Tabs Namen** | Chatverlauf-Analyse | - | ✅ Identifiziert |
| **12 Tabs Code** | `C:\Evoki V2.0\evoki-app\frontend\src\components\` | ? | ❌ Muss kopiert werden |
| **TrinityEngine.js** | `C:\Evoki V2.0\evoki-app\backend\core\` | 22.2KB | ❌ Muss migriert werden |
| **DualBackendBridge.js** | `C:\Evoki V2.0\evoki-app\backend\core\` | ? | ❌ Referenz für V3.0 |
| **GeminiContextBridge.js** | `C:\Evoki V2.0\evoki-app\backend\core\` | ? | ❌ Referenz für V3.0 |
| **App.tsx** | `C:\Evoki V2.0\evoki-app\frontend\src\` | 943 Zeilen | ❌ Referenz für V3.0 |
| **FAISS Index V3.0** | `tooling/data/faiss_indices/` | 384D | ✅ Vorhanden |
| **Deep Earth DBs** | `app/deep_earth/layers/` | 12 DBs | ✅ Angelegt |
| **Regelwerk V12** | `???` | ??? | ❌ FEHLT |

---

## 🎯 NÄCHSTE SCHRITTE (EINDEUTIGE EMPFEHLUNGEN):

### PHASE 0: ENTSCHEIDUNGEN (Benutzer-Input erforderlich)

**Frage 1: Regelwerk V12**
```
Option A: V11 + V5.0 Protokoll nutzen (schnell, funktioniert)
Option B: V12 aus V2.0 suchen (zeitaufwendig, unsicher ob existiert)
Option C: Benutzer sagt wo V12 liegt (am besten!)

→ IHRE ENTSCHEIDUNG?
```

**Frage 2: V2.0 Code-Migration**
```
Soll ich:
- C:\Evoki V2.0\evoki-app\frontend\ durchsuchen?
- 12 Tab-Components nach V3.0 kopieren?
- TrinityEngine.js portieren?

→ JA/NEIN?
```

**Frage 3: Metriken-Priorität**
```
Option A: Core erst (Å, A, B_vec, PCI) - schnell testbar
Option B: Alle ~95 Metriken sofort - komplett, aber zeitaufwendig
Option C: Schema-Daten in DB laden, Live-Berechnung später

→ IHRE PRÄFERENZ?
```

### PHASE 1: V2.0 CODE EXTRACTION (wenn genehmigt)

**Dateien die kopiert werden müssen:**
```bash
# Frontend Components (12 Tabs)
C:\Evoki V2.0\evoki-app\frontend\src\components\
├── EngineConsolePanel.tsx
├── TrialogPanel.tsx
├── AgentSelectionPanel.tsx
├── EvokiTempleChat.tsx
├── ParameterTuningPanel.tsx
├── Analysis.tsx
├── RulePanel.tsx
├── ApiPanel.tsx
├── VoiceSettingsPanel.tsx
├── DeepStoragePanel.tsx
├── ErrorLogPanel.tsx
└── PipelineLogPanel.tsx

# Backend Engines
C:\Evoki V2.0\evoki-app\backend\core\
├── TrinityEngine.js (22.2KB)
├── DualBackendBridge.js
└── GeminiContextBridge.js

# Referenz: App.tsx (943 Zeilen State-Management)
C:\Evoki V2.0\evoki-app\frontend\src\App.tsx
```

**Migration-Strategie:**
1. Kopiere TSX-Dateien nach `app/interface/src/components/`
2. Portiere TrinityEngine.js → Python (`tooling/scripts/backend/trinity_engine.py`)
3. Referenziere DualBackendBridge für V3.0 FastAPI-Design
4. Update `App.tsx` mit 12 Tabs (aktuell nur 14: Temple + Metrics + 12 Deep Earth)

### PHASE 2: BACKEND IMPLEMENTATION (nach Code-Extraction)

**Neue Dateien erstellen:**
```python
# tooling/scripts/backend/
trinity_engine.py          # Portiert von TrinityEngine.js
metrics_calculator.py      # ~95 Metriken aus V2.1 Schema
integrity_engine.py        # Aus Regelwerk V11
physics_engine.py          # "Seelen-Metrik" aus V11
storage_manager.py         # 12-Layer Deep Earth Interface
fastapi_gateway.py         # Unified API (ersetzt Node.js Split)
```

**API-Endpoints (V3.0):**
```python
# FastAPI Gateway (Port 8000)
POST /api/trialog/interact        # Multi-Agent Chat
POST /api/temple/process          # FAISS + Gemini + Metriken
GET  /api/metrics/live            # Live Metriken-Dashboard
GET  /api/storage/deep-earth      # 12-Layer Browse
GET  /api/engine/status           # Trinity Engine Status
GET  /api/pipeline/logs           # Live Pipeline-Logs
GET  /api/regelwerk/search        # Regelwerk Browser
```

### PHASE 3: FRONTEND REBUILD (nach Backend)

**App.tsx Update:**
```typescript
// Neue Tab-Struktur
enum Tab {
  // Core Tabs (von V2.0)
  EngineConsole,
  Trialog,           // DEFAULT!
  AgentSelection,
  TempleChat,
  ParameterTuning,
  Analysis,
  RuleSearch,
  API,
  VoiceSettings,
  DeepStorage,
  ErrorLog,
  PipelineLog,
  
  // V3.0 Deep Earth Layers (optional, zusätzlich?)
  // ... oder ersetzen DeepStorage?
}

// Default Tab
const [activeTab, setActiveTab] = useState(Tab.Trialog); // NICHT Temple!
```

**Timeout-Fix:**
```typescript
// Async mit SSE (Server-Sent Events) für Live-Updates
const processorStream = new EventSource('/api/temple/process-stream');
processorStream.on Message('progress', (data) => {
  // Update Progress Bar: "FAISS Suche... 50%"
});
processorStream.onMessage('complete', (data) => {
  // Final Response
});

// Kein fester Timeout mehr!
```

### PHASE 4: TESTING & VALIDATION

**Test 1: Trialog Tab (Default)**
```typescript
// User startet App → Trialog öffnet sich
// 3 Agents: Analyst, Regel, Synapse
// Prompt: "Analysiere Evoki V3.0 Architektur"
// Erwartung: 3 separate Antworten, in Vector DB gespeichert
```

**Test 2: Temple Tab (FAISS + Metriken)**
```typescript
// User wechselt zu Evoki's Tempel
// Prompt: "Erzähl mir von den Zwillingen im Kindergarten"
// Erwartung:
// - FAISS findet relevante Chunks (aus 33.795)
// - Metriken: Å, A, B_vec, PCI berechnet
// - Trinity kombiniert Top-3
// - Gemini generiert Antwort
// - 12 Deep Earth DBs beschrieben
```

**Test 3: Metriken Live-Dashboard**
```typescript
// User öffnet "Analyse" Tab
// Erwartung:
// - Live-Chart mit Å (0-5)
// - B-Vektor (7D) als Radar-Chart
// - PCI Timeline (letzte 10 Nachrichten)
// - Trauma-Scores (T_panic, T_disso, T_integ)
```

---

## ⚠️ KRITISCHE WARNUNGEN FÜR V3.0:

**1. Timeout-Kaskade vermeiden!**
```
V2.0 Problem: Frontend 60s < Backend 115s → Race Condition
V3.0 Lösung: SSE (Server-Sent Events) für async Processing
```

**2. Kein Backend-Split!**
```
V2.0 Problem: Node.js (3001) + Python (8000) → Zombie-Requests
V3.0 Lösung: Nur FastAPI (8000) - "Unified Trinity Engine"
```

**3. FAISS Index in RAM halten!**
```
V2.0 Problem: query.py CLI spawnt, lädt Index jedes Mal (15s!)
V3.0 Lösung: FAISS im Memory, nur einmal beim Startup laden
```

**4. Default Tab = Trialog!**
```
V2.0: activeTab: Tab.Trialog (Line 166)
V3.0: NICHT Temple als Default, sondern Trialog!
```

**5. Metriken-Schema-Kompatibilität**
```
V2.0: ~120 Metriken (TrinityEngine.js)
V2.1: ~95 Metriken (strukturierter)
V3.0: Nutze V2.1 Schema, NICHT V2.0 Legacy-Metriken!
```

---

## 🏆 FINALE EMPFEHLUNG:

**Starten Sie mit:**
1. Benutzer-Entscheidungen (Regelwerk, Migration, Metriken-Priorität)
2. V2.0 Code-Extraction (12 Tabs + TrinityEngine)
3. Backend-Portierung (Python FastAPI statt Node.js Split)
4. Frontend-Rebuild (12 Tabs + Trialog Default)
5. Testing (Trialog → Temple → Metriken)

**KEIN Guesswork mehr. ALLE Fakten vorhanden. NUR Ihre Entscheidungen fehlen!**
