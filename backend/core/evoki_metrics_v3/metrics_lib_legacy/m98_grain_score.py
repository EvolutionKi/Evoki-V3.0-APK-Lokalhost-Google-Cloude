"""
m98_grain_score: Grain-Dichte
"""




def compute_m98_grain_score(text: str, grain_word: str) -> float:
    """m98_grain_score: Grain-Dichte"""
    if not grain_word:
        return 0.0
    count = text.lower().count(grain_word.lower())
    word_count = len(text.split())
    return round(count / max(1, word_count), 4)
