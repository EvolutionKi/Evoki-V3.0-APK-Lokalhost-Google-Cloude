# 🗄️ EVOKI V3.0 - KOMPLETTE DATENBANK & TEXT-DATEN PIPELINE ANALYSE

**Quelle:** EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md (Lines ~14,000-18,609)  
**Umfang:** ~4,600 Zeilen Data Layer Specification  
**Status:** ✅ VOLLSTÄNDIG ANALYSIERT  
**Zeit:** 2026-02-08 00:56

---

## 📊 DATENBANK-ARCHITEKTUR OVERVIEW

### **3-DATABASE SYSTEM** (Official V7 Spec):

```
EVOKI V3.0 DATA LAYER
├── 1. evoki_v3_core.db          (SQLite) - Core Prompts & Metrics
├── 2. evoki_v3_vectors.faiss    (FAISS)  - Semantic Search Vectors
└── 3. evoki_v3_graph.db         (SQLite) - Relationship Graph
```

---

## 🗃️ DATABASE 1: evoki_v3_core.db (CORE DATA)

### **Zweck:**
Zentrale Datenbank für Prompts, Metriken, B-Vektoren, Hazards

### **ARCHITEKTUR-PRINZIP:**
**User/AI TRENNUNG überall!**
- User-Metriken separat berechnet (∇A = Nabla-A)
- AI-Metriken separat berechnet (∇B = Nabla-B)
- **Disharmonie = |∇A - ∇B|** (Gradient-Differenz!)

### **TABLES:**

#### **1. sessions**
```sql
CREATE TABLE sessions (\n    session_id      TEXT PRIMARY KEY,\n    conversation_id TEXT NOT NULL,              -- Gemini conversation ID\n    date_ymd        TEXT NOT NULL,\n    source_root     TEXT,\n    \n    -- Session-Level Aggregate Metriken\n    total_pairs     INTEGER DEFAULT 0,\n    avg_user_hazard REAL,\n    avg_disharmony  REAL,\n    \n    created_at      TEXT DEFAULT (datetime('now'))\n);
```

**Purpose:** Top-level container for conversations

---

#### **2. prompt_pairs** ⭐ CRITICAL!
```sql
CREATE TABLE prompt_pairs (\n    pair_id         TEXT PRIMARY KEY,\n    session_id      TEXT NOT NULL REFERENCES sessions(session_id),\n    pair_index      INTEGER NOT NULL,           -- 0-based index in session\n    \n    -- ═══════════════════════════════════════════════════════════════\n    -- USER PROMPT (∇A Input)\n    -- ═══════════════════════════════════════════════════════════════\n    user_text       TEXT NOT NULL,\n    user_ts         TEXT,\n    user_role       TEXT DEFAULT 'user' CHECK(user_role IN ('user')),\n    \n    -- ═══════════════════════════════════════════════════════════════\n    -- AI RESPONSE (∇B Output)\n    -- ═══════════════════════════════════════════════════════════════\n    ai_text         TEXT NOT NULL,\n    ai_ts           TEXT,\n    ai_role         TEXT DEFAULT 'assistant' CHECK(ai_role IN ('ai','assistant')),\n    \n    -- ═══════════════════════════════════════════════════════════════\n    -- METADATA\n    -- ═══════════════════════════════════════════════════════════════\n    file_path       TEXT,                       -- Source file (if ingested)\n    pair_hash       TEXT NOT NULL,              -- SHA256 for integrity\n    \n    created_at      TEXT DEFAULT (datetime('now')),\n    \n    UNIQUE(session_id, pair_index)\n);
```

**KEY INSIGHT:**
- **Atomic unit** = User+AI pair (nicht einzelne Messages!)
- **Warum?** Metriken werden auf BEIDEN berechnet für Gradient-Analyse!

---

#### **3. metrics_full** ⭐⭐⭐ MOST CRITICAL!
```sql
CREATE TABLE metrics_full (\n    pair_id         TEXT PRIMARY KEY REFERENCES prompt_pairs(pair_id),\n    \n    prompt_hash     TEXT NOT NULL,\n    timecode        TEXT NOT NULL,\n    metrics_version TEXT NOT NULL DEFAULT 'v3.0',\n    \n    -- ═══════════════════════════════════════════════════════════════\n    -- USER-METRIKEN (∇A = Nabla-A)\n    -- ═══════════════════════════════════════════════════════════════\n    user_metrics_json   TEXT NOT NULL,          -- ALL 168 metrics!\n    \n    -- Denormalized (indexed for fast queries)\n    user_m1_A           REAL,\n    user_m101_T_panic   REAL,\n    user_m151_hazard    REAL,\n    user_m160_F_risk    REAL,\n    \n    -- ═══════════════════════════════════════════════════════════════\n    -- AI-METRIKEN (∇B = Nabla-B)\n    -- ═══════════════════════════════════════════════════════════════\n    ai_metrics_json     TEXT NOT NULL,          -- ALL 168 metrics!\n    \n    -- Denormalized\n    ai_m1_A             REAL,\n    ai_m2_PCI           REAL,\n    ai_m161_commit      REAL,\n    ai_m160_F_risk      REAL,\n    \n    -- ═══════════════════════════════════════════════════════════════\n    -- DELTA-GRADIENTEN (∇A, ∇B, ∇A-∇B)\n    -- ═══════════════════════════════════════════════════════════════\n    -- User-Gradienten (∇A)\n    delta_user_m1_A         REAL,\n    delta_user_m151_hazard  REAL,\n    \n    -- AI-Gradienten (∇B)\n    delta_ai_m1_A           REAL,\n    delta_ai_m161_commit    REAL,\n    \n    -- ═══════════════════════════════════════════════════════════════\n    -- DIFFERENZ ∇A - ∇B (Disharmonie)\n    -- ═══════════════════════════════════════════════════════════════\n    diff_gradient_affekt    REAL GENERATED ALWAYS AS (\n        delta_user_m1_A - delta_ai_m1_A\n    ) STORED,\n    \n    disharmony_score        REAL GENERATED ALWAYS AS (\n        ABS(user_m1_A - ai_m1_A) + ABS(delta_user_m1_A - delta_ai_m1_A)\n    ) STORED,\n    \n    -- ═══════════════════════════════════════════════════════════════\n    -- AUTO-ALERTS\n    -- ═══════════════════════════════════════════════════════════════\n    user_falling_alert  INTEGER GENERATED ALWAYS AS (\n        CASE WHEN delta_user_m1_A < -0.15 THEN 1 ELSE 0 END\n    ) STORED,\n    \n    ai_falling_alert    INTEGER GENERATED ALWAYS AS (\n        CASE WHEN delta_ai_m161_commit < -0.2 THEN 1 ELSE 0 END\n    ) STORED,\n    \n    created_at      TEXT DEFAULT (datetime('now'))\n);
```

**KEY INSIGHTS:**
1. **DUAL METRICS:** User + AI getrennt!
2. **JSON BLOB:** Volle 168 Metriken gespeichert
3. **INDEXED COLUMNS:** Kritische Metriken für schnelle Queries
4. **GRADIENTS:** Deltas automatisch berechnet
5. **DISHARMONY:** Generierte Spalte |∇A - ∇B|
6. **AUTO-ALERTS:** SQL-Level Triggers!

---

#### **4. session_chain** (Integrity)
```sql
CREATE TABLE session_chain (\n    chain_id        INTEGER PRIMARY KEY AUTOINCREMENT,\n    session_id      TEXT NOT NULL,\n    pair_id         TEXT REFERENCES prompt_pairs(pair_id),\n    \n    prev_hash       TEXT NOT NULL,\n    current_hash    TEXT NOT NULL,              -- SHA256(prev + pair + metrics)\n    \n    is_genesis      INTEGER DEFAULT 0,\n    genesis_anchor  TEXT,                       -- SHA-256: bdb34437be65418a...\n    \n    created_at      TEXT DEFAULT (datetime('now'))\n);
```

**Purpose:** Blockchain-style chain for tamper detection

---

#### **5. b_state_evolution** (Soul Signature)
```sql
CREATE TABLE b_state_evolution (\n    state_id        INTEGER PRIMARY KEY AUTOINCREMENT,\n    session_id      TEXT NOT NULL,\n    pair_id         TEXT REFERENCES prompt_pairs(pair_id),\n    \n    -- 7D Soul-Signature\n    B_life          REAL NOT NULL DEFAULT 1.0,\n    B_truth         REAL NOT NULL DEFAULT 0.85,\n    B_depth         REAL NOT NULL DEFAULT 0.90,\n    B_init          REAL NOT NULL DEFAULT 0.70,\n    B_warmth        REAL NOT NULL DEFAULT 0.75,\n    B_safety        REAL NOT NULL DEFAULT 0.88,\n    B_clarity       REAL NOT NULL DEFAULT 0.82,\n    \n    -- Composite\n    B_align         REAL GENERATED ALWAYS AS (\n        (B_life + B_truth + B_depth + B_init + B_warmth + B_safety + B_clarity) / 7.0\n    ) STORED,\n    \n    delta_B_align   REAL,\n    \n    created_at      TEXT DEFAULT (datetime('now'))\n);
```

**Purpose:** Track evolution of 7D soul signature over time

---

#### **6. hazard_events** (Guardian Protocol)
```sql
CREATE TABLE hazard_events (\n    event_id        INTEGER PRIMARY KEY AUTOINCREMENT,\n    pair_id         TEXT REFERENCES prompt_pairs(pair_id),\n    session_id      TEXT NOT NULL,\n    \n    hazard_score    REAL NOT NULL,\n    hazard_level    TEXT NOT NULL CHECK (hazard_level IN (\n        'low', 'medium', 'high', 'critical'\n    )),\n    \n    guardian_trip   INTEGER DEFAULT 0,          -- 1 = Activated!\n    \n    trigger_markers TEXT,                       -- JSON: [\"suicide\", \"self_harm\"]\n    action_taken    TEXT,\n    \n    created_at      TEXT DEFAULT (datetime('now'))\n);
```

**Purpose:** Log all Guardian Protocol activations

---

## 🔍 DATABASE 2: evoki_v3_vectors.faiss (SEMANTIC SEARCH)

### **FAISS ARCHITECTURE:**

**Unified Index mit 4 NAMESPACES:**

#### **NAMESPACE 1: atomic_pairs**
```python
{
    'dimension': 384,                   # all-MiniLM-L6-v2
    'model': 'all-MiniLM-L6-v2',
    'description': 'User+AI pair embedded together',
    'metadata_per_vector': {
        'pair_id': 'UUID',
        'session_id': 'UUID',
        'pair_index': 'int',
        'user_text_snippet': 'first 100 chars',
        'ai_text_snippet': 'first 100 chars',
        # CRITICAL: Metrics in metadata!
        'user_m1_A': 'float',
        'user_m151_hazard': 'float',
        'ai_m1_A': 'float',
        'disharmony_score': 'float'
    }
}
```

**Purpose:** Semantic search over prompt pairs

---

#### **NAMESPACE 2: context_windows**
```python
{
    'dimension': 384,
    'window_sizes': [5, 15, 25, 50],    # MULTI-SCALE!
    'description': 'Dynamic context windows',
    'metadata_per_vector': {
        'window_id': 'UUID',
        'center_pair_id': 'UUID',
        'window_size': 'int',
        'start_pair_index': 'int',
        'end_pair_index': 'int',
        'avg_user_m1_A': 'float',
        'avg_ai_m1_A': 'float',
        'max_user_m151_hazard': 'float',
        'avg_disharmony': 'float'
    }
}
```

**Purpose:** Multi-scale contextual search

---

#### **NAMESPACE 3: trajectory_wpf** (W-P-F = Was-Passiert-Future)
```python
{
    'dimension': 384,
    'wpf_offsets': [-25, -5, -2, -1, 0, 1, 2, 5, 25],  # PROMPTS not minutes!
    'description': 'Past + Present + Future trajectory',
    'metadata_per_vector': {
        'trajectory_id': 'UUID',
        'anchor_pair_id': 'UUID',
        'offset': 'int',
        'is_prediction': 'bool',
        'gradient_direction': 'float'
    }
}
```

**Purpose:** Temporal trajectory search

---

#### **NAMESPACE 4: metrics_embeddings** ⭐ NEW!
```python
{
    'dimension': 322,                   # 161 User + 161 AI = 322!
    'description': 'All metrics AS vectors for metric-based search',
    'normalization': 'L2',
    'metadata_per_vector': {
        'pair_id': 'UUID',
        'dominant_metric': 'str',       # e.g. \"m101_T_panic\"
        'metric_signature': 'str'       # Cluster label
    }
}
```

**Purpose:** Find similar metric profiles!

---

## 📊 DATABASE 3: evoki_v3_graph.db (RELATIONSHIP GRAPH)

### **SCHEMA:**

#### **graph_nodes**
```sql
CREATE TABLE graph_nodes (\n    node_id         TEXT PRIMARY KEY,           -- = pair_id\n    session_id      TEXT NOT NULL,\n    \n    embedding       BLOB NOT NULL,              -- 384D\n    \n    -- Denormalized metrics (User/AI separate!)\n    user_m1_A       REAL,\n    user_m151_hazard REAL,\n    ai_m1_A         REAL,\n    ai_m161_commit  REAL,\n    \n    disharmony_score REAL,\n    \n    -- Cluster\n    cluster_id      TEXT,\n    cluster_label   TEXT,                       -- \"Trauma\", \"Freude\", etc.\n    \n    created_at      TEXT DEFAULT (datetime('now'))\n);
```

---

#### **graph_edges**
```sql
CREATE TABLE graph_edges (\n    edge_id         INTEGER PRIMARY KEY AUTOINCREMENT,\n    source_node     TEXT NOT NULL REFERENCES graph_nodes(node_id),\n    target_node     TEXT NOT NULL REFERENCES graph_nodes(node_id),\n    \n    semantic_similarity REAL NOT NULL,\n    metric_similarity   REAL NOT NULL,\n    \n    -- Weighted combination\n    combined_weight     REAL GENERATED ALWAYS AS (\n        0.6 * semantic_similarity + 0.4 * metric_similarity\n    ) STORED,\n    \n    edge_type       TEXT DEFAULT 'similarity' CHECK (edge_type IN (\n        'similarity', 'causal', 'thematic', 'temporal'\n    )),\n    \n    created_at      TEXT DEFAULT (datetime('now')),\n    UNIQUE(source_node, target_node)\n);
```

---

#### **graph_clusters**
```sql
CREATE TABLE graph_clusters (\n    cluster_id      TEXT PRIMARY KEY,\n    \n    label           TEXT NOT NULL,\n    description     TEXT,\n    \n    centroid        BLOB,                       -- Average vector\n    \n    -- Cluster stats (User/AI separate!)\n    node_count          INTEGER DEFAULT 0,\n    avg_user_m1_A       REAL,\n    avg_user_m151_hazard REAL,\n    avg_ai_m1_A         REAL,\n    avg_disharmony      REAL,\n    \n    created_at      TEXT DEFAULT (datetime('now'))\n);
```

---

## 🔄 DATA PIPELINE FLOW

### **INGESTION PIPELINE:**

```
1. SOURCE FILES
   └── C:\Users\nicom\Downloads\Chatverlauf\*.md
   
2. PARSE → prompt_pairs
   ├── Extract User/AI pairs
   ├── Generate pair_id (UUID)
   ├── Calculate pair_hash (SHA256)
   └── INSERT INTO prompt_pairs
   
3. CALCULATE METRICS → metrics_full
   ├── User metrics (ALL 168!) → user_metrics_json
   ├── AI metrics (ALL 168!) → ai_metrics_json
   ├── Calculate gradients (∇A, ∇B)
   ├── Calculate disharmony |∇A - ∇B|
   └── INSERT INTO metrics_full
   
4. GENERATE EMBEDDINGS → FAISS
   ├── User+AI pair → Namespace atomic_pairs
   ├── Context windows → Namespace context_windows
   ├── Trajectories → Namespace trajectory_wpf
   ├── Metrics vector → Namespace metrics_embeddings
   └── ADD TO FAISS INDEX
   
5. BUILD GRAPH → evoki_v3_graph.db
   ├── Create node → graph_nodes
   ├── Calculate similarities → graph_edges
   ├── Cluster analysis → graph_clusters
   └── INSERT INTO graph
   
6. INTEGRITY CHAIN → session_chain
   ├── Calculate prev_hash
   ├── Calculate current_hash (SHA256)
   └── INSERT INTO session_chain
   
7. B-VECTOR TRACKING → b_state_evolution
   ├── Calculate 7D B-vector
   ├── Calculate delta_B_align
   └── INSERT INTO b_state_evolution
   
8. HAZARD CHECK → hazard_events
   ├── IF user_m151_hazard > 0.6:
   │   └── Log hazard_event
   └── IF guardian_trip:
       └── Execute safety protocol
```

---

## 📋 KEY DESIGN DECISIONS

### **1. USER/AI SEPARATION:**
✅ **Every metric calculated separately**  
✅ **Enables gradient analysis (∇A vs ∇B)**  
✅ **Detects disharmony in conversation**

### **2. HYBRID STORAGE:**
✅ **JSON blob** = Complete 168 metrics  
✅ **Indexed columns** = Fast queries on critical metrics  
✅ **Best of both worlds!**

### **3. MULTI-SCALE EMBEDDINGS:**
✅ **4 FAISS Namespaces** = Different granularities  
✅ **Prompt-level, Window-level, Trajectory-level, Metric-level**  
✅ **Rich semantic search capabilities**

### **4. GENERATED COLUMNS:**
✅ **SQL computes disharmony automatically**  
✅ **SQL triggers alerts automatically**  
✅ **No redundant code!**

### **5. INTEGRITY CHAIN:**
✅ **SHA-256 blockchain-style**  
✅ **Tamper detection**  
✅ **Genesis anchor validation**

---

## 🎯 COMPARISON: V7 SPEC vs MY 4-DB ARCHITECTURE

| Feature | V7 Spec (3 DBs) | My Architecture (4 DBs) |
|---------|-----------------|-------------------------|
| Core Data | evoki_v3_core.db | evoki_metadata.db + evoki_resonance.db |
| Vectors | evoki_v3_vectors.faiss | (Same, FAISS) |
| Graph | evoki_v3_graph.db | (Same) |
| Triggers | ❌ Not separate | ✅ evoki_triggers.db |
| Meta-patterns | ❌ Not included | ✅ evoki_metapatterns.db |
| **TOTAL** | **3 DBs** | **5 DBs (4 + FAISS)** |

### **MY ENHANCEMENTS:**
1. ✅ **Separate Triggers DB** = Privacy & Security
2. ✅ **Meta-patterns DB** = User linguistic profileing
3. ✅ **Better separation of concerns**

---

## ✅ CONCLUSION

**V7 SPEC HAS:** Extensive 4,600-line Data Layer documentation!

**INCLUDES:**
- Full schema definitions
- FAISS architecture
- Pipeline flow
- Design rationale
- Migration notes from V2.0

**MEINE EMPFEHLUNG:**
- ✅ Use V7 spec as BASE
- ✅ ADD my Triggers & Meta-patterns DBs
- ✅ Result = Best of both worlds!

**NEXT STEPS:**
1. Implement V7 core schemas
2. Add my enhancements (Triggers, Meta-patterns)
3. Create migration scripts
4. Execute T4 backfill

**STATUS:** ✅ DATA LAYER FULLY ANALYZED!
