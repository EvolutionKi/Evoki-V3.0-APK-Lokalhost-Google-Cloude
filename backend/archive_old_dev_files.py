#!/usr/bin/env python3
"""
Archive all files NOT created TODAY (2026-02-08)
Move to _archive_development/
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, date

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
ARCHIVE_DIR = PROJECT_ROOT / "_archive_development"
TODAY = date(2026, 2, 8)

# Directories to check
DOCS_TO_CHECK = [
    PROJECT_ROOT / "*.md",  # Root markdown files
]

# Exclusions (keep these always)
KEEP_ALWAYS = [
    "README.md",
    "ARCHITECTURE.txt",
    "HOW_TO_EVOKI_V3.md",
    "BLUEPRINT_SOVEREIGN_EXTENSION.md",
    ".gitignore",
    ".geminiignore"
]

def is_today_file(file_path: Path) -> bool:
    """Check if file was modified today"""
    try:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime).date()
        return mtime == TODAY
    except:
        return False

def archive_old_files():
    """Archive all files NOT from today"""
    
    print("="*70)
    print("🗑️  ARCHIVING OLD DEVELOPMENT FILES")
    print(f"   Keep only: {TODAY}")
    print("="*70)
    
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    archived_count = 0
    kept_count = 0
    
    # Check root .md files
    for md_file in PROJECT_ROOT.glob("*.md"):
        if md_file.name in KEEP_ALWAYS:
            print(f"✅ KEEP (whitelist): {md_file.name}")
            kept_count += 1
            continue
        
        if is_today_file(md_file):
            print(f"✅ KEEP (today):     {md_file.name}")
            kept_count += 1
        else:
            # Archive it
            dest = ARCHIVE_DIR / md_file.name
            print(f"📦 ARCHIVE:          {md_file.name}")
            shutil.move(str(md_file), str(dest))
            archived_count += 1
    
    print("\n" + "="*70)
    print(f"📊 SUMMARY:")
    print(f"   Kept:     {kept_count} files")
    print(f"   Archived: {archived_count} files")
    print(f"   Archive:  {ARCHIVE_DIR}")
    print("="*70)

if __name__ == "__main__":
    archive_old_files()
