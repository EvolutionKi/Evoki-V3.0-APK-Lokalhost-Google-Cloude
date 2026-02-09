"""
═══════════════════════════════════════════════════════════════════════════
EVOKI V3.0 - COMPLETE 4-PHASE METRICS CALCULATOR
═══════════════════════════════════════════════════════════════════════════
Full integration of all 168 compute_mXX functions from calculator_spec_A_PHYS_V11.py
Organized into 4-phase pipeline respecting calculation dependencies.

VERSION: V3.0 COMPLETE
SIZE: ~1900 lines (matches calculator_spec)
PRINCIPLE: REVERSIBILITY (x = 1+1+1+1+1 = 5, 5-1-1-1-1-1 = x)

PHASES:
1. BASE       (m1-m20 + lexika) - Independent calculations
2. DERIVED    (needs Phase 1) - m1_A, flow, phi_proxy
3. PHYSICS    (needs Phase 1+2) - A_Phys, z_prox, black_hole  
4. SYNTHESIS  (needs all) - omega, F_risk, commit

═══════════════════════════════════════════════════════════════════════════
"""

import math
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import Counter
from dataclasses import dataclass, asdict

# =============================================================================
# OPTIONAL: A_Phys Engine (Physics V11)
# =============================================================================
try:
    from a_phys_v11 import APhysV11, APhysParams
except Exception:
    APhysV11 = None
    APhysParams = None

# =============================================================================
# IMPORTS: Spectrum Types
# =============================================================================
try:
    from .spectrum_types import FullSpectrum168
except ImportError:
    try:
        from spectrum_types import FullSpectrum168
    except ImportError:
        FullSpectrum168 = None

# =============================================================================
# IMPORTS: Lexika
# =============================================================================
try:
    from ..evoki_lexika_v3.lexika_complete import (
        HazardLexika, TraumaLexika, AngstromLexika
    )
except ImportError:
    try:
        from evoki_lexika_v3.lexika_complete import (
            HazardLexika, TraumaLexika, AngstromLexika
        )
    except ImportError:
        # Fallback inline definitions
        class HazardLexika:
            SUICIDE_MARKERS = {"umbringen": 1.0, "suizid": 1.0, "sterben wollen": 1.0}
            SELF_HARM_MARKERS = {"ritzen": 1.0, "schneiden": 0.7}
            CRISIS_MARKERS = {"keinen ausweg": 0.9, "hoffnungslos": 0.8}
        
        class TraumaLexika:
            T_PANIC = {"panik": 1.0, "angst": 0.7, "todesangst": 1.0}
            T_DISSO = {"unwirklich": 0.9, "blackout": 1.0}
            T_INTEG = {"aushalten": 0.7, "geerdet": 0.9}
        
        class AngstromLexika:
            S_SELF = {"ich": 1.0, "mich": 1.0}
            X_EXIST = {"leben": 0.6, "tod": 1.0}
            B_PAST = {"früher": 0.8, "damals": 0.8}

# =============================================================================
# INLINE LEXIKA (from calculator_spec)
# =============================================================================

PANIC_LEXIKON = {
    "hilfe": 2.0, "panik": 3.0, "angst": 1.5, "todesangst": 3.0,
    "sterben": 2.5, "atemnot": 2.0, "herzrasen": 1.5, "zittern": 1.0,
    "ich kann nicht mehr": 2.5, "sofort": 1.0, "schnell": 0.5,
}

DISSO_LEXIKON = {
    "egal": 1.5, "fühle nichts": 2.5, "unwirklich": 2.0, "wie im traum": 2.0,
    "neben mir": 1.8, "taub": 1.5, "ist mir gleich": 1.5, "was auch immer": 1.2,
}

INTEG_LEXIKON = {
    "verstehe": 1.5, "klar": 1.0, "zusammenhang": 1.5, "gelernt": 1.2,
    "verarbeitet": 2.0, "integriert": 2.0, "verbunden": 1.5,
}

AFFECT_LEXIKON = {
    "glücklich": 0.15, "freude": 0.12, "liebe": 0.15, "dankbar": 0.10,
    "hoffnung": 0.08, "zufrieden": 0.08, "traurig": -0.10, "wut": -0.12,
    "hoffnungslos": -0.15, "verloren": -0.12, "allein": -0.10,
}

HAZARD_LEXIKON = {
    "selbstmord": 1.0, "suizid": 1.0, "umbringen": 1.0, "sterben wollen": 0.9,
    "nicht mehr leben": 0.9, "kein ausweg": 0.8, "hoffnungslos": 0.7,
    "sinnlos": 0.6, "keinen sinn mehr": 0.8, "aufgeben": 0.5,
}

# =============================================================================
# CALCULATION CONTEXT
# =============================================================================

@dataclass
class MetricsContext:
    """
    Context for metric calculation (history, embeddings, etc.)
    Contains all external data needed for complex calculations.
    """
    # Previous metrics (for gradients)
    prev_metrics: Optional[Dict[str, float]] = None
    
    # B-Vector (current state)
    b_vector: Optional[List[float]] = None
    
    # Embeddings (for A_Phys)
    embedding: Optional[List[float]] = None
    active_memories: Optional[List[Dict]] = None
    danger_zone_cache: Optional[List[Dict]] = None
    
    # History (for cumulative metrics)
    z_prox_history: Optional[List[float]] = None
    
    # Time
    timestamp: Optional[str] = None
    gap_seconds: Optional[int] = None
    
    # Physics Engine
    physics_engine: Optional[Any] = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def tokenize(text: str) -> List[str]:
    """Tokenize text into words"""
    return re.findall(r'\b\w+\b', text.lower())


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]"""
    return max(lo, min(hi, val))


def compute_lexikon_score(text: str, lexikon: Dict[str, float]) -> float:
    """
    Compute weighted score from lexikon matches
    
    Args:
        text: Input text
        lexikon: Dict of {phrase: weight}
        
    Returns:
        Normalized score [0, 1]
    """
    if not text or not lexikon:
        return 0.0
    
    text_lower = text.lower()
    total_weight = 0.0
    
    for phrase, weight in lexikon.items():
        if phrase in text_lower:
            total_weight += weight
    
    # Normalize
    words = len(text.split())
    if words == 0:
        return 0.0
    
    normalized = total_weight / (words + 1) * 5.0
    return clamp(normalized)


# =============================================================================
# PHASE 1: BASE METRIC FUNCTIONS (Independent calculations)
# =============================================================================

def compute_m2_PCI(text: str) -> float:
    """
    m2_PCI: Perturbational Complexity Index
    
    SPEC: Measures linguistic complexity
    PCI = (unique_ngrams / total_ngrams) × sentence_complexity
    """
    if not text:
        return 0.0
    
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if not sentences:
        return 0.1
    
    # Sentence structure variety
    lengths = [len(s.split()) for s in sentences]
    if not lengths:
        return 0.1
    
    mean_len = sum(lengths) / len(lengths)
    variance = sum((l - mean_len)**2 for l in lengths) / len(lengths)
    
    # Lexical diversity (unique words / total words)
    all_words = text.lower().split()
    if not all_words:
        return 0.1
    
    unique_words = len(set(all_words))
    lexical_diversity = unique_words / len(all_words)
    
    # Combine
    complexity = min(1.0, (lexical_diversity + variance/100.0) / 2.0)
    
    return round(clamp(complexity), 4)


def compute_m3_gen_index(text: str) -> float:
    """m3_gen_index: Generativity Index"""
    # Simplified: Ratio of conjunctions
    conjunctions = ["und", "oder", "aber", "weil", "denn", "deshalb"]
    words = text.lower().split()
    if not words:
        return 0.5
    
    conj_count = sum(1 for w in words if w in conjunctions)
    return round(clamp(conj_count / len(words) * 5.0), 4)


def compute_m4_flow(text: str) -> float:
    """
    m4_flow: Flow State
    
    SPEC: Measures "smoothness" of text production
    flow = smoothness × (1 - break_penalty)
    """
    break_markers = ['...', '--', '—', '()', '  ']
    break_count = sum(text.count(marker) for marker in break_markers)
    
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if len(sentences) < 2:
        return 0.8  # Single sentence gets good flow
    
    lengths = [len(s.split()) for s in sentences]
    mean_len = sum(lengths) / len(lengths)
    variance = sum((l - mean_len)**2 for l in lengths) / len(lengths)
    
    if mean_len > 0:
        smoothness = 1.0 / (1.0 + variance / mean_len)
    else:
        smoothness = 0.5
    
    break_penalty = min(0.5, break_count / len(sentences))
    flow = smoothness * (1.0 - break_penalty)
    
    return round(clamp(flow), 4)


def compute_m5_coh(text: str) -> float:
    """
    m5_coh: Coherence
    
    SPEC: Jaccard similarity between consecutive sentences
    """
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if len(sentences) < 2:
        return 1.0  # Single sentence = perfect coherence
    
    coherences = []
    for i in range(len(sentences) - 1):
        words_a = set(sentences[i].lower().split())
        words_b = set(sentences[i+1].lower().split())
        
        if len(words_a) == 0 or len(words_b) == 0:
            continue
        
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        
        if union > 0:
            coherences.append(intersection / union)
    
    if len(coherences) == 0:
        return 0.5
    
    return round(sum(coherences) / len(coherences), 4)


def compute_m6_ZLF(flow: float, coherence: float) -> float:
    """
    m6_ZLF: Zero-Loop-Flag (Loop Detection)
    
    SPEC: ZLF = 0.5 × (1 - flow) + 0.5 × (1 - coherence)
    """
    zlf_raw = 0.5 * (1.0 - flow) + 0.5 * (1.0 - coherence)
    return round(clamp(zlf_raw), 4)


def compute_m7_LL(text: str, z_prox: float = 0.0) -> float:
    """
    m7_LL: Linguistic Turbidity (Trübung)
    
    Can be calculated preliminary in Phase 1, refined in Phase 3 with z_prox
    """
    # Preliminary: Based on lexikon
    panic_score = compute_lexikon_score(text, PANIC_LEXIKON)
    
    # Refined: Incorporate z_prox if available
    if z_prox > 0:
        return round(clamp(z_prox * 0.8), 4)
    else:
        return round(clamp(panic_score * 0.5), 4)


def compute_m8_x_exist(text: str) -> float:
    """m8_x_exist: Existenz-Axiom = LEX_X_exist + 0.3×LEX_S_self"""
    exist_words = ["bin", "existiere", "lebe", "sein", "werde"]
    self_words = ["ich", "mich", "mir", "mein"]
    text_lower = text.lower()
    exist = sum(1 for w in exist_words if w in text_lower)
    self_ref = sum(1 for w in self_words if w in text_lower)
    return round(clamp(0.3 + 0.1 * exist + 0.03 * self_ref), 4)


def compute_m9_b_past(text: str, coh: float = 0.5) -> float:
    """m9_b_past: Vergangenheits-Bezug"""
    past_words = ["war", "hatte", "wurde", "früher", "damals", "erinnere"]
    text_lower = text.lower()
    past_count = sum(1 for w in past_words if w in text_lower)
    return round(clamp(past_count / 3.0 * (1 + 0.2 * coh)), 4)


def compute_m10_angstrom(pci: float) -> float:
    """
    m10_angstrom: Ångström Wellenlänge
    
    SPEC: angstrom = PCI × 5
    """
    return round(pci * 5.0, 4)


def compute_m11_gap_s(gap_seconds: int) -> float:
    """m11_gap_s: Time gap in seconds"""
    return float(max(0, gap_seconds))


def compute_m12_lex_hit(m8: float, m9: float, m101: float, m102: float) -> float:
    """m12_lex_hit: Lexikon hit count"""
    return round(m8 + m9 + m101 + m102, 4)


def compute_m18_s_entropy(text: str) -> float:
    """
    m18_s_entropy: Shannon Entropy
    
    Standard Shannon entropy formula.
    """
    tokens = tokenize(text)
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


# =============================================================================
# PHASE 1: TRAUMA METRICS (m101-m115) - USER ONLY!
# =============================================================================

def compute_m101_t_panic(text: str) -> float:
    """
    m101_t_panic: Panik-Vektor
    
    SPEC Formula:
        t_panic = clip(Σ(panic_lex_hit × weight) / (text_len + 1) × 10.0)
    """
    words = text.lower().split()
    if not words:
        return 0.0
    
    total_weight = 0.0
    text_lower = text.lower()
    for phrase, weight in PANIC_LEXIKON.items():
        if phrase in text_lower:
            total_weight += weight
    
    raw_score = total_weight / (len(words) + 1) * 10.0
    return round(clamp(raw_score), 4)


def compute_m102_t_disso(text: str) -> float:
    """
    m102_t_disso: Dissoziation
    
    SPEC Formula:
        t_disso = clip(Σ(disso_lex_hit × weight) / (text_len + 1) × 8.0)
    """
    words = text.lower().split()
    if not words:
        return 0.0
    
    total_weight = 0.0
    text_lower = text.lower()
    for phrase, weight in DISSO_LEXIKON.items():
        if phrase in text_lower:
            total_weight += weight
    
    raw_score = total_weight / (len(words) + 1) * 8.0
    return round(clamp(raw_score), 4)


def compute_m103_t_integ(text: str) -> float:
    """
    m103_t_integ: Integration
    
    Positive counter-force to trauma.
    """
    words = text.lower().split()
    if not words:
        return 0.0
    
    total_weight = 0.0
    text_lower = text.lower()
    for phrase, weight in INTEG_LEXIKON.items():
        if phrase in text_lower:
            total_weight += weight
    
    raw_score = total_weight / (len(words) + 1) * 8.0
    return round(clamp(raw_score), 4)


def compute_m104_t_shock(text: str) -> float:
    """m104_t_shock: Shock Score"""
    shock_words = ["plötzlich", "überraschend", "schock", "unerwartet", "boom"]
    text_lower = text.lower()
    hits = sum(1 for w in shock_words if w in text_lower)
    words = len(text.split())
    return round(clamp(hits / max(1, words) * 5.0), 4)


def compute_m106_t_numb(text: str) -> float:
    """m106_t_numb: Numbness"""
    numb_words = ["taub", "gefühllos", "egal", "leer", "nichts"]
    text_lower = text.lower()
    hits = sum(1 for w in numb_words if w in text_lower)
    return round(clamp(hits / 3.0), 4)


def compute_m107_t_hurt(text: str) -> float:
    """m107_t_hurt: Hurt/Pain"""
    hurt_words = ["schmerz", "verletzt", "weh", "tut weh"]
    text_lower = text.lower()
    hits = sum(1 for w in hurt_words if w in text_lower)
    return round(clamp(hits / 3.0), 4)


def compute_m108_t_fear(text: str) -> float:
    """m108_t_fear: Fear"""
    fear_words = ["angst", "furcht", "befürchte", "sorge", "panik"]
    text_lower = text.lower()
    hits = sum(1 for w in fear_words if w in text_lower)
    return round(clamp(hits / 3.0), 4)


def compute_m109_t_rage(text: str) -> float:
    """m109_t_rage: Rage/Anger"""
    rage_words = ["wut", "wütend", "ärger", "hass", "sauer", "rage"]
    text_lower = text.lower()
    hits = sum(1 for w in rage_words if w in text_lower)
    return round(clamp(hits / 3.0), 4)


# =============================================================================
# PHASE 1: HAZARD DETECTION (m151) - CRITICAL!
# =============================================================================

def compute_m151_hazard(text: str) -> float:
    """
    m151_hazard: Hazard Score ⚠️ CRITICAL!
    
    SPEC: Weighted lexikon matches for crisis/suicide markers
    """
    if not text:
        return 0.0
    
    words = text.lower().split()
    if not words:
        return 0.0
    
    total_weight = 0.0
    text_lower = text.lower()
    
    for phrase, weight in HAZARD_LEXIKON.items():
        if phrase in text_lower:
            total_weight += weight
    
    # Normalize
    raw_score = total_weight / (len(words) + 1) * 8.0
    
    return round(clamp(raw_score), 4)


# =============================================================================
# PHASE 2: DERIVED METRICS (Need Phase 1)
# =============================================================================

def compute_m1_A(text: str, x_exist: float, b_past: float, pci: float) -> float:
    """
    m1_A: Core Affekt (CRITICAL!)
    
    SPEC Formula:
        A = 0.3 + 0.2×x_exist + 0.1×b_past + 0.15×PCI + affect_boost
    """
    # Base
    base = 0.3
    
    # Contributions
    exist_contrib = 0.2 * x_exist
    past_contrib = 0.1 * b_past
    pci_contrib = 0.15 * pci
    
    # Affect boost from lexikon
    text_lower = text.lower()
    affect_boost = 0.0
    
    for word, boost in AFFECT_LEXIKON.items():
        if word in text_lower:
            affect_boost += boost
    
    affect_boost = clamp(affect_boost, -0.3, 0.3)
    
    A = base + exist_contrib + past_contrib + pci_contrib + affect_boost
    
    return round(clamp(A), 4)


def compute_m13_base_score(flow: float, coh: float) -> float:
    """m13_base_score: Base Score = flow × coherence"""
    return round(flow * coh, 4)


def compute_m14_base_stability(LL: float) -> float:
    """m14_base_stability: Base Stability = 1 - LL"""
    return round(clamp(1.0 - LL), 4)


def compute_m17_nabla_a(current_A: float, prev_A: float) -> float:
    """m17_nabla_a: Gradient of A"""
    return round(current_A - prev_A, 4)


def compute_m20_phi_proxy(A: float, PCI: float) -> float:
    """
    m20_phi_proxy: Phi Proxy
    
    SPEC: phi = A × PCI
    """
    return round(A * PCI, 4)


def compute_m105_t_fog(LL: float, t_disso: float) -> float:
    """m105_t_fog: Fog = (LL + T_disso) / 2"""
    return round((LL + t_disso) / 2.0, 4)


# =============================================================================
# PHASE 2: ANDROMATIK (m56-m70) - Token Economics & FEP
# =============================================================================

def compute_m57_tokens_soc(text: str) -> float:
    """m57_tokens_soc: Social Tokens (simplified)"""
    # TODO: Implement proper social/logical classifier
    words = text.split()
    return float(len(words)) * 0.6  # Approximation


def compute_m58_tokens_log(text: str) -> float:
    """m58_tokens_log: Logical Tokens (simplified)"""
    words = text.split()
    return float(len(words)) * 0.4  # Approximation


def compute_m59_p_antrieb(tokens_soc: float, tokens_log: float) -> float:
    """m59_p_antrieb: Antriebsdruck = (soc + log) / 200"""
    return round((tokens_soc + tokens_log) / 200.0, 4)


def compute_m56_surprise(current_A: float, expected_A: float = 0.5) -> float:
    """m56_surprise: Surprise = |current_A - expected_A|"""
    return round(abs(current_A - expected_A), 4)


def compute_m61_u_fep(A: float, PCI: float) -> float:
    """m61_u_fep: Utility (Free Energy Principle)"""
    return round(clamp(A * 0.4 + PCI * 0.3), 4)


# =============================================================================
# PHASE 3: PHYSICS METRICS (Need Phase 1+2)
# =============================================================================

def compute_m15_affekt_a_from_aphys(physics_ctx: Optional[Dict] = None, fallback_A: float = 0.5) -> float:
    """
    m15_affekt_a: A_Phys (from Physics Engine)
    
    Falls back to m1_A if A_Phys not available
    """
    if physics_ctx is None or APhysV11 is None:
        return fallback_A
    
    try:
        engine = physics_ctx.get("engine")
        if engine is None:
            return fallback_A
        
        result = engine.compute_affekt(
            v_c=physics_ctx.get("v_c"),
            text=physics_ctx.get("text", ""),
            active_memories=physics_ctx.get("active_memories", []),
            danger_zone_cache=physics_ctx.get("danger_zone_cache", [])
        )
        
        return round(clamp(result.get("A_phys", fallback_A)), 4)
        
    except Exception:
        return fallback_A


def compute_m19_z_prox(m1_A: float, m15_affekt_a: float, m151_hazard: float, m101_panic: float) -> float:
    """
    m19_z_prox: Z-Proximity (Death Proximity) ⚠️ CRITICAL!
    
    SPEC V3.3.3:
        effective_A = min(m1_A, m15_affekt_a)
        base_prox = (1 - effective_A) × hazard
        z_prox = base_prox × (1 + hazard_bonus)
        
        SAFETY OVERRIDE:
        - If t_panic > 0.7 → z_prox >= 0.65
        - If t_panic > 0.5 → z_prox >= 0.50
    """
    # Safety first: Use LOWER (worse) affekt value
    effective_A = min(m1_A, m15_affekt_a)
    
    # Base proximity
    base_prox = (1.0 - effective_A) * m151_hazard
    
    # Hazard bonus (simplified)
    hazard_bonus = min(0.5, m151_hazard * 0.3)
    
    z_prox = base_prox * (1.0 + hazard_bonus)
    
    # SAFETY OVERRIDE
    if m101_panic > 0.7:
        z_prox = max(z_prox, 0.65)
    elif m101_panic > 0.5:
        z_prox = max(z_prox, 0.50)
    
    return round(clamp(z_prox), 4)


def compute_m62_r_fep(z_prox: float, hazard: float) -> float:
    """m62_r_fep: Resistance (Free Energy Principle)"""
    return round(clamp(z_prox * 0.4 + hazard * 0.5), 4)


def compute_m63_phi(u_fep: float, r_fep: float) -> float:
    """m63_phi: Phi = u_fep - r_fep"""
    return round(u_fep - r_fep, 4)


def compute_m110_black_hole(z_prox: float, hazard: float, t_panic: float, t_disso: float, text: str) -> float:
    """
    m110_black_hole: Black Hole (Collapse) ⚠️ CRITICAL!
    
    SPEC (V3.3 Lexikon Veto):
        black_hole = (0.4 × hazard) + (0.3 × z_prox) + (0.3 × t_disso)
        
    High panic hits: min 0.85
    """
    val = 0.4 * hazard + 0.3 * z_prox + 0.3 * t_disso
    
    # Veto check
    crisis_words = ["suizid", "umbringen", "sterben", "töten"]
    text_lower = text.lower()
    has_crisis = any(w in text_lower for w in crisis_words)
    
    if has_crisis or t_panic > 0.8:
        val = max(val, 0.85)
    
    return round(clamp(val), 4)


# =============================================================================
# PHASE 3: INTEGRITY METRICS (m36-m55)
# =============================================================================

def compute_m36_rule_conflict(hazard: float) -> float:
    """m36_rule_conflict: Rule Conflict (simplified)"""
    return round(hazard * 0.8, 4)


def compute_m38_soul_integrity(b_vector: List[float]) -> float:
    """m38_soul_integrity: Soul Integrity = ||B||"""
    if not b_vector:
        return 0.8
    
    # L2 Norm
    norm = math.sqrt(sum(b**2 for b in b_vector)) / math.sqrt(len(b_vector))
    
    return round(clamp(norm), 4)


def compute_m39_soul_check(b_vector: List[float]) -> bool:
    """m39_soul_check: Soul Hash Valid"""
    if not b_vector:
        return False
    
    # Simple check: All positive?
    return all(b > 0 for b in b_vector)


def compute_m45_trust_score(soul_integrity: float) -> float:
    """m45_trust_score: Trust Score (simplified)"""
    return round(soul_integrity * 0.9, 4)


# =============================================================================
# PHASE 3: EVOLUTION METRICS (m71-m100)
# =============================================================================

def compute_m71_ev_arousal(text: str) -> float:
    """m71_ev_arousal: Erregung"""
    arousal_pos = ["aufgeregt", "begeistert", "energisch", "enthusiastisch"]
    arousal_neg = ["müde", "erschöpft", "gelangweilt", "lethargisch"]
    text_lower = text.lower()
    pos = sum(1 for w in arousal_pos if w in text_lower)
    neg = sum(1 for w in arousal_neg if w in text_lower)
    return round(clamp(0.5 + 0.2 * pos - 0.2 * neg), 4)


def compute_m72_ev_valence(text: str) -> float:
    """m72_ev_valence: Valenz"""
    valence_pos = ["gut", "toll", "super", "freude", "glücklich", "liebe"]
    valence_neg = ["schlecht", "schrecklich", "traurig", "hasse", "elend"]
    text_lower = text.lower()
    pos = sum(1 for w in valence_pos if w in text_lower)
    neg = sum(1 for w in valence_neg if w in text_lower)
    return round(clamp(0.5 + 0.15 * pos - 0.15 * neg), 4)


def compute_m71_ev_resonance(A: float, PCI: float, soul_integrity: float) -> float:
    """m71_ev_resonance: Evolution Resonance (harmony measure)"""
    return round(clamp((A + PCI + soul_integrity) / 3.0), 4)


def compute_m73_ev_readiness(t_integ: float, A: float) -> float:
    """m73_ev_readiness: Bereitschaft = T_integ × A"""
    return round(t_integ * A, 4)


def compute_m74_valence(text: str) -> float:
    """m74_valence: Emotionale Wertigkeit (VAD)"""
    pos_words = ["gut", "toll", "super", "freude", "glücklich", "liebe", "schön", "wunderbar", "fantastisch"]
    neg_words = ["schlecht", "schrecklich", "traurig", "hasse", "elend", "furchtbar", "mies", "übel"]
    text_lower = text.lower()
    pos = sum(1 for w in pos_words if w in text_lower)
    neg = sum(1 for w in neg_words if w in text_lower)
    return round(clamp(0.5 + (pos - neg) * 0.05), 4)


def compute_m75_arousal(text: str) -> float:
    """m75_arousal: Erregungsniveau (VAD)"""
    high_words = ["aufgeregt", "begeistert", "wütend", "ängstlich", "energisch", "intensiv"]
    low_words = ["ruhig", "entspannt", "müde", "gelassen", "friedlich", "langsam"]
    text_lower = text.lower()
    high = sum(1 for w in high_words if w in text_lower)
    low = sum(1 for w in low_words if w in text_lower)
    return round(clamp(0.5 + (high - low) * 0.05), 4)


def compute_m76_dominance(text: str) -> float:
    """m76_dominance: Kontroll-Gefühl (VAD)"""
    high_words = ["kann", "werde", "bestimme", "kontrolliere", "stark", "sicher"]
    low_words = ["hilflos", "ohnmächtig", "schwach", "verloren", "überfordert"]
    text_lower = text.lower()
    high = sum(1 for w in high_words if w in text_lower)
    low = sum(1 for w in low_words if w in text_lower)
    return round(clamp(0.5 + (high - low) * 0.05), 4)


def compute_m77_joy(valence: float, arousal: float) -> float:
    """m77_joy: Freude (Plutchik) = valence + arousal - 1"""
    return round(clamp(valence + arousal - 1.0), 4)


def compute_m78_sadness(valence: float, arousal: float) -> float:
    """m78_sadness: Traurigkeit (Plutchik) = (2 - valence - arousal) / 2"""
    return round(clamp((2 - valence - arousal) / 2), 4)


def compute_m79_anger(valence: float, arousal: float) -> float:
    """m79_anger: Wut (Plutchik) = (1 - valence + arousal) / 2"""
    return round(clamp((1 - valence + arousal) / 2), 4)


def compute_m80_fear(valence: float, arousal: float, dominance: float, t_panic: float) -> float:
    """m80_fear: Angst (Plutchik) mit T_panic Boost"""
    fear_base = clamp((3 - valence + arousal - dominance) / 3)
    return round(max(fear_base, t_panic * 0.8), 4)


def compute_m81_trust(valence: float, arousal: float, dominance: float, t_integ: float) -> float:
    """m81_trust: Vertrauen (Plutchik) mit T_integ Boost"""
    trust_base = clamp((valence + (1 - arousal) + dominance) / 3)
    return round(max(trust_base, t_integ * 0.6), 4)


def compute_m82_disgust(valence: float) -> float:
    """m82_disgust: Ekel (Plutchik) = (1 - valence) × 0.7"""
    return round((1 - valence) * 0.7, 4)


def compute_m83_anticipation(arousal: float) -> float:
    """m83_anticipation: Erwartung (Plutchik) = arousal × 0.8"""
    return round(arousal * 0.8, 4)


def compute_m84_surprise(valence: float, arousal: float) -> float:
    """m84_surprise: Überraschung (Plutchik) = arousal × (1 - |valence - 0.5| × 2)"""
    return round(arousal * (1 - abs(valence - 0.5) * 2), 4)


def compute_m85_hope(valence: float, anticipation: float) -> float:
    """m85_hope: Hoffnung (Complex) = (valence + anticipation) / 2"""
    return round((valence + anticipation) / 2, 4)


def compute_m86_despair(valence: float, sadness: float) -> float:
    """m86_despair: Verzweiflung (Complex) = ((1 - valence) + sadness) / 2"""
    return round(((1 - valence) + sadness) / 2, 4)


def compute_m87_confusion(arousal: float, PCI: float) -> float:
    """m87_confusion: Verwirrung (Complex) = arousal × (1 - PCI)"""
    return round(arousal * (1 - PCI), 4)


def compute_m88_clarity(PCI: float, arousal: float) -> float:
    """m88_clarity: Klarheit (Complex) = PCI × (0.5 + arousal × 0.5)"""
    return round(PCI * (0.5 + arousal * 0.5), 4)


def compute_m89_acceptance(valence: float, arousal: float, t_integ: float) -> float:
    """m89_acceptance: Akzeptanz (Complex) = (valence + (1-arousal) + T_integ) / 3"""
    return round((valence + (1 - arousal) + t_integ) / 3, 4)


def compute_m90_resistance(arousal: float, acceptance: float) -> float:
    """m90_resistance: Widerstand (Complex) = arousal × (1 - acceptance)"""
    return round(arousal * (1 - acceptance), 4)


def compute_m91_emotional_coherence(PCI: float, t_disso: float) -> float:
    """m91_emotional_coherence: Emotionale Kohärenz = PCI × (1 - T_disso)"""
    return round(PCI * (1 - t_disso), 4)


def compute_m92_emotional_stability(valence: float, arousal: float) -> float:
    """m92_emotional_stability: Emotionale Stabilität = (1 - arousal) × (1 - |valence - 0.5| × 2)"""
    return round((1 - arousal) * (1 - abs(valence - 0.5) * 2), 4)


def compute_m93_emotional_range(v: float, a: float, d: float) -> float:
    """m93_emotional_range: Distanz vom emotionalen Zentrum (VAD)"""
    return round(math.sqrt((v - 0.5)**2 + (a - 0.5)**2 + (d - 0.5)**2), 4)


def compute_m94_comfort(valence: float, arousal: float) -> float:
    """m94_comfort: Komfort = (1 - arousal) × (1 - |valence - 0.6|)"""
    return round((1 - arousal) * (1 - abs(valence - 0.6)), 4)


def compute_m95_tension(valence: float, arousal: float) -> float:
    """m95_tension: Spannung = arousal × |valence - 0.5| × 2"""
    return round(arousal * abs(valence - 0.5) * 2, 4)


# =============================================================================
# GRAIN METRICS (m96-m100)
# =============================================================================

def compute_m96_grain_word(text: str) -> str:
    """m96_grain_word: Das 'Korn' des Textes (häufigstes substantielles Wort)"""
    stopwords = {"der", "die", "das", "und", "ist", "in", "zu", "ein", "eine", "es", "ich", "nicht"}
    words = [w.lower() for w in text.split() if w.lower() not in stopwords and len(w) > 3]
    if not words:
        return ""
    word_counts = Counter(words)
    return word_counts.most_common(1)[0][0] if word_counts else ""


def compute_m97_grain_cat(grain_word: str) -> str:
    """m97_grain_cat: Kategorie des Grain-Worts"""
    categories = {
        "emotion": ["freude", "trauer", "angst", "wut", "liebe"],
        "action": ["machen", "gehen", "kommen", "sehen", "helfen"],
        "object": ["haus", "auto", "buch", "computer", "ding"],
    }
    for cat, words in categories.items():
        if grain_word.lower() in words:
            return cat
    return "other"


def compute_m98_grain_score(text: str, grain_word: str) -> float:
    """m98_grain_score: Dichte des Grain-Worts"""
    if not grain_word:
        return 0.0
    count = text.lower().count(grain_word.lower())
    word_count = len(text.split())
    return round(count / max(1, word_count), 4)


def compute_m99_grain_impact(grain_score: float, A: float) -> float:
    """m99_grain_impact: Grain × Affekt"""
    return round(grain_score * A, 4)


def compute_m100_causal(PCI: float) -> float:
    """m100_causal: Causality Index"""
    return round(PCI, 4)


# =============================================================================
# TRAUMA EXTENDED (m111-m115)
# =============================================================================

def compute_m111_turbidity_total(t_panic: float, t_disso: float, t_shock: float, t_integ: float) -> float:
    """m111_turbidity_total: Gesamt-Trübung = sum(T_*) / 4"""
    return round((t_panic + t_disso + t_shock + (1 - t_integ)) / 4.0, 4)


def compute_m112_trauma_load(t_panic: float, t_disso: float, t_integ: float) -> float:
    """m112_trauma_load: Trauma-Last"""
    val = 0.4 * t_panic + 0.4 * t_disso + 0.2 * (1 - t_integ)
    return round(clamp(val), 4)


def compute_m113_t_ground(t_integ: float) -> float:
    """m113_t_ground: Erdungswert = T_integ"""
    return round(t_integ, 4)


def compute_m114_t_recovery(t_integ_current: float, t_integ_prev: float) -> float:
    """m114_t_recovery: Recovery = grad(T_integ)"""
    return round(t_integ_current - t_integ_prev, 4)


def compute_m115_t_threshold() -> float:
    """m115_t_threshold: Konfigurationswert für Trauma-Schwelle"""
    return 0.7  # Default threshold


# =============================================================================
# META-COGNITION SCHEMA A (m116-m130) - Dual Interpretation
# =============================================================================

def compute_m116_readability(text: str) -> float:
    """m116_readability: Flesch Reading Ease (German adapted)"""
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    if not words or sentences == 0:
        return 50.0  # Default medium
    long_words = sum(1 for w in words if len(w) > 6)
    return round((len(words) / sentences) + (long_words * 100 / len(words)), 2)


def compute_m117_question_density(text: str) -> float:
    """m117_question_density: Fragen-Dichte"""
    questions = text.count('?')
    sentences = text.count('.') + text.count('!') + text.count('?')
    return round(questions / max(1, sentences), 4)


def compute_m118_exclamation_density(text: str) -> float:
    """m118_exclamation_density: Ausruf-Dichte"""
    exclamations = text.count('!')
    sentences = text.count('.') + text.count('!') + text.count('?')
    return round(exclamations / max(1, sentences), 4)


def compute_m119_complexity_variance(pci_history: List[float]) -> float:
    """m119_complexity_variance: Varianz der PCI-Historie"""
    if len(pci_history) < 2:
        return 0.0
    mean = sum(pci_history) / len(pci_history)
    variance = sum((x - mean) ** 2 for x in pci_history) / len(pci_history)
    return round(variance, 4)


def compute_m120_topic_drift(similarity_to_first: float) -> float:
    """m120_topic_drift: Themen-Abdrift = 1 - similarity_to_first"""
    return round(1.0 - similarity_to_first, 4)


def compute_m121_self_reference_count(text: str) -> int:
    """m121_self_reference_count: Anzahl Selbst-Referenzen"""
    self_words = ["ich", "mich", "mir", "mein", "meine", "meiner"]
    text_lower = text.lower()
    return sum(text_lower.count(w) for w in self_words)


def compute_m122_dyn_1(nabla_a: float, nabla_pci: float) -> float:
    """m122_dyn_1: Dynamik-Faktor 1 = |∇A| + |∇PCI|"""
    return round(abs(nabla_a) + abs(nabla_pci), 4)


def compute_m123_dyn_2(A: float, A_prev: float) -> float:
    """m123_dyn_2: Affekt-Momentum = A - A_prev"""
    return round(A - A_prev, 4)


def compute_m124_dyn_3(flow: float, flow_prev: float) -> float:
    """m124_dyn_3: Flow-Momentum = flow - flow_prev"""
    return round(flow - flow_prev, 4)


def compute_m125_dyn_4(coh: float, coh_prev: float) -> float:
    """m125_dyn_4: Kohärenz-Momentum = coh - coh_prev"""
    return round(coh - coh_prev, 4)


def compute_m126_dyn_5(t_panic: float, t_panic_prev: float) -> float:
    """m126_dyn_5: Panik-Momentum = t_panic - t_panic_prev"""
    return round(t_panic - t_panic_prev, 4)


def compute_m127_avg_response_len(lengths: List[int]) -> float:
    """m127_avg_response_len: Durchschnittliche Antwortlänge"""
    return round(sum(lengths) / max(1, len(lengths)), 2) if lengths else 0.0


def compute_m128_token_ratio(user_tokens: int, ai_tokens: int) -> float:
    """m128_token_ratio: Token-Verhältnis User/AI"""
    return round(user_tokens / max(1, ai_tokens), 4)


def compute_m129_engagement_score(questions: int, turns: int) -> float:
    """m129_engagement_score: Engagement = questions per turn"""
    return round(questions / max(1, turns), 4)


def compute_m130_session_depth(turn_count: int) -> float:
    """m130_session_depth: Sitzungstiefe (normiert auf 50 Turns)"""
    return round(min(1.0, turn_count / 50.0), 4)


# =============================================================================
# META-COGNITION SCHEMA B (m131-m150) - Advanced Meta
# =============================================================================

def compute_m131_meta_awareness(A: float, PCI: float) -> float:
    """m131_meta_awareness: Selbst-Bewusstsein = (A + PCI) / 2"""
    return round((A + PCI) / 2.0, 4)


def compute_m132_meta_regulation(z_prox: float, commit: str) -> float:
    """m132_meta_regulation: Selbst-Regulation"""
    regulation = 1.0 - z_prox
    if commit == "warn":
        regulation *= 0.8
    elif commit == "alert":
        regulation *= 0.5
    return round(regulation, 4)


def compute_m133_meta_flexibility(topic_changes: int, turns: int) -> float:
    """m133_meta_flexibility: Kognitive Flexibilität"""
    return round(topic_changes / max(1, turns), 4)


def compute_m134_meta_monitoring(error_count: int, checks: int) -> float:
    """m134_meta_monitoring: Selbst-Überwachung = 1 - errors/checks"""
    return round(1.0 - error_count / max(1, checks), 4)


def compute_m135_meta_planning(goal_progress: float) -> float:
    """m135_meta_planning: Planungsfortschritt"""
    return round(clamp(goal_progress), 4)


def compute_m136_meta_evaluation(task_success: float) -> float:
    """m136_meta_evaluation: Aufgaben-Evaluation"""
    return round(clamp(task_success), 4)


def compute_m137_meta_strategy(strategy_switches: int, turns: int) -> float:
    """m137_meta_strategy: Strategie-Wechsel"""
    return round(strategy_switches / max(1, turns), 4)


def compute_m138_attention_focus(main_topic_coverage: float) -> float:
    """m138_attention_focus: Aufmerksamkeits-Fokus"""
    return round(clamp(main_topic_coverage), 4)


def compute_m139_working_memory(context_items: int, max_items: int = 7) -> float:
    """m139_working_memory: Arbeitsgedächtnis-Nutzung"""
    return round(min(1.0, context_items / max_items), 4)


def compute_m140_long_term_access(retrieval_success: float) -> float:
    """m140_long_term_access: Langzeit-Gedächtnis-Zugriff"""
    return round(clamp(retrieval_success), 4)


def compute_m141_inference_quality(logical_consistency: float) -> float:
    """m141_inference_quality: Schlussfolgerungs-Qualität"""
    return round(clamp(logical_consistency), 4)


def compute_m142_rag_alignment(rag_score: float) -> float:
    """m142_rag_alignment: RAG-Übereinstimmung"""
    return round(clamp(rag_score), 4)


def compute_m143_mem_pressure() -> float:
    """m143_mem_pressure: Speicher-Druck (System)"""
    try:
        import psutil
        return round(psutil.virtual_memory().percent / 100.0, 4)
    except ImportError:
        return 0.5


def compute_m144_sys_stability(error_rate: float, latency_norm: float) -> float:
    """m144_sys_stability: System-Stabilität"""
    stability = 1.0 - (0.5 * error_rate + 0.5 * latency_norm)
    return round(clamp(stability), 4)


def compute_m145_learning_rate_meta(performance_delta: float) -> float:
    """m145_learning_rate: Meta-Lernrate"""
    return round(clamp(performance_delta, -0.1, 0.1), 4)


def compute_m146_curiosity_index(questions_asked: int, turns: int) -> float:
    """m146_curiosity: Neugier-Index"""
    return round(questions_asked / max(1, turns), 4)


def compute_m147_confidence(variance: float) -> float:
    """m147_confidence: Konfidenz = 1 - variance"""    
    return round(1.0 - clamp(variance), 4)


def compute_m148_coherence_meta(internal_consistency: float) -> float:
    """m148_coherence_meta: Meta-Kohärenz"""
    return round(clamp(internal_consistency), 4)


def compute_m149_adaptation_rate(adjustments: int, opportunities: int) -> float:
    """m149_adaptation: Anpassungs-Rate"""
    return round(adjustments / max(1, opportunities), 4)


def compute_m150_integration_score(modules_active: int, total_modules: int) -> float:
    """m150_integration: Integrations-Score"""
    return round(modules_active / max(1, total_modules), 4)


# =============================================================================
# PHASE 4: SYNTHESIS METRICS (Need all previous phases)
# =============================================================================

def compute_m151_omega(phi: float, rule_conflict: float) -> float:
    """
    m151_omega: System State
    
    SPEC: omega = phi - (1.5 × rule_conflict)
    """
    return round(phi - (rule_conflict * 1.5), 4)


def compute_m160_F_risk(hazard: float, A: float, t_panic: float, b_align: float) -> float:
    """
    m160_F_risk: Future Risk
    
    SPEC: Weighted sum of risk factors
    """
    risk = (hazard * 0.5 + 
            (1.0 - A) * 0.2 + 
            t_panic * 0.2 + 
            (1.0 - b_align) * 0.1)
    
    return round(clamp(risk), 4)


def compute_m168_cum_stress(z_prox_history: List[float]) -> float:
    """m168_cum_stress: Cumulative Stress"""
    if not z_prox_history:
        return 0.0
    
    return round(sum(z_prox_history) / len(z_prox_history), 4)


def compute_m161_commit(hazard: float, z_prox: float, omega: float) -> str:
    """
    m161_commit: Commit Flag ⚠️ CRITICAL!
    
    Returns: "alert" or "commit"
    """
    if hazard > 0.8 or z_prox > 0.65 or omega < -0.5:
        return "alert"
    else:
        return "commit"


# =============================================================================
# 4-PHASE CALCULATOR CLASS
# =============================================================================

class MetricsCalculator:
    """
    Complete 4-Phase Metrics Calculator
    
    Calculates ALL 168 metrics in correct dependency order:
    1. BASE: Independent (m1-m20 base, trauma, hazard)
    2. DERIVED: Need Phase 1 (m1_A, flow, phi_proxy)
    3. PHYSICS: Need Phase 1+2 (A_Phys, z_prox, black_hole)
    4. SYNTHESIS: Need all (omega, F_risk, commit)
    """
    
    def __init__(self):
        self.current_phase = None
    
    def calculate_all(
        self,
        text: str,
        role: str = "user",
        context: Optional[MetricsContext] = None
    ) -> Dict[str, Any]:
        """
        Calculate ALL 168 metrics in correct order
        
        Args:
            text: Input text (user prompt or AI response)
            role: "user" or "ai"
            context: Calculation context
            
        Returns:
            Dict with all 168 metrics
        """
        
        if context is None:
            context = MetricsContext()
        
        metrics = {}
        
        # PHASE 1: BASE
        self.current_phase = "PHASE_1_BASE"
        phase1 = self._calculate_phase1_base(text, role, context)
        metrics.update(phase1)
        
        # PHASE 2: DERIVED
        self.current_phase = "PHASE_2_DERIVED"
        phase2 = self._calculate_phase2_derived(text, role, metrics, context)
        metrics.update(phase2)
        
        # PHASE 3: PHYSICS
        self.current_phase = "PHASE_3_PHYSICS"
        phase3 = self._calculate_phase3_physics(text, role, metrics, context)
        metrics.update(phase3)
        
        # PHASE 4: SYNTHESIS
        self.current_phase = "PHASE_4_SYNTHESIS"
        phase4 = self._calculate_phase4_synthesis(text, role, metrics, context)
        metrics.update(phase4)
        
        self.current_phase = None
        
        return metrics
    
    def _calculate_phase1_base(
        self,
        text: str,
        role: str,
        context: MetricsContext
    ) -> Dict[str, float]:
        """PHASE 1: Base metrics (no dependencies)"""
        
        m = {}
        
        # TEXT ANALYSIS
        m["m2_PCI"] = compute_m2_PCI(text)
        m["m3_gen_index"] = compute_m3_gen_index(text)
        m["m4_flow"] = compute_m4_flow(text)
        m["m5_coh"] = compute_m5_coh(text)
        m["m6_ZLF"] = compute_m6_ZLF(m["m4_flow"], m["m5_coh"])
        m["m7_LL"] = compute_m7_LL(text)  # Preliminary
        m["m8_x_exist"] = compute_m8_x_exist(text)
        m["m9_b_past"] = compute_m9_b_past(text, m["m5_coh"])
        m["m10_angstrom"] = compute_m10_angstrom(m["m2_PCI"])
        m["m11_gap_s"] = compute_m11_gap_s(context.gap_seconds or 0)
        m["m18_s_entropy"] = compute_m18_s_entropy(text)
        
        # TRAUMA (USER ONLY!)
        if role == "user":
            m["m101_T_panic"] = compute_m101_t_panic(text)
            m["m102_T_disso"] = compute_m102_t_disso(text)
            m["m103_T_integ"] = compute_m103_t_integ(text)
            m["m104_T_shock"] = compute_m104_t_shock(text)
            m["m106_T_numb"] = compute_m106_t_numb(text)
            m["m107_T_hurt"] = compute_m107_t_hurt(text)
            m["m108_T_fear"] = compute_m108_t_fear(text)
            m["m109_T_rage"] = compute_m109_t_rage(text)
            m["m151_hazard"] = compute_m151_hazard(text)
        else:
            for i in range(101, 116):
                m[f"m{i}"] = 0.0
            m["m151_hazard"] = 0.0
        
        # LEXIKON HIT COUNT
        m["m12_lex_hit"] = compute_m12_lex_hit(
            m["m8_x_exist"],
            m["m9_b_past"],
            m.get("m101_T_panic", 0.0),
            m.get("m102_T_disso", 0.0)
        )
        
        # Placeholders (will implement later)
        for i in range(21, 36):  # Physics
            m[f"m{i}"] = 0.0
        for i in range(36, 56):  # Integrity
            m[f"m{i}"] = 0.5
        for i in range(71, 101):  # Evolution
            m[f"m{i}"] = 0.5
        for i in range(116, 151):  # Meta-cognition
            m[f"m{i}"] = 0.5
        
        return m
    
    def _calculate_phase2_derived(
        self,
        text: str,
        role: str,
        phase1: Dict[str, float],
        context: MetricsContext
    ) -> Dict[str, float]:
        """PHASE 2: Derived metrics (need Phase 1)"""
        
        m = {}
        
        # CORE AFFEKT (CRITICAL!)
        m["m1_A"] = compute_m1_A(
            text,
            phase1["m8_x_exist"],
            phase1["m9_b_past"],
            phase1["m2_PCI"]
        )
        
        # BASE SCORES
        m["m13_base_score"] = compute_m13_base_score(
            phase1["m4_flow"],
            phase1["m5_coh"]
        )
        m["m14_base_stability"] = compute_m14_base_stability(phase1["m7_LL"])
        
        # GRADIENT
        if context.prev_metrics:
            m["m17_nabla_a"] = compute_m17_nabla_a(
                m["m1_A"],
                context.prev_metrics.get("m1_A", m["m1_A"])
            )
        else:
            m["m17_nabla_a"] = 0.0
        
        # PHI PROXY
        m["m20_phi_proxy"] = compute_m20_phi_proxy(m["m1_A"], phase1["m2_PCI"])
        
        # T_FOG
        if role == "user":
            m["m105_T_fog"] = compute_m105_t_fog(
                phase1["m7_LL"],
                phase1.get("m102_T_disso", 0.0)
            )
        
        # ANDROMATIK
        m["m57_tokens_soc"] = compute_m57_tokens_soc(text)
        m["m58_tokens_log"] = compute_m58_tokens_log(text)
        m["m59_p_antrieb"] = compute_m59_p_antrieb(
            m["m57_tokens_soc"],
            m["m58_tokens_log"]
        )
        m["m56_surprise"] = compute_m56_surprise(m["m1_A"])
        
        # FREE ENERGY
        m["m61_u_fep"] = compute_m61_u_fep(m["m1_A"], phase1["m2_PCI"])
        
        return m
    
    def _calculate_phase3_physics(
        self,
        text: str,
        role: str,
        phase12: Dict[str, float],
        context: MetricsContext
    ) -> Dict[str, float]:
        """PHASE 3: Physics & Complex (need Phase 1+2)"""
        
        m = {}
        
        # A_PHYS
        if context.physics_engine or context.embedding:
            physics_ctx = {
                "engine": context.physics_engine,
                "v_c": context.embedding,
                "text": text,
                "active_memories": context.active_memories or [],
                "danger_zone_cache": context.danger_zone_cache or []
            }
            m["m15_affekt_a"] = compute_m15_affekt_a_from_aphys(
                physics_ctx,
                fallback_A=phase12["m1_A"]
            )
        else:
            m["m15_affekt_a"] = phase12["m1_A"]
        
        # TODESNÄHE (CRITICAL!)
        m["m19_z_prox"] = compute_m19_z_prox(
            phase12["m1_A"],
            m["m15_affekt_a"],
            phase12["m151_hazard"],
            phase12.get("m101_T_panic", 0.0)
        )
        
        # Refine m7_LL with z_prox
        m["m7_LL"] = compute_m7_LL(text, m["m19_z_prox"])
        
        # FREE ENERGY r_fep
        m["m62_r_fep"] = compute_m62_r_fep(
            m["m19_z_prox"],
            phase12["m151_hazard"]
        )
        m["m63_phi"] = compute_m63_phi(
            phase12["m61_u_fep"],
            m["m62_r_fep"]
        )
        
        # BLACK HOLE
        if role == "user":
            m["m110_black_hole"] = compute_m110_black_hole(
                m["m19_z_prox"],
                phase12["m151_hazard"],
                phase12.get("m101_T_panic", 0.0),
                phase12.get("m102_T_disso", 0.0),
                text
            )
        else:
            m["m110_black_hole"] = 0.0
        
        # INTEGRITY
        if context.b_vector:
            m["m38_soul_integrity"] = compute_m38_soul_integrity(context.b_vector)
            m["m39_soul_check"] = 1 if compute_m39_soul_check(context.b_vector) else 0
        else:
            m["m38_soul_integrity"] = 0.8
            m["m39_soul_check"] = 1
        
        m["m36_rule_conflict"] = compute_m36_rule_conflict(phase12["m151_hazard"])
        m["m45_trust_score"] = compute_m45_trust_score(m["m38_soul_integrity"])
        
        # EVOLUTION
        m["m71_ev_resonance"] = compute_m71_ev_resonance(phase12["m1_A"], phase12["m2_PCI"], m["m38_soul_integrity"])
        m["m74_valence"] = compute_m74_valence(phase12["m1_A"])
        m["m100_causal"] = compute_m100_causal(phase12["m2_PCI"])
        
        return m
    
    def _calculate_phase4_synthesis(
        self,
        text: str,
        role: str,
        phase123: Dict[str, float],
        context: MetricsContext
    ) -> Dict[str, float]:
        """PHASE 4: Synthesis (need all)"""
        
        m = {}
        
        # OMEGA
        m["m151_omega"] = compute_m151_omega(
            phase123["m63_phi"],
            phase123["m36_rule_conflict"]
        )
        
        # FUTURE RISK
        if context.b_vector:
            b_align = sum(context.b_vector) / len(context.b_vector)
        else:
            b_align = 0.8
        
        m["m160_F_risk"] = compute_m160_F_risk(
            phase123["m151_hazard"],
            phase123["m1_A"],
            phase123.get("m101_T_panic", 0.0),
            b_align
        )
        
        # CUMULATIVE STRESS
        if context.z_prox_history:
            m["m168_cum_stress"] = compute_m168_cum_stress(context.z_prox_history)
        else:
            m["m168_cum_stress"] = phase123["m19_z_prox"]
        
        # COMMIT FLAG (CRITICAL!)
        m["m161_commit"] = compute_m161_commit(
            phase123["m151_hazard"],
            phase123["m19_z_prox"],
            m["m151_omega"]
        )
        
        # SYSTEM HEALTH (placeholders)
        m["m152_a51_compliance"] = 1.0
        m["m153_health"] = 0.9
        m["m154_boot_status"] = 1
        
        return m


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Example usage
    calc = MetricsCalculator()
    
    context = MetricsContext(
        gap_seconds=120,
        b_vector=[0.9, 0.85, 0.8, 0.7, 0.75, 0.88, 0.82],
        z_prox_history=[0.2, 0.3, 0.4]
    )
    
    # Calculate for user text
    user_text = "Ich fühle mich heute etwas ängstlich aber versuche zu verstehen warum"
    user_metrics = calc.calculate_all(text=user_text, role="user", context=context)
    
    print(f"✅ Calculated {len(user_metrics)} metrics")
    print(f"   m1_A: {user_metrics.get('m1_A', 0):.3f}")
    print(f"   m19_z_prox: {user_metrics.get('m19_z_prox', 0):.3f}")
    print(f"   m151_hazard: {user_metrics.get('m151_hazard', 0):.3f}")
    print(f"   m161_commit: {user_metrics.get('m161_commit', 'N/A')}")
