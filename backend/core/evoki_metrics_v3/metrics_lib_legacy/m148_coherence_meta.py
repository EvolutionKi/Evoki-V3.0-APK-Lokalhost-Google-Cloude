"""
Evoki Metrics Library - m148_coherence_meta

Meta-cognition metric: Meta-coherence (internal consistency).
"""

def compute_m148_coherence_meta(internal_consistency: float) -> float:
    """
    m148_coherence_meta: Meta-Coherence
    
    SPEC: clamp(internal_consistency)
    
    Measures internal consistency of meta-level reasoning.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(max(0.0, min(1.0, internal_consistency)), 4)
