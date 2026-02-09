"""
m3_gen_index: Generativity Index

SPEC Formula (FINAL7 line 2131):
    gen_index = (|new_bigrams| / |total_bigrams|) × novelty_boost
    
where:
    new_bigrams = current_bigrams \ history_bigrams
    novelty_boost = 1 + rare_word_bonus × 0.2
    rare_word_bonus = Σ(1/freq(word_i)) / |words|

Reference: EVOKI_V3_METRICS_SPECIFICATION.md:2109-2199
"""

from typing import List, Dict, Optional
from ._helpers import clamp


def compute_m3_gen_index(
    text: str,
    history: Optional[List[str]] = None,
    word_frequencies: Optional[Dict[str, int]] = None
) -> float:
    """
    Calculate m3_gen_index (Generativity/Novelty)
    
    Args:
        text: Input text
        history: Previous texts for comparison (optional)
        word_frequencies: Word frequency dict for rarity bonus (optional)
    
    Returns:
        Generativity score [0, 1]
    """
    if history is None:
        history = []
    
    words = text.lower().split()
    
    if len(words) < 2:
        return 0.5
    
    # Create bigrams for current text
    current_bigrams = set(zip(words[:-1], words[1:]))
    
    # Collect historical bigrams
    history_bigrams = set()
    for hist_text in history:
        hist_words = hist_text.lower().split()
        if len(hist_words) >= 2:
            history_bigrams.update(zip(hist_words[:-1], hist_words[1:]))
    
    # Calculate novelty (new bigrams)
    if len(history_bigrams) == 0:
        base_novelty = 1.0  # First text is completely novel
    else:
        new_bigrams = current_bigrams - history_bigrams
        base_novelty = len(new_bigrams) / len(current_bigrams) if len(current_bigrams) > 0 else 0.0
    
    # Rare word bonus (optional enhancement)
    if word_frequencies:
        rarity_scores = [1.0 / max(word_frequencies.get(w, 1), 1) for w in words]
        rarity_bonus = sum(rarity_scores) / len(words)
        novelty_boost = 1.0 + rarity_bonus * 0.2
    else:
        novelty_boost = 1.0
    
    # Final generativity score
    gen_index = base_novelty * novelty_boost
    
    return round(clamp(gen_index), 4)


__all__ = ['compute_m3_gen_index']
