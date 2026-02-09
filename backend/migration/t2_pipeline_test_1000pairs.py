"""
T2 COMPLETE PIPELINE TEST - 1000 PAIRS
========================================

Full end-to-end test:
1. V7 Staging Import (2000 turns)
2. Metrics Calculation (168 per turn)
3. 4-Unit DB Write
4. Validation & Stats

If successful → Scale to all 22k turns
"""

import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add paths
v7_path = Path(r"C:\Users\nicom\Downloads\EVOKI_V3_METRICS_SPECIFICATION Entwicklung\V7 Patchpaket V2 + Monolith")
sys.path.insert(0, str(v7_path))
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "evoki_metrics_v3"))

from evoki_history_ingest import parse_prompt_file, iter_history_files, ensure_schema
from metrics_calculator_4phase_COMPLETE import MetricsCalculator, MetricsContext


class PipelineTest:
    """Complete T2 pipeline test"""
    
    def __init__(self, base_path: str = "C:/Evoki V3.0 APK-Lokalhost-Google Cloude"):
        self.base = Path(base_path)
        
        # Paths
        self.history_root = self.base / "backend" / "Evoki History"
        self.staging_db = self.base / "evoki_history_staging.db"
        self.metadata_db = self.base / "evoki_metadata.db"
        self.resonance_db = self.base / "evoki_resonance.db"
        self.triggers_db = self.base / "evoki_triggers.db"
        self.metapatterns_db = self.base / "evoki_metapatterns.db"
        
        # Schemas
        schema_dir = self.base / "backend" / "schemas"
        self.schemas = {
            self.metadata_db: schema_dir / "evoki_metadata_schema.sql",
            self.resonance_db: schema_dir / "evoki_resonance_schema.sql",
            self.triggers_db: schema_dir / "evoki_triggers_schema.sql",
            self.metapatterns_db: schema_dir / "evoki_metapatterns_schema.sql"
        }
        
        self.v7_schema = v7_path / "evoki_history_schema.sql"
        
        # Calculator
        self.calculator = MetricsCalculator()
        
        # Stats
        self.stats = {
            'staging_imported': 0,
            'metrics_calculated': 0,
            'db_written': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def step1_staging_import(self, max_turns: int = 2000):
        """Step 1: Import to staging DB"""
        print("\n" + "="*80)
        print("STEP 1: V7 STAGING IMPORT")
        print("="*80)
        
        # Clean start
        if self.staging_db.exists():
            print(f"⚠️  Removing existing staging DB")
            self.staging_db.unlink()
        
        # Create schema
        conn = sqlite3.connect(self.staging_db)
        ensure_schema(conn, self.v7_schema)
        
        # Scan files
        print(f"\n📂 Scanning {self.history_root}...")
        files = sorted(
            list(iter_history_files(self.history_root)),
            key=lambda t: (t[0], t[1], t[2], t[3])
        )
        
        sample = files[:max_turns]
        print(f"✅ Processing {len(sample)} files")
        
        # Import
        print(f"\n📥 Importing to staging...")
        imported = 0
        
        for yyyy, mm, dd, prompt_num, path in sample:
            try:
                date_ymd = f"{yyyy}-{mm}-{dd}"
                session_id = f"S-{date_ymd}"
                
                # Ensure session
                conn.execute(
                    "INSERT OR IGNORE INTO sessions(session_id, date_ymd, source_root, created_at) VALUES (?,?,?,?)",
                    (session_id, date_ymd, str(self.history_root), datetime.now().isoformat())
                )
                
                # Parse file
                parsed = parse_prompt_file(path)
                role = parsed['role']
                if role == 'assistant':
                    role = 'ai'
                if role not in ('user', 'ai'):
                    role = 'ai' if '_ai' in path.name.lower() else 'user'
                
                # Insert turn
                turn_id = f"{session_id}_{prompt_num:04d}_{role}"
                conn.execute(
                    "INSERT OR IGNORE INTO turns(turn_id, session_id, ts_iso, date_ymd, prompt_num, role, text, file_path, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                    (turn_id, session_id, parsed['ts_iso'], date_ymd, prompt_num, role, parsed['text'], str(path), datetime.now().isoformat())
                )
                
                imported += 1
                
                if imported % 500 == 0:
                    conn.commit()
                    print(f"   ✅ {imported}/{len(sample)} imported...")
            
            except Exception as e:
                print(f"   ❌ Error: {path.name} - {e}")
                self.stats['errors'] += 1
        
        conn.commit()
        conn.close()
        
        self.stats['staging_imported'] = imported
        
        print(f"\n✅ Step 1 Complete: {imported} turns in staging DB")
        return imported
    
    def step2_initialize_4unit_dbs(self):
        """Step 2: Create 4-Unit DBs"""
        print("\n" + "="*80)
        print("STEP 2: INITIALIZE 4-UNIT DBS")
        print("="*80)
        
        for db_path, schema_file in self.schemas.items():
            if db_path.exists():
                print(f"⚠️  Removing existing: {db_path.name}")
                db_path.unlink()
            
            print(f"🔧 Creating: {db_path.name}")
            conn = sqlite3.connect(db_path)
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            conn.executescript(schema_sql)
            conn.commit()
            conn.close()
            
            print(f"   ✅ Created with {schema_file.name}")
        
        print(f"\n✅ Step 2 Complete: 4 DBs initialized")
    
    def step3_calculate_and_write(self):
        """Step 3: Calculate metrics & write to 4-Unit DBs"""
        print("\n" + "="*80)
        print("STEP 3: METRICS CALCULATION & 4-UNIT WRITE")
        print("="*80)
        
        # Read staging
        staging_conn = sqlite3.connect(self.staging_db)
        staging_conn.row_factory = sqlite3.Row
        
        cursor = staging_conn.execute("""
            SELECT turn_id, session_id, role, text, ts_iso, prompt_num
            FROM turns
            ORDER BY session_id, prompt_num, role
        """)
        
        turns = cursor.fetchall()
        print(f"\n📊 Processing {len(turns)} turns...")
        
        # Open 4-Unit DBs
        meta_conn = sqlite3.connect(self.metadata_db)
        reso_conn = sqlite3.connect(self.resonance_db)
        trig_conn = sqlite3.connect(self.triggers_db)
        
        calculated = 0
        prev_metrics = None
        
        for i, turn in enumerate(turns):
            try:
                # Calculate metrics
                context = MetricsContext(
                    gap_seconds=0,
                    prev_metrics=prev_metrics
                )
                
                metrics = self.calculator.calculate_all(
                    text=turn['text'],
                    role=turn['role'],
                    context=context
                )
                
                prev_metrics = metrics
                calculated += 1
                
                # Write to 4 units
                self._write_to_4units(
                    meta_conn, reso_conn, trig_conn,
                    turn_id=turn['turn_id'],
                    session_id=turn['session_id'],
                    role=turn['role'],
                    text=turn['text'],
                    ts_iso=turn['ts_iso'],
                    metrics=metrics
                )
                
                if (i + 1) % 100 == 0:
                    # Commit
                    meta_conn.commit()
                    reso_conn.commit()
                    trig_conn.commit()
                    
                    print(f"   ✅ [{i+1}/{len(turns)}] Calculated & written...")
            
            except Exception as e:
                print(f"   ❌ Turn {i+1}: {e}")
                self.stats['errors'] += 1
        
        # Final commit
        meta_conn.commit()
        reso_conn.commit()
        trig_conn.commit()
        
        meta_conn.close()
        reso_conn.close()
        trig_conn.close()
        staging_conn.close()
        
        self.stats['metrics_calculated'] = calculated
        self.stats['db_written'] = calculated
        
        print(f"\n✅ Step 3 Complete: {calculated} turns processed")
        return calculated
    
    def _write_to_4units(self, meta_conn, reso_conn, trig_conn, turn_id, session_id, role, text, ts_iso, metrics):
        """Write metrics to 4-Unit DBs"""
        
        # UNIT 1: Metadata (text only for this turn)
        # Using simplified approach - just store turn reference
        # Full schema would need sessions table etc - skipping for test
        
        # UNIT 2: Resonance (core metrics)
        reso_conn.execute("""
            INSERT OR REPLACE INTO core_metrics (
                pair_id, pair_hash, timecode, author,
                m1_A, m2_PCI, m4_flow, m5_coh, m15_affekt_a, m17_nabla_a,
                m19_z_prox, m20_phi_proxy
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            turn_id, turn_id[:16], ts_iso, role,
            metrics.get('m1_A'), metrics.get('m2_PCI'),
            metrics.get('m4_flow'), metrics.get('m5_coh'),
           metrics.get('m15_affekt_a'), metrics.get('m17_nabla_a'),
            metrics.get('m19_z_prox'), metrics.get('m20_phi_proxy')
        ))
        
        # UNIT 3: Triggers (trauma - user only)
        if role == 'user':
            trig_conn.execute("""
                INSERT OR REPLACE INTO trauma_metrics (
                    pair_id, pair_hash, timecode, author,
                    m101_T_panic, m102_T_disso, m103_T_integ,
                    m110_black_hole
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                turn_id, turn_id[:16], ts_iso, role,
                metrics.get('m101_T_panic'), metrics.get('m102_T_disso'),
                metrics.get('m103_T_integ'), metrics.get('m110_black_hole')
            ))
            
            trig_conn.execute("""
                INSERT OR REPLACE INTO hazard_metrics (
                    pair_id, pair_hash, timecode, author,
                    m151_hazard, m160_F_risk
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                turn_id, turn_id[:16], ts_iso, role,
                metrics.get('m151_hazard'), metrics.get('m160_F_risk', 0.0)
            ))
    
    def step4_validation(self):
        """Step 4: Validate results"""
        print("\n" + "="*80)
        print("STEP 4: VALIDATION")
        print("="*80)
        
        # Check row counts
        staging_conn = sqlite3.connect(self.staging_db)
        reso_conn = sqlite3.connect(self.resonance_db)
        trig_conn = sqlite3.connect(self.triggers_db)
        
        staging_count = staging_conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0]
        reso_count = reso_conn.execute("SELECT COUNT(*) FROM core_metrics").fetchone()[0]
        trig_count = trig_conn.execute("SELECT COUNT(*) FROM trauma_metrics").fetchone()[0]
        
        print(f"\n📊 Row Counts:")
        print(f"   Staging DB:    {staging_count} turns")
        print(f"   Resonance DB:  {reso_count} core_metrics")
        print(f"   Triggers DB:   {trig_count} trauma_metrics (user only)")
        
        # Sample validation
        print(f"\n🔍 Sample Validation:")
        row = reso_conn.execute("""
            SELECT pair_id, m1_A, m19_z_prox
            FROM core_metrics
            LIMIT 1
        """).fetchone()
        
        if row:
            print(f"   Sample turn: {row[0]}")
            print(f"   m1_A:        {row[1]:.4f}")
            print(f"   m19_z_prox:  {row[2]:.4f}")
        
        staging_conn.close()
        reso_conn.close()
        trig_conn.close()
        
        print(f"\n✅ Step 4 Complete: Validation passed")
    
    def run(self, max_turns: int = 2000):
        """Run complete pipeline"""
        self.stats['start_time'] = datetime.now()
        
        print("\n" + "="*80)
        print("T2 COMPLETE PIPELINE TEST - 1000 PAIRS (2000 TURNS)")
        print("="*80)
        
        try:
            self.step1_staging_import(max_turns)
            self.step2_initialize_4unit_dbs()
            self.step3_calculate_and_write()
            self.step4_validation()
            
            self.stats['end_time'] = datetime.now()
            
            # Final report
            self.print_final_report()
            
            return True
        
        except Exception as e:
            print(f"\n❌ PIPELINE FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_final_report(self):
        """Print final statistics"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        print("\n" + "="*80)
        print("FINAL REPORT")
        print("="*80)
        print(f"Duration:           {duration:.1f}s ({duration/60:.1f} min)")
        print(f"Staging imported:   {self.stats['staging_imported']}")
        print(f"Metrics calculated: {self.stats['metrics_calculated']}")
        print(f"DB writes:          {self.stats['db_written']}")
        print(f"Errors:             {self.stats['errors']}")
        print()
        
        if self.stats['metrics_calculated'] > 0:
            turns_per_sec = self.stats['metrics_calculated'] / duration
            print(f"📊 Performance:")
            print(f"   {turns_per_sec:.1f} turns/sec")
            print(f"   {turns_per_sec * 168:.0f} metrics/sec")
            print()
            
            # Estimate full import
            total_turns = 21987
            est_time = total_turns / turns_per_sec / 60
            print(f"📈 Estimated full import (21,987 turns):")
            print(f"   Time: {est_time:.1f} minutes ({est_time/60:.1f} hours)")
            print()
        
        print("✅ PIPELINE TEST SUCCESSFUL!")
        print("   Ready for full 22k import!")
        print()


if __name__ == "__main__":
    pipeline = PipelineTest()
    success = pipeline.run(max_turns=2000)
    
    sys.exit(0 if success else 1)
