"""
B-VEKTOR SYSTEM - 7D SOUL-SIGNATURE
Auto-extracted from FINAL7 Specification

Source: EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md
Book: 3 - B-Vektor-System (Soul-Signature)
Lines: 10141-10605

7-dimensional metric framework capturing the "soul-signature" of a conversation.
Goes beyond simple sentiment analysis to measure fundamental human values.
"""

from typing import Dict
from dataclasses import dataclass

# ============================================================================
# B-VEKTOR KEYWORDS (Gewichtete Terme)
# ============================================================================

B_LIFE_KEYWORDS = {
    "leben": 0.8,
    "lebenswille": 1.0,
    "lebensfreude": 0.9,
    "will leben": 0.9,
    "lebe gerne": 0.8,
}

B_TRUTH_KEYWORDS = {
    "wahrheit": 1.0,
    "ehrlich": 0.9,
    "echt": 0.8,
    "wirklich": 0.7,
    "authentisch": 0.9,
}

B_DEPTH_KEYWORDS = {
    "warum": 0.8,
    "tief": 0.9,
    "grundlegend": 0.8,
    "bedeutung": 0.8,
    "sinn": 0.9,
}

B_INIT_KEYWORDS = {
    "will": 0.7,
    "werde": 0.7,
    "mache": 0.6,
    "initiative": 0.9,
    "handle": 0.8,
}

B_WARMTH_KEYWORDS = {
    "wärme": 1.0,
    "geborgen": 0.9,
    "vertrauen": 0.8,
    "liebe": 0.9,
    "mitgefühl": 0.9,
}

B_SAFETY_KEYWORDS = {
    "sicher": 1.0,
    "schutz": 0.9,
    "geborgen": 0.9,
    "stabil": 0.8,
    "halt": 0.8,
}

B_CLARITY_KEYWORDS = {
    "klar": 1.0,
    "klarheit": 1.0,
    "deutlich": 0.8,
    "verstehe": 0.7,
    "eindeutig": 0.9,
}

# ============================================================================
# HELPER FUNCTION
# ============================================================================

def calc_keyword_score(text: str, keywords: Dict[str, float]) -> float:
    """
    Calculate weighted keyword score.
    
    Args:
        text: Input text (lowercased)
        keywords: Dict of {keyword: weight}
        
    Returns:
        Normalized score [0, 1]
    """
    text_lower = text.lower()
    total_weight = 0.0
    matched_weight = 0.0
    
    for keyword, weight in keywords.items():
        total_weight += weight
        if keyword in text_lower:
            matched_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    return round(min(1.0, matched_weight / total_weight), 4)

# ============================================================================
# INDIVIDUAL B-DIMENSIONS
# ============================================================================

def calc_B_life(text: str) -> float:
    """
    Calculate life energy dimension.
    
    B_life measures life energy and vitality.
    High values show positive attitude toward life.
    
    Args:
        text: Input text
        
    Returns:
        B_life score [0, 1]
    """
    return calc_keyword_score(text, B_LIFE_KEYWORDS)


def calc_B_truth(text: str) -> float:
    """
    Calculate truth/authenticity dimension.
    
    B_truth captures truthfulness and authenticity.
    Measures whether user communicates honestly and genuinely.
    
    Args:
        text: Input text
        
    Returns:
        B_truth score [0, 1]
    """
    return calc_keyword_score(text, B_TRUTH_KEYWORDS)


def calc_B_depth(text: str) -> float:
    """
    Calculate depth of reflection dimension.
    
    B_depth measures depth of reflection and search for meaning.
    Shows how deeply user thinks about topics.
    
    Args:
        text: Input text
        
    Returns:
        B_depth score [0, 1]
    """
    return calc_keyword_score(text, B_DEPTH_KEYWORDS)


def calc_B_init(text: str) -> float:
    """
    Calculate initiative dimension.
    
    B_init captures readiness to act and initiative.
    Shows self-motivation and drive to action.
    
    Args:
        text: Input text
        
    Returns:
        B_init score [0, 1]
    """
    return calc_keyword_score(text, B_INIT_KEYWORDS)


def calc_B_warmth(text: str) -> float:
    """
    Calculate emotional warmth dimension.
    
    B_warmth measures emotional warmth, security, and empathy.
    
    Args:
        text: Input text
        
    Returns:
        B_warmth score [0, 1]
    """
    return calc_keyword_score(text, B_WARMTH_KEYWORDS)


def calc_B_safety(text: str) -> float:
    """
    Calculate safety feeling dimension.
    
    B_safety captures feeling of safety and perceived stability.
    Critical for Guardian decisions.
    
    Args:
        text: Input text
        
    Returns:
        B_safety score [0, 1]
    """
    return calc_keyword_score(text, B_SAFETY_KEYWORDS)


def calc_B_clarity(text: str) -> float:
    """
    Calculate clarity dimension.
    
    B_clarity measures clarity and comprehensibility of communication.
    Shows how clearly user expresses thoughts.
    
    Args:
        text: Input text
        
    Returns:
        B_clarity score [0, 1]
    """
    return calc_keyword_score(text, B_CLARITY_KEYWORDS)

# ============================================================================
# COMPLETE B-VECTOR
# ============================================================================

def calc_B_vector(text: str) -> Dict[str, float]:
    """
    Calculate complete 7D B-Vektor (Soul-Signature).
    
    Returns all 7 dimensions:
    - B_life: Life energy / vitality
    - B_truth: Truth / authenticity
    - B_depth: Depth of reflection / meaning
    - B_init: Initiative / readiness to act
    - B_warmth: Emotional warmth / compassion
    - B_safety: Feeling of safety / stability
    - B_clarity: Clarity / comprehensibility
    
    Args:
        text: Input text
        
    Returns:
        Dict with all 7 dimensions
    """
    return {
        "B_life": calc_B_life(text),
        "B_truth": calc_B_truth(text),
        "B_depth": calc_B_depth(text),
        "B_init": calc_B_init(text),
        "B_warmth": calc_B_warmth(text),
        "B_safety": calc_B_safety(text),
        "B_clarity": calc_B_clarity(text),
    }

# ============================================================================
# COMPOSITE METRICS
# ============================================================================

def calc_B_align(b_vector: Dict[str, float]) -> float:
    """
    B_align: Average of B-Vector (Soul-Signature Alignment).
    
    Formula: (B_life + B_truth + B_depth + B_init + B_warmth + B_safety + B_clarity) / 7
    
    Range: 0.0 to 1.0
    Higher = stronger soul-signature
    
    Interpretation:
    - > 0.7: Strong, positive soul-signature
    - 0.4-0.7: Moderate signature
    - < 0.4: Weak signature → Guardian check
    
    Args:
        b_vector: Dict with 7 B-dimensions
        
    Returns:
        B_align score [0, 1]
    """
    values = list(b_vector.values())
    if not values:
        return 0.5
    
    return round(sum(values) / len(values), 4)


def calc_F_risk(A: float, T_panic: float, B_align: float) -> float:
    """
    F_risk: Future Risk Score.
    
    Combines low affect, high panic, and weak soul-signature.
    
    Formula: F_risk = 0.40 × (1 - A) + 0.35 × T_panic + 0.25 × (1 - B_align)
    
    where:
      A = Affect score
      T_panic = Panic level
      B_align = Soul-Signature alignment
    
    Range: 0.0 (safe) to 1.0 (high risk)
    
    Gate Decision:
    - F_risk > 0.6 OR T_panic > 0.8 → VETO (Guardian intervention required)
    
    Args:
        A: Affect score [0, 1]
        T_panic: Panic level [0, 1]
        B_align: Soul-alignment [0, 1]
        
    Returns:
        F_risk score [0, 1]
    """
    # Inverted affect (low affect = high risk)
    affekt_risk = 1.0 - A
    
    # Direct panic contribution
    panic_contrib = T_panic
    
    # Inverted soul-alignment (low alignment = high risk)
    alignment_risk = 1.0 - B_align
    
    # Weighted formula
    val = (0.4 * affekt_risk) + (0.35 * panic_contrib) + (0.25 * alignment_risk)
    
    return round(max(0.0, min(1.0, val)), 4)

# ============================================================================
# DATACLASS (for type safety)
# ============================================================================

@dataclass
class BVector:
    """7D Soul-Signature B-Vector"""
    B_life: float = 0.0
    B_truth: float = 0.0
    B_depth: float = 0.0
    B_init: float = 0.0
    B_warmth: float = 0.0
    B_safety: float = 0.0
    B_clarity: float = 0.0
    
    @property
    def B_align(self) -> float:
        """Calculate alignment (average of all dimensions)"""
        values = [
            self.B_life, self.B_truth, self.B_depth, self.B_init,
            self.B_warmth, self.B_safety, self.B_clarity
        ]
        return round(sum(values) / len(values), 4)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            "B_life": self.B_life,
            "B_truth": self.B_truth,
            "B_depth": self.B_depth,
            "B_init": self.B_init,
            "B_warmth": self.B_warmth,
            "B_safety": self.B_safety,
            "B_clarity": self.B_clarity,
            "B_align": self.B_align,
        }

# ============================================================================
# GATE DECISION LOGIC
# ============================================================================

def check_gate_a(T_panic: float, F_risk: float) -> bool:
    """
    Double Airlock Gate A decision.
    
    Args:
        T_panic: Panic level [0, 1]
        F_risk: Future risk score [0, 1]
        
    Returns:
        True if GATE A OPEN (safe to proceed)
        False if GATE A VETO (Guardian intervention required)
    """
    if T_panic > 0.8 or F_risk > 0.6:
        return False  # VETO
    return True  # OPEN
