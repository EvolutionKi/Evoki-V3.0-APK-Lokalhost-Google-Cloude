"""
m61_U: Free Energy
"""




def compute_m61_U(PCI: float, s_entropy: float) -> float:
    """m61_U: Free Energy"""
    lambda_coeff = 0.3
    return round(PCI - lambda_coeff * s_entropy, 4)
