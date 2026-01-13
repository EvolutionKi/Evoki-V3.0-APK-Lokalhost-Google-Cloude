import json
import hashlib
import sys
import os
from pathlib import Path

HISTORY_FILE = Path(r"c:\Evoki V3.0 APK-Lokalhost-Google Cloude\tooling\data\synapse\status\status_window_history.json")

def canonical_json_dump(data):
    """Produces canonical JSON string for hashing (no spaces, sorted keys)."""
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def calculate_window_hash(entry):
    """
    Calculates the hash of a user status window entry.
    Format: sha256(canonical_json(status_window_without_self_hash)|timestamp|salt)
    """
    # 1. Get status_window content
    sw = entry.get("status_window", {}).copy()
    
    # 2. Remove the self-hash 'window_hash' field from the content to avoid recursion
    if "window_hash" in sw:
        del sw["window_hash"]
        
    # 3. Canonicalize
    sw_json = canonical_json_dump(sw)
    
    # 4. Concatenate with PIPE separators (Matches synapse_logic.py)
    timestamp = entry.get("timestamp", "")
    salt = entry.get("salt", "")
    payload = f"{sw_json}|{timestamp}|{salt}"
    
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def repair_chain():
    if not HISTORY_FILE.exists():
        print(f"File not found: {HISTORY_FILE}")
        return

    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        return

    entries = data.get("entries", [])
    if not entries:
        print("No entries found.")
        return

    print(f"Loaded {len(entries)} entries. Repairing chain...")

    # Iterate and fix
    for i in range(len(entries)):
        entry = entries[i]
        
        # 1. Fix prev_window_hash
        if i == 0:
            entry["status_window"]["prev_window_hash"] = None
        else:
            prev_entry = entries[i-1]
            prev_hash = prev_entry["window_hash"]
            entry["status_window"]["prev_window_hash"] = prev_hash

        # 2. Re-calculate THIS entry's hash using CORRECT algorithm
        new_hash = calculate_window_hash(entry)
        entry["window_hash"] = new_hash
        entry["status_window"]["window_hash"] = new_hash 
        
        print(f"Entry {i}: Hash {new_hash[:8]}... (linked to {str(entry['status_window']['prev_window_hash'])[:8]}...)")

    # Save back
    data["entries"] = entries
    
    # Write to file
    HISTORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Repaired chain saved to {HISTORY_FILE}")

if __name__ == "__main__":
    repair_chain()
