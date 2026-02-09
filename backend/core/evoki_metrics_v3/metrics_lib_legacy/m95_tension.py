"""
Evoki Metrics Library - m95_tension

Complex emotion metric: Tension.
"""

def compute_m95_tension(valence: float, arousal: float) -> float:
    """
    m95_tension: Complex Emotion - Tension
    
    SPEC: Tension is high arousal with extreme valence (either positive or negative).
    
    Formula: arousal × |valence - 0.5| × 2
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(arousal * abs(valence - 0.5) * 2, 4)
