# -*- coding: utf-8 -*-
"""m31_phys_4: Überlebenswahrscheinlichkeit

Survival Probability (inverse of death proximity).

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m31_phys_4(z_prox: float) -> float:
    """
    Calculates survival probability

 as 1 - z_prox.
    
    Args:
        z_prox: Death proximity value
        
    Returns:
        Survival probability (0.0-1.0)
    """
    return round(1.0 - z_prox, 4)
