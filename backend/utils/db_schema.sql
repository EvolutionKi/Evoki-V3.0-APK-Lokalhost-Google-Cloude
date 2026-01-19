-- Master Timeline DB Schema
-- Speichert ALLE Chunks mit 153 Metriken

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id TEXT UNIQUE NOT NULL,
    session_id TEXT,
    timestamp TEXT,
    source TEXT CHECK(source IN ('tempel', 'trialog')),
    text TEXT NOT NULL,
    
    -- Core Metriken
    A REAL,              -- Affekt (0.0-1.0)
    PCI REAL,            -- Prozess-Kohärenz-Index
    coh REAL,            -- Kohärenz
    
    -- Trauma Metriken
    T_panic REAL,        -- Panik-Level
    T_disso REAL,        -- Dissoziation
    T_trigger REAL,      -- Trigger-Wahrscheinlichkeit
    
    -- B-Vektor (7D Soul-Signature)
    B_life REAL,         -- Lebenswille
    B_truth REAL,        -- Wahrheit
    B_depth REAL,        -- Tiefe
    B_init REAL,         -- Initiative
    B_warmth REAL,       -- Wärme
    B_safety REAL,       -- Sicherheit
    B_clarity REAL,      -- Klarheit
    
    -- Composite Scores
    B_align REAL,        -- Durchschnitt B-Vektor
    F_risk REAL,         -- Gefährdungs-Score
    risk_z REAL,         -- Z-Score Risiko
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_timestamp ON chunks(timestamp);
CREATE INDEX IF NOT EXISTS idx_source ON chunks(source);
CREATE INDEX IF NOT EXISTS idx_B_align ON chunks(B_align);
CREATE INDEX IF NOT EXISTS idx_F_risk ON chunks(F_risk);
CREATE INDEX IF NOT EXISTS idx_session ON chunks(session_id);
