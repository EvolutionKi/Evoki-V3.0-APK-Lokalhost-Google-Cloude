#!/usr/bin/env python3
"""
COMPLIANCE ENFORCER - Aktive Durchsetzung der Status Window Regel

Dieses Script läuft ZUSAMMEN mit dem pending_status_watcher und:
1. Überwacht die decrypted_history.json (neue User-Prompts)
2. Prüft ob innerhalb von X Sekunden ein Status Window geschrieben wurde
3. WARNT sofort wenn nicht (Windows Toast Notification)
4. Optional: Schreibt automatisch ein BREACH-Status-Window

ZIEL: Nicht nur registrieren, sondern AKTIV DURCHSETZEN!
"""

import json
import time
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Windows Notifications
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("⚠️  plyer nicht installiert - pip install plyer")

# Pfade
V3_ROOT = Path(__file__).parent.parent.parent.parent
DECRYPTED_HISTORY = V3_ROOT / "tooling" / "data" / "synapse" / "decrypted_history.json"
STATUS_HISTORY = V3_ROOT / "tooling" / "data" / "synapse" / "status" / "status_window_history.json"
PENDING_STATUS = V3_ROOT / "tooling" / "data" / "synapse" / "status" / "pending_status.json"
ENFORCER_LOG = V3_ROOT / "tooling" / "data" / "synapse" / "compliance_enforcer.log"

# Konfiguration
CHECK_INTERVAL = 10  # Sekunden zwischen Checks
MAX_RESPONSE_TIME = 60  # Sekunden die der Agent hat um ein Status Window zu schreiben
AUTO_BREACH_WINDOW = True  # Automatisch BREACH-Window schreiben wenn Zeit abgelaufen


class ComplianceEnforcer:
    def __init__(self):
        self.last_prompt_time = None
        self.last_prompt_text = None
        self.last_status_count = 0
        self.breach_count = 0
        self.warned = False
        
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║           COMPLIANCE ENFORCER - ACTIVE ENFORCEMENT                ║
║   Nicht nur registrieren - DURCHSETZEN!                           ║
╚═══════════════════════════════════════════════════════════════════╝
""")
        print(f"📁 Decrypted History: {DECRYPTED_HISTORY}")
        print(f"📁 Status History: {STATUS_HISTORY}")
        print(f"⏱️  Max Response Time: {MAX_RESPONSE_TIME}s")
        print(f"🔔 Notifications: {'✅' if NOTIFICATIONS_AVAILABLE else '❌'}")
        print(f"🚨 Auto BREACH Window: {'✅' if AUTO_BREACH_WINDOW else '❌'}")
        print()
    
    def log(self, message: str):
        """Log to file and console"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        
        try:
            with open(ENFORCER_LOG, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
        except:
            pass
    
    def notify(self, title: str, message: str, urgent: bool = False):
        """Send Windows notification"""
        if not NOTIFICATIONS_AVAILABLE:
            self.log(f"🔔 NOTIFICATION (would send): {title} - {message}")
            return
        
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Evoki Compliance Enforcer",
                timeout=10 if not urgent else 30
            )
        except Exception as e:
            self.log(f"❌ Notification failed: {e}")
    
    def get_latest_prompt(self):
        """Get the most recent user prompt from decrypted_history"""
        if not DECRYPTED_HISTORY.exists():
            return None, None
        
        try:
            with open(DECRYPTED_HISTORY, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            latest_time = None
            latest_text = None
            
            for thread in data:
                for msg in thread.get("messages", []):
                    if msg.get("role") == "user":
                        timestamp_str = msg.get("timestamp", "")
                        text = msg.get("text", "")
                        
                        if timestamp_str and text:
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                if latest_time is None or timestamp > latest_time:
                                    latest_time = timestamp
                                    latest_text = text
                            except:
                                pass
            
            return latest_time, latest_text
        except:
            return None, None
    
    def get_status_count(self):
        """Get current count of status window entries"""
        if not STATUS_HISTORY.exists():
            return 0
        
        try:
            with open(STATUS_HISTORY, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return len(data.get("entries", []))
        except:
            return 0
    
    def write_breach_window(self, prompt_text: str):
        """Automatically write a BREACH status window"""
        breach_window = {
            "step_id": f"AUTO_BREACH_{int(time.time())}",
            "cycle": "BREACH/BREACH",
            "time_source": f"metadata (STRICT_SYNC): {datetime.now().isoformat()}",
            "goal": "AUTOMATISCHES BREACH WINDOW - Agent hat nicht rechtzeitig geantwortet",
            "inputs": {
                "raw_user_request": prompt_text[:500] if prompt_text else "UNKNOWN"
            },
            "actions": [
                "COMPLIANCE ENFORCER hat eingegriffen",
                f"Keine Antwort innerhalb von {MAX_RESPONSE_TIME} Sekunden"
            ],
            "risk": ["Protokollbruch durch Agent"],
            "assumptions": [],
            "rule_tangency": {
                "tangency_detected": True,
                "notes": "AUTOMATISCH GENERIERT wegen Protokollbruch"
            },
            "reflection_curve": {
                "delta": "Agent hat Status Window nicht geschrieben",
                "correction": "Enforcer hat automatisch BREACH-Window erstellt",
                "next": "Agent muss Disziplin verbessern"
            },
            "output_plan": ["Agent muss reagieren"],
            "window_type": "verification",
            "schema_version": "3.2",
            "window_source": "COMPLIANCE_ENFORCER_AUTO",
            "confidence": 0.0,
            "system_versions": {},
            "cycle_backend_controlled": True,
            "critical_summary": {
                "status": "RED",
                "notes": "AUTOMATISCHES BREACH WINDOW"
            },
            "project_awareness": {},
            "window_hash": "PLACEHOLDER_BACKEND",
            "prev_window_hash": "AUTO",
            "mcp_trigger": {
                "action": "save_to_history",
                "target": "status_history_manager.py",
                "enabled": True
            }
        }
        
        try:
            with open(PENDING_STATUS, 'w', encoding='utf-8') as f:
                json.dump(breach_window, f, indent=2, ensure_ascii=False)
            self.log("🚨 BREACH WINDOW AUTOMATISCH GESCHRIEBEN!")
            return True
        except Exception as e:
            self.log(f"❌ Konnte BREACH Window nicht schreiben: {e}")
            return False
    
    def check(self):
        """Main check cycle"""
        # Get latest prompt
        prompt_time, prompt_text = self.get_latest_prompt()
        current_status_count = self.get_status_count()
        
        # New prompt detected?
        if prompt_time and prompt_text:
            if self.last_prompt_text != prompt_text:
                # New prompt!
                self.last_prompt_time = prompt_time
                self.last_prompt_text = prompt_text
                self.last_status_count = current_status_count
                self.warned = False
                
                preview = prompt_text[:50].replace('\n', ' ')
                self.log(f"📝 Neuer Prompt erkannt: \"{preview}...\"")
        
        # Check if status window was written
        if self.last_prompt_time:
            time_since_prompt = (datetime.now() - self.last_prompt_time).total_seconds()
            status_written = current_status_count > self.last_status_count
            
            if status_written:
                if not self.warned:
                    self.log(f"✅ Status Window geschrieben ({time_since_prompt:.0f}s nach Prompt)")
                self.last_prompt_time = None  # Reset
                self.last_status_count = current_status_count
                self.warned = False
            
            elif time_since_prompt > MAX_RESPONSE_TIME:
                if not self.warned:
                    self.breach_count += 1
                    self.log(f"🚨 BREACH! Kein Status Window nach {time_since_prompt:.0f}s!")
                    
                    self.notify(
                        "🚨 COMPLIANCE BREACH!",
                        f"Kein Status Window nach {MAX_RESPONSE_TIME}s!\nBreach #{self.breach_count}",
                        urgent=True
                    )
                    
                    if AUTO_BREACH_WINDOW:
                        self.write_breach_window(self.last_prompt_text)
                    
                    self.warned = True
            
            elif time_since_prompt > MAX_RESPONSE_TIME / 2 and not self.warned:
                # Warning at 50%
                remaining = MAX_RESPONSE_TIME - time_since_prompt
                self.log(f"⚠️  WARNUNG: Noch {remaining:.0f}s für Status Window!")
                self.notify(
                    "⚠️ Status Window fehlt!",
                    f"Noch {remaining:.0f}s Zeit!",
                    urgent=False
                )
    
    def run(self):
        """Main loop"""
        self.log("🚀 Enforcer gestartet - Überwache Compliance...")
        
        try:
            while True:
                self.check()
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            self.log("\n🛑 Enforcer gestoppt")
            print(f"\n📊 Statistik: {self.breach_count} Breaches erkannt")


if __name__ == "__main__":
    enforcer = ComplianceEnforcer()
    enforcer.run()
