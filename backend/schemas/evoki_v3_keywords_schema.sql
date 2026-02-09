-- EVOKI V3.0 KEYWORDS DATABASE SCHEMA
-- Learning Keyword Engine

CREATE TABLE IF NOT EXISTS keyword_registry (
    keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT UNIQUE NOT NULL,
    frequency INTEGER DEFAULT 1,
    last_seen TEXT,
    first_seen TEXT,
    category TEXT,
    weight REAL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS keyword_associations (
    assoc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_a TEXT NOT NULL,
    keyword_b TEXT NOT NULL,
    cooccurrence_count INTEGER DEFAULT 1,
    association_strength REAL
);

CREATE TABLE IF NOT EXISTS keyword_clusters (
    cluster_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_name TEXT,
    keywords_json TEXT,
    created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keyword_registry(keyword);
CREATE INDEX IF NOT EXISTS idx_keywords_frequency ON keyword_registry(frequency DESC);
