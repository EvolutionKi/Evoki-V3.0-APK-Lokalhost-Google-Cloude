# -*- coding: utf-8 -*-
"""m32_phys_5: Flow-Bewusstsein

Flow-Consciousness interaction (flow × phi).

Reference: EVOKI_V3_METRICS_SPECIFICATION.md
"""

def compute_m32_phys_5(flow: float, phi: float) -> float:
    """
    Calculates flow-consciousness as flow × phi.
    
    Args:
        flow: Flow metric value
        phi: Integrated information (consciousness proxy)
        
    Returns:
        Flow-consciousness value
    """
    return round(flow * phi, 4)
