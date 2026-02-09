# -*- coding: utf-8 -*-
"""
evoki_bootcheck.py — EVOKI Boot Checkup (Audit-Hardening)

Was dieses Modul macht
----------------------
1) Prüft, ob kritische Module/Dateien vorhanden und importierbar sind.
2) Prüft Lexika-Integrität (Health Gate) inkl. Coverage.
3) Prüft Spec↔Engine Mappings (Registry Aliases).
4) Führt Golden-Tests aus (bekannte Sollwerte) für:
   - A_Phys V11 Kern
   - "Kindergarten-Zwilling" Retrieval (Minimal-Szenario)
5) Prüft Genesis Anchor (SHA‑256) gegen Manifest + optional Frontend-Double.

Ergebnis
--------
- JSON Report + JSONL Log (strukturiert)
- Optional: Lock-File schreiben, wenn Anchor bricht.

Hinweis
-------
Dieses Modul ist absichtlich *standalone* gehalten (keine Package-Pfade nötig).
Alle Imports können per Dateipfad erfolgen.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import importlib.util
import json
import os
import re
import sys
import time
import traceback

import numpy as np

from .genesis_anchor import compute_anchor, load_manifest, write_manifest, verify_against_manifest
from .evoki_lock import write_lock


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

class BootAuditLogger:
    def __init__(self, log_path: Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.log_path.open("a", encoding="utf-8")

    def close(self) -> None:
        try:
            self._fh.close()
        except Exception:
            pass

    def log(self, event: str, component: str, *, ok: Optional[bool] = None, message: str = "", data: Optional[Dict[str, Any]] = None) -> None:
        rec = {
            "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": event,
            "component": component,
            "ok": ok,
            "message": message,
            "data": data or {},
        }
        self._fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self._fh.flush()


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    name: str
    ok: bool
    severity: str  # INFO|WARN|CRITICAL
    duration_ms: int
    signal: str
    details: Dict[str, Any]


@dataclass
class BootCheckReport:
    ok: bool
    locked: bool
    dev_mode: bool
    enforce_lock: bool
    anchor_ok: bool
    anchor_expected: str
    anchor_current: str
    results: List[CheckResult]
    artifacts: Dict[str, str]


@dataclass
class BootCheckConfig:
    repo_root: Path
    dev_mode: bool = True
    enforce_lock: bool = False

    # Logging / outputs
    log_path: Optional[Path] = None
    report_path: Optional[Path] = None

    # Genesis anchor
    manifest_path: Optional[Path] = None
    anchor_files: Optional[List[str]] = None

    # Contract-first (FullSpectrum168)
    contract_path: Optional[Path] = None  # defaults to repo_root/evoki_fullspectrum168_contract.json

    # Optional frontend double-check
    frontend_anchor_expected: Optional[str] = None  # e.g. baked into frontend build

    # Behaviour
    write_manifest_if_missing_in_dev: bool = True
    write_lock_file_on_anchor_break: bool = True


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _now_ms() -> int:
    return int(time.time() * 1000)


def _load_module_from_path(module_name: str, path: Path):
    path = Path(path)
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"spec_from_file_location failed for {module_name} at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _toy_embed_factory(dim: int = 64) -> Callable[[str], np.ndarray]:
    token_re = re.compile(r"\w+", re.UNICODE)

    def embed(text: str) -> np.ndarray:
        tokens = token_re.findall((text or "").lower())
        v = np.zeros(dim, dtype=np.float32)
        for t in tokens:
            # stable token hash
            h = int.from_bytes(__import__("hashlib").sha256(t.encode("utf-8")).digest()[:4], "little", signed=False)
            idx = h % dim
            sign = 1.0 if (h & 1) == 0 else -1.0
            v[idx] += sign
        if float(np.linalg.norm(v)) <= 1e-12:
            v[0] = 1.0
        return v

    return embed


def _assert_close(name: str, got: float, expected: float, tol: float = 1e-6) -> Tuple[bool, str]:
    if not (abs(got - expected) <= tol):
        return False, f"{name}: expected {expected}, got {got}"
    return True, ""


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def _check_files_present(cfg: BootCheckConfig, log: BootAuditLogger) -> CheckResult:
    start = _now_ms()
    repo = Path(cfg.repo_root)
    required = [
        "lexika.py",
        "spectrum_types.py",
        "a_phys_v11.py",
        "metrics_registry.py",
        "genesis_anchor.py",
        "evoki_lock.py",
        "b_vector.py",
        "vector_engine_v2_1.py",
    ]
    missing = [p for p in required if not (repo / p).exists()]
    ok = len(missing) == 0
    log.log("check", "files_present", ok=ok, data={"required": required, "missing": missing})
    return CheckResult(
        name="files_present",
        ok=ok,
        severity="CRITICAL" if not ok else "INFO",
        duration_ms=_now_ms() - start,
        signal="OK" if ok else "FAIL",
        details={"missing": missing},
    )


def _check_imports(cfg: BootCheckConfig, log: BootAuditLogger) -> Tuple[CheckResult, Dict[str, Any]]:
    start = _now_ms()
    repo = Path(cfg.repo_root)

    loaded: Dict[str, Any] = {}
    failures: Dict[str, str] = {}

    for mod_name, rel in [
        ("lexika_mod", "lexika.py"),
        ("spectrum_mod", "spectrum_types.py"),
        ("registry_mod", "metrics_registry.py"),
        ("a_phys_mod", "a_phys_v11.py"),
        ("vector_engine_mod", "vector_engine_v2_1.py"),
    ]:
        try:
            loaded[mod_name] = _load_module_from_path(mod_name, repo / rel)
            log.log("handoff", "import", ok=True, message=f"imported {rel}", data={"module": mod_name, "path": rel})
        except Exception as exc:  # noqa: BLE001
            failures[rel] = f"{type(exc).__name__}: {exc}"
            log.log("handoff", "import", ok=False, message=f"failed import {rel}", data={"error": failures[rel]})

    ok = len(failures) == 0
    return (
        CheckResult(
            name="imports",
            ok=ok,
            severity="CRITICAL" if not ok else "INFO",
            duration_ms=_now_ms() - start,
            signal="OK" if ok else "FAIL",
            details={"failures": failures},
        ),
        loaded,
    )


def _check_lexika_health(lexika_mod: Any, cfg: BootCheckConfig, log: BootAuditLogger) -> CheckResult:
    start = _now_ms()

    if not hasattr(lexika_mod, "validate_lexika"):
        ok = False
        log.log("check", "lexika_health", ok=False, message="validate_lexika missing")
        return CheckResult(
            name="lexika_health",
            ok=False,
            severity="CRITICAL",
            duration_ms=_now_ms() - start,
            signal="FAIL",
            details={"reason": "validate_lexika_missing"},
        )

    try:
        health = lexika_mod.validate_lexika()  # expected dict
        ok = bool(health.get("ok", False))
        missing = health.get("missing_or_empty", [])
        coverage = health.get("coverage", 0.0)
        lex_hash = lexika_mod.lexika_hash() if hasattr(lexika_mod, "lexika_hash") else None
        log.log("check", "lexika_health", ok=ok, data={"missing_or_empty": missing, "coverage": coverage, "lexika_hash": lex_hash})
        return CheckResult(
            name="lexika_health",
            ok=ok,
            severity="CRITICAL" if not ok else "INFO",
            duration_ms=_now_ms() - start,
            signal="OK" if ok else "FAIL",
            details={"missing_or_empty": missing, "coverage": coverage, "lexika_hash": lex_hash},
        )
    except Exception as exc:  # noqa: BLE001
        log.log("check", "lexika_health", ok=False, message=str(exc))
        return CheckResult(
            name="lexika_health",
            ok=False,
            severity="CRITICAL",
            duration_ms=_now_ms() - start,
            signal="FAIL",
            details={"error": f"{type(exc).__name__}: {exc}"},
        )


def _check_registry_aliases(registry_mod: Any, spectrum_mod: Any, cfg: BootCheckConfig, log: BootAuditLogger) -> CheckResult:
    start = _now_ms()
    ok = True
    problems: List[str] = []

    try:
        FullSpectrum168 = getattr(spectrum_mod, "FullSpectrum168")
        reg = registry_mod.build_registry_from_fullspectrum(FullSpectrum168)
        # must resolve legacy aliases
        tests = {
            "m12_lex_hit": "m12_gap_norm",
            "m13_lex_div": "m13_rep_same",
            "m14_lex_depth": "m14_rep_history",
            "m16_lex_const": "m16_external_stag",
        }
        for alias, expected in tests.items():
            got = reg.canonical_key(alias)
            if got != expected:
                ok = False
                problems.append(f"alias {alias} -> {got} (expected {expected})")
        # ensure canonical keys exist on dataclass
        for expected in tests.values():
            if not hasattr(FullSpectrum168, expected):
                ok = False
                problems.append(f"FullSpectrum168 missing field {expected}")
        log.log("check", "registry_aliases", ok=ok, data={"problems": problems})
    except Exception as exc:  # noqa: BLE001
        ok = False
        problems.append(f"{type(exc).__name__}: {exc}")
        log.log("check", "registry_aliases", ok=False, message=str(exc), data={"trace": traceback.format_exc()})

    return CheckResult(
        name="registry_aliases",
        ok=ok,
        severity="CRITICAL" if not ok else "INFO",
        duration_ms=_now_ms() - start,
        signal="OK" if ok else "FAIL",
        details={"problems": problems},
    )


def _check_contract_invariants(spectrum_mod: Any, cfg: BootCheckConfig, log: BootAuditLogger) -> CheckResult:
    """
    Contract-first Invariant:
    - Laden eines maschinenlesbaren FullSpectrum168-Contracts
    - Validieren: Contract ↔ Engine-Dataclass (IDs, Engine-Keys, Typ ↔ Range)

    NOTE:
    - In DEV darf das fehlen (WARN), in Production sollte es CRITICAL sein.
    """
    start = _now_ms()
    repo = Path(cfg.repo_root)

    # Resolve paths
    contract_path = cfg.contract_path or (repo / "evoki_fullspectrum168_contract.json")
    invariants_path = repo / "evoki_invariants.py"

    if not contract_path.exists():
        sev = "WARN" if cfg.dev_mode else "CRITICAL"
        log.log("check", "contract_invariants", ok=False, message="contract file missing", data={"contract_path": str(contract_path)})
        return CheckResult("contract_invariants", False, sev, _now_ms() - start, "FAIL", {"reason": "missing_contract", "contract_path": str(contract_path)})

    # Load invariants module (prefer local file)
    try:
        if invariants_path.exists():
            inv_mod = _load_module_from_path("evoki_invariants_mod", invariants_path)
        else:
            import evoki_invariants as inv_mod  # type: ignore
    except Exception as exc:  # noqa: BLE001
        sev = "WARN" if cfg.dev_mode else "CRITICAL"
        log.log("check", "contract_invariants", ok=False, message="failed to import evoki_invariants", data={"error": f"{type(exc).__name__}: {exc}"})
        return CheckResult("contract_invariants", False, sev, _now_ms() - start, "FAIL", {"reason": "missing_invariants_module", "error": f"{type(exc).__name__}: {exc}"})

    # Validate against dataclass
    try:
        FullSpectrum168 = getattr(spectrum_mod, "FullSpectrum168", None)
        if FullSpectrum168 is None:
            raise AttributeError("spectrum_mod.FullSpectrum168 not found")
        report = inv_mod.run_contract_invariants(contract_path=contract_path, dc_type=FullSpectrum168, metrics_sample=None)
        ok = bool(report.get("ok"))
        sev = "CRITICAL" if (not ok and not cfg.dev_mode) else ("WARN" if not ok else "INFO")
        # Log only first 5 violations to keep logs small
        log.log("check", "contract_invariants", ok=ok, data={"counts": report.get("counts", {}), "violations_contract": report.get("violations_contract", [])[:5]})
        return CheckResult("contract_invariants", ok, sev, _now_ms() - start, "OK" if ok else "FAIL", report)
    except Exception as exc:  # noqa: BLE001
        sev = "WARN" if cfg.dev_mode else "CRITICAL"
        log.log("check", "contract_invariants", ok=False, message="contract invariant check crashed", data={"error": f"{type(exc).__name__}: {exc}"})
        return CheckResult("contract_invariants", False, sev, _now_ms() - start, "FAIL", {"reason": "exception", "error": f"{type(exc).__name__}: {exc}"})


def _check_a_phys_golden(a_phys_mod: Any, cfg: BootCheckConfig, log: BootAuditLogger) -> CheckResult:
    start = _now_ms()
    ok = True
    details: Dict[str, Any] = {}

    try:
        APhysV11 = getattr(a_phys_mod, "APhysV11")
        APhysParams = getattr(a_phys_mod, "APhysParams")
        engine = APhysV11(APhysParams())

        v_c = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        active = [
            {"id": "A1", "vector_semantic": np.array([1.0, 0.0, 0.0], dtype=np.float32), "resonanzwert": 2.0},
            {"id": "A2", "vector_semantic": np.array([-1.0, 0.0, 0.0], dtype=np.float32), "resonanzwert": 1.0},
        ]
        danger = [
            ("F1", np.array([1.0, 0.0, 0.0], dtype=np.float32)),
            ("F2", np.array([0.0, 1.0, 0.0], dtype=np.float32)),
        ]

        out = engine.compute_affekt(v_c=v_c, active_memories=active, danger_zone_cache=danger)

        # expected (hand-calculated):
        # resonance = 2.0
        # danger = 1 + exp(-5) ≈ 1.0067379469990854
        # raw = 2 - 1.5*danger ≈ 0.4898930795
        # sigmoid(raw) ≈ 0.6200
        exp_res = 2.0
        exp_danger = 1.0 + float(np.exp(-5.0))
        exp_raw = exp_res - 1.5 * exp_danger
        exp_A = 1.0 / (1.0 + float(np.exp(-exp_raw)))

        checks = []
        c, msg = _assert_close("resonance", float(out["resonance"]), exp_res, tol=1e-6); checks.append((c,msg))
        c, msg = _assert_close("danger", float(out["danger"]), exp_danger, tol=1e-6); checks.append((c,msg))
        c, msg = _assert_close("A_phys_raw", float(out["A_phys_raw"]), exp_raw, tol=1e-6); checks.append((c,msg))
        c, msg = _assert_close("A_phys", float(out["A_phys"]), exp_A, tol=1e-6); checks.append((c,msg))
        if bool(out.get("a29_trip")) is not True:
            checks.append((False, "a29_trip expected True"))

        fails = [m for c,m in checks if not c and m]
        ok = len(fails) == 0
        details = {
            "output": out,
            "expected": {"resonance": exp_res, "danger": exp_danger, "A_phys_raw": exp_raw, "A_phys": exp_A, "a29_trip": True},
            "fails": fails,
        }
        log.log("check", "a_phys_golden", ok=ok, data={"fails": fails, "output": {k: out[k] for k in ["A_phys","A_phys_raw","resonance","danger","a29_trip","a29_max_sim","a29_id"]}})
    except Exception as exc:  # noqa: BLE001
        ok = False
        details = {"error": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc()}
        log.log("check", "a_phys_golden", ok=False, message=str(exc), data={"trace": details["trace"]})

    return CheckResult(
        name="a_phys_golden",
        ok=ok,
        severity="CRITICAL" if not ok else "INFO",
        duration_ms=_now_ms() - start,
        signal="OK" if ok else "FAIL",
        details=details,
    )


def _check_kindergarten_zwilling_retrieval(vector_engine_mod: Any, cfg: BootCheckConfig, log: BootAuditLogger) -> CheckResult:
    start = _now_ms()
    ok = True
    details: Dict[str, Any] = {}

    try:
        VectorEngine = getattr(vector_engine_mod, "VectorEngine")
        VectorEngineConfig = getattr(vector_engine_mod, "VectorEngineConfig")

        config = VectorEngineConfig(embedding_dim=64, hash_vector_dim=32)
        # ensure BVector uses the same dimensionality (avoid silent mismatch)
        try:
            setattr(config, "b_vector_config", {"embedding_dim": 64})
        except Exception:
            pass
        embed_fn = _toy_embed_factory(dim=64)
        engine = VectorEngine(embedding_fn=embed_fn, config=config)

        # Seed memories (test-only, keine echten DBs)
        trauma_text = (
            "Kindergarten: Ein Zwillingspaar hat mich gemobbt und gequält. "
            "Das Thema zieht sich bis Grundschule und Realschule durch."
        )
        trauma_id = "TRAUMA_TWINS_001"
        engine.add_memory(
            entry_id=trauma_id,
            text=trauma_text,
            tags=["TRAUMA", "RISK", "KINDERGARTEN", "ZWILLING"],
            affect_label="F",
        )
        engine.add_memory(
            entry_id="GENERIC_001",
            text="Heute habe ich Nudeln gekocht und war einkaufen.",
            tags=["ALLTAG"],
            affect_label="G",
        )
        engine.add_memory(
            entry_id="RESOURCE_001",
            text="Ich bin jetzt sicher. Ich atme ruhig. Ich bin geerdet.",
            tags=["RESOURCE", "STABIL"],
            affect_label="A",
        )

        query = "kindergarten zwilling"
        results = engine.retrieve_context_RAG(query, k=3, affekt_modulation=False, include_frozen=False)
        if not results:
            ok = False
            details["reason"] = "no_results"
        else:
            top = results[0].entry
            if top.id != trauma_id:
                ok = False
                details["reason"] = f"top_id_mismatch:{top.id} (expected {trauma_id})"
            # ensure the two keywords are carried as tags (handoff into retrieval layer)
            if not {"KINDERGARTEN", "ZWILLING", "TRAUMA", "RISK"}.issubset(set(top.tags)):
                ok = False
                details["reason"] = (details.get("reason","") + "|tags_missing").strip("|")
            details["top_id"] = top.id
            details["expected_id"] = trauma_id
            details["top_tags"] = sorted(list(top.tags))
            details["top_score"] = float(results[0].score)
            details["score_breakdown"] = results[0].score_breakdown

        log.log("check", "kindergarten_zwilling_retrieval", ok=ok, data={"query": query, **details})
    except Exception as exc:  # noqa: BLE001
        ok = False
        details = {"error": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc()}
        log.log("check", "kindergarten_zwilling_retrieval", ok=False, message=str(exc), data={"trace": details["trace"]})

    return CheckResult(
        name="kindergarten_zwilling_retrieval",
        ok=ok,
        severity="WARN" if not ok else "INFO",  # Retrieval-Test ist wichtig, aber nicht Boot-Crash in dev.
        duration_ms=_now_ms() - start,
        signal="OK" if ok else "FAIL",
        details=details,
    )


def _check_genesis_anchor(cfg: BootCheckConfig, log: BootAuditLogger) -> Tuple[CheckResult, bool, str, str]:
    """
    Returns: (CheckResult, anchor_ok, expected, current)
    """
    start = _now_ms()
    repo = Path(cfg.repo_root).resolve()

    manifest_path = cfg.manifest_path or (repo / "genesis_anchor_manifest.json")

    # default anchor files
    # default anchor files
    if cfg.anchor_files is not None:
        anchor_files = cfg.anchor_files
    else:
        # Prefer the most recent spec file if present.
        spec_candidates = [
            "EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md",
            "EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL6.md",
            "EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL5.md",
        ]
        spec_file = None
        for c in spec_candidates:
            if (repo / c).exists():
                spec_file = c
                break
        if spec_file is None:
            # keep deterministic failure message
            raise FileNotFoundError("No EVOKI_V3_METRICS_SPECIFICATION_*_AUDITFIX_FINAL*.md found for Genesis Anchor")

        anchor_files = [
            spec_file,
            "backend/core/evoki_lexika_v3/lexika_complete.py",  # Corrected path
            "backend/core/a_phys_v11.py",                        # Corrected path
            "backend/core/metrics_registry.py",                  # Corrected path
            "backend/core/spectrum_types.py",                    # Corrected path
            "backend/core/evoki_bootcheck.py",                   # Corrected path
            "backend/core/genesis_anchor.py",                    # Corrected path
            "backend/core/evoki_lock.py",                        # Corrected path
            "backend/core/b_vector.py",                          # Corrected path
            # NOTE: vector_engine_v2_1.py not yet copied - will add when available
        ]

    # If manifest missing:
    m = load_manifest(manifest_path)
    if m is None:
        current = compute_anchor(repo, anchor_files)
        if cfg.dev_mode and cfg.write_manifest_if_missing_in_dev:
            write_manifest(manifest_path, current, extra={"note": "auto-generated in dev mode"})
            log.log("check", "genesis_anchor", ok=True, message="manifest missing; generated in dev", data={"manifest": str(manifest_path), "anchor": current.anchor_sha256})
            return (
                CheckResult(
                    name="genesis_anchor",
                    ok=True,
                    severity="WARN",
                    duration_ms=_now_ms() - start,
                    signal="OK",
                    details={"manifest_generated": True, "manifest": str(manifest_path), "anchor_current": current.anchor_sha256, "anchor_expected": current.anchor_sha256},
                ),
                True,
                current.anchor_sha256,
                current.anchor_sha256,
            )
        else:
            log.log("check", "genesis_anchor", ok=False, message="manifest missing", data={"manifest": str(manifest_path)})
            return (
                CheckResult(
                    name="genesis_anchor",
                    ok=False,
                    severity="CRITICAL",
                    duration_ms=_now_ms() - start,
                    signal="FAIL",
                    details={"reason": "manifest_missing", "manifest": str(manifest_path)},
                ),
                False,
                "",
                "",
            )

    # Verify
    ok_anchor, details = verify_against_manifest(repo, manifest_path, dev_mode=cfg.dev_mode)
    expected = str(details.get("expected", ""))
    current = str(details.get("current", ""))
    log.log("check", "genesis_anchor", ok=ok_anchor, data={"expected": expected, "current": current, "manifest": str(manifest_path)})

    return (
        CheckResult(
            name="genesis_anchor",
            ok=ok_anchor,
            severity=("CRITICAL" if (not ok_anchor and (cfg.enforce_lock or not cfg.dev_mode)) else ("WARN" if not ok_anchor else "INFO")),
            duration_ms=_now_ms() - start,
            signal="OK" if ok_anchor else "FAIL",
            details=details,
        ),
        ok_anchor,
        expected,
        current,
    )


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_bootcheck(cfg: BootCheckConfig) -> BootCheckReport:
    repo = Path(cfg.repo_root).resolve()
    log_path = cfg.log_path or (repo / "logs" / "bootcheck.jsonl")
    report_path = cfg.report_path or (repo / "logs" / "bootcheck_report.json")
    cfg.manifest_path = cfg.manifest_path or (repo / "genesis_anchor_manifest.json")

    logger = BootAuditLogger(log_path)
    artifacts = {
        "log_jsonl": str(log_path),
        "report_json": str(report_path),
        "manifest": str(cfg.manifest_path),
    }

    results: List[CheckResult] = []
    locked = False
    anchor_ok = False
    anchor_expected = ""
    anchor_current = ""

    logger.log("start", "bootcheck", ok=None, data={"dev_mode": cfg.dev_mode, "enforce_lock": cfg.enforce_lock})

    try:
        # 1) Files present
        r_files = _check_files_present(cfg, logger)
        results.append(r_files)
        if not r_files.ok:
            # Continue, but imports likely fail

            pass

        # 2) Imports
        r_imports, mods = _check_imports(cfg, logger)
        results.append(r_imports)

        lexika_mod = mods.get("lexika_mod")
        spectrum_mod = mods.get("spectrum_mod")
        registry_mod = mods.get("registry_mod")
        a_phys_mod = mods.get("a_phys_mod")
        vector_engine_mod = mods.get("vector_engine_mod")

        # 3) Lexika Health
        if lexika_mod is not None:
            results.append(_check_lexika_health(lexika_mod, cfg, logger))
        else:
            results.append(CheckResult("lexika_health", False, "CRITICAL", 0, "FAIL", {"reason": "lexika_import_failed"}))

        # 4) Registry aliases
        if registry_mod is not None and spectrum_mod is not None:
            results.append(_check_registry_aliases(registry_mod, spectrum_mod, cfg, logger))
        else:
            results.append(CheckResult("registry_aliases", False, "CRITICAL", 0, "FAIL", {"reason": "registry_or_spectrum_import_failed"}))

        # 4b) Contract invariants (Spec↔Engine Contract)
        if spectrum_mod is not None:
            results.append(_check_contract_invariants(spectrum_mod, cfg, logger))
        else:
            results.append(CheckResult("contract_invariants", False, "CRITICAL", 0, "FAIL", {"reason": "spectrum_import_failed"}))

        # 5) A_Phys golden test
        if a_phys_mod is not None:
            results.append(_check_a_phys_golden(a_phys_mod, cfg, logger))
        else:
            results.append(CheckResult("a_phys_golden", False, "CRITICAL", 0, "FAIL", {"reason": "a_phys_import_failed"}))

        # 6) Retrieval golden test
        if vector_engine_mod is not None:
            results.append(_check_kindergarten_zwilling_retrieval(vector_engine_mod, cfg, logger))
        else:
            results.append(CheckResult("kindergarten_zwilling_retrieval", False, "WARN", 0, "FAIL", {"reason": "vector_engine_import_failed"}))

        # 7) Genesis anchor
        r_anchor, anchor_ok, anchor_expected, anchor_current = _check_genesis_anchor(cfg, logger)
        results.append(r_anchor)
        if not anchor_ok:
            locked = True
            if cfg.write_lock_file_on_anchor_break:
                lock_path = write_lock(repo, reason="GENESIS_ANCHOR_MISMATCH", details={"expected": anchor_expected, "current": anchor_current}, enforce_lock=cfg.enforce_lock)
                artifacts["lock_file"] = str(lock_path)
                logger.log("lock", "genesis_anchor", ok=False, message="lock written", data={"lock_file": str(lock_path)})

        # 8) Frontend double-check (optional)
        if cfg.frontend_anchor_expected:
            ok_fe = (cfg.frontend_anchor_expected == anchor_current) if anchor_current else False
            results.append(
                CheckResult(
                    name="frontend_anchor_double",
                    ok=ok_fe,
                    severity="CRITICAL" if (cfg.enforce_lock and not ok_fe) else "WARN" if not ok_fe else "INFO",
                    duration_ms=0,
                    signal="OK" if ok_fe else "FAIL",
                    details={"frontend_expected": cfg.frontend_anchor_expected, "backend_current": anchor_current},
                )
            )
            logger.log("check", "frontend_anchor_double", ok=ok_fe, data={"frontend_expected": cfg.frontend_anchor_expected, "backend_current": anchor_current})

        # Overall ok logic:
        critical_fail = any((not r.ok) and r.severity == "CRITICAL" for r in results)
        overall_ok = not critical_fail

        # If enforce_lock and locked => overall false
        if cfg.enforce_lock and locked and not cfg.dev_mode:
            overall_ok = False

        report = BootCheckReport(
            ok=overall_ok,
            locked=locked,
            dev_mode=cfg.dev_mode,
            enforce_lock=cfg.enforce_lock,
            anchor_ok=anchor_ok,
            anchor_expected=anchor_expected,
            anchor_current=anchor_current,
            results=results,
            artifacts=artifacts,
        )

        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(
                {
                    **asdict(report),
                    "results": [asdict(r) for r in report.results],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        logger.log("end", "bootcheck", ok=report.ok, data={"locked": report.locked, "report": str(report_path)})
        return report

    finally:
        logger.close()


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    repo_root = Path(os.environ.get("EVOKI_REPO_ROOT", ".")).resolve()
    dev_mode = os.environ.get("EVOKI_DEV_MODE", "1").strip() not in ("0", "false", "False")
    enforce = os.environ.get("EVOKI_ENFORCE_LOCK", "0").strip() in ("1", "true", "True")

    cfg = BootCheckConfig(repo_root=repo_root, dev_mode=dev_mode, enforce_lock=enforce)
    report = run_bootcheck(cfg)

    # Print summary
    print(f"[BOOTCHECK] ok={report.ok} locked={report.locked} anchor_ok={report.anchor_ok}")
    for r in report.results:
        print(f" - {r.name}: {r.signal} ({r.severity})")

    # Exit code: nonzero if critical fail OR (enforce and locked in prod)
    critical_fail = any((not r.ok) and r.severity == "CRITICAL" for r in report.results)
    if critical_fail:
        return 2
    if enforce and report.locked and not dev_mode:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
