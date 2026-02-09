"""
Create evoki_v3_trajectories.db - Metric Trajectories & Predictions
"""
import sqlite3
from pathlib import Path
from datetime import datetime


def create_trajectories_db():
    """Create trajectories database for metric evolution tracking"""
    
    db_path = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_trajectories.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    
    print(f"Creating trajectories database: {db_path}")
    
    # 1. Metric Trajectories (Historical metric paths)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metric_trajectories (
            trajectory_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            trajectory_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    print("✅ Created metric_trajectories")
    
    # 2. Metric Predictions (Future predictions based on patterns)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metric_predictions (
            prediction_id TEXT PRIMARY KEY,
            pair_id TEXT,
            metric_name TEXT NOT NULL,
            predicted_plus_1 REAL,
            predicted_plus_5 REAL,
            predicted_plus_25 REAL,
            confidence_score REAL,
            created_at TEXT NOT NULL
        )
    """)
    print("✅ Created metric_predictions")
    
    # 3. Phase Detections (W-P-F phase shifts)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS phase_detections (
            detection_id TEXT PRIMARY KEY,
            pair_id TEXT,
            phase TEXT NOT NULL,
            confidence REAL,
            indicators TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    print("✅ Created phase_detections")
    
    # Indices
    conn.execute("CREATE INDEX IF NOT EXISTS idx_traj_session ON metric_trajectories(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_traj_metric ON metric_trajectories(metric_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pred_pair ON metric_predictions(pair_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pred_metric ON metric_predictions(metric_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_phase_pair ON phase_detections(pair_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_phase_type ON phase_detections(phase)")
    print("✅ Created all indices")
    
    # Metadata
    conn.execute("CREATE TABLE IF NOT EXISTS _metadata (key TEXT PRIMARY KEY, value TEXT)")
    metadata = {
        "created_at": datetime.now().isoformat(),
        "version": "3.0",
        "purpose": "Metric Trajectories & Predictions (W-P-F Analysis)",
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
    create_trajectories_db()
    print("\n✅ evoki_v3_trajectories.db ready!")
