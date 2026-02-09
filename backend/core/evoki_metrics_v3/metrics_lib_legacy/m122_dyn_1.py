"""
Evoki Metrics Library - m122_dyn_1

Cognitive metric: Dynamic Factor 1 - total gradient magnitude.
"""

def compute_m122_dyn_1(nabla_a: float, nabla_pci: float) -> float:
    """
    m122_dyn_1: Dynamic Factor 1
    
    SPEC: |∇A| + |∇PCI|
    
    Total system change (affect + complexity gradients).
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(abs(nabla_a) + abs(nabla_pci), 4)
