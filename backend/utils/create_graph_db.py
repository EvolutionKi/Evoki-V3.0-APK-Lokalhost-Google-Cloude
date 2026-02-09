"""
Create evoki_v3_graph.db - Graph Relationships
"""
import sqlite3
from pathlib import Path
from datetime import datetime


def create_graph_db():
    """Create graph database for prompt-pair relationships"""
    
    db_path = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_graph.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    
    print(f"Creating graph database: {db_path}")
    
    # 1. Graph Nodes (Prompt-pairs, chunks, keywords)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS graph_nodes (
            node_id TEXT PRIMARY KEY,
            pair_id TEXT,
            node_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    print("✅ Created graph_nodes")
    
    # 2. Graph Edges (Similarity connections)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS graph_edges (
            edge_id TEXT PRIMARY KEY,
            source_node_id TEXT NOT NULL,
            target_node_id TEXT NOT NULL,
            similarity_score REAL NOT NULL,
            edge_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (source_node_id) REFERENCES graph_nodes(node_id),
            FOREIGN KEY (target_node_id) REFERENCES graph_nodes(node_id)
        )
    """)
    print("✅ Created graph_edges")
    
    # 3. Graph Clusters (Thematic groupings)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS graph_clusters (
            cluster_id TEXT PRIMARY KEY,
            cluster_name TEXT,
            node_ids TEXT NOT NULL,
            centroid_vector BLOB,
            created_at TEXT NOT NULL
        )
    """)
    print("✅ Created graph_clusters")
    
    # Indices
    conn.execute("CREATE INDEX IF NOT EXISTS idx_node_type ON graph_nodes(node_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_node_pair ON graph_nodes(pair_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_edge_source ON graph_edges(source_node_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_edge_target ON graph_edges(target_node_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_edge_similarity ON graph_edges(similarity_score)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_edge_type ON graph_edges(edge_type)")
    print("✅ Created all indices")
    
    # Metadata
    conn.execute("CREATE TABLE IF NOT EXISTS _metadata (key TEXT PRIMARY KEY, value TEXT)")
    metadata = {
        "created_at": datetime.now().isoformat(),
        "version": "3.0",
        "purpose": "Graph Relationships between Prompt-Pairs",
        "schema_version": "1.0"
    }
    for key, value in metadata.items():
        conn.execute("INSERT OR REPLACE INTO _metadata (key, value) VALUES (?, ?)", (key, value))
    
    conn.commit()
    
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\n📊 Database created successfully!")
    print(f"   Tables: {len(tables)}")
    print(f"   Location: {db_path}")
    print(f"   Size: {db_path.stat().st_size / 1024:.1f} KB")
    
    conn.close()
    return db_path


if __name__ == "__main__":
    create_graph_db()
    print("\n✅ evoki_v3_graph.db ready!")
