"""
T2: HISTORY INGESTION PIPELINE
================================

Imports conversation history into 4-Unit Database Architecture:
- Unit 1: evoki_metadata.db (raw text)
- Unit 2: evoki_resonance.db (core metrics m1-m100)
- Unit 3: evoki_triggers.db (trauma m101-m115, hazard)
- Unit 4: evoki_metapatterns.db (meta-cognition m116-m168)

Converts PAIR-based data → TURN-based model for calculator compatibility.
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys

# Add calculator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend" / "core" / "evoki_metrics_v3"))

from metrics_calculator_4phase_COMPLETE import MetricsCalculator, MetricsContext


class HistoryImporter:
    """Imports conversation history into 4-Unit DB architecture"""
    
    def __init__(self, db_base_path: str = "C:/Evoki V3.0 APK-Lokalhost-Google Cloude"):
        self.db_base_path = Path(db_base_path)
        
        # Database paths
        self.metadata_db = self.db_base_path / "evoki_metadata.db"
        self.resonance_db = self.db_base_path / "evoki_resonance.db"
        self.triggers_db = self.db_base_path / "evoki_triggers.db"
        self.metapatterns_db = self.db_base_path / "evoki_metapatterns.db"
        
        # Calculator
        self.calculator = MetricsCalculator()
        
        # Import log
        self.import_log = []
    
    def initialize_databases(self):
        """Create database schemas from SQL files"""
        schema_dir = self.db_base_path / "backend" / "schemas"
        
        schemas = {
            self.metadata_db: schema_dir / "evoki_metadata_schema.sql",
            self.resonance_db: schema_dir / "evoki_resonance_schema.sql",
            self.triggers_db: schema_dir / "evoki_triggers_schema.sql",
            self.metapatterns_db: schema_dir / "evoki_metapatterns_schema.sql"
        }
        
        for db_path, schema_file in schemas.items():
            if db_path.exists():
                print(f"⚠️  DB exists: {db_path.name}")
                response = input(f"   Drop and recreate? (yes/no): ")
                if response.lower() != 'yes':
                    continue
                db_path.unlink()
            
            print(f"🔧 Creating: {db_path.name}")
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            conn = sqlite3.connect(db_path)
            conn.executescript(schema_sql)
            conn.commit()
            conn.close()
            
            print(f"   ✅ Created with schema from {schema_file.name}")
    
    def find_history_files(self, history_dir: str) -> List[Path]:
        """Find all conversation history files"""
        history_path = Path(history_dir)
        
        if not history_path.exists():
            raise FileNotFoundError(f"History directory not found: {history_dir}")
        
        # Look for JSON files (adjust pattern as needed)
        json_files = list(history_path.rglob("*.json"))
        
        print(f"📂 Found {len(json_files)} JSON files in {history_dir}")
        
        return json_files
    
    def parse_history_file(self, file_path: Path) -> Optional[Dict]:
        """Parse a single history file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Adjust parsing based on your file format
            # This is a placeholder - update based on actual format
            return data
        
        except Exception as e:
            print(f"❌ Error parsing {file_path.name}: {e}")
            return None
    
    def generate_pair_id(self, session_id: str, pair_index: int) -> str:
        """Generate unique pair_id"""
        return f"{session_id}_{pair_index:04d}"
    
    def generate_pair_hash(self, user_text: str, ai_text: str) -> str:
        """Generate hash for pair"""
        combined = f"{user_text}||{ai_text}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def import_pair(
        self,
        session_id: str,
        pair_index: int,
        user_text: str,
        ai_text: str,
        user_ts: str,
        ai_ts: str,
        conversation_id: str,
        gap_seconds: int = 0
    ) -> Tuple[str, Dict, Dict]:
        """
        Import one user+AI pair
        
        Returns:
            (pair_id, user_metrics, ai_metrics)
        """
        
        # Generate IDs
        pair_id = self.generate_pair_id(session_id, pair_index)
        pair_hash = self.generate_pair_hash(user_text, ai_text)
        
        # === UNIT 1: METADATA (Text Storage) ===
        conn_meta = sqlite3.connect(self.metadata_db)
        cur_meta = conn_meta.cursor()
        
        # Ensure session exists
        cur_meta.execute("""
            INSERT OR IGNORE INTO sessions (session_id, conversation_id, date_ymd, total_pairs)
            VALUES (?, ?, ?, 0)
        """, (session_id, conversation_id, datetime.now().strftime("%Y-%m-%d")))
        
        # Insert pair
        cur_meta.execute("""
            INSERT INTO prompt_pairs (
                pair_id, session_id, pair_index,
                user_text, user_ts, ai_text, ai_ts,
                pair_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair_id, session_id, pair_index, user_text, user_ts, ai_text, ai_ts, pair_hash))
        
        conn_meta.commit()
        conn_meta.close()
        
        # === CALCULATE METRICS ===
        
        # User metrics
        user_context = MetricsContext(gap_seconds=gap_seconds)
        user_metrics = self.calculator.calculate_all(
            text=user_text,
            role="user",
            context=user_context
        )
        
        # AI metrics (needs prev from user)
        ai_context = MetricsContext(
            gap_seconds=0,  # AI response immediate
            prev_metrics=user_metrics
        )
        ai_metrics = self.calculator.calculate_all(
            text=ai_text,
            role="ai",
            context=ai_context
        )
        
        # === UNIT 2: RESONANCE (Core Metrics) ===
        self._insert_resonance_metrics(pair_id, pair_hash, user_ts, "user", user_metrics)
        self._insert_resonance_metrics(pair_id, pair_hash, ai_ts, "ai", ai_metrics)
        
        # === UNIT 3: TRIGGERS (Trauma/Hazard) ===
        self._insert_trigger_metrics(pair_id, pair_hash, user_ts, "user", user_metrics)
        self._insert_trigger_metrics(pair_id, pair_hash, ai_ts, "ai", ai_metrics)
        
        # === UNIT 4: METAPATTERNS (Meta-cognition) ===
        self._insert_metapattern_metrics(pair_id, pair_hash, user_ts, "user", user_metrics)
        self._insert_metapattern_metrics(pair_id, pair_hash, ai_ts, "ai", ai_metrics)
        
        return (pair_id, user_metrics, ai_metrics)
    
    def _insert_resonance_metrics(self, pair_id: str, pair_hash: str, timecode: str, author: str, metrics: Dict):
        """Insert into evoki_resonance.db"""
        conn = sqlite3.connect(self.resonance_db)
        cur = conn.cursor()
        
        # Core metrics (m1-m20)
        cur.execute("""
            INSERT INTO core_metrics (
                pair_id, pair_hash, timecode, author,
                m1_A, m2_PCI, m3_gen_index, m4_flow, m5_coh, m6_ZLF, m7_LL,
                m8_x_exist, m9_b_past, m10_angstrom, m11_gap_s, m12_lex_hit,
                m13_base_score, m14_base_stability, m15_affekt_a, m16_pci_alias,
                m17_nabla_a, m18_s_entropy, m19_z_prox, m20_phi_proxy
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pair_id, pair_hash, timecode, author,
            metrics.get('m1_A'), metrics.get('m2_PCI'), metrics.get('m3_gen_index'),
            metrics.get('m4_flow'), metrics.get('m5_coh'), metrics.get('m6_ZLF'),
            metrics.get('m7_LL'), metrics.get('m8_x_exist'), metrics.get('m9_b_past'),
            metrics.get('m10_angstrom'), metrics.get('m11_gap_s'), metrics.get('m12_lex_hit'),
            metrics.get('m13_base_score'), metrics.get('m14_base_stability'),
            metrics.get('m15_affekt_a'), metrics.get('m16_pci_alias'),
            metrics.get('m17_nabla_a'), metrics.get('m18_s_entropy'),
            metrics.get('m19_z_prox'), metrics.get('m20_phi_proxy')
        ))
        
        # Evolution metrics (m71-m100) - simplified, add more as needed
        cur.execute("""
            INSERT INTO evolution_metrics (
                pair_id, pair_hash, timecode, author,
                m71_ev_arousal, m74_valence, m100_causal
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            pair_id, pair_hash, timecode, author,
            metrics.get('m71_ev_arousal'), metrics.get('m74_valence'),
            metrics.get('m100_causal')
        ))
        
        conn.commit()
        conn.close()
    
    def _insert_trigger_metrics(self, pair_id: str, pair_hash: str, timecode: str, author: str, metrics: Dict):
        """Insert into evoki_triggers.db (user only)"""
        if author != "user":
            return  # Trauma metrics only for user
        
        conn = sqlite3.connect(self.triggers_db)
        cur = conn.cursor()
        
        # Trauma metrics (m101-m115)
        cur.execute("""
            INSERT INTO trauma_metrics (
                pair_id, pair_hash, timecode, author,
                m101_T_panic, m102_T_disso, m103_T_integ, m104_T_shock,
                m106_T_numb, m107_T_hurt, m108_T_fear, m109_T_rage,
                m110_black_hole
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pair_id, pair_hash, timecode, author,
            metrics.get('m101_T_panic'), metrics.get('m102_T_disso'),
            metrics.get('m103_T_integ'), metrics.get('m104_T_shock'),
            metrics.get('m106_T_numb'), metrics.get('m107_T_hurt'),
            metrics.get('m108_T_fear'), metrics.get('m109_T_rage'),
            metrics.get('m110_black_hole')
        ))
        
        # Hazard log
        cur.execute("""
            INSERT INTO hazard_log (
                pair_id, pair_hash, timecode, author,
                m151_hazard, m161_commit
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            pair_id, pair_hash, timecode, author,
            metrics.get('m151_hazard'), metrics.get('m161_commit')
        ))
        
        conn.commit()
        conn.close()
    
    def _insert_metapattern_metrics(self, pair_id: str, pair_hash: str, timecode: str, author: str, metrics: Dict):
        """Insert into evoki_metapatterns.db"""
        # Placeholder - implement when metacog metrics are ready
        pass
    
    def import_conversation(self, conversation_data: Dict) -> int:
        """Import entire conversation"""
        session_id = conversation_data.get('session_id', f"session_{datetime.now().timestamp()}")
        conversation_id = conversation_data.get('conversation_id', session_id)
        pairs = conversation_data.get('pairs', [])
        
        print(f"\n📥 Importing conversation: {conversation_id}")
        print(f"   Pairs: {len(pairs)}")
        
        imported_count = 0
        
        for idx, pair in enumerate(pairs):
            try:
                pair_id, user_m, ai_m = self.import_pair(
                    session_id=session_id,
                    pair_index=idx,
                    user_text=pair['user_text'],
                    ai_text=pair['ai_text'],
                    user_ts=pair['user_ts'],
                    ai_ts=pair['ai_ts'],
                    conversation_id=conversation_id,
                    gap_seconds=pair.get('gap_seconds', 0)
                )
                
                imported_count += 1
                
                # Log
                self.import_log.append({
                    'pair_id': pair_id,
                    'user_hazard': user_m.get('m151_hazard'),
                    'user_commit': user_m.get('m161_commit'),
                    'timestamp': datetime.now().isoformat()
                })
                
                if (idx + 1) % 10 == 0:
                    print(f"   ✅ Imported {idx + 1}/{len(pairs)} pairs...")
            
            except Exception as e:
                print(f"   ❌ Error importing pair {idx}: {e}")
                continue
        
        print(f"   ✅ Complete: {imported_count}/{len(pairs)} pairs imported")
        
        return imported_count
    
    def save_import_log(self, log_path: str = "import_log.jsonl"):
        """Save import log"""
        with open(log_path, 'w', encoding='utf-8') as f:
            for entry in self.import_log:
                f.write(json.dumps(entry) + '\n')
        
        print(f"\n📝 Import log saved: {log_path}")


def main():
    print("="*80)
    print("T2: HISTORY INGESTION PIPELINE")
    print("="*80)
    print()
    
    importer = HistoryImporter()
    
    # Step 1: Initialize databases
    print("🔧 Step 1: Initialize databases")
    importer.initialize_databases()
    print()
    
    # Step 2: Find history files
    print("📂 Step 2: Find history files")
    history_dir = input("   Enter history directory path: ").strip()
    
    if not history_dir:
        history_dir = "C:/Users/nicom/Downloads/history"  # Default
    
    try:
        files = importer.find_history_files(history_dir)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    print()
    
    # Step 3: Import conversations
    print("📥 Step 3: Import conversations")
    
    # TODO: Parse actual files - this is placeholder
    print("⚠️  File parsing not yet implemented")
    print("   Create conversation_data dict manually for now")
    
    # Example manual import:
    # conversation_data = {
    #     'session_id': 'test-session',
    #     'conversation_id': 'test-conv',
    #     'pairs': [
    #         {
    #             'user_text': 'Hallo',
    #             'ai_text': 'Hallo! Wie kann ich helfen?',
    #             'user_ts': '2026-02-08T00:00:00',
    #             'ai_ts': '2026-02-08T00:00:01',
    #             'gap_seconds': 0
    #         }
    #     ]
    # }
    # importer.import_conversation(conversation_data)
    
    # Step 4: Save log
    importer.save_import_log()
    
    print()
    print("="*80)
    print("✅ T2 IMPORT COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
