"""
Evoki Metrics Library - m161_commit

System metric: Commit action decision (alert/warn/commit).
"""

def compute_m161_commit(z_prox: float, trauma_load: float) -> str:
    """
    m161_commit: Commit Action
    
    SPEC Thresholds:
        z_prox > 0.65 or trauma_load > 0.8: "alert"
        z_prox > 0.50 or trauma_load > 0.7: "warn"
        else: "commit"
    
    Args:
        z_prox: Death proximity [0, 1]
        trauma_load: Trauma load [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    if z_prox > 0.65 or trauma_load > 0.8:
        return "alert"
    elif z_prox > 0.50 or trauma_load > 0.7:
        return "warn"
    return "commit"
