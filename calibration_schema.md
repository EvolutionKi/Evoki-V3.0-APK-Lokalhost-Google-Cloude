# Metric Calibration Layer (Non?Destructive)

**Goal:** Metrics are always measured and logged, but can be *down?weighted* or *disabled* in the **effective layer** without changing historical raw data.

## Prinzip
- **Raw?Layer:** `metrics_raw` (unchanged, historical integrity)
- **Effective?Layer:** calibration rules applied *on read* or *for analytics* (can change anytime)

## Disable / Down?weight
- **Disable:** `enabled=false` (metric ignored in effective scoring)
- **Down?weight:** `weight=0..1` (e.g., 0.3 for untested metrics)
- **Raw logging stays ON** in all cases.

## Transform Types
- `linear`: `y = a*x + b`
- `log`: `y = a*log(1 + b*x)`
- `sigmoid`: `y = 1/(1 + exp(-k*(x-x0)))`
- `power`: `y = x^p`
- `piecewise`: segment mapping for threshold effects

## Recommended Storage
- `metrics_raw(metric_id, value, created_at, actor, version)`
- `metric_calibration_rules(version_id, metric_id, enabled, weight, transform, params_json, clamp_min, clamp_max)`
- Optional `metrics_effective(raw_id, version_id, value)` for speed

## Notes
- You can keep multiple calibration versions for reproducibility.
- Raw data never changes; only interpretation does.