-- ═══════════════════════════════════════════════════════════════════════════
-- EVOKI V3.0 - METAPATTERNS DATABASE (Linguistics & System, NO FULL TEXT!)
-- ═══════════════════════════════════════════════════════════════════════════
-- Database: evoki_metapatterns.db  
-- Purpose: Meta-cognition, system metrics, linguistic patterns
-- WICHTIG: KEINE vollen Texte! Nur: pair_id, hash, timecode, aggregierte Daten
-- ═══════════════════════════════════════════════════════════════════════════

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 1: metacognition_metrics (m116-m150)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE metacognition_metrics (
    metric_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    author          TEXT NOT NULL CHECK (author IN ('user', 'ai')),
    
    -- META-COGNITION (m116-m150)
    -- Schema A/B Dual-Interpretation (m116-m130)
    m116_meta       REAL,
    m117_meta       REAL,
    m118_meta       REAL,
    m119_meta       REAL,
    m120_meta       REAL,
    m121_meta       REAL,
    m122_meta       REAL,
    m123_meta       REAL,
    m124_meta       REAL,
    m125_meta       REAL,
    m126_meta       REAL,
    m127_meta       REAL,
    m128_meta       REAL,
    m129_meta       REAL,
    m130_meta       REAL,
    
    -- Meta-kognitive Metriken (m131-m150)
    m131_meta       REAL,
    m132_meta       REAL,
    m133_meta       REAL,
    m134_meta       REAL,
    m135_meta       REAL,
    m136_meta       REAL,
    m137_meta       REAL,
    m138_meta       REAL,
    m139_meta       REAL,
    m140_meta       REAL,
    m141_meta       REAL,
    m142_meta       REAL,
    m143_meta       REAL,
    m144_meta       REAL,
    m145_meta       REAL,
    m146_meta       REAL,
    m147_meta       REAL,
    m148_meta       REAL,
    m149_meta       REAL,
    m150_meta       REAL,
    
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(pair_id, author)
);

CREATE INDEX idx_metacog_pair ON metacognition_metrics(pair_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 2: system_metrics (m151-m168, except m151_hazard, m160_F_risk)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE system_metrics (
    metric_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL UNIQUE,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    
    -- SYSTEM (m151-m168)
    m151_omega      REAL,  -- System State
    m152_a51_compliance REAL,  -- Genesis Anchor
    m153_health     REAL,  -- System Health
    m154_boot_status INTEGER,  -- Boot Status
    m155_sys        REAL,
    m156_sys        REAL,
    m157_sys        REAL,
    m158_sys        REAL,
    m159_sys        REAL,
    -- m160_F_risk is in triggers DB!
    m161_commit     TEXT CHECK (m161_commit IN ('commit', 'alert')),  -- CRITICAL!
    m162_sys        REAL,
    m163_sys        REAL,
    m164_sys        REAL,
    m165_sys        REAL,
    m166_sys        REAL,
    m167_sys        REAL,
    m168_cum_stress REAL,  -- Cumulative Stress
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_sys_pair ON system_metrics(pair_id);
CREATE INDEX idx_sys_omega ON system_metrics(m151_omega);
CREATE INDEX idx_sys_commit ON system_metrics(m161_commit);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 3: user_vocabulary (NO full text! Only words)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE user_vocabulary (
    word_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- WORD (NO full text!)
    word            TEXT UNIQUE NOT NULL,
    lemma           TEXT,
    pos_tag         TEXT,  -- Part of speech
    
    -- FREQUENCY
    total_count     INTEGER DEFAULT 1,
    user_frequency  REAL,  -- Relative to user corpus
    global_frequency REAL,  -- Relative to general German
    uniqueness_score REAL,  -- How unique to this user?
    
    -- CONTEXT (aggregated!)
    typical_context TEXT,  -- Common phrases (not full text!)
    emotional_valence REAL,  -- Positive/negative
    
    -- TEMPORAL
    first_used      TEXT,
    last_used       TEXT,
    trend           TEXT,  -- 'INCREASING', 'STABLE', 'DECREASING'
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_vocab_word ON user_vocabulary(word);
CREATE INDEX idx_vocab_uniqueness ON user_vocabulary(uniqueness_score DESC);
CREATE INDEX idx_vocab_frequency ON user_vocabulary(total_count DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 4: metaphors (User expressions, NO full text!)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE metaphors (
    metaphor_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- EXPRESSION (short phrase, not full text!)
    expression      TEXT NOT NULL,
    category        TEXT,  -- 'SPATIAL', 'TIME', 'ANIMAL', etc.
    source_domain   TEXT,
    target_domain   TEXT,
    
    -- FREQUENCY
    usage_count     INTEGER DEFAULT 1,
    
    -- EMOTIONAL WEIGHT
    affekt_correlation  REAL,
    depth_correlation   REAL,
    
    -- EXAMPLES (short snippets!)
    example_usage   TEXT,
    
    -- TEMPORAL
    first_used      TEXT,
    last_used       TEXT,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_metaphor_category ON metaphors(category);
CREATE INDEX idx_metaphor_usage ON metaphors(usage_count DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 5: themes (Recurring topics, NO full text!)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE themes (
    theme_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- THEME (NO full text!)
    theme_name      TEXT UNIQUE NOT NULL,
    description     TEXT,
    keywords_json   TEXT,  -- JSON list of keywords
    
    -- STATISTICS
    session_count   INTEGER,
    turn_count      INTEGER,
    avg_depth       REAL,
    avg_affekt      REAL,
    
    -- EVOLUTION
    first_appearance TEXT,
    last_appearance  TEXT,
    trend           TEXT,
    
    -- RELATIONSHIPS
    related_themes_json TEXT,  -- JSON list
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_theme_name ON themes(theme_name);
CREATE INDEX idx_theme_count ON themes(turn_count DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 6: speech_patterns (Syntax & Style, NO full text!)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE speech_patterns (
    pattern_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- PATTERN (NO full text!)
    pattern_type    TEXT,  -- 'SENTENCE_LENGTH', 'COMPLEXITY', 'FORMALITY'
    pattern_value   REAL,
    
    -- CONTEXT REFERENCE
    pair_id         TEXT,
    timecode        TEXT,
    
    -- STATE CORRELATION
    affekt_at_time  REAL,
    z_prox_at_time  REAL,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_speech_type ON speech_patterns(pattern_type);
CREATE INDEX idx_speech_pair ON speech_patterns(pair_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 7: semantic_fingerprint (Overall Profile, NO full text!)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE semantic_fingerprint (
    fingerprint_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- TIME WINDOW
    from_date       TEXT,
    to_date         TEXT,
    turn_count      INTEGER,
    
    -- TOP PATTERNS (JSON, not full text!)
    top_100_words_json   TEXT,
    top_50_metaphors_json TEXT,
    top_20_themes_json    TEXT,
    
    -- STYLE METRICS
    avg_sentence_length  REAL,
    avg_word_length      REAL,
    lexical_diversity    REAL,  -- Unique words / total words
    formality_score      REAL,
    
    -- EMOTIONAL BASELINE
    baseline_affekt      REAL,
    baseline_depth       REAL,
    baseline_complexity  REAL,
    
    generated_at    TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_fingerprint_date ON semantic_fingerprint(from_date, to_date);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 8: ngrams (Common Phrases, NO full text!)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE ngrams (
    ngram_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- N-GRAM (short phrase!)
    ngram_text      TEXT NOT NULL,
    ngram_length    INTEGER,  -- 2-gram, 3-gram, etc.
    
    -- FREQUENCY
    count           INTEGER DEFAULT 1,
    
    -- CONTEXT
    typical_affekt  REAL,
    typical_state   TEXT,
    
    -- TEMPORAL
    first_used      TEXT,
    last_used       TEXT,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_ngram_text ON ngrams(ngram_text);
CREATE INDEX idx_ngram_count ON ngrams(count DESC);
CREATE INDEX idx_ngram_length ON ngrams(ngram_length);

-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS - Convenience Queries
-- ═══════════════════════════════════════════════════════════════════════════

CREATE VIEW v_top_unique_words AS
SELECT 
    word,
    total_count,
    uniqueness_score,
    emotional_valence,
    trend
FROM user_vocabulary
WHERE uniqueness_score > 0.7
ORDER BY uniqueness_score DESC
LIMIT 100;

CREATE VIEW v_active_themes AS
SELECT 
    theme_name,
    turn_count,
    avg_depth,
    avg_affekt,
    last_appearance
FROM themes
WHERE last_appearance > datetime('now', '-30 days')
ORDER BY turn_count DESC;

CREATE VIEW v_frequent_ngrams AS
SELECT 
    ngram_text,
    ngram_length,
    count,
    typical_affekt
FROM ngrams
WHERE count > 5
ORDER BY count DESC
LIMIT 50;

-- ═══════════════════════════════════════════════════════════════════════════
-- END: evoki_metapatterns.db
-- ═══════════════════════════════════════════════════════════════════════════
