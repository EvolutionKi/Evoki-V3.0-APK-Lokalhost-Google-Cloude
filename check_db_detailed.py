import sqlite3
from pathlib import Path

db_path = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude/backend/data/databases/evoki_v3_core.db")
print(f"Checking DB: {db_path}")
print(f"Exists: {db_path.exists()}")

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    # Get all tables
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"\nTables found: {len([t for t in tables])}")
    for table in tables:
        print(f"  - {table[0]}")
        
        # Count rows
        count = cur.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
        print(f"    Rows: {count}")
    
    conn.close()
