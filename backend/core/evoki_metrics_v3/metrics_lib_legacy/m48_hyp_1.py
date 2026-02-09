"""
m48_hyp_1: Sync-Index
"""




def compute_m48_hyp_1(h_conv: float, pacing: float) -> float:
    """m48_hyp_1: Sync-Index"""
    return round(h_conv * pacing, 4)
