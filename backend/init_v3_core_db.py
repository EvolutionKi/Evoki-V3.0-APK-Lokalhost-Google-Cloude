#!/usr/bin/env python3
"""
Initialize evoki_v3_core.db from BUCH7 Schema
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
SCHEMA_FILE = PROJECT_ROOT / "backend/schemas/BUCH7_evoki_v3_core_schema.sql"
DB_PATH = PROJECT_ROOT / "backend/data/databases/evoki_v3_core.db"

def init_v3_core_db():
    """Initialize v3_core.db from BUCH 7 schema"""
    
    print("="*70)
    print("🔧 INITIALIZING evoki_v3_core.db (BUCH 7)")
    print("="*70)
    
    # Read schema
    if not SCHEMA_FILE.exists():
        print(f"❌ Schema file not found: {SCHEMA_FILE}")
        return False
    
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Create DB
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Drop existing tables (CLEAN SLATE!)
    print(f"⚠️  Dropping existing tables (if any)...")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cur.fetchall()]
    for table in existing_tables:
        if table != 'sqlite_sequence':  # Skip system table
            cur.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    
    # Execute schema
    try:
        cur.executescript(schema_sql)
        conn.commit()
        print(f"✅ Schema applied successfully")
    except Exception as e:
        print(f"❌ Error applying schema: {e}")
        return False
    
    # Check tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    
    print(f"\n📊 Created tables:")
    for table in sorted(tables):
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"   • {table:30} ({count} rows)")
    
    conn.close()
    
    print(f"\n✅ Database initialized: {DB_PATH}")
    print("="*70)
    return True

if __name__ == "__main__":
    success = init_v3_core_db()
    exit(0 if success else 1)
