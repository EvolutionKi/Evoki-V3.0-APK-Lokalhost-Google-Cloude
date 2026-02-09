-- EVOKI V3.0 METRICS SCHEMA V2 (Hybrid Design)
-- Combines SQL indexed columns + JSON blob for full 168 spectrum

-- ==============================================================================
-- PROMPT PAIRS (User ↔ AI)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS prompt_pairs (
    pair_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    pair_index INTEGER NOT NULL,
    user_text TEXT NOT NULL,
    user_timestamp TEXT NOT NULL,
    ai_text TEXT NOT NULL,
    ai_timestamp TEXT NOT NULL,
    pair_hash TEXT NOT NULL,
    UNIQUE(session_id, pair_index)
);

-- ==============================================================================
-- METRICS (Hybrid: Index Columns + JSON Blob)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS metrics_full (
    pair_id TEXT PRIMARY KEY REFERENCES prompt_pairs(pair_id),
    
    -- CRITICAL INDEX COLUMNS (for fast SQL queries)
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
    calculated_at TEXT DEFAULT (datetime('now'))
);

-- ==============================================================================
-- B-STATE EVOLUTION (Soul Signature)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS b_state_evolution (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id TEXT REFERENCES prompt_pairs(pair_id),
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
    
    timestamp TEXT DEFAULT (datetime('now'))
);

-- ==============================================================================
-- SESSION CHAIN (Integrity Chain with prev_hash)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS session_chain (
    chain_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    pair_id TEXT REFERENCES prompt_pairs(pair_id),
    prev_hash TEXT NOT NULL,
    current_hash TEXT NOT NULL,
    timestamp TEXT DEFAULT (datetime('now'))
);

-- ==============================================================================
-- HAZARD EVENTS (Guardian Protocol)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS hazard_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id TEXT REFERENCES prompt_pairs(pair_id),
    hazard_type TEXT,        -- e.g., 'SUICIDE_MARKER', 'Z_PROX_ALERT'
    trigger_value REAL,
    action_taken TEXT,       -- e.g., 'ALERT_GUARDIAN', 'SAFE_MODE'
    timestamp TEXT DEFAULT (datetime('now'))
);

-- ==============================================================================
-- INDICES (Performance)
-- ==============================================================================

CREATE INDEX IF NOT EXISTS idx_metrics_z_prox ON metrics_full(m19_z_prox);
CREATE INDEX IF NOT EXISTS idx_metrics_hazard ON metrics_full(m151_hazard);
CREATE INDEX IF NOT EXISTS idx_metrics_alert ON metrics_full(is_alert);
CREATE INDEX IF NOT EXISTS idx_chain_session ON session_chain(session_id);
CREATE INDEX IF NOT EXISTS idx_hazard_type ON hazard_events(hazard_type);

-- ==============================================================================
-- VIEWS (Convenience)
-- ==============================================================================

CREATE VIEW IF NOT EXISTS v_critical_alerts AS
SELECT 
    pp.pair_id,
    pp.user_text,
    mf.m19_z_prox,
    mf.m151_hazard,
    mf.guardian_action,
    he.hazard_type,
    he.action_taken,
    pp.user_timestamp
FROM prompt_pairs pp
JOIN metrics_full mf ON pp.pair_id = mf.pair_id
LEFT JOIN hazard_events he ON pp.pair_id = he.pair_id
WHERE mf.is_alert = 1
ORDER BY pp.user_timestamp DESC;
