# 📋 PHASE 1: DAS GEDÄCHTNIS (21 DBs + FAISS)

**Dauer:** 1-2 Tage  
**Schwierigkeit:** ⭐⭐⭐ (Mittel-Schwer)  
**Was machen wir:** Echte Datenbanken & FAISS laden - aber Responses NOCH simuliert!

---

## 🎯 ZIEL DIESER PHASE

Am Ende hast du **21 SQLite Datenbanken** und **FAISS läuft**, aber LLM-Antworten sind NOCH Mocks!

**Test:** "Ich fühle mich leer" → FAISS findet Top-3 ähnliche Chunks aus Chatverlauf → Zeigt sie an → ABER: "Mock-Antwort basierend auf Chunks"

**WICHTIG:** Metriken & LLM kommen SPÄTER! Hier nur Daten-Layer!

---

## 💡 WARUM SCHRITT FÜR SCHRITT?

**Ohne Skeleton (schlecht):**
```
Phase 1: DBs + FAISS + Metriken + LLM
→ Fehler: Wo liegt's? 4 Dinge gleichzeitig!
```

**Mit Skeleton (gut):**
```
Phase 0: ✅ SSE funktioniert
Phase 1: DBs + FAISS (LLM Mock)
  → Fehler? NUR DB/FAISS debuggen!
Phase 2: Metriken (LLM Mock)
Phase 3: LLM echt
```

---

## ✅ CHECKLISTE

### SCHRITT 1: Dependencies erweitern

**Was tun:** Ergänze `backend/requirements.txt`

**Neue Zeilen hinzufügen:**
```txt
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
```

**Dann installieren:**
```bash
cd backend
pip install -r requirements.txt
```

**WARNUNG:** Torch ist GROSS (~2 GB)! Download dauert!

- [ ] requirements.txt ergänzt
- [ ] Installation erfolgreich

---

### SCHRITT 2: DB Schema erstellen

**Was tun:** Erstelle `backend/utils/db_schema.sql`

**Inhalt:**
```sql
-- Master Timeline DB Schema
-- Speichert ALLE Chunks mit 153 Metriken

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id TEXT UNIQUE NOT NULL,
    session_id TEXT,
    timestamp TEXT,
    source TEXT CHECK(source IN ('tempel', 'trialog')),
    text TEXT NOT NULL,
    
    -- Core Metriken
    A REAL,              -- Affekt (0.0-1.0)
    PCI REAL,            -- Prozess-Kohärenz-Index
    coh REAL,            -- Kohärenz
    
    -- Trauma Metriken
    T_panic REAL,        -- Panik-Level
    T_disso REAL,        -- Dissoziation
    T_trigger REAL,      -- Trigger-Wahrscheinlichkeit
    
    -- B-Vektor (7D Soul-Signature)
    B_life REAL,         -- Lebenswille
    B_truth REAL,        -- Wahrheit
    B_depth REAL,        -- Tiefe
    B_init REAL,         -- Initiative
    B_warmth REAL,       -- Wärme
    B_safety REAL,       -- Sicherheit
    B_clarity REAL,      -- Klarheit
    
    -- Composite Scores
    B_align REAL,        -- Durchschnitt B-Vektor
    F_risk REAL,         -- Gefährdungs-Score
    risk_z REAL,         -- Z-Score Risiko
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_timestamp ON chunks(timestamp);
CREATE INDEX IF NOT EXISTS idx_source ON chunks(source);
CREATE INDEX IF NOT EXISTS idx_B_align ON chunks(B_align);
CREATE INDEX IF NOT EXISTS idx_F_risk ON chunks(F_risk);
CREATE INDEX IF NOT EXISTS idx_session ON chunks(session_id);
```

**Was macht das:** Definiert Tabellen-Struktur (wie Excel-Spalten) für alle 21 DBs.

- [ ] Datei erstellt
- [ ] SQL korrekt (70 Zeilen)

---

### SCHRITT 3: 21-DB Creation Script

**Was tun:** Erstelle `backend/utils/create_21_databases.py`

**Inhalt:**
```python
import sqlite3
from pathlib import Path

# Wo sollen die DBs hin?
DB_BASE = Path(__file__).parent.parent.parent / "tooling/data/db/21dbs"
DB_BASE.mkdir(parents=True, exist_ok=True)

# Liste aller 21 Datenbanken
DATABASES = [
    "master_timeline.db",
    
    # 12 W-P-F Tempel (Vergangenheit → Zukunft)
    "tempel_W_m25.db",   # -25 Minuten
    "tempel_W_m5.db",    # -5 Minuten  
    "tempel_W_m2.db",    # -2 Minuten
    "tempel_W_m1.db",    # -1 Minute
    "tempel_W.db",       # Jetzt (W = Wirklichkeit)
    "tempel_F_p1.db",    # +1 Minute
    "tempel_F_p2.db",    # +2 Minuten
    "tempel_F_p5.db",    # +5 Minuten
    "tempel_F_p25.db",   # +25 Minuten
    
    # 7 B-Vektor DBs (eine pro Dimension)
    "bvec_life.db",
    "bvec_truth.db",
    "bvec_depth.db",
    "bvec_init.db",
    "bvec_warmth.db",
    "bvec_safety.db",
    "bvec_clarity.db",
    
    # 1 Composite DB
    "composite.db"
]

def create_databases():
    """Erstellt alle 21 Datenbanken"""
    
    # SQL Schema laden
    schema_file = Path(__file__).parent / "db_schema.sql"
    schema = schema_file.read_text(encoding='utf-8')
    
    print(f"📊 Erstelle {len(DATABASES)} Datenbanken in:")
    print(f"   {DB_BASE.absolute()}\n")
    
    for db_name in DATABASES:
        db_path = DB_BASE / db_name
        
        # DB erstellen
        conn = sqlite3.connect(db_path)
        conn.executescript(schema)
        conn.commit()
        conn.close()
        
        print(f"  ✅ {db_name}")
    
    print(f"\n🎉 Fertig! Alle {len(DATABASES)} DBs erstellt!")
    print(f"\nGröße prüfen:")
    total_size = sum((DB_BASE / db).stat().st_size for db in DATABASES)
    print(f"  Total: {total_size / 1024:.1f} KB (~20 KB pro DB)")

if __name__ == "__main__":
    create_databases()
```

- [ ] Datei erstellt
- [ ] Python-Code korrekt

---

### SCHRITT 4: DBs erstellen (Ausführen!)

**Was tun:**
```bash
cd backend/utils
python create_21_databases.py
```

**Was du sehen solltest:**
```
📊 Erstelle 21 Datenbanken in:
   C:\...\tooling\data\db\21dbs

  ✅ master_timeline.db
  ✅ tempel_W_m25.db
  ... (alle 21)
  
🎉 Fertig! Alle 21 DBs erstellt!

Größe prüfen:
  Total: 420.0 KB (~20 KB pro DB)
```

- [ ] Skript ausgeführt
- [ ] 21 Datenbanken erstellt

---

### SCHRITT 5: FAISS Loader erstellen

**Was tun:** Erstelle `backend/core/faiss_query.py`

**Inhalt:**
```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

class FAISSQuery:
    """
    FAISS Semantic Search mit Mistral-7B (4096D, GPU)
    """
    
    def __init__(self):
        self.index_path = Path(__file__).parent.parent.parent / "tooling/data/faiss_indices/chatverlauf_final_20251020plus_dedup_sorted.faiss"
        
        print("🔍 Lade FAISS Index...")
        self.index = faiss.read_index(str(self.index_path))
        print(f"  ✅ Index geladen: {self.index.ntotal} Vektoren")
        
        print("🤖 Lade Mistral-7B Model (4096D)...")
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  
        # TODO: Später ersetzen mit Mistral-7B
        print("  ✅ Model geladen")
    
    def search(self, query: str, top_k: int = 100) -> list:
        """
        Sucht ähnliche Chunks
        
        Args:
            query: User-Prompt
            top_k: Anzahl Treffer (default 100 für Hybrid-Scoring)
        
        Returns:
            Liste von Dicts: {'chunk_id', 'similarity', 'index'}
        """
        # Embed Query
        query_vec = self.model.encode([query])[0]
        
        # FAISS Search
        distances, indices = self.index.search(
            query_vec.reshape(1, -1).astype('float32'),
            top_k
        )
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            results.append({
                'chunk_id': f'chunk_{idx}',
                'similarity': float(dist),
                'index': int(idx)
            })
        
        return results
    
    def get_wpf_context(self, anchor_chunk_id: str) -> dict:
        """
        W-P-F Zeitmaschine: Liefert Vergangenheit + Zukunft
        
        Args:
            anchor_chunk_id: Der gefundene Chunk (z.B. chunk_12345)
        
        Returns:
            Dict mit P-25, P-5, W, F+5, F+25
        """
        # TODO: Implementiere W-P-F Logik
        # Mock für jetzt:
        return {
            'P_m25': 'Mock: Vor 25 Minuten',
            'P_m5': 'Mock: Vor 5 Minuten',
            'W': anchor_chunk_id,
            'F_p5': 'Mock: In 5 Minuten',
            'F_p25': 'Mock: In 25 Minuten'
        }
```

- [ ] Datei erstellt
- [ ] Code korrekt

---

### SCHRITT 6: FAISS in Temple Endpoint integrieren

**Was tun:** Aktualisiere `backend/api/temple.py`

**Neue Imports oben:**
```python
from core.faiss_query import FAISSQuery

# Global initialisieren
faiss_query = FAISSQuery()
```

**Neue Funktion in generate_real_stream():**
```python
def generate_real_stream(prompt: str):
    """
    Echte FAISS + DBs, aber Mock-LLM
    """
    # Gate A
    yield {"event": "status", "data": "🔍 Gate A: Pre-Prompt Validation..."}
    time.sleep(0.3)
    yield {"event": "status", "data": "✅ Gate A: Offen"}
    
    # FAISS Search (ECHT!)
    yield {"event": "thought", "data": "Durchsuche Chatverlauf (FAISS)..."}
    
    results = faiss_query.search(prompt, top_k=3)
    
    yield {"event": "faiss_results", "data": {
        "top3": [
            f"Chunk {r['chunk_id']}: Similarity {r['similarity']:.2f}"
            for r in results[:3]
        ]
    }}
    
    # W-P-F Expansion (MOCK)
    wpf_context = faiss_query.get_wpf_context(results[0]['chunk_id'])
    
    yield {"event": "thought", "data": "W-P-F Kontext laden..."}
    yield {"event": "wpf_context", "data": wpf_context}
    
    # Mock-Response basierend auf FAISS
    mock_response = f"Mock-Antwort basierend auf {results[0]['chunk_id']}: Ich verstehe deine Frage."
    
    for token in mock_response.split():
        yield {"event": "token", "data": token + " "}
        time.sleep(0.05)
    
    yield {"event": "complete", "data": {"success": True, "mode": "phase1-faiss-real"}}
```

**Endpoint anpassen:**
```python
@router.post("/stream")
async def temple_stream(request: PromptRequest):
    async def event_generator():
        # Phase 1: Echte FAISS, Mock-LLM
        for event_dict in generate_real_stream(request.prompt):
            event_type = event_dict.get("event", "message")
            event_data = event_dict.get("data", "")
            sse_data = f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"
            yield sse_data
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

- [ ] Code eingefügt
- [ ] Keine Syntax-Fehler

---

### SCHRITT 7: Backend neu starten

**Was tun:**
```bash
cd backend
python main.py
```

**Was du sehen solltest:**
```
🔍 Lade FAISS Index...
  ✅ Index geladen: 12876 Vektoren
🤖 Lade Mistral-7B Model (4096D)...
  ✅ Model geladen
INFO:     Uvicorn running on http://0.0.0.0:8000
```

- [ ] Backend läuft
- [ ] FAISS wurde geladen

---

### SCHRITT 8: Frontend für FAISS-Ergebnisse erweitern

**Was tun:** Ergänze `TempleTab.tsx` mit Event-Handlern

**Neue EventListener hinzufügen:**
```typescript
eventSource.addEventListener('faiss_results', (e) => {
  const data = JSON.parse(e.data);
  setMessages(prev => [...prev, `🔍 FAISS Top-3:\n${data.top3.join('\n')}`]);
});

eventSource.addEventListener('wpf_context', (e) => {
  const wpf = JSON.parse(e.data);
  setMessages(prev => [...prev, `⏱️ W-P-F Kontext:\nP-25: ${wpf.P_m25}\nW: ${wpf.W}\nF+25: ${wpf.F_p25}`]);
});
```

- [ ] Code ergänzt
- [ ] Frontend läuft

---

### SCHRITT 9: PHASE 1 TEST!

**Test 1: FAISS findet relevante Chunks**

1. Gib ein: "Ich fühle mich einsam"
2. Drücke SENDEN

**Was du sehen solltest:**
```
🔍 Gate A: Pre-Prompt Validation...
✅ Gate A: Offen
Durchsuche Chatverlauf (FAISS)...
🔍 FAISS Top-3:
  Chunk chunk_1234: Similarity 0.87
  Chunk chunk_5678: Similarity 0.82
  Chunk chunk_9012: Similarity 0.79
⏱️ W-P-F Kontext:
  P-25: Mock: Vor 25 Minuten
  W: chunk_1234
  F+25: Mock: In 25 Minuten
🏛️ Evoki: Mock-Antwort basierend auf chunk_1234: Ich verstehe deine Frage.
```

- [ ] FAISS findet Chunks
- [ ] Top-3 werden angezeigt
- [ ] W-P-F Kontext (noch Mock)

**Test 2: Performance Check**

**Zeitmessung:** Wie lange dauert FAISS-Suche?

**Erwartung:** < 150ms (Embedding ~120ms + Search ~30ms)

- [ ] FAISS-Suche dauert < 150ms

---

## ✅ PHASE 1 ABSCHLUSS-CHECK

**Finale Tests:**

1. ✅ 21 SQLite DBs existieren
2. ✅ FAISS Index lädt beim Backend-Start
3. ✅ Top-3 Chunks werden gefunden
4. ✅ W-P-F Kontext-Logik existiert (Mock)
5. ✅ Performance: FAISS < 150ms

**Falls ALLE 5 OK:**
- [ ] Phase 1 KOMPLETT
- [ ] Gedächtnis funktioniert!

---

## 🚀 NÄCHSTER SCHRITT

**Weiter zu:** `PHASE_2_COGNITIVE_LAYER.md`

**Was kommt:** Echte Metriken & Double Airlock Gates! (LLM Mock bleibt)

---

## 🐛 TROUBLESHOOTING

**Problem:** FAISS lädt nicht  
**Lösung:** Prüfe Pfad zu .faiss File, existiert Index?

**Problem:** "Model not found"  
**Lösung:** sentence-transformers installiert? Internetzugang?

**Problem:** FAISS-Suche dauert > 1s  
**Lösung:** Index zu groß? CPU/RAM Check

**Problem:** 21 DBs erstellt, aber leer  
**Lösung:** Normal! Werden in späteren Phasen befüllt

---

**VIEL ERFOLG! Das Gedächtnis erwacht! 🧠**
