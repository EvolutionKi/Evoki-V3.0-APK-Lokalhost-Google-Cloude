"""
Extend evoki_v3_core.db with Dual-Gradient columns
"""
import sqlite3
from pathlib import Path


def extend_core_db():
    """Add Dual-Gradient columns to metrics_full table"""
    
    db_path = Path(__file__).parent.parent / "data" / "databases" / "evoki_v3_core.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    
    print(f"Extending database: {db_path}")
    
    # Check current schema
    cursor = conn.execute("PRAGMA table_info(metrics_full)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    print(f"Current columns in metrics_full: {len(columns)}")
    
    # Add new columns if they don't exist
    new_columns = {
        "ai_metrics_json": "TEXT",
        "delta_user_m1_A": "REAL",
        "delta_ai_m1_A": "REAL",
        "diff_gradient_affekt": "REAL",
        "disharmony_score": "REAL"
    }
    
    added = 0
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            try:
                conn.execute(f"ALTER TABLE metrics_full ADD COLUMN {col_name} {col_type}")
                print(f"  ✅ Added column: {col_name}")
                added += 1
            except sqlite3.OperationalError as e:
                print(f"  ⚠️ Could not add {col_name}: {e}")
        else:
            print(f"  ⏭️ Column already exists: {col_name}")
    
    conn.commit()
    
    # Verify
    cursor = conn.execute("PRAGMA table_info(metrics_full)")
    columns_after = {row[1]: row[2] for row in cursor.fetchall()}
    
    print(f"\n📊 Schema extended!")
    print(f"   Columns before: {len(columns)}")
    print(f"   Columns after: {len(columns_after)}")
    print(f"   Added: {added}")
    
    # Get data stats
    cursor = conn.execute("SELECT COUNT(*) FROM prompt_pairs")
    pair_count = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) FROM metrics_full")
    metrics_count = cursor.fetchone()[0]
    
    print(f"\n📊 Data Stats:")
    print(f"   Prompt Pairs: {pair_count:,}")
    print(f"   Metrics Rows: {metrics_count:,}")
    
    conn.close()
    
    return db_path


if __name__ == "__main__":
    extend_core_db()
    print("\n✅ evoki_v3_core.db extended!")
