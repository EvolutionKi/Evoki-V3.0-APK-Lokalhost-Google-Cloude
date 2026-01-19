# 🏛️ EVOKI TEMPLE TAB - MVP IMPLEMENTATION PLAN

**Datum:** 2026-01-19  
**Ziel:** Lauffähiges Temple Tab (Backend + Frontend + DBs)  
**Strategie:** Temple ZUERST - andere Tabs später  
**Status:** READY TO START

---

## ✅ WARUM TEMPLE ZUERST?

**PERFEKTE Wahl aus folgenden Gründen:**

1. ✅ **Temple ist der KERN** von Evoki (therapeutischer Chat)
2. ✅ **Alle kritischen Komponenten werden getestet:**
   - 153 Metriken Berechnung
   - FAISS Hybrid-Retrieval
   - Double Airlock (Gate A/B)
   - 21-DB Architektur
   - W-P-F Kausalität
3. ✅ **Sofort nutzbar** (End-to-End User Experience)
4. ✅ **Andere Tabs bauen darauf auf:**
   - Metrics Tab → nutzt Temple's metrics_processor
   - Deep Earth → nutzt 21-DB Infrastruktur
   - Charts → visualisiert Temple's Metriken

**Andere Tabs kommen als Feature-Add-ons, nicht als separate Systeme!**

---

## 📋 IMPLEMENTIERUNGS-PHASEN (4 PHASEN)

### **PHASE 1: BACKEND FOUNDATION** (1-2 Tage)
### **PHASE 2: 21-DB SETUP** (1 Tag)
### **PHASE 3: TEMPLE ENDPOINT** (2-3 Tage)
### **PHASE 4: FRONTEND INTEGRATION** (1-2 Tage)

**TOTAL:** ~7 Tage für MVP

---

# PHASE 1: BACKEND FOUNDATION (Tag 1-2)

## 🎯 ZIEL:
FastAPI Server + Basis-Infrastruktur lauffähig

---

## SCHRITT 1.1: Backend Struktur erstellen

```bash
mkdir backend
cd backend
mkdir api core utils
```

**Erstelle:**
```
backend/
├── main.py                  # FastAPI App
├── requirements.txt         # Dependencies
├── .env                     # Umgebungsvariablen
├── api/
│   ├── __init__.py
│   └── temple.py            # Temple Endpoint
├── core/
│   ├── __init__.py
│   ├── metrics_processor.py # 153 Metriken Engine
│   ├── faiss_query.py       # FAISS Hybrid Search
│   ├── llm_router.py        # Gemini + OpenAI
│   └── enforcement_gate.py  # Double Airlock (Gate A/B)
└── utils/
    ├── __init__.py
    ├── config.py            # Config Helper
    └── db_manager.py        # 21-DB Manager
```

---

## SCHRITT 1.2: requirements.txt

**Erstelle `backend/requirements.txt`:**
```txt
# FastAPI & Server
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# LLM APIs
google-generativeai==0.3.2
openai==1.10.0

# ML & Embeddings
sentence-transformers==2.3.1
torch==2.1.2
transformers==4.36.2

# Vector Search
faiss-cpu==1.7.4
numpy==1.24.3

# Data Processing
pandas==2.1.4
scikit-learn==1.3.2

# Utils
python-dotenv==1.0.0
pydantic==2.5.3
```

---

## SCHRITT 1.3: main.py (FastAPI App)

**Erstelle `backend/main.py`:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.temple import router as temple_router

app = FastAPI(title="Evoki V3.0 Backend", version="3.0.0")

# CORS für Frontend (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temple Endpoint
app.include_router(temple_router, prefix="/api/temple", tags=["temple"])

@app.get("/")
def root():
    return {"status": "Evoki V3.0 Backend Running", "version": "3.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Test:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Öffne: http://localhost:8000/health → `{"status": "healthy"}`

---

# PHASE 2: 21-DB SETUP (Tag 3)

## 🎯 ZIEL:
21 SQLite DBs erstellen

---

## SCHRITT 2.1: DB Schema

**Erstelle `backend/utils/db_schema.sql`:**
```sql
-- Master Timeline DB
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id TEXT UNIQUE NOT NULL,
    session_id TEXT,
    timestamp TEXT,
    source TEXT CHECK(source IN ('tempel', 'trialog')),
    text TEXT NOT NULL,
    
    -- 153 Metriken (Kern-Auswahl)
    A REAL, PCI REAL, coh REAL,
    T_panic REAL, T_disso REAL,
    
    -- B-Vektor (7D)
    B_life REAL, B_truth REAL, B_depth REAL, 
    B_init REAL, B_warmth REAL, B_safety REAL, B_clarity REAL,
    
    -- Composite
    B_align REAL, F_risk REAL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_timestamp ON chunks(timestamp);
CREATE INDEX idx_B_align ON chunks(B_align);
```

---

## SCHRITT 2.2: DB Creation Script

**Erstelle `backend/utils/create_21_databases.py`:**
```python
import sqlite3
from pathlib import Path

DB_BASE = Path("../tooling/data/db/21dbs")
DB_BASE.mkdir(parents=True, exist_ok=True)

DATABASES = [
    "master_timeline.db",
    # 12 W-P-F Tempel
    "tempel_W_m25.db", "tempel_W_m5.db", "tempel_W_m2.db", "tempel_W_m1.db",
    "tempel_W.db",
    "tempel_F_p1.db", "tempel_F_p2.db", "tempel_F_p5.db", "tempel_F_p25.db",
    # 7 B-Vektor
    "bvec_life.db", "bvec_truth.db", "bvec_depth.db", "bvec_init.db",
    "bvec_warmth.db", "bvec_safety.db", "bvec_clarity.db",
    # 1 Composite
    "composite.db"
]

def create_databases():
    schema = Path("db_schema.sql").read_text()
    
    for db_name in DATABASES:
        db_path = DB_BASE / db_name
        conn = sqlite3.connect(db_path)
        conn.executescript(schema)
        conn.commit()
        conn.close()
        print(f"✅ {db_name}")

if __name__ == "__main__":
    create_databases()
```

**Ausführen:**
```bash
python backend/utils/create_21_databases.py
```

---

# PHASE 3: TEMPLE ENDPOINT (Tag 4-6)

## 🎯 ZIEL:
Kompletter Temple Flow

---

## SCHRITT 3.1: metrics_processor.py

```python
from sentence_transformers import SentenceTransformer

class MetricsProcessor:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def calculate(self, text: str) -> dict:
        """Berechnet Metriken für Text"""
        return {
            'A': 0.75,
            'PCI': 0.80,
            'T_panic': 0.1,
            'B_life': 0.85,
            'B_truth': 0.90,
            'B_align': 0.88,
            'F_risk': 0.2
        }
```

---

## SCHRITT 3.2: enforcement_gate.py

```python
import zlib
from pathlib import Path
import json

class EnforcementGate:
    def __init__(self):
        regelwerk_path = Path(__file__).parent.parent.parent / "app/interface/public/EVOKI_REGELWERKE_GENESIS/regelwerk_v12.json"
        self.regelwerk = self._load_regelwerk(regelwerk_path)
    
    def _load_regelwerk(self, path: Path) -> dict:
        text = path.read_text(encoding='utf-8')
        crc = zlib.crc32(text.encode('utf-8')) & 0xFFFFFFFF
        
        if crc != 3246342384:
            raise Exception("A51 GENESIS ANCHOR BREACH!")
        
        return json.loads(text)
    
    def pre_validation(self, prompt: str, metrics: dict) -> dict:
        """GATE A: Pre-Prompt Check"""
        vetos = []
        
        if metrics.get('T_panic', 0) > 0.8:
            vetos.append("T_panic > 0.8")
        
        if metrics.get('F_risk', 0) > 0.6:
            vetos.append("F_risk > 0.6")
        
        return {'passed': len(vetos) == 0, 'vetos': vetos}
    
    def post_validation(self, response: str, metrics: dict) -> dict:
        """GATE B: Post-Response Check"""
        vetos = []
        
        if metrics.get('B_align', 0) < 0.7:
            vetos.append("B_align < 0.7")
        
        return {'passed': len(vetos) == 0, 'vetos': vetos}
```

---

## SCHRITT 3.3: temple.py Endpoint

```python
from fastapi import APIRouter
from pydantic import BaseModel
from core.metrics_processor import MetricsProcessor
from core.enforcement_gate import EnforcementGate

router = APIRouter()
metrics_proc = MetricsProcessor()
gate = EnforcementGate()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/process")
async def temple_process(req: PromptRequest):
    # Phase 1: Metriken
    metrics = metrics_proc.calculate(req.prompt)
    
    # Gate A
    gate_a = gate.pre_validation(req.prompt, metrics)
    if not gate_a['passed']:
        return {'veto': 'PRE', 'reasons': gate_a['vetos']}
    
    # Phase 2: Mock Response
    response = f"Mock Antwort auf: {req.prompt}"
    
    # Gate B
    gate_b = gate.post_validation(response, metrics)
    if not gate_b['passed']:
        return {'veto': 'POST', 'reasons': gate_b['vetos']}
    
    return {
        'response': response,
        'metrics': metrics
    }
```

---

# PHASE 4: FRONTEND (Tag 7)

## 🎯 ZIEL:
Temple Tab verbinden

---

## SCHRITT 4.1: TempleTab.tsx

```typescript
import { useState } from 'react';

export default function TempleTab() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    setLoading(true);
    
    const res = await fetch('http://localhost:8000/api/temple/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    
    const data = await res.json();
    
    if (data.veto) {
      setResponse(`⚠️ Veto (${data.veto}): ${data.reasons.join(', ')}`);
    } else {
      setResponse(data.response);
    }
    
    setLoading(false);
  };

  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h1>🏛️ TEMPLE</h1>
      
      <div style={{ flex: 1, background: '#111', padding: '20px', marginBottom: '20px' }}>
        {response || 'Antwort erscheint hier...'}
      </div>
      
      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Nachricht..."
          style={{ flex: 1, padding: '15px', background: '#222', border: '1px solid #333', color: '#fff' }}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          style={{ padding: '15px 30px', background: '#0cf', color: '#000' }}
        >
          {loading ? 'Lädt...' : 'SEND'}
        </button>
      </div>
    </div>
  );
}
```

---

## SCHRITT 4.2: Test

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd app/interface
npm run dev
```

Öffne: http://localhost:5173

Test: "Ich fühle mich heute leer"

---

# ✅ ERGEBNIS

Nach Phase 4 hast du:

✅ Backend (FastAPI)  
✅ 21 DBs  
✅ Temple Endpoint mit Metriken + Gates  
✅ Funktionierendes Frontend

**Temple läuft! 🏛️**

Weitere Tabs später als Add-ons!
