"""
Evoki Metrics Library - m149_adaptation_rate

Meta-cognition metric: Adaptation rate (adjustments per opportunity).
"""

def compute_m149_adaptation_rate(adjustments: int, opportunities: int) -> float:
    """
    m149_adaptation_rate: Adaptation Rate
    
    SPEC: adjustments / opportunities
    
    Measures how frequently the system adapts when given the chance.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(adjustments / max(1, opportunities), 4)
