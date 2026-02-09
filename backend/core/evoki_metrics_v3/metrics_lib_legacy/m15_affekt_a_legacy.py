"""m15_affekt_a_legacy: Legacy Affekt (V3 Original Formula)
Original V3 formula kept for comparison & fallback.
A_legacy = clip01(0.40*flow + 0.30*coh + 0.20*(1-LL) + 0.10*(1-ZLF))"""
from ._helpers import clamp
def compute_m15_affekt_a_legacy(flow: float, coh: float, ll: float, zlf: float) -> float:
    a_legacy = 0.40 * flow + 0.30 * coh + 0.20 * (1.0 - ll) + 0.10 * (1.0 - zlf)
    return round(clamp(a_legacy), 4)
__all__ = ['compute_m15_affekt_a_legacy']
