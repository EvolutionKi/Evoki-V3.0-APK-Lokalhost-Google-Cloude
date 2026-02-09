"""
Evoki Metrics Library - m91_emotional_coherence

Complex emotion metric: Emotional coherence.
"""

def compute_m91_emotional_coherence(PCI: float, t_disso: float) -> float:
    """
    m91_emotional_coherence: Complex Emotion - Emotional Coherence
    
    SPEC: Emotional coherence combines system coherence with low dissociation.
    
    Formula: PCI × (1 - T_disso)
    
    Args:
        PCI: Process Coherence Index [0, 1]
        t_disso: Trauma dissociation [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(PCI * (1 - t_disso), 4)
