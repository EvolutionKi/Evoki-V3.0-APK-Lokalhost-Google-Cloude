#!/usr/bin/env python3
"""
Live Pipeline Monitor — V3.0 (Terminal UI)
Zeigt Status für ALLE 5 V3.0 Datenbanken
"""

import json
import time
from pathlib import Path

STATUS_FILE = Path("backend/data/pipeline_status.json")

def render_status(status):
    """Render terminal UI"""
    # Clear screen (ANSI escape)
    print("\033[2J\033[H", end="")
    
    print("="*70)
    print("🔴 LIVE IMPORT MONITOR — V3.0 PIPELINE (5 DATABASES)")
    print("="*70)
    
    # Status
    s = status.get("status", "unknown")
    status_emoji = {
        "initializing": "⏳",
        "running": "🔴",
        "completed": "✅",
        "failed": "❌"
    }
    print(f"\nStatus:     {status_emoji.get(s, '❓')} {s.upper()}")
    
    # Progress bar
    prog = status.get("progress", {})
    pct = prog.get("percentage", 0)
    bar_width = 50
    filled = int((pct / 100) * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"Progress:   [{bar}] {pct}%")
    print(f"Processed:  {prog.get('processed', 0)} / {prog.get('total', 0)} Paare")
    
    # Performance
    perf = status.get("performance", {})
    print(f"\nSpeed:      {perf.get('current_speed', 0):.1f} Paare/s")
    print(f"Avg Time:   {perf.get('avg_time_per_pair', 0)*1000:.2f} ms/Paar")
    print(f"Elapsed:    {perf.get('elapsed_seconds', 0):.1f}s")
    print(f"ETA:        {perf.get('eta_seconds', 0):.1f}s")
    
    # Database Stats (ALL 5 DBs!)
    db_stats = status.get("db_stats", {})
    print(f"\n📊 DATABASE STATUS (5 V3.0 DBs):")
    print("-"*70)
    print(f"  evoki_v3_core.db:")
    print(f"    • prompt_pairs:     {db_stats.get('prompt_pairs', 0):6}")
    print(f"    • metrics_full:     {db_stats.get('metrics_full', 0):6}")
    print(f"    • b_state_evolution:{db_stats.get('b_state_evolution', 0):6}")
    print(f"    • hazard_events:    {db_stats.get('hazard_events', 0):6}")
    
    print(f"\n  evoki_v3_graph.db:")
    print(f"    • nodes:            {db_stats.get('graph_nodes', 0):6}")
    print(f"    • edges:            {db_stats.get('graph_edges', 0):6}")
    
    print(f"\n  evoki_v3_keywords.db:")
    print(f"    • keywords:         {db_stats.get('keywords', 0):6}")
    
    print(f"\n  evoki_v3_analytics.db:")
    print(f"    • b_vector_verif:   {db_stats.get('b_vector_verifications', 0):6}")
    
    print(f"\n  evoki_v3_trajectories.db:")
    print(f"    • trajectories:     {db_stats.get('metric_trajectories', 0):6}")
    print(f"    • predictions:      {db_stats.get('metric_predictions', 0):6}")
    
    # Errors/Warnings
    errors = status.get("errors", [])
    warnings = status.get("warnings", [])
    print(f"\n{'✅' if len(errors) == 0 else '❌'} Errors:     {len(errors)}")
    print(f"{'✅' if len(warnings) == 0 else '⚠️ '} Warnings:   {len(warnings)}")
    
    if errors:
        print("\n❌ LATEST ERRORS (last 3):")
        for err in errors[-3:]:
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            print(f"   • {msg[:60]}")
    
    # Last Pair Stats
    last = status.get("last_pair", {})
    if last.get("pair_id"):
        print(f"\n📈 Last Pair:  {last.get('pair_id')}")
        print(f"  m1_A:        {last.get('m1_A', 'N/A')}")
        print(f"  hazard:      {last.get('hazard', 'N/A')}")
        print(f"  B_safety:    {last.get('B_safety', 'N/A')}")
    
    # Footer
    print("\n" + "="*70)
    print(f"Last Update: {status.get('last_update', 'N/A')}")
    print("[Auto-refresh: 0.5s] | Ctrl+C to exit")
    print("="*70)

def watch(refresh_interval=0.5):
    """Watch status file and render live"""
    print("🔍 Monitoring V3.0 Pipeline (5 Databases)...")
    print(f"📁 Status file: {STATUS_FILE}")
    print("\nWaiting for pipeline to start...\n")
    
    try:
        while True:
            if STATUS_FILE.exists():
                try:
                    with open(STATUS_FILE, encoding='utf-8') as f:
                        status = json.load(f)
                    
                    render_status(status)
                    
                    # Exit if completed or failed
                    if status.get("status") in ["completed", "failed"]:
                        print("\n✅ Pipeline finished. Exiting monitor.")
                        break
                except json.JSONDecodeError:
                    print("⚠️  Status file corrupted, waiting...")
                except Exception as e:
                    print(f"⚠️  Error reading status: {e}")
            else:
                print("⏳ Waiting for pipeline to start...")
            
            time.sleep(refresh_interval)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitor stopped by user.")

if __name__ == "__main__":
    watch()
