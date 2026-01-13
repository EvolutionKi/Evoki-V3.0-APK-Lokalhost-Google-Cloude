#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Status Window History Manager (CLI Interface)
V3.0 - Clean path structure
"""

import sys
import json
import argparse
from pathlib import Path

# Import the core logic from temple.automation
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from temple.automation.synapse_logic import StatusHistoryManager


def main():
    """CLI interface for Status History Manager"""
    parser = argparse.ArgumentParser(description="Status Window History Manager (CLI)")
    parser.add_argument("command", choices=["add", "list", "stats", "latest", "verify"], help="Command to execute")
    parser.add_argument("--file", help="JSON file containing Status Window to add")
    parser.add_argument("--source", default="manual", help="Source identifier")
    parser.add_argument("--count", type=int, default=5, help="Number of entries to show")
    
    args = parser.parse_args()
    
    manager = StatusHistoryManager()
    
    if args.command == "add":
        if not args.file:
            print("Error: --file required for 'add' command", file=sys.stderr)
            sys.exit(1)
        
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract status_window if wrapped
            status_window = data.get("status_window", data)
            
            print(f"DEBUG: Calling add_status_window...", file=sys.stderr)
            success = manager.add_status_window(status_window, source=args.source)
            print(f"DEBUG: add_status_window returned: {success}", file=sys.stderr)
            sys.exit(0 if success else 1)
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif args.command == "list":
        entries = manager.get_all()
        print(json.dumps(entries, indent=2, ensure_ascii=False))
    
    elif args.command == "latest":
        entries = manager.get_latest(args.count)
        print(json.dumps(entries, indent=2, ensure_ascii=False))
    
    elif args.command == "stats":
        stats = manager.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.command == "verify":
        entries = manager.get_all()
        if not entries:
            print("✅ No entries to verify (history is empty)")
            sys.exit(0)
        
        print(f"🔍 Verifying {len(entries)} entries...")
        
        # Check chain integrity
        for i in range(1, len(entries)):
            prev_entry = entries[i-1]
            curr_entry = entries[i]
            
            prev_hash = prev_entry.get("window_hash")
            claimed_prev = curr_entry.get("status_window", {}).get("prev_window_hash")
            
            if claimed_prev != prev_hash:
                print(f"❌ Chain break at entry {i}!")
                print(f"   Expected: {prev_hash}")
                print(f"   Got:      {claimed_prev}")
                sys.exit(1)
        
        print(f"✅ Chain integrity verified ({len(entries)} entries)")
        sys.exit(0)


if __name__ == "__main__":
    main()
