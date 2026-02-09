# -*- coding: utf-8 -*-
"""m26_e_i_proxy: Energy-Information Proxy

SPEC: e_i_proxy = |∇A| × (1 - PCI)

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m26_e_i_proxy(nabla_a: float, PCI: float) -> float:
    """
    Calculates energy-information proxy from affect gradient and PCI.
    
    Args:
        nabla_a: Gradient of affect (∇A)
        PCI: Process Coherence Index
        
    Returns:
        Energy-information value (0.0-1.0)
    """
    return round(abs(nabla_a) * (1.0 - PCI), 4)
