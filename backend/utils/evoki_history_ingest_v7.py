# -*- coding: utf-8 -*-
"""
evoki_history_ingest.py — History Import (File Tree -> SQLite)

Eingabe
-------
Root:
  .../backend/Evoki History/YYYY/MM/DD/Prompt{N}_{role}.txt
Beispiel:
  2025/02/08/Prompt1_user.txt
  2025/02/08/Prompt1_ai.txt

Dateiformat
-----------
Timestamp: 12.08.2025, 00:01:56 MESZ
Speaker: user|ai

<body...>

Ziel
----
- deterministisch importieren
- idempotent (file_path UNIQUE)
- optional: metrics computation hook
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import argparse
import datetime as _dt
import json
import os
import re
import sqlite3
import uuid

TS_RE = re.compile(r"^Timestamp:\s*(\d{2})\.(\d{2})\.(\d{4}),\s*(\d{2}):(\d{2}):(\d{2})\s*(MEZ|MESZ)\s*$", re.IGNORECASE)
SP_RE = re.compile(r"^Speaker:\s*(ai|user|assistant)\s*$", re.IGNORECASE)
FN_RE = re.compile(r"^Prompt(\d+)_([a-z]+)\.txt$", re.IGNORECASE)

def parse_prompt_file(path: Path) -> Dict[str, str]:
    txt = path.read_text(encoding="utf-8", errors="replace")
    lines = txt.splitlines()
    ts_iso = None
    role = None
    body_start = 0

    for i, line in enumerate(lines[:20]):
        m = TS_RE.match(line.strip())
        if m:
            dd, mm, yyyy, HH, MM, SS, tz = m.groups()
            # We store as ISO without timezone for now; keep tz label separately if needed.
            ts_iso = f"{yyyy}-{mm}-{dd}T{HH}:{MM}:{SS}"
            continue
        m2 = SP_RE.match(line.strip())
        if m2:
            role = m2.group(1).lower()
            body_start = i + 2  # skip blank line
            continue

    body = "\n".join(lines[body_start:]).strip()
    return {"ts_iso": ts_iso or "", "role": role or "", "text": body}

def iter_history_files(root: Path) -> Iterable[Tuple[str, str, str, int, Path]]:
    # yields: (yyyy, mm, dd, prompt_num, path)
    for path in root.rglob("Prompt*_*.txt"):
        parts = path.parts
        # Try to locate YYYY/MM/DD in path
        yyyy = mm = dd = None
        for i in range(len(parts)-3):
            if re.fullmatch(r"\d{4}", parts[i]) and re.fullmatch(r"\d{2}", parts[i+1]) and re.fullmatch(r"\d{2}", parts[i+2]):
                yyyy, mm, dd = parts[i], parts[i+1], parts[i+2]
                break
        m = FN_RE.match(path.name)
        if not m or not (yyyy and mm and dd):
            continue
        prompt_num = int(m.group(1))
        yield yyyy, mm, dd, prompt_num, path

def ensure_schema(conn: sqlite3.Connection, schema_sql_path: Path):
    sql = schema_sql_path.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()

def upsert_session(conn: sqlite3.Connection, date_ymd: str, source_root: str) -> str:
    session_id = f"S-{date_ymd}"
    now = _dt.datetime.utcnow().isoformat()
    conn.execute(
        "INSERT OR IGNORE INTO sessions(session_id, date_ymd, source_root, created_at) VALUES (?,?,?,?)",
        (session_id, date_ymd, source_root, now),
    )
    return session_id

def insert_turn(conn: sqlite3.Connection, session_id: str, date_ymd: str, prompt_num: int, role: str, ts_iso: str, text: str, file_path: str) -> Optional[str]:
    turn_id = str(uuid.uuid4())
    now = _dt.datetime.utcnow().isoformat()
    try:
        conn.execute(
            "INSERT INTO turns(turn_id, session_id, ts_iso, date_ymd, prompt_num, role, text, file_path, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (turn_id, session_id, ts_iso, date_ymd, prompt_num, role, text, file_path, now),
        )
        return turn_id
    except sqlite3.IntegrityError:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="History root folder (Evoki History)")
    ap.add_argument("--db", default="evoki_history.sqlite", help="SQLite output path")
    ap.add_argument("--schema", default="evoki_history_schema.sql", help="Schema SQL path")
    ap.add_argument("--dry", action="store_true", help="Do not write, only scan")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    db_path = Path(args.db).expanduser().resolve()
    schema_path = Path(args.schema).expanduser().resolve()

    files = sorted(list(iter_history_files(root)), key=lambda t: (t[0], t[1], t[2], t[3], str(t[4]).lower()))
    print(f"Found {len(files)} prompt files under: {root}")

    if args.dry:
        for item in files[:10]:
            print(item)
        return 0

    conn = sqlite3.connect(str(db_path))
    ensure_schema(conn, schema_path)

    imported = 0
    for yyyy, mm, dd, prompt_num, path in files:
        date_ymd = f"{yyyy}-{mm}-{dd}"
        session_id = upsert_session(conn, date_ymd, str(root))

        parsed = parse_prompt_file(path)
        role = parsed["role"]
        # normalize role naming
        if role == "assistant":
            role = "ai"
        if role not in ("user", "ai"):
            role = "ai" if "_ai" in path.name.lower() else "user"

        tid = insert_turn(
            conn,
            session_id=session_id,
            date_ymd=date_ymd,
            prompt_num=prompt_num,
            role=role,
            ts_iso=parsed["ts_iso"],
            text=parsed["text"],
            file_path=str(path),
        )
        if tid:
            imported += 1

        if imported % 500 == 0:
            conn.commit()
            print(f"Imported {imported}…")

    conn.commit()
    conn.close()
    print(f"Done. Imported new rows: {imported}. DB: {db_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
