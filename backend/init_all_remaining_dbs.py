#!/usr/bin/env python3
"""
Initialize REMAINING 6 databases:
- evoki_v3_graph.db
- evoki_v3_keywords.db
- evoki_v3_analytics.db
- evoki_v3_trajectories.db
- evoki_triggers.db
- evoki_metapatterns.db
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")

# Database definitions
DATABASES = [
    {
        "name": "evoki_v3_graph.db",
        "path": PROJECT_ROOT / "backend/data/databases/evoki_v3_graph.db",
        "schema": PROJECT_ROOT / "backend/schemas/BUCH7_evoki_v3_graph_schema.sql"
    },
    {
        "name": "evoki_v3_keywords.db",
        "path": PROJECT_ROOT / "backend/data/databases/evoki_v3_keywords.db",
        "schema": PROJECT_ROOT / "backend/schemas/evoki_v3_keywords_schema.sql"
    },
    {
        "name": "evoki_v3_analytics.db",
        "path": PROJECT_ROOT / "backend/data/databases/evoki_v3_analytics.db",
        "schema": PROJECT_ROOT / "backend/schemas/evoki_v3_analytics_schema.sql"
    },
    {
        "name": "evoki_v3_trajectories.db",
        "path": PROJECT_ROOT / "backend/data/databases/evoki_v3_trajectories.db",
        "schema": PROJECT_ROOT / "backend/schemas/evoki_v3_trajectories_schema.sql"
    },
    {
        "name": "evoki_triggers.db",
        "path": PROJECT_ROOT / "evoki_triggers.db",
        "schema": PROJECT_ROOT / "backend/schemas/evoki_triggers_schema.sql"
    },
    {
        "name": "evoki_metapatterns.db",
        "path": PROJECT_ROOT / "evoki_metapatterns.db",
        "schema": PROJECT_ROOT / "backend/schemas/evoki_metapatterns_schema.sql"
    }
]

def init_database(db_config: dict) -> bool:
    """Initialize a single database"""
    
    name = db_config["name"]
    db_path = db_config["path"]
    schema_file = db_config["schema"]
    
    print(f"\n{'='*70}")
    print(f"🔧 INITIALIZING {name}")
    print(f"{'='*70}")
    
    # Check schema
    if not schema_file.exists():
        print(f"❌ Schema not found: {schema_file}")
        return False
    
    # Read schema
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Create DB
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Drop existing
    print(f"⚠️  Dropping existing tables/views...")
    cur.execute("SELECT name FROM sqlite_master WHERE type='view'")
    for view in [row[0] for row in cur.fetchall()]:
        cur.execute(f"DROP VIEW IF EXISTS {view}")
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for table in [row[0] for row in cur.fetchall()]:
        if table != 'sqlite_sequence':
            cur.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    
    # Apply schema
    try:
        cur.executescript(schema_sql)
        conn.commit()
        print(f"✅ Schema applied successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.close()
        return False
    
    # List tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    
    print(f"\n📊 Created {len(tables)} tables:")
    for table in sorted(tables):
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"   • {table:30} ({count} rows)")
    
    conn.close()
    print(f"\n✅ {name} initialized!")
    return True

def init_all_remaining():
    """Initialize all remaining databases"""
    
    print("="*70)
    print("🚀 INITIALIZING REMAINING 6 DATABASES")
    print("="*70)
    
    results = {}
    
    for db_config in DATABASES:
        success = init_database(db_config)
        results[db_config["name"]] = success
    
    # Summary
    print("\n" + "="*70)
    print("📊 INITIALIZATION SUMMARY")
    print("="*70)
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
    
    print(f"\n{'='*70}")
    print(f"✅ Successfully initialized: {success_count}/{total_count}")
    print(f"{'='*70}")
    
    return all(results.values())

if __name__ == "__main__":
    success = init_all_remaining()
    exit(0 if success else 1)
