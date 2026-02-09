#!/usr/bin/env python3
"""
PHASE 1 MVP PIPELINE - EXTENDED VERSION
Populates ALL critical tables including Physics + Andromatik
"""

import sys
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

# Add metrics to path
PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
sys.path.insert(0, str(PROJECT_ROOT / "backend/core/evoki_metrics_v3"))

from full_spectrum_168 import calculate_full_168

# Database paths
DB_V3_CORE = PROJECT_ROOT / "backend/data/databases/evoki_v3_core.db"
DB_METADATA = PROJECT_ROOT / "evoki_metadata.db"
DB_RESONANCE = PROJECT_ROOT / "evoki_resonance.db"

class ExtendedPipeline:
    """Extended MVP Pipeline with Physics + Andromatik"""
    
    def __init__(self):
        self.session_id = "mvp_2025_session_ext"
        self.genesis_hash = hashlib.sha256(b"EVOKI_V3_GENESIS_2026").hexdigest()
        
    def init_sessions(self):
        """Create session entries in all DBs"""
        timestamp = datetime.now().isoformat()
        date_ymd = datetime.now().strftime("%Y-%m-%d")
        
        # v3_core sessions
        with sqlite3.connect(DB_V3_CORE) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions
                (session_id, conversation_id, date_ymd, total_pairs, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (self.session_id, self.session_id[:8], date_ymd, 0, timestamp))
        
        # metadata sessions
        with sqlite3.connect(DB_METADATA) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions
                (session_id, conversation_id, date_ymd, total_pairs, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (self.session_id, self.session_id[:8], date_ymd, 0, timestamp))
        
        print(f"✓ Sessions initialized: {self.session_id}")
    
    def process_all(self, pairs_file: Path):
        """Process all pairs with FULL metric coverage"""
        
        # Load pairs
        with open(pairs_file, encoding='utf-8') as f:
            pairs = json.load(f)
        
        total = len(pairs)
        print(f"\n🚀 EXTENDED PIPELINE: Processing {total} pairs...")
        print(f"   ✓ Physics Metrics (m21-m35)")
        print(f"   ✓ Andromatik Metrics (m56-m70)")
        print(f"   ✓ Sessions Tables")
        print()
        
        # Connect to all 3 DBs
        conn_core = sqlite3.connect(DB_V3_CORE)
        conn_meta = sqlite3.connect(DB_METADATA)
        conn_reso = sqlite3.connect(DB_RESONANCE)
        
        # DEBUG: Check what DB we actually opened
        print(f"\n🔍 ACTUAL CONNECTION DEBUG:")
        print(f"   conn_core path: {DB_V3_CORE}")
        cur_check = conn_core.cursor()
        tables = cur_check.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print(f"   Tables in conn_core: {[t[0] for t in tables]}")
        print()
        
        # CLOSE and REOPEN to ensure schema is visible
        conn_core.close()
        conn_meta.close()
        conn_reso.close()
        
        # FRESH connections
        conn_core = sqlite3.connect(DB_V3_CORE)
        conn_meta = sqlite3.connect(DB_METADATA)
        conn_reso = sqlite3.connect(DB_RESONANCE)
        
        # Create cursors ONCE
        cur_core = conn_core.cursor()
        cur_meta = conn_meta.cursor()
        cur_reso = conn_reso.cursor()
        
        errors = []
        
        # Process each pair
        for i, pair in enumerate(pairs, 1):
            try:
                self._process_pair(
                    pair, i,
                    cur_core,
                    cur_meta,
                    cur_reso
                )
                
                # Commit every 50
                if i % 50 == 0:
                    conn_core.commit()
                    conn_meta.commit()
                    conn_reso.commit()
                    print(f"  ✓ {i}/{total} pairs processed...")
                    
            except Exception as e:
                errors.append((i, str(e)))
                if len(errors) <= 5:  # Show first 5 errors only
                    print(f"  ❌ Error on pair {i}: {e}")
                    if i == 1:  # Full traceback for first error
                        import traceback
                        traceback.print_exc()
        
        # Final commit
        conn_core.commit()
        conn_meta.commit()
        conn_reso.commit()
        
        # Update session total_pairs
        with sqlite3.connect(DB_V3_CORE) as conn:
            conn.execute("UPDATE sessions SET total_pairs = ? WHERE session_id = ?", (total, self.session_id))
        
        with sqlite3.connect(DB_METADATA) as conn:
            conn.execute("UPDATE sessions SET total_pairs = ? WHERE session_id = ?", (total, self.session_id))
        
        # Close
        conn_core.close()
        conn_meta.close()
        conn_reso.close()
        
        print(f"\n✅ Processing complete!")
        if errors:
            print(f"⚠️  {len(errors)} errors occurred")
        else:
            print(f"✅ ALL {total} pairs processed without errors!")
    
    def _process_pair(self, pair, idx, cur_core, cur_meta, cur_reso):
        """Process single pair - EXTENDED with Physics + Andromatik"""
        
        user_text = pair.get('user', '')
        ai_text = pair.get('ai', '')
        timestamp = datetime.now().isoformat()
        
        pair_id = f"pair_{idx:04d}"
        pair_hash = hashlib.sha256(f"{user_text}{ai_text}".encode()).hexdigest()
        
        # Calculate metrics (NOW 161!)
        user_metrics_dict = calculate_full_168(user_text)
        ai_metrics_dict = calculate_full_168(ai_text)
        
        # Helper to get metric from dict
        def get_metric(d, key, default=0.0):
            return d.get(key, default)
        
        # ───────────────────────────────────────────────────────────────────
        # 1. WRITE TO v3_core.db
        # ───────────────────────────────────────────────────────────────────
        
        # DEBUG: Check if we're using correct DB
        if idx == 1:
            print(f"\n🔍 DEBUG: DB_V3_CORE path = {DB_V3_CORE}")
            print(f"🔍 DEBUG: DB exists = {DB_V3_CORE.exists()}")
        
        # prompt_pairs
        cur_core.execute("""
            INSERT OR REPLACE INTO prompt_pairs 
            (pair_id, session_id, pair_index, user_text, ai_text, pair_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pair_id, self.session_id, idx - 1, user_text, ai_text, pair_hash, timestamp))
        
        # metrics_full (JSON + denormalized)
        cur_core.execute("""
            INSERT OR REPLACE INTO metrics_full 
            (pair_id, prompt_hash, timecode, 
             user_metrics_json, user_m1_A, user_m101_T_panic, user_m151_hazard, user_m160_F_risk,
             ai_metrics_json, ai_m1_A, ai_m2_PCI, ai_m161_commit, ai_m160_F_risk)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair_id,
              pair_hash,
              timestamp,
              json.dumps(user_metrics_dict),
              get_metric(user_metrics_dict, 'm1_A'),
              get_metric(user_metrics_dict, 'm101_t_panic'),
              get_metric(user_metrics_dict, 'm151_omega'),  # Note: m151 is omega not hazard
              get_metric(user_metrics_dict, 'm160_F_risk'),
              json.dumps(ai_metrics_dict),
              get_metric(ai_metrics_dict, 'm1_A'),
              get_metric(ai_metrics_dict, 'm2_PCI'),
              get_metric(ai_metrics_dict, 'm161_commit'),
              get_metric(ai_metrics_dict, 'm160_F_risk')))
        
        #───────────────────────────────────────────────────────────────────
        # 2. WRITE TO metadata.db
        # ───────────────────────────────────────────────────────────────────
        
        # NOTE: prompt_pairs is ONLY in core.db, NOT metadata.db!
        
        # session_chain
        current_hash = hashlib.sha256(f"{pair_hash}{self.genesis_hash}".encode()).hexdigest()
        
        cur_meta.execute("""
            INSERT OR REPLACE INTO session_chain
            (session_id, pair_id, prev_hash, current_hash, is_genesis)
            VALUES (?, ?, ?, ?, ?)
        """, (self.session_id, pair_id, self.genesis_hash, current_hash, 1 if idx == 1 else 0))
        
        # Update genesis for next
        self.genesis_hash = current_hash
        
        # ───────────────────────────────────────────────────────────────────
        # 3. WRITE TO resonance.db - EXTENDED!
        # ───────────────────────────────────────────────────────────────────
        
        # core_metrics (m1-m20) - USER
        cur_reso.execute("""
            INSERT OR REPLACE INTO core_metrics
            (pair_id, pair_hash, timecode, author, 
             m1_A, m2_PCI, m5_coh, m6_ZLF, m7_LL, m19_z_prox, m20_phi_proxy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair_id, pair_hash, timestamp, 'user',
              get_metric(user_metrics_dict, 'm1_A'),
              get_metric(user_metrics_dict, 'm2_PCI'),
              get_metric(user_metrics_dict, 'm5_I_coh'),
              get_metric(user_metrics_dict, 'm6_ZLF'),
              get_metric(user_metrics_dict, 'm7_LL'),
              get_metric(user_metrics_dict, 'm19_z_prox'),
              get_metric(user_metrics_dict, 'm20_phi_proxy')))
        
        # physics_metrics (m21-m35) - USER
        cur_reso.execute("""
            INSERT OR REPLACE INTO physics_metrics
            (pair_id, pair_hash, timecode, author,
             m21_phys, m22_phys, m28_phys, m29_phys, m30_phys, m31_phys, m32_phys)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair_id, pair_hash, timestamp, 'user',
              get_metric(user_metrics_dict, 'm21_chaos'),
              get_metric(user_metrics_dict, 'm22_cog_load'),
              get_metric(user_metrics_dict, 'm28_phys_1'),
              get_metric(user_metrics_dict, 'm29_phys_2'),
              get_metric(user_metrics_dict, 'm30_phys_3'),
              get_metric(user_metrics_dict, 'm31_phys_4'),
              get_metric(user_metrics_dict, 'm32_phys_5')))
        
        # andromatik_metrics (m56-m70) - USER
        cur_reso.execute("""
            INSERT OR REPLACE INTO andromatik_metrics
            (pair_id, pair_hash, timecode, author,
             m56_surprise, m57_tokens_soc, m58_tokens_log)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pair_id, pair_hash, timestamp, 'user',
              get_metric(user_metrics_dict, 'm56_surprise'),
              get_metric(user_metrics_dict, 'm57_tokens_soc'),
              get_metric(user_metrics_dict, 'm58_tokens_log')))


if __name__ == "__main__":
    print("="*70)
    print("🚀 EVOKI V3.0 - EXTENDED MVP PIPELINE")
    print("="*70)
    
    pipeline = ExtendedPipeline()
    
    # Initialize sessions
    pipeline.init_sessions()
    
    # Process pairs
    pairs_file = PROJECT_ROOT / "backend/data/test_1000_pairs_2025.json"
    pipeline.process_all(pairs_file)
    
    print("\n✅ Extended pipeline complete!")
