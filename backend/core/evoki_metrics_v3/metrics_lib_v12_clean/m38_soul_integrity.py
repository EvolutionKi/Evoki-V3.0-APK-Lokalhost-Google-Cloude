"""m38_soul_integrity: Seelen-Integrität"""
import math
from typing import List
from ._helpers import clamp

def compute_m38_soul_integrity(b_vector: List[float] = None) -> float:
    if not b_vector or len(b_vector) != 7:
        return 1.0
    norm = math.sqrt(sum(x**2 for x in b_vector))
    return round(clamp(norm / 7.0), 4)
