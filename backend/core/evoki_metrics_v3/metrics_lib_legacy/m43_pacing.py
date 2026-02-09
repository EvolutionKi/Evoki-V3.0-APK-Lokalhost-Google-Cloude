"""
m43_pacing: Tempo-Synchronisation
"""




def compute_m43_pacing(wc_user: int = 50, wc_ai: int = 50) -> float:
    """m43_pacing: Tempo-Synchronisation"""
    max_wc = max(wc_user, wc_ai, 1)
    diff = abs(wc_user - wc_ai)
    return round(1.0 - (diff / max_wc), 4)
