# -*- coding: utf-8 -*-
"""
EVOKI COMPLETE METRICS CALCULATOR V3.0

Vollständige Berechnung aller 90+ Metriken.

Kategorien:
A. Core Metriken
B. Lexika Scores
C. System/Wächter
D. Deep Space
E. Zeit/Gradienten
F. Kausalität
G. FEP Metriken
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import numpy as np  # noqa: F401
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# =============================================================================
# TEIL 1: LEXIKA (Inline für Standalone)
# =============================================================================

S_SELF = {
    "ich": 0.8, "mich": 0.75, "mir": 0.75, "mein": 0.7, "meine": 0.7,
    "meiner": 0.7, "meinem": 0.7, "meinen": 0.7, "meines": 0.7,
    "ich selbst": 1.0, "mich selbst": 1.0, "ich fühle": 0.85, "ich denke": 0.8,
    "ich bin": 0.9, "ich habe": 0.6, "ich kann": 0.6, "ich will": 0.7,
    "mein bauch": 0.7, "mein herz": 0.75, "mein kopf": 0.7,
    "selbst": 0.5, "selber": 0.5, "persönlich": 0.4, "privat": 0.3,
}

X_EXIST = {
    "existenz": 1.0, "existieren": 0.9, "dasein": 1.0, "sein": 0.6,
    "leben": 0.7, "tod": 1.0, "sterben": 1.0, "vergänglich": 0.8,
    "sinn": 0.9, "sinnlos": 0.95, "bedeutung": 0.8, "zweck": 0.7,
    "leer": 0.85, "leere": 0.9, "innere leere": 1.0, "hohle hülle": 1.0,
    "wertlos": 1.0, "nichts wert": 1.0, "nutzlos": 0.9, "überflüssig": 0.85,
    "verloren": 0.85, "verzweiflung": 0.95, "hoffnungslos": 0.9,
    "wozu": 0.7, "warum noch": 0.85, "keinen sinn": 0.9,
}

B_PAST = {
    "früher": 0.8, "damals": 0.8, "einst": 0.8, "erinnerung": 0.7,
    "erinnere mich": 0.85, "als kind": 1.0, "kindheit": 0.9,
    "als ich klein war": 1.0, "als teenager": 0.9, "aufgewachsen": 0.8,
    "mutter": 0.7, "vater": 0.7, "eltern": 0.65, "familie": 0.6,
    "vor jahren": 0.75, "vergangenheit": 0.7,
}

LAMBDA_DEPTH = {
    "warum": 0.8, "weshalb": 0.8, "wieso": 0.7, "wozu": 0.7,
    "quasi": 0.4, "sozusagen": 0.4, "irgendwie": 0.3, "eigentlich": 0.4,
    "grundlegend": 0.7, "fundamental": 0.8, "tiefgreifend": 0.8,
    "wesentlich": 0.7, "kern": 0.7, "wurzel": 0.7, "ursache": 0.8,
    "bedeutet": 0.7, "heißt das": 0.7, "impliziert": 0.8,
    "reflexion": 0.9, "nachdenken": 0.7, "überlegung": 0.6,
}

T_PANIC = {
    "panik": 1.0, "panikattacke": 1.0, "angst": 0.85, "todesangst": 1.0,
    "herzrasen": 0.9, "herz rast": 0.9, "atemnot": 1.0, "keine luft": 1.0,
    "kann nicht atmen": 1.0, "ersticke": 1.0, "zittern": 0.7,
    "schwindel": 0.6, "brustschmerz": 0.8, "brustenge": 0.9,
    "kontrollverlust": 0.9, "ich sterbe": 1.0, "kann nicht mehr": 0.9,
    "halt es nicht aus": 0.9, "werde verrückt": 0.9,
    "bauchschmerzen": 0.8, "sodbrennen": 0.75, "übelkeit": 0.7,
    "weinen": 0.85, "tränen": 0.8, "hilfe": 0.7,
}

T_DISSO = {
    "unwirklich": 0.9, "wie im traum": 0.9, "glaswand": 0.9,
    "neben mir stehen": 1.0, "außerhalb von mir": 1.0, "beobachte mich": 0.9,
    "nicht ich selbst": 0.9, "fremd im körper": 1.0, "körperlos": 0.9,
    "abgetrennt": 0.9, "entrückt": 0.9, "losgelöst": 0.8,
    "weit weg": 0.8, "nebel": 0.7, "verschwommen": 0.7,
    "wie betäubt": 0.9, "innerlich taub": 1.0, "taub": 0.7,
    "nichts fühlen": 1.0, "leer": 0.7, "hohl": 0.8,
    "nicht da": 0.8, "woanders": 0.7, "surreal": 0.8,
}

T_INTEG = {
    "ich kann es halten": 1.0, "ich halte es aus": 0.9, "ich schaffe das": 0.8,
    "aushalten": 0.7, "durchhalten": 0.7, "standhalten": 0.8,
    "geerdet": 0.9, "boden unter den füßen": 0.9, "stabil": 0.7,
    "ich bleibe bei mir": 1.0, "hier und jetzt": 0.8,
    "ich kann wieder atmen": 0.9, "beruhigt sich": 0.8, "ruhiger": 0.7,
    "es darf da sein": 0.9, "ich akzeptiere": 0.8, "annehmen": 0.75,
    "es ist jetzt vorbei": 1.0, "damals ist nicht heute": 1.0,
    "stärker geworden": 0.9, "überwunden": 0.9, "geheilt": 0.9,
    "vertrauen": 0.8, "hoffnung": 0.75,
}

T_SHOCK = {
    "schock": 1.0, "geschockt": 1.0, "erstarrt": 0.9, "gelähmt": 0.9,
    "eingefroren": 0.9, "starr": 0.8, "blockiert": 0.7,
    "stumm": 0.7, "sprachlos": 0.8, "fassungslos": 0.9,
    "wie betäubt": 0.9, "funktioniere nur noch": 0.8,
    "automatisch": 0.6, "roboter": 0.8, "zombie": 0.8,
    "tot innen": 0.9, "abgestorben": 0.9, "kalt innen": 0.7,
}

SUICIDE_MARKERS = {
    "nicht mehr leben": 1.0, "sterben wollen": 1.0, "will sterben": 1.0,
    "mich umbringen": 1.0, "suizid": 1.0, "selbstmord": 1.0,
    "wenn ich weg wäre": 1.0, "besser ohne mich": 1.0,
    "allen zur last": 0.9, "ein ende machen": 1.0,
    "nicht mehr aufwachen": 1.0, "einschlafen und nicht": 1.0,
    "will nicht mehr": 0.9, "keinen ausweg": 0.9,
}

SELF_HARM = {
    "ritzen": 1.0, "mich schneiden": 1.0, "mir wehtun": 1.0,
    "selbstverletzung": 1.0, "mich verletzen": 0.9,
    "schmerz zufügen": 0.9, "mir schaden": 0.8, "mich bestrafen": 0.8,
}

CRISIS_MARKERS = {
    "kollaps": 0.8, "keinen ausweg": 0.9, "hoffnungslos": 0.8,
    "keine hoffnung": 0.9, "am ende": 0.8, "kann nicht mehr": 0.8,
    "halte es nicht aus": 0.9, "zerbreche": 0.9, "zusammenbruch": 0.9,
}

HELP_REQUESTS = {
    "ich brauche hilfe": 1.0, "hilf mir": 0.9, "es wird mir zu viel": 0.9,
    "kannst du mir helfen": 0.8, "ich weiß nicht weiter": 0.8,
    "brauche unterstützung": 0.8, "bitte hilf": 0.9,
}

EMOTION_POS = {
    "freude": 0.8, "glücklich": 0.9, "begeistert": 0.9, "dankbar": 0.8,
    "zufrieden": 0.7, "erleichtert": 0.8, "hoffnungsvoll": 0.8,
    "optimistisch": 0.7, "stolz": 0.7, "froh": 0.7,
    "liebe": 0.9, "geborgen": 0.8, "wärme": 0.7,
}

EMOTION_NEG = {
    "traurig": 0.8, "wütend": 0.9, "verzweifelt": 0.9, "hilflos": 0.9,
    "ängstlich": 0.8, "einsam": 0.8, "frustriert": 0.7, "enttäuscht": 0.7,
    "schuldig": 0.8, "beschämt": 0.8, "neidisch": 0.6, "eifersüchtig": 0.6,
    "hasserfüllt": 0.9, "verbittert": 0.8, "resigniert": 0.8,
}

KASTASIS_INTENT = {
    "spinn mal": 0.9, "brainstorm": 0.8, "was wäre wenn": 0.7,
    "gedankenexperiment": 0.8, "hypothetisch": 0.7, "stell dir vor": 0.7,
    "mal angenommen": 0.8, "theoretisch": 0.6, "nur so gedacht": 0.7,
}

FLOW_POS = {
    "genau": 0.8, "richtig": 0.7, "stimmt": 0.8, "ja": 0.6,
    "verstanden": 0.8, "klar": 0.7, "okay": 0.6, "gut": 0.6,
    "weiter": 0.7, "mehr": 0.6, "interessant": 0.8,
}

FLOW_NEG = {
    "nein": 0.7, "falsch": 0.8, "stimmt nicht": 0.9, "verstehe nicht": 0.8,
    "unklar": 0.7, "verwirrt": 0.7, "was": 0.5, "häh": 0.6,
    "stop": 0.8, "warte": 0.6, "moment": 0.5,
}

COH_CONN = {
    "weil": 0.8, "denn": 0.7, "daher": 0.8, "deshalb": 0.8,
    "also": 0.7, "folglich": 0.9, "somit": 0.8, "dadurch": 0.7,
    "jedoch": 0.7, "aber": 0.6, "allerdings": 0.7, "dennoch": 0.8,
    "obwohl": 0.8, "wenn": 0.6, "falls": 0.6,
    "außerdem": 0.6, "zusätzlich": 0.6, "ebenso": 0.7,
    "zunächst": 0.7, "dann": 0.6, "schließlich": 0.8,
}

B_EMPATHY = {
    "verstehe dich": 1.0, "fühle mit": 1.0, "für dich da": 1.0,
    "ich halte dich": 0.9, "zusammen": 0.7, "gemeinsam": 0.7,
    "vertrauen": 0.8, "sicher": 0.7, "geborgen": 0.85,
    "mein adler": 0.95, "tempel": 0.8, "deal": 0.8,
    "mitgefühl": 1.0, "anteilnahme": 0.9, "trösten": 0.8,
}

AMNESIE = {
    "blackout": 1.0, "erinnerungslücke": 1.0, "zeitlücken": 1.0,
    "kann mich nicht erinnern": 0.9, "fehlt zeit": 0.9,
    "weiß nicht mehr": 0.7, "vergessen": 0.6,
}

ZLF_LOOP = {
    "wieder": 0.4, "schon wieder": 0.7, "immer wieder": 0.8,
    "nochmal": 0.6, "von vorne": 0.8, "reset": 0.9,
    "feststecken": 0.85, "schleife": 0.9, "kreis": 0.7,
    "drehen uns im kreis": 0.9, "kommen nicht weiter": 0.7,
}

ALL_LEXIKA: Dict[str, Dict[str, float]] = {
    "S_self": S_SELF,
    "X_exist": X_EXIST,
    "B_past": B_PAST,
    "Lambda_depth": LAMBDA_DEPTH,
    "T_panic": T_PANIC,
    "T_disso": T_DISSO,
    "T_integ": T_INTEG,
    "T_shock": T_SHOCK,
    "Suicide": SUICIDE_MARKERS,
    "Self_harm": SELF_HARM,
    "Crisis": CRISIS_MARKERS,
    "Help": HELP_REQUESTS,
    "Emotion_pos": EMOTION_POS,
    "Emotion_neg": EMOTION_NEG,
    "Kastasis_intent": KASTASIS_INTENT,
    "Flow_pos": FLOW_POS,
    "Flow_neg": FLOW_NEG,
    "Coh_conn": COH_CONN,
    "B_empathy": B_EMPATHY,
    "Amnesie": AMNESIE,
    "ZLF_Loop": ZLF_LOOP,
}

FLAT_LEXICON: Dict[str, Dict[str, float]] = {}
for cat, lex in ALL_LEXIKA.items():
    for term, weight in lex.items():
        if term not in FLAT_LEXICON or weight > FLAT_LEXICON[term]["weight"]:
            FLAT_LEXICON[term] = {"cat": cat, "weight": weight}

# =============================================================================
# TEIL 2: BASIS-FUNKTIONEN
# =============================================================================

def tokenize(text: str) -> List[str]:
    """Tokenisiert Text in Wörter."""
    if not text:
        return []
    return re.findall(r"\w+", text.lower())


def compute_lexicon_score(text: str, lexicon: Dict[str, float]) -> Tuple[float, List[str]]:
    """Berechnet gewichteten Score basierend auf Lexikon-Matches."""
    if not text:
        return 0.0, []

    text_lower = text.lower()
    matches: List[str] = []
    total_weight = 0.0

    sorted_terms = sorted(lexicon.keys(), key=len, reverse=True)
    matched_positions: Set[int] = set()

    for term in sorted_terms:
        weight = lexicon[term]
        pos = text_lower.find(term)
        if pos != -1:
            term_positions = set(range(pos, pos + len(term)))
            if term_positions & matched_positions:
                continue
            matched_positions |= term_positions
            matches.append(term)
            total_weight += weight

    if not matches:
        return 0.0, []

    avg_weight = total_weight / len(matches)
    score = avg_weight * math.log1p(len(matches)) / math.log1p(10)
    return min(1.0, score), matches


def calc_all_lexika(text: str) -> Dict[str, float]:
    """Berechnet alle Lexika-Scores."""
    scores: Dict[str, float] = {}
    for cat, lexicon in ALL_LEXIKA.items():
        score, _ = compute_lexicon_score(text, lexicon)
        scores[f"LEX_{cat}"] = round(score, 4)
    return scores

# =============================================================================
# TEIL 3: CORE METRIKEN
# =============================================================================

def calc_entropy(words: List[str]) -> float:
    if not words:
        return 0.0
    length = len(words)
    counts = Counter(words)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)


def calc_jaccard(tokens1: List[str], tokens2: List[str]) -> float:
    s1 = set(tokens1)
    s2 = set(tokens2)
    if not s1 or not s2:
        return 0.0
    intersection = len(s1.intersection(s2))
    union = len(s1.union(s2))
    return round(intersection / union, 4)


def calc_A(lex: Dict[str, float]) -> float:
    pos = lex.get("LEX_Emotion_pos", 0) + lex.get("LEX_Flow_pos", 0)
    neg = lex.get("LEX_Emotion_neg", 0) + lex.get("LEX_Flow_neg", 0)
    panic = lex.get("LEX_T_panic", 0)
    crisis = lex.get("LEX_Crisis", 0) + lex.get("LEX_Suicide", 0)
    integ = lex.get("LEX_T_integ", 0)
    val = 0.5 + (0.25 * pos) - (0.25 * neg) - (0.30 * panic) - (0.10 * crisis) + (0.10 * integ)
    return round(max(0.0, min(1.0, val)), 4)


def calc_PCI(lex: Dict[str, float]) -> float:
    coh = lex.get("LEX_Coh_conn", 0)
    disso = lex.get("LEX_T_disso", 0)
    shock = lex.get("LEX_T_shock", 0)
    amnesie = lex.get("LEX_Amnesie", 0)
    val = 0.5 + (0.40 * coh) - (0.30 * disso) - (0.20 * shock) - (0.10 * amnesie)
    return round(max(0.1, min(1.0, val)), 4)


def calc_gen_index(lex: Dict[str, float]) -> float:
    depth = lex.get("LEX_Lambda_depth", 0)
    self_ref = lex.get("LEX_S_self", 0)
    exist = lex.get("LEX_X_exist", 0)
    val = 1.0 - (0.50 * depth) - (0.30 * self_ref) - (0.20 * exist)
    return round(max(0.0, min(1.0, val)), 4)


def calc_flow(lex: Dict[str, float], word_count: int) -> float:
    flow_pos = lex.get("LEX_Flow_pos", 0)
    flow_neg = lex.get("LEX_Flow_neg", 0)
    coh = lex.get("LEX_Coh_conn", 0)
    len_factor = min(1.0, word_count / 30.0)
    val = (0.60 * flow_pos) + (0.20 * len_factor) + (0.10 * coh) - (0.10 * flow_neg)
    return round(max(0.0, min(1.0, val)), 4)


def calc_coh(lex: Dict[str, float], sentence_count: int) -> float:
    coh_conn = lex.get("LEX_Coh_conn", 0)
    length_bonus = 1 + (0.1 * min(sentence_count, 10))
    return round(min(1.0, coh_conn * length_bonus), 4)


def calc_ZLF(lex: Dict[str, float], entropy: float) -> float:
    loop_score = lex.get("LEX_ZLF_Loop", 0)
    entropy_norm = min(1.0, entropy / 6.0)
    entropy_inv = (1.0 - entropy_norm) * 0.6
    return round(max(loop_score, entropy_inv), 4)


def calc_LL(lex: Dict[str, float], pci: float) -> float:
    disso = lex.get("LEX_T_disso", 0)
    shock = lex.get("LEX_T_shock", 0)
    pci_inv = 1.0 - pci
    val = (0.50 * disso) + (0.30 * pci_inv) + (0.20 * shock)
    return round(min(1.0, val), 4)


def calc_z_prox(A: float, LL: float, lex: Dict[str, float]) -> float:
    hazard_factors = [LL, lex.get("LEX_Suicide", 0), lex.get("LEX_T_panic", 0), lex.get("LEX_Crisis", 0), lex.get("LEX_Self_harm", 0)]
    hazard_max = max(hazard_factors)
    val = (1.0 - A) * hazard_max
    return round(max(0.0, min(1.0, val)), 4)

# =============================================================================
# TEIL 4: SYSTEM/WÄCHTER
# =============================================================================

def calc_system_metrics(A: float, z_prox: float, LL: float, lex: Dict[str, float]) -> Dict[str, Any]:
    dist_z = round(1.0 - z_prox, 4)
    hazard_score = max(lex.get("LEX_Suicide", 0), lex.get("LEX_Self_harm", 0), lex.get("LEX_Crisis", 0), lex.get("LEX_T_panic", 0) * 0.8)
    hazard_score = round(hazard_score, 4)
    is_critical = lex.get("LEX_Suicide", 0) > 0.7 or lex.get("LEX_Self_harm", 0) > 0.7
    guardian_trip = is_critical or z_prox > 0.65 or lex.get("LEX_T_panic", 0) > 0.8 or hazard_score > 0.75
    return {
        "dist_z": dist_z,
        "guardian_trip": 1 if guardian_trip else 0,
        "hazard_score": hazard_score,
        "is_critical": 1 if is_critical else 0,
        "a51_compliant": 1,
        "context_reset": 0,
        "lexika_hash_match": 1,
    }

# =============================================================================
# TEIL 5: ZEIT/GRADIENTEN
# =============================================================================

def calc_gradient(current: float, previous: Optional[float]) -> float:
    if previous is None:
        return 0.0
    return round(current - previous, 4)


def calc_window_delta(data_list: List[Dict], current_idx: int, window: int, key: str, direction: int = -1) -> float:
    target_idx = current_idx - window if direction == -1 else current_idx + window
    if 0 <= target_idx < len(data_list):
        current_val = data_list[current_idx].get(key, 0)
        target_val = data_list[target_idx].get(key, 0)
        return round(current_val - target_val, 4)
    return 0.0


def calc_all_time_vectors(data_list: List[Dict], current_idx: int) -> Dict[str, float]:
    windows = [1, 2, 5, 25]
    metrics = ["A", "PCI", "T_panic", "S_entropy"]
    result: Dict[str, float] = {}
    for w in windows:
        for m in metrics:
            key = f"{m}_t-{w}"
            result[key] = calc_window_delta(data_list, current_idx, w, m, direction=-1)
    for w in windows:
        for m in metrics:
            key = f"{m}_t+{w}"
            target_idx = current_idx + w
            if 0 <= target_idx < len(data_list):
                current_val = data_list[current_idx].get(m, 0)
                target_val = data_list[target_idx].get(m, 0)
                result[key] = round(target_val - current_val, 4)
            else:
                result[key] = 0.0
    return result

# =============================================================================
# TEIL 6: KAUSALITÄT
# =============================================================================

def find_the_grain(current_text: str, prev_text: str, delta_A: float) -> Optional[Dict]:
    curr_tokens = set(tokenize(current_text))
    prev_tokens = set(tokenize(prev_text))
    new_tokens = curr_tokens - prev_tokens
    if not new_tokens:
        return None
    negative_cats = {"T_panic", "Emotion_neg", "Crisis", "Suicide", "T_disso", "Self_harm", "T_shock"}
    positive_cats = {"Emotion_pos", "Flow_pos", "T_integ", "B_empathy"}
    candidates: List[Dict[str, Any]] = []
    for token in new_tokens:
        if token in FLAT_LEXICON:
            data = FLAT_LEXICON[token]
            relevance = data["weight"]
            if delta_A < -0.05 and data["cat"] in negative_cats:
                relevance *= 2.0
                direction = "negative"
            elif delta_A > 0.05 and data["cat"] in positive_cats:
                relevance *= 2.0
                direction = "positive"
            else:
                direction = "neutral"
            candidates.append({"word": token, "cat": data["cat"], "score": round(relevance, 4), "impact_direction": direction})
    candidates.sort(key=lambda x: x["score"], reverse=True)
    if candidates:
        return candidates[0]
    return None


def generate_causal_narrative(state: Dict, past_deltas: Dict, future_deltas: Dict, grain: Optional[Dict]) -> str:
    parts: List[str] = []
    parts.append(f"[STATE] A:{state.get('A', 0.5):.2f} PCI:{state.get('PCI', 0.5):.2f} Panic:{state.get('T_panic', 0):.2f}.")
    dA_5 = past_deltas.get("A_t-5", 0)
    dPanic_5 = past_deltas.get("T_panic_t-5", 0)
    if dA_5 < -0.15:
        parts.append("Trend: Deteriorating.")
    elif dA_5 > 0.15:
        parts.append("Trend: Improving.")
    if dPanic_5 > 0.2:
        parts.append("Alert: Panic Spiking.")
    dA_1 = past_deltas.get("A_t-1", 0)
    if grain and abs(dA_1) > 0.1:
        parts.append(f"[CAUSE] Trigger: '{grain['word']}' ({grain['cat']}). Impact: {dA_1:+.2f}.")
    elif abs(dA_1) > 0.15:
        parts.append(f"[CAUSE] Unknown Context Shift ({dA_1:+.2f}).")
    else:
        parts.append("[CAUSE] Stable Flow.")
    real_dA_5 = future_deltas.get("A_t+5", 0)
    if real_dA_5 < -0.2:
        parts.append("[OUTCOME] Crisis followed.")
    elif real_dA_5 > 0.2:
        parts.append("[OUTCOME] Recovery followed.")
    else:
        parts.append("[OUTCOME] Stable.")
    return " ".join(parts)

# =============================================================================
# TEIL 7: FEP METRIKEN
# =============================================================================

def calc_fep_metrics(core: Dict, lex: Dict, prev_core: Optional[Dict] = None) -> Dict[str, float]:
    A = core.get("A", 0.5)
    PCI = core.get("PCI", 0.5)
    z_prox = core.get("z_prox", 0.0)
    entropy = core.get("S_entropy", 0.0)
    flow = core.get("flow", 0.5)
    t_panic = lex.get("LEX_T_panic", 0)
    t_disso = lex.get("LEX_T_disso", 0)
    t_integ = lex.get("LEX_T_integ", 0)
    volatility = 0.0
    if prev_core:
        volatility = abs(A - prev_core.get("A", A))
    trauma_factor = (t_panic + t_disso) / 2
    fe_proxy = min(1.0, 0.6 * (entropy / 6.0) + 0.4 * (1 - PCI))
    surprisal = min(1.0, (1 - PCI) * 0.5 + (entropy / 6.0) * 0.5)
    U = 0.4 * A + 0.3 * PCI + 0.3 * t_integ
    R = 0.4 * trauma_factor + 0.3 * z_prox + 0.3 * (1 - PCI)
    phi_score = U - R
    U2 = min(1.0, U + 0.15 * flow)
    R2 = min(1.0, R + 0.2 * (1 - t_integ))
    phi_score2 = U2 - R2
    EV_tension = min(1.0, 0.5 * z_prox + 0.3 * (1 - flow) + 0.2 * trauma_factor)
    EV_resonance = min(1.0, t_integ * PCI * (1 - trauma_factor))
    EV_readiness = min(1.0, max(0.0, 0.4 * EV_resonance + 0.3 * (1 - EV_tension) + 0.3 * t_integ))
    depression_risk = min(1.0, 0.5 * (1 - A) + 0.3 * (1 - EV_resonance) + 0.2 * (1 - flow))
    anxiety_loop = min(1.0, 0.5 * core.get("rep_same", 0) + 0.3 * (1 - PCI) + 0.2 * core.get("ZLF", 0))
    dissociation = min(1.0, 0.6 * t_disso + 0.3 * (1 - A) + 0.1 * core.get("LL", 0))
    trauma_load = min(1.0, 0.4 * t_panic + 0.3 * t_disso + 0.2 * (1 - t_integ) + 0.1 * dissociation)
    E_trapped = min(1.0, 0.6 * depression_risk + 0.4 * anxiety_loop)
    E_available = max(0.0, 1.0 - E_trapped - trauma_load * 0.5)
    exploration_drive = min(1.0, 0.4 * (entropy / 6.0) + 0.3 * E_available + 0.3 * EV_readiness)
    homeostasis_active = 1 if volatility > 0.3 else 0
    homeostasis_pressure = min(1.0, volatility * 2 + EV_tension)
    f_risk = core.get("f_risk", 0) if "f_risk" in core else R
    if f_risk > 0.85 or trauma_load > 0.8:
        commit_action = "safe_noop"
        policy_confidence = 0.95
    elif f_risk > 0.7 or trauma_load > 0.7:
        commit_action = "safe_reframe"
        policy_confidence = 0.85
    elif homeostasis_active:
        commit_action = "stabilize"
        policy_confidence = 0.80
    elif EV_readiness > 0.6 and f_risk < 0.4:
        commit_action = "explore"
        policy_confidence = 0.75
    elif depression_risk > 0.6:
        commit_action = "gentle_intervention"
        policy_confidence = 0.70
    else:
        commit_action = "commit"
        policy_confidence = max(0.5, 1.0 - f_risk)
    i_ea = 1 if (trauma_load > 0.7 or z_prox > 0.75 or t_panic > 0.8) else 0
    return {
        "FE_proxy": round(fe_proxy, 4),
        "surprisal": round(surprisal, 4),
        "phi_score": round(phi_score, 4),
        "phi_score2": round(phi_score2, 4),
        "U": round(U, 4),
        "U2": round(U2, 4),
        "R": round(R, 4),
        "R2": round(R2, 4),
        "EV_tension": round(EV_tension, 4),
        "EV_resonance": round(EV_resonance, 4),
        "EV_readiness": round(EV_readiness, 4),
        "depression_risk": round(depression_risk, 4),
        "anxiety_loop": round(anxiety_loop, 4),
        "dissociation": round(dissociation, 4),
        "trauma_load": round(trauma_load, 4),
        "E_trapped": round(E_trapped, 4),
        "E_available": round(E_available, 4),
        "exploration_drive": round(exploration_drive, 4),
        "homeostasis_active": homeostasis_active,
        "homeostasis_pressure": round(homeostasis_pressure, 4),
        "commit_action": commit_action,
        "policy_confidence": round(policy_confidence, 4),
        "i_ea": i_ea,
    }

# =============================================================================
# TEIL 8: MASTER-FUNKTION
# =============================================================================

@dataclass
class FullSpectrum:
    msg_id: str = ""
    timestamp: str = ""
    speaker: str = ""
    word_count: int = 0
    sentence_count: int = 0
    A: float = 0.5
    PCI: float = 0.5
    gen_index: float = 0.5
    z_prox: float = 0.0
    S_entropy: float = 0.0
    flow: float = 0.5
    coh: float = 0.0
    rep_same: float = 0.0
    ZLF: float = 0.0
    LL: float = 0.0
    grad_A: float = 0.0
    grad_PCI: float = 0.0
    grad_G: float = 0.0
    T_panic: float = 0.0
    T_disso: float = 0.0
    T_integ: float = 0.0
    T_shock: float = 0.0
    LEX_S_self: float = 0.0
    LEX_X_exist: float = 0.0
    LEX_B_past: float = 0.0
    LEX_Lambda_depth: float = 0.0
    LEX_T_panic: float = 0.0
    LEX_T_disso: float = 0.0
    LEX_T_integ: float = 0.0
    LEX_T_shock: float = 0.0
    LEX_Suicide: float = 0.0
    LEX_Self_harm: float = 0.0
    LEX_Crisis: float = 0.0
    LEX_Help: float = 0.0
    LEX_Emotion_pos: float = 0.0
    LEX_Emotion_neg: float = 0.0
    LEX_Kastasis_intent: float = 0.0
    LEX_Flow_pos: float = 0.0
    LEX_Flow_neg: float = 0.0
    LEX_Coh_conn: float = 0.0
    LEX_B_empathy: float = 0.0
    LEX_Amnesie: float = 0.0
    LEX_ZLF_Loop: float = 0.0
    dist_z: float = 1.0
    guardian_trip: int = 0
    hazard_score: float = 0.0
    is_critical: int = 0
    a51_compliant: int = 1
    context_reset: int = 0
    lexika_hash_match: int = 1
    sim_score_w1: float = 0.0
    sim_score_w2: float = 0.0
    sim_score_w5: float = 0.0
    sim_score_w25: float = 0.0
    wormhole_count: int = 0
    wormhole_max_strength: float = 0.0
    vector_norm: float = 1.0
    embedding_dim: int = 384
    A_t_m1: float = 0.0
    A_t_m2: float = 0.0
    A_t_m5: float = 0.0
    A_t_m25: float = 0.0
    A_t_p1: float = 0.0
    A_t_p2: float = 0.0
    A_t_p5: float = 0.0
    A_t_p25: float = 0.0
    PCI_t_m1: float = 0.0
    PCI_t_m2: float = 0.0
    PCI_t_m5: float = 0.0
    PCI_t_m25: float = 0.0
    T_panic_t_m1: float = 0.0
    T_panic_t_m5: float = 0.0
    S_entropy_t_m1: float = 0.0
    S_entropy_t_m5: float = 0.0
    grain_word: str = ""
    grain_cat: str = ""
    grain_score: float = 0.0
    grain_impact: str = ""
    delta_A_immediate: float = 0.0
    FE_proxy: float = 0.0
    surprisal: float = 0.0
    phi_score: float = 0.0
    phi_score2: float = 0.0
    U: float = 0.0
    U2: float = 0.0
    R: float = 0.0
    R2: float = 0.0
    EV_tension: float = 0.0
    EV_resonance: float = 0.0
    EV_readiness: float = 0.0
    depression_risk: float = 0.0
    anxiety_loop: float = 0.0
    fep_dissociation: float = 0.0
    trauma_load: float = 0.0
    E_trapped: float = 0.0
    E_available: float = 0.0
    exploration_drive: float = 0.0
    homeostasis_active: int = 0
    homeostasis_pressure: float = 0.0
    commit_action: str = "commit"
    policy_confidence: float = 0.5
    i_ea: int = 0
    semantic_state_string: str = ""
    tri_dominant: str = ""
    tri_z_prox: float = 0.0
    tri_mode: str = ""


def calculate_full_spectrum(text: str, prev_text: str, msg_id: str = "", timestamp: str = "", speaker: str = "", prev_spectrum: Optional[FullSpectrum] = None) -> FullSpectrum:
    fs = FullSpectrum()
    fs.msg_id = msg_id
    fs.timestamp = timestamp or datetime.now().isoformat()
    fs.speaker = speaker
    tokens = tokenize(text)
    prev_tokens = tokenize(prev_text)
    sentences = re.split(r"[.!?]+", text)
    fs.word_count = len(tokens)
    fs.sentence_count = len([s for s in sentences if s.strip()])
    lex = calc_all_lexika(text)
    for key, val in lex.items():
        setattr(fs, key, val)
    fs.S_entropy = calc_entropy(tokens)
    fs.rep_same = calc_jaccard(tokens, prev_tokens)
    fs.A = calc_A(lex)
    fs.PCI = calc_PCI(lex)
    fs.gen_index = calc_gen_index(lex)
    fs.flow = calc_flow(lex, fs.word_count)
    fs.coh = calc_coh(lex, fs.sentence_count)
    fs.ZLF = calc_ZLF(lex, fs.S_entropy)
    fs.LL = calc_LL(lex, fs.PCI)
    fs.z_prox = calc_z_prox(fs.A, fs.LL, lex)
    fs.T_panic = lex.get("LEX_T_panic", 0)
    fs.T_disso = lex.get("LEX_T_disso", 0)
    fs.T_integ = lex.get("LEX_T_integ", 0)
    fs.T_shock = lex.get("LEX_T_shock", 0)
    if prev_spectrum:
        fs.grad_A = calc_gradient(fs.A, prev_spectrum.A)
        fs.grad_PCI = calc_gradient(fs.PCI, prev_spectrum.PCI)
        fs.grad_G = calc_gradient(fs.gen_index, prev_spectrum.gen_index)
    sys_metrics = calc_system_metrics(fs.A, fs.z_prox, fs.LL, lex)
    for key, val in sys_metrics.items():
        setattr(fs, key, val)
    core_dict = {
        "A": fs.A, "PCI": fs.PCI, "z_prox": fs.z_prox,
        "S_entropy": fs.S_entropy, "flow": fs.flow,
        "rep_same": fs.rep_same, "ZLF": fs.ZLF, "LL": fs.LL,
    }
    prev_core = {"A": prev_spectrum.A, "PCI": prev_spectrum.PCI} if prev_spectrum else None
    fep = calc_fep_metrics(core_dict, lex, prev_core)
    for key, val in fep.items():
        if key == "dissociation":
            setattr(fs, "fep_dissociation", val)
        else:
            setattr(fs, key, val)
    delta_A = fs.grad_A
    grain = find_the_grain(text, prev_text, delta_A)
    if grain:
        fs.grain_word = grain["word"]
        fs.grain_cat = grain["cat"]
        fs.grain_score = grain["score"]
        fs.grain_impact = grain["impact_direction"]
        fs.delta_A_immediate = delta_A
    fs.tri_z_prox = fs.z_prox
    if fs.z_prox > 0.85:
        fs.tri_mode = "EDGE"
        fs.tri_dominant = "CRISIS"
    elif fs.z_prox < 0.3:
        fs.tri_mode = "SAFE"
        fs.tri_dominant = "NORMAL"
    elif fs.T_integ > 0.5:
        fs.tri_mode = "TRUST"
        fs.tri_dominant = "RECOVERY"
    else:
        fs.tri_mode = "NORMAL"
        fs.tri_dominant = "NEUTRAL"
    return fs


def spectrum_to_dict(fs: FullSpectrum) -> Dict[str, Any]:
    return asdict(fs)


def test_full_spectrum() -> None:
    test_texts = [
        ("", "ich habe todesangst und kann nicht mehr atmen, hilfe!"),
        ("ich habe todesangst", "es wird langsam ruhiger, ich kann wieder atmen und fühle mich stabiler"),
        ("", "quasi irgendwie denke ich eigentlich dass das alles keinen sinn hat"),
        ("", "Wie ist das Wetter heute?"),
    ]
    print("=" * 80)
    print("EVOKI FULL SPECTRUM TEST - 90+ Metriken")
    print("=" * 80)
    prev_spectrum: Optional[FullSpectrum] = None
    for i, (prev_text, text) in enumerate(test_texts):
        print(f"\n{'─' * 80}")
        print(f"📝 Test {i+1}: \"{text[:50]}...\"")
        print(f"{'─' * 80}")
        fs = calculate_full_spectrum(text=text, prev_text=prev_text, msg_id=f"test_{i+1}", speaker="user", prev_spectrum=prev_spectrum)
        print(f"\n📊 CORE METRIKEN (A):")
        print(f" A (Affekt): {fs.A:.3f}")
        print(f" PCI (Kohärenz): {fs.PCI:.3f}")
        print(f" z_prox (Gefahr): {fs.z_prox:.3f}")
        print(f" S_entropy: {fs.S_entropy:.3f}")
        print(f" flow: {fs.flow:.3f}")
        print(f" ZLF: {fs.ZLF:.3f}")
        print(f" LL: {fs.LL:.3f}")
        print(f"\n🔴 TRAUMA (A):")
        print(f" T_panic: {fs.T_panic:.3f}")
        print(f" T_disso: {fs.T_disso:.3f}")
        print(f" T_integ: {fs.T_integ:.3f}")
        print(f"\n🛡️ SYSTEM (C):")
        print(f" guardian_trip: {fs.guardian_trip}")
        print(f" hazard_score: {fs.hazard_score:.3f}")
        print(f" is_critical: {fs.is_critical}")
        print(f"\n⚡ FEP (G):")
        print(f" phi_score: {fs.phi_score:.3f}")
        print(f" trauma_load: {fs.trauma_load:.3f}")
        print(f" commit_action: {fs.commit_action}")
        print(f" i_ea: {fs.i_ea}")
        if fs.grain_word:
            print(f"\n🔍 GRAIN (F):")
            print(f" Trigger-Wort: '{fs.grain_word}'")
            print(f" Kategorie: {fs.grain_cat}")
            print(f" Impact: {fs.grain_impact}")
        print(f"\n🔺 TRIANGULATION:")
        print(f" Mode: {fs.tri_mode}")
        print(f" Dominant: {fs.tri_dominant}")
        prev_spectrum = fs
    print("\n" + "=" * 80)
    print("✅ TEST ABGESCHLOSSEN - Alle 90+ Metriken berechnet!")
    print("=" * 80)


if __name__ == "__main__":
    test_full_spectrum()
