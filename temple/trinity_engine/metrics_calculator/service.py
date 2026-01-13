from __future__ import annotations

from dataclasses import dataclass

from core.soul_physics import SoulPhysics


@dataclass(frozen=True)
class Metrics:
    resonance: float
    tension: float


class MetricsCalculator:
    """Cipher/Antigravity Grenzschicht: Metriken (placeholder).

    Warum hier? Weil Metriken der Unterschied sind zwischen:
    - „Es fühlt sich richtig an“
    und
    - „Es ist messbar und reproduzierbar“

    (Spoiler: nur eins davon hält eine Woche.)
    """

    def __init__(self, soul: SoulPhysics) -> None:
        self._soul = soul

    def calculate(self, prompt: str) -> Metrics:
        # Dummy‑Heuristik: Länge ~ Signalstärke, Wortvarianz ~ Neuheit (grob).
        signal_strength = min(1.0, max(0.05, len(prompt) / 240.0))
        coherence = 0.85  # placeholder
        novelty = min(1.0, max(0.05, len(set(prompt.split())) / 60.0))
        contradiction = 0.10  # placeholder

        resonance = self._soul.calculate_resonance(signal_strength, coherence)
        tension = self._soul.measure_tension(novelty, contradiction)
        return Metrics(resonance=resonance, tension=tension)
