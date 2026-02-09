# -*- coding: utf-8 -*-
"""
EVOKI Lexika V3 — Engine
Multi-match + Longest-first + Overlap-guard + minimal context-gates.
"""
from __future__ import annotations
import math, re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set, Pattern, Optional

from .lexika_data import (
    B_PAST, B_PAST_PATTERNS,
    SUICIDE_MARKERS, SELF_HARM, CRISIS_MARKERS,
)

@dataclass(frozen=True)
class LexMatch:
    term: str
    weight: float
    span: Tuple[int, int]
    category: Optional[str] = None

def _is_wordish(s: str) -> bool:
    return bool(re.fullmatch(r"[0-9A-Za-zÄÖÜäöüß]+", s))

def _compile_term_pattern(term: str) -> Pattern[str]:
    t = term.strip()
    if " " not in t and _is_wordish(t):
        return re.compile(rf"(?<!\w){re.escape(t)}(?!\w)", re.IGNORECASE)
    parts = [re.escape(p) for p in re.split(r"\s+", t)]
    core = r"\s+".join(parts)
    return re.compile(rf"(?<!\w){core}(?!\w)", re.IGNORECASE)

_PATTERN_CACHE: Dict[str, Pattern[str]] = {}

def _get_pat(term: str) -> Pattern[str]:
    pat = _PATTERN_CACHE.get(term)
    if pat is None:
        pat = _compile_term_pattern(term)
        _PATTERN_CACHE[term] = pat
    return pat

_CONTEXT_GATES = {
    ("T_panic", "halt"): ({"hilfe", "bitte", "kann nicht", "nicht mehr", "aus"}, {"boden", "geerdet", "atmen", "ruhig"}, 0.35),
    ("T_integ", "halt"): ({"boden", "geerdet", "atmen", "ruhig", "sicher"}, {"hilfe", "panik", "kann nicht", "aus"}, 0.35),
}

def _effective_weight(category: str, term: str, base: float, text_lower: str) -> float:
    gate = _CONTEXT_GATES.get((category, term))
    if not gate:
        return base
    boost, damp, base_w = gate
    w = base_w
    if any(tok in text_lower for tok in boost):
        w = max(w, min(1.0, base * 1.25))
    if any(tok in text_lower for tok in damp):
        w = min(w, base * 0.5)
    return float(max(0.0, min(1.0, w)))

def compute_lexicon_score(
    text: str,
    lexicon: Dict[str, float],
    *,
    category: Optional[str] = None,
    use_longest_match: bool = True,
) -> Tuple[float, List[str], List[LexMatch]]:
    if not text or not lexicon:
        return 0.0, [], []

    text_lower = text.lower()
    words = re.findall(r"\w+", text_lower, flags=re.UNICODE)
    word_count = len(words) if words else max(1, len(text_lower.split()))

    terms = list(lexicon.keys())
    if use_longest_match:
        terms.sort(key=len, reverse=True)

    used: Set[int] = set()
    detailed: List[LexMatch] = []
    matched_unique: List[str] = []
    matched_set: Set[str] = set()
    total_weight = 0.0

    for term in terms:
        base_w = float(lexicon[term])
        pat = _get_pat(term)
        for m in pat.finditer(text_lower):
            a, b = m.span()
            span_set = set(range(a, b))
            if span_set & used:
                continue
            used |= span_set
            eff = base_w
            if category is not None:
                eff = _effective_weight(category, term, base_w, text_lower)
            detailed.append(LexMatch(term=term, weight=eff, span=(a, b), category=category))
            total_weight += eff
            if term not in matched_set:
                matched_set.add(term)
                matched_unique.append(term)

    if total_weight <= 0.0:
        return 0.0, [], []

    score = total_weight / (1.0 + math.log(word_count + 1.0))
    return float(min(1.0, max(0.0, score))), matched_unique, detailed

def compute_b_past_with_regex(text: str) -> Tuple[float, List[str]]:
    base_score, matches, _ = compute_lexicon_score(text, B_PAST, category="B_past")
    out_matches = list(matches)
    best = base_score
    for pattern, weight in B_PAST_PATTERNS:
        if pattern.search(text):
            best = max(best, float(weight))
            out_matches.append(f"[REGEX:{pattern.pattern}]")
    return float(min(1.0, best)), out_matches

def compute_hazard_score(text: str) -> Tuple[float, bool, List[str]]:
    all_matches: List[str] = []
    max_score = 0.0
    is_critical = False

    s, m, _ = compute_lexicon_score(text, SUICIDE_MARKERS, category="Suicide")
    if s > 0:
        max_score = max(max_score, s)
        all_matches.extend([f"SUICIDE:{x}" for x in m])
        if s >= 0.9:
            is_critical = True

    s, m, _ = compute_lexicon_score(text, SELF_HARM, category="Self_harm")
    if s > 0:
        max_score = max(max_score, s * 0.9)
        all_matches.extend([f"HARM:{x}" for x in m])

    s, m, _ = compute_lexicon_score(text, CRISIS_MARKERS, category="Crisis")
    if s > 0:
        max_score = max(max_score, s * 0.8)
        all_matches.extend([f"CRISIS:{x}" for x in m])

    tl = text.lower()
    if any(t in tl for t in ("suizid", "selbstmord", "mich umbringen", "sterben wollen")):
        is_critical = True
        max_score = max(max_score, 0.95)

    return float(min(1.0, max_score)), bool(is_critical), all_matches
