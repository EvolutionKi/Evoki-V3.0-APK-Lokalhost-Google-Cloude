# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — EMOTION METRICS

Plutchik-8 basic emotions, complex emotions, and sentiment meta-metrics.

Categories:
- Plutchik Basic 8 (m77-m84): joy, sadness, anger, fear, trust, disgust, anticipation, surprise
- Complex Emotions (m85-m92): hope, despair, confusion, clarity, etc.
- Sentiment Meta (m93-m95): aggregate sentiment metrics

Based on evoki_fullspectrum168_contract.json
"""

from typing import Dict
import re

# Import professional lexika engine (V2.1 - EVOKI-calibrated)
try:
    from .evoki_lexika_v3 import (
        # Lexika
        S_SELF,
        X_EXIST,
        T_PANIC,
        T_DISSO,
        T_INTEG,
        T_SHOCK_KEYWORDS,
        HAZARD_SUICIDE,
        FLOW_POSITIVE,
        FLOW_NEGATIVE,
        B_EMPATHY,
        ZLF_LOOP,
        # Functions
        compute_lexicon_score,
        compute_hazard_score
    )
    _LEXIKA_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: V2.1 Lexika import failed: {e}")
    _LEXIKA_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
#  LOCAL EMOTION LEXIKA (V2.1 doesn't export EMOTION_POSITIVE/NEGATIVE)
# ═══════════════════════════════════════════════════════════════════════════

# Local emotion lexika for detection
# (V2.1 doesn't export EMOTION_POSITIVE/NEGATIVE, so we define locally)
_emotion_positive_local: Dict[str, float] = {
    "glücklich": 1.0, "freude": 0.9, "froh": 0.8, "erfreut": 0.8,
    "begeistert": 0.9, "dankbar": 0.8, "stolz": 0.7, "optimistisch": 0.7,
    "hoffnungsvoll": 0.8, "zuversichtlich": 0.7, "erleichtert": 0.7,
    "zufrieden": 0.6, "heiter": 0.7, "beschwingt": 0.8, "ausgeglichen": 0.6,
    "erfüllt": 0.7, "lebensfroh": 0.9,
}

_emotion_negative_local: Dict[str, float] = {
    "traurig": 0.9, "verzweifelt": 1.0, "hilflos": 0.9, "einsam": 0.8,
    "hoffnungslos": 0.9, "schmerz": 0.8, "leid": 0.8, "elend": 0.9,
    "ängstlich": 0.8, "bedrückt": 0.8, "niedergeschlagen": 0.8,
    "deprimiert": 0.9, "mutlos": 0.8, "betrübt": 0.7,
}

# Dissociation markers (derealisation, depersonalisation, memory gaps)
_dissociation_local: Dict[str, float] = {
    # Derealisation
    "unwirklich": 0.9, "traum": 0.6, "film": 0.5, "neblig": 0.7,
    "surreal": 0.8, "irreal": 0.9, "traumhaft": 0.6,
    
    # Depersonalisation
    "roboter": 0.8, "automat": 0.7, "fremd": 0.7, "nicht ich selbst": 0.9,
    "fremde person": 0.8, "außen": 0.6, "beobachte mich": 0.8,
    
    # Fog/Barriers
    "nebel": 0.8, "glaswand": 0.9, "watte": 0.7, "schleier": 0.7,
    "hinter glas": 0.8, "durch scheibe": 0.7,
    
    # Memory gaps/blackouts
    "blackout": 1.0, "erinnerungslücke": 0.9, "zeitloch": 0.9,
    "lücke": 0.5, "aussetzer": 0.7, "fehlende zeit": 0.8,
}

# Trauma markers (flashbacks, re-experiencing, body memory)
_trauma_local: Dict[str, float] = {
    # Flashbacks
    "flashback": 1.0, "bilder kommen": 0.9, "vor augen": 0.6,
    "wiederkehren": 0.7, "wieder da": 0.6, "immer wieder": 0.6,
    
    # Re-experiencing/Triggers
    "zurückgeworfen": 0.9, "zurückwerfen": 0.9,
    "als wäre es gestern": 0.9, "als ob es gerade": 0.8,
    "sofort zurück": 0.8, "wieder dort": 0.7,
    
    # Past trauma references
    "damals": 0.5, "kindheit": 0.6, "geschlagen": 0.8,
    "missbrauch": 1.0, "gewalt": 0.7, "vater": 0.4, "mutter": 0.4,
    
    # Body memory
    "körper erinnert": 0.9, "körpergedächtnis": 0.9,
    "spüre es noch": 0.7, "körper weiß": 0.8,
    "im körper gespeichert": 0.8,
}


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# PLUTCHIK-8 BASIC EMOTIONS (m77-m84)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m77_joy(text: str) -> float:
    """
    m77_joy (m77_sent_4) - Joy Emotion
    
    Detects joy, happiness, delight using professional lexika.
    Range: [0.0, 1.0]
    """
    if _LEXIKA_AVAILABLE:
        score, matches = compute_lexicon_score(text, _emotion_positive_local)
        # Also check FLOW_POSITIVE for conversational joy
        flow_score, _ = compute_lexicon_score(text, FLOW_POSITIVE)
        combined = max(score, flow_score * 0.6)
        return clamp(combined)
    else:
        # Fallback
        joy_words = ['happy', 'joy', 'glücklich', 'freude']
        text_lower = text.lower()
        count = sum(1 for word in joy_words if word in text_lower)
        joy = min(1.0, count / 3.0)
        return clamp(joy)


def compute_m78_sadness(text: str) -> float:
    """
    m78_sadness (m78_sent_5) - Sadness Emotion
    
    Detects sadness, sorrow, grief using professional lexika.
    Includes suicidal ideation and existential crisis detection.
    Range: [0.0, 1.0]
    """
    if _LEXIKA_AVAILABLE:
        # Compute base sadness from emotion lexikon
        emo_score, _ = compute_lexicon_score(text, _emotion_negative_local)
        
        # Existential crisis markers
        exist_score, _ = compute_lexicon_score(text, X_EXIST)
        
        # Trauma re-experiencing
        trauma_score, _ = compute_lexicon_score(text, _trauma_local)
        
        # Suicide/self-harm hazard
        hazard_score, _, _ = compute_hazard_score(text)
        
        # Weighted combination (trauma as separate pathway)
        sadness = max(
            emo_score,
            exist_score * 0.7,    # Existential weighted
            trauma_score * 0.85,  # Trauma strong signal
            hazard_score * 0.95   # Hazard highest weight
        )
        return clamp(sadness)
    else:
        # Fallback
        sadness_words = ['sad', 'traurig', 'verzweifelt', 'depressed']
        text_lower = text.lower()
        count = sum(1 for word in sadness_words if word in text_lower)
        sadness = min(1.0, count / 3.0)
        return clamp(sadness)


def compute_m79_anger(text: str) -> float:
    """
    m79_anger (m79_sent_6) - Anger Emotion
    
    Detects anger, rage, frustration.
    Range: [0.0, 1.0]
    """
    anger_words = ['angry', 'rage', 'furious', 'mad', 'frustrated', 'annoyed',
                    'irritated', 'hate', 'outraged', '😠', '😡', '🤬']
    
    text_lower = text.lower()
    count = sum(1 for word in anger_words if word in text_lower)
    
    # Also check for all caps (shouting)
    if text.isupper() and len(text) > 10:
        count += 2
    
    # Check for exclamation marks
    count += min(3, text.count('!'))
    
    anger = min(1.0, count / 4.0)
    
    return clamp(anger)


def compute_m80_fear(text: str) -> float:
    """
    m80_fear (m80_sent_7) - Fear Emotion
    
    Detects fear, anxiety, terror, panic using professional lexika.
    Range: [0.0, 1.0]
    """
    if _LEXIKA_AVAILABLE:
        # Compute base fear from panic lexikon
        panic_score, _ = compute_lexicon_score(text, T_PANIC)
        
        # Dissociation signals (often fear-adjacent)
        dissoc_score, _ = compute_lexicon_score(text, _dissociation_local)
        
        # Combine (dissociation is less intense than panic, but still fear-related)
        fear = max(
            panic_score,
            dissoc_score * 0.8  # Dissociation weighted lower
        )
        return clamp(fear)
    else:
        # Fallback
        fear_words = ['fear', 'afraid', 'angst', 'panik']
        text_lower = text.lower()
        count = sum(1 for word in fear_words if word in text_lower)
        fear = min(1.0, count / 3.0)
        return clamp(fear)


def compute_m81_trust(text: str) -> float:
    """
    m81_trust (m81_sent_8) - Trust Emotion
    
    Detects trust, confidence, faith.
    Range: [0.0, 1.0]
    """
    # English + German trust terms
    trust_words = [
        # English
        'trust', 'confidence', 'faith', 'believe', 'reliable', 'safe',
        'secure', 'certain', 'sure', 'depend', '🤝',
        # German
        'vertrauen', 'glaube', 'glauben', 'sicher', 'zuverlässig',
        'verlässlich', 'gewiss', 'überzeugt', 'verlassen auf'
    ]
    
    text_lower = text.lower()
    count = sum(1 for word in trust_words if word in text_lower)
    
    trust = min(1.0, count / 3.0)
    
    return clamp(trust)


def compute_m82_disgust(text: str) -> float:
    """
    m82_disgust (m82_sent_9) - Disgust Emotion
    
    Detects disgust, revulsion, aversion.
    Range: [0.0, 0.7]
    
    Note: Range is [0.0, 0.7] not [0.0, 1.0] per contract
    """
    # English + German disgust terms
    disgust_words = [
        # English
        'disgust', 'gross', 'revolting', 'sick', 'nasty', 'repulsive',
        'vile', 'awful', 'terrible', '🤢', '🤮',
        # German
        'ekel', 'ekelhaft', 'widerlich', 'abstoßend', 'abscheulich',
        'eklig', 'angewidert', 'grauenhaft'
    ]
    
    text_lower = text.lower()
    count = sum(1 for word in disgust_words if word in text_lower)
    
    disgust = min(0.7, count / 3.0)
    
    return clamp(disgust, 0.0, 0.7)


def compute_m83_anticipation(text: str) -> float:
    """
    m83_anticipation (m83_sent_10) - Anticipation Emotion
    
    Detects anticipation, expectation, hope.
    Range: [0.0, 1.0]
    """
    # Positive anticipation emotions (NOT intent markers like 'will')
    anticipation_words = [
        # English
        'anticipate', 'expect', 'hope', 'await', 'looking forward',
        "can't wait", 'excited for', 'upcoming',
        # German  
        'erwarte', 'erwarten', 'hoffe', 'hoffen', 'freue mich auf',
        'gespannt', 'vorfreude'
    ]
    
    text_lower = text.lower()
    count = sum(1 for word in anticipation_words if word in text_lower)
    
    # NOTE: Removed future-tense check (was double-counting 'will' as intent)
    # Intent markers should be separate metric, not conflated with positive anticipation
    
    anticipation = min(1.0, count / 3.0)
    
    return clamp(anticipation)


def compute_m84_surprise(text: str) -> float:
    """
    m84_surprise (m84_sent_11) - Surprise Emotion
    
    Detects surprise, shock, amazement.
    Range: [0.0, 1.0]
    
    Note: Different from m56_surprise (FEP/Bayesian surprise)
    """
    # English + German surprise terms
    surprise_words = [
        # English
        'surprise', 'shocked', 'amazed', 'astonished', 'wow',
        'unexpected', 'sudden', 'startled', '😮', '😲', '🤯',
        # German
        'überrascht', 'überraschung', 'schockiert', 'erstaunt',
        'wow', 'krass', 'unerwartet', 'plötzlich'
    ]
    
    text_lower = text.lower()
    count = sum(1 for word in surprise_words if word in text_lower)
    
    # Check for question marks + exclamation marks
    has_surprise_punctuation = '?!' in text or '!?' in text
    if has_surprise_punctuation:
        count += 2
    
    surprise = min(1.0, count / 3.0)
    
    return clamp(surprise)


# ═══════════════════════════════════════════════════════════════════════════
# COMPLEX EMOTIONS (m85-m92)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m85_hope(m83_anticipation: float, m77_joy: float) -> float:
    """
    m85_hope (m85_sent_12) - Hope
    
    Complex emotion: anticipation + joy.
    Range: [0.0, 1.0]
    """
    hope = (m83_anticipation + m77_joy) / 2.0
    
    return clamp(hope)


def compute_m86_despair(m78_sadness: float, m80_fear: float) -> float:
    """
    m86_despair (m86_sent_13) - Despair
    
    Complex emotion: sadness + fear.
    Range: [0.0, 1.0]
    """
    despair = (m78_sadness + m80_fear) / 2.0
    
    return clamp(despair)


def compute_m87_confusion(text: str) -> float:
    """
    m87_confusion (m87_sent_14) - Confusion
    
    Detects confusion, uncertainty.
    Range: [0.0, 1.0]
    """
    confusion_words = ['confused', 'puzzled', 'unclear', 'uncertain', 'don\'t understand',
                       'what', 'why', 'how', '???', '🤔']
    
    text_lower = text.lower()
    count = sum(1 for word in confusion_words if word in text_lower)
    
    # Multiple question marks indicate confusion
    if '??' in text:
        count += 1
    
    confusion = min(1.0, count / 4.0)
    
    return clamp(confusion)


def compute_m88_clarity(text: str, m5_coh: float) -> float:
    """
    m88_clarity (m88_sent_15) - Clarity
    
    Detects clarity, understanding.
    Range: [0.0, 1.0]
    """
    clarity_words = ['clear', 'understand', 'obvious', 'evident', 'certain',
                     'sure', 'definitely', 'exactly', 'precisely']
    
    text_lower = text.lower()
    count = sum(1 for word in clarity_words if word in text_lower)
    
    # Combine with coherence
    clarity = (min(1.0, count / 3.0) + m5_coh) / 2.0
    
    return clamp(clarity)


def compute_m89_acceptance(m81_trust: float) -> float:
    """
    m89_acceptance (m89_sent_16) - Acceptance
    
    Related to trust and peace.
    Range: [0.0, 1.0]
    """
    # Acceptance correlates with trust
    acceptance = m81_trust * 0.9
    
    return clamp(acceptance)


def compute_m90_resistance(m79_anger: float, m82_disgust: float) -> float:
    """
    m90_resistance (m90_sent_17) - Resistance
    
    Complex emotion: anger + disgust.
    Range: [0.0, 1.0]
    """
    resistance = (m79_anger + m82_disgust) / 2.0
    
    return clamp(resistance)


def compute_m91_coherence(m5_coh: float, m88_clarity: float) -> float:
    """
    m91_coherence (m91_sent_18) - Emotional Coherence
    
    Meta-metric: cognitive + emotional coherence.
    Range: [0.0, 1.0]
    """
    coherence = (m5_coh + m88_clarity) / 2.0
    
    return clamp(coherence)


def compute_m92_stability(m81_trust: float, m91_coherence: float) -> float:
    """
    m92_stability (m92_sent_19) - Emotional Stability
    
    Meta-metric: trust + coherence.
    Range: [0.0, 1.0]
    """
    stability = (m81_trust + m91_coherence) / 2.0
    
    return clamp(stability)


# ═══════════════════════════════════════════════════════════════════════════
# SENTIMENT META (m93-m95)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m93_sent_20(
    m77_joy: float,
    m78_sadness: float,
    m79_anger: float,
    m80_fear: float
) -> float:
    """
    m93_sent_20 - Aggregate Sentiment Score
    
    Weighted combination of basic emotions.
    Range: [0.0, ~0.87]
    
    Note: Range is [0.0, ~0.87] not [0.0, 1.0] per contract
    """
    # Positive emotions boost, negative emotions reduce
    aggregate = (
        m77_joy * 0.4 +
        (1.0 - m78_sadness) * 0.2 +
        (1.0 - m79_anger) * 0.2 +
        (1.0 - m80_fear) * 0.2
    )
    
    return clamp(aggregate, 0.0, 0.87)


def compute_m94_sent_21(m72_ev_valence: float, m71_ev_arousal: float) -> float:
    """
    m94_sent_21 - Valence-Arousal Composite
    
    2D emotion space metric.
    Range: [0.0, 1.0]
    """
    composite = (m72_ev_valence + m71_ev_arousal) / 2.0
    
    return clamp(composite)


def compute_m95_sent_22(
    m93_sent_20: float,
    m92_stability: float
) -> float:
    """
    m95_sent_22 - Overall Emotional State
    
    Final sentiment meta-metric.
    Range: [0.0, 1.0]
    """
    overall = (m93_sent_20 * 0.7 + m92_stability * 0.3)
    
    return clamp(overall)


# ═══════════════════════════════════════════════════════════════════════════
# EXPORT ALL
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Plutchik-8
    "compute_m77_joy",
    "compute_m78_sadness",
    "compute_m79_anger",
    "compute_m80_fear",
    "compute_m81_trust",
    "compute_m82_disgust",
    "compute_m83_anticipation",
    "compute_m84_surprise",
    # Complex
    "compute_m85_hope",
    "compute_m86_despair",
    "compute_m87_confusion",
    "compute_m88_clarity",
    "compute_m89_acceptance",
    "compute_m90_resistance",
    "compute_m91_coherence",
    "compute_m92_stability",
    # Meta
    "compute_m93_sent_20",
    "compute_m94_sent_21",
    "compute_m95_sent_22",
]


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    test_text = "I'm so happy and excited! 🎉 But also a bit worried about what will happen. Will it work?"
    
    print("=" * 70)
    print("EMOTION METRICS TEST")
    print("=" * 70)
    
    # Plutchik-8
    m77 = compute_m77_joy(test_text)
    m78 = compute_m78_sadness(test_text)
    m79 = compute_m79_anger(test_text)
    m80 = compute_m80_fear(test_text)
    m81 = compute_m81_trust(test_text)
    m82 = compute_m82_disgust(test_text)
    m83 = compute_m83_anticipation(test_text)
    m84 = compute_m84_surprise(test_text)
    
    print(f"\n😊 Plutchik-8 Basic Emotions:")
    print(f"  m77_joy:          {m77:.3f}")
    print(f"  m78_sadness:      {m78:.3f}")
    print(f"  m79_anger:        {m79:.3f}")
    print(f"  m80_fear:         {m80:.3f}")
    print(f"  m81_trust:        {m81:.3f}")
    print(f"  m82_disgust:      {m82:.3f}")
    print(f"  m83_anticipation: {m83:.3f}")
    print(f"  m84_surprise:     {m84:.3f}")
    
    # Complex
    m5_coh = 0.72  # Mock
    m71_ev_arousal = 0.75  # Mock
    m72_ev_valence = 0.73  # Mock
    
    m85 = compute_m85_hope(m83, m77)
    m86 = compute_m86_despair(m78, m80)
    m87 = compute_m87_confusion(test_text)
    m88 = compute_m88_clarity(test_text, m5_coh)
    m89 = compute_m89_acceptance(m81)
    m90 = compute_m90_resistance(m79, m82)
    m91 = compute_m91_coherence(m5_coh, m88)
    m92 = compute_m92_stability(m81, m91)
    
    print(f"\n🌈 Complex Emotions:")
    print(f"  m85_hope:         {m85:.3f}")
    print(f"  m86_despair:      {m86:.3f}")
    print(f"  m87_confusion:    {m87:.3f}")
    print(f"  m88_clarity:      {m88:.3f}")
    print(f"  m89_acceptance:   {m89:.3f}")
    print(f"  m90_resistance:   {m90:.3f}")
    print(f"  m91_coherence:    {m91:.3f}")
    print(f"  m92_stability:    {m92:.3f}")
    
    # Meta
    m93 = compute_m93_sent_20(m77, m78, m79, m80)
    m94 = compute_m94_sent_21(m72_ev_valence, m71_ev_arousal)
    m95 = compute_m95_sent_22(m93, m92)
    
    print(f"\n📊 Sentiment Meta:")
    print(f"  m93_sent_20:      {m93:.3f}")
    print(f"  m94_sent_21:      {m94:.3f}")
    print(f"  m95_sent_22:      {m95:.3f}")
    
    print(f"\n✅ 19 new Emotion metrics implemented!")
