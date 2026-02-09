# 🏗️ EVOKI V3.0 - 4 DATABASE ARCHITECTURE

**Konzept:** Daten-Separation für optimale Performance & Sicherheit!

---

## 📊 DATABASE OVERVIEW

```
EVOKI V3.0 SYSTEM
├── 1. METADATA DB         (evoki_metadata.db)
│   └── Sessions, Turns, Timestamps, File paths
│
├── 2. RESONANCE DB        (evoki_resonance.db)
│   └── Metrics, Trajectories, Embeddings, A_Phys
│
├── 3. PERSONAL TRIGGER DB (evoki_triggers.db)
│   └── User's specific trigger words, patterns, hazards
│
└── 4. META-PATTERN DB     (evoki_metapatterns.db)
    └── Metaphors, speech style, frequent words, themes
```

---

## 🗄️ DATABASE 1: METADATA (evoki_metadata.db)

### **Zweck:** 
Strukturelle Daten, Timestamps, File Management

### **Tables:**

```sql
-- Sessions
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    date_ymd TEXT NOT NULL,
    source_root TEXT,
    turn_count INTEGER,
    duration_minutes REAL,
    created_at TEXT,
    updated_at TEXT
);

-- Turns (Messages)
CREATE TABLE turns (
    turn_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    ts_iso TEXT NOT NULL,
    date_ymd TEXT NOT NULL,
    prompt_num INTEGER,
    role TEXT CHECK(role IN ('user','ai','assistant')),
    text TEXT NOT NULL,
    text_length INTEGER,
    word_count INTEGER,
    file_path TEXT UNIQUE,
    pair_index INTEGER,
    created_at TEXT,
    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);

-- File Tracking
CREATE TABLE source_files (
    file_id INTEGER PRIMARY KEY,
    turn_id TEXT,
    file_path TEXT UNIQUE,
    file_size INTEGER,
    file_hash TEXT,
    ingested_at TEXT,
    FOREIGN KEY(turn_id) REFERENCES turns(turn_id)
);

-- Genesis Chain (Integrity)
CREATE TABLE genesis_chain (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_iso TEXT NOT NULL,
    session_id TEXT,
    turn_id TEXT,
    prev_hash TEXT,
    content_hash TEXT NOT NULL,
    chain_hash TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(session_id),
    FOREIGN KEY(turn_id) REFERENCES turns(turn_id)
);
```

### **Indices:**
```sql
CREATE INDEX idx_turns_session ON turns(session_id);
CREATE INDEX idx_turns_date ON turns(date_ymd);
CREATE INDEX idx_turns_role ON turns(role);
CREATE INDEX idx_chain_timestamp ON genesis_chain(ts_iso);
```

---

## 🌊 DATABASE 2: RESONANCE (evoki_resonance.db)

### **Zweck:**
Metriken, Trajektorien, Embeddings, A_Phys Telemetry

### **Tables:**

```sql
-- Core Metrics
CREATE TABLE metrics (
    turn_id TEXT PRIMARY KEY,
    
    -- INDEXED CRITICAL METRICS
    m1_A REAL,
    m2_PCI REAL,
    m19_z_prox REAL,
    m101_t_panic REAL,
    m110_black_hole REAL,
    m151_hazard REAL,
    F_risk REAL,
    
    -- FULL 168 SPECTRUM
    metrics_json TEXT NOT NULL,
    
    -- FLAGS
    is_alert INTEGER DEFAULT 0,
    guardian_action TEXT,
    
    calculated_at TEXT
);

-- B-Vector Evolution (Soul Signature)
CREATE TABLE b_state_evolution (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id TEXT,
    session_id TEXT,
    
    -- 7D Soul Signature
    B_life REAL,
    B_truth REAL,
    B_depth REAL,
    B_init REAL,
    B_warmth REAL,
    B_safety REAL,
    B_clarity REAL,
    B_align REAL,  -- Composite
    
    timestamp TEXT,
    FOREIGN KEY(turn_id) REFERENCES turns(turn_id)
);

-- Trajectories (∇A, ∇z, etc.)
CREATE TABLE trajectories (
    trajectory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    turn_id TEXT,
    
    -- Gradients (Deltas)
    nabla_A REAL,            -- Affekt change
    nabla_PCI REAL,          -- Complexity change
    nabla_z_prox REAL,       -- Danger change
    nabla_panic REAL,        -- Panic change
    nabla_disso REAL,        -- Dissociation change
    nabla_B_align REAL,      -- Soul alignment change
    
    -- Trajectory metrics
    trajectory_slope REAL,   -- Rate of change
    trajectory_cumsum REAL,  -- Cumulative change
    volatility REAL,         -- Variability
    
    -- Context
    time_delta_seconds REAL,
    turn_distance INTEGER,
    
    timestamp TEXT
);

-- Embeddings (Semantic Vectors)
CREATE TABLE embeddings (
    turn_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    dim INTEGER NOT NULL,
    vector_json TEXT NOT NULL,
    vector_norm REAL,
    created_at TEXT
);

-- A_Phys Telemetry (Physics Engine Details)
CREATE TABLE a_phys_telemetry (
    turn_id TEXT PRIMARY KEY,
    
    -- Core A_Phys
    A_phys REAL,
    A_phys_raw REAL,
    resonance REAL,
    danger REAL,
    
    -- A29 Guardian
    a29_trip INTEGER,
    a29_max_sim REAL,
    a29_id TEXT,
    
    -- Top Contributors (JSON)
    top_resonance_json TEXT,  -- Top 5 memory contributions
    
    -- Context
    active_memories_count INTEGER,
    danger_zone_count INTEGER,
    
    calculated_at TEXT
);

-- Dual-Gradient Analysis (User vs AI)
CREATE TABLE gradient_analysis (
    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_turn_id TEXT,
    ai_turn_id TEXT,
    
    -- User metrics snapshot
    user_A REAL,
    user_z_prox REAL,
    user_panic REAL,
    user_hazard REAL,
    
    -- AI metrics snapshot
    ai_A REAL,
    ai_z_prox REAL,
    ai_panic REAL,
    ai_hazard REAL,
    
    -- Gradients
    nabla_A REAL,
    nabla_z_prox REAL,
    nabla_panic REAL,
    nabla_hazard REAL,
    
    -- Disharmony
    disharmony REAL,
    recommended_action TEXT,  -- 'OK', 'WARN', 'ALERT'
    
    timestamp TEXT
);

-- Hazard Events
CREATE TABLE hazard_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id TEXT,
    session_id TEXT,
    hazard_type TEXT,
    trigger_value REAL,
    action_taken TEXT,
    timestamp TEXT
);
```

### **Indices:**
```sql
CREATE INDEX idx_metrics_z_prox ON metrics(m19_z_prox) WHERE m19_z_prox > 0.5;
CREATE INDEX idx_metrics_hazard ON metrics(m151_hazard) WHERE m151_hazard > 0.5;
CREATE INDEX idx_metrics_alert ON metrics(is_alert) WHERE is_alert = 1;
CREATE INDEX idx_trajectories_session ON trajectories(session_id);
CREATE INDEX idx_gradient_session ON gradient_analysis(session_id);
```

---

## 🎯 DATABASE 3: PERSONAL TRIGGERS (evoki_triggers.db)

### **Zweck:**
User's specific trigger words, trauma markers, hazards

### **Tables:**

```sql
-- Lexikon Matches (Which terms triggered)
CREATE TABLE lexikon_matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id TEXT NOT NULL,
    
    -- Match Details
    lexikon_name TEXT NOT NULL,  -- 'T_PANIC', 'HAZARD_SUICIDE', etc.
    matched_term TEXT NOT NULL,  -- 'umbringen', 'panik', etc.
    term_weight REAL,            -- 1.0, 0.9, etc.
    
    -- Position in text
    char_position INTEGER,
    word_position INTEGER,
    context_snippet TEXT,        -- 10 words around match
    
    -- Metadata
    role TEXT,                   -- 'user' or 'ai'
    timestamp TEXT
);

-- Personal Trauma Markers (Learned over time)
CREATE TABLE personal_trauma_markers (
    marker_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Term
    term TEXT UNIQUE NOT NULL,
    category TEXT,               -- 'PANIC', 'DISSO', 'SUICIDE', etc.
    
    -- Statistics
    occurrence_count INTEGER DEFAULT 1,
    last_seen TEXT,
    first_seen TEXT,
    
    -- User-specific weight (learned)
    base_weight REAL,
    personal_weight REAL,
    
    -- Context
    typical_context TEXT,        -- Common phrases it appears in
    correlation_with_state TEXT  -- JSON: correlates with high z_prox?
);

-- Crisis Patterns (Recurring hazard patterns)
CREATE TABLE crisis_patterns (
    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Pattern
    pattern_type TEXT,           -- 'WORD_SEQUENCE', 'TOPIC', 'TONE_SHIFT'
    pattern_description TEXT,
    pattern_regex TEXT,
    
    -- Statistics
    occurrence_count INTEGER,
    avg_hazard_score REAL,
    max_hazard_score REAL,
    
    -- Temporal
    first_detected TEXT,
    last_detected TEXT,
    
    -- Actions
    recommended_intervention TEXT
);

-- Safety Protocol History
CREATE TABLE safety_interventions (
    intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id TEXT,
    
    -- Trigger
    trigger_type TEXT,           -- 'Z_PROX_CRITICAL', 'SUICIDE_MARKER', etc.
    trigger_value REAL,
    
    -- Action
    action_type TEXT,            -- 'GUARDIAN_ALERT', 'SAFE_MODE', 'PAUSE'
    action_details TEXT,
    
    -- Outcome
    was_effective INTEGER,       -- Did it help?
    follow_up_needed INTEGER,
    
    timestamp TEXT
);
```

### **Indices:**
```sql
CREATE INDEX idx_lexikon_turn ON lexikon_matches(turn_id);
CREATE INDEX idx_lexikon_name ON lexikon_matches(lexikon_name);
CREATE INDEX idx_trauma_term ON personal_trauma_markers(term);
CREATE INDEX idx_trauma_category ON personal_trauma_markers(category);
CREATE INDEX idx_interventions_type ON safety_interventions(trigger_type);
```

---

## 🎨 DATABASE 4: META-PATTERNS (evoki_metapatterns.db)

### **Zweck:**
User's speech style, metaphors, themes, linguistic fingerprint

### **Tables:**

```sql
-- User Vocabulary (Unique to this user)
CREATE TABLE user_vocabulary (
    word_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Word
    word TEXT UNIQUE NOT NULL,
    lemma TEXT,                  -- Base form
    pos_tag TEXT,                -- Part of speech
    
    -- Frequency
    total_count INTEGER DEFAULT 1,
    user_frequency REAL,         -- Relative to corpus
    global_frequency REAL,       -- Relative to general German
    uniqueness_score REAL,       -- How unique to this user?
    
    -- Context
    typical_context TEXT,        -- Common phrases
    emotional_valence REAL,      -- Positive/negative association
    
    -- Temporal
    first_used TEXT,
    last_used TEXT,
    trend TEXT                   -- 'INCREASING', 'STABLE', 'DECREASING'
);

-- Metaphors & Expressions
CREATE TABLE metaphors (
    metaphor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Expression
    expression TEXT NOT NULL,
    category TEXT,               -- 'SPATIAL', 'TIME', 'ANIMAL', etc.
    source_domain TEXT,          -- What it refers to literally
    target_domain TEXT,          -- What it means conceptually
    
    -- Frequency
    usage_count INTEGER DEFAULT 1,
    
    -- Emotional weight
    affekt_correlation REAL,
    depth_correlation REAL,
    
    -- Examples
    example_usage TEXT,
    
    -- Temporal
    first_used TEXT,
    last_used TEXT
);

-- Recurring Themes
CREATE TABLE themes (
    theme_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Theme
    theme_name TEXT UNIQUE NOT NULL,
    description TEXT,
    keywords_json TEXT,          -- List of related keywords
    
    -- Statistics
    session_count INTEGER,       -- How many sessions mention this
    turn_count INTEGER,          -- How many turns
    avg_depth REAL,              -- Avg Ångström when discussing
    avg_affekt REAL,
    
    -- Evolution
    first_appearance TEXT,
    last_appearance TEXT,
    trend TEXT,
    
    -- Relationships
    related_themes_json TEXT     -- Other themes that co-occur
);

-- Speech Patterns (Syntax & Style)
CREATE TABLE speech_patterns (
    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Pattern
    pattern_type TEXT,           -- 'SENTENCE_LENGTH', 'COMPLEXITY', 'FORMALITY'
    pattern_value REAL,
    
    -- Context
    session_id TEXT,
    turn_id TEXT,
    
    -- State correlation
    affekt_at_time REAL,
    z_prox_at_time REAL,
    
    timestamp TEXT
);

-- User Semantic Fingerprint (Overall profile)
CREATE TABLE semantic_fingerprint (
    fingerprint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Time window
    from_date TEXT,
    to_date TEXT,
    turn_count INTEGER,
    
    -- Top vocabulary (JSON)
    top_100_words_json TEXT,
    top_50_metaphors_json TEXT,
    top_20_themes_json TEXT,
    
    -- Style metrics
    avg_sentence_length REAL,
    avg_word_length REAL,
    lexical_diversity REAL,     -- Unique words / total words
    formality_score REAL,
    
    -- Emotional baseline
    baseline_affekt REAL,
    baseline_depth REAL,
    baseline_complexity REAL,
    
    generated_at TEXT
);

-- N-grams (Common phrases)
CREATE TABLE ngrams (
    ngram_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- N-gram
    ngram_text TEXT NOT NULL,
    ngram_length INTEGER,        -- 2-gram, 3-gram, etc.
    
    -- Frequency
    count INTEGER DEFAULT 1,
    
    -- Context
    typical_affekt REAL,
    typical_state TEXT,
    
    first_used TEXT,
    last_used TEXT
);
```

### **Indices:**
```sql
CREATE INDEX idx_vocab_word ON user_vocabulary(word);
CREATE INDEX idx_vocab_uniqueness ON user_vocabulary(uniqueness_score DESC);
CREATE INDEX idx_metaphors_category ON metaphors(category);
CREATE INDEX idx_themes_name ON themes(theme_name);
CREATE INDEX idx_ngrams_text ON ngrams(ngram_text);
CREATE INDEX idx_ngrams_count ON ngrams(count DESC);
```

---

## 📋 TODO LISTS - DATABASE CREATION

### ✅ TODO 1: METADATA DB

- [ ] Create `evoki_metadata.db`
- [ ] Implement schema (sessions, turns, files, chain)
- [ ] Migrate existing turns data
- [ ] Add integrity checks
- [ ] Create backup script

### ✅ TODO 2: RESONANCE DB

- [ ] Create `evoki_resonance.db`
- [ ] Implement schema (metrics, b_state, trajectories, embeddings, a_phys, gradient, hazards)
- [ ] Migrate existing metrics
- [ ] Calculate trajectories from history
- [ ] Implement gradient analysis
- [ ] Add A_Phys telemetry capture

### ✅ TODO 3: PERSONAL TRIGGERS DB

- [ ] Create `evoki_triggers.db`
- [ ] Implement schema (lexikon_matches, personal_trauma_markers, crisis_patterns, interventions)
- [ ] Scan history for trigger matches
- [ ] Build personal trauma marker vocabulary
- [ ] Detect crisis patterns
- [ ] Log safety interventions

### ✅ TODO 4: META-PATTERNS DB

- [ ] Create `evoki_metapatterns.db`
- [ ] Implement schema (vocabulary, metaphors, themes, patterns, fingerprint, ngrams)
- [ ] Extract user vocabulary from history
- [ ] Detect metaphors (NLP)
- [ ] Identify themes (topic modeling)
- [ ] Calculate speech patterns
- [ ] Generate semantic fingerprint
- [ ] Build n-gram index

---

## 🚀 IMPLEMENTATION PRIORITY

1. **P0:** METADATA DB (foundation!)
2. **P0:** RESONANCE DB (core metrics!)
3. **P1:** PERSONAL TRIGGERS DB (safety!)
4. **P2:** META-PATTERNS DB (enrichment!)

---

## 💾 DATABASE SIZES (Estimate)

```
METADATA DB:      ~50 MB  (983 turns × 50 KB/turn)
RESONANCE DB:     ~200 MB (metrics + trajectories + embeddings)
TRIGGERS DB:      ~20 MB  (sparse - only when triggered)
META-PATTERNS DB: ~100 MB (vocabulary + ngrams)
-----------------------------------
TOTAL:            ~370 MB
```

---

## 🎯 BENEFITS

1. **Separation of Concerns:** Each DB has clear purpose
2. **Performance:** Optimized queries per domain
3. **Privacy:** Triggers & patterns separate from metrics
4. **Scalability:** Each DB can grow independently
5. **Backup:** Selective backup strategies
6. **Security:** Different access levels per DB

---

**STATUS:** Architecture defined! Ready for implementation! 🏗️
