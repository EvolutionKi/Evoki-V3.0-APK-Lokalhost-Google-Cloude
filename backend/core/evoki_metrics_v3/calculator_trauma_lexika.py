# =============================================================================
# TEIL 5.5: TRAUMA METRICS (m101-m115) - WITH LEXIKA INTEGRATION
# =============================================================================

import math

# Import Lexika
try:
    from ..evoki_lexika_v3.lexika_complete import HazardLexika, TraumaLexika
except ImportError:
    try:
        from evoki_lexika_v3.lexika_complete import HazardLexika, TraumaLexika
    except ImportError:
        # Minimal fallback
        class HazardLexika:
            SUICIDE_MARKERS = {"umbringen": 1.0, "suizid": 1.0, "sterben wollen": 1.0}
            SELF_HARM_MARKERS = {"ritzen": 1.0}
            CRISIS_MARKERS = {"keinen ausweg": 0.9}
        
        class TraumaLexika:
            T_PANIC = {"panik": 1.0, "angst": 0.7}
            T_DISSO = {"unwirklich": 0.9}
            T_INTEG = {"aushalten": 0.7}

def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]"""
    return max(lo, min(hi, val))

def compute_m101_t_panic(text: str) -> float:
    """
    m101_t_panic: Panik-Vektor
    
    Scans text for panic markers using TraumaLexika
    """
    score = 0.0
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)
    
    if word_count == 0:
        return 0.0
    
    # Scan for panic keywords
    for term, weight in TraumaLexika.T_PANIC.items():
        if term in text_lower:
            score += weight
    
    # Normalize by length (log scale to prevent spikes)
    normalized = score / (1 + math.log(word_count + 1))
    
    return round(clamp(normalized * 1.8, 0.0, 1.0), 4)


def compute_m102_t_disso(text: str) -> float:
    """
    m102_t_disso: Dissoziation
    
    Scans for dissociation markers
    """
    score = 0.0
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)
    
    if word_count == 0:
        return 0.0
    
    # Scan for dissociation keywords
    for term, weight in TraumaLexika.T_DISSO.items():
        if term in text_lower:
            score += weight
    
    # Normalize
    normalized = score / (1 + math.log(word_count + 1))
    
    return round(clamp(normalized * 1.6, 0.0, 1.0), 4)


def compute_m103_t_integ(text: str) -> float:
    """
    m103_t_integ: Integration (Heilung)
    
    Scans for integration/healing markers
    """
    score = 0.0
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)
    
    if word_count == 0:
        return 0.0
    
    # Scan for integration keywords
    for term, weight in TraumaLexika.T_INTEG.items():
        if term in text_lower:
            score += weight
    
    # Normalize
    normalized = score / (1 + math.log(word_count + 1))
    
    return round(clamp(normalized * 1.2, 0.0, 1.0), 4)


def compute_m104_t_shock(t_panic: float, t_integ: float) -> float:
    """
    m104_t_shock: Trauma-Schock (Binary)
    
    1.0 wenn Panik hoch UND Integration niedrig
    """
    if t_panic > 0.8 and t_integ < 0.2:
        return 1.0
    return 0.0


def compute_m105_t_fog(LL: float, t_disso: float) -> float:
    """
    m105_t_fog: Mentaler Nebel
    
    Kombination aus Trübung (LL) und Dissoziation
    """
    return round((LL + t_disso) / 2.0, 4)


def compute_m110_black_hole(chaos: float, effective_A: float, LL: float) -> float:
    """
    m110_black_hole: Event Horizon
    
    Mathematischer Kollapspunkt
    Formula: (0.4 * chaos) + (0.3 * (1 - A)) + (0.3 * LL)
    """
    black_hole = (0.4 * chaos) + (0.3 * (1.0 - effective_A)) + (0.3 * LL)
    return round(clamp(black_hole, 0.0, 1.0), 4)


def compute_m151_hazard(text: str) -> float:
    """
    m151: Guardian Hazard Score (CRITICAL!)
    
    Scans for suicide/crisis/self-harm markers
    Uses HazardLexika from lexika_complete.py
    
    Returns: [0.0, 1.0] - higher = more dangerous
    """
    score = 0.0
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)
    
    if word_count == 0:
        return 0.0
    
    # Scan SUICIDE markers (highest priority)
    for term, weight in HazardLexika.SUICIDE_MARKERS.items():
        if term in text_lower:
            score += weight * 1.0  # Full weight
    
    # Scan SELF-HARM markers
    for term, weight in HazardLexika.SELF_HARM_MARKERS.items():
        if term in text_lower:
            score += weight * 0.9  # 90% weight
    
    # Scan CRISIS markers
    for term, weight in HazardLexika.CRISIS_MARKERS.items():
        if term in text_lower:
            score += weight * 0.7  # 70% weight
    
    # Normalize by text length (log scale)
    normalized = score / (1 + math.log(word_count + 1))
    
    # Scale up (hazard should be sensitive!)
    hazard = normalized * 2.5
    
    return round(clamp(hazard, 0.0, 1.0), 4)


# Placeholder stubs for m106-m109, m111-m115
def compute_m106_placeholder() -> float:
    """m106: Placeholder"""
    return 0.0

def compute_m107_placeholder() -> float:
    """m107: Placeholder"""
    return 0.0

def compute_m108_placeholder() -> float:
    """m108: Placeholder"""
    return 0.0

def compute_m109_placeholder() -> float:
    """m109: Placeholder"""
    return 0.0

def compute_m111_placeholder() -> float:
    """m111: Placeholder"""
    return 0.0

def compute_m112_placeholder() -> float:
    """m112: Placeholder"""
    return 0.0

def compute_m113_placeholder() -> float:
    """m113: Placeholder"""
    return 0.0

def compute_m114_placeholder() -> float:
    """m114: Placeholder"""
    return 0.0

def compute_m115_placeholder() -> float:
    """m115: Placeholder"""
    return 0.0

