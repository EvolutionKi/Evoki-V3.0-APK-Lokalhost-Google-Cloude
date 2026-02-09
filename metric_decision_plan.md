Decision Plan for Metric Removal/Merge

Goals
- Preserve safety-critical behavior and gate logic.
- Reduce redundancy and unused feature cost.
- Avoid breaking downstream dashboards and decisions.

Protected Set (Do Not Remove)
- Core: m1_A, m2_PCI, m4_flow
- Safety: m19_z_prox, m101_t_panic, m104_t_shock, m110_black_hole, m161_commit_action, m168_cum_stress
- Integrity/Gates: m36_rule_conflict, m37_rule_stable, m38_soul_integrity, m151_omega

Preferred Actions
- Merge alias metrics (m48->m46, m50->m37) via registry alias.
- Keep dual-schema IDs but drop Schema B only if never used.
- Remove optional telemetry and meta-markers only after dependency check.

Process
1) Dependency scan: confirm upstream inputs and downstream usage.
2) Impact map: identify gates, thresholds, and dashboards using the metric.
3) Remove or merge in code and registry; update DB schema if needed.
4) Recalibrate thresholds (A29, m161, F_risk) if inputs change.
5) Run regression tests on safety scenarios and quality metrics.

Acceptance Criteria
- No change in safety-critical triggers under test corpus.
- Equivalent decisions from m161 on baseline tests.
- Dashboards continue to render or use alias mapping.
