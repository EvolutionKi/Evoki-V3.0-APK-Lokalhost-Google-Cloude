#!/usr/bin/env python3
"""Extract 1000 pairs from evoki_v3_core.db for testing"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path("backend/data/databases/evoki_v3_core.db")
OUTPUT = Path("backend/data/test_1000_pairs.json")

print("="*70)
print("📤 EXTRACTING 1000 TEST PAIRS FROM DB")
print("="*70)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get first 1000 pairs
cur.execute("""
    SELECT pair_id, session_id, turn_number,
           user_text, ai_text, ts_unix, created_at
    FROM prompt_pairs
    ORDER BY session_id, turn_number
    LIMIT 1000
""")

rows = cur.fetchall()
conn.close()

# Convert to JSON
pairs = []
for row in rows:
    pairs.append({
        "pair_id": row[0],
        "session_id": row[1],
        "turn_number": row[2],
        "user_text": row[3],
        "ai_text": row[4],
        "ts_unix": row[5],
        "created_at": row[6]
    })

# Save
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(pairs, f, indent=2, ensure_ascii=False)

print(f"✅ Extracted {len(pairs)} pairs")
print(f"📁 Saved to: {OUTPUT}")
print(f"📊 First pair preview:")
print(f"   User: {pairs[0]['user_text'][:60]}...")
print(f"   AI:   {pairs[0]['ai_text'][:60]}...")
print("="*70)
