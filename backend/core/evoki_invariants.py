# -*- coding: utf-8 -*-
"""
evoki_invariants.py — FullSpectrum168 Contract & Invariant Checks

Ziel
----
Dieses Modul bringt das "Contract-first" Prinzip in ausführbare Form:

1) CONTRACT: Eine maschinenlesbare Abbildung der 168 Slots
   (Spec-ID(s), Kategorie, Range, Source, Version) ↔ Engine-Key (Storage).
2) INVARIANTS: Tests, die *immer* gelten müssen:
   - Keys vorhanden
   - Werte endlich (keine NaN/Inf) für numerische Slots
   - Werte im Range (sofern Range maschinell interpretierbar)
   - Typ ↔ Range (z.B. Enum/hex vs float) nicht widersprüchlich

Wichtig
-------
- Dieses Modul ist absichtlich "low dependency" (Standardlib + optional numpy).
- Es ist dafür gedacht, im Bootcheck/CI zu laufen.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import math
import re

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore


# ---------------------------------------------------------------------------
# Range Parsing
# ---------------------------------------------------------------------------

_NUM_INTERVAL = re.compile(r"^\[\s*([^\],]+)\s*,\s*([^\]]+)\s*\]\s*$")
_ENUM = re.compile(r"^Enum:\s*\{(.+)\}\s*$", re.IGNORECASE)
_HEX = re.compile(r"hex\[(\d+)\]", re.IGNORECASE)


def _parse_float_token(tok: str) -> Optional[float]:
    """Parse tokens like '0.0', '∞', '+∞', '-∞', '~6.0', '5.0+'."""
    t = tok.strip().replace("~", "").replace("+", "")
    if not t:
        return None
    tl = t.lower()
    if "inf" in tl or "∞" in tl:
        return math.inf if not tl.startswith("-") else -math.inf
    try:
        return float(t)
    except Exception:
        return None


def parse_range(range_str: str) -> Dict[str, Any]:
    """
    Convert Spec range strings into machine-readable rules.

    Supported:
    - Numeric interval: [0.0, 1.0], [-1, 1], [0, ∞]
    - Enum: Enum: {"pc", "apk", "rover"}
    - Hex length: hex[64]
    - Binary set hints like "{0.0, 1.0} (binär)" (treated as [0,1])

    Returns dict with keys:
      kind: 'numeric'|'enum'|'hex'|'unknown'
    """
    s = (range_str or "").strip()
    if not s:
        return {"kind": "unknown"}

    # Normalize some common variants
    # "{0.0, 1.0} (binär)" -> treat as [0,1]
    if "binär" in s.lower() and "0" in s and "1" in s:
        return {"kind": "numeric", "lo": 0.0, "hi": 1.0, "raw": s}

    m = _ENUM.match(s)
    if m:
        raw_items = m.group(1)
        # split by comma, strip quotes/spaces
        items = []
        for part in raw_items.split(","):
            p = part.strip()
            p = p.strip('"').strip("'")
            if p:
                items.append(p)
        return {"kind": "enum", "values": sorted(set(items)), "raw": s}

    m = _HEX.search(s)
    if m:
        return {"kind": "hex", "len": int(m.group(1)), "raw": s}

    m = _NUM_INTERVAL.match(s)
    if m:
        lo = _parse_float_token(m.group(1))
        hi = _parse_float_token(m.group(2))
        if lo is None or hi is None:
            return {"kind": "unknown", "raw": s}
        return {"kind": "numeric", "lo": lo, "hi": hi, "raw": s}

    # Some lines contain two ranges e.g. "[-π, π] / [0.0, 1.0]" -> unknown (needs schema choice)
    return {"kind": "unknown", "raw": s}


# ---------------------------------------------------------------------------
# Contract Loading
# ---------------------------------------------------------------------------

def load_contract(contract_path: Union[str, Path]) -> Dict[str, Any]:
    p = Path(contract_path)
    return json.loads(p.read_text(encoding="utf-8"))


def contract_items(contract: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = contract.get("items", [])
    if not isinstance(items, list):
        raise TypeError("contract['items'] must be a list")
    return items


# ---------------------------------------------------------------------------
# Engine introspection
# ---------------------------------------------------------------------------

def dataclass_metric_fields(dc_type: Any) -> Dict[int, Tuple[str, str]]:
    """
    Return mapping metric_id -> (engine_key, engine_type_name)
    """
    if not is_dataclass(dc_type):
        raise TypeError("dc_type must be dataclass")
    out: Dict[int, Tuple[str, str]] = {}
    for f in fields(dc_type):
        m = re.match(r"^m(\d+)_", f.name)
        if not m:
            continue
        mid = int(m.group(1))
        out[mid] = (f.name, str(f.type))
    return out


# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------

def _is_finite_number(x: Any) -> bool:
    try:
        if x is None:
            return False
        if isinstance(x, bool):
            return True
        if isinstance(x, (int, float)):
            if isinstance(x, float):
                return math.isfinite(x)
            return True
        if np is not None and isinstance(x, (np.floating, np.integer)):  # type: ignore
            return bool(np.isfinite(x))  # type: ignore
        return False
    except Exception:
        return False


def validate_metrics_dict(metrics: Dict[str, Any], contract: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Validate a metrics dict against contract rules.

    - Presence: each engine_key must exist
    - Numeric: finite + range if parseable
    - Enum: string in allowed values
    - Hex: string of expected hex length

    Returns list of violation dicts.
    """
    violations: List[Dict[str, Any]] = []
    items = contract_items(contract)

    for it in items:
        ek = it.get("engine_key") or ""
        mid = it.get("metric_id")
        if not ek:
            violations.append({"metric_id": mid, "rule": "engine_key_present", "ok": False, "msg": "missing engine_key in contract item"})
            continue

        if ek not in metrics:
            violations.append({"metric_id": mid, "engine_key": ek, "rule": "present", "ok": False, "msg": "missing key in metrics output"})
            continue

        val = metrics.get(ek)
        # Determine a range string.
        # Contract-first rule:
        # - If range_effective is present in the contract, we respect it (even if empty => 'unknown').
        # - Otherwise we fall back to default/schema A/schema B.
        if "range_effective" in it:
            rstr = (it.get("range_effective") or "")
        else:
            rstr = (it.get("range_default") or it.get("range_schema_a") or it.get("range_schema_b") or "")
        rr = parse_range(rstr)

        if rr["kind"] == "numeric":
            if not _is_finite_number(val):
                violations.append({"metric_id": mid, "engine_key": ek, "rule": "finite", "ok": False, "msg": f"expected finite numeric, got {type(val).__name__}: {val}"})
                continue
            fval = float(val)
            lo, hi = float(rr["lo"]), float(rr["hi"])
            if fval < lo - 1e-12 or fval > hi + 1e-12:
                violations.append({"metric_id": mid, "engine_key": ek, "rule": "range", "ok": False, "msg": f"value {fval} out of range [{lo}, {hi}] ({rstr})"})
        elif rr["kind"] == "enum":
            if not isinstance(val, str):
                violations.append({"metric_id": mid, "engine_key": ek, "rule": "enum_type", "ok": False, "msg": f"expected str enum, got {type(val).__name__}"})
                continue
            if val not in rr["values"]:
                violations.append({"metric_id": mid, "engine_key": ek, "rule": "enum_values", "ok": False, "msg": f"value '{val}' not in {rr['values']}"})
        elif rr["kind"] == "hex":
            if not isinstance(val, str):
                violations.append({"metric_id": mid, "engine_key": ek, "rule": "hex_type", "ok": False, "msg": f"expected hex string, got {type(val).__name__}"})
                continue
            exp_len = int(rr["len"])
            # hex[64] in spec means 64 hex chars, not bytes
            if len(val) != exp_len:
                violations.append({"metric_id": mid, "engine_key": ek, "rule": "hex_len", "ok": False, "msg": f"expected len {exp_len}, got {len(val)}"})
            if not re.fullmatch(r"[0-9a-fA-F]+", val or ""):
                violations.append({"metric_id": mid, "engine_key": ek, "rule": "hex_chars", "ok": False, "msg": "string is not hex"})
        else:
            # unknown ranges: only do finiteness check for floats/ints
            if isinstance(val, float) and not math.isfinite(val):
                violations.append({"metric_id": mid, "engine_key": ek, "rule": "finite", "ok": False, "msg": "float is NaN/Inf"})

    return violations


def validate_contract_vs_engine(contract: Dict[str, Any], dc_type: Any) -> List[Dict[str, Any]]:
    """
    Check that the contract itself is compatible with the engine dataclass.

    - Metric IDs 1..168 present
    - engine_key exists on dataclass for each item
    - Basic type ↔ range sanity (numeric ranges should map to float/int; enum/hex to str)
    """
    violations: List[Dict[str, Any]] = []
    items = contract_items(contract)
    by_id = {int(it.get("metric_id")): it for it in items if it.get("metric_id") is not None}

    # id coverage
    expected_ids = set(range(1, 169))
    present_ids = set(by_id.keys())
    missing = sorted(list(expected_ids - present_ids))
    extra = sorted(list(present_ids - expected_ids))
    if missing:
        violations.append({"rule": "id_coverage", "ok": False, "msg": f"missing metric_ids: {missing[:10]}{'...' if len(missing)>10 else ''}"})
    if extra:
        violations.append({"rule": "id_coverage_extra", "ok": False, "msg": f"unexpected metric_ids: {extra[:10]}{'...' if len(extra)>10 else ''}"})

    # dataclass fields
    dc_map = dataclass_metric_fields(dc_type)

    for mid, it in by_id.items():
        ek = it.get("engine_key") or ""
        if mid not in dc_map:
            violations.append({"metric_id": mid, "rule": "engine_field_missing", "ok": False, "msg": "metric id not found in dataclass"})
            continue
        dc_key, dc_type_str = dc_map[mid]
        if ek and dc_key != ek:
            # contract expects different engine key than dataclass — fatal
            violations.append({"metric_id": mid, "rule": "engine_key_mismatch", "ok": False, "msg": f"contract engine_key='{ek}' != dataclass='{dc_key}'"})
        # type-range sanity
        if "range_effective" in it:
            rstr = (it.get("range_effective") or "")
        else:
            rstr = (it.get("range_default") or it.get("range_schema_a") or it.get("range_schema_b") or "")
        rr = parse_range(rstr)
        # simplify dc type
        dc_simple = dc_type_str.replace("<class '", "").replace("'>", "")
        if rr["kind"] == "numeric":
            if ("float" not in dc_simple) and ("int" not in dc_simple) and ("bool" not in dc_simple):
                violations.append({"metric_id": mid, "rule": "type_range", "ok": False, "msg": f"numeric range but dataclass type {dc_simple}"})
        elif rr["kind"] in ("enum", "hex"):
            if "str" not in dc_simple:
                violations.append({"metric_id": mid, "rule": "type_range", "ok": False, "msg": f"{rr['kind']} range but dataclass type {dc_simple}"})

    return violations


# ---------------------------------------------------------------------------
# Runner helper
# ---------------------------------------------------------------------------

def run_contract_invariants(
    *,
    contract_path: Union[str, Path],
    dc_type: Any,
    metrics_sample: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run both contract-vs-engine checks and (optionally) metrics-vs-contract checks.

    Returns JSON-serializable report.
    """
    contract = load_contract(contract_path)

    v_contract = validate_contract_vs_engine(contract, dc_type)
    v_metrics: List[Dict[str, Any]] = []
    if metrics_sample is not None:
        v_metrics = validate_metrics_dict(metrics_sample, contract)

    ok = (len(v_contract) == 0) and (len(v_metrics) == 0)
    return {
        "ok": ok,
        "contract_path": str(contract_path),
        "violations_contract": v_contract,
        "violations_metrics": v_metrics,
        "counts": {"contract": len(v_contract), "metrics": len(v_metrics)},
    }
