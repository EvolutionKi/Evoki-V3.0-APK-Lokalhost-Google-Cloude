"""
Evoki Metrics Library - m93_emotional_range

Complex emotion metric: Emotional range (VAD distance from center).
"""
import math

def compute_m93_emotional_range(v: float, a: float, d: float) -> float:
    """
    m93_emotional_range: Complex Emotion - Emotional Range
    
    SPEC: Distance from emotional center (0.5, 0.5, 0.5) in VAD space.
    Measures intensity/extremity of emotional state.
    
    Formula: sqrt((v - 0.5)² + (a - 0.5)² + (d - 0.5)²)
    
    Args:
        v: Valence [0, 1]
        a: Arousal [0, 1]
        d: Dominance [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(math.sqrt((v - 0.5)**2 + (a - 0.5)**2 + (d - 0.5)**2), 4)
