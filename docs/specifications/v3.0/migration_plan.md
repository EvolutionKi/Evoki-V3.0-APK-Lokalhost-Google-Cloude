# 🚀 V2.0 → V3.0 MIGRATION PLAN - CODE EXTRACTION

**Status:** ✅ ALLE DATEIEN GEFUNDEN  
**Quelle:** `C:\Evoki V2.0\evoki-app\`  
**Ziel:** `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\`

---

## ✅ GEFUNDENE DATEIEN (VOLLSTÄNDIG):

### **FRONTEND COMPONENTS (12 Tabs)**

| # | Component | V2.0 Path | Size | Status |
|---|-----------|-----------|------|--------|
| 1 | EngineConsolePanel.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 2 | TrialogPanel.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 3 | AgentSelectionPanel.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 4 | EvokiTempleChat.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 5 | ParameterTuningPanel.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 6 | Analysis.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 7 | RulePanel.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 8 | ApiPanel.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 9 | VoiceSettingsPanel.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 10 | DeepStoragePanel.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 11 | ErrorLogPanel.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |
| 12 | PipelineLogPanel.tsx | `frontend\src\components\` | ✅ | GEFUNDEN |

**PLUS:**
- `App.tsx` - 943 Zeilen State-Management ✅
- `AnalysisPanel.tsx` - Alternative zu `Analysis.tsx` ✅

### **BACKEND ENGINES (V2.0 Core)**

| Component | V2.0 Path | Size | Status |
|-----------|-----------|------|--------|
| TrinityEngine.js | `backend\core\` | 22.2KB | ✅ GEFUNDEN |
| DualBackendBridge.js | `backend\core\` | ? | ✅ GEFUNDEN |
| GeminiContextBridge.js | `backend\core\` | ? | ✅ GEFUNDEN |

---

## 📋 MIGRATIONS-STRATEGIE:

### **PHASE 1: FRONTEND-COMPONENTS KOPIEREN**

**Ziel-Verzeichnis:** `app/interface/src/components/v2_tabs/`

**Strategie:**
```bash
# Erstelle neues Verzeichnis für V2.0 Tabs
mkdir app/interface/src/components/v2_tabs

# Kopiere alle 12 Tab-Components
cp "C:\Evoki V2.0\evoki-app\frontend\src\components\*.tsx" \
   "app/interface/src/components/v2_tabs/"

# Spezifische Dateien:
- EngineConsolePanel.tsx
- TrialogPanel.tsx
- AgentSelectionPanel.tsx
- EvokiTempleChat.tsx
- ParameterTuningPanel.tsx
- Analysis.tsx
- RulePanel.tsx
- ApiPanel.tsx
- VoiceSettingsPanel.tsx
- DeepStoragePanel.tsx
- ErrorLogPanel.tsx
- PipelineLogPanel.tsx
```

**Anpassungsbedarf:**
1. **Import-Pfade aktualisieren:**
   - V2.0: `../../services/core/` → V3.0: `@/services/`
   - V2.0: Node.js Backend (Port 3001) → V3.0: FastAPI (Port 8000)

2. **API-Endpoints ändern:**
   ```typescript
   // V2.0
   const response = await fetch('http://localhost:3001/api/bridge/process');
   
   // V3.0
   const response = await fetch('http://localhost:8000/api/temple/process');
   ```

3. **State-Management:**
   - V2.0: Lokaler Component-State
   - V3.0: Möglicherweise globaler State in `App.tsx`

### **PHASE 2: APP.TSX REFERENZ-ANALYSE**

**Quelle:** `C:\Evoki V2.0\evoki-app\frontend\src\App.tsx` (943 Zeilen)

**Was extrahieren:**
1. **Tab-Enum Definition:**
   ```typescript
   enum Tab {
     EngineConsole,
     Trialog,
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
   }
   ```

2. **Error Handling Pattern:**
   - Global Error Handler (Line 358)
   - Console Capture (Line 385)
   - Fetch Interceptor (Line 407)

3. **Backend Health Check:**
   - Loading Screen Logic (Line 6-70)
   - Health Check Loop (Line 518, aber DEAKTIVIERT wegen SIGINT-Bug!)

4. **Auto-Save System:**
   - LocalStorage Management (30s Interval)
   - Circuit Breaker bei QuotaExceeded

**Nicht übernehmen:**
- Backend Health Check Loop (crasht Backend!)
- SQLite Client-Side Code (nicht kompatibel mit Vite)

### **PHASE 3: BACKEND-ENGINES PORTIERUNG**

**TrinityEngine.js → Python**

**Quelle:** `C:\Evoki V2.0\evoki-app\backend\core\TrinityEngine.js` (22.2KB)

**Ziel:** `tooling/scripts/backend/trinity_engine.py`

**Funktionen zu portieren:**
- Metriken-Berechnung (~120 Metriken)
- Session Management
- Vector DB Integration (12-DB-Sharding)

**Anpassungen:**
- JavaScript → Python (async/await → asyncio)
- Express Middleware → FastAPI Dependency Injection
- Node.js Buffer → Python bytes

**DualBackendBridge.js → FastAPI Endpoint**

**Quelle:** `C:\Evoki V2.0\evoki-app\backend\core\DualBackendBridge.js`

**Ziel:** `tooling/scripts/backend/fastapi_gateway.py`

**Was übernehmen:**
- Pipeline-Struktur (Metrics → FAISS → Trinity → Gemini)
- Timeout-Management (aber FIX: SSE statt fester Timeouts)
- Error-Handling

**Was NICHT übernehmen:**
- Node.js + Python Split (→ Unified FastAPI!)
- CLI-Spawning für query.py (→ In-Memory FAISS)

**GeminiContextBridge.js → API-Zipper**

**Quelle:** `C:\Evoki V2.0\evoki-app\backend\core\GeminiContextBridge.js`

**Ziel:** `tooling/scripts/backend/llm_router.py`

**Funktionen:**
- Gemini API (90s Timeout)
- OpenAI Fallback (30s Timeout)
- Context-Window Management
- Token-Counting

---

## 🔧 MIGRATIONS-SCHRITTE (DETAILLIERT):

### **STEP 1: Frontend-Verzeichnis erstellen**

```bash
cd "C:\Evoki V3.0 APK-Lokalhost-Google Cloude"
mkdir -p app/interface/src/components/v2_tabs
```

### **STEP 2: Alle 12 Tab-Components kopieren**

```powershell
# PowerShell Script
$source = "C:\Evoki V2.0\evoki-app\frontend\src\components"
$dest = "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\app\interface\src\components\v2_tabs"

$components = @(
    "EngineConsolePanel.tsx",
    "TrialogPanel.tsx",
    "AgentSelectionPanel.tsx",
    "EvokiTempleChat.tsx",
    "ParameterTuningPanel.tsx",
    "Analysis.tsx",
    "RulePanel.tsx",
    "ApiPanel.tsx",
    "VoiceSettingsPanel.tsx",
    "DeepStoragePanel.tsx",
    "ErrorLogPanel.tsx",
    "PipelineLogPanel.tsx"
)

foreach ($comp in $components) {
    Copy-Item -Path "$source\$comp" -Destination "$dest\$comp" -Force
    Write-Host "✅ Copied: $comp"
}
```

### **STEP 3: App.tsx analysieren**

```bash
# Lese V2.0 App.tsx
cat "C:\Evoki V2.0\evoki-app\frontend\src\App.tsx"

# Extrahiere Tab-Enum (für V3.0 App.tsx)
# Extrahiere Error-Handling Pattern
# Dokumentiere State-Management
```

### **STEP 4: Backend-Verzeichnis erstellen**

```bash
mkdir -p tooling/scripts/backend
```

### **STEP 5: Backend-Engines kopieren (als Referenz)**

```bash
cp "C:\Evoki V2.0\evoki-app\backend\core\TrinityEngine.js" \
   "tooling/scripts/backend/TrinityEngine.js.REFERENCE"
   
cp "C:\Evoki V2.0\evoki-app\backend\core\DualBackendBridge.js" \
   "tooling/scripts/backend/DualBackendBridge.js.REFERENCE"
   
cp "C:\Evoki V2.0\evoki-app\backend\core\GeminiContextBridge.js" \
   "tooling/scripts/backend/GeminiContextBridge.js.REFERENCE"
```

### **STEP 6: Python-Portierung (manuell)**

**Datei 1: `trinity_engine.py`**
- Lese `TrinityEngine.js.REFERENCE`
- Portiere Metriken-Logik nach Python
- Nutze V2.1 Metriken-Schema (statt V2.0's ~120)

**Datei 2: `fastapi_gateway.py`**
- Lese `DualBackendBridge.js.REFERENCE`
- Implementiere FastAPI-Endpoints
- SSE für async Processing

**Datei 3: `llm_router.py`**
- Lese `GeminiContextBridge.js.REFERENCE`
- Implementiere Gemini + OpenAI Fallback
- Token-Counting für Context-Window

---

## 🎯 POST-MIGRATION TASKS:

### **1. Frontend-Integration**

**Update `app/interface/src/App.tsx`:**
```typescript
import { EngineConsolePanel } from './components/v2_tabs/EngineConsolePanel';
import { TrialogPanel } from './components/v2_tabs/TrialogPanel';
// ... alle 12 Tabs

enum Tab {
  EngineConsole,
  Trialog,        // DEFAULT!
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
}

const [activeTab, setActiveTab] = useState(Tab.Trialog);  // NICHT Temple!
```

### **2. API-Endpoints aktualisieren**

**In ALLEN 12 Tab-Components:**
```typescript
// V2.0 (alt)
const BASE_URL = 'http://localhost:3001';

// V3.0 (neu)
const BASE_URL = 'http://localhost:8000';
```

**Endpoint-Mapping:**
| V2.0 Endpoint | V3.0 Endpoint |
|---------------|---------------|
| `/api/bridge/process` | `/api/temple/process` |
| `/api/v1/interact` | `/api/trialog/interact` |
| `/api/v1/status` | `/api/engine/status` |
| `/api/pipeline/logs` | `/api/pipeline/logs` (gleich) |

### **3. Dependencies installieren**

**Frontend:**
```bash
cd app/interface
npm install
# Prüfe package.json - entferne SQLite-Pakete falls vorhanden!
```

**Backend:**
```bash
cd tooling/scripts/backend
pip install fastapi uvicorn python-multipart
pip install google-generativeai openai
pip install faiss-cpu numpy pandas
```

### **4. Testing-Sequenz**

**Test 1: Frontend-Build**
```bash
cd app/interface
npm run dev
# Erwartung: Vite startet ohne Errors
# Browser: http://localhost:5173
```

**Test 2: Backend-Start**
```bash
cd tooling/scripts/backend
python fastapi_gateway.py
# Erwartung: FastAPI startet auf Port 8000
# Test: curl http://localhost:8000/health
```

**Test 3: Tab-Navigation**
```
Browser: http://localhost:5173
→ Klicke durch alle 12 Tabs
→ Prüfe: Keine Console-Errors
→ Default Tab = Trialog? ✅
```

**Test 4: API-Connectivity**
```typescript
// Im Trialog-Tab
Input: "Test-Nachricht"
→ POST /api/trialog/interact
→ Erwartung: Response von FastAPI Backend
```

---

## ⚠️ KRITISCHE ADJUSTMENTS:

### **1. Timeout-Fix (SSE statt Fixed Timeout)**

**V2.0 Problem:**
```typescript
// Frontend
const response = await fetch('/api/bridge/process', {
  signal: AbortSignal.timeout(60000)  // 60s, aber Backend braucht 115s!
});
```

**V3.0 Lösung:**
```typescript
// Frontend (SSE)
const eventSource = new EventSource('/api/temple/process-stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'progress') {
    setProgress(data.message);  // "FAISS Suche... 50%"
  } else if (data.type === 'complete') {
    setResponse(data.result);
    eventSource.close();
  }
};
```

```python
# Backend (FastAPI)
from sse_starlette.sse import EventSourceResponse

@app.post("/api/temple/process-stream")
async def temple_process_stream(request: Request):
    async def event_generator():
        yield {"event": "progress", "data": json.dumps({"type": "progress", "message": "Metrics..."})}
        # ... Metrics-Berechnung
        
        yield {"event": "progress", "data": json.dumps({"type": "progress", "message": "FAISS..."})}
        # ... FAISS-Suche
        
        yield {"event": "complete", "data": json.dumps({"type": "complete", "result": final_response})}
    
    return EventSourceResponse(event_generator())
```

### **2. FAISS In-Memory statt CLI-Spawn**

**V2.0 Problem:**
```javascript
// Spawnt Python-Prozess JEDES MAL!
const result = await spawnPython('query.py', [prompt]);
// 15s nur zum Laden des Index!
```

**V3.0 Lösung:**
```python
# FastAPI Startup Event
faiss_index = None

@app.on_event("startup")
async def load_faiss():
    global faiss_index
    faiss_index = faiss.read_index("tooling/data/faiss_indices/chatverlauf.faiss")
    # Nur EINMAL beim Start! Danach in RAM!

@app.post("/api/temple/process")
async def temple_process(prompt: str):
    # FAISS-Suche jetzt <1s statt 15s!
    results = faiss_index.search(embedding, k=5)
```

### **3. Kein Backend-Split mehr**

**V2.0 Problem:**
```
Node.js (3001) ←→ HTTP ←→ Python (8000)
→ 2 Prozesse, 2 Health-Checks, Race Conditions
```

**V3.0 Lösung:**
```
NUR FastAPI (8000) - "Trinity Engine Unified"
→ 1 Prozess, 1 Port, Kein Split!
```

### **4. Default Tab = Trialog**

**V3.0 App.tsx:**
```typescript
const [activeTab, setActiveTab] = useState(Tab.Trialog);  // NICHT Temple!
```

---

## 📊 MIGRATIONS-CHECKLIST:

### **Frontend:**
- [ ] Verzeichnis `app/interface/src/components/v2_tabs` erstellt
- [ ] 12 Tab-Components kopiert
- [ ] `App.tsx` aktualisiert (Tab-Enum + Default = Trialog)
- [ ] API-URLs geändert (3001 → 8000)
- [ ] Import-Pfade angepasst
- [ ] `npm install` erfolgreich
- [ ] Vite Dev-Server startet ohne Errors

### **Backend:**
- [ ] Verzeichnis `tooling/scripts/backend` erstellt
- [ ] V2.0 Engines kopiert (als `.REFERENCE`)
- [ ] `trinity_engine.py` erstellt (portiert von TrinityEngine.js)
- [ ] `fastapi_gateway.py` erstellt (portiert von DualBackendBridge.js)
- [ ] `llm_router.py` erstellt (portiert von GeminiContextBridge.js)
- [ ] FAISS In-Memory Loading implementiert
- [ ] SSE für async Processing implementiert
- [ ] `pip install` erfolgreich
- [ ] FastAPI startet auf Port 8000

### **Testing:**
- [ ] Frontend lädt alle 12 Tabs
- [ ] Default Tab = Trialog
- [ ] Backend Health Check: `/health` → 200 OK
- [ ] Trialog-Interaction: POST `/api/trialog/interact` → Response
- [ ] Temple-Processing: SSE `/api/temple/process-stream` → Events
- [ ] FAISS-Suche < 2s (statt 15s)
- [ ] Keine Timeout-Errors mehr

---

## 🚀 NÄCHSTE AKTION:

**Ich empfehle:**
1. **STEP 2 ausführen** (12 Tab-Components kopieren)
2. **STEP 3 ausführen** (`App.tsx` analysieren)
3. **STEP 5 ausführen** (Backend-Engines als Referenz kopieren)
4. Dann: Python-Portierung (manuell, Schritt für Schritt)

**Soll ich mit STEP 2 starten (PowerShell-Script ausführen)?**
