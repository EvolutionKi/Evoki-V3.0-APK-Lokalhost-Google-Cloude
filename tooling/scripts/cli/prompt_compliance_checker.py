#!/usr/bin/env python3
"""
Prompt Compliance Checker - Vergleicht User-Prompts mit Status Window History

DATENQUELLEN:
1. decrypted_history.json (aus context_watcher.py) - ALLE User-Prompts
2. status_window_history.json (aus pending_status_watcher.py) - Meine Logs

ZIEL: Finde Prompts ohne entsprechendes Status Window = BREACH
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

# Pfade
V3_ROOT = Path(__file__).parent.parent.parent.parent

DECRYPTED_HISTORY = V3_ROOT / "tooling" / "data" / "synapse" / "decrypted_history.json"
STATUS_HISTORY = V3_ROOT / "tooling" / "data" / "synapse" / "status" / "status_window_history.json"


def load_decrypted_history():
    """Lädt alle User-Prompts aus der context_watcher Extraktion"""
    if not DECRYPTED_HISTORY.exists():
        print(f"❌ decrypted_history.json nicht gefunden: {DECRYPTED_HISTORY}")
        return []
    
    with open(DECRYPTED_HISTORY, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    user_prompts = []
    for thread in data:
        for msg in thread.get("messages", []):
            if msg.get("role") == "user":
                user_prompts.append({
                    "text": msg.get("text", ""),
                    "timestamp": msg.get("timestamp", ""),
                    "thread_id": thread.get("id", "unknown")
                })
    
    return user_prompts


def load_status_history():
    """Lädt alle raw_user_request aus der Status Window History"""
    if not STATUS_HISTORY.exists():
        print(f"❌ status_window_history.json nicht gefunden: {STATUS_HISTORY}")
        return []
    
    with open(STATUS_HISTORY, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logged_requests = []
    for entry in data.get("entries", []):
        sw = entry.get("status_window", {})
        inputs = sw.get("inputs", {})
        raw_request = inputs.get("raw_user_request", "")
        if not raw_request:
            messages = inputs.get("user_messages", [])
            if isinstance(messages, list):
                raw_request = " ".join(messages)
        
        if raw_request:
            logged_requests.append({
                "text": raw_request,
                "timestamp": sw.get("time_source", ""),
                "step_id": sw.get("step_id", "unknown")
            })
    
    return logged_requests


def similarity(a: str, b: str) -> float:
    """Berechnet Ähnlichkeit zwischen zwei Strings (0.0 - 1.0)"""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower()[:200], b.lower()[:200]).ratio()


def find_unlogged_prompts(user_prompts, logged_requests, threshold=0.6):
    """Findet User-Prompts die nicht in der Status History sind"""
    unlogged = []
    
    logged_texts = [r["text"] for r in logged_requests]
    
    for prompt in user_prompts:
        prompt_text = prompt["text"]
        
        # Suche nach ähnlichem Eintrag in den geloggten Requests
        best_match = 0.0
        for logged in logged_texts:
            sim = similarity(prompt_text, logged)
            if sim > best_match:
                best_match = sim
        
        if best_match < threshold:
            unlogged.append({
                **prompt,
                "best_match_score": best_match
            })
    
    return unlogged


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║           PROMPT COMPLIANCE CHECKER - V3.0                        ║
║   Vergleicht User-Prompts mit Status Window History               ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    # Lade Daten
    print("📥 Lade Datenquellen...")
    user_prompts = load_decrypted_history()
    logged_requests = load_status_history()
    
    print(f"   User-Prompts (aus VSCode DB): {len(user_prompts)}")
    print(f"   Geloggte Requests (Status Window): {len(logged_requests)}")
    
    if not user_prompts:
        print("\n⚠️  Keine User-Prompts gefunden. Starte context_watcher.py!")
        return
    
    # Finde ungeloggte Prompts
    print("\n🔍 Suche nach ungeloggten Prompts...")
    unlogged = find_unlogged_prompts(user_prompts, logged_requests)
    
    # Berechne Compliance Score
    if user_prompts:
        compliance_rate = (len(user_prompts) - len(unlogged)) / len(user_prompts) * 100
    else:
        compliance_rate = 0
    
    # Status bestimmen
    if compliance_rate >= 90:
        status = "GREEN ✅"
    elif compliance_rate >= 70:
        status = "YELLOW ⚠️"
    else:
        status = "RED 🚨"
    
    # Ausgabe
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║                    COMPLIANCE REPORT                              ║
╠═══════════════════════════════════════════════════════════════════╣
║  Total User-Prompts:           {len(user_prompts):>6}                            ║
║  Geloggte (mit Status Window): {len(user_prompts) - len(unlogged):>6}                            ║
║  UNGELOGGT (BREACH):           {len(unlogged):>6}                            ║
╠═══════════════════════════════════════════════════════════════════╣
║  COMPLIANCE RATE:              {compliance_rate:>5.1f}%                           ║
║  STATUS:                       {status:<12}                      ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    # Zeige ungeloggte Prompts
    if unlogged and len(sys.argv) > 1 and sys.argv[1] == "--details":
        print("\n📋 UNGELOGGTE PROMPTS (Details):")
        print("=" * 70)
        for i, prompt in enumerate(unlogged[:20], 1):
            preview = prompt["text"][:100].replace("\n", " ")
            print(f"\n{i}. [{prompt['thread_id'][:8]}] {prompt['timestamp'][:19]}")
            print(f"   \"{preview}...\"")
            print(f"   Best Match Score: {prompt['best_match_score']:.2f}")
        
        if len(unlogged) > 20:
            print(f"\n... und {len(unlogged) - 20} weitere")
    
    elif unlogged:
        print("💡 Tipp: Nutze --details für eine Liste der ungeloggten Prompts")
    
    print("\n✅ Analyse abgeschlossen")


if __name__ == "__main__":
    main()
