#!/usr/bin/env python3
"""
EVOKI Retrieval: Chatverlauf Search (Lib + CLI)

Ziele:
  - Single Source of Truth für Retrieval (MCP Tool + CLI benutzen dieselbe Logik)
  - Produktionspfad: FAISS + Sentence-Transformers (wenn installiert)
  - Deterministische CI-Tests: numpy + hash-embedding (offline, kein Model-Download)

Backends:
  vector_backend:  "faiss" | "numpy"
  embedding_backend: "sentence_transformers" | "hash"

CLI Beispiel:
  python tooling/scripts/automation/search_chatverlauf.py --query "atomic write" --top-k 5 --include-text
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


class SearchChatverlaufError(RuntimeError):
    """Hard failure for retrieval (missing files, deps, schema mismatch, etc.)."""


@dataclass(frozen=True)
class SearchChatverlaufConfig:
    index_path: Path
    meta_path: Path
    db_path: Optional[Path] = None

    # Retrieval controls
    vector_backend: str = "faiss"  # "faiss" | "numpy"
    embedding_backend: str = "sentence_transformers"  # "sentence_transformers" | "hash"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    normalize: bool = True

    # SQLite mapping (optional)
    sqlite_table: str = "chunks"
    sqlite_key_column: str = "chunk_id"
    sqlite_text_column: str = "text"


def _require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise SearchChatverlaufError(f"{label} not found: {path}")


def load_metadata(meta_path: Path) -> List[Dict[str, Any]]:
    _require_file(meta_path, "Metadata JSON")
    try:
        raw = meta_path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(raw)
    except Exception as e:
        raise SearchChatverlaufError(f"Failed to read/parse metadata JSON: {e}") from e

    chunks = data.get("chunks")
    if not isinstance(chunks, list):
        raise SearchChatverlaufError("Metadata JSON schema mismatch: expected top-level key `chunks: list`")
    return chunks


def hash_embed(text: str, dim: int = 384, normalize: bool = True):
    """
    Deterministische Offline-Embedding-Funktion.
    Wichtig: Nicht semantisch “gut”, aber stabil und CI-fähig.
    """
    try:
        import numpy as np
    except Exception as e:
        raise SearchChatverlaufError(f"numpy missing for hash_embed: {e}") from e

    # Generate dim*4 bytes deterministically via chained sha256 blocks
    needed = dim * 4
    buf = bytearray()
    ctr = 0
    base = text.encode("utf-8", errors="replace")
    while len(buf) < needed:
        h = hashlib.sha256(base + b"|" + str(ctr).encode("ascii")).digest()
        buf.extend(h)
        ctr += 1

    # Interpret as uint32 -> map to [-1, 1]
    vals = []
    for i in range(0, needed, 4):
        u = int.from_bytes(buf[i : i + 4], "little", signed=False)
        vals.append(u)
    v = np.array(vals, dtype=np.float32)
    v = (v / (2**32)) * 2.0 - 1.0

    if normalize:
        n = float(np.linalg.norm(v))
        if n > 0:
            v = v / n
    return v.astype(np.float32)


def embed_query(query: str, cfg: SearchChatverlaufConfig):
    if cfg.embedding_backend == "hash":
        return hash_embed(query, dim=cfg.embedding_dim, normalize=cfg.normalize)

    if cfg.embedding_backend == "sentence_transformers":
        try:
            import numpy as np
            from sentence_transformers import SentenceTransformer
        except Exception as e:
            raise SearchChatverlaufError(f"Missing deps for sentence_transformers embedding: {e}") from e

        model = SentenceTransformer(cfg.embedding_model)
        vec = model.encode([query], convert_to_numpy=True)[0].astype(np.float32)
        if cfg.normalize:
            n = float(np.linalg.norm(vec))
            if n > 0:
                vec = vec / n
        return vec

    raise SearchChatverlaufError(f"Unknown embedding_backend: {cfg.embedding_backend}")


def _load_faiss_index(index_path: Path):
    _require_file(index_path, "FAISS index")
    try:
        import faiss  # type: ignore
    except Exception as e:
        raise SearchChatverlaufError(f"faiss missing (cannot load .faiss index): {e}") from e

    try:
        return faiss.read_index(str(index_path))
    except Exception as e:
        raise SearchChatverlaufError(f"Failed to read faiss index: {e}") from e


def _load_numpy_vectors(index_path: Path):
    _require_file(index_path, "Numpy vector index")
    try:
        import numpy as np
    except Exception as e:
        raise SearchChatverlaufError(f"numpy missing for numpy backend: {e}") from e

    try:
        if index_path.suffix.lower() == ".npz":
            data = np.load(str(index_path))
            if "vectors" not in data:
                raise SearchChatverlaufError("npz schema mismatch: expected key `vectors`")
            vectors = data["vectors"]
        elif index_path.suffix.lower() == ".npy":
            vectors = np.load(str(index_path))
        else:
            raise SearchChatverlaufError("numpy backend expects .npz (vectors=...) or .npy matrix")
    except SearchChatverlaufError:
        raise
    except Exception as e:
        raise SearchChatverlaufError(f"Failed to load numpy vectors: {e}") from e

    if vectors.ndim != 2:
        raise SearchChatverlaufError(f"Vector matrix must be 2D; got shape={getattr(vectors, 'shape', None)}")
    return vectors.astype("float32", copy=False)


def vector_search(qvec, top_k: int, cfg: SearchChatverlaufConfig) -> Tuple[List[float], List[int]]:
    """
    Returns (scores, indices) in descending relevance order.
    """
    if top_k <= 0:
        return ([], [])

    if cfg.vector_backend == "faiss":
        try:
            import numpy as np
        except Exception as e:
            raise SearchChatverlaufError(f"numpy missing for faiss search: {e}") from e

        index = _load_faiss_index(cfg.index_path)
        q = qvec.reshape(1, -1).astype(np.float32)
        try:
            distances, indices = index.search(q, int(top_k))
        except Exception as e:
            raise SearchChatverlaufError(f"faiss search failed: {e}") from e

        scores = [float(x) for x in distances[0].tolist()]
        idxs = [int(x) for x in indices[0].tolist()]
        return scores, idxs

    if cfg.vector_backend == "numpy":
        try:
            import numpy as np
        except Exception as e:
            raise SearchChatverlaufError(f"numpy missing for numpy search: {e}") from e

        vectors = _load_numpy_vectors(cfg.index_path)
        q = qvec.astype(np.float32, copy=False)
        if vectors.shape[1] != q.shape[0]:
            raise SearchChatverlaufError(
                f"Embedding dim mismatch: vectors dim={vectors.shape[1]} vs query dim={q.shape[0]}"
            )

        sims = vectors @ q  # dot product
        k = min(int(top_k), int(sims.shape[0]))
        if k <= 0:
            return ([], [])

        # argpartition for top-k (descending), then sort those k
        top = np.argpartition(-sims, kth=k - 1)[:k]
        top_sorted = top[np.argsort(-sims[top])]
        scores = [float(sims[i]) for i in top_sorted.tolist()]
        idxs = [int(i) for i in top_sorted.tolist()]
        return scores, idxs

    raise SearchChatverlaufError(f"Unknown vector_backend: {cfg.vector_backend}")


def _fetch_text(conn: sqlite3.Connection, chunk_id: Any, cfg: SearchChatverlaufConfig) -> Optional[str]:
    try:
        row = conn.execute(
            f"SELECT {cfg.sqlite_text_column} FROM {cfg.sqlite_table} WHERE {cfg.sqlite_key_column} = ?",
            (chunk_id,),
        ).fetchone()
        return row[0] if row else None
    except Exception:
        # Optional; do not hard-fail retrieval on text fetch
        return None


def search_chatverlauf(
    query: str,
    top_k: int = 5,
    include_text: bool = False,
    config: Optional[SearchChatverlaufConfig] = None,
) -> List[Dict[str, Any]]:
    """
    Primary API. Returns list of result dicts:
      {chunk_id, start, end, score, preview, text?}
    """
    if not query or not query.strip():
        raise SearchChatverlaufError("query required")

    if config is None:
        raise SearchChatverlaufError("config required (explicit paths)")

    meta = load_metadata(config.meta_path)
    qvec = embed_query(query.strip(), config)
    scores, idxs = vector_search(qvec, top_k=top_k, cfg=config)

    conn: Optional[sqlite3.Connection] = None
    if include_text and config.db_path and config.db_path.exists():
        conn = sqlite3.connect(str(config.db_path))

    results: List[Dict[str, Any]] = []
    try:
        for idx, score in zip(idxs, scores):
            if idx < 0:
                continue
            if idx >= len(meta):
                # Guard: index might be bigger than metadata list
                continue
            chunk = meta[idx] if isinstance(meta[idx], dict) else {}
            item: Dict[str, Any] = {
                "chunk_id": chunk.get("chunk_id"),
                "start": chunk.get("start"),
                "end": chunk.get("end"),
                "score": float(score),
                "preview": chunk.get("preview", ""),
            }
            if conn and item.get("chunk_id") is not None:
                text = _fetch_text(conn, item["chunk_id"], config)
                if text is not None:
                    item["text"] = text
            results.append(item)
    finally:
        if conn:
            conn.close()

    return results


def _default_repo_root() -> Path:
    """
    Best-effort repo root detection when executed standalone.
    """
    here = Path(__file__).resolve()
    # tooling/scripts/automation/search_chatverlauf.py -> parents[3] == tooling, parents[4] == repo root
    for p in here.parents:
        if (p / "tooling").exists() and (p / "app").exists():
            return p
    # fallback
    return here.parents[4] if len(here.parents) >= 5 else here.parent


def build_default_config(
    index_path: Optional[str] = None,
    meta_path: Optional[str] = None,
    db_path: Optional[str] = None,
    vector_backend: Optional[str] = None,
    embedding_backend: Optional[str] = None,
    embedding_model: Optional[str] = None,
    embedding_dim: Optional[int] = None,
) -> SearchChatverlaufConfig:
    """
    Used by CLI and can be reused by MCP wrapper.
    Defaults target repo-local tooling/data/faiss_indices.
    """
    repo = _default_repo_root()
    base = repo / "tooling" / "data" / "faiss_indices"

    idx = Path(index_path) if index_path else base / "chatverlauf_final_20251020plus_dedup_sorted.faiss"
    meta = Path(meta_path) if meta_path else base / "chatverlauf_final_20251020plus_dedup_sorted.metadata.json"
    db = Path(db_path) if db_path else base / "chatverlauf_final_20251020plus_dedup_sorted.db"

    vb = vector_backend or os.getenv("EVOKI_VECTOR_BACKEND", "")
    eb = embedding_backend or os.getenv("EVOKI_EMBEDDING_BACKEND", "")

    if not vb:
        # Heuristic: by extension
        vb = "faiss" if idx.suffix.lower() == ".faiss" else "numpy"
    if not eb:
        eb = "sentence_transformers"

    return SearchChatverlaufConfig(
        index_path=idx,
        meta_path=meta,
        db_path=db,
        vector_backend=vb,
        embedding_backend=eb,
        embedding_model=embedding_model or os.getenv("EVOKI_EMBED_MODEL", "all-MiniLM-L6-v2"),
        embedding_dim=int(embedding_dim or int(os.getenv("EVOKI_EMBED_DIM", "384"))),
    )


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EVOKI Chatverlauf Retrieval (FAISS+SQLite)")
    p.add_argument("--query", "-q", required=True, help="Search query")
    p.add_argument("--top-k", type=int, default=5, help="Number of results")
    p.add_argument("--include-text", action="store_true", help="Fetch full text from SQLite (if available)")

    p.add_argument("--index", help="Path to FAISS (.faiss) or numpy (.npz/.npy) index")
    p.add_argument("--meta", help="Path to metadata json (expects key `chunks` list)")
    p.add_argument("--db", help="Path to sqlite db (optional)")

    p.add_argument("--vector-backend", choices=["faiss", "numpy"], help="Vector backend")
    p.add_argument("--embedding-backend", choices=["sentence_transformers", "hash"], help="Embedding backend")
    p.add_argument("--embedding-model", default=None, help="SentenceTransformer model name/path")
    p.add_argument("--embedding-dim", type=int, default=None, help="Embedding dim (hash backend / numpy backend)")
    return p.parse_args(list(argv))


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    cfg = build_default_config(
        index_path=args.index,
        meta_path=args.meta,
        db_path=args.db,
        vector_backend=args.vector_backend,
        embedding_backend=args.embedding_backend,
        embedding_model=args.embedding_model,
        embedding_dim=args.embedding_dim,
    )
    try:
        results = search_chatverlauf(
            query=args.query,
            top_k=args.top_k,
            include_text=bool(args.include_text),
            config=cfg,
        )
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    except SearchChatverlaufError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    # Allow running as a script from repo root without PYTHONPATH
    repo = _default_repo_root()
    app_dir = repo / "app"
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    raise SystemExit(main())
