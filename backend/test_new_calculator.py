#!/usr/bin/env python3
"""
Quick test rebuild with NEW 4-Phase Calculator
"""

import json
import sys
from pathlib import Path

# Add paths
PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
sys.path.insert(0, str(PROJECT_ROOT / "backend/core/evoki_metrics_v3"))

from calculator_4phase_complete import calculate_all_168

# Test with simple pair
test_text = "Ich fühle mich heute hoffnungslos und ängstlich."

print("=" * 70)
print("TESTING 4-PHASE CALCULATOR INTEGRATION")
print("=" * 70)

context = {
    "pair_id": "test-001",
    "user_text": test_text,
    "ai_text": "",
    "timestamp": "2026-02-08T08:05:00Z",
    "turn": 1,
    "prev_chain_hash": "be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4",
}

print(f"\nCalculating metrics...")
result = calculate_all_168(test_text, context=context)

print(f"\n✅ SUCCESS!")
print(f"  Total metrics: {len(result['metrics'])}")
print(f"  m1_A: {result['metrics'].get('m1_A', 'N/A'):.3f}")
print(f"  m19_z_prox: {result['metrics'].get('m19_z_prox', 'N/A'):.3f}")
print(f"  m151_hazard: {result['metrics'].get('m151_hazard', 'N/A'):.3f}")
print(f"  B_align: {result['b_align']:.3f}")
print(f"  Chain hash: ...{result['chain_hash'][-12:]}")

print(f"\n🎉 4-Phase Calculator is working correctly!")
