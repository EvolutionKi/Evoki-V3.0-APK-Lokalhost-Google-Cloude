"""
m113_t_resilience: Resilienz
"""




def compute_m113_t_resilience(t_integ: float, t_panic: float) -> float:
    """m113_t_resilience: Resilienz"""
    return round(t_integ / (1.0 + t_panic), 4)
