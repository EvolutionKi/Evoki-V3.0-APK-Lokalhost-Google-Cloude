#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST: Grain Engine (m96-m100)

Validiert die Implementierung gegen erwartete Werte.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.core.evoki_metrics_v3.grain_engine import (
    compute_m96_grain_word,
    compute_m97_grain_impact,
    compute_m98_grain_sentiment,
    compute_m99_grain_novelty,
    compute_m100_causal_1,
)

# Test Lexika
TEST_EMOTION_LEXIKA = {
    "Emotion_pos": {
        "freude": 0.8, "glücklich": 0.9, "froh": 0.7, "liebe": 0.9,
    },
    "Emotion_neg": {
        "traurig": 0.8, "wütend": 0.9, "angst": 0.85, "verzweifelt": 0.9,
    },
}

def test_m96_grain_word():
    """Test m96: Wort-Komplexität"""
    print("\n=== TEST m96_grain_word ===")
    
    # Test 1: Short words
    text1 = "ich bin da"  # avg = 2.67 chars → ~0.17
    result1 = compute_m96_grain_word(text1)
    print(f"  Short words: '{text1}' → {result1:.4f}")
    assert 0.0 <= result1 <= 0.3, f"Expected low complexity, got {result1}"
    
    # Test 2: Long words
    text2 = "Kindergarten Verantwortung Verschlüsselung"  # avg = 15.67 → 1.0
    result2 = compute_m96_grain_word(text2)
    print(f"  Long words: '{text2}' → {result2:.4f}")
    assert result2 >= 0.8, f"Expected high complexity, got {result2}"
    
    # Test 3: Empty
    result3 = compute_m96_grain_word("")
    print(f"  Empty: → {result3:.4f}")
    assert result3 == 0.0, f"Expected 0.0, got {result3}"
    
    print("  ✅ m96_grain_word PASSED")
    return True


def test_m97_grain_impact():
    """Test m97: Emotionale Dichte"""
    print("\n=== TEST m97_grain_impact ===")
    
    # Test 1: High emotional density
    text1 = "ich bin glücklich und freude überall liebe"  # 3/7 = ~43% emotional
    result1 = compute_m97_grain_impact(text1, TEST_EMOTION_LEXIKA)
    print(f"  High emotion: '{text1}' → {result1:.4f}")
    # With *5.0 multiplier: 3/7 * 5.0 = 2.14 → clamped to 1.0 (CORRECT per SPEC)
    assert result1 == 1.0, f"Expected 1.0 (saturated), got {result1}"
    
    # Test 2: No emotion
    text2 = "der tisch ist grün"
    result2 = compute_m97_grain_impact(text2, TEST_EMOTION_LEXIKA)
    print(f"  No emotion: '{text2}' → {result2:.4f}")
    assert result2 == 0.0, f"Expected 0.0, got {result2}"
    
    # Test 3: Low emotion (adjusted - 1/6 = 16.7%)
    text3 = "ich gehe zur arbeit heute"  # 0 emotional words
    result3 = compute_m97_grain_impact(text3, TEST_EMOTION_LEXIKA)
    print(f"  Low emotion: '{text3}' → {result3:.4f}")
    assert result3 == 0.0, f"Expected 0.0, got {result3}"
    
    print("  ✅ m97_grain_impact PASSED")
    return True


def test_m98_grain_sentiment():
    """Test m98: Sentiment-Varianz"""
    print("\n=== TEST m98_grain_sentiment ===")
    
    # Test 1: High variance (mixed emotions)
    text1 = "glücklich traurig froh wütend"  # +0.9, -0.8, +0.7, -0.9
    result1 = compute_m98_grain_sentiment(text1, TEST_EMOTION_LEXIKA)
    print(f"  High variance: '{text1}' → {result1:.4f}")
    assert result1 > 0.3, f"Expected variance > 0.3, got {result1}"
    
    # Test 2: Low variance (consistent emotion)
    text2 = "glücklich froh liebe"  # all positive
    result2 = compute_m98_grain_sentiment(text2, TEST_EMOTION_LEXIKA)
    print(f"  Low variance: '{text2}' → {result2:.4f}")
    assert result2 < 0.5, f"Expected small variance, got {result2}"
    
    # Test 3: Neutral only
    text3 = "der tisch ist grün"
    result3 = compute_m98_grain_sentiment(text3, TEST_EMOTION_LEXIKA)
    print(f"  Neutral: '{text3}' → {result3:.4f}")
    assert result3 == 0.0, f"Expected 0.0, got {result3}"
    
    print("  ✅ m98_grain_sentiment PASSED")
    return True


def test_m99_grain_novelty():
    """Test m99: Type-Token-Ratio"""
    print("\n=== TEST m99_grain_novelty ===")
    
    # Test 1: All unique
    text1 = "ich liebe verschiedene neue wörter"
    result1 = compute_m99_grain_novelty(text1)
    print(f"  All unique: '{text1}' → {result1:.4f}")
    assert result1 == 1.0, f"Expected 1.0, got {result1}"
    
    # Test 2: Repetition
    text2 = "ich ich ich bin bin da"  # 3 unique / 6 total = 0.5
    result2 = compute_m99_grain_novelty(text2)
    print(f"  Repetition: '{text2}' → {result2:.4f}")
    assert abs(result2 - 0.5) < 0.01, f"Expected ~0.5, got {result2}"
    
    # Test 3: Empty
    result3 = compute_m99_grain_novelty("")
    print(f"  Empty: → {result3:.4f}")
    assert result3 == 0.0, f"Expected 0.0, got {result3}"
    
    print("  ✅ m99_grain_novelty PASSED")
    return True


def test_m100_causal_1():
    """Test m100: Kausaler Index"""
    print("\n=== TEST m100_causal_1 ===")
    
    # Test 1: High causal density
    text1 = "weil ich angst habe deshalb bin ich hier denn ich brauche hilfe"  # 3 markers / 13 words
    result1 = compute_m100_causal_1(text1)
    print(f"  High causal: '{text1}' → {result1:.4f}")
    assert result1 >= 0.2, f"Expected >= 0.2, got {result1}"
    
    # Test 2: No causality
    text2 = "der hund ist braun"
    result2 = compute_m100_causal_1(text2)
    print(f"  No causal: '{text2}' → {result2:.4f}")
    assert result2 == 0.0, f"Expected 0.0, got {result2}"
    
    # Test 3: Single marker
    text3 = "ich bin müde weil ich nicht geschlafen habe"  # 1/8 = 0.125 → normalized ~1.25
    result3 = compute_m100_causal_1(text3)
    print(f"  Single marker: '{text3}' → {result3:.4f}")
    assert 0.1 <= result3 <= 0.3, f"Expected 0.1-0.3, got {result3}"
    
    print("  ✅ m100_causal_1 PASSED")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("GRAIN ENGINE VALIDATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_m96_grain_word,
        test_m97_grain_impact,
        test_m98_grain_sentiment,
        test_m99_grain_novelty,
        test_m100_causal_1,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ ERROR: {type(e).__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {failed} tests FAILED")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
