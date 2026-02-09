# EVOKI – Deprecation Ledger (V1)

Diese Tabelle ist **maschinenlesbar** und dient als einzige Quelle für gefährliche Alias-/Rename‑Fälle.

| Alias | Canonical | Status | Grund |
|---|---|---|---|
| `m12_lex_hit` | `m12_gap_norm` | DEPRECATED_ALIAS | Semantic collision / historical spec mismatch — export must remain canonical |
| `m13_lex_div` | `m13_rep_same` | DEPRECATED_ALIAS | Semantic collision / historical spec mismatch — export must remain canonical |
| `m14_lex_depth` | `m14_rep_history` | DEPRECATED_ALIAS | Semantic collision / historical spec mismatch — export must remain canonical |
| `m16_lex_const` | `m16_external_stag` | DEPRECATED_ALIAS | Semantic collision / historical spec mismatch — export must remain canonical |
| `external_stag` | `m16_external_stag` | SHORTHAND_ALIAS | Semantic collision / historical spec mismatch — export must remain canonical |
| `gap_norm` | `m12_gap_norm` | SHORTHAND_ALIAS | Semantic collision / historical spec mismatch — export must remain canonical |
| `rep_history` | `m14_rep_history` | SHORTHAND_ALIAS | Semantic collision / historical spec mismatch — export must remain canonical |
| `rep_same` | `m13_rep_same` | SHORTHAND_ALIAS | Semantic collision / historical spec mismatch — export must remain canonical |