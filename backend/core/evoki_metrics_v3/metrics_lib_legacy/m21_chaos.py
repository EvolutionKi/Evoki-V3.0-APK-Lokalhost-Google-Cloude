"""m21_chaos: Entropy-Chaos
SPEC Formula: chaos = clip(s_entropy / 4.0)
Reference: EVOKI_V3_METRICS_SPECIFICATION.md:3215-3237"""
from ._helpers import clamp
def compute_m21_chaos(s_entropy: float) -> float:
    return round(clamp(s_entropy / 4.0), 4)
__all__ = ['compute_m21_chaos']
