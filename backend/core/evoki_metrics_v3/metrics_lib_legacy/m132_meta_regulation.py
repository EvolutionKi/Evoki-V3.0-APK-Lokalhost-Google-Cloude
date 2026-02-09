"""
Evoki Metrics Library - m132_meta_regulation

Meta-cognition metric: Self-regulation based on death proximity.
"""

def compute_m132_meta_regulation(z_prox: float, commit: str) -> float:
    """
    m132_meta_regulation: Self-Regulation
    
    SPEC: Base regulation from death proximity, modulated by commit state.
    
    Formula: 
        regulation = 1.0 - z_prox
        If commit == "warn": × 0.8
        If commit == "alert": × 0.5
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    regulation = 1.0 - z_prox
    
    if commit == "warn":
        regulation *= 0.8
    elif commit == "alert":
        regulation *= 0.5
    
    return round(regulation, 4)
