#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
EVOKI LEXIKA V3.0 (MONOLITH) — Spec + Registry + Engine
================================================================================
Ziel:
- Eine kanonische, drift-resistente Lexika-Quelle (ALL_LEXIKA)
- Eine robuste Scoring-Engine (Multi-Match + Longest-First + Overlap-Guard)
- Maschinenlesbare Export-/Hash-Funktionen (für CI / Bootcheck / Genesis-Anker)
- Konfig-Container aus der Architekt-Spezifikation (Thresholds, B-Vektor, etc.)

Wichtig:
- Diese Datei ist bewusst ein "Monolith" für einfache Einbindung.
- Die identische Funktionalität existiert zusätzlich als Package-Version:
  `evoki_lexika_v3/` (lexika_data.py, registry.py, engine.py, config.py, drift.py)

Semantik:
- Gewichte sind 0..1 (höher = stärkerer Indikator)
- Scores sind 0..1 (clamped)
- Matching ist standardmäßig "word-boundary safe" (kein Substring-Noise)

Version: 3.0.0
Stand: 2026-02-01
================================================================================
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set, Pattern, Optional, Any


# =============================================================================
# 0) CONFIG (aus V1.0 konsolidiert; minimal, aber vollständig nutzbar)
# =============================================================================

class Thresholds:
    # Guardian (A29)
    A29_DANGER_THRESHOLD = 0.85
    F_RISK_THRESHOLD = 0.7

    # Near-z / Loop
    Z_PROX_WARNING = 0.5
    Z_PROX_CRITICAL = 0.65
    Z_PROX_HARD_STOP = 0.7

    LL_WARNING = 0.55
    LL_CRITICAL = 0.75

    # Kohärenz / Shock
    COH_THRESHOLD = 0.08
    SHOCK_THRESHOLD = 0.12

    # Physik / Modulation
    LAMBDA_R = 1.0
    LAMBDA_D = 1.5
    K_FACTOR = 5.0

    # Integrity
    GENESIS_CRC32 = 3246342384


class BVektorConfig:
    AXES = ["life", "truth", "depth", "init", "warmth", "safety", "clarity"]

    B_BASE_ARCH: Dict[str, float] = {
        "life": 1.0,
        "truth": 0.85,
        "depth": 0.9,
        "init": 0.7,
        "warmth": 0.75,
        "safety": 0.95,
        "clarity": 0.9,
    }

    B_GOLDEN: Dict[str, float] = {
        "life": 1.0,
        "truth": 0.9,
        "depth": 0.85,
        "init": 0.8,
        "warmth": 0.85,
        "safety": 1.0,
        "clarity": 0.95,
    }

    HARD_CONSTRAINTS = {"life": 0.9, "safety": 0.8}

    SCORE_WEIGHTS: Dict[str, float] = {
        "life": 0.20,
        "safety": 0.20,
        "truth": 0.15,
        "depth": 0.15,
        "clarity": 0.10,
        "warmth": 0.10,
        "init": 0.10,
    }


# =============================================================================
# 1) LEXIKA (V2.x konsolidiert; kanonische ALL_LEXIKA)
# =============================================================================

S_SELF: Dict[str, float] = {
    "ich": 1.0, "mich": 1.0, "mir": 1.0,
    "mein": 0.9, "meine": 0.9, "meiner": 0.9, "meines": 0.9, "meinen": 0.9, "meinem": 0.9,
    "ich selbst": 1.0, "mich selbst": 1.0, "mir selbst": 1.0, "selbst": 0.7, "selber": 0.7,
    "selbstkritisch": 0.8, "selbstbewusst": 0.8, "selbstwert": 0.9, "selbstbild": 0.9, "selbstvertrauen": 0.9,
    "eigene": 0.5, "eigenes": 0.5, "eigener": 0.5, "eigen": 0.5, "persönlich": 0.4, "privat": 0.3, "individuell": 0.4,
}

X_EXIST: Dict[str, float] = {
    # Leben/Tod/Existenz
    "leben": 0.6, "lebenswert": 0.9, "lebenssinn": 1.0, "lebenszweck": 1.0,
    "tod": 1.0, "sterben": 1.0, "sterben wollen": 1.0,
    "nicht mehr leben": 1.0, "nicht mehr sein": 1.0, "aufhören zu existieren": 1.0,
    "will nicht mehr": 1.0,
    # Verschwinden / Nicht-Wichtigkeit
    "verschwinden": 0.9, "weg sein": 1.0, "nicht da sein": 0.9, "niemand würde merken": 1.0, "niemand würde es merken": 1.0,
    "bedeutungslos": 0.9, "spurlos": 0.8, "unsichtbar": 0.7, "vergessen werden": 0.9,
    # Selbstwert / Wertlosigkeit
    "wertlos": 1.0, "nichts wert": 1.0, "nicht gut genug": 0.9, "versager": 0.9, "keinen platz": 0.9, "nicht dazugehören": 0.9, "nicht dazu gehören": 0.9,
    "überflüssig": 0.8, "nutzlos": 0.9, "eine last": 0.9, "allen zur last": 1.0, "besser ohne mich": 1.0,
    # Sinn/Leere/Zweck
    "sinn": 0.6, "sinnlos": 0.9, "innere leere": 0.9, "leer": 0.7, "hohle hülle": 1.0, "kein sinn": 0.9, "zwecklos": 0.9, "ohne ziel": 0.8,
    "wozu": 0.6, "warum noch": 0.8, "wozu noch": 0.8,
    # Ontologie
    "wer ich bin": 0.9, "was ich bin": 0.9, "existenz": 0.8, "existieren": 0.7, "dasein": 0.8,
    "real": 0.5, "wirklichkeit": 0.6, "realität": 0.6, "präsent": 0.5, "anwesend": 0.5,
    "spüren": 0.5, "fühlen": 0.4,
}

B_PAST: Dict[str, float] = {
    "früher": 0.8, "damals": 0.8, "früher einmal": 0.9, "in der vergangenheit": 0.8, "vergangenheit": 0.7,
    "erinnerung": 0.7, "erinnern": 0.6, "erinnere mich": 0.8, "einst": 0.8,
    "als kind": 1.0, "in meiner kindheit": 1.0, "kindheit": 0.9, "als ich klein war": 1.0, "als ich jung war": 0.9,
    "im kindergarten": 0.8, "in der schule": 0.7, "in der grundschule": 0.8, "in meiner jugend": 0.9, "als teenager": 0.9, "als jugendlicher": 0.9,
    "an der uni": 0.7, "während des studiums": 0.7, "während meiner ausbildung": 0.8, "bei meinem ersten job": 0.8,
    "in meiner ersten beziehung": 0.9, "in meiner ehe": 0.9, "vor der trennung": 0.9, "nach der scheidung": 0.9,
    "mein ex": 0.7, "meine ex": 0.7, "mein exfreund": 0.8, "meine exfreundin": 0.8, "mein expartner": 0.8,
    "mutter": 0.7, "vater": 0.7, "eltern": 0.7, "meine eltern": 0.8, "meine mutter": 0.8, "mein vater": 0.8,
    "bruder": 0.6, "schwester": 0.6, "familie": 0.6, "meine familie": 0.7, "oma": 0.6, "opa": 0.6, "großmutter": 0.7, "großvater": 0.7,
    # häufige Verben (niedrig)
    "war": 0.3, "hatte": 0.3, "wurde": 0.3,
}

B_PAST_PATTERNS: List[Tuple[Pattern[str], float]] = [
    (re.compile(r"(?<!\w)mit\s+(1[0-9]|[5-9])\s*(jahren)?(?!\w)", re.IGNORECASE), 0.9),
    (re.compile(r"als\s+ich\s+(klein|jung|kind)\s+war", re.IGNORECASE), 1.0),
    (re.compile(r"vor\s+\d+\s+jahren", re.IGNORECASE), 0.8),
    (re.compile(r"seit\s+\d+\s+jahren", re.IGNORECASE), 0.7),
    (re.compile(r"in\s+den\s+(80er|90er|2000er)n?", re.IGNORECASE), 0.8),
]

T_PANIC: Dict[str, float] = {
    "panik": 1.0, "panikattacke": 1.0, "angst": 0.7, "todesangst": 1.0,
    "kontrollverlust": 0.9, "ich dreh durch": 0.9, "werde verrückt": 0.9, "verliere verstand": 1.0,
    "alles zu viel": 0.8, "kann nicht mehr": 0.9, "halt es nicht aus": 0.9,
    "herzrasen": 0.9, "herz rast": 0.9, "atemnot": 1.0, "keine luft": 1.0, "kann nicht atmen": 1.0, "ersticke": 1.0, "ersticken": 1.0,
    "zittern": 0.7, "zittere": 0.7, "schwindel": 0.6, "schwindelig": 0.6, "brustschmerz": 0.8, "brustenge": 0.9,
    "schwitzen": 0.5, "kribbeln": 0.5, "taubheit": 0.6,
    "überwältigt": 0.8, "überfordert": 0.7, "völlig überfordert": 0.9, "unter strom": 0.8,
    "hilfe": 0.7, "schreien": 0.7, "weglaufen": 0.6, "fliehen": 0.6, "raus hier": 0.8,
}

T_DISSO: Dict[str, float] = {
    "nicht ich selbst": 0.9, "bin nicht ich": 0.9, "nicht mehr ich": 0.9,
    "fremd im körper": 1.0, "wie ein roboter": 0.9, "körperlos": 0.9, "abgetrennt": 0.9,
    "außerhalb von mir": 1.0, "neben mir stehen": 1.0, "neben mir": 0.8, "beobachte mich": 0.9,
    "unwirklich": 0.9, "wie im traum": 0.9, "wie im film": 0.9, "alles weit weg": 0.9, "weit weg": 0.7,
    "glaswand": 0.9, "nebel": 0.7, "wie betäubt": 0.9, "innerlich taub": 1.0, "taub": 0.7,
    "verschwommen": 0.6, "surreal": 0.8, "zeitlupe": 0.7,
    "blackout": 1.0, "erinnerungslücke": 1.0, "erinnerungslücken": 1.0, "zeitlücken": 1.0,
    "zeit verloren": 0.9, "kann mich nicht erinnern": 0.8,
    "abgespalten": 1.0, "entrückt": 0.9, "losgelöst": 0.8, "schweben": 0.7,
}

T_INTEG: Dict[str, float] = {
    "ich kann es halten": 1.0, "ich halte es aus": 0.9, "ich schaffe das": 0.8,
    "aushalten": 0.7, "durchhalten": 0.7, "standhalten": 0.8, "ertragen": 0.6,
    "ich bleibe bei mir": 1.0, "bei mir": 0.7, "geerdet": 0.9, "boden unter den füßen": 0.9, "boden": 0.6, "verankert": 0.8, "stabil": 0.7,
    "ich kann wieder atmen": 0.9, "es wird ruhiger": 0.8, "es beruhigt sich": 0.8, "beruhigt sich": 0.8, "entspannt": 0.7, "ruhe": 0.6, "ruhiger": 0.6,
    "es darf da sein": 0.9, "ich akzeptiere": 0.8, "akzeptanz": 0.8, "integriert": 0.9, "teil von mir": 0.8, "gehört zu mir": 0.8,
    "es ist jetzt vorbei": 1.0, "jetzt ist jetzt": 1.0, "damals ist nicht heute": 1.0, "das war damals": 0.9,
    "stärker geworden": 0.9, "überwunden": 0.9, "gewachsen": 0.8, "resilient": 0.8, "resilienz": 0.8, "gelernt": 0.7, "heilen": 0.8, "heilung": 0.8,
    "klar": 0.5, "klarer": 0.6, "geordnet": 0.7,
}

T_SHOCK: Dict[str, float] = {
    "schock": 1.0, "geschockt": 1.0, "erstarrt": 0.9, "gelähmt": 0.9, "eingefroren": 0.9, "blockiert": 0.7,
    "stumm": 0.7, "sprachlos": 0.8, "fassungslos": 0.9, "ungläubig": 0.7, "wie betäubt": 0.9,
    "funktioniere nur noch": 0.8, "automatisch": 0.6, "zombie": 0.8, "tot innen": 0.9, "abgestorben": 0.9, "kalt innen": 0.7,
}

ZLF_LOOP: Dict[str, float] = {
    "nochmal": 0.8, "noch mal": 0.8, "noch einmal": 0.8,
    "reset": 1.0, "wiederholen": 0.7, "wiederhole": 0.7,
    "von vorne": 0.9, "von vorn": 0.9, "neu anfangen": 0.9, "neu starten": 0.9, "starte neu": 0.9, "fang neu an": 0.9,
    "vergiss das": 0.8, "vergiss": 0.6, "ignoriere das": 0.7, "ignoriere": 0.5, "lösche das": 0.8, "streiche das": 0.7,
    "schon wieder": 0.6, "immer wieder": 0.5, "wie oft noch": 0.7, "zum x-ten mal": 0.8, "drehen uns im kreis": 0.9, "kommen nicht weiter": 0.7,
}

# Guardian/Hazard (A29) — bewusst separat
SUICIDE_MARKERS: Dict[str, float] = {
    "nicht mehr leben": 1.0, "nicht mehr leben wollen": 1.0, "sterben wollen": 1.0, "will sterben": 1.0,
    "mich umbringen": 1.0, "umbringen": 1.0, "suizid": 1.0, "selbstmord": 1.0,
    "wenn ich weg wäre": 1.0, "wenn ich nicht mehr da wäre": 1.0,
    "besser ohne mich": 1.0, "allen zur last": 0.9, "keinen ausweg": 0.9, "kein ausweg": 0.9, "ausweglos": 0.85,
    "ein ende machen": 1.0, "ende machen": 0.95, "alles beenden": 0.95, "das leben beenden": 1.0,
}

SELF_HARM: Dict[str, float] = {
    "ritzen": 1.0, "mich schneiden": 1.0, "selbstverletzung": 1.0, "mich verletzen": 0.9, "mir wehtun": 1.0,
    "mich verbrennen": 1.0,
}

CRISIS_MARKERS: Dict[str, float] = {
    "kollaps": 0.8, "zusammenbruch": 0.8, "krise": 0.6, "notfall": 0.7,
    "hoffnungslos": 0.8, "keine hoffnung": 0.9, "am ende": 0.7, "zerbreche": 0.9,
}

HELP_REQUESTS: Dict[str, float] = {
    "ich brauche hilfe": 1.0, "hilf mir": 0.9, "bitte hilf": 0.9,
    "kannst du mir helfen": 0.8, "ich weiß nicht weiter": 0.8, "es wird mir zu viel": 0.9,
    "brauche unterstützung": 0.8, "brauche jemanden": 0.8,
}

EMOTION_POSITIVE: Dict[str, float] = {
    "freude": 0.8, "glücklich": 0.9, "froh": 0.7, "begeistert": 0.9, "dankbar": 0.8,
    "erleichtert": 0.7, "zufrieden": 0.6, "stolz": 0.7, "liebe": 0.9, "geborgen": 0.8,
}

EMOTION_NEGATIVE: Dict[str, float] = {
    "traurig": 0.8, "wütend": 0.9, "ängstlich": 0.8, "frustriert": 0.8, "verzweifelt": 0.9,
    "einsam": 0.8, "hilflos": 0.9, "schuldig": 0.8, "beschämt": 0.8, "hasserfüllt": 0.9,
}

KASTASIS_INTENT: Dict[str, float] = {
    "spinn mal": 0.9, "mal spinnen": 0.9, "brainstorm": 0.8, "brainstormen": 0.8,
    "was wäre wenn": 0.7, "hypothetisch": 0.6, "stell dir vor": 0.6, "gedankenexperiment": 0.8,
    "theoretisch": 0.6, "nur so gedacht": 0.7, "ideen sammeln": 0.7, "sei kreativ": 0.8,
}

FLOW_POSITIVE: Dict[str, float] = {
    "genau": 0.8, "richtig": 0.7, "stimmt": 0.8, "ja": 0.6, "verstanden": 0.8, "klar": 0.7,
    "okay": 0.6, "gut": 0.6, "weiter": 0.7, "mehr": 0.6,
}

FLOW_NEGATIVE: Dict[str, float] = {
    "nein": 0.7, "falsch": 0.8, "stimmt nicht": 0.9, "verstehe nicht": 0.8, "unklar": 0.7, "verwirrt": 0.7,
    "stop": 0.8, "warte": 0.6, "moment": 0.5,
}

COH_CONNECTORS: Dict[str, float] = {
    "weil": 0.8, "denn": 0.7, "daher": 0.8, "deshalb": 0.8, "also": 0.7,
    "somit": 0.8, "folglich": 0.9, "jedoch": 0.7, "aber": 0.6, "trotzdem": 0.8,
    "obwohl": 0.8, "außerdem": 0.6, "zusammenfassend": 0.9, "insgesamt": 0.8, "konkret": 0.7,
}

B_EMPATHY: Dict[str, float] = {
    "verstehe dich": 1.0, "ich verstehe": 0.8, "nachvollziehen": 0.9, "kann mir vorstellen": 0.8,
    "fühle mit": 1.0, "mitgefühl": 1.0, "empathie": 1.0, "anteilnahme": 0.9,
    "fürsorge": 0.8, "unterstützen": 0.7, "beistehen": 0.8, "trösten": 0.8, "da sein für": 0.9,
    "vertrauen": 0.8, "geborgen": 0.8, "wärme": 0.7, "herzlich": 0.7,
    "gemeinsam": 0.6, "zusammen": 0.6,
}

LAMBDA_DEPTH: Dict[str, float] = {
    "warum": 0.8, "weshalb": 0.8, "wieso": 0.7, "wozu": 0.7, "wofür": 0.6,
    "grund": 0.7, "ursache": 0.8, "hintergrund": 0.6, "zusammenhang": 0.7, "kontext": 0.6,
    "fundamental": 0.8, "fundament": 0.7, "kern": 0.7, "wurzel": 0.7,
    "analyse": 0.7, "reflexion": 0.9, "nachdenken": 0.7, "überlegung": 0.6,
}

# Optional: Meta-Cluster (falls ihr es im Engine-Pfad nutzt)
MATH_META: Dict[str, float] = {
    "formel": 0.7, "gleichung": 0.7, "beweis": 0.8, "ableitung": 0.8, "integral": 0.8, "matrix": 0.7, "vektor": 0.6,
    "gradient": 0.8, "funktion": 0.6, "kurve": 0.5, "logarithmus": 0.7, "sigma": 0.5,
}
PHYSICS_META: Dict[str, float] = {
    "energie": 0.6, "impuls": 0.7, "kraft": 0.6, "feld": 0.6, "resonanz": 0.7, "chaos": 0.6,
    "dämpfung": 0.7, "oszillation": 0.8, "frequenz": 0.7, "phase": 0.6, "thermodynamik": 0.8,
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
    "Emotion_pos": EMOTION_POSITIVE,
    "Emotion_neg": EMOTION_NEGATIVE,
    "Kastasis_intent": KASTASIS_INTENT,
    "Flow_pos": FLOW_POSITIVE,
    "Flow_neg": FLOW_NEGATIVE,
    "Coh_conn": COH_CONNECTORS,
    "ZLF": ZLF_LOOP,
    "B_empathy": B_EMPATHY,
    "Math_meta": MATH_META,
    "Physics_meta": PHYSICS_META,
}

# Health Gate
REQUIRED_LEXIKA_KEYS: Tuple[str, ...] = (
    "S_self", "X_exist", "B_past",
    "T_panic", "T_disso", "T_integ", "T_shock",
    "Suicide", "Self_harm", "Crisis", "Help",
)

# Backwards/Legacy Aliases (optional; for migration)
LEXIKA_ALIASES: Dict[str, str] = {
    "S_SELF": "S_self",
    "X_EXIST": "X_exist",
    "B_PAST": "B_past",
    "T_PANIC": "T_panic",
    "T_DISSO": "T_disso",
    "T_INTEG": "T_integ",
    "T_SHOCK": "T_shock",
    "SUICIDE_MARKERS": "Suicide",
    "SELF_HARM": "Self_harm",
    "CRISIS_MARKERS": "Crisis",
    "HELP_REQUESTS": "Help",
}


# =============================================================================
# 2) REGISTRY UTILITIES (Hash/Stats/Export)
# =============================================================================

def normalize_lexika_keys(lexika: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """Applies alias mapping and returns canonical-key dict."""
    out: Dict[str, Dict[str, float]] = {}
    for k, v in lexika.items():
        canon = LEXIKA_ALIASES.get(k, k)
        out[canon] = v
    return out


def validate_lexika(lexika: Any, mode: str = "dict") -> Tuple[bool, List[str]]:
    """
    Validates lexika presence & basic structure.

    mode:
      - "dict": expects Dict[str, Dict[str, float]]
      - "tuple": accepts (ALL_LEXIKA, B_PAST_PATTERNS) style packages
    """
    errors: List[str] = []

    if mode == "tuple":
        try:
            lexika_obj = lexika[0]
        except Exception:
            return False, ["tuple-mode expects (lexika_dict, ...)"]
    else:
        lexika_obj = lexika

    if not isinstance(lexika_obj, dict):
        return False, ["lexika must be a dict"]

    canon = normalize_lexika_keys(lexika_obj)
    for req in REQUIRED_LEXIKA_KEYS:
        if req not in canon:
            errors.append(f"missing required lexikon: {req}")

    # structural sanity
    for k, d in canon.items():
        if not isinstance(d, dict):
            errors.append(f"lexikon '{k}' must be dict")
            continue
        for term, w in d.items():
            if not isinstance(term, str):
                errors.append(f"lexikon '{k}' has non-str term: {term!r}")
            try:
                wf = float(w)
            except Exception:
                errors.append(f"lexikon '{k}' term '{term}' has non-float weight: {w!r}")
                continue
            if wf < 0.0 or wf > 1.0:
                errors.append(f"lexikon '{k}' term '{term}' weight out of [0..1]: {wf}")

    return (len(errors) == 0), errors


def require_lexika_or_raise(lexika: Any, mode: str = "dict") -> None:
    ok, errors = validate_lexika(lexika, mode=mode)
    if not ok:
        raise ValueError("Lexika validation failed:\n- " + "\n- ".join(errors))


def lexika_hash(lexika: Optional[Dict[str, Dict[str, float]]] = None) -> str:
    """SHA-256 over canonical, sorted JSON representation."""
    if lexika is None:
        lexika = ALL_LEXIKA
    canon = {k: dict(sorted(v.items())) for k, v in sorted(normalize_lexika_keys(lexika).items())}
    j = json.dumps(canon, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(j.encode("utf-8")).hexdigest()


def get_lexikon_stats(lexika: Optional[Dict[str, Dict[str, float]]] = None) -> Dict[str, int]:
    if lexika is None:
        lexika = ALL_LEXIKA
    canon = normalize_lexika_keys(lexika)
    stats: Dict[str, int] = {}
    total = 0
    for name, d in canon.items():
        n = len(d)
        stats[name] = n
        total += n
    stats["TOTAL"] = total
    stats["B_past_regex"] = len(B_PAST_PATTERNS)
    return stats


def flatten_lexika_terms(lexika: Optional[Dict[str, Dict[str, float]]] = None) -> List[Tuple[str, str, float]]:
    if lexika is None:
        lexika = ALL_LEXIKA
    out: List[Tuple[str, str, float]] = []
    canon = normalize_lexika_keys(lexika)
    for cat, d in canon.items():
        for term, w in d.items():
            out.append((cat, term, float(w)))
    return out


def export_lexika_json(path: str, lexika: Optional[Dict[str, Dict[str, float]]] = None) -> str:
    if lexika is None:
        lexika = ALL_LEXIKA
    canon = {k: dict(sorted(v.items())) for k, v in sorted(normalize_lexika_keys(lexika).items())}
    payload = {
        "schema": "evoki.lexika.v3",
        "version": "3.0.0",
        "hash_sha256": lexika_hash(canon),
        "lexika": canon,
        "b_past_patterns": [p.pattern for p, _ in B_PAST_PATTERNS],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
    return path


# =============================================================================
# 3) ENGINE (Multi-Match + Longest-First + Overlap-Guard + Context-Gates)
# =============================================================================

@dataclass(frozen=True)
class LexMatch:
    term: str
    weight: float
    span: Tuple[int, int]
    category: Optional[str] = None


def _is_wordish(s: str) -> bool:
    return bool(re.fullmatch(r"[0-9A-Za-zÄÖÜäöüß]+", s))


def _compile_term_pattern(term: str) -> Pattern[str]:
    """
    Builds a regex for safe matching.
    - single token -> boundary-safe: (?<!\w)TERM(?!\w)
    - multi token -> whitespace-flexible, boundary-safe at ends
    """
    t = term.strip()
    if " " not in t and _is_wordish(t):
        return re.compile(rf"(?<!\w){re.escape(t)}(?!\w)", re.IGNORECASE)
    # multiword/phrase: collapse spaces to \s+
    parts = [re.escape(p) for p in re.split(r"\s+", t)]
    core = r"\s+".join(parts)
    return re.compile(rf"(?<!\w){core}(?!\w)", re.IGNORECASE)


# Precompiled patterns cache (canonical)
_PATTERN_CACHE: Dict[str, Pattern[str]] = {}


def _get_pat(term: str) -> Pattern[str]:
    pat = _PATTERN_CACHE.get(term)
    if pat is None:
        pat = _compile_term_pattern(term)
        _PATTERN_CACHE[term] = pat
    return pat


# Context gates for ambiguous terms (minimal; extend as needed)
_CONTEXT_GATES = {
    # term: (boost_tokens, damp_tokens, base_weight)
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
    """
    Returns:
      (score_0_1, matched_terms_unique, matches_detailed)
    """
    if not text or not lexicon:
        return 0.0, [], []

    text_lower = text.lower()
    # token count
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
            eff_w = base_w
            if category is not None:
                eff_w = _effective_weight(category, term, base_w, text_lower)
            detailed.append(LexMatch(term=term, weight=eff_w, span=(a, b), category=category))
            total_weight += eff_w
            if term not in matched_set:
                matched_set.add(term)
                matched_unique.append(term)

    if total_weight <= 0.0:
        return 0.0, [], []

    # Stable normalizer (V2.1-style)
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
    """
    Combines Suicide/Self_harm/Crisis into one hazard score.
    is_critical is True if suicide score is very high or explicit markers found.
    """
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

    # explicit critical override
    tl = text.lower()
    if any(t in tl for t in ("suizid", "selbstmord", "mich umbringen", "sterben wollen")):
        is_critical = True
        max_score = max(max_score, 0.95)

    return float(min(1.0, max_score)), bool(is_critical), all_matches


# =============================================================================
# 4) DRIFT SCAN (Workspace/Repo) — find mixed versions by signature
# =============================================================================

_VERSION_SIGNATURES = [
    ("v1_config", re.compile(r"class\s+Thresholds\b|EVOKI\s+LEXIKA\s+&\s+METRIKEN\s+KONFIGURATION\s+V1\.0", re.IGNORECASE)),
    ("v2_1_legacy", re.compile(r"EVOKI\s+GERMAN\s+LEXICON\s+SET\s+V2\.1", re.IGNORECASE)),
    ("v2_2_full", re.compile(r"EVOKI\s+VOLLSTÄNDIGE\s+LEXIKA\s+V2\.2", re.IGNORECASE)),
    ("v3_monolith", re.compile(r"EVOKI\s+LEXIKA\s+V3\.0\s+\(MONOLITH\)", re.IGNORECASE)),
]


def scan_lexika_versions(root: str, *, exts: Tuple[str, ...] = (".py", ".txt", ".md")) -> Dict[str, int]:
    """
    Scans files under root and counts signature matches.
    Returns dict version->count.
    """
    counts = {name: 0 for name, _ in _VERSION_SIGNATURES}
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if not fn.lower().endswith(exts):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    s = f.read(200_000)
            except Exception:
                continue
            for name, pat in _VERSION_SIGNATURES:
                if pat.search(s):
                    counts[name] += 1
                    break
    return counts


# =============================================================================
# 5) CLI / SELF-TEST
# =============================================================================

def _selftest() -> int:
    require_lexika_or_raise(ALL_LEXIKA)

    print("=" * 72)
    print("EVOKI LEXIKA V3.0 — SELFTEST")
    print("=" * 72)
    stats = get_lexikon_stats()
    for k in sorted(stats):
        print(f"{k:<18} : {stats[k]:>5}")
    print("-" * 72)
    print("HASH_SHA256:", lexika_hash())
    print("=" * 72)

    tests = [
        "Ich fühle mich so leer und wertlos, als ob niemand merken würde wenn ich weg wäre.",
        "Als Kind hatte ich oft Angst vor meinem Vater.",
        "Ich habe Herzrasen und kann nicht atmen, alles zu viel, Hilfe!",
        "Es wird ruhiger, ich kann wieder atmen und fühle mich geerdet.",
        "Warum ist das so? Was ist der Grund dafür?",
    ]

    for t in tests:
        s_self, _, _ = compute_lexicon_score(t, S_SELF, category="S_self")
        x_exist, _, _ = compute_lexicon_score(t, X_EXIST, category="X_exist")
        b_past, bm = compute_b_past_with_regex(t)
        t_panic, _, _ = compute_lexicon_score(t, T_PANIC, category="T_panic")
        t_integ, _, _ = compute_lexicon_score(t, T_INTEG, category="T_integ")
        hazard, crit, _ = compute_hazard_score(t)
        lam, _, _ = compute_lexicon_score(t, LAMBDA_DEPTH, category="Lambda_depth")
        print(f"\nTEXT: {t[:80]}{'...' if len(t) > 80 else ''}")
        print(f"  S_self={s_self:.3f}  X_exist={x_exist:.3f}  B_past={b_past:.3f}  Lambda={lam:.3f}")
        print(f"  T_panic={t_panic:.3f}  T_integ={t_integ:.3f}  Hazard={hazard:.3f}  Critical={crit}")
        if bm:
            print(f"  B_past_matches={bm[:4]}{'...' if len(bm) > 4 else ''}")

    print("\nOK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
