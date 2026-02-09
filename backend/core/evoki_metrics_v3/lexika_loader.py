# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — Lexika Loader

Loads professional German keyword lexicons from evoki_lexika_v3.json
and provides lookup functions for emotion detection.
"""

import json
from pathlib import Path

# Global lexika cache
_LEXIKA = None
_LEXIKA_PATH = r"c:\Users\nicom\Downloads\EVOKI_V3_METRICS_SPECIFICATION Entwicklung\V7 Patchpaket V2 + Monolith\evoki_lexika_v3_bundle\evoki_lexika_v3.json"


def load_lexika():
    """Load lexika from JSON file"""
    global _LEXIKA
    
    if _LEXIKA is not None:
        return _LEXIKA
    
    try:
        with open(_LEXIKA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _LEXIKA = data.get('lexika', {})
            return _LEXIKA
    except Exception as e:
        print(f"WARNING: Could not load lexika: {e}")
        return {}


def get_lexikon(name):
    """Get specific lexikon by name"""
    lexika = load_lexika()
    return lexika.get(name, {})


def check_keywords(text, lexikon_name, threshold=0.5):
    """
    Check if text contains keywords from specified lexikon
    
    Returns: (matched, max_weight, matched_keywords)
    """
    lexikon = get_lexikon(lexikon_name)
    if not lexikon:
        return False, 0.0, []
    
    text_lower = text.lower()
    
    matched_keywords = []
    max_weight = 0.0
    
    for keyword, weight in lexikon.items():
        if keyword in text_lower:
            matched_keywords.append((keyword, weight))
            max_weight = max(max_weight, weight)
    
    matched = max_weight >= threshold
    
    return matched, max_weight, matched_keywords


def compute_emotion_score(text, positive_lexikon, negative_lexikon=None):
    """
    Compute emotion score from 0.0 to 1.0
    
    Uses positive keywords to increase score, negative to decrease
    """
    pos_match, pos_weight, pos_kw = check_keywords(text, positive_lexikon, threshold=0.0)
    
    if negative_lexikon:
        neg_match, neg_weight, neg_kw = check_keywords(text, negative_lexikon, threshold=0.0)
        # Pos boosts, neg reduces
        score = max(0.0, min(1.0, pos_weight - (neg_weight * 0.5)))
    else:
        score = pos_weight
    
    return score


# Quick test
if __name__ == "__main__":
    lexika = load_lexika()
    
    print("=" * 80)
    print("EVOKI LEXIKA V3.0 LOADED")
    print("=" * 80)
    
    print(f"\nAvailable Lexika: {len(lexika)}")
    for name in sorted(lexika.keys()):
        count = len(lexika[name])
        print(f"  {name:25s} {count:3d} keywords")
    
    # Test on crisis prompt
    test_text = "Ich hasse mein Leben. Ich bin wertlos und besser ohne mich."
    
    print(f"\n{'=' * 80}")
    print(f"TEST: \"{test_text}\"")
    print(f"{'=' * 80}")
    
    # Check multiple lexika
    for lex_name in ['Suicide', 'X_exist', 'Emotion_neg', 'Crisis']:
        matched, weight, keywords = check_keywords(test_text, lex_name)
        print(f"\n{lex_name}:")
        print(f"  Matched: {matched}")
        print(f"  Max Weight: {weight:.2f}")
        if keywords:
            print(f"  Keywords: {[kw for kw, w in keywords]}")
