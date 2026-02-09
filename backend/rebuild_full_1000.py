#!/usr/bin/env python3
"""
FULL REBUILD: 1000 PAIRS with NEW 4-Phase Calculator
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import time

# Paths
PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
sys.path.insert(0, str(PROJECT_ROOT / "backend/core/evoki_metrics_v3"))

from calculator_4phase_complete import calculate_all_168

# DB Path
DB_PATH = PROJECT_ROOT / "backend/data/databases/evoki_v3_core.db"
GENESIS_ANCHOR = "be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4"

# Delete old DB
if DB_PATH.exists():
    DB_PATH.unlink()
    print("🗑️  Deleted old database")

# Create DB
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create tables
cur.execute("""
    CREATE TABLE IF NOT EXISTS prompt_pairs (
        pair_id TEXT PRIMARY KEY,
        session_id TEXT,
        user_text TEXT,
        ai_text TEXT,
        created_at TEXT
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics_full (
        pair_id TEXT PRIMARY KEY,
        user_metrics_json TEXT,
        user_m1_A REAL,
        user_m19_z_prox REAL,
        user_m151_hazard REAL,
        ai_metrics_json TEXT,
        ai_m1_A REAL,
        ai_m19_z_prox REAL,
        ai_m151_hazard REAL,
        b_vector_json TEXT,
        b_align REAL,
        chain_hash TEXT,
        created_at TEXT
    )
""")

# Load ALL 1000 pairs
with open(PROJECT_ROOT / "backend/data/test_1000_pairs_2025.json", encoding="utf-8") as f:
    pairs = json.load(f)

print("=" * 70)
print(f"🚀 REBUILDING {len(pairs)} PAIRS WITH NEW 4-PHASE CALCULATOR")
print("=" * 70)

prev_hash = GENESIS_ANCHOR
start_time = time.time()
total_calc_time = 0.0

for i, pair in enumerate(pairs, 1):
    pair_id = pair["pair_id"]
    user_text = pair["user_text"]
    ai_text = pair["ai_text"]
    timestamp = datetime.now().isoformat()
    
    # Calculate USER metrics
    calc_start = time.time()
    
    user_ctx = {
        "pair_id": pair_id,
        "user_text": user_text,
        "ai_text": "",
        "timestamp": timestamp,
        "turn": i,
        "prev_chain_hash": prev_hash,
    }
    
    user_result = calculate_all_168(user_text, context=user_ctx)
    
    # Calculate AI metrics
    ai_ctx = {
        "pair_id": pair_id,
        "user_text": user_text,
        "ai_text": ai_text,
        "timestamp": timestamp,
        "turn": i,
        "prev_chain_hash": user_result["chain_hash"],
        "prev_m1_A": user_result["metrics"].get("m1_A", 0.5),
        "prev_nabla_a": user_result["metrics"].get("m17_nabla_a", 0.0),
    }
    
    ai_result = calculate_all_168(ai_text, context=ai_ctx)
    
    calc_time = (time.time() - calc_start) * 1000  # ms
    total_calc_time += calc_time
    
    # Update chain
    prev_hash = ai_result["chain_hash"]
    
    # Write to DB
    cur.execute("""
        INSERT OR REPLACE INTO prompt_pairs 
        (pair_id, session_id, user_text, ai_text, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (pair_id, pair.get("session_id", "rebuild_2025"), user_text, ai_text, timestamp))
    
    cur.execute("""
        INSERT OR REPLACE INTO metrics_full
        (pair_id, user_metrics_json, user_m1_A, user_m19_z_prox, user_m151_hazard,
         ai_metrics_json, ai_m1_A, ai_m19_z_prox, ai_m151_hazard,
         b_vector_json, b_align, chain_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pair_id,
        json.dumps(user_result["metrics"]),
        user_result["metrics"].get("m1_A", 0.0),
        user_result["metrics"].get("m19_z_prox", 0.0),
        user_result["metrics"].get("m151_hazard", 0.0),
        json.dumps(ai_result["metrics"]),
        ai_result["metrics"].get("m1_A", 0.0),
        ai_result["metrics"].get("m19_z_prox", 0.0),
        ai_result["metrics"].get("m151_hazard", 0.0),
        json.dumps(ai_result["b_vector"]),
        ai_result["b_align"],
        ai_result["chain_hash"],
        timestamp
    ))
    
    # Progress every 50 pairs
    if i % 50 == 0:
        elapsed = (time.time() - start_time) / 60  # minutes
        avg_calc = total_calc_time / (i * 2)  # avg per calculation
        eta_mins = (avg_calc * (len(pairs) - i) * 2) / 1000 / 60
        
        print(f"\n[{i}/{len(pairs)}] Progress Report:")
        print(f"  ⏱️  Elapsed: {elapsed:.1f}min | ETA: {eta_mins:.1f}min")
        print(f"  ⚡ Avg calc: {avg_calc:.1f}ms")
        print(f"  📊 Last pair:")
        print(f"     User m1_A: {user_result['metrics'].get('m1_A', 0):.3f}")
        print(f"     AI m1_A: {ai_result['metrics'].get('m1_A', 0):.3f}")
        print(f"     B_align: {ai_result['b_align']:.3f}")
        print(f"     Chain: ...{ai_result['chain_hash'][-12:]}")
        
        # Commit every 50
        conn.commit()

# Final commit
conn.commit()
conn.close()

total_time = (time.time() - start_time) / 60
avg_per_pair = (total_calc_time / (len(pairs) * 2))

print("\n" + "=" * 70)
print("✅ REBUILD COMPLETE!")
print("=" * 70)
print(f"  📊 Total pairs: {len(pairs)}")
print(f"  ⏱️  Total time: {total_time:.1f} minutes")
print(f"  ⚡ Avg per calculation: {avg_per_pair:.1f}ms")
print(f"  💾 Database: {DB_PATH}")
print(f"  🔗 Final hash: ...{prev_hash[-12:]}")
print(f"\n🎉 ALL DATA NOW CALCULATED WITH CORRECT 4-PHASE SYSTEM!")
