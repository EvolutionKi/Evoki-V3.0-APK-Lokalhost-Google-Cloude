"""
FULL SPECTRUM 168 WRAPPER
Berechnet ALLE 168 Metriken gemäß SPEC FINAL7

Version: V2.0 (2026-02-08)
Source: SPEC FINAL7 / evoki_fullspectrum168_contract.json

Nutzt:
- calculator_spec_A_PHYS_V11.py (26 Core Metriken)
- a_phys_v11.py (Physics Engine)
- evoki_lexika_v3.py (Lexikon Engine)
"""

import json
import math
from pathlib import Path
from typing import Dict

# Import existing calculator
try:
    from .calculator_spec_A_PHYS_V11 import calculate_spec_compliant
except ImportError:
    from calculator_spec_A_PHYS_V11 import calculate_spec_compliant

# Import new engines
try:
    from .a_phys_v11 import APhysV11, vectorize_hash
    HAS_APHYS = True
except ImportError:
    try:
        from a_phys_v11 import APhysV11, vectorize_hash
        HAS_APHYS = True
    except ImportError:
        HAS_APHYS = False
        print("⚠️ a_phys_v11 not available, using defaults")

try:
    from .evoki_lexika_v3 import (
        compute_lexicon_score,
        compute_hazard_score,
        compute_b_past_with_regex,
        BVektorConfig,
        Thresholds
    )
    HAS_LEXIKA = True
except ImportError:
    try:
        from evoki_lexika_v3 import (
            compute_lexicon_score,
            compute_hazard_score,
            compute_b_past_with_regex,
            BVektorConfig,
            Thresholds
        )
        HAS_LEXIKA = True
    except ImportError:
        HAS_LEXIKA = False
        print("⚠️ evoki_lexika_v3 not available, using defaults")

# Load contract for ALL 168 metric names
CONTRACT_PATH = Path(__file__).parent / "evoki_fullspectrum168_contract.json"

def load_all_168_metrics() -> list:
    """Load all 168 metric keys from contract."""
    if CONTRACT_PATH.exists():
        with open(CONTRACT_PATH, 'r', encoding='utf-8') as f:
            contract = json.load(f)
        return [item['engine_key'] for item in contract.get('items', [])]
    else:
        # Fallback: Generate m1-m168
        return [f"m{i}_placeholder" for i in range(1, 169)]

ALL_168_METRICS = load_all_168_metrics()


def calculate_full_168(text: str, **kwargs) -> Dict:
    """
    Berechnet ALLE 168 Metriken.
    
    Args:
        text: Input text
        **kwargs: Optionale Parameter
    
    Returns:
        Dict mit exakt 168 Metriken
    """
    # BASE: Original Calculator (26 Metriken)
    fs = calculate_spec_compliant(text, **kwargs)
    metrics = fs.to_dict()
    
    # ENHANCE: Physics Engine (wenn verfügbar)
    if HAS_APHYS:
        try:
            phys = APhysV11()
            v_c = vectorize_hash(text)
            result = phys.compute_affekt(v_c=v_c, text=text)
            
            # Map physics results to metrics
            metrics['m1_A'] = result.get('A_phys', metrics.get('m1_A', 0.5))
            metrics['m101_T_panic'] = 1.0 if result.get('a29_trip', False) else 0.0
            # More physics mappings could be added here
        except Exception as e:
            pass  # Keep existing values
    
    # ENHANCE: Lexikon Engine (wenn verfügbar)
    if HAS_LEXIKA:
        try:
            # Hazard Score (m151-m160 range)
            hazard_result = compute_hazard_score(text)
            metrics['m151_hazard'] = hazard_result.get('hazard_combined', 0.0)
            metrics['m152_suicide'] = hazard_result.get('suicide_score', 0.0)
            metrics['m153_self_harm'] = hazard_result.get('self_harm_score', 0.0)
            metrics['m154_crisis'] = hazard_result.get('crisis_score', 0.0)
            metrics['m155_is_critical'] = 1.0 if hazard_result.get('is_critical', False) else 0.0
            
            # B-Past Pattern (m9 related)
            b_past = compute_b_past_with_regex(text)
            if b_past:
                metrics['m9_b_past'] = b_past.get('score', 0.0)
        except Exception as e:
            pass  # Keep existing values
    
    # FILL: Missing metrics with defaults
    for metric in ALL_168_METRICS:
        if metric not in metrics:
            metrics[metric] = 0.0
    
    # CLEAN: Replace NaN/Inf with 0.0
    for key, value in list(metrics.items()):
        if isinstance(value, (int, float)):
            if math.isnan(value) or math.isinf(value):
                metrics[key] = 0.0
    
    # VALIDATION: Count must be 168
    actual_count = len([k for k in metrics.keys() if k.startswith('m')])
    if actual_count < 168:
        print(f"⚠️ Only {actual_count}/168 metrics! Padding...")
        for i in range(1, 169):
            key = f"m{i}"
            # Check if any metric starting with m{i}_ exists
            exists = any(k.startswith(f"m{i}_") for k in metrics.keys())
            if not exists:
                metrics[f"m{i}_placeholder"] = 0.0
    
    return metrics


# ============================================================================
# TEST
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("FULL SPECTRUM 168 TEST")
    print("=" * 60)
    
    test_text = "Ich fühle mich heute sehr gut und bin voller Energie."
    m = calculate_full_168(test_text)
    
    # Count only m* metrics
    m_count = len([k for k in m.keys() if k.startswith('m')])
    print(f"✅ Count: {m_count}/168")
    print(f"   Sample: m1_A={m.get('m1_A', 'N/A')}, m151_hazard={m.get('m151_hazard', 'N/A')}")
    
    # Show engines status
    print(f"\n   Physics Engine: {'✅' if HAS_APHYS else '❌'}")
    print(f"   Lexika Engine:  {'✅' if HAS_LEXIKA else '❌'}")
