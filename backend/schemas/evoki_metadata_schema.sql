-- ═══════════════════════════════════════════════════════════════════════════
-- EVOKI V3.0 - METADATA DATABASE (Text Storage)
-- ═══════════════════════════════════════════════════════════════════════════
-- Database: evoki_metadata.db
-- Purpose: Session structure, prompt text, integrity chain
-- WICHTIG: NUR diese DB enthält TEXTE!
-- ═══════════════════════════════════════════════════════════════════════════

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 1: sessions
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE sessions (
    session_id      TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    date_ymd        TEXT NOT NULL,
    total_pairs     INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_sessions_conv ON sessions(conversation_id);
CREATE INDEX idx_sessions_date ON sessions(date_ymd);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 2: prompt_pairs (EINZIGE Tabelle mit VOLLEM TEXT!)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE prompt_pairs (
    pair_id         TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL REFERENCES sessions(session_id),
    pair_index      INTEGER NOT NULL,
    
    -- USER PROMPT (TEXT!)
    user_text       TEXT NOT NULL,
    user_ts         TEXT NOT NULL,
    
    -- AI RESPONSE (TEXT!)
    ai_text         TEXT NOT NULL,
    ai_ts           TEXT NOT NULL,
    
    -- METADATA (für Referenz in anderen DBs)
    pair_hash       TEXT NOT NULL,
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(session_id, pair_index)
);

CREATE INDEX idx_pairs_session ON prompt_pairs(session_id);
CREATE INDEX idx_pairs_hash ON prompt_pairs(pair_hash);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 3: session_chain (Integrity)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE session_chain (
    chain_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    pair_id         TEXT REFERENCES prompt_pairs(pair_id),
    
    prev_hash       TEXT NOT NULL,
    current_hash    TEXT NOT NULL,
    is_genesis      INTEGER DEFAULT 0,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_chain_session ON session_chain(session_id);
CREATE INDEX idx_chain_pair ON session_chain(pair_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- VIEW: Quick References (for other DBs)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE VIEW v_pair_references AS
SELECT 
    pair_id,
    session_id,
    pair_index,
    pair_hash,
    user_ts as timecode,
    'user' as author_user,
    'ai' as author_ai,
    created_at
FROM prompt_pairs;

-- ═══════════════════════════════════════════════════════════════════════════
-- END: evoki_metadata.db
-- ═══════════════════════════════════════════════════════════════════════════
