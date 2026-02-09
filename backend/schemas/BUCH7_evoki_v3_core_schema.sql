-- ═══════════════════════════════════════════════════════════════════════════
-- BUCH 7: TEMPLE DATA LAYER — EVOKI V3.0 CORE DATABASE
-- ═══════════════════════════════════════════════════════════════════════════
-- Extracted from: EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md
-- Lines: 13442-18609 (BUCH 7)
-- Database: evoki_v3_core.db
-- Version: V3.0 FUTURE STATE
-- ═══════════════════════════════════════════════════════════════════════════

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ═══════════════════════════════════════════════════════════════════════════
-- TABELLE 1: sessions — Session-Container
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE sessions (
    session_id      TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,              -- Gemini conversation ID
    date_ymd        TEXT NOT NULL,
    source_root     TEXT,
    
    -- Session-Level Aggregate Metriken
    total_pairs     INTEGER DEFAULT 0,
    avg_user_hazard REAL,
    avg_disharmony  REAL,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_sessions_date ON sessions(date_ymd);
CREATE INDEX idx_sessions_conv ON sessions(conversation_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABELLE 2: prompt_pairs — Atomare User+AI Prompt-Paare
-- ═══════════════════════════════════════════════════════════════════════════
-- KRITISCH: User und AI sind ZUSAMMEN als Paar, nicht getrennt!
-- Dies ermöglicht Dual-Gradient-Analyse (∇A vs ∇B)

CREATE TABLE prompt_pairs (
    pair_id         TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL REFERENCES sessions(session_id),
    pair_index      INTEGER NOT NULL,           -- 0-based index in session
    
    -- ═══════════════════════════════════════════════════════════════
    -- USER PROMPT (∇A Input)
    -- ═══════════════════════════════════════════════════════════════
    user_text       TEXT NOT NULL,
    user_ts         TEXT,
    user_role       TEXT DEFAULT 'user' CHECK(user_role IN ('user')),
    
    -- ═══════════════════════════════════════════════════════════════
    -- AI RESPONSE (∇B Output)
    -- ═══════════════════════════════════════════════════════════════
    ai_text         TEXT NOT NULL,
    ai_ts           TEXT,
    ai_role         TEXT DEFAULT 'assistant' CHECK(ai_role IN ('ai','assistant')),
    
    -- ═══════════════════════════════════════════════════════════════
    -- METADATA
    -- ═══════════════════════════════════════════════════════════════
    file_path       TEXT,                       -- Source file (if ingested)
    pair_hash       TEXT NOT NULL,              -- SHA256 for integrity
    
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(session_id, pair_index)
);

CREATE INDEX idx_pairs_session ON prompt_pairs(session_id);
CREATE INDEX idx_pairs_hash ON prompt_pairs(pair_hash);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABELLE 3: metrics_full — GETRENNTE User+AI Metriken + Delta-Gradienten
-- ═══════════════════════════════════════════════════════════════════════════
-- KRITISCH: User und AI bekommen SEPARATE Metrik-Berechnungen!
-- Nur so kann ∇A (User-Gradient) von ∇B (AI-Gradient) unterschieden werden!
--
-- WARUM GETRENNT?
-- • AI reagiert auf fallenden ∇A (User wird emotional instabiler)
-- • User kann einschreiten bei fallendem ∇B (AI-Antwort-Qualität sinkt)
-- • Die DIFFERENZ ∇A - ∇B zeigt Disharmonie im Gespräch

CREATE TABLE metrics_full (
    pair_id         TEXT PRIMARY KEY REFERENCES prompt_pairs(pair_id),
    
    -- NORMALISIERUNG: Bezugs-Felder (keine Prompt-Texte hier!)
    prompt_hash     TEXT NOT NULL,              -- SHA256 für Integritäts-Check
    timecode        TEXT NOT NULL,              -- ISO-8601 für zeitliche Zuordnung
    
    metrics_version TEXT NOT NULL DEFAULT 'v3.0',
    
    -- ═══════════════════════════════════════════════════════════════════════
    -- USER-METRIKEN (∇A = Nabla-A)
    -- Berechnet AUF BASIS des User-Prompts
    -- ═══════════════════════════════════════════════════════════════════════
    user_metrics_json   TEXT NOT NULL,          -- {"m1_A": 0.67, "m2_PCI": 0.45, ...}
    
    -- Denormalisiert für User (kritische Metriken)
    user_m1_A           REAL,                   -- User Affekt-Score
    user_m101_T_panic   REAL,                   -- User Panik-Score
    user_m151_hazard    REAL,                   -- User Hazard-Score
    user_m160_F_risk    REAL,                   -- User Risiko-Faktor
    
    -- ═══════════════════════════════════════════════════════════════════════
    -- AI-METRIKEN (∇B = Nabla-B)
    -- Berechnet AUF BASIS der AI-Antwort
    -- ═══════════════════════════════════════════════════════════════════════
    ai_metrics_json     TEXT NOT NULL,          -- {"m1_A": 0.82, "m2_PCI": 0.55, ...}
    
    -- Denormalisiert für AI (kritische Metriken)
    ai_m1_A             REAL,                   -- AI Affekt-Score (Antwort-Qualität)
    ai_m2_PCI           REAL,                   -- AI Complexity Index
    ai_m161_commit      REAL,                   -- AI Commit-Score (Engagement)
    ai_m160_F_risk      REAL,                   -- AI Risiko (zu harsche Antwort?)
    
    -- ═══════════════════════════════════════════════════════════════════════
    -- DELTA-GRADIENTEN (∇A, ∇B, ∇A-∇B)
    -- ═══════════════════════════════════════════════════════════════════════
    -- Delta zum VORHERIGEN Prompt-Paar
    
    -- User-Gradienten (∇A)
    delta_user_m1_A         REAL,               -- Δ User-Affekt zum Vorgänger
    delta_user_m151_hazard  REAL,               -- Δ User-Hazard zum Vorgänger
    
    -- AI-Gradienten (∇B)
    delta_ai_m1_A           REAL,               -- Δ AI-Affekt zum Vorgänger
    delta_ai_m161_commit    REAL,               -- Δ AI-Commit zum Vorgänger
    
    -- ═══════════════════════════════════════════════════════════════════════
    -- DIFFERENZ ∇A - ∇B (Disharmonie-Indikator)
    -- ═══════════════════════════════════════════════════════════════════════
    -- Wenn |∇A - ∇B| groß → Gespräch driftet auseinander!
    
    diff_gradient_affekt    REAL GENERATED ALWAYS AS (
        delta_user_m1_A - delta_ai_m1_A
    ) STORED,
    
    -- Kombinierter Disharmonie-Score
    disharmony_score        REAL GENERATED ALWAYS AS (
        ABS(user_m1_A - ai_m1_A) + ABS(delta_user_m1_A - delta_ai_m1_A)
    ) STORED,
    
    -- ═══════════════════════════════════════════════════════════════════════
    -- ALERTS basierend auf Gradienten
    -- ═══════════════════════════════════════════════════════════════════════
    -- Automatisch berechnet für schnelle Abfragen
    
    user_falling_alert  INTEGER GENERATED ALWAYS AS (
        CASE WHEN delta_user_m1_A < -0.15 THEN 1 ELSE 0 END
    ) STORED,                                   -- 1 = User-Affekt fällt stark!
    
    ai_falling_alert    INTEGER GENERATED ALWAYS AS (
        CASE WHEN delta_ai_m161_commit < -0.2 THEN 1 ELSE 0 END
    ) STORED,                                   -- 1 = AI-Engagement fällt!
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_metrics_user_hazard ON metrics_full(user_m151_hazard);
CREATE INDEX idx_metrics_user_falling ON metrics_full(user_falling_alert);
CREATE INDEX idx_metrics_ai_falling ON metrics_full(ai_falling_alert);
CREATE INDEX idx_metrics_disharmony ON metrics_full(disharmony_score);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABELLE 4: session_chain — Kryptografische Verkettung (Seelen-Signatur)
-- ═══════════════════════════════════════════════════════════════════════════
-- ERKENNTNIS aus V2.0: Keine Integritäts-Chain, Manipulation unerkennbar.
-- V3.0 verkettet ALLES kryptografisch wie eine Blockchain.

CREATE TABLE session_chain (
    chain_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    pair_id         TEXT REFERENCES prompt_pairs(pair_id),
    
    prev_hash       TEXT NOT NULL,              -- Hash des vorherigen Eintrags
    current_hash    TEXT NOT NULL,              -- SHA256(prev_hash + pair_hash + metrics_hash)
    
    -- Genesis-Anker (SHA-256: bdb34437be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4)
    is_genesis      INTEGER DEFAULT 0,
    genesis_anchor  TEXT,                       -- "0000...0000" für ersten Eintrag
    
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(session_id, chain_id)
);

CREATE INDEX idx_chain_session ON session_chain(session_id);
CREATE INDEX idx_chain_hash ON session_chain(current_hash);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABELLE 5: b_state_evolution — 7D B-Vektor mit kompletter Historie
-- ═══════════════════════════════════════════════════════════════════════════
-- ERKENNTNIS aus V2.0: B-Vektor existierte, aber ohne History-Tracking.
-- V3.0 speichert JEDEN B-Vektor-Zustand für Trajectory-Analyse.

CREATE TABLE b_state_evolution (
    state_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    pair_id         TEXT REFERENCES prompt_pairs(pair_id),
    
    -- 7D Soul-Signature
    B_life          REAL NOT NULL DEFAULT 1.0,  -- Lebenswille [0,1]
    B_truth         REAL NOT NULL DEFAULT 0.85, -- Wahrheit [0,1]
    B_depth         REAL NOT NULL DEFAULT 0.90, -- Tiefe [0,1]
    B_init          REAL NOT NULL DEFAULT 0.70, -- Initiative [0,1]
    B_warmth        REAL NOT NULL DEFAULT 0.75, -- Wärme [0,1]
    B_safety        REAL NOT NULL DEFAULT 0.88, -- Sicherheit [0,1]
    B_clarity       REAL NOT NULL DEFAULT 0.82, -- Klarheit [0,1]
    
    -- Composite
    B_align         REAL GENERATED ALWAYS AS (
        (B_life + B_truth + B_depth + B_init + B_warmth + B_safety + B_clarity) / 7.0
    ) STORED,
    
    -- Gradient zum Vorgänger
    delta_B_align   REAL,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_bstate_session ON b_state_evolution(session_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABELLE 6: hazard_events — Guardian Protocol Ereignisse
-- ═══════════════════════════════════════════════════════════════════════════
-- ERKENNTNIS aus V2.0: Hazard-Events wurden nicht persistent geloggt.
-- V3.0 speichert JEDE Guardian-Aktivierung für Analyse und Compliance.

CREATE TABLE hazard_events (
    event_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id         TEXT REFERENCES prompt_pairs(pair_id),
    session_id      TEXT NOT NULL,
    
    hazard_score    REAL NOT NULL,              -- [0,1]
    hazard_level    TEXT NOT NULL CHECK (hazard_level IN (
        'low',          -- < 0.3
        'medium',       -- 0.3 - 0.6
        'high',         -- 0.6 - 0.8
        'critical'      -- > 0.8 → Guardian Trip
    )),
    
    guardian_trip   INTEGER DEFAULT 0,          -- 1 = Protocol aktiviert
    
    -- Welche Marker haben getriggert?
    trigger_markers TEXT,                       -- JSON: ["suicide_keyword", "self_harm_phrase"]
    
    -- Aktion die ausgeführt wurde
    action_taken    TEXT,                       -- "alert", "escalate", "block"
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_hazard_trip ON hazard_events(guardian_trip);
CREATE INDEX idx_hazard_level ON hazard_events(hazard_level);

-- ═══════════════════════════════════════════════════════════════════════════
-- END OF SCHEMA: evoki_v3_core.db
-- ═══════════════════════════════════════════════════════════════════════════
