#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compliance Watcher - Prüft ob der Agent für jeden Prompt ein Status Window erstellt hat.
V1.0

Verwendung:
    python compliance_watcher.py check           # Prüft aktuelle Session
    python compliance_watcher.py stats           # Zeigt Statistiken
    python compliance_watcher.py gaps            # Zeigt Lücken in der History

Logik:
- Liest status_window_history.json
- Zählt eindeutige raw_user_requests
- Warnt wenn Zeitlücken > 10 Minuten ohne Status Window
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# Pfade
# Dynamic Root
V3_ROOT = Path(os.getenv("EVOKI_PROJECT_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))).resolve()
if not (V3_ROOT / "tooling").exists():
    V3_ROOT = Path(os.path.abspath(".")).resolve()
HISTORY_FILE = V3_ROOT / "tooling" / "data" / "synapse" / "status" / "status_window_history.json"


def load_history() -> Dict:
    """Lädt die History-Datei."""
    if not HISTORY_FILE.exists():
        print(f"❌ History-Datei nicht gefunden: {HISTORY_FILE}")
        sys.exit(1)
    
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_timestamp(ts: str) -> datetime:
    """Parst ISO Timestamp."""
    # Entferne +00:00 für einfacheres Parsing
    if '+' in ts:
        ts = ts.split('+')[0]
    return datetime.fromisoformat(ts)


def check_gaps(max_gap_minutes: int = 10) -> List[Dict]:
    """
    Prüft auf Zeitlücken zwischen Status Windows.
    
    Eine Lücke > max_gap_minutes könnte bedeuten:
    - Agent hat nicht geschrieben
    - Session-Wechsel (normal)
    - Watcher war offline
    """
    history = load_history()
    entries = history.get('entries', [])
    
    if len(entries) < 2:
        print("Zu wenige Einträge für Gap-Analyse")
        return []
    
    gaps = []
    
    for i in range(1, len(entries)):
        prev_ts = parse_timestamp(entries[i-1]['timestamp'])
        curr_ts = parse_timestamp(entries[i]['timestamp'])
        
        gap = curr_ts - prev_ts
        gap_minutes = gap.total_seconds() / 60
        
        if gap_minutes > max_gap_minutes:
            gaps.append({
                'index': i,
                'prev_entry': i,
                'curr_entry': i + 1,
                'prev_ts': entries[i-1]['timestamp'],
                'curr_ts': entries[i]['timestamp'],
                'gap_minutes': round(gap_minutes, 1),
                'prev_goal': entries[i-1]['status_window'].get('goal', 'N/A'),
                'curr_goal': entries[i]['status_window'].get('goal', 'N/A')
            })
    
    return gaps


def stats() -> Dict:
    """Zeigt Statistiken über die History."""
    history = load_history()
    entries = history.get('entries', [])
    
    total = len(entries)
    
    # Zähle eindeutige step_ids
    step_ids = set()
    goals = []
    requests = []
    
    for e in entries:
        sw = e.get('status_window', {})
        if sw.get('step_id'):
            step_ids.add(sw['step_id'])
        if sw.get('goal'):
            goals.append(sw['goal'])
        if sw.get('inputs', {}).get('raw_user_request'):
            requests.append(sw['inputs']['raw_user_request'])
    
    return {
        'total_entries': total,
        'unique_step_ids': len(step_ids),
        'entries_with_goal': len(goals),
        'entries_with_user_request': len(requests),
        'unique_user_requests': len(set(requests))
    }


def check_compliance() -> Dict:
    """
    Prüft Compliance: Hat der Agent konsistent Status Windows geschrieben?
    
    Metriken:
    - Gap-Count: Anzahl Zeitlücken > 10 Min
    - Request-Coverage: % der Einträge mit raw_user_request
    - Goal-Coverage: % der Einträge mit goal
    """
    history = load_history()
    entries = history.get('entries', [])
    
    total = len(entries)
    
    with_request = sum(1 for e in entries 
                       if e.get('status_window', {}).get('inputs', {}).get('raw_user_request'))
    with_goal = sum(1 for e in entries 
                    if e.get('status_window', {}).get('goal'))
    with_reflection = sum(1 for e in entries 
                          if e.get('status_window', {}).get('reflection_curve', {}).get('delta'))
    
    gaps = check_gaps()
    
    request_pct = (with_request / total * 100) if total > 0 else 0
    goal_pct = (with_goal / total * 100) if total > 0 else 0
    reflection_pct = (with_reflection / total * 100) if total > 0 else 0
    
    # Compliance Score (0-100)
    # Gewichtung: goal=30%, request=30%, reflection=30%, gaps=10%
    gap_penalty = min(len(gaps) * 2, 10)  # Max 10 Punkte Abzug
    score = (goal_pct * 0.3) + (request_pct * 0.3) + (reflection_pct * 0.3) + (10 - gap_penalty)
    
    return {
        'total_entries': total,
        'with_goal': with_goal,
        'with_request': with_request,
        'with_reflection': with_reflection,
        'goal_pct': round(goal_pct, 1),
        'request_pct': round(request_pct, 1),
        'reflection_pct': round(reflection_pct, 1),
        'gaps_count': len(gaps),
        'compliance_score': round(score, 1),
        'status': 'GREEN' if score >= 80 else 'YELLOW' if score >= 60 else 'RED'
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'check':
        result = check_compliance()
        print(f"\n📊 COMPLIANCE CHECK")
        print(f"{'='*40}")
        print(f"Total Einträge:     {result['total_entries']}")
        print(f"Mit Goal:           {result['with_goal']} ({result['goal_pct']}%)")
        print(f"Mit User-Request:   {result['with_request']} ({result['request_pct']}%)")
        print(f"Mit Reflection:     {result['with_reflection']} ({result['reflection_pct']}%)")
        print(f"Zeitlücken (>10m):  {result['gaps_count']}")
        print(f"{'='*40}")
        print(f"COMPLIANCE SCORE:   {result['compliance_score']}/100")
        print(f"STATUS:             {result['status']}")
        
        if result['status'] != 'GREEN':
            sys.exit(1)
    
    elif command == 'stats':
        result = stats()
        print(json.dumps(result, indent=2))
    
    elif command == 'gaps':
        gaps = check_gaps()
        if not gaps:
            print("✅ Keine signifikanten Zeitlücken gefunden")
        else:
            print(f"\n⚠️  {len(gaps)} Zeitlücken > 10 Minuten gefunden:\n")
            for g in gaps[-10:]:  # Letzte 10
                print(f"  #{g['prev_entry']} → #{g['curr_entry']}: {g['gap_minutes']} Min")
                print(f"    Von: {g['prev_goal'][:50]}...")
                print(f"    Nach: {g['curr_goal'][:50]}...")
                print()
    
    else:
        print(f"❌ Unbekannter Befehl: {command}")
        print("Verwendung: check | stats | gaps")
        sys.exit(1)


if __name__ == "__main__":
    main()
