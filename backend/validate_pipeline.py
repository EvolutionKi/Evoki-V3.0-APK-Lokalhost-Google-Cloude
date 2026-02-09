#!/usr/bin/env python3
"""
PIPELINE VALIDATION - Check what was written to DBs
"""

import sqlite3
import json
from pathlib import Path

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")

DB_V3_CORE = PROJECT_ROOT / "backend/data/databases/evoki_v3_core.db"
DB_METADATA = PROJECT_ROOT / "evoki_metadata.db"
DB_RESONANCE = PROJECT_ROOT / "evoki_resonance.db"

def validate_db(db_path: Path, name: str):
    """Validate a database"""
    print(f"\n{'='*70}")
    print(f"📊 {name}: {db_path.name}")
    print(f"{'='*70}")
    
    if not db_path.exists():
        print(f"❌ Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cur.fetchall()]
    
    print(f"\n📋 Tables ({len(tables)}):")
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"   • {table}: {count} rows")
        
        # Sample first row
        if count > 0:
            cur.execute(f"SELECT * FROM {table} LIMIT 1")
            columns = [desc[0] for desc in cur.description]
            row = cur.fetchone()
            print(f"     Columns: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}")
            
            # Check for metrics in core tables
            if 'metrics' in table.lower() or table == 'core_metrics':
                # Get metric columns
                metric_cols = [c for c in columns if c.startswith('m') and c[1:].split('_')[0].isdigit()]
                if metric_cols:
                    print(f"     📈 Metrics found: {len(metric_cols)}")
                    # Sample values
                    cur.execute(f"SELECT {', '.join(metric_cols[:5])} FROM {table} LIMIT 5")
                    sample = cur.fetchall()
                    for i, s in enumerate(sample[:3], 1):
                        non_zero = sum(1 for v in s if v and v != 0.0)
                        print(f"        Row {i}: {non_zero}/{len(s)} non-zero metrics")
    
    conn.close()

def check_metrics_json():
    """Check if JSON metrics were written correctly"""
    print(f"\n{'='*70}")
    print(f"📊 METRICS JSON CHECK (v3_core.db)")
    print(f"{'='*70}")
    
    conn = sqlite3.connect(DB_V3_CORE)
    cur = conn.cursor()
    
    # Check if metrics_full has JSON
    cur.execute("SELECT user_metrics_json, ai_metrics_json FROM metrics_full LIMIT 3")
    rows = cur.fetchall()
    
    for i, (user_json, ai_json) in enumerate(rows, 1):
        print(f"\n📄 Pair {i}:")
        if user_json:
            user_metrics = json.loads(user_json)
            print(f"   USER: {len(user_metrics)} metrics")
            non_zero_user = sum(1 for v in user_metrics.values() if v != 0.0)
            print(f"   Non-zero: {non_zero_user}/{len(user_metrics)}")
            # Show sample
            sample = list(user_metrics.items())[:5]
            for k, v in sample:
                print(f"      {k}: {v:.4f}" if isinstance(v, float) else f"      {k}: {v}")
        
        if ai_json:
            ai_metrics = json.loads(ai_json)
            print(f"   AI: {len(ai_metrics)} metrics")
            non_zero_ai = sum(1 for v in ai_metrics.values() if v != 0.0)
            print(f"   Non-zero: {non_zero_ai}/{len(ai_metrics)}")
    
    conn.close()

if __name__ == "__main__":
    print("\n🔍 EVOKI V3.0 PIPELINE VALIDATION")
    print("="*70)
    
    validate_db(DB_V3_CORE, "EVOKI V3.0 CORE")
    validate_db(DB_METADATA, "METADATA")
    validate_db(DB_RESONANCE, "RESONANCE")
    
    check_metrics_json()
    
    print(f"\n{'='*70}")
    print("✅ Validation complete!")
    print(f"{'='*70}\n")
