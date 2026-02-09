"""
m20_phi_proxy: Phi Consciousness Proxy

SPEC Formula:
    phi_proxy = A × PCI

Simple product of Affekt and Integrated Information.
Represents integrated consciousness estimate (Tononi's Phi concept).

Reference: EVOKI_V3_METRICS_SPECIFICATION.md:3168-3185
"""


def compute_m20_phi_proxy(A: float, PCI: float) -> float:
    """
    Calculate m20_phi_proxy (Consciousness Proxy)
    
    Args:
        A: Affekt score [0,1] (m1_A)
        PCI: Integrated information [0,1] (m2_PCI)
    
    Returns:
        Phi proxy [0, 1] - Consciousness estimate
    """
    return round(A * PCI, 4)


__all__ = ['compute_m20_phi_proxy']
