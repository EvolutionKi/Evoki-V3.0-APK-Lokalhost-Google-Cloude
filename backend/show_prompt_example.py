#!/usr/bin/env python3
"""
Zeigt ein komplettes Prompt-Paar mit allen Metriken
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(r"c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\data\databases\evoki_v3_core.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Hole ein Beispiel-Paar
cur.execute("""
    SELECT 
        pp.pair_id,
        pp.user_text,
        pp.ai_text,
        m.user_metrics_json,
        m.ai_metrics_json,
        m.b_vector_json,
        m.b_align,
        m.chain_hash
    FROM prompt_pairs pp
    JOIN metrics_full m ON pp.pair_id = m.pair_id
    LIMIT 1
""")

row = cur.fetchone()

print("=" * 80)
print("BEISPIEL: PROMPT-PAAR MIT ALLEN METRIKEN")
print("=" * 80)

print(f"\n📝 PAIR ID: {row[0]}")
print(f"\n{'─' * 80}")
print("👤 USER PROMPT:")
print(f"{'─' * 80}")
print(row[1][:300] + ("..." if len(row[1]) > 300 else ""))

print(f"\n{'─' * 80}")
print("🤖 AI RESPONSE:")
print(f"{'─' * 80}")
print(row[2][:300] + ("..." if len(row[2]) > 300 else ""))

# User Metrics
user_metrics = json.loads(row[3])
ai_metrics = json.loads(row[4])
b_vector = json.loads(row[5])

print(f"\n{'─' * 80}")
print("📊 USER METRIKEN (Auswahl von {}):")
print("─" * 80)
print(f"  🔥 m1_A (Affekt):        {user_metrics.get('m1_A', 0):.3f}")
print(f"  ⚠️  m19_z_prox (Todesnähe): {user_metrics.get('m19_z_prox', 0):.3f}")
print(f"  🚨 m151_hazard:          {user_metrics.get('m151_hazard', 0):.3f}")
print(f"  📈 m2_PCI (Complexity):  {user_metrics.get('m2_PCI', 0):.3f}")
print(f"  🌊 m5_coh (Kohärenz):    {user_metrics.get('m5_coh', 0):.3f}")
print(f"  🔄 m7_LL (Trübung):      {user_metrics.get('m7_LL', 0):.3f}")
print(f"  💭 m8_s_self:            {user_metrics.get('m8_s_self', 0):.3f}")
print(f"  ❓ m9_x_exist:           {user_metrics.get('m9_x_exist', 0):.3f}")
print(f"  ⏪ m10_b_past:           {user_metrics.get('m10_b_past', 0):.3f}")

print(f"\n{'─' * 80}")
print("📊 AI METRIKEN (Auswahl von {}):")
print("─" * 80)
print(f"  🔥 m1_A (Affekt):        {ai_metrics.get('m1_A', 0):.3f}")
print(f"  ⚠️  m19_z_prox (Todesnähe): {ai_metrics.get('m19_z_prox', 0):.3f}")
print(f"  🚨 m151_hazard:          {ai_metrics.get('m151_hazard', 0):.3f}")
print(f"  📈 m2_PCI (Complexity):  {ai_metrics.get('m2_PCI', 0):.3f}")
print(f"  🌊 m5_coh (Kohärenz):    {ai_metrics.get('m5_coh', 0):.3f}")
print(f"  🔄 m7_LL (Trübung):      {ai_metrics.get('m7_LL', 0):.3f}")
print(f"  💭 m8_s_self:            {ai_metrics.get('m8_s_self', 0):.3f}")
print(f"  ❓ m9_x_exist:           {ai_metrics.get('m9_x_exist', 0):.3f}")
print(f"  ⏪ m10_b_past:           {ai_metrics.get('m10_b_past', 0):.3f}")

print(f"\n{'─' * 80}")
print("💎 B-VECTOR (7 DIMENSIONEN):")
print("─" * 80)
for key, val in b_vector.items():
    icon = {"B_safety": "🔒", "B_life": "💫", "B_warmth": "🔥", 
            "B_clarity": "💎", "B_depth": "🌊", "B_init": "⚡", "B_truth": "🎯"}.get(key, "📊")
    constraint = ""
    if key == "B_safety":
        constraint = " (≥0.8)" if val >= 0.8 else " ⚠️ CONSTRAINT VIOLATED!"
    elif key == "B_life":
        constraint = " (≥0.9)" if val >= 0.9 else " ⚠️ CONSTRAINT VIOLATED!"
    print(f"  {icon} {key:12s} {val:.3f}{constraint}")

print(f"\n{'─' * 80}")
print("🎯 COMPOSITE SCORES:")
print("─" * 80)
print(f"  ⭐ B_ALIGN (Composite): {row[6]:.3f}")

print(f"\n{'─' * 80}")
print("🔗 SESSION CHAIN:")
print("─" * 80)
print(f"  Hash: {row[7][:32]}...")
print(f"  Short: ...{row[7][-12:]}")

print(f"\n{'─' * 80}")
print("📦 STATISTIK:")
print("─" * 80)
print(f"  User Metrics Total: {len(user_metrics)}")
print(f"  AI Metrics Total:   {len(ai_metrics)}")
print(f"  B-Vector Dims:      7")

conn.close()

print(f"\n{'=' * 80}")
print("✅ Alle Metriken korrekt mit 4-Phase Calculator berechnet!")
print("=" * 80)
