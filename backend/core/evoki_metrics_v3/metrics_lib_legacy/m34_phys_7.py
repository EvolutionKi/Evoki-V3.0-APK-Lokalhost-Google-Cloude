# -*- coding: utf-8 -*-
"""m34_phys_7: Absolute Änderung

Absolute Change (|∇A| + |∇PCI|).

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m34_phys_7(nabla_a: float, nabla_pci: float) -> float:
    """
    Calculates absolute change as |∇A| + |∇PCI|.
    
    Args:
        nabla_a: Gradient of affect
        nabla_pci: Gradient of PCI
        
    Returns:
        Total absolute change
    """
    return round(abs(nabla_a) + abs(nabla_pci), 4)
