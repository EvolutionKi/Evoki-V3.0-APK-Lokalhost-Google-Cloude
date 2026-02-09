"""m17_nabla_a: Gradient of A (Delta A)
∇A = A_current - A_previous
Measures consciousness evolution direction."""
def compute_m17_nabla_a(a_current: float, a_previous: float) -> float:
    return round(a_current - a_previous, 4)
__all__ = ['compute_m17_nabla_a']
