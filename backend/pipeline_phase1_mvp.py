#!/usr/bin/env python3
"""
PHASE 1 MVP PIPELINE — 3 Critical Databases Only
================================================

Processes 1000 pairs from 2025 into:
1. evoki_v3_core.db      (BUCH 7 - prompt_pairs, metrics_full, b_state_evolution)
2. evoki_metadata.db     (turns tracking, genesis chain)
3. evoki_resonance.db    (metrics mirror, gradients)

Uses EXISTING calculator_spec_A_PHYS_V11.py for metrics!
"""

import json
import sqlite3
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
sys.path.insert(0, str(PROJECT_ROOT / "backend/core/evoki_metrics_v3"))

# Import existing calculator!
from calculator_spec_A_PHYS_V11 import calculate_spec_compliant

# Database paths
DB_V3_CORE = PROJECT_ROOT / "backend/data/databases/evoki_v3_core.db"
DB_METADATA = PROJECT_ROOT / "evoki_metadata.db"
DB_RESONANCE = PROJECT_ROOT / "evoki_resonance.db"

# Input data
INPUT_JSON = PROJECT_ROOT / "backend/data/test_1000_pairs_2025.json"
STATUS_FILE = PROJECT_ROOT / "backend/data/pipeline_phase1_status.json"

# ═══════════════════════════════════════════════════════════════════════════
# LIVE STATUS
# ═══════════════════════════════════════════════════════════════════════════

class LiveStatus:
    def __init__(self, file: Path):
        self.file = file
        self.start_time = None
    
    def update(self, data: dict):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file, 'w') as f:
            json.dump(data, f, indent=2)

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1 MVP PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

class Phase1Pipeline:
    """MVP Pipeline for 3 critical databases"""
    
    def __init__(self):
        self.status = LiveStatus(STATUS_FILE)
        self.session_id = "mvp_2025_session"
        self.genesis_hash = hashlib.sha256(b"EVOKI_V3_GENESIS_2026").hexdigest()
    
    def process_all(self, pairs_file: Path):
        """Process all pairs"""
        
        # Load pairs
        with open(pairs_file, encoding='utf-8') as f:
            pairs = json.load(f)
        
        total = len(pairs)
        print(f"\n🚀 Processing {total} pairs (Phase 1 MVP)...")
        print(f"   v3_core:    {DB_V3_CORE}")
        print(f"   metadata:   {DB_METADATA}")
        print(f"   resonance:  {DB_RESONANCE}")
        print()
        
        self.start_time = datetime.now()
        
        # Connect to all 3 DBs
        conn_core = sqlite3.connect(DB_V3_CORE)
        conn_meta = sqlite3.connect(DB_METADATA)
        conn_reso = sqlite3.connect(DB_RESONANCE)
        
        # Process each pair
        for i, pair in enumerate(pairs, 1):
            try:
                self._process_pair(
                    pair, i,
                    conn_core.cursor(),
                    conn_meta.cursor(),
                    conn_reso.cursor()
                )
                
                # Commit every 50 pairs
                if i % 50 == 0:
                    conn_core.commit()
                    conn_meta.commit()
                    conn_reso.commit()
                    print(f"  ✓ {i}/{total} pairs processed...")
                
                # Update status every 10
                if i % 10 == 0:
                    self._update_status(i, total)
            
            except Exception as e:
                print(f"  ❌ Error on pair {i}: {e}")
        
        # Final commit
        conn_core.commit()
        conn_meta.commit()
        conn_reso.commit()
        
        conn_core.close()
        conn_meta.close()
        conn_reso.close()
        
        print(f"\n✅ Pipeline complete! Processed {total} pairs.")
    
    def _process_pair(self, pair: dict, idx: int, cur_core, cur_meta, cur_reso):
        """Process single pair into all 3 DBs"""
        
        pair_id = pair["pair_id"]
        user_text = pair["user_text"]
        ai_text = pair["ai_text"]
        timestamp = datetime.now().isoformat()
        
        # ───────────────────────────────────────────────────────────────────
        # CALCULATE METRICS (using existing calculator!)
        # ───────────────────────────────────────────────────────────────────
        
        user_spectrum = calculate_spec_compliant(user_text)
        ai_spectrum = calculate_spec_compliant(ai_text)
        
        # ───────────────────────────────────────────────────────────────────
        # 1. WRITE TO v3_core.db
        # ───────────────────────────────────────────────────────────────────
        
        # Insert prompt_pair (with pair_index as required by BUCH7 schema!)
        cur_core.execute("""
            INSERT OR REPLACE INTO prompt_pairs 
            (pair_id, session_id, pair_index, user_text, ai_text, pair_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pair_id, self.session_id, idx - 1, user_text, ai_text, 
              hashlib.sha256(f"{user_text}{ai_text}".encode()).hexdigest(), timestamp))
        
        # Insert metrics_full (BUCH7 schema: JSON + denormalized critical fields)
        user_metrics_dict = user_spectrum.to_dict()
        ai_metrics_dict = ai_spectrum.to_dict()
        
        cur_core.execute("""
            INSERT OR REPLACE INTO metrics_full 
            (pair_id, prompt_hash, timecode, 
             user_metrics_json, user_m1_A, user_m101_T_panic, user_m151_hazard, user_m160_F_risk,
             ai_metrics_json, ai_m1_A, ai_m2_PCI, ai_m161_commit, ai_m160_F_risk)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair_id,
              hashlib.sha256(f"{user_text}{ai_text}".encode()).hexdigest(),
              timestamp,
              json.dumps(user_metrics_dict),
              getattr(user_spectrum, 'm1_A', 0.0),
              getattr(user_spectrum, 'm101_t_panic', 0.0),
              getattr(user_spectrum, 'm151_omega', 0.0),
              getattr(user_spectrum, 'm160_F_risk', 0.0),
              json.dumps(ai_metrics_dict),
              getattr(ai_spectrum, 'm1_A', 0.0),
              getattr(ai_spectrum, 'm2_PCI', 0.0),
              getattr(ai_spectrum, 'm161_commit', 0.0),
              getattr(ai_spectrum, 'm160_F_risk', 0.0)))
        
        
        # ───────────────────────────────────────────────────────────────────
        # 2. WRITE TO metadata.db
        # ───────────────────────────────────────────────────────────────────
        
        # Insert user + AI turns (metadata DB also needs pair_hash!)
        pair_hash = hashlib.sha256(f"{user_text}{ai_text}".encode()).hexdigest()
        cur_meta.execute("""
            INSERT OR REPLACE INTO prompt_pairs 
            (pair_id, session_id, pair_index, user_text, ai_text, user_ts, ai_ts, pair_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair_id, self.session_id, idx - 1, user_text, ai_text, timestamp, timestamp, pair_hash, timestamp))
        
        # Genesis chain (simplified - just prev/current hash)
        current_hash = hashlib.sha256(f"{pair_hash}{self.genesis_hash}".encode()).hexdigest()
        
        cur_meta.execute("""
            INSERT OR REPLACE INTO session_chain
            (session_id, pair_id, prev_hash, current_hash, is_genesis)
            VALUES (?, ?, ?, ?, ?)
        """, (self.session_id, pair_id, self.genesis_hash, current_hash, 1 if idx == 1 else 0))
        
        # Update genesis for next
        self.genesis_hash = current_hash
        
        # ───────────────────────────────────────────────────────────────────
        # 3. WRITE TO resonance.db (core metrics only - author='user')
        # ───────────────────────────────────────────────────────────────────
        
        # Write USER metrics to core_metrics table (author='user')
        cur_reso.execute("""
            INSERT OR REPLACE INTO core_metrics
            (pair_id, pair_hash, timecode, author, m1_A, m2_PCI, m5_coh, m19_z_prox, m20_phi_proxy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair_id,
              pair_hash,
              timestamp,
              'user',
              getattr(user_spectrum, 'm1_A', 0.0),
              getattr(user_spectrum, 'm2_PCI', 0.0),
              getattr(user_spectrum, 'm5_coh', 0.0),
              getattr(user_spectrum, 'm19_z_prox', 0.0),
              getattr(user_spectrum, 'm20_phi_proxy', 0.0)))
    
    def _update_status(self, processed: int, total: int):
        """Update live status file"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        speed = processed / elapsed if elapsed > 0 else 0
        eta = (total - processed) / speed if speed > 0 else 0
        
        self.status.update({
            "status": "running",
            "progress": {"processed": processed, "total": total, "percentage": int((processed / total) * 100)},
            "performance": {"elapsed_sec": elapsed, "speed": speed, "eta_sec": eta},
            "last_update": datetime.now().isoformat()
        })

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not INPUT_JSON.exists():
        print(f"❌ Input not found: {INPUT_JSON}")
        print(f"   Run: python backend/extract_1000_pairs_2025.py first!")
        sys.exit(1)
    
    print("="*70)
    print("🚀 PHASE 1 MVP PIPELINE (3 Critical Databases)")
    print("="*70)
    
    pipeline = Phase1Pipeline()
    pipeline.process_all(INPUT_JSON)
    
    print("\n✅ Done! Run validation to check results.")
