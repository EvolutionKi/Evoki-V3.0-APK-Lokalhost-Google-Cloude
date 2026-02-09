"""
m67_precision: Precision FEP
"""




def compute_m67_precision(variance: float) -> float:
    """m67_precision: Precision FEP"""
    return round(1.0 / max(0.01, variance), 4)
