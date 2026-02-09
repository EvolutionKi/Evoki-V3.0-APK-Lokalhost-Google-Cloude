"""
Evoki Metrics Library - m166_hazard

V3.1 Extension: Hazard Level (Combined Risk)
"""

def compute_m166_hazard(z_prox: float, t_panic: float, t_fog: float) -> float:
    """
    m166_hazard: Hazard Level (V3.1 Extension)
    
    SPEC V3.1: Combined hazard from proximity to death, panic, and fog.
    
    Formula: hazard = 0.5 × z_prox + 0.3 × T_panic + 0.2 × T_fog
    
    Physics Interpretation:
    - z_prox (50%): Proximity to system collapse
    - T_panic (30%): Acute stress/panic state
    - T_fog (20%): Cognitive impairment from trauma
    
    High hazard indicates immediate intervention needed.
    
    Reference: Andromatische Abhandlung, Safety Layer
    """
    hazard = 0.5 * z_prox + 0.3 * t_panic + 0.2 * t_fog
    return round(max(0.0, min(1.0, hazard)), 4)
