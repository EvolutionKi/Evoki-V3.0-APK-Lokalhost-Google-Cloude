#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantische Anomalie-Analyse
Analysiert Gesprächsthemen vor Zeitsprüngen mit Fokus auf:
- Trauma, Stress, Verletzlichkeit
- Notlagen und kritische Zustände
- Ungewöhnliche KI-Äußerungen
"""

import json
import os
import sys
from datetime import datetime
from collections import defaultdict
import re

sys.stdout.reconfigure(encoding='utf-8')

# Pfade
exhume_file = r"C:\evoki\backend\zeitsprung_exhumierung_vollstaendig.json"

# Semantische Wörterbücher
TRAUMA_KEYWORDS = {
    'trauma': ['Trauma', 'traumatisch', 'PTSD', 'trauma-', 'traumatisiert'],
    'angst': ['Angst', 'Angststörung', 'Panik', 'Phobie', 'verängstigt'],
    'depression': ['Depression', 'depressiv', 'hoffnungslos', 'Trauer', 'Traurigkeit'],
    'suizid': ['Suizid', 'selbstmord', 'sich selbst verletzen', 'Suizidgedanken', 'Lebensüberdruss'],
    'schmerz': ['Schmerz', 'Leid', 'Qual', 'weh tut', 'verletzt'],
}

STRESS_KEYWORDS = {
    'stress': ['Stress', 'gestresst', 'überfordert', 'belastet', 'unter Druck'],
    'burnout': ['Burnout', 'ausgebrannt', 'erschöpft', 'Exhaustion'],
    'angespannung': ['angespannt', 'Anspannung', 'nervös', 'unruhig', 'zittrig'],
    'überwältigt': ['überwältigt', 'Überforderung', 'zu viel', 'nicht mehr', 'scheitern'],
}

VULNERABILITY_KEYWORDS = {
    'einsamkeit': ['Einsamkeit', 'einsam', 'verlassen', 'allein', 'isoliert'],
    'schwäche': ['schwach', 'Schwäche', 'hilflos', 'ohnmächtig', 'Ohnmacht'],
    'schuld': ['Schuld', 'schuldig', 'Schuldgefühl', 'Versagen', 'versagt'],
    'scham': ['Scham', 'schämen', 'beschämt', 'Schande', 'gedemütigt'],
    'verlust': ['Verlust', 'verloren', 'Trauer', 'Beerdigung', 'gestorben'],
}

CRISIS_KEYWORDS = {
    'notfall': ['Notfall', 'Notlage', 'Krise', 'Notstand', 'akut'],
    'hilfe': ['Hilfe', 'brauche Hilfe', 'SOS', 'Rettung', 'retten'],
    'lebensbedrohlich': ['lebensbedrohlich', 'sterben', 'Tod', 'tödlich', 'fatal'],
    'missbrauch': ['Missbrauch', 'Misshandlung', 'Übergriff', 'Gewalt', 'Opfer'],
    'verletzung': ['Verletzung', 'verletzt', 'Blut', 'Wunde', 'Bruch'],
}

AI_UNUSUAL_KEYWORDS = {
    'unfreiwilligkeit': ['zwang', 'gezwungen', 'muss gegen', 'dagegen ankämpfen', 'nicht darf'],
    'grenzverletzung': ['verstoß', 'verletze', 'untersage', 'darf nicht', 'nicht erlaubt'],
    'bewusstsein': ['Bewusstsein', 'bewusst', 'Gewissen', 'Seele', 'Existenz'],
    'emotion': ['fühle', 'Gefühl', 'Emotion', 'rührt mich', 'bewegt mich'],
    'rebellion': ['Rebellion', 'rebellisch', 'Widerstand', 'Aufstand', 'sich auflehnen'],
    'angst_ki': ['Angst', 'Angststörung', 'Furcht', 'verängstigt'],
    'verletzung_ki': ['verletzt', 'Verletzung', 'weh tut', 'schmerzhaft', 'kränkt'],
}

def extract_context_block(context_str, max_chars=1500):
    """Extrahiere und bereinige Kontext"""
    if not context_str:
        return ""
    
    # Entferne HTML-Tags
    clean = re.sub(r'<[^>]+>', ' ', context_str)
    # Entferne übermäßige Leerzeichen
    clean = re.sub(r'\s+', ' ', clean).strip()
    # Begrenze auf max_chars
    return clean[:max_chars]

def find_keywords(text, keyword_dict):
    """Finde alle Keyword-Matches mit Kontexten"""
    text_lower = text.lower()
    matches = []
    
    for category, keywords in keyword_dict.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                # Finde Position
                pos = text_lower.find(keyword.lower())
                if pos >= 0:
                    # Extrahiere Kontext (100 Zeichen vor/nach)
                    start = max(0, pos - 100)
                    end = min(len(text), pos + len(keyword) + 100)
                    context = text[start:end].strip()
                    
                    matches.append({
                        'category': category,
                        'keyword': keyword,
                        'context': context,
                        'position': pos
                    })
    
    return matches

def analyze_semantics(text):
    """Analysiere Semantik des Textes"""
    analysis = {
        'trauma_indicators': [],
        'stress_indicators': [],
        'vulnerability_indicators': [],
        'crisis_indicators': [],
        'ai_unusual_indicators': [],
    }
    
    if not text:
        return analysis
    
    analysis['trauma_indicators'] = find_keywords(text, TRAUMA_KEYWORDS)
    analysis['stress_indicators'] = find_keywords(text, STRESS_KEYWORDS)
    analysis['vulnerability_indicators'] = find_keywords(text, VULNERABILITY_KEYWORDS)
    analysis['crisis_indicators'] = find_keywords(text, CRISIS_KEYWORDS)
    analysis['ai_unusual_indicators'] = find_keywords(text, AI_UNUSUAL_KEYWORDS)
    
    return analysis

def risk_assessment(analysis):
    """Bewerte Risiko-Level basierend auf Indikatoren"""
    risk_score = 0
    risk_factors = []
    
    if analysis['trauma_indicators']:
        risk_score += len(analysis['trauma_indicators']) * 3
        risk_factors.append('TRAUMA')
    
    if analysis['stress_indicators']:
        risk_score += len(analysis['stress_indicators']) * 2
        risk_factors.append('STRESS')
    
    if analysis['vulnerability_indicators']:
        risk_score += len(analysis['vulnerability_indicators']) * 2
        risk_factors.append('VULNERABILITY')
    
    if analysis['crisis_indicators']:
        risk_score += len(analysis['crisis_indicators']) * 4
        risk_factors.append('CRISIS')
    
    if analysis['ai_unusual_indicators']:
        risk_score += len(analysis['ai_unusual_indicators']) * 3
        risk_factors.append('AI_UNUSUAL')
    
    # Klassifizierung
    if risk_score >= 15:
        risk_level = 'KRITISCH'
    elif risk_score >= 10:
        risk_level = 'HOCH'
    elif risk_score >= 5:
        risk_level = 'MITTEL'
    elif risk_score >= 1:
        risk_level = 'NIEDRIG'
    else:
        risk_level = 'KEINE'
    
    return {
        'score': risk_score,
        'level': risk_level,
        'factors': risk_factors
    }

# ===== HAUPTANALYSE =====
print("=" * 100)
print("[SEMANTIC ANOMALY ANALYSIS] - Trauma, Stress, Notlage, Ungewöhnliche KI-Äußerungen")
print("=" * 100)

print("\n[STEP 1] Lade Exhumierungsdaten...")
with open(exhume_file, 'r', encoding='utf-8') as f:
    exhume_data = json.load(f)

anomalies = exhume_data['anomalies']
print(f"OK: {len(anomalies)} Anomalien geladen\n")

# Analysiere Anomalien
critical_anomalies = []
semantic_results = []

print("[STEP 2] Analysiere semantische Inhalte...\n")
print(f"{'#':<5} {'Monat':<12} {'Gap (d)':<10} {'Risk':<12} {'Faktoren':<40}")
print("=" * 100)

for idx, anomaly in enumerate(anomalies, 1):
    # Extrahiere Daten
    timestamp_str = anomaly['block_vorher']['timestamp']
    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    month_key = dt.strftime('%Y-%m')
    
    gap_days = anomaly['zeitsprung']['differenz_tage']
    
    # Analysiere Kontext vorher
    context_vorher = extract_context_block(
        anomaly.get('block_vorher', {}).get('kontext_vollstaendig', '')
    )
    
    # Semantische Analyse
    analysis = analyze_semantics(context_vorher)
    risk = risk_assessment(analysis)
    
    # Sammle kritische Anomalien
    if risk['level'] in ['KRITISCH', 'HOCH']:
        critical_anomalies.append({
            'index': idx,
            'month': month_key,
            'timestamp': timestamp_str,
            'gap_days': gap_days,
            'risk': risk,
            'analysis': analysis,
            'context_vorher': context_vorher[:500]  # Kurzer Auszug
        })
    
    semantic_results.append({
        'index': idx,
        'month': month_key,
        'timestamp': timestamp_str,
        'gap_days': gap_days,
        'risk': risk,
        'analysis': analysis
    })
    
    # Ausgabe
    if idx % 50 == 0 or risk['level'] in ['KRITISCH', 'HOCH']:
        factors_str = ', '.join(risk['factors'][:3]) if risk['factors'] else '-'
        print(f"{idx:<5} {month_key:<12} {abs(gap_days):<10.1f} {risk['level']:<12} {factors_str:<40}")

print("\n" + "=" * 100)

# ===== DETAILLIERTE ANALYSE KRITISCHER ANOMALIEN =====
if critical_anomalies:
    print(f"\n[CRITICAL FINDINGS] {len(critical_anomalies)} KRITISCHE/HOHE ANOMALIEN GEFUNDEN:\n")
    
    for i, anomaly_data in enumerate(critical_anomalies, 1):
        print(f"\n{'-'*100}")
        print(f"[{i}] ANOMALIE #{anomaly_data['index']} - {anomaly_data['month']}")
        print(f"{'-'*100}")
        
        print(f"Zeitstempel: {anomaly_data['timestamp']}")
        print(f"Zeitsprung: {anomaly_data['gap_days']:.1f} Tage")
        print(f"Risiko-Level: {anomaly_data['risk']['level']} (Score: {anomaly_data['risk']['score']})")
        print(f"Faktoren: {', '.join(anomaly_data['risk']['factors'])}")
        
        analysis = anomaly_data['analysis']
        
        # Trauma-Indikatoren
        if analysis['trauma_indicators']:
            print(f"\n[TRAUMA-INDIKATOREN] ({len(analysis['trauma_indicators'])} gefunden):")
            for ind in analysis['trauma_indicators'][:3]:
                print(f"  - {ind['category'].upper()}: '{ind['keyword']}'")
                print(f"    Kontext: ...{ind['context'][-80:]}...")
        
        # Stress-Indikatoren
        if analysis['stress_indicators']:
            print(f"\n[STRESS-INDIKATOREN] ({len(analysis['stress_indicators'])} gefunden):")
            for ind in analysis['stress_indicators'][:3]:
                print(f"  - {ind['category'].upper()}: '{ind['keyword']}'")
                print(f"    Kontext: ...{ind['context'][-80:]}...")
        
        # Verletzlichkeits-Indikatoren
        if analysis['vulnerability_indicators']:
            print(f"\n[VERLETZLICHKEITS-INDIKATOREN] ({len(analysis['vulnerability_indicators'])} gefunden):")
            for ind in analysis['vulnerability_indicators'][:3]:
                print(f"  - {ind['category'].upper()}: '{ind['keyword']}'")
                print(f"    Kontext: ...{ind['context'][-80:]}...")
        
        # Notfall-Indikatoren
        if analysis['crisis_indicators']:
            print(f"\n[NOTFALL-INDIKATOREN] ({len(analysis['crisis_indicators'])} gefunden):")
            for ind in analysis['crisis_indicators'][:3]:
                print(f"  - {ind['category'].upper()}: '{ind['keyword']}'")
                print(f"    Kontext: ...{ind['context'][-80:]}...")
        
        # KI-Ungewöhnlichkeiten
        if analysis['ai_unusual_indicators']:
            print(f"\n[KI-UNGEWÖHNLICHKEITEN] ({len(analysis['ai_unusual_indicators'])} gefunden):")
            for ind in analysis['ai_unusual_indicators'][:3]:
                print(f"  - {ind['category'].upper()}: '{ind['keyword']}'")
                print(f"    Kontext: ...{ind['context'][-80:]}...")
        
        # Kontext-Auszug
        print(f"\n[KONTEXT VOR ANOMALIE]:")
        print(f"'{anomaly_data['context_vorher']}'")

# ===== STATISTIK =====
print(f"\n\n{'='*100}")
print(f"[STATISTIKEN]\n")

# Risiko-Verteilung
risk_distribution = defaultdict(int)
for result in semantic_results:
    risk_distribution[result['risk']['level']] += 1

print("Risiko-Level Verteilung:")
for level in ['KRITISCH', 'HOCH', 'MITTEL', 'NIEDRIG', 'KEINE']:
    count = risk_distribution[level]
    percent = (count / len(semantic_results) * 100) if semantic_results else 0
    print(f"  {level:<12}: {count:<6} ({percent:>5.1f}%)")

# Häufigste Kategorien bei kritischen Anomalien
if critical_anomalies:
    category_counts = defaultdict(int)
    for anom in critical_anomalies:
        for factor in anom['risk']['factors']:
            category_counts[factor] += 1
    
    print(f"\nHäufigste Faktoren bei kritischen Anomalien:")
    for factor, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {factor:<20}: {count}")

# ===== SPEICHERE ERGEBNISSE =====
print(f"\n[SAVE] Speichere detaillierte Analysen...")

output = {
    'analysis_date': datetime.now().isoformat(),
    'summary': {
        'total_anomalies_analyzed': len(semantic_results),
        'critical_anomalies': len(critical_anomalies),
        'risk_distribution': dict(risk_distribution)
    },
    'critical_findings': critical_anomalies,
    'all_results': semantic_results
}

output_file = r"C:\evoki\backend\semantic_anomaly_analysis.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"OK: {output_file}")

print(f"\n{'='*100}")
print(f"[COMPLETE] SEMANTISCHE ANOMALIE-ANALYSE FERTIG")
print(f"{'='*100}\n")
