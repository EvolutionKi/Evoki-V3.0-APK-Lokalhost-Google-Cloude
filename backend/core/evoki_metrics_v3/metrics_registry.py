# -*- coding: utf-8 -*-
"""
metrics_registry.py — EVOKI Metrics Registry (Spec ↔ Engine Alias-Layer)

Audit-Ziel
----------
Dieses Modul verhindert, dass Metriken *falsch gelabelt* werden, wenn
Spezifikation und Engine unterschiedliche Slot-Namen geführt haben.

Grundprinzip:
- Canonical Key = Feldname in FullSpectrum168 (Storage-Contract)
- Aliases = Spezifikationsnamen / historische Namen / Kurzformen

Wichtig:
- Für bekannte "Semantic Override" Slots wird Alias-Export *absichtlich* auf canonical gezwungen,
  um gefährliche Fehlbezeichnungen auszuschließen (Audit-Härtung).
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

import re


# ---------------------------------------------------------------------------
# Registry Types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MetricDef:
    metric_id: int
    canonical: str
    aliases: Tuple[str, ...] = ()


class MetricsRegistry:
    """
    Registry zur Canonicalisierung von Metric-Keys.
    """

    def __init__(self, defs: Iterable[MetricDef], *, semantic_overrides: Optional[Dict[str, str]] = None):
        self._defs: Dict[int, MetricDef] = {d.metric_id: d for d in defs}
        self._alias_to_canonical: Dict[str, str] = {}
        self._canonical_to_id: Dict[str, int] = {}
        self._semantic_overrides = dict(semantic_overrides or {})

        for d in defs:
            self._canonical_to_id[d.canonical] = d.metric_id
            for a in (d.canonical, *d.aliases):
                if not a:
                    continue
                self._alias_to_canonical[self._norm(a)] = d.canonical

        # Add semantic overrides as hard alias mappings
        for alias, canonical in self._semantic_overrides.items():
            if alias and canonical:
                self._alias_to_canonical[self._norm(alias)] = canonical

    @staticmethod
    def _norm(key: str) -> str:
        return re.sub(r"[\s\-\(\)\[\]]+", "", str(key).strip().lower())

    def canonical_key(self, key_or_alias: Union[str, int]) -> Optional[str]:
        """
        Resolve alias/metric-id to canonical key (FullSpectrum168 field).
        """
        if key_or_alias is None:
            return None
        if isinstance(key_or_alias, int):
            d = self._defs.get(int(key_or_alias))
            return d.canonical if d else None
        k = str(key_or_alias)
        # direct
        if k in self._canonical_to_id:
            return k
        # alias
        return self._alias_to_canonical.get(self._norm(k))

    def metric_id(self, key_or_alias: str) -> Optional[int]:
        ck = self.canonical_key(key_or_alias)
        if ck is None:
            return None
        return self._canonical_to_id.get(ck)

    def spec_primary_for(self, metric_id: int) -> str:
        """
        Liefert den *primären* Export-Key für Spec.

        Audit-Härtung:
        - bei semantisch kritischen Slots wird canonical zurückgegeben, nicht der historische Alias.
        """
        d = self._defs.get(int(metric_id))
        if not d:
            return f"m{metric_id}"
        # if this metric has a semantic override (i.e., dangerous alias exists), we keep canonical
        inv = {v: k for k, v in self._semantic_overrides.items()}
        if d.canonical in inv:
            return d.canonical
        # otherwise: prefer first alias if provided
        return d.aliases[0] if d.aliases else d.canonical

    def list_missing(self, keys: Iterable[str]) -> List[str]:
        missing = []
        for k in keys:
            if self.canonical_key(k) is None:
                missing.append(str(k))
        return missing


# ---------------------------------------------------------------------------
# Factory from FullSpectrum168
# ---------------------------------------------------------------------------

def _parse_metric_id(field_name: str) -> Optional[int]:
    """
    Extract mNN from dataclass field names like 'm12_gap_norm'.
    """
    m = re.match(r"^m(\d+)_", field_name)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def build_registry_from_fullspectrum(FullSpectrum168_type: object) -> MetricsRegistry:
    if not is_dataclass(FullSpectrum168_type):
        raise TypeError("FullSpectrum168_type muss eine dataclass sein")

    defs: List[MetricDef] = []
    for f in fields(FullSpectrum168_type):
        mid = _parse_metric_id(f.name)
        if mid is None:
            continue
        # Default aliases: id-only + shorthand
        aliases: Set[str] = set()
        aliases.add(f"m{mid}")
        aliases.add(f.name)
        # common shorthands
        if f.name.endswith("_A"):
            aliases.add("A")
        if "PCI" in f.name:
            aliases.add("PCI")
        if f.name.endswith("_LL"):
            aliases.add("LL")
        if f.name.endswith("_ZLF"):
            aliases.add("ZLF")
        defs.append(MetricDef(metric_id=mid, canonical=f.name, aliases=tuple(sorted(aliases))))

    # Known dangerous historical/spec aliases (SEMANTIC OVERRIDES)
    # These aliases must NEVER be exported as if they were other semantics.
    semantic_overrides = {
        # Spec legacy naming collisions:
        "m12_lex_hit": "m12_gap_norm",
        "m13_lex_div": "m13_rep_same",
        "m14_lex_depth": "m14_rep_history",
        "m16_lex_const": "m16_external_stag",
        # convenience
        "gap_norm": "m12_gap_norm",
        "rep_same": "m13_rep_same",
        "rep_history": "m14_rep_history",
        "external_stag": "m16_external_stag",
    }

    return MetricsRegistry(defs, semantic_overrides=semantic_overrides)


def get_default_registry() -> MetricsRegistry:
    """
    Default registry based on local `spectrum_types.FullSpectrum168`.
    """
    try:
        from spectrum_types import FullSpectrum168  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise ImportError("Konnte spectrum_types.FullSpectrum168 nicht importieren") from exc

    return build_registry_from_fullspectrum(FullSpectrum168)
