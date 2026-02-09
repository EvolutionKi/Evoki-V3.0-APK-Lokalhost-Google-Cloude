-- evoki_v3_graph_schema.sql
-- Graph Database for Semantic Similarity Network

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- =============================================================================
-- 1. GRAPH_NODES — Prompt-Pair als Graph-Knoten
-- =============================================================================

CREATE TABLE IF NOT EXISTS graph_nodes (
  node_id TEXT PRIMARY KEY,          -- Same as pair_id from core.db
  session_id TEXT NOT NULL,
  
  -- Node Properties
  created_at TEXT NOT NULL,
  node_type TEXT DEFAULT 'prompt',   -- 'prompt', 'cluster', 'theme'
  
  -- Metrics Snapshot (für Graph-Algorithmen)
  a_score REAL,
  pci REAL,
  depth REAL,
  
  -- Cluster Assignment
  cluster_id TEXT,
  
  -- Metadata
  tags TEXT,
  importance_score REAL DEFAULT 0.5
);

CREATE INDEX idx_graph_nodes_session ON graph_nodes(session_id);
CREATE INDEX idx_graph_nodes_cluster ON graph_nodes(cluster_id);
CREATE INDEX idx_graph_nodes_created ON graph_nodes(created_at);


-- =============================================================================
-- 2. GRAPH_EDGES — Similarity-Kanten
-- =============================================================================

CREATE TABLE IF NOT EXISTS graph_edges (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  
  -- Edge Endpoints
  source_node_id TEXT NOT NULL,
  target_node_id TEXT NOT NULL,
  
  -- Similarity Scores
  semantic_similarity REAL NOT NULL,  -- [0, 1] von FAISS semantic_wpf
  metrics_similarity REAL NOT NULL,   -- [0, 1] von FAISS metrics_wpf
  combined_similarity REAL NOT NULL,  -- Weighted combination
  
  -- Edge Type
  edge_type TEXT DEFAULT 'semantic',  -- 'semantic', 'metrics', 'temporal', 'causal'
  
  -- Weights
  weight REAL DEFAULT 1.0,
  
  created_at TEXT NOT NULL,
  
  FOREIGN KEY(source_node_id) REFERENCES graph_nodes(node_id),
  FOREIGN KEY(target_node_id) REFERENCES graph_nodes(node_id),
  
  UNIQUE(source_node_id, target_node_id)
);

CREATE INDEX idx_graph_edges_source ON graph_edges(source_node_id);
CREATE INDEX idx_graph_edges_target ON graph_edges(target_node_id);
CREATE INDEX idx_graph_edges_similarity ON graph_edges(combined_similarity);


-- =============================================================================
-- 3. GRAPH_CLUSTERS — Themen-Gruppierung
-- =============================================================================

CREATE TABLE IF NOT EXISTS graph_clusters (
  cluster_id TEXT PRIMARY KEY,
  
  -- Cluster Properties
  cluster_name TEXT,
  cluster_type TEXT DEFAULT 'semantic', -- 'semantic', 'temporal', 'emotional'
  
  -- Centroid
  centroid_node_id TEXT,              -- Repräsentativer Knoten
  
  -- Statistics
  node_count INTEGER DEFAULT 0,
  avg_a_score REAL,
  avg_pci REAL,
  avg_depth REAL,
  
  -- Coherence
  intra_cluster_coherence REAL,       -- [0, 1] Wie ähnlich sind Knoten innerhalb?
  inter_cluster_separation REAL,      -- [0, 1] Wie unterschiedlich zu anderen Clustern?
  
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  
  FOREIGN KEY(centroid_node_id) REFERENCES graph_nodes(node_id)
);

CREATE INDEX idx_graph_clusters_type ON graph_clusters(cluster_type);
CREATE INDEX idx_graph_clusters_coherence ON graph_clusters(intra_cluster_coherence);


-- =============================================================================
-- 4. CLUSTER_KEYWORDS — Automatisch extrahierte Cluster-Keywords
-- =============================================================================

CREATE TABLE IF NOT EXISTS cluster_keywords (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cluster_id TEXT NOT NULL,
  
  keyword TEXT NOT NULL,
  frequency INTEGER NOT NULL,         -- Wie oft im Cluster?
  tfidf_score REAL,                   -- TF-IDF Score
  
  FOREIGN KEY(cluster_id) REFERENCES graph_clusters(cluster_id),
  UNIQUE(cluster_id, keyword)
);

CREATE INDEX idx_cluster_keywords_cluster ON cluster_keywords(cluster_id);
CREATE INDEX idx_cluster_keywords_keyword ON cluster_keywords(keyword);


-- =============================================================================
-- VIEWS
-- =============================================================================

-- Cluster Overview
CREATE VIEW IF NOT EXISTS v_cluster_overview AS
SELECT 
  c.cluster_id,
  c.cluster_name,
  c.node_count,
  c.avg_a_score,
  c.intra_cluster_coherence,
  GROUP_CONCAT(ck.keyword, ', ') AS top_keywords
FROM graph_clusters c
LEFT JOIN cluster_keywords ck ON c.cluster_id = ck.cluster_id
GROUP BY c.cluster_id
ORDER BY c.node_count DESC;

-- Node Connections
CREATE VIEW IF NOT EXISTS v_node_connections AS
SELECT 
  n.node_id,
  n.session_id,
  COUNT(e.id) AS connection_count,
  AVG(e.combined_similarity) AS avg_similarity
FROM graph_nodes n
LEFT JOIN graph_edges e ON n.node_id = e.source_node_id OR n.node_id = e.target_node_id
GROUP BY n.node_id;
