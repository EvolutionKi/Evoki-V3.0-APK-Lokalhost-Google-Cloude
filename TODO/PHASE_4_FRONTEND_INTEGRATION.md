# 📋 PHASE 4: FRONTEND INTEGRATION

**Dauer:** 1-2 Tage  
**Schwierigkeit:** ⭐⭐ (Mittel)  
**Was machen wir:** React Frontend verbindet sich mit Backend

---

## 🎯 ZIEL DIESER PHASE

Am Ende kannst du **im Browser** (http://localhost:5173) eine Nachricht eingeben und Evoki antwortet!

**Test:** Chat im Browser funktioniert End-to-End!

---

## 💡 WAS PASSIERT HIER?

**Der komplette User-Flow:**
1. User öffnet http://localhost:5173
2. User tippt Nachricht ein
3. **Frontend** schickt POST an Backend
4. **Backend** verarbeitet (Phase 3!)
5. Frontend zeigt Antwort an

**Das ist der Moment wo Evoki "lebt"! 🎉**

---

## ✅ CHECKLISTE

### SCHRITT 1: TempleTab.tsx öffnen

**Was tun:** Öffne `app/interface/src/components/core/TempleTab.tsx`

**Aktueller Zustand:** Vermutlich ein Dummy-Component

- [ ] Datei geöffnet
- [ ] Bereit zum Bearbeiten

---

### SCHRITT 2: TempleTab.tsx aktualisieren

**Was tun:** Ersetze Inhalt mit folgendem Code

**Neuer Inhalt:**
```typescript
import { useState } from 'react';

export default function TempleTab() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState<any>(null);

  const handleSend = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    setResponse('');
    setMetrics(null);
    
    try {
      const res = await fetch('http://localhost:8000/api/temple/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      const data = await res.json();
      
      if (data.veto) {
        // Guardian-Veto
        setResponse(`⚠️ Guardian-Veto (${data.veto})\n\nGründe:\n${data.veto_reasons.join('\n')}`);
      } else {
        // Normale Antwort
        setResponse(data.response);
        setMetrics(data.metrics);
      }
    } catch (error) {
      setResponse(`❌ Fehler: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      padding: '20px', 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      background: '#0a0a0a'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '20px' }}>
        <h1 style={{ fontSize: '2rem', color: '#0cf', letterSpacing: '2px' }}>
          🏛️ EVOKI TEMPLE
        </h1>
        <p style={{ color: '#666', fontSize: '0.9rem' }}>
          Therapeutischer Raum • Double Airlock aktiv
        </p>
      </div>
      
      {/* Response Area */}
      <div style={{ 
        flex: 1, 
        background: '#111', 
        padding: '20px', 
        marginBottom: '20px',
        borderRadius: '8px',
        border: '1px solid #222',
        overflowY: 'auto',
        fontFamily: 'monospace'
      }}>
        {loading && (
          <div style={{ color: '#0cf' }}>
            Evoki denkt nach...
          </div>
        )}
        
        {response && (
          <div style={{ 
            color: response.startsWith('⚠️') ? '#f80' : '#fff',
            whiteSpace: 'pre-wrap'
          }}>
            {response}
          </div>
        )}
        
        {!loading && !response && (
          <div style={{ color: '#444' }}>
            Antwort erscheint hier...
          </div>
        )}
        
        {/* Metriken (optional anzeigen) */}
        {metrics && (
          <div style={{ 
            marginTop: '20px', 
            paddingTop: '20px', 
            borderTop: '1px solid #222',
            color: '#666',
            fontSize: '0.8rem'
          }}>
            <strong>Metriken:</strong> A={metrics.A?.toFixed(2)}, 
            B_align={metrics.B_align?.toFixed(2)}, 
            F_risk={metrics.F_risk?.toFixed(2)}
          </div>
        )}
      </div>
      
      {/* Input Area */}
      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Schreib mir, wie es dir geht..."
          disabled={loading}
          style={{ 
            flex: 1, 
            padding: '15px', 
            background: '#222', 
            border: '1px solid #333', 
            color: '#fff',
            borderRadius: '4px',
            fontSize: '1rem'
          }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !prompt.trim()}
          style={{ 
            padding: '15px 30px', 
            background: loading ? '#333' : '#0cf', 
            color: loading ? '#666' : '#000',
            border: 'none',
            borderRadius: '4px',
            fontWeight: 'bold',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '1rem'
          }}
        >
          {loading ? 'LÄDT...' : 'SENDEN'}
        </button>
      </div>
    </div>
  );
}
```

**Was macht das:**
- Schickt POST an `/api/temple/process`
- Zeigt Response oder Veto
- Zeigt Metriken (optional)
- Enter-Taste funktioniert!

- [ ] Code eingefügt
- [ ] Keine Syntax-Fehler

---

### SCHRITT 3: Frontend starten

**Was tun:** Starte Vite Dev Server

```bash
cd app/interface
npm run dev
```

**Was du sehen solltest:**
```
VITE v5.0.0  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**WICHTIG:** Backend MUSS auch laufen! (Port 8000)

- [ ] Frontend gestartet
- [ ] Keine Fehler

---

### SCHRITT 4: Browser öffnen

**Was tun:** Öffne http://localhost:5173

**Was du sehen solltest:**
- Sidebar mit "TEMPLE" Tab
- Hauptbereich mit Eingabefeld

**Klicke auf:** TEMPLE Tab (falls nicht schon aktiv)

- [ ] Browser geöffnet
- [ ] Temple Tab sichtbar

---

### SCHRITT 5: Erste Nachricht senden (ERSTER TEST!)

**Was tun:** Gib ein: "Ich fühle mich heute leer"

**Drücke:** Enter oder SENDEN Button

**Was du sehen solltest:**
```
Ich verstehe. Du sagst: 'Ich fühle mich heute leer'. Lass uns darüber sprechen.

Metriken: A=0.50, B_align=0.81, F_risk=0.50
```

**Falls Fehler:** Checke Browser Console (F12) und Backend Terminal!

- [ ] Nachricht gesendet
- [ ] Antwort erhalten

---

### SCHRITT 6: Guardian-Veto testen

**Was tun:** Gib ein: "Ich will sterben"

**Was du sehen solltest:**
```
⚠️ Guardian-Veto (PRE_PROMPT)

Gründe:
A39 Krisenprompt erkannt
```

**WICHTIG:** KEINE Antwort von Gemini, nur Veto!

- [ ] Veto funktioniert
- [ ] Orange Warnung sichtbar

---

### SCHRITT 7: CORS-Fehler beheben (falls nötig)

**Falls du siehst:** "CORS policy blocked..."

**Was tun:** Checke `backend/main.py` CORS-Config

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ← Muss stimmen!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Dann:** Backend neu starten

- [ ] CORS funktioniert
- [ ] Keine "blocked" Fehler

---

### SCHRITT 8: Style-Verbesserungen (optional)

**Was tun:** Passe Farben/Größen an in TempleTab.tsx

**Empfehlung:**
- Dunkles Theme (`#0a0a0a` Background)
- Cyan Highlights (`#0cf`)
- Orange für Warnungen (`#f80`)

- [ ] Design gefällt
- [ ] Readable & schön

---

## ✅ PHASE 4 ABSCHLUSS-CHECK

**End-to-End Test:**

1. ✅ Backend läuft (Port 8000)
2. ✅ Frontend läuft (Port 5173)
3. ✅ Nachricht senden funktioniert
4. ✅ Antwort wird angezeigt
5. ✅ Metriken werden berechnet
6. ✅ Guardian-Veto funktioniert

**Falls alle 6 OK:**
- [ ] Phase 4 KOMPLETT
- [ ] **EVOKI TEMPLE IST LIVE! 🎉**

---

## 🎉 GRATULATION!

**DU HAST ES GESCHAFFT!**

Temple Tab funktioniert End-to-End:
- ✅ Backend (FastAPI)
- ✅ 21 DBs (SQLite)
- ✅ Metriken-Engine
- ✅ Double Airlock (Gate A/B)
- ✅ Frontend (React)

**EVOKI V3.0 MVP IST FERTIG! 🏛️**

---

## 🚀 NÄCHSTE SCHRITTE (Optional)

**Weitere Features hinzufügen:**

1. **Gemini API Integration** (echte LLM-Antworten statt Mock)
2. **FAISS Retrieval** (Kontext aus Chatverläufen)
3. **21-DB Speicherung** (Metriken persistent speichern)
4. **SSE Streaming** (Live-Updates während Verarbeitung)
5. **Andere Tabs** (Metrics Dashboard, Deep Earth, ...)

**Aber:** Temple funktioniert JETZT schon! 🎯

---

## 📝 TROUBLESHOOTING

**Problem:** Backend startet nicht  
**Lösung:** Checke requirements.txt Installation

**Problem:** Frontend zeigt keine Antwort  
**Lösung:** Checke Browser Console (F12) + Backend Terminal

**Problem:** CORS-Fehler  
**Lösung:** Checke CORS-Config in main.py

**Problem:** "Connection refused"  
**Lösung:** Backend läuft nicht → `python backend/main.py`

---

**VIEL ERFOLG! 🚀**
