#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRAIN ENGINE — m96-m100 (Text Granularity / Sentiment)

Implementiert gemäß evoki_fullspectrum168_contract.json:
- m96_grain_word: Wort-Komplexität
- m97_grain_impact: Emotionale Dichte
- m98_grain_sentiment: Sentiment-Varianz
- m99_grain_novelty: Novelty-Index (Type-Token-Ratio)
- m100_causal_1: Kausaler Index
"""

import re
import numpy as np
from typing import Dict, List, Set


# =============================================================================
# m96: Wort-Komplexität
# =============================================================================
def compute_m96_grain_word(text: str) -> float:
    """
    Wort-Komplexität: Durchschnittliche Wortlänge.
    
    Range: [0.0, 1.0]
    Formula: min(1.0, len(word)/12.0) per word, then average
    SPEC: FINAL7 Line 5942
    """
    if not text or not text.strip():
        return 0.0
    
    words = text.split()
    if not words:
        return 0.0
    
    # SPEC FORMULA: Per-word complexity, then average
    total_complexity = 0.0
    for word in words:
        word_complexity = min(1.0, len(word) / 12.0)
        total_complexity += word_complexity
    
    return total_complexity / len(words)


# =============================================================================
# m97: Emotionale Dichte
# =============================================================================
def compute_m97_grain_impact(text: str, emotion_lexika: Dict[str, Dict[str, float]]) -> float:
    """
    Emotionale Dichte: Anteil emotionaler Wörter.
    
    Range: [0.0, 1.0]
    Formula: % of words matching emotion lexika
    """
    if not text or not text.strip():
        return 0.0
    
    words = text.lower().split()
    if not words:
        return 0.0
    
    # Combine all emotion lexika
    emotional_terms: Set[str] = set()
    for lex_name, lex_dict in emotion_lexika.items():
        if "emotion" in lex_name.lower() or "sent_" in lex_name.lower():
            emotional_terms.update(lex_dict.keys())
    
    if not emotional_terms:
        return 0.0
    
    # Count hits
    hits = sum(1 for w in words if w in emotional_terms)
    
    # SPEC FORMULA: * 5.0 scale factor (FINAL7 Line 6014)
    return min(1.0, hits / len(words) * 5.0)


# =============================================================================
# m98: Sentiment-Varianz
# =============================================================================
def compute_m98_grain_sentiment(text: str, emotion_lexika: Dict[str, Dict[str, float]]) -> float:
    """
    Lokale Sentiment-Varianz auf Wort-Ebene.
    
    Range: [0.0, 1.0]
    Formula: Variance of word-level sentiment scores
    """
    if not text or not text.strip():
        return 0.0
    
    words = text.lower().split()
    if len(words) < 2:
        return 0.0
    
    # Get positive/negative lexika
    pos_lex = emotion_lexika.get("Emotion_pos", {})
    neg_lex = emotion_lexika.get("Emotion_neg", {})
    
    if not pos_lex and not neg_lex:
        return 0.0
    
    # Assign sentiment to each word: +val for positive, -val for negative, 0 for neutral
    sentiments: List[float] = []
    for w in words:
        if w in pos_lex:
            sentiments.append(pos_lex[w])
        elif w in neg_lex:
            sentiments.append(-neg_lex[w])
        else:
            sentiments.append(0.0)
    
    if not sentiments:
        return 0.0
    
    # Calculate variance
    variance = float(np.var(sentiments))
    
    # SPEC FORMULA: variance * 4.0 (FINAL7 Line 6082)
    return min(1.0, variance * 4.0)


# =============================================================================
# m99: Novelty Index (Type-Token-Ratio)
# =============================================================================
def compute_m99_grain_novelty(text: str) -> float:
    """
    Novelty-Index: Inverse of repetition (Type-Token-Ratio variant).
    
    Range: [0.0, 1.0]
    Formula: 1.0 - (1.0 - unique/total) = unique/total (simplified)
    SPEC: FINAL7 Line 6156-6158
    """
    if not text or not text.strip():
        return 0.0
    
    words = text.lower().split()
    if len(words) < 2:
        return 1.0  # Single word = perfectly novel
    
    unique_count = len(set(words))
    total_count = len(words)
    
    # SPEC FORMULA (simplified from double inversion):
    # repetition_score = 1 - (unique/total)
    # novelty = 1 - repetition_score = unique/total
    return unique_count / total_count


# =============================================================================
# m100: Kausaler Index
# =============================================================================
def compute_m100_causal_1(text: str) -> float:
    """
    Kausaler Index: Dichte kausaler Konnektoren.
    
    Range: [0.0, 1.0]
    Formula: Count of causal markers / words
    """
    if not text or not text.strip():
        return 0.0
    
    # Causal connectors (German)
    causal_markers = [
        'weil', 'daher', 'deshalb', 'denn', 'folglich', 
        'somit', 'deswegen', 'dadurch', 'infolgedessen',
        'aus diesem grund', 'darum', 'also'
    ]
    
    text_lower = text.lower()
    words = text.split()
    
    if not words:
        return 0.0
    
    # Count markers
    hits = 0
    for marker in causal_markers:
        if ' ' in marker:
            # Multi-word marker
            hits += text_lower.count(marker)
        else:
            # Single word marker (use word boundaries)
            pattern = r'\b' + re.escape(marker) + r'\b'
            hits += len(re.findall(pattern, text_lower))
    
    # SPEC FORMULA: min(1.0, hits / 4.0)
    # 4 causal markers = 1.0 (NICHT word-normalized!)
    return min(1.0, hits / 4.0)


# =============================================================================
# EXPORT ALL
# =============================================================================
__all__ = [
    'compute_m96_grain_word',
    'compute_m97_grain_impact',
    'compute_m98_grain_sentiment',
    'compute_m99_grain_novelty',
    'compute_m100_causal_1',
]
