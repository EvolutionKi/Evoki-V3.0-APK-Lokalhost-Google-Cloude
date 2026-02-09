#!/usr/bin/env python3
"""
Extract 1000 pairs from 2025 History for MVP testing
"""

import os
import re
from pathlib import Path
from typing import List, Tuple
import json

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
HISTORY_ROOT = PROJECT_ROOT / "backend/Evoki History/2025"
OUTPUT_JSON = PROJECT_ROOT / "backend/data/test_1000_pairs_2025.json"

def parse_filename(filename: str) -> Tuple[str, int, str]:
    """
    Parse filename like: Prompt10_user.txt or Prompt10_ai.txt
    Returns: (role, prompt_num, filename)
    """
    match = re.match(r'Prompt(\d+)_(user|ai)\.txt', filename)
    if match:
        prompt_num = int(match.group(1))
        role = match.group(2)
        return (role, prompt_num, filename)
    return None

def scan_2025_history() -> List[Tuple[Path, str, int, str]]:
    """
    Scan 2025 history and find all prompt files
    Returns: [(file_path, date_folder, prompt_num, role), ...]
    """
    files = []
    
    if not HISTORY_ROOT.exists():
        print(f"❌ History root not found: {HISTORY_ROOT}")
        return []
    
    # Scan all subdirectories (MM/DD/)
    for month_dir in HISTORY_ROOT.iterdir():
        if not month_dir.is_dir():
            continue
        
        for day_dir in month_dir.iterdir():
            if not day_dir.is_dir():
                continue
            
            date_folder = f"2025/{month_dir.name}/{day_dir.name}"
            
            # Find all prompt files
            for txt_file in day_dir.glob("Prompt*_*.txt"):
                parsed = parse_filename(txt_file.name)
                if parsed:
                    role, prompt_num, _ = parsed
                    files.append((txt_file, date_folder, prompt_num, role))
    
    return sorted(files, key=lambda x: (x[1], x[2], x[3]))  # Sort by date, prompt_num, role

def extract_pairs(limit: int = 1000) -> List[dict]:
    """
    Extract prompt pairs (user + ai) as JSON objects
    """
    all_files = scan_2025_history()
    
    print(f"📂 Found {len(all_files)} total files in 2025 history")
    
    # Group by (date_folder, prompt_num)
    pairs_dict = {}
    
    for file_path, date_folder, prompt_num, role in all_files:
        key = (date_folder, prompt_num)
        
        if key not in pairs_dict:
            pairs_dict[key] = {"user": None, "ai": None, "date": date_folder, "num": prompt_num}
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
            pairs_dict[key][role] = content
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    # Convert to list of complete pairs (both user AND ai exist)
    complete_pairs = []
    
    for (date_folder, prompt_num), data in sorted(pairs_dict.items()):
        if data["user"] and data["ai"]:  # Both exist
            complete_pairs.append({
                "pair_id": f"pair_{date_folder.replace('/', '_')}_{prompt_num:04d}",
                "session_id": f"session_{date_folder.replace('/', '_')}",
                "date_folder": date_folder,
                "prompt_num": prompt_num,
                "user_text": data["user"],
                "ai_text": data["ai"]
            })
        
        if len(complete_pairs) >= limit:
            break
    
    return complete_pairs[:limit]

def save_to_json(pairs: List[dict]):
    """Save pairs to JSON"""
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(pairs, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(pairs)} pairs to: {OUTPUT_JSON}")

if __name__ == "__main__":
    print("="*70)
    print("📤 EXTRACTING 1000 PAIRS FROM 2025 HISTORY")
    print("="*70)
    
    pairs = extract_pairs(limit=1000)
    
    if pairs:
        save_to_json(pairs)
        
        # Print sample
        print(f"\n📊 Sample (first pair):")
        print(f"   ID:   {pairs[0]['pair_id']}")
        print(f"   User: {pairs[0]['user_text'][:60]}...")
        print(f"   AI:   {pairs[0]['ai_text'][:60]}...")
    else:
        print("\n❌ No pairs found!")
    
    print("="*70)
