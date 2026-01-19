#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXHUMIERUNGS-TOOL - INTELLIGENTE PROMPT-EXTRAKTION
==================================================
Extrahiert echten Prompt-Inhalt um Zeitstempel herum
"""

import re
import json
import html
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

html_path = Path(r"C:\evoki\backend\Google Massenexport 16.10.25\MeineAktivitäten.html")
output_file = Path(r"C:\evoki\backend\zeitsprung_exhumierung_vollstaendig.json")

print("="*80)
print("EXHUMIERUNGS-TOOL: VOLLSTÄNDIGE PROMPT-EXTRAKTION")
print("="*80)

# Pattern für Timestamps
timestamp_pattern = r'(\d{1,2})\.(\d{1,2})\.(\d{4}),?\s+(\d{1,2}):(\d{2}):(\d{2})\s*(?:MESZ|UTC|MEZ)?'

anomalies = []
all_messages = []

# Lese die gesamte Datei
print("Lese HTML-Datei...")
with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    html_content = f.read()

file_size = len(html_content)
print(f"Datei geladen: {file_size / (1024*1024):.1f} MB")

print("\nExtraktion mit Kontext...")

# Sammle ALLE Timestamps mit ihrem umgebenden Text
all_blocks = []
for match in re.finditer(timestamp_pattern, html_content):
    day, month, year, hour, minute, second = match.groups()
    timestamp_str = f"{year}-{month.zfill(2)}-{day.zfill(2)} {hour.zfill(2)}:{minute}:{second}"
    
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        
        # Extrahiere umgebenden Text (±1000 Zeichen für Kontext)
        start = max(0, match.start() - 1000)
        end = min(len(html_content), match.end() + 1000)
        
        context = html_content[start:end]
        
        # Dekodiere HTML entities
        context_clean = html.unescape(context)
        # Entferne HTML-Tags
        context_clean = re.sub(r'<[^>]+>', '\n', context_clean)
        context_clean = context_clean.replace('&quot;', '"').replace('&amp;', '&')
        context_clean = context_clean.strip()
        
        all_blocks.append({
            'index': len(all_blocks),
            'timestamp': ts,
            'timestamp_str': timestamp_str,
            'position': match.start(),
            'context': context_clean,
            'raw_context': context  # Speichere auch raw für spätere Analyse
        })
        
    except:
        pass

print(f"Blöcke extrahiert: {len(all_blocks)}")

# Finde Zeitsprünge
print("\nDetektiere Zeitsprünge...")

for i in range(len(all_blocks) - 1):
    current_ts = all_blocks[i]['timestamp']
    next_ts = all_blocks[i+1]['timestamp']
    
    diff_seconds = (next_ts - current_ts).total_seconds()
    abs_diff_seconds = abs(diff_seconds)
    
    is_anomaly = abs_diff_seconds > 1800  # >30 min
    
    if is_anomaly:
        # Kontext: 2 Blöcke vor + 2 danach
        context_before = []
        context_after = []
        
        for j in range(max(0, i-2), i):
            context_before.append({
                'index': all_blocks[j]['index'],
                'timestamp': all_blocks[j]['timestamp_str'],
                'kontext_auszug': all_blocks[j]['context'][:300]
            })
        
        for j in range(i+1, min(len(all_blocks), i+3)):
            context_after.append({
                'index': all_blocks[j]['index'],
                'timestamp': all_blocks[j]['timestamp_str'],
                'kontext_auszug': all_blocks[j]['context'][:300]
            })
        
        anomaly = OrderedDict([
            ('found_at_index', i),
            ('sequence_number', len(anomalies) + 1),
            ('block_vorher', {
                'index': all_blocks[i]['index'],
                'timestamp': all_blocks[i]['timestamp_str'],
                'timecode_position': all_blocks[i]['position'],
                'kontext_vollstaendig': all_blocks[i]['context'][:1500]
            }),
            ('zeitsprung', {
                'richtung': 'VORWÄRTS' if diff_seconds > 0 else 'RÜCKWÄRTS',
                'differenz_sekunden': diff_seconds,
                'differenz_stunden': diff_seconds / 3600,
                'differenz_tage': diff_seconds / 86400,
                'absolut': abs_diff_seconds
            }),
            ('block_nachher', {
                'index': all_blocks[i+1]['index'],
                'timestamp': all_blocks[i+1]['timestamp_str'],
                'timecode_position': all_blocks[i+1]['position'],
                'kontext_vollstaendig': all_blocks[i+1]['context'][:1500]
            }),
            ('kontext_umgebung', {
                'zwei_bloecke_vorher': context_before,
                'zwei_bloecke_nachher': context_after
            })
        ])
        
        anomalies.append(anomaly)
        
        if len(anomalies) % 100 == 0:
            print(f"  ... {len(anomalies)} Anomalien gefunden")

print(f"\n✅ Gesamt Zeitsprünge: {len(anomalies)}")

# Schreibe JSON
output_data = OrderedDict([
    ('metadata', {
        'source_file': str(html_path),
        'file_size_mb': file_size / (1024*1024),
        'analysis_date': datetime.now().isoformat(),
        'total_blocks': len(all_blocks),
        'total_anomalies': len(anomalies),
        'threshold_seconds': 1800,
        'inhalt': 'VOLLSTÄNDIGE KONTEXT-BLÖCKE (1500 Zeichen vor/nachher)',
        'note': 'Chronologisch wie gefunden'
    }),
    ('zeitsprung_statistiken', {
        'größter_vorwärts': max([a['zeitsprung']['differenz_sekunden'] for a in anomalies if a['zeitsprung']['differenz_sekunden'] > 0], default=0),
        'größter_rückwärts': min([a['zeitsprung']['differenz_sekunden'] for a in anomalies if a['zeitsprung']['differenz_sekunden'] < 0], default=0),
        'durchschnitt': sum([a['zeitsprung']['differenz_sekunden'] for a in anomalies]) / len(anomalies) if anomalies else 0
    }),
    ('anomalies', anomalies)
])

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\n📄 JSON gespeichert: {output_file}")
print(f"   Größe: {output_file.stat().st_size / (1024*1024):.1f} MB")

# Zeige Beispiel
print(f"\n🔴 BEISPIEL - GRÖSSTER RÜCKSPRUNG:")
print("="*80)

anomalies_by_size = sorted(anomalies, key=lambda x: abs(x['zeitsprung']['differenz_sekunden']), reverse=True)

if anomalies_by_size:
    anom = anomalies_by_size[0]
    anom_data = anom['zeitsprung']
    block_v = anom['block_vorher']
    block_n = anom['block_nachher']
    
    print(f"\nZeitsprung #{anom['sequence_number']} (Index {anom['found_at_index']}):")
    print(f"  {block_v['timestamp']} → {block_n['timestamp']}")
    print(f"  Rücksprung: {anom_data['differenz_tage']:.2f} Tage")
    print(f"\nKONTEXT VORHER (Timecode {block_v['timecode_position']}):")
    print("-"*80)
    print(block_v['kontext_vollstaendig'][:800])
    print(f"\nKONTEXT NACHHER (Timecode {block_n['timecode_position']}):")
    print("-"*80)
    print(block_n['kontext_vollstaendig'][:800])
