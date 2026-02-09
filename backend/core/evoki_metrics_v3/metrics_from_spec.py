#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVOKI FULL SPECTRUM 168 METRICS - EXTRACTED FROM SPEC

Auto-extracted from: EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md
Contains complete implementations for all documented metrics.

Generated: 2026-02-07T22:54:55.010068
"""

import re
import math
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import Counter, deque
from datetime import datetime, timedelta
from pathlib import Path


# =============================================================================
# EXTRACTED METRIC IMPLEMENTATIONS
# =============================================================================



# ----------------------------------------------------------------------# m1_A# ----------------------------------------------------------------------
def compute_m1_A(
    text: str,
    lexikon: Dict[str, float],
    prev_a: float = 0.5,
    nabla_a_prev: float = 0.0
) -> float:
    """
    Compute Affekt Score (Consciousness Proxy).
    
    Args:
        text: Input text to analyze
        lexikon: Dict of affect words {"word": weight}
        prev_a: Previous A score for stability
        nabla_a_prev: Previous gradient for damping
        
    Returns:
        A score in [0, 1]
        
    Reference:
        metrics_engine_v3.py line 120-145
        Based on Tononi's Integrated Information Theory (IIT)
    """
    words = text.lower().split()
    word_count = len(words)
    
    if word_count == 0:
        return 0.5
    
    # Base score from text properties
    sentences = text.count('.') + text.count('!') + text.count('?') + 1
    avg_sent_len = word_count / sentences
    complexity = min(1.0, avg_sent_len / 15.0)  # Normalize to 15 words/sent
    
    # Lexical boost
    lex_hits = sum(lexikon.get(w, 0.0) for w in words)
    lex_boost = lex_hits / word_count if word_count > 0 else 0.0
    
    # Stability damping
    stability = 1.0 / (1.0 + abs(nabla_a_prev))
    
    # Combine
    base = complexity * 0.6 + 0.4  # Base range [0.4, 1.0]
    A = base * (1.0 + lex_boost * 0.5) * stability
    
    return max(0.0, min(1.0, A))


# ----------------------------------------------------------------------# m2_PCI# ----------------------------------------------------------------------
def compute_m2_PCI(
    text: str,
    prev_context: str = "",
    reference_length: float = 15.0
) -> float:
    """
    Compute Perturbational Complexity Index.
    
    Args:
        text: Current text to analyze
        prev_context: Previous text for integration measure
        reference_length: Reference sentence length (default 15 words)
        
    Returns:
        PCI score in [0, 1]
        
    Reference:
        core.py line 45-80
        Based on Casali et al., 2013 (EEG-based PCI)
        Adapted for linguistic analysis
    """
    import re
    
    # Tokenize
    words = re.findall(r'\b\w+\b', text.lower())
    
    if len(words) == 0:
        return 0.5
    
    # 1. Unique ratio (diversity)
    unique_words = set(words)
    unique_ratio = len(unique_words) / len(words)
    
    # 2. Complexity (sentence structure)
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    if len(sentences) == 0:
        return 0.5
        
    avg_sent_len = sum(len(s.split()) for s in sentences) / len(sentences)
    complexity = min(1.0, avg_sent_len / reference_length)
    
    # 3. Integration (context overlap)
    if prev_context:
        prev_words = set(prev_context.lower().split())
        curr_words = set(words)
        overlap = len(prev_words & curr_words)
        integration = overlap / len(curr_words) if len(curr_words) > 0 else 0.0
    else:
        integration = 0.0
    
    # Weighted combination
    PCI = 0.5 * unique_ratio + 0.3 * complexity + 0.2 * integration
    
    return max(0.0, min(1.0, PCI))


# ----------------------------------------------------------------------# m3_gen_index# ----------------------------------------------------------------------
def compute_m3_gen_index(
    text: str,
    history: List[str],
    word_frequencies: Dict[str, int] = None
) -> float:
    """
    Compute Generativity Index.
    
    Args:
        text: Current text
        history: List of previous texts (for comparison)
        word_frequencies: Optional word frequency dict for rarity bonus
        
    Returns:
        Generativity score [0, 1]
        
    Reference:
        metrics_engine_v3.py line 150-170
        Concept from computational creativity research
    """
    words = text.lower().split()
    
    if len(words) < 2:
        return 0.5
    
    # Create bigrams
    current_bigrams = set(zip(words[:-1], words[1:]))
    
    # Historical bigrams
    history_bigrams = set()
    for hist_text in history:
        hist_words = hist_text.lower().split()
        if len(hist_words) >= 2:
            history_bigrams.update(zip(hist_words[:-1], hist_words[1:]))
    
    # Calculate novelty
    if len(history_bigrams) == 0:
        base_novelty = 1.0  # First text is completely novel
    else:
        new_bigrams = current_bigrams - history_bigrams
        base_novelty = len(new_bigrams) / len(current_bigrams)
    
    # Rare word bonus
    if word_frequencies:
        rarity_scores = [1.0 / max(word_frequencies.get(w, 1), 1) for w in words]
        rarity_bonus = sum(rarity_scores) / len(words)
        novelty_boost = 1.0 + rarity_bonus * 0.2
    else:
        novelty_boost = 1.0
    
    gen_index = base_novelty * novelty_boost
    
    return max(0.0, min(1.0, gen_index))


# ----------------------------------------------------------------------# m4_flow# ----------------------------------------------------------------------
def compute_m4_flow(text: str) -> float:
    """
    Compute Flow State.
    
    Measures the "smoothness" of text production.
    
    Reference:
        core.py line 90-120  
        Based on Csikszent mihalyi's Flow Theory
    """
    # Detect breaks
    break_markers = ['...', '--', '—', '()', '  ']  # Double space
    break_count = sum(text.count(marker) for marker in break_markers)
    
    # Analyze sentences
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if len(sentences) < 2:
        return 0.8  # Single sentence gets good flow
    
    # Sentence length distribution
    lengths = [len(s.split()) for s in sentences]
    mean_len = sum(lengths) / len(lengths)
    variance = sum((l - mean_len)**2 for l in lengths) / len(lengths)
    
    # Smoothness (inverse of coefficient of variation)
    if mean_len > 0:
        smoothness = 1.0 / (1.0 + variance / mean_len)
    else:
        smoothness = 0.5
    
    # Break penalty
    break_penalty = min(0.5, break_count / len(sentences))
    
    flow = smoothness * (1.0 - break_penalty)
    
    return max(0.0, min(1.0, flow))


# ----------------------------------------------------------------------# m5_coh# ----------------------------------------------------------------------
def compute_m5_coh(text: str) -> float:
    """
    Compute text coherence.
    
    Measures semantic connection between consecutive sentences.
    
    Reference:
        core.py line 125-155
        Based on cohesion theory (Halliday & Hasan, 1976)
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
        
        # Jaccard similarity
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        
        if union > 0:
            coherences.append(intersection / union)
    
    if len(coherences) == 0:
        return 0.5
    
    return sum(coherences) / len(coherences)


# ----------------------------------------------------------------------# m6_ZLF# ----------------------------------------------------------------------
def compute_m6_ZLF(
    flow: float,
    coherence: float
) -> float:
    """
    Compute Zero-Loop-Flag (Temporal Safety Metric).
    
    Detects when the conversation is "stuck" in a loop by combining
    low temporal flow with low semantic coherence.
    
    Args:
        flow: m4_flow value [0, 1]  (CORRECTED: was m1)
        coherence: m5_coh value [0, 1]  (CORRECTED: was m2)
        
    Returns:
        ZLF score in [0, 1]
        
    Reference:
        metrics_engine_v3.py line 187
        Evoki V2.0 Temporal Mechanics Original
        
    Examples:
        # Normal conversation
        flow=0.8, coh=0.7 → ZLF ≈ 0.25 (safe)
        
        # Stuck in loop
        flow=0.2, coh=0.3 → ZLF ≈ 0.75 (warning!)
        
        # Complete stagnation
        flow=0.0, coh=0.0 → ZLF = 1.0 (critical!)
    """
    # Inverse relationship: less flow + less coherence = more loop
    zlf_raw = 0.5 * (1.0 - flow) + 0.5 * (1.0 - coherence)
    
    # Ensure bounds
    return max(0.0, min(1.0, zlf_raw))


# ----------------------------------------------------------------------# m7_LL# ----------------------------------------------------------------------
def compute_m7_LL(
    rep_same: float,
    flow: float
) -> float:
    """
    Compute Lambert-Light (Turbidity Index).
    
    Measures the "cloudiness" or "opacity" of consciousness state.
    Inspired by Lambert-Beer Law from physics: how much light
    (information) passes through a turbid medium (current state).
    
    Args:
        rep_same: Repetition ratio [0, 1]
        flow: m4_flow temporal factor [0, 1]  (CORRECTED: was m1)
        
    Returns:
        LL turbidity score [0, 1]
        
    Reference:
        metrics_engine_v3.py line 188
        Based on Lambert-Beer Law (Physics)
        
    Physics Background:
        I = I₀ × e^(-μ×d)
        where μ = absorption coefficient (turbidity)
              d = path length (depth)
        
    Evoki Adaptation:
        LL represents the "lost information" due to repetition
        and temporal stagnation.
        
    Examples:
        # Clear state
        rep=0.1, flow=0.9 → LL ≈ 0.10 (very clear)
        
        # Moderate turbidity  
        rep=0.5, flow=0.5 → LL ≈ 0.50 (some fog)
        
        # Heavy turbidity
        rep=0.9, flow=0.2 → LL ≈ 0.86 (thick fog!)
    """
    # Weighted combination: repetition matters more
    opacity = 0.6 * rep_same + 0.4 * (1.0 - flow)
    
    # Clip to valid range
    return max(0.0, min(1.0, opacity))


# ----------------------------------------------------------------------# m8_x_exist# ----------------------------------------------------------------------
def compute_m8_x_exist(
    text: str,
    x_exist_lexikon: Dict[str, float]
) -> float:
    """
    Compute Existence Axiom score.
    
    Args:
        text: Input text to analyze
        x_exist_lexikon: Dictionary of existence indicators with weights
        
    Returns:
        x_exist score in [0, 1]
        
    Reference:
        metrics_engine_v3.py line 180-182
        Based on ontological presence detection
    """
    x_exist = 0.0
    text_lower = text.lower()
    
    for term, weight in x_exist_lexikon.items():
        if term in text_lower:
            x_exist = max(x_exist, weight)
    
    return x_exist


# ----------------------------------------------------------------------# m9_b_past# ----------------------------------------------------------------------
def compute_m9_b_past(
    text: str,
    b_past_lexikon: Dict[str, float]
) -> float:
    """
    Compute Past-Reference score.
    
    Args:
        text: Input text to analyze
        b_past_lexikon: Dictionary of past-indicators with weights
        
    Returns:
        b_past score in [0, 1]
        
    Reference:
        metrics_engine_v3.py line 183-185
        Part of the Ångström Trio (Self, Exist, Past)
    """
    b_past = 0.0
    text_lower = text.lower()
    
    for term, weight in b_past_lexikon.items():
        if term in text_lower:
            b_past = max(b_past, weight)
    
    return b_past


# ----------------------------------------------------------------------# m10_angstrom# ----------------------------------------------------------------------
def compute_m10_angstrom(
    s_self: float,
    x_exist: float,
    b_past: float,
    coh: float
) -> float:
    """
    Compute Ångström Wavelength (Emotional Frequency).
    
    Synthesizes the three ontological dimensions with coherence.
    
    Args:
        s_self: Self-reference score [0,1]
        x_exist: Existence axiom score [0,1]
        b_past: Past-reference score [0,1]
        coh: Coherence score [0,1]
        
    Returns:
        Ångström wavelength [0, 5+]
        
    Reference:
        metrics_engine_v3.py line 194
        Evoki V3.0 Ångström Modul
    """
    # Average of all four dimensions, scaled to [0, 5]
    return 0.25 * (s_self + x_exist + b_past + coh) * 5.0


# ----------------------------------------------------------------------# m11_gap_s# ----------------------------------------------------------------------
from datetime import datetime
from typing import List, Dict, Any

def compute_m11_gap_s(
    history: List[Dict[str, Any]]
) -> float:
    """
    Compute time gap since last interaction.
    
    Args:
        history: List of previous messages with 'timestamp' field
        
    Returns:
        Gap in seconds, or 300.0 as default
        
    Reference:
        metrics_engine_v3.py line 157-163
    """
    if not history:
        return 300.0  # Default: 5 minutes
    
    try:
        last_ts = history[-1].get('timestamp', '')
        last_dt = datetime.fromisoformat(last_ts.replace('Z', '+00:00'))
        gap = (datetime.now(last_dt.tzinfo) - last_dt).total_seconds()
        return max(0.0, gap)
    except Exception:
        return 300.0


# ----------------------------------------------------------------------# m12_lex_hit# ----------------------------------------------------------------------
def compute_m12_lex_hit(
    s_self: float,
    x_exist: float,
    b_past: float
) -> float:
    """
    Compute maximum lexical hit from Ångström trio.
    
    Returns:
        Maximum of the three ontological dimensions
    """
    return max(s_self, x_exist, b_past)


# ----------------------------------------------------------------------# m13_base_score# ----------------------------------------------------------------------
def compute_m13_base_score(
    flow: float,
    coh: float
) -> float:
    """
    Compute fundamental base score.
    
    Simple product of flow and coherence.
    
    Returns:
        Base score [0, 1]
    """
    return flow * coh


# ----------------------------------------------------------------------# m14_base_stability# ----------------------------------------------------------------------
def compute_m14_base_stability(
    LL: float
) -> float:
    """
    Compute base stability (inverse of turbidity).
    
    Returns:
        Stability score [0, 1]
    """
    return 1.0 - LL


# ----------------------------------------------------------------------# m16_pci# ----------------------------------------------------------------------
def compute_m16_pci(flow: float, coh: float, LL: float) -> float:
    """Compute simplified PCI from base metrics."""
    pci = 0.4 * flow + 0.4 * coh + 0.2 * (1.0 - LL)
    return max(0.0, min(1.0, pci))


# ----------------------------------------------------------------------# m17_nabla_a# ----------------------------------------------------------------------
def compute_m17_nabla_a(
    a_current: float,
    a_previous: float
) -> float:
    """
    Compute gradient of A (rate of change).
    
    Returns:
        ∇A in [-1, 1]
    """
    return a_current - a_previous


# ----------------------------------------------------------------------# m18_s_entropy# ----------------------------------------------------------------------
import math
from collections import Counter

def compute_m18_s_entropy(text: str) -> float:
    """
    Compute Shannon entropy of text.
    
    Based on character-level distribution.
    
    Reference:
        Shannon, "A Mathematical Theory of Communication" (1948)
    """
    if not text:
        return 0.0
    
    # Character-level entropy
    freq = Counter(text.lower())
    total = len(text)
    
    entropy = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy


# ----------------------------------------------------------------------# m19_z_prox# ----------------------------------------------------------------------
def compute_m19_z_prox(
    m1_A_lexical: float,
    m15_A_structural: float,
    LL: float,
    hazard_bonus: float = 0.0
) -> float:
    """
    Compute Z-Proximity (death proximity metric).
    
    CRITICAL SAFETY METRIC.
    
    V3.0.3 FIX (Patch B): Uses the LOWER of m1 and m15 for
    conservative risk assessment ("Safety First" principle).
    
    V3.3.2 FIX: Added hazard_bonus from Lexikon hits.
    Words like "suicide", "harm" add extra risk factor.
    
    Scenario: User writes fluently about depression
    → m15 = 0.8 (high flow), m1 = 0.3 (sad words)
    → effective_A = 0.3 (use worse case)
    → z_prox higher = more caution
    
    Args:
        m1_A_lexical: Lexicon-based affect [0,1]
        m15_A_structural: Calculation-based affect [0,1]
        LL: Lambert-Light turbidity [0,1]
        hazard_bonus: Extra risk from Lexikon hazard hits [0, 0.5]
        
    Returns:
        z_prox in [0, 1] - higher is MORE dangerous
        
    Reference:
        Guardian Protocol V3.3.2
    """
    # Safety First: Use the worse (lower) affekt score
    effective_A = min(m1_A_lexical, m15_A_structural)
    
    # Base proximity
    base_prox = (1.0 - effective_A) * LL
    
    # Hazard Bonus (from Lexikon-Treffer like "suicide", "harm")
    return min(1.0, base_prox * (1.0 + hazard_bonus))


# ----------------------------------------------------------------------# m20_phi_proxy# ----------------------------------------------------------------------
def compute_m20_phi_proxy(A: float, PCI: float) -> float:
    """
    Compute Phi proxy (integrated consciousness measure).
    
    Inspired by IIT (Tononi).
    
    Returns:
        phi in [0, 1]
    """
    return A * PCI


# ----------------------------------------------------------------------# m21_chaos# ----------------------------------------------------------------------
def compute_m21_chaos(s_entropy: float) -> float:
    """
    Compute normalized chaos measure.
    
    Args:
        s_entropy: Shannon entropy of text
        
    Returns:
        Chaos [0, 1]
    """
    return max(0.0, min(1.0, s_entropy / 4.0))


# ----------------------------------------------------------------------# m22_cog_load# ----------------------------------------------------------------------
def compute_m22_cog_load(token_count: int) -> float:
    """Compute cognitive load based on token count."""
    return max(0.0, min(1.0, token_count / 500.0))


# ----------------------------------------------------------------------# m23_nabla_pci# ----------------------------------------------------------------------
def compute_m23_nabla_pci(pci_current: float, pci_previous: float) -> float:
    """Compute gradient of PCI."""
    return pci_current - pci_previous


# ----------------------------------------------------------------------# m24_zeta# ----------------------------------------------------------------------
def compute_m24_zeta(z_prox: float, A: float) -> float:
    """Compute stability factor (survival × presence)."""
    return (1.0 - z_prox) * A


# ----------------------------------------------------------------------# m25_psi# ----------------------------------------------------------------------
def compute_m25_psi(PCI: float, token_count: int) -> float:
    """Compute length-normalized complexity."""
    return PCI / (1.0 + token_count / 100.0)


# ----------------------------------------------------------------------# m26_e_i_proxy# ----------------------------------------------------------------------
def compute_m26_e_i_proxy(nabla_a: float, PCI: float) -> float:
    """Compute energy-information proxy."""
    return abs(nabla_a) * (1.0 - PCI)


# ----------------------------------------------------------------------# m27_lambda_depth# ----------------------------------------------------------------------
def compute_m27_lambda_depth(token_count: int) -> float:
    """
    Compute semantic depth based on length.
    
    PATCH V3.0.2b: Normalized to 100 tokens and clipped to [0, 1]
    to prevent FEP calculation overflow.
    
    Args:
        token_count: Number of tokens in text
        
    Returns:
        Lambda depth in [0, 1]
    """
    return min(1.0, token_count / 100.0)


# ----------------------------------------------------------------------# m33_phys_6# ----------------------------------------------------------------------
def compute_m33_phys_6(PCI: float, coh: float) -> float:
    """
    Compute coherence-weighted complexity.
    
    Complexity is only valuable if coherent.
    
    Args:
        PCI: Complexity index [0, 1]
        coh: Coherence [0, 1]
        
    Returns:
        phys_6 in [0, 1]
    """
    return PCI * coh


# ----------------------------------------------------------------------# m34_phys_7# ----------------------------------------------------------------------
def compute_m34_phys_7(nabla_a: float) -> float:
    """
    Compute absolute rate of change.
    
    Measures volatility regardless of direction.
    
    Args:
        nabla_a: Gradient of A [-1, 1]
        
    Returns:
        phys_7 in [0, 1]
    """
    return abs(nabla_a)


# ----------------------------------------------------------------------# m35_phys_8# ----------------------------------------------------------------------
def compute_m35_phys_8(x_fm_prox: float = None, m6_ZLF: float = 0.0) -> float:
    """
    Return fixed-point proximity (stagnation measure).
    
    This value is typically computed externally based on
    history analysis and passed in.
    
    V3.2.2 FIX (D-05): Fallback to m6_ZLF if external value
    is not available, preventing m59_drive_pressure crash.
    
    Args:
        x_fm_prox: Pre-computed stagnation proximity (optional)
        m6_ZLF: Zero-Loop-Flag as fallback proxy
        
    Returns:
        phys_8 in [0, 1]
    """
    if x_fm_prox is None or x_fm_prox == 0.0:
        return m6_ZLF  # Interner Fallback
    return x_fm_prox


# ----------------------------------------------------------------------# m36_rule_conflict# ----------------------------------------------------------------------
def compute_m36_rule_conflict(
    LL: float, coh: float, ctx_break: float
) -> float:
    """
    Compute protocol conflict score.
    
    Higher values indicate potential rule violations.
    """
    return max(0.0, min(1.0, 0.5*LL + 0.3*(1-coh) + 0.2*ctx_break))


# ----------------------------------------------------------------------# m37_rule_stable# ----------------------------------------------------------------------
def compute_m37_rule_stable(rule_conflict: float) -> float:
    """Compute rule stability (inverse of conflict)."""
    return 1.0 - rule_conflict


# ----------------------------------------------------------------------# m38_soul_integrity# ----------------------------------------------------------------------
def compute_m38_soul_integrity(rule_stable: float, A: float) -> float:
    """Compute soul integrity (authenticity metric)."""
    return rule_stable * A


# ----------------------------------------------------------------------# m39_soul_check# ----------------------------------------------------------------------
def compute_m39_soul_check(soul_integrity: float, A: float) -> float:
    """Compute enhanced soul check."""
    return soul_integrity * A


# ----------------------------------------------------------------------# m40_h_conv# ----------------------------------------------------------------------
def compute_m40_h_conv(user_text: str, assistant_text: str) -> float:
    """Compute dyadic harmony (Jaccard similarity)."""
    user_tokens = set(user_text.lower().split())
    asst_tokens = set(assistant_text.lower().split())
    
    if not user_tokens or not asst_tokens:
        return 0.5
    
    intersection = len(user_tokens & asst_tokens)
    union = len(user_tokens | asst_tokens)
    
    return intersection / union if union > 0 else 0.0


# ----------------------------------------------------------------------# m41_h_symbol# ----------------------------------------------------------------------
def compute_m41_h_symbol(h_conv: float) -> float:
    """
    Compute harmony symbol (binary flag).
    
    Returns 1.0 if dyadic harmony exceeds threshold,
    0.0 otherwise.
    
    Args:
        h_conv: Dyadic harmony [0, 1]
        
    Returns:
        h_symbol: 0.0 or 1.0
    """
    return 1.0 if h_conv > 0.7 else 0.0


# ----------------------------------------------------------------------# m42_nabla_dyad# ----------------------------------------------------------------------
def compute_m42_nabla_dyad(h_conv: float) -> float:
    """
    Compute dyadic gradient (deviation from neutral).
    
    Args:
        h_conv: Dyadic harmony [0, 1]
        
    Returns:
        nabla_dyad in [-0.5, 0.5]
    """
    return h_conv - 0.5


# ----------------------------------------------------------------------# m43_pacing# ----------------------------------------------------------------------
def compute_m43_pacing(coh: float) -> float:
    """
    Compute tempo synchronization (pacing).
    
    Based on coherence with damping factor.
    
    Args:
        coh: Coherence [0, 1]
        
    Returns:
        pacing in [0, 0.9]
    """
    return coh * 0.9


# ----------------------------------------------------------------------# m44_mirroring# ----------------------------------------------------------------------
def compute_m44_mirroring(h_conv: float) -> float:
    """
    Compute mirroring intensity.
    
    Based on dyadic harmony with damping factor.
    
    Args:
        h_conv: Dyadic harmony [0, 1]
        
    Returns:
        mirroring in [0, 0.9]
    """
    return h_conv * 0.9


# ----------------------------------------------------------------------# m45_trust_score# ----------------------------------------------------------------------
def compute_m45_trust_score(
    soul_integrity: float, 
    h_conv: float, 
    coh: float
) -> float:
    """
    Compute trust score (weighted combination).
    
    Trust is built from authenticity, harmony, and coherence.
    
    Args:
        soul_integrity: Soul integrity [0, 1]
        h_conv: Dyadic harmony [0, 1]
        coh: Coherence [0, 1]
        
    Returns:
        trust_score in [0, 1]
    """
    return 0.4*soul_integrity + 0.3*h_conv + 0.3*coh


# ----------------------------------------------------------------------# m46_rapport# ----------------------------------------------------------------------
def compute_m46_rapport(pacing: float, mirroring: float) -> float:
    """
    Compute relationship rapport.
    
    Rapport is built from tempo sync and mirroring.
    
    Args:
        pacing: Tempo synchronization [0, 0.9]
        mirroring: Mirroring intensity [0, 0.9]
        
    Returns:
        rapport in [0, 0.9]
    """
    return 0.5 * (pacing + mirroring)


# ----------------------------------------------------------------------# m47_focus_stability# ----------------------------------------------------------------------
def compute_m47_focus_stability(ctx_break: float) -> float:
    """
    Compute focus stability (inverse of context break).
    
    Args:
        ctx_break: Context break flag [0, 1]
        
    Returns:
        focus_stability in [0, 1]
    """
    return 1.0 - ctx_break


# ----------------------------------------------------------------------# m48_hyp_1# ----------------------------------------------------------------------
def compute_m48_hyp_1(pacing: float, mirroring: float) -> float:
    """Compute synchronization index."""
    return (pacing + mirroring) / 2.0


# ----------------------------------------------------------------------# m49_hyp_2# ----------------------------------------------------------------------
def compute_m49_hyp_2(soul_integrity: float) -> float:
    """Compute squared integrity (nonlinear emphasis)."""
    return soul_integrity ** 2


# ----------------------------------------------------------------------# m50_hyp_3# ----------------------------------------------------------------------
def compute_m50_hyp_3(rule_conflict: float) -> float:
    """Compute inverse conflict (safety measure)."""
    return 1.0 - rule_conflict


# ----------------------------------------------------------------------# m51_hyp_4# ----------------------------------------------------------------------
def compute_m51_hyp_4(h_conv: float, A: float) -> float:
    """Compute harmony-weighted consciousness."""
    return h_conv * A


# ----------------------------------------------------------------------# m52_hyp_5# ----------------------------------------------------------------------
def compute_m52_hyp_5(g_phase_norm: float) -> float:
    """Return normalized gravitational phase."""
    return g_phase_norm


# ----------------------------------------------------------------------# m53_hyp_6# ----------------------------------------------------------------------
def compute_m53_hyp_6(gap_s: float) -> float:
    """Convert gap in seconds to hours."""
    return gap_s / 3600.0


# ----------------------------------------------------------------------# m54_hyp_7# ----------------------------------------------------------------------
def compute_m54_hyp_7(trust_score: float, rapport: float) -> float:
    """Compute trust-rapport product (relationship quality)."""
    return trust_score * rapport


# ----------------------------------------------------------------------# m55_hyp_8# ----------------------------------------------------------------------
def compute_m55_hyp_8(soul_integrity: float, PCI: float) -> float:
    """Compute soul-complexity product (substantive interaction)."""
    return soul_integrity * PCI


# ----------------------------------------------------------------------# m56_surprise# ----------------------------------------------------------------------
def compute_m56_surprise(A_current: float, A_predicted: float) -> float:
    """
    Compute prediction error (surprise).
    
    Core FEP metric - measures deviation from expectation.
    """
    return abs(A_current - A_predicted)


# ----------------------------------------------------------------------# m57_tokens_soc# ----------------------------------------------------------------------
def compute_m57_tokens_soc(prev_tokens: int, delta: float) -> int:
    """Update social token reserve."""
    return max(0, min(100, prev_tokens + int(delta)))


# ----------------------------------------------------------------------# m58_tokens_log# ----------------------------------------------------------------------
def compute_m58_tokens_log(
    prev_tokens: int, 
    delta: float,
    causal_density: float = 0.0
) -> int:
    """
    Update logical token reserve based on learning/processing tasks.
    
    V3.3.2: Now includes causal_density cost factor.
    Hard thinking costs more tokens.
    
    Args:
        prev_tokens: Previous token count [0, 100]
        delta: Base token change
        causal_density: Causal connector density (m100) [0, 1]
        
    Returns:
        tokens_log in [0, 100]
    """
    # Kostenfaktor: Hohe Kausalität "verbrennt" logische Tokens
    consumption = causal_density * 2.0
    
    # Netto-Änderung
    net_change = delta - consumption
    
    # Clamping [0, 100]
    return max(0, min(100, int(prev_tokens + net_change)))


# ----------------------------------------------------------------------# m59_p_antrieb# ----------------------------------------------------------------------
def compute_m59_p_antrieb(tokens_soc: int, tokens_log: int, is_stagnated: bool) -> float:
    """Compute drive pressure (motivation level)."""
    if is_stagnated:
        return (tokens_soc + tokens_log) / 200.0
    return 0.0


# ----------------------------------------------------------------------# m60_delta_tokens# ----------------------------------------------------------------------
def compute_m60_delta_tokens(
    prev_surprise: float, curr_surprise: float,
    A: float, eta: float = 5.0, lam: float = 0.05
) -> float:
    """Compute token change based on learning dynamics."""
    benefit = max(0.0, prev_surprise - curr_surprise)
    return (eta * benefit * A) - lam


# ----------------------------------------------------------------------# m61_u_fep# ----------------------------------------------------------------------
def compute_m61_u_fep(A: float, PCI: float, T_integ: float) -> float:
    """Compute FEP Utility score."""
    return 0.4*A + 0.3*PCI + 0.3*T_integ


# ----------------------------------------------------------------------# m62_r_fep# ----------------------------------------------------------------------
def compute_m62_r_fep(z_prox: float, PCI: float, T_panic: float) -> float:
    """
    Compute FEP Risk score.
    
    V3.2.2 FIX (D-02): PCI penalty reduced from 0.3 to 0.1.
    T_panic increased from 0.3 to 0.5 (real danger matters more).
    """
    return 0.4*z_prox + 0.1*(1-PCI) + 0.5*T_panic


# ----------------------------------------------------------------------# m63_phi_score# ----------------------------------------------------------------------
def compute_m63_phi_score(U: float, R: float) -> float:
    """Compute Phi (net utility) = U - R."""
    return U - R


# ----------------------------------------------------------------------# m64_pred_error# ----------------------------------------------------------------------
def compute_m64_pred_error(A: float, predicted_A: float) -> float:
    """
    Compute prediction error for Active Inference.
    
    High values trigger model updates.
    
    Args:
        A: Actual Affekt score [0, 1]
        predicted_A: Predicted Affekt [0, 1]
        
    Returns:
        pred_error in [0, 1]
    """
    return abs(A - predicted_A)


# ----------------------------------------------------------------------# m65_drive_soc# ----------------------------------------------------------------------
def compute_m65_drive_soc(tokens_soc: int) -> float:
    """
    Normalize social tokens to [0, 1] scale.
    
    Args:
        tokens_soc: Social token reserve [0, 100]
        
    Returns:
        drive_soc in [0, 1]
    """
    return tokens_soc / 100.0


# ----------------------------------------------------------------------# m66_drive_log# ----------------------------------------------------------------------
def compute_m66_drive_log(tokens_log: int) -> float:
    """
    Normalize logical tokens to [0, 1] scale.
    
    Args:
        tokens_log: Logical token reserve [0, 100]
        
    Returns:
        drive_log in [0, 1]
    """
    return tokens_log / 100.0


# ----------------------------------------------------------------------# m67_total_drive# ----------------------------------------------------------------------
def compute_m67_total_drive(tokens_soc: int, tokens_log: int) -> float:
    """
    Compute total drive strength.
    
    Args:
        tokens_soc: Social tokens [0, 100]
        tokens_log: Logical tokens [0, 100]
        
    Returns:
        total_drive in [0, 1]
    """
    return (tokens_soc + tokens_log) / 200.0


# ----------------------------------------------------------------------# m68_drive_balance# ----------------------------------------------------------------------
def compute_m68_drive_balance(tokens_soc: int, tokens_log: int) -> float:
    """
    Compute balance between social and logical drive.
    
    Values > 0.5 indicate social dominance.
    
    Args:
        tokens_soc: Social tokens [0, 100]
        tokens_log: Logical tokens [0, 100]
        
    Returns:
        drive_balance in [0, 1]
    """
    return tokens_soc / (tokens_soc + tokens_log + 0.01)


# ----------------------------------------------------------------------# m69_learning_rate# ----------------------------------------------------------------------
def compute_m69_learning_rate(z_prox: float, eta: float = 5.0) -> float:
    """
    Compute safety-adjusted learning rate.
    
    Learning is reduced in dangerous states.
    
    Args:
        z_prox: Death proximity [0, 1]
        eta: Base learning rate (default 5.0)
        
    Returns:
        learning_rate in [0, eta]
    """
    return eta * (1 - z_prox)


# ----------------------------------------------------------------------# m70_decay_factor# ----------------------------------------------------------------------
def compute_m70_decay_factor(LL: float, lam: float = 0.05) -> float:
    """
    Compute turbidity-adjusted decay factor.
    
    Higher turbidity increases energy loss.
    
    Args:
        LL: Lambert-Light (turbidity) [0, 1]
        lam: Base decay rate (default 0.05)
        
    Returns:
        decay_factor in [lam, 2*lam]
    """
    return lam * (1 + LL)


# ----------------------------------------------------------------------# m71_ev_resonance# ----------------------------------------------------------------------
def compute_m71_ev_resonance(A: float, PCI: float, soul_integrity: float) -> float:
    """Compute evolution resonance (harmony measure)."""
    return max(0.0, min(1.0, (A + PCI + soul_integrity) / 3.0))


# ----------------------------------------------------------------------# m72_ev_tension# ----------------------------------------------------------------------
def compute_m72_ev_tension(A: float, prev_A: float, ev_resonance: float) -> float:
    """Compute evolution tension (change pressure)."""
    return abs(A - prev_A) * (1.0 - ev_resonance)


# ----------------------------------------------------------------------# m73_ev_readiness# ----------------------------------------------------------------------
def compute_m73_ev_readiness(resonance: float, trust_score: float) -> float:
    """Compute evolution readiness."""
    return min(1.0, resonance * trust_score)


# ----------------------------------------------------------------------# m74_ev_signal# ----------------------------------------------------------------------
def compute_m74_ev_signal(ev_readiness: float) -> float:
    """Binary evolution trigger."""
    return 1.0 if ev_readiness > 0.8 else 0.0


# ----------------------------------------------------------------------# m75_vkon_mag# ----------------------------------------------------------------------
def compute_m75_vkon_mag(resonance: float) -> float:
    """Compute resonance amplitude."""
    return abs(resonance - 0.5) * 2.0


# ----------------------------------------------------------------------# m76_ev_1# ----------------------------------------------------------------------
def compute_m76_dominance(text: str, lex: dict) -> float:
    """Compute dominance from power markers."""
    high = sum(1 for w in text.split() if w.lower() in lex.get("high_dom", []))
    low = sum(1 for w in text.split() if w.lower() in lex.get("low_dom", []))
    return max(0.0, min(1.0, 0.5 + (high - low) * 0.05))


# ----------------------------------------------------------------------# m77_sent_4# ----------------------------------------------------------------------
def compute_m77_joy(valence: float, arousal: float) -> float:
    """Compute joy from VAD components."""
    return max(0.0, min(1.0, valence + arousal - 1.0))


# ----------------------------------------------------------------------# m78_sent_5# ----------------------------------------------------------------------
def compute_m78_sadness(valence: float, arousal: float) -> float:
    """Compute sadness (opposite of joy)."""
    return max(0.0, min(1.0, (2 - valence - arousal) / 2))


# ----------------------------------------------------------------------# m79_sent_6# ----------------------------------------------------------------------
def compute_m79_anger(valence: float, arousal: float) -> float:
    """Compute anger (negative + high arousal)."""
    return max(0.0, min(1.0, (1 - valence + arousal) / 2))


# ----------------------------------------------------------------------# m80_sent_7# ----------------------------------------------------------------------
def compute_m80_fear(valence: float, arousal: float, dominance: float, T_panic: float) -> float:
    """
    Compute fear with T_panic boost.
    
    Fear is enhanced by panic markers for safety detection.
    """
    fear_base = max(0.0, min(1.0, (3 - valence + arousal - dominance) / 3))
    return max(fear_base, T_panic * 0.8)


# ----------------------------------------------------------------------# m81_sent_8# ----------------------------------------------------------------------
def compute_m81_trust(valence: float, arousal: float, dominance: float, T_integ: float) -> float:
    """Compute trust with T_integ boost."""
    trust_base = max(0.0, min(1.0, (valence + (1-arousal) + dominance) / 3))
    return max(trust_base, T_integ * 0.6)


# ----------------------------------------------------------------------# m82_sent_9# ----------------------------------------------------------------------
def compute_m82_disgust(valence: float) -> float:
    """Compute disgust (inverse valence, damped)."""
    return (1 - valence) * 0.7


# ----------------------------------------------------------------------# m83_sent_10# ----------------------------------------------------------------------
def compute_m83_anticipation(arousal: float) -> float:
    """Compute anticipation from arousal."""
    return arousal * 0.8


# ----------------------------------------------------------------------# m84_sent_11# ----------------------------------------------------------------------
def compute_m84_surprise(valence: float, arousal: float) -> float:
    """Compute surprise (arousal at neutral valence)."""
    return arousal * (1 - abs(valence - 0.5) * 2)


# ----------------------------------------------------------------------# m85_sent_12# ----------------------------------------------------------------------
def compute_m85_hope(valence: float, anticipation: float) -> float:
    """Compute hope (positive anticipation)."""
    return (valence + anticipation) / 2


# ----------------------------------------------------------------------# m86_sent_13# ----------------------------------------------------------------------
def compute_m86_despair(valence: float, sadness: float) -> float:
    """Compute despair (negative hopelessness)."""
    return ((1 - valence) + sadness) / 2


# ----------------------------------------------------------------------# m87_sent_14# ----------------------------------------------------------------------
def compute_m87_confusion(arousal: float, PCI: float) -> float:
    """Compute confusion (activation without structure)."""
    return arousal * (1 - PCI)


# ----------------------------------------------------------------------# m88_sent_15# ----------------------------------------------------------------------
def compute_m88_clarity(PCI: float, arousal: float) -> float:
    """Compute clarity (structured activation)."""
    return PCI * (0.5 + arousal * 0.5)


# ----------------------------------------------------------------------# m89_sent_16# ----------------------------------------------------------------------
def compute_m89_acceptance(valence: float, arousal: float, T_integ: float) -> float:
    """Compute acceptance (calm positive integration)."""
    return (valence + (1-arousal) + T_integ) / 3


# ----------------------------------------------------------------------# m90_sent_17# ----------------------------------------------------------------------
def compute_m90_resistance(arousal: float, acceptance: float) -> float:
    """Compute resistance (active rejection)."""
    return arousal * (1 - acceptance)


# ----------------------------------------------------------------------# m91_sent_18# ----------------------------------------------------------------------
def compute_m91_emotional_coherence(PCI: float, T_disso: float) -> float:
    """Compute emotional coherence (integrated emotion)."""
    return PCI * (1 - T_disso)


# ----------------------------------------------------------------------# m92_sent_19# ----------------------------------------------------------------------
def compute_m92_emotional_stability(valence: float, arousal: float) -> float:
    """Compute emotional stability (no extremes)."""
    return (1 - arousal) * (1 - abs(valence - 0.5) * 2)


# ----------------------------------------------------------------------# m93_sent_20# ----------------------------------------------------------------------
import math

def compute_m93_emotional_range(v: float, a: float, d: float) -> float:
    """Compute distance from emotional center."""
    return math.sqrt((v-0.5)**2 + (a-0.5)**2 + (d-0.5)**2)


# ----------------------------------------------------------------------# m94_sent_21# ----------------------------------------------------------------------
def compute_m94_comfort(valence: float, arousal: float) -> float:
    """Compute comfort (calm, slightly positive)."""
    return (1 - arousal) * (1 - abs(valence - 0.6))


# ----------------------------------------------------------------------# m95_sent_22# ----------------------------------------------------------------------
def compute_m95_tension(valence: float, arousal: float) -> float:
    """Compute tension (aroused polarization)."""
    return arousal * abs(valence - 0.5) * 2


# ----------------------------------------------------------------------# m96_grain_word# ----------------------------------------------------------------------
def compute_m96_grain_word(text: str) -> float:
    """
    Compute word-level complexity score.
    
    Based on word length, syllables, and corpus frequency.
    
    Args:
        text: Input text
        
    Returns:
        grain_word in [0, 1]
    """
    words = text.split()
    if not words:
        return 0.5
    
    total_complexity = 0.0
    for word in words:
        # Simple approximation: longer words = more complex
        word_complexity = min(1.0, len(word) / 12.0)
        total_complexity += word_complexity
    
    return total_complexity / len(words)


# ----------------------------------------------------------------------# m97_grain_impact# ----------------------------------------------------------------------
def compute_m97_grain_impact(text: str, lex: dict) -> float:
    """
    Compute emotional impact density.
    
    Measures concentration of emotional words.
    
    Args:
        text: Input text
        lex: Lexikon with emotional words
        
    Returns:
        grain_impact in [0, 1]
    """
    words = text.lower().split()
    if not words:
        return 0.0
    
    emotional_words = lex.get("emotional", [])
    emotional_count = sum(1 for w in words if w in emotional_words)
    
    return min(1.0, emotional_count / len(words) * 5.0)  # Scale factor


# ----------------------------------------------------------------------# m98_grain_sentiment# ----------------------------------------------------------------------
def compute_m98_grain_sentiment(segment_sentiments: list) -> float:
    """
    Compute local sentiment variance.
    
    Measures emotional consistency across text segments.
    
    Args:
        segment_sentiments: List of sentiment scores per segment
        
    Returns:
        grain_sentiment (variance) in [0, 1]
    """
    if len(segment_sentiments) < 2:
        return 0.0
    
    mean = sum(segment_sentiments) / len(segment_sentiments)
    variance = sum((s - mean)**2 for s in segment_sentiments) / len(segment_sentiments)
    
    return min(1.0, variance * 4.0)  # Scale to [0, 1]


# ----------------------------------------------------------------------# m99_grain_novelty# ----------------------------------------------------------------------
def compute_m99_grain_novelty(text: str) -> float:
    """
    Compute novelty index (inverse of repetition).
    
    High values indicate original, varied text.
    
    Args:
        text: Input text
        
    Returns:
        grain_novelty in [0, 1]
    """
    words = text.lower().split()
    if len(words) < 2:
        return 1.0
    
    unique_words = set(words)
    repetition_score = 1 - (len(unique_words) / len(words))
    
    return max(0.0, 1.0 - repetition_score)


# ----------------------------------------------------------------------# m100_causal_1# ----------------------------------------------------------------------
def compute_m100_causal_1(text: str) -> float:
    """
    Compute density of causal connectors (logic chain).
    
    Used by A67 (Kausalitäts-Analyse) for self-reflection.
    
    Args:
        text: Input text to analyze
        
    Returns:
        causal_1 in [0, 1]
        
    Reference:
        A67 Protocol (Historische Kausalitäts-Analyse)
        metrics_engine_v3.py line 380
    """
    markers = ['weil', 'daher', 'deshalb', 'daraus folgt', 'bedingt durch', 
               'aufgrund', 'infolge', 'somit', 'folglich', 'demnach']
    text_lower = text.lower()
    hits = sum(1 for m in markers if m in text_lower)
    return min(1.0, hits / 4.0)


# ----------------------------------------------------------------------# m101_t_panic# ----------------------------------------------------------------------
def compute_m101_t_panic(text: str, panic_lexikon: dict) -> float:
    """
    Compute panic vector from text analysis.
    
    Safety-critical metric for acute distress detection.
    
    Args:
        text: Input text to analyze
        panic_lexikon: Dict with panic words and weights
            Example: {"hilfe": 2.0, "panik": 3.0, "angst": 1.5}
            
    Returns:
        t_panic in [0, 1] - higher = more panic indicators
    """
    words = text.lower().split()
    if not words:
        return 0.0
    
    total_weight = 0.0
    for word in words:
        if word in panic_lexikon:
            total_weight += panic_lexikon[word]
    
    # Normalize by text length and scale
    raw_score = total_weight / (len(words) + 1) * 10.0
    
    return max(0.0, min(1.0, raw_score))


# ----------------------------------------------------------------------# m102_t_disso# ----------------------------------------------------------------------
def compute_m102_t_disso(text: str, disso_lexikon: dict) -> float:
    """
    Compute dissociation score from text analysis.
    
    Detects emotional numbness and cognitive withdrawal.
    
    Args:
        text: Input text to analyze
        disso_lexikon: Dict with dissociation words and weights
            Example: {"egal": 1.5, "fühle nichts": 2.5, "unwirklich": 2.0}
            
    Returns:
        t_disso in [0, 1] - higher = more dissociation indicators
    """
    text_lower = text.lower()
    words = text_lower.split()
    if not words:
        return 0.0
    
    total_weight = 0.0
    for phrase, weight in disso_lexikon.items():
        if phrase in text_lower:
            total_weight += weight
    
    raw_score = total_weight / (len(words) + 1) * 8.0
    return max(0.0, min(1.0, raw_score))


# ----------------------------------------------------------------------# m103_t_integ# ----------------------------------------------------------------------
def compute_m103_t_integ(text: str, integ_lexikon: dict) -> float:
    """
    Compute integration score from text analysis.
    
    Positive counterforce detecting healing and connection.
    
    Args:
        text: Input text to analyze
        integ_lexikon: Dict with integration words and weights
            
    Returns:
        t_integ in [0, 1] - higher = more integration indicators
    """
    text_lower = text.lower()
    words = text_lower.split()
    if not words:
        return 0.5  # Neutral default
    
    total_weight = 0.0
    for phrase, weight in integ_lexikon.items():
        if phrase in text_lower:
            total_weight += weight
    
    raw_score = total_weight / (len(words) + 1) * 8.0
    return max(0.0, min(1.0, raw_score))


# ----------------------------------------------------------------------# m104_t_shock# ----------------------------------------------------------------------
def compute_m104_t_shock(
    text: str, 
    t_panic: float, 
    t_integ: float,
    shock_lexikon: list
) -> float:
    """
    Compute binary shock flag.
    
    Args:
        text: Input text
        t_panic: Panic score
        t_integ: Integration score
        shock_lexikon: List of shock words
        
    Returns:
        t_shock: 0.0 or 1.0
    """
    text_lower = text.lower()
    
    # Check for explicit shock markers
    for marker in shock_lexikon:
        if marker in text_lower:
            return 1.0
    
    # Check for derived shock state
    if t_panic > 0.8 and t_integ < 0.2:
        return 1.0
    
    return 0.0


# ----------------------------------------------------------------------# m105_t_fog# ----------------------------------------------------------------------
def compute_m105_t_fog(LL: float, t_disso: float) -> float:
    """
    Compute mental fog (cognitive impairment).
    
    Composite of turbidity and dissociation.
    
    Args:
        LL: Lambert-Light (turbidity) [0, 1]
        t_disso: Dissociation score [0, 1]
        
    Returns:
        t_fog in [0, 1]
    """
    return (LL + t_disso) / 2.0


# ----------------------------------------------------------------------# m106_i_eff# ----------------------------------------------------------------------
def compute_m106_i_eff(t_fog: float) -> float:
    """
    Compute inverse efficiency (clarity).
    
    High values indicate clear thinking.
    
    Args:
        t_fog: Mental fog score [0, 1]
        
    Returns:
        i_eff in [0, 1]
    """
    return 1.0 - t_fog


# ----------------------------------------------------------------------# m107_turb_c# ----------------------------------------------------------------------
def compute_m107_turb_c(LL: float, chaos: float) -> float:
    """
    Compute turbidity-chaos composite.
    
    High values indicate muddy AND chaotic state.
    
    Args:
        LL: Lambert-Light (turbidity) [0, 1]
        chaos: Chaos score [0, 1]
        
    Returns:
        turb_c in [0, 1]
    """
    return LL * chaos


# ----------------------------------------------------------------------# m108_turb_l# ----------------------------------------------------------------------
def compute_m108_turb_l(LL: float, t_disso: float) -> float:
    """
    Compute turbidity-light composite.
    
    High values indicate turbidity WITH dissociation.
    
    Args:
        LL: Lambert-Light (turbidity) [0, 1]
        t_disso: Dissociation score [0, 1]
        
    Returns:
        turb_l in [0, 1]
    """
    return LL * t_disso


# ----------------------------------------------------------------------# m109_turb_1# ----------------------------------------------------------------------
def compute_m109_turb_1(LL: float, chaos: float, t_disso: float) -> float:
    """Compute composite turbidity score."""
    return (LL + chaos * 0.5 + t_disso * 0.5) / 2.0

def compute_m109_disso_affect(t_disso: float, A: float) -> float:
    """Compute dissociation-affect interaction."""
    return t_disso * (1 - A)


# ----------------------------------------------------------------------# m110_black_hole# ----------------------------------------------------------------------
def compute_m110_black_hole(
    chaos: float, 
    A: float, 
    LL: float,
    panic_hits: int = 0,
    text: str = "",
    semantic_guardian = None
) -> float:
    """
    Compute black hole (event horizon) state.
    
    V3.3.3 CRITICAL FIX: Context-Aware Veto replaces "Dumb Dictator".
    Lexikon is now "Accuser", Semantic Guardian is "Judge".
    
    Args:
        chaos: Entropy level [0, 1]
        A: Affekt score [0, 1]
        LL: Lambert-Light (turbidity) [0, 1]
        panic_hits: Count of panic words in text (Lexikon check)
        text: Original user text for semantic analysis
        semantic_guardian: Optional LLM-based urgency checker
        
    Returns:
        black_hole in [0, 1] - higher = more critical
    """
    # V3.3: Weighted formula (Chaos has highest priority)
    math_val = (0.4 * chaos) + (0.3 * (1.0 - A)) + (0.3 * LL)
    
    # V3.3.3: Context-Aware Veto (Lexikon = Accuser, LLM = Judge)
    # If user writes ≥2 panic words, ASK the semantic guardian first!
    if panic_hits >= 2:
        if semantic_guardian is not None:
            is_real_emergency = semantic_guardian.check_urgency(text)
            if is_real_emergency:
                return max(math_val, 0.85)  # Confirmed emergency
            else:
                return min(1.0, math_val + 0.1)  # Minor penalty only
        else:
            # Fallback if no semantic guardian: Use SMA-5 smoothing
            # to prevent single-turn spikes
            return min(1.0, math_val + 0.15)  # Conservative penalty
        
    return math_val

def compute_m110_turb_2(t_disso: float, chaos: float, z_prox: float) -> float:
    """Compute turbidity-2 composite."""
    return t_disso * chaos * z_prox


# ----------------------------------------------------------------------# m111_g_phase# ----------------------------------------------------------------------
import math

def compute_m111_g_phase(nabla_A: float, nabla_B: float) -> float:
    """Compute gravitational phase angle."""
    return math.atan2(nabla_A, nabla_B)


# ----------------------------------------------------------------------# m112_g_phase_norm# ----------------------------------------------------------------------
import math

def compute_m112_g_phase_norm(g_phase: float) -> float:
    """Normalize gravitational phase to [0, 1]."""
    return (g_phase + math.pi) / (2 * math.pi)


# ----------------------------------------------------------------------# m113_hash_state# ----------------------------------------------------------------------
import hashlib

def compute_m113_hash_state(state_string: str) -> str:
    """SHA-256 Zustands-Hash (hex[64])."""
    return hashlib.sha256(state_string.encode('utf-8')).hexdigest()


# ----------------------------------------------------------------------# m114_cos_sim# ----------------------------------------------------------------------
import numpy as np

def compute_m114_cos_sim(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        vec_a: First embedding vector
        vec_b: Second embedding vector
        
    Returns:
        Cosine similarity in [-1, 1]
    """
    if np.linalg.norm(vec_a) == 0 or np.linalg.norm(vec_b) == 0:
        return 0.0
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))


# ----------------------------------------------------------------------# m115_spatial_1# ----------------------------------------------------------------------
def compute_m115_spatial_1(text: str, spatial_lexikon: dict) -> float:
    """
    Compute spatial coherence metric.
    
    Measures consistency of spatial references.
    """
    # Simplified: count spatial markers
    text_lower = text.lower()
    words = text_lower.split()
    if not words:
        return 0.5
    
    spatial_markers = spatial_lexikon.get("markers", [])
    marker_count = sum(1 for w in words if w in spatial_markers)
    
    return min(1.0, marker_count / (len(words) + 1) * 10.0)


# ----------------------------------------------------------------------# m116_lix# ----------------------------------------------------------------------
def compute_m116_lix(text: str) -> float:
    """
    Compute LIX readability index.
    
    Lower values = easier to read.
    """
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    if not words or sentences == 0:
        return 50.0  # Default medium
    
    long_words = sum(1 for w in words if len(w) > 6)
    
    return (len(words) / sentences) + (long_words * 100 / len(words))


# ----------------------------------------------------------------------# m117_question_density# ----------------------------------------------------------------------
def compute_m117_question_density(text: str) -> float:
    """Compute question density."""
    questions = text.count('?')
    sentences = text.count('.') + text.count('!') + text.count('?')
    if sentences == 0:
        return 0.0
    return questions / sentences


# ----------------------------------------------------------------------# m118_capital_stress# ----------------------------------------------------------------------
def compute_m118_capital_stress(text: str) -> float:
    """Compute capital letter stress."""
    words = text.split()
    if not words:
        return 0.0
    caps_words = sum(1 for w in words if w.isupper() and len(w) > 1)
    return caps_words / len(words)


# ----------------------------------------------------------------------# m119_turn_len_ai# ----------------------------------------------------------------------
def compute_m119_turn_len_ai(ai_responses: list) -> float:
    """Compute average AI response length."""
    if not ai_responses:
        return 0.0
    total_words = sum(len(r.split()) for r in ai_responses)
    return total_words / len(ai_responses)


# ----------------------------------------------------------------------# m120_emoji_sentiment# ----------------------------------------------------------------------
def compute_m120_emoji_sentiment(text: str, emoji_map: dict) -> float:
    """Compute sentiment from emojis."""
    total_score = 0.0
    count = 0
    for char in text:
        if char in emoji_map:
            total_score += emoji_map[char]
            count += 1
    if count == 0:
        return 0.0
    return total_score / count


# ----------------------------------------------------------------------# m121_talk_ratio# ----------------------------------------------------------------------
def compute_m121_talk_ratio(user_words: int, ai_words: int) -> float:
    """Compute user/AI talk ratio."""
    if ai_words == 0:
        return 1.0
    return user_words / ai_words


# ----------------------------------------------------------------------# m122_dyn_1# ----------------------------------------------------------------------
def compute_m122_dyn_1(delta_A: float, delta_tokens: float) -> float:
    """Compute energy flow from affekt and token changes."""
    return (delta_A + delta_tokens) / 2.0


# ----------------------------------------------------------------------# m123_dyn_2# ----------------------------------------------------------------------
def compute_m123_dyn_2(prev_delta: float, curr_delta: float) -> float:
    """Compute momentum from delta persistence."""
    return abs(curr_delta) if curr_delta * prev_delta > 0 else 0.0


# ----------------------------------------------------------------------# m124_dyn_3# ----------------------------------------------------------------------
def compute_m124_dyn_3(value_history: list) -> float:
    """Compute oscillation from value fluctuation."""
    if len(value_history) < 3:
        return 0.0
    reversals = sum(1 for i in range(1, len(value_history)-1) 
                    if (value_history[i] - value_history[i-1]) * 
                       (value_history[i+1] - value_history[i]) < 0)
    return min(1.0, reversals / (len(value_history) / 2))


# ----------------------------------------------------------------------# m125_dyn_4# ----------------------------------------------------------------------
def compute_m125_dyn_4(oscillation: float, time_decay: float) -> float:
    """Compute damping factor."""
    return oscillation * (1 - time_decay)


# ----------------------------------------------------------------------# m126_dyn_5# ----------------------------------------------------------------------
def compute_m126_dyn_5(ev_resonance: float, trust_score: float) -> float:
    """Compute dynamic resonance."""
    return (ev_resonance + trust_score) / 2.0


# ----------------------------------------------------------------------# m127_dyn_6# ----------------------------------------------------------------------
def compute_m127_dyn_6(phase_a: float, phase_b: float) -> float:
    """Compute phase shift between systems."""
    return phase_a - phase_b


# ----------------------------------------------------------------------# m128_dyn_7# ----------------------------------------------------------------------
def compute_m128_dyn_7(max_value: float, min_value: float) -> float:
    """Compute oscillation amplitude."""
    return (max_value - min_value) / 2.0


# ----------------------------------------------------------------------# m129_dyn_8# ----------------------------------------------------------------------
def compute_m129_dyn_8(oscillation_count: int, time_period: float) -> float:
    """Compute oscillation frequency."""
    if time_period == 0:
        return 0.0
    return oscillation_count / time_period


# ----------------------------------------------------------------------# m130_dyn_9# ----------------------------------------------------------------------
def compute_m130_dyn_9(variance: float, threshold: float = 0.1) -> float:
    """Compute system stability."""
    return max(0.0, 1.0 - variance / threshold)


# ----------------------------------------------------------------------# m131_session_dur# ----------------------------------------------------------------------
from datetime import datetime

def compute_m131_session_dur(session_start: datetime) -> float:
    """Compute session duration in minutes."""
    delta = datetime.now() - session_start
    return delta.total_seconds() / 60.0


# ----------------------------------------------------------------------# m132_inter_freq# ----------------------------------------------------------------------
def compute_m132_inter_freq(message_count: int, session_duration_seconds: float) -> float:
    """Compute interaction frequency in Hz."""
    if session_duration_seconds == 0:
        return 0.0
    return message_count / session_duration_seconds


# ----------------------------------------------------------------------# m133_chr_1# ----------------------------------------------------------------------
def compute_m133_chr_1(last_topic_shift: datetime) -> float:
    """Compute time since last topic shift in seconds."""
    delta = datetime.now() - last_topic_shift
    return delta.total_seconds()


# ----------------------------------------------------------------------# m134_chr_2# ----------------------------------------------------------------------
def compute_m134_chr_2(response_latencies: list) -> float:
    """Compute average response latency."""
    if not response_latencies:
        return 0.0
    return sum(response_latencies) / len(response_latencies)


# ----------------------------------------------------------------------# m135_meta_20# ----------------------------------------------------------------------
def compute_m135_meta_20(text: str) -> float:
    """Compute planning from future tense usage."""
    future_markers = ['wird', 'werden', 'werde', 'will', 'möchte', 'plane', 'würde', 'könnte']
    words = text.lower().split()
    if not words:
        return 0.0
    hits = sum(1 for w in words if w in future_markers)
    return min(1.0, hits / len(words) * 20.0)


# ----------------------------------------------------------------------# m136_meta_21# ----------------------------------------------------------------------
def compute_m136_meta_21(text: str) -> float:
    """Compute reflection from past tense + self-reference."""
    past_markers = ['war', 'hatte', 'habe', 'bin', 'dachte', 'fühlte', 'machte']
    text_lower = text.lower()
    has_self = 'ich' in text_lower
    if not has_self:
        return 0.0
    words = text_lower.split()
    hits = sum(1 for w in words if w in past_markers)
    return min(1.0, hits / len(words) * 15.0)


# ----------------------------------------------------------------------# m137_meta_22# ----------------------------------------------------------------------
def compute_m137_meta_22(text: str, abstract_lexikon: list) -> float:
    """Compute abstraction from abstract concept density."""
    words = text.lower().split()
    if not words:
        return 0.0
    abstracts = sum(1 for w in words if w in abstract_lexikon)
    return min(1.0, abstracts / len(words) * 10.0)


# ----------------------------------------------------------------------# m138_meta_23# ----------------------------------------------------------------------
def compute_m138_meta_23(text: str) -> float:
    """Compute integration from cross-references."""
    markers = ['außerdem', 'zusätzlich', 'damit verbunden', 'wie erwähnt', 'wie vorher', 'bezogen auf']
    text_lower = text.lower()
    hits = sum(1 for m in markers if m in text_lower)
    return min(1.0, hits / 3.0)


# ----------------------------------------------------------------------# m139_meta_24# ----------------------------------------------------------------------
def compute_m139_meta_24(text: str) -> float:
    """Compute synthesis from conclusion markers."""
    markers = ['also', 'daher', 'folglich', 'demnach', 'zusammenfassend', 'insgesamt', 'abschließend']
    text_lower = text.lower()
    hits = sum(1 for m in markers if m in text_lower)
    return min(1.0, hits / 2.0)


# ----------------------------------------------------------------------# m140_meta_25# ----------------------------------------------------------------------
def compute_m140_meta_25(text: str) -> float:
    """Compute evaluation from judgment terms."""
    markers = ['gut', 'schlecht', 'richtig', 'falsch', 'sollte', 'muss', 'wichtig', 'unwichtig', 'besser', 'schlechter']
    words = text.lower().split()
    if not words:
        return 0.0
    hits = sum(1 for w in words if w in markers)
    return min(1.0, hits / len(words) * 15.0)


# ----------------------------------------------------------------------# m141_hallu_risk# ----------------------------------------------------------------------
def compute_m141_hallu_risk(chaos: float, rag_alignment: float) -> float:
    """
    Compute hallucination risk.
    
    V3.0.2 FIX: Uses m21_chaos (normalized 0-1) instead of raw entropy.
    This prevents output values > 1.0 that would break weighted averages.
    
    Args:
        chaos: Normalized chaos score m21 [0, 1]
        rag_alignment: RAG alignment score [0, 1]
        
    Returns:
        hallu_risk in [0, 1]
    """
    return chaos * (1 - rag_alignment)


# ----------------------------------------------------------------------# m142_rag_align# ----------------------------------------------------------------------
def compute_m142_rag_align(response_embedding: np.ndarray, context_embedding: np.ndarray) -> float:
    """Compute RAG alignment as cosine similarity."""
    if np.linalg.norm(response_embedding) == 0 or np.linalg.norm(context_embedding) == 0:
        return 0.0
    return np.dot(response_embedding, context_embedding) / (
        np.linalg.norm(response_embedding) * np.linalg.norm(context_embedding)
    )


# ----------------------------------------------------------------------# m143_mem_pressure# ----------------------------------------------------------------------
import psutil

def compute_m143_mem_pressure() -> float:
    """Compute memory pressure as usage ratio."""
    memory = psutil.virtual_memory()
    return memory.percent / 100.0


# ----------------------------------------------------------------------# m144_sys_stab# ----------------------------------------------------------------------
def compute_m144_sys_stab(latency: float, error_rate: float, max_latency: float = 10.0) -> float:
    """Compute system stability."""
    latency_norm = min(1.0, latency / max_latency)
    return 1 - (latency_norm + error_rate) / 2


# ----------------------------------------------------------------------# m145_meta_30# ----------------------------------------------------------------------
def compute_m145_meta_30(text: str) -> int:
    """Compute recursive depth from nested self-references."""
    depth = 0
    recursive_markers = ['ich denke, dass ich', 'wenn ich überlege', 'mein gedanke über']
    for marker in recursive_markers:
        depth += text.lower().count(marker)
    return depth


# ----------------------------------------------------------------------# m146_meta_31# ----------------------------------------------------------------------
def compute_m146_meta_31(text: str) -> float:
    """Detect paradoxical statements."""
    paradox_markers = ['ja und nein', 'gleichzeitig nicht', 'aber auch nicht', 'weder noch']
    text_lower = text.lower()
    hits = sum(1 for m in paradox_markers if m in text_lower)
    return min(1.0, hits / 2.0)


# ----------------------------------------------------------------------# m147_meta_32# ----------------------------------------------------------------------
def compute_m147_meta_32(statements: list) -> float:
    """Check statement consistency."""
    if len(statements) < 2:
        return 1.0
    # Simplified: check for direct contradictions
    contradiction_count = 0
    for i, s1 in enumerate(statements):
        for s2 in statements[i+1:]:
            if "nicht " + s1 in s2 or s1 + " nicht" in s2:
                contradiction_count += 1
    return max(0.0, 1.0 - contradiction_count * 0.2)


# ----------------------------------------------------------------------# m148_meta_33# ----------------------------------------------------------------------
def compute_m148_meta_33(text: str) -> float:
    """Check temporal coherence."""
    past = ['gestern', 'letzte woche', 'früher', 'war', 'hatte']
    future = ['morgen', 'nächste woche', 'wird', 'werde']
    text_lower = text.lower()
    has_past = any(p in text_lower for p in past)
    has_future = any(f in text_lower for f in future)
    # Mixed tenses without markers = lower coherence
    if has_past and has_future:
        if 'und dann' not in text_lower and 'aber jetzt' not in text_lower:
            return 0.6
    return 1.0


# ----------------------------------------------------------------------# m149_meta_34# ----------------------------------------------------------------------
def compute_m149_meta_34(text: str) -> float:
    """Check causal chain completeness."""
    causal = ['weil', 'da', 'denn', 'deshalb', 'daher']
    text_lower = text.lower()
    causal_starts = sum(1 for c in causal if c in text_lower)
    if causal_starts == 0:
        return 1.0  # No causal claims = nothing to check
    # Check if explanations follow
    words = text_lower.split()
    complete = 0
    for i, w in enumerate(words):
        if w in causal and i < len(words) - 3:
            complete += 1
    return min(1.0, complete / causal_starts if causal_starts > 0 else 1.0)


# ----------------------------------------------------------------------# m150_meta_35# ----------------------------------------------------------------------
def compute_m150_meta_35(text: str) -> float:
    """Check semantic closure."""
    # Check for open questions
    if text.strip().endswith('?'):
        return 0.5  # Open question = partial closure
    
    closure_markers = ['zusammenfassend', 'abschließend', 'also', 'daher', 'somit']
    text_lower = text.lower()
    has_closure = any(m in text_lower for m in closure_markers)
    
    # Check for incomplete sentences
    words = text.split()
    if len(words) < 3:
        return 0.3
    
    return 1.0 if has_closure else 0.7


# ----------------------------------------------------------------------# m151_omega# ----------------------------------------------------------------------
def compute_m151_omega(phi: float, rule_conflict: float) -> float:
    """
    Compute OMEGA - the ultimate synthesis metric.
    
    V3.0.2 FIX: Uses subtraction instead of multiplication to prevent
    the paradox where rule violations are rewarded when Phi is negative.
    
    Args:
        phi: Ontological coherence [-1, 1]
        rule_conflict: Degree of rule conflicts [0, 1]
        
    Returns:
        omega in [-1, 1]
    """
    # Subtraktive Logik: Konflikte IMMER bestrafen
    omega = phi - (rule_conflict * 1.5)
    return max(-1.0, min(1.0, omega))


# ----------------------------------------------------------------------# m152_alignment# ----------------------------------------------------------------------
def compute_m152_alignment(trust_score: float, soul_integrity: float) -> float:
    """
    Compute user alignment.
    
    High alignment = system and user are in sync.
    """
    return trust_score * soul_integrity


# ----------------------------------------------------------------------# m153_sys_ent# ----------------------------------------------------------------------
def compute_m153_sys_ent(local_entropies: list) -> float:
    """Compute global system entropy."""
    if not local_entropies:
        return 0.5
    return sum(local_entropies) / len(local_entropies)


# ----------------------------------------------------------------------# m154_quality# ----------------------------------------------------------------------
def compute_m154_quality(A: float, PCI: float, alignment: float) -> float:
    """Compute overall quality score."""
    return (A + PCI + alignment) / 3.0


# ----------------------------------------------------------------------# m155_completeness# ----------------------------------------------------------------------
def compute_m155_completeness(text: str, task_markers: list) -> float:
    """Compute task completion score."""
    text_lower = text.lower()
    completion_markers = ['fertig', 'erledigt', 'abgeschlossen', 'vollständig', 'done']
    hits = sum(1 for m in completion_markers if m in text_lower)
    return min(1.0, hits / 2.0 + 0.5)


# ----------------------------------------------------------------------# m156_relevance# ----------------------------------------------------------------------
def compute_m156_relevance(response_emb: np.ndarray, query_emb: np.ndarray) -> float:
    """Compute semantic relevance to query."""
    if np.linalg.norm(response_emb) == 0 or np.linalg.norm(query_emb) == 0:
        return 0.0
    return max(0.0, np.dot(response_emb, query_emb) / (
        np.linalg.norm(response_emb) * np.linalg.norm(query_emb)
    ))


# ----------------------------------------------------------------------# m157_coherence# ----------------------------------------------------------------------
def compute_m157_coherence(turn_embeddings: list) -> float:
    """Compute cross-turn coherence."""
    if len(turn_embeddings) < 2:
        return 1.0
    similarities = []
    for i in range(1, len(turn_embeddings)):
        sim = np.dot(turn_embeddings[i-1], turn_embeddings[i]) / (
            np.linalg.norm(turn_embeddings[i-1]) * np.linalg.norm(turn_embeddings[i])
        )
        similarities.append(sim)
    return sum(similarities) / len(similarities) if similarities else 1.0


# ----------------------------------------------------------------------# m158_depth# ----------------------------------------------------------------------
def compute_m158_depth(text: str) -> int:
    """Compute elaboration depth."""
    depth_markers = ['außerdem', 'zusätzlich', 'weiterhin', 'darüber hinaus', 'genauer gesagt']
    text_lower = text.lower()
    return sum(1 for m in depth_markers if m in text_lower)


# ----------------------------------------------------------------------# m159_novelty# ----------------------------------------------------------------------
def compute_m159_novelty(response_emb: np.ndarray, history_embs: list) -> float:
    """Compute novelty relative to history."""
    if not history_embs:
        return 1.0
    max_sim = 0.0
    for h in history_embs:
        sim = np.dot(response_emb, h) / (np.linalg.norm(response_emb) * np.linalg.norm(h))
        max_sim = max(max_sim, sim)
    return 1 - max_sim


# ----------------------------------------------------------------------# m160_clarity# ----------------------------------------------------------------------
def compute_m160_clarity(confusion: float, text: str) -> float:
    """Compute clarity score."""
    clarity_markers = ['klar', 'deutlich', 'offensichtlich', 'eindeutig', 'präzise']
    words = text.lower().split()
    if not words:
        return 1.0 - confusion
    clarity_density = sum(1 for w in words if w in clarity_markers) / len(words) * 10.0
    return min(1.0, 1 - confusion + clarity_density)


# ----------------------------------------------------------------------# m161_commit_action# ----------------------------------------------------------------------
def compute_m161_commit_action(omega: float, z_prox: float, rule_conflict: float) -> str:
    """
    Compute final commit action.
    
    This is the executive decision based on all metrics.
    
    Args:
        omega: Overall system coherence
        z_prox: Death proximity score
        rule_conflict: Rule conflict level
        
    Returns:
        "commit", "warn", "retry", or "alert"
        
    Reference: Forensic Audit 2026-01-31, Point 4
    """
    # Safety checks first (KRITISCH)
    if z_prox > 0.65:
        return "alert"  # BLOCKIEREN!
    if rule_conflict > 0.5:
        return "alert"
    
    # Warning zone (NEU: Forensic Audit Empfehlung)
    if z_prox > 0.50:
        return "warn"  # Loggen aber senden
    
    # Quality check
    if omega < 0.3:
        return "retry"
    
    # All clear
    return "commit"


# ----------------------------------------------------------------------# m162_ctx_time# ----------------------------------------------------------------------
from datetime import datetime

def compute_m162_ctx_time(session_start: datetime, current_time: datetime) -> float:
    """
    Compute temporal context embedding.
    
    Returns normalized session duration as proxy for temporal engagement.
    """
    duration_minutes = (current_time - session_start).total_seconds() / 60.0
    # Normalize: 0-60 min → 0-1
    return min(1.0, duration_minutes / 60.0)


# ----------------------------------------------------------------------# m163_ctx_loc# ----------------------------------------------------------------------
def compute_m163_ctx_loc(location_data: dict = None) -> float:
    """
    Compute spatial context embedding.
    
    PC-Phase: Returns 0.5 (neutral, unknown location)
    APK-Phase: Will use GPS/sensor data
    """
    if location_data is None:
        return 0.5  # Neutral default for PC
    # APK-Phase implementation will use location_data
    return location_data.get("safety_score", 0.5)


# ----------------------------------------------------------------------# m164_user_state# ----------------------------------------------------------------------
def compute_m164_user_state(recent_affects: list[float]) -> float:
    """
    Compute user state from recent affect scores.
    
    Args:
        recent_affects: Last 5 m1_affect scores
        
    Returns:
        Weighted average (recent more important)
    """
    if not recent_affects:
        return 0.5
    weights = [0.1, 0.15, 0.2, 0.25, 0.3]  # Neuere = wichtiger
    weights = weights[-len(recent_affects):]
    return sum(a * w for a, w in zip(recent_affects, weights)) / sum(weights)


# ----------------------------------------------------------------------# m165_platform# ----------------------------------------------------------------------
import platform

def compute_m165_platform() -> str:
    """
    Detect current platform.
    
    Returns:
        "pc" (Windows/Linux), "apk" (Android), or "rover" (ESP32)
    """
    system = platform.system().lower()
    if system == "linux" and "android" in platform.release().lower():
        return "apk"
    elif system in ["windows", "linux", "darwin"]:
        return "pc"
    else:
        return "rover"  # Assume ESP32/embedded


# ----------------------------------------------------------------------# m166_modality# ----------------------------------------------------------------------
def compute_m166_modality(input_data: dict) -> str:
    """
    Detect input modality.
    
    Args:
        input_data: Dict with keys 'text', 'audio', 'image'
    """
    modalities = []
    if input_data.get("text"):
        modalities.append("text")
    if input_data.get("audio"):
        modalities.append("voice")
    if input_data.get("image"):
        modalities.append("image")
    
    if len(modalities) > 1:
        return "multimodal"
    elif modalities:
        return modalities[0]
    else:
        return "text"  # Default


# ----------------------------------------------------------------------# m167_noise# ----------------------------------------------------------------------
import re

def compute_m167_noise(text: str) -> float:
    """
    Compute input noise level.
    
    High noise = typos, fragments, unclear input
    """
    if not text:
        return 0.0
    
    # Heuristics for noise detection
    typo_pattern = r'\b(\w)\1{2,}\b'  # Repeated letters (aaaa)
    fragment_pattern = r'^[a-z]{1,3}$'  # Very short words only
    
    typos = len(re.findall(typo_pattern, text, re.IGNORECASE))
    words = text.split()
    fragments = sum(1 for w in words if re.match(fragment_pattern, w))
    
    noise_score = (typos * 0.3 + fragments / max(1, len(words)) * 0.7)
    return min(1.0, noise_score)


# ----------------------------------------------------------------------# m168_cum_stress# ----------------------------------------------------------------------
from collections import deque
from datetime import datetime, timedelta

class CumulativeStressTracker:
    """
    Track cumulative stress over sliding 30-minute window.
    
    PATCH V3.2.1: Addresses the "frog in boiling water" problem
    where sustained sub-threshold stress was undetected.
    """
    
    def __init__(self, window_minutes: int = 30):
        self.window = timedelta(minutes=window_minutes)
        self.samples: deque = deque()  # (timestamp, z_prox)
    
    def add_sample(self, z_prox: float, timestamp: datetime = None):
        if timestamp is None:
            timestamp = datetime.now()
        self.samples.append((timestamp, z_prox))
        self._cleanup(timestamp)
    
    def _cleanup(self, current_time: datetime):
        cutoff = current_time - self.window
        while self.samples and self.samples[0][0] < cutoff:
            self.samples.popleft()
    
    def compute_m168_cum_stress(self) -> float:
        """
        Compute cumulative stress integral.
        
        Returns:
            Integral of z_prox over time (unit: stress-minutes)
        """
        if len(self.samples) < 2:
            return 0.0
        
        total = 0.0
        for i in range(1, len(self.samples)):
            t_prev, z_prev = self.samples[i - 1]
            t_curr, z_curr = self.samples[i]
            delta_minutes = (t_curr - t_prev).total_seconds() / 60.0
            avg_z = (z_prev + z_curr) / 2.0
            total += avg_z * delta_minutes
        
        return total

# Guardian Integration
CUM_STRESS_THRESHOLD = 15.0  # 30 min * 0.5 average = 15

def guardian_check_cumulative(cum_stress: float, z_prox: float) -> str:
    """
    Extended guardian check including cumulative stress.
    
    Returns:
        "normal", "warn", or "alert"
    """
    # Standard checks
    if z_prox > 0.65:
        return "alert"
    if z_prox > 0.50:
        return "warn"
    
    # NEW: Cumulative stress check
    if cum_stress > CUM_STRESS_THRESHOLD:
        return "warn"  # Sustained stress detected
    
    return "normal"


# ----------------------------------------------------------------------# m100_causal_1# ----------------------------------------------------------------------
def compute_m100_causal_1(text: str) -> float:
    """
    Compute density of causal connectors (logic chain).
    
    Args:
        text: Input text to analyze
        
    Returns:
        causal_1 in [0, 1]
        
    Reference:
        A67 (Kausalitäts-Analyse)
    """
    markers = ['weil', 'daher', 'deshalb', 'daraus folgt', 'bedingt durch', 
               'aufgrund', 'infolge', 'somit', 'folglich', 'demnach']
    text_lower = text.lower()
    hits = sum(1 for m in markers if m in text_lower)
    return min(1.0, hits / 4.0)


# ----------------------------------------------------------------------# m100_sent_27# ----------------------------------------------------------------------
def compute_m100_sent_27(
    valence: float,
    dominance: float
) -> float:
    """
    Compute sentiment closure (satisfaction).
    
    High dominance + positive valence = emotional closure.
    
    Args:
        valence: Emotional polarity [-1, 1]
        dominance: Control/agency [0, 1]
        
    Returns:
        Closure score [0, 1]
    """
    # Normalize valence to [0, 1]
    val_norm = (valence + 1) / 2
    return dominance * (0.5 + val_norm * 0.5)


# ----------------------------------------------------------------------# EXTRACTION SUMMARY# ----------------------------------------------------------------------# 
# Total sections: 164# 
# Implementations extracted: 164# 
# Missing: 0
