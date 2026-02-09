# -*- coding: utf-8 -*-
"""
genesis_anchor.py — Genesis Anchor (SHA‑256) Utilities

Ziel
----
- Ein *deterministischer* Anchor über eine definierte Dateiliste.
- Unterstützt "Backend vs Frontend Double-Check".

Warum SHA‑256?
--------------
CRC32 ist als Debug/Legacy ok, aber audit-technisch zu schwach (Kollisionen).
SHA‑256 ist Standard für Integritätsanker.

Design
------
- Pro Datei wird SHA‑256 berechnet.
- Der Genesis Anchor ist SHA‑256 über die geordnete Liste:
  "<relpath>|<sha256>\n"
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import hashlib
import json
import os
import time


@dataclass(frozen=True)
class AnchorResult:
    anchor_sha256: str
    files: List[Dict[str, str]]  # [{"path": "...", "sha256":"..."}]
    algorithm: str = "sha256"
    created_at_utc: str = ""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_anchor(repo_root: Path, relpaths: Iterable[str]) -> AnchorResult:
    repo_root = Path(repo_root).resolve()
    entries: List[Dict[str, str]] = []
    lines: List[bytes] = []

    for rp in relpaths:
        p = (repo_root / rp).resolve()
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"Anchor file missing: {rp}")
        digest = sha256_file(p)
        rp_norm = rp.replace("\\", "/")
        entries.append({"path": rp_norm, "sha256": digest})
        lines.append((rp_norm + "|" + digest + "\n").encode("utf-8"))

    anchor = sha256_bytes(b"".join(lines))
    created = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return AnchorResult(anchor_sha256=anchor, files=entries, created_at_utc=created)


def load_manifest(path: Path) -> Optional[Dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None


def write_manifest(path: Path, anchor: AnchorResult, *, extra: Optional[Dict] = None) -> None:
    payload = {
        "algorithm": anchor.algorithm,
        "anchor_sha256": anchor.anchor_sha256,
        "files": anchor.files,
        "created_at_utc": anchor.created_at_utc,
    }
    if extra:
        payload.update(extra)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def verify_against_manifest(repo_root: Path, manifest_path: Path, *, dev_mode: bool = True) -> Tuple[bool, Dict]:
    """
    Returns (ok, details)
    """
    m = load_manifest(manifest_path)
    if not m:
        return False, {"reason": "manifest_missing_or_invalid"}
    relpaths = [f["path"] for f in m.get("files", []) if isinstance(f, dict) and "path" in f]
    if not relpaths:
        return False, {"reason": "manifest_empty_filelist"}

    current = compute_anchor(repo_root, relpaths)
    expected = str(m.get("anchor_sha256", ""))

    ok = current.anchor_sha256 == expected
    return ok, {
        "expected": expected,
        "current": current.anchor_sha256,
        "files": current.files,
        "manifest": str(manifest_path),
    }
