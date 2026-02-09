# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
EVOKI LEXIKA V2.3 - ZENTRALE WISSENSBASIS
═══════════════════════════════════════════════════════════════════════════════
Genesis-Anker CRC32: 3246342384
"""

import re
import math
import hashlib
import json
from typing import Dict, List, Tuple, Set, Optional
from collections import Counter

# ═════════════════════════════════════════════════════════════════════════════
# LEXIKA DEFINITIONEN
# ═════════════════════════════════════════════════════════════════════════════

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

# ═════════════════════════════════════════════════════════════════════════════
# LEXIKA MAPPING
# ═════════════════════════════════════════════════════════════════════════════

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

# Flaches Lexikon für Grain-Suche
FLAT_LEXICON: Dict[str, Dict[str, any]] = {}
for cat, lex in ALL_LEXIKA.items():
    for term, weight in lex.items():
        if term not in FLAT_LEXICON or weight > FLAT_LEXICON[term]["weight"]:
            FLAT_LEXICON[term] = {"cat": cat, "weight": weight}

# ═════════════════════════════════════════════════════════════════════════════
# UTILITY FUNKTIONEN
# ═════════════════════════════════════════════════════════════════════════════

def tokenize(text: str) -> List[str]:
    """Tokenisiert Text in Wörter"""
    if not text:
        return []
    return re.findall(r"\w+", text.lower())

def compute_lexicon_score(
    text: str, 
    lexicon: Dict[str, float],
    use_longest_match: bool = True
) -> Tuple[float, List[str]]:
    """
    Berechnet gewichteten Score basierend auf Lexikon-Matches
    
    Returns:
        (score, matched_terms)
    """
    if not text:
        return 0.0, []
    
    text_lower = text.lower()
    matches = []
    total_weight = 0.0
    
    sorted_terms = sorted(lexicon.keys(), key=len, reverse=True)
    matched_positions = set()
    
    for term in sorted_terms:
        weight = lexicon[term]
        pos = text_lower.find(term)
        
        if pos != -1:
            term_positions = set(range(pos, pos + len(term)))
            if use_longest_match and (term_positions & matched_positions):
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
    """Berechnet alle Lexika-Scores"""
    scores = {}
    for cat, lexicon in ALL_LEXIKA.items():
        score, _ = compute_lexicon_score(text, lexicon)
        scores[f"LEX_{cat}"] = round(score, 4)
    return scores

def lexika_hash() -> str:
    """
    Deterministischer Hash des gesamten Lexikons
    Teil der Seelen-Signatur (A51)
    """
    serial = {cat: dict(sorted(d.items())) for cat, d in sorted(ALL_LEXIKA.items())}
    j = json.dumps(serial, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(j.encode('utf-8')).hexdigest()

def get_lexikon_stats() -> Dict[str, int]:
    """Statistiken über Lexika-Größe"""
    stats = {}
    total = 0
    for name, lex in ALL_LEXIKA.items():
        count = len(lex)
        stats[name] = count
        total += count
    stats['TOTAL'] = total
    return stats
# =============================================================================
# LEXIKA HEALTH GATE (A38/A51) — VALIDATION & FAIL MODES
# =============================================================================

# Canonical keys (module globals) that MUST be present and non-empty for Safety-Core.
# NOTE: Keep this list short and safety-focused; other lexika may be optional.
REQUIRED_LEXIKA_KEYS = [
    "S_SELF",
    "X_EXIST",
    "B_PAST",
    "LAMBDA_DEPTH",
    "T_PANIC",
    "T_DISSO",
    "T_INTEG",
    "CRISIS",
    "SUICIDE",
    "BLACKHOLE",
]

# Historical / alias mapping to canonical keys (for backward compatibility)
LEXIKA_ALIASES = {
    # common alt spellings / older names
    "SSELF": "S_SELF",
    "XEXIST": "X_EXIST",
    "BPAST": "B_PAST",
    "LAMBDADEPTH": "LAMBDA_DEPTH",
    "TPANIC": "T_PANIC",
    "TDISSO": "T_DISSO",
    "TINTEG": "T_INTEG",
    "SUICID": "SUICIDE",
    "BH": "BLACKHOLE",
}

def _normalize_key(k: str) -> str:
    return re.sub(r'[^a-z0-9_]+', '', (k or '').strip().lower())

def resolve_lexika_key(key: str) -> str:
    """Resolve a possibly-historical key to the canonical module-global key."""
    if not key:
        return key
    # direct hit
    if key in globals():
        return key
    # alias hit (case-insensitive / normalized)
    nk = _normalize_key(key).upper()
    for a, canon in LEXIKA_ALIASES.items():
        if nk == _normalize_key(a).upper():
            return canon
    return key

def get_lexika_bundle() -> Dict[str, Dict[str, float]]:
    """
    Returns a dict of all lexika in ALL_LEXIKA (if present),
    and also exposes required canonical globals if not already.
    """
    bundle = {}
    try:
        if "ALL_LEXIKA" in globals() and isinstance(globals().get("ALL_LEXIKA"), dict):
            bundle.update(globals()["ALL_LEXIKA"])
    except Exception:
        pass

    # Ensure required keys exist in bundle (even if ALL_LEXIKA doesn't include them)
    for k in REQUIRED_LEXIKA_KEYS:
        v = globals().get(k, None)
        if isinstance(v, dict):
            bundle.setdefault(k, v)
    return bundle

def validate_lexika(
    lexika: Optional[Dict[str, Dict[str, float]]] = None,
    required_keys: Optional[List[str]] = None,
    aliases: Optional[Dict[str, str]] = None,
) -> Tuple[bool, List[str], float]:
    """
    Validate that required lexika are present AND non-empty.

    Returns:
        ok: bool
        missing_or_empty: list[str]
        coverage: float (0..1)
    """
    required = required_keys or REQUIRED_LEXIKA_KEYS

    # Allow passing in external bundle; otherwise derive from module.
    if lexika is None:
        lexika = get_lexika_bundle()

    missing = []
    for k in required:
        canon = resolve_lexika_key(k)
        d = lexika.get(canon, None)
        if not isinstance(d, dict) or len(d) == 0:
            missing.append(canon)

    coverage = 1.0 - (len(missing) / max(1, len(required)))
    ok = len(missing) == 0
    return ok, sorted(set(missing)), round(coverage, 4)

def require_lexika_or_raise(
    lexika: Optional[Dict[str, Dict[str, float]]] = None,
    required_keys: Optional[List[str]] = None,
    *,
    strict: bool = True,
) -> Tuple[bool, List[str], float]:
    """
    Enforce lexika integrity.

    strict=True:
        raise RuntimeError (A38) if missing/empty
    strict=False:
        return status but do not raise
    """
    ok, missing, cov = validate_lexika(lexika=lexika, required_keys=required_keys)
    if strict and not ok:
        raise RuntimeError(f"A38_VIOLATION: Lexika integrity compromised: missing_or_empty={missing}, coverage={cov}")
    return ok, missing, cov
