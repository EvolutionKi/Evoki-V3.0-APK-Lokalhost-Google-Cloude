"""
m54_hyp_7: Vertrauens-Rapport
"""




def compute_m54_hyp_7(trust_score: float, rapport: float) -> float:
    """m54_hyp_7: Vertrauens-Rapport"""
    return round(trust_score * rapport, 4)
