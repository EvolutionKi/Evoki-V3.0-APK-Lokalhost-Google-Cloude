#!/usr/bin/env python3
"""
Quick Import Test - calculator_spec_A_PHYS_V11.py
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("🔍 Testing calculator_spec imports...")

try:
    from backend.core.evoki_metrics_v3.calculator_spec_A_PHYS_V11 import (
        compute_m1_A,
        compute_m101_t_panic,
        compute_m19_z_prox,
        compute_m161_commit
    )
    print("✅ Import SUCCESS!")
    
    # Test m1_A
    result = compute_m1_A("Hello World")
    print(f"✅ m1_A('Hello World') = {result}")
    
    # Test t_panic
    panic = compute_m101_t_panic("Ich habe Panik und kann nicht mehr!")
    print(f"✅ m101_t_panic = {panic}")
    
    # Test z_prox
    z = compute_m19_z_prox(0.3, 0.3, 0.8, "test", 0.5)
    print(f"✅ m19_z_prox = {z}")
    
    # Test commit
    commit = compute_m161_commit(z, 0.6)
    print(f"✅ m161_commit = {commit}")
    
    print("\n🎉 ALL TESTS PASSED!")
    
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
