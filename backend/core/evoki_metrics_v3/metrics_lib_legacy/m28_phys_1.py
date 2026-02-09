# -*- coding: utf-8 -*-
"""m28_phys_1: Affekt-Energie

Affect Energy (squared affect for physics engine).

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m28_phys_1(A: float) -> float:
    """
    Calculates affect energy as A².
    
    Args:
        A: Affect value
        
    Returns:
        Affect energy (A squared)
    """
    return round(A ** 2, 4)
