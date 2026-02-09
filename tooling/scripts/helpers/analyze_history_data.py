#!/usr/bin/env python3
"""
Evoki History Data Analyzer
Scans backend/Evoki History directory and generates analysis report.
"""
import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Dynamic project root
EVOKI_ROOT = Path(__file__).resolve().parent.parent.parent.parent
HISTORY_DIR = EVOKI_ROOT / "backend" / "Evoki History" / "2025"
OUTPUT_FILE = EVOKI_ROOT / "tooling" / "data" / "history_analysis_report.json"

def parse_timestamp(line: str):
    """Parse timestamp from format: 'Timestamp: 16.10.2025, 00:16:23 MESZ'"""
    try:
        parts = line.split(": ", 1)[1].strip()
        date_str, time_str = parts.split(", ")
        dt = datetime.strptime(f"{date_str} {time_str.split()[0]}", "%d.%m.%Y %H:%M:%S")
        return dt.isoformat()
    except Exception as e:
        return None

def analyze_prompt_file(filepath: Path):
    """Extract metadata from a single prompt file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        timestamp_line = lines[0] if len(lines) > 0 else ""
        speaker_line = lines[1] if len(lines) > 1 else ""
        content = "".join(lines[3:]) if len(lines) > 3 else ""
        
        timestamp = parse_timestamp(timestamp_line)
        speaker = speaker_line.split(": ", 1)[1].strip() if ": " in speaker_line else "unknown"
        
        return {
            "filepath": str(filepath.relative_to(EVOKI_ROOT)),
            "timestamp": timestamp,
            "speaker": speaker,
            "content_length": len(content),
            "line_count": len(lines)
        }
    except Exception as e:
        return {
            "filepath": str(filepath.relative_to(EVOKI_ROOT)),
            "error": str(e)
        }

def scan_history_directory():
    """Scan entire history directory and collect statistics."""
    print(f"🔍 Scanning: {HISTORY_DIR}")
    
    if not HISTORY_DIR.exists():
        print(f"❌ Directory not found: {HISTORY_DIR}")
        return None
    
    prompt_files = list(HISTORY_DIR.rglob("Prompt*_*.txt"))
    print(f"📂 Found {len(prompt_files)} prompt files")
    
    # Organize data
    user_prompts = []
    ai_responses = []
    errors = []
    stats_by_month = defaultdict(int)
    stats_by_day = defaultdict(int)
    
    for filepath in prompt_files:
        metadata = analyze_prompt_file(filepath)
        
        if "error" in metadata:
            errors.append(metadata)
            continue
        
        if "_user.txt" in filepath.name:
            user_prompts.append(metadata)
        elif "_ai.txt" in filepath.name:
            ai_responses.append(metadata)
        
        # Statistics
        if metadata["timestamp"]:
            month = metadata["timestamp"][:7]  # YYYY-MM
            day = metadata["timestamp"][:10]   # YYYY-MM-DD
            stats_by_month[month] += 1
            stats_by_day[day] += 1
    
    # Date range
    all_timestamps = [p["timestamp"] for p in user_prompts + ai_responses if p["timestamp"]]
    date_range = {
        "earliest": min(all_timestamps) if all_timestamps else None,
        "latest": max(all_timestamps) if all_timestamps else None
    }
    
    # Conversation pairs
    total_pairs = min(len(user_prompts), len(ai_responses))
    
    report = {
        "scan_timestamp": datetime.now().isoformat(),
        "source_directory": str(HISTORY_DIR.relative_to(EVOKI_ROOT)),
        "summary": {
            "total_files": len(prompt_files),
            "user_prompts": len(user_prompts),
            "ai_responses": len(ai_responses),
            "conversation_pairs": total_pairs,
            "errors": len(errors),
            "date_range": date_range
        },
        "statistics": {
            "by_month": dict(sorted(stats_by_month.items())),
            "by_day": dict(sorted(stats_by_day.items()))
        },
        "sample_data": {
            "first_user_prompt": user_prompts[0] if user_prompts else None,
            "first_ai_response": ai_responses[0] if ai_responses else None
        },
        "errors": errors[:10]  # First 10 errors only
    }
    
    return report

def main():
    print("=" * 60)
    print("EVOKI HISTORY DATA ANALYZER")
    print("=" * 60)
    
    report = scan_history_directory()
    
    if report:
        # Save report
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Report saved: {OUTPUT_FILE.relative_to(EVOKI_ROOT)}")
        
        # Print summary
        print("\n📊 SUMMARY:")
        print(f"  Total Files: {report['summary']['total_files']}")
        print(f"  User Prompts: {report['summary']['user_prompts']}")
        print(f"  AI Responses: {report['summary']['ai_responses']}")
        print(f"  Conversation Pairs: {report['summary']['conversation_pairs']}")
        print(f"  Date Range: {report['summary']['date_range']['earliest']} → {report['summary']['date_range']['latest']}")
        if report['summary']['errors']:
            print(f"  ⚠️  Errors: {report['summary']['errors']}")
    else:
        print("❌ Analysis failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
