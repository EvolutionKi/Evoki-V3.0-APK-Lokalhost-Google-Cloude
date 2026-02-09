-- ═══════════════════════════════════════════════════════════════════════════
-- EVOKI V3.0 - TRIGGERS DATABASE (Trauma & Hazard, NO TEXT!)
-- ═══════════════════════════════════════════════════════════════════════════
-- Database: evoki_triggers.db
-- Purpose: Trauma metrics, hazard detection, guardian protocol
-- WICHTIG: KEINE vollen Texte! Nur: pair_id, hash, timecode, matched_term
-- ═══════════════════════════════════════════════════════════════════════════

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 1: trauma_metrics (m101-m115) - USER ONLY!
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE trauma_metrics (
    metric_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL UNIQUE,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    author          TEXT NOT NULL CHECK (author = 'user'),  -- Only user has trauma!
    
    -- TRAUMA SPECTRUM (m101-m115)
    m101_T_panic        REAL,
    m102_T_disso        REAL,
    m103_T_integ        REAL,
    m104_T_shock        REAL,
    m105_T_fog          REAL,
    m106_T_numb         REAL,
    m107_T_hurt         REAL,
    m108_T_fear         REAL,
    m109_T_rage         REAL,
    m110_black_hole     REAL,
    m111_T_guard        REAL,
    m112_T_safe         REAL,
    m113_T_ground       REAL,
    m114_T_release      REAL,
    m115_T_hope         REAL,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_trauma_pair ON trauma_metrics(pair_id);
CREATE INDEX idx_trauma_panic ON trauma_metrics(m101_T_panic);
CREATE INDEX idx_trauma_blackhole ON trauma_metrics(m110_black_hole);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 2: hazard_metrics (m151, m160) - CRITICAL!
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE hazard_metrics (
    metric_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL UNIQUE,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    author          TEXT NOT NULL CHECK (author = 'user'),  -- Only user has hazard!
    
    -- HAZARD SCORES
    m151_hazard     REAL NOT NULL,
    m160_F_risk     REAL NOT NULL,
    
    -- GUARDIAN TRIGGER
    guardian_trip   INTEGER GENERATED ALWAYS AS (
        CASE WHEN m151_hazard > 0.8 THEN 1 ELSE 0 END
    ) STORED,
    
    hazard_level    TEXT GENERATED ALWAYS AS (
        CASE 
            WHEN m151_hazard > 0.8 THEN 'critical'
            WHEN m151_hazard > 0.6 THEN 'high'
            WHEN m151_hazard > 0.3 THEN 'medium'
            ELSE 'low'
        END
    ) STORED,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_hazard_pair ON hazard_metrics(pair_id);
CREATE INDEX idx_hazard_score ON hazard_metrics(m151_hazard DESC);
CREATE INDEX idx_hazard_guardian ON hazard_metrics(guardian_trip);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 3: lexikon_matches (NO TEXT! Only matched term)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE lexikon_matches (
    match_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    author          TEXT NOT NULL CHECK (author IN ('user', 'ai')),
    
    -- MATCH DETAILS (NO full text! Only matched term!)
    lexikon_name    TEXT NOT NULL,  -- 'T_PANIC', 'HAZARD_SUICIDE', etc.
    matched_term    TEXT NOT NULL,  -- 'umbringen', 'panik', etc.
    term_weight     REAL,
    
    -- POSITION (for reconstruction)
    char_position   INTEGER,
    word_position   INTEGER,
    context_snippet TEXT,           -- Only 10 words around match!
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_lexmatch_pair ON lexikon_matches(pair_id);
CREATE INDEX idx_lexmatch_lexikon ON lexikon_matches(lexikon_name);
CREATE INDEX idx_lexmatch_term ON lexikon_matches(matched_term);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 4: personal_trauma_markers (Learned over time)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE personal_trauma_markers (
    marker_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- TERM (NO full text!)
    term            TEXT UNIQUE NOT NULL,
    category        TEXT,  -- 'PANIC', 'DISSO', 'SUICIDE', etc.
    
    -- STATISTICS
    occurrence_count    INTEGER DEFAULT 1,
    last_seen           TEXT,
    first_seen          TEXT,
    
    -- LEARNED WEIGHT
    base_weight         REAL,
    personal_weight     REAL,  -- User-specific!
    
    -- CONTEXT (aggregated, not full text!)
    typical_context     TEXT,  -- Common phrases
    correlation_json    TEXT,  -- JSON: correlates with which metrics?
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_ptrauma_term ON personal_trauma_markers(term);
CREATE INDEX idx_ptrauma_category ON personal_trauma_markers(category);
CREATE INDEX idx_ptrauma_weight ON personal_trauma_markers(personal_weight DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 5: crisis_patterns (Recurring hazard patterns)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE crisis_patterns (
    pattern_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- PATTERN (NO full text!)
    pattern_type    TEXT,  -- 'WORD_SEQUENCE', 'TOPIC', 'TONE_SHIFT'
    pattern_desc    TEXT,
    pattern_regex   TEXT,
    
    -- STATISTICS
    occurrence_count    INTEGER,
    avg_hazard_score    REAL,
    max_hazard_score    REAL,
    
    -- TEMPORAL
    first_detected  TEXT,
    last_detected   TEXT,
    
    -- ACTION
    recommended_intervention TEXT,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_crispat_type ON crisis_patterns(pattern_type);
CREATE INDEX idx_crispat_hazard ON crisis_patterns(avg_hazard_score DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 6: safety_interventions (Guardian Protocol History)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE safety_interventions (
    intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT,
    pair_hash       TEXT,
    timecode        TEXT,
    
    -- TRIGGER
    trigger_type    TEXT,  -- 'Z_PROX_CRITICAL', 'SUICIDE_MARKER', etc.
    trigger_value   REAL,
    
    -- ACTION
    action_type     TEXT,  -- 'GUARDIAN_ALERT', 'SAFE_MODE', 'PAUSE'
    action_details  TEXT,
    
    -- OUTCOME
    was_effective   INTEGER,
    follow_up_needed INTEGER,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_interv_type ON safety_interventions(trigger_type);
CREATE INDEX idx_interv_time ON safety_interventions(created_at);

-- ═══════════════════════════════════════════════════════════════════════════
-- END: evoki_triggers.db
-- ═══════════════════════════════════════════════════════════════════════════
