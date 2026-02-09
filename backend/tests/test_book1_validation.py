"""
Book 1 Foundation - Validation Test

Tests m1-m5 gegen Contract ranges.
"""

import sys
sys.path.insert(0, r"C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3")

from calculator_spec_A_PHYS_V11 import (
    compute_m1_A,
    compute_m2_PCI,
    compute_m3_gen_index,
    compute_m4_flow,
    compute_m5_coh
)

def test_m1_A():
    """m1_A: Range [0.0, 1.0]"""
    # Neutral
    m1 = compute_m1_A("Ich habe heute gearbeitet.")
    print(f"m1_A (neutral): {m1}")
    assert 0.0 <= m1 <= 1.0, f"m1_A out of range: {m1}"
    
    # High affect
    m1 = compute_m1_A("Ich bin SO glücklich und aufgeregt!")
    print(f"m1_A (high affect): {m1}")
    assert 0.0 <= m1 <= 1.0, f"m1_A out of range: {m1}"
    
    # Empty
    m1 = compute_m1_A("")
    print(f"m1_A (empty): {m1}")
    assert 0.0 <= m1 <= 1.0, f"m1_A out of range: {m1}"
    
    print("✅ m1_A: PASS")

def test_m2_PCI():
    """m2_PCI: Range [0.0, 1.0]"""
    m2 = compute_m2_PCI("Ich denke über komplexe philosophische Fragen nach.")
    print(f"m2_PCI: {m2}")
    assert 0.0 <= m2 <= 1.0, f"m2_PCI out of range: {m2}"
    print("✅ m2_PCI: PASS")

def test_m3_gen_index():
    """m3_gen_index: Range [0.0, 1.0]"""
    m3 = compute_m3_gen_index(50, 25)
    print(f"m3_gen_index: {m3}")
    assert 0.0 <= m3 <= 1.0, f"m3_gen_index out of range: {m3}"
    print("✅ m3_gen_index: PASS")

def test_m4_flow():
    """m4_flow: Range [0.0, 1.0]"""
    m4 = compute_m4_flow("Ich schreibe einen fließenden Text. Die Gedanken kommen leicht.")
    print(f"m4_flow: {m4}")
    assert 0.0 <= m4 <= 1.0, f"m4_flow out of range: {m4}"
    print("✅ m4_flow: PASS")

def test_m5_coh():
    """m5_coh: Range [0.0, 1.0]"""
    m5 = compute_m5_coh("Das ist ein Test. Der Test läuft gut. Gut ist wichtig.")
    print(f"m5_coh: {m5}")
    assert 0.0 <= m5 <= 1.0, f"m5_coh out of range: {m5}"
    print("✅ m5_coh: PASS")

if __name__ == "__main__":
    print("=" * 50)
    print("BOOK 1 FOUNDATION - VALIDATION TEST")
    print("=" * 50)
    
    test_m1_A()
    test_m2_PCI()
    test_m3_gen_index()
    test_m4_flow()
    test_m5_coh()
    
    print("=" * 50)
    print("✅ ALL BOOK 1 TESTS PASSED!")
    print("=" * 50)
