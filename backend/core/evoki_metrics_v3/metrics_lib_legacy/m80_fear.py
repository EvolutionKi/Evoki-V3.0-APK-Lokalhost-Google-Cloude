"""
Evoki Metrics Library - m80_fear

Plutchik emotion metric: Fear with trauma panic boost.
"""

def compute_m80_fear(valence: float, arousal: float, dominance: float, t_panic: float) -> float:
    """
    m80_fear: Plutchik Fear
    
    SPEC: Fear emotion from Plutchik wheel, with T_panic boost.
    Low valence + high arousal + low dominance = fear.
    T_panic provides a floor value (trauma-informed).
    
    Formula: max(fear_base, t_panic × 0.8)
    where fear_base = (3 - valence + arousal - dominance) / 3
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    fear_base = (3 - valence + arousal - dominance) / 3
    fear_base = max(0.0, min(1.0, fear_base))
    return round(max(fear_base, t_panic * 0.8), 4)
