"""
Evoki Metrics Library - m133_meta_flexibility

Meta-cognition metric: Cognitive flexibility (topic switches per turn).
"""

def compute_m133_meta_flexibility(topic_changes: int, turns: int) -> float:
    """
    m133_meta_flexibility: Cognitive Flexibility
    
    SPEC: topic_changes / turns
    
    Measures adaptability via topic switching frequency.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(topic_changes / max(1, turns), 4)
