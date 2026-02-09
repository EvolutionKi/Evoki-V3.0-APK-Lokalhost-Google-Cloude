"""
Evoki Metrics Library - m118_exclamation_density

Cognitive metric: Exclamation density (proportion of exclamations).
"""

def compute_m118_exclamation_density(text: str) -> float:
    """
    m118_exclamation_density: Exclamation Density
    
    SPEC: exclamations / total_sentences
    
    Measures emphasis/intensity level in communication.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    exclamations = text.count('!')
    sentences = text.count('.') + text.count('!') + text.count('?')
    
    return round(exclamations / max(1, sentences), 4)
