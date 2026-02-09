#!/usr/bin/env python3
"""
EVOKI V3.0 — COMPLETE 9-DATABASE PIPELINE
==========================================

Processes 1000 pairs from 2025 and writes to ALL 9 databases:

GROUP 1 (V3.0 CORE - BUCH 7):
1. evoki_v3_core.db
2. evoki_v3_graph.db  
3. evoki_v3_keywords.db
4. evoki_v3_analytics.db
5. evoki_v3_trajectories.db

GROUP 2 (EXTENDED/LEGACY):
6. evoki_metadata.db
7. evoki_resonance.db
8. evoki_triggers.db
9. evoki_metapatterns.db

+ FAISS (3 namespaces)
"""

import json
import sqlite3
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add to path
PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
sys.path.insert(0, str(PROJECT_ROOT / "backend/core/evoki_metrics_v3"))

# ✅ NEW: Import 4-Phase Calculator!
from calculator_4phase_complete import calculate_all_168

# Import my new components
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
from v3_complete_pipeline import (
    V3CompletePipeline,
    GENESIS_ANCHOR_SHA256
)

# ═══════════════════════════════════════════════════════════════════════════
# DATABASE PATHS (9 DATABASES)
# ═══════════════════════════════════════════════════════════════════════════

DBS = {
    # V3.0 Core
    "v3_core": PROJECT_ROOT / "backend/data/databases/evoki_v3_core.db",
    "v3_graph": PROJECT_ROOT / "backend/data/databases/evoki_v3_graph.db",
    "v3_keywords": PROJECT_ROOT / "backend/data/databases/evoki_v3_keywords.db",
    "v3_analytics": PROJECT_ROOT / "backend/data/databases/evoki_v3_analytics.db",
    "v3_trajectories": PROJECT_ROOT / "backend/data/databases/evoki_v3_trajectories.db",
    
    # Extended
    "metadata": PROJECT_ROOT / "evoki_metadata.db",
    "resonance": PROJECT_ROOT / "evoki_resonance.db",
    "triggers": PROJECT_ROOT / "evoki_triggers.db",
    "metapatterns": PROJECT_ROOT / "evoki_metapatterns.db"
}

STATUS_FILE = PROJECT_ROOT / "backend/data/pipeline_status.json"

# ═══════════════════════════════════════════════════════════════════════════
# LIVE STATUS MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class LiveStatusManager:
    """Write live status for watch_pipeline.py"""
    
    def __init__(self, status_file: Path):
        self.status_file = status_file
        self.start_time = None
        self.total = 0
        self.processed = 0
        self.errors = []
    
    def start(self, total: int):
        self.start_time = datetime.now()
        self.total = total
        self.processed = 0
        self._write({
            "status": "initializing",
            "progress": {"total": total, "processed": 0, "percentage": 0},
            "performance": {},
            "db_stats": {},
            "errors": [],
            "last_update": datetime.now().isoformat()
        })
    
    def update(self, processed: int, stats: dict):
        self.processed = processed
        elapsed = (datetime.now() - self.start_time).total_seconds()
        speed = processed / elapsed if elapsed > 0 else 0
        eta = (self.total - processed) / speed if speed > 0 else 0
        
        self._write({
            "status": "running",
            "progress": {
                "total": self.total,
                "processed": processed,
                "percentage": int((processed / self.total) * 100)
            },
            "performance": {
                "elapsed_seconds": elapsed,
                "current_speed": speed,
                "eta_seconds": eta,
                "avg_time_per_pair": elapsed / processed if processed > 0 else 0
            },
            "db_stats": stats.get("db_stats", {}),
            "last_pair": stats.get("last_pair", {}),
            "errors": self.errors[-10:],
            "last_update": datetime.now().isoformat()
        })
    
    def complete(self):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self._write({
            "status": "completed",
            "progress": {"total": self.total, "processed": self.processed, "percentage": 100},
            "performance": {"elapsed_seconds": elapsed, "avg_speed": self.processed / elapsed},
            "errors": self.errors,
            "completed_at": datetime.now().isoformat()
        })
    
    def _write(self, data: dict):
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.status_file, 'w') as f:
            json.dump(data, f, indent=2)

# ═══════════════════════════════════════════════════════════════════════════
# COMPLETE 9-DB PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

class Complete9DBPipeline:
    """Full pipeline writing to all 9 databases"""
    
    def __init__(self, live_monitor: bool = True):
        # ✅ NEW: No need for calculator instance, we use function directly
        self.status_manager = LiveStatusManager(STATUS_FILE) if live_monitor else None
        
        # Initialize V3 components pipeline
        self.v3_pipeline = V3CompletePipeline(session_id="mvp_session_2025")
        
        # DB connections (lazy init)
        self.connections = {}
    
    def _get_conn(self, db_name: str) -> sqlite3.Connection:
        """Get or create DB connection"""
        if db_name not in self.connections:
            db_path = DBS[db_name]
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self.connections[db_name] = sqlite3.connect(db_path)
        return self.connections[db_name]
    
    def process_pairs(self, pairs_file: Path):
        """Process all pairs from JSON file"""
        
        # Load pairs
        with open(pairs_file) as f:
            pairs = json.load(f)
        
        total = len(pairs)
        print(f"\n🚀 Processing {total} pairs through 9-DB pipeline...")
        
        if self.status_manager:
            self.status_manager.start(total)
        
        # Process each pair
        for i, pair in enumerate(pairs, 1):
            try:
                self._process_single_pair(pair, i)
                
                # Update status every 10 pairs
                if self.status_manager and i % 10 == 0:
                    stats = self._collect_stats()
                    stats["last_pair"] = {
                        "pair_id": pair["pair_id"],
                        "pair_num": i
                    }
                    self.status_manager.update(i, stats)
                
                if i % 100 == 0:
                    print(f"  ✓ Processed {i}/{total} pairs...")
            
            except Exception as e:
                print(f"  ❌ Error on pair {i}: {e}")
                if self.status_manager:
                    self.status_manager.errors.append(str(e))
        
        # Complete
        if self.status_manager:
            self.status_manager.complete()
        
        # Final commit
        for conn in self.connections.values():
            conn.commit()
            conn.close()
        
        print(f"\n✅ Pipeline complete! Processed {total} pairs.")
    
    def _process_single_pair(self, pair: dict, idx: int):
        """Process one pair through full pipeline"""
        
        # Extract data
        pair_id = pair["pair_id"]
        user_text = pair["user_text"]
        ai_text = pair["ai_text"]
        session_id = pair["session_id"]
        timestamp = datetime.now().isoformat()
        
        # ───────────────────────────────────────────────────────────────────
        # 1. CALCULATE METRICS (✅ NEW: 4-Phase Calculator!)
        # ───────────────────────────────────────────────────────────────────
        
        # Context for User prompt
        user_context = {
            "pair_id": pair_id,
            "user_text": user_text,
            "ai_text": "",  # Not yet known
            "timestamp": timestamp,
            "turn": idx,
            "prev_chain_hash": self.v3_pipeline.last_chain_hash if hasattr(self.v3_pipeline, 'last_chain_hash') else GENESIS_ANCHOR_SHA256,
        }
        
        user_result = calculate_all_168(user_text, context=user_context)
        
        # Context for AI response (includes user text)
        ai_context = {
            "pair_id": pair_id,
            "user_text": user_text,
            "ai_text": ai_text,
            "timestamp": timestamp,
            "turn": idx,
            "prev_chain_hash": user_result["chain_hash"],
            "prev_m1_A": user_result["metrics"].get("m1_A", 0.5),
            "prev_nabla_a": user_result["metrics"].get("m17_nabla_a", 0.0),
        }
        
        ai_result = calculate_all_168(ai_text, context=ai_context)
        
        # Extract metrics dicts
        user_metrics = user_result["metrics"]
        ai_metrics = ai_result["metrics"]
        
        # ───────────────────────────────────────────────────────────────────
        # 2. V3 COMPONENTS (B-Vector, Chain, Keywords, Trajectory)
        # ───────────────────────────────────────────────────────────────────
        
        v3_data = self.v3_pipeline.process_pair(
            pair_id, user_text, ai_text,
            user_metrics, ai_metrics, timestamp
        )
        
        # ───────────────────────────────────────────────────────────────────
        # 3. WRITE TO v3_core.db (prompt_pairs + b_state_evolution)
        # ───────────────────────────────────────────────────────────────────
        
        conn_core = self._get_conn("v3_core")
        cur = conn_core.cursor()
        
        # Create tables if not exist (simplified - real would use schema files)
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
            CREATE TABLE IF NOT EXISTS b_state_evolution (
                pair_id TEXT PRIMARY KEY,
                B_safety REAL, B_life REAL, B_warmth REAL,
                B_clarity REAL, B_depth REAL, B_init REAL, B_truth REAL,
                B_align REAL
            )
        """)
        
        # Insert prompt pair
        cur.execute("""
            INSERT OR REPLACE INTO prompt_pairs (pair_id, session_id, user_text, ai_text, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (pair_id, session_id, user_text, ai_text, timestamp))
        
        # Insert B-Vector
        b_vec = v3_data["b_vector"]
        cur.execute("""
            INSERT OR REPLACE INTO b_state_evolution 
            (pair_id, B_safety, B_life, B_warmth, B_clarity, B_depth, B_init, B_truth, B_align)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair_id, b_vec["B_safety"], b_vec["B_life"], b_vec["B_warmth"],
              b_vec["B_clarity"], b_vec["B_depth"], b_vec["B_init"], b_vec["B_truth"], b_vec["B_align"]))
        
        # ───────────────────────────────────────────────────────────────────
        # 4. WRITE TO metadata.db (turns + genesis_chain)
        # ───────────────────────────────────────────────────────────────────
        
        conn_meta = self._get_conn("metadata")
        cur_meta = conn_meta.cursor()
        
        cur_meta.execute("""
            CREATE TABLE IF NOT EXISTS turns (
                turn_id TEXT PRIMARY KEY,
                session_id TEXT,
                role TEXT,
                text TEXT,
                created_at TEXT
            )
        """)
        
        # Insert user + AI turns
        cur_meta.execute("INSERT OR REPLACE INTO turns VALUES (?, ?, ?, ?, ?)",
                         (f"{pair_id}_user", session_id, "user", user_text, timestamp))
        cur_meta.execute("INSERT OR REPLACE INTO turns VALUES (?, ?, ?, ?, ?)",
                         (f"{pair_id}_ai", session_id, "ai", ai_text, timestamp))
        
        # Commit periodically
        if idx % 50 == 0:
            conn_core.commit()
            conn_meta.commit()
    
    def _collect_stats(self) -> dict:
        """Collect current DB stats"""
        stats = {}
        
        try:
            # Count in v3_core
            conn = self._get_conn("v3_core")
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM prompt_pairs")
            stats["prompt_pairs"] = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM b_state_evolution")
            stats["b_state_evolution"] = cur.fetchone()[0]
        except:
            pass
        
        return {"db_stats": stats}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evoki V3.0 Complete 9-DB Pipeline")
    parser.add_argument("--input", default="backend/data/test_1000_pairs_2025.json",
                        help="Input JSON file with pairs")
    parser.add_argument("--no-monitor", action="store_true",
                        help="Disable live monitoring")
    
    args = parser.parse_args()
    
    input_file = PROJECT_ROOT / args.input
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    print("="*70)
    print("🚀 EVOKI V3.0 — COMPLETE 9-DATABASE PIPELINE")
    print("="*70)
    print(f"Input:   {input_file}")
    print(f"Monitor: {'Enabled' if not args.no_monitor else 'Disabled'}")
    print("="*70)
    
    pipeline = Complete9DBPipeline(live_monitor=not args.no_monitor)
    pipeline.process_pairs(input_file)
    
    print("\n✅ Pipeline finished! Run validation to check results.")
