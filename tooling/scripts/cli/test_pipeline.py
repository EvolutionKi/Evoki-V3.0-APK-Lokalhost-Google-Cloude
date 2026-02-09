#!/usr/bin/env python3
"""
Stand 0 Pipeline Test - Testet die komplette Status Window Pipeline

1. Schreibt ein Test-Status-Window in pending_status.json
2. Führt status_history_manager.py add aus
3. Verifiziert die Chain-Integrität
4. Zeigt den letzten History-Eintrag

Nutzung:
    python tooling/scripts/cli/test_pipeline.py
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Dynamic Root Resolution
PROJECT_ROOT = Path(
    os.getenv(
        "EVOKI_PROJECT_ROOT",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")),
    )
).resolve()

PENDING_PATH = PROJECT_ROOT / "tooling" / "data" / "synapse" / "status" / "pending_status.json"
HISTORY_PATH = PROJECT_ROOT / "tooling" / "data" / "synapse" / "status" / "status_window_history.json"
MANAGER_PATH = PROJECT_ROOT / "tooling" / "scripts" / "automation" / "status_history_manager.py"


def create_test_status():
    """Erstellt ein V5-konformes Test-Status-Window"""
    return {
        "schema_version": "3.2",
        "window_source": "pipeline_test",
        "cycle_backend_controlled": True,
        "step_id": f"test_{datetime.now().strftime('%H%M%S')}",
        "cycle": "1/1",
        "time_source": f"metadata (STRICT_SYNC): {datetime.now(timezone.utc).isoformat()}",
        "prev_window_hash": "AUTO",
        "window_hash": "PLACEHOLDER_BACKEND",
        "mcp_trigger": {"timestamp": datetime.now(timezone.utc).isoformat()},
        "goal": "Pipeline-Test: Verifiziere Stand 0 Funktionalität",
        "inputs": {
            "raw_user_request": "Test der Status Window Pipeline nach Stand 0 Migration",
            "user_messages": ["Pipeline-Test ausgeführt"],
            "system_events": ["test_pipeline.py invoked"],
            "context": {"trigger": "test_pipeline.py", "repo_root": str(PROJECT_ROOT)}
        },
        "actions": ["create_test_status", "write_pending", "add_to_history", "verify_chain"],
        "risk": [],
        "assumptions": ["Watcher ist nicht aktiv - manueller Add"],
        "rule_tangency": {"tangency_detected": False, "notes": "Pipeline-Test"},
        "reflection_curve": {
            "delta": "Stand 0 Migration abgeschlossen",
            "correction": "Keine - Test",
            "next": "Verify Chain Integrity"
        },
        "output_plan": ["Verify chain", "Show last entry"],
        "window_type": "verification",
        "confidence": 0.95,
        "critical_summary": "Pipeline-Test nach Stand 0 Migration"
    }


def main():
    print("=" * 60)
    print("   STAND 0 PIPELINE TEST")
    print("=" * 60)
    print(f"\n📁 PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"📄 PENDING:      {PENDING_PATH}")
    print(f"📜 HISTORY:      {HISTORY_PATH}")
    print(f"🔧 MANAGER:      {MANAGER_PATH}")
    
    # 1. Aktuelle History-Größe
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
            history = json.load(f)
        entries_before = len(history.get("entries", []))
        print(f"\n📊 History vor Test: {entries_before} Einträge")
    else:
        entries_before = 0
        print("\n⚠️  History existiert nicht - wird erstellt")
    
    # 2. Test-Status erstellen und schreiben
    print("\n[1/4] Erstelle Test-Status-Window...")
    status = create_test_status()
    
    print("[2/4] Schreibe nach pending_status.json...")
    PENDING_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PENDING_PATH, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"      ✅ Geschrieben: {PENDING_PATH.name}")
    
    # 3. Manager ausführen (add)
    print("\n[3/4] Führe status_history_manager.py add aus...")
    result = subprocess.run(
        [sys.executable, str(MANAGER_PATH), "add", "--file", str(PENDING_PATH), "--source", "pipeline_test"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    
    if result.returncode == 0:
        print(f"      ✅ Add erfolgreich")
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"         {line}")
    else:
        print(f"      ❌ Add fehlgeschlagen (Exit {result.returncode})")
        if result.stderr:
            print(f"         Error: {result.stderr[:200]}")
        return 1
    
    # 4. Verify ausführen
    print("\n[4/4] Verifiziere Chain-Integrität...")
    result = subprocess.run(
        [sys.executable, str(MANAGER_PATH), "verify"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    
    if result.returncode == 0:
        print(f"      ✅ {result.stdout.strip()}")
    else:
        print(f"      ❌ Verify fehlgeschlagen")
        if result.stderr:
            print(f"         Error: {result.stderr[:200]}")
        return 1
    
    # 5. Zeige letzten Eintrag
    print("\n" + "=" * 60)
    print("   LETZTER HISTORY-EINTRAG")
    print("=" * 60)
    
    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    entries_after = len(history.get("entries", []))
    last_entry = history["entries"][-1] if history.get("entries") else None
    
    if last_entry:
        sw = last_entry.get("status_window", {})
        print(f"  Index:      {last_entry.get('entry_index')}")
        print(f"  Timestamp:  {last_entry.get('timestamp')}")
        print(f"  Goal:       {sw.get('goal', 'N/A')[:50]}")
        print(f"  Source:     {last_entry.get('source')}")
        print(f"  Hash:       {sw.get('window_hash', 'N/A')[:16]}...")
    
    print(f"\n📊 History nach Test: {entries_after} Einträge (+{entries_after - entries_before})")
    
    print("\n" + "=" * 60)
    print("   ✅ PIPELINE TEST ERFOLGREICH!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
