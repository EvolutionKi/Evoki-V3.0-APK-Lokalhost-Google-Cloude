-- ==============================================================================
-- EVOKI V3.0 PRODUCTION SCHEMA (FINAL)
-- ==============================================================================
-- Based on:
--   - Official V7 Patchpaket schema (evoki_history_schema.sql)
--   - User's Hybrid Design (superior for Temple queries!)
--   - Session 2 Integration learnings
--
-- Design: HYBRID (SQL indexed columns + JSON blob)
-- ==============================================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ==============================================================================
-- 1. SESSIONS (Top-Level Container)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    date_ymd TEXT NOT NULL,
    source_root TEXT,
    genesis_hash TEXT,  -- Chain anchor
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ==============================================================================
-- 2. TURNS (Individual User/AI Messages)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS turns (
    turn_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    ts_iso TEXT,
    date_ymd TEXT NOT NULL,
    prompt_num INTEGER,
    role TEXT NOT NULL CHECK(role IN ('user','ai','assistant')),
    text TEXT NOT NULL,
    file_path TEXT UNIQUE,
    pair_index INTEGER,  -- For user-ai pairing
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);

-- ==============================================================================
-- 3. METRICS (HYBRID: Indexed + JSON Blob)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS metrics (
    turn_id TEXT PRIMARY KEY,
    
    -- CRITICAL INDEXED COLUMNS (for fast SQL queries)
    m1_A REAL,              -- Affekt (Consciousness Proxy)
    m2_PCI REAL,            -- Complexity
    m4_flow REAL,           -- Flow State
    m7_LL REAL,             -- Lambert-Light (Turbidity)
    m10_angstrom REAL,      -- Conversation Depth
    m19_z_prox REAL,        -- [CRITICAL] Todesnähe
    m101_t_panic REAL,      -- [CRITICAL] Panic
    m102_t_disso REAL,      -- [CRITICAL] Dissociation
    m103_t_integ REAL,      -- Integration (Healing)
    m110_black_hole REAL,   -- Event Horizon
    m151_hazard REAL,       -- [CRITICAL] Guardian Hazard Score
    F_risk REAL,            -- Future Risk
    m151_omega REAL,        -- Quality Indicator
    m168_cum_stress REAL,   -- Cumulative Stress
    
    -- FULL SPECTRUM CONTAINER (All 168 metrics as JSON)
    metrics_json TEXT NOT NULL,
    
    -- FLAGS
    is_alert INTEGER DEFAULT 0,
    guardian_action TEXT,
    
    -- METADATA
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    FOREIGN KEY(turn_id) REFERENCES turns(turn_id)
);

-- ==============================================================================
-- 4. B-STATE EVOLUTION (Soul Signature Tracking)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS b_state_evolution (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id TEXT,
    session_id TEXT NOT NULL,
    
    -- B-Vector (7 dimensions)
    B_life REAL,
    B_truth REAL,
    B_depth REAL,
    B_init REAL,
    B_warmth REAL,
    B_safety REAL,
    B_clarity REAL,
    B_align REAL,  -- Composite
    
    timestamp TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY(turn_id) REFERENCES turns(turn_id),
    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);

-- ==============================================================================
-- 5. EMBEDDINGS (Semantic Vectors)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS embeddings (
    turn_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    dim INTEGER NOT NULL,
    vector_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(turn_id) REFERENCES turns(turn_id)
);

-- ==============================================================================
-- 6. GENESIS CHAIN (Integrity Chain with prev_hash)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS genesis_chain (
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

-- ==============================================================================
-- 7. HAZARD EVENTS (Guardian Protocol)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS hazard_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id TEXT,
    session_id TEXT,
    hazard_type TEXT,        -- e.g., 'SUICIDE_MARKER', 'Z_PROX_ALERT'
    trigger_value REAL,
    action_taken TEXT,       -- e.g., 'ALERT_GUARDIAN', 'SAFE_MODE'
    timestamp TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY(turn_id) REFERENCES turns(turn_id),
    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);

-- ==============================================================================
-- INDICES (Performance Optimization)
-- ==============================================================================

-- Metrics indices (critical metrics)
CREATE INDEX IF NOT EXISTS idx_metrics_z_prox ON metrics(m19_z_prox) WHERE m19_z_prox > 0.5;
CREATE INDEX IF NOT EXISTS idx_metrics_hazard ON metrics(m151_hazard) WHERE m151_hazard > 0.5;
CREATE INDEX IF NOT EXISTS idx_metrics_alert ON metrics(is_alert) WHERE is_alert = 1;
CREATE INDEX IF NOT EXISTS idx_metrics_A ON metrics(m1_A);

-- Session/Turn indices
CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id);
CREATE INDEX IF NOT EXISTS idx_turns_date ON turns(date_ymd);
CREATE INDEX IF NOT EXISTS idx_turns_role ON turns(role);

-- Chain indices
CREATE INDEX IF NOT EXISTS idx_chain_session ON genesis_chain(session_id);
CREATE INDEX IF NOT EXISTS idx_chain_timestamp ON genesis_chain(ts_iso);

-- Hazard indices
CREATE INDEX IF NOT EXISTS idx_hazard_type ON hazard_events(hazard_type);
CREATE INDEX IF NOT EXISTS idx_hazard_session ON hazard_events(session_id);

-- ==============================================================================
-- VIEWS (Convenience Queries)
-- ==============================================================================

-- V1: Critical Alerts View
CREATE VIEW IF NOT EXISTS v_critical_alerts AS
SELECT 
    t.turn_id,
    t.session_id,
    t.text,
    t.role,
    t.ts_iso,
    m.m19_z_prox,
    m.m151_hazard,
    m.guardian_action,
    he.hazard_type,
    he.action_taken
FROM turns t
JOIN metrics m ON t.turn_id = m.turn_id
LEFT JOIN hazard_events he ON t.turn_id = he.turn_id
WHERE m.is_alert = 1
ORDER BY t.ts_iso DESC;

-- V2: Session Health Summary
CREATE VIEW IF NOT EXISTS v_session_health AS
SELECT 
    t.session_id,
    COUNT(*) as turn_count,
    AVG(m.m1_A) as avg_affekt,
    AVG(m.m19_z_prox) as avg_z_prox,
    MAX(m.m19_z_prox) as max_z_prox,
    SUM(m.is_alert) as alert_count,
    AVG(b.B_align) as avg_b_align
FROM turns t
JOIN metrics m ON t.turn_id = m.turn_id
LEFT JOIN b_state_evolution b ON t.turn_id = b.turn_id
GROUP BY t.session_id;

-- V3: User Prompts Only (for Temple display)
CREATE VIEW IF NOT EXISTS v_user_prompts AS
SELECT 
    t.turn_id,
    t.session_id,
    t.text,
    t.ts_iso,
    m.m1_A,
    m.m19_z_prox,
    m.m151_hazard,
    m.F_risk
FROM turns t
JOIN metrics m ON t.turn_id = m.turn_id
WHERE t.role = 'user'
ORDER BY t.ts_iso DESC;

-- ==============================================================================
-- COMMENTS
-- ==============================================================================

-- Design Rationale:
-- 1. HYBRID METRICS: Combines SQL-indexed columns (fast WHERE clauses) with 
--    JSON blob (complete 168 spectrum). Best of both worlds.
--
-- 2. NORMALIZED: Separates turns, metrics, embeddings, b_state into proper tables.
--
-- 3. CHAIN INTEGRITY: genesis_chain tracks prev_hash for tamper detection.
--
-- 4. GUARDIAN READY: hazard_events + is_alert flag for safety protocol.
--
-- 5. TEMPLE OPTIMIZED: Views provide instant access to critical data for UI.
--
-- 6. COMPATIBLE: Extends official V7 schema with production enhancements.

-- ==============================================================================
-- END OF SCHEMA
-- ==============================================================================
