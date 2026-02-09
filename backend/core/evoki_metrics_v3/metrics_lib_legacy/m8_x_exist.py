"""
m8_x_exist: Existenz-Axiom (Existence Score)

SPEC (FINAL7 Line 2579): 
    x_exist = max(weight_i) for all matching terms in lexicon

Measures existential content - references to being, existence.
Uses MAX weight (not sum) from lexicon matches.

Reference: EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md:2553-2637

Example lexicon:
    {"existiert": 1.0, "ich bin": 0.8, "wirklich": 0.6, "vorhanden": 0.7}
"""

from typing import Dict
from ._helpers import clamp


def compute_m8_x_exist(text: str, x_exist_lexikon: Dict[str, float]) -> float:
    """
    Calculate m8_x_exist (Existence Axiom)
    
    Args:
        text: Input text
        x_exist_lexikon: Dict of existence indicators {"term": weight}
                        REQUIRED - no hardcoded defaults!
                        Should be loaded from external lexikon files
    
    Returns:
        x_exist score [0, 1] - MAX weight of all found terms
    """
    x_exist = 0.0
    text_lower = text.lower()
    
    for term, weight in x_exist_lexikon.items():
        if term in text_lower:
            x_exist = max(x_exist, weight)  # FINAL7: MAX, not SUM!
    
    return round(clamp(x_exist), 4)


__all__ = ['compute_m8_x_exist']
