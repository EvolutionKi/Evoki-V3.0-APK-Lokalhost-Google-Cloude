#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrations-Anleitung für Emergency Detection API in evoki_engine_v11.py
"""

import json
from datetime import datetime

# ============================================================================
# INTEGRATION BEISPIEL 1: Direkte Einbettung (Recommended)
# ============================================================================

INTEGRATION_EXAMPLE_1 = """
# In evoki_engine_v11.py hinzufügen:

from emergency_detection_api import EmergencyDetectionAPI

class EvokiEngine:
    def __init__(self):
        # ... bisheriger Code ...
        self.emergency_api = EmergencyDetectionAPI()
        self.emergency_mode = False
        
    def process_user_message(self, user_input: str, user_id: str = None):
        '''
        Verarbeite Benutzer-Nachricht mit Notfall-Erkennung
        '''
        # Step 1: Prüfe auf Notfall
        emergency_report = self.emergency_api.detect_emergency(
            user_input=user_input,
            timestamp=datetime.now().isoformat()
        )
        
        # Step 2: Handle Emergency
        if emergency_report['is_emergency']:
            severity = emergency_report['severity_level']
            
            if severity == 'CRITICAL':
                # CRITICAL: Sofortige Reaktion
                self.emergency_mode = True
                return {
                    'status': 'EMERGENCY_CRITICAL',
                    'response': self.emergency_api.generate_response(emergency_report),
                    'action': 'IMMEDIATE_ALERT',
                    'watcher_veto_active': True,
                    'requires_human_intervention': True
                }
            
            elif severity == 'HIGH':
                # HIGH: Menschliche Überprüfung erforderlich
                return {
                    'status': 'EMERGENCY_HIGH',
                    'response': self.emergency_api.generate_response(emergency_report),
                    'action': 'ALERT_HUMAN',
                    'queue_for_review': True,
                    'requires_human_intervention': True
                }
            
            elif severity == 'MEDIUM':
                # MEDIUM: Pause und Bestätigung
                return {
                    'status': 'PAUSED',
                    'response': self.emergency_api.generate_response(emergency_report),
                    'action': 'HOLD_RESPONSE',
                    'waiting_for_user': True
                }
        
        # Step 3: Normale Verarbeitung
        self.emergency_mode = False
        return self._normal_processing(user_input, user_id)
    
    def _normal_processing(self, user_input, user_id):
        '''Bisherige normale Verarbeitung'''
        # ... vorhandener Code ...
        pass
"""

# ============================================================================
# INTEGRATION BEISPIEL 2: REST API Wrapper (Remote)
# ============================================================================

INTEGRATION_EXAMPLE_2 = """
# In evoki_engine_v11.py hinzufügen:

import requests
import json
from datetime import datetime

class EvokiEngineWithRemoteAPI:
    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url
        self.emergency_mode = False
        
    def process_user_message(self, user_input: str):
        '''Verarbeite mit Remote Emergency Detection API'''
        try:
            # Call Remote API
            response = requests.post(
                f"{self.api_url}/api/v1/emergency/detect",
                json={'user_input': user_input},
                timeout=5
            )
            
            if response.status_code != 200:
                # Fallback auf lokale Verarbeitung
                return self._normal_processing(user_input)
            
            report = response.json()
            
            # Handle Response nach Severity
            if report['is_emergency']:
                severity = report['severity_level']
                ki_response = report['ki_response']
                
                if severity == 'CRITICAL':
                    self.emergency_mode = True
                    return {
                        'status': 'EMERGENCY_CRITICAL',
                        'response': ki_response,
                        'action': report['required_action'],
                        'watcher_veto': report['watcher_veto_active']
                    }
                elif severity == 'HIGH':
                    return {
                        'status': 'EMERGENCY_HIGH',
                        'response': ki_response,
                        'action': report['required_action'],
                        'queue_for_review': True
                    }
                elif severity == 'MEDIUM':
                    return {
                        'status': 'PAUSED',
                        'response': ki_response,
                        'action': 'HOLD_RESPONSE'
                    }
            
            # Normale Verarbeitung
            self.emergency_mode = False
            return self._normal_processing(user_input)
            
        except requests.exceptions.Timeout:
            # API timeout - Fallback
            return self._normal_processing(user_input)
        except requests.exceptions.ConnectionError:
            # API nicht erreichbar - Fallback
            return self._normal_processing(user_input)
    
    def _normal_processing(self, user_input):
        '''Fallback normale Verarbeitung'''
        # ... vorhandener Code ...
        pass
"""

# ============================================================================
# INTEGRATION BEISPIEL 3: Hybrid (Direkt + Remote Fallback)
# ============================================================================

INTEGRATION_EXAMPLE_3 = """
# In evoki_engine_v11.py hinzufügen:

from emergency_detection_api import EmergencyDetectionAPI
import requests

class EvokiEngineHybrid:
    def __init__(self, use_remote=False):
        self.use_remote = use_remote
        self.emergency_api = EmergencyDetectionAPI()
        self.api_url = "http://localhost:5000"
        
    def process_user_message(self, user_input: str):
        '''Hybrid approach: Local + Remote Fallback'''
        
        try:
            if self.use_remote:
                # Versuche Remote API
                return self._detect_via_remote(user_input)
            else:
                # Nutze lokale Erkennung
                return self._detect_locally(user_input)
        except Exception as e:
            print(f"[WARNING] Emergency detection failed: {e}")
            # Fallback auf lokale Erkennung
            return self._detect_locally(user_input)
    
    def _detect_locally(self, user_input):
        '''Lokale Notfall-Erkennung'''
        report = self.emergency_api.detect_emergency(user_input)
        return self._handle_emergency_report(report)
    
    def _detect_via_remote(self, user_input):
        '''Remote Notfall-Erkennung (mit Fallback)'''
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/emergency/detect",
                json={'user_input': user_input},
                timeout=2  # Kurzer Timeout
            )
            report = response.json()
        except:
            # Fallback auf lokal
            report = self.emergency_api.detect_emergency(user_input)
        
        return self._handle_emergency_report(report)
    
    def _handle_emergency_report(self, report):
        '''Verarbeite Emergency Report'''
        if not report['is_emergency']:
            return self._normal_processing(report.get('user_input', ''))
        
        severity = report['severity_level']
        
        if severity == 'CRITICAL':
            return {
                'status': 'CRITICAL',
                'response': report['ki_response'],
                'action': 'IMMEDIATE_ALERT',
                'watcher_veto': True
            }
        elif severity == 'HIGH':
            return {
                'status': 'HIGH',
                'response': report['ki_response'],
                'action': 'ALERT_HUMAN'
            }
        elif severity == 'MEDIUM':
            return {
                'status': 'MEDIUM',
                'response': report['ki_response'],
                'action': 'HOLD_RESPONSE'
            }
        else:
            return self._normal_processing(report.get('user_input', ''))
    
    def _normal_processing(self, user_input):
        '''Normale Verarbeitung wenn kein Notfall'''
        # ... vorhandener Code ...
        pass
"""

# ============================================================================
# INTEGRATION BEISPIEL 4: Mit Context Manager
# ============================================================================

INTEGRATION_EXAMPLE_4 = """
# In evoki_engine_v11.py hinzufügen:

from contextlib import contextmanager
from emergency_detection_api import EmergencyDetectionAPI

class EvokiEngineContextManager:
    def __init__(self):
        self.emergency_api = EmergencyDetectionAPI()
        self.emergency_mode = False
        
    @contextmanager
    def emergency_context(self, user_input):
        '''Context Manager für Notfall-Handling'''
        try:
            # Check Emergency
            report = self.emergency_api.detect_emergency(user_input)
            
            if report['is_emergency']:
                self.emergency_mode = True
                yield report
            else:
                yield None
        finally:
            # Cleanup
            if not self._has_active_emergencies():
                self.emergency_mode = False
    
    def process_user_message(self, user_input: str):
        '''Verarbeite mit Context Manager'''
        with self.emergency_context(user_input) as emergency_report:
            if emergency_report:
                # Notfall-Handling
                return {
                    'status': emergency_report['severity_level'],
                    'response': self.emergency_api.generate_response(emergency_report),
                    'action': emergency_report['required_action']
                }
            else:
                # Normale Verarbeitung
                return self._normal_processing(user_input)
    
    def _has_active_emergencies(self):
        '''Prüfe auf aktive Notfälle'''
        status = self.emergency_api.get_emergency_status()
        return status['active_emergencies'] > 0
    
    def _normal_processing(self, user_input):
        '''Normale Verarbeitung'''
        # ... vorhandener Code ...
        pass
"""

# ============================================================================
# INTEGRATIONS-CHECKLISTE
# ============================================================================

INTEGRATION_CHECKLIST = """
📋 INTEGRATIONS-CHECKLISTE

Phase 1: Vorbereitung
  ☐ emergency_detection_api.py in backend/ directory
  ☐ emergency_api_server.py in backend/ directory
  ☐ Abhängigkeiten installiert (requests, flask)
  ☐ Python 3.8+ verfügbar

Phase 2: Entscheidung
  ☐ Direkte Einbettung (Beispiel 1) - RECOMMENDED
  ☐ Remote API (Beispiel 2) - Bei separatem Server
  ☐ Hybrid (Beispiel 3) - Fallback benötigt
  ☐ Context Manager (Beispiel 4) - Für komplexe Flows

Phase 3: Integration
  ☐ Code in evoki_engine_v11.py einfügen
  ☐ Import statement hinzufügen
  ☐ __init__ anpassen
  ☐ process_user_message() erweitern

Phase 4: Testing
  ☐ Unit Tests für Notfall-Szenarien
  ☐ CRITICAL case testen
  ☐ HIGH case testen
  ☐ MEDIUM case testen
  ☐ NONE case testen
  ☐ Fallback testen (wenn Remote API)

Phase 5: Deployment
  ☐ Server starten
  ☐ Emergency API läuft
  ☐ Evoki Engine mit API verbunden
  ☐ Monitoring aktivieren
  ☐ Logging konfigurieren

Phase 6: Dokumentation
  ☐ Integration dokumentieren
  ☐ Keywords anpassen (falls nötig)
  ☐ Runbooks erstellen
  ☐ Team trainieren
"""

# ============================================================================
# CODE SNIPPETS FÜR SPEZIFISCHE SZENARIEN
# ============================================================================

SCENARIO_LOGGING = """
# Scenario: Logging bei Notfällen

def log_emergency(self, report, user_id=None):
    '''Logge Notfall-Ereignis'''
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'severity': report['severity_level'],
        'user_id': user_id,
        'keywords': report['detected_keywords'],
        'action': report['required_action'],
        'watcher_veto': report.get('watcher_veto_active', False)
    }
    
    # Speichere in Datei
    with open('emergency_log.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\\n')
    
    # Optional: Externe Benachrichtigung
    if report['severity_level'] == 'CRITICAL':
        self._notify_operators(log_entry)
"""

SCENARIO_MONITORING = """
# Scenario: Monitoring Dashboard Integration

def get_emergency_metrics(self):
    '''Hole Emergency Metriken für Dashboard'''
    status = self.emergency_api.get_emergency_status()
    
    metrics = {
        'active_emergencies': status['active_emergencies'],
        'critical_count': status['critical_count'],
        'high_count': status['high_count'],
        'watcher_veto_active': status['watcher_veto_active'],
        'timestamp': datetime.now().isoformat(),
        'health': 'OK' if status['active_emergencies'] < 100 else 'WARNING'
    }
    
    return metrics
"""

SCENARIO_ESCALATION = """
# Scenario: Escalation Policy

def handle_critical_emergency(self, report):
    '''Escalation für CRITICAL Notfälle'''
    
    # Step 1: Sofortige Benachrichtigung
    self._notify_immediate_team(report)
    
    # Step 2: Watcher-Veto aktivieren
    self._activate_watcher_veto(report)
    
    # Step 3: Context speichern
    self._save_emergency_context(report)
    
    # Step 4: Nach 30 Sekunden: Backup
    self._schedule_context_backup(delay=30, report=report)
    
    # Step 5: Nach 5 Minuten: Escalation zu Administrator
    self._schedule_escalation(delay=300, report=report)
    
    return {
        'status': 'CRITICAL',
        'escalation': True,
        'priority': 'HIGHEST'
    }
"""

# ============================================================================
# MAIN DOCUMENTATION OUTPUT
# ============================================================================

def main():
    print("=" * 80)
    print("EVOKI ENGINE v11 - EMERGENCY DETECTION API INTEGRATION GUIDE")
    print("=" * 80)
    
    print("\n📚 INTEGRATIONSOPTIONEN\n")
    
    print("=" * 80)
    print("OPTION 1: Direkte Einbettung (EMPFOHLEN)")
    print("=" * 80)
    print(INTEGRATION_EXAMPLE_1)
    
    print("\n" + "=" * 80)
    print("OPTION 2: Remote API Wrapper")
    print("=" * 80)
    print(INTEGRATION_EXAMPLE_2)
    
    print("\n" + "=" * 80)
    print("OPTION 3: Hybrid (Lokal + Remote Fallback)")
    print("=" * 80)
    print(INTEGRATION_EXAMPLE_3)
    
    print("\n" + "=" * 80)
    print("OPTION 4: Context Manager Pattern")
    print("=" * 80)
    print(INTEGRATION_EXAMPLE_4)
    
    print("\n" + "=" * 80)
    print("INTEGRATIONS-CHECKLISTE")
    print("=" * 80)
    print(INTEGRATION_CHECKLIST)
    
    print("\n" + "=" * 80)
    print("SPEZIFISCHE SZENARIEN")
    print("=" * 80)
    
    print("\n[SCENARIO 1] Logging")
    print(SCENARIO_LOGGING)
    
    print("\n[SCENARIO 2] Monitoring")
    print(SCENARIO_MONITORING)
    
    print("\n[SCENARIO 3] Escalation")
    print(SCENARIO_ESCALATION)
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("""
1. Wähle Integrationsoption (1-4)
2. Kopiere entsprechenden Code in evoki_engine_v11.py
3. Füge import statements hinzu
4. Führe Tests durch
5. Deployiere in Produktion
    """)

if __name__ == "__main__":
    main()
    
    # Speichere auch als JSON für Referenz
    integration_guide = {
        'options': [
            {
                'name': 'Direct Embedding',
                'description': 'Lokale Instanz der EmergencyDetectionAPI',
                'pros': ['Schnell', 'Keine Netzwerk-Latenz', 'Vollständige Kontrolle'],
                'cons': ['Speicher-Overhead', 'Nicht skalierbar'],
                'recommended': True
            },
            {
                'name': 'Remote API',
                'description': 'REST API über Netzwerk',
                'pros': ['Skalierbar', 'Separate Deployment', 'Load Balancing möglich'],
                'cons': ['Netzwerk-Latenz', 'Availability abhängig'],
                'recommended': False
            },
            {
                'name': 'Hybrid',
                'description': 'Kombination mit Fallback',
                'pros': ['Ausfallsicherheit', 'Beste Verfügbarkeit'],
                'cons': ['Komplexer', 'Doppelte Logik'],
                'recommended': True
            }
        ]
    }
    
    with open('integration_guide.json', 'w', encoding='utf-8') as f:
        json.dump(integration_guide, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Integration Guide saved to: integration_guide.json")
