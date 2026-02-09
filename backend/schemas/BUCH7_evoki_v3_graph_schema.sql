-- ═══════════════════════════════════════════════════════════════════════════
-- BUCH 7: TEMPLE DATA LAYER — EVOKI V3.0 GRAPH DATABASE
-- ═══════════════════════════════════════════════════════════════════════════
-- Extracted from: EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md
-- Lines: ~14306-14800 (BUCH 7, Section 2.4)
-- Database: evoki_v3_graph.db
-- Version: V3.0 FUTURE STATE
-- ═══════════════════════════════════════════════════════════════════════════
-- ERKENNTNIS aus V2.0: wormhole_graph war statisch und chunk-basiert.
-- V3.0 Graph ist dynamisch, prompt-paar-basiert, und metrik-gewichtet.
-- ═══════════════════════════════════════════════════════════════════════════

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ═══════════════════════════════════════════════════════════════════════════
-- TABELLE 1: graph_nodes — Prompt-Paar-Knoten
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE graph_nodes (
    node_id         TEXT PRIMARY KEY,           -- = pair_id aus evoki_v3_core.db
    session_id      TEXT NOT NULL,
    
    -- Embedding für Similarity-Berechnung (384D als BLOB)
    embedding       BLOB NOT NULL,
    
    -- Node-Eigenschaften (denormalisiert für schnelle Graph-Traversierung)
    -- WICHTIG: Getrennte User/AI Metriken (konsistent mit metrics_full)
    user_m1_A       REAL,                       -- User Affekt-Score
    user_m151_hazard REAL,                      -- User Hazard-Score
    ai_m1_A         REAL,                       -- AI Antwort-Qualität
    ai_m161_commit  REAL,                       -- AI Engagement
    
    -- Kombiniert für Graph-Traversierung
    disharmony_score REAL,                      -- |User - AI| Disharmonie
    
    -- Cluster-Zugehörigkeit (automatisch berechnet)
    cluster_id      TEXT,
    cluster_label   TEXT,                       -- z.B. "Trauma", "Freude", "Reflexion"
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_nodes_cluster ON graph_nodes(cluster_id);
CREATE INDEX idx_nodes_session ON graph_nodes(session_id);
CREATE INDEX idx_nodes_disharmony ON graph_nodes(disharmony_score DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABELLE 2: graph_edges — Similarity-Kanten mit Metrik-Gewichtung
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE graph_edges (
    edge_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source_node     TEXT NOT NULL REFERENCES graph_nodes(node_id),
    target_node     TEXT NOT NULL REFERENCES graph_nodes(node_id),
    
    -- Similarity Scores
    semantic_similarity REAL NOT NULL,          -- Cosine Similarity [0,1]
    metric_similarity   REAL NOT NULL,          -- Metrik-Vektor Similarity [0,1]
    
    -- Gewichtete Kombination (für Suche)
    combined_weight     REAL GENERATED ALWAYS AS (
        0.6 * semantic_similarity + 0.4 * metric_similarity
    ) STORED,
    
    -- Edge-Typ
    edge_type       TEXT DEFAULT 'similarity' CHECK (edge_type IN (
        'similarity',   -- Semantisch ähnlich
        'causal',       -- Direkte Kausalität (Vorgänger/Nachfolger)
        'thematic',     -- Gleiches Thema/Cluster
        'temporal'      -- Zeitlich nah
    )),
    
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(source_node, target_node)
);

CREATE INDEX idx_edges_weight ON graph_edges(combined_weight DESC);
CREATE INDEX idx_edges_type ON graph_edges(edge_type);
CREATE INDEX idx_edges_source ON graph_edges(source_node);
CREATE INDEX idx_edges_target ON graph_edges(target_node);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABELLE 3: graph_clusters — Automatische Themen-Gruppierung
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE graph_clusters (
    cluster_id      TEXT PRIMARY KEY,
    
    -- Cluster-Eigenschaften
    label           TEXT NOT NULL,              -- "Trauma", "Freude", etc.
    description     TEXT,
    
    -- Zentroid (durchschnittlicher Vektor des Clusters)
    centroid        BLOB,                       -- 384D average vector
    
    -- Cluster-Statistiken (User/AI getrennt)
    node_count          INTEGER DEFAULT 0,
    avg_user_m1_A       REAL,
    avg_user_m151_hazard REAL,
    avg_ai_m1_A         REAL,
    avg_disharmony      REAL,
    
    -- Temporal
    first_occurrence    TEXT,
    last_occurrence     TEXT,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_clusters_label ON graph_clusters(label);
CREATE INDEX idx_clusters_hazard ON graph_clusters(avg_user_m151_hazard DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABELLE 4: graph_paths — Vorberechnete Pfade (Performance)
-- ═══════════════════════════════════════════════════════════════════════════
-- Speichert häufig genutzte Pfade für schnellere Navigation

CREATE TABLE graph_paths (
    path_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    start_node      TEXT NOT NULL REFERENCES graph_nodes(node_id),
    end_node        TEXT NOT NULL REFERENCES graph_nodes(node_id),
    
    -- Pfad als JSON Array von node_ids
    path_nodes      TEXT NOT NULL,              -- ["node1", "node2", ..., "nodeN"]
    
    -- Pfad-Metriken
    path_length     INTEGER NOT NULL,           -- Anzahl Hops
    total_weight    REAL NOT NULL,              -- Summe aller Edge-Weights
    avg_weight      REAL GENERATED ALWAYS AS (
        total_weight / NULLIF(path_length, 0)
    ) STORED,
    
    -- Pfad-Typ
    path_type       TEXT,                       -- "semantic", "temporal", "causal"
    
    -- Usage tracking (für Cache-Management)
    access_count    INTEGER DEFAULT 0,
    last_accessed   TEXT,
    
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(start_node, end_node, path_type)
);

CREATE INDEX idx_paths_start ON graph_paths(start_node);
CREATE INDEX idx_paths_end ON graph_paths(end_node);
CREATE INDEX idx_paths_weight ON graph_paths(avg_weight DESC);
CREATE INDEX idx_paths_access ON graph_paths(access_count DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS — Convenience Queries
-- ═══════════════════════════════════════════════════════════════════════════

-- V1: Cluster Summary
CREATE VIEW IF NOT EXISTS v_cluster_summary AS
SELECT 
    c.cluster_id,
    c.label,
    c.node_count,
    c.avg_user_m1_A,
    c.avg_user_m151_hazard,
    c.avg_disharmony,
    COUNT(DISTINCT e.edge_id) as edge_count,
    AVG(e.combined_weight) as avg_edge_weight
FROM graph_clusters c
LEFT JOIN graph_nodes n ON n.cluster_id = c.cluster_id
LEFT JOIN graph_edges e ON e.source_node = n.node_id OR e.target_node = n.node_id
GROUP BY c.cluster_id;

-- V2: High-Risk Nodes (for Guardian)
CREATE VIEW IF NOT EXISTS v_high_risk_nodes AS
SELECT 
    n.node_id,
    n.session_id,
    n.user_m151_hazard,
    n.disharmony_score,
    n.cluster_label,
    COUNT(e.edge_id) as connection_count
FROM graph_nodes n
LEFT JOIN graph_edges e ON e.source_node = n.node_id
WHERE n.user_m151_hazard > 0.5 OR n.disharmony_score > 0.7
GROUP BY n.node_id
ORDER BY n.user_m151_hazard DESC;

-- V3: Most Connected Nodes (Hubs)
CREATE VIEW IF NOT EXISTS v_hub_nodes AS
SELECT 
    n.node_id,
    n.cluster_label,
    COUNT(DISTINCT e.edge_id) as degree,
    AVG(e.combined_weight) as avg_edge_weight,
    n.user_m1_A,
    n.ai_m1_A
FROM graph_nodes n
JOIN graph_edges e ON e.source_node = n.node_id OR e.target_node = n.node_id
GROUP BY n.node_id
HAVING degree > 5
ORDER BY degree DESC;

-- ═══════════════════════════════════════════════════════════════════════════
-- END OF SCHEMA: evoki_v3_graph.db
-- ═══════════════════════════════════════════════════════════════════════════
