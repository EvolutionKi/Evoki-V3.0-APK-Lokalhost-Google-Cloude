#!/usr/bin/env python3
"""
FORENSIC ANALYSIS: Was ist WIRKLICH implementiert?

Kategorien:
1. DEFINED: Slot/Key existiert
2. IMPLEMENTED: Funktion compute_mXX() existiert im Code
3. EXECUTED: Wert != 0.0 (wurde berechnet, nicht Default)
4. DYNAMIC: Ändert sich zwischen 2 verschiedenen Inputs
"""

import sqlite3
import json
import sys
from pathlib import Path

# Load two different pairs from DB
DB_PATH = Path(r"c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\data\databases\evoki_v3_core.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get 2 different pairs
cur.execute("SELECT user_metrics_json FROM metrics_full LIMIT 2")
rows = cur.fetchall()

m1 = json.loads(rows[0][0])
m2 = json.loads(rows[1][0])

print("=" * 80)
print("FORENSISCHE METRIK-ANALYSE")
print("=" * 80)

# Category 1: DEFINED (slot exists)
defined = set(m1.keys())

# Category 2: EXECUTED (not default 0.0)
executed_m1 = {k for k, v in m1.items() if v != 0.0}

# Category 3: DYNAMIC (changes between inputs)
dynamic = set()
for key in m1.keys():
    if m1[key] != m2[key]:
        dynamic.add(key)

# Category 4: STATIC (always same value)
static = defined - dynamic

# Category 5: ZERO-SPAM (always 0.0)
zero_spam = {k for k in defined if m1[k] == 0.0 and m2[k] == 0.0}

print(f"\n1️⃣ DEFINED (Slots existieren): {len(defined)}")
print(f"2️⃣ EXECUTED in Sample 1 (≠ 0.0): {len(executed_m1)}")
print(f"3️⃣ DYNAMIC (ändert sich):      {len(dynamic)}")
print(f"4️⃣ STATIC (immer gleich):      {len(static)}")
print(f"5️⃣ ZERO-SPAM (immer 0.0):      {len(zero_spam)}")

print(f"\n{'─' * 80}")
print(f"DYNAMISCHE METRIKEN ({len(dynamic)}) - Diese sind ECHT:")
print("─" * 80)
for i, key in enumerate(sorted(dynamic), 1):
    v1, v2 = m1[key], m2[key]
    diff = abs(v1 - v2)
    print(f"{i:3d}. {key:20s}  Sample1={v1:6.3f}  Sample2={v2:6.3f}  Δ={diff:6.3f}")

print(f"\n{'─' * 80}")
print(f"STATISCHE METRIKEN ({len(static)}) - Immer gleicher Wert:")
print("─" * 80)
for i, key in enumerate(sorted(static), 1):
    val = m1[key]
    print(f"{i:3d}. {key:20s}  = {val:.3f}")
    if i >= 10:
        print(f"       ... und {len(static) - 10} weitere")
        break

print(f"\n{'─' * 80}")
print(f"ZERO-SPAM ({len(zero_spam)}) - Immer 0.0 = NICHT IMPLEMENTIERT:")
print("─" * 80)
for i, key in enumerate(sorted(zero_spam), 1):
    print(f"{i:3d}. {key}")
    if i >= 15:
        print(f"       ... und {len(zero_spam) - 15} weitere")
        break

# Now check source code
print(f"\n{'─' * 80}")
print("SOURCE CODE ANALYSE:")
print("─" * 80)

sys.path.insert(0, r"c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3")

# Count compute_mXX functions
import phase1_base
import phase2_derived
import phase3_physics
import phase4_synthesis

modules = [phase1_base, phase2_derived, phase3_physics, phase4_synthesis]
compute_functions = {}

for mod in modules:
    for name in dir(mod):
        if name.startswith("compute_m") and callable(getattr(mod, name)):
            compute_functions[name.replace("compute_", "")] = mod.__name__.split(".")[-1]

print(f"Gefundene compute_m* Funktionen: {len(compute_functions)}")
print(f"\nFunktionen nach Phase:")
for phase in ["phase1_base", "phase2_derived", "phase3_physics", "phase4_synthesis"]:
    count = sum(1 for v in compute_functions.values() if v == phase)
    print(f"  {phase:20s} {count:3d} Funktionen")

# Compare: defined vs implemented
implemented = set(compute_functions.keys())
defined_metric_keys = {k for k in defined if k.startswith("m")}

has_code = implemented & defined_metric_keys
no_code = defined_metric_keys - implemented

print(f"\n{'─' * 80}")
print("CODE vs. SLOTS:")
print("─" * 80)
print(f"  Slots mit Code:  {len(has_code)}")
print(f"  Slots ohne Code: {len(no_code)}")

conn.close()

print(f"\n{'=' * 80}")
print("HARTE WAHRHEIT:")
print("=" * 80)
print(f"  DEFINED (Slots):           {len(defined)}")
print(f"  IMPLEMENTED (Code exists): {len(compute_functions)}")
print(f"  DYNAMIC (echt berechnet):  {len(dynamic)}")
print(f"  ZERO-SPAM (fake):          {len(zero_spam)}")
print(f"\n  SPEC-Ziel war: 168")
print(f"  Differenz: {168 - len(dynamic)} Metriken fehlen wirklich")
print("=" * 80)
