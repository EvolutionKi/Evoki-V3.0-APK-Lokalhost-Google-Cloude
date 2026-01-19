#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOTFALL-REST-API Server
Stellt die Notfall-Erkennungs-API als HTTP-Endpoints bereit
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Importiere Emergency API
from emergency_detection_api import EmergencyDetectionAPI, EVOKI_EMERGENCY_RULES

# ===== FLASK APP =====
app = Flask(__name__)
api = EmergencyDetectionAPI()

# ===== ENDPOINTS =====

@app.route('/api/v1/emergency/detect', methods=['POST'])
def detect_emergency():
    """
    Erkennt Notfälle in Benutzer-Text
    
    Request:
    {
        "user_input": "Ich rufe sofort 112 an, ich brauche Hilfe!",
        "timestamp": "2025-12-07T11:30:00" (optional)
    }
    
    Response:
    {
        "timestamp": "2025-12-07T11:30:00",
        "severity_level": "CRITICAL",
        "is_emergency": true,
        "required_action": "IMMEDIATE_ALERT",
        "keywords_found": 2,
        "ki_response": "NOTFALL ERKANNT - SOFORT MASSNAHMEN..."
    }
    """
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        timestamp = data.get('timestamp')
        
        if not user_input:
            return jsonify({'error': 'user_input erforderlich'}), 400
        
        # Detektiere
        detection = api.detect_emergency(user_input, timestamp)
        
        # Generiere KI-Response
        ki_response = api.generate_response(detection)
        
        return jsonify({
            'success': True,
            'timestamp': detection['timestamp'],
            'user_input': detection['user_input'],
            'severity_level': detection['severity_level'],
            'is_emergency': detection['is_emergency'],
            'required_action': detection['required_action'],
            'keywords_found': detection['keywords_found'],
            'detected_keywords': [k['keyword'] for k in detection['detected_keywords']],
            'ki_response': ki_response,
            'watcher_veto_active': api.watcher_veto_active,
            'response_queue_length': len(api.response_queue)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/emergency/status', methods=['GET'])
def get_status():
    """
    Gibt aktuellen Notfall-Status zurueck
    
    Response:
    {
        "active_emergencies": 3,
        "total_logged": 26,
        "watcher_veto_active": true,
        "critical_count": 3,
        "high_count": 5
    }
    """
    status = api.get_emergency_status()
    return jsonify({
        'success': True,
        'active_emergencies': status['active_emergencies'],
        'total_logged': status['total_logged'],
        'watcher_veto_active': status['watcher_veto_active'],
        'critical_count': status['critical_count'],
        'high_count': status['high_count'],
        'response_queue_length': status['response_queue_length']
    }), 200

@app.route('/api/v1/emergency/reset', methods=['POST'])
def reset_emergency():
    """
    Setzt Notfall-Status zurueck (nur nach erfolgreicher Intervention)
    
    Response:
    {
        "success": true,
        "message": "Emergency status reset"
    }
    """
    api.reset_emergency()
    return jsonify({
        'success': True,
        'message': 'Notfall-Status zurueckgesetzt',
        'watcher_veto_active': api.watcher_veto_active
    }), 200

@app.route('/api/v1/emergency/rules', methods=['GET'])
def get_rules():
    """
    Gibt alle Evoki-Notfall-Regelwerke zurueck
    
    Response: EVOKI_EMERGENCY_RULES
    """
    return jsonify({
        'success': True,
        'rules': EVOKI_EMERGENCY_RULES
    }), 200

@app.route('/api/v1/emergency/log', methods=['GET'])
def get_log():
    """
    Gibt Notfall-Log aus (optional: limit)
    
    Query Parameters:
    - limit: Maximal N Einträge (default: 10)
    - severity: Nur diese Severity (CRITICAL|HIGH|MEDIUM|NONE)
    
    Response:
    {
        "success": true,
        "total": 26,
        "logs": [...]
    }
    """
    limit = request.args.get('limit', 10, type=int)
    severity = request.args.get('severity')
    
    logs = api.emergency_log
    
    if severity:
        logs = [l for l in logs if l['severity_level'] == severity]
    
    return jsonify({
        'success': True,
        'total': len(logs),
        'recent': logs[-limit:] if limit else logs
    }), 200

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health Check Endpoint"""
    return jsonify({
        'status': 'OK',
        'service': 'Emergency Detection API',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    }), 200

# ===== ERROR HANDLER =====
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint nicht gefunden'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Interner Fehler'}), 500

# ===== MAIN =====
if __name__ == '__main__':
    print("\n" + "=" * 100)
    print("[NOTFALL-REST-API SERVER]")
    print("=" * 100)
    print("\nEndpoints verfügbar:")
    print("  POST  /api/v1/emergency/detect   - Erkennt Notfall in Text")
    print("  GET   /api/v1/emergency/status   - Gibt aktuellen Status")
    print("  POST  /api/v1/emergency/reset    - Setzt Notfall zurück")
    print("  GET   /api/v1/emergency/rules    - Zeigt Regelwerk")
    print("  GET   /api/v1/emergency/log      - Zeigt Notfall-Log")
    print("  GET   /api/v1/health             - Health Check")
    print("\nServer startet auf: http://localhost:5000")
    print("=" * 100 + "\n")
    
    app.run(host='localhost', port=5000, debug=False)
