"""
Create evoki_v3_keywords.db - Learning Keyword System
"""
import sqlite3
from pathlib import Path
from datetime import datetime


def create_keywords_db():
    """Create keywords database with learning capabilities"""
    
    db_path = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_keywords.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    
    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    
    print(f"Creating keywords database: {db_path}")
    
    # 1. Keyword Registry (Master list of all keywords)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS keyword_registry (
            keyword_id TEXT PRIMARY KEY,
            keyword TEXT UNIQUE NOT NULL,
            frequency INTEGER DEFAULT 1,
            vector_384d BLOB,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL
        )
    """)
    print("✅ Created keyword_registry")
    
    # 2. Keyword-Pair Links (Which keywords appear in which prompts)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS keyword_pair_links (
            link_id TEXT PRIMARY KEY,
            keyword_id TEXT NOT NULL,
            pair_id TEXT NOT NULL,
            context_window TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (keyword_id) REFERENCES keyword_registry(keyword_id)
        )
    """)
    print("✅ Created keyword_pair_links")
    
    # 3. Keyword Associations (Co-occurrence learning)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS keyword_associations (
            assoc_id TEXT PRIMARY KEY,
            keyword_a TEXT NOT NULL,
            keyword_b TEXT NOT NULL,
            co_occurrence_count INTEGER DEFAULT 1,
            pmi_score REAL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            UNIQUE(keyword_a, keyword_b)
        )
    """)
    print("✅ Created keyword_associations")
    
    # 4. Keyword Clusters (Synonym groups, themes)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS keyword_clusters (
            cluster_id TEXT PRIMARY KEY,
            keywords TEXT NOT NULL,
            cluster_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    print("✅ Created keyword_clusters")
    
    # 5. Live Session Index (Current session keywords - instantly searchable!)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS live_session_index (
            session_id TEXT NOT NULL,
            pair_id TEXT NOT NULL,
            keywords TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            PRIMARY KEY (session_id, pair_id)
        )
    """)
    print("✅ Created live_session_index")
    
    # Create indices for performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_keyword ON keyword_registry(keyword)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_frequency ON keyword_registry(frequency)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kpl_keyword ON keyword_pair_links(keyword_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kpl_pair ON keyword_pair_links(pair_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assoc_keywords ON keyword_associations(keyword_a, keyword_b)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assoc_pmi ON keyword_associations(pmi_score)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_live_session ON live_session_index(session_id)")
    print("✅ Created all indices")
    
    # Insert metadata
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    metadata = {
        "created_at": datetime.now().isoformat(),
        "version": "3.0",
        "purpose": "Learning Keyword System with Co-occurrence Tracking",
        "schema_version": "1.0"
    }
    
    for key, value in metadata.items():
        conn.execute("INSERT OR REPLACE INTO _metadata (key, value) VALUES (?, ?)", (key, value))
    
    conn.commit()
    
    # Get stats
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\n📊 Database created successfully!")
    print(f"   Tables: {len(tables)}")
    print(f"   Location: {db_path}")
    print(f"   Size: {db_path.stat().st_size / 1024:.1f} KB")
    
    conn.close()
    
    return db_path


if __name__ == "__main__":
    create_keywords_db()
    print("\n✅ evoki_v3_keywords.db ready!")
