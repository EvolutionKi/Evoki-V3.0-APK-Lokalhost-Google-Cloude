#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KORREKTE HTML-ANALYSE DIREKT AUS DER ROHDATEI
Suche nach Zeitstempeln im Format: "03.10.2025, 01:41:54 MESZ"
"""

import re
from pathlib import Path
from datetime import datetime

html_path = Path(r"C:\evoki\backend\Google Massenexport 16.10.25\MeineAktivitäten.html")
output_file = Path(r"C:\evoki\backend\HTML_DIRECT_ANALYSIS.txt")

print("="*80)
print("DIREKTE HTML-ANALYSE (Rohdatei, keine TXT-Zwischenschicht)")
print("="*80)

# Das korrekte Pattern: "03.10.2025, 01:41:54 MESZ"
timestamp_pattern = r'(\d{1,2})\.(\d{1,2})\.(\d{4}),?\s+(\d{1,2}):(\d{2}):(\d{2})\s*(?:MESZ|UTC|MEZ)?'

all_timestamps = []
context_samples = []

# Lese die gesamte Datei in Chunks
chunk_size = 2 * 1024 * 1024  # 2MB
with open(html_path, 'rb') as f:
    file_size = html_path.stat().st_size
    bytes_read = 0
    
    while bytes_read < file_size:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        
        # Dekodiere mit Fehlerignore
        text = chunk.decode('utf-8', errors='ignore')
        
        # Finde alle Timestamps MIT Kontext
        for match in re.finditer(timestamp_pattern, text):
            day, month, year, hour, minute, second = match.groups()
            timestamp_str = f"{year}-{month.zfill(2)}-{day.zfill(2)} {hour.zfill(2)}:{minute}:{second}"
            
            try:
                ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                all_timestamps.append(ts)
                
                # Extrahiere Context (100 Zeichen vorher/nachher)
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].replace('\n', ' ')
                context_samples.append((ts, context))
            except:
                pass
        
        bytes_read += len(chunk)
        pct = 100 * bytes_read / file_size
        print(f"  [{pct:5.1f}%] {bytes_read/(1024*1024):6.1f} / {file_size/(1024*1024):6.1f} MB ... {len(all_timestamps):6} TS")

print(f"\n✅ ERGEBNISSE:")
print(f"   Timestamps gefunden: {len(all_timestamps)}")

if all_timestamps:
    all_timestamps_sorted = sorted(all_timestamps)
    print(f"   Zeitspanne (sortiert): {all_timestamps_sorted[0]} bis {all_timestamps_sorted[-1]}")
    
    # Detektiere negative Paare in ORIGINAL-Reihenfolge (wie sie in der Datei stehen)
    print(f"\n   ANALYSE DER ORIGINAL-REIHENFOLGE:")
    negative_pairs = []
    max_backward = None
    max_backward_diff = 0
    
    for i in range(len(all_timestamps) - 1):
        if all_timestamps[i+1] < all_timestamps[i]:
            diff_seconds = (all_timestamps[i] - all_timestamps[i+1]).total_seconds()
            negative_pairs.append((i, all_timestamps[i], all_timestamps[i+1], diff_seconds))
            
            if diff_seconds > max_backward_diff:
                max_backward_diff = diff_seconds
                max_backward = (i, all_timestamps[i], all_timestamps[i+1], diff_seconds)
    
    print(f"   Negative Paare (Rücksprünge): {len(negative_pairs)}")
    
    if max_backward:
        idx, ts1, ts2, diff = max_backward
        print(f"\n   🔴 GRÖSSTER RÜCKSPRUNG (Index {idx}):")
        print(f"       {ts1} → {ts2}")
        print(f"       Differenz: {diff}s = {diff/3600:.1f}h = {diff/86400:.2f}d")

# Schreibe Report
with open(output_file, 'w', encoding='utf-8') as out:
    out.write("="*80 + "\n")
    out.write("HTML-DIREKTANALYSE (Rohdatei)\n")
    out.write("="*80 + "\n\n")
    
    out.write(f"Datei: {html_path}\n")
    out.write(f"Größe: {file_size / (1024*1024):.1f} MB\n")
    out.write(f"Timestamps gefunden: {len(all_timestamps)}\n\n")
    
    if all_timestamps:
        out.write(f"Zeitspanne: {min(all_timestamps)} bis {max(all_timestamps)}\n")
        out.write(f"Zeitspanne (sortiert): {sorted(all_timestamps)[0]} bis {sorted(all_timestamps)[-1]}\n\n")
        
        out.write("NEGATIVE PAARE:\n")
        out.write("-"*80 + "\n")
        negative_pairs_sorted = sorted(negative_pairs, key=lambda x: x[3], reverse=True)
        for idx, ts1, ts2, diff in negative_pairs_sorted[:20]:
            out.write(f"Position {idx}: {ts1} → {ts2}\n")
            out.write(f"  Rücksprung: {diff}s ({diff/3600:.1f}h)\n\n")

print(f"\n📄 Report gespeichert: {output_file}")
