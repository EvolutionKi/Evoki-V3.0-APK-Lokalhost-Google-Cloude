from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Projekt‑Settings.

    Nico, ja: Settings sind langweilig.
    Aber ohne stabile Konstanten driftet selbst die schönste Resonanzmaschine
    irgendwann in Richtung Zufallsgenerator.
    """

    model_config = SettingsConfigDict(env_prefix="EVOKI_", env_file=".env", extra="ignore")

    app_name: str = "EVOKI V3.0 — The Resonance Engine"
    api_prefix: str = "/api/v1"
    integrity_interval_seconds: float = 10.0  # Silent Integrity tick (small but stubborn)

    # Deep Earth root (relative to repo root by default)
    deep_earth_path: str = "../deep_earth"

    # Genesis anchor (repo root)
    genesis_anchor_path: str = "../GENESIS_ANCHOR_V3.md"


settings = Settings()
