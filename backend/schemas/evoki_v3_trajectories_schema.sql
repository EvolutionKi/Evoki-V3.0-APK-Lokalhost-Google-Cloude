-- EVOKI V3.0 TRAJECTORIES DATABASE SCHEMA
-- Metric Trajectories & Predictions

CREATE TABLE IF NOT EXISTS metric_trajectories (
    trajectory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id TEXT NOT NULL,
    session_id TEXT,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    gradient REAL,
    trend TEXT,
    velocity REAL,
    timestamp TEXT
);

CREATE TABLE IF NOT EXISTS metric_predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id TEXT NOT NULL,
    metric_name TEXT,
    predicted_value REAL,
    confidence REAL,
    horizon INTEGER,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS trajectory_patterns (
    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT,
    pattern_description TEXT,
    occurrence_count INTEGER DEFAULT 1,
    avg_accuracy REAL,
    detected_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_traj_pair ON metric_trajectories(pair_id);
CREATE INDEX IF NOT EXISTS idx_traj_metric ON metric_trajectories(metric_name);
CREATE INDEX IF NOT EXISTS idx_pred_pair ON metric_predictions(pair_id);
