# -*- coding: utf-8 -*-
"""m25_psi: Normalized Complexity (Psi)

SPEC: psi = PCI / (1 + token_count/100.0)

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m25_psi(PCI: float, token_count: int) -> float:
    """
    Calculates normalized complexity metric.
    
    Args:
        PCI: Process Coherence Index
        token_count: Number of tokens in text
        
    Returns:
        Normalized complexity value (0.0-1.0)
    """
    return round(PCI / (1.0 + token_count / 100.0), 4)
