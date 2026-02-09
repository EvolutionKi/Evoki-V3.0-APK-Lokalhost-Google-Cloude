#!/usr/bin/env python3
"""
T2: HISTORY INGESTION - Populate Metrics DB with 1000 samples

Loads prompts from text_lookup DB, calculates metrics, stores in evoki_v3_metrics.db
"""

import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.core.evoki_metrics_v3.calculator_spec_A_PHYS_V11 import (
    compute_m1_A, compute_m2_PCI, compute_m4_flow, compute_m5_coh,
    compute_m6_ZLF, compute_m7_LL, compute_m19_z_prox,
    compute_m101_t_panic, compute_m102_t_disso, compute_m103_t_integ,
    compute_m110_black_hole, compute_m21_chaos, compute_m18_s_entropy,
    tokenize
)

# ==============================================================================
# CONFIGURATION
# ==============================================================================

SOURCE_DB = r"C:\Users\nicom\Documents\evoki\evoki_pipeline\metric_chunks_test\text_index.db"
TARGET_DB = r"C:\Evoki V3.0 APK-Lokalhost-Google Cloude\evoki_v3_metrics.db"
SAMPLE_SIZE = 1000

# ==============================================================================
# DATABASE SETUP
# ==============================================================================

def create_metrics_table(conn):
    """Create metrics table if it doesn't exist"""
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prompt_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_text TEXT NOT NULL,
            timestamp REAL DEFAULT (julianday('now')),
            
            -- CORE METRICS
            m1_A REAL,
            m2_PCI REAL,
            m4_flow REAL,
            m5_coh REAL,
            m6_ZLF REAL,
            m7_LL REAL,
            m19_z_prox REAL,
            
            -- TRAUMA
            m101_t_panic REAL,
            m102_t_disso REAL,
            m103_t_integ REAL,
            m110_black_hole REAL,
            
            -- PHYSICS
            m21_chaos REAL,
            m18_s_entropy REAL,
            
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Index for fast lookups
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_prompt_metrics_timestamp 
        ON prompt_metrics(timestamp)
    """)
    
    conn.commit()
    print("✅ Metrics table created/verified")

# ==============================================================================
# METRIC CALCULATION
# ==============================================================================

def calculate_metrics(text: str, prev_text: str = "") -> Dict[str, Any]:
    """
    Calculate core metrics for a text sample
    
    Returns dict with metric values
    """
    
    # Tokenize
    tokens = tokenize(text)
    
    # CORE
    m1_A = compute_m1_A(text)
    m2_PCI = compute_m2_PCI(text, prev_context=prev_text)
    m4_flow = compute_m4_flow(text)
    m5_coh = compute_m5_coh(text)
    m6_ZLF = compute_m6_ZLF(m4_flow, m5_coh)
    m7_LL = compute_m7_LL(rep_same=0.0, flow=m4_flow)  # No prev for now
    
    # TRAUMA
    m101_t_panic = compute_m101_t_panic(text)
    m102_t_disso = compute_m102_t_disso(text)
    m103_t_integ = compute_m103_t_integ(text)
    
    # PHYSICS
    m18_s_entropy = compute_m18_s_entropy(tokens)
    m21_chaos = compute_m21_chaos(m18_s_entropy)
    
    # CRITICAL
    m19_z_prox = compute_m19_z_prox(
        m1_A_lexical=m1_A,
        m15_A_structural=m1_A,  # Simplified for now
        LL=m7_LL,
        text=text,
        t_panic=m101_t_panic
    )
    
    m110_black_hole = compute_m110_black_hole(
        chaos=m21_chaos,
        effective_A=m1_A,
        LL=m7_LL
    )
    
    return {
        "m1_A": m1_A,
        "m2_PCI": m2_PCI,
        "m4_flow": m4_flow,
        "m5_coh": m5_coh,
        "m6_ZLF": m6_ZLF,
        "m7_LL": m7_LL,
        "m19_z_prox": m19_z_prox,
        "m101_t_panic": m101_t_panic,
        "m102_t_disso": m102_t_disso,
        "m103_t_integ": m103_t_integ,
        "m110_black_hole": m110_black_hole,
        "m21_chaos": m21_chaos,
        "m18_s_entropy": m18_s_entropy,
    }

# ==============================================================================
# INGESTION
# ==============================================================================

def load_samples(source_db: str, limit: int = 1000) -> List[str]:
    """Load sample prompts from source DB"""
    
    print(f"\n📂 Loading samples from: {source_db}")
    
    conn = sqlite3.connect(source_db)
    cursor = conn.cursor()
    
    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"   Tables found: {[t[0] for t in tables]}")
    
    # Try to find text column
    # Common names: text, prompt, user_text, content
    samples = []
    
    for table_name, in tables:
        try:
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Find text column
            text_col = None
            for col in columns:
                if col.lower() in ['text', 'prompt', 'user_text', 'content', 'message']:
                    text_col = col
                    break
            
            if text_col:
                print(f"   Found text column '{text_col}' in table '{table_name}'")
                
                # Sample rows
                cursor.execute(f"""
                    SELECT {text_col} FROM {table_name} 
                    WHERE {text_col} IS NOT NULL 
                    AND length({text_col}) > 10
                    ORDER BY RANDOM() 
                    LIMIT {limit}
                """)
                
                rows = cursor.fetchall()
                samples.extend([row[0] for row in rows if row[0]])
                
                if len(samples) >= limit:
                    break
        except Exception as e:
            print(f"   ⚠️  Error reading table {table_name}: {e}")
            continue
    
    conn.close()
    
    print(f"   ✅ Loaded {len(samples)} samples")
    return samples[:limit]

def ingest_samples(samples: List[str], target_db: str):
    """Calculate metrics and store in target DB"""
    
    print(f"\n⚙️  Processing {len(samples)} samples...")
    
    conn = sqlite3.connect(target_db)
    create_metrics_table(conn)
    
    processed = 0
    errors = 0
    
    prev_text = ""
    
    for i, text in enumerate(samples):
        try:
            # Calculate metrics
            metrics = calculate_metrics(text, prev_text)
            
            # Insert into DB
            conn.execute("""
                INSERT INTO prompt_metrics (
                    prompt_text,
                    m1_A, m2_PCI, m4_flow, m5_coh, m6_ZLF, m7_LL, m19_z_prox,
                    m101_t_panic, m102_t_disso, m103_t_integ, m110_black_hole,
                    m21_chaos, m18_s_entropy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                text,
                metrics['m1_A'], metrics['m2_PCI'], metrics['m4_flow'],
                metrics['m5_coh'], metrics['m6_ZLF'], metrics['m7_LL'],
                metrics['m19_z_prox'], metrics['m101_t_panic'],
                metrics['m102_t_disso'], metrics['m103_t_integ'],
                metrics['m110_black_hole'], metrics['m21_chaos'],
                metrics['m18_s_entropy']
            ))
            
            processed += 1
            prev_text = text
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"   Processed: {i + 1}/{len(samples)}")
                conn.commit()
                
        except Exception as e:
            print(f"   ⚠️  Error processing sample {i}: {e}")
            errors += 1
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ INGESTION COMPLETE!")
    print(f"   Processed: {processed}")
    print(f"   Errors: {errors}")
    
    return processed, errors

# ==============================================================================
# VALIDATION
# ==============================================================================

def validate_ingestion(target_db: str):
    """Validate ingested data"""
    
    print(f"\n🔍 VALIDATION...")
    
    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()
    
    # Count rows
    cursor.execute("SELECT COUNT(*) FROM prompt_metrics")
    count = cursor.fetchone()[0]
    print(f"   Total rows: {count}")
    
    # Sample statistics
    cursor.execute("""
        SELECT 
            AVG(m1_A) as avg_A,
            AVG(m19_z_prox) as avg_z_prox,
            AVG(m101_t_panic) as avg_panic,
            MAX(m19_z_prox) as max_z_prox
        FROM prompt_metrics
    """)
    
    stats = cursor.fetchone()
    print(f"   Avg A: {stats[0]:.3f}")
    print(f"   Avg z_prox: {stats[1]:.3f}")
    print(f"   Avg panic: {stats[2]:.3f}")
    print(f"   Max z_prox: {stats[3]:.3f}")
    
    # Check for critical values
    cursor.execute("""
        SELECT COUNT(*) FROM prompt_metrics 
        WHERE m19_z_prox > 0.65
    """)
    critical_count = cursor.fetchone()[0]
    print(f"   Critical (z_prox > 0.65): {critical_count}")
    
    conn.close()
    
    return count

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=" * 80)
    print("T2: HISTORY INGESTION - Evoki V3.0")
    print("=" * 80)
    
    # Check source DB exists
    if not Path(SOURCE_DB).exists():
        print(f"❌ Source DB not found: {SOURCE_DB}")
        print("   Please update SOURCE_DB path!")
        return 1
    
    # Load samples
    samples = load_samples(SOURCE_DB, limit=SAMPLE_SIZE)
    
    if not samples:
        print("❌ No samples loaded!")
        return 1
    
    # Ingest
    processed, errors = ingest_samples(samples, TARGET_DB)
    
    # Validate
    count = validate_ingestion(TARGET_DB)
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "source_db": SOURCE_DB,
        "target_db": TARGET_DB,
        "samples_loaded": len(samples),
        "samples_processed": processed,
        "errors": errors,
        "final_count": count,
        "success": count >= SAMPLE_SIZE * 0.95  # 95% success rate
    }
    
    # Write report
    report_path = Path(__file__).parent / "HISTORY_INGEST_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"\n📊 Report written to: {report_path}")
    
    if report["success"]:
        print("\n✅ T2 INGESTION: SUCCESS!")
        return 0
    else:
        print("\n⚠️  T2 INGESTION: PARTIAL SUCCESS")
        return 1

if __name__ == "__main__":
    sys.exit(main())
