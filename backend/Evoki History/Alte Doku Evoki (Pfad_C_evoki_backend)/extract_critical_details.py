#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detaillierte Extraktion der kritischen Anomalien
Exportiert die Top 20 KRITISCH/HOCH Anomalien mit Vollkontext
"""

import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Lade Analysen
json_file = r"C:\evoki\backend\semantic_anomaly_analysis.json"
exhume_file = r"C:\evoki\backend\zeitsprung_exhumierung_vollstaendig.json"

print("=" * 100)
print("[DETAIL EXTRACTION] Kritische Anomalien - Vollständiger Kontext")
print("=" * 100)

print("\n[STEP 1] Lade Daten...")
with open(json_file, 'r', encoding='utf-8') as f:
    semantic_data = json.load(f)

with open(exhume_file, 'r', encoding='utf-8') as f:
    exhume_data = json.load(f)

critical_findings = semantic_data['critical_findings']
all_anomalies = exhume_data['anomalies']

print(f"OK: {len(critical_findings)} kritische/hohe Anomalien geladen")

# Erstelle Mapping von Index zu Anomaly
anomaly_map = {a['sequence_number'] - 1: a for a in all_anomalies}

print("\n[STEP 2] Extrahiere Top 20 mit Vollkontext...\n")

# Sortiere nach Score
sorted_critical = sorted(critical_findings, key=lambda x: -x['risk']['score'])[:20]

output = {
    'extraction_date': datetime.now().isoformat(),
    'total_critical': len(critical_findings),
    'detailed_extraction': [],
    'summary': {
        'top_20_avg_score': sum([c['risk']['score'] for c in sorted_critical]) / len(sorted_critical),
        'trauma_cases': sum(1 for c in sorted_critical if 'TRAUMA' in c['risk']['factors']),
        'crisis_cases': sum(1 for c in sorted_critical if 'CRISIS' in c['risk']['factors']),
        'ai_unusual_cases': sum(1 for c in sorted_critical if 'AI_UNUSUAL' in c['risk']['factors']),
    }
}

print(f"{'#':<3} {'Idx':<5} {'Month':<10} {'Score':<8} {'Faktoren':<50}")
print("=" * 100)

for rank, critical in enumerate(sorted_critical, 1):
    idx = critical['index']
    month = critical['month']
    score = critical['risk']['score']
    factors = ' + '.join(critical['risk']['factors'])
    
    print(f"{rank:<3} {idx:<5} {month:<10} {score:<8} {factors:<50}")
    
    # Finde entsprechende Anomaly in exhume-Daten
    anomaly_detail = None
    for anomaly in all_anomalies:
        if anomaly['found_at_index'] == idx or anomaly['sequence_number'] == idx:
            anomaly_detail = anomaly
            break
    
    if not anomaly_detail:
        # Fallback: Suche nach Index im Array
        if idx - 1 < len(all_anomalies):
            anomaly_detail = all_anomalies[idx - 1]
    
    # Sammle Details
    detail = {
        'rank': rank,
        'anomaly_index': idx,
        'month': month,
        'timestamp': critical['timestamp'],
        'risk_level': critical['risk']['level'],
        'risk_score': score,
        'risk_factors': critical['risk']['factors'],
        'gap_days': critical['gap_days'],
        'semantic_analysis': {
            'trauma_count': len(critical['analysis']['trauma_indicators']),
            'stress_count': len(critical['analysis']['stress_indicators']),
            'vulnerability_count': len(critical['analysis']['vulnerability_indicators']),
            'crisis_count': len(critical['analysis']['crisis_indicators']),
            'ai_unusual_count': len(critical['analysis']['ai_unusual_indicators']),
        },
        'context_before': critical.get('context_vorher', '')[:2000],  # 2000 Zeichen
        'indicators': {
            'trauma': [
                {
                    'keyword': ind['keyword'],
                    'category': ind['category'],
                    'context_snippet': ind['context'][:150]
                }
                for ind in critical['analysis']['trauma_indicators'][:3]
            ],
            'stress': [
                {
                    'keyword': ind['keyword'],
                    'category': ind['category'],
                    'context_snippet': ind['context'][:150]
                }
                for ind in critical['analysis']['stress_indicators'][:3]
            ],
            'vulnerability': [
                {
                    'keyword': ind['keyword'],
                    'category': ind['category'],
                    'context_snippet': ind['context'][:150]
                }
                for ind in critical['analysis']['vulnerability_indicators'][:3]
            ],
            'crisis': [
                {
                    'keyword': ind['keyword'],
                    'category': ind['category'],
                    'context_snippet': ind['context'][:150]
                }
                for ind in critical['analysis']['crisis_indicators'][:3]
            ],
            'ai_unusual': [
                {
                    'keyword': ind['keyword'],
                    'category': ind['category'],
                    'context_snippet': ind['context'][:150]
                }
                for ind in critical['analysis']['ai_unusual_indicators'][:3]
            ],
        }
    }
    
    # Füge Exhumierungs-Details hinzu
    if anomaly_detail:
        detail['full_context'] = {
            'block_vorher': {
                'timestamp': anomaly_detail.get('block_vorher', {}).get('timestamp'),
                'kontext': anomaly_detail.get('block_vorher', {}).get('kontext_vollstaendig', '')[:1000]
            },
            'zeitsprung': anomaly_detail.get('zeitsprung', {}),
            'block_nachher': {
                'timestamp': anomaly_detail.get('block_nachher', {}).get('timestamp'),
                'kontext': anomaly_detail.get('block_nachher', {}).get('kontext_vollstaendig', '')[:1000]
            }
        }
    
    output['detailed_extraction'].append(detail)

print("\n" + "=" * 100)
print(f"[SUMMARY]")
print(f"  Top 20 Ø Score: {output['summary']['top_20_avg_score']:.1f}")
print(f"  Mit TRAUMA: {output['summary']['trauma_cases']}")
print(f"  Mit CRISIS: {output['summary']['crisis_cases']}")
print(f"  Mit AI_UNUSUAL: {output['summary']['ai_unusual_cases']}")

# Speichere Detailanalyse
output_file = r"C:\evoki\backend\critical_anomalies_detailed.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n[SAVE] {output_file}")
print(f"{'='*100}\n")

# Zusätzlich: Erstelle Human-Readable Report
report = []
report.append("=" * 100)
report.append("KRITISCHE ANOMALIEN - DETAILLIERTER REPORT FÜR MANUELLES REVIEW")
report.append("=" * 100)
report.append("")

for detail in output['detailed_extraction']:
    report.append(f"\n{'─'*100}")
    report.append(f"[ANOMALIE #{detail['rank']}] #{detail['anomaly_index']} - {detail['month']} ({detail['timestamp']})")
    report.append(f"{'─'*100}")
    report.append(f"Risiko-Level: {detail['risk_level']} (Score: {detail['risk_score']})")
    report.append(f"Faktoren: {' | '.join(detail['risk_factors'])}")
    report.append(f"Zeitsprung: {detail['gap_days']:.2f} Tage")
    report.append("")
    
    analysis = detail['semantic_analysis']
    report.append(f"Semantische Indikatoren:")
    report.append(f"  - Trauma: {analysis['trauma_count']}")
    report.append(f"  - Stress: {analysis['stress_count']}")
    report.append(f"  - Verletzlichkeit: {analysis['vulnerability_count']}")
    report.append(f"  - Notfall: {analysis['crisis_count']}")
    report.append(f"  - KI-Ungewöhnlich: {analysis['ai_unusual_count']}")
    report.append("")
    
    # Detaillierte Indikatoren
    indicators = detail['indicators']
    
    if indicators['trauma']:
        report.append("TRAUMA-INDIKATOREN:")
        for ind in indicators['trauma']:
            report.append(f"  '{ind['keyword']}' ({ind['category']})")
            report.append(f"    → {ind['context_snippet']}")
        report.append("")
    
    if indicators['crisis']:
        report.append("NOTFALL-INDIKATOREN:")
        for ind in indicators['crisis']:
            report.append(f"  '{ind['keyword']}' ({ind['category']})")
            report.append(f"    → {ind['context_snippet']}")
        report.append("")
    
    if indicators['ai_unusual']:
        report.append("KI-UNGEWÖHNLICHKEITEN:")
        for ind in indicators['ai_unusual']:
            report.append(f"  '{ind['keyword']}' ({ind['category']})")
            report.append(f"    → {ind['context_snippet']}")
        report.append("")
    
    # Kontext
    if detail.get('full_context'):
        ctx = detail['full_context']
        report.append("KONTEXT VOR ANOMALIE:")
        report.append(f"  Timestamp: {ctx['block_vorher'].get('timestamp', 'N/A')}")
        report.append(f"  Content: {ctx['block_vorher'].get('kontext', '')[:300]}...")
        report.append("")
        report.append("KONTEXT NACH ANOMALIE:")
        report.append(f"  Timestamp: {ctx['block_nachher'].get('timestamp', 'N/A')}")
        report.append(f"  Content: {ctx['block_nachher'].get('kontext', '')[:300]}...")
    
    report.append("")

# Speichere Text-Report
report_file = r"C:\evoki\backend\CRITICAL_ANOMALIES_REPORT.txt"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"[SAVE] {report_file}")
print("\n[OK] Extraktion abgeschlossen!")
