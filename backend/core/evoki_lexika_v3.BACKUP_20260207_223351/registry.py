# -*- coding: utf-8 -*-
"""
EVOKI Lexika V3 — Registry
Single source of truth: ALL_LEXIKA + aliases + hashing/export helpers.
"""
from __future__ import annotations
import hashlib, json
from typing import Dict, List, Tuple, Any, Optional

from .lexika_data import (
    ALL_LEXIKA,
    B_PAST_PATTERNS,
    REQUIRED_LEXIKA_KEYS,
    LEXIKA_ALIASES,
)

def normalize_lexika_keys(lexika: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    for k, v in lexika.items():
        out[LEXIKA_ALIASES.get(k, k)] = v
    return out

def validate_lexika(lexika: Any, mode: str = "dict") -> Tuple[bool, List[str]]:
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
        stats[name] = len(d)
        total += len(d)
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
