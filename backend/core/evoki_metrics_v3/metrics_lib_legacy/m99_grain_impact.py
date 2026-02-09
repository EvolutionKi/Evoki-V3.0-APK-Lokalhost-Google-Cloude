"""
m99_grain_impact: Grain × Affekt
"""




def compute_m99_grain_impact(grain_score: float, A: float) -> float:
    """m99_grain_impact: Grain × Affekt"""
    return round(grain_score * A, 4)
