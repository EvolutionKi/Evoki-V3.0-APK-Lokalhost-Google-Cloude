# -*- coding: utf-8 -*-
"""
evoki_contract_builder.py — Build Contract & Reports from Spec + Engine

Usage (repo root):
    python evoki_contract_builder.py \
        --spec EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md \
        --spectrum spectrum_types.py \
        --registry metrics_registry.py \
        --out contracts_out

Outputs:
- evoki_fullspectrum168_contract.json
- EVOKI_FULLSPECTRUM168_* CSVs
- EVOKI_SPEC_vs_ENGINE_SCHEMA_MISMATCH_REPORT_FINAL7.{md,csv}
- EVOKI_DEPRECATION_LEDGER_V1.{csv,md}

Notes:
- This is a builder script (CI-friendly). It does NOT modify your engine.
"""

from __future__ import annotations

import argparse
from dataclasses import fields
from pathlib import Path
import importlib.util
import json
import re
import sys
from typing import Any, Dict, List, Tuple

import pandas as pd


ID_LINE_PAT = re.compile(r"\*\*ID:\*\*\s*(.+)")
CAT_PAT = re.compile(r"\*\*Kategorie:\*\*\s*(.+)")
RANGE_PAT = re.compile(r"\*\*Range:\*\*\s*(.+)")
RANGE_A_PAT = re.compile(r"\*\*Range \(Schema A\):\*\*\s*(.+)")
RANGE_B_PAT = re.compile(r"\*\*Range \(Schema B\):\*\*\s*(.+)")
SOURCE_PAT = re.compile(r"\*\*Source:\*\*\s*`([^`]+)`")
VERSION_PAT = re.compile(r"\*\*Version:\*\*\s*(.+)")


def classify_range(r: str) -> str:
    r = (r or "").strip()
    if not r:
        return "unknown"
    if r.lower().startswith("enum"):
        return "enum"
    if "hex" in r.lower():
        return "hex"
    if r.strip().startswith("["):
        return "numeric"
    return "other"


def parse_spec(spec_text: str) -> pd.DataFrame:
    lines = spec_text.splitlines()

    # find all sections start indices
    sections: List[Tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        m = ID_LINE_PAT.search(line)
        if not m:
            continue
        id_line = m.group(1).strip()
        mnum = re.search(r"\bm(\d+)_", id_line) or re.search(r"\bm(\d+)\b", id_line)
        if not mnum:
            continue
        mid = int(mnum.group(1))
        sections.append((mid, i, id_line))
    sections.sort(key=lambda x: x[1])

    entries: Dict[int, Dict[str, Any]] = {}
    for idx, (mid, start, id_line) in enumerate(sections):
        end = sections[idx + 1][1] if idx + 1 < len(sections) else len(lines)
        seg = lines[start:end][:60]
        ent: Dict[str, Any] = {"metric_id": mid, "id_line": id_line}
        ids = re.findall(r"\bm\d+_[A-Za-z0-9_]+\b", id_line)
        if ids:
            ent["spec_ids"] = ids
            ent["spec_id_primary"] = ids[0]
            if len(ids) > 1:
                ent["spec_id_secondary"] = ids[1]

        ranges: Dict[str, str] = {}
        for l in seg:
            mc = CAT_PAT.search(l)
            if mc and "category" not in ent:
                ent["category"] = mc.group(1).strip()
            mr = RANGE_PAT.search(l)
            if mr:
                ranges["default"] = mr.group(1).strip()
            mra = RANGE_A_PAT.search(l)
            if mra:
                ranges["schema_a"] = mra.group(1).strip()
            mrb = RANGE_B_PAT.search(l)
            if mrb:
                ranges["schema_b"] = mrb.group(1).strip()
            ms = SOURCE_PAT.search(l)
            if ms and "source" not in ent:
                ent["source"] = ms.group(1).strip()
            mv = VERSION_PAT.search(l)
            if mv and "version" not in ent:
                ent["version"] = mv.group(1).strip()

        ent["range_default"] = ranges.get("default", "")
        ent["range_schema_a"] = ranges.get("schema_a", "")
        ent["range_schema_b"] = ranges.get("schema_b", "")

        entries[mid] = ent

    df = pd.DataFrame([entries[i] for i in sorted(entries.keys())])
    df["spec_ids"] = df["spec_ids"].apply(lambda x: ";".join(x) if isinstance(x, list) else "")
    return df


def load_dataclass(spectrum_path: Path):
    spec = importlib.util.spec_from_file_location("spectrum_types", str(spectrum_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["spectrum_types"] = mod
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    FullSpectrum168 = getattr(mod, "FullSpectrum168")
    return FullSpectrum168


def engine_fields_df(FullSpectrum168) -> pd.DataFrame:
    rows = []
    for f in fields(FullSpectrum168):
        m = re.match(r"^m(\d+)_", f.name)
        if not m:
            continue
        rows.append({"metric_id": int(m.group(1)), "engine_key": f.name, "engine_type": str(f.type)})
    df = pd.DataFrame(rows).sort_values("metric_id")
    df["engine_type_simple"] = df["engine_type"].astype(str).str.replace("<class '", "", regex=False).str.replace("'>", "", regex=False)
    return df


def choose_effective_range(row: Dict[str, Any]) -> Tuple[str, str]:
    et = str(row.get("engine_type_simple", "")).lower()
    rd = str(row.get("range_default", "")).strip()
    ra = str(row.get("range_schema_a", "")).strip()
    rb = str(row.get("range_schema_b", "")).strip()

    if "str" in et:
        # only keep enum/hex
        if rd and classify_range(rd) in ("enum", "hex"):
            return rd, "default"
        if ra and classify_range(ra) in ("enum", "hex"):
            return ra, "schema_a"
        if rb and classify_range(rb) in ("enum", "hex"):
            return rb, "schema_b"
        return "", ""

    if "bool" in et:
        if rd:
            return rd, "default"
        if ra:
            return ra, "schema_a"
        if rb:
            return rb, "schema_b"
        return "", ""

    # numeric
    if rd:
        return rd, "default"
    if "float" in et or "int" in et:
        if rb and classify_range(rb) == "numeric":
            return rb, "schema_b"
        if ra and classify_range(ra) == "numeric":
            return ra, "schema_a"
        if rb:
            return rb, "schema_b"
        if ra:
            return ra, "schema_a"
    if ra:
        return ra, "schema_a"
    if rb:
        return rb, "schema_b"
    return "", ""


def build_contract(spec_df: pd.DataFrame, eng_df: pd.DataFrame) -> pd.DataFrame:
    df = spec_df.merge(eng_df, on="metric_id", how="left")
    df["name_match"] = (df["engine_key"].fillna("") == df["spec_id_primary"].fillna("")) | (df["engine_key"].fillna("") == df["spec_id_secondary"].fillna(""))
    eff = df.apply(lambda r: choose_effective_range(r), axis=1, result_type="expand")
    df["range_effective"] = eff[0]
    df["schema_effective"] = eff[1]
    return df


def write_mismatch_report(df: pd.DataFrame, out_dir: Path, tag: str):
    mismatch = df.loc[~df["name_match"], ["metric_id", "category", "spec_id_primary", "spec_id_secondary", "engine_key", "engine_type_simple", "range_default", "range_effective", "schema_effective", "source", "version"]]
    mismatch_csv = out_dir / f"EVOKI_SPEC_vs_ENGINE_SCHEMA_MISMATCH_REPORT_{tag}.csv"
    mismatch.to_csv(mismatch_csv, index=False)

    total = len(df)
    mism = int((~df["name_match"]).sum())
    by_cat = (df.assign(is_mismatch=~df["name_match"]).groupby("category")["is_mismatch"].agg(total="count", mismatches="sum").reset_index())
    by_cat["matches"] = by_cat["total"] - by_cat["mismatches"]
    by_cat = by_cat.sort_values("mismatches", ascending=False)

    md = []
    md.append(f"# EVOKI – SPEC ↔ ENGINE Schema Mismatch Report ({tag})\n")
    md.append(f"**Total IDs:** {total}  ")
    md.append(f"**Matches:** {total - mism}  ")
    md.append(f"**Mismatches:** {mism}\n")
    md.append("## Mismatch-Verteilung (nach Kategorie)\n")
    md.append("| Kategorie | Total | Matches | Mismatches |")
    md.append("|---|---:|---:|---:|")
    for _, r in by_cat.iterrows():
        md.append(f"| {r['category']} | {int(r['total'])} | {int(r['matches'])} | {int(r['mismatches'])} |")
    md.append("\n## Erste 35 Mismatches (Vorschau)\n")
    md.append("| ID | Kategorie | Spec-Name | Spec-Alt | Engine-Name | Typ | Range(eff) |")
    md.append("|---:|---|---|---|---|---|---|")
    for _, r in mismatch.head(35).iterrows():
        md.append(f"| m{int(r['metric_id'])} | {r['category']} | {r['spec_id_primary']} | {r['spec_id_secondary'] or ''} | {r['engine_key']} | {r['engine_type_simple']} | {r['range_effective'] or r['range_default']} |")
    (out_dir / f"EVOKI_SPEC_vs_ENGINE_SCHEMA_MISMATCH_REPORT_{tag}.md").write_text("\n".join(md), encoding="utf-8")


def write_contract_json(df: pd.DataFrame, out_dir: Path, tag: str):
    items = []
    for _, r in df.sort_values("metric_id").iterrows():
        items.append({
            "metric_id": int(r["metric_id"]),
            "category": r.get("category", "") or "",
            "spec_id_primary": r.get("spec_id_primary", "") or "",
            "spec_id_secondary": r.get("spec_id_secondary", "") or "",
            "engine_key": r.get("engine_key", "") or "",
            "engine_type": r.get("engine_type_simple", "") or "",
            "range_default": r.get("range_default", "") or "",
            "range_schema_a": r.get("range_schema_a", "") or "",
            "range_schema_b": r.get("range_schema_b", "") or "",
            "range_effective": r.get("range_effective", "") or "",
            "schema_effective": r.get("schema_effective", "") or "",
            "source": r.get("source", "") or "",
            "version": r.get("version", "") or "",
            "name_match": bool(r.get("name_match", False)),
        })
    out = {"schema": "EVOKI-FullSpectrum168-Contract", "tag": tag, "items": items}
    (out_dir / "evoki_fullspectrum168_contract.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def write_deprecation_ledger(registry_path: Path, out_dir: Path):
    spec = importlib.util.spec_from_file_location("metrics_registry", str(registry_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["metrics_registry"] = mod
    assert spec and spec.loader
    spec.loader.exec_module(mod)

    reg = mod.get_default_registry()
    semantic_overrides = getattr(reg, "_semantic_overrides", {})
    rows = []
    for alias, canonical in semantic_overrides.items():
        rows.append({
            "alias": alias,
            "canonical": canonical,
            "status": "DEPRECATED_ALIAS" if str(alias).startswith("m") else "SHORTHAND_ALIAS",
            "reason": "Semantic collision / historical spec mismatch — export must remain canonical",
            "introduced_in": "AUDITFIX (FINAL7)",
            "migration_action": "canonicalize on ingress; never export semantic aliases",
        })
    df = pd.DataFrame(rows).sort_values(["status", "alias"])
    df.to_csv(out_dir / "EVOKI_DEPRECATION_LEDGER_V1.csv", index=False)

    md = []
    md.append("# EVOKI – Deprecation Ledger (V1)\n")
    md.append("| Alias | Canonical | Status | Grund |")
    md.append("|---|---|---|---|")
    for _, r in df.iterrows():
        md.append(f"| `{r['alias']}` | `{r['canonical']}` | {r['status']} | {r['reason']} |")
    (out_dir / "EVOKI_DEPRECATION_LEDGER_V1.md").write_text("\n".join(md), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--spectrum", required=True, type=Path)
    ap.add_argument("--registry", required=False, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--tag", default="FINAL7", type=str)
    args = ap.parse_args()

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    spec_text = args.spec.read_text(encoding="utf-8", errors="replace")
    spec_df = parse_spec(spec_text)
    FullSpectrum168 = load_dataclass(args.spectrum)
    eng_df = engine_fields_df(FullSpectrum168)
    contract_df = build_contract(spec_df, eng_df)

    # save CSVs
    spec_df.to_csv(out_dir / f"EVOKI_FULLSPECTRUM168_SPEC_INDEX_{args.tag}.csv", index=False)
    eng_df.to_csv(out_dir / f"EVOKI_FULLSPECTRUM168_ENGINE_FIELDS_{args.tag}.csv", index=False)
    contract_df.to_csv(out_dir / f"EVOKI_FULLSPECTRUM168_CONTRACT_MERGED_{args.tag}.csv", index=False)

    write_mismatch_report(contract_df, out_dir, args.tag)
    write_contract_json(contract_df, out_dir, args.tag)

    if args.registry and args.registry.exists():
        write_deprecation_ledger(args.registry, out_dir)

    print(f"[OK] wrote contract + reports to: {out_dir}")


if __name__ == "__main__":
    main()
