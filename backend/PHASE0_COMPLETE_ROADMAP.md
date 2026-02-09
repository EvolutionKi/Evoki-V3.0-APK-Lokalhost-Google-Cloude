# Phase 0 Complete - Implementation Roadmap

## Ground Truth (Audit Results)

**Date:** 2026-02-08  
**Source:** Contract vs. Implementation Audit

### Current Status
- **Total in Contract:** 168 metrics
- **Currently Implemented:** 26 compute functions (7.7% coverage)
- **Missing:** 157 metrics
- **Name Mismatches:** 89 (need alias/rename)

### Implementation by Phase
- Phase 1 (Base): 7 functions
- Phase 2 (Derived): 9 functions
- Phase 3 (Physics): 7 functions
- Phase 4 (Synthesis): 3 functions

---

## Missing Metrics Breakdown (Top Categories)

| Category | Count | Priority |
|----------|-------|----------|
| Dynamics / Meta-Cognition | 9 | P4 |
| Sentiment / Complex | 8 | P3 |
| Sentiment / Plutchik | 7 | P3 |
| Text Analytics / Meta-Cognition | 6 | P4 |
| Hypermetrics / Dyadic | 5 | P1 |
| Hypermetrics / Composite | 5 | P1 |
| FEP / Drive | 4 | P2 |
| Text / Granularity / Sentiment | 4 | P4 |
| Turbidity / Trauma | 4 | P5 |
| Evolution / Sentiment | 3 | P2 |

**Total:** 55 metrics in top 10 categories (33% of missing)

---

## Implementation Strategy

### Priority 1: Core & Hypermetrics (15-20 metrics)
**Goal:** Fix base and hypermetric foundation

1. Fix name mismatches for existing implementations
2. Add missing Hypermetrics (m40-m55 range):
   - Dyadic: h_conv, h_symbol, nabla_dyad, pacing, mirroring
   - Composite: rapport, hyp_1, hyp_4, hyp_7, hyp_8
3. Complete Core missing (m2_PCI, m5_coh, etc. - fix name conflicts)

**Est:** 4-6 hours

### Priority 2: FEP & Evolution (15-20 metrics)
**Goal:** Free Energy Principle + Evolution metrics

1. FEP Decision (m61-m64): U, R, phi_score, pred_error
2. FEP Drive (m65-m68): drive_soc, drive_log, total_drive, drive_balance
3. FEP Learning (m69-m70): learning_rate, decay_factor
4. Evolution Sentiment (m71-m76): resonance, tension, signals

**Est:** 4-6 hours

### Priority 3: Emotions (15-20 metrics)
**Goal:** Complete emotion recognition

1. Plutchik 8 (m77-m84): joy, sadness, anger, fear, trust, disgust, anticipation, surprise
2. Complex (m85-m92): hope, despair, confusion, clarity, acceptance, resistance, coherence, stability
3. Sentiment Meta (m93-m95)

**Est:** 3-4 hours

### Priority 4: Text & Meta-Cognition (20-25 metrics)
**Goal:** Advanced cognitive metrics

1. Text Analytics (m116-m120)
2. Granularity (m96-m99)
3. Meta-Cognition (m122-m130)
4. Dynamics (remaining)

**Est:** 5-7 hours

### Priority 5: Synthesis & System (40-50 metrics)
**Goal:** Final completion

1. Turbidity/Trauma metrics
2. Chronos/Temporal metrics
3. Synthesis quality metrics
4. System health metrics
5. Remaining edge cases

**Est:** 8-10 hours

---

## Name Mismatch Resolution

**89 mismatches identified.** Strategy:

1. **Keep engine names** (m12_gap_norm, m13_rep_same, etc.)
2. **Add spec aliases** in contract registry
3. **Update code references** to use contract names where visible
4. **Internal** can keep engine names

Example:
- Contract: `m12_lex_hit` → Engine: `m12_gap_norm` 
- Decision: Use `m12_gap_norm` in code, document `m12_lex_hit` as alias

---

## Next Actions

1. ✅ Phase 0 Complete - Contract loaded, audit done
2. ⏭️ Start Priority 1: Hypermetrics + Core fixes
3. Create systematic test suite for validation
4. Document progress in task.md after each priority block

---

## Success Metrics (Checkpoints)

- [ ] Priority 1 Complete: 90+ metrics (53%)
- [ ] Priority 2 Complete: 105+ metrics (62%)
- [ ] Priority 3 Complete: 125+ metrics (74%)
- [ ] Priority 4 Complete: 150+ metrics (89%)
- [ ] Priority 5 Complete: 168 metrics (100%)
- [ ] All metrics DYNAMIC (forensic proof)
- [ ] Performance <50ms
- [ ] Bootcheck passes
