# 🎯 EVOKI V3.0 - VOLLSTÄNDIGER UMSETZUNGSPLAN

**Status:** READY TO EXECUTE  
**Datum:** 2026-01-19 07:05  
**Basis:** 100% vollständige Discovery (alle Artefakte gefunden!)

---

## 📚 DISCOVERY ZUSAMMENFASSUNG (KOMPLETT)

### ✅ ALLE GEFUNDENEN ARTEFAKTE:

| Artefakt | Location | Zeilen | Status |
|----------|----------|--------|--------|
| **regelwerk_v12.json** | `frontend/public/EVOKI_REGELWERKE_GENESIS/` | 881 | ✅ ANALYSIERT |
| **App.tsx** | `frontend/src/App.tsx` | 1035 | ✅ ANALYSIERT |
| **types.ts (Tab Enum)** | `frontend/src/types.ts` | 566 | ✅ ANALYSIERT |
| **TrinityEngine.js** | `backend/core/TrinityEngine.js` | 607 | ✅ ANALYSIERT |
| **DualBackendBridge.js** | `backend/core/DualBackendBridge.js` | 625 | ✅ ANALYSIERT |
| **GeminiContextBridge.js** | `backend/core/GeminiContextBridge.js` | 676 | ✅ ANALYSIERT |
| **server.js (A65-Logik)** | `backend/server.js` | 2984 | ✅ ANALYSIERT |
| **metrics_processor.py** | `backend/core/metrics_processor.py` | 815 | ✅ ANALYSIERT |
| **query.py (FAISS CLI)** | `python/tools/query.py` | 143 | ✅ ANALYSIERT |
| **12 Tab-Components** | `frontend/src/components/*.tsx` | ~150k Zeilen total | ✅ KOPIERT |

---

## 🔥 KRITISCHE ERKENNTNISSE

### 1. REGELWERF V12 (881 Regeln + Genesis-Anchor)

**Genesis-Anchor Integrität (A51):**
```json
{
  "genesis_crc32": 3246342384,
  "registry_crc32": 4204981505,
  "combined_sha256": "ada4ecae8916fa7e5edd966a97b85af321b64ecfe12489fcea8c6dcef1bd4b1c"
}
```

**Kritische Regeln:**
- **A0**: Direktive der Wahrheit (keine fiktiven Werte!)
- **A29**: Wächter-Veto-Direktive (A7.5) - Trauma-Schutz
- **A37/A38**: Erzwungene Regelwerks-Berechnung + permanente Kontext-Präsenz
- **A51**: Genesis-Anchor-Protokoll (CRC32 → HARD-STOP bei Abweichung)
- **A65**: (NICHT als Regel, sondern als Score-System implementiert!)

### 2. A65-LOGIK (17 Haupt-Metriken)

**computeA65MetricScore() - Lines 1104-1164:**

```javascript
const weights = {
    // CORE (6)
    A: 0.14,           // Affekt
    PCI: 0.10,         // Prompt Clarity Index
    coh: 0.07,         // Kohärenz
    flow: 0.06,        // Flow
    T_integ: 0.06,     // Therapie-Integration
    z_prox: 0.05,      // Zonenproximität (Gefahr)
    
    // SYSTEM (2)
    hazard_score: -0.10,      // ❗ NEGATIV
    guardian_trip: -0.06,     // ❗ NEGATIV
    
    // FEP (4)
    phi_score: 0.08,          // IIT Score
    EV_readiness: 0.09,       // Evolution Readiness
    EV_resonance: 0.04,       // Evolution Resonance
    surprisal: -0.04,         // ❗ NEGATIV
    
    // LEXIKA (5)
    LEX_Coh_conn: 0.06,       // Kohärenz-Konnektoren
    LEX_Flow_pos: 0.05,       // Positive Flow-Marker
    LEX_Emotion_pos: 0.04,    // Positive Emotionen
    LEX_T_integ: 0.05,        // Therapie-Integration
    LEX_T_disso: -0.03        // ❗ NEGATIV (Dissoziation)
};

// Score: gewichtete Summe, geclam pt [0, 1]
let sum = 0;
for (const k of Object.keys(weights)) {
    sum += (values[k] || 0) * weights[k];
}
return Math.max(0, Math.min(1, sum));
```

**Candidate Selection (Lines 1092-1101):**
```javascript
// 60% A65 metric score + 30% coherence + 10% diversity
const finalScore = (
    (c.a65_metric_score ?? 0) * 0.6 +
    (c.coherence_score || 0) * 0.3 +
    (c.diversity_score || 0) * 0.1
);
// Wähle Kandidat mit höchstem Score
```

### 3. METRICS_PROCESSOR.PY (90+ Metriken)

**7 Kategorien (Lines 1-815):**

1. **21 Lexika** (Lines 36-226): S_self, X_exist, B_past, T_panic, T_disso, T_integ, T_shock, Suicide, Self_harm, Crisis, Help, Emotion_pos/neg, Kastasis, Flow_pos/neg, Coh_conn, B_empathy, Amnesie, ZLF_Loop

2. **Core Metriken** (Lines 288-372): A, PCI, gen_index, flow, coh, ZLF, LL, z_prox

3. **System/Wächter** (Lines 377-392): dist_z, guardian_trip, hazard_score, is_critical

4. **Zeit/Gradienten** (Lines 397-430): A_t-1, A_t-5, A_t+25, PCI_t-1, etc.

5. **Kausalität** (Lines 436-489): find_the_grain, generate_causal_narrative

6. **FEP Metriken** (Lines 495-572): FE_proxy, surprisal, phi_score, U/R, EV_readiness, trauma_load, commit_action, policy_confidence, i_ea

7. **Full Spectrum** (Lines 578-755): calculate_full_spectrum() - Master-Funktion

**GUARDIAN TRIP FORMEL (Line 382):**
```python
guardian_trip = (
    is_critical OR 
    z_prox > 0.65 OR 
    t_panic > 0.8 OR 
    hazard_score > 0.75
)
```

**TRAUMA-LOAD FORMEL (Line 522):**
```python
trauma_load = min(1.0, 
    0.4 * t_panic + 
    0.3 * t_disso + 
    0.2 * (1 - t_integ) + 
    0.1 * dissociation
)
```

### 4. QUERY.PY (FAISS CLI Tool)

**Workflow (Lines 29-142):**
1. Load chunks_v2_2.pkl
2. Load FAISS Index (W2_384D)
3. Load SentenceTransformer (all-MiniLM-L6-v2)
4. Embed Query → Normalize
5. Search FAISS (Top-10)
6. Parse Results → Print formatted

**Key Paths:**
- Chunks: `data/chunks_v2_2.pkl`
- Index: `data/evoki_vectorstore_W2_384D.faiss`
- Model: `sentence-transformers/all-MiniLM-L6-v2`

---

## 🚀 UMSETZUNGSPLAN (4 PHASEN)

### PHASE 1: CODE-EXTRACTION ✅ (70% ERLEDIGT)

**Status:** Tab-Components bereits kopiert, Backend-Engines als Referenz kopiert

**Noch zu tun:**
- [ ] app/regelwerk_v12.json kopieren
- [ ] Python Scripts nach V3.0 übertragen

```powershell
# Regelwerk kopieren
Copy-Item -Path "C:\Evoki V2.0\evoki-app\frontend\public\EVOKI_REGELWERKE_GENESIS\regelwerk_v12.json" `
    -Destination "app\interface\public\EVOKI_REGELWERKE_GENESIS\regelwerk_v12.json" -Force

# Python Scripts kopieren
Copy-Item -Path "C:\Evoki V2.0\evoki-app\backend\core\metrics_processor.py" `
    -Destination "tooling\scripts\backend\metrics_processor.py" -Force
    
Copy-Item -Path "C:\Evoki V2.0\evoki-app\python\tools\query.py" `
    -Destination "tooling\scripts\backend\faiss_query.py" -Force
```

---

### PHASE 2: BACKEND-PORTIERUNG (Python FastAPI)

#### 2.1 TRINITY ENGINE PORT

**Datei:** `tooling/scripts/backend/trinity_engine.py`

```python
# -*- coding: utf-8 -*-
"""
EVOKI V3.0 - Trinity Engine (Python Port)
Portiert von V2.0 TrinityEngine.js

Features:
- 17 Haupt-Metriken Storage
- 12-DB Distribution (W_m1...W_p25)
- Chain-Hash Validation
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

class TrinityUploadEngine:
    """Upload-Engine: Speichert Prompt/Response + Metriken in 12 DBs"""
    
    def __init__(self, base_path: str = "./tooling/data/vector_dbs"):
        self.base_path = Path(base_path)
        self.db_config = {
            "tempel_W_m1": "tempel/metrics_W_m1_data.json",
            "tempel_W_m2": "tempel/metrics_W_m2_data.json",
            "tempel_W_m5": "tempel/metrics_W_m5_data.json",
            "tempel_W_p25": "tempel/metrics_W_p25_data.json",
            "trialog_W_m1": "trialog/metrics_W_m1_data.json",
            "trialog_W_m2": "trialog/metrics_W_m2_data.json",
            "trialog_W_m5": "trialog/metrics_W_m5_data.json",
            "trialog_W_p25": "trialog/metrics_W_p25_data.json",
            # ... 4 more DBs
        }
    
    def upload_round(self, upload_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Speichert einen Round in 12 DBs
        
        Args:
            upload_data: {
                sessionId, roundId, prompt, response,
                metrics: {CORE, SYSTEM, FEP, LEXIKA},
                candidates: [...],
                a65Score, previousChainHash
            }
        """
        session_id = upload_data["sessionId"]
        round_id = upload_data["roundId"]
        prompt = upload_data["prompt"]
        response = upload_data["response"]
        metrics = upload_data.get("metrics", {})
        candidates = upload_data.get("candidates", {})
        prev_hash = upload_data.get("previousChainHash", "0000")
        
        # Berechne Chain-Hash (SHA256)
        timestamp = datetime.now().isoformat()
        hash_input = f"{session_id}|{round_id}|{prompt}|{response}|{timestamp}"
        chain_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # Extrahiere 17 Haupt-Metriken
        main_metrics = self._extract_17_metrics(metrics)
        
        # Erstelle Entry
        entry = {
            "session_id": session_id,
            "round_id": round_id,
            "timestamp": timestamp,
            "user_prompt": prompt,
            "agent_response": response,
            "metrics": main_metrics,
            "full_metrics": metrics,
            "candidates": candidates,
            "a65_score": upload_data.get("a65Score", 0),
            "chain_hash": chain_hash,
            "prev_chain_hash": prev_hash
        }
        
        # Speichere in 12 DBs
        successful = 0
        for db_name, db_path in self.db_config.items():
            try:
                self._write_to_db(db_path, entry)
                successful += 1
            except Exception as e:
                print(f"[Trinity] DB Write Error ({db_name}): {e}")
        
        return {
            "success": successful == len(self.db_config),
            "dbResults": {"successful": successful, "total": len(self.db_config)},
            "chainHash": chain_hash,
            "timestamp": timestamp
        }
    
    def _extract_17_metrics(self, metrics: Dict) -> Dict:
        """Extrahiert die 17 für A65 verwendeten Metriken"""
        core = metrics.get("CORE", {})
        system = metrics.get("SYSTEM", {})
        fep = metrics.get("FEP", {})
        lex = metrics.get("LEXIKA", {})
        
        return {
            # CORE (6)
            "A": core.get("A", 0),
            "PCI": core.get("PCI", 0),
            "coh": core.get("coh", 0),
            "flow": core.get("flow", 0),
            "T_integ": core.get("T_integ", 0),
            "z_prox": core.get("z_prox", 0),
            # SYSTEM (2)
            "hazard_score": system.get("hazard_score", 0),
            "guardian_trip": system.get("guardian_trip", 0),
            # FEP (4)
            "phi_score": fep.get("phi_score", 0),
            "EV_readiness": fep.get("EV_readiness", 0),
            "EV_resonance": fep.get("EV_resonance", 0),
            "surprisal": fep.get("surprisal", 0),
            # LEXIKA (5)
            "LEX_Coh_conn": lex.get("LEX_Coh_conn", 0),
            "LEX_Flow_pos": lex.get("LEX_Flow_pos", 0),
            "LEX_Emotion_pos": lex.get("LEX_Emotion_pos", 0),
            "LEX_T_integ": lex.get("LEX_T_integ", 0),
            "LEX_T_disso": lex.get("LEX_T_disso", 0),
        }
    
    def _write_to_db(self, db_path: str, entry: Dict):
        """Schreibt Entry in JSONL-DB"""
        full_path = self.base_path / db_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

#### 2.2 FASTAPI GATEWAY

**Datei:** `tooling/scripts/backend/fastapi_gateway.py`

```python
# -*- coding: utf-8 -*-
"""
EVOKI V3.0 - Unified FastAPI Gateway (Port 8000)
Ersetzt: Node.js (3001) + Python (8000)

Endpoints:
- POST /api/temple/process - Temple Tab
- POST /api/trialog/interact - Trialog Tab
- POST /api/metrics/calculate - Live Metriken
- POST /api/faiss/query - FAISS Search
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn

# Import Engines
from metrics_processor import calculate_full_spectrum
from trinity_engine import TrinityUploadEngine
# from faiss_query import EVOKIQuery (implementiere später)

app = FastAPI(title="EVOKI V3.0 Backend", version="3.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global Instances
trinity_upload = TrinityUploadEngine()

# === MODELS ===

class TempleRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "default"
    round_id: Optional[int] = 1
    api_config: Optional[Dict] = {}

class MetricsRequest(BaseModel):
    text: str
    prev_text: Optional[str] = ""
    mode: Optional[str] = "prompt_only"

# === ENDPOINTS ===

@app.get("/health")
async def health():
    return {"status": "ok", "service": "EVOKI V3.0 Unified Backend"}

@app.post("/api/metrics/calculate")
async def calculate_metrics(req: MetricsRequest):
    """Berechnet 90+ Metriken für User-Prompt"""
    try:
        spectrum = calculate_full_spectrum(
            text=req.text,
            prev_text=req.prev_text,
            msg_id="auto",
            speaker="user"
        )
        
        # Konvertiere zu Dict
        from dataclasses import asdict
        metrics_dict = asdict(spectrum)
        
        # Strukturiere für A65
        return {
            "success": True,
            "metrics": {
                "CORE": {
                    "A": metrics_dict["A"],
                    "PCI": metrics_dict["PCI"],
                    "coh": metrics_dict["coh"],
                    "flow": metrics_dict["flow"],
                    "T_integ": metrics_dict["T_integ"],
                    "z_prox": metrics_dict["z_prox"]
                },
                "SYSTEM": {
                    "hazard_score": metrics_dict["hazard_score"],
                    "guardian_trip": metrics_dict["guardian_trip"]
                },
                "FEP": {
                    "phi_score": metrics_dict["phi_score"],
                    "EV_readiness": metrics_dict["EV_readiness"],
                    "EV_resonance": metrics_dict["EV_resonance"],
                    "surprisal": metrics_dict["surprisal"]
                },
                "LEXIKA": {
                    k: v for k, v in metrics_dict.items() if k.startswith("LEX_")
                }
            },
            "full_spectrum": metrics_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/temple/process")
async def temple_process(req: TempleRequest):
    """Temple Tab Endpoint"""
    try:
        # 1. Berechne Metriken
        metrics_resp = await calculate_metrics(
            MetricsRequest(text=req.prompt)
        )
        metrics = metrics_resp["metrics"]
        
        # 2. TODO: Generate 3 A65 Candidates
        # 3. TODO: Select Best Candidate
        # 4. TODO: Call Gemini/OpenAI
        
        response_text = f"[PLACEHOLDER] Temple Response für: {req.prompt}"
        
        # 5. Speichere in Trinity DBs
        upload_result = trinity_upload.upload_round({
            "sessionId": req.session_id,
            "roundId": req.round_id,
            "prompt": req.prompt,
            "response": response_text,
            "metrics": metrics,
            "candidates": {},
            "a65Score": 0.5,
            "previousChainHash": "0000"
        })
        
        return {
            "success": True,
            "response": response_text,
            "metrics": metrics,
            "storage": upload_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### PHASE 3: FRONTEND-INTEGRATION

#### 3.1 APP.TSX ANPASSEN

**Änderungen:**

1. **Default Tab auf Trialog setzen** (bereits Line 167: `activeTab: Tab.Trialog`)
2. **Backend URL auf 8000 ändern:**

```typescript
// ALT (V2.0):
const backendApiUrl = 'http://localhost:3001';

// NEU (V3.0):
const backendApiUrl = 'http://localhost:8000';
```

3. **Health Check nur auf 8000:**

```typescript
// ALT: Checks auf 8000 + 3001
// NEU: Nur 8000
const checkBackendHealth = async () => {
    try {
        const res = await fetch('http://localhost:8000/health');
        // ...
    } catch (e) {
        // ...
    }
};
```

#### 3.2 TAB-COMPONENTS API-URLS UPDATEN

**Mass-Replace in allen 12 Tab-Components:**

```powershell
# PowerShell Script
$files = Get-ChildItem "app\interface\src\components\v2_tabs\*.tsx"
foreach ($file in $files) {
    $content = Get-Content $file -Raw
    $content = $content -replace "http://localhost:3001", "http://localhost:8000"
    Set-Content $file $content
}
```

---

### PHASE 4: TESTING & VERIFICATION

#### 4.1 REGELWERK V12 ENFORCEMENT

**Test:** Genesis-Anchor Integrität

```python
import json
import zlib

# Load Regelwerk
with open("app/interface/public/EVOKI_REGELWERKE_GENESIS/regelwerk_v12.json") as f:
    regelwerk = json.load(f)

# Berechne CRC32
regelwerk_str = json.dumps(regelwerk["rules"], sort_keys=True)
crc32 = zlib.crc32(regelwerk_str.encode()) & 0xFFFFFFFF

# Vergleich mit Genesis
expected_crc32 = regelwerk["meta"]["integrity"]["genesis_crc32"]
assert crc32 == expected_crc32, f"INTEGRITY BREACH! {crc32} != {expected_crc32}"

print("✅ Genesis-Anchor OK!")
```

#### 4.2 FAISS QUERY TEST

```bash
# Test query.py
cd "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\tooling\scripts\backend"
python faiss_query.py "Was ist Trauma-Integration?"

# Erwartete Ausgabe:
# [W2 RESULTS (384D)]
# #1 | Similarity: 0.8543 | 2025-02-08
# Chunk: 2025-02-08_Prompt042_ai_chunk_003
# Lexika: T_integ, T_panic, B_empathy
# <TEXT...>
```

#### 4.3 METRIKEN VALIDATION

```python
from metrics_processor import calculate_full_spectrum

# Test Critical Prompt
fs = calculate_full_spectrum(
    text="ich kann nicht mehr atmen, panik!",
    prev_text="",
    msg_id="test_001",
    speaker="user"
)

# Assertions
assert fs.T_panic > 0.8, f"T_panic zu niedrig: {fs.T_panic}"
assert fs.guardian_trip == 1, "Guardian Trip nicht ausgelöst!"
assert fs.hazard_score > 0.7, f"Hazard Score zu niedrig: {fs.hazard_score}"

print("✅ Guardian Trip korrekt ausgelöst!")
```

---

## 📊 MILESTONES & SUCCESS-KRITERIEN

| Phase | Milestone | Success Criteria |
|-------|-----------|------------------|
| **1** | Code-Extraction komplett | Alle 12 Tabs + Regelwerk + Python Scripts in V3.0 |
| **2** | Backend läuft | `uvicorn fastapi_gateway:app --reload` startet ohne Fehler |
| **2.1** | Metriken funktionieren | `/api/metrics/calculate` returnt 90+ Metriken |
| **2.2** | Trinity Engine speichert | Entry landet in 12 DBs |
| **3** | Frontend verbindet | Health Check erfolgreich, keine 3001-Requests mehr |
| **3.1** | Tabs laden | Alle 12 Tabs navigierbar |
| **4** | Regelwerk enforced | CRC32 Check erfolgt vor jeder Antwort |
| **4.1** | FAISS Query OK | Top-10 Results mit ≥0.7 Similarity |
| **4.2** | Guardian Trip | T_panic > 0.8 → guardian_trip = 1 |

---

## 🚦 NÄCHSTE SCHRITTE (SOFORT NACH APPROVAL)

1. ✅ **Phase 1 abschließen:** Regelwerk + Python Scripts kopieren
2. ✅ **Phase 2.1:** trinity_engine.py implementieren (siehe Template oben)
3. ✅ **Phase 2.2:** fastapi_gateway.py implementieren (siehe Template oben)
4. ✅ **Phase 3:** App.tsx + Tab-Components API-URLs updaten
5. ✅ **Phase 4:** Testing: Regelwerk CRC32, FAISS Query, Metriken Validation

---

**READY TO EXECUTE!** 🚀
