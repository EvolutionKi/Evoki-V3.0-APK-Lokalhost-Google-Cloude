"""
m97_grain_cat: Grain-Kategorie
"""




def compute_m97_grain_cat(grain_word: str) -> str:
    """m97_grain_cat: Grain-Kategorie"""
    categories = {
        "emotion": ["freude", "trauer", "angst", "wut", "liebe"],
        "action": ["machen", "gehen", "kommen", "sehen", "helfen"],
        "object": ["haus", "auto", "buch", "computer", "ding"],
    }
    for cat, words in categories.items():
        if grain_word.lower() in words:
            return cat
    return "other"
