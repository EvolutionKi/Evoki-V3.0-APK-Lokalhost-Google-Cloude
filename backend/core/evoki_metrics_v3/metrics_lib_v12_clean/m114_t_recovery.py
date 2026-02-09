"""m114_t_recovery: Recovery Rate
Measures integration improvement: grad(T_integ)"""
def compute_m114_t_recovery(t_integ_current: float, t_integ_prev: float) -> float:
    return round(t_integ_current - t_integ_prev, 4)
__all__ = ['compute_m114_t_recovery']
