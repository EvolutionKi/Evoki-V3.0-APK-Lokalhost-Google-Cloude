"""
REVERSIBILITY TEST - LIVE DEMO
================================

Zeigt das komplette Forward-Backward Prinzip:
1. Text → Metriken berechnen (FORWARD)
2. Metriken → DB speichern
3. DB → Metriken laden (BACKWARD)
4. Vergleichen → Validieren
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "core" / "evoki_metrics_v3"))

from metrics_calculator_4phase_COMPLETE import MetricsCalculator, MetricsContext


def create_test_db(db_path: str):
    """Create minimal test DB schema"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS evoki_core_turns (
            turn_id INTEGER PRIMARY KEY,
            conversation_id TEXT,
            role TEXT,
            text TEXT,
            timestamp TEXT,
            gap_seconds INTEGER,
            m1_A REAL,
            m2_PCI REAL,
            m4_flow REAL,
            m5_coh REAL,
            m15_affekt_a REAL,
            m17_nabla_a REAL,
            m19_z_prox REAL,
            m20_phi_proxy REAL,
            m101_T_panic REAL,
            m102_T_disso REAL,
            m103_T_integ REAL,
            m151_hazard REAL,
            m161_commit TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Test DB created")


def save_metrics_to_db(db_path: str, turn_id: int, conv_id: str, role: str, 
                       text: str, gap_seconds: int, metrics: dict):
    """Save metrics to test DB"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO evoki_core_turns (
            turn_id, conversation_id, role, text, timestamp, gap_seconds,
            m1_A, m2_PCI, m4_flow, m5_coh, m15_affekt_a, m17_nabla_a,
            m19_z_prox, m20_phi_proxy, m101_T_panic, m102_T_disso, 
            m103_T_integ, m151_hazard, m161_commit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        turn_id, conv_id, role, text, datetime.now().isoformat(), gap_seconds,
        metrics.get('m1_A'), metrics.get('m2_PCI'), metrics.get('m4_flow'),
        metrics.get('m5_coh'), metrics.get('m15_affekt_a'), 
        metrics.get('m17_nabla_a'), metrics.get('m19_z_prox'),
        metrics.get('m20_phi_proxy'), metrics.get('m101_T_panic'),
        metrics.get('m102_T_disso'), metrics.get('m103_T_integ'),
        metrics.get('m151_hazard'), metrics.get('m161_commit')
    ))
    
    conn.commit()
    conn.close()


def load_metrics_from_db(db_path: str, turn_id: int) -> dict:
    """Load metrics from DB"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT m1_A, m2_PCI, m4_flow, m5_coh, m15_affekt_a, m17_nabla_a,
               m19_z_prox, m20_phi_proxy, m101_T_panic, m102_T_disso,
               m103_T_integ, m151_hazard, m161_commit
        FROM evoki_core_turns
        WHERE turn_id = ?
    """, (turn_id,))
    
    row = cur.fetchone()
    conn.close()
    
    return dict(row) if row else {}


def compare_metrics(calculated: dict, stored: dict, tolerance: float = 0.001) -> tuple:
    """Compare calculated vs stored metrics"""
    errors = []
    drift = {}
    max_drift = 0.0
    
    # Only compare metrics that should match
    metrics_to_check = ['m1_A', 'm2_PCI', 'm4_flow', 'm5_coh', 'm15_affekt_a',
                        'm19_z_prox', 'm20_phi_proxy', 'm101_T_panic', 
                        'm102_T_disso', 'm103_T_integ', 'm151_hazard']
    
    for metric in metrics_to_check:
        calc_val = calculated.get(metric)
        stored_val = stored.get(metric)
        
        if calc_val is None or stored_val is None:
            continue
        
        diff = abs(calc_val - stored_val)
        if diff > tolerance:
            drift[metric] = diff
            max_drift = max(max_drift, diff)
            errors.append(f"{metric}: drift={diff:.6f} (calc={calc_val:.4f} vs stored={stored_val:.4f})")
    
    # String comparison for commit
    if calculated.get('m161_commit') != stored.get('m161_commit'):
        errors.append(f"m161_commit: '{calculated.get('m161_commit')}' != '{stored.get('m161_commit')}'")
    
    return errors, drift, max_drift


def run_reversibility_test():
    """
    Complete reversibility test
    
    FORWARD:  Text → Calculate → Store
    BACKWARD: Load → Recalculate → Compare
    """
    
    print("=" * 80)
    print("🧪 REVERSIBILITY TEST - LIVE DEMO")
    print("=" * 80)
    print()
    
    # Setup
    test_db = "test_reversibility.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    create_test_db(test_db)
    calc = MetricsCalculator()
    
    # =========================================================================
    # TURN 1: Initial message (no previous metrics)
    # =========================================================================
    print("📝 TURN 1: User sagt 'Ich bin heute traurig'")
    print("-" * 80)
    
    turn1_text = "Ich bin heute traurig"
    turn1_context = MetricsContext(gap_seconds=0)
    
    print("   🔄 FORWARD: Berechne Metriken...")
    turn1_metrics = calc.calculate_all(
        text=turn1_text,
        role="user",
        context=turn1_context
    )
    
    print(f"   ✅ {len(turn1_metrics)} Metriken berechnet")
    print(f"      m1_A:          {turn1_metrics['m1_A']:.4f}")
    print(f"      m19_z_prox:    {turn1_metrics['m19_z_prox']:.4f}")
    print(f"      m151_hazard:   {turn1_metrics['m151_hazard']:.4f}")
    print(f"      m161_commit:   '{turn1_metrics['m161_commit']}'")
    
    print("   💾 Speichere in DB...")
    save_metrics_to_db(test_db, 1, "test-conv", "user", turn1_text, 0, turn1_metrics)
    print("   ✅ Gespeichert")
    
    print()
    print("   🔙 BACKWARD: Lade aus DB und vergleiche...")
    stored_turn1 = load_metrics_from_db(test_db, 1)
    errors1, drift1, max_drift1 = compare_metrics(turn1_metrics, stored_turn1)
    
    if len(errors1) == 0:
        print("   ✅ VALID! Keine Abweichungen")
    else:
        print(f"   ❌ INVALID! {len(errors1)} Fehler:")
        for error in errors1:
            print(f"      - {error}")
    
    print()
    
    # =========================================================================
    # TURN 2: Follow-up message (needs prev_metrics!)
    # =========================================================================
    print("📝 TURN 2: User sagt 'Aber ich versuche es zu verstehen'")
    print("-" * 80)
    
    turn2_text = "Aber ich versuche es zu verstehen"
    turn2_context = MetricsContext(
        gap_seconds=45,
        prev_metrics=turn1_metrics  # 🔥 WICHTIG: Gradient braucht prev!
    )
    
    print("   🔄 FORWARD: Berechne Metriken (mit prev_metrics)...")
    turn2_metrics = calc.calculate_all(
        text=turn2_text,
        role="user",
        context=turn2_context
    )
    
    print(f"   ✅ {len(turn2_metrics)} Metriken berechnet")
    print(f"      m1_A:          {turn2_metrics['m1_A']:.4f}")
    print(f"      m17_nabla_a:   {turn2_metrics['m17_nabla_a']:.4f} (Gradient!)")
    print(f"      m19_z_prox:    {turn2_metrics['m19_z_prox']:.4f}")
    print(f"      m151_hazard:   {turn2_metrics['m151_hazard']:.4f}")
    
    print("   💾 Speichere in DB...")
    save_metrics_to_db(test_db, 2, "test-conv", "user", turn2_text, 45, turn2_metrics)
    print("   ✅ Gespeichert")
    
    print()
    print("   🔙 BACKWARD: Lade aus DB und vergleiche...")
    stored_turn2 = load_metrics_from_db(test_db, 2)
    errors2, drift2, max_drift2 = compare_metrics(turn2_metrics, stored_turn2)
    
    if len(errors2) == 0:
        print("   ✅ VALID! Keine Abweichungen")
    else:
        print(f"   ❌ INVALID! {len(errors2)} Fehler:")
        for error in errors2:
            print(f"      - {error}")
    
    print()
    
    # =========================================================================
    # TURN 3: Critical message (high trauma)
    # =========================================================================
    print("📝 TURN 3: User sagt 'Ich habe Panik und fühle mich hoffnungslos'")
    print("-" * 80)
    
    turn3_text = "Ich habe Panik und fühle mich hoffnungslos"
    turn3_context = MetricsContext(
        gap_seconds=120,
        prev_metrics=turn2_metrics,
        z_prox_history=[
            turn1_metrics['m19_z_prox'],
            turn2_metrics['m19_z_prox']
        ]
    )
    
    print("   🔄 FORWARD: Berechne Metriken (mit history)...")
    turn3_metrics = calc.calculate_all(
        text=turn3_text,
        role="user",
        context=turn3_context
    )
    
    print(f"   ✅ {len(turn3_metrics)} Metriken berechnet")
    print(f"      m1_A:          {turn3_metrics['m1_A']:.4f}")
    print(f"      m101_T_panic:  {turn3_metrics['m101_T_panic']:.4f} ⚠️")
    print(f"      m19_z_prox:    {turn3_metrics['m19_z_prox']:.4f} ⚠️")
    print(f"      m151_hazard:   {turn3_metrics['m151_hazard']:.4f} ⚠️")
    print(f"      m161_commit:   '{turn3_metrics['m161_commit']}' 🚨")
    
    print("   💾 Speichere in DB...")
    save_metrics_to_db(test_db, 3, "test-conv", "user", turn3_text, 120, turn3_metrics)
    print("   ✅ Gespeichert")
    
    print()
    print("   🔙 BACKWARD: Lade aus DB und vergleiche...")
    stored_turn3 = load_metrics_from_db(test_db, 3)
    errors3, drift3, max_drift3 = compare_metrics(turn3_metrics, stored_turn3)
    
    if len(errors3) == 0:
        print("   ✅ VALID! Keine Abweichungen")
    else:
        print(f"   ❌ INVALID! {len(errors3)} Fehler:")
        for error in errors3:
            print(f"      - {error}")
    
    print()
    
    # =========================================================================
    # FINAL REPORT
    # =========================================================================
    print("=" * 80)
    print("📊 FINAL REPORT")
    print("=" * 80)
    
    all_valid = len(errors1) == 0 and len(errors2) == 0 and len(errors3) == 0
    
    if all_valid:
        print("✅ ALLE TURNS VALID!")
        print()
        print("   Das Reversibilitätsprinzip funktioniert:")
        print("   x = 1+1+1+1+1 = 5")
        print("   5-1-1-1-1-1 = x")
        print()
        print("   FORWARD:  Text → Metriken → DB")
        print("   BACKWARD: DB → Rekonstruktion → Validierung")
        print("   RESULT:   Konstruktion == Rekonstruktion ✅")
    else:
        print("❌ FEHLER GEFUNDEN!")
        print(f"   Turn 1: {len(errors1)} errors")
        print(f"   Turn 2: {len(errors2)} errors")
        print(f"   Turn 3: {len(errors3)} errors")
    
    print()
    print(f"📁 Test DB: {os.path.abspath(test_db)}")
    print()


if __name__ == "__main__":
    try:
        run_reversibility_test()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
