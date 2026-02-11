# EVOKI V3.0 - FINAL HYBRID DATABASE ARCHITECTURE

**Version:** V3.0 HYBRID (BUCH 7 + Enhancements)
**Created:** 2026-02-08
**Status:** PRODUCTION READY

---

## COMPLETE ARCHITECTURE OVERVIEW

### 5-DATABASE SYSTEM (BUCH 7 + Enhancements)

```
EVOKI V3.0 COMPLETE DATA LAYER
├── 1. evoki_v3_core.db          (SQLite) - Core Prompts & Metrics [BUCH 7]
├── 2. evoki_v3_graph.db         (SQLite) - Relationship Graph [BUCH 7]
├── 3. evoki_v3_vectors.faiss    (FAISS)  - Semantic Search [BUCH 7]
├── 4. evoki_triggers.db         (SQLite) - Personal Triggers [ENHANCEMENT]
└── 5. evoki_metapatterns.db     (SQLite) - User Linguistics [ENHANCEMENT]
```

---

## ARCHITECTURAL DECISION RATIONALE

### WHY 5 DATABASES?

| Database | Purpose | Separation Reason |
|----------|---------|-------------------|
| core | Prompts, Metrics, Chain | Core system data, high write frequency |
| graph | Relationships, Clusters | Graph operations separate from linear data |
| vectors | FAISS indices | Different storage engine (FAISS vs SQLite) |
| triggers | Crisis patterns | Privacy: Keep sensitive patterns isolated |
| metapatterns | Linguistics | Scale: Large vocab/ngram tables grow fast |

### BENEFITS

- **Performance:** Each DB optimized for its workload
- **Privacy:** Sensitive patterns isolated
- **Scalability:** Large tables don't slow down core queries
- **Backup:** Granular backup strategies
- **Security:** Fine-grained access control

---

## DATABASE SCHEMAS

### 1. evoki_v3_core.db (BUCH 7)

**Tables:**
- `sessions` - Session containers
- `prompt_pairs` - Atomic User+AI pairs
- `metrics_full` - DUAL METRICS (User nabla-A + AI nabla-B)
- `session_chain` - Blockchain-style integrity
- `b_state_evolution` - 7D Soul-Signature tracking
- `hazard_events` - Guardian Protocol log

**File:** `backend/schemas/BUCH7_evoki_v3_core_schema.sql`

**Key Features:**
- User/AI metrics separated
- Gradients calculated (nabla-A, nabla-B, |nabla-A - nabla-B|)
- Auto-alerts via generated columns
- SHA-256 integrity chain

---

### 2. evoki_v3_graph.db (BUCH 7)

**Tables:**
- `graph_nodes` - Prompt pairs as nodes
- `graph_edges` - Semantic + Metric similarities
- `graph_clusters` - Auto-detected themes
- `graph_paths` - Precomputed navigation paths

**Views:**
- `v_cluster_summary` - Cluster statistics
- `v_high_risk_nodes` - Guardian hotspots
- `v_hub_nodes` - Most connected nodes

**File:** `backend/schemas/BUCH7_evoki_v3_graph_schema.sql`

**Key Features:**
- Hybrid similarity (semantic + metric)
- Multiple edge types (causal, thematic, temporal)
- Path caching for performance

---

### 3. evoki_v3_vectors.faiss (BUCH 7)

**4 FAISS Namespaces:**

| Namespace | Dimensions | Content |
|-----------|------------|---------|
| NS1: `atomic_pairs` | 384D | User+AI pairs embedded together, metrics in metadata |
| NS2: `context_windows` | 384D | Multi-scale windows: 5, 15, 25, 50 prompts with aggregated metrics |
| NS3: `trajectory_wpf` | 384D | W-P-F: Past + Present + Future, Offsets: -25, -5, -2, -1, 0, +1, +2, +5, +25 |
| NS4: `metrics_embeddings` | 322D | Metrics themselves as vectors: 161 User + 161 AI = 322D |

**File:** `backend/core/BUCH7_evoki_v3_vector_store.py`

**Key Features:**
- Unified index (not 6+ folders like V2.0!)
- Dynamic updates
- L2 normalization

---

### 4. evoki_triggers.db (ENHANCEMENT)

**Tables:**
- `lexikon_matches` - Which terms triggered
- `personal_trauma_markers` - Learned over time
- `crisis_patterns` - Recurring hazards
- `safety_interventions` - Guardian history

**File:** `backend/schemas/evoki_triggers_schema.sql`

**NEW Capabilities:**
- Learn user-specific trigger words
- Pattern detection (not just keyword matching!)
- Intervention effectiveness tracking

**Why Separate?**
- Privacy: Most sensitive data
- Security: Restrict access
- Focus: Guardian can query ONLY this DB

---

### 5. evoki_metapatterns.db (ENHANCEMENT)

**Tables:**
- `user_vocabulary` - Unique words & frequency
- `metaphors` - User's expressions
- `themes` - Recurring topics
- `speech_patterns` - Syntax & style
- `semantic_fingerprint` - Overall profile
- `ngrams` - Common phrases (2-5 grams)

**Views:**
- `v_top_unique_words` - Linguistic fingerprint
- `v_active_themes` - Recent topics
- `v_frequent_ngrams` - Speech habits

**File:** `backend/schemas/evoki_metapatterns_schema.sql`

**NEW Capabilities:**
- Track vocabulary evolution
- Detect metaphor patterns
- Build linguistic fingerprint
- Measure lexical diversity

**Why Separate?**
- Scale: Can grow to millions of n-grams
- AI Training: Separate corpus for personalization
- Analysis: Complex NLP queries don't slow core

---

## DATA FLOW PIPELINE

### Ingestion Flow

```
1. SOURCE --> prompt_pairs (core)
   └── Parse User/AI pairs

2. CALCULATE --> metrics_full (core)
   ├── User metrics (ALL 168)
   ├── AI metrics (ALL 168)
   ├── Gradients (nabla-A, nabla-B)
   └── Disharmony |nabla-A - nabla-B|

3. EMBED --> FAISS (vectors)
   ├── Namespace: atomic_pairs
   ├── Namespace: context_windows
   ├── Namespace: trajectory_wpf
   └── Namespace: metrics_embeddings

4. BUILD GRAPH --> graph_nodes/edges (graph)
   ├── Calculate similarities
   ├── Cluster analysis
   └── Path precomputation

5. INTEGRITY --> session_chain (core)
   └── SHA-256 blockchain

6. B-VECTOR --> b_state_evolution (core)
   └── 7D Soul-Signature

7. HAZARD CHECK --> hazard_events (core)
   └── IF m151_hazard > 0.6

8. LEXIKON ANALYSIS --> lexikon_matches (triggers)
   └── Track which terms triggered

9. LINGUISTICS --> user_vocabulary/ngrams (metapatterns)
   └── Update word frequencies, n-grams
```

---

## SCHEMA COMPARISON

| Feature | BUCH 7 (3 DBs) | HYBRID (5 DBs) | Benefit |
|---------|-----------------|-----------------|---------|
| Core Data | evoki_v3_core | evoki_v3_core | Same |
| Graph | evoki_v3_graph | evoki_v3_graph | Same |
| Vectors | evoki_v3_vectors | evoki_v3_vectors | Same |
| Personal Triggers | -- | evoki_triggers | Privacy! |
| Linguistics | -- | evoki_metapatterns | Personalization! |
| **TOTAL** | **3** | **5** | **+2 DBs** |

---

## ADVANTAGES OF HYBRID

### Over BUCH 7 alone:
- **Privacy:** Trigger words isolated
- **Personalization:** Linguistic fingerprint
- **Scale:** Large tables don't impact core
- **Guardian:** Focused hazard DB

### Over original 4-DB plan:
- **Graph DB:** BUCH 7 has better graph schema!
- **FAISS:** 4 namespaces vs simpler approach
- **Integrity Chain:** SHA-256 blockchain
- **Official:** Aligned with V7 spec

---

## IMPLEMENTATION PRIORITY

### PHASE 1: Core Foundation (P0)
1. Create `evoki_v3_core.db`
2. Implement `sessions` + `prompt_pairs`
3. Implement `metrics_full` (DUAL METRICS!)
4. Test integrity chain

### PHASE 2: Search & Navigation (P0)
1. Initialize FAISS indices (4 namespaces)
2. Implement embedding pipeline
3. Test search across namespaces

### PHASE 3: Graph & Analysis (P1)
1. Create `evoki_v3_graph.db`
2. Build graph from core data
3. Cluster analysis
4. Path computation

### PHASE 4: Enhancements (P2)
1. Create `evoki_triggers.db`
2. Implement lexikon tracking
3. Create `evoki_metapatterns.db`
4. Implement linguistic analysis

---

## FILE LOCATIONS

```
backend/schemas/
├── BUCH7_evoki_v3_core_schema.sql        <-- From BUCH 7
├── BUCH7_evoki_v3_graph_schema.sql       <-- From BUCH 7
├── evoki_triggers_schema.sql             <-- Enhancement
└── evoki_metapatterns_schema.sql         <-- Enhancement

backend/core/
└── BUCH7_evoki_v3_vector_store.py        <-- From BUCH 7

backend/data/
├── evoki_v3_core.db                      <-- Generated
├── evoki_v3_graph.db                     <-- Generated
├── evoki_triggers.db                     <-- Generated
├── evoki_metapatterns.db                 <-- Generated
└── vectors/
    ├── atomic_pairs.index                <-- FAISS
    ├── context_windows.index             <-- FAISS
    ├── trajectory_wpf.index              <-- FAISS
    └── metrics_embeddings.index          <-- FAISS
```

---

## NEXT STEPS

### Immediate:
- DONE: Extract all schemas
- TODO: Create initialization script
- TODO: Implement ingestion pipeline
- TODO: Execute T4 backfill

### T4 METRICS BACKFILL
Per `T4_METRICS_BACKFILL_ROADMAP.md`:
1. Calculate ALL 168 metrics for existing history
2. Populate `metrics_full` with DUAL metrics
3. Generate embeddings for all 4 namespaces
4. Build graph from existing data

---

## CRITICAL INSIGHTS

### From BUCH 7:
- **User/AI Separation:** Gradient analysis requires separate metrics!
- **4 FAISS Namespaces:** Multi-scale search is powerful
- **Integrity Chain:** SHA-256 blockchain for tamper detection
- **Generated Columns:** SQL calculates disharmony automatically!

### From Enhancements:
- **Triggers DB:** Learn user-specific patterns over time
- **Meta-patterns DB:** Build linguistic fingerprint
- **Privacy:** Sensitive data deserves its own DB
- **Scale:** Large analytical tables separate from core

---

## CONCLUSION

**HYBRID ARCHITECTURE = BEST OF BOTH WORLDS!**

- BUCH 7's robust core (3 DBs)
- Privacy & personalization enhancements (2 DBs)
- Complete data pipeline documented
- Ready for implementation!

**Total: 5 Databases + 4 FAISS Namespaces**

**Status: ARCHITECTURE COMPLETE!**

**Next: Implement initialization & execute T4 backfill!**
