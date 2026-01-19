#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeWrap Balkendiagramme pro Monat
Zeigt die tatsächlichen Zeitlücken zwischen Interaktionen
"""

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict
import os
import numpy as np

# Deutsche Schriftart für Diagramme
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# Laden der Exhumierungsdaten
json_file = r"C:\evoki\backend\zeitsprung_exhumierung_vollstaendig.json"

print("📊 Lade Exhumierungsdaten...")
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

anomalies = data['anomalies']
print(f"✅ {len(anomalies)} Anomalien geladen")

# Organisiere Daten nach Monat
timewraps_by_month = defaultdict(list)
month_data = defaultdict(lambda: {'days': [], 'gaps_hours': [], 'gaps_days': []})

for anomaly in anomalies:
    # Timestamp vor dem Sprung
    timestamp_str = anomaly['block_vorher']['timestamp']
    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    month_key = dt.strftime('%Y-%m')  # YYYY-MM
    
    # Zeitlücke (in Sekunden -> Stunden/Tage)
    gap_seconds = abs(anomaly['zeitsprung']['differenz_sekunden'])
    gap_hours = gap_seconds / 3600
    gap_days = gap_seconds / (3600 * 24)
    
    # Speichere gruppiert nach Monat
    month_data[month_key]['days'].append(dt.day)
    month_data[month_key]['gaps_hours'].append(gap_hours)
    month_data[month_key]['gaps_days'].append(gap_days)

# Sortiere Monate chronologisch
sorted_months = sorted(month_data.keys())

print(f"\n📅 Monate mit TimeWraps: {len(sorted_months)}")
for month in sorted_months:
    count = len(month_data[month]['gaps_hours'])
    avg_hours = np.mean(month_data[month]['gaps_hours'])
    max_days = np.max(month_data[month]['gaps_days'])
    print(f"   {month}: {count} Anomalien | Ø {avg_hours:.1f}h | Max {max_days:.1f}d")

# Erstelle Balkendiagramme für jeden Monat
print("\n🎨 Generiere Balkendiagramme...")
output_dir = r"C:\evoki\backend\timewrap_charts"
os.makedirs(output_dir, exist_ok=True)

for i, month in enumerate(sorted_months, 1):
    data_month = month_data[month]
    
    # Gruppiere nach Tagen (alle Anomalien am selben Tag zusammenfassen)
    day_gaps = defaultdict(list)
    for day, gap_h in zip(data_month['days'], data_month['gaps_hours']):
        day_gaps[day].append(gap_h)
    
    # Berechne Durchschnitt pro Tag
    days_sorted = sorted(day_gaps.keys())
    avg_gaps = [np.mean(day_gaps[d]) for d in days_sorted]
    max_gaps = [np.max(day_gaps[d]) for d in days_sorted]
    counts = [len(day_gaps[d]) for d in days_sorted]
    
    # Erstelle Figur
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    fig.suptitle(f'TimeWraps für {month} - Tatsächliche Zeitlücken zwischen Interaktionen', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    # Diagramm 1: Durchschnittliche Zeitlücke (Stunden)
    ax1 = axes[0]
    bars1 = ax1.bar(days_sorted, avg_gaps, color='#FF6B6B', alpha=0.7, edgecolor='darkred', linewidth=1.5)
    ax1.set_xlabel('Tag des Monats', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Ø Zeitlücke (Stunden)', fontsize=12, fontweight='bold')
    ax1.set_title('Durchschnittliche TimeWrap pro Tag', fontsize=13)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_xticks(range(1, max(days_sorted) + 2, 1))
    
    # Beschriftung der Balken
    for bar, gap in zip(bars1, avg_gaps):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{gap:.1f}h', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Diagramm 2: Maximale Zeitlücke (Stunden)
    ax2 = axes[1]
    bars2 = ax2.bar(days_sorted, max_gaps, color='#4ECDC4', alpha=0.7, edgecolor='darkblue', linewidth=1.5)
    ax2.set_xlabel('Tag des Monats', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Max. Zeitlücke (Stunden)', fontsize=12, fontweight='bold')
    ax2.set_title('Maximale TimeWrap pro Tag', fontsize=13)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_xticks(range(1, max(days_sorted) + 2, 1))
    
    # Beschriftung und Anomalien-Anzahl
    for bar, gap, count in zip(bars2, max_gaps, counts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{gap:.1f}h\n({count})', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    
    # Speichere Diagramm
    filename = f"{month}_timewrap_chart.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"   ✅ {filename}")
    
    plt.close()

# Erstelle Übersichtsdiagramm für alle Monate
print("\n📈 Generiere Übersichtsdiagramm...")

fig, axes = plt.subplots(2, 1, figsize=(18, 10))
fig.suptitle('TimeWrap Übersicht - Alle Monate', fontsize=16, fontweight='bold', y=0.995)

# Diagramm 1: Durchschnittliche Lücke pro Monat
month_labels = [m.replace('-', '/') for m in sorted_months]
avg_per_month = [np.mean(month_data[m]['gaps_hours']) for m in sorted_months]
max_per_month = [np.max(month_data[m]['gaps_hours']) for m in sorted_months]
count_per_month = [len(month_data[m]['gaps_hours']) for m in sorted_months]

ax1 = axes[0]
x_pos = np.arange(len(month_labels))
bars1 = ax1.bar(x_pos - 0.2, avg_per_month, 0.4, label='Ø Zeitlücke', color='#FF6B6B', alpha=0.7, edgecolor='darkred')
bars1b = ax1.bar(x_pos + 0.2, max_per_month, 0.4, label='Max. Zeitlücke', color='#4ECDC4', alpha=0.7, edgecolor='darkblue')

ax1.set_xlabel('Monat', fontsize=12, fontweight='bold')
ax1.set_ylabel('Zeitlücke (Stunden)', fontsize=12, fontweight='bold')
ax1.set_title('Durchschnittliche und Maximale TimeWrap pro Monat', fontsize=13)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(month_labels, rotation=45, ha='right')
ax1.legend(fontsize=11)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Beschriftung
for bars in [bars1, bars1b]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}h', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Diagramm 2: Anomalien-Count pro Monat
ax2 = axes[1]
bars2 = ax2.bar(x_pos, count_per_month, color='#95E1D3', alpha=0.7, edgecolor='darkgreen', linewidth=2)
ax2.set_xlabel('Monat', fontsize=12, fontweight='bold')
ax2.set_ylabel('Anzahl Anomalien', fontsize=12, fontweight='bold')
ax2.set_title('Zeitsprünge pro Monat', fontsize=13)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(month_labels, rotation=45, ha='right')
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Beschriftung
for bar, count in zip(bars2, count_per_month):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(count)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
filepath = os.path.join(output_dir, "00_OVERVIEW_all_months.png")
plt.savefig(filepath, dpi=300, bbox_inches='tight')
print(f"   ✅ 00_OVERVIEW_all_months.png")
plt.close()

# Erstelle Statistik-CSV
print("\n📊 Generiere CSV-Statistiken...")

csv_content = "Monat,Anomalien,Ø_Stunden,Max_Stunden,Ø_Tage,Max_Tage\n"
for month in sorted_months:
    gaps_h = month_data[month]['gaps_hours']
    gaps_d = month_data[month]['gaps_days']
    
    csv_content += f"{month},{len(gaps_h)},{np.mean(gaps_h):.2f},{np.max(gaps_h):.2f},{np.mean(gaps_d):.2f},{np.max(gaps_d):.2f}\n"

csv_file = os.path.join(output_dir, "timewrap_statistics.csv")
with open(csv_file, 'w', encoding='utf-8') as f:
    f.write(csv_content)
print(f"   ✅ timewrap_statistics.csv")

print(f"\n✅ Alle Diagramme gespeichert in: {output_dir}")
print(f"📊 Gesamt {len(sorted_months)} Monate analysiert")
print(f"📈 Gesamt {len(anomalies)} Zeitsprünge verarbeitet")
