"""
Evoki Metrics Library - m87_confusion

Complex emotion metric: Confusion.
"""

def compute_m87_confusion(arousal: float, PCI: float) -> float:
    """
    m87_confusion: Complex Emotion - Confusion
    
    SPEC: Confusion combines high arousal with low coherence.
    
    Formula: arousal × (1 - PCI)
    
    Args:
        arousal: Arousal level [0, 1]
        PCI: Process Coherence Index [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(arousal * (1 - PCI), 4)
