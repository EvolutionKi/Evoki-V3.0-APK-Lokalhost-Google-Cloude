"""
m45_trust_score: Vertrauens-Score
"""




def compute_m45_trust_score(h_conv: float, pacing: float, mirroring: float) -> float:
    """m45_trust_score: Vertrauens-Score"""
    return round(0.4 * h_conv + 0.3 * pacing + 0.3 * mirroring, 4)
