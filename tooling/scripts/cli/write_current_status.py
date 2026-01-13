import json
import os
import sys
import time
import argparse
import tempfile
import hashlib
from pathlib import Path

# KONFIGURATION
# Dynamic Root Resolution (Stand 0 Requirement)
PROJECT_ROOT = os.getenv("EVOKI_PROJECT_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
try:
    PROJECT_ROOT = Path(PROJECT_ROOT).resolve()
except:
    PROJECT_ROOT = Path(os.path.abspath(".")).resolve()

# Fallback check if we are too deep or wrong
if not (PROJECT_ROOT / "tooling").exists():
    # Last ditch: try to find up to 5 levels up
    current = Path(__file__).resolve()
    for _ in range(5):
        if (current / "tooling").exists():
            PROJECT_ROOT = current
            break
        current = current.parent

PENDING_PATH = PROJECT_ROOT / "tooling/data/synapse/status/pending_status.json"
HISTORY_PATH = PROJECT_ROOT / "tooling/data/synapse/status/status_window_history.json"
TIMEOUT_SECONDS = 10

def parse_arguments():
    parser = argparse.ArgumentParser(description="Schreibt ein S2 Status Window und verifiziert die Persistenz.")
    parser.add_argument("--goal", type=str, default="Manuelles Status Update", help="Ziel des Status Windows")
    parser.add_argument("--input", type=str, default="Manual Trigger", help="User Input / Auslöser")
    parser.add_argument("--status", type=str, default="GREEN", choices=["GREEN", "YELLOW", "RED"], help="Critical Summary Status")
    parser.add_argument("--confidence", type=float, default=1.0, help="Confidence Score (0.0 - 1.0)")
    return parser.parse_args()

def read_last_history_entry():
    """Liest den letzten Eintrag aus der Historie sicher aus."""
    if not HISTORY_PATH.exists():
        return None
    try:
        with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data:
                return None
            
            # Handle Dictionary format (v3.0+) vs Legacy List
            if isinstance(data, dict):
                entries = data.get("entries", [])
            elif isinstance(data, list):
                entries = data
            else:
                return None

            if not entries:
                return None
                
            return entries[-1]
    except Exception as e:
        print(f"❌ Fehler beim Lesen der Historie: {e}")
        return None

def wait_for_persistence(expected_goal, timeout=TIMEOUT_SECONDS):
    """Wartet, bis ein Eintrag mit dem erwarteten Goal in der Historie erscheint."""
    print(f"⏳ Warte auf Watcher-Persistenz (Timeout: {timeout}s)...")
    start_time = time.time()
    
    last_known_entry = read_last_history_entry()
    start_index = last_known_entry['entry_index'] if last_known_entry else 0

    while time.time() - start_time < timeout:
        current_entry = read_last_history_entry()
        if current_entry:
            current_index = current_entry.get('entry_index', 0)
            
            # Prüfen ob neuer Eintrag da ist
            if current_index > start_index:
                # Optional: Inhalt prüfen
                if current_entry['status_window'].get('goal') == expected_goal:
                    return True, current_entry
        
        time.sleep(0.5)

    return False, None

def write_pending_status(args):
    """Schreibt das Status Window atomar in pending_status.json."""
    status_content = {
        "step_id": f"manual_{int(time.time())}",
        "cycle": "1/5",
        "time_source": "...: AUTO",  # V5 Compliant Placeholder
        "goal": args.goal,
        "inputs": {
            "raw_user_request": args.input
        },
        "actions": [
            "Manuelles Status-Update via CLI",
            "Warten auf Watcher-Persistenz"
        ],
        "risk": [],
        "rule_tangency": {
            "tangency_detected": False,
            "notes": "Manuelles Tooling"
        },
        "reflection_curve": {
            "delta": "Manueller Trigger ausgelöst",
            "correction": "None",
            "next": "Verifikation durchführen"
        },
        "output_plan": [
            "Persistenz bestätigen"
        ],
        "window_type": "verification",
        "schema_version": "3.2",
        "window_source": "backend_generated",
        "confidence": args.confidence,
        "system_versions": {},
        "cycle_backend_controlled": True,
        "critical_summary": {
            "status": args.status,
            "notes": "Manuell generiert"
        },
        "project_awareness": {
            "active_files": [],
            "context": "CLI Execution"
        },
        "window_hash": "PLACEHOLDER_BACKEND",
        "prev_window_hash": "AUTO",
        "mcp_trigger": {
            "action": "save_to_history",
            "target": "status_history_manager.py",
            "enabled": True
        }
    }

    target_dir = PENDING_PATH.parent
    if not target_dir.exists():
        target_dir.mkdir(parents=True)

    # Atomic Write (Regel B2)
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=str(target_dir), encoding='utf-8') as tmp_file:
            json.dump(status_content, tmp_file, indent=2, ensure_ascii=False)
            tmp_path = tmp_file.name
        
        os.replace(tmp_path, PENDING_PATH)
        print(f"✅ Status Window geschrieben: {PENDING_PATH}")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Schreiben: {e}")
        return False

def main():
    args = parse_arguments()
    
    print("🚀 Starte write_current_status...")
    
    # 1. Schreiben
    if not write_pending_status(args):
        sys.exit(1)

    # 2. Verifizieren
    success, entry = wait_for_persistence(args.goal)
    
    if success:
        print(f"\n✅ ERFOLG! Eintrag wurde persistiert.")
        print(f"   Entry Index: {entry.get('entry_index')}")
        print(f"   Hash:        {entry.get('window_hash')}")
        print(f"   Timestamp:   {entry.get('timestamp')}")
        sys.exit(0)
    else:
        print("\n❌ TIMEOUT! Watcher hat den Eintrag nicht rechtzeitig verarbeitet.")
        print("   Mögliche Ursachen:")
        print("   1. Watcher läuft nicht (pending_status_watcher.py)")
        print("   2. JSON Validierung fehlgeschlagen (siehe pending_watcher.log)")
        sys.exit(1)

if __name__ == "__main__":
    main()
