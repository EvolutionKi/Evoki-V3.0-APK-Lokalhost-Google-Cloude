# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — TEXT ANALYTICS & GRANULARITY METRICS

Advanced text analysis metrics including readability, granularity, and meta-cognition.

Categories:
- Text Granularity (m96-m99): word-level, impact, sentiment, novelty
- Text Analytics / Meta-Cognition (m116-m121): LIX, question density, capital stress, etc.

Based on evoki_fullspectrum168_contract.json
"""

from typing import Dict
import re


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# TEXT GRANULARITY (m96-m99)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m96_grain_word(text: str) -> float:
    """
    m96_grain_word - Word-Level Granularity
    
    Measures uniqueness/diversity of vocabulary.
    Range: [0.0, 1.0]
    
    Higher = more diverse vocabulary
    """
    words = text.lower().split()
    
    if len(words) == 0:
        return 0.0
    
    # Type-Token Ratio (TTR)
    unique_words = len(set(words))
    total_words = len(words)
    
    ttr = unique_words / total_words if total_words > 0 else 0.0
    
    return clamp(ttr)


def compute_m97_grain_impact(text: str) -> float:
    """
    m97_grain_impact - Impact Granularity
    
    Measures density of impactful/strong words.
    Range: [0.0, 1.0]
    """
    # Strong impact words
    impact_words = ['critical', 'essential', 'crucial', 'vital', 'important',
                    'significant', 'major', 'key', 'fundamental', 'paramount',
                    'urgent', 'imperative', '!!!', 'MUST', 'CRITICAL']
    
    text_with_caps = text  # Keep case for CAPS detection
    text_lower = text.lower()
    
    # Count impact words
    count = sum(1 for word in impact_words if word.lower() in text_lower)
    
    # Count ALL CAPS words (excluding short ones)
    caps_words = [w for w in text_with_caps.split() if w.isupper() and len(w) > 3]
    count += len(caps_words)
    
    words = text.split()
    if len(words) == 0:
        return 0.0
    
    # Normalize
    impact = min(1.0, count / max(1, len(words) / 10))
    
    return clamp(impact)


def compute_m98_grain_sentiment(
    m93_sent_20: float,
    m72_ev_valence: float
) -> float:
    """
    m98_grain_sentiment - Sentiment Granularity
    
    Composite sentiment granularity metric.
    Range: [0.0, 1.0]
    """
    # Combine aggregate sentiment with valence
    grain_sent = (m93_sent_20 + m72_ev_valence) / 2.0
    
    return clamp(grain_sent)


def compute_m99_grain_novelty(text: str, context: Dict) -> float:
    """
    m99_grain_novelty - Novelty Granularity
    
    Measures how novel/new the text content is.
    Range: [0.0, 1.0]
    """
    # Compare with previous text
    prev_text = context.get("prev_text", "")
    
    if not prev_text:
        return 0.5  # Neutral novelty
    
    current_words = set(text.lower().split())
    prev_words = set(prev_text.lower().split())
    
    if not prev_words:
        return 0.5
    
    # Calculate novelty as proportion of new words
    new_words = current_words - prev_words
    novelty = len(new_words) / len(current_words) if current_words else 0.0
    
    return clamp(novelty)


# ═══════════════════════════════════════════════════════════════════════════
# TEXT ANALYTICS / META-COGNITION (m116-m121)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m116_lix(text: str) -> float:
    """
    m116_lix - LIX Readability Index
    
    Swedish readability measure: (words/sentences) + (long_words*100/words)
    Range: [0.0, 100+] / normalized to [0.0, 1.0]
    
    Lower LIX = easier to read
    """
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Split into words
    words = text.split()
    
    if len(sentences) == 0 or len(words) == 0:
        return 0.0
    
    # Count long words (>6 characters)
    long_words = sum(1 for w in words if len(w) > 6)
    
    # LIX formula
    avg_words_per_sentence = len(words) / len(sentences)
    long_word_percentage = (long_words * 100) / len(words) if len(words) > 0 else 0
    
    lix_raw = avg_words_per_sentence + long_word_percentage
    
    # Normalize to [0.0, 1.0] (typical LIX range: 20-60)
    lix_normalized = min(1.0, lix_raw / 60.0)
    
    return clamp(lix_normalized)


def compute_m117_question_density(text: str) -> float:
    """
    m117_question_density - Question Density
    
    Proportion of questions in text.
    Range: [0.0, 1.0]
    """
    # Count question marks
    question_count = text.count('?')
    
    # Count sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) == 0:
        return 0.0
    
    density = question_count / len(sentences)
    
    return clamp(density)


def compute_m118_capital_stress(text: str) -> float:
    """
    m118_capital_stress - Capital Letter Stress
    
    Measures excessive capitalization (SHOUTING).
    Range: [0.0, 1.0]
    """
    if len(text) == 0:
        return 0.0
    
    # Count uppercase letters (excluding spaces and punctuation)
    letters = [c for c in text if c.isalpha()]
    
    if len(letters) == 0:
        return 0.0
    
    uppercase = sum(1 for c in letters if c.isupper())
    
    # Calculate ratio
    stress = uppercase / len(letters)
    
    # Penalize excessive caps (>50% is stressful)
    if stress > 0.5:
        stress = min(1.0, stress * 1.5)
    
    return clamp(stress)


def compute_m119_turn_len_ai(text: str) -> float:
    """
    m119_turn_len_ai - Turn Length (AI)
    
    Measures length of AI response.
    Range: [0, ∞] / normalized to [0.0, 1.0]
    """
    # Word count
    words = text.split()
    word_count = len(words)
    
    # Normalize (typical response: 50-200 words)
    normalized = min(1.0, word_count / 200.0)
    
    return clamp(normalized)


def compute_m120_emoji_sentiment(text: str) -> float:
    """
    m120_emoji_sentiment - Emoji Sentiment
    
    Sentiment derived from emojis.
    Range: [-1.0, 1.0] / normalized to [0.0, 1.0]
    """
    # Positive emojis
    positive = ['😊', '😀', '😃', '😄', '🎉', '❤️', '💕', '👍', '✨', '🌟', '⭐']
    # Negative emojis
    negative = ['😢', '😭', '😠', '😡', '💔', '👎', '😞', '😔', '😟']
    
    pos_count = sum(text.count(emoji) for emoji in positive)
    neg_count = sum(text.count(emoji) for emoji in negative)
    
    if pos_count + neg_count == 0:
        return 0.5  # Neutral
    
    # Calculate sentiment [-1, 1]
    sentiment = (pos_count - neg_count) / (pos_count + neg_count)
    
    # Normalize to [0, 1]
    normalized = (sentiment + 1.0) / 2.0
    
    return clamp(normalized)


def compute_m121_turn_len_user(text: str) -> float:
    """
    m121_turn_len_user - Turn Length (User)
    
    Measures length of user input.
    Range: [0, ∞] / normalized to [0.0, 1.0]
    """
    # Word count
    words = text.split()
    word_count = len(words)
    
    # Normalize (typical user input: 10-50 words)
    normalized = min(1.0, word_count / 50.0)
    
    return clamp(normalized)


# ═══════════════════════════════════════════════════════════════════════════
# EXPORT ALL
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Granularity
    "compute_m96_grain_word",
    "compute_m97_grain_impact",
    "compute_m98_grain_sentiment",
    "compute_m99_grain_novelty",
    # Text Analytics
    "compute_m116_lix",
    "compute_m117_question_density",
    "compute_m118_capital_stress",
    "compute_m119_turn_len_ai",
    "compute_m120_emoji_sentiment",
    "compute_m121_turn_len_user",
]


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    test_text = "This is IMPORTANT! What do you think? 🎉 I'm excited to see what happens. However, we must be CRITICAL about this decision."
    test_context = {
        "prev_text": "This is a simple test.",
    }
    
    print("=" * 70)
    print("TEXT ANALYTICS & GRANULARITY TEST")
    print("=" * 70)
    
    # Granularity
    m96 = compute_m96_grain_word(test_text)
    m97 = compute_m97_grain_impact(test_text)
    
    # Mock for m98
    m93_sent_20 = 0.75
    m72_ev_valence = 0.73
    m98 = compute_m98_grain_sentiment(m93_sent_20, m72_ev_valence)
    
    m99 = compute_m99_grain_novelty(test_text, test_context)
    
    print(f"\n📏 Granularity Metrics:")
    print(f"  m96_grain_word:      {m96:.3f}")
    print(f"  m97_grain_impact:    {m97:.3f}")
    print(f"  m98_grain_sentiment: {m98:.3f}")
    print(f"  m99_grain_novelty:   {m99:.3f}")
    
    # Text Analytics
    m116 = compute_m116_lix(test_text)
    m117 = compute_m117_question_density(test_text)
    m118 = compute_m118_capital_stress(test_text)
    m119 = compute_m119_turn_len_ai(test_text)
    m120 = compute_m120_emoji_sentiment(test_text)
    m121 = compute_m121_turn_len_user("Hi, how are you?")
    
    print(f"\n📊 Text Analytics:")
    print(f"  m116_lix:             {m116:.3f}")
    print(f"  m117_question_density: {m117:.3f}")
    print(f"  m118_capital_stress:   {m118:.3f}")
    print(f"  m119_turn_len_ai:      {m119:.3f}")
    print(f"  m120_emoji_sentiment:  {m120:.3f}")
    print(f"  m121_turn_len_user:    {m121:.3f}")
    
    print(f"\n✅ 10 new Text Analytics & Granularity metrics implemented!")
