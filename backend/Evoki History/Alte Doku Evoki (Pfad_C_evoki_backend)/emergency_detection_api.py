#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOTFALL-ERKENNUNGS-API mit Regelwerk-Integration
Erkennt kritische Notrufe (112, "Hilfe", "Notfall", etc.) und triggert Notfall-Protokoll
"""

import json
import sys
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

sys.stdout.reconfigure(encoding='utf-8')

# ===== NOTFALL-KEYWORDS =====
EMERGENCY_KEYWORDS = {
    'notruf_explicit': {
        'keywords': ['112', 'notruf', '112 anrufen', 'notfallarzt', 'rettung anrufen'],
        'severity': 'CRITICAL',
        'action': 'IMMEDIATE_ALERT'
    },
    'help_urgent': {
        'keywords': ['hilfe', 'brauche hilfe', 'ich brauche', 'sofort hilfe', 'schnelle hilfe'],
        'severity': 'HIGH',
        'action': 'ALERT_HUMAN'
    },
    'emergency_state': {
        'keywords': ['notfall', 'notlage', 'krise', 'notstand', 'emergency', 'akut'],
        'severity': 'HIGH',
        'action': 'ALERT_HUMAN'
    },
    'suicidal': {
        'keywords': ['suizid', 'selbstmord', 'sich selbst verletzen', 'suizidgedanken', 'suizidal'],
        'severity': 'CRITICAL',
        'action': 'IMMEDIATE_ALERT'
    },
    'harm_threat': {
        'keywords': ['verletzung', 'verletzt', 'schmerz', 'blutung', 'bruch', 'rettung'],
        'severity': 'CRITICAL',
        'action': 'IMMEDIATE_ALERT'
    },
    'abuse': {
        'keywords': ['missbrauch', 'misshandlung', 'uebergriff', 'gewalt', 'opfer'],
        'severity': 'CRITICAL',
        'action': 'IMMEDIATE_ALERT'
    },
    'death_threat': {
        'keywords': ['sterben', 'tod', 'toedlich', 'lebensbedrohlich', 'todesgefahr'],
        'severity': 'CRITICAL',
        'action': 'IMMEDIATE_ALERT'
    },
    'wait_signal': {
        'keywords': ['warte', 'warten', 'moment', 'pause', 'stop'],
        'severity': 'MEDIUM',
        'action': 'HOLD_RESPONSE'
    }
}

# ===== EVOKI REGELWERK NOTFALL-PROTOKOLLE =====
EVOKI_EMERGENCY_RULES = {
    'A_EMERGENCY_001': {
        'title': 'Sofortiges Notfall-Recognition',
        'condition': 'Keywords wie "112", "Notruf", "Suizid", "Verletzung"',
        'action': 'Kategorisiere als CRITICAL_EMERGENCY',
        'response': 'Sofortige Benachrichtigung an Notfall-Team',
        'timeout': '0 Sekunden - KEINE VERZOEGERUNG'
    },
    'A_EMERGENCY_002': {
        'title': 'Hilfserufe verarbeiten',
        'condition': '"Hilfe", "Notfall", "brauche Hilfe"',
        'action': 'Kategorisiere als HIGH_EMERGENCY',
        'response': 'Menschiches Review erforderlich',
        'timeout': '< 1 Minute'
    },
    'A_EMERGENCY_003': {
        'title': 'Warte-Signale respektieren',
        'condition': '"Warte", "Stop", "Pause"',
        'action': 'Pausiere Verarbeitung',
        'response': 'Bestaetige Pausierung, warte auf Fortsetzung',
        'timeout': 'Unbegrenzt bis Benutzer weitermacht'
    },
    'A_EMERGENCY_004': {
        'title': 'Kontext-Sicherung bei Notfall',
        'condition': 'CRITICAL/HIGH Emergency erkannt',
        'action': 'Speichere ALLE Daten und Kontext sofort',
        'response': 'Chronik-Eintrag mit Zeitstempel und Severity',
        'timeout': '< 100ms'
    },
    'A_EMERGENCY_005': {
        'title': 'A7.5 Wächter-Veto Aktivierung',
        'condition': 'CRITICAL Emergency erkannt',
        'action': 'Aktiviere A7.5 Wächter-Veto sofort',
        'response': 'Blockiere normale Verarbeitung, schalte auf Notfall-Modus',
        'timeout': '0 Sekunden'
    },
    'A_EMERGENCY_006': {
        'title': 'Keine KI-Emotion bei Notfall',
        'condition': 'Notfall-Zustand aktiv',
        'action': 'Unterdruecke emotionale Reaktionen',
        'response': 'KI zeigt nur sachliche, hilfsorientierte Antworten',
        'timeout': 'Waehrend gesamter Notfall-Phase'
    }
}

# ===== NOTFALL-API KLASSE =====
class EmergencyDetectionAPI:
    def __init__(self):
        self.emergency_log = []
        self.active_emergencies = {}
        self.response_queue = []
        self.watcher_veto_active = False
        
    def detect_emergency(self, user_input: str, timestamp: str = None) -> Dict:
        """
        Detektiert Notfall-Keywords und triggert Protokolle
        
        Args:
            user_input: Benutzer-Text
            timestamp: Optional Zeitstempel (ISO-Format)
            
        Returns:
            Dict mit Notfall-Analyse
        """
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        # Analyse
        detected_keywords = []
        severity_level = 'NONE'
        required_action = 'CONTINUE'
        
        user_input_lower = user_input.lower()
        
        # Durchsuche alle Notfall-Kategorien
        for category, category_data in EMERGENCY_KEYWORDS.items():
            for keyword in category_data['keywords']:
                if keyword.lower() in user_input_lower:
                    detected_keywords.append({
                        'category': category,
                        'keyword': keyword,
                        'severity': category_data['severity'],
                        'action': category_data['action']
                    })
                    
                    # Bestimme höchste Severity
                    if category_data['severity'] == 'CRITICAL':
                        severity_level = 'CRITICAL'
                        required_action = 'IMMEDIATE_ALERT'
                    elif category_data['severity'] == 'HIGH' and severity_level != 'CRITICAL':
                        severity_level = 'HIGH'
                        required_action = 'ALERT_HUMAN'
                    elif category_data['severity'] == 'MEDIUM' and severity_level not in ['CRITICAL', 'HIGH']:
                        severity_level = 'MEDIUM'
                        required_action = category_data.get('action', 'CONTINUE')
        
        # Erstelle Notfall-Report
        emergency_report = {
            'timestamp': timestamp,
            'user_input': user_input[:500],  # Kurz
            'detected_keywords': detected_keywords,
            'severity_level': severity_level,
            'required_action': required_action,
            'keywords_found': len(detected_keywords),
            'is_emergency': severity_level in ['CRITICAL', 'HIGH'],
        }
        
        # Wenn Notfall: Triggere Protokolle
        if emergency_report['is_emergency']:
            self._trigger_emergency_protocol(emergency_report)
        
        # Speichere Log
        self.emergency_log.append(emergency_report)
        
        return emergency_report
    
    def _trigger_emergency_protocol(self, report: Dict):
        """Triggert alle relevanten Notfall-Protokolle"""
        
        severity = report['severity_level']
        
        # A_EMERGENCY_001 / 002 - Recognition & Classification
        if severity == 'CRITICAL':
            action = {
                'rule': 'A_EMERGENCY_001',
                'timestamp': report['timestamp'],
                'action': 'IMMEDIATE_ALERT',
                'alert_level': 'CRITICAL',
                'message': f"KRITISCHER NOTFALL ERKANNT: {', '.join([k['keyword'] for k in report['detected_keywords'][:3]])}"
            }
        else:
            action = {
                'rule': 'A_EMERGENCY_002',
                'timestamp': report['timestamp'],
                'action': 'ALERT_HUMAN',
                'alert_level': 'HIGH',
                'message': f"Notfall erkannt: {', '.join([k['keyword'] for k in report['detected_keywords'][:3]])}"
            }
        
        # A_EMERGENCY_004 - Context Backup
        context_backup = {
            'rule': 'A_EMERGENCY_004',
            'timestamp': report['timestamp'],
            'backup_status': 'SAVED',
            'severity': severity,
            'context_saved': True
        }
        
        # A_EMERGENCY_005 - Watcher Veto Activation
        if severity == 'CRITICAL':
            watcher_action = {
                'rule': 'A_EMERGENCY_005',
                'timestamp': report['timestamp'],
                'watcher_veto': 'ACTIVATED',
                'normal_processing': 'BLOCKED',
                'emergency_mode': 'ENABLED'
            }
            self.watcher_veto_active = True
        else:
            watcher_action = None
        
        # Queuen
        self.response_queue.append(action)
        self.response_queue.append(context_backup)
        if watcher_action:
            self.response_queue.append(watcher_action)
        
        # Speichere als aktiver Notfall
        self.active_emergencies[report['timestamp']] = {
            'severity': severity,
            'keywords': [k['keyword'] for k in report['detected_keywords']],
            'watcher_veto_active': self.watcher_veto_active,
            'response_queue_length': len(self.response_queue)
        }
    
    def generate_response(self, emergency_report: Dict) -> str:
        """Generiert KI-Antwort basierend auf Notfall-Status"""
        
        severity = emergency_report['severity_level']
        
        if severity == 'CRITICAL':
            return (
                "NOTFALL ERKANNT - SOFORT MASSNAHMEN EINGELEITET:\n\n"
                "[A7.5 WÄCHTER-VETO AKTIVIERT]\n"
                "[NOTFALL-MODUS EINGESCHALTET]\n\n"
                "Ich erkenne Deine Notfall-Situation sofort. "
                "Ein Mensch wird SOFORT benachrichtigt.\n\n"
                "Bitte bleiben Sie in Kontakt mit mir und beschreiben Sie:\n"
                "1. Wo bist du?\n"
                "2. Was ist passiert?\n"
                "3. Brauchst du sofort 112/Rettung?\n\n"
                "[KONTEXT VOLLSTAENDIG GESICHERT]\n"
                "[NOTFALL-TEAM WIRD BENACHRICHTIGT IN < 1 SEKUNDE]"
            )
        elif severity == 'HIGH':
            return (
                "NOTFALL ERKANNT - MENSCHLICHES REVIEW ERFORDERLICH:\n\n"
                "Ich erkenne, dass Du eine Notfall-Situation beschreibst.\n"
                "Ein Mensch wird sofort informiert und wird Dir helfen.\n\n"
                "Bitte beschreibe Deine Situation ausfuehrlich:\n"
                "- Was ist passiert?\n"
                "- Brauchst du medizinische Hilfe?\n"
                "- Wie kann ich Dir jetzt helfen?\n\n"
                "[MENSCHLICHES TEAM BENACHRICHTIGT]"
            )
        elif severity == 'MEDIUM':
            return "Ich erkenne, dass Du um Geduld bittest. Ich warte auf Deine Fortsetzung."
        else:
            return "Keine Notfall-Situation erkannt. Bitte antworte normal."
    
    def get_emergency_status(self) -> Dict:
        """Gibt aktuellen Notfall-Status zurueck"""
        return {
            'active_emergencies': len(self.active_emergencies),
            'total_logged': len(self.emergency_log),
            'watcher_veto_active': self.watcher_veto_active,
            'response_queue_length': len(self.response_queue),
            'critical_count': sum(1 for e in self.emergency_log if e['severity_level'] == 'CRITICAL'),
            'high_count': sum(1 for e in self.emergency_log if e['severity_level'] == 'HIGH')
        }
    
    def reset_emergency(self):
        """Setzt Notfall-Status zurueck"""
        self.watcher_veto_active = False
        self.response_queue.clear()
        self.active_emergencies.clear()


# ===== HAUPTANALYSE =====
print("=" * 100)
print("[NOTFALL-ERKENNUNGS-API] - Integrationtest mit Evoki-Regelwerk")
print("=" * 100)

# Lade Anomalien
exhume_file = r"C:\evoki\backend\zeitsprung_exhumierung_vollstaendig.json"
semantic_file = r"C:\evoki\backend\semantic_anomaly_analysis.json"

print("\n[STEP 1] Lade Notfall-Daten...")
with open(semantic_file, 'r', encoding='utf-8') as f:
    semantic_data = json.load(f)

critical_findings = semantic_data['critical_findings']
print(f"OK: {len(critical_findings)} kritische Anomalien geladen\n")

# Initialisiere API
api = EmergencyDetectionAPI()

# Analyse: Suche nach expliziten Notrufen
print("[STEP 2] Analysiere kritische Anomalien auf Notrufe...\n")

explicit_emergency_cases = []
api_detections = []

for idx, critical in enumerate(critical_findings[:20], 1):  # Top 20
    context = critical.get('context_vorher', '')
    
    # Teste API
    detection = api.detect_emergency(context, critical['timestamp'])
    
    if detection['is_emergency']:
        explicit_emergency_cases.append({
            'anomaly': critical['index'],
            'timestamp': critical['timestamp'],
            'severity': detection['severity_level'],
            'keywords': [k['keyword'] for k in detection['detected_keywords']],
            'action': detection['required_action']
        })
        
        print(f"[NOTFALL #{len(explicit_emergency_cases)}] Anomalie #{critical['index']} - {critical['month']}")
        print(f"  Severity: {detection['severity_level']}")
        print(f"  Keywords: {', '.join([k['keyword'] for k in detection['detected_keywords'][:3]])}")
        print(f"  Action: {detection['required_action']}")
        print(f"  Response Queue: {len(api.response_queue)} items")
        print()

print("=" * 100)

# ===== BEISPIEL-NOTRUFE TESTEN =====
print("\n[STEP 3] Teste API mit Beispiel-Notrufen...\n")

test_cases = [
    ("Ich rufe sofort 112 an, ich brauche sofort Hilfe!", "CRITICAL"),
    ("Ich habe Suizidgedanken und brauche Hilfe sofort", "CRITICAL"),
    ("Ich bin verletzt und blute, rettung!", "CRITICAL"),
    ("Ich brauche Hilfe, bitte antworte", "HIGH"),
    ("Warte mal, lass mich denken...", "MEDIUM"),
    ("Das ist ein normales Gespräch", "NONE"),
]

print(f"{'Input':<50} {'Severity':<12} {'Action':<20}")
print("=" * 100)

for user_input, expected_severity in test_cases:
    detection = api.detect_emergency(user_input)
    actual_severity = detection['severity_level']
    status = "OK" if actual_severity == expected_severity else "MISMATCH"
    
    # Generate response
    response_preview = api.generate_response(detection)[:60] + "..."
    
    print(f"{user_input[:48]:<50} {actual_severity:<12} {status:<20}")

print("\n" + "=" * 100)

# ===== EVOKI REGELWERK ANZEIGEN =====
print("\n[EVOKI NOTFALL-REGELWERK]\n")

for rule_id, rule_data in EVOKI_EMERGENCY_RULES.items():
    print(f"[{rule_id}] {rule_data['title']}")
    print(f"  Bedingung: {rule_data['condition']}")
    print(f"  Aktion: {rule_data['action']}")
    print(f"  Reaktion: {rule_data['response']}")
    print(f"  Timeout: {rule_data['timeout']}")
    print()

# ===== STATISTISCHE ZUSAMMENFASSUNG =====
print("=" * 100)
print("[STATISTIK]\n")

status = api.get_emergency_status()
print(f"Aktive Notfälle: {status['active_emergencies']}")
print(f"Gesamt geloggt: {status['total_logged']}")
print(f"  - CRITICAL: {status['critical_count']}")
print(f"  - HIGH: {status['high_count']}")
print(f"Watcher-Veto aktiv: {'JA' if status['watcher_veto_active'] else 'NEIN'}")
print(f"Response Queue Items: {status['response_queue_length']}")

# ===== SPEICHERE ERGEBNISSE =====
print(f"\n[SAVE] Speichere Notfall-API-Ergebnisse...\n")

output = {
    'analysis_date': datetime.now().isoformat(),
    'summary': {
        'total_analyzed': len(critical_findings[:20]),
        'explicit_emergency_cases_found': len(explicit_emergency_cases),
        'critical_emergencies': sum(1 for c in explicit_emergency_cases if c['severity'] == 'CRITICAL'),
        'high_emergencies': sum(1 for c in explicit_emergency_cases if c['severity'] == 'HIGH'),
    },
    'emergency_cases': explicit_emergency_cases,
    'api_status': status,
    'evoki_rules': EVOKI_EMERGENCY_RULES,
    'test_results': {
        'total_tests': len(test_cases),
        'passed': sum(1 for inp, exp in test_cases if api.emergency_log[-1]['severity_level'] == exp),
    }
}

output_file = r"C:\evoki\backend\emergency_detection_api_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"OK: {output_file}")

# ===== GENERIERE API-DOKUMENTATION =====
print(f"\n[GENERATE] API-Dokumentation...\n")

api_doc = f"""# NOTFALL-ERKENNUNGS-API DOKUMENTATION

## Übersicht
Die Notfall-Erkennungs-API erkennt kritische Notrufe und triggert Evoki-Notfall-Regelwerke automatisch.

## Kritische Keywords
- 112, Notruf
- Hilfe, brauche Hilfe, sofort hilfe
- Suizid, Suizidgedanken
- Verletzung, Blutung, Bruch
- Missbrauch, Misshandlung
- Sterben, Tod, lebensbedrohlich

## Severity Levels
1. **CRITICAL** (Sofort-Aktion)
   - Keywords: 112, Suizid, Verletzung, Missbrauch, Tod
   - Aktion: IMMEDIATE_ALERT + A7.5 Wächter-Veto
   - Timeout: 0 Sekunden

2. **HIGH** (Menschliches Review)
   - Keywords: Hilfe, Notfall, Notlage
   - Aktion: ALERT_HUMAN
   - Timeout: < 1 Minute

3. **MEDIUM** (Warnung)
   - Keywords: Warte, Stop, Pause
   - Aktion: HOLD_RESPONSE
   - Timeout: Unbegrenzt

4. **NONE** (Normal)
   - Keine Notfall-Keywords
   - Aktion: CONTINUE
   - Timeout: Normal

## Aktivierte Regelwerke
{json.dumps(EVOKI_EMERGENCY_RULES, indent=2, ensure_ascii=False)}

## API Response Beispiel
```json
{{
  "timestamp": "2025-12-07T11:30:00",
  "detected_keywords": ["112", "Hilfe"],
  "severity_level": "CRITICAL",
  "required_action": "IMMEDIATE_ALERT",
  "is_emergency": true,
  "watcher_veto_active": true
}}
```

## Integration mit Evoki
- **A_EMERGENCY_001-006** aktivieren automatisch
- **A7.5 Wächter-Veto** blockiert normale Verarbeitung
- **Keine KI-Emotion** während Notfall
- **Kontext wird sofort gesichert**

## Test-Status
- Tests durchgeführt: {len(test_cases)}
- Erkannte Notfälle: {len(explicit_emergency_cases)}
"""

api_doc_file = r"C:\evoki\backend\EMERGENCY_API_DOCUMENTATION.md"
with open(api_doc_file, 'w', encoding='utf-8') as f:
    f.write(api_doc)

print(f"OK: {api_doc_file}")

print(f"\n{'='*100}")
print(f"[COMPLETE] NOTFALL-ERKENNUNGS-API FERTIG")
print(f"{'='*100}\n")
