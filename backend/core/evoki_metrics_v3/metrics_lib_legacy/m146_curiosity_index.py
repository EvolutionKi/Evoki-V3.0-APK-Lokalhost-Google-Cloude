"""
Evoki Metrics Library - m146_curiosity_index

Meta-cognition metric: Curiosity (questions asked per turn).
"""

def compute_m146_curiosity_index(questions_asked: int, turns: int) -> float:
    """
    m146_curiosity_index: Curiosity Index
    
    SPEC: questions_asked / turns
    
    Measures curiosity via question frequency.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(questions_asked / max(1, turns), 4)
