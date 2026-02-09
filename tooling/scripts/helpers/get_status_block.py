#!/usr/bin/env python3
"""
V5 Status Block Generator (Legacy-Free)
=======================================
Generates a valid V5 Status Window JSON block for insertion into prompts or manual usage.
Adheres to "Backend Authoritative" principle:
- No local ID generation (step_id=manual)
- No local hashing (window_hash=PLACEHOLDER)
- No local timestamping (time_source=...: AUTO)
"""

import sys
import json
import argparse
import os
from pathlib import Path

# === Dynamic Root Resolution ===
PROJECT_ROOT = os.getenv("EVOKI_PROJECT_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
try:
    PROJECT_ROOT = Path(PROJECT_ROOT).resolve()
except:
    PROJECT_ROOT = Path(os.path.abspath(".")).resolve()

# Fallback check
if not (PROJECT_ROOT / "tooling").exists():
    current = Path(__file__).resolve()
    for _ in range(5):
        if (current / "tooling").exists():
            PROJECT_ROOT = current
            break
        current = current.parent

OUTPUT_FILE = PROJECT_ROOT / "tooling/data/synapse/current_status.json"

def generate_block():
    parser = argparse.ArgumentParser(description="Generate V5 Status Block")
    parser.add_argument("--goal", default="Manual Status Block", help="Goal description")
    parser.add_argument("--inputs", default="Manual Trigger", help="Comma separated inputs")
    args = parser.parse_args()

    # Split inputs if comma separated
    inputs_list = [i.strip() for i in args.inputs.split(',')] if ',' in args.inputs else [args.inputs]

    block = {
        "step_id": "manual_gen",
        "cycle": "1/5",
        "time_source": "...: AUTO",
        "goal": args.goal,
        "inputs": {
            "raw_user_request": inputs_list[0] if inputs_list else "Unknown Input",
            "user_messages": inputs_list,
            "system_events": [],
            "context": "cli_generated"
        },
        "actions": [
            "Generated via tooling/scripts/helpers/get_status_block.py"
        ],
        "risk": [],
        "rule_tangency": {
            "tangency_detected": False,
            "notes": "Manual Generation"
        },
        "reflection_curve": {
            "delta": "Manual Block Requested",
            "correction": "None",
            "next": "Paste into context"
        },
        "output_plan": [
            "Verify Block"
        ],
        "window_type": "planner",
        "schema_version": "3.2",
        "window_source": "agent_generated_manual",
        "confidence": 1.0,
        "system_versions": {},
        "cycle_backend_controlled": True,
        
        "critical_summary": {
            "status": "GREEN",
            "notes": "Manual Block"
        },
        
        "project_awareness": {
            "status": "MANUAL_GEN",
            "context": "Tooling CLI"
        },
        
        "window_hash": "PLACEHOLDER_BACKEND",
        "prev_window_hash": "AUTO",
        
        "mcp_trigger": {
            "action": "save_to_history",
            "target": "status_history_manager.py",
            "enabled": True
        }
    }
    
    json_output = json.dumps(block, indent=2, ensure_ascii=False)
    
    # Print to stdout for capture
    print(json_output)
    
    # Write to file (Draft)
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(json_output)
        # We also logging to stderr so as not to pollute stdout (which might be piped)
        print(f"\n[INFO] Draft block written to: {OUTPUT_FILE}", file=sys.stderr)
    except Exception as e:
        print(f"\n[WARN] Could not write draft file: {e}", file=sys.stderr)

if __name__ == "__main__":
    generate_block()
