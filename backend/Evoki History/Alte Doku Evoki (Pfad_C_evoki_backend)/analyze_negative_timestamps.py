#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEGATIVE ZEITSTEMPEL-PAARE ANALYSE
==================================
Analysiert VectorRegs_FORENSIC auf logisch unmögliche Zeitspannen.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(r"C:\evoki\backend\VectorRegs_FORENSIC")
OUTPUT_FILE = Path(r"C:\evoki\backend\NEGATIVE_TIMESTAMPS_ANALYSE.txt")

print("=" * 80)
print("NEGATIVE ZEITSTEMPEL-PAARE ANALYSE")
print("=" * 80)

# Scan alle TXT-Dateien
txt_files = list(BASE_DIR.glob("2025/**/*.txt"))
print(f"\nGefundene Dateien: {len(txt_files):,}")

negative_pairs = []
total_files = 0
files_with_timestamps = 0
timestamp_pairs = 0

# Regex-Patterns für Zeitstempel
TIMESTAMP_PATTERNS = [
    r'\b(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2}):(\d{2})',  # ISO 8601
    r'(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})',  # DD.MM.YYYY HH:MM
    r'(\d{4})/(\d{2})/(\d{2})\s+(\d{2}):(\d{2})',  # YYYY/MM/DD HH:MM
]

for txt_file in txt_files:
    total_files += 1
    
    try:
        with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Suche nach Zeitstempel-Paaren (z.B. "Start: ... End: ...")
        start_patterns = [
            r'(?:Start|Anfang|Begin|Von|From)[:\s]+(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2}):(\d{2})',
            r'(?:Start|Anfang)[:\s]+(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})',
        ]
        
        end_patterns = [
            r'(?:End|Ende|Stop|Bis|To)[:\s]+(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2}):(\d{2})',
            r'(?:End|Ende)[:\s]+(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})',
        ]
        
        # Simpler: Suche nach zwei aufeinanderfolgenden ISO-Timestamps
        iso_timestamps = re.findall(r'(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2}):(\d{2})', content)
        
        if iso_timestamps:
            files_with_timestamps += 1
            
            # Konvertiere zu datetime Objects
            datetimes = []
            for match in iso_timestamps:
                try:
                    year, month, day, hour, minute, second = map(int, match)
                    dt = datetime(year, month, day, hour, minute, second)
                    datetimes.append(dt)
                except ValueError:
                    continue
            
            # Suche nach Paaren wo zweiter < erster
            for i in range(len(datetimes) - 1):
                timestamp_pairs += 1
                time_start = datetimes[i]
                time_end = datetimes[i + 1]
                
                if time_end < time_start:
                    # NEGATIV! Time-Gap ist negativ
                    gap = (time_start - time_end).total_seconds()
                    
                    negative_pairs.append({
                        'file': txt_file.name,
                        'path': str(txt_file.relative_to(BASE_DIR)),
                        'time_start': time_start.isoformat(),
                        'time_end': time_end.isoformat(),
                        'negative_gap_seconds': gap,
                        'negative_gap_days': gap / 86400.0,
                    })
    
    except Exception as e:
        print(f"  ⚠️ Fehler bei {txt_file.name}: {e}")

# Statistiken
print(f"\n{'=' * 80}")
print(f"STATISTIK")
print(f"{'=' * 80}")
print(f"Total TXT-Dateien gescannt: {total_files:,}")
print(f"Dateien mit Zeitstempeln: {files_with_timestamps:,}")
print(f"Zeitstempel-Paare gefunden: {timestamp_pairs:,}")
print(f"NEGATIVE PAARE GEFUNDEN: {len(negative_pairs):,}")

if negative_pairs:
    print(f"\n{'=' * 80}")
    print(f"TOP 20 NEGATIVE ZEITSTEMPEL-PAARE")
    print(f"{'=' * 80}\n")
    
    # Sortiere nach Gap (größte Diskrepanzen zuerst)
    sorted_pairs = sorted(negative_pairs, key=lambda x: x['negative_gap_seconds'], reverse=True)
    
    for idx, pair in enumerate(sorted_pairs[:20], 1):
        print(f"{idx}. {pair['path']}")
        print(f"   Start:  {pair['time_start']}")
        print(f"   End:    {pair['time_end']}")
        print(f"   ❌ NEGATIV: -{pair['negative_gap_seconds']:.0f}s ({pair['negative_gap_days']:.2f} Tage rückwärts)")
        print()

# Gruppierung nach Datums-Muster
print(f"\n{'=' * 80}")
print(f"ANALYSE: HÄUFIGSTE MUSTER BEI NEGATIVEN PAAREN")
print(f"{'=' * 80}\n")

patterns = defaultdict(int)
for pair in negative_pairs:
    start = datetime.fromisoformat(pair['time_start'])
    end = datetime.fromisoformat(pair['time_end'])
    
    # Muster: "Heute vs. Gestern", "Heute vs. Vor X Tagen", etc.
    days_back = (start.date() - end.date()).days
    
    if days_back == 1:
        patterns['Vorheriger Tag (1 Tag rückwärts)'] += 1
    elif days_back > 1:
        patterns[f'{days_back} Tage rückwärts'] += 1
    elif days_back == 0:
        patterns['Gleicher Tag (nur Tageszeit rückwärts)'] += 1
    else:
        patterns['Zukünftig (should not happen)'] += 1

for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / len(negative_pairs) * 100) if negative_pairs else 0
    print(f"  {pattern:40s}: {count:4,} ({percentage:5.1f}%)")

# Speichere Report
print(f"\n{'=' * 80}")
print(f"VOLLSTÄNDIGER REPORT")
print(f"{'=' * 80}\n")

report_lines = [
    "NEGATIVE ZEITSTEMPEL-PAARE - DETAILLIERTER REPORT",
    "=" * 80,
    f"Scan-Datum: {datetime.now().isoformat()}",
    f"Quelle: {BASE_DIR}",
    f"\nStatistik:",
    f"  Total TXT-Dateien: {total_files:,}",
    f"  Dateien mit Zeitstempeln: {files_with_timestamps:,}",
    f"  Zeitstempel-Paare gefunden: {timestamp_pairs:,}",
    f"  NEGATIVE PAARE: {len(negative_pairs):,}",
    f"\nInterpretation:",
    f"  - Negative Paare = time_end < time_start",
    f"  - Deutet auf: Datensortierungs-Fehler, Zeitzone-Probleme, oder Daten-Corruption",
    f"\n" + "=" * 80,
    "DETAILLIERTE LISTE (Sortiert nach Gap-Größe):",
    "=" * 80 + "\n",
]

for idx, pair in enumerate(sorted_pairs, 1):
    report_lines.extend([
        f"{idx}. {pair['path']}",
        f"   Start:        {pair['time_start']}",
        f"   End:          {pair['time_end']}",
        f"   Negative Gap: -{pair['negative_gap_seconds']:.0f}s ({pair['negative_gap_days']:.3f} days)",
        "",
    ])

# Schreibe Report
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f"✅ Report gespeichert: {OUTPUT_FILE}")
print(f"\nWeitere Analysen möglich:")
print(f"  - Zeitzone-Analyse (UTC vs. Local)")
print(f"  - Chronologische Sortierung prüfen")
print(f"  - Datenquellen-Validierung (HTML Extractor)")

