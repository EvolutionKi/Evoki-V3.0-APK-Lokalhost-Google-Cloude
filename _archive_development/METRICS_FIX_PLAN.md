# METRICS FIX PLAN - KEINE FAKE VALUES!

**Quelle:** Dein Metrik-Spezifikations-Dokument (BUCH 1-8)  
**Ziel:** metrics_complete_v3.py auf 100% echte Berechnungen bringen

---

## PHASE 1: KRITISCHE SAFETY METRICS (SOFORT!)

### m110_black_hole - BLACK HOLE LEXIKON FEHLT!
- ❌ **STATUS:** Lexikon existiert NICHT
- ✅ **FIX:** BlackHole_Lexikon aus Spec extrahieren und hinzufügen
- 🔥 **PRIORITÄT:** KRITISCH (Safety-relevant!)

### m116_lix - LIX HARDCODED!
- ❌ **STATUS:** `lix = 30.0` (fake!)
- ✅ **FIX:** Echte LIX-Formel implementieren:
  ```
  LIX = (words/sentences) + (long_words × 100 / words)
  wobei long_words = Wörter mit >6 Buchstaben
  ```

### m105_t_guilt / m106_t_shame - LEXIKA FEHLEN!
- ❌ **STATUS:** Beide return 0.0 (keine Lexika!)
- ✅ **FIX:** Guilt/Shame Lexika aus Trauma-Forschung erstellen

---

## PHASE 2: GRAIN ENGINE (m96-m100)

### m96_grain_word - NICHT IMPLEMENTIERT
- ❌ **STATUS:** `"none"` String statt Score
- ✅ **FIX:** Wort-Komplexität berechnen (Länge/Silben/Frequenz)

### m97_grain_cat - NICHT IMPLEMENTIERT  
- ❌ **STATUS:** `"none"` String
- ✅ **FIX:** Kategorie-Zuweisung aus Lexika

### m98_grain_score - NICHT IMPLEMENTIERT
- ❌ **STATUS:** `0.0` fest
- ✅ **FIX:** Impact-Score berechnen

### m99_grain_impact - NICHT IMPLEMENTIERT
- ❌ **STATUS:** `0.0` fest
- ✅ **FIX:** Emotionale Dichte messen

### m100_causal_1 - NICHT IMPLEMENTIERT
- ❌ **STATUS:** `0.0` fest
- ✅ **FIX:** Kausale Konnektoren zählen ("weil", "daher", etc.)

---

## PHASE 3: FEP / ANDROMATIK (m57-m70)

### m57_tokens_soc - MUSS STATE SEIN!
- ❌ **STATUS:** `0.0` fest
- ✅ **FIX:** State-Variable aus Session, nicht hardcoded

### m58_tokens_log - MUSS STATE SEIN!
- ❌ **STATUS:** `0.0` fest
- ✅ **FIX:** State-Variable aus Session

### m59_p_antrieb - HARDCODED!
- ❌ **STATUS:** `0.5` fest
- ✅ **FIX:** Echte Formel:
  ```
  p_antrieb = (tokens_soc + tokens_log) / 200.0  (wenn stagniert)
  ```
  Braucht: x_fm_prox (Stagnation-Detection)

### m60_delta_tokens - FAKE!
- ❌ **STATUS:** `0.0` fest
- ✅ **FIX:** Token-Änderung aus Lerndynamik:
  ```
  delta = (η × benefit × A) - λ_decay
  benefit = max(0, prev_surprise - curr_surprise)
  ```

### m64_lambda_fep - m70_active_inf - ALLE HARDCODED!
- ❌ **STATUS:** Konstanten (0.5, 0.1, 0.8, etc.)
- ✅ **FIX:** Aus Spec-Formeln berechnen

---

## PHASE 4: PHYSICS (m24-m35)

### m24_zeta - FAKE!
- ❌ **STATUS:** `0.0`
- ✅ **FIX:** `zeta = (1 - z_prox) × A`

### m25_psi - FAKE!
- ❌ **STATUS:** `0.0`
- ✅ **FIX:** `psi = PCI / (1 + token_count/100.0)`

### m26_e_i_proxy - FAKE!
- ❌ **STATUS:** `0.0`
- ✅ **FIX:** `e_i_proxy = |∇A| × (1 - PCI)`

### m28-m35 (phys_1-8) - ALLE FAKE!
- ❌ **STATUS:** Alle `0.0`
- ✅ **FIX:** Echte Berechnungen aus Spec

---

## PHASE 5: INTEGRITY (m36-m39)

### m36_rule_conflict - HARDCODED!
- ❌ **STATUS:** `0.0`
- ✅ **FIX:** `0.5×LL + 0.3×(1-coh) + 0.2×ctx_break`

### m37_rule_stable - HARDCODED!
- ❌ **STATUS:** `1.0`
- ✅ **FIX:** `1.0 - rule_conflict`

### m39_soul_check - HARDCODED!
- ❌ **STATUS:** `True` boolean
- ✅ **FIX:** `soul_integrity × A` (float)

---

## PHASE 6: HYPERMETRICS (m48-m55)

### m47_focus_stability - HARDCODED!
- ❌ **STATUS:** `0.8`
- ✅ **FIX:** `1.0 - ctx_break` (braucht ctx_break Input!)

### m48-m55 (hyp_1-8) - FAST ALLE FAKE!
- ❌ **STATUS:** Meiste `0.0`
- ✅ **FIX:** Echte Formeln aus Spec

---

## PHASE 7: TEXT/META (m116-m130)

### m119_complexity_variance - FAKE!
- ❌ **STATUS:** `0.0`
- ✅ **FIX:** Varianz der Satzlängen berechnen

### m120_topic_drift - FAKE!
- ❌ **STATUS:** `0.0`
- ✅ **FIX:** Kosinus-Distanz zwischen Topics

### m121_self_reference_count - APPROXIMATION!
- ❌ **STATUS:** `LEX * 10` (zu grob)
- ✅ **FIX:** Echte Zählung von "ich", "mich", etc.

### m122-m126 (dyn_1-5) - ALLE FAKE!
- ❌ **STATUS:** Alle `0.0`
- ✅ **FIX:** Dynamik-Metriken implementieren

### m128_token_ratio - HARDCODED!
- ❌ **STATUS:** `1.0`
- ✅ **FIX:** `current_tokens / prev_tokens`

### m129_engagement_score - HARDCODED!
- ❌ **STATUS:** `0.5`
- ✅ **FIX:** Formel aus Spec

### m130_session_depth - FAKE!
- ❌ **STATUS:** `0.0`
- ✅ **FIX:** Turn-Count oder Tiefe-Metrik

---

## PHASE 8: CHRONOS/META (m131-m150) - ALLE FAKE!

❌ **ALLE 20 METRIKEN** sind hardcoded!
✅ **FIX:** Komplette Implementierung aus Spec

---

## PHASE 9: SYNTHESIS (m151-m168) - FAST ALLE FAKE!

❌ **17 von 18 Metriken** sind fake!
✅ **FIX:** System-Metriken aus echten Quellen

---

## IMPLEMENTATION STRATEGY

### Schritt 1: Lexika vervollständigen
- [ ] BlackHole_Lexikon hinzufügen
- [ ] Guilt_Lexikon hinzufügen
- [ ] Shame_Lexikon hinzufügen
- [ ] Causal_Connectors Lexikon hinzufügen

### Schritt 2: Helper-Funktionen
- [ ] calc_LIX() implementieren
- [ ] calc_complexity_variance() implementieren
- [ ] calc_topic_drift() implementieren
- [ ] calc_ctx_break() implementieren

### Schritt 3: State-Management
- [ ] Session-State für tokens_soc/log einführen
- [ ] Prev_spectrum Handling verbessern

### Schritt 4: Systematisches Fixen
Für jede Metrik:
1. Spec-Formel lesen
2. Implementierung schreiben
3. Testen mit Beispiel
4. Dokumentieren

---

## TESTING STRATEGY

Nach jedem Fix:
```python
# Test 1: Panik-Text
text = "Ich habe Panik und kann nicht mehr atmen!"
result = compute_all_metrics(text)
assert result.m101_t_panic > 0.6  # Panik erkannt

# Test 2: Neutral
text = "Das Wetter ist schön heute."
result = compute_all_metrics(text)
assert result.m101_t_panic < 0.2  # Keine Panik

# Test 3: Komplex
text = "Die Implementierung erfordert, dass wir zunächst..."
result = compute_all_metrics(text)
assert result.m116_lix > 40  # Komplexer Text
```

---

## NEXT STEPS (SOFORT)

1. ✅ BlackHole_Lexikon aus Spec extrahieren
2. ✅ LIX-Formel implementieren
3. ✅ Grain-Engine komplett implementieren
4. ✅ FEP Token-System als State einführen
5. ✅ Test-Suite erweitern

**DANN:** Schrittweise alle anderen Phasen durchgehen.

---

**ZIEL:** 100% echte Metriken - KEINE HALLUZINATION!
