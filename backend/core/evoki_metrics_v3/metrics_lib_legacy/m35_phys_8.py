# -*- coding: utf-8 -*-
"""m35_phys_8: Fixpunkt-Nähe

Fixed Point Proximity (max(ZLF, stagnation)).

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m35_phys_8(ZLF: float, stagnation: float = 0.0) -> float:
    """
    Calculates fixed point proximity.
    
    Args:
        ZLF: Zero-Line-Flow (stagnation indicator)
        stagnation: External stagnation measure
        
    Returns:
        Maximum stagnation value
    """
    return round(max(ZLF, stagnation), 4)
