"""
Evoki Metrics Library - m117_question_density

Cognitive metric: Question density (proportion of questions).
"""

def compute_m117_question_density(text: str) -> float:
    """
    m117_question_density: Question Density
    
    SPEC: questions / total_sentences
    
    Measures inquiry/uncertainty level in communication.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    questions = text.count('?')
    sentences = text.count('.') + text.count('!') + text.count('?')
    
    return round(questions / max(1, sentences), 4)
