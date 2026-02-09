-- EVOKI V3.0 ANALYTICS DATABASE SCHEMA
-- B-Vector Verification & API Logging

CREATE TABLE IF NOT EXISTS b_vector_verifications (
    verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id TEXT NOT NULL,
    B_safety REAL,
    B_life REAL,
    B_align REAL,
    verification_method TEXT,
    verified_at TEXT,
    constraints_passed INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS lexika_verification_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id TEXT NOT NULL,
    lexikon_name TEXT,
    matched_count INTEGER,
    total_weight REAL,
    verified_at TEXT
);

CREATE TABLE IF NOT EXISTS dual_response_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id TEXT NOT NULL,
    user_response TEXT,
    ai_response TEXT,
    divergence_score REAL,
    logged_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_b_verif_pair ON b_vector_verifications(pair_id);
CREATE INDEX IF NOT EXISTS idx_lexika_pair ON lexika_verification_log(pair_id);
