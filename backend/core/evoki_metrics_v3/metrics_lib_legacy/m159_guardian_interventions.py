"""
Evoki Metrics Library - m159_guardian_interventions

System metric: Guardian intervention rate.
"""

def compute_m159_guardian_interventions(interventions: int, turns: int) -> float:
    """
    m159_guardian_interventions: Guardian Intervention Rate
    
    SPEC: interventions / turns
    
    Measures how often the Guardian (Wächter) intervenes per turn.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(interventions / max(1, turns), 4)
