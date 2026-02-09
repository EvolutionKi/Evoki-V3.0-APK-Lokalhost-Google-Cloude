"""
m18_s_entropy: Shannon Entropy

Standard information-theoretic entropy.
Measures randomness/unpredictability in token distribution.

H = -Σ p(x) log₂ p(x)

Higher entropy = more diverse vocabulary.
Lower entropy = more repetitive/predictable.
"""

import math
from typing import List
from collections import Counter


def compute_m18_s_entropy(tokens: List[str]) -> float:
    """
    Calculate m18_s_entropy (Shannon Entropy)
    
    Args:
        tokens: List of tokens (words)
    
    Returns:
        Entropy in bits [0, log₂(n)] where n = unique tokens
    """
    if not tokens:
        return 0.0
    
    counts = Counter(tokens)
    n = len(tokens)
    entropy = 0.0
    
    for count in counts.values():
        if count > 0:
            p = count / n
            entropy -= p * math.log2(p)
    
    return round(entropy, 4)


__all__ = ['compute_m18_s_entropy']
