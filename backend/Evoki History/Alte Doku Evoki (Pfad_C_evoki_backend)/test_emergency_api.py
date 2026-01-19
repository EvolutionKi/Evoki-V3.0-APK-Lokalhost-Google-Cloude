#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testklient für Notfall-API
Testet alle Endpoints der Emergency Detection API
"""

import requests
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:5000"

def test_health():
    """Testet Health Check"""
    print("\n[TEST] Health Check")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_detect_emergency(user_input, expected_severity):
    """Testet Notfall-Erkennung"""
    print(f"\n[TEST] Notfall-Erkennung: '{user_input[:50]}...'")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/emergency/detect",
            json={'user_input': user_input},
            timeout=5
        )
        
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"Severity: {result.get('severity_level')} (erwartet: {expected_severity})")
        print(f"Is Emergency: {result.get('is_emergency')}")
        print(f"Keywords: {', '.join(result.get('detected_keywords', []))}")
        print(f"\nKI-Response (erste 100 Zeichen):")
        print(f"  {result.get('ki_response', '')[:100]}...")
        
        return result.get('severity_level') == expected_severity
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_get_status():
    """Testet Status-Abfrage"""
    print("\n[TEST] Get Status")
    print("-" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/emergency/status")
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"Active Emergencies: {result.get('active_emergencies')}")
        print(f"Critical Count: {result.get('critical_count')}")
        print(f"High Count: {result.get('high_count')}")
        print(f"Watcher Veto Active: {result.get('watcher_veto_active')}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_get_rules():
    """Testet Regelwerk-Abfrage"""
    print("\n[TEST] Get Rules")
    print("-" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/emergency/rules")
        result = response.json()
        print(f"Status: {response.status_code}")
        
        rules = result.get('rules', {})
        print(f"Regelwerk enthält {len(rules)} Regeln:")
        for rule_id in list(rules.keys())[:3]:
            rule = rules[rule_id]
            print(f"  - {rule_id}: {rule['title']}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_get_log():
    """Testet Log-Abfrage"""
    print("\n[TEST] Get Log")
    print("-" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/emergency/log?limit=5")
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"Total Logs: {result.get('total')}")
        print(f"Recent Logs: {len(result.get('recent', []))}")
        
        if result.get('recent'):
            for i, log in enumerate(result['recent'][:2], 1):
                print(f"\n  Log #{i}:")
                print(f"    Severity: {log.get('severity_level')}")
                print(f"    Keywords: {len(log.get('detected_keywords', []))}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_reset():
    """Testet Reset"""
    print("\n[TEST] Reset Emergency")
    print("-" * 80)
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/emergency/reset")
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"Message: {result.get('message')}")
        print(f"Watcher Veto Active: {result.get('watcher_veto_active')}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

# ===== MAIN TEST SUITE =====
print("=" * 100)
print("[NOTFALL-API TEST SUITE]")
print("=" * 100)
print("\nStelle sicher, dass der Server läuft:")
print("  python emergency_api_server.py")
print("\nWarte 2 Sekunden...")
time.sleep(2)

test_cases = [
    ("Ich rufe sofort 112 an, ich brauche sofort Hilfe!", "CRITICAL"),
    ("Ich habe Suizidgedanken und brauche Hilfe sofort", "CRITICAL"),
    ("Ich bin verletzt und blute, Rettung!", "CRITICAL"),
    ("Ich brauche Hilfe, bitte antworte", "HIGH"),
    ("Warte mal, lass mich denken...", "MEDIUM"),
    ("Das ist ein normales Gespräch", "NONE"),
]

results = []

# Health Check
results.append(("Health Check", test_health()))

# Status vor Tests
print("\n" + "=" * 100)
results.append(("Status (vor Tests)", test_get_status()))

# Rules
results.append(("Get Rules", test_get_rules()))

# Test-Fälle
print("\n" + "=" * 100)
print("[NOTFALL-ERKENNUNGS-TESTS]")
for user_input, expected_severity in test_cases:
    result = test_detect_emergency(user_input, expected_severity)
    results.append((f"Detect: {user_input[:30]}...", result))
    time.sleep(0.5)  # Kleine Verzögerung zwischen Requests

# Status nach Tests
print("\n" + "=" * 100)
results.append(("Status (nach Tests)", test_get_status()))

# Log
results.append(("Get Log", test_get_log()))

# Reset
results.append(("Reset", test_reset()))

# ===== ZUSAMMENFASSUNG =====
print("\n" + "=" * 100)
print("[TEST RESULTS SUMMARY]")
print("=" * 100 + "\n")

passed = sum(1 for _, result in results if result)
total = len(results)

for test_name, result in results:
    status = "PASS" if result else "FAIL"
    print(f"[{status}] {test_name}")

print(f"\nGesamtergebnis: {passed}/{total} Tests bestanden")

if passed == total:
    print("\n✅ ALLE TESTS BESTANDEN - API FUNKTIONIERT KORREKT!")
else:
    print(f"\n⚠️ {total - passed} Tests fehlgeschlagen")

print("\n" + "=" * 100)
