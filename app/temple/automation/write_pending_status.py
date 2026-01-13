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
from datetime import datetime, timezone


def write_pending_status(status_window: dict):
    """Write Status Window to pending_status.json"""
    # V3.0 Optimized Path
    v3_root = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
    pending_path = v3_root / "tooling" / "data" / "synapse" / "status" / "pending_status.json"
    
    # Ensure directory exists
    pending_path.parent.mkdir(parents=True, exist_ok=True)

    # Minimal shape so MCP monitor can react (it checks presence of mcp_trigger)
    if "mcp_trigger" not in status_window or not isinstance(status_window.get("mcp_trigger"), dict):
        status_window["mcp_trigger"] = {"timestamp": "PLACEHOLDER"}

    # Atomic write: tmp file in same dir + replace
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(pending_path.parent),
            delete=False,
            suffix=".tmp",
        ) as tmp:
            json.dump(status_window, tmp, indent=4, ensure_ascii=False)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)

        tmp_path.replace(pending_path)
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
    
    print(f"✅ Status Window written to pending_status.json", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Status window passed as JSON argument
        status_window = json.loads(sys.argv[1])
        write_pending_status(status_window)
    else:
        print("Usage: python write_pending_status.py '<status_window_json>'", file=sys.stderr)
        sys.exit(1)
