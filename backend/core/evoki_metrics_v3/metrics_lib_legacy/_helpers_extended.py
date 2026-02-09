"""
EVOKI V3.0 METRICS LIBRARY - Core Helpers (EXTENDED)
Shared utility functions for all metrics

EXTENDED 2026-02-08 by CODEX:
- Added sigmoid() (was missing!)
- Added jaccard() (reduce duplication)
- Added normalize() (convenience)
- Added safe_divide() (robustness)
"""

import math
from typing import List, Set


# ============================================================================
# ORIGINAL HELPERS (Unchanged)
# ============================================================================

def tokenize(text: str) -> List[str]:
    """
    Tokenize text into words
    
    Simple whitespace tokenization with lowercase normalization.
    No punctuation removal or stopword filtering.
    
    Args:
        text: Input text
    
    Returns:
        List of lowercase words
    
    Example:
        >>> tokenize("Hello World!")
        ['hello', 'world!']
    """
    return text.lower().split()


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """
    Clamp value to [lo, hi] range
    
    Args:
        val: Value to clamp
        lo: Lower bound (default: 0.0)
        hi: Upper bound (default: 1.0)
    
    Returns:
        Clamped value in [lo, hi]
    
    Example:
        >>> clamp(-0.5)
        0.0
        >>> clamp(0.5)
        0.5
        >>> clamp(1.5)
        1.0
    """
    return max(lo, min(hi, val))


# ============================================================================
# EXTENDED HELPERS (Added 2026-02-08)
# ============================================================================

def sigmoid(x: float) -> float:
    """
    Sigmoid activation function
    
    Maps input to [0, 1] with smooth S-curve.
    sigmoid(0) = 0.5
    sigmoid(+∞) → 1.0
    sigmoid(-∞) → 0.0
    
    Args:
        x: Input value
    
    Returns:
        Sigmoid output in [0, 1]
    
    Example:
        >>> sigmoid(0)
        0.5
        >>> sigmoid(5)
        0.9933...
        >>> sigmoid(-5)
        0.0066...
    
    Used in:
        - m73_ev_readiness.py (EV_readiness calculation)
    """
    return 1.0 / (1.0 + math.exp(-x))


def jaccard(set_a: Set, set_b: Set) -> float:
    """
    Jaccard similarity coefficient
    
    Measures overlap between two sets:
    J(A, B) = |A ∩ B| / |A ∪ B|
    
    Args:
        set_a: First set
        set_b: Second set
    
    Returns:
        Jaccard similarity [0, 1]
        - 0.0: No overlap
        - 1.0: Identical sets
    
    Example:
        >>> jaccard({'a', 'b', 'c'}, {'b', 'c', 'd'})
        0.5
        >>> jaccard({'a', 'b'}, {'a', 'b'})
        1.0
    
    Used in:
        - m5_coh.py (coherence calculation)
        - m13_rep_same.py (repetition detection)
        - m14_rep_history.py (historical repetition)
    """
    if not set_a or not set_b:
        return 0.0
    
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    
    return intersection / union if union > 0 else 0.0


def normalize(val: float, min_val: float, max_val: float) -> float:
    """
    Normalize value from [min_val, max_val] to [0, 1]
    
    Linear mapping with edge case handling.
    
    Args:
        val: Value to normalize
        min_val: Minimum of input range
        max_val: Maximum of input range
    
    Returns:
        Normalized value in [0, 1]
    
    Example:
        >>> normalize(5, 0, 10)
        0.5
        >>> normalize(7.5, 5, 10)
        0.5
        >>> normalize(100, 0, 50)  # Clips to 1.0
        1.0
    
    Note:
        If min_val == max_val, returns 0.5 (midpoint)
    """
    if max_val == min_val:
        return 0.5
    
    normalized = (val - min_val) / (max_val - min_val)
    return clamp(normalized, 0.0, 1.0)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division with default for zero denominator
    
    Prevents division by zero errors.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Value to return if denominator is zero (default: 0.0)
    
    Returns:
        numerator / denominator, or default if denominator == 0
    
    Example:
        >>> safe_divide(10, 2)
        5.0
        >>> safe_divide(10, 0)
        0.0
        >>> safe_divide(10, 0, default=1.0)
        1.0
    
    Used in:
        - Various ratio calculations
        - Mean/variance computations
    """
    return numerator / denominator if denominator != 0 else default


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Original
    'tokenize',
    'clamp',
    
    # Extended (2026-02-08)
    'sigmoid',
    'jaccard',
    'normalize',
    'safe_divide',
]
