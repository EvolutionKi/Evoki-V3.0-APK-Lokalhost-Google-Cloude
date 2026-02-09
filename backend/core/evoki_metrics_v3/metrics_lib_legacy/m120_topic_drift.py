"""
Evoki Metrics Library - m120_topic_drift

Cognitive metric: Topic drift from conversation start.
"""

def compute_m120_topic_drift(similarity_to_first: float) -> float:
    """
    m120_topic_drift: Topic Drift
    
    SPEC: 1 - similarity_to_first
    
    Measures how far the conversation has drifted from initial topic.
    
    Args:
        similarity_to_first: Cosine similarity to first interaction [0, 1]
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(1.0 - similarity_to_first, 4)
