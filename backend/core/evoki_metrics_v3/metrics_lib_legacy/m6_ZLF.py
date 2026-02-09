"""
m6_ZLF: Zero-Loop-Flag (Loop Detection)

V11.1 ANDROMATIK (Lines 40, 173):
ZLF = clip01(0.5·lexicon_hit + 0.25·(1-flow) + 0.25·(1-coh))

Detects repetitive loops in thinking patterns.
Higher ZLF = more looping/stuck patterns.

Reference:
    V2.0 Andromatik V11.1 Master-Metrik-Registry
    Loop-Metriken Section, Line 173
"""

from ._helpers import clamp


def compute_m6_ZLF(flow: float, coherence: float, zlf_lexicon_hit: bool = False) -> float:
    """
    Calculate m6_ZLF (Zero-Loop-Flag)
    
    Args:
        flow: Flow score [0,1] (m4_flow)
        coherence: Coherence score [0,1] (m5_coh)
        zlf_lexicon_hit: Lexicon indicator (True if ZLF terms detected)
    
    Returns:
        ZLF score [0, 1] - Higher means more looping
    """
    lexicon_term = 0.5 if zlf_lexicon_hit else 0.0
    zlf_raw = lexicon_term + 0.25 * (1.0 - flow) + 0.25 * (1.0 - coherence)
    return round(clamp(zlf_raw), 4)


__all__ = ['compute_m6_ZLF']
