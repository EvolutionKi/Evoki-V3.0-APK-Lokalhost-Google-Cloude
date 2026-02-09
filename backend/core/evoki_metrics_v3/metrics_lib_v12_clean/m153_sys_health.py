"""
m153: System-Gesundheit
"""

from ._helpers import clamp, tokenize


def compute_m153_sys_health(latency: float, error_rate: float, mem_pressure: float) -> float:
    """m153: System-Gesundheit"""
    health = 1.0 - (0.3 * min(1.0, latency / 5.0) + 0.4 * error_rate + 0.3 * mem_pressure)
    return round(clamp(health), 4)
