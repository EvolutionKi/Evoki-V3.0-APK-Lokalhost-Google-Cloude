#!/usr/bin/env python3
"""
Write current Status Window to pending_status.json
V3.0 - Clean V3 structure

This script is called by Antigravity at the end of each response
to enable automatic saving via MCP server monitoring.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def write_pending_status(status_window: dict):
    """Write Status Window to pending_status.json"""
    # V3.0 Optimized Path
    v3_root = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
    pending_path = v3_root / "data" / "synapse" / "status" / "pending_status.json"
    
    # Ensure directory exists
    pending_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure timestamp is set
    if status_window.get("mcp_trigger", {}).get("timestamp") == "PLACEHOLDER":
        status_window["mcp_trigger"]["timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    if status_window.get("time_source", "").endswith("PLACEHOLDER"):
        status_window["time_source"] = f"metadata (STRICT_SYNC): {datetime.now().isoformat()}"
    
    # Write atomically
    with open(pending_path, 'w', encoding='utf-8') as f:
        json.dump(status_window, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Status Window written to pending_status.json", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Status window passed as JSON argument
        status_window = json.loads(sys.argv[1])
        write_pending_status(status_window)
    else:
        print("Usage: python write_pending_status.py '<status_window_json>'", file=sys.stderr)
        sys.exit(1)
