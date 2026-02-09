"""
Quick Test of Metrics Library Modules
Tests import and basic functionality of extracted metrics
"""

import sys
from pathlib import Path

# Add parent directory to path for metrics_lib import
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Test imports
try:
    from metrics_lib import (
        compute_m1_A,
        compute_m2_PCI,
        compute_m4_flow,
        compute_m5_coh,
        compute_m19_z_prox,
        compute_m101_t_panic,
    )
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test basic calls
test_text = "Ich habe große Angst und Panik. Es fühlt sich unwirklich an."

print("\n📊 Testing metrics...")
print(f"Input: '{test_text}'\n")

try:
    # Test flow and coh (no dependencies)
    flow = compute_m4_flow(test_text)
    coh = compute_m5_coh(test_text)
    print(f"m4_flow: {flow}")
    print(f"m5_coh: {coh}")
    
    # Test trauma (lexikon-based)
    panic = compute_m101_t_panic(test_text)
    print(f"m101_t_panic: {panic}")
    
    # Test core V11.1 (with dependencies)
    pci = compute_m2_PCI(flow=flow, coh=coh, LL=0.3)
    print(f"m2_PCI: {pci}")
    
    A = compute_m1_A(coh=coh, flow=flow, LL=0.3, ZLF=0.2)
    print(f"m1_A: {A}")
    
    # Test safety-critical
    z_prox = compute_m19_z_prox(
        m1_A_lexical=A,
        m15_A_structural=A,
        LL=0.3,
        text=test_text,
        t_panic=panic
    )
    print(f"m19_z_prox (CRITICAL): {z_prox}")
    
    print("\n✅ All metrics calculated successfully!")
    print("\n📚 Metrics Library Test: PASSED! 🎉")

except Exception as e:
    print(f"\n❌ Calculation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
