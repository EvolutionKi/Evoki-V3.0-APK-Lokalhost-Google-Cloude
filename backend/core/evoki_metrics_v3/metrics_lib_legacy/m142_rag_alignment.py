"""
Evoki Metrics Library - m142_rag_alignment

Meta-cognition metric: RAG (Retrieval-Augmented Generation) alignment.
"""

def compute_m142_rag_alignment(rag_score: float) -> float:
    """
    m142_rag_alignment: RAG Alignment
    
    SPEC: clamp(rag_score)
    
    Measures alignment between retrieval and generation.
    
    Reference: EVOKI_V3_METRICS_SPECIFICATION.md
    """
    return round(max(0.0, min(1.0, rag_score)), 4)
