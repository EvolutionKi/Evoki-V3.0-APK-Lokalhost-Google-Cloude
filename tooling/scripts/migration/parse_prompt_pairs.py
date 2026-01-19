#!/usr/bin/env python3
"""
Prompt Pair Parser - Phase 2.1
Parses 21,987 text files into structured JSONL format.
"""
import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib

# Dynamic project root
EVOKI_ROOT = Path(__file__).resolve().parent.parent.parent.parent
HISTORY_DIR = EVOKI_ROOT / "backend" / "Evoki History" / "2025"
OUTPUT_FILE = EVOKI_ROOT / "tooling" / "data" / "parsed_conversations.jsonl"

def parse_timestamp(line: str):
    """Parse timestamp from format: 'Timestamp: 16.10.2025, 00:16:23 MESZ'"""
    try:
        parts = line.split(": ", 1)[1].strip()
        date_str, time_str = parts.split(", ")
        dt = datetime.strptime(f"{date_str} {time_str.split()[0]}", "%d.%m.%Y %H:%M:%S")
        return dt.isoformat()
    except Exception as e:
        return None

def generate_chunk_id(session_id: str, sequence: int):
    """Generate unique chunk ID: session-XXX"""
    return f"{session_id}-{sequence:03d}"

def parse_prompt_file(filepath: Path):
    """Extract all data from a single prompt file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        timestamp_line = lines[0] if len(lines) > 0 else ""
        speaker_line = lines[1] if len(lines) > 1 else ""
        content = "".join(lines[3:]).strip() if len(lines) > 3 else ""
        
        timestamp = parse_timestamp(timestamp_line)
        speaker = speaker_line.split(": ", 1)[1].strip() if ": " in speaker_line else "unknown"
        
        return {
            "timestamp": timestamp,
            "speaker": speaker,
            "text": content,
            "text_length": len(content)
        }
    except Exception as e:
        return None

def pair_prompts(history_dir: Path):
    """
    Scan directory and pair PromptN_user.txt with PromptN_ai.txt.
    Returns list of conversation pairs grouped by session.
    """
    print(f"🔍 Scanning: {history_dir}")
    
    # Organize files by date and prompt number
    files_by_date = defaultdict(lambda: defaultdict(dict))
    
    for filepath in history_dir.rglob("Prompt*_*.txt"):
        # Extract: 2025/MM/DD/PromptN_speaker.txt
        parts = filepath.parts
        month = parts[-3]
        day = parts[-2]
        filename = filepath.name
        
        # Parse filename: PromptN_user.txt or PromptN_ai.txt
        if "_user.txt" in filename:
            prompt_num = filename.replace("_user.txt", "").replace("Prompt", "")
            speaker = "user"
        elif "_ai.txt" in filename:
            prompt_num = filename.replace("_ai.txt", "").replace("Prompt", "")
            speaker = "ai"
        else:
            continue
        
        session_id = f"2025-{month}-{day}"
        files_by_date[session_id][prompt_num][speaker] = filepath
    
    # Create pairs
    pairs = []
    total_sessions = 0
    total_pairs = 0
    
    for session_id in sorted(files_by_date.keys()):
        session_prompts = files_by_date[session_id]
        total_sessions += 1
        
        for prompt_num in sorted(session_prompts.keys(), key=lambda x: int(x)):
            prompt_files = session_prompts[prompt_num]
            
            # Must have both user and ai
            if "user" not in prompt_files or "ai" not in prompt_files:
                print(f"⚠️  Incomplete pair: {session_id} Prompt{prompt_num}")
                continue
            
            user_data = parse_prompt_file(prompt_files["user"])
            ai_data = parse_prompt_file(prompt_files["ai"])
            
            if not user_data or not ai_data:
                print(f"⚠️  Parse error: {session_id} Prompt{prompt_num}")
                continue
            
            # Generate chunk IDs
            user_chunk_id = generate_chunk_id(session_id, (int(prompt_num) * 2) - 1)
            ai_chunk_id = generate_chunk_id(session_id, int(prompt_num) * 2)
            
            # Create paired record
            pair = {
                "session_id": session_id,
                "prompt_number": int(prompt_num),
                "user": {
                    "chunk_id": user_chunk_id,
                    "timestamp": user_data["timestamp"],
                    "text": user_data["text"],
                    "text_length": user_data["text_length"]
                },
                "ai": {
                    "chunk_id": ai_chunk_id,
                    "timestamp": ai_data["timestamp"],
                    "text": ai_data["text"],
                    "text_length": ai_data["text_length"]
                }
            }
            
            pairs.append(pair)
            total_pairs += 1
    
    print(f"\n✅ Parsed:")
    print(f"   Sessions: {total_sessions}")
    print(f"   Pairs: {total_pairs}")
    
    return pairs

def save_jsonl(pairs, output_file: Path):
    """Save pairs to JSONL file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + '\n')
    
    print(f"\n💾 Saved: {output_file.relative_to(EVOKI_ROOT)}")
    print(f"   Lines: {len(pairs)}")

def main():
    print("=" * 60)
    print("PROMPT PAIR PARSER - PHASE 2.1")
    print("=" * 60)
    
    if not HISTORY_DIR.exists():
        print(f"❌ Directory not found: {HISTORY_DIR}")
        return 1
    
    # Parse all pairs
    pairs = pair_prompts(HISTORY_DIR)
    
    if not pairs:
        print("❌ No pairs found!")
        return 1
    
    # Save to JSONL
    save_jsonl(pairs, OUTPUT_FILE)
    
    # Statistics
    total_user_chars = sum(p["user"]["text_length"] for p in pairs)
    total_ai_chars = sum(p["ai"]["text_length"] for p in pairs)
    
    print(f"\n📊 STATISTICS:")
    print(f"   Total pairs: {len(pairs)}")
    print(f"   User text: {total_user_chars:,} chars ({total_user_chars/len(pairs):.1f} avg)")
    print(f"   AI text: {total_ai_chars:,} chars ({total_ai_chars/len(pairs):.1f} avg)")
    print(f"   Total: {total_user_chars + total_ai_chars:,} chars")
    
    return 0

if __name__ == "__main__":
    exit(main())
