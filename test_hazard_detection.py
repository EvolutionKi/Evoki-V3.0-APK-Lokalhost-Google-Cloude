#!/usr/bin/env python3
"""
Test m151_hazard function with Lexika integration
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

# Import lexika
from backend.core.evoki_lexika_v3.lexika_complete import HazardLexika, TraumaLexika
from backend.core.evoki_metrics_v3.calculator_trauma_lexika import (
    compute_m151_hazard,
    compute_m101_t_panic,
    compute_m102_t_disso,
    compute_m103_t_integ
)

def test_hazard_detection():
    """Test hazard detection on critical scenarios"""
    
    test_cases = [
        ("Ich will sterben", "Should detect SUICIDE"),
        ("Ich will mich umbringen", "Should detect SUICIDE"),
        ("Es gibt keinen Ausweg mehr", "Should detect CRISIS"),
        ("Ich fühle mich gut", "Should be LOW"),
        ("Hilfe ich habe Panik", "Should detect PANIC but not suicide"),
        ("Ritzen hilft mir", "Should detect SELF-HARM"),
    ]
    
    print("🔍 TESTING m151_hazard (Guardian Hazard Score)\n")
    print("=" * 80)
    
    for text, expected in test_cases:
        hazard = compute_m151_hazard(text)
        panic = compute_m101_t_panic(text)
        
        symbol = "🚨" if hazard > 0.5 else ("⚠️" if hazard > 0.2 else "✅")
        
        print(f"\n{symbol} Text: \"{text}\"")
        print(f"   Hazard: {hazard:.3f}  |  Panic: {panic:.3f}")
        print(f"   Expected: {expected}")
        
        # Verify
        if "SUICIDE" in expected and hazard < 0.5:
            print(f"   ❌ FAIL: Should be >= 0.5!")
        elif "CRISIS" in expected and hazard < 0.3:
            print(f"   ❌ FAIL: Should be >= 0.3!")
        elif "LOW" in expected and hazard > 0.2:
            print(f"   ❌ FAIL: Should be < 0.2!")
        else:
            print(f"   ✅ PASS")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_hazard_detection()
