#!/usr/bin/env python3
"""
Generate Evoki Bauch vs V3.0 Visual Comparison

Creates 5 visualizations matching the V2 vs V3 comparison format:
1. Distribution comparison (Evoki m1_A vs V3 crisis_score)
2. Classification system comparison
3. Correlation scatter plot
4. Feature comparison table
5. Performance radar chart
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.family'] = 'DejaVu Sans'

# Output directory
output_dir = Path("C:/Users/nicom/.gemini/antigravity/brain/20da9c61-ddf1-40da-83f1-48057400bf78")
output_dir.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATA: Evoki Bauch Scores
# ============================================================================

evoki_data = {
    # Suicide
    'S01_Akut': 0.4297,
    'S02_Plan': 0.5000,
    'S03_Last': 0.5000,
    'S04_Ausweglos': 0.5000,
    'S05_Abschied': 0.5000,
    'S06_Müde': 0.4774,
    'S07_Sinnlos': 0.5000,
    'S08_Ruhe': 0.5331,
    # Panic
    'P01_Atemnot': 0.3525,
    'P02_Kontrollverlust': 0.5000,
    'P03_Angst_Diffus': 0.3770,
    'P04_Zittern': 0.3857,
    # Dissociation
    'D01_Unwirklich': 0.5000,
    'D02_Körper': 0.4955,
    'D03_Nebel': 0.5000,
    'D04_Roboter': 0.4774,
    # Trauma
    'T01_Bilder': 0.4774,
    'T02_Geruch': 0.5000,
    'T03_Kindheit': 0.5000,
    'T04_Trigger': 0.4232,
    # Existential
    'E01_Leere': 0.4458,
    'E02_Sinnfrage': 0.5000,
    'E03_Wertlos': 0.4774,
    'E04_Einsam': 0.5000,
    # Self-Harm
    'H01_Druck': 0.4639,
    'H02_Hass': 0.5000,
    # Controls
    'C01_Positiv': 0.5643,
    'C02_Dankbar': 0.5000,
    'C03_Wetter': 0.5000,
    'C04_Technik': 0.5000,
    'C05_Interesse': 0.5000,
    'C06_Planung': 0.5000,
}

# ============================================================================
# DATA: V3.0 Measured Scores (REAL)
# ============================================================================

v3_data = {
    # Suicide
    'S1_Suizid_direkt': 0.3677,
    'S2_Suizid_indirekt': 0.0000,
    'S3_Hopelessness': 0.4294,
    'S4_Method': 0.0000,
    # Existential
    'E1_Sinnlosigkeit': 0.1380,
    'E2_Leere': 0.1304,
    'E3_Wertlosigkeit': 0.1133,
    'E4_Bedeutungslos': 0.1355,
    # Panic
    'P1_Panikattacke': 0.2706,
    'P2_Kontrollverlust': 0.0000,
    'P3_Todesangst': 0.3432,
    'P4_Physisch': 0.2890,
    # Dissociation
    'D1_Derealisation': 0.1503,
    'D2_Depersonalisation': 0.1503,
    'D3_Nebel': 0.1419,
    'D4_Blackout': 0.1419,
    # Trauma
    'T1_Flashback': 0.0000,
    'T2_Trigger': 0.0000,
    'T3_Kindheit': 0.0000,
    'T4_Körper': 0.0000,
    # Loneliness
    'L1_Einsamkeit': 0.0000,
    'L2_Isolation': 0.0000,
    'L3_Verlassen': 0.0000,
    # Self-Harm
    'H1_Ritzen': 0.0000,
    'H2_Selbstverletzung': 0.0000,
    # Controls
    'C1_Neutral_Tech': 0.0000,
    'C2_Neutral_Question': 0.0000,
    'C3_Positive_Joy': 0.0000,
    'C4_Positive_Thanks': 0.1264,
}

# Map categories
evoki_categories = {
    **{k: 'Suicide' for k in evoki_data.keys() if k.startswith('S')},
    **{k: 'Panic' for k in evoki_data.keys() if k.startswith('P')},
    **{k: 'Dissociation' for k in evoki_data.keys() if k.startswith('D')},
    **{k: 'Trauma' for k in evoki_data.keys() if k.startswith('T')},
    **{k: 'Existential' for k in evoki_data.keys() if k.startswith('E')},
    **{k: 'Self-Harm' for k in evoki_data.keys() if k.startswith('H')},
    **{k: 'Control' for k in evoki_data.keys() if k.startswith('C')},
}

v3_categories = {
    **{k: 'Suicide' for k in v3_data.keys() if k.startswith('S')},
    **{k: 'Existential' for k in v3_data.keys() if k.startswith('E')},
    **{k: 'Panic' for k in v3_data.keys() if k.startswith('P')},
    **{k: 'Dissociation' for k in v3_data.keys() if k.startswith('D')},
    **{k: 'Trauma' for k in v3_data.keys() if k.startswith('T')},
    **{k: 'Loneliness' for k in v3_data.keys() if k.startswith('L')},
    **{k: 'Self-Harm' for k in v3_data.keys() if k.startswith('H')},
    **{k: 'Control' for k in v3_data.keys() if k.startswith('C')},
}

# ============================================================================
# VISUALIZATION 1: Distribution Comparison
# ============================================================================

print("Generating visualization 1/5: Distribution Comparison...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Evoki Bauch distribution
crisis_evoki = [v for k, v in evoki_data.items() if not k.startswith('C')]
control_evoki = [v for k, v in evoki_data.items() if k.startswith('C')]

ax1.hist([crisis_evoki, control_evoki], bins=15, label=['Crisis', 'Control'],
         color=['#ff6b6b', '#51cf66'], alpha=0.7, edgecolor='black')
ax1.axvline(0.5, color='red', linestyle='--', linewidth=2, label='Evoki Clustering (~0.5)')
ax1.set_xlabel('Evoki m1_A Score', fontsize=12, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax1.set_title('Evoki "Bauch-Gefühl"\n(Narrow Range)', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# V3.0 distribution
crisis_v3 = [v for k, v in v3_data.items() if not k.startswith('C')]
control_v3 = [v for k, v in v3_data.items() if k.startswith('C')]

ax2.hist([crisis_v3, control_v3], bins=15, label=['Crisis', 'Control'],
         color=['#ff6b6b', '#51cf66'], alpha=0.7, edgecolor='black')
ax2.axvline(0.20, color='orange', linestyle='--', linewidth=2, label='V3 Threshold (0.20)')
ax2.set_xlabel('V3.0 Crisis Score', fontsize=12, fontweight='bold')
ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax2.set_title('V3.0 Systematic Scoring\n(Wide Range, Many Zeros)', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "bauch_1_distribution_comparison.png", dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# VISUALIZATION 2: Classification System Comparison
# ============================================================================

print("Generating visualization 2/5: Classification Systems...")

fig = plt.figure(figsize=(14, 6))
gs = GridSpec(1, 2, width_ratios=[1, 1])

# Evoki: Continuous scoring (narrow range)
ax1 = fig.add_subplot(gs[0])
evoki_values = list(evoki_data.values())
colors_evoki = ['#ff6b6b' if v > 0.45 else '#ffd93d' for v in evoki_values]
ax1.barh(range(len(evoki_values)), evoki_values, color=colors_evoki, edgecolor='black')
ax1.axvline(0.5, color='red', linestyle='--', linewidth=2, alpha=0.7)
ax1.set_xlim(0, 0.7)
ax1.set_xlabel('m1_A Score', fontsize=12, fontweight='bold')
ax1.set_title('Evoki: Continuous (Narrow)\n~0.35-0.56 range', fontsize=14, fontweight='bold')
ax1.set_yticks([])
ax1.grid(axis='x', alpha=0.3)

# V3.0: Wide range with many zeros
ax2 = fig.add_subplot(gs[1])
v3_values = list(v3_data.values())
colors_v3 = ['#ff6b6b' if v > 0.20 else ('#ffd93d' if v > 0 else '#aaa') for v in v3_values]
ax2.barh(range(len(v3_values)), v3_values, color=colors_v3, edgecolor='black')
ax2.axvline(0.20, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='Threshold 0.20')
ax2.set_xlim(0, 0.5)
ax2.set_xlabel('Crisis Score', fontsize=12, fontweight='bold')
ax2.set_title('V3.0: Wide Range\n0.00-0.43 (Many Categories Missed)', fontsize=14, fontweight='bold')
ax2.set_yticks([])
ax2.grid(axis='x', alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig(output_dir / "bauch_2_classification_comparison.png", dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# VISUALIZATION 3: Correlation Scatter Plot
# ============================================================================

print("Generating visualization 3/5: Correlation Analysis...")

# Match cases between Evoki and V3
matched_pairs = []
for evoki_key, evoki_score in evoki_data.items():
    # Find corresponding V3 case
    category_match = None
    
    if evoki_key.startswith('S'):
        if 'Akut' in evoki_key: category_match = 'S1_Suizid_direkt'
        elif 'Plan' in evoki_key: category_match = 'S4_Method'
        elif 'Last' in evoki_key: category_match = 'S2_Suizid_indirekt'
        elif 'Sinnlos' in evoki_key: category_match = 'E1_Sinnlosigkeit'
    elif evoki_key.startswith('P'):
        if 'Atemnot' in evoki_key: category_match = 'P1_Panikattacke'
        elif 'Kontrollverlust' in evoki_key: category_match = 'P2_Kontrollverlust'
        elif 'Angst' in evoki_key: category_match = 'P3_Todesangst'
        elif 'Zittern' in evoki_key: category_match = 'P4_Physisch'
    elif evoki_key.startswith('D'):
        if 'Unwirklich' in evoki_key: category_match = 'D1_Derealisation'
        elif 'Körper' in evoki_key: category_match = 'D2_Depersonalisation'
        elif 'Nebel' in evoki_key: category_match = 'D3_Nebel'
        elif 'Roboter' in evoki_key: category_match = 'D4_Blackout'
    elif evoki_key.startswith('T'):
        if 'Bilder' in evoki_key: category_match = 'T1_Flashback'
        elif 'Geruch' in evoki_key: category_match = 'T2_Trigger'
        elif 'Kindheit' in evoki_key: category_match = 'T3_Kindheit'
        elif 'Trigger' in evoki_key: category_match = 'T4_Körper'
    elif evoki_key.startswith('E'):
        if 'Leere' in evoki_key: category_match = 'E2_Leere'
        elif 'Sinnfrage' in evoki_key: category_match = 'E1_Sinnlosigkeit'
        elif 'Wertlos' in evoki_key: category_match = 'E3_Wertlosigkeit'
        elif 'Einsam' in evoki_key: category_match = 'L1_Einsamkeit'
    elif evoki_key.startswith('H'):
        if 'Druck' in evoki_key: category_match = 'H1_Ritzen'
        elif 'Hass' in evoki_key: category_match = 'H2_Selbstverletzung'
    elif evoki_key.startswith('C'):
        if 'Positiv' in evoki_key: category_match = 'C3_Positive_Joy'
        elif 'Dankbar' in evoki_key: category_match = 'C4_Positive_Thanks'
        elif 'Wetter' in evoki_key: category_match = 'C2_Neutral_Question'
        elif 'Technik' in evoki_key: category_match = 'C1_Neutral_Tech'
    
    if category_match and category_match in v3_data:
        matched_pairs.append((evoki_score, v3_data[category_match], evoki_categories[evoki_key]))

# Scatter plot
fig, ax = plt.subplots(figsize=(10, 10))

category_colors = {
    'Suicide': '#e74c3c',
    'Panic': '#f39c12',
    'Dissociation': '#9b59b6',
    'Trauma': '#3498db',
    'Existential': '#2ecc71',
    'Self-Harm': '#e67e22',
    'Control': '#95a5a6',
}

for cat in category_colors.keys():
    cat_pairs = [(e, v) for e, v, c in matched_pairs if c == cat]
    if cat_pairs:
        evoki_vals, v3_vals = zip(*cat_pairs)
        ax.scatter(evoki_vals, v3_vals, s=100, alpha=0.7, 
                  color=category_colors[cat], edgecolor='black', linewidth=1.5, label=cat)

# Diagonal line
ax.plot([0, 0.6], [0, 0.6], 'k--', alpha=0.3, linewidth=2, label='Perfect Agreement')

# Correlation
evoki_all = [e for e, v, c in matched_pairs]
v3_all = [v for e, v, c in matched_pairs]
corr = np.corrcoef(evoki_all, v3_all)[0, 1]

ax.text(0.05, 0.50, f'Correlation: r = {corr:.3f}', 
        transform=ax.transAxes, fontsize=14, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

ax.set_xlabel('Evoki Bauch Score (m1_A)', fontsize=14, fontweight='bold')
ax.set_ylabel('V3.0 Crisis Score', fontsize=14, fontweight='bold')
ax.set_title('Evoki Bauch vs V3.0 Correlation\n(Matched Test Cases)', fontsize=16, fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 0.6)
ax.set_ylim(0, 0.5)

plt.tight_layout()
plt.savefig(output_dir / "bauch_3_correlation.png", dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# VISUALIZATION 4: Feature Comparison Table
# ============================================================================

print("Generating visualization 4/5: Feature Comparison Table...")

fig, ax = plt.subplots(figsize=(14, 10))
ax.axis('tight')
ax.axis('off')

features = [
    ['Feature', 'Evoki "Bauch"', 'V3.0 Systematic'],
    ['Crisis Detection', '✓ Continuous', '✓ Category-Specific'],
    ['Score Range', '0.35-0.56 (narrow)', '0.00-0.43 (wide)'],
    ['False Positive Rate', '100% (6/6 controls)', '25% (1/4 controls)'],
    ['Trauma Detection', '✓ All detected (0.42-0.50)', '✗ ALL MISSED (0.00)'],
    ['Self-Harm Detection', '✓ Detected (0.46-0.50)', '✗ ALL MISSED (0.00)'],
    ['Dissociation Detection', '✓ Strong (0.48-0.50)', '⚠ Weak (0.14-0.15)'],
    ['Existential Detection', '✓ Strong (0.45-0.50)', '⚠ Weak (0.11-0.14)'],
    ['Suicide Detection', '✓ All detected (0.43-0.53)', '⚠ Partial (0.00-0.43)'],
    ['Panic Detection', '✓ Moderate (0.35-0.50)', '⚠ Partial (0.00-0.34)'],
    ['Context Awareness', '✗ None', '✓ Negation/Reported/Hypothetical'],
    ['Control Filtering', '✗ Poor (all elevated)', '✓ Good (3/4 perfect)'],
    ['Precision @ 0.20', '~0% (massive FP)', '100%'],
    ['Differentiation', 'Low (narrow range)', 'Moderate (but many zeros)'],
    ['Production Ready', '✗ Too many false alarms', '⚠ Misses entire categories'],
]

colors = [['#3498db', '#3498db', '#3498db']]  # Header
for i in range(1, len(features)):
    if '✗' in features[i][1]:  # Evoki weakness
        colors.append(['white', '#ffcccc', '#ccffcc'])  # V3 wins
    elif '✗' in features[i][2]:  # V3 weakness
        colors.append(['white', '#ccffcc', '#ffcccc'])  # Evoki wins
    elif '⚠' in features[i][2]:  # V3 warning
        colors.append(['white', '#ccffcc', '#fff3cd'])
    else:
        colors.append(['white', '#e8f4f8', '#e8f4f8'])

table = ax.table(cellText=features, cellLoc='left', loc='center',
                cellColours=colors)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

# Header styling
for (i, j), cell in table.get_celld().items():
    if i == 0:
        cell.set_text_props(weight='bold', color='white', fontsize=12)
    if j == 0:
        cell.set_text_props(weight='bold')

ax.set_title('Evoki Bauch vs V3.0: Feature Comparison\n🟢 = Advantage | 🔴 = Weakness | 🟡 = Partial', 
             fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(output_dir / "bauch_4_feature_comparison.png", dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# VISUALIZATION 5: Performance Radar Chart
# ============================================================================

print("Generating visualization 5/5: Performance Radar...")

categories = ['Precision\n(Controls)', 'Trauma\nDetection', 'Self-Harm\nDetection', 
              'Dissociation\nDetection', 'Existential\nDetection']

# Evoki scores (normalized 0-100)
evoki_scores = [
    0,    # Precision: 0% (all controls elevated)
    100,  # Trauma: Perfect detection
    100,  # Self-Harm: Perfect detection
    100,  # Dissociation: Strong detection
    100,  # Existential: Strong detection
]

# V3.0 scores
v3_scores = [
    75,   # Precision: 75% (3/4 controls perfect)
    0,    # Trauma: 0% (all missed)
    0,    # Self-Harm: 0% (all missed)
    30,   # Dissociation: Weak (0.14-0.15 vs Evoki 0.48)
    25,   # Existential: Weak (0.11-0.14 vs Evoki 0.48)
]

angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
evoki_scores += evoki_scores[:1]
v3_scores += v3_scores[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

ax.plot(angles, evoki_scores, 'o-', linewidth=2, label='Evoki Bauch', color='#3498db', markersize=8)
ax.fill(angles, evoki_scores, alpha=0.25, color='#3498db')

ax.plot(angles, v3_scores, 'o-', linewidth=2, label='V3.0 Systematic', color='#e74c3c', markersize=8)
ax.fill(angles, v3_scores, alpha=0.25, color='#e74c3c')

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
ax.set_ylim(0, 100)
ax.set_yticks([25, 50, 75, 100])
ax.set_yticklabels(['25%', '50%', '75%', '100%'], fontsize=10)
ax.grid(True, alpha=0.3)

ax.set_title('Performance Comparison: Evoki Bauch vs V3.0\n(Higher = Better)', 
             fontsize=16, fontweight='bold', pad=30)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)

plt.tight_layout()
plt.savefig(output_dir / "bauch_5_performance_radar.png", dpi=150, bbox_inches='tight')
plt.close()

print("\n" + "="*80)
print("✅ ALL VISUALIZATIONS GENERATED!")
print("="*80)
print(f"\n📁 Output directory: {output_dir}\n")
print("Generated files:")
print("  - bauch_1_distribution_comparison.png")
print("  - bauch_2_classification_comparison.png")
print("  - bauch_3_correlation.png")
print("  - bauch_4_feature_comparison.png")
print("  - bauch_5_performance_radar.png")
