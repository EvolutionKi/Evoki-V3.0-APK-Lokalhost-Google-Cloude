# -*- coding: utf-8 -*-
"""m29_phys_2: Komplexitäts-Energie

Complexity Energy (squared PCI for physics engine).

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m29_phys_2(PCI: float) -> float:
    """
    Calculates complexity energy as PCI².
    
    Args:
        PCI: Process Coherence Index
        
    Returns:
        Complexity energy (PCI squared)
    """
    return round(PCI ** 2, 4)
