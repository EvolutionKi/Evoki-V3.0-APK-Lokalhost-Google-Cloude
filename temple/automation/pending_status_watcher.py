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
3. Auto-triggers: python temple/automation/status_history_manager.py add --file pending_status.json
4. History saved with salt and cryptographic hash
"""

import sys
import time
import json
import subprocess
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
    
    # V3.0 Optimized Paths
    V3_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
    PENDING_FILE = V3_ROOT / "data" / "synapse" / "status" / "pending_status.json"
    HISTORY_MANAGER = V3_ROOT / "temple" / "automation" / "status_history_manager.py"
    LOG_FILE = V3_ROOT / "data" / "synapse" / "pending_watcher.log"
    
    def __init__(self):
        super().__init__()
        
        # Ensure paths exist
        self.PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Track last modification time to avoid duplicate triggers
        self.last_mtime = 0
        
        print(f"🔍 Pending Status Watcher initialized (V3.0)")
        print(f"   Watching: {self.PENDING_FILE}")
        print(f"   Manager:  {self.HISTORY_MANAGER}")
        print(f"   Log:      {self.LOG_FILE}")
    
    def on_modified(self, event: FileModifiedEvent):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only process pending_status.json
        if file_path.name != "pending_status.json":
            return
        
        # Check if file actually changed (avoid duplicate events)
        try:
            current_mtime = file_path.stat().st_mtime
            if current_mtime == self.last_mtime:
                return  # No actual change
            self.last_mtime = current_mtime
        except:
            return
        
        self._log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "file_modified",
            "file": str(file_path)
        })
        
        # Wait for file to be fully written
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
