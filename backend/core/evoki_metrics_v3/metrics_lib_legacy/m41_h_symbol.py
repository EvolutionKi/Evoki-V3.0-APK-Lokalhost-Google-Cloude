"""
m41_h_symbol: Harmonie-Symbol
"""




def compute_m41_h_symbol(h_conv: float) -> float:
    """m41_h_symbol: Harmonie-Symbol"""
    return 1.0 if h_conv > 0.7 else 0.0
