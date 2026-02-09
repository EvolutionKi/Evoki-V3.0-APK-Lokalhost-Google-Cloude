# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — HYPERMETRICS MODULE

Dyadic, Composite, and Advanced Hypermetrics (m40-m55)

These metrics measure interaction patterns, conversation dynamics,
and composite scores across multiple dimensions.

Based on evoki_fullspectrum168_contract.json
"""

from typing import Dict
import re


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# HYPERMETRICS / DYADIC (m40-m44)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m40_h_conv(text: str, context: Dict) -> float:
    """
    m40_h_conv - Hypermetric Conversation Flow
    
    Measures conversational coherence and flow.
    Range: [0.0, 1.0]
    
    Based on:
    - Sentence connectivity
    - Topic consistency
    - Logical progression
    """
    # Simple implementation: check for connectors
    connectors = ['also', 'however', 'therefore', 'furthermore', 'additionally',
                  'but', 'and', 'so', 'thus', 'hence']
    
    text_lower = text.lower()
    connector_count = sum(1 for conn in connectors if conn in text_lower)
    
    # Normalize by text length (roughly)
    words = len(text.split())
    if words == 0:
        return 0.0
    
    h_conv = min(1.0, connector_count / max(1, words / 20))
    
    return clamp(h_conv)


def compute_m41_h_symbol(text: str, context: Dict) -> float:
    """
    m41_h_symbol - Symbol/Emoji Usage
    
    Binary indicator of symbolic communication.
    Range: {0.0, 1.0} (binary)
    
    Returns 1.0 if text contains emojis or symbolic characters.
    """
    # Check for common emojis and symbols
    has_emoji = bool(re.search(r'[😀-🙏🌀-🗿🚀-🛿✨💫⭐🔥💎🌊⚡]', text))
    has_special = bool(re.search(r'[★☆♥♡→←↑↓⇒⇐]', text))
    
    return 1.0 if (has_emoji or has_special) else 0.0


def compute_m42_nabla_dyad(
    current_h_conv: float,
    context: Dict
) -> float:
    """
    m42_nabla_dyad - Dyadic Flow Derivative
    
    Change in conversational flow over time.
    Range: [-0.5, 0.5]
    
    nabla_dyad = h_conv(t) - h_conv(t-1)
    """
    prev_h_conv = context.get("prev_h_conv", current_h_conv)
    
    nabla = current_h_conv - prev_h_conv
    
    return clamp(nabla, -0.5, 0.5)


def compute_m43_pacing(text: str, context: Dict) -> float:
    """
    m43_pacing - Conversation Pacing
    
    Measures rhythm and cadence of dialogue.
    Range: [0.0, 1.0]
    
    Based on:
    - Sentence length variation
    - Message timing (if available in context)
    """
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return 0.5  # Neutral pacing
    
    # Calculate length variation
    lengths = [len(s.split()) for s in sentences]
    mean_len = sum(lengths) / len(lengths)
    variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
    
    # Normalize pacing score (more variation = different pacing)
    pacing = 1.0 - min(1.0, variance / max(1, mean_len ** 2))
    
    return clamp(pacing)


def compute_m44_mirroring(text: str, context: Dict) -> float:
    """
    m44_mirroring - Linguistic Mirroring
    
    Measures how much current text mirrors previous text.
    Range: [0.0, 1.0]
    
    Based on:
    - Shared vocabulary
    - Syntactic similarity
    """
    prev_text = context.get("prev_text", "")
    
    if not prev_text:
        return 0.0
    
    # Extract words
    current_words = set(text.lower().split())
    prev_words = set(prev_text.lower().split())
    
    if not prev_words:
        return 0.0
    
    # Jaccard similarity
    intersection = current_words & prev_words
    union = current_words | prev_words
    
    mirroring = len(intersection) / len(union) if union else 0.0
    
    return clamp(mirroring)


# ═══════════════════════════════════════════════════════════════════════════
# HYPERMETRICS / COMPOSITE (m46, m48, m51, m54, m55)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m46_rapport(
    m43_pacing: float,
    m44_mirroring: float,
    m45_trust_score: float
) -> float:
    """
    m46_rapport - Composite Rapport Score
    
    Combines pacing, mirroring, and trust.
    Range: [0.0, 1.0]
    
    rapport = weighted_avg(pacing, mirroring, trust)
    """
    rapport = (
        0.3 * m43_pacing +
        0.4 * m44_mirroring +
        0.3 * m45_trust_score
    )
    
    return clamp(rapport)


def compute_m48_hyp_1(m46_rapport: float) -> float:
    """
    m48_hyp_1 - Hypermetric 1 (Alias of rapport)
    
    Range: [0.0, 1.0]
    
    This is an alias for m46_rapport.
    """
    return m46_rapport


def compute_m51_hyp_4(
    m1_A: float,
    m5_coh: float,
    m63_phi: float
) -> float:
    """
    m51_hyp_4 - Hypermetric 4 (Composite Integration)
    
    Combines awareness, coherence, and phi.
    Range: [0.0, 1.0]
    """
    hyp_4 = (m1_A + m5_coh + m63_phi) / 3.0
    
    return clamp(hyp_4)


def compute_m54_hyp_7(
    m4_flow: float,
    m7_LL: float
) -> float:
    """
    m54_hyp_7 - Hypermetric 7 (Flow-Optics Composite)
    
    Combines flow and luminosity.
    Range: [0.0, 1.0]
    """
    hyp_7 = (m4_flow + m7_LL) / 2.0
    
    return clamp(hyp_7)


def compute_m55_hyp_8(
    m19_z_prox: float,
    m29_guardian: float
) -> float:
    """
    m55_hyp_8 - Hypermetric 8 (Safety Composite)
    
    Combines proximity to boundary and guardian status.
    Range: [0.0, 1.0]
    """
    # Inverse relationship - lower z_prox and guardian means higher safety
    hyp_8 = 1.0 - ((m19_z_prox + m29_guardian) / 2.0)
    
    return clamp(hyp_8)


# ═══════════════════════════════════════════════════════════════════════════
# HYPERMETRICS / PHYSICS & TEMPORAL (m52, m53)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m52_hyp_5(
    m26_nabla_phi: float,
    m27_lambda_depth: float
) -> float:
    """
    m52_hyp_5 - Hypermetric 5 (Physics Composite)
    
    Combines phi gradient and depth.
    Range: [0.0, 1.0]
    """
    # Weighted combination
    hyp_5 = 0.6 * abs(m26_nabla_phi) + 0.4 * m27_lambda_depth
    
    return clamp(hyp_5)


def compute_m53_hyp_6(context: Dict) -> float:
    """
    m53_hyp_6 - Hypermetric 6 (Temporal)
    
    Time-based metric, measures session duration or similar.
    Range: [0.0, ∞]
    
    For now, returns turn number as proxy for temporal progression.
    """
    turn = context.get("turn", 0)
    
    # Return turn number (unbounded)
    return float(turn)


# ═══════════════════════════════════════════════════════════════════════════
# EXPORT ALL
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "compute_m40_h_conv",
    "compute_m41_h_symbol",
    "compute_m42_nabla_dyad",
    "compute_m43_pacing",
    "compute_m44_mirroring",
    "compute_m46_rapport",
    "compute_m48_hyp_1",
    "compute_m51_hyp_4",
    "compute_m52_hyp_5",
    "compute_m53_hyp_6",
    "compute_m54_hyp_7",
    "compute_m55_hyp_8",
]


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    test_text = "This is a test. However, I think we should also consider the other option. ⭐"
    test_context = {
        "prev_text": "This is interesting.",
        "prev_h_conv": 0.5,
        "turn": 5
    }
    
    print("=" * 70)
    print("HYPERMETRICS TEST")
    print("=" * 70)
    
    m40 = compute_m40_h_conv(test_text, test_context)
    m41 = compute_m41_h_symbol(test_text, test_context)
    m42 = compute_m42_nabla_dyad(m40, test_context)
    m43 = compute_m43_pacing(test_text, test_context)
    m44 = compute_m44_mirroring(test_text, test_context)
    
    print(f"\nDyadic Metrics:")
    print(f"  m40_h_conv:      {m40:.3f}")
    print(f"  m41_h_symbol:    {m41:.3f} (binary)")
    print(f"  m42_nabla_dyad:  {m42:+.3f}")
    print(f"  m43_pacing:      {m43:.3f}")
    print(f"  m44_mirroring:   {m44:.3f}")
    
    # Mock dependencies
    m45 = 0.75  # trust_score (already exists)
    m46 = compute_m46_rapport(m43, m44, m45)
    m48 = compute_m48_hyp_1(m46)
    
    print(f"\nComposite Metrics:")
    print(f"  m46_rapport:     {m46:.3f}")
    print(f"  m48_hyp_1:       {m48:.3f} (alias)")
    
    # More composites (mock dependencies)
    m51 = compute_m51_hyp_4(0.75, 0.72, 0.68)
    m52 = compute_m52_hyp_5(0.05, 0.6)
    m53 = compute_m53_hyp_6(test_context)
    m54 = compute_m54_hyp_7(0.82, 0.25)
    m55 = compute_m55_hyp_8(0.08, 0.0)
    
    print(f"  m51_hyp_4:       {m51:.3f}")
    print(f"  m52_hyp_5:       {m52:.3f}")
    print(f"  m53_hyp_6:       {m53:.3f} (temporal)")
    print(f"  m54_hyp_7:       {m54:.3f}")
    print(f"  m55_hyp_8:       {m55:.3f}")
    
    print(f"\n✅ 12 new Hypermetrics implemented!")
