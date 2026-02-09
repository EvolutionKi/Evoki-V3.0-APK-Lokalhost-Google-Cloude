"""m24_zeta: Stability Factor (Zeta)
SPEC: zeta = (1 - z_prox) × A
Measures system stability as inverse of death proximity weighted by affekt."""
def compute_m24_zeta(z_prox: float, A: float) -> float:
    return round((1.0 - z_prox) * A, 4)
__all__ = ['compute_m24_zeta']
