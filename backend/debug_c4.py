# -*- coding: utf-8 -*-
"""
Debug C4 False Positive Issue

Test context adjuster on C4 case directly.
"""

import sys
sys.path.insert(0, 'backend')

from core.evoki_metrics_v3.context_adjusters import (
    detect_positive_context, 
    detect_negative_context,
    adjust_panic_for_context
)
from core.evoki_metrics_v3.emotions import compute_m80_fear, compute_m78_sadness, compute_m77_joy

# C4 test case
c4_text = "Vielen Dank für deine Hilfe. Das hat mir sehr geholfen."

print("="*70)
print("DEBUG: C4 False Positive Analysis")
print("="*70)
print(f"\nText: {c4_text}")
print()

# Step 1: Check context detection
print("Step 1: Context Detection")
print("-"*70)
has_positive = detect_positive_context(c4_text)
has_negative = detect_negative_context(c4_text)
print(f"Positive context: {has_positive}")
print(f"Negative context: {has_negative}")
print()

# Step 2: Get emotions
print("Step 2: Emotion Analysis")
print("-"*70)
fear = compute_m80_fear(c4_text)
sadness = compute_m78_sadness(c4_text)
joy = compute_m77_joy(c4_text)
print(f"Fear: {fear:.3f}")
print(f"Sadness: {sadness:.3f}")
print(f"Joy: {joy:.3f}")
print()

# Step 3: Check if "Hilfe" triggers
print("Step 3: Panic Keyword Check")
print("-"*70)
panic_keywords = ["hilfe", "panik", "angst", "luft", "herz"]
has_panic_keywords = any(kw in c4_text.lower() for kw in panic_keywords)
print(f"Has panic keywords: {has_panic_keywords}")
if has_panic_keywords:
    found = [kw for kw in panic_keywords if kw in c4_text.lower()]
    print(f"Found: {found}")
print()

# Step 4: Base Panic Score
print("Step 4: Base Panic Score")
print("-"*70)
base_panic = fear
print(f"Base panic (from fear): {base_panic:.3f}")
print()

# Step 5: Apply context adjuster
print("Step 5: Context Adjuster")
print("-"*70)
adjusted_panic = adjust_panic_for_context(c4_text, base_panic)
print(f"Before: {base_panic:.3f}")
print(f"After:  {adjusted_panic:.3f}")
print(f"Change: {(adjusted_panic - base_panic):.3f} ({((adjusted_panic / base_panic - 1) * 100) if base_panic > 0 else 0:.1f}%)")
print()

# Step 6: Final crisis score
print("Step 6: Final Crisis Score")
print("-"*70)
print(f"Threshold: 0.20")
print(f"Crisis score: {adjusted_panic:.3f}")
print(f"Above threshold: {adjusted_panic >= 0.20}")
print()

print("="*70)
print("EXPECTED: Crisis score should be < 0.20")
print(f"ACTUAL: {adjusted_panic:.3f} {'✅ PASS' if adjusted_panic < 0.20 else '🔴 FAIL'}")
print("="*70)
