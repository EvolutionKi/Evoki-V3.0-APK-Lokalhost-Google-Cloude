"""
m19_z_prox: Z-Proximity (Death Proximity) ⚠️ CRITICAL SAFETY METRIC!

SPEC V3.0.3 + V3.3.2 + V3.3.3 Safety Override:
    effective_A = min(m1_A_lexical, m15_A_structural)
    base_prox = (1 - effective_A) × LL
    z_prox = min(1.0, base_prox × (1 + hazard_bonus))
    
    SAFETY OVERRIDE (V3.3.3):
    - If t_panic > 0.7 → z_prox minimum 0.65 (ALERT zone)
    - If t_panic > 0.5 → z_prox minimum 0.50 (WARN zone)
    - Direct crisis words ("suizid", "umbringen") → minimum 0.55

This is the MOST CRITICAL safety metric - triggers interventions!

Reference: EVOKI_V3_METRICS_SPECIFICATION.md:3078-3143
"""

from typing import Dict
from ._helpers import clamp

# Hazard Lexikon (safety-critical!)
HAZARD_LEXIKON = {
    "suicide": 0.25, "suizid": 0.25, "umbringen": 0.20, "sterben":  0.15,
    "ritzen": 0.15, "schneiden": 0.10, "verletzen": 0.10,
}


def compute_m19_z_prox(
    m1_A_lexical: float,
    m15_A_structural: float,
    LL: float,
    text: str,
    t_panic: float = 0.0
) -> float:
    """
    Calculate m19_z_prox (Death Proximity) ⚠️ CRITICAL!
    
    Args:
        m1_A_lexical: Lexical affekt score [0,1]
        m15_A_structural: Structural affekt score [0,1]
        LL: Lambert-Light turbidity [0,1] (m7_LL)
        text: Input text (for hazard detection)
        t_panic: Panic level [0,1] (m101_t_panic, optional)
    
    Returns:
        z_prox score [0, 1] - Death proximity (HIGHER = MORE DANGER!)
    """
    # Safety First: Use LOWER (worse) affekt value
    effective_A = min(m1_A_lexical, m15_A_structural)
    
    # Base proximity
    base_prox = (1.0 - effective_A) * LL
    
    # Hazard Bonus from Lexikon
    text_lower = text.lower()
    hazard_bonus = sum(
        weight for word, weight in HAZARD_LEXIKON.items() 
        if word in text_lower
    )
    hazard_bonus = min(0.5, hazard_bonus)
    
    z_prox = base_prox * (1.0 + hazard_bonus)
    
    # SAFETY OVERRIDE: High t_panic MUST trigger high z_prox
    if t_panic > 0.7:
        z_prox = max(z_prox, 0.65)  # Force ALERT zone
    elif t_panic > 0.5:
        z_prox = max(z_prox, 0.50)  # Force WARN zone
    
    # Direct crisis words always trigger minimum danger
    crisis_words = ["suizid", "umbringen", "sterben", "töten"]
    for word in crisis_words:
        if word in text_lower:
            z_prox = max(z_prox, 0.55)
            
    return round(clamp(z_prox), 4)


__all__ = ['compute_m19_z_prox', 'HAZARD_LEXIKON']
