#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pending Status Watcher - Automatic History Logging
V3.0 - Clean V3 structure

Monitors pending_status.json for changes and automatically triggers
status_history_manager.py to save to history when the file is updated.

This completes the automatic logging pipeline:
1. Agent writes to pending_status.json
2. File Watcher detects change
3. Auto-triggers: python tooling/scripts/automation/status_history_manager.py add --file pending_status.json
4. History saved with salt and cryptographic hash
"""

import sys
import time
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime, timezone

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent
except ImportError:
    print("❌ ERROR: watchdog not installed")
    print("   Install: pip install watchdog")
    sys.exit(1)


class PendingStatusWatcher(FileSystemEventHandler):
    """Monitors pending_status.json and auto-saves to history"""
    
    def __init__(self):
        super().__init__()
        
        # V3.0 Optimized Paths (Dynamic with Fallback)
        # Determine PROJECT_ROOT dynamically
        self.V3_ROOT = Path(os.getenv("EVOKI_PROJECT_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))).resolve()
        
        # Fallback to current dir if env var not set or wrong (e.g., if 'tooling' doesn't exist under assumed root)
        if not (self.V3_ROOT / "tooling").exists():
            self.V3_ROOT = Path(os.path.abspath(".")).resolve()

        self.PENDING_FILE = self.V3_ROOT / "tooling" / "data" / "synapse" / "status" / "pending_status.json"
        
        # CHANGED: Now in tooling/scripts/automation
        self.HISTORY_MANAGER = self.V3_ROOT / "tooling" / "scripts" / "automation" / "status_history_manager.py"
        
        self.LOG_FILE = self.V3_ROOT / "tooling" / "data" / "synapse" / "logs" / "pending_watcher.log"
        
        # Ensure paths exist
        try:
            self.PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass # Ignore perms
        
        # Track last modification time to avoid duplicate triggers
        self.last_mtime = 0
        
        print(f"🔍 Pending Status Watcher initialized (V3.0)")
        print(f"   Root:     {self.V3_ROOT}")
        print(f"   Watching: {self.PENDING_FILE}")
        print(f"   Manager:  {self.HISTORY_MANAGER}")
        print(f"   Log:      {self.LOG_FILE}")
    
    def on_modified(self, event):
        """Handle file modification events"""
        self._process_change(event)

    def on_created(self, event):
        """Handle file creation events (atomic write first step)"""
        self._process_change(event)

    def on_moved(self, event):
        """Handle file move events (atomic write final step)"""
        # For move events, dest_path is the file we care about
        if not event.is_directory and Path(event.dest_path).name == "pending_status.json":
            self._handle_file_logic(Path(event.dest_path))

    def _process_change(self, event):
        """Unified event processor"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.name != "pending_status.json":
            return
            
        self._handle_file_logic(file_path)

    def _handle_file_logic(self, file_path: Path):
        """Core logic for file change handling"""
        # Check if file actually changed (avoid duplicate events)
        try:
            current_mtime = file_path.stat().st_mtime
            # Note: For atomic writes (moves), mtime might be preserved or updated. 
            # We trust the event trigger mostly, but debouncing is good.
            if current_mtime == self.last_mtime:
                return  # No actual change
            self.last_mtime = current_mtime
        except Exception:
            return
        
        self._log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "file_updated",
            "file": str(file_path)
        })
        
        # Wait for file to be fully written (if necessary)
        time.sleep(0.2)
        
        # Trigger auto-save
        self.auto_save()
    
    def auto_save(self):
        """Automatically save pending_status.json to history"""
        self._log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "auto_save_triggered"
        })
        
        try:
            # Call status_history_manager.py add
            cmd = [
                sys.executable,
                str(self.HISTORY_MANAGER),
                "add",
                "--file", str(self.PENDING_FILE),
                "--source", "pending_status_auto"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Print output for visibility
            if result.stdout:
                print(result.stdout)
            
            if result.returncode == 0:
                print(f"✅ Auto-saved to history at {datetime.now().strftime('%H:%M:%S')}")
                self._log({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "result": "SUCCESS"
                })
            else:
                print(f"❌ Auto-save failed (exit code {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}")
                
                self._log({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "result": "FAIL",
                    "error": result.stderr[:500] if result.stderr else "Unknown error"
                })
        
        except subprocess.TimeoutExpired:
            print(f"⌛ Auto-save timeout")
            self._log({"error": "Timeout"})
        
        except Exception as e:
            print(f"❌ Watcher error: {e}")
            self._log({"error": str(e)})
    
    def _log(self, data: dict):
        """Log event to JSONL file"""
        try:
            with open(self.LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"Failed to log: {e}", file=sys.stderr)


def main():
    """Start the watcher"""
    # Health Probe for Single Source of Truth
    if os.environ.get("EVOKI_MCP_MONITOR_ACTIVE") == "1":
         print("MCP Monitor already active. Skipping standalone watcher to prevent loop.")
         return

    watcher = PendingStatusWatcher()
    
    # Watch the directory containing pending_status.json
    watch_dir = watcher.PENDING_FILE.parent
    
    observer = Observer()
    observer.schedule(watcher, str(watch_dir), recursive=False)
    observer.start()
    
    print(f"\n🔍 Pending Status Watcher ACTIVE (V3.0)")
    print(f"   Monitoring: {watch_dir}")
    print(f"   Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Watcher stopped")


if __name__ == "__main__":
    main()
