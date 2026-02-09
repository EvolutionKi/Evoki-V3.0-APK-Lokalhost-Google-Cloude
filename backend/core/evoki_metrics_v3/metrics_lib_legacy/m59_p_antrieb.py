"""
m59_p_antrieb: Antriebsdruck
"""

from ._helpers import clamp, tokenize


def compute_m59_p_antrieb(tokens_soc: float, tokens_log: float, stagnation: float = 0.0) -> float:
    """m59_p_antrieb: Antriebsdruck"""
    return round(clamp((tokens_soc + tokens_log) / 200.0 + stagnation), 4)
