"""
Evoki Metrics Library - m150_integration_score

Meta-cognition metric: Integration score (active modules / total).
"""

def compute_m150_integration_score(modules_active: int, total_modules: int) -> float:
    """
    m150_integration_score: Integration Score
    
    SPEC: modules_active / total_modules
    
    Measures system integration level.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(modules_active / max(1, total_modules), 4)
