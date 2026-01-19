#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hochauflösende Visualisierung der Chatverlauf-Analyse
Zeigt Korrelationen zwischen Größe, Prompts, Zeitlöchern
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# Deutsche Schriftart
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# Lade Analysedaten
json_file = r"C:\evoki\backend\chat_size_analysis_detailed.json"
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

monthly = data['monthly_breakdown']

# Extrahiere Daten
months = [m['month'].replace('-', '/') for m in monthly]
sizes = [m['html_size_mb'] for m in monthly]
prompts = [m['prompts'] for m in monthly]
gaps = [m['avg_gap_days'] for m in monthly]
days = [m['days'] for m in monthly]
anomalies = [m['anomalies'] for m in monthly]

x_pos = np.arange(len(months))

# Erstelle Figur mit Subplots
fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Plot 1: Größe und Prompts (dual axis)
ax1 = fig.add_subplot(gs[0, :])
color1 = '#FF6B6B'
color2 = '#4ECDC4'

ax1_twin = ax1.twinx()
bars1 = ax1.bar(x_pos - 0.2, sizes, 0.4, label='HTML-Größe (MB)', color=color1, alpha=0.7, edgecolor='darkred', linewidth=2)
line1 = ax1_twin.plot(x_pos, prompts, 'o-', color=color2, label='Prompts', linewidth=3, markersize=10, markerfacecolor='white', markeredgewidth=2)

ax1.set_xlabel('Monat', fontsize=12, fontweight='bold')
ax1.set_ylabel('HTML-Größe (MB)', fontsize=12, fontweight='bold', color=color1)
ax1_twin.set_ylabel('Anzahl Prompts', fontsize=12, fontweight='bold', color=color2)
ax1.set_title('Chatverlauf-Größe und Prompt-Anzahl pro Monat', fontsize=14, fontweight='bold')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(months, rotation=45, ha='right')
ax1.tick_params(axis='y', labelcolor=color1)
ax1_twin.tick_params(axis='y', labelcolor=color2)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Beschriftung
for i, (bar, prompt) in enumerate(zip(bars1, prompts)):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}MB', 
            ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax1_twin.text(x_pos[i], prompt, f'{int(prompt)}', 
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 2: Zeitlöcher (Größe und Anzahl)
ax2 = fig.add_subplot(gs[1, 0])
ax2_twin = ax2.twinx()

bars2 = ax2.bar(x_pos, gaps, color='#95E1D3', alpha=0.7, edgecolor='darkgreen', linewidth=2, label='Ø Gap (Tage)')
line2 = ax2_twin.plot(x_pos, anomalies, 's-', color='#FF6B6B', linewidth=3, markersize=10, 
                      label='Anzahl Anomalien', markerfacecolor='white', markeredgewidth=2)

ax2.set_xlabel('Monat', fontsize=11, fontweight='bold')
ax2.set_ylabel('Ø Zeitlücke (Tage)', fontsize=11, fontweight='bold', color='darkgreen')
ax2_twin.set_ylabel('Anzahl Zeitsprünge', fontsize=11, fontweight='bold', color='#FF6B6B')
ax2.set_title('Zeitlöcher-Analyse', fontsize=12, fontweight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(months, rotation=45, ha='right')
ax2.tick_params(axis='y', labelcolor='darkgreen')
ax2_twin.tick_params(axis='y', labelcolor='#FF6B6B')
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Beschriftung
for i, (bar, anom) in enumerate(zip(bars2, anomalies)):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}d',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 3: Bytes pro Prompt
ax3 = fig.add_subplot(gs[1, 1])
bytes_per_prompt = [(sizes[i] * 1024 * 1024) / prompts[i] if prompts[i] > 0 else 0 for i in range(len(months))]
bars3 = ax3.bar(x_pos, bytes_per_prompt, color='#A8E6CF', alpha=0.7, edgecolor='darkblue', linewidth=2)
ax3.set_xlabel('Monat', fontsize=11, fontweight='bold')
ax3.set_ylabel('Bytes pro Prompt', fontsize=11, fontweight='bold')
ax3.set_title('Durchschnittliche Prompt-Größe', fontsize=12, fontweight='bold')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(months, rotation=45, ha='right')
ax3.grid(axis='y', alpha=0.3, linestyle='--')

# Beschriftung
for bar, bpp in zip(bars3, bytes_per_prompt):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}B',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 4: Tage mit Aktivität
ax4 = fig.add_subplot(gs[2, 0])
bars4 = ax4.bar(x_pos, days, color='#FFD3B6', alpha=0.7, edgecolor='darkorange', linewidth=2)
ax4.set_xlabel('Monat', fontsize=11, fontweight='bold')
ax4.set_ylabel('Tage mit Aktivität', fontsize=11, fontweight='bold')
ax4.set_title('Aktive Tage pro Monat', fontsize=12, fontweight='bold')
ax4.set_xticks(x_pos)
ax4.set_xticklabels(months, rotation=45, ha='right')
ax4.set_ylim([0, 32])
ax4.axhline(y=31, color='red', linestyle='--', linewidth=2, alpha=0.5, label='31 Tage im Monat')
ax4.grid(axis='y', alpha=0.3, linestyle='--')
ax4.legend(loc='upper right')

# Beschriftung
for bar, d in zip(bars4, days):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 5: Korrelation Größe vs Prompts
ax5 = fig.add_subplot(gs[2, 1])
scatter = ax5.scatter(prompts, sizes, s=200, c=list(range(len(months))), cmap='viridis', 
                      alpha=0.7, edgecolor='black', linewidth=2)

# Trend-Linie
z = np.polyfit(prompts, sizes, 1)
p = np.poly1d(z)
ax5.plot(prompts, p(prompts), "r--", linewidth=2, alpha=0.8, label=f'Trend: y={z[0]:.3f}x+{z[1]:.1f}')

ax5.set_xlabel('Anzahl Prompts', fontsize=11, fontweight='bold')
ax5.set_ylabel('HTML-Größe (MB)', fontsize=11, fontweight='bold')
ax5.set_title('Korrelation: Prompts vs. Größe', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3, linestyle='--')
ax5.legend(loc='upper left', fontsize=10)

# Beschrifte Punkte mit Monaten
for i, month in enumerate(months):
    ax5.annotate(month, (prompts[i], sizes[i]), textcoords="offset points", 
                xytext=(0,10), ha='center', fontsize=8, fontweight='bold')

# Colorbar
cbar = plt.colorbar(scatter, ax=ax5)
cbar.set_label('Monat (zeitlich)', fontsize=10)

# Gesamttitel
fig.suptitle('Hochauflösende Chatverlauf-Analyse: Größe, Prompts und Zeitlöcher', 
            fontsize=16, fontweight='bold', y=0.995)

# Speichere Diagramm
output_dir = r"C:\evoki\backend\timewrap_charts"
os.makedirs(output_dir, exist_ok=True)
filepath = os.path.join(output_dir, "01_DETAILED_ANALYSIS_all_metrics.png")
plt.savefig(filepath, dpi=300, bbox_inches='tight')
print(f"[OK] Gespeichert: 01_DETAILED_ANALYSIS_all_metrics.png")
plt.close()

# Erstelle zweites Diagramm: Zeitreihen mit exponentiellen Trends
fig, axes = plt.subplots(2, 2, figsize=(18, 10))
fig.suptitle('Zeitreihen-Trends mit Kurvenanpassung', fontsize=16, fontweight='bold')

x_num = np.arange(len(months))

# Subplot 1: Größe mit exponentieller Anpassung
ax = axes[0, 0]
ax.plot(x_num, sizes, 'o-', linewidth=3, markersize=10, color='#FF6B6B', label='Tatsächliche Größe')
z_poly = np.polyfit(x_num, sizes, 2)
p_poly = np.poly1d(z_poly)
ax.plot(x_num, p_poly(x_num), '--', linewidth=2, color='darkred', label='Polynom (Grad 2)')
ax.set_ylabel('Größe (MB)', fontweight='bold')
ax.set_title('HTML-Größen-Trend', fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_xticks(x_num)
ax.set_xticklabels(months, rotation=45, ha='right')

# Subplot 2: Prompts mit Trend
ax = axes[0, 1]
ax.plot(x_num, prompts, 's-', linewidth=3, markersize=10, color='#4ECDC4', label='Prompt-Anzahl')
z_prom = np.polyfit(x_num, prompts, 2)
p_prom = np.poly1d(z_prom)
ax.plot(x_num, p_prom(x_num), '--', linewidth=2, color='darkblue', label='Polynom (Grad 2)')
ax.set_ylabel('Anzahl', fontweight='bold')
ax.set_title('Prompt-Trend', fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_xticks(x_num)
ax.set_xticklabels(months, rotation=45, ha='right')

# Subplot 3: Zeitlöcher Größe
ax = axes[1, 0]
ax.plot(x_num, gaps, '^-', linewidth=3, markersize=10, color='#95E1D3', label='Ø Zeitlücke')
z_gaps = np.polyfit(x_num, gaps, 1)
p_gaps = np.poly1d(z_gaps)
ax.plot(x_num, p_gaps(x_num), '--', linewidth=2, color='darkgreen', label='Linear Trend')
ax.set_ylabel('Durchschnittliche Lücke (Tage)', fontweight='bold')
ax.set_title('Zeitlöcher-Größen-Trend', fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_xticks(x_num)
ax.set_xticklabels(months, rotation=45, ha='right')

# Subplot 4: Zeitlöcher Anzahl
ax = axes[1, 1]
ax.plot(x_num, anomalies, 'd-', linewidth=3, markersize=10, color='#FFD3B6', label='Anzahl Anomalien')
z_anom = np.polyfit(x_num, anomalies, 1)
p_anom = np.poly1d(z_anom)
ax.plot(x_num, p_anom(x_num), '--', linewidth=2, color='darkorange', label='Linear Trend')
ax.set_ylabel('Anzahl Zeitsprünge', fontweight='bold')
ax.set_title('Zeitsprünge-Anzahl-Trend', fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_xticks(x_num)
ax.set_xticklabels(months, rotation=45, ha='right')

plt.tight_layout()
filepath = os.path.join(output_dir, "02_TRENDS_with_curves.png")
plt.savefig(filepath, dpi=300, bbox_inches='tight')
print(f"[OK] Gespeichert: 02_TRENDS_with_curves.png")
plt.close()

print("\n[OK] Alle Diagramme generiert!")
