#!/usr/bin/env python3
"""
Initialize evoki_metadata.db from schema
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
SCHEMA_FILE = PROJECT_ROOT / "backend/schemas/evoki_metadata_schema.sql"
DB_PATH = PROJECT_ROOT / "evoki_metadata.db"

def init_metadata_db():
    """Initialize metadata.db from schema"""
    
    print("="*70)
    print("🔧 INITIALIZING evoki_metadata.db")
    print("="*70)
    
    # Read schema
    if not SCHEMA_FILE.exists():
        print(f"❌ Schema file not found: {SCHEMA_FILE}")
        return False
    
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Create DB
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Drop existing tables (CLEAN SLATE!)
    print(f"⚠️  Dropping existing tables/views (if any)...")
    
    # Drop views first
    cur.execute("SELECT name FROM sqlite_master WHERE type='view'")
    existing_views = [row[0] for row in cur.fetchall()]
    for view in existing_views:
        cur.execute(f"DROP VIEW IF EXISTS {view}")
    
    # Then tables
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
    success = init_metadata_db()
    exit(0 if success else 1)
