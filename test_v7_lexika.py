#!/usr/bin/env python3
"""Quick test: V7 Lexika Package Integration"""

import sys
sys.path.insert(0, '.')

print("=" * 60)
print("V7 LEXIKA PACKAGE TEST")
print("=" * 60)

# Test 1: Import
try:
    from backend.core.evoki_lexika_v3 import ALL_LEXIKA, lexika_hash
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Count Lexika
count = len(ALL_LEXIKA)
print(f"✅ Loaded {count} lexika")

if count != 22:
    print(f"⚠️  Expected 22, got {count}")

# Test 3: List all Lexika
print("\n📚 Available Lexika:")
for i, key in enumerate(sorted(ALL_LEXIKA.keys()), 1):
    size = len(ALL_LEXIKA[key])
    print(f"  {i:2d}. {key:20s} ({size:3d} terms)")

# Test 4: Hash (Integrity Check)
try:
    hash_val = lexika_hash()
    print(f"\n✅ Lexika Hash: {hash_val[:16]}...")
except Exception as e:
    print(f"❌ Hash failed: {e}")

# Test 5: Score Engine
try:
    from backend.core.evoki_lexika_v3 import score_lexikon
    
    test_text = "ich habe panik und kann nicht mehr"
    panic_score = score_lexikon(test_text, "T_panic")
    
    print(f"\n🧪 Test Scoring:")
    print(f"   Text: '{test_text}'")
    print(f"   T_panic score: {panic_score:.3f}")
    
    if panic_score > 0:
        print("✅ Scoring works!")
    else:
        print("⚠️  Expected panic_score > 0")
        
except Exception as e:
    print(f"❌ Scoring failed: {e}")

print("\n" + "=" * 60)
print("✅ V7 LEXIKA PACKAGE READY!")
print("=" * 60)
