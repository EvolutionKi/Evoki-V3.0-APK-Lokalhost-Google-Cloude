# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — FEP (FREE ENERGY PRINCIPLE) & EVOLUTION METRICS

Metrics based on Free Energy Principle and evolutionary dynamics.

Categories:
- FEP Core (m56-m60): Surprise, tokens, motivation, learning
- FEP Decision (m61-m64): U, R, phi, prediction error  
- FEP Drive (m65-m68): Social, logical, total, balance
- FEP Learning (m69-m70): Learning rate, decay
- Evolution (m71-m76): Resonance, tension, signals

Based on evoki_fullspectrum168_contract.json
"""

from typing import Dict
import math


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# FEP CORE (m56-m60)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m56_surprise(text: str, context: Dict) -> float:
    """
    m56_surprise - Bayesian Surprise
    
    Measures unexpectedness based on deviation from prediction.
    Range: [0.0, 1.0]
    
    Higher when input deviates from expected patterns.
    """
    # Simple heuristic: unusual word combinations, rare words
    words = text.lower().split()
    
    # Check for question marks (unexpected queries)
    has_questions = '?' in text
    
    # Check for exclamations (emotional surprise)
    has_exclamations = '!' in text
    
    # Check for unusual length
    word_count = len(words)
    unusual_length = word_count > 100 or word_count < 3
    
    surprise = 0.3  # Baseline
    if has_questions:
        surprise += 0.2
    if has_exclamations:
        surprise += 0.2
    if unusual_length:
        surprise += 0.3
    
    return clamp(surprise)


def compute_m57_tokens_soc(text: str) -> float:
    """
    m57_tokens_soc - Social context token count
    
    Rough estimate of social interaction tokens.
    Range: [0, 100]
    """
    # Count social/emotional words
    social_words = ['we', 'us', 'together', 'friend', 'you', 'i', 'feel', 
                    'think', 'believe', 'hope', 'want', 'need']
    
    text_lower = text.lower()
    count = sum(text_lower.count(word) for word in social_words)
    
    return min(100.0, float(count))


def compute_m58_tokens_log(text: str) -> float:
    """
    m58_tokens_log - Logical/causal reasoning token count
    
    Rough estimate of logical reasoning tokens.
    Range: [0, 100] (Integer)
    """
    # Count logical connectors
    logical_words = ['because', 'therefore', 'thus', 'hence', 'if', 'then',
                     'consequently', 'as a result', 'due to', 'since']
    
    text_lower = text.lower()
    count = sum(text_lower.count(word) for word in logical_words)
    
    return min(100.0, float(count))


def compute_m59_p_antrieb(m57_tokens_soc: float, m58_tokens_log: float) -> float:
    """
    m59_p_antrieb - Motivation/Drive
    
    Composite of social and logical engagement.
    Range: [0.0, 1.0]
    """
    # Normalize token counts
    soc_norm = min(1.0, m57_tokens_soc / 10.0)
    log_norm = min(1.0, m58_tokens_log / 10.0)
    
    p_antrieb = (soc_norm + log_norm) / 2.0
    
    return clamp(p_antrieb)


def compute_m60_delta_tokens(
    current_tokens: float,
    context: Dict
) -> float:
    """
    m60_delta_tokens - Token change over time
    
    Learning signal based on token count changes.
    Range: [-∞, +∞]
    """
    prev_tokens = context.get("prev_total_tokens", current_tokens)
    
    delta = current_tokens - prev_tokens
    
    return delta


# ═══════════════════════════════════════════════════════════════════════════
# FEP DECISION (m61-m64)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m61_U(m56_surprise: float, m2_PCI: float) -> float:
    """
    m61_U (m61_u_fep) - Decision Utility
    
    Utility function balancing surprise and complexity.
    Range: [0.0, 1.0]
    """
    # Higher utility when surprise is moderate and complexity is high
    U = (1.0 - abs(m56_surprise - 0.5)) * m2_PCI
    
    return clamp(U)


def compute_m62_R(m59_p_antrieb: float, m4_flow: float) -> float:
    """
    m62_R (m62_r_fep) - Decision Reward
    
    Reward signal based on motivation and flow.
    Range: [0.0, 1.0]
    """
    R = (m59_p_antrieb + m4_flow) / 2.0
    
    return clamp(R)


def compute_m63_phi(m61_U: float, m62_R: float) -> float:
    """
    m63_phi (m63_phi_score) - Decision Value
    
    Core FEP decision metric combining utility and reward.
    Range: [-1.0, 1.0]
    
    Note: This is DIFFERENT from m20_phi_proxy (consciousness)
    """
    # Weighted combination
    phi = (0.6 * m61_U) + (0.4 * m62_R) - 0.5
    
    return clamp(phi, -1.0, 1.0)


def compute_m64_lambda_fep(m63_phi: float, context: Dict) -> float:
    """
    m64_lambda_fep (m64_pred_error) - Prediction Error
    
    Measures deviation from expected phi.
    Range: [0.0, 1.0]
    """
    expected_phi = context.get("expected_phi", 0.0)
    
    pred_error = abs(m63_phi - expected_phi)
    
    return clamp(pred_error)


# ═══════════════════════════════════════════════════════════════════════════
# FEP DRIVE (m65-m68)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m65_alpha(m57_tokens_soc: float) -> float:
    """
    m65_alpha (m65_drive_soc) - Social Drive
    
    Drive towards social interaction.
    Range: [0.0, 1.0]
    """
    alpha = min(1.0, m57_tokens_soc / 20.0)
    
    return clamp(alpha)


def compute_m66_gamma(m58_tokens_log: float) -> float:
    """
    m66_gamma (m66_drive_log) - Logical Drive
    
    Drive towards logical reasoning.
    Range: [0.0, 1.0]
    """
    gamma = min(1.0, m58_tokens_log / 20.0)
    
    return clamp(gamma)


def compute_m67_precision(m65_alpha: float, m66_gamma: float) -> float:
    """
    m67_precision (m67_total_drive) - Total Drive
    
    Combined drive metric.
    Range: [0.0, 1.0]
    """
    precision = (m65_alpha + m66_gamma) / 2.0
    
    return clamp(precision)


def compute_m68_prediction_err(m65_alpha: float, m66_gamma: float) -> float:
    """
    m68_prediction_err (m68_drive_balance) - Drive Balance
    
    Measures balance between social and logical drives.
    Range: [0.0, 1.0]
    
    1.0 = perfectly balanced, 0.0 = highly imbalanced
    """
    # Balance score: 1.0 when alpha ≈ gamma
    balance = 1.0 - abs(m65_alpha - m66_gamma)
    
    return clamp(balance)


# ═══════════════════════════════════════════════════════════════════════════
# FEP LEARNING (m69-m70)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m69_model_evidence(m64_lambda_fep: float, context: Dict) -> float:
    """
    m69_model_evidence (m69_learning_rate) - Learning Rate
    
    Adaptive learning rate based on prediction error.
    Range: [0.0, 5.0]
    
    Higher error → higher learning rate
    """
    # Learning rate proportional to prediction error
    learning_rate = m64_lambda_fep * 5.0
    
    return min(5.0, learning_rate)


def compute_m70_active_inf(m67_precision: float) -> float:
    """
    m70_active_inf (m70_decay_factor) - Decay Factor
    
    Memory decay based on precision/drive.
    Range: [0.05, 0.1]
    
    Higher precision → slower decay
    """
    # Inverse relationship: high precision = low decay
    decay = 0.1 - (m67_precision * 0.05)
    
    return max(0.05, min(0.1, decay))


# ═══════════════════════════════════════════════════════════════════════════
# EVOLUTION (m71-m76)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m71_ev_arousal(m15_affekt_a: float, m4_flow: float) -> float:
    """
    m71_ev_arousal (m71_ev_resonance) - Evolution Arousal
    
    Emotional/energetic arousal state.
    Range: [0.0, 1.0]
    """
    arousal = (m15_affekt_a + m4_flow) / 2.0
    
    return clamp(arousal)


def compute_m72_ev_valence(m1_A: float, m5_coh: float) -> float:
    """
    m72_ev_valence (m72_ev_tension) - Evolution Valence
    
    Positive/negative emotional tone.
    Range: [0.0, 1.0]
    """
    valence = (m1_A + m5_coh) / 2.0
    
    return clamp(valence)


def compute_m73_ev_v_intensity(m71_ev_arousal: float) -> float:
    """
    m73_ev_v_intensity - Evolution Intensity
    
    Direct mapping of arousal to intensity.
    Range: [0.0, 1.0]
    """
    return m71_ev_arousal


def compute_m74_valence(m72_ev_valence: float) -> float:
    """
    m74_valence (m74_ev_signal) - Valence Signal
    
    Binary/continuous valence indicator.
    Range: {0.0, 1.0} (binary) / [0.0, 1.0] (continuous)
    """
    # Threshold at 0.5
    return 1.0 if m72_ev_valence > 0.5 else 0.0


def compute_m75_arousal(m71_ev_arousal: float) -> float:
    """
    m75_arousal (m75_vkon_mag) - Arousal Magnitude
    
    Direct arousal measurement.
    Range: [0.0, 1.0]
    """
    return m71_ev_arousal


def compute_m76_dominance(
    m1_A: float,
    m19_z_prox: float
) -> float:
    """
    m76_dominance (m76_ev_1) - Evolution Dominance
    
    Sense of control/agency.
    Range: [0.0, 1.0]
    
    High awareness + low boundary proximity = high dominance
    """
    dominance = m1_A * (1.0 - m19_z_prox)
    
    return clamp(dominance)


# ═══════════════════════════════════════════════════════════════════════════
# EXPORT ALL
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # FEP Core
    "compute_m56_surprise",
    "compute_m57_tokens_soc",
    "compute_m58_tokens_log",
    "compute_m59_p_antrieb",
    "compute_m60_delta_tokens",
    # FEP Decision
    "compute_m61_U",
    "compute_m62_R",
    "compute_m63_phi",
    "compute_m64_lambda_fep",
    # FEP Drive
    "compute_m65_alpha",
    "compute_m66_gamma",
    "compute_m67_precision",
    "compute_m68_prediction_err",
    # FEP Learning
    "compute_m69_model_evidence",
    "compute_m70_active_inf",
    # Evolution
    "compute_m71_ev_arousal",
    "compute_m72_ev_valence",
    "compute_m73_ev_v_intensity",
    "compute_m74_valence",
    "compute_m75_arousal",
    "compute_m76_dominance",
]


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    test_text = "I feel excited! However, I'm also thinking about the logical implications. What if we could work together?"
    test_context = {
        "prev_total_tokens": 50,
        "expected_phi": 0.3,
    }
    
    print("=" * 70)
    print("FEP & EVOLUTION METRICS TEST")
    print("=" * 70)
    
    # FEP Core
    m56 = compute_m56_surprise(test_text, test_context)
    m57 = compute_m57_tokens_soc(test_text)
    m58 = compute_m58_tokens_log(test_text)
    m59 = compute_m59_p_antrieb(m57, m58)
    m60 = compute_m60_delta_tokens(m57 + m58, test_context)
    
    print(f"\n🎯 FEP Core:")
    print(f"  m56_surprise:     {m56:.3f}")
    print(f"  m57_tokens_soc:   {m57:.1f}")
    print(f"  m58_tokens_log:   {m58:.1f}")
    print(f"  m59_p_antrieb:    {m59:.3f}")
    print(f"  m60_delta_tokens: {m60:+.1f}")
    
    # FEP Decision (mock dependencies)
    m2_PCI = 0.65
    m4_flow = 0.82
    
    m61 = compute_m61_U(m56, m2_PCI)
    m62 = compute_m62_R(m59, m4_flow)
    m63 = compute_m63_phi(m61, m62)
    m64 = compute_m64_lambda_fep(m63, test_context)
    
    print(f"\n🎲 FEP Decision:")
    print(f"  m61_U:            {m61:.3f}")
    print(f"  m62_R:            {m62:.3f}")
    print(f"  m63_phi:          {m63:+.3f}")
    print(f"  m64_lambda_fep:   {m64:.3f}")
    
    # FEP Drive
    m65 = compute_m65_alpha(m57)
    m66 = compute_m66_gamma(m58)
    m67 = compute_m67_precision(m65, m66)
    m68 = compute_m68_prediction_err(m65, m66)
    
    print(f"\n🚀 FEP Drive:")
    print(f"  m65_alpha:        {m65:.3f}")
    print(f"  m66_gamma:        {m66:.3f}")
    print(f"  m67_precision:    {m67:.3f}")
    print(f"  m68_balance:      {m68:.3f}")
    
    # FEP Learning
    m69 = compute_m69_model_evidence(m64, test_context)
    m70 = compute_m70_active_inf(m67)
    
    print(f"\n📚 FEP Learning:")
    print(f"  m69_learning_rate: {m69:.3f}")
    print(f"  m70_decay_factor:  {m70:.3f}")
    
    # Evolution (mock dependencies)
    m1_A = 0.75
    m5_coh = 0.72
    m15_affekt_a = 0.68
    m19_z_prox = 0.08
    
    m71 = compute_m71_ev_arousal(m15_affekt_a, m4_flow)
    m72 = compute_m72_ev_valence(m1_A, m5_coh)
    m73 = compute_m73_ev_v_intensity(m71)
    m74 = compute_m74_valence(m72)
    m75 = compute_m75_arousal(m71)
    m76 = compute_m76_dominance(m1_A, m19_z_prox)
    
    print(f"\n🧬 Evolution:")
    print(f"  m71_ev_arousal:   {m71:.3f}")
    print(f"  m72_ev_valence:   {m72:.3f}")
    print(f"  m73_intensity:    {m73:.3f}")
    print(f"  m74_valence:      {m74:.3f} (binary)")
    print(f"  m75_arousal:      {m75:.3f}")
    print(f"  m76_dominance:    {m76:.3f}")
    
    print(f"\n✅ 21 new FEP & Evolution metrics implemented!")
