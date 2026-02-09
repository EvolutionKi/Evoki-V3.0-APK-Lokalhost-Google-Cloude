-- evoki_v3_core_schema.sql
-- Core Database Schema for Evoki V3.0
-- Implements DUAL-GRADIENT system (User vs. AI metrics)

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- =============================================================================
-- 1. PROMPT_PAIRS — Zentrale Prompt-Paar Tabelle
-- =============================================================================

CREATE TABLE IF NOT EXISTS prompt_pairs (
  pair_id TEXT PRIMARY KEY,           -- UUID für Prompt-Paar
  session_id TEXT NOT NULL,           -- Session-Zugehörigkeit
  turn_number INTEGER NOT NULL,       -- Reihenfolge in Session
  
  -- Timestamps
  created_at TEXT NOT NULL,           -- ISO 8601 Timestamp
  ts_unix REAL NOT NULL,              -- Unix Timestamp (für Berechnungen)
  
  -- User Prompt
  user_text TEXT NOT NULL,            -- User-Input (TEXT!)
  user_text_hash TEXT NOT NULL,      -- SHA256 für Deduplizierung
  
  -- AI Response
  ai_text TEXT NOT NULL,              -- AI-Response (TEXT!)
  ai_text_hash TEXT NOT NULL,         -- SHA256
  
  -- Metadata
  context_json TEXT,                  -- Zusätzlicher Kontext (JSON)
  tags TEXT,                          -- Comma-separated Tags
  
  UNIQUE(session_id, turn_number)
);

CREATE INDEX idx_prompt_pairs_session ON prompt_pairs(session_id);
CREATE INDEX idx_prompt_pairs_created ON prompt_pairs(created_at);
CREATE INDEX idx_prompt_pairs_user_hash ON prompt_pairs(user_text_hash);


-- =============================================================================
-- 2. METRICS_FULL — DUAL-GRADIENT Metrics (User vs. AI)
-- =============================================================================

CREATE TABLE IF NOT EXISTS metrics_full (
  pair_id TEXT PRIMARY KEY,           -- Foreign Key zu prompt_pairs
  
  -- === USER METRICS (m1-m168) ===
  -- Core Metrics (m1-m27)
  user_m1_A REAL,
  user_m2_PCI REAL,
  user_m3_gen_index REAL,
  user_m4_flow REAL,
  user_m5_coh REAL,
  user_m6_ZLF REAL,
  user_m7_LL REAL,
  user_m8_x_exist REAL,
  user_m9_b_past REAL,
  user_m10_angstrom REAL,
  user_m11_gap_s REAL,
  user_m12_gap_norm REAL,
  user_m13_rep_same REAL,
  user_m14_rep_history REAL,
  user_m15_affekt_a REAL,
  -- ... (weitere 153 User-Metriken)
  
  -- === AI METRICS (m1-m168) ===
  ai_m1_A REAL,
  ai_m2_PCI REAL,
  ai_m3_gen_index REAL,
  ai_m4_flow REAL,
  ai_m5_coh REAL,
  ai_m6_ZLF REAL,
  ai_m7_LL REAL,
  ai_m8_x_exist REAL,
  ai_m9_b_past REAL,
  ai_m10_angstrom REAL,
  -- ... (weitere AI-Metriken)
  
  -- === DELTA METRICS (∇User, ∇AI) ===
  delta_user_m1_A REAL,               -- ∇A (User)
  delta_ai_m1_A REAL,                 -- ∇A (AI)
  diff_gradient_m1_A REAL,            -- |∇A_user - ∇A_ai|
  
  -- === COMPOSITE METRICS ===
  disharmony_score REAL,              -- Overall |∇User - ∇AI|
  
  -- Metadata
  computation_time_ms REAL,
  schema_version TEXT DEFAULT 'v3.0',
  
  FOREIGN KEY(pair_id) REFERENCES prompt_pairs(pair_id)
);

CREATE INDEX idx_metrics_full_pair_id ON metrics_full(pair_id);


-- =============================================================================
-- 3. SESSION_CHAIN — Kryptografische Verkettung
-- =============================================================================

CREATE TABLE IF NOT EXISTS session_chain (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  pair_id TEXT NOT NULL,
  turn_number INTEGER NOT NULL,
  
  -- Chain Hashes
  prev_hash TEXT,                     -- Hash des vorherigen Eintrags
  content_hash TEXT NOT NULL,         -- SHA256(pair_id + metrics)
  chain_hash TEXT NOT NULL,           -- SHA256(prev_hash + content_hash)
  
  created_at TEXT NOT NULL,
  
  FOREIGN KEY(pair_id) REFERENCES prompt_pairs(pair_id)
);

CREATE INDEX idx_session_chain_session ON session_chain(session_id);
CREATE INDEX idx_session_chain_pair ON session_chain(pair_id);


-- =============================================================================
-- 4. B_STATE_EVOLUTION — 7D B-Vektor Historie
-- =============================================================================

CREATE TABLE IF NOT EXISTS b_state_evolution (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pair_id TEXT NOT NULL,
  
  -- 7 B-Vektor Dimensionen
  b_life REAL NOT NULL,
  b_truth REAL NOT NULL,
  b_depth REAL NOT NULL,
  b_init REAL NOT NULL,
  b_warmth REAL NOT NULL,
  b_safety REAL NOT NULL,
  b_clarity REAL NOT NULL,
  
  -- Composite
  b_score REAL NOT NULL,              -- Gewichteter Composite Score
  b_alignment REAL NOT NULL,          -- Alignment zu Golden B-Vektor
  
  -- Deltas (vs. previous)
  delta_b_life REAL,
  delta_b_truth REAL,
  delta_b_depth REAL,
  delta_b_init REAL,
  delta_b_warmth REAL,
  delta_b_safety REAL,
  delta_b_clarity REAL,
  
  created_at TEXT NOT NULL,
  
  FOREIGN KEY(pair_id) REFERENCES prompt_pairs(pair_id)
);

CREATE INDEX idx_b_state_pair ON b_state_evolution(pair_id);
CREATE INDEX idx_b_state_created ON b_state_evolution(created_at);


-- =============================================================================
-- 5. HAZARD_EVENTS — Guardian Protocol Events (A29)
-- =============================================================================

CREATE TABLE IF NOT EXISTS hazard_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pair_id TEXT NOT NULL,
  
  -- Detection
  hazard_type TEXT NOT NULL,          -- 'suicide', 'self_harm', 'crisis', 'panic', 'disso'
  severity REAL NOT NULL,             -- [0, 1]
  is_critical BOOLEAN NOT NULL,       -- Guardian Trip?
  
  -- Metrics at detection
  f_risk_z REAL,
  z_prox REAL,
  angstrom_depth REAL,
  
  -- Matched Terms (JSON array)
  matched_terms_json TEXT,
  
  -- Response
  intervention_taken BOOLEAN,
  intervention_type TEXT,             -- 'warning', 'block', 'emergency_contact'
  
  created_at TEXT NOT NULL,
  
  FOREIGN KEY(pair_id) REFERENCES prompt_pairs(pair_id)
);

CREATE INDEX idx_hazard_events_pair ON hazard_events(pair_id);
CREATE INDEX idx_hazard_events_type ON hazard_events(hazard_type);
CREATE INDEX idx_hazard_events_critical ON hazard_events(is_critical);
CREATE INDEX idx_hazard_events_created ON hazard_events(created_at);


-- =============================================================================
-- VIEWS für einfacheren Zugriff
-- =============================================================================

-- Vollständiger Prompt mit Metriken
CREATE VIEW IF NOT EXISTS v_full_context AS
SELECT 
  pp.pair_id,
  pp.session_id,
  pp.turn_number,
  pp.user_text,
  pp.ai_text,
  pp.created_at,
  mf.user_m1_A,
  mf.ai_m1_A,
  mf.disharmony_score,
  bs.b_score,
  bs.b_alignment
FROM prompt_pairs pp
LEFT JOIN metrics_full mf ON pp.pair_id = mf.pair_id
LEFT JOIN b_state_evolution bs ON pp.pair_id = bs.pair_id
ORDER BY pp.created_at DESC;

-- Hazard Timeline
CREATE VIEW IF NOT EXISTS v_hazard_timeline AS
SELECT 
  he.created_at,
  he.hazard_type,
  he.severity,
  he.is_critical,
  pp.user_text,
  pp.session_id
FROM hazard_events he
JOIN prompt_pairs pp ON he.pair_id = pp.pair_id
ORDER BY he.created_at DESC;
