#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXHUMIERUNGS-TOOL FÜR ZEITSPRÜNGE - MIT VOLLSTÄNDIGEM PROMPT-INHALT
===================================================================
Extrahiert:
1. Echten Prompt-Text (nicht HTML-Müll)
2. ±2 Prompts Kontext (vollständig)
3. Timecode-Position
4. Chronologisch wie gefunden
"""

import re
import json
import html
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

html_path = Path(r"C:\evoki\backend\Google Massenexport 16.10.25\MeineAktivitäten.html")
output_file = Path(r"C:\evoki\backend\zeitsprung_exhumierung_prompts.json")

print("="*80)
print("EXHUMIERUNGS-TOOL: ZEITSPRÜNGE + PROMPT-INHALTE")
print("="*80)

# Pattern für Timestamps und Messages
timestamp_pattern = r'(\d{1,2})\.(\d{1,2})\.(\d{4}),?\s+(\d{1,2}):(\d{2}):(\d{2})\s*(?:MESZ|UTC|MEZ)?'

# Pattern um Message-Container zu finden
# Google Format: <div>...Prompt...</div> dann <br> dann TIMESTAMP dann <br> dann ANTWORT
message_pattern = r'<div[^>]*>([^<]*?(?:Eingegeben[^<]*?)?[^<]*?)</div>\s*(?:<br>)?\s*(\d{1,2})\.(\d{1,2})\.(\d{4}),?\s+(\d{1,2}):(\d{2}):(\d{2})'

anomalies = []
all_messages = []  # Alle Nachrichten mit vollständigem Inhalt

# Lese die gesamte Datei
print("Lese HTML-Datei...")
with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    html_content = f.read()

file_size = len(html_content)
print(f"Datei geladen: {file_size / (1024*1024):.1f} MB")

print("\nExtraktion von Prompts und Timestamps...")

# Strategie: Finde ALLE Timestamps, dann extrahiere davor/danach Inhalt
timestamp_positions = []
for match in re.finditer(timestamp_pattern, html_content):
    day, month, year, hour, minute, second = match.groups()
    timestamp_str = f"{year}-{month.zfill(2)}-{day.zfill(2)} {hour.zfill(2)}:{minute}:{second}"
    
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        timestamp_positions.append({
            'timestamp': ts,
            'timestamp_str': timestamp_str,
            'position': match.start(),
            'match_obj': match
        })
    except:
        pass

print(f"Timestamps gefunden: {len(timestamp_positions)}")

# Extrahiere Prompt-Inhalte
print("\nExtrahiere Prompt-Inhalte...")
for idx, ts_data in enumerate(timestamp_positions):
    pos = ts_data['position']
    
    # Suche RÜCKWÄRTS nach "Eingegeben[er] Prompt:" oder ähnlich
    search_back = max(0, pos - 2000)
    back_text = html_content[search_back:pos]
    
    # Extrahiere den eigentlichen Prompt
    prompt_match = re.search(
        r'(?:Eingegeben[er]* Prompt|Prompt):\s*([^<]*?)(?:</div>|</p>|<br>)',
        back_text,
        re.IGNORECASE | re.DOTALL
    )
    
    prompt_text = ""
    if prompt_match:
        prompt_text = prompt_match.group(1).strip()
        # Entferne HTML
        prompt_text = re.sub(r'<[^>]+>', '', prompt_text)
        prompt_text = html.unescape(prompt_text)
        prompt_text = prompt_text.replace('\n', ' ').replace('  ', ' ')[:500]
    
    # Suche VORWÄRTS nach Antwort-Text
    search_forward = min(len(html_content), pos + 500)
    forward_text = html_content[pos:search_forward]
    
    response_match = re.search(
        r'(?:Antwort|Ergebnis|Response):\s*([^<]*?)(?:</div>|</p>|<br>)',
        forward_text,
        re.IGNORECASE
    )
    
    response_text = ""
    if response_match:
        response_text = response_match.group(1).strip()
        response_text = re.sub(r'<[^>]+>', '', response_text)
        response_text = html.unescape(response_text)
        response_text = response_text.replace('\n', ' ').replace('  ', ' ')[:500]
    
    all_messages.append({
        'index': idx,
        'timestamp': ts_data['timestamp'].isoformat(),
        'timestamp_str': ts_data['timestamp_str'],
        'position': ts_data['position'],
        'prompt': prompt_text,
        'response': response_text,
    })

print(f"Prompts extrahiert: {len(all_messages)}")

# Detektiere Zeitsprünge
print("\nDetektiere Zeitsprünge...")

for i in range(len(all_messages) - 1):
    current_ts = datetime.fromisoformat(all_messages[i]['timestamp'])
    next_ts = datetime.fromisoformat(all_messages[i+1]['timestamp'])
    
    diff_seconds = (next_ts - current_ts).total_seconds()
    abs_diff_seconds = abs(diff_seconds)
    
    # Flagge: Zeitsprung > 30 Minuten
    is_anomaly = abs_diff_seconds > 1800
    
    if is_anomaly:
        # Sammle Kontext: 2 Nachrichten VOR + 2 NACH
        context_before = []
        context_after = []
        
        for j in range(max(0, i-2), i):
            context_before.append({
                'index': all_messages[j]['index'],
                'timestamp': all_messages[j]['timestamp_str'],
                'prompt': all_messages[j]['prompt'][:200] if all_messages[j]['prompt'] else '',
                'response': all_messages[j]['response'][:200] if all_messages[j]['response'] else ''
            })
        
        for j in range(i+1, min(len(all_messages), i+3)):
            context_after.append({
                'index': all_messages[j]['index'],
                'timestamp': all_messages[j]['timestamp_str'],
                'prompt': all_messages[j]['prompt'][:200] if all_messages[j]['prompt'] else '',
                'response': all_messages[j]['response'][:200] if all_messages[j]['response'] else ''
            })
        
        anomaly = OrderedDict([
            ('found_at_index', i),
            ('sequence_number', len(anomalies) + 1),
            ('nachricht_vorher', {
                'index': all_messages[i]['index'],
                'timestamp': all_messages[i]['timestamp_str'],
                'timecode_position': all_messages[i]['position'],
                'prompt': all_messages[i]['prompt'],
                'response': all_messages[i]['response']
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
                'timestamp': all_messages[i+1]['timestamp_str'],
                'timecode_position': all_messages[i+1]['position'],
                'prompt': all_messages[i+1]['prompt'],
                'response': all_messages[i+1]['response']
            }),
            ('kontext_umgebung', {
                'zwei_nachrichten_vorher': context_before,
                'zwei_nachrichten_nachher': context_after
            })
        ])
        
        anomalies.append(anomaly)
        
        if len(anomalies) % 100 == 0:
            print(f"  ... {len(anomalies)} Anomalien gefunden")

print(f"\n✅ Gesamt Zeitsprünge mit Prompts: {len(anomalies)}")

# Schreibe JSON
output_data = OrderedDict([
    ('metadata', {
        'source_file': str(html_path),
        'file_size_mb': file_size / (1024*1024),
        'analysis_date': datetime.now().isoformat(),
        'total_messages': len(all_messages),
        'total_anomalies': len(anomalies),
        'threshold_seconds': 1800,
        'content': 'Vollständige Prompt-Inhalte (nicht nur HTML-Kontext)',
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

print(f"\n📄 JSON mit Prompts gespeichert: {output_file}")
print(f"   Größe: {output_file.stat().st_size / 1024:.1f} KB")

# Zeige Top 3 mit Inhalten
print(f"\n🔴 TOP 3 GRÖSSTE ZEITSPRÜNGE (mit Prompt-Inhalten):")
print("="*80)

anomalies_by_size = sorted(anomalies, key=lambda x: abs(x['zeitsprung']['differenz_sekunden']), reverse=True)

for i, anomaly in enumerate(anomalies_by_size[:3]):
    anom = anomaly['zeitsprung']
    msg_v = anomaly['nachricht_vorher']
    msg_n = anomaly['nachricht_nachher']
    
    print(f"\n#{i+1} (Index {anomaly['found_at_index']}):")
    print(f"  {msg_v['timestamp']} → {msg_n['timestamp']}")
    print(f"  Sprung: {anom['differenz_tage']:.2f} Tage ({anom['richtung']})")
    print(f"\n  PROMPT VORHER:")
    print(f"    {msg_v['prompt'][:150]}...")
    print(f"  ANTWORT VORHER:")
    print(f"    {msg_v['response'][:150]}...")
    print(f"\n  PROMPT NACHHER:")
    print(f"    {msg_n['prompt'][:150]}...")
    print(f"  ANTWORT NACHHER:")
    print(f"    {msg_n['response'][:150]}...")
