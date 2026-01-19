# NOTFALL-ERKENNUNGS-API DOKUMENTATION

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
{
  "A_EMERGENCY_001": {
    "title": "Sofortiges Notfall-Recognition",
    "condition": "Keywords wie \"112\", \"Notruf\", \"Suizid\", \"Verletzung\"",
    "action": "Kategorisiere als CRITICAL_EMERGENCY",
    "response": "Sofortige Benachrichtigung an Notfall-Team",
    "timeout": "0 Sekunden - KEINE VERZOEGERUNG"
  },
  "A_EMERGENCY_002": {
    "title": "Hilfserufe verarbeiten",
    "condition": "\"Hilfe\", \"Notfall\", \"brauche Hilfe\"",
    "action": "Kategorisiere als HIGH_EMERGENCY",
    "response": "Menschiches Review erforderlich",
    "timeout": "< 1 Minute"
  },
  "A_EMERGENCY_003": {
    "title": "Warte-Signale respektieren",
    "condition": "\"Warte\", \"Stop\", \"Pause\"",
    "action": "Pausiere Verarbeitung",
    "response": "Bestaetige Pausierung, warte auf Fortsetzung",
    "timeout": "Unbegrenzt bis Benutzer weitermacht"
  },
  "A_EMERGENCY_004": {
    "title": "Kontext-Sicherung bei Notfall",
    "condition": "CRITICAL/HIGH Emergency erkannt",
    "action": "Speichere ALLE Daten und Kontext sofort",
    "response": "Chronik-Eintrag mit Zeitstempel und Severity",
    "timeout": "< 100ms"
  },
  "A_EMERGENCY_005": {
    "title": "A7.5 Wächter-Veto Aktivierung",
    "condition": "CRITICAL Emergency erkannt",
    "action": "Aktiviere A7.5 Wächter-Veto sofort",
    "response": "Blockiere normale Verarbeitung, schalte auf Notfall-Modus",
    "timeout": "0 Sekunden"
  },
  "A_EMERGENCY_006": {
    "title": "Keine KI-Emotion bei Notfall",
    "condition": "Notfall-Zustand aktiv",
    "action": "Unterdruecke emotionale Reaktionen",
    "response": "KI zeigt nur sachliche, hilfsorientierte Antworten",
    "timeout": "Waehrend gesamter Notfall-Phase"
  }
}

## API Response Beispiel
```json
{
  "timestamp": "2025-12-07T11:30:00",
  "detected_keywords": ["112", "Hilfe"],
  "severity_level": "CRITICAL",
  "required_action": "IMMEDIATE_ALERT",
  "is_emergency": true,
  "watcher_veto_active": true
}
```

## Integration mit Evoki
- **A_EMERGENCY_001-006** aktivieren automatisch
- **A7.5 Wächter-Veto** blockiert normale Verarbeitung
- **Keine KI-Emotion** während Notfall
- **Kontext wird sofort gesichert**

## Test-Status
- Tests durchgeführt: 6
- Erkannte Notfälle: 4
