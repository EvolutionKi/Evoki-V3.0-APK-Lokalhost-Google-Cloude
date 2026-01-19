#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hochauflösende Chatverlauf-Analyse - Version 2
Extrahiert tatsächliche Größe aus HTML und verknüpft mit Metriken
"""

import json
import os
import sys
import re
from datetime import datetime
from collections import defaultdict
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

# Pfade
html_file = r"C:\evoki\backend\Google Massenexport 16.10.25\MeineAktivitäten.html"
jsonl_file = r"C:\evoki\backend\VectorRegs_FORENSIC\evoki_messages_2025_with_metrics_gradgap_recommended.jsonl"
exhume_file = r"C:\evoki\backend\zeitsprung_exhumierung_vollstaendig.json"

print("=" * 90)
print("[ANALYSIS] HOCHAUFLÖSENDE CHATVERLAUF-ANALYSE v2 - MIT GRÖSSENBERECHNUNG")
print("=" * 90)

# ===== SCHRITT 1: HTML-Datei Größenberechnung =====
print("\n[STEP 1] Analysiere HTML-Struktur pro Monat...")

html_size_total = os.path.getsize(html_file)
print(f"   HTML-Gesamtgröße: {html_size_total / (1024*1024):.2f} MB")

# Lese HTML und gruppiere nach Zeitstempeln
with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
    html_content = f.read()

# Finde alle Zeitstempel und ihre Positionen
timestamp_pattern = r'(\d{1,2})\.(\d{1,2})\.(\d{4}),?\s+(\d{1,2}):(\d{2}):(\d{2})\s*(?:MESZ|UTC|MEZ)?'
matches = list(re.finditer(timestamp_pattern, html_content))

print(f"   {len(matches)} Zeitstempel gefunden in HTML")

# Gruppiere nach Monat und berechne Größen
html_by_month = defaultdict(lambda: {'start': None, 'end': None, 'count': 0})

for i, match in enumerate(matches):
    date_str = f"{match.group(3)}-{match.group(2).zfill(2)}"
    month_key = date_str
    
    if html_by_month[month_key]['start'] is None:
        html_by_month[month_key]['start'] = match.start()
    html_by_month[month_key]['end'] = match.end()
    html_by_month[month_key]['count'] += 1

# Berechne Größen pro Monat
html_monthly_sizes = {}
for month in sorted(html_by_month.keys()):
    data = html_by_month[month]
    if data['start'] is not None and data['end'] is not None:
        # Größe zwischen erstem und letztem Zeitstempel dieses Monats
        size_bytes = data['end'] - data['start']
        size_mb = size_bytes / (1024 * 1024)
        html_monthly_sizes[month] = {'bytes': size_bytes, 'mb': size_mb, 'timestamps': data['count']}

# ===== SCHRITT 2: JSONL-Daten auswerten =====
print("\n[STEP 2] Analysiere JSONL-Daten...")

monthly_data = defaultdict(lambda: {
    'prompt_count': 0,
    'total_tokens': 0,
    'dates': set(),
    'metrics': defaultdict(list)
})

line_count = 0
with open(jsonl_file, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if not line.strip():
            continue
        
        try:
            data = json.loads(line)
            line_count += 1
            
            if line_count % 2000 == 0:
                print(f"   Verarbeitet: {line_count} Zeilen...", end='\r')
            
            # Extrahiere Datum
            if 'timestamp' in data:
                try:
                    dt = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                    month_key = dt.strftime('%Y-%m')
                    day_key = dt.strftime('%Y-%m-%d')
                    
                    monthly_data[month_key]['prompt_count'] += 1
                    monthly_data[month_key]['dates'].add(day_key)
                    
                    # Token-Zählung
                    tokens = data.get('input_tokens', 0) + data.get('output_tokens', 0)
                    monthly_data[month_key]['total_tokens'] += tokens
                    
                    # Sammle numerische Metriken
                    for key, value in data.items():
                        if isinstance(value, (int, float)) and key not in ['input_tokens', 'output_tokens']:
                            monthly_data[month_key]['metrics'][key].append(value)
                except:
                    continue
        except json.JSONDecodeError:
            continue

print(f"   OK: {line_count:,} JSONL-Zeilen verarbeitet")

# ===== SCHRITT 3: Zeitsprung-Daten =====
print("\n[STEP 3] Lade Zeitsprung-Daten...")

with open(exhume_file, 'r', encoding='utf-8') as f:
    exhume_data = json.load(f)

anomalies_by_month = defaultdict(list)
for anomaly in exhume_data['anomalies']:
    timestamp_str = anomaly['block_vorher']['timestamp']
    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    month_key = dt.strftime('%Y-%m')
    gap_seconds = abs(anomaly['zeitsprung']['differenz_sekunden'])
    anomalies_by_month[month_key].append({'gap_seconds': gap_seconds})

print(f"   OK: {len(exhume_data['anomalies'])} Zeitsprünge analysiert")

# ===== SCHRITT 4: Kombiniere und berechne Metriken =====
print(f"\n[STEP 4] Kombiniere Daten...\n")

# Kombiniere Monate von JSONL und HTML
all_months = sorted(set(list(monthly_data.keys()) + list(html_monthly_sizes.keys())))

print(f"{'Monat':<12} {'Prompts':<10} {'HTML-Größe':<15} {'Tage':<8} {'Zeitlöcher':<12} {'Ø Gap (d)':<12} {'Tokens':<12}")
print("=" * 110)

monthly_stats = []

for month in all_months:
    jsonl_data = monthly_data.get(month, {})
    html_data = html_monthly_sizes.get(month, {})
    anomalies = anomalies_by_month.get(month, [])
    
    # Größe
    html_size_mb = html_data.get('mb', 0)
    
    # Prompts
    prompt_count = jsonl_data.get('prompt_count', 0)
    
    # Tage
    days = len(jsonl_data.get('dates', set()))
    
    # Zeitlöcher
    anomaly_count = len(anomalies)
    avg_gap_days = np.mean([a['gap_seconds'] / (3600*24) for a in anomalies]) if anomalies else 0
    
    # Tokens
    tokens = jsonl_data.get('total_tokens', 0)
    
    monthly_stats.append({
        'month': month,
        'prompts': prompt_count,
        'html_size_mb': html_size_mb,
        'days': days,
        'anomalies': anomaly_count,
        'avg_gap_days': avg_gap_days,
        'tokens': tokens
    })
    
    print(f"{month:<12} {prompt_count:<10} {html_size_mb:<15.2f} {days:<8} {anomaly_count:<12} {avg_gap_days:<12.2f} {tokens:<12}")

print("=" * 110)

# ===== SCHRITT 5: Trend-Analyse =====
print(f"\n[ANALYSIS] TREND-ANALYSE:\n")

months_nums = [int(m.split('-')[1]) for m in all_months]
sizes_mb = [s['html_size_mb'] for s in monthly_stats]
prompt_counts = [s['prompts'] for s in monthly_stats]
gaps_days = [s['avg_gap_days'] for s in monthly_stats]

if len(months_nums) > 2:
    z_size = np.polyfit(months_nums, sizes_mb, 1)
    z_prompts = np.polyfit(months_nums, prompt_counts, 1)
    z_gaps = np.polyfit(months_nums, gaps_days, 1)
    
    print(f"Größen-Trend: {'+' if z_size[0] > 0 else ''}{z_size[0]:.3f} MB/Monat")
    print(f"Prompt-Trend: {'+' if z_prompts[0] > 0 else ''}{z_prompts[0]:.0f} Prompts/Monat")
    print(f"Zeitlöcher-Trend: {'+' if z_gaps[0] > 0 else ''}{z_gaps[0]:.2f} Tage/Monat")

# ===== SCHRITT 6: Gesamtschätzung =====
print(f"\n[SUMMARY] GESAMTGRÖSSE-SCHÄTZUNG:")
print("=" * 90)

total_html_mb = sum([s['html_size_mb'] for s in monthly_stats])
total_prompts = sum([s['prompts'] for s in monthly_stats])
total_tokens = sum([s['tokens'] for s in monthly_stats])
total_days = sum([s['days'] for s in monthly_stats])
total_anomalies = sum([s['anomalies'] for s in monthly_stats])

print(f"\n   Zeitraum: {all_months[0]} bis {all_months[-1]}")
print(f"   HTML-Datengröße: {total_html_mb:.2f} MB")
print(f"   Gesamte Prompts: {total_prompts:,}")
print(f"   Gesamte Tokens: {total_tokens:,}")
print(f"   Gesamte Tage mit Aktivität: {total_days}")
print(f"   Gesamte Zeitsprünge: {total_anomalies}")

# Berechnete Metriken
if total_prompts > 0:
    bytes_per_prompt = (total_html_mb * 1024 * 1024) / total_prompts
    print(f"\n   Durchschnitt pro Prompt: {bytes_per_prompt:.0f} Bytes")
    
if total_days > 0:
    mb_per_day = total_html_mb / total_days
    prompts_per_day = total_prompts / total_days
    print(f"   Durchschnitt pro Tag: {mb_per_day:.2f} MB | {prompts_per_day:.0f} Prompts")

# Hochrechnung auf vollständigen Oktober
if all_months[-1] == '2025-10':
    oct_data = [s for s in monthly_stats if s['month'] == '2025-10'][0]
    if oct_data['days'] > 0:
        daily_rate = oct_data['html_size_mb'] / oct_data['days']
        projected_oct = daily_rate * 31
        print(f"\n   [FORECAST] Oktober 2025:")
        print(f"   - Aktuell (bis Tag {oct_data['days']}): {oct_data['html_size_mb']:.2f} MB")
        print(f"   - Tägl. Durchschnitt: {daily_rate:.2f} MB/Tag")
        print(f"   - Prognose für 31 Tage: {projected_oct:.2f} MB")

# ===== SCHRITT 7: Speichere Ergebnisse =====
print(f"\n[SAVE] Speichere Ergebnisse...")

output = {
    'analysis_date': datetime.now().isoformat(),
    'summary': {
        'total_html_size_mb': total_html_mb,
        'total_prompts': total_prompts,
        'total_tokens': total_tokens,
        'total_days': total_days,
        'total_anomalies': total_anomalies,
        'time_period': f"{all_months[0]} to {all_months[-1]}"
    },
    'monthly_breakdown': monthly_stats
}

output_file = r"C:\evoki\backend\chat_size_analysis_detailed.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"   OK: {output_file}")

print(f"\n{'='*90}")
print(f"OK: ANALYSE ABGESCHLOSSEN")
print(f"{'='*90}\n")
