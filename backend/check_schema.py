#!/usr/bin/env python3
"""Check DB schema"""

import sqlite3
from pathlib import Path

DB_PATH = Path("backend/data/databases/evoki_v3_core.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get table info
cur.execute("PRAGMA table_info(prompt_pairs)")
columns = cur.fetchall()

print("="*70)
print("📋 PROMPT_PAIRS TABLE SCHEMA")
print("="*70)
for col in columns:
    print(f"  {col[1]:20} {col[2]:10}")

# Get sample row
cur.execute("SELECT * FROM prompt_pairs LIMIT 1")
sample = cur.fetchone()

print("\n📊 SAMPLE ROW:")
print("="*70)
if sample:
    for i, (col, val) in enumerate(zip(columns, sample)):
        val_preview = str(val)[:60] if val else "NULL"
        print(f"  {col[1]:20} = {val_preview}")

conn.close()
print("="*70)
