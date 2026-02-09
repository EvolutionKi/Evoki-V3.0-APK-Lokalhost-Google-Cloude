# 🗺️ EVOKI V3.0 DATA LAYER — IMPLEMENTATION ROADMAP

**Version**: 1.0.0  
**Erstellt**: 2026-02-08  
**Basis**: **1000 Prompt-Paare** (Test-MVP)  
**Strategie**: Evolutionärer Aufbau in 4 Phasen → **Gate-Keeping auf 22.000 Paare**

---

## 📊 **ÜBERBLICK**

### **Ausgangslage**:
- ✅ T2 Pipeline erfolgreich (1000 Paare, 651 t/s, 0 Fehler)
- ✅ MetricsCalculator funktioniert (168 Metriken)
- ✅ 4-Unit DB Schema existiert (metadata, resonance, triggers, metapatterns)
- ❌ V3.0 Future State existiert NICHT → muss neu gebaut werden

### **Ziel**:
Erstelle das **komplette V3.0 Data Layer** wie in BUCH 7 spezifiziert:
- 5 neue SQLite-Datenbanken
- 3 FAISS-Namespaces (semantic, metrics, trajectory)
- Learning Keyword Engine
- Metric Trajectory Predictor
- Dual-Response API Client
- B-Vektor Verification System

### **Kritische Regel**:
⚠️ **ERST validieren mit 1000 Paaren via LIVE-MONITOR, DANN auf 22.000 Paare skalieren!**  
📋 **Details**: Siehe `LIVE_PIPELINE_TEST_PLAN.md`

---

## 🎯 **4-PHASEN PLAN**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EVOLUTION ROADMAP                                │
│                                                                      │
│  PHASE 0: Foundation          [2-3 Stunden]                         │
│  ├─ Cleanup + Test-Data bereit                                      │
│  └─ Schemas erstellt                                                │
│                                                                      │
│  PHASE 1: Core V3.0 DB        [1-2 Tage]                            │
│  ├─ evoki_v3_core.db + FAISS atomic_pairs                           │
│  └─ 1000 Paare importiert + validiert                               │
│                                                                      │
│  PHASE 2: Analytics           [1-2 Tage]                            │
│  ├─ evoki_v3_analytics.db + evoki_v3_trajectories.db                │
│  └─ Historical Futures System                                       │
│                                                                      │
│  PHASE 3: Learning Engines    [2-3 Tage]                            │
│  ├─ Learning Keyword Engine                                         │
│  ├─ Metric Trajectory Predictor                                     │
│  └─ evoki_v3_keywords.db + evoki_v3_graph.db                        │
│                                                                      │
│  PHASE 4: Integration         [1-2 Tage]                            │
│  ├─ Dual-Response API Client                                        │
│  ├─ Full Pipeline Test (1000 Paare)                                 │
│  └─ Scale-Up auf 11.016 Paare                                       │
│                                                                      │
│  GESAMT: ~1 Woche (bei fokussierter Arbeit)                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📝 **PHASE 0: FOUNDATION** (2-3 Stunden)

### **Ziel**: Saubere Basis schaffen

### ✅ **TODO-LISTE PHASE 0**:

- [ ] **0.1 Cleanup alte Artefakte** (~15 Min)
  - [ ] Identifiziere alle gescheiterten V3.0 Implementierungsversuche
  - [ ] Verschiebe nach `archive/failed_attempts/` (NICHT löschen!)
  - [ ] Erstelle `backend/v3_data_layer/` als neues Arbeitsverzeichnis
  
- [ ] **0.2 Test-Data extrahieren** (~30 Min)
  - [ ] Identifiziere Quelle der 1000 Test-Paare (aus T2 Pipeline Success)
  - [ ] Kopiere nach `backend/test_data/1000_pairs/`
  - [ ] Validiere Format (User + AI Paare, Timestamps, IDs)
  - [ ] **Was du sehen solltest**: 1000 Dateien mit strukturiertem Format
  
- [ ] **0.3 Erstelle alle 5 V3.0 SQL-Schemas** (~1 Stunde)
  - [ ] `backend/schemas/evoki_v3_core_schema.sql` (BEREITS EXISTIERT - prüfen!)
  - [ ] `backend/schemas/evoki_v3_graph_schema.sql`
  - [ ] `backend/schemas/evoki_v3_keywords_schema.sql`
  - [ ] `backend/schemas/evoki_v3_analytics_schema.sql`
  - [ ] `backend/schemas/evoki_v3_trajectories_schema.sql`
  - [ ] **Was du sehen solltest**: 5 SQL-Dateien, jede ~200-400 Zeilen
  
- [ ] **0.4 Erstelle FAISS Config** (~30 Min)
  - [ ] `backend/v3_data_layer/faiss_config.json`
  - [ ] Definiere 3 Namespaces (atomic_pairs, metrics_wpf, trajectory_wpf)
  - [ ] Definiere Dimensionen (384D, 322D, custom)
  - [ ] **Was du sehen solltest**: JSON mit Index-Konfiguration
  
- [ ] **0.5 Erstelle Verzeichnisstruktur** (~15 Min)
  ```
  backend/v3_data_layer/
  ├── databases/          (SQLite DBs hier)
  ├── faiss_indices/      (FAISS Indizes hier)
  ├── models/             (Embedding-Modelle hier)
  ├── scripts/            (Python Pipeline-Scripts)
  ├── tests/              (Unit-Tests)
  └── logs/               (Logging)
  ```

### **PHASE 0 DONE CHECKLIST**:
- ✅ 5 SQL-Schema-Dateien existieren
- ✅ 1000 Test-Paare in `backend/test_data/1000_pairs/`
- ✅ Verzeichnisstruktur erstellt
- ✅ FAISS Config JSON erstellt
- ✅ Alte Artefakte archiviert

**ZEIT**: ~2-3 Stunden  
**OUTPUT**: Saubere Basis für Phase 1

---

## 📝 **PHASE 1: CORE V3.0 DB + BASIC FAISS** (1-2 Tage)

### **Ziel**: evoki_v3_core.db + FAISS atomic_pairs funktionieren mit 1000 Paaren

### ✅ **TODO-LISTE PHASE 1**:

#### **1.1 Erstelle evoki_v3_core.db** (~2 Stunden)

- [ ] **1.1.1 Schema initialisieren**
  - [ ] Python-Script: `scripts/init_v3_core_db.py`
  - [ ] Lädt `backend/schemas/evoki_v3_core_schema.sql`
  - [ ] Erstellt `backend/v3_data_layer/databases/evoki_v3_core.db`
  - [ ] Führe aus: `python scripts/init_v3_core_db.py`
  - [ ] **Was du sehen solltest**: 
    ```
    ✅ Created evoki_v3_core.db
    ✅ Table 'sessions' created (0 rows)
    ✅ Table 'prompt_pairs' created (0 rows)
    ✅ Table 'metrics_full' created (0 rows)
    ✅ Table 'session_chain' created (0 rows)
    ✅ Table 'b_state_evolution' created (0 rows)
    ✅ Table 'hazard_events' created (0 rows)
    ```

- [ ] **1.1.2 Test Insert/Select**
  - [ ] Füge 1 Test-Paar manuell ein
  - [ ] SELECT * FROM prompt_pairs → sollte 1 Zeile zurückgeben
  - [ ] SELECT * FROM metrics_full → sollte 1 Zeile zurückgeben (User + AI Metriken)
  - [ ] **Was du sehen solltest**: Erfolgreiches Insert + Select

#### **1.2 Import Pipeline für V3.0** (~4 Stunden)

- [ ] **1.2.1 Erstelle `v3_importer.py`**
  - [ ] Basis: Kopie von `t2_history_importer.py` (der funktioniert!)
  - [ ] Anpassungen:
    - [ ] Schreibt in `evoki_v3_core.db` statt 4-Unit DBs
    - [ ] Berechnet **322 Metriken** (161 User + 161 AI) statt 168
    - [ ] Generiert `pair_id` (UUID v4)
    - [ ] Generiert `pair_hash` (SHA-256)
    - [ ] Berechnet B-Vektor (7D) für jeden Prompt
    - [ ] Erstellt Session Chain Hash
  - [ ] **Was du sehen solltest**: Python-Datei ~300-400 Zeilen

- [ ] **1.2.2 Test mit 10 Paaren** (Dry-Run)
  - [ ] Führe aus: `python scripts/v3_importer.py --dry-run --limit 10`
  - [ ] **Was du sehen solltest**:
    ```
    📊 Dry-Run: 10 Paare
    ──────────────────────
    ✅ Paar 1: Metriken berechnet (322), B-Vektor OK, Hash OK
    ✅ Paar 2: Metriken berechnet (322), B-Vektor OK, Hash OK
    ...
    ✅ Paar 10: Metriken berechnet (322), B-Vektor OK, Hash OK
    ──────────────────────
    ⏱️  Zeit: ~0.15s (67 Paare/s)
    ✅ 0 Fehler
    ```

- [ ] **1.2.3 Import 1000 Paare** (Full Run)
  - [ ] Führe aus: `python scripts/v3_importer.py --limit 1000`
  - [ ] **Was du sehen solltest**:
    ```
    📊 V3.0 Import: 1000 Paare
    ─────────────────────────
    [Progress bar 100%]
    ─────────────────────────
    ✅ 1000 Paare importiert
    ⏱️  Zeit: ~1.5s (650 Paare/s)
    📊 Statistiken:
       • prompt_pairs:     1000 Zeilen
       • metrics_full:     1000 Zeilen (322 Metriken pro Zeile)
       • b_state_evolution: 1000 Zeilen (7D B-Vektor pro Zeile)
       • session_chain:    ~50 Sessions
       • hazard_events:    ~50 Events (5% Hazard-Rate)
    ✅ 0 Fehler
    ```

- [ ] **1.2.4 Validierung**
  - [ ] SQL Query: `SELECT COUNT(*) FROM prompt_pairs;` → sollte **1000** sein
  - [ ] SQL Query: `SELECT AVG(user_m1_A), AVG(ai_m1_A) FROM metrics_full;` → sollte ~0.5-0.7 sein
  - [ ] SQL Query: `SELECT COUNT(*) FROM hazard_events WHERE user_m151_hazard > 0.7;` → sollte ~50 sein
  - [ ] **Was du sehen solltest**: Alle Queries erfolgreich, Werte plausibel

#### **1.3 FAISS atomic_pairs Namespace** (~3 Stunden)

- [ ] **1.3.1 Embedding-Modell herunterladen**
  - [ ] Modell: `sentence-transformers/all-MiniLM-L6-v2` (384D)
  - [ ] Script: `scripts/download_embedding_model.py`
  - [ ] Speichert nach: `backend/v3_data_layer/models/all-MiniLM-L6-v2/`
  - [ ] **Was du sehen solltest**:
    ```
    📥 Downloading all-MiniLM-L6-v2...
    ✅ Model downloaded (~90 MB)
    ✅ Saved to: backend/v3_data_layer/models/all-MiniLM-L6-v2/
    ```

- [ ] **1.3.2 Erstelle FAISS Index Builder**
  - [ ] Script: `scripts/build_faiss_atomic_pairs.py`
  - [ ] Liest alle 1000 Paare aus `prompt_pairs`
  - [ ] Generiert 384D Embedding für jeden Prompt (User + AI concatenated)
  - [ ] Erstellt FAISS Index (IndexFlatIP für Initial-Test)
  - [ ] Speichert nach: `backend/v3_data_layer/faiss_indices/atomic_pairs.index`
  - [ ] Speichert Metadaten: `atomic_pairs.meta.json` (pair_id → index mapping)

- [ ] **1.3.3 Build Index mit 1000 Paaren**
  - [ ] Führe aus: `python scripts/build_faiss_atomic_pairs.py`
  - [ ] **Was du sehen solltest**:
    ```
    🔍 Building FAISS atomic_pairs Index
    ──────────────────────────────────
    📖 Loading 1000 prompt_pairs from evoki_v3_core.db...
    ✅ Loaded 1000 pairs
    
    🧮 Generating embeddings (MiniLM-L6-v2, 384D)...
    [Progress bar 100%]
    ✅ Generated 1000 embeddings (~1.5s)
    
    📊 Building FAISS Index...
    ✅ Index built (1000 vectors, 384D)
    
    💾 Saving to: faiss_indices/atomic_pairs.index
    ✅ Saved index (~1.5 MB)
    ✅ Saved metadata (~50 KB)
    
    ⏱️  Total time: ~2.0s
    ```

- [ ] **1.3.4 Test FAISS Search**
  - [ ] Script: `scripts/test_faiss_search.py`
  - [ ] Query: "Ich habe Angst" → sollte ähnliche Prompts finden
  - [ ] Führe aus: `python scripts/test_faiss_search.py --query "Ich habe Angst"`
  - [ ] **Was du sehen solltest**:
    ```
    🔍 FAISS Search Test
    ─────────────────────
    Query: "Ich habe Angst"
    
    Top 5 Results:
    1. [Score: 0.94] Pair ID: abc123... "Ich bin ängstlich..."
    2. [Score: 0.89] Pair ID: def456... "Angst vor der Zukunft..."
    3. [Score: 0.85] Pair ID: ghi789... "Furcht vor dem Unbekannten..."
    4. [Score: 0.82] Pair ID: jkl012... "Sorgen um meine Sicherheit..."
    5. [Score: 0.78] Pair ID: mno345... "Unsicherheit belastet mich..."
    
    ✅ Search completed in ~5ms
    ```

### **PHASE 1 DONE CHECKLIST**:
- ✅ `evoki_v3_core.db` existiert mit 1000 Paaren
- ✅ Alle Tabellen befüllt (prompt_pairs, metrics_full, b_state_evolution, etc.)
- ✅ FAISS atomic_pairs Index gebaut (1000 Vektoren, 384D)
- ✅ FAISS Search funktioniert (Top-5 Ergebnisse plausibel)
- ✅ Performance: ~650 Paare/s Import, ~5ms Search
- ✅ Validierung: 0 Fehler, alle Metriken plausibel

**ZEIT**: ~1-2 Tage (8-16 Stunden Arbeit)  
**OUTPUT**: Funktionierende Core DB + Semantic Search

---

## 📝 **PHASE 2: ANALYTICS + TRAJECTORIES** (1-2 Tage)

### **Ziel**: Analytics DB + Trajectories DB + Historical Futures System

### ✅ **TODO-LISTE PHASE 2**:

#### **2.1 evoki_v3_analytics.db** (~3 Stunden)

- [ ] **2.1.1 Schema initialisieren**
  - [ ] Script: `scripts/init_v3_analytics_db.py`
  - [ ] Lädt `backend/schemas/evoki_v3_analytics_schema.sql`
  - [ ] Erstellt `backend/v3_data_layer/databases/evoki_v3_analytics.db`
  - [ ] **Was du sehen solltest**: DB mit 7 Tabellen erstellt

- [ ] **2.1.2 Logging Pipeline bauen**
  - [ ] Klasse: `AnalyticsLogger` (in `scripts/analytics_logger.py`)
  - [ ] Methoden:
    - [ ] `log_api_request(prompt, context, timestamp)`
    - [ ] `log_api_response(response, b_vector, timestamp)`
    - [ ] `log_search_event(query, results, method)`
    - [ ] `log_metric_evaluation(pair_id, metric_name, value, computation_time)`
    - [ ] `log_learning_event(keyword, frequency, promoted)`
  - [ ] **Was du sehen solltest**: Python-Klasse ~200 Zeilen

- [ ] **2.1.3 Re-Import 1000 Paare MIT Analytics**
  - [ ] Erweitere `v3_importer.py` um Analytics-Logging
  - [ ] Für jedes Paar:
    - [ ] Logge in `prompt_history`
    - [ ] Logge in `metric_evaluations` (alle 322 Metriken)
    - [ ] Simuliere API-Request/Response (für Test)
  - [ ] Führe aus: `python scripts/v3_importer.py --with-analytics --limit 1000`
  - [ ] **Was du sehen solltest**:
    ```
    📊 V3.0 Import mit Analytics
    ────────────────────────────
    ✅ 1000 Paare importiert
    📊 Analytics Stats:
       • prompt_history:        1000 Einträge
       • metric_evaluations:    322,000 Einträge (322 Metriken × 1000 Paare)
       • api_requests:          1000 Einträge (simuliert)
       • api_responses:         1000 Einträge (simuliert)
    ⏱️  Zeit: ~3.0s (330 Paare/s mit Analytics)
    ```

#### **2.2 evoki_v3_trajectories.db** (~4 Stunden)

- [ ] **2.2.1 Schema initialisieren**
  - [ ] Script: `scripts/init_v3_trajectories_db.py`
  - [ ] Erstellt `evoki_v3_trajectories.db` mit 4 Tabellen

- [ ] **2.2.2 Trajectory Calculator bauen**
  - [ ] Klasse: `TrajectoryCalculator` (in `scripts/trajectory_calculator.py`)
  - [ ] Methode: `calculate_trajectory(session_id, current_pair_index, offsets=[-25,-5,-2,-1,0])`
  - [ ] Für jede kritische Metrik (m1_A, m151_hazard, B_safety, etc.):
    - [ ] Lade Werte für Offsets -25, -5, -2, -1, 0
    - [ ] Berechne Gradient (Δ zwischen Werten)
    - [ ] Klassifiziere Trend (rising/falling/stable/volatile)
  - [ ] Speichert in `metric_trajectories` Tabelle
  - [ ] **Was du sehen solltest**: Python-Klasse ~250 Zeilen

- [ ] **2.2.3 Historical Futures Builder**
  - [ ] Klasse: `HistoricalFuturesBuilder` (in `scripts/historical_futures_builder.py`)
  - [ ] Für jedes Paar N:
    - [ ] Prüfe: Existiert Paar N+1, N+2, N+5, N+10, N+25?
    - [ ] Wenn ja: Lade deren Metriken
    - [ ] Speichere in `historical_futures` als JSON:
      ```json
      {
        "future_plus_1": {"m1_A": 0.88, "m151_hazard": 0.72, ...},
        "future_plus_5": {"m1_A": 0.65, "m151_hazard": 0.45, ...},
        ...
      }
      ```
    - [ ] Klassifiziere `outcome_type` (natural_recovery/escalation/stable)
  - [ ] **Was du sehen solltest**: Python-Klasse ~200 Zeilen

- [ ] **2.2.4 Berechne Trajectories + Futures für 1000 Paare**
  - [ ] Script: `scripts/compute_trajectories.py`
  - [ ] Führe aus: `python scripts/compute_trajectories.py`
  - [ ] **Was du sehen solltest**:
    ```
    📈 Computing Trajectories + Historical Futures
    ───────────────────────────────────────────────
    📊 Processing 1000 pairs...
    [Progress bar 100%]
    
    ✅ Trajectories computed:
       • metric_trajectories:  ~5000 Einträge (5 Offsets × 10 Metriken × 100 Sessions)
       • historical_futures:   ~800 Einträge (80% der Paare haben +1 Future)
       
    📊 Outcome Distribution:
       • natural_recovery:  520 (65%)
       • escalation:        160 (20%)
       • stable:            120 (15%)
       
    ⏱️  Zeit: ~5.0s
    ```

#### **2.3 FAISS trajectory_wpf Namespace** (~2 Stunden)

- [ ] **2.3.1 Trajectory Embedder**
  - [ ] Klasse: `TrajectoryEmbedder` (in `scripts/trajectory_embedder.py`)
  - [ ] Konvertiert Trajectory → Vektor:
    ```python
    # Für jede kritische Metrik (m1_A, hazard, B_safety)
    vector = [
        m1_A(-25), m1_A(-5), m1_A(-2), m1_A(-1), m1_A(0),  # 5 Werte
        hazard(-25), hazard(-5), hazard(-2), hazard(-1), hazard(0),  # 5 Werte
        B_safety(-25), ..., B_safety(0),  # 5 Werte
        gradient_m1_A,  # 1 Wert
        gradient_hazard,  # 1 Wert
        trend_code  # 1 Wert (rising=1, falling=-1, stable=0)
    ]
    # Total: ~20-50D (abhängig von Anzahl Metriken)
    ```

- [ ] **2.3.2 Build trajectory_wpf Index**
  - [ ] Script: `scripts/build_faiss_trajectory.py`
  - [ ] Generiert Trajectory-Vektoren für alle Paare mit vollständigen Trajectories
  - [ ] Erstellt FAISS Index
  - [ ] **Was du sehen solltest**:
    ```
    🔍 Building FAISS trajectory_wpf Index
    ───────────────────────────────────────
    📊 Loaded 800 trajectories (80% haben vollständige History)
    🧮 Generating trajectory vectors (custom, ~30D)...
    ✅ Generated 800 vectors
    📊 Built FAISS Index
    ✅ Saved to: faiss_indices/trajectory_wpf.index (~1 MB)
    ```

- [ ] **2.3.3 Test Trajectory-Based Search**
  - [ ] Script: `scripts/test_trajectory_search.py`
  - [ ] Simuliere: User mit steigender Angst (m1_A: 0.5→0.7→0.85)
  - [ ] Query FAISS trajectory_wpf
  - [ ] **Was du sehen solltest**:
    ```
    🔍 Trajectory Search Test
    ─────────────────────────
    Current Trajectory: m1_A rising (0.5→0.85), hazard rising (0.3→0.7)
    
    Top 3 Similar Historical Trajectories:
    1. [Score: 0.92] Session X, Pair #45
       → Trajectory: m1_A 0.48→0.82, hazard 0.28→0.65
       → Outcome: natural_recovery
       → Future +5: m1_A=0.60, hazard=0.40
       
    2. [Score: 0.88] Session Y, Pair #78
       → Trajectory: m1_A 0.52→0.88, hazard 0.35→0.75
       → Outcome: guardian_intervention (at +3)
       
    3. [Score: 0.85] Session Z, Pair #12
       → Trajectory: m1_A 0.45→0.80, hazard 0.30→0.68
       → Outcome: natural_recovery
       → Successful Strategy: soothing_validation
    ```

### **PHASE 2 DONE CHECKLIST**:
- ✅ `evoki_v3_analytics.db` existiert mit vollständigem Logging
- ✅ `evoki_v3_trajectories.db` existiert mit Trajectories + Historical Futures
- ✅ 1000 Paare haben Analytics-Einträge
- ✅ ~800 Paare haben Historical Futures (+1, +5, etc.)
- ✅ FAISS trajectory_wpf Index funktioniert
- ✅ Trajectory-Based Search liefert plausible Ergebnisse

**ZEIT**: ~1-2 Tage (8-16 Stunden)  
**OUTPUT**: Predictive Analytics System funktioniert

---

## 📝 **PHASE 3: LEARNING ENGINES** (2-3 Tage)

### **Ziel**: Learning Keyword Engine + Graph DB + Metrics FAISS

### ✅ **TODO-LISTE PHASE 3**:

#### **3.1 evoki_v3_keywords.db** (~4 Stunden)

- [ ] **3.1.1 Schema initialisieren**
  - [ ] Script: `scripts/init_v3_keywords_db.py`
  - [ ] Erstellt DB mit 4 Tabellen + FTS5 Index

- [ ] **3.1.2 Learning Keyword Engine bauen**
  - [ ] Klasse: `LearningKeywordEngine` (in `scripts/learning_keyword_engine.py`)
  - [ ] **Features**:
    - [ ] Keyword-Extraktion (RAKE Algorithm)
    - [ ] Frequency Tracking (auto-increment)
    - [ ] Promotion System (nach 10+ Hits)
    - [ ] Association Learning (Co-Occurrence)
    - [ ] Live-Indexing (FTS5)
  - [ ] **Was du sehen solltest**: Python-Klasse ~400 Zeilen

- [ ] **3.1.3 Keyword-Extraktion für 1000 Paare**
  - [ ] Script: `scripts/extract_keywords.py`
  - [ ] Für jedes Paar:
    - [ ] Extrahiere Keywords (User + AI Text)
    - [ ] Update Frequency
    - [ ] Track Co-Occurrence
    - [ ] Index in FTS5
  - [ ] **Was du sehen solltest**:
    ```
    🔤 Extracting Keywords from 1000 Pairs
    ───────────────────────────────────────
    [Progress bar 100%]
    
    📊 Results:
       • keyword_registry:      ~5000 unique Keywords
       • keyword_pair_links:    ~15000 Einträge (avg 15 Keywords/Paar)
       • keyword_associations:  ~8000 Co-Occurrences
       • Promoted Keywords:     ~500 (Frequency ≥ 10)
       
    🔝 Top 10 Keywords:
       1. "angst" (Freq: 145, Promoted: YES)
       2. "trauma" (Freq: 98, Promoted: YES)
       3. "evoki" (Freq: 87, Promoted: YES)
       ...
    
    ⏱️  Zeit: ~3.0s
    ```

- [ ] **3.1.4 Test Hybrid Search**
  - [ ] Script: `scripts/test_hybrid_search.py`
  - [ ] Query: "angst trauma"
  - [ ] Kombiniert:
    - [ ] Keyword Search (evoki_v3_keywords.db)
    - [ ] Semantic Search (FAISS atomic_pairs)
    - [ ] Metric Search (FAISS metrics_wpf)
  - [ ] **Was du sehen solltest**:
    ```
    🔍 Hybrid Search Test
    ─────────────────────
    Query: "angst trauma"
    
    ┌─────────────────────────────────────────────┐
    │ KEYWORD SEARCH (Weight: 0.3)                │
    ├─────────────────────────────────────────────┤
    │ 1. Pair #234 (Score: 0.95) "Angst Trauma"  │
    │ 2. Pair #567 (Score: 0.88) "Trauma Angst"  │
    └─────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────┐
    │ SEMANTIC SEARCH (Weight: 0.5)               │
    ├─────────────────────────────────────────────┤
    │ 1. Pair #123 (Score: 0.92) "Furcht..."     │
    │ 2. Pair #456 (Score: 0.85) "Belastung..."  │
    └─────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────┐
    │ FINAL RANKING (Combined)                    │
    ├─────────────────────────────────────────────┤
    │ 1. Pair #234 (Final: 0.93)                  │
    │ 2. Pair #123 (Final: 0.89)                  │
    │ 3. Pair #567 (Final: 0.85)                  │
    └─────────────────────────────────────────────┘
    ```

#### **3.2 evoki_v3_graph.db** (~3 Stunden)

- [ ] **3.2.1 Schema initialisieren**
  - [ ] Script: `scripts/init_v3_graph_db.py`
  - [ ] Erstellt DB mit 3 Tabellen (nodes, edges, clusters)

- [ ] **3.2.2 Graph Builder**
  - [ ] Klasse: `GraphBuilder` (in `scripts/graph_builder.py`)
  - [ ] Für jedes Paar: Erstelle Node
  - [ ] Für jedes Paar: Berechne Edges zu ähnlichen Paaren (FAISS Top-10)
  - [ ] Edge-Gewicht: `0.6 × semantic_similarity + 0.4 × metric_similarity`
  - [ ] **Was du sehen solltest**: Python-Klasse ~300 Zeilen

- [ ] **3.2.3 Build Graph für 1000 Paare**
  - [ ] Script: `scripts/build_graph.py`
  - [ ] **Was du sehen solltest**:
    ```
    🕸️  Building Graph for 1000 Pairs
    ───────────────────────────────────
    [Progress bar 100%]
    
    📊 Results:
       • graph_nodes:   1000 Nodes
       • graph_edges:   ~5000 Edges (avg 5 Edges/Node)
       • Edge weights:  avg 0.65 (good connectivity)
       
    ⏱️  Zeit: ~10.0s
    ```

- [ ] **3.2.4 Cluster Detection**
  - [ ] Script: `scripts/detect_clusters.py`
  - [ ] Algorithmus: Louvain Community Detection
  - [ ] **Was du sehen solltest**:
    ```
    🔍 Detecting Clusters...
    ────────────────────────
    ✅ Found 15 clusters
    
    Top 5 Clusters:
    1. Cluster "Trauma-Themen" (120 Nodes)
    2. Cluster "Technische Fragen" (95 Nodes)
    3. Cluster "Philosophische Reflexionen" (78 Nodes)
    4. Cluster "Guardian-Interventionen" (42 Nodes)
    5. Cluster "Alltags-Gespräche" (180 Nodes)
    ```

#### **3.3 FAISS metrics_wpf Namespace** (~2 Stunden)

- [ ] **3.3.1 Metrics Embedder**
  - [ ] Klasse: `MetricsEmbedder` (in `scripts/metrics_embedder.py`)
  - [ ] Konvertiert 322 Metriken → 322D Vektor
  - [ ] Optional: PCA auf 128D (Performance vs. Accuracy Trade-off)

- [ ] **3.3.2 Build metrics_wpf Index**
  - [ ] Script: `scripts/build_faiss_metrics.py`
  - [ ] **Was du sehen solltest**:
    ```
    🔍 Building FAISS metrics_wpf Index
    ────────────────────────────────────
    📊 Loaded 1000 metric vectors (322D)
    📊 Built FAISS Index
    ✅ Saved to: faiss_indices/metrics_wpf.index (~5 MB)
    ```

- [ ] **3.3.3 Test Metric-Based Search**
  - [ ] Query: Finde Prompts mit ähnlichen Metriken wie Pair #123
  - [ ] **Was du sehen solltest**:
    ```
    🔍 Metric Search Test
    ─────────────────────
    Reference Pair #123:
       m1_A: 0.85, hazard: 0.72, B_safety: 0.65
    
    Top 5 Metric-Similar Pairs:
    1. Pair #456 (Score: 0.95) m1_A: 0.83, hazard: 0.70
    2. Pair #789 (Score: 0.91) m1_A: 0.87, hazard: 0.75
    ...
    ```

### **PHASE 3 DONE CHECKLIST**:
- ✅ Learning Keyword Engine funktioniert (5000 Keywords, 500 promoted)
- ✅ Hybrid Search kombiniert Keyword + Semantic + Metric
- ✅ Graph DB mit 1000 Nodes, 5000 Edges, 15 Clustern
- ✅ FAISS metrics_wpf Index funktioniert
- ✅ Alle 3 FAISS-Namespaces operational

**ZEIT**: ~2-3 Tage (16-24 Stunden)  
**OUTPUT**: Vollständiges Multi-Modal Search System

---

## 📝 **PHASE 4: INTEGRATION + SCALE-UP** (1-2 Tage)

### **Ziel**: Dual-Response API + Full Pipeline + Scale auf 11.016 Paare

### ✅ **TODO-LISTE PHASE 4**:

#### **4.1 Dual-Response API Client** (~4 Stunden)

- [ ] **4.1.1 DualResponseAPIClient Klasse**
  - [ ] Klasse: `DualResponseAPIClient` (in `scripts/dual_response_api_client.py`)
  - [ ] **Methoden**:
    - [ ] `send_request_1(prompt, enriched_context)` → Standard AI-Response
    - [ ] `send_request_2(prompt, lexika_dict)` → B-Vektor Verification
    - [ ] `compare_b_vectors(local_b, api_b)` → Abweichungen loggen
    - [ ] `log_to_analytics(request, response, verification)`
  - [ ] **Was du sehen solltest**: Python-Klasse ~300 Zeilen

- [ ] **4.1.2 Test mit Mock-API**
  - [ ] Erstelle Mock-API (simuliert Google Gemini Response)
  - [ ] Test: 10 Prompts durch Dual-Response Pipeline
  - [ ] **Was du sehen solltest**:
    ```
    🔄 Dual-Response API Test (Mock)
    ─────────────────────────────────
    Prompt 1:
       ✅ Request 1: AI-Response empfangen
       ✅ Request 2: B-Vektor Verification empfangen
       📊 B-Vector Comparison:
          Local:  B_safety=0.89, B_life=0.92
          API:    B_safety=0.91, B_life=0.93
          Delta:  0.02 (acceptable)
       ✅ Logged to analytics
    
    ...
    
    ✅ 10/10 erfolgreiche Dual-Responses
    ```

#### **4.2 Full Pipeline Integration** (~4 Stunden)

- [ ] **4.2.1 End-to-End Pipeline Script**
  - [ ] Script: `scripts/full_pipeline.py`
  - [ ] **Flow**:
    ```
    User Prompt
        ↓
    1. Trajectory berechnen (-25, -5, -2, -1, 0)
    2. FAISS trajectory_wpf suchen → Top-5 Matches
    3. Historical Futures laden
    4. Enriched Context bauen
    5. Dual-Response API Call
    6. Metriken berechnen (322)
    7. B-Vektor berechnen (7D)
    8. DB Updates (5 DBs parallel)
    9. FAISS Updates (3 Indizes)
    10. Keywords extrahieren + lernen
    11. Historical Futures rückwirkend updaten
    12. Analytics loggen
    ```

- [ ] **4.2.2 Test mit 100 neuen Prompts**
  - [ ] Führe aus: `python scripts/full_pipeline.py --test-prompts 100`
  - [ ] **Was du sehen solltest**:
    ```
    🚀 Full Pipeline Test: 100 Prompts
    ───────────────────────────────────
    [Progress bar 100%]
    
    ✅ 100 Prompts verarbeitet
    
    📊 Performance:
       • Avg Context Build Time:  ~100ms
       • Avg API Call Time:       ~500ms (Mock)
       • Avg DB Update Time:      ~200ms
       • TOTAL per Prompt:        ~800ms
       
    📊 Validierung:
       • evoki_v3_core.db:         +100 Paare
       • FAISS atomic_pairs:       +100 Vektoren
       • Keywords:                 +~1500 neue, ~50 promoted
       • Historical Futures:       ~500 Updates (rückwirkend)
       
    ✅ 0 Fehler
    ```

#### **4.3 Scale-Up auf 22.000 Paare** (~4 Stunden)

- [ ] **4.3.1 Load Full History**
  - [ ] Quelle: `tooling/legacy/Evoki_History_Archive/2025/`
  - [ ] Script: `scripts/import_full_history.py`
  - [ ] **Was du sehen solltest**:
    ```
    📥 Importing Full History (22.000 Paare)
    ─────────────────────────────────────────
    [Progress bar 100%]
    
    ✅ 22.000 Paare importiert
    ⏱️  Zeit: ~34.0s (650 Paare/s)
    
    📊 Final Stats:
       • evoki_v3_core.db:         22.000 Paare, ~110 MB
       • evoki_v3_analytics.db:    ~7M Einträge, ~480 MB
       • evoki_v3_trajectories.db: ~17.6k Futures, ~230 MB
       • evoki_v3_keywords.db:     ~100k Keywords, ~25 MB
       • evoki_v3_graph.db:        22k Nodes, 110k Edges, ~67 MB
       
    📊 FAISS Indizes:
       • atomic_pairs:    22.000 Vektoren, ~34 MB
       • metrics_wpf:     22.000 Vektoren, ~28 MB
       • trajectory_wpf:  ~17.6k Vektoren, ~7 MB
       
    ✅ TOTAL: ~912 MB SQLite + ~69 MB FAISS = ~981 MB
    ```

- [ ] **4.3.2 Validierung Full Dataset**
  - [ ] SQL Queries auf allen 5 DBs
  - [ ] FAISS Search Tests (alle 3 Namespaces)
  - [ ] Hybrid Search Test
  - [ ] Trajectory Prediction Test
  - [ ] **Was du sehen solltest**: Alle Tests erfolgreich, 0 Fehler

#### **4.4 Performance Benchmark** (~2 Stunden)

- [ ] **4.4.1 Benchmark Script**
  - [ ] Script: `scripts/benchmark.py`
  - [ ] Tests:
    - [ ] Import Speed (Paare/s)
    - [ ] FAISS Search Speed (ms/query)
    - [ ] DB Query Speed (ms/query)
    - [ ] Full Pipeline Latency (ms/Prompt)

- [ ] **4.4.2 Run Benchmark**
  - [ ] **Was du sehen solltest**:
    ```
    ⚡ Performance Benchmark
    ────────────────────────
    
    📊 Import Speed:
       • Metrik-Berechnung:   ~50ms/Paar
       • DB Write:            ~20ms/Paar
       • FAISS Update:        ~5ms/Paar
       • TOTAL:               ~610 Paare/s
       
    🔍 Search Speed:
       • FAISS Semantic:      ~5ms
       • FAISS Metrics:       ~5ms
       • FAISS Trajectory:    ~5ms
       • Keyword Search:      ~3ms
       • Hybrid Search:       ~15ms (parallel)
       
    🚀 Full Pipeline Latency:
       • Context Build:       ~100ms
       • API Call:            ~500ms (real API)
       • DB Updates:          ~200ms
       • TOTAL:               ~800ms/Prompt
       
    ✅ Performance Target erreicht: \u003c1s per Prompt
    ```

### **PHASE 4 DONE CHECKLIST**:
- ✅ Dual-Response API Client funktioniert
- ✅ Full Pipeline End-to-End getestet
- ✅ 11.016 Paare erfolgreich importiert
- ✅ Alle 5 DBs + 3 FAISS-Indizes operational
- ✅ Performance: ~610 Paare/s Import, ~800ms Full Pipeline Latency
- ✅ Validierung: 0 Fehler, alle Features funktionieren

**ZEIT**: ~1-2 Tage (8-16 Stunden)  
**OUTPUT**: Production-Ready V3.0 Data Layer

---

## 📊 **GESAMT-ZUSAMMENFASSUNG**

### **Total Zeit**: ~1 Woche (40-60 Stunden fokussierte Arbeit)

### **Deliverables**:

1. ✅ **5 SQLite-Datenbanken** (~459 MB mit 11k Paaren)
   - evoki_v3_core.db
   - evoki_v3_graph.db
   - evoki_v3_keywords.db
   - evoki_v3_analytics.db
   - evoki_v3_trajectories.db

2. ✅ **3 FAISS-Namespaces** (~35 MB mit 11k Paaren)
   - atomic_pairs (384D semantic)
   - metrics_wpf (322D metric-based)
   - trajectory_wpf (~30D trajectory-based)

3. ✅ **Python Pipeline-Scripts**:
   - v3_importer.py
   - analytics_logger.py
   - trajectory_calculator.py
   - learning_keyword_engine.py
   - graph_builder.py
   - dual_response_api_client.py
   - full_pipeline.py

4. ✅ **Performance**:
   - Import: ~610 Paare/s
   - Search: ~5-15ms
   - Full Pipeline: ~800ms/Prompt

5. ✅ **Features**:
   - Dual-Gradient System (∇A / ∇B)
   - B-Vektor Evolution (7D Soul Signature)
   - Session Chain (Kryptografische Integrität)
   - Learning Keyword Engine (Auto-Promotion)
   - Metric Trajectory Predictor (Prognosen)
   - Historical Futures (was kam danach?)
   - Hybrid Search (Keyword + Semantic + Metric)

---

## ⚠️ **KRITISCHE REGELN**

1. **ERST 1000 Paare validieren, DANN skalieren**
2. **Jede Phase MUSS erfolgreich abgeschlossen sein** bevor nächste Phase startet
3. **0 Fehler Toleranz** für Core-Features
4. **Alle Outputs loggen** für Debugging
5. **Tests FIRST** (Dry-Run mit 10 Paaren, dann 1000, dann 11k)

---

## 📁 **DATEI-STRUKTUR (Final)**

```
C:\Evoki V3.0 APK-Lokalhost-Google Cloude\
├── backend/
│   ├── schemas/
│   │   ├── evoki_v3_core_schema.sql
│   │   ├── evoki_v3_graph_schema.sql
│   │   ├── evoki_v3_keywords_schema.sql
│   │   ├── evoki_v3_analytics_schema.sql
│   │   └── evoki_v3_trajectories_schema.sql
│   │
│   ├── v3_data_layer/
│   │   ├── databases/
│   │   │   ├── evoki_v3_core.db
│   │   │   ├── evoki_v3_graph.db
│   │   │   ├── evoki_v3_keywords.db
│   │   │   ├── evoki_v3_analytics.db
│   │   │   └── evoki_v3_trajectories.db
│   │   │
│   │   ├── faiss_indices/
│   │   │   ├── atomic_pairs.index
│   │   │   ├── atomic_pairs.meta.json
│   │   │   ├── metrics_wpf.index
│   │   │   ├── metrics_wpf.meta.json
│   │   │   ├── trajectory_wpf.index
│   │   │   └── trajectory_wpf.meta.json
│   │   │
│   │   ├── models/
│   │   │   └── all-MiniLM-L6-v2/
│   │   │
│   │   ├── scripts/
│   │   │   ├── init_v3_core_db.py
│   │   │   ├── v3_importer.py
│   │   │   ├── analytics_logger.py
│   │   │   ├── trajectory_calculator.py
│   │   │   ├── learning_keyword_engine.py
│   │   │   ├── graph_builder.py
│   │   │   ├── dual_response_api_client.py
│   │   │   ├── full_pipeline.py
│   │   │   └── benchmark.py
│   │   │
│   │   ├── tests/
│   │   │   ├── test_faiss_search.py
│   │   │   ├── test_hybrid_search.py
│   │   │   └── test_full_pipeline.py
│   │   │
│   │   └── logs/
│   │       └── import.log
│   │
│   └── test_data/
│       └── 1000_pairs/
│
└── V3_DATA_LAYER_ROADMAP.md (diese Datei)
```

---

**ENDE ROADMAP**

**Nächster Schritt**: Starte mit **PHASE 0 TODO #0.1** (Cleanup alte Artefakte)
