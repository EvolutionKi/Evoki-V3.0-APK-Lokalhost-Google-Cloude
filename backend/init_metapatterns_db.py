#!/usr/bin/env python3
"""
Initialize evoki_metapatterns.db from schema
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
SCHEMA_FILE = PROJECT_ROOT / "backend/schemas/evoki_metapatterns_schema.sql"
DB_PATH = PROJECT_ROOT / "evoki_metapatterns.db"

def init_metapatterns_db():
    """Initialize metapatterns.db from schema"""
    
    print("="*70)
    print("🔧 INITIALIZING evoki_metapatterns.db")
    print("="*70)
    
    if not SCHEMA_FILE.exists():
        print(f"❌ Schema file not found: {SCHEMA_FILE}")
        return False
    
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Drop existing
    print(f"⚠️  Dropping existing tables/views (if any)...")
    cur.execute("SELECT name FROM sqlite_master WHERE type='view'")
    for view in [row[0] for row in cur.fetchall()]:
        cur.execute(f"DROP VIEW IF EXISTS {view}")
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for table in [row[0] for row in cur.fetchall()]:
        if table != 'sqlite_sequence':
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
    success = init_metapatterns_db()
    exit(0 if success else 1)
