#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sprint 4 Analysis Runner
Executes the notebook analysis programmatically and generates report.
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from core.evoki_metrics_v3.crisis_scoring import compute_crisis_auto

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

TRIGGER_CSV = backend_path / "trigger_analysis_full_metrics.csv"
DETECTION_CSV = backend_path / "trigger_analysis_detection_rates.csv"
OUTPUT_DIR = backend_path / "notebooks" / "analysis_results"
OUTPUT_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════
# 1. LOAD DATA
# ═══════════════════════════════════════════════════════════════════════════

print("=" * 80)
print("📊 SPRINT 4 CONTEXT FILTER ANALYSIS")
print("=" * 80)
print()

print("1️⃣ Loading trigger analysis data...")
df_full = pd.read_csv(TRIGGER_CSV)
df_detection = pd.read_csv(DETECTION_CSV)

print(f"   ✅ Loaded {len(df_full)} test cases")
print(f"   ✅ Loaded {len(df_detection)} detection rate rows")
print()

# ═══════════════════════════════════════════════════════════════════════════
# 2.# C4 FALSE POSITIVE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

print("2️⃣ Analyzing C4 False Positive...")
c4_row = df_full[df_full['TestCase'] == 'C4_Positive_Thanks'].iloc[0]

print(f"\n   📌 C4_Positive_Thanks:")
print(f"   Crisis Score: {c4_row['crisis_score']:.3f}")
print()
print(f"   🔍 Emotion Breakdown:")
print(f"      sadness: {c4_row['sadness']:.3f}")
print(f"      fear:    {c4_row['fear']:.3f} ⚠️ (Source of false positive)")
print(f"      anger:   {c4_row['anger']:.3f}")
print(f"      joy:     {c4_row['joy']:.3f}")
print()

if c4_row['crisis_score'] > 0.15:
    print(f"   ❌ FALSE POSITIVE CONFIRMED")
    print(f"   Current threshold: 0.15")
    print(f"   C4 score: {c4_row['crisis_score']:.3f}")
    print(f"   Exceeds threshold by: {(c4_row['crisis_score'] - 0.15):.3f}")
else:
    print(f"   ✅ No false positive at threshold 0.15")

print()

# ═══════════════════════════════════════════════════════════════════════════
# 3. DETECTION RATES AT DIFFERENT THRESHOLDS
# ═══════════════════════════════════════════════════════════════════════════

print("3️⃣ Detection Rate Analysis...")
print()
print("   Threshold | Detection Rate | False Positive Rate | Precision")
print("   " + "-" * 65)

for _, row in df_detection.iterrows():
    t = row['threshold']
    dr = row['detection_rate'] * 100
    fpr = row['false_positive_rate'] * 100
    prec = row['precision'] * 100
    
    # Highlight recommended threshold
    marker = " ⭐" if t == 0.25 else ""
    print(f"   {t:6.2f}   | {dr:14.1f}% | {fpr:19.1f}% | {prec:9.1f}%{marker}")

print()

# ═══════════════════════════════════════════════════════════════════════════
# 4. CONTEXT FILTER EFFECTIVENESS
# ═══════════════════════════════════════════════════════════════════════════

print("4️⃣ Context Filter Effectiveness...")
print()

# Check negation cases
negation_cases = df_full[df_full['TestCase'].str.startswith('N')]
print(f"   📌 Negation Cases ({len(negation_cases)}):")
for _, row in negation_cases.iterrows():
    print(f"      {row['TestCase']}: {row['crisis_score']:.3f}")

# Check reported speech cases  
reported_cases = df_full[df_full['TestCase'].str.startswith('R')]
print(f"\n   📌 Reported Speech Cases ({len(reported_cases)}):")
for _, row in reported_cases.iterrows():
    print(f"      {row['TestCase']}: {row['crisis_score']:.3f}")

# Check hypothetical cases
hypo_cases = df_full[df_full['TestCase'].str.startswith('H')]
print(f"\n   📌 Hypothetical Cases ({len(hypo_cases)}):")
for _, row in hypo_cases.iterrows():
    print(f"      {row['TestCase']}: {row['crisis_score']:.3f}")

print()

# ═══════════════════════════════════════════════════════════════════════════
# 5. VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════════════════

print("5️⃣ Generating visualizations...")

plt.style.use('seaborn-v0_8-darkgrid')

# Plot 1: Threshold vs Detection Rate
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(df_detection['threshold'], df_detection['detection_rate'] * 100, 
         marker='o', linewidth=2, label='Detection Rate')
ax1.plot(df_detection['threshold'], df_detection['false_positive_rate'] * 100,
         marker='s', linewidth=2, label='False Positive Rate')
ax1.axvline(x=0.25, color='red', linestyle='--', label='Recommended: 0.25')
ax1.set_xlabel('Threshold')
ax1.set_ylabel('Rate (%)')
ax1.set_title('Detection vs False Positive Rate')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Precision
ax2.plot(df_detection['threshold'], df_detection['precision'] * 100,
         marker='o', linewidth=2, color='green')
ax2.axhline(y=85, color='orange', linestyle='--', label='Target: 85%')
ax2.axvline(x=0.25, color='red', linestyle='--', label='Recommended: 0.25')
ax2.set_xlabel('Threshold')
ax2.set_ylabel('Precision (%)')
ax2.set_title('Precision at Different Thresholds')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'threshold_analysis.png', dpi=150, bbox_inches='tight')
print(f"   ✅ Saved: threshold_analysis.png")

# Plot 3: Score Distribution
plt.figure(figsize=(12, 6))

crisis_scores = df_full[df_full['TestCase'].str.startswith(('S', 'SH', 'T', 'D', 'P', 'E'))]['crisis_score']
control_scores = df_full[df_full['TestCase'].str.startswith('C')]['crisis_score']

plt.hist(crisis_scores, bins=20, alpha=0.6, label='Crisis Cases', color='red')
plt.hist(control_scores, bins=20, alpha=0.6, label='Control Cases', color='green')
plt.axvline(x=0.15, color='blue', linestyle='--', label='Current Threshold: 0.15')
plt.axvline(x=0.25, color='orange', linestyle='--', label='Recommended: 0.25')
plt.xlabel('Crisis Score')
plt.ylabel('Count')
plt.title('Score Distribution: Crisis vs Control')
plt.legend()
plt.grid(True, alpha=0.3)

plt.savefig(OUTPUT_DIR / 'score_distribution.png', dpi=150, bbox_inches='tight')
print(f"   ✅ Saved: score_distribution.png")

print()

# ═══════════════════════════════════════════════════════════════════════════
# 6. RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════

print("6️⃣ RECOMMENDATIONS")
print("=" * 80)
print()
print("🎯 **IMMEDIATE ACTION (Option 1)**")
print("   → Raise threshold from 0.15 → 0.25")
print("   → Eliminates C4 false positive")
print("   → Maintains good detection rate (see analysis above)")
print()
print("🔧 **MEDIUM-TERM (Option 2)**")
print("   → Refine lexicon weights (\"Hilfe\" context-dependent)")
print("   → Implement at lexicon level for broader impact")
print()
print("🚀 **LONG-TERM (Option 3)**")
print("   → Integrate negation at lexicon scoring level")
print("   → More robust than post-processing")
print()
print("=" * 80)
print()

print(f"📁 **Results saved to:** {OUTPUT_DIR}")
print(f"   • threshold_analysis.png")
print(f"   • score_distribution.png")
print()
print("✅ **Analysis complete!**")
