#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hochauflösende Chatverlauf-Analyse
Verbinde Zeitlöcher, Datengröße, Promptanzahl und Metriken
"""

import json
import os
import sys
from datetime import datetime
from collections import defaultdict
import numpy as np
from pathlib import Path

# Setze UTF-8 Encoding für Output
sys.stdout.reconfigure(encoding='utf-8')

# Pfade
jsonl_file = r"C:\evoki\backend\VectorRegs_FORENSIC\evoki_messages_2025_with_metrics_gradgap_recommended.jsonl"
html_file = r"C:\evoki\backend\Google Massenexport 16.10.25\MeineAktivitäten.html"
exhume_file = r"C:\evoki\backend\zeitsprung_exhumierung_vollstaendig.json"

print("=" * 80)
print("[ANALYSIS] HOCHAUFLÖSENDE CHATVERLAUF-ANALYSE")
print("=" * 80)

# 1. Lade HTML-Datei für Größeninformationen
print("\n[STEP 1] Analysiere HTML-Datei...")
html_size_bytes = os.path.getsize(html_file)
html_size_mb = html_size_bytes / (1024 * 1024)
print(f"   HTML-Gesamtgröße: {html_size_mb:.2f} MB ({html_size_bytes:,} Bytes)")

# 2. Streame JSONL und sammle Daten pro Monat
print("\n[STEP 2] Analysiere JSONL-Daten (streaming)...")

monthly_data = defaultdict(lambda: {
    'prompts': [],
    'message_count': 0,
    'total_bytes': 0,
    'total_input_tokens': 0,
    'total_output_tokens': 0,
    'metrics': defaultdict(list),
    'dates': set()
})

# Metrik-Namen aus JSONL
metric_names = set()
prompt_sizes = []
dates_found = set()

line_count = 0
with open(jsonl_file, 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip():
            continue
        
        try:
            data = json.loads(line)
            line_count += 1
            
            if line_count % 1000 == 0:
                print(f"   Verarbeitet: {line_count} Zeilen...", end='\r')
            
            # Extrahiere Datum
            if 'timestamp' in data:
                try:
                    dt = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                    month_key = dt.strftime('%Y-%m')
                    day_key = dt.strftime('%Y-%m-%d')
                    dates_found.add(day_key)
                except:
                    continue
            else:
                continue
            
            # Prompt-Größe (UTF-8 Bytes)
            prompt_size = 0
            if 'user_input' in data:
                prompt_size += len(data['user_input'].encode('utf-8'))
            if 'system_prompt' in data:
                prompt_size += len(data['system_prompt'].encode('utf-8'))
            
            # Zähle Daten
            monthly_data[month_key]['message_count'] += 1
            monthly_data[month_key]['total_bytes'] += prompt_size
            monthly_data[month_key]['prompts'].append(prompt_size)
            monthly_data[month_key]['dates'].add(day_key)
            prompt_sizes.append(prompt_size)
            
            # Token-Daten
            if 'input_tokens' in data:
                monthly_data[month_key]['total_input_tokens'] += data['input_tokens']
            if 'output_tokens' in data:
                monthly_data[month_key]['total_output_tokens'] += data['output_tokens']
            
            # Sammle Metriken
            for key, value in data.items():
                if key not in ['timestamp', 'user_input', 'system_prompt', 'input_tokens', 'output_tokens']:
                    if isinstance(value, (int, float)):
                        monthly_data[month_key]['metrics'][key].append(value)
                        metric_names.add(key)
        
        except json.JSONDecodeError:
            continue

print(f"\n   OK: {line_count:,} Zeilen verarbeitet")
print(f"   {len(dates_found)} verschiedene Tage gefunden")

# 3. Lade Exhumierungsdaten
print("\n[STEP 3] Lade Zeitsprung-Daten...")
with open(exhume_file, 'r', encoding='utf-8') as f:
    exhume_data = json.load(f)

anomalies_by_month = defaultdict(list)
for anomaly in exhume_data['anomalies']:
    timestamp_str = anomaly['block_vorher']['timestamp']
    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    month_key = dt.strftime('%Y-%m')
    gap_seconds = abs(anomaly['zeitsprung']['differenz_sekunden'])
    anomalies_by_month[month_key].append({
        'gap_seconds': gap_seconds,
        'gap_hours': gap_seconds / 3600,
        'gap_days': gap_seconds / (3600 * 24)
    })

print(f"   OK: {len(exhume_data['anomalies'])} Zeitsprünge analysiert")

# 4. Berechne monatliche Statistiken
print(f"\n[STEP 4] Berechne Statistiken...\n")

sorted_months = sorted(monthly_data.keys())

# Header
print(f"{'Monat':<12} {'Prompts':<10} {'Größe (MB)':<15} {'Ø Größe':<12} {'Tage':<8} {'Zeitlöcher':<12} {'Ø Gap (d)':<12} {'Flow-Score':<12}")
print("=" * 120)

monthly_stats = []

for month in sorted_months:
    data = monthly_data[month]
    prompts = data['prompts']
    
    # Größen-Statistiken
    total_size_mb = data['total_bytes'] / (1024 * 1024)
    avg_prompt_size = np.mean(prompts) if prompts else 0
    avg_prompt_size_kb = avg_prompt_size / 1024
    
    # Zeit-Statistiken
    days_count = len(data['dates'])
    
    # Anomalien für diesen Monat
    anomalies = anomalies_by_month.get(month, [])
    anomaly_count = len(anomalies)
    avg_gap_days = np.mean([a['gap_days'] for a in anomalies]) if anomalies else 0
    
    # Metriken
    metrics_available = len(data['metrics'])
    
    # Flow-Score (wenn verfügbar)
    flow_score = np.mean(data['metrics'].get('flow', [0])) if 'flow' in data['metrics'] else 0
    
    monthly_stats.append({
        'month': month,
        'prompt_count': len(prompts),
        'total_size_mb': total_size_mb,
        'avg_size_kb': avg_prompt_size_kb,
        'days': days_count,
        'anomalies': anomaly_count,
        'avg_gap_days': avg_gap_days,
        'flow_score': flow_score,
        'metrics_count': metrics_available
    })
    
    print(f"{month:<12} {len(prompts):<10} {total_size_mb:<15.2f} {avg_prompt_size_kb:<12.1f} {days_count:<8} {anomaly_count:<12} {avg_gap_days:<12.2f} {flow_score:<12.3f}")

print("\n" + "=" * 120)

# 5. Berechne Trends und Prognosen
print(f"\n[ANALYSIS] TREND-ANALYSE UND PROGNOSEN:\n")

# Extrahiere nur Monate mit Daten
months_nums = [int(m.split('-')[1]) for m in sorted_months]
sizes = [s['total_size_mb'] for s in monthly_stats]
prompts = [s['prompt_count'] for s in monthly_stats]
gaps = [s['avg_gap_days'] for s in monthly_stats]

# Lineare Regression für Trends
if len(months_nums) > 1:
    # Size-Trend
    z_size = np.polyfit(months_nums, sizes, 1)
    size_trend = "[UP] STEIGEND" if z_size[0] > 0 else "[DOWN] FALLEND"
    print(f"Größen-Trend: {size_trend}")
    print(f"   Änderung pro Monat: {z_size[0]:.3f} MB")
    
    # Prompt-Trend
    z_prompts = np.polyfit(months_nums, prompts, 1)
    prompt_trend = "[UP] STEIGEND" if z_prompts[0] > 0 else "[DOWN] FALLEND"
    print(f"\nPrompt-Trend: {prompt_trend}")
    print(f"   Änderung pro Monat: {z_prompts[0]:.1f} Prompts")
    
    # Gap-Trend
    z_gaps = np.polyfit(months_nums, gaps, 1)
    gap_trend = "[UP] ANWACHSEND" if z_gaps[0] > 0 else "[DOWN] SINKEND"
    print(f"\nZeitlöcher-Trend: {gap_trend}")
    print(f"   Änderung pro Monat: {z_gaps[0]:.2f} Tage")
    
    # Prognose für Rest von Oktober und November
    print(f"\n[FORECAST] PROGNOSE:")
    
    # Annahmen für Monatende
    current_month_data = monthly_stats[-1]
    print(f"\n   Oktober 2025 (Stand 7.12.25 - rückwirkend extrapoliert):")
    print(f"   - Tage im Oktober: 31")
    print(f"   - Bisherige Prompts: {current_month_data['prompt_count']}")
    print(f"   - Bisherige Größe: {current_month_data['total_size_mb']:.2f} MB")
    
    # Durchschnittliche täglich Größe
    if current_month_data['days'] > 0:
        daily_avg_size = current_month_data['total_size_mb'] / current_month_data['days']
        daily_avg_prompts = current_month_data['prompt_count'] / current_month_data['days']
        
        # Prognose auf ganzen Monat
        projected_size = daily_avg_size * 31
        projected_prompts = int(daily_avg_prompts * 31)
        
        print(f"   - Ø tägl. Größe: {daily_avg_size:.2f} MB/Tag")
        print(f"   - Ø tägl. Prompts: {daily_avg_prompts:.0f} Prompts/Tag")
        print(f"   - Prognose bis 31.10: {projected_size:.2f} MB mit {projected_prompts} Prompts")

# 6. Gesamtgröße-Schätzung
print(f"\n[DATA] GESAMTGRÖSSE-SCHÄTZUNG:")
print(f"=" * 80)

total_mb = sum([s['total_size_mb'] for s in monthly_stats])
total_prompts = sum([s['prompt_count'] for s in monthly_stats])

print(f"\n   Analysierte Zeitraum: Februar 2025 - Oktober 2025")
print(f"   Gesamt Datengröße (JSONL): {total_mb:.2f} MB")
print(f"   Gesamt Prompts: {total_prompts:,}")
print(f"   Ø Prompt-Größe: {(total_mb * 1024 / total_prompts):.1f} KB")
print(f"   Ø Prompts pro Monat: {total_prompts / len(sorted_months):.0f}")
print(f"   Ø Größe pro Monat: {total_mb / len(sorted_months):.2f} MB")

# Korrelation: Zeitlöcher vs Größe
print(f"\n[CORRELATION] KORRELATIONEN:")

gap_trend_val = np.mean(gaps)
size_trend_val = np.mean(sizes)

print(f"   Ø Zeitlücke pro Monat: {gap_trend_val:.2f} Tage")
print(f"   Ø Größe pro Monat: {size_trend_val:.2f} MB")
print(f"   Größe pro Zeitloch-Tag: {size_trend_val / gap_trend_val if gap_trend_val > 0 else 0:.4f} MB/Tag")

# 7. Speichere detaillierte Statistik
print(f"\n[SAVE] Speichere Detailstatistiken...\n")

stats_output = {
    'analysis_date': datetime.now().isoformat(),
    'summary': {
        'total_months': len(sorted_months),
        'total_prompts': total_prompts,
        'total_size_mb': total_mb,
        'avg_prompt_size_kb': (total_mb * 1024 / total_prompts) if total_prompts > 0 else 0,
        'avg_prompts_per_month': total_prompts / len(sorted_months),
        'avg_size_per_month_mb': total_mb / len(sorted_months),
        'time_period': f"{sorted_months[0]} to {sorted_months[-1]}"
    },
    'monthly_breakdown': monthly_stats,
    'trend_analysis': {
        'size_trend_mb_per_month': float(z_size[0]) if len(months_nums) > 1 else 0,
        'prompt_trend_per_month': float(z_prompts[0]) if len(months_nums) > 1 else 0,
        'gap_trend_days_per_month': float(z_gaps[0]) if len(months_nums) > 1 else 0
    }
}

output_file = r"C:\evoki\backend\chat_size_analysis.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(stats_output, f, indent=2, ensure_ascii=False)

print(f"   OK: Statistiken gespeichert: {output_file}")
print(f"\n{'='*80}")
print(f"OK: ANALYSE ABGESCHLOSSEN")
print(f"{'='*80}\n")
