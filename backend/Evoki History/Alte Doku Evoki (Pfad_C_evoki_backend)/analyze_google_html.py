#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GOOGLE MASSENEXPORT HTML ANALYSE
================================
Analysiert MeineAktivitäten.html direkt - Struktur, Zeitstempel, Inhalte
"""

import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import html as html_parser

HTML_FILE = Path(r"C:\evoki\backend\Google Massenexport 16.10.25\MeineAktivitäten.html")
OUTPUT_FILE = Path(r"C:\evoki\backend\GOOGLE_HTML_ANALYSE.txt")

print("=" * 80)
print("GOOGLE MASSENEXPORT HTML ANALYSE")
print("=" * 80)

if not HTML_FILE.exists():
    print(f"❌ FEHLER: {HTML_FILE} nicht gefunden")
    exit(1)

print(f"\n📄 Datei: {HTML_FILE}")
print(f"📊 Größe: {HTML_FILE.stat().st_size / 1024 / 1024:.1f} MB")

# Lese die HTML in Chunks (um nicht alles in RAM zu laden)
print("\n[SCAN 1] Grundstruktur & Zeilenzahl...")

total_lines = 0
html_content = ""
try:
    with open(HTML_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read(10_000_000)  # Lese erste 10MB
        total_lines = html_content.count('\n')
except Exception as e:
    print(f"❌ Fehler beim Lesen: {e}")
    exit(1)

print(f"  Total Zeilen (Excerpt): {total_lines:,}")
print(f"  Zeichen gelesen: {len(html_content):,}")

# Analysiere Struktur
print("\n[SCAN 2] HTML-Struktur...")

# Zähle Tags
div_count = html_content.count('<div')
span_count = html_content.count('<span')
a_count = html_content.count('<a')
br_count = html_content.count('<br')

print(f"  <div>: {div_count:,}")
print(f"  <span>: {span_count:,}")
print(f"  <a>: {a_count:,}")
print(f"  <br>: {br_count:,}")

# Suche nach Zeitstempeln (Google Format)
print("\n[SCAN 3] Zeitstempel-Muster...")

# Google Activity Logs Format: "Jan 15, 2024, 10:30:45 AM" oder ähnlich
timestamp_patterns = [
    r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s+(\d{4}),\s+(\d{1,2}):(\d{2}):(\d{2})\s+(AM|PM)',
    r'(\d{1,2})\.\s+(Jan|Feb|Mär|Apr|Mai|Jun|Jul|Aug|Sep|Okt|Nov|Dez)\s+(\d{4})\s+(\d{1,2}):(\d{2})',
    r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})',
]

timestamps_found = []
for pattern in timestamp_patterns:
    matches = re.findall(pattern, html_content, re.IGNORECASE)
    timestamps_found.extend(matches)

print(f"  Zeitstempel gefunden: {len(timestamps_found):,}")

if timestamps_found:
    # Zeige erste 10
    print(f"  Beispiele:")
    for ts in timestamps_found[:10]:
        print(f"    - {ts}")

# Suche nach Aktivitäts-Kategorien
print("\n[SCAN 4] Aktivitäts-Kategorien (Schlüsselwörter)...")

categories = defaultdict(int)
category_keywords = {
    'Search': ['search', 'suche', 'query'],
    'Visit': ['visited', 'view', 'besuch', 'geöffnet'],
    'Click': ['clicked', 'click', 'angeklickt'],
    'Download': ['download', 'heruntergeladen'],
    'Watch': ['watch', 'watched', 'video', 'youtube'],
    'Comment': ['comment', 'wrote', 'posted', 'kommentar'],
    'Share': ['share', 'shared', 'geteilt'],
    'Upload': ['upload', 'hochgeladen'],
}

content_lower = html_content.lower()
for category, keywords in category_keywords.items():
    for keyword in keywords:
        count = content_lower.count(keyword)
        if count > 0:
            categories[category] += count

for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    print(f"  {category:15s}: {count:6,}")

# Suche nach URLs/Domains
print("\n[SCAN 5] URL/Domain-Extraktion...")

url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]*'
urls = re.findall(url_pattern, html_content)
print(f"  URLs gefunden: {len(urls):,}")

domains = defaultdict(int)
for url in urls:
    # Extrahiere Domain
    match = re.search(r'https?://([^/]+)', url)
    if match:
        domain = match.group(1)
        domains[domain] += 1

print(f"  Eindeutige Domains: {len(domains)}")
print(f"  Top 10 Domains:")
for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"    - {domain:40s}: {count:6,}")

# Suche nach Textinhalten (nicht-HTML)
print("\n[SCAN 6] Textinhalt-Analyse...")

# Entferne HTML-Tags für Text-Analyse
text_only = re.sub(r'<[^>]+>', '', html_content)
text_only = html_parser.unescape(text_only)
words = re.findall(r'\b\w+\b', text_only.lower())

print(f"  Wörter (nach Tag-Removal): {len(words):,}")
print(f"  Zeichen: {len(text_only):,}")
print(f"  Durchschnittliche Wortlänge: {sum(len(w) for w in words) / len(words) if words else 0:.1f}")

# Häufigste Wörter
from collections import Counter
word_freq = Counter(words)
common_words = [w for w, c in word_freq.most_common(50) if len(w) > 3]  # Nur Wörter >3 Zeichen

print(f"  Häufigste Wörter (>3 Zeichen):")
for word, count in word_freq.most_common(15):
    if len(word) > 3:
        print(f"    - {word:20s}: {count:6,}")

# Zeitstempel-Verteilung
print("\n[SCAN 7] Zeitstempel-Verteilung...")

# Extrahiere Jahreszahlen
years = re.findall(r'\b(19|20)\d{2}\b', html_content)
year_freq = Counter(years)

print(f"  Jahreszahlen gefunden:")
for year, count in sorted(year_freq.items(), key=lambda x: x[1], reverse=True):
    print(f"    - 20{year}: {count:6,}" if year == '24' or year == '25' else f"    - {year}: {count:6,}")

# Schreibe Report
print(f"\n{'=' * 80}")
print("SCHREIBE REPORT...")

report_lines = [
    "GOOGLE MASSENEXPORT HTML - DETAILLIERTE ANALYSE",
    "=" * 80,
    f"Scan-Datum: {datetime.now().isoformat()}",
    f"Quelle: {HTML_FILE}",
    f"Dateigröße: {HTML_FILE.stat().st_size / 1024 / 1024:.1f} MB",
    f"\n=== STRUKTUR ===",
    f"Total Zeilen (Excerpt): {total_lines:,}",
    f"<div> Tags: {div_count:,}",
    f"<span> Tags: {span_count:,}",
    f"<a> Tags: {a_count:,}",
    f"<br> Tags: {br_count:,}",
    f"\n=== ZEITSTEMPEL ===",
    f"Gefundene Zeitstempel: {len(timestamps_found):,}",
]

if timestamps_found:
    report_lines.extend([
        f"Format-Beispiele:",
    ])
    for ts in timestamps_found[:5]:
        report_lines.append(f"  {ts}")

report_lines.extend([
    f"\n=== AKTIVITÄTS-KATEGORIEN ===",
])

for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    report_lines.append(f"{category:20s}: {count:8,}")

report_lines.extend([
    f"\n=== DOMAINS (Top 20) ===",
])

for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:20]:
    report_lines.append(f"{domain:50s}: {count:8,}")

report_lines.extend([
    f"\n=== TEXT-INHALT ===",
    f"Wörter: {len(words):,}",
    f"Zeichen: {len(text_only):,}",
    f"Eindeutige Wörter: {len(word_freq):,}",
    f"\nHäufigste Wörter (>3 Zeichen):",
])

for word, count in word_freq.most_common(20):
    if len(word) > 3:
        report_lines.append(f"  {word:30s}: {count:8,}")

report_lines.extend([
    f"\n=== NÄCHSTE SCHRITTE ===",
    f"1. html_forensic_extractor_v2.py re-run (wenn Änderungen in HTML)",
    f"2. Vektoren berechnen: vectorize_COMPLETE.py",
    f"3. Trialog aktivieren für tiefere Analyse",
])

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f"✅ Report gespeichert: {OUTPUT_FILE}\n")

