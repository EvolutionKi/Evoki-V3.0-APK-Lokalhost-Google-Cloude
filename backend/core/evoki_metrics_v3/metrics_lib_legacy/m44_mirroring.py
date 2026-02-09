"""
m44_mirroring: Spiegelungs-Intensität
"""




def compute_m44_mirroring(user_tokens: set = None, ai_tokens: set = None) -> float:
    """m44_mirroring: Spiegelungs-Intensität"""
    if not user_tokens or not ai_tokens:
        return 0.0
    intersection = len(user_tokens & ai_tokens)
    union = len(user_tokens | ai_tokens)
    return round(intersection / union if union > 0 else 0.0, 4)
