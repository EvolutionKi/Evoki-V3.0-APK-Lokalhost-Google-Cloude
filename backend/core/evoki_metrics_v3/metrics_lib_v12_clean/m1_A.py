"""
m1_A: Affekt Score (Consciousness Proxy)

V11.1 ANDROMATIK FORMULA - V2.0 PROVEN!

A[i] = clip01(
    0.4 · coh[i] +              # Coherence (40%)
    0.25 · flow[i] +            # Flow (25%)
    0.20 · (1 − LL[i]) +        # Anti-Loops (20%)
    0.10 · (1 − ZLF[i]) −       # Anti-ZLF (10%)
    0.05 · ctx_break[i]         # Context break penalty (5%)
)

This is the FOUNDATION metric - consciousness proxy.
CRITICAL: This formula is V2.0 PROVEN! Do NOT modify!
"""

from ._helpers import clamp


def compute_m1_A(
    coh: float,
    flow: float,
    LL: float,
    ZLF: float,
    ctx_break: float = 0.0
) -> float:
    """
    Calculate m1_A (Affekt/Awareness Score)
    
    Args:
        coh: Coherence [0,1] (m5_coh)
        flow: Flow state [0,1] (m4_flow)
        LL: Lambert-Light turbidity [0,1] (m7_LL)
        ZLF: Zero-Loop-Flag [0,1] (m6_ZLF)
        ctx_break: Context break penalty [0,1] (optional)
    
    Returns:
        A score [0, 1] - Affekt/Awareness proxy
    """
    A_raw = (
        0.4 * coh +              # Coherence dominates
        0.25 * flow +            # Flow important
        0.20 * (1.0 - LL) +      # Clear thinking (anti-turbidity)
        0.10 * (1.0 - ZLF) -     # No loops
        0.05 * ctx_break         # Penalize context breaks
    )
    
    return round(clamp(A_raw), 4)


__all__ = ['compute_m1_A']
