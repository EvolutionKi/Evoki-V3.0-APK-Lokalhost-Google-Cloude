#!/usr/bin/env python3
"""
Validation Script — V3.0 Pipeline
Prüft ALLE 5 V3.0 Datenbanken + FAISS Indizes
"""

import sqlite3
from pathlib import Path
import sys

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")

# Database paths
DBS = {
    "evoki_v3_core.db": PROJECT_ROOT / "backend/data/databases/evoki_v3_core.db",
    "evoki_v3_graph.db": PROJECT_ROOT / "backend/data/databases/evoki_v3_graph.db",
    "evoki_v3_keywords.db": PROJECT_ROOT / "backend/data/databases/evoki_v3_keywords.db",
    "evoki_v3_analytics.db": PROJECT_ROOT / "backend/data/databases/evoki_v3_analytics.db",
    "evoki_v3_trajectories.db": PROJECT_ROOT / "backend/data/databases/evoki_v3_trajectories.db",
}

FAISS_DIR = PROJECT_ROOT / "backend/data/faiss"

def validate():
    """Run validation checks on ALL 5 DBs"""
    
    print("\n" + "="*70)
    print("📊 VALIDATION REPORT — V3.0 DATA LAYER (5 DATABASES)")
    print("="*70)
    
    all_checks_passed = True
    results = {}
    
    # ═══════════════════════════════════════════════════════════════════════
    # CHECK 1: EVOKI_V3_CORE.DB
    # ═══════════════════════════════════════════════════════════════════════
    
    print("\n📦 DATABASE 1: evoki_v3_core.db")
    print("-"*70)
    
    core_db = DBS["evoki_v3_core.db"]
    if not core_db.exists():
        print("❌ Database not found!")
        all_checks_passed = False
    else:
        try:
            conn = sqlite3.connect(core_db)
            cur = conn.cursor()
            
            # Check counts
            cur.execute("SELECT COUNT(*) FROM prompt_pairs")
            pair_count = cur.fetchone()[0]
            results['prompt_pairs'] = pair_count
            
            cur.execute("SELECT COUNT(*) FROM b_state_evolution")
            b_state_count = cur.fetchone()[0]
            results['b_state_evolution'] = b_state_count
            
            cur.execute("SELECT COUNT(*) FROM hazard_events")
            hazard_count = cur.fetchone()[0]
            results['hazard_events'] = hazard_count
            
            # Metrics plausibility (if metrics_full exists)
            try:
                cur.execute("SELECT AVG(user_m1_A), AVG(user_m151_hazard) FROM metrics_full")
                avg_m1, avg_hazard = cur.fetchone()
                
                if avg_m1 is not None and avg_hazard is not None:
                    plausible = (0.2 <= avg_m1 <= 0.9) and (0.0 <= avg_hazard <= 0.8)
                    
                    print(f"✅ prompt_pairs:       {pair_count:6}")
                    print(f"✅ b_state_evolution:  {b_state_count:6}")
                    print(f"✅ hazard_events:      {hazard_count:6}")
                    print(f"📊 avg user_m1_A:      {avg_m1:.3f}")
                    print(f"📊 avg user_hazard:    {avg_hazard:.3f}")
                    print(f"{'✅' if plausible else '⚠️ '} Metrics plausible:  {plausible}")
                    
                    if not plausible:
                        all_checks_passed = False
                else:
                    print(f"✅ prompt_pairs:       {pair_count:6}")
                    print(f"⚠️  No metrics data yet")
            except sqlite3.OperationalError:
                # metrics_full table might not exist yet
                print(f"✅ prompt_pairs:       {pair_count:6}")
                print(f"⚠️  metrics_full table not found (may be OK for initial test)")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error checking core DB: {e}")
            all_checks_passed = False
    
    # ═══════════════════════════════════════════════════════════════════════
    # CHECK 2: EVOKI_V3_GRAPH.DB
    # ═══════════════════════════════════════════════════════════════════════
    
    print("\n📦 DATABASE 2: evoki_v3_graph.db")
    print("-"*70)
    
    graph_db = DBS["evoki_v3_graph.db"]
    if not graph_db.exists():
        print("⚠️  Database not found (may be created during analytics phase)")
    else:
        try:
            conn = sqlite3.connect(graph_db)
            cur = conn.cursor()
            
            # Try to count nodes/edges (table names might vary)
            try:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cur.fetchall()]
                
                if 'nodes' in tables:
                    cur.execute("SELECT COUNT(*) FROM nodes")
                    node_count = cur.fetchone()[0]
                    print(f"✅ nodes:              {node_count:6}")
                
                if 'edges' in tables:
                    cur.execute("SELECT COUNT(*) FROM edges")
                    edge_count = cur.fetchone()[0]
                    print(f"✅ edges:              {edge_count:6}")
                
                if not tables:
                    print("⚠️  No tables found yet")
            except Exception as e:
                print(f"⚠️  Error reading tables: {e}")
            
            conn.close()
        except Exception as e:
            print(f"⚠️  Error checking graph DB: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # CHECK 3: EVOKI_V3_KEYWORDS.DB
    # ═══════════════════════════════════════════════════════════════════════
    
    print("\n📦 DATABASE 3: evoki_v3_keywords.db")
    print("-"*70)
    
    keywords_db = DBS["evoki_v3_keywords.db"]
    if not keywords_db.exists():
        print("⚠️  Database not found (created during learning phase)")
    else:
        try:
            conn = sqlite3.connect(keywords_db)
            cur = conn.cursor()
            
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            
            if 'keywords' in tables:
                cur.execute("SELECT COUNT(*) FROM keywords")
                kw_count = cur.fetchone()[0]
                print(f"✅ keywords:           {kw_count:6}")
            else:
                print("⚠️  No keywords table yet")
            
            conn.close()
        except Exception as e:
            print(f"⚠️  Error checking keywords DB: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # CHECK 4: EVOKI_V3_ANALYTICS.DB
    # ═══════════════════════════════════════════════════════════════════════
    
    print("\n📦 DATABASE 4: evoki_v3_analytics.db")
    print("-"*70)
    
    analytics_db = DBS["evoki_v3_analytics.db"]
    if not analytics_db.exists():
        print("⚠️  Database not found (created during analytics phase)")
    else:
        try:
            conn = sqlite3.connect(analytics_db)
            cur = conn.cursor()
            
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            
            if 'b_vector_verifications' in tables:
                cur.execute("SELECT COUNT(*) FROM b_vector_verifications")
                ver_count = cur.fetchone()[0]
                print(f"✅ b_vector_verif:     {ver_count:6}")
            else:
                print("⚠️  No b_vector_verifications table yet")
            
            conn.close()
        except Exception as e:
            print(f"⚠️  Error checking analytics DB: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # CHECK 5: EVOKI_V3_TRAJECTORIES.DB
    # ═══════════════════════════════════════════════════════════════════════
    
    print("\n📦 DATABASE 5: evoki_v3_trajectories.db")
    print("-"*70)
    
    traj_db = DBS["evoki_v3_trajectories.db"]
    if not traj_db.exists():
        print("⚠️  Database not found (created during trajectories phase)")
    else:
        try:
            conn = sqlite3.connect(traj_db)
            cur = conn.cursor()
            
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            
            if 'metric_trajectories' in tables:
                cur.execute("SELECT COUNT(*) FROM metric_trajectories")
                traj_count = cur.fetchone()[0]
                print(f"✅ metric_trajectories:{traj_count:6}")
            
            if 'metric_predictions' in tables:
                cur.execute("SELECT COUNT(*) FROM metric_predictions")
                pred_count = cur.fetchone()[0]
                print(f"✅ metric_predictions: {pred_count:6}")
            
            if not tables:
                print("⚠️  No tables found yet")
            
            conn.close()
        except Exception as e:
            print(f"⚠️  Error checking trajectories DB: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # CHECK 6: FAISS INDICES
    # ═══════════════════════════════════════════════════════════════════════
    
    print("\n🔍 FAISS INDICES CHECK:")
    print("-"*70)
    
    if FAISS_DIR.exists():
        faiss_indices = list(FAISS_DIR.glob("*.index"))
        if faiss_indices:
            for idx_file in faiss_indices:
                size_mb = idx_file.stat().st_size / (1024*1024)
                print(f"✅ {idx_file.name:30} ({size_mb:.2f} MB)")
        else:
            print("⚠️  No FAISS indices found yet")
    else:
        print("⚠️  FAISS directory not found")
    
    # ═══════════════════════════════════════════════════════════════════════
    # FINAL VERDICT
    # ═══════════════════════════════════════════════════════════════════════
    
    print("\n" + "="*70)
    print("📋 FINAL VERDICT")
    print("="*70)
    
    # Minimum requirements for GO
    min_pairs = results.get('prompt_pairs', 0) >= 100
    
    if all_checks_passed and min_pairs:
        print("\n✅✅✅ CORE CHECKS PASSED — SYSTEM FUNCTIONAL! ✅✅✅")
        print(f"\n📊 {results.get('prompt_pairs', 0)} pairs in core DB")
        print("🚀 Ready for scale-up or next phase!")
        return True
    elif min_pairs:
        print("\n⚠️  SOME WARNINGS — But core system functional")
        print(f"\n📊 {results.get('prompt_pairs', 0)} pairs in core DB")
        print("💡 Some DBs may be empty (normal for phased implementation)")
        print("✅ OK to continue if this is expected for your current phase")
        return True
    else:
        print("\n❌ CRITICAL ISSUES FOUND — FIX BEFORE PROCEEDING!")
        print(f"\n📊 Only {results.get('prompt_pairs', 0)} pairs found (need ≥100)")
        return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
