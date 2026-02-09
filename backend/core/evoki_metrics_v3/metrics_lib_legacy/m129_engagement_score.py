"""
Evoki Metrics Library - m129_engagement_score

Cognitive metric: Engagement score (questions per turn).
"""

def compute_m129_engagement_score(questions: int, turns: int) -> float:
    """
    m129_engagement_score: Engagement Score
    
    SPEC: questions / turns
    
    Measures user engagement via question frequency.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(questions / max(1, turns), 4)
