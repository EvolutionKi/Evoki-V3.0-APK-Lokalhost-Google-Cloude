"""
m167: Input-Rauschen
"""

import re


def compute_m167_noise(text: str) -> float:
    """m167: Input-Rauschen"""
    if not text:
        return 0.0
    typo_pattern = r'\b(\w)\1{2,}\b'
    fragment_pattern = r'^[a-z]{1,3}$'
    typos = len(re.findall(typo_pattern, text, re.IGNORECASE))
    words = text.split()
    fragments = sum(1 for w in words if re.match(fragment_pattern, w))
    noise_score = (typos * 0.3 + fragments / max(1, len(words)) * 0.7)
    return round(min(1.0, noise_score), 4)
