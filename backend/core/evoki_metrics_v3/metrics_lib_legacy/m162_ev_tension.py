"""
Evoki Metrics Library - m162_ev_tension

V3.1 Extension: Evolution Tension (counter-force to resonance)
"""

def compute_m162_ev_tension(z_prox: float, x_fm_prox: float, e_i_proxy: float) -> float:
    """
    m162_ev_tension: Evolution Tension (V3.1 Extension)
    
    SPEC V3.1: The "load" opposing evolution - sum of all resistive forces.
    
    Formula: EV_tension = 0.5 × z_prox + 0.2 × x_fm_prox + 0.3 × E_I_proxy
    
    Physics Interpretation:
    - z_prox (50%): Fear of chaos/death
    - x_fm_prox (20%): Danger of freezing/stagnation  
    - E_I_proxy (30%): Uncontrolled chaotic pressure
    
    High tension opposes readiness - system must overcome these forces to evolve.
    
    Reference: VektorMathik.txt Line 136-137
    """
    tension = 0.5 * z_prox + 0.2 * x_fm_prox + 0.3 * e_i_proxy
    return round(max(0.0, min(1.0, tension)), 4)
