#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grundwort-Häufigkeitsanalyse basierend auf Zeitsprung-Daten
Analysiert die häufigsten Keywords und Begriffe aus den Chat-Anomalien
"""

import json
import re
from collections import Counter
from datetime import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 100)
print("[GRUNDWORT-ANALYSE] Evoki Chat-Daten - Häufigkeitsanalyse der Grundwörter")
print("=" * 100)

# Lade Zeitsprung-Daten
print("\n[SCHRITT 1] Lade Zeitsprung-Exhumierung-Daten...")
try:
    with open('C:/evoki/backend/zeitsprung_exhumierung_vollstaendig.json', 'r', encoding='utf-8') as f:
        timewarp_data = json.load(f)
    anomalies = timewarp_data.get('anomalies', [])
    print(f"✅ {len(anomalies)} Anomalien mit Context-Blöcken geladen")
except Exception as e:
    print(f"❌ Fehler: {e}")
    anomalies = []

# Sammle alle Texte aus Kontext-Blöcken
print("\n[SCHRITT 2] Extrahiere Text aus Kontext-Blöcken...")

all_texts = []
context_blocks_count = 0

for anomaly in anomalies:
    if 'context_blocks' in anomaly:
        blocks = anomaly['context_blocks']
        if isinstance(blocks, dict):
            for block_type, block_content in blocks.items():
                if isinstance(block_content, str) and block_content.strip():
                    all_texts.append(block_content)
                    context_blocks_count += 1

print(f"✅ {context_blocks_count} Kontext-Blöcke extrahiert")
print(f"✅ {len(all_texts)} Text-Segmente zur Analyse verfügbar")

# Definiere Stop-Words (häufige Funktionswörter, die keine Bedeutung tragen)
stop_words = {
    # Deutsche Stop-Words
    'die', 'der', 'das', 'und', 'ist', 'in', 'zu', 'von', 'den', 'mit', 'für',
    'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr', 'mich', 'dich', 'sich',
    'mir', 'dir', 'uns', 'euch', 'den', 'dem', 'das', 'denen',
    'ein', 'eine', 'einen', 'einer', 'einem', 'eins',
    'was', 'wie', 'wo', 'wann', 'warum', 'wer', 'wen', 'wem', 'wessen',
    'bin', 'bist', 'seid', 'sind', 'habe', 'hast', 'hat', 'haben', 'habt',
    'mein', 'dein', 'sein', 'sein', 'unser', 'euer',
    'auf', 'über', 'unter', 'neben', 'vor', 'nach', 'zwischen', 'an', 'bei',
    'aber', 'oder', 'denn', 'wenn', 'dann', 'weil', 'obwohl', 'während',
    'sehr', 'so', 'nur', 'auch', 'noch', 'immer', 'schon', 'eben', 'ja', 'nein',
    'doch', 'ach', 'oh', 'ah', 'hm', 'hmm', 'huh', 'eh', 'naja',
    'dieser', 'dieses', 'diesen', 'dieser', 'diesem',
    'that', 'this', 'these', 'those', 'a', 'an', 'the', 'of', 'or', 'not',
    'be', 'have', 'do', 'go', 'get', 'can', 'will', 'would', 'should', 'could',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
}

# Extrahiere Wörter
print("\n[SCHRITT 3] Analysiere Wörter aus Texten...")

word_counter = Counter()
word_length_counter = Counter()
total_words = 0
analyzed_chars = 0

for text in all_texts:
    if not isinstance(text, str):
        continue
    
    analyzed_chars += len(text)
    
    # Konvertiere zu Kleinbuchstaben
    text = text.lower()
    
    # Entferne Sonderzeichen aber behalte Umlaute
    text = re.sub(r'[^\w\säöüß\-]', ' ', text)
    
    # Teile in Wörter
    words = text.split()
    
    for word in words:
        word = word.strip('-').strip()
        # Behalte nur Wörter mit mehr als 2 Zeichen, nicht in Stop-Words
        if len(word) > 2 and word not in stop_words:
            word_counter[word] += 1
            word_length_counter[len(word)] += 1
            total_words += 1

print(f"✅ {len(word_counter)} einzigartige Wörter identifiziert")
print(f"✅ {total_words} Gesamt-Wort-Vorkommen")
print(f"✅ {analyzed_chars} Zeichen analysiert")

# Top Wörter
print("\n" + "=" * 100)
print("[TOP 50 GRUNDWÖRTER] - Häufigste Begriffe in den Zeitsprung-Anomalien")
print("=" * 100)

print(f"\n{'Rang':<5} {'Wort':<25} {'Häufigkeit':<15} {'Prozent':<10} {'Wort-Länge':<10}")
print("-" * 65)

for i, (word, count) in enumerate(word_counter.most_common(50), 1):
    percentage = (count / total_words) * 100 if total_words > 0 else 0
    print(f"{i:<5} {word:<25} {count:<15} {percentage:>6.2f}% {len(word):>10}")

# Häufigkeit nach Wortlänge
print("\n" + "=" * 100)
print("[WORT-LÄNGEN-VERTEILUNG]")
print("=" * 100)

print(f"\n{'Länge':<8} {'Anzahl':<15} {'%':<10}")
print("-" * 35)

for length in sorted(word_length_counter.keys()):
    count = word_length_counter[length]
    percentage = (count / total_words) * 100 if total_words > 0 else 0
    print(f"{length:<8} {count:<15} {percentage:>6.2f}%")

# Thematische Analyse - Gruppiere ähnliche Wörter
print("\n" + "=" * 100)
print("[THEMATISCHE GRUPPEN] - Emotionen, Psychologie, Trauma")
print("=" * 100)

theme_groups = {
    'Trauma & Angst': ['trauma', 'angst', 'angststörung', 'panik', 'schrecken', 'horror', 'furcht'],
    'Stress & Belastung': ['stress', 'belastung', 'überfordert', 'anspannung', 'burnout', 'erschöpfung'],
    'Einsamkeit & Verlust': ['einsamkeit', 'verlust', 'trauer', 'traurigkeit', 'alleine', 'verlassen'],
    'Verzweiflung & Hoffnung': ['verzweiflung', 'hoffnung', 'hoffnungslos', 'aussichtslos', 'trostlos'],
    'Vertrauen & Beziehung': ['vertrauen', 'vertrauenskrise', 'beziehung', 'bindung', 'nähe', 'distanz'],
    'Körper & Schmerz': ['schmerz', 'körper', 'körperlich', 'verletzung', 'verletzt', 'schwäche'],
    'Gedanken & Bewusstsein': ['gedanke', 'gedanken', 'bewusstsein', 'bewusst', 'unbewusst', 'erkenntnis'],
    'Zeit & Kontinuität': ['zeit', 'zeitsprung', 'kontinuität', 'erinnerung', 'moment', 'gegenwart', 'zukunft'],
}

print("\n{'Thema':<35} {'Relevante Wörter (Top 5)':<65}")
print("-" * 100)

for theme, keywords in theme_groups.items():
    found_words = []
    for keyword in keywords:
        if keyword in word_counter:
            found_words.append(f"{keyword}({word_counter[keyword]})")
    
    if found_words:
        top_words = ', '.join(found_words[:5])
        print(f"{theme:<35} {top_words:<65}")

# Speichere detaillierte Ergebnisse
print("\n[SCHRITT 4] Speichere Ergebnisse...")

results = {
    'timestamp': datetime.now().isoformat(),
    'analysis_type': 'Grundwort-Häufigkeitsanalyse',
    'data_source': 'zeitsprung_exhumierung_vollstaendig.json',
    'statistics': {
        'total_anomalies': len(anomalies),
        'context_blocks_analyzed': context_blocks_count,
        'unique_words': len(word_counter),
        'total_word_occurrences': total_words,
        'total_characters_analyzed': analyzed_chars,
    },
    'top_100_words': dict(word_counter.most_common(100)),
    'word_length_distribution': dict(word_length_counter),
    'themed_words': {}
}

# Speichere thematische Wörter
for theme, keywords in theme_groups.items():
    found = {}
    for keyword in keywords:
        if keyword in word_counter:
            found[keyword] = word_counter[keyword]
    if found:
        results['themed_words'][theme] = dict(sorted(found.items(), key=lambda x: x[1], reverse=True))

with open('C:/evoki/backend/grundwort_analyse_ergebnisse.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("✅ Gespeichert: grundwort_analyse_ergebnisse.json")

# Zusammenfassung
print("\n" + "=" * 100)
print("[ZUSAMMENFASSUNG DER GRUNDWORT-ANALYSE]")
print("=" * 100)

print(f"""
DATENQUELLE:
  └─ zeitsprung_exhumierung_vollstaendig.json

ANALYSIUMFANG:
  ├─ Anomalien: {len(anomalies)}
  ├─ Kontext-Blöcke: {context_blocks_count}
  ├─ Zeichen analysiert: {analyzed_chars:,}
  └─ Gesamt-Wort-Vorkommen: {total_words:,}

ERGEBNISSE:
  ├─ Einzigartige Wörter: {len(word_counter)}
  ├─ Durchschnittliche Wort-Länge: {sum(len(w)*c for w,c in word_counter.items())/total_words:.1f} Zeichen
  └─ Wort-Längen-Range: {min(word_length_counter.keys())}-{max(word_length_counter.keys())} Zeichen

TOP 10 HÄUFIGSTE WÖRTER:
""")

for i, (word, count) in enumerate(word_counter.most_common(10), 1):
    percentage = (count / total_words) * 100
    print(f"  {i:>2}. {word:<20} - {count:>6}x ({percentage:>5.2f}%)")

print(f"""
THEMATISCHE SCHWERPUNKTE:
  ├─ Trauma & Angst: {sum(1 for w in theme_groups['Trauma & Angst'] if w in word_counter)} Wörter
  ├─ Stress & Belastung: {sum(1 for w in theme_groups['Stress & Belastung'] if w in word_counter)} Wörter
  ├─ Einsamkeit & Verlust: {sum(1 for w in theme_groups['Einsamkeit & Verlust'] if w in word_counter)} Wörter
  ├─ Verzweiflung: {sum(1 for w in theme_groups['Verzweiflung & Hoffnung'] if w in word_counter)} Wörter
  └─ Zeit & Kontinuität: {sum(1 for w in theme_groups['Zeit & Kontinuität'] if w in word_counter)} Wörter
""")

print("✅ GRUNDWORT-ANALYSE COMPLETE")
