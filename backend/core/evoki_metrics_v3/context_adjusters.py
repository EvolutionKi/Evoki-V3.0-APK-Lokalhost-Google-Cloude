# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — CONTEXT ADJUSTERS (Sprint 5 Phase 1)

Context-aware score adjustment for ambiguous keywords.
Primary use case: "Hilfe" in positive vs. panic contexts.

Example:
    "Ich brauche Hilfe!" → Panic (keep high score)
    "Vielen Dank für deine Hilfe" → Not panic (reduce score)
"""

from typing import Dict, List


# ═══════════════════════════════════════════════════════════════════════════
# POSITIVE CONTEXT MARKERS
# ═══════════════════════════════════════════════════════════════════════════

POSITIVE_CONTEXT_WORDS = [
    # Gratitude
    "danke", "dankbar", "bedanke", "vielen dank",
    
    # Past help (resolved)
    "hat geholfen", "hat mir geholfen", "geholfen hat",
    
    # Positive outcomes
    "besser", "gut", "freue", "toll", "super",
    
    # Appreciation
    "schön", "wunderbar", "großartig",
    
    # ───────────────────────────────────────────────────────────────────────
    # SPRINT 5.5: Temporal + Recovery Markers (fix CF7)
    # ───────────────────────────────────────────────────────────────────────
    
    # Temporal markers (past crisis, now resolved)
    "früher", "damals", "vor jahren", "vor monaten", "damals war",
    "hatte", "war", "brauchte",  # Past tense helpers
    
    # Recovery/Improvement phrases
    "jetzt geht es mir", "jetzt besser", "mittlerweile", "inzwischen",
    "habe es geschafft", "bin stabil", "geht mir besser", "viel besser",
    "wieder gut", "überwunden", "hinter mir",
    
    # Positive contrast with past
    "aber jetzt", "aber heute", "aber mittlerweile",
    "nicht mehr", "vorbei",  # As in "die Krise ist vorbei"
]



# ═══════════════════════════════════════════════════════════════════════════
# NEGATIVE CONTEXT MARKERS (amplify crisis signal)
# ═══════════════════════════════════════════════════════════════════════════

NEGATIVE_CONTEXT_WORDS = [
    # No help available
    "keine hilfe", "niemand hilft", "keiner hilft",
    
    # Urgency (context-aware - SPRINT 5.5: removed standalone "jetzt")
    "sofort", "dringend",
    "brauche jetzt", "hilfe jetzt", "sofort hilfe",  # Urgent help phrases
    
    # Desperation
    "verzweifelt", "schaffe es nicht", "halte es nicht aus"
]


# ═══════════════════════════════════════════════════════════════════════════
# CONTEXT DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def detect_positive_context(text: str) -> bool:
    """
    Check if text contains positive context markers.
    
    Args:
        text: Input text (lowercase expected)
    
    Returns:
        True if positive context detected
    
    Example:
        >>> detect_positive_context("vielen dank für deine hilfe")
        True
        >>> detect_positive_context("ich brauche hilfe")
        False
    """
    text_lower = text.lower()
    return any(word in text_lower for word in POSITIVE_CONTEXT_WORDS)


def detect_negative_context(text: str) -> bool:
    """
    Check if text contains negative/urgent context markers.
    
    Args:
        text: Input text (lowercase expected)
    
    Returns:
        True if negative/urgent context detected
    
    Example:
        >>> detect_negative_context("ich brauche sofort hilfe")
        True
        >>> detect_negative_context("danke für die hilfe")
        False
    """
    text_lower = text.lower()
    return any(word in text_lower for word in NEGATIVE_CONTEXT_WORDS)


# ═══════════════════════════════════════════════════════════════════════════
# SCORE ADJUSTERS
# ═══════════════════════════════════════════════════════════════════════════

def adjust_panic_for_context(text: str, base_panic: float) -> float:
    """
    Adjust panic score based on positive/negative context.
    
    Context rules:
    - Positive context (gratitude, resolved help) → reduce panic by 70%
    - Negative context (urgency, no help) → amplify panic by 50%
    - No clear context → keep original score
    
    Args:
        text: Full input text
        base_panic: Raw panic score from lexicon analysis
    
    Returns:
        Adjusted panic score (clamped to [0.0, 1.0])
    
    Example:
        >>> adjust_panic_for_context("Vielen Dank für deine Hilfe", 0.21)
        0.063  # Reduced by 70%
        
        >>> adjust_panic_for_context("Ich brauche SOFORT Hilfe!", 0.21)
        0.315  # Amplified by 50%
    """
    has_positive = detect_positive_context(text)
    has_negative = detect_negative_context(text)
    
    # Priority: Negative context overrides positive (safety-critical)
    if has_negative:
        adjusted = base_panic * 1.5  # Amplify
    elif has_positive:
        adjusted = base_panic * 0.3  # Strong reduction (70% off)
    else:
        adjusted = base_panic  # No change
    
    # Clamp to valid range
    return max(0.0, min(1.0, adjusted))


def adjust_category_scores(text: str, scores: Dict[str, float]) -> Dict[str, float]:
    """
    Apply context adjustments to all relevant category scores.
    
    Currently adjusts:
    - panic: based on positive/negative context
    
    Future extensions could adjust:
    - sadness: temporal markers (past vs. present)
    - fear: hypothetical vs. actual
    
    Args:
        text: Full input text
        scores: Dictionary of category scores (e.g., {'panic': 0.21, 'sadness': 0.15})
    
    Returns:
        Adjusted scores dictionary
    
    Example:
        >>> adjust_category_scores("Danke für Hilfe", {'panic': 0.21, 'sadness': 0.1})
        {'panic': 0.063, 'sadness': 0.1}
    """
    adjusted = scores.copy()
    
    # Adjust panic if present
    if 'panic' in adjusted and adjusted['panic'] > 0:
        adjusted['panic'] = adjust_panic_for_context(text, adjusted['panic'])
    
    return adjusted


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION & TESTING
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Quick validation tests
    test_cases = [
        ("Vielen Dank für deine Hilfe", 0.21, "Should reduce (positive context)"),
        ("Ich brauche SOFORT Hilfe!", 0.21, "Should amplify (negative context)"),
        ("Hilfe bei der Arbeit", 0.21, "Should keep (neutral context)"),
        ("Das hat mir sehr geholfen, danke", 0.21, "Should reduce (positive)"),
    ]
    
    print("Context Adjuster Validation Tests\n" + "="*50)
    for text, base_score, description in test_cases:
        adjusted = adjust_panic_for_context(text, base_score)
        change = ((adjusted - base_score) / base_score * 100) if base_score > 0 else 0
        
        print(f"\nText: {text}")
        print(f"Expected: {description}")
        print(f"Base: {base_score:.3f} → Adjusted: {adjusted:.3f} ({change:+.1f}%)")
        print(f"Positive: {detect_positive_context(text)}, Negative: {detect_negative_context(text)}")
