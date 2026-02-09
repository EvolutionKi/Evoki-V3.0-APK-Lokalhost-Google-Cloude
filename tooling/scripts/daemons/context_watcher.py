
import sqlite3
import json
import os
import time
import shutil
import hashlib
import tempfile
import sys
import glob
from datetime import datetime

# Configuration - V3.0 Paths
V3_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ARCHIVE_FILE = os.path.join(V3_ROOT, "tooling", "data", "synapse", "decrypted_history.json")
POLL_INTERVAL = 5  # Seconds

class ContextWatcher:
    def __init__(self, archive_path=ARCHIVE_FILE):
        self.archive_path = archive_path
        self.last_hashes = {}  # Map path -> hash
        self.known_message_hashes = set()
        print(f"[*] Context Watcher initialized.")
        print(f"    Archive: {self.archive_path}")
        
        self.load_archive()

    def get_all_dbs(self):
        """Finds all relevant state.vscdb files (Global + Workspaces + Gemini)."""
        paths = [
            os.path.expandvars(r"%APPDATA%\Code\User\globalStorage\state.vscdb"),
            os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb"),
        ]
        
        # Scan all workspace folders
        ws_root = os.path.expandvars(r"%APPDATA%\Code\User\workspaceStorage")
        if os.path.exists(ws_root):
            # Look for state.vscdb in immediate subdirectories
            ws_dbs = glob.glob(os.path.join(ws_root, "*", "state.vscdb"))
            paths.extend(ws_dbs)
            
        # Filter existing unique paths
        valid_paths = list(set([p for p in paths if os.path.exists(p)]))
        return valid_paths

    def load_archive(self):
        if os.path.exists(self.archive_path):
            try:
                with open(self.archive_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    count = 0
                    for thread in data:
                        for msg in thread.get("messages", []):
                            h = self.hash_message(msg)
                            self.known_message_hashes.add(h)
                            count += 1
                    print(f"[+] Loaded archive: {len(data)} threads, {count} messages.")
            except Exception as e:
                print(f"[!] Failed to load archive: {e}")
        else:
            print("[*] No existing archive found. Starting fresh.")

    def hash_message(self, msg):
        # Create a unique signature: timestamp|role|text
        sig = f"{msg.get('timestamp','')}|{msg.get('role','')}|{msg.get('text','')}"
        return hashlib.sha256(sig.encode('utf-8')).hexdigest()

    def get_file_hash(self, path):
        try:
            stat = os.stat(path)
            # Use size + mtime as a quick change detector
            return f"{stat.st_mtime}-{stat.st_size}"
        except:
            return None

    def parse_interactive_session(self, value_json):
        """Parses the memento/interactive-session structure (User Inputs)."""
        messages = []
        try:
            data = json.loads(value_json)
            # Check for history.copilot struct
            if "history" in data:
                copilot_msgs = data["history"].get("copilot", [])
                for item in copilot_msgs:
                    text = item.get("text")
                    if text:
                        # Estimate timestamp or use current if missing
                        # This source usually lacks timestamps
                        messages.append({
                            "role": "user",
                            "text": text,
                            "timestamp": datetime.now().isoformat()
                        })
        except:
            pass
        return messages

    def parse_history(self, history_list):
        """Parses the standard geminiCodeAssist history."""
        parsed = []
        for item in history_list:
            role = item.get("entity", "unknown")
            text = item.get("markdownText") or item.get("text") or ""
            timestamp = item.get("timestamp", "")
            
            if text:
                parsed.append({
                    "role": role,
                    "text": text,
                    "timestamp": timestamp
                })
        return parsed

    def extract_from_db(self, db_path):
        """safely extracts messages from a single DB."""
        messages = [] # List of threads or flat messages?
        # We'll return a list of 'thread' objects to keep consistent structure
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            shutil.copy2(db_path, tmp_path)
            conn = sqlite3.connect(tmp_path)
            cursor = conn.cursor()
            
            # 1. Global / Standard Keys
            cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%gemini%' OR key LIKE '%chatThreads%' OR key LIKE '%history%' OR key = 'memento/interactive-session'")
            rows = cursor.fetchall()
            
            for key, value in rows:
                if key == 'memento/interactive-session':
                    # Flat list of user messages
                    msgs = self.parse_interactive_session(value)
                    if msgs:
                        messages.append({
                            "id": "interactive-session",
                            "email": "local",
                            "key": key,
                            "messages": msgs
                        })
                else:
                    # Standard Parsing
                    try:
                        data = json.loads(value)
                        
                        target_data = data
                        if isinstance(data, dict) and "geminiCodeAssist.chatThreads" in data:
                             target_data = data["geminiCodeAssist.chatThreads"]
                        elif isinstance(data, dict) and "google.geminicodeassist" in data:
                             inner = json.loads(data["google.geminicodeassist"])
                             if "geminiCodeAssist.chatThreads" in inner:
                                 target_data = inner["geminiCodeAssist.chatThreads"]

                        if isinstance(target_data, dict):
                            for email, threads in target_data.items():
                                if isinstance(threads, dict):
                                    for thread_id, thread_data in threads.items():
                                        if isinstance(thread_data, dict) and "history" in thread_data:
                                            msgs = self.parse_history(thread_data["history"])
                                            if msgs:
                                                messages.append({
                                                    "id": thread_id,
                                                    "email": email,
                                                    "key": key,
                                                    "messages": msgs
                                                })
                    except:
                        continue

            conn.close()
        except:
             pass
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
        
        return messages

    def update_archive(self, new_threads):
        updates_count = 0
        
        current_data = []
        if os.path.exists(self.archive_path):
            try:
                with open(self.archive_path, "r", encoding="utf-8") as f:
                    current_data = json.load(f)
            except:
                pass
                
        thread_map = {t["id"]: t for t in current_data}
        
        for new_t in new_threads:
            tid = new_t["id"]
            if tid not in thread_map:
                thread_map[tid] = {"id": tid, "email": new_t["email"], "messages": []}
            
            existing_msgs = thread_map[tid]["messages"]
            
            for msg in new_t["messages"]:
                h = self.hash_message(msg)
                if h not in self.known_message_hashes:
                    existing_msgs.append(msg)
                    self.known_message_hashes.add(h)
                    updates_count += 1
        
        if updates_count > 0:
            print(f"[+] Archiving {updates_count} new messages.")
            try:
                with open(self.archive_path, "w", encoding="utf-8") as f:
                    json.dump(list(thread_map.values()), f, indent=2)
            except Exception as e:
                print(f"[!] Failed to write archive: {e}")

    def check_live_log(self):
        log_path = os.path.expandvars(r"C:\Evoki V2.0\evoki-app\.agent\live_context.log")
        if not os.path.exists(log_path): return
        
        new_msgs = []
        try:
            with open(log_path, 'rb') as f:
                offset = 0
                for line in f:
                    line_len = len(line)
                    try:
                        line_str = line.decode('utf-8', errors='ignore').strip()
                        if line_str and line_str.startswith('[') and '] ' in line_str:
                            parts = line_str.split('] ', 1)
                            channel = parts[0][1:]
                            text = parts[1]
                            
                            if "Gemini" in channel or "Output" in channel:
                                # Stable hash based on file offset
                                sig = f"LOG|{offset}|{text}"
                                h = hashlib.sha256(sig.encode('utf-8')).hexdigest()
                                
                                if h not in self.known_message_hashes:
                                    new_msgs.append({
                                        "role": "model",
                                        "text": text,
                                        "timestamp": datetime.now().isoformat(),
                                        "source": "live_log"
                                    })
                                    self.known_message_hashes.add(h)
                    except:
                        pass
                    offset += line_len
            
            if new_msgs:
                # Merge into a special thread or distributed?
                # Using a single stream thread for logs is safest
                self.update_archive([{"id": "live-log-stream", "email": "local", "messages": new_msgs}])
                
        except Exception as e:
            print(f"[!] Log check error: {e}")

    def run_once(self):
        dbs = self.get_all_dbs()
        if not dbs:
            # print("No DBs found.")
            return

        for db_path in dbs:
            current_hash = self.get_file_hash(db_path)
            last_hash = self.last_hashes.get(db_path)
            
            if current_hash != last_hash:
                print(f"[*] Change detected in {os.path.basename(db_path)}...")
                threads = self.extract_from_db(db_path)
                self.update_archive(threads)
                self.last_hashes[db_path] = current_hash
        
        self.check_live_log()

    def loop(self):
        print(f"[*] Watching {len(self.get_all_dbs())} database files...")
        try:
            while True:
                self.run_once()
                time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("\n[*] Watcher stopped.")

if __name__ == "__main__":
    if "--monitor" in sys.argv:
        watcher = ContextWatcher()
        watcher.loop()
    else:
        print("Run with --monitor to start watching.")
