#!/usr/bin/env python3
"""
Quick Import Test - lexika_complete.py
"""

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("🔍 Testing lexika_complete imports...")

try:
    from backend.core.evoki_lexika_v3.lexika_complete import (
        LEXIKON_T_PANIC,
        LEXIKON_T_DISSO,
        LEXIKON_SUICIDE,
        LEXIKON_AFFEKT_BOOST,
        ALL_LEXIKA
    )
    print("✅ Import SUCCESS!")
    
    # Check lexika counts
    print(f"\n📊 Lexika Statistics:")
    print(f"  T_panic terms: {len(LEXIKON_T_PANIC)}")
    print(f"  T_disso terms: {len(LEXIKON_T_DISSO)}")
    print(f"  Suicide terms: {len(LEXIKON_SUICIDE)}")
    print(f"  Affekt terms: {len(LEXIKON_AFFEKT_BOOST)}")
    print(f"  Total categories: {len(ALL_LEXIKA)}")
    
    # Show some examples
    print(f"\n🔍 Example T_panic terms:")
    for term, weight in list(LEXIKON_T_PANIC.items())[:5]:
        print(f"  '{term}': {weight}")
    
    print(f"\n🔍 Example Suicide terms:")
    for term, weight in list(LEXIKON_SUICIDE.items())[:5]:
        print(f"  '{term}': {weight}")
    
    print("\n🎉 ALL LEXIKA LOADED!")
    
except ImportError as e:
    print(f"❌ Import FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
