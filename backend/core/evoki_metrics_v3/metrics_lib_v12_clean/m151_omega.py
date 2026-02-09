"""
m151_omega: OMEGA-Konstante
"""

from ._helpers import clamp, tokenize


def compute_m151_omega(A: float, PCI: float, z_prox: float, trauma_load: float) -> float:
    """m151_omega: OMEGA-Konstante"""
    positive = 0.4 * A + 0.3 * PCI
    negative = 0.3 * z_prox + 0.2 * trauma_load
    omega = positive - negative
    return round(clamp(omega, -1.0, 1.0), 4)
