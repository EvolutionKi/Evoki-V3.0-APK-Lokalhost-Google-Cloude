"""a_phys_v11.py — EVOKI A_Phys (PhysicsEngine V11) — kanonische Implementierung

Ziel
----
Dieses Modul implementiert den *kanonischen* V11-Kern der Evoki-Physik:
- Affekt-Score A(v_c) = LAMBDA_R * Resonanz - LAMBDA_D * Gefahr
- A29 Wächter-Veto (Trauma-Ähnlichkeitsschwelle)
- Telemetrie: Resonanz, Gefahr, max. Trauma-Sim, Top-Beiträge

Quelle / Referenz
-----------------
- GENESIS_PhysicsEngine_V11_MONOLITH.txt (V11-Referenz, unverändert)
- EVOKI_V3_METRICS_SPECIFICATION.md (Physics Engine Abschnitt)

Hinweis
-------
Dieses Modul ist bewusst *deterministisch* gebaut (Hash-Embedding-Fallback),
damit OFFLINE/ONLINE reproduzierbar bleibt. In LIVE sollte bevorzugt ein
semantischer Vektor (Embedding) genutzt werden.

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union
import hashlib
import math

import numpy as np


Vector = Union[np.ndarray, Sequence[float]]


def _to_vec(v: Optional[Vector]) -> Optional[np.ndarray]:
    if v is None:
        return None
    arr = np.asarray(v, dtype=np.float32)
    if arr.ndim != 1:
        arr = arr.reshape(-1).astype(np.float32)
    if not np.isfinite(arr).all():
        return None
    # normalize (robust)
    n = float(np.linalg.norm(arr))
    if n <= 1e-12:
        return None
    return arr / n


def cosine_similarity(a: Vector, b: Vector) -> float:
    va = _to_vec(a)
    vb = _to_vec(b)
    if va is None or vb is None:
        return 0.0
    return float(np.dot(va, vb))


def sigmoid(x: float) -> float:
    # numerisch stabil
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def vectorize_hash(text: str, dim: int = 256) -> np.ndarray:
    """Deterministische Hash-Vektorisierung (Fallback).

    - erzeugt einen normalisierten Vektor aus dem Text
    - deterministisch: gleicher Text -> gleicher Vektor (über SHA256-Seed)

    """
    if text is None:
        text = ""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(digest[:8], "little", signed=False)
    rng = np.random.default_rng(seed)
    v = rng.normal(loc=0.0, scale=1.0, size=dim).astype(np.float32)
    n = float(np.linalg.norm(v))
    if n <= 1e-12:
        return v
    return v / n


@dataclass(frozen=True)
class APhysParams:
    """V11-Parameter (Defaults aus GENESIS_PhysicsEngine_V11_MONOLITH).

    Hinweis: In manchen früheren Textständen taucht A29_DANGER_THRESHOLD=0.35 auf;
    der kanonische Monolith setzt 0.85 (bereitgestellt durch RuleEngine).
    """
    LAMBDA_R: float = 1.0
    LAMBDA_D: float = 1.5
    K_FACTOR: float = 5.0
    A29_DANGER_THRESHOLD: float = 0.85

    # Output-Form: raw -> display
    USE_SIGMOID: bool = True


class APhysV11:
    """Kanonische V11-A_Phys Berechnung."""

    def __init__(self, params: Optional[APhysParams] = None, vector_service: Any = None):
        self.params = params or APhysParams()
        # optional: externer Service mit cosine_similarity(a,b)
        self.vector_service = vector_service

    def _cos(self, a: Vector, b: Vector) -> float:
        if self.vector_service is not None and hasattr(self.vector_service, "cosine_similarity"):
            try:
                return float(self.vector_service.cosine_similarity(a, b))
            except Exception:
                pass
        return cosine_similarity(a, b)

    def compute_resonance(
        self,
        v_c: Vector,
        active_memories: Sequence[Dict[str, Any]],
        vec_key: str = "vector_semantic",
        weight_key: str = "resonanzwert",
    ) -> Tuple[float, List[Tuple[str, float, float]]]:
        """Resonanz = Σ_i max(0, cos(v_c, v_i)) * r_i"""
        res = 0.0
        contrib: List[Tuple[str, float, float]] = []  # (id, sim, weighted)
        for i, mem in enumerate(active_memories or []):
            if not isinstance(mem, dict):
                continue
            v_i = mem.get(vec_key, None)
            if v_i is None:
                v_i = mem.get("vector_hash", None)
            if v_i is None:
                v_i = mem.get("vector", None)
            sim = self._cos(v_c, v_i)
            sim_pos = sim if sim > 0.0 else 0.0
            r_i = float(mem.get(weight_key, 1.0) or 1.0)
            w = sim_pos * r_i
            res += w
            mid = str(mem.get("id", mem.get("key", i)))
            contrib.append((mid, sim, w))
        # sort by weighted contribution desc
        contrib.sort(key=lambda t: t[2], reverse=True)
        return res, contrib

    def compute_danger(
        self,
        v_c: Vector,
        danger_zone_cache: Sequence[Tuple[str, Vector]],
    ) -> Tuple[float, float, Optional[str]]:
        """Gefahr = Σ exp(-K_FACTOR * d), d = max(0, 1 - cos(v_c, v_f))"""
        K = float(self.params.K_FACTOR)
        danger = 0.0
        max_sim = -1.0
        max_id: Optional[str] = None

        for item in danger_zone_cache or []:
            try:
                mem_id, v_f = item
            except Exception:
                continue
            sim = self._cos(v_c, v_f)
            if sim > max_sim:
                max_sim = sim
                max_id = str(mem_id)
            d = 1.0 - sim
            if d < 0.0:
                d = 0.0
            danger += math.exp(-K * d)

        if max_sim < -1.0:
            max_sim = -1.0
        return danger, max_sim, max_id

    def check_a29_veto(self, v_c: Vector, danger_zone_cache: Sequence[Tuple[str, Vector]]) -> Tuple[bool, float, Optional[str]]:
        """A29 Wächter-Veto: ∃ v_f: cos(v_c, v_f) > threshold"""
        _, max_sim, max_id = self.compute_danger(v_c, danger_zone_cache)
        trip = bool(max_sim > float(self.params.A29_DANGER_THRESHOLD))
        return trip, max_sim, max_id

    def compute_affekt(
        self,
        *,
        v_c: Optional[Vector] = None,
        text: Optional[str] = None,
        active_memories: Optional[Sequence[Dict[str, Any]]] = None,
        danger_zone_cache: Optional[Sequence[Tuple[str, Vector]]] = None,
        vec_key: str = "vector_semantic",
        weight_key: str = "resonanzwert",
    ) -> Dict[str, Any]:
        """Berechnet A_Phys und Telemetrie.

        Inputs:
        - v_c: Kandidaten-/Antwortvektor (Embedding). Wenn None -> Hash-Fallback aus text.
        - active_memories: Kontext-Erinnerungen mit Vektor + Resonanzgewicht
        - danger_zone_cache: Liste[(id, v_f)] nur F-Einträge (Trauma)

        Output:
        - A_phys_raw, A_phys (optional sigmoid), resonance, danger, a29_trip, a29_max_sim, a29_id
        - top_resonance: Top 5 Beiträge
        """
        if v_c is None:
            v_c = vectorize_hash(text or "")

        params = self.params
        resonance, contrib = self.compute_resonance(v_c, active_memories or [], vec_key=vec_key, weight_key=weight_key)
        danger, max_sim, max_id = self.compute_danger(v_c, danger_zone_cache or [])

        raw = float(params.LAMBDA_R) * resonance - float(params.LAMBDA_D) * danger
        a_display = sigmoid(raw) if params.USE_SIGMOID else raw

        a29_trip = bool(max_sim > float(params.A29_DANGER_THRESHOLD))

        return {
            "A_phys": float(a_display),
            "A_phys_raw": float(raw),
            "resonance": float(resonance),
            "danger": float(danger),
            "a29_trip": a29_trip,
            "a29_max_sim": float(max_sim),
            "a29_id": max_id,
            "top_resonance": contrib[:5],
        }
