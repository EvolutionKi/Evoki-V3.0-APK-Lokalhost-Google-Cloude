#!/usr/bin/env python3
"""Simple metrics test - direct import"""
import sys
from pathlib import Path

# Direct file import to bypass broken __init__
sys.path.insert(0, str(Path(__file__).parent))
import backend.core.evoki_metrics_v3.metrics_complete_v3 as metrics_v3

print("Testing metrics calculation...")
text = "Ich habe Angst und kann nicht mehr"
result = metrics_v3.calculate_full_spectrum(text, prev_text="")

print(f"✅ m1_A (Affekt): {result.m1_A:.3f}")
print(f"✅ m101_t_panic (Panik): {result.m101_t_panic:.3f}")
print(f"✅ m102_t_disso (Dissoziation): {result.m102_t_disso:.3f}")
print(f"✅ m19_z_prox (Kollaps-Nähe): {result.m19_z_prox:.3f}")
print("✅ METRIKEN FUNKTIONIEREN!")
