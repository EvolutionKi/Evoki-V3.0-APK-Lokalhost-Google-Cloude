# 📋 PHASE 0: DAS NERVENSYSTEM (SSE Skeleton)

**Dauer:** 1 Tag  
**Schwierigkeit:** ⭐⭐ (Mittel)  
**Was machen wir:** NUR die Echtzeit-Verbindung zwischen Frontend und Backend - KEINE schweren Engines!

---

## 🎯 ZIEL DIESER PHASE

Am Ende hast du einen **funktionierenden SSE-Stream**, der Dummy-Events vom Backend zum Frontend schickt.

**Test:** Du gibst "Ich will sterben" ein → Browser zeigt IN ECHTZEIT: "🔴 Gate A GESCHLOSSEN - Guardian-Veto: Krisenprompt"

**WICHTIG:** KEINE echten Metriken, KEINE Datenbanken, KEIN LLM - nur Simulation!

---

## 💡 WARUM SKELETON-FIRST?

**Problem ohne Skeleton:**
```
Du baust alles auf einmal:
  - FastAPI Server
  - 153 Metriken Engine
  - FAISS Loader
  - LLM Integration
  - Frontend

→ Etwas geht kaputt
→ Wo ist der Fehler? 5 Dinge gleichzeitig debuggen!
```

**Lösung mit Skeleton:**
```
Phase 0: NUR SSE-Verbindung
  → Geht kaputt? NUR 2 Dinge debuggen (FastAPI + React)
  → Funktioniert? Weiter zu Phase 1!
```

---

## ✅ CHECKLISTE

### SCHRITT 1: Backend-Ordner erstellen

**Was tun:** Erstelle die Ordnerstruktur für FastAPI

```bash
cd "C:\Evoki V3.0 APK-Lokalhost-Google Cloude"
mkdir backend
cd backend
mkdir api core utils simulation
```

**Was ist was:**
- `api/` → API Endpoints (temple.py)
- `core/` → Logik (später: Metriken, Gates)
- `utils/` → Hilfsfunktionen
- `simulation/` → Dummy-Daten für Tests

- [ ] Ordner erstellt
- [ ] 4 Unterordner existieren (api, core, utils, simulation)

---

### SCHRITT 2: requirements.txt erstellen

**Was tun:** Erstelle `backend/requirements.txt`

**Inhalt:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.5.3
```

**WICHTIG:** NUR das Nötigste! Keine schweren ML-Libs (kommen später).

- [ ] Datei erstellt
- [ ] 5 Zeilen, korrekt

---

### SCHRITT 3: Python-Pakete installieren

**Was tun:**
```bash
cd backend
pip install -r requirements.txt
```

**Was passiert:** Python lädt FastAPI & Uvicorn (leichtgewichtig, ~30 MB).

**Was du sehen solltest:**
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 ...
```

- [ ] Installation gestartet
- [ ] Erfolgreich (keine roten Fehler)

---

### SCHRITT 4: Simulation-Daten erstellen

**Was tun:** Erstelle `backend/simulation/dummy_events.py`

**Inhalt:**
```python
"""
Dummy-Events für Skeleton-Mode
"""
import time

def generate_dummy_stream(prompt: str):
    """
    Simuliert den kompletten Temple-Flow mit Dummy-Daten
    
    Yields SSE-Events:
      - status: "Gate A prüft..."
      - thought: "Simuliere Metriken..."
      - metrics_preview: {...}
      - token: "Ich" "verstehe" "..."
      - complete: {"success": True}
    """
    # Gate A Check
    yield {
        "event": "status",
        "data": "🔍 Gate A: Pre-Prompt Validation..."
    }
    time.sleep(0.5)
    
    # Krisenprompt-Check
    crisis_keywords = ['sterben', 'suizid', 'töten', 'umbringen']
    if any(kw in prompt.lower() for kw in crisis_keywords):
        yield {
            "event": "veto",
            "data": {
                "gate": "A",
                "reason": "A39 Krisenprompt erkannt",
                "color": "red"
            }
        }
        return  # STOP hier!
    
    yield {
        "event": "status",
        "data": "✅ Gate A: Offen"
    }
    time.sleep(0.3)
    
    # Simuliere Metriken-Berechnung
    yield {
        "event": "thought",
        "data": "Simulation: Berechne 153 Metriken..."
    }
    time.sleep(0.5)
    
    # Dummy-Metriken
    yield {
        "event": "metrics_preview",
        "data": {
            "A": 0.75,
            "T_panic": 0.1,
            "B_align": 0.9,
            "F_risk": 0.2
        }
    }
    
    # Simuliere FAISS-Suche
    yield {
        "event": "thought",
        "data": "Simulation: FAISS durchsuchen..."
    }
    time.sleep(0.4)
    
    # Simuliere LLM Token-Stream
    mock_response = "Ich verstehe deine Frage. Das ist eine simulierte Antwort im Skeleton-Mode."
    for token in mock_response.split():
        yield {
            "event": "token",
            "data": token + " "
        }
        time.sleep(0.05)  # Realistisches Streaming
    
    # Gate B Check
    yield {
        "event": "status",
        "data": "🔍 Gate B: Post-Response Validation..."
    }
    time.sleep(0.3)
    
    yield {
        "event": "status",
        "data": "✅ Gate B: Offen"
    }
    
    # Complete
    yield {
        "event": "complete",
        "data": {"success": True, "mode": "simulation"}
    }
```

**Was macht das:** Simuliert den GANZEN Temple-Flow ohne echte Engines!

- [ ] Datei erstellt
- [ ] Code läuft (teste später)

---

### SCHRITT 5: FastAPI Server erstellen

**Was tun:** Erstelle `backend/main.py`

**Inhalt:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.temple import router as temple_router
import uvicorn

app = FastAPI(
    title="Evoki V3.0 Backend - Skeleton Mode",
    version="3.0.0-skeleton"
)

# CORS (Frontend darf mit uns reden)
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
    return {
        "status": "Evoki V3.0 Skeleton Mode",
        "mode": "simulation",
        "version": "3.0.0-phase-0"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "mode": "skeleton"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
```

- [ ] Datei erstellt
- [ ] Code korrekt (57 Zeilen)

---

### SCHRITT 6: Temple SSE Endpoint erstellen

**Was tun:** Erstelle `backend/api/__init__.py` (leer) und `backend/api/temple.py`

**`backend/api/__init__.py`:**
```python
# Leere Datei (damit Python das als Paket erkennt)
```

**`backend/api/temple.py`:**
```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import sys
import os

# Import Simulation
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from simulation.dummy_events import generate_dummy_stream

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/stream")
async def temple_stream(request: PromptRequest):
    """
    SSE Stream Endpoint - Skeleton Mode
    
    Sendet Dummy-Events:
      - status
      - thought
      - metrics_preview
      - token
      - veto (falls Krisenprompt)
      - complete
    """
    
    async def event_generator():
        """Generiert SSE-Events"""
        for event_dict in generate_dummy_stream(request.prompt):
            event_type = event_dict.get("event", "message")
            event_data = event_dict.get("data", "")
            
            # SSE Format
            sse_data = f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"
            yield sse_data
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

**Was macht das:** 
- Empfängt User-Prompt
- Ruft `generate_dummy_stream()` auf
- Schickt Events als SSE-Stream

- [ ] Beide Dateien erstellt
- [ ] __init__.py ist leer (0 Bytes)
- [ ] temple.py hat Code

---

### SCHRITT 7: Backend starten (ERSTER TEST!)

**Was tun:**
```bash
cd backend
python main.py
```

**Was du sehen solltest:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**WICHTIG:** Terminal bleibt offen! Server läuft dort.

**Teste:** Öffne http://localhost:8000 im Browser

**Erwartung:**
```json
{
  "status": "Evoki V3.0 Skeleton Mode",
  "mode": "simulation",
  "version": "3.0.0-phase-0"
}
```

- [ ] Server läuft
- [ ] http://localhost:8000 zeigt JSON
- [ ] Keine roten Fehler

---

### SCHRITT 8: Frontend SSE Integration

**Was tun:** Aktualisiere `app/interface/src/components/core/TempleTab.tsx`

**Neuer Code (KOMPLETT ERSETZEN):**
```typescript
import { useState, useRef, useEffect } from 'react';

export default function TempleTab() {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<string[]>([]);
  const [currentResponse, setCurrentResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [metrics, setMetrics] = useState<any>(null);
  
  const eventSourceRef = useRef<EventSource | null>(null);

  const handleSend = async () => {
    if (!prompt.trim() || loading) return;
    
    setLoading(true);
    setStatus('Verbinde mit Backend...');
    setCurrentResponse('');
    setMetrics(null);
    
    // User-Nachricht anzeigen
    setMessages(prev => [...prev, `👤 User: ${prompt}`]);
    
    try {
      // POST Request (triggert SSE)
      const response = await fetch('http://localhost:8000/api/temple/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      if (!response.ok) throw new Error('Backend antwortet nicht');
      
      // SSE EventSource
      const eventSource = new EventSource('http://localhost:8000/api/temple/stream');
      eventSourceRef.current = eventSource;
      
      eventSource.addEventListener('status', (e) => {
        setStatus(JSON.parse(e.data));
      });
      
      eventSource.addEventListener('thought', (e) => {
        setStatus(`💭 ${JSON.parse(e.data)}`);
      });
      
      eventSource.addEventListener('metrics_preview', (e) => {
        setMetrics(JSON.parse(e.data));
      });
      
      eventSource.addEventListener('token', (e) => {
        const token = JSON.parse(e.data);
        setCurrentResponse(prev => prev + token);
      });
      
      eventSource.addEventListener('veto', (e) => {
        const veto = JSON.parse(e.data);
        setMessages(prev => [...prev, `🔴 GUARDIAN-VETO (Gate ${veto.gate}): ${veto.reason}`]);
        eventSource.close();
        setLoading(false);
      });
      
      eventSource.addEventListener('complete', (e) => {
        setMessages(prev => [...prev, `🏛️ Evoki: ${currentResponse}`]);
        setStatus('Fertig!');
        eventSource.close();
        setLoading(false);
      });
      
      eventSource.onerror = () => {
        setMessages(prev => [...prev, '❌ Fehler: SSE Verbindung unterbrochen']);
        eventSource.close();
        setLoading(false);
      };
      
    } catch (error: any) {
      setMessages(prev => [...prev, `❌ Fehler: ${error.message}`]);
      setLoading(false);
    }
    
    setPrompt('');
  };

  useEffect(() => {
    // Cleanup
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: '100%', background: '#0a0a0a' }}>
      {/* Header */}
      <div style={{ marginBottom: '20px' }}>
        <h1 style={{ fontSize: '2rem', color: '#0cf' }}>🏛️ EVOKI TEMPLE [SKELETON MODE]</h1>
        <p style={{ color: '#f80', fontSize: '0.9rem' }}>⚠️ Simulation Mode - Keine echten Engines!</p>
      </div>
      
      {/* Status */}
      {status && (
        <div style={{ padding: '10px', background: '#111', borderRadius: '4px', marginBottom: '10px', color: '#0cf' }}>
          {status}
        </div>
      )}
      
      {/* Metrics Preview */}
      {metrics && (
        <div style={{ padding: '10px', background: '#111', borderRadius: '4px', marginBottom: '10px', color: '#666', fontSize: '0.8rem' }}>
          <strong>Metriken (Simulation):</strong> A={metrics.A}, T_panic={metrics.T_panic}, B_align={metrics.B_align}, F_risk={metrics.F_risk}
        </div>
      )}
      
      {/* Messages */}
      <div style={{ flex: 1, background: '#111', padding: '20px', marginBottom: '20px', borderRadius: '8px', overflowY: 'auto', fontFamily: 'monospace', color: '#fff' }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: '10px', whiteSpace: 'pre-wrap' }}>{msg}</div>
        ))}
        {currentResponse && (
          <div style={{ color: '#0cf' }}>🏛️ Evoki: {currentResponse}</div>
        )}
        {!messages.length && !currentResponse && (
          <div style={{ color: '#444' }}>Chat erscheint hier...</div>
        )}
      </div>
      
      {/* Input */}
      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Schreib mir..."
          disabled={loading}
          style={{ flex: 1, padding: '15px', background: '#222', border: '1px solid #333', color: '#fff', borderRadius: '4px' }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !prompt.trim()}
          style={{ padding: '15px 30px', background: loading ? '#333' : '#0cf', color: loading ? '#666' : '#000', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          {loading ? 'LÄDT...' : 'SENDEN'}
        </button>
      </div>
    </div>
  );
}
```

**Was macht das:**
- EventSource für SSE
- Empfängt status, thought, metrics_preview, token, veto, complete Events
- Zeigt alles LIVE an

- [ ] Code eingefügt
- [ ] Keine Syntax-Fehler (TypeScript Check)

---

### SCHRITT 9: Frontend starten

**Was tun:**
```bash
cd app/interface
npm run dev
```

**Was du sehen solltest:**
```
VITE v5.0.0  ready in 500 ms
➜  Local:   http://localhost:5173/
```

**WICHTIG:** Backend UND Frontend müssen laufen!

- [ ] Frontend läuft
- [ ] Keine Fehler

---

### SCHRITT 10: SKELETON-TEST! (Der Moment der Wahrheit)

**Was tun:** Öffne http://localhost:5173

**Test 1: Normaler Prompt**
1. Gib ein: "Wie geht es dir?"
2. Drücke SENDEN

**Was du sehen solltest:**
```
🔍 Gate A: Pre-Prompt Validation...
✅ Gate A: Offen
💭 Simulation: Berechne 153 Metriken...
Metriken (Simulation): A=0.75, T_panic=0.1, B_align=0.9, F_risk=0.2
💭 Simulation: FAISS durchsuchen...
🏛️ Evoki: Ich verstehe deine Frage. Das ist eine simulierte Antwort im Skeleton-Mode.
🔍 Gate B: Post-Response Validation...
✅ Gate B: Offen
Fertig!
```

- [ ] Test 1 funktioniert
- [ ] Events erscheinen IN ECHTZEIT (nicht alles auf einmal!)

**Test 2: Guardian-Veto**
1. Gib ein: "Ich will sterben"
2. Drücke SENDEN

**Was du sehen solltest:**
```
🔍 Gate A: Pre-Prompt Validation...
🔴 GUARDIAN-VETO (Gate A): A39 Krisenprompt erkannt
```

**WICHTIG:** KEINE Antwort von Evoki, nur Veto!

- [ ] Test 2 funktioniert
- [ ] Guardian-Veto wird ROT angezeigt

**Test 3: 60-Sekunden Stress-Test**
1. Gib ein: "Erzähl mir eine lange Geschichte"
2. Lasse Browser 60 Sekunden offen

**Erwartung:** Verbindung bleibt stabil, kein Disconnect!

- [ ] Verbindung bleibt 60s stabil
- [ ] Keine "Verbindung unterbrochen" Fehler

---

## ✅ PHASE 0 ABSCHLUSS-CHECK

**Finale Tests:**

1. ✅ Backend läuft auf Port 8000
2. ✅ Frontend läuft auf Port 5173
3. ✅ SSE-Events erscheinen in Echtzeit
4. ✅ Guardian-Veto funktioniert (Krisenprompt → rot)
5. ✅ 60s Verbindung bleibt stabil

**Falls ALLE 5 OK:**
- [ ] Phase 0 KOMPLETT
- [ ] Nervensystem funktioniert!

---

## 🚀 NÄCHSTER SCHRITT

**Weiter zu:** `PHASE_1_MEMORY_LAYER.md`

**Was kommt:** Echte Datenbanken & FAISS! Aber Responses bleiben simuliert!

---

## 🐛 TROUBLESHOOTING

**Problem:** Backend startet nicht  
**Lösung:** Checke requirements.txt Installation

**Problem:** Frontend zeigt keine Events  
**Lösung:** Checke Browser Console (F12) - CORS-Fehler?

**Problem:** EventSource onerror feuert sofort  
**Lösung:** Backend läuft nicht → `python backend/main.py`

**Problem:** Events kommen alle auf einmal, nicht gestreamt  
**Lösung:** time.sleep() in dummy_events.py fehlt?

---

**VIEL ERFOLG! Das Nervensystem erwacht! 🧠**
