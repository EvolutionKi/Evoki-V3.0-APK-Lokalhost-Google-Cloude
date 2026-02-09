"""m111_turbidity_total: Total Turbidity
Composite trauma turbidity from all trauma vectors."""
def compute_m111_turbidity_total(t_panic: float, t_disso: float, t_shock: float, t_integ: float) -> float:
    return round((t_panic + t_disso + t_shock + (1 - t_integ)) / 4.0, 4)
__all__ = ['compute_m111_turbidity_total']
