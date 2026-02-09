# -*- coding: utf-8 -*-
"""
EVOKI Lexika V3 — Drift scanning utilities.
Usage:
  python -m evoki_lexika_v3.drift --root "C:\\Evoki\\..."
"""
from __future__ import annotations
import os, re, argparse
from typing import Dict, Tuple

_SIGNATURES = [
    ("v1_config", re.compile(r"class\s+Thresholds\b|EVOKI\s+LEXIKA\s+&\s+METRIKEN\s+KONFIGURATION\s+V1\.0", re.IGNORECASE)),
    ("v2_1_legacy", re.compile(r"EVOKI\s+GERMAN\s+LEXICON\s+SET\s+V2\.1", re.IGNORECASE)),
    ("v2_2_full", re.compile(r"EVOKI\s+VOLLSTÄNDIGE\s+LEXIKA\s+V2\.2", re.IGNORECASE)),
    ("v3", re.compile(r"EVOKI\s+LEXIKA\s+V3", re.IGNORECASE)),
]

def scan_lexika_versions(root: str, *, exts: Tuple[str, ...] = (".py", ".txt", ".md")) -> Dict[str, int]:
    counts = {name: 0 for name, _ in _SIGNATURES}
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
            for name, pat in _SIGNATURES:
                if pat.search(s):
                    counts[name] += 1
                    break
    return counts

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Root folder to scan")
    args = ap.parse_args()
    res = scan_lexika_versions(args.root)
    print("Lexika drift scan:", args.root)
    for k, v in res.items():
        print(f"  {k:<12}: {v}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
