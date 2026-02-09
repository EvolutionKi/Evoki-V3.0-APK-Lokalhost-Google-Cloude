CREATE TABLE IF NOT EXISTS vectors (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  embedding BLOB,
  meta_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_vectors_created_at ON vectors(created_at);
