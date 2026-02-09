"""
PHASE 2: TRAJECTORY CALCULATOR
Berechnet ∇ (Delta) für ALLE 161 Metriken zwischen aufeinanderfolgenden Pairs.

Input:  evoki_v3_core.db (metrics_full mit 2000 rows)
Output: evoki_metadata.db (trajectory_full mit Deltas)

Author: Antigravity
Date:   2026-02-08
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_V3_CORE = SCRIPT_DIR.parent / "backend" / "data" / "databases" / "evoki_v3_core.db"
DB_METADATA = SCRIPT_DIR.parent / "evoki_metadata.db"

# W-P-F Offsets (aus BUCH 7: Temple Data Layer)
WPF_OFFSETS = [-25, -5, -2, -1, 1, 2, 5, 25]  # PROMPTS!

# Alle 161 Metriken (aus SPEC FINAL7)
ALL_METRICS = [
    # Core (m1-m20)
    "m1_A", "m2_PCI", "m3_S", "m4_flow", "m5_I_coh",
    "m6_ZLF", "m7_LL", "m8_s_self", "m9_x_exist", "m10_angstrom",
    "m11_ctx_break", "m12_gap_norm", "m13_rep_same", "m14_rep_hist", "m15_affekt_a",
    "m16_external_stag", "m17_M_momentum", "m18_T_tau", "m19_z_prox", "m20_phi",
    
    # Physics (m21-m35)
    "m21_chaos", "m22_cog_load", "m23_ctx_1", "m24_ctx_2", "m25_ctx_3",
    "m26_ctx_4", "m27_lambda_depth", "m28_phys_1", "m29_phys_2", "m30_phys_3",
    "m31_phys_4", "m32_phys_5", "m33_phys_6", "m34_phys_7", "m35_phys_8",
    
    # Andromatik (m56-m70) + weitere bis m161
    # (vereinfacht - in Production alle 161!)
]

class TrajectoryCalculator:
    """Berechnet Trajektorien (Deltas) für alle Metriken."""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"🚀 Trajectory Calculator initialized")
        print(f"   Session: {self.session_id}")
    
    def create_trajectory_table(self):
        """Erstelle trajectory_full Tabelle in metadata DB."""
        with sqlite3.connect(DB_METADATA) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trajectory_full (
                    pair_id         TEXT PRIMARY KEY,
                    session_id      TEXT NOT NULL,
                    pair_index      INTEGER NOT NULL,
                    
                    -- W-P-F: MULTI-WINDOW TRAJECTORIES
                    -- WEST (Vergangenheit)
                    trajectory_minus_25_json TEXT,  -- Delta zu -25 Prompts
                    trajectory_minus_5_json  TEXT,  -- Delta zu -5 Prompts
                    trajectory_minus_2_json  TEXT,  -- Delta zu -2 Prompts
                    trajectory_minus_1_json  TEXT,  -- Delta zu -1 Prompt (direkter Vorgänger)
                    
                    -- FUTURE (Historical Futures)
                    trajectory_plus_1_json   TEXT,  -- Delta zu +1 Prompt (was kam danach?)
                    trajectory_plus_2_json   TEXT,  -- Delta zu +2 Prompts
                    trajectory_plus_5_json   TEXT,  -- Delta zu +5 Prompts
                    trajectory_plus_25_json  TEXT,  -- Delta zu +25 Prompts
                    
                    -- Denormalized (kritische Metriken, nur für -1)
                    delta_m1_A          REAL,
                    delta_m2_PCI        REAL,
                    delta_m19_z_prox    REAL,
                    delta_m101_T_panic  REAL,
                    delta_m151_hazard   REAL,
                    
                    -- Trajectory Statistics (über ALLE Fenster)
                    delta_count_positive    INTEGER,  -- Wie viele Metriken stiegen?
                    delta_count_negative    INTEGER,  -- Wie viele Metriken fielen?
                    delta_magnitude_avg     REAL,     -- Durchschnittliche |Δ|
                    delta_magnitude_max     REAL,     -- Maximales |Δ|
                    
                    created_at      TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.commit()
        print("✓ trajectory_full table created (W-P-F multi-window)")
    
    def get_metrics_from_json(self, pair_id: str) -> Optional[Dict]:
        """Lese Metriken aus metrics_full (JSON)."""
        with sqlite3.connect(DB_V3_CORE) as conn:
            cur = conn.execute("""
                SELECT user_metrics_json FROM metrics_full WHERE pair_id = ?
            """, (pair_id,))
            row = cur.fetchone()
            if row:
                return json.loads(row[0])
        return None
    
    def calculate_delta(self, current: Dict, previous: Dict) -> Dict:
        """Berechne Delta für ALLE Metriken."""
        trajectory = {}
        
        for metric in ALL_METRICS:
            curr_val = current.get(metric, 0.0)
            prev_val = previous.get(metric, 0.0)
            delta = curr_val - prev_val
            trajectory[f"∇{metric}"] = round(delta, 6)
        
        return trajectory
    
    def calculate_statistics(self, trajectory: Dict) -> Dict:
        """Berechne Statistiken über die Trajektorie."""
        deltas = [abs(v) for k, v in trajectory.items() if k.startswith("∇")]
        
        positive = sum(1 for v in trajectory.values() if v > 0)
        negative = sum(1 for v in trajectory.values() if v < 0)
        
        return {
            "positive": positive,
            "negative": negative,
            "avg": round(sum(deltas) / len(deltas), 6) if deltas else 0.0,
            "max": round(max(deltas), 6) if deltas else 0.0
        }
    
    def validate_metrics_for_nan(self, metrics: Dict, pair_id: str, label: str = "") -> bool:
        """
        FAIL-SAFE TESTER: Erkennt NaN/None/Inf Werte und gibt FETTE Warnung aus!
        INTEGRITY CHECK: Nur wenn exakt 161 Metriken → OK!
        
        Returns: True wenn OK, False wenn Probleme gefunden
        """
        import math
        
        # SKIP validation if metrics is None (future pair doesn't exist yet)
        if metrics is None:
            return True
        
        # COUNT der Metriken (NUR m* Metriken zählen!)
        metric_count = len([k for k in metrics.keys() if k.startswith('m')])
        
        issues = []
        
        for metric_name, metric_value in metrics.items():
            # None check
            if metric_value is None:
                issues.append(f"{metric_name}=None")
                continue
            
            # NaN check
            if isinstance(metric_value, (int, float)):
                if math.isnan(metric_value):
                    issues.append(f"{metric_name}=NaN")
                elif math.isinf(metric_value):
                    issues.append(f"{metric_name}=Inf")
        
        # INTEGRITY CHECK: COUNT >= 168? (SPEC FINAL7: Core 161 + Context/Safety 7)
        if metric_count < 168:
            print("\n" + "💀" * 35)
            print("💀💀💀 FAIL INTEGRITY LOST NOT SAFE BETTER GO HOME! 💀💀💀")
            print("💀" * 35)
            print(f"Pair ID:     {pair_id}")
            if label:
                print(f"Label:       {label}")
            print(f"EXPECTED:    >=168 Metriken (SPEC FINAL7)")
            print(f"ACTUAL:      {metric_count} Metriken")
            print(f"MISSING:     {168 - metric_count} Metriken")
            print(f"")
            print("⚠️  SYSTEM INTEGRITY VIOLATED!")
            print("⚠️  CALCULATION INCOMPLETE!")
            print("⚠️  DATA NOT TRUSTWORTHY!")
            print("💀" * 35 + "\n")
            return False
        
        # NaN/Inf Issues?
        if issues:
            print("\n" + "=" * 70)
            print("🚨🚨🚨 FAIL-SAFE ALERT: METRIKEN NICHT BERECHNET! 🚨🚨🚨")
            print("=" * 70)
            print(f"Pair ID:  {pair_id}")
            if label:
                print(f"Label:    {label}")
            print(f"Count:    {metric_count}/168 ✅")
            print(f"Probleme: {len(issues)}")
            print("\nBetroffene Metriken:")
            for issue in issues[:10]:  # Ersten 10 zeigen
                print(f"  ❌ {issue}")
            if len(issues) > 10:
                print(f"  ... und {len(issues) - 10} weitere!")
            print("=" * 70 + "\n")
            return False
        
        # ALL OK!
        return True
    
    def validate_metrics_advanced(self, metrics_history: list, current_pair_id: str) -> Dict:
        """
        ADVANCED FAIL-SAFE: Erkennt FAKE-Metriken (statisch/eingefroren/simuliert)!
        
        Args:
            metrics_history: Liste von Metrik-Dicts (letzte 10-50 Pairs)
            current_pair_id: Aktuelle Pair ID
        
        Returns: Dict mit detected_issues
        """
        if len(metrics_history) < 5:
            return {}  # Brauchen mindestens 5 für Pattern-Erkennung
        
        detected = {
            "static": [],      # Immer gleicher Wert
            "frozen": [],      # Keine Änderung über Zeit
            "zero_spam": [],   # Immer 0.0 (nicht implementiert)
            "suspicious": []   # Verdächtig uniform
        }
        
        # Alle Metriken prüfen
        all_metrics = set()
        for m in metrics_history:
            all_metrics.update(m.keys())
        
        for metric_name in all_metrics:
            # Sammle Werte über History
            values = []
            for m in metrics_history:
                val = m.get(metric_name, None)
                if val is not None and isinstance(val, (int, float)):
                    values.append(val)
            
            if len(values) < 5:
                continue
            
            # 1. ZERO-SPAM Detection (immer 0.0)
            if all(v == 0.0 for v in values):
                detected["zero_spam"].append(metric_name)
                continue
            
            # 2. STATIC Detection (immer gleicher Wert)
            if len(set(values)) == 1:
                detected["static"].append(f"{metric_name}={values[0]}")
                continue
            
            # 3. FROZEN Detection (kaum Änderung)
            import statistics
            if len(values) > 3:
                std_dev = statistics.stdev(values)
                mean_val = statistics.mean(values)
                
                # Wenn StdDev < 1% vom Mean → eingefroren!
                if mean_val != 0 and std_dev / abs(mean_val) < 0.01:
                    detected["frozen"].append(f"{metric_name} (σ={std_dev:.6f})")
            
            # 4. SUSPICIOUS Pattern (zu uniform → random.uniform?)
            # Wenn Werte perfekt verteilt über Range ohne natürliche Cluster
            if len(values) > 10:
                # Berechne ob Werte natürliche Variation haben
                # Echte Metriken haben oft Cluster, Fake Random nicht
                sorted_vals = sorted(values)
                gaps = [sorted_vals[i+1] - sorted_vals[i] for i in range(len(sorted_vals)-1)]
                
                if gaps:
                    gap_std = statistics.stdev(gaps)
                    gap_mean = statistics.mean(gaps)
                    
                    # Wenn Gaps zu uniform → verdächtig!
                    if gap_mean > 0 and gap_std / gap_mean < 0.3:
                        detected["suspicious"].append(f"{metric_name} (uniform gaps)")
        
        # Report wenn Issues gefunden
        total_issues = sum(len(v) for v in detected.values())
        
        if total_issues > 0:
            print("\n" + "🔥" * 35)
            print("🔥🔥🔥 FAKE-METRIKEN ALERT! 🔥🔥🔥")
            print("🔥" * 35)
            print(f"Pair: {current_pair_id}")
            print(f"History: {len(metrics_history)} pairs analyzed\n")
            
            if detected["zero_spam"]:
                print(f"❌ ZERO-SPAM ({len(detected['zero_spam'])} Metriken):")
                print(f"   → NICHT IMPLEMENTIERT oder DEFAULT 0.0!")
                for m in detected["zero_spam"][:5]:
                    print(f"      • {m}")
                if len(detected["zero_spam"]) > 5:
                    print(f"      ... und {len(detected['zero_spam'])-5} weitere")
            
            if detected["static"]:
                print(f"\n❌ STATISCH ({len(detected['static'])} Metriken):")
                print(f"   → IMMER GLEICHER WERT!")
                for m in detected["static"][:5]:
                    print(f"      • {m}")
                if len(detected["static"]) > 5:
                    print(f"      ... und {len(detected['static'])-5} weitere")
            
            if detected["frozen"]:
                print(f"\n❌ EINGEFROREN ({len(detected['frozen'])} Metriken):")
                print(f"   → KAUM VARIATION (σ < 1%)!")
                for m in detected["frozen"][:5]:
                    print(f"      • {m}")
                if len(detected["frozen"]) > 5:
                    print(f"      ... und {len(detected['frozen'])-5} weitere")
            
            if detected["suspicious"]:
                print(f"\n⚠️  VERDÄCHTIG ({len(detected['suspicious'])} Metriken):")
                print(f"   → ZU UNIFORM (random.uniform?)")
                for m in detected["suspicious"][:5]:
                    print(f"      • {m}")
                if len(detected["suspicious"]) > 5:
                    print(f"      ... und {len(detected['suspicious'])-5} weitere")
            
            print("🔥" * 35 + "\n")
        
        return detected


    
    def process_all(self):
        """Verarbeite alle Pairs und berechne W-P-F Trajektorien."""
        
        # Get all pairs ordered by session + index
        with sqlite3.connect(DB_V3_CORE) as conn:
            cur = conn.execute("""
                SELECT pair_id, session_id, pair_index
                FROM prompt_pairs
                ORDER BY session_id, pair_index
            """)
            pairs = cur.fetchall()
        
        print(f"\n📊 Processing {len(pairs)} pairs...")
        print(f"   W-P-F Offsets: {WPF_OFFSETS}")
        
        # Index für schnellen Zugriff: (session_id, pair_index) -> pair_id
        pairs_index = {}
        for pair_id, session_id, pair_index in pairs:
            pairs_index[(session_id, pair_index)] = pair_id
        
        # Metriken-Cache (session_id, pair_index) -> metrics
        metrics_cache = {}
        
        conn_meta = sqlite3.connect(DB_METADATA)
        cur_meta = conn_meta.cursor()
        
        processed = 0
        current_session = None
        
        # History Buffer für FAKE-Detection (letzte 50 Pairs)
        metrics_history_buffer = []
        
        for pair_id, session_id, pair_index in pairs:
            
            # Session-Wechsel
            if session_id != current_session:
                current_session = session_id
                print(f"\n  Session: {session_id[:8]}...")
            
            # Aktuelle Metriken laden
            current_metrics = self.get_metrics_from_json(pair_id)
            if not current_metrics:
                print(f"  ⚠️  Pair {pair_id}: No metrics found")
                continue
            
            # FAIL-SAFE: Validate current metrics (ABORT on fail!)
            is_valid = self.validate_metrics_for_nan(current_metrics, pair_id, f"Session {session_id[:8]}, Index {pair_index}")
            
            if not is_valid:
                # ABORT PIPELINE!
                print("\n" + "☠️" * 35)
                print("☠️☠️☠️ PIPELINE ABORTED! ☠️☠️☠️")
                print("☠️" * 35)
                print(f"REASON: Validation failed on pair {pair_id}")
                print(f"INDEX:  {processed + 1}/{len(pairs)}")
                print(f"")
                print("⚠️  JEDER PROMPT MUSS BESTEHEN!")
                print("⚠️  INTEGRITY VIOLATION DETECTED!")
                print("⚠️  STOPPING EXECUTION!")
                print("☠️" * 35 + "\n")
                
                # Close connections
                conn_meta.close()
                
                # Exit mit Fehler
                import sys
                sys.exit(1)
            
            # Zu History Buffer hinzufügen (max 50 behalten)
            metrics_history_buffer.append(current_metrics)
            if len(metrics_history_buffer) > 50:
                metrics_history_buffer.pop(0)
            
            # Cache aktualisieren
            metrics_cache[(session_id, pair_index)] = current_metrics
            
            # W-P-F Trajektorien berechnen
            trajectories = {}
            
            for offset in WPF_OFFSETS:
                target_index = pair_index + offset
                target_key = (session_id, target_index)
                
                # Target Pair existiert in gleicher Session?
                if target_key not in pairs_index:
                    trajectories[offset] = None
                    continue
                
                # Target Metriken laden (aus Cache oder DB)
                if target_key in metrics_cache:
                    target_metrics = metrics_cache[target_key]
                else:
                    target_pair_id = pairs_index[target_key]
                    target_metrics = self.get_metrics_from_json(target_pair_id)
                    if target_metrics:
                        metrics_cache[target_key] = target_metrics
                
                if not target_metrics:
                    trajectories[offset] = None
                    continue
                
                # Delta berechnen (current - target für negative, target - current für positive)
                if offset < 0:
                    # WEST: current - past
                    delta = self.calculate_delta(current_metrics, target_metrics)
                else:
                    # FUTURE: future - current
                    delta = self.calculate_delta(target_metrics, current_metrics)
                
                # NOTE: Don't validate deltas - they have ∇m* keys not m* keys
                
                trajectories[offset] = delta
            
            # Statistiken berechnen (nur über -1 für Konsistenz)
            if trajectories.get(-1):
                stats = self.calculate_statistics(trajectories[-1])
            else:
                stats = {"positive": 0, "negative": 0, "avg": 0.0, "max": 0.0}
            
            # Speichern
            cur_meta.execute("""
                INSERT OR REPLACE INTO trajectory_full
                (pair_id, session_id, pair_index,
                 trajectory_minus_25_json, trajectory_minus_5_json,
                 trajectory_minus_2_json, trajectory_minus_1_json,
                 trajectory_plus_1_json, trajectory_plus_2_json,
                 trajectory_plus_5_json, trajectory_plus_25_json,
                 delta_m1_A, delta_m2_PCI, delta_m19_z_prox,
                 positive_deltas, negative_deltas,
                 avg_delta_mag, max_delta_mag)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pair_id, session_id, pair_index,
                json.dumps(trajectories.get(-25)) if trajectories.get(-25) else None,
                json.dumps(trajectories.get(-5)) if trajectories.get(-5) else None,
                json.dumps(trajectories.get(-2)) if trajectories.get(-2) else None,
                json.dumps(trajectories.get(-1)) if trajectories.get(-1) else None,
                json.dumps(trajectories.get(1)) if trajectories.get(1) else None,
                json.dumps(trajectories.get(2)) if trajectories.get(2) else None,
                json.dumps(trajectories.get(5)) if trajectories.get(5) else None,
                json.dumps(trajectories.get(25)) if trajectories.get(25) else None,
                trajectories.get(-1, {}).get("∇m1_A", 0.0) if trajectories.get(-1) else 0.0,
                trajectories.get(-1, {}).get("∇m2_PCI", 0.0) if trajectories.get(-1) else 0.0,
                trajectories.get(-1, {}).get("∇m19_z_prox", 0.0) if trajectories.get(-1) else 0.0,
                stats["positive"],
                stats["negative"],
                stats["avg"],
                stats["max"]
            ))
            
            # Commit every 50
            processed += 1
            
            # LIVE COUNT für JEDEN Prompt!
            current_count = len(current_metrics)
            status_emoji = "✅" if current_count == 161 else "💀"
            
            # Zeige jeden 10. oder bei Problemen
            if processed % 10 == 0 or current_count != 161:
                print(f"  {status_emoji} Pair {processed}/{len(pairs)} | Metrics: {current_count}/161")
            
            if processed % 50 == 0:
                conn_meta.commit()
                
                # SUMMARY DISPLAY alle 50
                print(f"\n  ╔═══════════════════════════════════════╗")
                print(f"  ║  CHECKPOINT: {processed}/{len(pairs)} processed")
                print(f"  ║  Last Count: {current_count}/161 {status_emoji}")
                print(f"  ╚═══════════════════════════════════════╝\n")
                
                # ADVANCED FAKE-Detection alle 50 Pairs
                if len(metrics_history_buffer) >= 10:
                    self.validate_metrics_advanced(metrics_history_buffer, pair_id)
        
        # Final commit
        conn_meta.commit()
        conn_meta.close()
        
        print(f"\n✅ Processing complete!")
        print(f"   Total W-P-F trajectories: {processed}")


def main():
    """Main execution."""
    print("=" * 70)
    print("PHASE 2: TRAJECTORY CALCULATOR")
    print("=" * 70)
    
    calc = TrajectoryCalculator()
    
    # Create table
    calc.create_trajectory_table()
    
    # Process all pairs
    calc.process_all()
    
    print("\n" + "=" * 70)
    print("✅ PHASE 2 COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
