"""
Evoki Metrics Library - m119_complexity_variance

Cognitive metric: Variance of PCI history.
"""
from typing import List

def compute_m119_complexity_variance(pci_history: List[float]) -> float:
    """
    m119_complexity_variance: PCI Variance
    
    SPEC: Variance of PCI over recent history
    
    Measures stability of cognitive complexity over time.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    if len(pci_history) < 2:
        return 0.0
    
    mean = sum(pci_history) / len(pci_history)
    variance = sum((x - mean) ** 2 for x in pci_history) / len(pci_history)
    
    return round(variance, 4)
