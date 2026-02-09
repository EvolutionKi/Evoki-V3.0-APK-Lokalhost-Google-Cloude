# 🎯 EVOKI V3.0 - EXECUTIONER PLAN (UMSETZBAR)

**Status:** ✅ FUNDAMENT KOMPLETT - BEREIT FÜR PHASE 1  
**Datum:** 2026-01-19  
**Ziel:** UI lädt 12 Tabs, Temple an FAISS+DB, 150+ Metriken live, Regelwerk V12 compliant

---

## 📊 WAS ICH GEFUNDEN HABE (BEWEISE)

### 1. APP.TSX (V2.0) - KOMPLETT ANALYSIERT

**Location:** `C:\Evoki V2.0\evoki-app\frontend\src\App.tsx` (1035 Zeilen, 50KB)

**DEFAULT TAB (LINE 167):**
```typescript
activeTab: Tab.Trialog  // ✅ BESTÄTIGT - NICHT Temple!
```

**TAB ENUM - MUSS GESUCHT WERDEN:**
- grep search "enum Tab" fand NICHTS im Bereich 1-800
- BEFUND: Enum muss in separater Datei sein → **MUSS NOCH GEFUNDEN WERDEN**

**BACKEND URLs (Lines 14, 141):**
```typescript
Line 14: fetch('http://localhost:8000/health')  // Python Backend (FAISS)
Line 24: fetch('http://localhost:3001/health')  // Node Backend (Trinity)
Line 141: backendApiUrl: 'http://localhost:3001'
```

**IMPORTS (Lines 86-110) - ALLE 12 TABS:**
```typescript
import EngineConsolePanel from './components/EngineConsolePanel';
import TrialogPanel from './components/TrialogPanel';
import AgentSelectionPanel from './components/AgentSelectionPanel';
import ParameterTuning Panel from '../components/ParameterTuningPanel';
import EvokiTempleChat from './components/EvokiTempleChat';
import VoiceSettingsPanel from './components/VoiceSettingsPanel';
import DeepStoragePanel from './components/DeepStoragePanel';
import ErrorLogPanel from './components/ErrorLogPanel';
import PipelineLogPanel from './components/PipelineLogPanel';
import AnalysisPanel from './components/Analysis';
import RulePanel from './components/RulePanel';
import ApiPanel from './components/ApiPanel';
```

✅ **12 TABS BESTÄTIGT** - Alle Component-Imports vorhanden!

---

### 2. TRINITY ENGINE (V2.0) - METRIKEN-CORE

**Location:** `C:\Evoki V2.0\evoki-app\backend\core\TrinityEngine.js` (607 Zeilen)

**17 HAUPTMETRIKEN (Lines 140-157):**
```javascript
A, PCI, coh, flow, T_integ, z_prox, hazard_score, guardian_trip,
phi_score, EV_readiness, EV_resonance, surprisal,
LEX_Coh_conn, LEX_Flow_pos, LEX_Emotion_pos, LEX_T_integ, LEX_T_disso
```

**12-DB-VERTEILUNG:**
```
tempel_W_m1/m2/m5/m25, tempel_W_p1/p2/p5/p25
trialog_W_m1/m2/m5/p25
```

**VECTOR SEARCH:**
```javascript
relevance_score = (textSim * 0.5) + (metricSim * 0.5)
```

---

## 🎯 PHASE 1: CODE-EXTRACTION (PowerShell-Scripts)

### SCHRITT 1.1: TAB-ENUM FINDEN

```powershell
Get-Content "C:\Evoki V2.0\evoki-app\frontend\src\types.ts" | Select-String "enum Tab" -Context 20
```

### SCHRITT 1.2: 12 TABS KOPIEREN

```powershell
New-Item -ItemType Directory -Path "app\interface\src\components\v2_tabs" -Force

$components = @(
    "EngineConsolePanel.tsx", "TrialogPanel.tsx", "Agent SelectionPanel.tsx",
    "EvokiTempleChat.tsx", "ParameterTuningPanel.tsx", "Analysis.tsx",
    "RulePanel.tsx", "ApiPanel.tsx", "VoiceSettingsPanel.tsx",
    "DeepStoragePanel.tsx", "ErrorLogPanel.tsx", "PipelineLogPanel.tsx"
)

foreach ($comp in $components) {
    Copy-Item -Path "C:\Evoki V2.0\evoki-app\frontend\src\components\$comp" `
              -Destination "app\interface\src\components\v2_tabs\$comp" -Force
}
```

### SCHRITT 1.3: BACKEND-ENGINES KOPIEREN

```powershell
New-Item -ItemType Directory -Path "tooling\scripts\backend\v2_reference" -Force

Copy-Item "C:\Evoki V2.0\evoki-app\backend\core\TrinityEngine.js" `
          "tooling\scripts\backend\v2_reference\TrinityEngine.js.REFERENCE"
Copy-Item "C:\Evoki V2.0\evoki-app\backend\core\DualBackendBridge.js" `
          "tooling\scripts\backend\v2_reference\DualBackendBridge.js.REFERENCE"
```

---

## 🎯 PHASE 2: BACKEND-PORTIERUNG (Python)

**Erstelle:** `tooling/scripts/backend/trinity_engine.py`

**Erstelle:** `tooling/scripts/backend/fastapi_gateway.py`

(Vollständiger Code siehe Master-Discovery-Dokument)

---

## 🎯 PHASE 3: TESTING

```bash
# Backend
python tooling\scripts\backend\fastapi_gateway.py

# Frontend
cd app\interface && npm run dev

# Health Check
curl http://localhost:8000/health
```

---

## ⚠️ KRITISCHE PUNKTE

1. **Tab-Enum MUSS gefunden werden** (types.ts)
2. **"Frontend Only" Ordner existiert NICHT** (Konzept, kein Ordner)
3. **V3.0 = Unified FastAPI** (kein Split wie V2.0)

---

**BEREIT FÜR PHASE 1, SCHRITT 1.1!**
