"""
Evoki Metrics Library - m88_clarity

Complex emotion metric: Clarity/mental clearness.
"""

def compute_m88_clarity(PCI: float, arousal: float) -> float:
    """
    m88_clarity: Complex Emotion - Clarity
    
    SPEC: Mental clarity combines coherence with moderate arousal.
    
    Formula: PCI × (0.5 + arousal × 0.5)
    
    Args:
        PCI: Process Coherence Index [0, 1]
        arousal: Arousal level [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(PCI * (0.5 + arousal * 0.5), 4)
