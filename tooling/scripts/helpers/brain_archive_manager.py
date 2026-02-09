# Brain Archive Manager
# Automatically sorts old .resolved files by type instead of deleting

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

BRAIN_ROOT = Path(r"C:\Users\nicom\.gemini\antigravity\brain")
ARCHIVE_ROOT = Path(r"C:\Users\nicom\.gemini\antigravity\_brain_archive")

def setup_archive_structure():
    """Create archive folder structure"""
    archive_dirs = [
        ARCHIVE_ROOT / "resolved_artifacts",
        ARCHIVE_ROOT / "resolved_artifacts" / "todos",
        ARCHIVE_ROOT / "resolved_artifacts" / "plans",
        ARCHIVE_ROOT / "resolved_artifacts" / "mappings",
        ARCHIVE_ROOT / "resolved_artifacts" / "analyses",
        ARCHIVE_ROOT / "resolved_artifacts" / "walkthroughs",
        ARCHIVE_ROOT / "screenshots",
        ARCHIVE_ROOT / "metadata",
        ARCHIVE_ROOT / "other"
    ]
    
    for dir_path in archive_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Archive structure created at {ARCHIVE_ROOT}")


def categorize_file(filename: str) -> str:
    """Determine archive category for file"""
    lower = filename.lower()
    
    if "todo" in lower or "task" in lower:
        return "todos"
    elif "plan" in lower or "implementation" in lower:
        return "plans"
    elif "mapping" in lower or "module" in lower:
        return "mappings"
    elif "analysis" in lower or "vector" in lower:
        return "analyses"
    elif "walkthrough" in lower or "guide" in lower:
        return "walkthroughs"
    elif filename.endswith(('.webp', '.png', '.jpg', '.jpeg')):
        return "screenshots"
    elif filename.endswith('.metadata.json'):
        return "metadata"
    else:
        return "other"


def archive_conversation_artifacts(conversation_id: str, dry_run: bool = True):
    """
    Archive old .resolved files from a conversation
    
    Args:
        conversation_id: The conversation UUID
        dry_run: If True, only shows what would be archived
    """
    conv_path = BRAIN_ROOT / conversation_id
    
    if not conv_path.exists():
        print(f"❌ Conversation not found: {conversation_id}")
        return
    
    # Find all .resolved files
    resolved_files = list(conv_path.glob("*.resolved*"))
    
    if not resolved_files:
        print(f"✅ No .resolved files to archive in {conversation_id}")
        return
    
    print(f"\n📦 Found {len(resolved_files)} .resolved files in conversation {conversation_id}")
    
    archive_manifest = {
        "conversation_id": conversation_id,
        "archived_at": datetime.now().isoformat(),
        "files": []
    }
    
    for file_path in resolved_files:
        category = categorize_file(file_path.name)
        
        # Create timestamped filename to avoid collisions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{conversation_id[:8]}_{timestamp}_{file_path.name}"
        
        target_dir = ARCHIVE_ROOT / "resolved_artifacts" / category
        target_path = target_dir / new_name
        
        file_info = {
            "original_path": str(file_path),
            "archive_path": str(target_path),
            "category": category,
            "size_bytes": file_path.stat().st_size,
            "original_name": file_path.name
        }
        
        archive_manifest["files"].append(file_info)
        
        if dry_run:
            print(f"   [{category:12s}] {file_path.name:40s} → {new_name}")
        else:
            shutil.move(str(file_path), str(target_path))
            print(f"   ✅ Moved: {file_path.name} → {category}/{new_name}")
    
    # Save manifest
    if not dry_run:
        manifest_path = ARCHIVE_ROOT / "metadata" / f"{conversation_id}_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(archive_manifest, f, indent=2)
        print(f"\n✅ Manifest saved: {manifest_path}")
    else:
        print(f"\n🔍 DRY RUN - No files moved. Run with dry_run=False to execute.")
    
    # Summary
    total_size = sum(f["size_bytes"] for f in archive_manifest["files"])
    print(f"\n📊 Summary:")
    print(f"   Files: {len(resolved_files)}")
    print(f"   Total size: {total_size / 1024 / 1024:.2f} MB")
    
    return archive_manifest


def archive_all_conversations(dry_run: bool = True):
    """Archive .resolved files from ALL conversations"""
    
    if not BRAIN_ROOT.exists():
        print(f"❌ Brain root not found: {BRAIN_ROOT}")
        return
    
    conversations = [d for d in BRAIN_ROOT.iterdir() if d.is_dir()]
    
    print(f"🔍 Scanning {len(conversations)} conversations...")
    
    total_files = 0
    total_size = 0
    
    for conv_path in conversations:
        manifest = archive_conversation_artifacts(conv_path.name, dry_run=dry_run)
        if manifest:
            total_files += len(manifest["files"])
            total_size += sum(f["size_bytes"] for f in manifest["files"])
    
    print(f"\n" + "="*80)
    print(f"📊 TOTAL SUMMARY")
    print(f"="*80)
    print(f"   Conversations scanned: {len(conversations)}")
    print(f"   Files to archive: {total_files}")
    print(f"   Total size: {total_size / 1024 / 1024 / 1024:.2f} GB")
    
    if dry_run:
        print(f"\n⚠️  This was a DRY RUN. No files were moved.")
        print(f"   Run with dry_run=False to execute the archival.")


def restore_from_archive(conversation_id: str, category: str = None):
    """Restore archived files back to brain"""
    manifest_path = ARCHIVE_ROOT / "metadata" / f"{conversation_id}_manifest.json"
    
    if not manifest_path.exists():
        print(f"❌ No archive manifest found for {conversation_id}")
        return
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    conv_path = BRAIN_ROOT / conversation_id
    conv_path.mkdir(parents=True, exist_ok=True)
    
    for file_info in manifest["files"]:
        if category and file_info["category"] != category:
            continue
        
        archive_path = Path(file_info["archive_path"])
        original_name = file_info["original_name"]
        restore_path = conv_path / original_name
        
        if archive_path.exists():
            shutil.copy2(str(archive_path), str(restore_path))
            print(f"✅ Restored: {original_name}")
        else:
            print(f"⚠️  Archive file not found: {archive_path}")


if __name__ == "__main__":
    import sys
    
    print("="*80)
    print("BRAIN ARCHIVE MANAGER")
    print("="*80)
    print()
    
    # Setup archive structure
    setup_archive_structure()
    print()
    
    # Example usage
    if len(sys.argv) > 1:
        conv_id = sys.argv[1]
        dry_run = "--execute" not in sys.argv
        
        print(f"📦 Archiving conversation: {conv_id}")
        print(f"   Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        print()
        
        archive_conversation_artifacts(conv_id, dry_run=dry_run)
    else:
        print("Usage:")
        print("  python brain_archive_manager.py <conversation_id> [--execute]")
        print()
        print("  --execute: Actually move files (without it, just shows what would happen)")
        print()
        print("Examples:")
        print("  # Dry run (preview only)")
        print("  python brain_archive_manager.py 20da9c61-ddf1-40da-83f1-48057400bf78")
        print()
        print("  # Actually archive")
        print("  python brain_archive_manager.py 20da9c61-ddf1-40da-83f1-48057400bf78 --execute")
        print()
        print("  # Archive ALL conversations (DRY RUN)")
        print("  # Comment out the if/else and call archive_all_conversations(dry_run=True)")
