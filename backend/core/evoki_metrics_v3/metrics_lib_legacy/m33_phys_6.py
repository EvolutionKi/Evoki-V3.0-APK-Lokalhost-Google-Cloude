# -*- coding: utf-8 -*-
"""m33_phys_6: Kohärenz-Komplex

Coherence-Complexity interaction (coh × PCI).

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m33_phys_6(coh: float, PCI: float) -> float:
    """
    Calculates coherence-complexity as coh × PCI.
    
    Args:
        coh: Coherence metric value
        PCI: Process Coherence Index
        
    Returns:
        Coherence-complexity value
    """
    return round(coh * PCI, 4)
