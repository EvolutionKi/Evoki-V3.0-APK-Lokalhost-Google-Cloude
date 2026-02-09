"""
m53_hyp_6: Zeit-Faktor
"""




def compute_m53_hyp_6(gap_seconds: float) -> float:
    """m53_hyp_6: Zeit-Faktor"""
    return round(gap_seconds / 3600.0, 4)
