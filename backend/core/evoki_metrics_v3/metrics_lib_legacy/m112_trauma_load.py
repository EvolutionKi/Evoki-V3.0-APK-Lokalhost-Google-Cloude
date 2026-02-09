"""m112_trauma_load: Trauma Load ⚠️ SAFETY METRIC
Weighted sum of trauma vectors: 0.4*panic + 0.4*disso + 0.2*(1-integ)"""
from ._helpers import clamp
def compute_m112_trauma_load(t_panic: float, t_disso: float, t_integ: float) -> float:
    val = 0.4 * t_panic + 0.4 * t_disso + 0.2 * (1 - t_integ)
    return round(clamp(val), 4)
__all__ = ['compute_m112_trauma_load']
