#!/usr/bin/env python3
"""
Write current Status Window to pending_status.json
V3.0 - Clean V3 structure

This script is called by Antigravity at the end of each response
to enable automatic saving via MCP server monitoring.
"""

import json
import sys
import os
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PENDING_PATH = REPO_ROOT / "tooling" / "data" / "synapse" / "status" / "pending_status.json"

def _atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent), delete=False, suffix=".tmp") as tmp:
            json.dump(payload, tmp, indent=2, ensure_ascii=False)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        tmp_path.replace(path)  # atomic rename on same filesystem
    finally:
        if tmp_path and tmp_path.exists() and tmp_path != path:
            try:
                tmp_path.unlink()
            except Exception:
                pass

def write_pending_status(status_window: dict):
    """Write Status Window to pending_status.json"""
    # Writer darf NICHT “Wahrheit” erzeugen (kein Timestamp/Hash faken).
    _atomic_write_json(PENDING_PATH, status_window)
    
    print(f"✅ Status Window written to pending_status.json", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Status window passed as JSON argument
        status_window = json.loads(sys.argv[1])
        write_pending_status(status_window)
    else:
        # Read from stdin if no argument provided (robustness)
        try:
            input_data = sys.stdin.read()
            if input_data:
                status_window = json.loads(input_data)
                write_pending_status(status_window)
            else:
                print("Usage: python write_pending_status.py '<status_window_json>'", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error reading input: {e}", file=sys.stderr)
            sys.exit(1)
