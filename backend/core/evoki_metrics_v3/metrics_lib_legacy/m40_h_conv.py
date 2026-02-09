"""
m40_h_conv: Dyade-Harmonie
"""




def compute_m40_h_conv(a_user: float = 0.5, a_ai: float = 0.5) -> float:
    """m40_h_conv: Dyade-Harmonie"""
    diff = abs(a_user - a_ai)
    return round(1.0 - diff, 4)
