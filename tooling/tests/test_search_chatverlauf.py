```python
import json
import sqlite3
from pathlib import Path

import pytest

import sys
from pathlib import Path

# Add automation dir to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts" / "automation"))

from search_chatverlauf import (
    SearchChatverlaufConfig,
    SearchChatverlaufError,
    hash_embed,
    search_chatverlauf,
)


def test_missing_index_raises(tmp_path: Path):
    meta = tmp_path / "meta.json"
    meta.write_text(json.dumps({"chunks": []}), encoding="utf-8")

    cfg = SearchChatverlaufConfig(
        index_path=tmp_path / "missing.npz",
        meta_path=meta,
        db_path=None,
        vector_backend="numpy",
        embedding_backend="hash",
        embedding_dim=16,
    )
    with pytest.raises(SearchChatverlaufError):
        search_chatverlauf("alpha", top_k=3, include_text=False, config=cfg)


def test_numpy_hash_backend_returns_text(tmp_path: Path):
    # Create small deterministic vector index
    try:
        import numpy as np
    except Exception as e:
        pytest.skip(f"numpy not available: {e}")

    index_path = tmp_path / "index.npz"
    meta_path = tmp_path / "meta.json"
    db_path = tmp_path / "chunks.db"

    chunks = [
        {"chunk_id": "c1", "start": 0, "end": 10, "preview": "alpha"},
        {"chunk_id": "c2", "start": 11, "end": 20, "preview": "beta"},
        {"chunk_id": "c3", "start": 21, "end": 30, "preview": "gamma"},
    ]
    vectors = np.vstack([hash_embed(c["preview"], dim=16) for c in chunks]).astype(np.float32)
    np.savez(str(index_path), vectors=vectors)

    meta_path.write_text(json.dumps({"chunks": chunks}, ensure_ascii=False), encoding="utf-8")

    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE chunks (chunk_id TEXT PRIMARY KEY, text TEXT)")
    conn.execute("INSERT INTO chunks(chunk_id, text) VALUES (?, ?)", ("c1", "ALPHA FULL TEXT"))
    conn.execute("INSERT INTO chunks(chunk_id, text) VALUES (?, ?)", ("c2", "BETA FULL TEXT"))
    conn.commit()
    conn.close()

    cfg = SearchChatverlaufConfig(
        index_path=index_path,
        meta_path=meta_path,
        db_path=db_path,
        vector_backend="numpy",
        embedding_backend="hash",
        embedding_dim=16,
    )

    results = search_chatverlauf("alpha", top_k=2, include_text=True, config=cfg)
    assert results, "Expected non-empty results"
    assert results[0]["chunk_id"] == "c1"
    assert results[0].get("text") == "ALPHA FULL TEXT"
