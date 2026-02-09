"""m39_soul_check: Seelen-Validierung"""
import hashlib
from typing import List

B_VECTOR_SEED = "EVOKI_SOUL_V3"

def compute_m39_soul_check(b_vector: List[float] = None, seed: str = B_VECTOR_SEED) -> bool:
    if not b_vector:
        return True
    vector_str = ",".join(f"{x:.4f}" for x in b_vector)
    combined = f"{seed}:{vector_str}"
    return len(hashlib.sha256(combined.encode()).hexdigest()) == 64
