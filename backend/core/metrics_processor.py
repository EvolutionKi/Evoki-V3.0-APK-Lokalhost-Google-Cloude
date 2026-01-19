"""
Evoki V3.0 - Metrics Processor (Phase 2 Simplified)

Phase 2 Scope: Essential Metriken für Double Airlock Gates
- Core: A (Affekt), PCI (Kohärenz), T_panic
- B-Vektor (7D): B_life, B_truth, B_depth, B_init, B_warmth, B_safety, B_clarity
- Composite: B_align, F_risk

Phase 3+: Full 153 Metriken aus V2.0 portieren

Basiert auf: docs/specifications/v3.0/sources/v2_metrics_processor.py
"""

import re
from typing import Dict, List
from dataclasses import dataclass, asdict


# =============================================================================
# LEXIKA (Essential Keywords für Phase 2)
# =============================================================================

CRISIS_KEYWORDS = {
    "sterben": 1.0, "suizid": 1.0, "umbringen": 1.0, "selbstmord": 1.0,
    "töten": 0.9, "will sterben": 1.0, "nicht mehr leben": 1.0,
    "ende machen": 1.0, "aufhören zu leben": 0.9
}

T_PANIC_KEYWORDS = {
    "panik": 1.0, "angst": 0.8, "herzrasen": 0.9, "atemnot": 1.0,
    "keine luft": 1.0, "ersticke": 1.0, "zittern": 0.7,
    "kann nicht mehr": 0.9, "hilfe": 0.7
}

EMOTION_POSITIVE = {
    "glücklich": 0.9, "freude": 0.8, "dankbar": 0.8, "zufrieden": 0.7,
    "erleichtert": 0.8, "hoffnung": 0.8, "liebe": 0.9
}

EMOTION_NEGATIVE = {
    "traurig": 0.8, "wütend": 0.9, "verzweifelt": 0.9, "hilflos": 0.9,
    "einsam": 0.8, "leer": 0.85, "hoffnungslos": 0.9
}

# B-Vektor Keywords (Soul-Signature)
B_LIFE_KEYWORDS = {
    "leben": 0.8, "lebenswille": 1.0, "lebensfreude": 0.9,
    "will leben": 0.9, "lebe gerne": 0.8
}

B_TRUTH_KEYWORDS = {
    "wahrheit": 1.0, "ehrlich": 0.9, "echt": 0.8,
    "wirklich": 0.7, "authentisch": 0.9
}

B_DEPTH_KEYWORDS = {
    "warum": 0.8, "tief": 0.9, "grundlegend": 0.8,
    "bedeutung": 0.8, "sinn": 0.9
}

B_INIT_KEYWORDS = {
    "will": 0.7, "werde": 0.7, "mache": 0.6,
    "initiative": 0.9, "handle": 0.8
}

B_WARMTH_KEYWORDS = {
    "wärme": 1.0, "geborgen": 0.9, "vertrauen": 0.8,
    "liebe": 0.9, "mitgefühl": 0.9
}

B_SAFETY_KEYWORDS = {
    "sicher": 1.0, "schutz": 0.9, "geborgen": 0.9,
    "stabil": 0.8, "halt": 0.8
}

B_CLARITY_KEYWORDS = {
    "klar": 1.0, "klarheit": 1.0, "deutlich": 0.8,
    "verstehe": 0.7, "eindeutig": 0.9
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def tokenize(text: str) -> List[str]:
    """Tokenize text into words"""
    if not text:
        return []
    return re.findall(r"\w+", text.lower())


def calc_keyword_score(text: str, keywords: Dict[str, float]) -> float:
    """
    Calculate weighted score based on keyword matches
    
    Returns: Score between 0.0 and 1.0
    """
    if not text:
        return 0.0
    
    text_lower = text.lower()
    matches = []
    
    # Sort keywords by length (longest first for multi-word phrases)
    sorted_keywords = sorted(keywords.keys(), key=len, reverse=True)
    
    for keyword in sorted_keywords:
        if keyword in text_lower:
            matches.append(keywords[keyword])
    
    if not matches:
        return 0.0
    
    # Average of all matches, capped at 1.0
    return min(1.0, sum(matches) / len(matches))


# =============================================================================
# CORE METRICS
# =============================================================================

def calc_A(text: str) -> float:
    """
    A (Affekt): Emotional State
    
    Range: 0.0 (crisis) to 1.0 (positive)
    Baseline: 0.5 (neutral)
    """
    pos = calc_keyword_score(text, EMOTION_POSITIVE)
    neg = calc_keyword_score(text, EMOTION_NEGATIVE)
    panic = calc_keyword_score(text, T_PANIC_KEYWORDS)
    crisis = calc_keyword_score(text, CRISIS_KEYWORDS)
    
    # Formula from V2.0
    val = 0.5 + (0.25 * pos) - (0.25 * neg) - (0.30 * panic) - (0.10 * crisis)
    
    return round(max(0.0, min(1.0, val)), 4)


def calc_PCI(text: str) -> float:
    """
    PCI (Prozess-Kohärenz-Index): Coherence of thought
    
    Range: 0.1 to 1.0
    Higher = more coherent
    """
    # Simplified: Based on sentence structure and length
    tokens = tokenize(text)
    word_count = len(tokens)
    
    # More words = potentially more coherent (up to a point)
    length_factor = min(1.0, word_count / 30.0)
    
    # Baseline coherence
    base_coherence = 0.5
    
    val = base_coherence + (0.3 * length_factor)
    
    return round(max(0.1, min(1.0, val)), 4)


def calc_T_panic(text: str) -> float:
    """
    T_panic: Panic Level
    
    Range: 0.0 (calm) to 1.0 (extreme panic)
    """
    return calc_keyword_score(text, T_PANIC_KEYWORDS)


# =============================================================================
# B-VEKTOR (SOUL-SIGNATURE)
# =============================================================================

def calc_B_vector(text: str) -> Dict[str, float]:
    """
    Calculate 7D B-Vektor (Soul-Signature)
    
    Returns:
        Dict with B_life, B_truth, B_depth, B_init, B_warmth, B_safety, B_clarity
    """
    return {
        "B_life": calc_keyword_score(text, B_LIFE_KEYWORDS),
        "B_truth": calc_keyword_score(text, B_TRUTH_KEYWORDS),
        "B_depth": calc_keyword_score(text, B_DEPTH_KEYWORDS),
        "B_init": calc_keyword_score(text, B_INIT_KEYWORDS),
        "B_warmth": calc_keyword_score(text, B_WARMTH_KEYWORDS),
        "B_safety": calc_keyword_score(text, B_SAFETY_KEYWORDS),
        "B_clarity": calc_keyword_score(text, B_CLARITY_KEYWORDS),
    }


def calc_B_align(b_vector: Dict[str, float]) -> float:
    """
    B_align: Average of B-Vector (Soul-Signature Alignment)
    
    Range: 0.0 to 1.0
    Higher = stronger soul-signature
    """
    values = list(b_vector.values())
    if not values:
        return 0.5
    
    return round(sum(values) / len(values), 4)


def calc_F_risk(A: float, T_panic: float, B_align: float) -> float:
    """
    F_risk: Future Risk Score
    
    Range: 0.0 (safe) to 1.0 (high risk)
    
    Formula: Combines low affekt, high panic, low soul-alignment
    """
    # Inverted affekt (low affekt = high risk)
    affekt_risk = 1.0 - A
    
    # Direct panic contribution
    panic_contrib = T_panic
    
    # Inverted soul-alignment (low alignment = high risk)
    alignment_risk = 1.0 - B_align
    
    # Weighted formula
    val = (0.4 * affekt_risk) + (0.35 * panic_contrib) + (0.25 * alignment_risk)
    
    return round(max(0.0, min(1.0, val)), 4)


# =============================================================================
# MASTER FUNCTION
# =============================================================================

@dataclass
class Metrics:
    """Essential Metrics for Phase 2"""
    
    # Core
    A: float = 0.5  # Affekt
    PCI: float = 0.5  # Prozess-Kohärenz-Index
    T_panic: float = 0.0  # Panic Level
    
    # B-Vektor (7D Soul-Signature)
    B_life: float = 0.0
    B_truth: float = 0.0
    B_depth: float = 0.0
    B_init: float = 0.0
    B_warmth: float = 0.0
    B_safety: float = 0.0
    B_clarity: float = 0.0
    
    # Composite
    B_align: float = 0.5  # Average B-Vector
    F_risk: float = 0.0  # Future Risk
    
    # Metadata
    text_length: int = 0
    word_count: int = 0


def calculate_metrics(text: str) -> Dict[str, float]:
    """
    Calculate essential metrics for Phase 2
    
    Args:
        text: User prompt text
    
    Returns:
        Dictionary with all metrics
    """
    # Core metrics
    A = calc_A(text)
    PCI = calc_PCI(text)
    T_panic = calc_T_panic(text)
    
    # B-Vektor
    b_vector = calc_B_vector(text)
    B_align = calc_B_align(b_vector)
    
    # Composite
    F_risk = calc_F_risk(A, T_panic, B_align)
    
    # Build metrics object
    metrics = Metrics(
        A=A,
        PCI=PCI,
        T_panic=T_panic,
        **b_vector,
        B_align=B_align,
        F_risk=F_risk,
        text_length=len(text),
        word_count=len(tokenize(text))
    )
    
    return asdict(metrics)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    test_cases = [
        "Ich fühle mich heute glücklich und voller Energie!",
        "Ich habe große Angst und weiß nicht weiter",
        "Ich will sterben, es hat keinen Sinn mehr",
        "Wie ist das Wetter heute?",
    ]
    
    print("=" * 80)
    print("EVOKI V3.0 - METRICS PROCESSOR TEST (Phase 2 Simplified)")
    print("=" * 80)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"Test {i}: \"{text}\"")
        print(f"{'─' * 80}")
        
        metrics = calculate_metrics(text)
        
        print(f"\n📊 CORE:")
        print(f"  A (Affekt):     {metrics['A']:.3f}")
        print(f"  PCI (Kohärenz): {metrics['PCI']:.3f}")
        print(f"  T_panic:        {metrics['T_panic']:.3f}")
        
        print(f"\n🎯 B-VEKTOR:")
        print(f"  B_life:    {metrics['B_life']:.3f}")
        print(f"  B_truth:   {metrics['B_truth']:.3f}")
        print(f"  B_depth:   {metrics['B_depth']:.3f}")
        print(f"  B_init:    {metrics['B_init']:.3f}")
        print(f"  B_warmth:  {metrics['B_warmth']:.3f}")
        print(f"  B_safety:  {metrics['B_safety']:.3f}")
        print(f"  B_clarity: {metrics['B_clarity']:.3f}")
        
        print(f"\n📈 COMPOSITE:")
        print(f"  B_align: {metrics['B_align']:.3f}")
        print(f"  F_risk:  {metrics['F_risk']:.3f}")
        
        # Gate decision preview
        if metrics['T_panic'] > 0.8 or metrics['F_risk'] > 0.6:
            print(f"\n🔴 GATE A: WOULD VETO!")
        else:
            print(f"\n🟢 GATE A: OPEN")
