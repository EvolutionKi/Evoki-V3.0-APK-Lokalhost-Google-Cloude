"""
T2 HISTORY IMPORT - DRY RUN (1000 Paare)
==========================================

Simplified import with limit for testing.
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add V7 script path
v7_path = Path(r"C:\Users\nicom\Downloads\EVOKI_V3_METRICS_SPECIFICATION Entwicklung\V7 Patchpaket V2 + Monolith")
sys.path.insert(0, str(v7_path))

from evoki_history_ingest import parse_prompt_file, iter_history_files

def dry_run_sample(history_root: str, max_turns: int = 2000):
    """
    Dry run: Scan and validate files without writing DB
    
    Args:
        history_root: Path to Evoki History
        max_turns: Maximum turns to process (2000 = 1000 pairs)
    """
    root = Path(history_root)
    
    print("="*80)
    print(f"DRY RUN: First {max_turns} turns ({max_turns//2} pairs)")
    print("="*80)
    print()
    
    # Scan files
    print("📂 Scanning files...")
    files = sorted(
        list(iter_history_files(root)),
        key=lambda t: (t[0], t[1], t[2], t[3], str(t[4]).lower())
    )
    
    print(f"✅ Found {len(files)} total files")
    print(f"   Processing first {min(max_turns, len(files))} files")
    print()
    
    # Sample first N
    sample = files[:max_turns]
    
    # Parse and validate
    print("🔍 Validating sample...")
    print()
    
    valid_count = 0
    error_count = 0
    
    for i, (yyyy, mm, dd, prompt_num, path) in enumerate(sample):
        try:
            parsed = parse_prompt_file(path)
            
            # Validate
            if not parsed['ts_iso']:
                print(f"⚠️  [{i+1:4d}] No timestamp: {path.name}")
                error_count += 1
                continue
            
            if not parsed['role'] in ['user', 'ai', 'assistant']:
                print(f"⚠️  [{i+1:4d}] Invalid role '{parsed['role']}': {path.name}")
                error_count += 1
                continue
            
            if len(parsed['text']) < 5:
                print(f"⚠️  [{i+1:4d}] Text too short ({len(parsed['text'])}): {path.name}")
                error_count += 1
                continue
            
            valid_count += 1
            
            # Progress
            if (i + 1) % 100 == 0:
                print(f"✅ [{i+1:4d}/{max_turns}] Valid: {valid_count}, Errors: {error_count}")
        
        except Exception as e:
            print(f"❌ [{i+1:4d}] Parse error: {path.name} - {e}")
            error_count += 1
    
    print()
    print("="*80)
    print("DRY RUN SUMMARY")
    print("="*80)
    print(f"Total scanned:  {len(files):,} files")
    print(f"Sample size:    {len(sample):,} files")
    print(f"Valid:          {valid_count:,} ({valid_count/len(sample)*100:.1f}%)")
    print(f"Errors:         {error_count:,} ({error_count/len(sample)*100:.1f}%)")
    print()
    
    if error_count > 0:
        print(f"⚠️  Found {error_count} errors - check logs above")
    else:
        print(f"✅ All {valid_count} files valid!")
    
    print()
    print(f"📊 Estimated full import:")
    print(f"   Total files: {len(files):,}")
    print(f"   Pairs (user+ai): ~{len(files)//2:,}")
    print(f"   Error rate: {error_count/len(sample)*100:.2f}%")
    print(f"   Expected valid: ~{int(len(files) * (valid_count/len(sample))):,}")
    print()
    
    return valid_count, error_count


if __name__ == "__main__":
    history_root = r"C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\Evoki History"
    
    print(f"History root: {history_root}")
    print()
    
    valid, errors =dry_run_sample(history_root, max_turns=2000)
    
    print()
    print("✅ DRY RUN COMPLETE")
    
    if errors == 0:
        print("   Ready for full import!")
    else:
        print(f"   Fix {errors} errors before full import")
