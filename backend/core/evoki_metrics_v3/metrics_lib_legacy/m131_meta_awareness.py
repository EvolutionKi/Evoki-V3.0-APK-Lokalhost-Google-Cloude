"""
Evoki Metrics Library - m131_meta_awareness

Meta-cognition metric: Self-awareness.
"""

def compute_m131_meta_awareness(A: float, PCI: float) -> float:
    """
    m131_meta_awareness: Meta Self-Awareness
    
    SPEC: (A + PCI) / 2
    
    Combined measure of affect and cognitive coherence as self-awareness proxy.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round((A + PCI) / 2.0, 4)
