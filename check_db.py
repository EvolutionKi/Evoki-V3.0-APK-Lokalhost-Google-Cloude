import sqlite3
from pathlib import Path

db_path = Path("backend/data/databases/evoki_v3_core.db")
print(f"DB exists: {db_path.exists()}")
print(f"DB path: {db_path}")

if db_path.exists():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    conn.close()
