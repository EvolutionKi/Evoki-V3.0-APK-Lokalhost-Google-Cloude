"""
EVOKI V3.0 METRICS LIBRARY - Core Helpers
Shared utility functions for all metrics
"""

from typing import List


def tokenize(text: str) -> List[str]:
    """Tokenize text into words"""
    return text.lower().split()


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi] range"""
    return max(lo, min(hi, val))
