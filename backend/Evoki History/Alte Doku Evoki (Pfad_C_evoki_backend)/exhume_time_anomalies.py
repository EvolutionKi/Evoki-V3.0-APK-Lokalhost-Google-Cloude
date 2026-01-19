#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXHUMIERUNGS-TOOL FÜR ZEITSPRÜNGE
==================================
Findet alle Zeitsprünge (±2 Prompts) mit Kontext und speichert in JSON
Chronologisch WIE GEFUNDEN (nicht sortiert)
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

html_path = Path(r"C:\evoki\backend\Google Massenexport 16.10.25\MeineAktivitäten.html")
output_file = Path(r"C:\evoki\backend\ZEITSPRUNG_EXHUMIERUNG.json")

print("="*80)
print("EXHUMIERUNGS-TOOL: ZEITSPRÜNGE MIT KONTEXT")
print("="*80)

# Pattern für Timestamps und Nachrichten-Container
timestamp_pattern = r'(\d{1,2})\.(\d{1,2})\.(\d{4}),?\s+(\d{1,2}):(\d{2}):(\d{2})\s*(?:MESZ|UTC|MEZ)?'
message_boundary_pattern = r'<(?:div|p)[^>]*>([^<]*?)(?:<br>|</(?:div|p)>)'

anomalies = []
all_messages = []  # Speichere alle Nachrichten mit Timestamps

# Lese die gesamte Datei
print("Lese HTML-Datei...")
with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    html_content = f.read()

file_size = len(html_content)
print(f"Datei geladen: {file_size / (1024*1024):.1f} MB")

# Finde ALLE Timestamps und ihren Kontext
print("\nExtraktion von Nachrichten und Timestamps...")
for match in re.finditer(timestamp_pattern, html_content):
    day, month, year, hour, minute, second = match.groups()
    timestamp_str = f"{year}-{month.zfill(2)}-{day.zfill(2)} {hour.zfill(2)}:{minute}:{second}"
    
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        
        # Extrahiere umgebenden Text (Kontext)
        start_context = max(0, match.start() - 500)
        end_context = min(len(html_content), match.end() + 500)
        
        context = html_content[start_context:end_context]
        
        # Entferne HTML-Tags für Lesbarkeit
        context_clean = re.sub(r'<[^>]+>', '', context)
        context_clean = context_clean.replace('\n', ' ').replace('  ', ' ')[:300]
        
        all_messages.append({
            'index': len(all_messages),
            'timestamp': ts.isoformat(),
            'timestamp_parsed': timestamp_str,
            'position_in_file': match.start(),
            'context': context_clean.strip(),
        })
        
    except Exception as e:
        pass

print(f"Nachrichten extrahiert: {len(all_messages)}")

# Detektiere Zeitsprünge
print("\nDetektiere Zeitsprünge (±2 Prompts = ±4 Nachrichten)...")

for i in range(len(all_messages) - 1):
    current_ts = datetime.fromisoformat(all_messages[i]['timestamp'])
    next_ts = datetime.fromisoformat(all_messages[i+1]['timestamp'])
    
    diff_seconds = (next_ts - current_ts).total_seconds()
    abs_diff_seconds = abs(diff_seconds)
    
    # Flagge: Zeitsprung > 30 Minuten
    is_anomaly = abs_diff_seconds > 1800  # 30 Minuten
    
    if is_anomaly:
        # Sammle Kontext: 2 Nachrichten VOR + 2 NACH
        context_before = []
        context_after = []
        
        for j in range(max(0, i-2), i):
            context_before.append({
                'index': all_messages[j]['index'],
                'timestamp': all_messages[j]['timestamp_parsed'],
                'context': all_messages[j]['context']
            })
        
        for j in range(i+1, min(len(all_messages), i+3)):
            context_after.append({
                'index': all_messages[j]['index'],
                'timestamp': all_messages[j]['timestamp_parsed'],
                'context': all_messages[j]['context']
            })
        
        anomaly = OrderedDict([
            ('found_at_index', i),
            ('sequence_number', len(anomalies) + 1),
            ('nachricht_vorher', {
                'index': all_messages[i]['index'],
                'timestamp': all_messages[i]['timestamp_parsed'],
                'timecode_position': all_messages[i]['position_in_file'],
                'context': all_messages[i]['context']
            }),
            ('zeitsprung', {
                'richtung': 'VORWÄRTS' if diff_seconds > 0 else 'RÜCKWÄRTS',
                'differenz_sekunden': diff_seconds,
                'differenz_stunden': diff_seconds / 3600,
                'differenz_tage': diff_seconds / 86400,
                'absolut': abs_diff_seconds
            }),
            ('nachricht_nachher', {
                'index': all_messages[i+1]['index'],
                'timestamp': all_messages[i+1]['timestamp_parsed'],
                'timecode_position': all_messages[i+1]['position_in_file'],
                'context': all_messages[i+1]['context']
            }),
            ('kontext_umgebung', {
                'zwei_nachrichten_vorher': context_before,
                'zwei_nachrichten_nachher': context_after
            })
        ])
        
        anomalies.append(anomaly)
        
        # Progress
        if len(anomalies) % 50 == 0:
            print(f"  ... {len(anomalies)} Anomalien gefunden")

print(f"\n✅ Gesamt Zeitsprünge gefunden: {len(anomalies)}")

# Schreibe JSON (chronologisch WIE GEFUNDEN)
output_data = OrderedDict([
    ('metadata', {
        'source_file': str(html_path),
        'file_size_mb': file_size / (1024*1024),
        'analysis_date': datetime.now().isoformat(),
        'total_messages': len(all_messages),
        'total_anomalies': len(anomalies),
        'threshold_seconds': 1800,
        'note': 'Chronologisch wie gefunden (Index-Reihenfolge), nicht sortiert'
    }),
    ('zeitsprung_statistics', {
        'größter_vorwärts': max([a['zeitsprung']['differenz_sekunden'] for a in anomalies if a['zeitsprung']['differenz_sekunden'] > 0], default=0),
        'größter_rückwärts': min([a['zeitsprung']['differenz_sekunden'] for a in anomalies if a['zeitsprung']['differenz_sekunden'] < 0], default=0),
        'durchschnitt': sum([a['zeitsprung']['differenz_sekunden'] for a in anomalies]) / len(anomalies) if anomalies else 0
    }),
    ('anomalies', anomalies)
])

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\n📄 JSON gespeichert: {output_file}")
print(f"   Größe: {output_file.stat().st_size / 1024:.1f} KB")

# Zeige Top 5
print(f"\n🔴 TOP 5 GRÖSSTE ZEITSPRÜNGE (chronologisch wie gefunden):")
print("="*80)
for i, anomaly in enumerate(anomalies[:5]):
    anom = anomaly['zeitsprung']
    msg_v = anomaly['nachricht_vorher']
    msg_n = anomaly['nachricht_nachher']
    
    print(f"\n#{i+1} (Index {anomaly['found_at_index']}):")
    print(f"  {msg_v['timestamp']} → {msg_n['timestamp']}")
    print(f"  Sprung: {anom['differenz_tage']:.2f} Tage ({anom['richtung']})")
    print(f"  Vorher: ...{msg_v['context'][:80]}...")
    print(f"  Nachher: ...{msg_n['context'][:80]}...")
