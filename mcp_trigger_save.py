#!/usr/bin/env python3
"""
MCP Trigger Script - Notifies MCP server of new Status Window save
Called by backend after browser extension triggers save
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def trigger_mcp_update(status_file_path):
    """
    Notify MCP server that a new Status Window has been saved.
    This allows the MCP server to update its prompt_chain resource.
    """
    
    # Load the saved status window
    try:
        with open(status_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading status file: {e}", file=sys.stderr)
        return False
    
    status_window = data.get("status_window", {})
    
    # Update MCP server state (if running)
    # This could be done via HTTP, file system, or shared memory
    # For now, we'll use a simple file-based approach
    
    mcp_state_dir = Path("C:/Evoki V2.0/evoki-app/data/synapse/mcp_state")
    mcp_state_dir.mkdir(parents=True, exist_ok=True)
    
    # Write latest status to MCP state
    latest_status_file = mcp_state_dir / "latest_status_window.json"
    
    try:
        with open(latest_status_file, 'w', encoding='utf-8') as f:
            json.dump({
                "status_window": status_window,
                "source_file": str(status_file_path),
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "trigger": "browser_extension"
            }, f, indent=2)
        
        print(f"✅ MCP state updated: {latest_status_file}")
        return True
        
    except Exception as e:
        print(f"Error updating MCP state: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: mcp_trigger_save.py <status_file_path>", file=sys.stderr)
        sys.exit(1)
    
    status_file = sys.argv[1]
    
    if not Path(status_file).exists():
        print(f"Error: Status file not found: {status_file}", file=sys.stderr)
        sys.exit(1)
    
    success = trigger_mcp_update(status_file)
    sys.exit(0 if success else 1)
