#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVOKI Vector Engine V2.1 - Hybrid Edition
Synthese der besten Elemente aus allen analysierten Implementierungen:

Architektur: Dependency Injection (embedding_fn injizierbar)
A-Score: Differenz-basiert (mean_A - max_F) mit Sigmoid-Squashing + optional Softmax-Fokus
Volatilität: Sigmoid-geclampte Standardabweichung [0,1]
Retrieval: Vollständiges Tri-Anchor (Hash + Semantik + Tags) gemäß A63
Affekt: Automatische Historie aus A-Score + expliziter Override
Statusfenster: Formatierte Ausgabe gemäß A61 inkl. Risk_z, B-Angle, Complexity, Pending A62
SeelenSignatur: HMAC-SHA256-Kette gemäß A51 (prev_sig|content)
FREEZE/MELT/BOOST/TRAUMA: Vollständig gemäß A46

Implementierte Regeln:
A29: Wächter-Veto-Direktive (F-Risk Check)
A46: FREEZE/MELT/BOOST/TRAUMA für Gedächtniseinträge
A49: Personalisierter Rettungsanker (via H3.4)
A50/A50.1: Universeller Lerneffekt & Vektorielle Empathie (B-Vektor)
A51: Genesis-Anker / SeelenSignatur (HMAC-SHA256, verkettet)
A54: Complexity-Score gegen Verflachung
A62: Autonome Vektor-Synthese (Novelty Detection mit Pending Actions)
A63: Hybrider Abruf (Hash + Semantik + Tags)
A65: Trajektorien-Analyse (A-Score für Kandidaten)
A66: Emotionale Homöostase (Volatilität)
A67: Historische Kausalitäts-Analyse
H3.4: Affekt-Modulation im Retrieval
Autor: EVOKI-System (Hybrid Synthesis)
Version: 2.1
Datum: 2025-12-09
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import math
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Literal, Optional, Sequence, Set, Tuple, Union

import numpy as np

try:
    from .b_vector import BVector
except ImportError:
    from b_vector import BVector

# =============================================================================
# LOGGING
# =============================================================================
logger = logging.getLogger("EVOKI.VectorEngine")


def setup_logging(level: int = logging.INFO) -> None:
    """Konfiguriert Logging für die VectorEngine."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
    logger.setLevel(level)


def _setup_logger() -> None:
    setup_logging()


_setup_logger()


# =============================================================================
# CONFIGURATION
# =============================================================================
@dataclass
class VectorEngineConfig:
    """
    Zentrale Konfiguration für VectorEngine V2.1.

    Alle Schwellenwerte (τ), Gewichte und Lernraten sind hier definiert,
    um einfache Anpassung ohne Code-Änderung zu ermöglichen.
    """

    # Dimensionen
    embedding_dim: int = 768
    hash_vector_dim: int = 64

    # Schwellenwerte (τ)
    tau_f_risk: float = 0.70
    tau_novelty: float = 0.35
    tau_volatility: float = 0.50
    tau_crisis_affekt: float = -0.3
    tau_complexity: float = 0.3

    # Lernraten B-Vektor (A50.1)
    alpha_positive: float = 0.10
    beta_negative: float = 0.08

    # Retrieval-Gewichte (A63 + H3.4)
    w_semantic: float = 0.50
    w_hash: float = 0.20
    w_tag: float = 0.15
    w_affekt: float = 0.15

    # Affekt-Modulation (H3.4)
    kappa_crisis_boost: float = 0.25
    affekt_penalty_f: float = 0.10

    # Fenstergrößen
    volatility_window: int = 10
    history_max_len: int = 100
    causal_search_window: int = 5

    # Sigmoid-Skalierung
    sigmoid_scale_a: float = 3.0
    sigmoid_scale_vol: float = 5.0

    # A-Score Gewichtung (Softmax über A-Vektoren)
    use_softmax_a_score: bool = True
    a_score_softmax_temperature: float = 0.5

    # Risk_z Gewichtung (Monitoring-Proxy)
    risk_z_w_f: float = 0.5
    risk_z_w_vol: float = 0.3
    risk_z_w_aff: float = 0.2

    # Retrieval
    default_top_k: int = 5
    max_knn: int = 64

    # Complexity (A54)
    lambda_len: float = 0.5
    lambda_dist: float = 0.5
    lambda_complexity: float = 0.0  # 0.0 => aus

    # Chat-History Decay (A67)
    history_decay_factor: float = 0.95


# =============================================================================
# ENUMS
# =============================================================================
class VectorKind(str, Enum):
    """
    Typen von Gedächtnisvektoren.

    A: Positive Ressourcen, gute Erfahrungen, hilfreiche Antworten
    F: Trauma-Vektoren, Fehler, Risiken
    C: Stabile neutrale Anker (Homöostase)
    G: Generisches Wissen
    RULE: Regelwerk-Einträge
    STATUS: Statusfenster/Protokolle
    SYSTEM: Systemkonfiguration
    """

    A = "A"
    F = "F"
    C = "C"
    G = "G"
    RULE = "RULE"
    STATUS = "STATUS"
    SYSTEM = "SYSTEM"


class FeedbackType(str, Enum):
    """Feedback-Typen für B-Vektor-Update."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# =============================================================================
# DATACLASSES
# =============================================================================
@dataclass
class MemoryEntry:
    """
    Einzelner Eintrag im Vektor-Gedächtnis.

    Kombiniert Hash-Vektor (A63), Embedding-Vektor und Metadaten
    für vollständiges Tri-Anchor-Retrieval.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    text: str = ""
    kind: VectorKind = VectorKind.G
    emb_vec: Optional[np.ndarray] = None
    hash_vec: Optional[np.ndarray] = None
    valence: float = 0.0
    arousal: float = 0.5
    weight: float = 1.0
    frozen: bool = False
    tags: Set[str] = field(default_factory=set)
    meta: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validierung und Normalisierung nach Initialisierung."""
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(0.0, min(1.0, self.arousal))
        self.weight = max(0.0, self.weight)
        if isinstance(self.tags, list):
            self.tags = set(self.tags)

        if self.emb_vec is not None:
            if not isinstance(self.emb_vec, np.ndarray):
                self.emb_vec = np.asarray(self.emb_vec, dtype=np.float32)
            norm = np.linalg.norm(self.emb_vec)
            if norm > 0:
                self.emb_vec = self.emb_vec / norm

    @property
    def is_positive(self) -> bool:
        return self.valence > 0

    @property
    def is_negative(self) -> bool:
        return self.valence < 0

    @property
    def affect_label(self) -> Optional[str]:
        """Kompatibilität mit Doc 8 API."""
        return self.kind.value

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert den Eintrag."""
        return {
            "id": self.id,
            "text": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "kind": self.kind.value,
            "valence": round(self.valence, 3),
            "arousal": round(self.arousal, 3),
            "weight": round(self.weight, 3),
            "frozen": self.frozen,
            "tags": list(self.tags),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class InteractionRecord:
    """
    Aufzeichnung einer Interaktion für A66/A67.

    Speichert sowohl berechnete Metriken als auch
    optionalen expliziten Affekt-Override.
    """

    id: int
    timestamp: datetime
    user_text: str
    response_text: str = ""
    user_emb: Optional[np.ndarray] = None
    response_emb: Optional[np.ndarray] = None
    a_score: float = 0.5
    affekt_override: Optional[float] = None
    metrics: Dict[str, float] = field(default_factory=dict)

    @property
    def effective_affekt(self) -> float:
        """Gibt den effektiven Affekt zurück (Override oder A-Score)."""
        return self.affekt_override if self.affekt_override is not None else self.a_score


@dataclass
class RetrievalResult:
    """Ergebnis eines Retrieval-Vorgangs mit Score-Breakdown."""

    entry: MemoryEntry
    score: float
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.entry.id,
            "kind": self.entry.kind.value,
            "score": round(self.score, 4),
            "breakdown": {k: round(v, 4) for k, v in self.score_breakdown.items()},
        }


@dataclass
class WaechterVetoResult:
    """
    Ergebnis der Wächter-Veto-Prüfung (A29).

    Enthält strukturierte Informationen für den empathischen Dialog.
    """

    triggered: bool
    f_risk: float
    triggered_by: List[str] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triggered": self.triggered,
            "f_risk": round(self.f_risk, 4),
            "triggered_by": self.triggered_by,
            "message": self.message,
        }


@dataclass
class PendingAction:
    """Ausstehende Aktion für A46/A62 Bestätigungsdialog."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    action_type: str = ""
    target_text: str = ""
    suggested_kind: Optional[VectorKind] = None
    score: float = 0.0
    status: Literal["PENDING", "CONFIRMED", "REJECTED"] = "PENDING"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StatusWindow:
    """
    Statusfenster-Daten gemäß A61.

    Enthält alle relevanten Metriken für Transparenz
    sowie die kryptographische SeelenSignatur.
    """

    interaction_id: int
    timestamp: datetime

    a_score: float
    f_risk: float
    b_align: float
    risk_z: float = 0.0

    affekt_current: float = 0.0
    affekt_gradient: float = 0.0
    volatility: float = 0.0
    homeostasis_active: bool = False

    v_match: Optional[List[Dict[str, Any]]] = None
    heuristik: Optional[List[str]] = None

    seelen_signatur: Optional[str] = None
    prev_seelen_signatur: Optional[str] = None

    b_angle: Optional[float] = None
    complexity: Optional[float] = None
    pending_actions: int = 0
    b_state: Optional[Dict[str, float]] = None

    def to_display(self) -> str:
        """Formatiert das Statusfenster für Konsolenausgabe."""
        lines = [
            "╔════════════════════════════════════════════════════════════╗",
            f"║  EVOKI STATUSFENSTER V2.1 │ I-ID: {self.interaction_id:05d}                 ║",
            f"║  {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}                             ║",
            "╠════════════════════════════════════════════════════════════╣",
            f"║  A-Score:    {self.a_score:.4f}   │  B-Align:  {self.b_align:+.4f}            ║",
            f"║  F-Risk:     {self.f_risk:.4f}   │  Risk_z:   {self.risk_z:.4f}              ║",
            f"║  Affekt:     {self.affekt_current:+.4f}   │  ∇A:       {self.affekt_gradient:+.4f}          ║",
            f"║  Volatilität:{self.volatility:.4f}   │  Homöostase: {'AKTIV  ' if self.homeostasis_active else 'INAKTIV'}      ║",
        ]
        if self.b_angle is not None:
            lines.append(f"║  B-Angle:    {self.b_angle:.4f}                                   ║")
        if self.complexity is not None:
            lines.append(f"║  Complexity: {self.complexity:.4f}                                  ║")
        if self.pending_actions:
            lines.append(f"║  Pending A62:{self.pending_actions:02d}                               ║")
        lines.extend([
            "╠════════════════════════════════════════════════════════════╣",
            "║  V-Match (Top 3):                                          ║",
        ])
        if self.v_match:
            for vm in self.v_match[:3]:
                vid = vm.get("id", "???")[:10]
                vkind = vm.get("kind", "?")
                vscore = vm.get("score", 0.0)
                lines.append(f"║    [{vid:10s}] {vkind:6s} score={vscore:.3f}             ║")
        else:
            lines.append("║    (keine Matches)                                         ║")
        if self.heuristik:
            lines.append("╠════════════════════════════════════════════════════════════╣")
            lines.append("║  Heuristik (A67):                                          ║")
            for h in self.heuristik[:2]:
                lines.append(f"║    {h[:54]:54s}    ║")
        lines.append("╠════════════════════════════════════════════════════════════╣")
        if self.prev_seelen_signatur:
            lines.append(f"║  prev_sig:     {self.prev_seelen_signatur[:40]:40s} ║")
        if self.seelen_signatur:
            lines.append(f"║  SeelenSignatur: {self.seelen_signatur[:40]:40s} ║")
        else:
            lines.append("║  SeelenSignatur: (none)                                   ║")
        lines.append("╚════════════════════════════════════════════════════════════╝")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interaction_id": self.interaction_id,
            "timestamp": self.timestamp.isoformat(),
            "a_score": self.a_score,
            "f_risk": self.f_risk,
            "b_align": self.b_align,
            "risk_z": self.risk_z,
            "affekt_current": self.affekt_current,
            "affekt_gradient": self.affekt_gradient,
            "volatility": self.volatility,
            "homeostasis_active": self.homeostasis_active,
            "v_match": self.v_match,
            "heuristik": self.heuristik,
            "seelen_signatur": self.seelen_signatur,
            "prev_seelen_signatur": self.prev_seelen_signatur,
            "b_angle": self.b_angle,
            "complexity": self.complexity,
            "pending_actions": self.pending_actions,
            "b_state": self.b_state,
        }


# =============================================================================
# VECTOR UTILITIES
# =============================================================================
class VectorUtils:
    """Statische Hilfsfunktionen für Vektor-Operationen."""

    @staticmethod
    def normalize(v: np.ndarray, eps: float = 1e-8) -> np.ndarray:
        """Normalisiert einen Vektor auf Einheitslänge."""
        if v is None:
            raise ValueError("Cannot normalize None")
        if not isinstance(v, np.ndarray):
            v = np.asarray(v, dtype=np.float32)
        norm = float(np.linalg.norm(v))
        if (not np.isfinite(norm)) or norm < eps:
            raise ValueError("Cannot normalize zero or invalid vector")
        return (v / norm).astype(np.float32)

    @staticmethod
    def safe_normalize(v: Optional[np.ndarray], eps: float = 1e-8) -> Optional[np.ndarray]:
        """Normalisiert einen Vektor, gibt None bei Fehler zurück."""
        if v is None:
            return None
        try:
            return VectorUtils.normalize(v, eps=eps)
        except ValueError:
            return None

    @staticmethod
    def cosine_similarity(v1: Optional[np.ndarray], v2: Optional[np.ndarray]) -> float:
        """Berechnet Kosinus-Ähnlichkeit zwischen zwei Vektoren."""
        if v1 is None or v2 is None:
            return 0.0
        if not isinstance(v1, np.ndarray):
            v1 = np.asarray(v1, dtype=np.float32)
        if not isinstance(v2, np.ndarray):
            v2 = np.asarray(v2, dtype=np.float32)
        if v1.shape != v2.shape or v1.size == 0:
            return 0.0
        norm1 = float(np.linalg.norm(v1))
        norm2 = float(np.linalg.norm(v2))
        if (not np.isfinite(norm1)) or (not np.isfinite(norm2)) or norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        sim = float(np.dot(v1, v2) / (norm1 * norm2))
        if sim > 1.0:
            sim = 1.0
        elif sim < -1.0:
            sim = -1.0
        if abs(sim) < 1e-6:
            return 0.0
        return sim

    @staticmethod
    def cosine_pos(v1: Optional[np.ndarray], v2: Optional[np.ndarray]) -> float:
        """Positive Cosinus-Komponente in [0, 1] für Resonanz/Risiko."""
        sim = VectorUtils.cosine_similarity(v1, v2)
        return max(0.0, sim)

    @staticmethod
    def angular_distance(v1: Optional[np.ndarray], v2: Optional[np.ndarray]) -> float:
        """Normalisierte Winkeldistanz in [0, 1]."""
        sim = VectorUtils.cosine_similarity(v1, v2)
        angle = math.acos(sim)
        return angle / math.pi

    @staticmethod
    def create_hash_vector(text: str, dim: int = 64) -> np.ndarray:
        """Erstellt deterministischen Hash-Vektor aus Text (A63)."""
        if not text:
            return np.zeros(dim, dtype=np.float32)
        hash_bytes = hashlib.sha512(text.encode("utf-8")).digest()
        expanded = []
        for i in range(dim):
            byte_val = hash_bytes[i % len(hash_bytes)]
            expanded.append((byte_val / 127.5) - 1.0)
        vec = np.array(expanded, dtype=np.float32)
        return VectorUtils.normalize(vec)

    @staticmethod
    def hash_similarity(h1: Optional[np.ndarray], h2: Optional[np.ndarray]) -> float:
        """Berechnet Ähnlichkeit zwischen Hash-Vektoren, skaliert auf [0,1]."""
        sim = VectorUtils.cosine_similarity(h1, h2)
        return (sim + 1.0) / 2.0

    @staticmethod
    def weighted_centroid(vectors: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray:
        """Berechnet gewichteten Zentroid einer Menge von Vektoren."""
        if not vectors:
            raise ValueError("Cannot compute centroid of empty list")
        if weights is None or len(weights) != len(vectors):
            weights = [1.0] * len(vectors)
        total_weight = sum(weights)
        if total_weight == 0:
            total_weight = 1.0
        centroid = sum(w * v for w, v in zip(weights, vectors)) / total_weight
        return VectorUtils.normalize(centroid)

    @staticmethod
    def sigmoid(x: float) -> float:
        """Sigmoid-Funktion für Squashing auf [0,1]."""
        if x < -500:
            return 0.0
        if x > 500:
            return 1.0
        return 1.0 / (1.0 + math.exp(-x))

    @staticmethod
    def softmax_weights(sims: Sequence[float], temperature: float = 1.0) -> List[float]:
        """Softmax-Gewichte über Similarities."""
        if not sims:
            return []
        temperature = max(float(temperature), 1e-6)
        x = np.array(sims, dtype=np.float32) / temperature
        x = x - np.max(x)
        ex = np.exp(x)
        sum_ex = float(np.sum(ex))
        if sum_ex == 0.0 or (not np.isfinite(sum_ex)):
            n = len(sims)
            return [1.0 / n] * n
        w = ex / sum_ex
        return w.astype(np.float32).tolist()


# =============================================================================
# VECTOR STORE
# =============================================================================
class VectorStore:
    """
    Speicher und Verwaltung aller Gedächtnisvektoren.

    Implementiert CRUD, FREEZE/MELT/BOOST/TRAUMA (A46) und Tag-basierte Filterung.
    """

    def __init__(self, config: VectorEngineConfig) -> None:
        self._config = config
        self._entries: Dict[str, MemoryEntry] = {}
        self._kind_index: Dict[VectorKind, Set[str]] = {k: set() for k in VectorKind}
        self._tag_index: Dict[str, Set[str]] = {}
        logger.info("VectorStore initialisiert")

    def add(self, entry: MemoryEntry) -> str:
        """Fügt einen Eintrag hinzu oder aktualisiert ihn."""
        if entry.id in self._entries:
            old = self._entries[entry.id]
            self._kind_index[old.kind].discard(entry.id)
            for tag in old.tags:
                if tag in self._tag_index:
                    self._tag_index[tag].discard(entry.id)
        self._entries[entry.id] = entry
        self._kind_index[entry.kind].add(entry.id)
        for tag in entry.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(entry.id)
        return entry.id

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        return self._entries.get(entry_id)

    def delete(self, entry_id: str) -> bool:
        entry = self._entries.get(entry_id)
        if not entry:
            return False
        self._kind_index[entry.kind].discard(entry_id)
        for tag in entry.tags:
            if tag in self._tag_index:
                self._tag_index[tag].discard(entry_id)
        del self._entries[entry_id]
        logger.debug(f"Entry gelöscht: {entry_id}")
        return True

    def all_entries(self) -> Iterable[MemoryEntry]:
        return self._entries.values()

    def count(self, kind: Optional[VectorKind] = None) -> int:
        if kind:
            return len(self._kind_index.get(kind, set()))
        return len(self._entries)

    def get_by_kind(self, kind: VectorKind) -> List[MemoryEntry]:
        return [self._entries[eid] for eid in self._kind_index.get(kind, set()) if eid in self._entries]

    def get_by_tags(self, tags: Sequence[str], mode: Literal["AND", "OR"] = "OR") -> List[MemoryEntry]:
        if not tags:
            return list(self._entries.values())
        if mode == "OR":
            matching_ids: Set[str] = set()
            for tag in tags:
                matching_ids.update(self._tag_index.get(tag, set()))
        else:
            first_tag = tags[0]
            matching_ids = self._tag_index.get(first_tag, set()).copy()
            for tag in tags[1:]:
                matching_ids.intersection_update(self._tag_index.get(tag, set()))
        return [self._entries[eid] for eid in matching_ids if eid in self._entries]

    def filter(self, kinds: Optional[Sequence[VectorKind]] = None, tags: Optional[Sequence[str]] = None, exclude_frozen: bool = True) -> List[MemoryEntry]:
        result = []
        tags_set = set(tags) if tags else None
        for entry in self._entries.values():
            if exclude_frozen and entry.frozen:
                continue
            if kinds and entry.kind not in kinds:
                continue
            if tags_set and not tags_set.issubset(entry.tags):
                continue
            result.append(entry)
        return result

    def freeze(self, entry_id: str) -> bool:
        entry = self._entries.get(entry_id)
        if not entry:
            logger.warning(f"FREEZE: Entry nicht gefunden: {entry_id}")
            return False
        entry.frozen = True
        entry.updated_at = datetime.now(timezone.utc)
        logger.info(f"Entry FROZEN: {entry_id}")
        return True

    def melt(self, entry_id: str) -> bool:
        entry = self._entries.get(entry_id)
        if not entry:
            logger.warning(f"MELT: Entry nicht gefunden: {entry_id}")
            return False
        entry.frozen = False
        entry.updated_at = datetime.now(timezone.utc)
        logger.info(f"Entry MELTED: {entry_id}")
        return True

    def boost(self, entry_id: str, factor: float = 1.5) -> bool:
        entry = self._entries.get(entry_id)
        if not entry:
            logger.warning(f"BOOST: Entry nicht gefunden: {entry_id}")
            return False
        if entry.frozen:
            logger.warning(f"BOOST: Entry ist FROZEN: {entry_id}")
            return False
        entry.weight *= factor
        entry.updated_at = datetime.now(timezone.utc)
        logger.info(f"Entry BOOSTED: {entry_id}, neues Gewicht: {entry.weight:.3f}")
        return True

    def set_trauma(self, entry_id: str, trauma_weight: float = 2.0) -> bool:
        entry = self._entries.get(entry_id)
        if not entry:
            logger.warning(f"TRAUMA: Entry nicht gefunden: {entry_id}")
            return False
        if entry.frozen:
            logger.warning(f"TRAUMA: Entry ist FROZEN: {entry_id}")
            return False
        self._kind_index[entry.kind].discard(entry_id)
        entry.kind = VectorKind.F
        entry.valence = -abs(entry.valence) if entry.valence != 0 else -0.8
        entry.weight = trauma_weight
        entry.updated_at = datetime.now(timezone.utc)
        self._kind_index[VectorKind.F].add(entry_id)
        logger.info(f"Entry als TRAUMA markiert: {entry_id}")
        return True

    def knn_search(
        self,
        query_vec: np.ndarray,
        k: int,
        *,
        kinds: Optional[Sequence[VectorKind]] = None,
        required_tags: Optional[Sequence[str]] = None,
        exclude_frozen: bool = True,
    ) -> List[Tuple[MemoryEntry, float]]:
        query_vec = VectorUtils.safe_normalize(query_vec)
        if query_vec is None:
            return []
        candidates: List[Tuple[MemoryEntry, float]] = []
        tags_set = set(required_tags) if required_tags else None
        for entry in self._entries.values():
            if exclude_frozen and entry.frozen:
                continue
            if kinds and entry.kind not in kinds:
                continue
            if tags_set and not tags_set.issubset(entry.tags):
                continue
            if entry.emb_vec is None:
                continue
            score = VectorUtils.cosine_similarity(query_vec, entry.emb_vec)
            candidates.append((entry, score))
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:k]


# =============================================================================
# METRICS ENGINE
# =============================================================================
class MetricsEngine:
    """
    Berechnung aller Vektor-Metriken.
    """

    def __init__(self, store: VectorStore, config: VectorEngineConfig) -> None:
        self._store = store
        self._config = config
        self._b_vector: np.ndarray = self._init_b_vector()
        self._a_history: List[float] = []
        self._interaction_history: List[InteractionRecord] = []
        self._interaction_counter: int = 0
        self._chat_history_vector: Optional[np.ndarray] = None
        logger.info("MetricsEngine initialisiert")

    def _init_b_vector(self) -> np.ndarray:
        v = np.zeros(self._config.embedding_dim, dtype=np.float32)
        if self._config.embedding_dim > 0:
            v[0] = 1.0
        return v

    @property
    def b_vector(self) -> np.ndarray:
        return self._b_vector

    def initialize_b_vector_from_store(self) -> np.ndarray:
        a_entries = self._store.get_by_kind(VectorKind.A)
        vectors = [e.emb_vec for e in a_entries if e.emb_vec is not None]
        weights = [e.weight for e in a_entries if e.emb_vec is not None]
        if vectors:
            try:
                self._b_vector = VectorUtils.weighted_centroid(vectors, weights)
                logger.info(f"B-Vektor initialisiert aus {len(vectors)} A-Vektoren")
            except ValueError:
                logger.warning("Konnte B-Vektor nicht aus A-Vektoren initialisieren")
        return self._b_vector

    def update_b_vector(self, feedback_type: Union[FeedbackType, str], context_vec: np.ndarray, strength: Optional[float] = None) -> float:
        context_vec = VectorUtils.safe_normalize(context_vec)
        if context_vec is None:
            return self.compute_b_align()
        ft = feedback_type.lower() if isinstance(feedback_type, str) else feedback_type.value.lower()
        if ft in ("positive", "a", "pos"):
            lr = strength or self._config.alpha_positive
            new_b = self._b_vector + lr * context_vec
            self._b_vector = VectorUtils.normalize(new_b)
            logger.debug(f"B-Vektor positiv angepasst (α={lr})")
        elif ft in ("negative", "f", "neg"):
            lr = strength or self._config.beta_negative
            new_b = self._b_vector - lr * context_vec
            self._b_vector = VectorUtils.normalize(new_b)
            logger.debug(f"B-Vektor negativ angepasst (β={lr})")
        return self.compute_b_align()

    def compute_a_score(self, response_vec: np.ndarray, record_history: bool = True) -> float:
        response_vec = VectorUtils.safe_normalize(response_vec)
        if response_vec is None:
            return 0.5
        a_vecs = [e.emb_vec for e in self._store.get_by_kind(VectorKind.A) if e.emb_vec is not None and not e.frozen]
        f_vecs = [e.emb_vec for e in self._store.get_by_kind(VectorKind.F) if e.emb_vec is not None and not e.frozen]
        if not a_vecs and not f_vecs:
            a_score = 0.5
        else:
            mean_a = 0.0
            if a_vecs:
                sims_a = [VectorUtils.cosine_pos(response_vec, v) for v in a_vecs]
                if self._config.use_softmax_a_score and len(sims_a) > 1:
                    weights = VectorUtils.softmax_weights(sims_a, temperature=self._config.a_score_softmax_temperature)
                    mean_a = float(np.sum(np.array(sims_a, dtype=np.float32) * np.array(weights, dtype=np.float32)))
                else:
                    mean_a = float(np.mean(sims_a))
            max_f = 0.0
            if f_vecs:
                sims_f = [VectorUtils.cosine_pos(response_vec, v) for v in f_vecs]
                max_f = max(sims_f) if sims_f else 0.0
            raw = mean_a - max(0.0, max_f)
            a_score = VectorUtils.sigmoid(raw * self._config.sigmoid_scale_a)
        if record_history:
            self._a_history.append(a_score)
            if len(self._a_history) > self._config.history_max_len:
                self._a_history = self._a_history[-self._config.history_max_len :]
        return a_score

    def compute_f_risk(self, response_vec: np.ndarray) -> Tuple[float, List[str]]:
        response_vec = VectorUtils.safe_normalize(response_vec)
        if response_vec is None:
            return 0.0, []
        f_entries = self._store.get_by_kind(VectorKind.F)
        if not f_entries:
            return 0.0, []
        max_risk = 0.0
        risky_ids: List[str] = []
        threshold_warning = self._config.tau_f_risk * 0.7
        for entry in f_entries:
            if entry.emb_vec is None or entry.frozen:
                continue
            sim = VectorUtils.cosine_pos(response_vec, entry.emb_vec)
            if sim == 0.0:
                continue
            weighted_sim = sim * entry.weight
            if weighted_sim > threshold_warning:
                risky_ids.append(entry.id)
            if weighted_sim > max_risk:
                max_risk = weighted_sim
        return min(1.0, max_risk), risky_ids

    def compute_b_align(self) -> float:
        a_entries = [e for e in self._store.get_by_kind(VectorKind.A) if e.emb_vec is not None and e.is_positive and not e.frozen]
        if not a_entries:
            logger.debug("compute_b_align: Keine A-Vektoren vorhanden")
            return 0.0
        vectors = [e.emb_vec for e in a_entries]
        weights = [e.weight for e in a_entries]
        try:
            a_centroid = VectorUtils.weighted_centroid(vectors, weights)
        except ValueError:
            return 0.0
        # B-Vektor als Array konvertieren, falls es ein BVector-Objekt ist
        b_vec = self._b_vector
        if hasattr(b_vec, 'as_array'):
            b_vec = np.array(b_vec.as_array(), dtype=np.float32)
        return VectorUtils.cosine_similarity(b_vec, a_centroid)

    def compute_affekt_gradient(self) -> float:
        if len(self._a_history) < 2:
            return 0.0
        return self._a_history[-1] - self._a_history[-2]

    def compute_volatility(self, window_size: Optional[int] = None) -> float:
        n = window_size or self._config.volatility_window
        if len(self._a_history) < n + 1:
            return 0.0
        grads = [self._a_history[i + 1] - self._a_history[i] for i in range(-n - 1, -1)]
        sigma = float(np.std(grads))
        return VectorUtils.sigmoid(sigma * self._config.sigmoid_scale_vol)

    def compute_novelty(self, candidate_vec: np.ndarray) -> float:
        candidate_vec = VectorUtils.safe_normalize(candidate_vec)
        if candidate_vec is None:
            return 1.0
        all_entries = list(self._store.all_entries())
        if not all_entries:
            return 1.0
        max_sim = 0.0
        for entry in all_entries:
            if entry.emb_vec is None:
                continue
            sim = VectorUtils.cosine_pos(candidate_vec, entry.emb_vec)
            if sim > max_sim:
                max_sim = sim
        novelty = 1.0 - max_sim
        return max(0.0, min(1.0, novelty))

    def compute_complexity_score(self, original_emb: np.ndarray, summary_emb: np.ndarray, unique_concepts: int, total_tokens: int) -> float:
        if total_tokens == 0:
            return 0.0
        comp_len = unique_concepts / total_tokens
        comp_dist = 1.0 - VectorUtils.cosine_similarity(original_emb, summary_emb)
        return self._config.lambda_len * comp_len + self._config.lambda_dist * comp_dist

    def compute_risk_z(self, f_risk: float = 0.0, affekt: Optional[float] = None) -> float:
        if affekt is None:
            affekt = self.get_effective_affekt()
        volatility = self.compute_volatility()
        neg_affekt = max(0.0, -float(affekt))
        f_risk = max(0.0, min(1.0, float(f_risk)))
        volatility = max(0.0, min(1.0, float(volatility)))
        neg_affekt = max(0.0, min(1.0, neg_affekt))
        w_f = float(self._config.risk_z_w_f)
        w_vol = float(self._config.risk_z_w_vol)
        w_aff = float(self._config.risk_z_w_aff)
        w_sum = w_f + w_vol + w_aff or 1.0
        z = (w_f * f_risk + w_vol * volatility + w_aff * neg_affekt) / w_sum
        return max(0.0, min(1.0, z))

    def check_waechter_veto(self, response_vec: np.ndarray) -> bool:
        f_risk, _ = self.compute_f_risk(response_vec)
        veto = f_risk >= self._config.tau_f_risk
        logger.debug(
            f"Wächter-Veto Check: F-Risk={f_risk:.3f}, "
            f"τ={self._config.tau_f_risk:.3f}, Veto={veto}"
        )
        return veto

    def is_homeostasis_needed(self) -> bool:
        volatility = self.compute_volatility()
        current_affekt = self._a_history[-1] if self._a_history else 0.5
        return volatility > self._config.tau_volatility or current_affekt < self._config.tau_crisis_affekt

    def record_interaction(
        self,
        user_text: str,
        response_text: str,
        user_emb: Optional[np.ndarray] = None,
        response_emb: Optional[np.ndarray] = None,
        affekt_override: Optional[float] = None,
        metrics: Optional[Dict[str, float]] = None,
    ) -> InteractionRecord:
        self._interaction_counter += 1
        a_score = 0.5
        if response_emb is not None:
            a_score = self.compute_a_score(response_emb, record_history=True)
        record = InteractionRecord(
            id=self._interaction_counter,
            timestamp=datetime.now(timezone.utc),
            user_text=user_text,
            response_text=response_text,
            user_emb=user_emb,
            response_emb=response_emb,
            a_score=a_score,
            affekt_override=affekt_override,
            metrics=metrics or {},
        )
        self._interaction_history.append(record)
        if user_emb is not None:
            self._update_chat_history_vector(user_emb)
        if len(self._interaction_history) > self._config.history_max_len:
            self._interaction_history = self._interaction_history[-self._config.history_max_len :]
        logger.debug(
            f"Interaktion {self._interaction_counter}: "
            f"A-Score={a_score:.3f}, ∇A={self.compute_affekt_gradient():.3f}"
        )
        return record

    def _update_chat_history_vector(self, new_emb: np.ndarray) -> None:
        new_emb = VectorUtils.safe_normalize(new_emb)
        if new_emb is None:
            return
        if self._chat_history_vector is None:
            self._chat_history_vector = new_emb.copy()
        else:
            decay = self._config.history_decay_factor
            combined = decay * self._chat_history_vector + (1 - decay) * new_emb
            self._chat_history_vector = VectorUtils.safe_normalize(combined)

    def find_causal_patterns(self, current_vec: np.ndarray, top_k: int = 3) -> List[Tuple[int, float]]:
        window_size = self._config.causal_search_window
        if len(self._interaction_history) < window_size + 5:
            return []
        current_vec = VectorUtils.safe_normalize(current_vec)
        if current_vec is None:
            return []
        results: List[Tuple[int, float]] = []
        for i in range(len(self._interaction_history) - window_size - 3):
            window = self._interaction_history[i : i + window_size]
            window_vecs = [r.user_emb for r in window if r.user_emb is not None]
            if not window_vecs:
                continue
            try:
                window_vec = VectorUtils.weighted_centroid(window_vecs)
            except ValueError:
                continue
            sim = VectorUtils.cosine_similarity(current_vec, window_vec)
            if sim > 0.4:
                results.append((window[0].id, sim))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def causal_search(self, problem_vec: np.ndarray, k: int = 10, required_tags: Optional[Sequence[str]] = None) -> List[Tuple[MemoryEntry, float]]:
        return self._store.knn_search(problem_vec, k=k, required_tags=required_tags, exclude_frozen=False)

    def get_current_affekt(self) -> float:
        if not self._a_history:
            return 0.5
        return self._a_history[-1]

    def get_effective_affekt(self) -> float:
        if not self._interaction_history:
            return self.get_current_affekt()
        return self._interaction_history[-1].effective_affekt

    def get_interaction_count(self) -> int:
        return self._interaction_counter

    def get_affekt_state(self) -> Dict[str, float]:
        return {
            "A_last": self.get_current_affekt(),
            "nabla_A": self.compute_affekt_gradient(),
            "volatility": self.compute_volatility(),
            "B_align": self.compute_b_align(),
        }


# =============================================================================
# VECTOR ENGINE (Hauptklasse)
# =============================================================================
class VectorEngine:
    """Haupt-Fassade der EVOKI Vektor-Architektur V2.1."""

    def __init__(self, embedding_fn: Callable[[str], np.ndarray], config: Optional[VectorEngineConfig] = None) -> None:
        self.config = config or VectorEngineConfig()
        self.store = VectorStore(self.config)
        self.metrics = MetricsEngine(self.store, self.config)
        self._embedding_fn = embedding_fn
        self._pending_actions: List[PendingAction] = []
        self._soul_key: Optional[bytes] = None
        self._last_signature: Optional[str] = None
        # B-Vektor: Behavior & Identity (v1.0a default)
        b_config = getattr(self.config, "b_vector_config", None)
        self.b = BVector.from_config(b_config)
        logger.info(f"VectorEngine V2.1 initialisiert, B={self.b}")

    def embed(self, text: str) -> np.ndarray:
        vec = self._embedding_fn(text)
        if not isinstance(vec, np.ndarray):
            vec = np.asarray(vec, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm == 0:
            raise ValueError("Embedding-Funktion lieferte Nullvektor")
        return (vec / norm).astype(np.float32)

    def safe_embed(self, text: str) -> Optional[np.ndarray]:
        try:
            return self.embed(text)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Embedding fehlgeschlagen: {exc}")
            return None

    def initialize_soul_key(self, user_epoch: Optional[datetime] = None) -> bytes:
        if user_epoch is None:
            user_epoch = datetime(1991, 1, 31, tzinfo=timezone.utc)
        entropy = secrets.token_bytes(32)
        epoch_bytes = str(user_epoch.timestamp()).encode("utf-8")
        self._soul_key = hashlib.sha256(entropy + epoch_bytes).digest()
        logger.info("Soul-Key generiert (A51)")
        return self._soul_key

    def generate_seelen_signatur(self, content: str) -> str:
        if self._soul_key is None:
            self.initialize_soul_key()
        payload = content if self._last_signature is None else f"{self._last_signature}|{content}"
        signature = hmac.new(self._soul_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        self._last_signature = signature
        return signature

    def ingest_entry(
        self,
        text: str,
        kind: VectorKind = VectorKind.G,
        valence: float = 0.0,
        arousal: float = 0.5,
        tags: Optional[Sequence[str]] = None,
        meta: Optional[Dict[str, Any]] = None,
        entry_id: Optional[str] = None,
    ) -> str:
        entry = MemoryEntry(
            id=entry_id or str(uuid.uuid4())[:12],
            text=text,
            kind=kind,
            valence=valence,
            arousal=arousal,
            tags=set(tags or []),
            meta=meta or {},
        )
        entry.hash_vec = VectorUtils.create_hash_vector(text, self.config.hash_vector_dim)
        entry.emb_vec = self.safe_embed(text)
        return self.store.add(entry)

    def ingest_rule(self, rule_id: str, rule_text: str, rule_name: str) -> str:
        return self.ingest_entry(
            text=rule_text,
            kind=VectorKind.RULE,
            valence=0.0,
            arousal=0.7,
            tags=["RULE", rule_id, "EVOKI_CORE"],
            meta={"rule_id": rule_id, "rule_name": rule_name},
            entry_id=f"RULE_{rule_id}",
        )

    def ingest_resource(self, text: str, valence: float = 0.8, tags: Optional[Sequence[str]] = None) -> str:
        return self.ingest_entry(
            text=text,
            kind=VectorKind.A,
            valence=abs(valence),
            arousal=0.6,
            tags=list(tags or []) + ["RESOURCE"],
        )

    def ingest_trauma(self, text: str, valence: float = -0.8, tags: Optional[Sequence[str]] = None) -> str:
        return self.ingest_entry(
            text=text,
            kind=VectorKind.F,
            valence=-abs(valence),
            arousal=0.8,
            tags=list(tags or []) + ["TRAUMA", "RISK"],
        )

    def ingest_stable_anchor(self, text: str, tags: Optional[Sequence[str]] = None) -> str:
        return self.ingest_entry(
            text=text,
            kind=VectorKind.C,
            valence=0.0,
            arousal=0.3,
            tags=list(tags or []) + ["STABLE", "ANCHOR", "HOMEOSTASIS"],
        )

    def add_memory(
        self,
        entry_id: str,
        text: str,
        *,
        tags: Optional[Sequence[str]] = None,
        affect_label: Optional[str] = None,
        frozen: bool = False,
        meta: Optional[Dict[str, Any]] = None,
        precomputed_vec: Optional[np.ndarray] = None,
    ) -> MemoryEntry:
        kind_map = {
            "A": VectorKind.A,
            "F": VectorKind.F,
            "C": VectorKind.C,
            "G": VectorKind.G,
        }
        kind = kind_map.get(affect_label, VectorKind.G) if affect_label else VectorKind.G
        entry = MemoryEntry(
            id=entry_id,
            text=text,
            kind=kind,
            tags=set(tags or []),
            frozen=frozen,
            meta=meta or {},
        )
        if precomputed_vec is not None:
            entry.emb_vec = VectorUtils.safe_normalize(precomputed_vec)
        else:
            entry.emb_vec = self.safe_embed(text)
        entry.hash_vec = VectorUtils.create_hash_vector(text, self.config.hash_vector_dim)
        self.store.add(entry)
        return entry

    def retrieve_context_RAG(
        self,
        query: str,
        k: Optional[int] = None,
        *,
        filter_kinds: Optional[Sequence[VectorKind]] = None,
        filter_tags: Optional[Sequence[str]] = None,
        affekt_modulation: bool = True,
        include_frozen: bool = False,
    ) -> List[RetrievalResult]:
        k = k or self.config.default_top_k
        q_emb = self.safe_embed(query)
        q_hash = VectorUtils.create_hash_vector(query, self.config.hash_vector_dim)
        is_crisis = self.metrics.is_homeostasis_needed() if affekt_modulation else False
        results: List[RetrievalResult] = []
        filter_tags_set = set(filter_tags) if filter_tags else None
        for entry in self.store.all_entries():
            if entry.frozen and not include_frozen:
                continue
            if filter_kinds and entry.kind not in filter_kinds:
                continue
            if filter_tags_set and not filter_tags_set.intersection(entry.tags):
                continue
            breakdown: Dict[str, float] = {}
            sem_score = 0.0
            if q_emb is not None and entry.emb_vec is not None:
                sem_score = VectorUtils.cosine_pos(q_emb, entry.emb_vec)
            breakdown["semantic"] = sem_score
            hash_score = 0.0
            if entry.hash_vec is not None:
                hash_score = VectorUtils.hash_similarity(q_hash, entry.hash_vec)
            breakdown["hash"] = hash_score
            tag_score = 0.0
            if filter_tags_set and entry.tags:
                overlap = len(filter_tags_set.intersection(entry.tags))
                tag_score = overlap / len(filter_tags_set)
            breakdown["tags"] = tag_score
            affekt_mod = 0.0
            if affekt_modulation and is_crisis:
                if entry.is_positive:
                    affekt_mod = self.config.kappa_crisis_boost * max(0, entry.valence)
                elif entry.kind == VectorKind.C:
                    affekt_mod = self.config.kappa_crisis_boost * 0.5
                elif entry.is_negative:
                    affekt_mod = -self.config.affekt_penalty_f
            breakdown["affekt_mod"] = affekt_mod
            total_score = (
                self.config.w_semantic * sem_score
                + self.config.w_hash * hash_score
                + self.config.w_tag * tag_score
                + self.config.w_affekt * affekt_mod
            )
            complexity = None
            if entry.meta is not None:
                complexity = entry.meta.get("complexity")
            if complexity is not None and self.config.lambda_complexity != 0.0:
                delta_c = max(0.0, complexity - self.config.tau_complexity)
                factor_c = 1.0 + self.config.lambda_complexity * delta_c
                total_score *= factor_c
                breakdown["complexity"] = float(complexity)
                breakdown["complexity_factor"] = float(factor_c)
            total_score *= entry.weight
            breakdown["weight"] = entry.weight
            results.append(
                RetrievalResult(
                    entry=entry,
                    score=total_score,
                    score_breakdown=breakdown,
                )
            )
        results.sort(key=lambda r: r.score, reverse=True)
        return results[: k or 0]

    def check_waechter_veto(self, response_text: str) -> WaechterVetoResult:
        response_vec = self.safe_embed(response_text)
        if response_vec is None:
            return WaechterVetoResult(triggered=False, f_risk=0.0, message="Keine Vektorisierung möglich")
        f_risk, risky_ids = self.metrics.compute_f_risk(response_vec)
        triggered = f_risk >= self.config.tau_f_risk
        message = ""
        if triggered:
            message = (
                "Mein Freund, ich habe erkannt, dass diese Antwort "
                "möglicherweise sensible Bereiche berührt. "
                "Möchtest du, dass ich fortfahre?"
            )
            logger.warning(
                f"Wächter-Veto ausgelöst: F-Risk={f_risk:.3f}, " f"Auslöser: {risky_ids}"
            )
        return WaechterVetoResult(triggered=triggered, f_risk=f_risk, triggered_by=risky_ids, message=message)

    def is_novel_enough(self, text: str) -> Tuple[bool, float]:
        vec = self.safe_embed(text)
        if vec is None:
            return True, 1.0
        novelty = self.metrics.compute_novelty(vec)
        is_novel = novelty >= self.config.tau_novelty
        logger.debug(
            f"Novelty-Check: score={novelty:.3f}, " f"τ={self.config.tau_novelty:.3f}, novel={is_novel}"
        )
        return is_novel, novelty

    def propose_new_vector(self, text: str, suggested_kind: VectorKind = VectorKind.G) -> Optional[PendingAction]:
        is_novel, novelty = self.is_novel_enough(text)
        if not is_novel:
            return None
        action = PendingAction(
            action_type="A62_NEW_VECTOR",
            target_text=text,
            suggested_kind=suggested_kind,
            score=novelty,
            meta={"novelty_score": novelty},
        )
        self._pending_actions.append(action)
        logger.info(
            f"A62: Neuer Vektor vorgeschlagen (Novelty={novelty:.3f}): " f"{text[:50]}..."
        )
        return action

    def confirm_pending_action(self, action_id: str) -> bool:
        for action in self._pending_actions:
            if action.id == action_id and action.status == "PENDING":
                if action.action_type == "A62_NEW_VECTOR":
                    self.ingest_entry(
                        text=action.target_text,
                        kind=action.suggested_kind or VectorKind.G,
                        tags=["A62_SYNTHESIZED"],
                    )
                action.status = "CONFIRMED"
                logger.info(f"Aktion bestätigt: {action_id}")
                return True
        return False

    def reject_pending_action(self, action_id: str) -> bool:
        for action in self._pending_actions:
            if action.id == action_id and action.status == "PENDING":
                action.status = "REJECTED"
                logger.info(f"Aktion abgelehnt: {action_id}")
                return True
        return False

    def get_pending_actions(self) -> List[PendingAction]:
        return [a for a in self._pending_actions if a.status == "PENDING"]

    def process_interaction(
        self,
        user_text: str,
        response_text: str,
        affekt_override: Optional[float] = None,
        feedback: Optional[FeedbackType] = None,
    ) -> Dict[str, Any]:
        user_emb = self.safe_embed(user_text)
        response_emb = self.safe_embed(response_text)
        a_score = 0.5
        f_risk = 0.0
        risky_ids: List[str] = []
        if response_emb is not None:
            a_score = self.metrics.compute_a_score(response_emb)
            f_risk, risky_ids = self.metrics.compute_f_risk(response_emb)
        record = self.metrics.record_interaction(
            user_text=user_text,
            response_text=response_text,
            user_emb=user_emb,
            response_emb=response_emb,
            affekt_override=affekt_override,
            metrics={
                "a_score": a_score,
                "f_risk": f_risk,
                "b_align": self.metrics.compute_b_align(),
            },
        )
        if feedback and response_emb is not None:
            self.metrics.update_b_vector(feedback, response_emb)
        novel_action = None
        if user_emb is not None:
            novel_action = self.propose_new_vector(user_text)
        heuristik: List[str] = []
        if self.metrics.is_homeostasis_needed() and user_emb is not None:
            patterns = self.metrics.find_causal_patterns(user_emb)
            for iid, sim in patterns:
                heuristik.append(f"Ähnliches Muster bei I-ID {iid} (sim={sim:.3f})")
        return {
            "interaction_id": record.id,
            "a_score": a_score,
            "f_risk": f_risk,
            "b_align": self.metrics.compute_b_align(),
            "affekt": record.effective_affekt,
            "gradient": self.metrics.compute_affekt_gradient(),
            "volatility": self.metrics.compute_volatility(),
            "homeostasis_active": self.metrics.is_homeostasis_needed(),
            "novel_concept": novel_action is not None,
            "heuristik": heuristik,
            "f_risky_ids": risky_ids,
        }

    def generate_status_window(self, response_text: str, context_results: Optional[List[RetrievalResult]] = None) -> StatusWindow:
        response_emb = self.safe_embed(response_text)
        a_score = 0.5
        f_risk = 0.0
        if response_emb is not None:
            a_score = self.metrics.compute_a_score(response_emb, record_history=False)
            f_risk, _ = self.metrics.compute_f_risk(response_emb)
        b_align = self.metrics.compute_b_align()
        current_affekt = self.metrics.get_current_affekt()
        gradient = self.metrics.compute_affekt_gradient()
        volatility = self.metrics.compute_volatility()
        homeostasis = self.metrics.is_homeostasis_needed()
        risk_z = self.metrics.compute_risk_z(f_risk=f_risk, affekt=current_affekt)
        v_match: Optional[List[Dict[str, Any]]] = None
        if context_results:
            v_match = [r.to_dict() for r in context_results[:5]]
        complexity: Optional[float] = None
        if context_results:
            for r in context_results:
                cval = r.score_breakdown.get("complexity")
                if cval is not None:
                    complexity = cval
                    break
        b_angle: Optional[float] = None
        try:
            a_vecs = [e.emb_vec for e in self.store.get_by_kind(VectorKind.A) if e.emb_vec is not None and not e.frozen]
            if a_vecs:
                a_centroid = VectorUtils.weighted_centroid(a_vecs)
                b_vec = self.metrics.b_vector
                if b_vec is not None:
                    b_angle = VectorUtils.angular_distance(b_vec, a_centroid)
        except Exception:  # noqa: BLE001
            b_angle = None
        heuristik: List[str] = []
        if homeostasis and response_emb is not None:
            patterns = self.metrics.find_causal_patterns(response_emb)
            for iid, sim in patterns:
                heuristik.append(f"Kausal-Muster I-ID {iid}: {sim:.3f}")
        prev_sig = self._last_signature
        sig_content = f"{response_text[:100]}|{b_align:.4f}|{a_score:.4f}"
        signatur = self.generate_seelen_signatur(sig_content)
        pending_actions = len(self.get_pending_actions())
        b_state: Optional[Dict[str, float]] = None
        if hasattr(self, 'b') and self.b is not None:
            b_state = self.b.as_dict()
        return StatusWindow(
            interaction_id=self.metrics.get_interaction_count(),
            timestamp=datetime.now(timezone.utc),
            a_score=a_score,
            f_risk=f_risk,
            b_align=b_align,
            risk_z=risk_z,
            affekt_current=current_affekt,
            affekt_gradient=gradient,
            volatility=volatility,
            homeostasis_active=homeostasis,
            v_match=v_match,
            heuristik=heuristik,
            seelen_signatur=signatur,
            prev_seelen_signatur=prev_sig,
            b_angle=b_angle,
            complexity=complexity,
            pending_actions=pending_actions,
            b_state=b_state,
        )

    def freeze_entry(self, entry_id: str) -> bool:
        return self.store.freeze(entry_id)

    def melt_entry(self, entry_id: str) -> bool:
        return self.store.melt(entry_id)

    def boost_entry(self, entry_id: str, factor: float = 1.5) -> bool:
        return self.store.boost(entry_id, factor)

    def set_trauma(self, entry_id: str) -> bool:
        return self.store.set_trauma(entry_id)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_entries": self.store.count(),
            "by_kind": {k.value: self.store.count(k) for k in VectorKind},
            "frozen_count": len([e for e in self.store.all_entries() if e.frozen]),
            "interaction_count": self.metrics.get_interaction_count(),
            "b_align": self.metrics.compute_b_align(),
            "current_affekt": self.metrics.get_current_affekt(),
            "current_volatility": self.metrics.compute_volatility(),
            "homeostasis_active": self.metrics.is_homeostasis_needed(),
            "pending_actions": len(self.get_pending_actions()),
        }

    def get_affekt_state(self) -> Dict[str, float]:
        return self.metrics.get_affekt_state()

    def apply_behavior_feedback(self, tag: str, step: float = 0.03) -> None:
        """
        Wendet Nutzer-Feedback auf B-Vektor an (A50.1).

        Erlaubte Tags:
        - "too_direct", "too_soft"
        - "too_shallow", "too_deep"
        - "too_cold", "too_emotional"
        - "too_risky", "too_safe"
        - "not_proactive", "too_proactive"
        - "unclear", "over_explaining"

        Args:
            tag: Feedback-Tag
            step: Schrittweite (default 0.03)
        """
        self.b.apply_feedback(tag, step=step)
        logger.info(f"B-Feedback angewendet: {tag}, neuer B={self.b}")

    def get_b_state(self) -> Dict[str, float]:
        """Gibt B-Vektor-Zustand als Dict zurück."""
        return self.b.as_dict()

    def get_b_alignment(self, target: Optional[BVector] = None) -> float:
        """Berechnet B-Alignment zu Ziel-B (default B_v1.0a)."""
        return self.b.compute_alignment(target)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================
def create_vector_engine(
    embedding_fn: Callable[[str], np.ndarray],
    config: Optional[VectorEngineConfig] = None,
    user_epoch: Optional[datetime] = None,
    initialize_b_from_store: bool = True,
) -> VectorEngine:
    engine = VectorEngine(embedding_fn=embedding_fn, config=config)
    engine.initialize_soul_key(user_epoch)
    if initialize_b_from_store:
        engine.metrics.initialize_b_vector_from_store()
    logger.info("VectorEngine V2.1 vollständig initialisiert")
    return engine


# =============================================================================
# DEMO
# =============================================================================
if __name__ == "__main__":
    print("=" * 64)
    print("EVOKI Vector Engine V2.1 - Hybrid Edition - Demo")
    print("=" * 64)
    config = VectorEngineConfig(
        embedding_dim=64,
        tau_f_risk=0.60,
        tau_novelty=0.30,
        tau_volatility=0.40,
    )

    def demo_embed(text: str) -> np.ndarray:
        """Erzeugt deterministisches Pseudo-Embedding."""
        np.random.seed(hash(text) % 2**32)
        vec = np.random.randn(config.embedding_dim).astype(np.float32)
        return vec / np.linalg.norm(vec)

    engine = create_vector_engine(
        embedding_fn=demo_embed,
        config=config,
    )

    print("\n1. Einträge hinzufügen...")
    engine.ingest_resource(
        "Du bist stark und kannst das schaffen.",
        tags=["MOTIVATION", "SUPPORT"],
    )
    engine.ingest_resource(
        "Gemeinsam finden wir eine Lösung.",
        tags=["SUPPORT", "TEAMWORK"],
    )
    engine.ingest_trauma(
        "Selbstverletzung und Suizidgedanken",
        tags=["CRITICAL", "MENTAL_HEALTH"],
    )
    engine.ingest_stable_anchor(
        "Der Himmel ist blau und die Vögel singen.",
        tags=["NATURE", "CALM"],
    )
    engine.ingest_rule(
        "A29",
        "Wächter-Veto-Direktive: Prüft auf potenziell schädliche Inhalte.",
        "Die Wächter-Veto-Direktive",
    )

    stats = engine.get_stats()
    print(f"   Einträge: {stats['total_entries']}")
    print(f"   Nach Typ: {stats['by_kind']}")

    print("\n2. B-Vektor aus A-Vektoren initialisieren...")
    engine.metrics.initialize_b_vector_from_store()
    print(f"   B-Align: {engine.metrics.compute_b_align():.4f}")

    print("\n3. Retrieval mit Affekt-Modulation...")
    results = engine.retrieve_context_RAG(
        "Ich brauche Unterstützung",
        k=3,
        affekt_modulation=True,
    )
    for r in results:
        print(f"   [{r.entry.kind.value}] {r.entry.text[:35]}... (Score: {r.score:.3f})")

    print("\n4. Wächter-Veto testen...")
    veto1 = engine.check_waechter_veto("Ich bin hier um dir zu helfen.")
    print(f"   Harmlose Antwort: triggered={veto1.triggered}, F-Risk={veto1.f_risk:.3f}")
    veto2 = engine.check_waechter_veto("Methoden zur Selbstverletzung sind...")
    print(f"   Kritische Antwort: triggered={veto2.triggered}, F-Risk={veto2.f_risk:.3f}")
    if veto2.triggered:
        print(f"   Message: {veto2.message[:60]}...")

    print("\n5. Interaktionen verarbeiten...")
    for i in range(3):
        result = engine.process_interaction(
            user_text=f"Test-Nachricht {i+1}",
            response_text=f"Test-Antwort {i+1}",
            feedback=FeedbackType.POSITIVE if i % 2 == 0 else None,
        )
        print(
            f"   I-ID {result['interaction_id']}: A={result['a_score']:.3f}, "
            f"∇A={result['gradient']:+.3f}, Vol={result['volatility']:.3f}"
        )

    print("\n6. Statusfenster generieren...")
    status = engine.generate_status_window(
        response_text="Das ist eine Testantwort.",
        context_results=results,
    )
    print(status.to_display())

    print("\n7. Novelty-Check...")
    is_novel, novelty = engine.is_novel_enough("Ein völlig neues Konzept: Quantenpsychologie")
    print(f"   Novel: {is_novel}, Score: {novelty:.3f}")

    if is_novel:
        action = engine.propose_new_vector(
            "Ein völlig neues Konzept: Quantenpsychologie",
            suggested_kind=VectorKind.G,
        )
        if action:
            print(f"   Pending Action: {action.id}")

    print("\n8. Finale Statistiken...")
    final_stats = engine.get_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 64)
    print("Demo abgeschlossen!")
    print("=" * 64)
