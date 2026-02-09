"""
Create evoki_v3_analytics.db - Complete Logging System
"""
import sqlite3
from pathlib import Path
from datetime import datetime


def create_analytics_db():
    """Create analytics database for comprehensive logging"""
    
    db_path = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_analytics.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    
    print(f"Creating analytics database: {db_path}")
    
    # 1. API Requests
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_requests (
            request_id TEXT PRIMARY KEY,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL,
            payload TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    print("✅ Created api_requests")
    
    # 2. API Responses
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_responses (
            response_id TEXT PRIMARY KEY,
            request_id TEXT NOT NULL,
            status_code INTEGER NOT NULL,
            response_body TEXT,
            latency_ms REAL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (request_id) REFERENCES api_requests(request_id)
        )
    """)
    print("✅ Created api_responses")
    
    # 3. Search Events
    conn.execute("""
        CREATE TABLE IF NOT EXISTS search_events (
            search_id TEXT PRIMARY KEY,
            query TEXT NOT NULL,
            search_type TEXT NOT NULL,
            results_count INTEGER,
            top_5_results TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    print("✅ Created search_events")
    
    # 4. Prompt History
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prompt_history (
            prompt_id TEXT PRIMARY KEY,
            pair_id TEXT,
            user_text TEXT,
            ai_text TEXT,
            user_metrics TEXT,
            ai_metrics TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    print("✅ Created prompt_history")
    
    # 5. Metric Evaluations
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metric_evaluations (
            eval_id TEXT PRIMARY KEY,
            pair_id TEXT,
            metric_name TEXT NOT NULL,
            user_value REAL,
            ai_value REAL,
            delta_value REAL,
            timestamp TEXT NOT NULL
        )
    """)
    print("✅ Created metric_evaluations")
    
    # 6. B-Vector Verifications
    conn.execute("""
        CREATE TABLE IF NOT EXISTS b_vector_verifications (
            verify_id TEXT PRIMARY KEY,
            pair_id TEXT,
            computed_b_vector TEXT,
            verified_b_vector TEXT,
            difference_score REAL,
            timestamp TEXT NOT NULL
        )
    """)
    print("✅ Created b_vector_verifications")
    
    # 7. Lexika Verification Log
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lexika_verification_log (
            verify_id TEXT PRIMARY KEY,
            pair_id TEXT,
            lexikon_name TEXT NOT NULL,
            hits_count INTEGER,
            matched_terms TEXT,
            score REAL,
            timestamp TEXT NOT NULL
        )
    """)
    print("✅ Created lexika_verification_log")
    
    # 8. Learning Events
    conn.execute("""
        CREATE TABLE IF NOT EXISTS learning_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    print("✅ Created learning_events")
    
    # 9. System Events
    conn.execute("""
        CREATE TABLE IF NOT EXISTS system_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    print("✅ Created system_events")
    
    # Indices
    conn.execute("CREATE INDEX IF NOT EXISTS idx_api_req_endpoint ON api_requests(endpoint)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_api_req_timestamp ON api_requests(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_api_resp_request ON api_responses(request_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_search_type ON search_events(search_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_search_timestamp ON search_events(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_prompt_pair ON prompt_history(pair_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_metric_pair ON metric_evaluations(pair_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_metric_name ON metric_evaluations(metric_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lexika_pair ON lexika_verification_log(pair_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lexika_name ON lexika_verification_log(lexikon_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_learning_type ON learning_events(event_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_system_type ON system_events(event_type)")
    print("✅ Created all indices")
    
    # Metadata
    conn.execute("CREATE TABLE IF NOT EXISTS _metadata (key TEXT PRIMARY KEY, value TEXT)")
    metadata = {
        "created_at": datetime.now().isoformat(),
        "version": "3.0",
        "purpose": "Complete Analytics & Logging System",
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
    create_analytics_db()
    print("\n✅ evoki_v3_analytics.db ready!")
