-- evoki_history_schema.sql — minimal ingestion schema (SQLite)

PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS sessions (
  session_id TEXT PRIMARY KEY,
  date_ymd TEXT NOT NULL,
  source_root TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS turns (
  turn_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  ts_iso TEXT,
  date_ymd TEXT NOT NULL,
  prompt_num INTEGER,
  role TEXT NOT NULL CHECK(role IN ('user','ai','assistant')),
  text TEXT NOT NULL,
  file_path TEXT UNIQUE,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS metrics (
  turn_id TEXT PRIMARY KEY,
  metrics_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(turn_id) REFERENCES turns(turn_id)
);

CREATE TABLE IF NOT EXISTS embeddings (
  turn_id TEXT PRIMARY KEY,
  model_id TEXT NOT NULL,
  dim INTEGER NOT NULL,
  vector_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(turn_id) REFERENCES turns(turn_id)
);

CREATE TABLE IF NOT EXISTS genesis_chain (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts_iso TEXT NOT NULL,
  prev_hash TEXT,
  content_hash TEXT NOT NULL,
  chain_hash TEXT NOT NULL
);
