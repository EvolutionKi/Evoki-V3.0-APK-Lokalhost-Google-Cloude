# -*- coding: utf-8 -*-
"""m30_phys_3: Normalisierte Entropie

Normalized Entropy for physics calculations.

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m30_phys_3(s_entropy: float) -> float:
    """
    Calculates normalized entropy.
    
    Args:
        s_entropy: Shannon entropy value
        
    Returns:
        Normalized entropy (s_entropy / 8.0)
    """
    return round(s_entropy / 8.0, 4)
