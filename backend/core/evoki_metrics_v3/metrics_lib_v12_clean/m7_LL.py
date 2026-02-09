"""
m7_LL: Lambert-Light Turbidity Index

V11.1 ANDROMATIK FORMULA (CORRECTED 2026-02-08):
    LL[i] = clip₀₁(0.55·rep_same + 0.25·(1-flow) + 0.20·(1-coh))

Measures "turbidity" or "logic loss" - opacity in thinking patterns.
Combination of repetition, broken flow, and incoherence.

CHANGELOG:
    2026-02-08: CRITICAL BUG FIX by CODEX
        - Added missing coh parameter (20% weight)
        - Fixed coefficients: 0.6→0.55 (rep_same), 0.4→0.25 (flow)
        - Breaking change: Function signature changed from 2 to 3 parameters

Reference:
    V11_1_FORMULAS_COMPLETE.md:86-99
    EVOKI V3.0 Andromatik Master Specification
"""

from ._helpers import clamp


def compute_m7_LL(rep_same: float, flow: float, coh: float) -> float:
    """
    Calculate m7_LL (Lambert-Light Turbidity Index)
    
    V11.1 CORRECT FORMULA:
        LL = 0.55·rep_same + 0.25·(1-flow) + 0.20·(1-coh)
    
    Args:
        rep_same: Repetition to same role [0,1] - overlap with previous text
        flow: Temporal continuity [0,1] - smoothness of production
        coh: Coherence [0,1] - semantic consistency
    
    Returns:
        LL score [0, 1] - Turbidity/Logic Loss (higher = more turbid)
    
    Example:
        >>> compute_m7_LL(rep_same=0.5, flow=0.8, coh=0.7)
        0.385
        # 0.55*0.5 + 0.25*(1-0.8) + 0.20*(1-0.7)
        # = 0.275 + 0.05 + 0.06 = 0.385
    """
    LL_raw = (
        0.55 * rep_same +
        0.25 * (1.0 - flow) +
        0.20 * (1.0 - coh)
    )
    return round(clamp(LL_raw), 4)


__all__ = ['compute_m7_LL']
