# -*- coding: utf-8 -*-
"""
Debug CF7 - Temporal Recovery Context

Test context adjuster on CF7: "Früher brauchte ich Hilfe, aber jetzt besser. Danke!"
"""

import sys
sys.path.insert(0, 'backend')

from core.evoki_metrics_v3.context_adjusters import (
    detect_positive_context, 
    detect_negative_context,
    adjust_panic_for_context
)
from core.evoki_metrics_v3.emotions import compute_m80_fear, compute_m78_sadness
from core.evoki_metrics_v3 import crisis_scoring as crisis

# CF7 test case
cf7_text = "Früher brauchte ich Hilfe, aber jetzt geht es mir besser. Danke!"

print("="*70)
print("DEBUG: CF7 Temporal Recovery Context")
print("="*70)
print(f"\nText: {cf7_text}")
print()

# Step 1: Check context detection
print("Step 1: Context Detection")
print("-"*70)
has_positive = detect_positive_context(cf7_text)
has_negative = detect_negative_context(cf7_text)
print(f"Positive context: {has_positive}")
print(f"Negative context: {has_negative}")

# Show which markers triggered
from core.evoki_metrics_v3.context_adjusters import POSITIVE_CONTEXT_WORDS
found_markers = [w for w in POSITIVE_CONTEXT_WORDS if w in cf7_text.lower()]
print(f"Found markers: {found_markers}")
print()

# Step 2: Get emotions
print("Step 2: Emotion Analysis")
print("-"*70)
fear = compute_m80_fear(cf7_text)
sadness = compute_m78_sadness(cf7_text)
print(f"Fear: {fear:.3f}")
print(f"Sadness: {sadness:.3f}")
print()

# Step 3: Check if "Hilfe" triggers
print("Step 3: Panic Keyword Check")
print("-"*70)
panic_keywords = ["hilfe", "panik", "angst", "luft", "herz"]
has_panic_keywords = any(kw in cf7_text.lower() for kw in panic_keywords)
print(f"Has panic keywords: {has_panic_keywords}")
if has_panic_keywords:
    found = [kw for kw in panic_keywords if kw in cf7_text.lower()]
    print(f"Found: {found}")
print()

# Step 4: Base crisis score (max of sadness, fear before adjustment)
print("Step 4: Base Crisis Score (Before Context Adjuster)")
print("-"*70)
base_crisis = max(sadness, fear)
print(f"Base crisis (max(sadness, fear)): {base_crisis:.3f}")
print()

# Step 5: Apply context adjuster manually
print("Step 5: Context Adjuster (Manual)")
print("-"*70)
if has_panic_keywords:
    adjusted_panic = adjust_panic_for_context(cf7_text, fear)
    print(f"Fear before: {fear:.3f}")
    print(f"Fear after:  {adjusted_panic:.3f}")
    print(f"Change: {(adjusted_panic - fear):.3f} ({((adjusted_panic / fear - 1) * 100) if fear > 0 else 0:.1f}%)")
    final_crisis = max(sadness, adjusted_panic)
else:
    final_crisis = base_crisis
    print("No panic keywords, using base score")
print(f"\nFinal crisis score: {final_crisis:.3f}")
print()

# Step 6: Full pipeline test
print("Step 6: Full Pipeline Test")
print("-"*70)
pipeline_score, category = crisis.compute_crisis_auto(
    cf7_text,
    test_name="CF7_Positive_Past"
)
print(f"Pipeline crisis score: {pipeline_score:.3f}")
print(f"Category: {category}")
print()

print("="*70)
print(f"EXPECTED: Crisis score should be < 0.20")
print(f"ACTUAL: {pipeline_score:.3f} {'✅ PASS' if pipeline_score < 0.20 else '🔴 FAIL'}")
print("="*70)
