#!/usr/bin/env python3
"""
Quick Check: Was fehlt noch für V3 Pipeline?
"""

import sqlite3
from pathlib import Path
import json

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")

print("="*70)
print("🔍 EVOKI V3.0 — QUICK STATUS CHECK")
print("="*70)

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 1: Databases
# ═══════════════════════════════════════════════════════════════════════════

db_checks = {
    "evoki_v3_core.db": PROJECT_ROOT / "backend/data/databases/evoki_v3_core.db",
    "evoki_metadata.db": PROJECT_ROOT / "evoki_metadata.db",
    "evoki_resonance.db": PROJECT_ROOT / "evoki_resonance.db",
}

print("\n📊 DATABASE CHECK:")
print("-"*70)

for name, path in db_checks.items():
    exists = path.exists()
    status = "✅ EXISTS" if exists else "❌ MISSING"
    
    if exists:
        try:
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            
            # Try to count pairs
            try:
                cur.execute("SELECT COUNT(*) FROM prompt_pairs")
                count = cur.fetchone()[0]
                print(f"{status:12} | {name:25} | {count:6} pairs")
            except:
                print(f"{status:12} | {name:25} | (no pairs table)")
            
            conn.close()
        except Exception as e:
            print(f"{status:12} | {name:25} | ERROR: {e}")
    else:
        print(f"{status:12} | {name:25}")

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 2: History Files
# ═══════════════════════════════════════════════════════════════════════════

print("\n📂 HISTORY FILES CHECK:")
print("-"*70)

history_root = PROJECT_ROOT / "backend/Evoki History"
if history_root.exists():
    txt_files = list(history_root.rglob("*.txt"))
    print(f"✅ History folder exists: {len(txt_files)} .txt files found")
    
    # Show first few
    for f in txt_files[:3]:
        rel_path = f.relative_to(history_root)
        print(f"   📄 {rel_path}")
    
    if len(txt_files) > 3:
        print(f"   ... and {len(txt_files) - 3} more")
else:
    print("❌ History folder NOT found")

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 3: Test Data
# ═══════════════════════════════════════════════════════════════════════════

print("\n🧪 TEST DATA CHECK:")
print("-"*70)

test_data_locations = [
    PROJECT_ROOT / "backend/data/test_1000_pairs.json",
    PROJECT_ROOT / "backend/test_data/1000_pairs/pairs.json",
]

test_data_found = None
for path in test_data_locations:
    if path.exists():
        try:
            with open(path) as f:
                data = json.load(f)
            print(f"✅ Test data found: {path.name}")
            print(f"   📊 {len(data)} pairs")
            test_data_found = path
            break
        except Exception as e:
            print(f"⚠️  File exists but can't parse: {e}")

if not test_data_found:
    print("❌ No test data JSON found")
    print("   💡 Need to create: backend/data/test_1000_pairs.json")

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 4: Scripts
# ═══════════════════════════════════════════════════════════════════════════

print("\n📜 SCRIPT CHECK:")
print("-"*70)

scripts = {
    "Master Pipeline": PROJECT_ROOT / "backend/v3_pipeline_master.py",
    "Watch Monitor": PROJECT_ROOT / "backend/scripts/watch_pipeline.py",
    "Validation": PROJECT_ROOT / "backend/scripts/validate_import.py",
}

for name, path in scripts.items():
    exists = path.exists()
    status = "✅ EXISTS" if exists else "❌ MISSING"
    print(f"{status:12} | {name}")

# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📋 SUMMARY — WHAT'S MISSING?")
print("="*70)

missing = []

# Check if we have data source
if test_data_found:
    print("✅ Test data available")
else:
    has_db_with_data = any([
        path.exists() and sqlite3.connect(path).execute("SELECT COUNT(*) FROM prompt_pairs").fetchone()[0] > 0
        for path in [PROJECT_ROOT / "evoki_metadata.db"]
        if path.exists()
    ])
    
    has_history = history_root.exists() and len(list(history_root.rglob("*.txt"))) > 0
    
    if has_db_with_data:
        print("⚠️  No test JSON, but DB has data → can extract!")
        missing.append("Extract 1000 pairs to JSON")
    elif has_history:
        print("⚠️  No test JSON, but History files exist → can import!")
        missing.append("Import 1000 pairs from History")
    else:
        print("❌ No data source found!")
        missing.append("FIND DATA SOURCE")

# Check scripts
if not (PROJECT_ROOT / "backend/scripts/watch_pipeline.py").exists():
    missing.append("Create watch_pipeline.py")

if not (PROJECT_ROOT / "backend/scripts/validate_import.py").exists():
    missing.append("Create validate_import.py")

if missing:
    print("\n🔧 TODO:")
    for i, item in enumerate(missing, 1):
        print(f"   {i}. {item}")
else:
    print("\n✅✅✅ EVERYTHING READY! ✅✅✅")
    print("\n🚀 Ready to run:")
    print("   python backend/v3_pipeline_master.py --test --limit 1000")

print("="*70)
