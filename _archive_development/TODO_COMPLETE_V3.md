# EVOKI V3.0 — DEFINITIVE TODO LISTE
**Erstellt:** 2026-02-07 20:06  
**Basis:** 
- MASTER_TODO.md.resolved (769 Zeilen)
- implementation_plan.md.resolved (127 Zeilen)
- backend_module_mapping.md.resolved (205 Zeilen)
- Live-System-Status (binärer Test)
- 774KB V3.0 Spezifikation

**Status:** KOMPLETT - Alle 3 Brain-Dokumente + Live-Tests integriert

---

## 📚 QUELLPFADE

**V7 Patchpaket:** `C:\Users\nicom\Downloads\EVOKI_V3_METRICS_SPECIFICATION Entwicklung\V7 Patchpaket V2 + Monolith\`  
**evoki_pipeline:** `C:\Users\nicom\Documents\evoki\evoki_pipeline\`  
**Projekt-Root:** `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\`

**Brain-Dokumente:** `C:\Users\nicom\.gemini\antigravity\brain\20da9c61-ddf1-40da-83f1-48057400bf78\`
- MASTER_TODO.md.resolved (27 Tasks)
- implementation_plan.md.resolved (18 Tasks, Offene Fragen!)
- backend_module_mapping.md.resolved (Vollständiges Mapping)

---

## 📊 EXECUTIVE SUMMARY

### ✅ WAS FUNKTIONIERT (PHASE T0 ABGESCHLOSSEN)
- ✅ Backend (FastAPI, Port 8000)
- ✅ Frontend (React/Vite, Port 5173)
- ✅ 10.971 Prompt-Paare importiert
- ✅ 10.971 FAISS Vektoren (384D, metrics_wpf)
- ✅ Temple API mit SSE Streaming
- ✅ **V7 Module kopiert** (T0.2 ✅)
  - a_phys_v11.py, evoki_bootcheck.py, evoki_lock.py
  - genesis_anchor.py, evoki_invariants.py, metrics_registry.py
  - evoki_history_ingest.py, lexika.py
  - evoki_lexika_v3/ Package
  - b_vector.py (Diff-Version)
  - evoki_fullspectrum168_contract.json
- ✅ **Alte Module archiviert** (T0.1 ✅)
  - backend/_archive_v2/ erstellt

### ❌ WAS FEHLT (PHASEN T1-T5)

#### 🔥 KRITISCH (Blockiert Tests):
- ❌ **Import-Fehler beheben** (T1.1-T1.2)
  - `from core import genesis_anchor` schlägt fehl
  - `evoki_metrics_v3` Import-Fehler
- ❌ **evoki_pipeline Module** (T1.3-T1.8)
  - vector_engine_v2_1.py (1597 Zeilen!) ← **FRAGE: Wo ist diese Datei?**
  - metrics_complete_v3.py (41KB - ECHTE 168 Metriken!)
  - timeline_4d_complete.py (53KB)
  - chunk_vectorize_full.py (42KB)
  - spectrum_types.py (MUSS generiert werden)

#### ⚡ HIGH PRIORITY:
- ❌ **4/5 Datenbanken fehlen** (T2.1-T2.5)
- ❌ **2/3 FAISS Indices fehlen** (T3.1-T3.2)
- ❌ **Dual-Gradient System** (T4.1)
- ❌ **Lexika-Integration** in Metriken (T5.1)

---

## ⚠️ KRITISCHE OFFENE FRAGEN (aus implementation_plan.md)

### ❓ FRAGE 1: vector_engine_v2_1.py existiert?
**Kontext:** implementation_plan.md sagt:
> **Gibt es eine Version irgendwo auf deinem System?**
> Diese Datei existiert nirgends. Interface nur durch Bootcheck-Referenzen rekonstruierbar.

**ABER:** MASTER_TODO.md & backend_module_mapping.md sagen beide:
- Quelle: `C:\Users\nicom\Documents\evoki\evoki_pipeline\vector_engine_v2_1.py`
- Größe: 65KB, 1597 Zeilen
- Status: T1.1 ✅ **ABGESCHLOSSEN** (laut MASTER_TODO)

**ACTION REQUIRED:** ✅ Prüfe ob Datei existiert!

### ❓ FRAGE 2: b_vector.py Versionen
**Kontext:** 2 verschiedene Versionen gefunden:
1. **Diff-Version** (4.2KB, 127 Zeilen) — in `backend/core/` ← V7 Patchpaket
2. **Pipeline-Version** (2.4KB, 85 Zeilen) — in `evoki_pipeline/` ← evoki_pipeline

**MASTER_TODO sagt:**
> **T1.2 — b_vector.py ersetzen (FORCE!)**  
> Diff-Version hat Interface-Mismatch.  
> Pipeline-Version ist perfekt kompatibel mit vector_engine_v2_1.py

**ACTION REQUIRED:** ❓ Welche Version ist kanonisch?

### ❓ FRAGE 3: Backend-Framework
**implementation_plan.md fragt:**
> **Backend-Framework** — `backend/main.py` ist FastAPI oder Flask? V7 nutzt Flask.

**ANTWORT:** ✅ **FastAPI** (bestätigt durch Live-System)
- Server: Uvicorn (ASGI), Port 8000
- Router: `/api/temple`, `/api/integrity`

**ABER:** V7 Patchpaket nutzt Flask!
- **Lösung:** V7-Endpoints als FastAPI-Router adaptieren (✅ bereits klar)

### ❓ FRAGE 4: Soll ich sofort mit T0 beginnen?
**ANTWORT:** ✅ **T0 ist ABGESCHLOSSEN** (laut MASTER_TODO.md)

---

## 🏗️ BACKEND-ARCHITEKTUR LOGIK (aus Dokumenten)

### Zentrale Komponenten die implementiert werden müssen:

#### 1. **INTEGRITY GATE** (3 Checks)
- ✅ Bootcheck (b71_error_code) — `evoki_bootcheck.py` vorhanden
- ✅ Genesis (b51_anchor_lock) — `genesis_anchor.py` vorhanden
- ✅ Lock Mechanism — `evoki_lock.py` vorhanden

**Status:** ✅ Module vorhanden, ❌ Import-Fehler beheben!

---

#### 2. **EVOKI ENGINE** (Zentrale Pipeline)

##### Task Orchestrator
- **User prompts processing tools & data** 
- **Frontend Interaction** (Chatbot User, QA Queries, Agentic Tasks)
- **Secure API** zu Data Loader
- **Status:** ❌ FEHLT - Muss in `backend/api/temple.py` implementiert werden

##### Metrics Evaluator  
- **Scoring | Events** (retry retry / alert)
- **Real-time verification**
- **Status:** ❌ FEHLT - Braucht `metrics_complete_v3.py` + Integration

---

#### 3. **EVALUATOR FRAMEWORK** (Rechte Seite)

##### Metric Registry (Alias-Layer — Spec)
- ✅ `metrics_registry.py` vorhanden
- **Funktion:** Maps m1_A → "Affekt", m2_PCI → "Panic Index"

##### Configurations
- Weighted scoring & evolutionary rules
- **Status:** ❌ Konfigurationsdateien fehlen

##### History Analyzer
- Hard constraints, calibration logs, history data
- **Status:** ❌ FEHLT - Braucht Timeline 4D Integration

##### Aggregator
- Aggregates dimension scores, final weighted scores
- **Status:** ❌ FEHLT - Backend-API-Endpoint nötig

---

#### 4. **DATA LAYER** (Untere Schicht)

##### History DB / SQLite WAL
- ✅ `evoki_v3_core.db` existiert (10.971 Paare)
- ❌ 4 weitere Datenbanken fehlen

##### Events
- commit → **Decision commit**
- retry → **Decision retry**  
- alert → **Decision alert**
- **Status:** ❌ Events-System fehlt komplett

##### QA Probes, Metric Scores, Aggregated Scores
- **Status:** ❌ Analytics DB fehlt

---

#### 5. **DATA LOADER & INGEST**
- **APIs & External Knowledge**
- ✅ `evoki_history_ingest.py` vorhanden
- ❌ Integration mit `chunk_vectorize_full.py` fehlt

---

### Was diese Architektur KONKRET bedeutet:

**Fehlende Backend-Komponenten:**

1. **Task Orchestrator API** → `backend/api/orchestrator.py`
2. **Metrics Evaluator Integration** → `backend/core/metrics_complete_v3.py` + API
3. **History Analyzer** → `backend/core/timeline_4d_complete.py` + Integration
4. **Aggregator API** → `backend/api/aggregator.py`
5. **Events System** → `backend/core/events_system.py`
6. **Configurations Layer** → `backend/core/configurations/` (weighted scoring rules)
7. **Real-time Verification** → SSE-Integration in Temple API

**Diese laufen ALLE durch `backend/api/temple.py`!**

---

# PHASE T1: IMPORT-FEHLER BEHEBEN 🔥 KRITISCH

## [ ] T1.1 — V7 Module Fix: genesis_anchor.py

**Problem:** `from core import genesis_anchor` schlägt fehl

**Diagnose:**
```powershell
cd backend
python -c "from core import genesis_anchor"
# ModuleNotFoundError: No module named 'genesis_anchor'
```

**Ursache:** Wahrscheinlich Import-Zyklus oder fehlende __init__.py

**Fix:**
```python
# backend/core/__init__.py erweitern
from . import genesis_anchor
from . import evoki_invariants
from . import evoki_lock
from . import evoki_bootcheck
```

**Test:**
```powershell
cd backend
python -c "from core import genesis_anchor; print('OK')"
```

**Priorität:** 🔥 KRITISCH - Blockiert Tests

---

## [ ] T1.2 — evoki_pipeline Module Fix

**Problem:** `'str' object has no attribute '_uninitialized_submodules'`

**Diagnose:**
```powershell
cd backend
python -c "from core.evoki_metrics_v3 import metrics_complete_v3"
```

**Wahrscheinliche Ursache:** 
- Fehlendes `__init__.py` in evoki_metrics_v3/
- Zirkuläre Imports
- PyTorch Import-Konflikt

**Fix:** Package-Struktur prüfen und bereinigen

**Priorität:** 🔥 KRITISCH - Blockiert Metriken

---

# PHASE T2: FEHLENDE DATENBANKEN ERSTELLEN 📊

## [ ] T2.1 — evoki_v3_graph.db

**Status:** ❌ FEHLT

**Schema:** (aus Spezifikation)
```sql
CREATE TABLE graph_nodes (
    node_id TEXT PRIMARY KEY,
    pair_id TEXT REFERENCES prompt_pairs(pair_id),
    node_type TEXT,  -- 'prompt_pair', 'chunk', 'keyword'
    created_at TEXT
);

CREATE TABLE graph_edges (
    edge_id TEXT PRIMARY KEY,
    source_node_id TEXT,
    target_node_id TEXT,
    similarity_score REAL,
    edge_type TEXT,  -- 'semantic', 'metrics', 'trajectory'
    created_at TEXT
);

CREATE TABLE graph_clusters (
    cluster_id TEXT PRIMARY KEY,
    cluster_name TEXT,
    node_ids TEXT,  -- JSON array
    centroid_vector BLOB,
    created_at TEXT
);
```

**Erstellen:**
```powershell
python backend/utils/create_graph_db.py
```

**Priorität:** HIGH

---

## [ ] T2.2 — evoki_v3_keywords.db (LERNEND!)

**Status:** ❌ FEHLT

**Schema:**
```sql
CREATE TABLE keyword_registry (
    keyword_id TEXT PRIMARY KEY,
    keyword TEXT UNIQUE,
    frequency INTEGER DEFAULT 1,
    vector_384d BLOB,
    first_seen TEXT,
    last_seen TEXT
);

CREATE TABLE keyword_pair_links (
    link_id TEXT PRIMARY KEY,
    keyword_id TEXT,
    pair_id TEXT,
    context_window TEXT,  -- 20 chars vor + 20 nach
    created_at TEXT
);

CREATE TABLE keyword_associations (
    assoc_id TEXT PRIMARY KEY,
    keyword_a TEXT,
    keyword_b TEXT,
    co_occurrence_count INTEGER,
    pmi_score REAL,  -- Pointwise Mutual Information
    created_at TEXT
);

CREATE TABLE keyword_clusters (
    cluster_id TEXT PRIMARY KEY,
    keywords TEXT,  -- JSON: ["angst", "furcht", "panik"]
    cluster_type TEXT,  -- 'synonym', 'theme', 'topic'
    created_at TEXT
);

CREATE TABLE live_session_index (
    session_id TEXT,
    pair_id TEXT,
    keywords TEXT,  -- JSON array
    timestamp TEXT,
    PRIMARY KEY (session_id, pair_id)
);
```

**Erstellen:**
```powershell
python backend/utils/create_keywords_db.py
```

**Priorität:** HIGH

---

## [ ] T2.3 — evoki_v3_analytics.db (VOLLSTÄNDIGES LOGGING!)

**Status:** ❌ FEHLT

**Schema:**
```sql
CREATE TABLE api_requests (
    request_id TEXT PRIMARY KEY,
    endpoint TEXT,
    method TEXT,
    payload TEXT,  -- JSON
    timestamp TEXT
);

CREATE TABLE api_responses (
    response_id TEXT PRIMARY KEY,
    request_id TEXT,
    status_code INTEGER,
    response_body TEXT,  -- JSON
    latency_ms REAL,
    timestamp TEXT
);

CREATE TABLE search_events (
    search_id TEXT PRIMARY KEY,
    query TEXT,
    search_type TEXT,  -- 'semantic', 'metrics', 'trajectory', 'keyword'
    results_count INTEGER,
    top_5_results TEXT,  -- JSON
    timestamp TEXT
);

CREATE TABLE prompt_history (
    prompt_id TEXT PRIMARY KEY,
    pair_id TEXT,
    user_text TEXT,
    ai_text TEXT,
    user_metrics TEXT,  -- JSON: 161 Metriken
    ai_metrics TEXT,    -- JSON: 161 Metriken
    timestamp TEXT
);

CREATE TABLE metric_evaluations (
    eval_id TEXT PRIMARY KEY,
    pair_id TEXT,
    metric_name TEXT,  -- z.B. "m1_A"
    user_value REAL,
    ai_value REAL,
    delta_value REAL,
    timestamp TEXT
);

CREATE TABLE b_vector_verifications (
    verify_id TEXT PRIMARY KEY,
    pair_id TEXT,
    computed_b_vector TEXT,  -- JSON: 7D
    verified_b_vector TEXT,  -- JSON: 7D (von API)
    difference_score REAL,
    timestamp TEXT
);

CREATE TABLE lexika_verification_log (
    verify_id TEXT PRIMARY KEY,
    pair_id TEXT,
    lexikon_name TEXT,  -- z.B. "T_panic", "Suicide"
    hits_count INTEGER,
    matched_terms TEXT,  -- JSON array
    score REAL,
    timestamp TEXT
);

CREATE TABLE learning_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT,  -- 'new_keyword', 'cluster_update', 'association_learned'
    details TEXT,  -- JSON
    timestamp TEXT
);

CREATE TABLE system_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT,  -- 'session_start', 'session_end', 'error', 'bootcheck'
    details TEXT,  -- JSON
    timestamp TEXT
);
```

**Erstellen:**
```powershell
python backend/utils/create_analytics_db.py
```

**Priorität:** MEDIUM

---

## [ ] T2.4 — evoki_v3_trajectories.db

**Status:** ❌ FEHLT

**Schema:**
```sql
CREATE TABLE metric_trajectories (
    trajectory_id TEXT PRIMARY KEY,
    session_id TEXT,
    metric_name TEXT,  -- z.B. "m1_A"
    trajectory_data TEXT,  -- JSON: [{pair_index: 0, value: 0.5}, ...]
    created_at TEXT
);

CREATE TABLE metric_predictions (
    prediction_id TEXT PRIMARY KEY,
    pair_id TEXT,
    metric_name TEXT,
    predicted_plus_1 REAL,
    predicted_plus_5 REAL,
    predicted_plus_25 REAL,
    confidence_score REAL,
    created_at TEXT
);
```

**Erstellen:**
```powershell
python backend/utils/create_trajectories_db.py
```

**Priorität:** MEDIUM

---

# PHASE T3: FEHLENDE FAISS INDICES 🔍

## [ ] T3.1 — semantic_wpf (4096D, Mistral-7B)

**Status:** ❌ FEHLT

**Zweck:** TEXT-basierte Ähnlichkeitssuche

**Erstellen:**
```python
import faiss
import numpy as np

# 4096D für Mistral-7B-Instruct-v0.2
dim = 4096
index = faiss.IndexFlatIP(dim)  # Inner Product für normalized vectors

# Speichern
faiss.write_index(index, "backend/data/faiss/evoki_v3_vectors_semantic.faiss")
```

**Priorität:** HIGH

---

## [ ] T3.2 — trajectory_wpf (~50D, custom)

**Status:** ❌ FEHLT

**Zweck:** VERLAUFS-basierte Ähnlichkeitssuche

**Dimensionen:** ~50D (10 Metriken × 5 Zeitpunkte)

**Erstellen:**
```python
dim = 50  # Anpassen je nach Trajectory-Design
index = faiss.IndexFlatL2(dim)
faiss.write_index(index, "backend/data/faiss/evoki_v3_vectors_trajectory.faiss")
```

**Priorität:** MEDIUM

---

# PHASE T4: DUAL-GRADIENT SYSTEM IMPLEMENTIEREN 📈

## [ ] T4.1 — Dual-Metriken in metrics_full

**Status:** ❌ FEHLT - Aktuell nur EINE Metrik-Berechnung

**Was fehlt:**
1. User-Metriken werden berechnet → `user_metrics_json`
2. AI-Metriken **NICHT** berechnet → `ai_metrics_json` fehlt!
3. Deltas **NICHT** berechnet → `delta_user_*`, `delta_ai_*` fehlen!

**Schema-Erweiterung:**
```sql
ALTER TABLE metrics_full ADD COLUMN ai_metrics_json TEXT;
ALTER TABLE metrics_full ADD COLUMN delta_user_m1_A REAL;
ALTER TABLE metrics_full ADD COLUMN delta_ai_m1_A REAL;
ALTER TABLE metrics_full ADD COLUMN diff_gradient_affekt REAL;
ALTER TABLE metrics_full ADD COLUMN disharmony_score REAL;
```

**Code-Änderung:**
```python
# backend/api/temple.py

# VORHER:
metrics = compute_metrics(prompt)

# NACHHER:
user_metrics = compute_metrics(user_prompt, target='user')
ai_metrics = compute_metrics(ai_response, target='ai')

# Delta berechnen
delta_user_A = user_metrics['m1_A'] - prev_user_metrics['m1_A']
delta_ai_A = ai_metrics['m1_A'] - prev_ai_metrics['m1_A']
diff_gradient = delta_user_A - delta_ai_A
```

**Priorität:** 🔥 KRITISCH - Kernfeature!

---

## [ ] T4.2 — Gradient-Alerts implementieren

**Logic:**
```python
def check_gradient_alerts(delta_user_A, delta_ai_A):
    alerts = []
    
    # User-Affekt fällt stark
    if delta_user_A < -0.15:
        alerts.append({
            "type": "user_falling",
            "severity": "high",
            "message": "User-Affekt fällt rapide! AI muss Empathie erhöhen."
        })
    
    # AI-Engagement fällt
    if delta_ai_A < -0.20:
        alerts.append({
            "type": "ai_falling",
            "severity": "medium",
            "message": "AI-Engagement fällt! User kann einschreiten."
        })
    
    # Disharmonie
    if abs(delta_user_A - delta_ai_A) > 0.3:
        alerts.append({
            "type": "disharmony",
            "severity": "high",
            "message": "Gespräch driftet auseinander! Rekalibrierung nötig."
        })
    
    return alerts
```

**Priorität:** HIGH

---

# PHASE T5: LEXIKA-INTEGRATION 📚

## [ ] T5.1 — Lexika in Metriken-Berechnung einbinden

**Status:** ❌ Lexika existieren, werden aber NICHT genutzt

**Code-Änderung:**
```python
# backend/core/evoki_metrics_v3/metrics_complete_v3.py

from backend.core.lexika import (
    AngstromLexika, TraumaLexika, HazardLexika
)

def compute_m8_s_self(text: str) -> float:
    """S_self: Selbstbezug"""
    words = text.lower().split()
    hits = [AngstromLexika.S_SELF.get(word, 0) for word in words]
    return sum(hits) / max(1, len(hits))

def compute_m9_x_exist(text: str) -> float:
    """X_exist: Existenz-Marker"""
    words = text.lower().split()
    hits = [AngstromLexika.X_EXIST.get(word, 0) for word in words]
    return sum(hits) / max(1, len(hits))

# ... 168 Metriken implementieren!
```

**Priorität:** 🔥 KRITISCH

---

## [ ] T5.2 — Lexika-Verification Logging

**In Analytics DB loggen:**
```python
def log_lexika_verification(pair_id, text):
    for lexikon_name, lexikon_dict in ALL_LEXIKA.items():
        hits = [word for word in text.lower().split() if word in lexikon_dict]
        
        if hits:
            conn.execute("""
                INSERT INTO lexika_verification_log 
                (pair_id, lexikon_name, hits_count, matched_terms, score)
                VALUES (?, ?, ?, ?, ?)
            """, (pair_id, lexikon_name, len(hits), json.dumps(hits), sum(...)))
```

**Priorität:** MEDIUM

---

# PHASE T6: HISTORICAL FUTURES SYSTEM 🔮

## [ ] T6.1 — Historical Futures berechnen

**Konzept:** Für jeden Prompt N speichern was bei N+1, N+2, N+5, N+10, N+25 passierte

**Schema-Erweiterung:**
```sql
CREATE TABLE historical_futures (
    pair_id TEXT PRIMARY KEY,
    future_plus_1_metrics TEXT,   -- JSON: Metriken von N+1
    future_plus_2_metrics TEXT,   -- JSON: Metriken von N+2
    future_plus_5_metrics TEXT,   -- JSON: Metriken von N+5
    future_plus_10_metrics TEXT,  -- JSON: Metriken von N+10
    future_plus_25_metrics TEXT,  -- JSON: Metriken von N+25
    created_at TEXT
);
```

**Rückwirkende Updates:**
```python
def update_historical_futures(new_pair_id, new_pair_index, new_metrics):
    # Prompt N-1: future_plus_1 = new_metrics
    # Prompt N-2: future_plus_2 = new_metrics
    # ... etc.
    
    offsets = [1, 2, 5, 10, 25]
    for offset in offsets:
        target_index = new_pair_index - offset
        if target_index >= 0:
            update_future_field(target_index, f"future_plus_{offset}", new_metrics)
```

**Priorität:** HIGH

---

## [ ] T6.2 — Historical Futures in Context

**API-Integration:**
```python
@router.post("/stream")
async def temple_stream(request):
    # 1. Trajectory berechnen (-1, -2, -5, -25)
    trajectory = compute_trajectory(session_id)
    
    # 2. FAISS-Suche trajectory_wpf
    similar_trajectories = faiss_search(trajectory_wpf, trajectory, k=5)
    
    # 3. Historical Futures laden
    futures = []
    for match in similar_trajectories:
        future = load_historical_future(match.pair_id)
        futures.append(future)
    
    # 4. In System Prompt einbauen
    context = f"""
    Basierend auf ähnlichen Verläufen:
    - In 50% der Fälle kam als nächstes: {futures[0].most_common_next()}
    - Risiko-Score: {futures[0].avg_risk_escalation}
    """
```

**Priorität:** MEDIUM

---

# PHASE T7: KEYWORD LEARNING SYSTEM 🧠

## [ ] T7.1 — Auto-Keyword-Extraktion

**Code:**
```python
import re
from collections import Counter

def extract_keywords(text: str) -> list:
    # Stopwords entfernen
    stopwords = {'der', 'die', 'das', 'und', 'oder', 'aber', ...}
    
    # Normalisieren
    words = re.findall(r'\b\w+\b', text.lower())
    words = [w for w in words if w not in stopwords and len(w) > 3]
    
    # Frequenz
    freq = Counter(words)
    
    return [word for word, count in freq.items() if count >= 2]
```

**Priorität:** MEDIUM

---

## [ ] T7.2 — Keyword-Assoziationen lernen

**Co-Occurrence:**
```python
def learn_keyword_associations(keywords: list):
    for i, kw_a in enumerate(keywords):
        for kw_b in keywords[i+1:]:
            # Co-Occurrence +1
            conn.execute("""
                INSERT INTO keyword_associations (keyword_a, keyword_b, co_occurrence_count)
                VALUES (?, ?, 1)
                ON CONFLICT (keyword_a, keyword_b) 
                DO UPDATE SET co_occurrence_count = co_occurrence_count + 1
            """, (kw_a, kw_b))
```

**PMI Score:**
```python
pmi = log(P(A,B) / (P(A) * P(B)))
```

**Priorität:** LOW

---

# PHASE T8: ANALYTICS LOGGING VOLLSTÄNDIG 📊

## [ ] T8.1 — Alle API-Requests loggen

```python
@router.post("/stream")
async def temple_stream(request):
    request_id = str(uuid.uuid4())
    
    # BEFORE
    log_api_request(request_id, "/api/temple/stream", "POST", request.dict())
    
    try:
        response = await process_request(request)
        
        # AFTER
        log_api_response(request_id, 200, response, latency_ms)
        
        return response
    except Exception as e:
        log_api_response(request_id, 500, {"error": str(e)}, latency_ms)
        raise
```

**Priorität:** MEDIUM

---

## [ ] T8.2 — Alle Suchanfragen loggen

```python
def log_search_event(query, search_type, results):
    conn.execute("""
        INSERT INTO search_events 
        (query, search_type, results_count, top_5_results, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (query, search_type, len(results), json.dumps(results[:5]), now()))
```

**Priorität:** LOW

---

# ZUSAMMENFASSUNG

## Gesamt-Status

| Phase | Tasks | Status | Priorität |
|-------|-------|--------|-----------|
| T0: V7 Archivierung | 3 | ✅ DONE | - |
| T1: Import-Fehler Fix | 2 | ❌ TODO | 🔥 KRITISCH |
| T2: Datenbanken | 4 | ❌ TODO | HIGH |
| T3: FAISS Indices | 2 | ❌ TODO | HIGH |
| T4: Dual-Gradient | 2 | ❌ TODO | 🔥 KRITISCH |
| T5: Lexika-Integration | 2 | ❌ TODO | 🔥 KRITISCH |
| T6: Historical Futures | 2 | ❌ TODO | HIGH |
| T7: Keyword Learning | 2 | ❌ TODO | MEDIUM |
| T8: Analytics Logging | 2 | ❌ TODO | MEDIUM |
| **GESAMT** | **21** | **3 DONE, 18 TODO** | - |

---

## Priorisierte Reihenfolge

### 🔥 SOFORT (Kritisch):
1. **T1.1** — V7 Module Import-Fix
2. **T1.2** — evoki_pipeline Import-Fix
3. **T4.1** — Dual-Gradient System
4. **T5.1** — Lexika-Integration

### ⚡ DANN (High):
5. **T2.1** — evoki_v3_graph.db
6. **T2.2** — evoki_v3_keywords.db
7. **T3.1** — semantic_wpf FAISS
8. **T6.1** — Historical Futures

### 📊 SPÄTER (Medium):
9. **T2.3** — evoki_v3_analytics.db
10. **T2.4** — evoki_v3_trajectories.db
11. **T3.2** — trajectory_wpf FAISS
12. **T7.1** — Keyword Learning
13. **T8.1** — Analytics Logging

### 🎨 OPTIONAL (Low):
14. **T4.2** — Gradient-Alerts UI
15. **T5.2** — Lexika-Verification Logging
16. **T6.2** — Historical Futures Context
17. **T7.2** — Keyword-Assoziationen
18. **T8.2** — Search-Events Logging

---

## Zeitschätzung

**Kritische Tasks (1-4):** ~8-10 Stunden  
**High-Priority Tasks (5-8):** ~10-12 Stunden  
**Medium-Priority Tasks (9-13):** ~8-10 Stunden  
**Optional Tasks (14-18):** ~6-8 Stunden

**GESAMT:** ~32-40 Stunden

---

## Was SOFORT gemacht werden muss

1. **Import-Fehler fixen** (2-3 Stunden)
2. **Dual-Gradient implementieren** (3-4 Stunden)
3. **Lexika integrieren** (3-4 Stunden)

**Nach diesen 8-11 Stunden:**
- System erfüllt 70% der Spezifikation
- Alle Kernfeatures laufen
- Rest ist "Nice-to-Have" Performance-Features

---

**ENDE TODO_COMPLETE_V3.md**
