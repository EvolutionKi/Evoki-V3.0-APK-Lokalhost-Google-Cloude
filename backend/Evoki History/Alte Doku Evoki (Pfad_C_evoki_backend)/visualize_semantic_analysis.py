#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualisierung der Semantischen Anomalie-Analyse
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from collections import defaultdict
import os

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# Lade Analysen
json_file = r"C:\evoki\backend\semantic_anomaly_analysis.json"
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

summary = data['summary']
critical_findings = data['critical_findings']

# Extrahiere Daten
risk_dist = summary['risk_distribution']
risk_levels = list(risk_dist.keys())
risk_counts = list(risk_dist.values())

# Statistik über kritische Anomalien
trauma_count = sum(1 for c in critical_findings if 'TRAUMA' in c['risk']['factors'])
stress_count = sum(1 for c in critical_findings if 'STRESS' in c['risk']['factors'])
vulnerability_count = sum(1 for c in critical_findings if 'VULNERABILITY' in c['risk']['factors'])
crisis_count = sum(1 for c in critical_findings if 'CRISIS' in c['risk']['factors'])
ai_unusual_count = sum(1 for c in critical_findings if 'AI_UNUSUAL' in c['risk']['factors'])

# Erstelle Figur
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

# Plot 1: Risiko-Verteilung (Pie-Chart)
ax1 = fig.add_subplot(gs[0, 0])
colors = ['#2ECC71', '#F39C12', '#E74C3C', '#C0392B', '#8B0000']
explode = (0, 0, 0, 0.1, 0.2)
wedges, texts, autotexts = ax1.pie(risk_counts, labels=risk_levels, autopct='%1.1f%%',
                                     colors=colors, explode=explode, startangle=90)
ax1.set_title('Risiko-Level Verteilung\n(alle 1194 Anomalien)', fontsize=13, fontweight='bold')

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(10)

# Plot 2: Faktoren in kritischen Anomalien
ax2 = fig.add_subplot(gs[0, 1])
factors = ['TRAUMA', 'VULNERABILITY', 'CRISIS', 'AI_UNUSUAL', 'STRESS']
factor_counts = [trauma_count, vulnerability_count, crisis_count, ai_unusual_count, stress_count]
colors_bar = ['#8B0000', '#FF6B6B', '#E74C3C', '#9B59B6', '#F39C12']

bars = ax2.barh(factors, factor_counts, color=colors_bar, edgecolor='black', linewidth=2)
ax2.set_xlabel('Anzahl kritischer Anomalien mit Faktor', fontsize=11, fontweight='bold')
ax2.set_title('Häufigste Faktoren bei kritischen/hohen Anomalien\n(57 Anomalien)', fontsize=13, fontweight='bold')
ax2.grid(axis='x', alpha=0.3, linestyle='--')

# Beschriftung
for i, (bar, count) in enumerate(zip(bars, factor_counts)):
    ax2.text(count, i, f' {count}', va='center', fontweight='bold', fontsize=11)

# Plot 3: Zeitliche Verteilung kritischer Anomalien
ax3 = fig.add_subplot(gs[1, 0])

months_data = defaultdict(int)
for c in critical_findings:
    month = c['month']
    months_data[month] += 1

months_sorted = sorted(months_data.keys())
counts_sorted = [months_data[m] for m in months_sorted]
month_labels = [m.replace('-', '/') for m in months_sorted]

bars3 = ax3.bar(range(len(month_labels)), counts_sorted, color='#C0392B', alpha=0.7, edgecolor='darkred', linewidth=2)
ax3.set_xlabel('Monat', fontsize=11, fontweight='bold')
ax3.set_ylabel('Anzahl kritischer Anomalien', fontsize=11, fontweight='bold')
ax3.set_title('Zeitliche Verteilung kritischer/hoher Anomalien', fontsize=13, fontweight='bold')
ax3.set_xticks(range(len(month_labels)))
ax3.set_xticklabels(month_labels, rotation=45, ha='right')
ax3.grid(axis='y', alpha=0.3, linestyle='--')

# Beschriftung
for bar, count in zip(bars3, counts_sorted):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}',
            ha='center', va='bottom', fontweight='bold', fontsize=10)

# Plot 4: Risiko-Score Verteilung
ax4 = fig.add_subplot(gs[1, 1])

# Berechne Risiko-Scores für alle kritischen
scores = [c['risk']['score'] for c in critical_findings]
ax4.hist(scores, bins=range(min(scores)-1, max(scores)+2), color='#E74C3C', alpha=0.7, edgecolor='black', linewidth=2)
ax4.set_xlabel('Risiko-Score', fontsize=11, fontweight='bold')
ax4.set_ylabel('Häufigkeit', fontsize=11, fontweight='bold')
ax4.set_title('Verteilung der Risiko-Scores\n(kritische und hohe Anomalien)', fontsize=13, fontweight='bold')
ax4.grid(axis='y', alpha=0.3, linestyle='--')

# Gesamttitel
fig.suptitle('Semantische Anomalie-Analyse: Trauma, Stress, Verletzlichkeit, Notlagen', 
            fontsize=16, fontweight='bold', y=0.995)

# Speichere
output_dir = r"C:\evoki\backend\timewrap_charts"
os.makedirs(output_dir, exist_ok=True)
filepath = os.path.join(output_dir, "03_SEMANTIC_ANALYSIS_risk_factors.png")
plt.savefig(filepath, dpi=300, bbox_inches='tight')
print(f"[OK] Gespeichert: 03_SEMANTIC_ANALYSIS_risk_factors.png")
plt.close()

# Erstelle zweites Diagramm: Top kritische Anomalien mit Details
fig, axes = plt.subplots(3, 1, figsize=(16, 12))
fig.suptitle('Top 15 kritische Anomalien - Detailansicht', fontsize=16, fontweight='bold')

# Sortiere nach Score
sorted_critical = sorted(critical_findings, key=lambda x: -x['risk']['score'])[:15]

# Subplot 1: Risiko-Scores
ax = axes[0]
indices = list(range(1, len(sorted_critical) + 1))
scores = [c['risk']['score'] for c in sorted_critical]
colors = ['#8B0000' if s >= 15 else '#C0392B' for s in scores]

bars = ax.bar(indices, scores, color=colors, edgecolor='black', linewidth=2)
ax.set_ylabel('Risiko-Score', fontsize=11, fontweight='bold')
ax.set_title('Risiko-Scores der Top 15 kritischen Anomalien', fontsize=12, fontweight='bold')
ax.set_xlabel('Anomalie-Ranking', fontsize=11, fontweight='bold')
ax.grid(axis='y', alpha=0.3, linestyle='--')

for i, (bar, score) in enumerate(zip(bars, scores)):
    height = bar.get_height()
    ax.text(i+1, height, f'{int(score)}', ha='center', va='bottom', fontweight='bold', fontsize=10)

# Subplot 2: Faktoren-Mix
ax = axes[1]
factor_matrix = []
for c in sorted_critical:
    factors_present = [
        1 if 'TRAUMA' in c['risk']['factors'] else 0,
        1 if 'STRESS' in c['risk']['factors'] else 0,
        1 if 'VULNERABILITY' in c['risk']['factors'] else 0,
        1 if 'CRISIS' in c['risk']['factors'] else 0,
        1 if 'AI_UNUSUAL' in c['risk']['factors'] else 0,
    ]
    factor_matrix.append(factors_present)

factor_matrix = np.array(factor_matrix)
im = ax.imshow(factor_matrix.T, cmap='Reds', aspect='auto')

ax.set_yticks(range(5))
ax.set_yticklabels(['TRAUMA', 'STRESS', 'VULNERABILITY', 'CRISIS', 'AI_UNUSUAL'], fontsize=10)
ax.set_xticks(range(len(sorted_critical)))
ax.set_xticklabels([f"#{c['index']}" for c in sorted_critical], fontsize=9)
ax.set_xlabel('Anomalie #', fontsize=11, fontweight='bold')
ax.set_title('Faktoren-Mix der Top 15', fontsize=12, fontweight='bold')

# Colorbar
cbar = plt.colorbar(im, ax=ax, orientation='vertical')
cbar.set_label('Präsent', fontsize=10)

# Subplot 3: Zeitsprung-Größe
ax = axes[2]
gaps = [abs(c['gap_days']) for c in sorted_critical]
bars = ax.bar(indices, gaps, color='#3498DB', alpha=0.7, edgecolor='darkblue', linewidth=2)
ax.set_ylabel('Zeitsprung (Tage)', fontsize=11, fontweight='bold')
ax.set_xlabel('Anomalie-Ranking', fontsize=11, fontweight='bold')
ax.set_title('Größe der Zeitsprünge bei kritischen Anomalien', fontsize=12, fontweight='bold')
ax.set_yscale('log')
ax.grid(axis='y', alpha=0.3, linestyle='--')

for i, (bar, gap) in enumerate(zip(bars, gaps)):
    height = bar.get_height()
    ax.text(i+1, height*1.5, f'{gap:.1f}d', ha='center', va='bottom', fontweight='bold', fontsize=8)

plt.tight_layout()
filepath = os.path.join(output_dir, "04_TOP_CRITICAL_ANOMALIES.png")
plt.savefig(filepath, dpi=300, bbox_inches='tight')
print(f"[OK] Gespeichert: 04_TOP_CRITICAL_ANOMALIES.png")
plt.close()

print("\n[OK] Alle Diagramme generiert!")
