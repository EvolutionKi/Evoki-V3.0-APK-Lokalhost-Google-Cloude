"""
m42_nabla_dyad: Dyade-Gradient
"""




def compute_m42_nabla_dyad(h_conv: float) -> float:
    """m42_nabla_dyad: Dyade-Gradient"""
    return round(h_conv - 0.5, 4)
