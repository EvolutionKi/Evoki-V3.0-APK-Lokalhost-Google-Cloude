"""
m96_grain_word: Grain-Wort
"""

from collections import Counter


def compute_m96_grain_word(text: str) -> str:
    """m96_grain_word: Grain-Wort"""
    stopwords = {"der", "die", "das", "und", "ist", "in", "zu", "ein", "eine", "es", "ich", "nicht"}
    words = [w.lower() for w in text.split() if w.lower() not in stopwords and len(w) > 3]
    if not words:
        return ""
    word_counts = Counter(words)
    return word_counts.most_common(1)[0][0] if word_counts else ""
