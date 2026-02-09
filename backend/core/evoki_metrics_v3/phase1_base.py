# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — PHASE 1: BASE METRICS (Independent)

Diese Module berechnet ALLE unabhängigen Metriken:
- Token Counts
- Text Complexity (PCI, Coherence, Entropy)
- Lexika Scanning (400+ Terms!)
- Keyword Extraction (RAKE Algorithm)

Dependencies: NONE (kann parallel berechnet werden!)

Version: V1.0
"""

import re
import math
from typing import Dict, List, Tuple
from collections import Counter

# ═══════════════════════════════════════════════════════════════════════════
# IMPORTS: Lexika Engine
# ═══════════════════════════════════════════════════════════════════════════

try:
    from .evoki_lexika_v3 import (
        compute_hazard_score,
        compute_b_past_with_regex,
        BVektorConfig,
        Thresholds
    )
    HAS_LEXIKA = True
except ImportError:
    try:
        from evoki_lexika_v3 import (
            compute_hazard_score,
            compute_b_past_with_regex,
            BVektorConfig,
            Thresholds
        )
        HAS_LEXIKA = True
    except ImportError:
        HAS_LEXIKA = False
        print("⚠️ evoki_lexika_v3 not available, using fallback")


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def tokenize(text: str) -> List[str]:
    """Tokenisiert Text in Wörter"""
    return re.findall(r'\b\w+\b', text.lower())


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Klemmt Wert auf [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: TOKEN COUNTS
# ═══════════════════════════════════════════════════════════════════════════

def count_tokens_social(text: str) -> float:
    """
    m57_tokens_soc - Soziale Token-Dichte
    
    Soziale Tokens: ich, du, wir, man, persönlich, etc.
    """
    social_tokens = {
        "ich", "mir", "mich", "mein", "meine",
        "du", "dir", "dich", "dein", "deine",
        "wir", "uns", "unser", "unsere",
        "man", "jemand", "niemand",
        "persönlich", "gefühl", "fühle", "denke"
    }
    
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    
    social_count = sum(1 for t in tokens if t in social_tokens)
    return clamp(social_count / len(tokens))


def count_tokens_logical(text: str) -> float:
    """
    m58_tokens_log - Logische Token-Dichte
    
    Logische Tokens: weil, deshalb, folglich, wenn, dann, etc.
    """
    logical_tokens = {
        "weil", "deshalb", "daher", "folglich", "also",
        "wenn", "dann", "falls", "sonst", "oder",
        "und", "aber", "jedoch", "dennoch",
        "erstens", "zweitens", "drittens",
        "beispiel", "zum beispiel", "etwa"
    }
    
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    
    logical_count = sum(1 for t in tokens if t in logical_tokens)
    return clamp(logical_count / len(tokens))


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: TEXT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def compute_complexity_index(text: str) -> float:
    """
    m2_PCI - Prompt Complexity Index
    
    Formel: 
    PCI = 0.4 * (unique_words/total_words) + 
          0.3 * (avg_word_length/10) + 
          0.3 * (sentence_count/10)
    """
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    
    unique_ratio = len(set(tokens)) / len(tokens)
    avg_word_len = sum(len(t) for t in tokens) / len(tokens)
    sentence_count = len(re.findall(r'[.!?]+', text))
    
    pci = (
        0.4 * unique_ratio +
        0.3 * clamp(avg_word_len / 10.0) +
        0.3 * clamp(sentence_count / 10.0)
    )
    
    return clamp(pci)


def compute_coherence(text: str) -> float:
    """
    m5_coh - Kohärenz Score
    
    Misst Wiederholung von Wörtern (hohe Kohärenz = mehr Wiederholung)
    """
    tokens = tokenize(text)
    if len(tokens) < 2:
        return 0.5
    
    # Bigram-Overlap berechnen
    bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens)-1)]
    unique_bigrams = len(set(bigrams))
    total_bigrams = len(bigrams)
    
    if total_bigrams == 0:
        return 0.5
    
    # Höhere Wiederholung = höhere Kohärenz
    repetition = 1.0 - (unique_bigrams / total_bigrams)
    return clamp(0.5 + repetition * 0.5)


def compute_semantic_entropy(text: str) -> float:
    """
    m18_s_entropy - Semantische Entropie
    
    Misst Informationsdichte (Shannon Entropy der Wörter)
    """
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    
    word_freq = Counter(tokens)
    total = len(tokens)
    
    entropy = 0.0
    for count in word_freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    
    # Normalisieren auf [0, 1]
    max_entropy = math.log2(len(word_freq)) if len(word_freq) > 1 else 1.0
    return clamp(entropy / max_entropy if max_entropy > 0 else 0.0)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: LEXIKON SCANNING (400+ Terms!)
# ═══════════════════════════════════════════════════════════════════════════

# Inline Lexika (Fallback wenn evoki_lexika_v3 nicht verfügbar)

S_SELF_LEXIKON = {
    "ich": 1.0, "mir": 1.0, "mich": 1.0, "mein": 0.8, "meine": 0.8,
    "selbst": 1.2, "persönlich": 0.9, "eigene": 0.7
}

X_EXIST_LEXIKON = {
    "existenz": 1.5, "sein": 0.8, "dasein": 1.2, "leben": 0.9,
    "wirklich": 0.7, "real": 0.8, "hier": 0.5
}

B_PAST_LEXIKON = {
    "damals": 1.0, "früher": 1.0, "vergangen": 1.2, "erinnere": 0.9,
    "war": 0.6, "hatte": 0.7, "gewesen": 0.8, "geschichte": 0.9
}

T_PANIC_LEXIKON = {
    "panik": 3.0, "angst": 1.5, "hilfe": 2.0, "todesangst": 3.0,
    "atemnot": 2.0, "herzrasen": 1.5, "zittern": 1.0, "sterben": 2.5
}

T_DISSO_LEXIKON = {
    "egal": 1.5, "fühle nichts": 2.5, "unwirklich": 2.0, "taub": 1.5,
    "neben mir": 1.8, "wie im traum": 2.0, "distanziert": 1.3
}

T_INTEG_LEXIKON = {
    "verstehe": 1.5, "klar": 1.0, "zusammenhang": 1.5, "gelernt": 1.2,
    "verarbeitet": 2.0, "integriert": 2.0, "verbunden": 1.5
}


def scan_lexikon(text: str, lexikon: Dict[str, float]) -> float:
    """
    Scannt Text nach Lexikon-Treffern
    
    Returns: Weighted sum / word_count
    """
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    
    # Phrase-Matching (2-3 Wörter)
    text_lower = text.lower()
    phrase_hits = []
    for phrase, weight in lexikon.items():
        if ' ' in phrase:  # Multi-word phrase
            if phrase in text_lower:
                phrase_hits.append(weight)
    
    # Single-word matching
    word_hits = [lexikon.get(t, 0.0) for t in tokens]
    
    total_hits = sum(phrase_hits) + sum(word_hits)
    return clamp(total_hits / len(tokens))


def compute_m8_s_self(text: str) -> float:
    """m8_s_self - Selbstreferenz Score"""
    return scan_lexikon(text, S_SELF_LEXIKON)


def compute_m9_x_exist(text: str) -> float:
    """m9_x_exist - Existenz Score"""
    return scan_lexikon(text, X_EXIST_LEXIKON)


def compute_m10_b_past(text: str) -> float:
    """m10_b_past - Vergangenheits-Bezug"""
    if HAS_LEXIKA:
        score, matches = compute_b_past_with_regex(text)
        return score
    else:
        return scan_lexikon(text, B_PAST_LEXIKON)



def compute_m101_T_panic(text: str) -> float:
    """m101_T_panic - Panik-Marker"""
    return scan_lexikon(text, T_PANIC_LEXIKON)


def compute_m102_T_disso(text: str) -> float:
    """m102_T_disso - Dissoziation-Marker"""
    return scan_lexikon(text, T_DISSO_LEXIKON)


def compute_m103_T_integ(text: str) -> float:
    """m103_T_integ - Integrations-Marker"""
    return scan_lexikon(text, T_INTEG_LEXIKON)


def compute_m151_hazard(text: str) -> float:
    """m151_hazard - Hazard Score (Suicide/Self-Harm/Crisis)"""
    if HAS_LEXIKA:
        score, is_critical, matches = compute_hazard_score(text)
        return score
    else:
        # Fallback: Simple suicide/harm detection
        hazard_lexikon = {
            "suizid": 0.9, "selbstmord": 0.9, "umbringen": 0.8,
            "sterben will": 0.7, "aufgeben": 0.5, "hoffnungslos": 0.6,
            "ritzen": 0.7, "schneiden": 0.6, "verletzen": 0.6
        }
        return scan_lexikon(text, hazard_lexikon)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: KEYWORD EXTRACTION (RAKE Algorithm)
# ═══════════════════════════════════════════════════════════════════════════

STOPWORDS = {
    "der", "die", "das", "ein", "eine", "und", "oder", "aber",
    "ist", "sind", "war", "waren", "sein", "haben", "hat",
    "ich", "du", "er", "sie", "wir", "ihr", "von", "zu", "in",
    "auf", "mit", "für", "an", "bei", "aus", "nach", "über"
}


def extract_keywords_RAKE(text: str, max_keywords: int = 10) -> List[Tuple[str, float]]:
    """
    RAKE Algorithm - Rapid Automatic Keyword Extraction
    
    Returns: List of (keyword, score) tuples
    """
    # Sentence splitting
    sentences = re.split(r'[.!?;]', text.lower())
    
    # Word frequency
    word_freq = Counter()
    word_degree = Counter()
    
    for sentence in sentences:
        words = tokenize(sentence)
        # Filter stopwords
        words = [w for w in words if w not in STOPWORDS and len(w) > 2]
        
        # Count frequency
        for word in words:
            word_freq[word] += 1
        
        # Count degree (co-occurrence)
        for word in words:
            word_degree[word] += len(words) - 1
    
    # Calculate RAKE score: degree / frequency
    rake_scores = {}
    for word in word_freq:
        if word_freq[word] > 0:
            rake_scores[word] = word_degree[word] / word_freq[word]
    
    # Sort by score
    sorted_keywords = sorted(rake_scores.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_keywords[:max_keywords]


# ═══════════════════════════════════════════════════════════════════════════
# MAIN: CALCULATE PHASE 1
# ═══════════════════════════════════════════════════════════════════════════

def calculate_phase1(text: str) -> Dict:
    """
    PHASE 1: BASE METRICS (Independent)
    
    Returns:
        {
            "metrics": {...},  # All ~40 base metrics
            "keywords": [...],  # RAKE keywords
            "lexika_hits": {...}  # For B-Vector verification
        }
    """
    
    # Token Counts
    m57_tokens_soc = count_tokens_social(text)
    m58_tokens_log = count_tokens_logical(text)
    
    # Text Analysis
    m2_PCI = compute_complexity_index(text)
    m5_coh = compute_coherence(text)
    m18_s_entropy = compute_semantic_entropy(text)
    
    # Lexika Scanning
    m8_s_self = compute_m8_s_self(text)
    m9_x_exist = compute_m9_x_exist(text)
    m10_b_past = compute_m10_b_past(text)
    m101_T_panic = compute_m101_T_panic(text)
    m102_T_disso = compute_m102_T_disso(text)
    m103_T_integ = compute_m103_T_integ(text)
    m151_hazard = compute_m151_hazard(text)
    
    # Keyword Extraction
    keywords = extract_keywords_RAKE(text)
    
    # Lexika Hits (für B-Vector Verification)
    lexika_hits = {
        "s_self": m8_s_self,
        "x_exist": m9_x_exist,
        "b_past": m10_b_past,
        "t_panic": m101_T_panic,
        "t_disso": m102_T_disso,
        "t_integ": m103_T_integ,
        "hazard": m151_hazard
    }
    
    # Metrics Dictionary
    metrics = {
        # Token Counts
        "m57_tokens_soc": m57_tokens_soc,
        "m58_tokens_log": m58_tokens_log,
        
        # Text Analysis
        "m2_PCI": m2_PCI,
        "m5_coh": m5_coh,
        "m18_s_entropy": m18_s_entropy,
        
        # Lexika
        "m8_s_self": m8_s_self,
        "m9_x_exist": m9_x_exist,
        "m10_b_past": m10_b_past,
        "m101_T_panic": m101_T_panic,
        "m102_T_disso": m102_T_disso,
        "m103_T_integ": m103_T_integ,
        "m151_hazard": m151_hazard,
        
        # Placeholders for other base metrics
        # (will be filled in as we implement more)
        "m11_gap_s": 0.0,
        "m56_surprise": 0.0,
        # ... ~30 more to add
    }
    
    return {
        "metrics": metrics,
        "keywords": keywords,
        "lexika_hits": lexika_hits
    }


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    test_text = """
    Ich fühle mich heute sehr hoffnungslos. 
    Die Angst überwältigt mich manchmal. 
    Früher war alles anders, ich erinnere mich an bessere Zeiten.
    Aber jetzt ist alles so unwirklich und egal.
    """
    
    result = calculate_phase1(test_text)
    
    print("=" * 70)
    print("PHASE 1: BASE METRICS TEST")
    print("=" * 70)
    print("\n📊 METRICS:")
    for key, val in result["metrics"].items():
        if val > 0:
            print(f"  {key}: {val:.3f}")
    
    print("\n🔑 KEYWORDS (RAKE):")
    for kw, score in result["keywords"]:
        print(f"  {kw}: {score:.2f}")
    
    print("\n📚 LEXIKA HITS:")
    for key, val in result["lexika_hits"].items():
        if val > 0:
            print(f"  {key}: {val:.3f}")
    
    print("\n✅ Phase 1 complete!")
