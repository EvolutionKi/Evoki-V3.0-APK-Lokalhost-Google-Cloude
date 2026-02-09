"""
m2_PCI: Perturbational Complexity Index (Integrated Information)

V11.1 ANDROMATIK FORMULA - V2.0 PROVEN!

PCI[i] = clip01(
    0.4 × flow[i] +          # Flow (40%)
    0.35 × coh[i] +          # Coherence (35%)
    0.25 × (1 − LL[i])       # Anti-Loops (25%)
)

This measures PROCESS COHERENCE, not linguistic complexity!
CRITICAL: This formula is V2.0 PROVEN! Do NOT modify!
"""

from ._helpers import clamp


def compute_m2_PCI(
    flow: float,
    coh: float,
    LL: float
) -> float:
    """
    Calculate m2_PCI (Integrated Information)
    
    Args:
        flow: Flow state [0,1] (m4_flow)
        coh: Coherence [0,1] (m5_coh)
        LL: Lambert-Light turbidity [0,1] (m7_LL)
    
    Returns:
        PCI score [0, 1] - Process Coherence / Integrated Information
    """
    PCI_raw = (
        0.4 * flow +             # Flow dominates
        0.35 * coh +             # Coherence second
        0.25 * (1.0 - LL)        # Clear = high integration
    )
    
    return round(clamp(PCI_raw), 4)


__all__ = ['compute_m2_PCI']
