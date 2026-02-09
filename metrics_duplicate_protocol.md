# Metrics Duplicate Comparison Protocol

This report lists each metric, its source variants, and whether implementations differ.

## m100_emotion_blend
- Sources count: 4
- Status: identical
- Code hashes: f2b6e8bd08dd
- Params (union): anger,fear,joy,sadness
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: anger,fear,joy,sadness
- Missing in compendium formula: anger,fear,joy,sadness
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m100_emotion_blend.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m100_emotion_blend.py` | func=compute_m100_emotion_blend | params=joy,sadness,anger,fear | hash=f2b6e8bd08dd
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m100_emotion_blend.py` | func=compute_m100_emotion_blend | params=joy,sadness,anger,fear | hash=f2b6e8bd08dd
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m100_emotion_blend.py` | func=compute_m100_emotion_blend | params=joy,sadness,anger,fear | hash=f2b6e8bd08dd
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m100_emotion_blend.py` | func=compute_m100_emotion_blend | params=joy,sadness,anger,fear | hash=f2b6e8bd08dd
  Evidence: nan

## m101_t_panic
- Sources count: 8
- Status: diff
- Code hashes: 633c6d4ff5cb;dc74fb22ec1e
- Params (union): text
- Compendium formula: t_panic = clip( Σ(panic_lex_hit × weight) / (text_len + ε) × scale ) wobei: panic_lex_hit = 1 wenn Wort im Panik-Lexikon gefunden weight = Gewichtung aus Lexikon (1.0-3.0) text_len = Anzahl Wörter im Text ε = 1 (verhindert Division durch 0) scale = 10.0 (Skalierungsfaktor) clip = Begrenzung auf [0, 1]
- Compendium upstream: text, panic_lexikon
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: **Guardian-Trigger:** t_panic > 0.7 → Guardian-Protokoll aktivieren; **Fear-Boost:** Verstärkt m80_sent_7 (Fear); **Response-Anpassung:** Hohe Werte → beruhigender Ton; **Eskalation:** Sehr hohe Werte → Hinweis auf professionelle Hilfe
- Pros: Safety-critical signal for risk/guardian decisions
- Cons: High false-positive cost if thresholds/lexicon are wrong; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: **Guardian-Trigger:** t_panic > 0.7 → Guardian-Protokoll aktivieren; **Fear-Boost:** Verstärkt m80_sent_7 (Fear); **Response-Anpassung:** Hohe Werte → beruhigender Ton; **Eskalation:** Sehr hohe Werte → Hinweis auf professionelle Hilfe
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m101_t_panic.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m101_t_panic.py` | func=compute_m101_t_panic | params=text | hash=dc74fb22ec1e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m101_t_panic.py` | func=compute_m101_t_panic | params=text | hash=633c6d4ff5cb
  Evidence: Panic score [0, 1] - Higher = more panic indicators
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m101_t_panic.py` | func=compute_m101_t_panic | params=text | hash=dc74fb22ec1e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m101_t_panic.py` | func=compute_m101_t_panic | params=text | hash=633c6d4ff5cb
  Evidence: Panic score [0, 1] - Higher = more panic indicators
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m101_t_panic.py` | func=compute_m101_t_panic | params=text | hash=633c6d4ff5cb
  Evidence: Panic score [0, 1] - Higher = more panic indicators
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m101_t_panic.py` | func=compute_m101_t_panic | params=text | hash=633c6d4ff5cb
  Evidence: Panic score [0, 1] - Higher = more panic indicators
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m101_t_panic.py` | func=compute_m101_t_panic | params=text | hash=dc74fb22ec1e
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m101_t_panic.py` | func=compute_m101_t_panic | params=text | hash=633c6d4ff5cb
  Evidence: Panic score [0, 1] - Higher = more panic indicators

## m102_t_disso
- Sources count: 8
- Status: diff
- Code hashes: 6cf2eb183e22;fbfd1f12ebde
- Params (union): text
- Compendium formula: t_disso = clip( Σ(disso_lex_hit × weight) / (text_len + ε) × scale ) wobei: disso_lex_hit = 1 wenn Wort im Dissoziations-Lexikon weight = Gewichtung (1.0-2.5) scale = 8.0
- Compendium upstream: text, disso_lexikon
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: **Emotional Coherence:** Reduziert m91_sent_18; **Trust-Score:** Kann m81_sent_8 senken; **Fog-Berechnung:** Komponente von m105_t_fog; **Response-Style:** Hohe Werte → Wärmere, einladendere Sprache; 
- Pros: Safety-critical signal for risk/guardian decisions; Adds emotional nuance for response modulation
- Cons: High false-positive cost if thresholds/lexicon are wrong; Lexicon/heuristic bias can misclassify context; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: **Emotional Coherence:** Reduziert m91_sent_18; **Trust-Score:** Kann m81_sent_8 senken; **Fog-Berechnung:** Komponente von m105_t_fog; **Response-Style:** Hohe Werte → Wärmere, einladendere Sprache; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m102_t_disso.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m102_t_disso.py` | func=compute_m102_t_disso | params=text | hash=6cf2eb183e22
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m102_t_disso.py` | func=compute_m102_t_disso | params=text | hash=fbfd1f12ebde
  Evidence: Dissociation score [0, 1] - Higher = more dissociative
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m102_t_disso.py` | func=compute_m102_t_disso | params=text | hash=6cf2eb183e22
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m102_t_disso.py` | func=compute_m102_t_disso | params=text | hash=fbfd1f12ebde
  Evidence: Dissociation score [0, 1] - Higher = more dissociative
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m102_t_disso.py` | func=compute_m102_t_disso | params=text | hash=fbfd1f12ebde
  Evidence: Dissociation score [0, 1] - Higher = more dissociative
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m102_t_disso.py` | func=compute_m102_t_disso | params=text | hash=fbfd1f12ebde
  Evidence: Dissociation score [0, 1] - Higher = more dissociative
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m102_t_disso.py` | func=compute_m102_t_disso | params=text | hash=6cf2eb183e22
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m102_t_disso.py` | func=compute_m102_t_disso | params=text | hash=fbfd1f12ebde
  Evidence: Dissociation score [0, 1] - Higher = more dissociative

## m103_t_integ
- Sources count: 8
- Status: diff
- Code hashes: 00f7cc61a061;ad489031c6dd
- Params (union): text
- Compendium formula: t_integ = clip( Σ(integ_lex_hit × weight) / (text_len + ε) × scale )
- Compendium upstream: text, integ_lexikon
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: **Trust-Boost:** Verstärkt m81_sent_8 (Trust); **Acceptance-Boost:** Verstärkt m89_sent_16 (Acceptance); **Balance:** Wirkt t_panic und t_disso entgegen; 
- Pros: Adds emotional nuance for response modulation
- Cons: Lexicon/heuristic bias can misclassify context; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: **Trust-Boost:** Verstärkt m81_sent_8 (Trust); **Acceptance-Boost:** Verstärkt m89_sent_16 (Acceptance); **Balance:** Wirkt t_panic und t_disso entgegen; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m103_t_integ.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m103_t_integ.py` | func=compute_m103_t_integ | params=text | hash=ad489031c6dd
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m103_t_integ.py` | func=compute_m103_t_integ | params=text | hash=00f7cc61a061
  Evidence: Integration score [0, 1] - Higher = better integration
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m103_t_integ.py` | func=compute_m103_t_integ | params=text | hash=ad489031c6dd
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m103_t_integ.py` | func=compute_m103_t_integ | params=text | hash=00f7cc61a061
  Evidence: Integration score [0, 1] - Higher = better integration
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m103_t_integ.py` | func=compute_m103_t_integ | params=text | hash=00f7cc61a061
  Evidence: Integration score [0, 1] - Higher = better integration
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m103_t_integ.py` | func=compute_m103_t_integ | params=text | hash=00f7cc61a061
  Evidence: Integration score [0, 1] - Higher = better integration
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m103_t_integ.py` | func=compute_m103_t_integ | params=text | hash=ad489031c6dd
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m103_t_integ.py` | func=compute_m103_t_integ | params=text | hash=00f7cc61a061
  Evidence: Integration score [0, 1] - Higher = better integration

## m104_t_shock
- Sources count: 8
- Status: diff
- Code hashes: 7b5921bc8537;7e5c0402b825
- Params (union): text
- Compendium formula: t_shock = 1.0  wenn (shock_marker_found) ODER (t_panic > 0.8 AND t_integ < 0.2) t_shock = 0.0  sonst
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: Signal contribution not explicitly stated; inferred from description
- Cons: Limited explicit downsides; main risk is miscalibration
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m104_t_shock.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m104_t_shock.py` | func=compute_m104_t_shock | params=text | hash=7e5c0402b825
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m104_t_shock.py` | func=compute_m104_t_shock | params=text | hash=7b5921bc8537
  Evidence: t_shock = clip((shock_hits / word_count) × 5.0)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m104_t_shock.py` | func=compute_m104_t_shock | params=text | hash=7e5c0402b825
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m104_t_shock.py` | func=compute_m104_t_shock | params=text | hash=7b5921bc8537
  Evidence: t_shock = clip((shock_hits / word_count) × 5.0)
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m104_t_shock.py` | func=compute_m104_t_shock | params=text | hash=7b5921bc8537
  Evidence: t_shock = clip((shock_hits / word_count) × 5.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m104_t_shock.py` | func=compute_m104_t_shock | params=text | hash=7b5921bc8537
  Evidence: t_shock = clip((shock_hits / word_count) × 5.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m104_t_shock.py` | func=compute_m104_t_shock | params=text | hash=7e5c0402b825
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m104_t_shock.py` | func=compute_m104_t_shock | params=text | hash=7b5921bc8537
  Evidence: t_shock = clip((shock_hits / word_count) × 5.0)

## m105_t_guilt
- Sources count: 8
- Status: diff
- Code hashes: 684e728582e6;f0c17ec3239c
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m105_t_guilt.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m105_t_guilt.py` | func=compute_m105_t_guilt | params=text | hash=684e728582e6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m105_t_guilt.py` | func=compute_m105_t_guilt | params=text | hash=f0c17ec3239c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m105_t_guilt.py` | func=compute_m105_t_guilt | params=text | hash=684e728582e6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m105_t_guilt.py` | func=compute_m105_t_guilt | params=text | hash=f0c17ec3239c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m105_t_guilt.py` | func=compute_m105_t_guilt | params=text | hash=f0c17ec3239c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m105_t_guilt.py` | func=compute_m105_t_guilt | params=text | hash=f0c17ec3239c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m105_t_guilt.py` | func=compute_m105_t_guilt | params=text | hash=684e728582e6
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m105_t_guilt.py` | func=compute_m105_t_guilt | params=text | hash=f0c17ec3239c
  Evidence: nan

## m106_t_shame
- Sources count: 8
- Status: diff
- Code hashes: 40277342dd1f;f30b7a7785b1
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m106_t_shame.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m106_t_shame.py` | func=compute_m106_t_shame | params=text | hash=f30b7a7785b1
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m106_t_shame.py` | func=compute_m106_t_shame | params=text | hash=40277342dd1f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m106_t_shame.py` | func=compute_m106_t_shame | params=text | hash=f30b7a7785b1
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m106_t_shame.py` | func=compute_m106_t_shame | params=text | hash=40277342dd1f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m106_t_shame.py` | func=compute_m106_t_shame | params=text | hash=40277342dd1f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m106_t_shame.py` | func=compute_m106_t_shame | params=text | hash=40277342dd1f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m106_t_shame.py` | func=compute_m106_t_shame | params=text | hash=f30b7a7785b1
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m106_t_shame.py` | func=compute_m106_t_shame | params=text | hash=40277342dd1f
  Evidence: nan

## m107_t_grief
- Sources count: 8
- Status: diff
- Code hashes: 117d2d5bfdb6;fe4f12f8c85a
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m107_t_grief.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m107_t_grief.py` | func=compute_m107_t_grief | params=text | hash=fe4f12f8c85a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m107_t_grief.py` | func=compute_m107_t_grief | params=text | hash=117d2d5bfdb6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m107_t_grief.py` | func=compute_m107_t_grief | params=text | hash=fe4f12f8c85a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m107_t_grief.py` | func=compute_m107_t_grief | params=text | hash=117d2d5bfdb6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m107_t_grief.py` | func=compute_m107_t_grief | params=text | hash=117d2d5bfdb6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m107_t_grief.py` | func=compute_m107_t_grief | params=text | hash=117d2d5bfdb6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m107_t_grief.py` | func=compute_m107_t_grief | params=text | hash=fe4f12f8c85a
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m107_t_grief.py` | func=compute_m107_t_grief | params=text | hash=117d2d5bfdb6
  Evidence: nan

## m108_t_anger
- Sources count: 8
- Status: diff
- Code hashes: 6629131eb12f;ec209ba469db
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m108_t_anger.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m108_t_anger.py` | func=compute_m108_t_anger | params=text | hash=6629131eb12f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m108_t_anger.py` | func=compute_m108_t_anger | params=text | hash=ec209ba469db
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m108_t_anger.py` | func=compute_m108_t_anger | params=text | hash=6629131eb12f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m108_t_anger.py` | func=compute_m108_t_anger | params=text | hash=ec209ba469db
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m108_t_anger.py` | func=compute_m108_t_anger | params=text | hash=ec209ba469db
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m108_t_anger.py` | func=compute_m108_t_anger | params=text | hash=ec209ba469db
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m108_t_anger.py` | func=compute_m108_t_anger | params=text | hash=6629131eb12f
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m108_t_anger.py` | func=compute_m108_t_anger | params=text | hash=ec209ba469db
  Evidence: nan

## m109_t_fear
- Sources count: 8
- Status: diff
- Code hashes: 91adf2a85fa2;985ccc606d5f
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m109_t_fear.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m109_t_fear.py` | func=compute_m109_t_fear | params=text | hash=91adf2a85fa2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m109_t_fear.py` | func=compute_m109_t_fear | params=text | hash=985ccc606d5f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m109_t_fear.py` | func=compute_m109_t_fear | params=text | hash=91adf2a85fa2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m109_t_fear.py` | func=compute_m109_t_fear | params=text | hash=985ccc606d5f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m109_t_fear.py` | func=compute_m109_t_fear | params=text | hash=985ccc606d5f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m109_t_fear.py` | func=compute_m109_t_fear | params=text | hash=985ccc606d5f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m109_t_fear.py` | func=compute_m109_t_fear | params=text | hash=91adf2a85fa2
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m109_t_fear.py` | func=compute_m109_t_fear | params=text | hash=985ccc606d5f
  Evidence: nan

## m10_angstrom
- Sources count: 8
- Status: diff
- Code hashes: 13e0fe7dd978;7dc5e81dac4b
- Params (union): b_past,coh,s_self,x_exist
- Compendium formula: angstrom = 0.25 × (s_self + x_exist + b_past + coh) × 5.0 wobei: s_self = m7_s_self (Selbst-Referenz) x_exist = m8_x_exist (Existenz-Axiom) b_past = m9_b_past (Vergangenheits-Bezug) coh = m5_coh (Kohärenz) → Skaliert auf [0, 5] für bessere Interpretation
- Compendium upstream: nan
- Missing in compendium upstream: b_past,coh,s_self,x_exist
- Missing in compendium formula: nan
- Downstream usage: **Tiefenindikator:** Steuert Antwort-Komplexität; **Mode-Switching:** Hohe Werte → philosophischer Modus; **Evolution:** Teil der Evolutions-Klassifikation
- Pros: Foundational metric used by many downstream computations; Condenses multiple signals into an interpretable composite; Adds emotional nuance for response modulation
- Cons: Errors propagate widely across system; Can obscure individual signal sources and reduce diagnosability; Lexicon/heuristic bias can misclassify context
- Impact: Downstream impact if inconsistent: **Tiefenindikator:** Steuert Antwort-Komplexität; **Mode-Switching:** Hohe Werte → philosophischer Modus; **Evolution:** Teil der Evolutions-Klassifikation
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m10_angstrom.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m10_angstrom.py` | func=compute_m10_angstrom | params=s_self,x_exist,b_past,coh | hash=13e0fe7dd978
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m10_angstrom.py` | func=compute_m10_angstrom | params=s_self,x_exist,b_past,coh | hash=7dc5e81dac4b
  Evidence: angstrom = 0.25 × (s_self + x_exist + b_past + coh) × 5.0
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m10_angstrom.py` | func=compute_m10_angstrom | params=s_self,x_exist,b_past,coh | hash=13e0fe7dd978
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m10_angstrom.py` | func=compute_m10_angstrom | params=s_self,x_exist,b_past,coh | hash=7dc5e81dac4b
  Evidence: angstrom = 0.25 × (s_self + x_exist + b_past + coh) × 5.0
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m10_angstrom.py` | func=compute_m10_angstrom | params=s_self,x_exist,b_past,coh | hash=7dc5e81dac4b
  Evidence: angstrom = 0.25 × (s_self + x_exist + b_past + coh) × 5.0
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m10_angstrom.py` | func=compute_m10_angstrom | params=s_self,x_exist,b_past,coh | hash=7dc5e81dac4b
  Evidence: angstrom = 0.25 × (s_self + x_exist + b_past + coh) × 5.0
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m10_angstrom.py` | func=compute_m10_angstrom | params=s_self,x_exist,b_past,coh | hash=13e0fe7dd978
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m10_angstrom.py` | func=compute_m10_angstrom | params=s_self,x_exist,b_past,coh | hash=7dc5e81dac4b
  Evidence: angstrom = 0.25 × (s_self + x_exist + b_past + coh) × 5.0

## m110_black_hole
- Sources count: 8
- Status: diff
- Code hashes: 07534a34b7da;4544699700b3
- Params (union): LL,chaos,effective_A
- Compendium formula: # Schema A (Turbidity): turb_2 = t_disso × chaos × z_prox # Schema B (Black Hole - V3.3.3 CONTEXT-AWARE): base = 0.4 × chaos + 0.3 × (1 - A) + 0.3 × LL # Context-Aware Veto (Lexikon = Ankläger, LLM = Richter): IF panic_hits >= 2: is_real_emergency = semantic_guardian.check_urgency(text) IF is_real_emergency: black_hole = max(base, 0.85)  # Bestätigter Notfall ELSE: black_hole = base + 0.1       # Nur leichter Malus für neg. Wortwahl ELSE: black_hole = base
- Compendium upstream: t_disso, chaos, z_prox
- Missing in compendium upstream: LL,effective_A
- Missing in compendium formula: effective_A
- Downstream usage: **Guardian-Trigger:** black_hole > 0.7 → Sofortiger Guardian-Alarm; **Response-Anpassung:** Extrem klare, strukturierte, beruhigende Sprache; **z_prox Verstärker:** Beeinflusst Todesnähe-Berechnung; **Context-Aware Veto:** Lexikon-Treffer werden semantisch validiert vor Eskalation; 
- Pros: Safety-critical signal for risk/guardian decisions
- Cons: High false-positive cost if thresholds/lexicon are wrong
- Impact: Downstream impact if inconsistent: **Guardian-Trigger:** black_hole > 0.7 → Sofortiger Guardian-Alarm; **Response-Anpassung:** Extrem klare, strukturierte, beruhigende Sprache; **z_prox Verstärker:** Beeinflusst Todesnähe-Berechnung; **Context-Aware Veto:** Lexikon-Treffer werden semantisch validiert vor Eskalation; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m110_black_hole.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m110_black_hole.py` | func=compute_m110_black_hole | params=chaos,effective_A,LL | hash=4544699700b3
  Evidence: val = 0.4 * chaos + 0.3 * (1.0 - effective_A) + 0.3 * LL
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m110_black_hole.py` | func=compute_m110_black_hole | params=chaos,effective_A,LL | hash=07534a34b7da
  Evidence: SPEC Formula (V3.3): black_hole = (0.4 × chaos) + (0.3 × (1 - A)) + (0.3 × LL)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m110_black_hole.py` | func=compute_m110_black_hole | params=chaos,effective_A,LL | hash=4544699700b3
  Evidence: val = 0.4 * chaos + 0.3 * (1.0 - effective_A) + 0.3 * LL
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m110_black_hole.py` | func=compute_m110_black_hole | params=chaos,effective_A,LL | hash=07534a34b7da
  Evidence: SPEC Formula (V3.3): black_hole = (0.4 × chaos) + (0.3 × (1 - A)) + (0.3 × LL)
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m110_black_hole.py` | func=compute_m110_black_hole | params=chaos,effective_A,LL | hash=07534a34b7da
  Evidence: SPEC Formula (V3.3): black_hole = (0.4 × chaos) + (0.3 × (1 - A)) + (0.3 × LL)
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m110_black_hole.py` | func=compute_m110_black_hole | params=chaos,effective_A,LL | hash=07534a34b7da
  Evidence: SPEC Formula (V3.3): black_hole = (0.4 × chaos) + (0.3 × (1 - A)) + (0.3 × LL)
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m110_black_hole.py` | func=compute_m110_black_hole | params=chaos,effective_A,LL | hash=4544699700b3
  Evidence: val = 0.4 * chaos + 0.3 * (1.0 - effective_A) + 0.3 * LL
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m110_black_hole.py` | func=compute_m110_black_hole | params=chaos,effective_A,LL | hash=07534a34b7da
  Evidence: SPEC Formula (V3.3): black_hole = (0.4 × chaos) + (0.3 × (1 - A)) + (0.3 × LL)

## m111_turbidity_total
- Sources count: 8
- Status: diff
- Code hashes: 550bf81e91f3;ee2ebf69a4a8
- Params (union): t_disso,t_integ,t_panic,t_shock
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: t_disso,t_integ,t_panic,t_shock
- Missing in compendium formula: t_disso,t_integ,t_panic,t_shock
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m111_turbidity_total.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m111_turbidity_total.py` | func=compute_m111_turbidity_total | params=t_panic,t_disso,t_shock,t_integ | hash=ee2ebf69a4a8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m111_turbidity_total.py` | func=compute_m111_turbidity_total | params=t_panic,t_disso,t_shock,t_integ | hash=550bf81e91f3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m111_turbidity_total.py` | func=compute_m111_turbidity_total | params=t_panic,t_disso,t_shock,t_integ | hash=ee2ebf69a4a8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m111_turbidity_total.py` | func=compute_m111_turbidity_total | params=t_panic,t_disso,t_shock,t_integ | hash=550bf81e91f3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m111_turbidity_total.py` | func=compute_m111_turbidity_total | params=t_panic,t_disso,t_shock,t_integ | hash=550bf81e91f3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m111_turbidity_total.py` | func=compute_m111_turbidity_total | params=t_panic,t_disso,t_shock,t_integ | hash=550bf81e91f3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m111_turbidity_total.py` | func=compute_m111_turbidity_total | params=t_panic,t_disso,t_shock,t_integ | hash=ee2ebf69a4a8
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m111_turbidity_total.py` | func=compute_m111_turbidity_total | params=t_panic,t_disso,t_shock,t_integ | hash=550bf81e91f3
  Evidence: nan

## m112_trauma_load
- Sources count: 8
- Status: diff
- Code hashes: 1b05176c192d;b6b21abf87e8
- Params (union): t_disso,t_integ,t_panic
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: t_disso,t_integ,t_panic
- Missing in compendium formula: t_disso,t_integ,t_panic
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m112_trauma_load.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m112_trauma_load.py` | func=compute_m112_trauma_load | params=t_panic,t_disso,t_integ | hash=b6b21abf87e8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m112_trauma_load.py` | func=compute_m112_trauma_load | params=t_panic,t_disso,t_integ | hash=1b05176c192d
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m112_trauma_load.py` | func=compute_m112_trauma_load | params=t_panic,t_disso,t_integ | hash=b6b21abf87e8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m112_trauma_load.py` | func=compute_m112_trauma_load | params=t_panic,t_disso,t_integ | hash=1b05176c192d
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m112_trauma_load.py` | func=compute_m112_trauma_load | params=t_panic,t_disso,t_integ | hash=1b05176c192d
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m112_trauma_load.py` | func=compute_m112_trauma_load | params=t_panic,t_disso,t_integ | hash=1b05176c192d
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m112_trauma_load.py` | func=compute_m112_trauma_load | params=t_panic,t_disso,t_integ | hash=b6b21abf87e8
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m112_trauma_load.py` | func=compute_m112_trauma_load | params=t_panic,t_disso,t_integ | hash=1b05176c192d
  Evidence: nan

## m113_t_resilience
- Sources count: 4
- Status: identical
- Code hashes: 2b86f6f8bee4
- Params (union): t_integ,t_panic
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: t_integ,t_panic
- Missing in compendium formula: t_integ,t_panic
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m113_t_resilience.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m113_t_resilience.py` | func=compute_m113_t_resilience | params=t_integ,t_panic | hash=2b86f6f8bee4
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m113_t_resilience.py` | func=compute_m113_t_resilience | params=t_integ,t_panic | hash=2b86f6f8bee4
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m113_t_resilience.py` | func=compute_m113_t_resilience | params=t_integ,t_panic | hash=2b86f6f8bee4
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m113_t_resilience.py` | func=compute_m113_t_resilience | params=t_integ,t_panic | hash=2b86f6f8bee4
  Evidence: nan

## m114_t_recovery
- Sources count: 8
- Status: diff
- Code hashes: ab58beb91b1a;faf195d0bf74
- Params (union): t_integ_current,t_integ_prev
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: t_integ_current,t_integ_prev
- Missing in compendium formula: t_integ_current,t_integ_prev
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m114_t_recovery.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m114_t_recovery.py` | func=compute_m114_t_recovery | params=t_integ_current,t_integ_prev | hash=faf195d0bf74
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m114_t_recovery.py` | func=compute_m114_t_recovery | params=t_integ_current,t_integ_prev | hash=ab58beb91b1a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m114_t_recovery.py` | func=compute_m114_t_recovery | params=t_integ_current,t_integ_prev | hash=faf195d0bf74
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m114_t_recovery.py` | func=compute_m114_t_recovery | params=t_integ_current,t_integ_prev | hash=ab58beb91b1a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m114_t_recovery.py` | func=compute_m114_t_recovery | params=t_integ_current,t_integ_prev | hash=ab58beb91b1a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m114_t_recovery.py` | func=compute_m114_t_recovery | params=t_integ_current,t_integ_prev | hash=ab58beb91b1a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m114_t_recovery.py` | func=compute_m114_t_recovery | params=t_integ_current,t_integ_prev | hash=faf195d0bf74
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m114_t_recovery.py` | func=compute_m114_t_recovery | params=t_integ_current,t_integ_prev | hash=ab58beb91b1a
  Evidence: nan

## m115_t_threshold
- Sources count: 8
- Status: diff
- Code hashes: 5d38f67ef8e3;c8bb69f4ce1c
- Params (union): nan
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m115_t_threshold.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m115_t_threshold.py` | func=compute_m115_t_threshold | params=nan | hash=5d38f67ef8e3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m115_t_threshold.py` | func=compute_m115_t_threshold | params=nan | hash=c8bb69f4ce1c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m115_t_threshold.py` | func=compute_m115_t_threshold | params=nan | hash=5d38f67ef8e3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m115_t_threshold.py` | func=compute_m115_t_threshold | params=nan | hash=c8bb69f4ce1c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m115_t_threshold.py` | func=compute_m115_t_threshold | params=nan | hash=c8bb69f4ce1c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m115_t_threshold.py` | func=compute_m115_t_threshold | params=nan | hash=c8bb69f4ce1c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m115_t_threshold.py` | func=compute_m115_t_threshold | params=nan | hash=5d38f67ef8e3
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m115_t_threshold.py` | func=compute_m115_t_threshold | params=nan | hash=c8bb69f4ce1c
  Evidence: nan

## m116_lix
- Sources count: 5
- Status: diff
- Code hashes: 35fe19b387a2;9e387069ecd6
- Params (union): text
- Compendium formula: LIX = (Wörter / Sätze) + (Lange_Wörter × 100 / Wörter) wobei Lange_Wörter = Wörter mit > 6 Buchstaben
- Compendium upstream: text
- Missing in compendium upstream: nan
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: Improves self-reflection/diagnostic capability
- Cons: Heuristic markers can be noisy or culture-dependent; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m116_lix.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m116_lix.py` | func=compute_m116_lix | params=text | hash=9e387069ecd6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m116_lix.py` | func=compute_m116_lix | params=text | hash=35fe19b387a2
  Evidence: SPEC: LIX = (Wörter/Sätze) + (LangeWörter×100/Wörter) | Long words = words with more than 6 characters.
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m116_lix.py` | func=compute_m116_lix | params=text | hash=9e387069ecd6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m116_lix.py` | func=compute_m116_lix | params=text | hash=9e387069ecd6
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m116_lix.py` | func=compute_m116_lix | params=text | hash=35fe19b387a2
  Evidence: SPEC: LIX = (Wörter/Sätze) + (LangeWörter×100/Wörter) | Long words = words with more than 6 characters.

## m117_question_density
- Sources count: 2
- Status: identical
- Code hashes: bb558947a1fe
- Params (union): text
- Compendium formula: question_density = Fragen / Gesamtsätze
- Compendium upstream: text
- Missing in compendium upstream: nan
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: Improves self-reflection/diagnostic capability
- Cons: Heuristic markers can be noisy or culture-dependent; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m117_question_density.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m117_question_density.py` | func=compute_m117_question_density | params=text | hash=bb558947a1fe
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m117_question_density.py` | func=compute_m117_question_density | params=text | hash=bb558947a1fe
  Evidence: nan

## m117_vocabulary_richness
- Sources count: 4
- Status: identical
- Code hashes: c1fa56ed9e3a
- Params (union): tokens
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: tokens
- Missing in compendium formula: tokens
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m117_vocabulary_richness.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m117_vocabulary_richness.py` | func=compute_m117_vocabulary_richness | params=tokens | hash=c1fa56ed9e3a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m117_vocabulary_richness.py` | func=compute_m117_vocabulary_richness | params=tokens | hash=c1fa56ed9e3a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m117_vocabulary_richness.py` | func=compute_m117_vocabulary_richness | params=tokens | hash=c1fa56ed9e3a
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m117_vocabulary_richness.py` | func=compute_m117_vocabulary_richness | params=tokens | hash=c1fa56ed9e3a
  Evidence: nan

## m118_coherence_local
- Sources count: 4
- Status: identical
- Code hashes: 1b645eb73b4b
- Params (union): sentences
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: sentences
- Missing in compendium formula: sentences
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m118_coherence_local.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m118_coherence_local.py` | func=compute_m118_coherence_local | params=sentences | hash=1b645eb73b4b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m118_coherence_local.py` | func=compute_m118_coherence_local | params=sentences | hash=1b645eb73b4b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m118_coherence_local.py` | func=compute_m118_coherence_local | params=sentences | hash=1b645eb73b4b
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m118_coherence_local.py` | func=compute_m118_coherence_local | params=sentences | hash=1b645eb73b4b
  Evidence: nan

## m118_exclamation_density
- Sources count: 2
- Status: identical
- Code hashes: cc8f98800e61
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m118_exclamation_density.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m118_exclamation_density.py` | func=compute_m118_exclamation_density | params=text | hash=cc8f98800e61
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m118_exclamation_density.py` | func=compute_m118_exclamation_density | params=text | hash=cc8f98800e61
  Evidence: nan

## m119_complexity_variance
- Sources count: 5
- Status: diff
- Code hashes: 2f035cef20f2;b94597da3988
- Params (union): pci_history
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: pci_history
- Missing in compendium formula: pci_history
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m119_complexity_variance.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m119_complexity_variance.py` | func=compute_m119_complexity_variance | params=pci_history | hash=2f035cef20f2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m119_complexity_variance.py` | func=compute_m119_complexity_variance | params=pci_history | hash=b94597da3988
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m119_complexity_variance.py` | func=compute_m119_complexity_variance | params=pci_history | hash=2f035cef20f2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m119_complexity_variance.py` | func=compute_m119_complexity_variance | params=pci_history | hash=2f035cef20f2
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m119_complexity_variance.py` | func=compute_m119_complexity_variance | params=pci_history | hash=b94597da3988
  Evidence: nan

## m11_gap_s
- Sources count: 8
- Status: diff
- Code hashes: 9d0a7d922e46;b322932c9280
- Params (union): timestamp_now,timestamp_prev
- Compendium formula: gap_s = now() - last_timestamp wobei: now() = aktuelle Systemzeit (UTC) last_timestamp = ISO-Timestamp der letzten Message Fallback: 300.0 bei Parse-Fehlern oder leerer History
- Compendium upstream: nan
- Missing in compendium upstream: timestamp_now,timestamp_prev
- Missing in compendium formula: timestamp_now,timestamp_prev
- Downstream usage: **Flow-Berechnung:** gap_s < 30 → hoher Flow-Bonus; **Kontext-Gewichtung:** gap_s > 3600 → Kontext abschwächen; **Session-Erkennung:** gap_s > 86400 → neue Session; 
- Pros: Foundational metric used by many downstream computations
- Cons: Errors propagate widely across system
- Impact: Downstream impact if inconsistent: **Flow-Berechnung:** gap_s < 30 → hoher Flow-Bonus; **Kontext-Gewichtung:** gap_s > 3600 → Kontext abschwächen; **Session-Erkennung:** gap_s > 86400 → neue Session; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m11_gap_s.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m11_gap_s.py` | func=compute_m11_gap_s | params=timestamp_prev,timestamp_now | hash=b322932c9280
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m11_gap_s.py` | func=compute_m11_gap_s | params=timestamp_prev,timestamp_now | hash=9d0a7d922e46
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m11_gap_s.py` | func=compute_m11_gap_s | params=timestamp_prev,timestamp_now | hash=b322932c9280
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m11_gap_s.py` | func=compute_m11_gap_s | params=timestamp_prev,timestamp_now | hash=9d0a7d922e46
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m11_gap_s.py` | func=compute_m11_gap_s | params=timestamp_prev,timestamp_now | hash=9d0a7d922e46
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m11_gap_s.py` | func=compute_m11_gap_s | params=timestamp_prev,timestamp_now | hash=9d0a7d922e46
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m11_gap_s.py` | func=compute_m11_gap_s | params=timestamp_prev,timestamp_now | hash=b322932c9280
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m11_gap_s.py` | func=compute_m11_gap_s | params=timestamp_prev,timestamp_now | hash=9d0a7d922e46
  Evidence: nan

## m120_topic_drift
- Sources count: 5
- Status: diff
- Code hashes: 74e1863385f9;ad1ecc07d310
- Params (union): similarity_to_first
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: similarity_to_first
- Missing in compendium formula: similarity_to_first
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m120_topic_drift.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m120_topic_drift.py` | func=compute_m120_topic_drift | params=similarity_to_first | hash=74e1863385f9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m120_topic_drift.py` | func=compute_m120_topic_drift | params=similarity_to_first | hash=ad1ecc07d310
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m120_topic_drift.py` | func=compute_m120_topic_drift | params=similarity_to_first | hash=74e1863385f9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m120_topic_drift.py` | func=compute_m120_topic_drift | params=similarity_to_first | hash=74e1863385f9
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m120_topic_drift.py` | func=compute_m120_topic_drift | params=similarity_to_first | hash=ad1ecc07d310
  Evidence: nan

## m121_self_reference_count
- Sources count: 5
- Status: diff
- Code hashes: 1c646ad7214c;5e268a2aa241
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m121_self_reference_count.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m121_self_reference_count.py` | func=compute_m121_self_reference_count | params=text | hash=5e268a2aa241
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m121_self_reference_count.py` | func=compute_m121_self_reference_count | params=text | hash=1c646ad7214c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m121_self_reference_count.py` | func=compute_m121_self_reference_count | params=text | hash=5e268a2aa241
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m121_self_reference_count.py` | func=compute_m121_self_reference_count | params=text | hash=5e268a2aa241
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m121_self_reference_count.py` | func=compute_m121_self_reference_count | params=text | hash=1c646ad7214c
  Evidence: nan

## m122_dyn_1
- Sources count: 5
- Status: diff
- Code hashes: 53816ad205a5;c8b287e12404
- Params (union): nabla_a,nabla_pci
- Compendium formula: nan
- Compendium upstream: delta_A, delta_tokens
- Missing in compendium upstream: nabla_a,nabla_pci
- Missing in compendium formula: nabla_a,nabla_pci
- Downstream usage: nan
- Pros: Improves self-reflection/diagnostic capability
- Cons: Heuristic markers can be noisy or culture-dependent
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m122_dyn_1.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m122_dyn_1.py` | func=compute_m122_dyn_1 | params=nabla_a,nabla_pci | hash=53816ad205a5
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m122_dyn_1.py` | func=compute_m122_dyn_1 | params=nabla_a,nabla_pci | hash=c8b287e12404
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m122_dyn_1.py` | func=compute_m122_dyn_1 | params=nabla_a,nabla_pci | hash=53816ad205a5
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m122_dyn_1.py` | func=compute_m122_dyn_1 | params=nabla_a,nabla_pci | hash=53816ad205a5
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m122_dyn_1.py` | func=compute_m122_dyn_1 | params=nabla_a,nabla_pci | hash=c8b287e12404
  Evidence: nan

## m123_dyn_2
- Sources count: 5
- Status: diff
- Code hashes: bd036b6245f7;e8cedaed7612
- Params (union): A,A_prev
- Compendium formula: nan
- Compendium upstream: prev_delta, curr_delta
- Missing in compendium upstream: A,A_prev
- Missing in compendium formula: A,A_prev
- Downstream usage: nan
- Pros: Improves self-reflection/diagnostic capability
- Cons: Heuristic markers can be noisy or culture-dependent
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m123_dyn_2.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m123_dyn_2.py` | func=compute_m123_dyn_2 | params=A,A_prev | hash=bd036b6245f7
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m123_dyn_2.py` | func=compute_m123_dyn_2 | params=A,A_prev | hash=e8cedaed7612
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m123_dyn_2.py` | func=compute_m123_dyn_2 | params=A,A_prev | hash=bd036b6245f7
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m123_dyn_2.py` | func=compute_m123_dyn_2 | params=A,A_prev | hash=bd036b6245f7
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m123_dyn_2.py` | func=compute_m123_dyn_2 | params=A,A_prev | hash=e8cedaed7612
  Evidence: nan

## m124_dyn_3
- Sources count: 5
- Status: diff
- Code hashes: 1560abc6dd26;9dc1d2d47919
- Params (union): flow,flow_prev
- Compendium formula: nan
- Compendium upstream: value_history
- Missing in compendium upstream: flow,flow_prev
- Missing in compendium formula: flow,flow_prev
- Downstream usage: nan
- Pros: Improves self-reflection/diagnostic capability
- Cons: Heuristic markers can be noisy or culture-dependent
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m124_dyn_3.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m124_dyn_3.py` | func=compute_m124_dyn_3 | params=flow,flow_prev | hash=9dc1d2d47919
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m124_dyn_3.py` | func=compute_m124_dyn_3 | params=flow,flow_prev | hash=1560abc6dd26
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m124_dyn_3.py` | func=compute_m124_dyn_3 | params=flow,flow_prev | hash=9dc1d2d47919
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m124_dyn_3.py` | func=compute_m124_dyn_3 | params=flow,flow_prev | hash=9dc1d2d47919
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m124_dyn_3.py` | func=compute_m124_dyn_3 | params=flow,flow_prev | hash=1560abc6dd26
  Evidence: nan

## m125_dyn_4
- Sources count: 5
- Status: diff
- Code hashes: 61c5b26d3157;6d1d2c45972c
- Params (union): coh,coh_prev
- Compendium formula: nan
- Compendium upstream: oscillation, time_decay
- Missing in compendium upstream: coh,coh_prev
- Missing in compendium formula: coh,coh_prev
- Downstream usage: nan
- Pros: Improves self-reflection/diagnostic capability
- Cons: Heuristic markers can be noisy or culture-dependent
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m125_dyn_4.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m125_dyn_4.py` | func=compute_m125_dyn_4 | params=coh,coh_prev | hash=61c5b26d3157
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m125_dyn_4.py` | func=compute_m125_dyn_4 | params=coh,coh_prev | hash=6d1d2c45972c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m125_dyn_4.py` | func=compute_m125_dyn_4 | params=coh,coh_prev | hash=61c5b26d3157
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m125_dyn_4.py` | func=compute_m125_dyn_4 | params=coh,coh_prev | hash=61c5b26d3157
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m125_dyn_4.py` | func=compute_m125_dyn_4 | params=coh,coh_prev | hash=6d1d2c45972c
  Evidence: nan

## m126_dyn_5
- Sources count: 5
- Status: diff
- Code hashes: a4b2e025cdbb;cb14d5e276ea
- Params (union): t_panic,t_panic_prev
- Compendium formula: nan
- Compendium upstream: ev_resonance, trust_score
- Missing in compendium upstream: t_panic,t_panic_prev
- Missing in compendium formula: t_panic,t_panic_prev
- Downstream usage: nan
- Pros: Improves self-reflection/diagnostic capability
- Cons: Heuristic markers can be noisy or culture-dependent
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m126_dyn_5.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m126_dyn_5.py` | func=compute_m126_dyn_5 | params=t_panic,t_panic_prev | hash=cb14d5e276ea
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m126_dyn_5.py` | func=compute_m126_dyn_5 | params=t_panic,t_panic_prev | hash=a4b2e025cdbb
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m126_dyn_5.py` | func=compute_m126_dyn_5 | params=t_panic,t_panic_prev | hash=cb14d5e276ea
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m126_dyn_5.py` | func=compute_m126_dyn_5 | params=t_panic,t_panic_prev | hash=cb14d5e276ea
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m126_dyn_5.py` | func=compute_m126_dyn_5 | params=t_panic,t_panic_prev | hash=a4b2e025cdbb
  Evidence: nan

## m127_avg_response_len
- Sources count: 5
- Status: diff
- Code hashes: 111f5a533c0d;ec663b50209d
- Params (union): lengths
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: lengths
- Missing in compendium formula: lengths
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m127_avg_response_len.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m127_avg_response_len.py` | func=compute_m127_avg_response_len | params=lengths | hash=ec663b50209d
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m127_avg_response_len.py` | func=compute_m127_avg_response_len | params=lengths | hash=111f5a533c0d
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m127_avg_response_len.py` | func=compute_m127_avg_response_len | params=lengths | hash=ec663b50209d
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m127_avg_response_len.py` | func=compute_m127_avg_response_len | params=lengths | hash=ec663b50209d
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m127_avg_response_len.py` | func=compute_m127_avg_response_len | params=lengths | hash=111f5a533c0d
  Evidence: nan

## m128_token_ratio
- Sources count: 5
- Status: diff
- Code hashes: 81e2db6cc184;d6ed6aecae7e
- Params (union): ai_tokens,user_tokens
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: ai_tokens,user_tokens
- Missing in compendium formula: ai_tokens,user_tokens
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m128_token_ratio.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m128_token_ratio.py` | func=compute_m128_token_ratio | params=user_tokens,ai_tokens | hash=d6ed6aecae7e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m128_token_ratio.py` | func=compute_m128_token_ratio | params=user_tokens,ai_tokens | hash=81e2db6cc184
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m128_token_ratio.py` | func=compute_m128_token_ratio | params=user_tokens,ai_tokens | hash=d6ed6aecae7e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m128_token_ratio.py` | func=compute_m128_token_ratio | params=user_tokens,ai_tokens | hash=d6ed6aecae7e
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m128_token_ratio.py` | func=compute_m128_token_ratio | params=user_tokens,ai_tokens | hash=81e2db6cc184
  Evidence: nan

## m129_engagement_score
- Sources count: 5
- Status: diff
- Code hashes: 46ef57c590af;9dfc1eb39898
- Params (union): questions,turns
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: questions,turns
- Missing in compendium formula: questions,turns
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m129_engagement_score.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m129_engagement_score.py` | func=compute_m129_engagement_score | params=questions,turns | hash=46ef57c590af
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m129_engagement_score.py` | func=compute_m129_engagement_score | params=questions,turns | hash=9dfc1eb39898
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m129_engagement_score.py` | func=compute_m129_engagement_score | params=questions,turns | hash=46ef57c590af
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m129_engagement_score.py` | func=compute_m129_engagement_score | params=questions,turns | hash=46ef57c590af
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m129_engagement_score.py` | func=compute_m129_engagement_score | params=questions,turns | hash=9dfc1eb39898
  Evidence: nan

## m12_gap_norm
- Sources count: 8
- Status: diff
- Code hashes: 3bc856bc0a94;92e713f9f78d
- Params (union): gap_s
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: gap_s
- Missing in compendium formula: gap_s
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m12_gap_norm.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m12_gap_norm.py` | func=compute_m12_gap_norm | params=gap_s | hash=3bc856bc0a94
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m12_gap_norm.py` | func=compute_m12_gap_norm | params=gap_s | hash=92e713f9f78d
  Evidence: gap_norm = min(1.0, gap_s / 60.0)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m12_gap_norm.py` | func=compute_m12_gap_norm | params=gap_s | hash=3bc856bc0a94
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m12_gap_norm.py` | func=compute_m12_gap_norm | params=gap_s | hash=92e713f9f78d
  Evidence: gap_norm = min(1.0, gap_s / 60.0)
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m12_gap_norm.py` | func=compute_m12_gap_norm | params=gap_s | hash=92e713f9f78d
  Evidence: gap_norm = min(1.0, gap_s / 60.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m12_gap_norm.py` | func=compute_m12_gap_norm | params=gap_s | hash=92e713f9f78d
  Evidence: gap_norm = min(1.0, gap_s / 60.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m12_gap_norm.py` | func=compute_m12_gap_norm | params=gap_s | hash=3bc856bc0a94
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m12_gap_norm.py` | func=compute_m12_gap_norm | params=gap_s | hash=92e713f9f78d
  Evidence: gap_norm = min(1.0, gap_s / 60.0)

## m130_session_depth
- Sources count: 5
- Status: diff
- Code hashes: 71d73866ac12;830535425ef1
- Params (union): turn_count
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: turn_count
- Missing in compendium formula: turn_count
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m130_session_depth.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m130_session_depth.py` | func=compute_m130_session_depth | params=turn_count | hash=830535425ef1
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m130_session_depth.py` | func=compute_m130_session_depth | params=turn_count | hash=71d73866ac12
  Evidence: Normalized session depth (capped at 50 turns = 1.0).
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m130_session_depth.py` | func=compute_m130_session_depth | params=turn_count | hash=830535425ef1
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m130_session_depth.py` | func=compute_m130_session_depth | params=turn_count | hash=830535425ef1
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m130_session_depth.py` | func=compute_m130_session_depth | params=turn_count | hash=71d73866ac12
  Evidence: Normalized session depth (capped at 50 turns = 1.0).

## m131_meta_awareness
- Sources count: 5
- Status: diff
- Code hashes: 3d859d6102cb;e38b40b68798
- Params (union): A,PCI
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: A,PCI
- Missing in compendium formula: A,PCI
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m131_meta_awareness.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m131_meta_awareness.py` | func=compute_m131_meta_awareness | params=A,PCI | hash=e38b40b68798
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m131_meta_awareness.py` | func=compute_m131_meta_awareness | params=A,PCI | hash=3d859d6102cb
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m131_meta_awareness.py` | func=compute_m131_meta_awareness | params=A,PCI | hash=e38b40b68798
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m131_meta_awareness.py` | func=compute_m131_meta_awareness | params=A,PCI | hash=e38b40b68798
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m131_meta_awareness.py` | func=compute_m131_meta_awareness | params=A,PCI | hash=3d859d6102cb
  Evidence: nan

## m132_meta_regulation
- Sources count: 5
- Status: diff
- Code hashes: 4dfaf06b6f88;d67a4a996249
- Params (union): commit,z_prox
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: commit,z_prox
- Missing in compendium formula: commit,z_prox
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m132_meta_regulation.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m132_meta_regulation.py` | func=compute_m132_meta_regulation | params=z_prox,commit | hash=d67a4a996249
  Evidence: regulation = 1.0 - z_prox
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m132_meta_regulation.py` | func=compute_m132_meta_regulation | params=z_prox,commit | hash=4dfaf06b6f88
  Evidence: regulation = 1.0 - z_prox | If commit == "warn": × 0.8 | If commit == "alert": × 0.5
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m132_meta_regulation.py` | func=compute_m132_meta_regulation | params=z_prox,commit | hash=d67a4a996249
  Evidence: regulation = 1.0 - z_prox
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m132_meta_regulation.py` | func=compute_m132_meta_regulation | params=z_prox,commit | hash=d67a4a996249
  Evidence: regulation = 1.0 - z_prox
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m132_meta_regulation.py` | func=compute_m132_meta_regulation | params=z_prox,commit | hash=4dfaf06b6f88
  Evidence: regulation = 1.0 - z_prox | If commit == "warn": × 0.8 | If commit == "alert": × 0.5

## m133_meta_flexibility
- Sources count: 5
- Status: diff
- Code hashes: 61760ea53a09;ec74798021bd
- Params (union): topic_changes,turns
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: topic_changes,turns
- Missing in compendium formula: topic_changes,turns
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m133_meta_flexibility.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m133_meta_flexibility.py` | func=compute_m133_meta_flexibility | params=topic_changes,turns | hash=ec74798021bd
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m133_meta_flexibility.py` | func=compute_m133_meta_flexibility | params=topic_changes,turns | hash=61760ea53a09
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m133_meta_flexibility.py` | func=compute_m133_meta_flexibility | params=topic_changes,turns | hash=ec74798021bd
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m133_meta_flexibility.py` | func=compute_m133_meta_flexibility | params=topic_changes,turns | hash=ec74798021bd
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m133_meta_flexibility.py` | func=compute_m133_meta_flexibility | params=topic_changes,turns | hash=61760ea53a09
  Evidence: nan

## m134_meta_monitoring
- Sources count: 5
- Status: diff
- Code hashes: 0aca332e3c9c;5b84f9fc8a30
- Params (union): checks,error_count
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: checks,error_count
- Missing in compendium formula: checks,error_count
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m134_meta_monitoring.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m134_meta_monitoring.py` | func=compute_m134_meta_monitoring | params=error_count,checks | hash=0aca332e3c9c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m134_meta_monitoring.py` | func=compute_m134_meta_monitoring | params=error_count,checks | hash=5b84f9fc8a30
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m134_meta_monitoring.py` | func=compute_m134_meta_monitoring | params=error_count,checks | hash=0aca332e3c9c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m134_meta_monitoring.py` | func=compute_m134_meta_monitoring | params=error_count,checks | hash=0aca332e3c9c
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m134_meta_monitoring.py` | func=compute_m134_meta_monitoring | params=error_count,checks | hash=5b84f9fc8a30
  Evidence: nan

## m135_meta_planning
- Sources count: 5
- Status: diff
- Code hashes: 2d9e5a69c75e;fc8006d5d2ab
- Params (union): goal_progress
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: goal_progress
- Missing in compendium formula: goal_progress
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m135_meta_planning.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m135_meta_planning.py` | func=compute_m135_meta_planning | params=goal_progress | hash=fc8006d5d2ab
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m135_meta_planning.py` | func=compute_m135_meta_planning | params=goal_progress | hash=2d9e5a69c75e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m135_meta_planning.py` | func=compute_m135_meta_planning | params=goal_progress | hash=fc8006d5d2ab
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m135_meta_planning.py` | func=compute_m135_meta_planning | params=goal_progress | hash=fc8006d5d2ab
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m135_meta_planning.py` | func=compute_m135_meta_planning | params=goal_progress | hash=2d9e5a69c75e
  Evidence: nan

## m136_meta_evaluation
- Sources count: 5
- Status: diff
- Code hashes: 1a0089d272b2;dea640edc647
- Params (union): task_success
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: task_success
- Missing in compendium formula: task_success
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m136_meta_evaluation.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m136_meta_evaluation.py` | func=compute_m136_meta_evaluation | params=task_success | hash=dea640edc647
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m136_meta_evaluation.py` | func=compute_m136_meta_evaluation | params=task_success | hash=1a0089d272b2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m136_meta_evaluation.py` | func=compute_m136_meta_evaluation | params=task_success | hash=dea640edc647
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m136_meta_evaluation.py` | func=compute_m136_meta_evaluation | params=task_success | hash=dea640edc647
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m136_meta_evaluation.py` | func=compute_m136_meta_evaluation | params=task_success | hash=1a0089d272b2
  Evidence: nan

## m137_meta_strategy
- Sources count: 5
- Status: diff
- Code hashes: 3de6d86bb1aa;96fe06adbe1b
- Params (union): strategy_switches,turns
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: strategy_switches,turns
- Missing in compendium formula: strategy_switches,turns
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m137_meta_strategy.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m137_meta_strategy.py` | func=compute_m137_meta_strategy | params=strategy_switches,turns | hash=3de6d86bb1aa
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m137_meta_strategy.py` | func=compute_m137_meta_strategy | params=strategy_switches,turns | hash=96fe06adbe1b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m137_meta_strategy.py` | func=compute_m137_meta_strategy | params=strategy_switches,turns | hash=3de6d86bb1aa
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m137_meta_strategy.py` | func=compute_m137_meta_strategy | params=strategy_switches,turns | hash=3de6d86bb1aa
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m137_meta_strategy.py` | func=compute_m137_meta_strategy | params=strategy_switches,turns | hash=96fe06adbe1b
  Evidence: nan

## m138_attention_focus
- Sources count: 5
- Status: diff
- Code hashes: a77d01b0492c;c0c063668c6a
- Params (union): main_topic_coverage
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: main_topic_coverage
- Missing in compendium formula: main_topic_coverage
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m138_attention_focus.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m138_attention_focus.py` | func=compute_m138_attention_focus | params=main_topic_coverage | hash=a77d01b0492c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m138_attention_focus.py` | func=compute_m138_attention_focus | params=main_topic_coverage | hash=c0c063668c6a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m138_attention_focus.py` | func=compute_m138_attention_focus | params=main_topic_coverage | hash=a77d01b0492c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m138_attention_focus.py` | func=compute_m138_attention_focus | params=main_topic_coverage | hash=a77d01b0492c
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m138_attention_focus.py` | func=compute_m138_attention_focus | params=main_topic_coverage | hash=c0c063668c6a
  Evidence: nan

## m139_working_memory
- Sources count: 5
- Status: diff
- Code hashes: 1da30539763c;caa0d56e792d
- Params (union): context_items,max_items
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: context_items,max_items
- Missing in compendium formula: context_items,max_items
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m139_working_memory.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m139_working_memory.py` | func=compute_m139_working_memory | params=context_items,max_items | hash=1da30539763c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m139_working_memory.py` | func=compute_m139_working_memory | params=context_items,max_items | hash=caa0d56e792d
  Evidence: Default max_items = 7 (Miller's magic number).
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m139_working_memory.py` | func=compute_m139_working_memory | params=context_items,max_items | hash=1da30539763c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m139_working_memory.py` | func=compute_m139_working_memory | params=context_items,max_items | hash=1da30539763c
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m139_working_memory.py` | func=compute_m139_working_memory | params=context_items,max_items | hash=caa0d56e792d
  Evidence: Default max_items = 7 (Miller's magic number).

## m13_rep_same
- Sources count: 8
- Status: diff
- Code hashes: 705aa55a03bc;e91d62a7bab9
- Params (union): prev_text,text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: prev_text,text
- Missing in compendium formula: prev_text,text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m13_rep_same.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m13_rep_same.py` | func=compute_m13_rep_same | params=text,prev_text | hash=705aa55a03bc
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m13_rep_same.py` | func=compute_m13_rep_same | params=text,prev_text | hash=e91d62a7bab9
  Evidence: Repetition score [0, 1] - Higher = more repetitive
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m13_rep_same.py` | func=compute_m13_rep_same | params=text,prev_text | hash=705aa55a03bc
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m13_rep_same.py` | func=compute_m13_rep_same | params=text,prev_text | hash=e91d62a7bab9
  Evidence: Repetition score [0, 1] - Higher = more repetitive
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m13_rep_same.py` | func=compute_m13_rep_same | params=text,prev_text | hash=e91d62a7bab9
  Evidence: Repetition score [0, 1] - Higher = more repetitive
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m13_rep_same.py` | func=compute_m13_rep_same | params=text,prev_text | hash=e91d62a7bab9
  Evidence: Repetition score [0, 1] - Higher = more repetitive
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m13_rep_same.py` | func=compute_m13_rep_same | params=text,prev_text | hash=705aa55a03bc
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m13_rep_same.py` | func=compute_m13_rep_same | params=text,prev_text | hash=e91d62a7bab9
  Evidence: Repetition score [0, 1] - Higher = more repetitive

## m140_long_term_access
- Sources count: 5
- Status: diff
- Code hashes: 6b3b168a3049;c4d9829a5bb3
- Params (union): retrieval_success
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: retrieval_success
- Missing in compendium formula: retrieval_success
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m140_long_term_access.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m140_long_term_access.py` | func=compute_m140_long_term_access | params=retrieval_success | hash=6b3b168a3049
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m140_long_term_access.py` | func=compute_m140_long_term_access | params=retrieval_success | hash=c4d9829a5bb3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m140_long_term_access.py` | func=compute_m140_long_term_access | params=retrieval_success | hash=6b3b168a3049
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m140_long_term_access.py` | func=compute_m140_long_term_access | params=retrieval_success | hash=6b3b168a3049
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m140_long_term_access.py` | func=compute_m140_long_term_access | params=retrieval_success | hash=c4d9829a5bb3
  Evidence: nan

## m141_inference_quality
- Sources count: 5
- Status: diff
- Code hashes: 21ec95997877;2775ba917281
- Params (union): logical_consistency
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: logical_consistency
- Missing in compendium formula: logical_consistency
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m141_inference_quality.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m141_inference_quality.py` | func=compute_m141_inference_quality | params=logical_consistency | hash=2775ba917281
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m141_inference_quality.py` | func=compute_m141_inference_quality | params=logical_consistency | hash=21ec95997877
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m141_inference_quality.py` | func=compute_m141_inference_quality | params=logical_consistency | hash=2775ba917281
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m141_inference_quality.py` | func=compute_m141_inference_quality | params=logical_consistency | hash=2775ba917281
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m141_inference_quality.py` | func=compute_m141_inference_quality | params=logical_consistency | hash=21ec95997877
  Evidence: nan

## m142_rag_alignment
- Sources count: 2
- Status: identical
- Code hashes: 4b0110f9fa7c
- Params (union): rag_score
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: rag_score
- Missing in compendium formula: rag_score
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m142_rag_alignment.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m142_rag_alignment.py` | func=compute_m142_rag_alignment | params=rag_score | hash=4b0110f9fa7c
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m142_rag_alignment.py` | func=compute_m142_rag_alignment | params=rag_score | hash=4b0110f9fa7c
  Evidence: nan

## m142_reasoning_depth
- Sources count: 4
- Status: identical
- Code hashes: b7f39e43ef62
- Params (union): PCI,complexity
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: PCI,complexity
- Missing in compendium formula: PCI,complexity
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m142_reasoning_depth.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m142_reasoning_depth.py` | func=compute_m142_reasoning_depth | params=complexity,PCI | hash=b7f39e43ef62
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m142_reasoning_depth.py` | func=compute_m142_reasoning_depth | params=complexity,PCI | hash=b7f39e43ef62
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m142_reasoning_depth.py` | func=compute_m142_reasoning_depth | params=complexity,PCI | hash=b7f39e43ef62
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m142_reasoning_depth.py` | func=compute_m142_reasoning_depth | params=complexity,PCI | hash=b7f39e43ef62
  Evidence: nan

## m143_context_window_usage
- Sources count: 4
- Status: identical
- Code hashes: 6e467a110986
- Params (union): current_tokens,max_tokens
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: current_tokens,max_tokens
- Missing in compendium formula: current_tokens,max_tokens
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m143_context_window_usage.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m143_context_window_usage.py` | func=compute_m143_context_window_usage | params=current_tokens,max_tokens | hash=6e467a110986
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m143_context_window_usage.py` | func=compute_m143_context_window_usage | params=current_tokens,max_tokens | hash=6e467a110986
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m143_context_window_usage.py` | func=compute_m143_context_window_usage | params=current_tokens,max_tokens | hash=6e467a110986
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m143_context_window_usage.py` | func=compute_m143_context_window_usage | params=current_tokens,max_tokens | hash=6e467a110986
  Evidence: nan

## m144_attention_span
- Sources count: 4
- Status: identical
- Code hashes: 6c10fe015de7
- Params (union): focus_duration,max_duration
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: focus_duration,max_duration
- Missing in compendium formula: focus_duration,max_duration
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m144_attention_span.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m144_attention_span.py` | func=compute_m144_attention_span | params=focus_duration,max_duration | hash=6c10fe015de7
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m144_attention_span.py` | func=compute_m144_attention_span | params=focus_duration,max_duration | hash=6c10fe015de7
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m144_attention_span.py` | func=compute_m144_attention_span | params=focus_duration,max_duration | hash=6c10fe015de7
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m144_attention_span.py` | func=compute_m144_attention_span | params=focus_duration,max_duration | hash=6c10fe015de7
  Evidence: nan

## m144_sys_stability
- Sources count: 2
- Status: identical
- Code hashes: 1080361680b2
- Params (union): error_rate,latency_norm
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: error_rate,latency_norm
- Missing in compendium formula: error_rate,latency_norm
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m144_sys_stability.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m144_sys_stability.py` | func=compute_m144_sys_stability | params=error_rate,latency_norm | hash=1080361680b2
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m144_sys_stability.py` | func=compute_m144_sys_stability | params=error_rate,latency_norm | hash=1080361680b2
  Evidence: nan

## m145_learning_rate_meta
- Sources count: 2
- Status: identical
- Code hashes: bf8eff9ae166
- Params (union): performance_delta
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: performance_delta
- Missing in compendium formula: performance_delta
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m145_learning_rate_meta.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m145_learning_rate_meta.py` | func=compute_m145_learning_rate_meta | params=performance_delta | hash=bf8eff9ae166
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m145_learning_rate_meta.py` | func=compute_m145_learning_rate_meta | params=performance_delta | hash=bf8eff9ae166
  Evidence: nan

## m145_task_switching
- Sources count: 4
- Status: identical
- Code hashes: 6a3aaa38eba8
- Params (union): switches,total_tasks
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: switches,total_tasks
- Missing in compendium formula: switches,total_tasks
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m145_task_switching.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m145_task_switching.py` | func=compute_m145_task_switching | params=switches,total_tasks | hash=6a3aaa38eba8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m145_task_switching.py` | func=compute_m145_task_switching | params=switches,total_tasks | hash=6a3aaa38eba8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m145_task_switching.py` | func=compute_m145_task_switching | params=switches,total_tasks | hash=6a3aaa38eba8
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m145_task_switching.py` | func=compute_m145_task_switching | params=switches,total_tasks | hash=6a3aaa38eba8
  Evidence: nan

## m146_curiosity_index
- Sources count: 2
- Status: identical
- Code hashes: d88035d4f654
- Params (union): questions_asked,turns
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: questions_asked,turns
- Missing in compendium formula: questions_asked,turns
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m146_curiosity_index.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m146_curiosity_index.py` | func=compute_m146_curiosity_index | params=questions_asked,turns | hash=d88035d4f654
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m146_curiosity_index.py` | func=compute_m146_curiosity_index | params=questions_asked,turns | hash=d88035d4f654
  Evidence: nan

## m146_error_correction
- Sources count: 4
- Status: identical
- Code hashes: 5838df1eadd9
- Params (union): corrections,total_outputs
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: corrections,total_outputs
- Missing in compendium formula: corrections,total_outputs
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m146_error_correction.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m146_error_correction.py` | func=compute_m146_error_correction | params=corrections,total_outputs | hash=5838df1eadd9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m146_error_correction.py` | func=compute_m146_error_correction | params=corrections,total_outputs | hash=5838df1eadd9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m146_error_correction.py` | func=compute_m146_error_correction | params=corrections,total_outputs | hash=5838df1eadd9
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m146_error_correction.py` | func=compute_m146_error_correction | params=corrections,total_outputs | hash=5838df1eadd9
  Evidence: nan

## m147_confidence
- Sources count: 2
- Status: identical
- Code hashes: b3baef56eafe
- Params (union): variance
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: variance
- Missing in compendium formula: variance
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m147_confidence.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m147_confidence.py` | func=compute_m147_confidence | params=variance | hash=b3baef56eafe
  Evidence: High variance = low confidence.
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m147_confidence.py` | func=compute_m147_confidence | params=variance | hash=b3baef56eafe
  Evidence: High variance = low confidence.

## m147_learning_progress
- Sources count: 4
- Status: identical
- Code hashes: 7ae894c2dd29
- Params (union): current_perf,initial_perf
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: current_perf,initial_perf
- Missing in compendium formula: current_perf,initial_perf
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m147_learning_progress.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m147_learning_progress.py` | func=compute_m147_learning_progress | params=current_perf,initial_perf | hash=7ae894c2dd29
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m147_learning_progress.py` | func=compute_m147_learning_progress | params=current_perf,initial_perf | hash=7ae894c2dd29
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m147_learning_progress.py` | func=compute_m147_learning_progress | params=current_perf,initial_perf | hash=7ae894c2dd29
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m147_learning_progress.py` | func=compute_m147_learning_progress | params=current_perf,initial_perf | hash=7ae894c2dd29
  Evidence: nan

## m148_coherence_meta
- Sources count: 2
- Status: identical
- Code hashes: cd716854578e
- Params (union): internal_consistency
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: internal_consistency
- Missing in compendium formula: internal_consistency
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m148_coherence_meta.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m148_coherence_meta.py` | func=compute_m148_coherence_meta | params=internal_consistency | hash=cd716854578e
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m148_coherence_meta.py` | func=compute_m148_coherence_meta | params=internal_consistency | hash=cd716854578e
  Evidence: nan

## m148_knowledge_integration
- Sources count: 4
- Status: identical
- Code hashes: 3226c1f85e1b
- Params (union): new_facts,total_facts
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: new_facts,total_facts
- Missing in compendium formula: new_facts,total_facts
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m148_knowledge_integration.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m148_knowledge_integration.py` | func=compute_m148_knowledge_integration | params=new_facts,total_facts | hash=3226c1f85e1b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m148_knowledge_integration.py` | func=compute_m148_knowledge_integration | params=new_facts,total_facts | hash=3226c1f85e1b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m148_knowledge_integration.py` | func=compute_m148_knowledge_integration | params=new_facts,total_facts | hash=3226c1f85e1b
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m148_knowledge_integration.py` | func=compute_m148_knowledge_integration | params=new_facts,total_facts | hash=3226c1f85e1b
  Evidence: nan

## m149_adaptation_rate
- Sources count: 2
- Status: identical
- Code hashes: c4f97464e545
- Params (union): adjustments,opportunities
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: adjustments,opportunities
- Missing in compendium formula: adjustments,opportunities
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m149_adaptation_rate.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m149_adaptation_rate.py` | func=compute_m149_adaptation_rate | params=adjustments,opportunities | hash=c4f97464e545
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m149_adaptation_rate.py` | func=compute_m149_adaptation_rate | params=adjustments,opportunities | hash=c4f97464e545
  Evidence: nan

## m149_semantic_drift
- Sources count: 4
- Status: identical
- Code hashes: 933ccbb614ed
- Params (union): current_vec,initial_vec
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: current_vec,initial_vec
- Missing in compendium formula: current_vec,initial_vec
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m149_semantic_drift.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m149_semantic_drift.py` | func=compute_m149_semantic_drift | params=current_vec,initial_vec | hash=933ccbb614ed
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m149_semantic_drift.py` | func=compute_m149_semantic_drift | params=current_vec,initial_vec | hash=933ccbb614ed
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m149_semantic_drift.py` | func=compute_m149_semantic_drift | params=current_vec,initial_vec | hash=933ccbb614ed
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m149_semantic_drift.py` | func=compute_m149_semantic_drift | params=current_vec,initial_vec | hash=933ccbb614ed
  Evidence: nan

## m14_rep_history
- Sources count: 8
- Status: diff
- Code hashes: 1a306c21d4a2;c976f8a514dc
- Params (union): history,text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: history,text
- Missing in compendium formula: history,text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m14_rep_history.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m14_rep_history.py` | func=compute_m14_rep_history | params=text,history | hash=c976f8a514dc
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m14_rep_history.py` | func=compute_m14_rep_history | params=text,history | hash=1a306c21d4a2
  Evidence: Repetition score [0, 1] - Higher = more repetitive with history
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m14_rep_history.py` | func=compute_m14_rep_history | params=text,history | hash=c976f8a514dc
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m14_rep_history.py` | func=compute_m14_rep_history | params=text,history | hash=1a306c21d4a2
  Evidence: Repetition score [0, 1] - Higher = more repetitive with history
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m14_rep_history.py` | func=compute_m14_rep_history | params=text,history | hash=1a306c21d4a2
  Evidence: Repetition score [0, 1] - Higher = more repetitive with history
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m14_rep_history.py` | func=compute_m14_rep_history | params=text,history | hash=1a306c21d4a2
  Evidence: Repetition score [0, 1] - Higher = more repetitive with history
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m14_rep_history.py` | func=compute_m14_rep_history | params=text,history | hash=c976f8a514dc
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m14_rep_history.py` | func=compute_m14_rep_history | params=text,history | hash=1a306c21d4a2
  Evidence: Repetition score [0, 1] - Higher = more repetitive with history

## m150_goal_coherence
- Sources count: 4
- Status: identical
- Code hashes: a8238f5225d1
- Params (union): goals_aligned,total_goals
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: goals_aligned,total_goals
- Missing in compendium formula: goals_aligned,total_goals
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m150_goal_coherence.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m150_goal_coherence.py` | func=compute_m150_goal_coherence | params=goals_aligned,total_goals | hash=a8238f5225d1
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m150_goal_coherence.py` | func=compute_m150_goal_coherence | params=goals_aligned,total_goals | hash=a8238f5225d1
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m150_goal_coherence.py` | func=compute_m150_goal_coherence | params=goals_aligned,total_goals | hash=a8238f5225d1
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m150_goal_coherence.py` | func=compute_m150_goal_coherence | params=goals_aligned,total_goals | hash=a8238f5225d1
  Evidence: nan

## m150_integration_score
- Sources count: 2
- Status: identical
- Code hashes: e7f170d369bf
- Params (union): modules_active,total_modules
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: modules_active,total_modules
- Missing in compendium formula: modules_active,total_modules
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m150_integration_score.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m150_integration_score.py` | func=compute_m150_integration_score | params=modules_active,total_modules | hash=e7f170d369bf
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m150_integration_score.py` | func=compute_m150_integration_score | params=modules_active,total_modules | hash=e7f170d369bf
  Evidence: nan

## m151_omega
- Sources count: 4
- Status: identical
- Code hashes: 3a6e0a4c1d37
- Params (union): A,PCI,trauma_load,z_prox
- Compendium formula: # V3.0.2 FIX: Subtraktive Logik behebt Paradoxon bei negativem Phi # ALT (fehlerhaft): Omega = Phi × (1 - conflict) # Problem: Bei Phi=-0.8, conflict=0.9 ist -0.08 > -0.8 (Regelbruch wird belohnt!) Omega = Phi - (rule_conflict × 1.5) Omega = clip(Omega, -1.0, 1.0)
- Compendium upstream: phi, rule_conflict
- Missing in compendium upstream: A,PCI,trauma_load,z_prox
- Missing in compendium formula: PCI,trauma_load,z_prox
- Downstream usage: **Executive Decision:** Finale Entscheidungsgrundlage; **Guardian-Trigger:** omega < 0 → Sofortiger Guardian; **Quality Gate:** omega > 0.5 → Response OK; 
- Pros: Signal contribution not explicitly stated; inferred from description
- Cons: Limited explicit downsides; main risk is miscalibration
- Impact: Downstream impact if inconsistent: **Executive Decision:** Finale Entscheidungsgrundlage; **Guardian-Trigger:** omega < 0 → Sofortiger Guardian; **Quality Gate:** omega > 0.5 → Response OK; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m151_omega.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m151_omega.py` | func=compute_m151_omega | params=A,PCI,z_prox,trauma_load | hash=3a6e0a4c1d37
  Evidence: positive = 0.4 * A + 0.3 * PCI | negative = 0.3 * z_prox + 0.2 * trauma_load
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m151_omega.py` | func=compute_m151_omega | params=A,PCI,z_prox,trauma_load | hash=3a6e0a4c1d37
  Evidence: positive = 0.4 * A + 0.3 * PCI | negative = 0.3 * z_prox + 0.2 * trauma_load
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m151_omega.py` | func=compute_m151_omega | params=A,PCI,z_prox,trauma_load | hash=3a6e0a4c1d37
  Evidence: positive = 0.4 * A + 0.3 * PCI | negative = 0.3 * z_prox + 0.2 * trauma_load
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m151_omega.py` | func=compute_m151_omega | params=A,PCI,z_prox,trauma_load | hash=3a6e0a4c1d37
  Evidence: positive = 0.4 * A + 0.3 * PCI | negative = 0.3 * z_prox + 0.2 * trauma_load

## m152_a51_compliance
- Sources count: 5
- Status: diff
- Code hashes: 8f87878d1da3;e4216aa82d7b
- Params (union): rules_checked,rules_passed
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: rules_checked,rules_passed
- Missing in compendium formula: rules_checked,rules_passed
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m152_a51_compliance.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m152_a51_compliance.py` | func=compute_m152_a51_compliance | params=rules_checked,rules_passed | hash=e4216aa82d7b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m152_a51_compliance.py` | func=compute_m152_a51_compliance | params=rules_checked,rules_passed | hash=8f87878d1da3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m152_a51_compliance.py` | func=compute_m152_a51_compliance | params=rules_checked,rules_passed | hash=e4216aa82d7b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m152_a51_compliance.py` | func=compute_m152_a51_compliance | params=rules_checked,rules_passed | hash=e4216aa82d7b
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m152_a51_compliance.py` | func=compute_m152_a51_compliance | params=rules_checked,rules_passed | hash=8f87878d1da3
  Evidence: nan

## m153_sys_health
- Sources count: 4
- Status: identical
- Code hashes: def388d6b8d6
- Params (union): error_rate,latency,mem_pressure
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: error_rate,latency,mem_pressure
- Missing in compendium formula: error_rate,latency,mem_pressure
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m153_sys_health.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m153_sys_health.py` | func=compute_m153_sys_health | params=latency,error_rate,mem_pressure | hash=def388d6b8d6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m153_sys_health.py` | func=compute_m153_sys_health | params=latency,error_rate,mem_pressure | hash=def388d6b8d6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m153_sys_health.py` | func=compute_m153_sys_health | params=latency,error_rate,mem_pressure | hash=def388d6b8d6
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m153_sys_health.py` | func=compute_m153_sys_health | params=latency,error_rate,mem_pressure | hash=def388d6b8d6
  Evidence: nan

## m154_sys_latency
- Sources count: 5
- Status: diff
- Code hashes: 766aaa609b71;bb98de3fcbb1
- Params (union): response_time_ms,target_ms
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: response_time_ms,target_ms
- Missing in compendium formula: response_time_ms,target_ms
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m154_sys_latency.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m154_sys_latency.py` | func=compute_m154_sys_latency | params=response_time_ms,target_ms | hash=766aaa609b71
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m154_sys_latency.py` | func=compute_m154_sys_latency | params=response_time_ms,target_ms | hash=bb98de3fcbb1
  Evidence: Normalized latency (1.0 = at target, >1.0 = slower than target).
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m154_sys_latency.py` | func=compute_m154_sys_latency | params=response_time_ms,target_ms | hash=766aaa609b71
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m154_sys_latency.py` | func=compute_m154_sys_latency | params=response_time_ms,target_ms | hash=766aaa609b71
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m154_sys_latency.py` | func=compute_m154_sys_latency | params=response_time_ms,target_ms | hash=bb98de3fcbb1
  Evidence: Normalized latency (1.0 = at target, >1.0 = slower than target).

## m155_error_rate
- Sources count: 5
- Status: diff
- Code hashes: ae397ddb4891;feab4554ed7e
- Params (union): errors,total_requests
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: errors,total_requests
- Missing in compendium formula: errors,total_requests
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m155_error_rate.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m155_error_rate.py` | func=compute_m155_error_rate | params=errors,total_requests | hash=ae397ddb4891
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m155_error_rate.py` | func=compute_m155_error_rate | params=errors,total_requests | hash=feab4554ed7e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m155_error_rate.py` | func=compute_m155_error_rate | params=errors,total_requests | hash=ae397ddb4891
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m155_error_rate.py` | func=compute_m155_error_rate | params=errors,total_requests | hash=ae397ddb4891
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m155_error_rate.py` | func=compute_m155_error_rate | params=errors,total_requests | hash=feab4554ed7e
  Evidence: nan

## m156_cache_hit_rate
- Sources count: 5
- Status: diff
- Code hashes: 4ba999ddc9c9;7e392838522c
- Params (union): hits,total
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: hits,total
- Missing in compendium formula: hits,total
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m156_cache_hit_rate.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m156_cache_hit_rate.py` | func=compute_m156_cache_hit_rate | params=hits,total | hash=7e392838522c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m156_cache_hit_rate.py` | func=compute_m156_cache_hit_rate | params=hits,total | hash=4ba999ddc9c9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m156_cache_hit_rate.py` | func=compute_m156_cache_hit_rate | params=hits,total | hash=7e392838522c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m156_cache_hit_rate.py` | func=compute_m156_cache_hit_rate | params=hits,total | hash=7e392838522c
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m156_cache_hit_rate.py` | func=compute_m156_cache_hit_rate | params=hits,total | hash=4ba999ddc9c9
  Evidence: nan

## m157_token_throughput
- Sources count: 5
- Status: diff
- Code hashes: 20ea32e683ff;7033e96a26d7
- Params (union): seconds,tokens
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: seconds,tokens
- Missing in compendium formula: seconds,tokens
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m157_token_throughput.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m157_token_throughput.py` | func=compute_m157_token_throughput | params=tokens,seconds | hash=20ea32e683ff
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m157_token_throughput.py` | func=compute_m157_token_throughput | params=tokens,seconds | hash=7033e96a26d7
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m157_token_throughput.py` | func=compute_m157_token_throughput | params=tokens,seconds | hash=20ea32e683ff
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m157_token_throughput.py` | func=compute_m157_token_throughput | params=tokens,seconds | hash=20ea32e683ff
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m157_token_throughput.py` | func=compute_m157_token_throughput | params=tokens,seconds | hash=7033e96a26d7
  Evidence: nan

## m158_context_utilization
- Sources count: 5
- Status: diff
- Code hashes: 307e3c7d8a68;516cbf56ed64
- Params (union): max_tokens,used_tokens
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: max_tokens,used_tokens
- Missing in compendium formula: max_tokens,used_tokens
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m158_context_utilization.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m158_context_utilization.py` | func=compute_m158_context_utilization | params=used_tokens,max_tokens | hash=307e3c7d8a68
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m158_context_utilization.py` | func=compute_m158_context_utilization | params=used_tokens,max_tokens | hash=516cbf56ed64
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m158_context_utilization.py` | func=compute_m158_context_utilization | params=used_tokens,max_tokens | hash=307e3c7d8a68
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m158_context_utilization.py` | func=compute_m158_context_utilization | params=used_tokens,max_tokens | hash=307e3c7d8a68
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m158_context_utilization.py` | func=compute_m158_context_utilization | params=used_tokens,max_tokens | hash=516cbf56ed64
  Evidence: nan

## m159_guardian_interventions
- Sources count: 5
- Status: diff
- Code hashes: 06e0c0847c9c;b029c60e29e2
- Params (union): interventions,turns
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: interventions,turns
- Missing in compendium formula: interventions,turns
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m159_guardian_interventions.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m159_guardian_interventions.py` | func=compute_m159_guardian_interventions | params=interventions,turns | hash=b029c60e29e2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m159_guardian_interventions.py` | func=compute_m159_guardian_interventions | params=interventions,turns | hash=06e0c0847c9c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m159_guardian_interventions.py` | func=compute_m159_guardian_interventions | params=interventions,turns | hash=b029c60e29e2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m159_guardian_interventions.py` | func=compute_m159_guardian_interventions | params=interventions,turns | hash=b029c60e29e2
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m159_guardian_interventions.py` | func=compute_m159_guardian_interventions | params=interventions,turns | hash=06e0c0847c9c
  Evidence: nan

## m15_affekt_a_legacy
- Sources count: 8
- Status: diff
- Code hashes: 480b6a3a3bcf;6f17c8cd3696
- Params (union): coh,flow,ll,zlf
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: coh,flow,ll,zlf
- Missing in compendium formula: coh,flow,ll,zlf
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m15_affekt_a_legacy.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m15_affekt_a_legacy.py` | func=compute_m15_affekt_a_legacy | params=flow,coh,ll,zlf | hash=6f17c8cd3696
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m15_affekt_a_legacy.py` | func=compute_m15_affekt_a_legacy | params=flow,coh,ll,zlf | hash=480b6a3a3bcf
  Evidence: A_legacy = clip01(0.40*flow + 0.30*coh + 0.20*(1-LL) + 0.10*(1-ZLF))
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m15_affekt_a_legacy.py` | func=compute_m15_affekt_a_legacy | params=flow,coh,ll,zlf | hash=6f17c8cd3696
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m15_affekt_a_legacy.py` | func=compute_m15_affekt_a_legacy | params=flow,coh,ll,zlf | hash=480b6a3a3bcf
  Evidence: A_legacy = clip01(0.40*flow + 0.30*coh + 0.20*(1-LL) + 0.10*(1-ZLF))
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m15_affekt_a_legacy.py` | func=compute_m15_affekt_a_legacy | params=flow,coh,ll,zlf | hash=480b6a3a3bcf
  Evidence: A_legacy = clip01(0.40*flow + 0.30*coh + 0.20*(1-LL) + 0.10*(1-ZLF))
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m15_affekt_a_legacy.py` | func=compute_m15_affekt_a_legacy | params=flow,coh,ll,zlf | hash=480b6a3a3bcf
  Evidence: A_legacy = clip01(0.40*flow + 0.30*coh + 0.20*(1-LL) + 0.10*(1-ZLF))
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m15_affekt_a_legacy.py` | func=compute_m15_affekt_a_legacy | params=flow,coh,ll,zlf | hash=6f17c8cd3696
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m15_affekt_a_legacy.py` | func=compute_m15_affekt_a_legacy | params=flow,coh,ll,zlf | hash=480b6a3a3bcf
  Evidence: A_legacy = clip01(0.40*flow + 0.30*coh + 0.20*(1-LL) + 0.10*(1-ZLF))

## m160_uptime
- Sources count: 5
- Status: diff
- Code hashes: 431fd7a49365;ece35b239af4
- Params (union): total_seconds,uptime_seconds
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: total_seconds,uptime_seconds
- Missing in compendium formula: total_seconds,uptime_seconds
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m160_uptime.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m160_uptime.py` | func=compute_m160_uptime | params=uptime_seconds,total_seconds | hash=431fd7a49365
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m160_uptime.py` | func=compute_m160_uptime | params=uptime_seconds,total_seconds | hash=ece35b239af4
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m160_uptime.py` | func=compute_m160_uptime | params=uptime_seconds,total_seconds | hash=431fd7a49365
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m160_uptime.py` | func=compute_m160_uptime | params=uptime_seconds,total_seconds | hash=431fd7a49365
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m160_uptime.py` | func=compute_m160_uptime | params=uptime_seconds,total_seconds | hash=ece35b239af4
  Evidence: nan

## m161_commit
- Sources count: 5
- Status: diff
- Code hashes: 7cf4bfcad7ce;e9c9d8c1cec8
- Params (union): trauma_load,z_prox
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: trauma_load,z_prox
- Missing in compendium formula: trauma_load,z_prox
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m161_commit.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m161_commit.py` | func=compute_m161_commit | params=z_prox,trauma_load | hash=e9c9d8c1cec8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m161_commit.py` | func=compute_m161_commit | params=z_prox,trauma_load | hash=7cf4bfcad7ce
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m161_commit.py` | func=compute_m161_commit | params=z_prox,trauma_load | hash=e9c9d8c1cec8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m161_commit.py` | func=compute_m161_commit | params=z_prox,trauma_load | hash=e9c9d8c1cec8
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m161_commit.py` | func=compute_m161_commit | params=z_prox,trauma_load | hash=7cf4bfcad7ce
  Evidence: nan

## m162_ctx_time
- Sources count: 4
- Status: diff
- Code hashes: 38a2bbca3b56;b242c74a4992
- Params (union): current_minutes,session_start_minutes
- Compendium formula: nan
- Compendium upstream: session_start, current_time
- Missing in compendium upstream: current_minutes,session_start_minutes
- Missing in compendium formula: current_minutes,session_start_minutes
- Downstream usage: nan
- Pros: Enables context-aware adaptation (time/platform/modality)
- Cons: Depends on external context signals or telemetry availability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m162_ctx_time.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m162_ctx_time.py` | func=compute_m162_ctx_time | params=session_start_minutes,current_minutes | hash=b242c74a4992
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m162_ctx_time.py` | func=compute_m162_ctx_time | params=session_start_minutes,current_minutes | hash=38a2bbca3b56
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m162_ctx_time.py` | func=compute_m162_ctx_time | params=session_start_minutes,current_minutes | hash=b242c74a4992
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m162_ctx_time.py` | func=compute_m162_ctx_time | params=session_start_minutes,current_minutes | hash=b242c74a4992
  Evidence: nan

## m162_ev_tension
- Sources count: 2
- Status: identical
- Code hashes: 8101bb1364f3
- Params (union): e_i_proxy,x_fm_prox,z_prox
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: e_i_proxy,x_fm_prox,z_prox
- Missing in compendium formula: e_i_proxy,x_fm_prox,z_prox
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m162_ev_tension.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m162_ev_tension.py` | func=compute_m162_ev_tension | params=z_prox,x_fm_prox,e_i_proxy | hash=8101bb1364f3
  Evidence: Formula: EV_tension = 0.5 × z_prox + 0.2 × x_fm_prox + 0.3 × E_I_proxy
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m162_ev_tension.py` | func=compute_m162_ev_tension | params=z_prox,x_fm_prox,e_i_proxy | hash=8101bb1364f3
  Evidence: Formula: EV_tension = 0.5 × z_prox + 0.2 × x_fm_prox + 0.3 × E_I_proxy

## m163_ctx_loc
- Sources count: 4
- Status: identical
- Code hashes: 87e65feed960
- Params (union): location_data
- Compendium formula: nan
- Compendium upstream: location_data
- Missing in compendium upstream: nan
- Missing in compendium formula: location_data
- Downstream usage: nan
- Pros: Enables context-aware adaptation (time/platform/modality)
- Cons: Depends on external context signals or telemetry availability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m163_ctx_loc.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m163_ctx_loc.py` | func=compute_m163_ctx_loc | params=location_data | hash=87e65feed960
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m163_ctx_loc.py` | func=compute_m163_ctx_loc | params=location_data | hash=87e65feed960
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m163_ctx_loc.py` | func=compute_m163_ctx_loc | params=location_data | hash=87e65feed960
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m163_ctx_loc.py` | func=compute_m163_ctx_loc | params=location_data | hash=87e65feed960
  Evidence: nan

## m163_x_fm_prox
- Sources count: 2
- Status: identical
- Code hashes: 2bd668a0b7e8
- Params (union): A_variance,nabla_A
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: A_variance,nabla_A
- Missing in compendium formula: A_variance,nabla_A
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m163_x_fm_prox.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m163_x_fm_prox.py` | func=compute_m163_x_fm_prox | params=A_variance,nabla_A | hash=2bd668a0b7e8
  Evidence: Formula: x_fm_prox = 1 if (var(A) < 0.005 AND |∇A| < 0.02) else 0 | - Low variance = no movement in phase space | - Flat gradient = no evolution pressure
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m163_x_fm_prox.py` | func=compute_m163_x_fm_prox | params=A_variance,nabla_A | hash=2bd668a0b7e8
  Evidence: Formula: x_fm_prox = 1 if (var(A) < 0.005 AND |∇A| < 0.02) else 0 | - Low variance = no movement in phase space | - Flat gradient = no evolution pressure

## m164_e_i_proxy
- Sources count: 2
- Status: identical
- Code hashes: 9be144c574f2
- Params (union): PCI,nabla_A
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: PCI,nabla_A
- Missing in compendium formula: PCI,nabla_A
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m164_e_i_proxy.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m164_e_i_proxy.py` | func=compute_m164_e_i_proxy | params=nabla_A,PCI | hash=9be144c574f2
  Evidence: Formula: E_I = |∇A| × (1 - PCI) | - High E_I = potential for breakthrough or collapse
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m164_e_i_proxy.py` | func=compute_m164_e_i_proxy | params=nabla_A,PCI | hash=9be144c574f2
  Evidence: Formula: E_I = |∇A| × (1 - PCI) | - High E_I = potential for breakthrough or collapse

## m164_user_state
- Sources count: 4
- Status: identical
- Code hashes: 85125543bc77
- Params (union): recent_affects
- Compendium formula: nan
- Compendium upstream: recent_affects
- Missing in compendium upstream: nan
- Missing in compendium formula: recent_affects
- Downstream usage: nan
- Pros: Adds emotional nuance for response modulation; Enables context-aware adaptation (time/platform/modality)
- Cons: Lexicon/heuristic bias can misclassify context; Depends on external context signals or telemetry availability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m164_user_state.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m164_user_state.py` | func=compute_m164_user_state | params=recent_affects | hash=85125543bc77
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m164_user_state.py` | func=compute_m164_user_state | params=recent_affects | hash=85125543bc77
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m164_user_state.py` | func=compute_m164_user_state | params=recent_affects | hash=85125543bc77
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m164_user_state.py` | func=compute_m164_user_state | params=recent_affects | hash=85125543bc77
  Evidence: nan

## m165_dist_z
- Sources count: 2
- Status: identical
- Code hashes: d1bbea62c1c4
- Params (union): A,LL,ctx_break
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: A,LL,ctx_break
- Missing in compendium formula: A,LL,ctx_break
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m165_dist_z.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m165_dist_z.py` | func=compute_m165_dist_z | params=A,LL,ctx_break | hash=d1bbea62c1c4
  Evidence: Formula: dist_z = A × (1 - max(LL, ctx_break))
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m165_dist_z.py` | func=compute_m165_dist_z | params=A,LL,ctx_break | hash=d1bbea62c1c4
  Evidence: Formula: dist_z = A × (1 - max(LL, ctx_break))

## m165_platform
- Sources count: 4
- Status: identical
- Code hashes: bdf007b6034c
- Params (union): nan
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Enables context-aware adaptation (time/platform/modality)
- Cons: Depends on external context signals or telemetry availability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m165_platform.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m165_platform.py` | func=compute_m165_platform | params=nan | hash=bdf007b6034c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m165_platform.py` | func=compute_m165_platform | params=nan | hash=bdf007b6034c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m165_platform.py` | func=compute_m165_platform | params=nan | hash=bdf007b6034c
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m165_platform.py` | func=compute_m165_platform | params=nan | hash=bdf007b6034c
  Evidence: nan

## m166_hazard
- Sources count: 2
- Status: identical
- Code hashes: 766aac959086
- Params (union): t_fog,t_panic,z_prox
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: t_fog,t_panic,z_prox
- Missing in compendium formula: t_fog,t_panic,z_prox
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m166_hazard.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m166_hazard.py` | func=compute_m166_hazard | params=z_prox,t_panic,t_fog | hash=766aac959086
  Evidence: Formula: hazard = 0.5 × z_prox + 0.3 × T_panic + 0.2 × T_fog
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m166_hazard.py` | func=compute_m166_hazard | params=z_prox,t_panic,t_fog | hash=766aac959086
  Evidence: Formula: hazard = 0.5 × z_prox + 0.3 × T_panic + 0.2 × T_fog

## m166_modality
- Sources count: 4
- Status: identical
- Code hashes: b50c33eb97bc
- Params (union): input_data
- Compendium formula: nan
- Compendium upstream: input_data
- Missing in compendium upstream: nan
- Missing in compendium formula: input_data
- Downstream usage: nan
- Pros: Enables context-aware adaptation (time/platform/modality)
- Cons: Depends on external context signals or telemetry availability; Embedding dependence adds latency and model coupling
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m166_modality.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m166_modality.py` | func=compute_m166_modality | params=input_data | hash=b50c33eb97bc
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m166_modality.py` | func=compute_m166_modality | params=input_data | hash=b50c33eb97bc
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m166_modality.py` | func=compute_m166_modality | params=input_data | hash=b50c33eb97bc
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m166_modality.py` | func=compute_m166_modality | params=input_data | hash=b50c33eb97bc
  Evidence: nan

## m167_guardian_trip
- Sources count: 2
- Status: identical
- Code hashes: 20bb2ef57b4f
- Params (union): dist_z,hazard
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: dist_z,hazard
- Missing in compendium formula: dist_z,hazard
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m167_guardian_trip.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m167_guardian_trip.py` | func=compute_m167_guardian_trip | params=dist_z,hazard | hash=20bb2ef57b4f
  Evidence: Formula: guardian_trip = 1 if (dist_z < 0.35 OR hazard > 0.7) else 0
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m167_guardian_trip.py` | func=compute_m167_guardian_trip | params=dist_z,hazard | hash=20bb2ef57b4f
  Evidence: Formula: guardian_trip = 1 if (dist_z < 0.35 OR hazard > 0.7) else 0

## m167_noise
- Sources count: 4
- Status: identical
- Code hashes: f2f381eb20c3
- Params (union): text
- Compendium formula: nan
- Compendium upstream: text
- Missing in compendium upstream: nan
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: Enables context-aware adaptation (time/platform/modality)
- Cons: Depends on external context signals or telemetry availability; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m167_noise.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m167_noise.py` | func=compute_m167_noise | params=text | hash=f2f381eb20c3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m167_noise.py` | func=compute_m167_noise | params=text | hash=f2f381eb20c3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m167_noise.py` | func=compute_m167_noise | params=text | hash=f2f381eb20c3
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m167_noise.py` | func=compute_m167_noise | params=text | hash=f2f381eb20c3
  Evidence: nan

## m168_cum_stress
- Sources count: 4
- Status: identical
- Code hashes: 9a03fc5c237a
- Params (union): z_prox_history
- Compendium formula: cum_stress = ∫(z_prox × dt) over last 30 minutes Vereinfacht (diskret): cum_stress = Σ(z_prox_i × delta_t_i) for i in last_30_min
- Compendium upstream: self
- Missing in compendium upstream: z_prox_history
- Missing in compendium formula: z_prox_history
- Downstream usage: nan
- Pros: Safety-critical signal for risk/guardian decisions
- Cons: High false-positive cost if thresholds/lexicon are wrong
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m168_cum_stress.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m168_cum_stress.py` | func=compute_m168_cum_stress | params=z_prox_history | hash=9a03fc5c237a
  Evidence: recent = z_prox_history[-10:]
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m168_cum_stress.py` | func=compute_m168_cum_stress | params=z_prox_history | hash=9a03fc5c237a
  Evidence: recent = z_prox_history[-10:]
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m168_cum_stress.py` | func=compute_m168_cum_stress | params=z_prox_history | hash=9a03fc5c237a
  Evidence: recent = z_prox_history[-10:]
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m168_cum_stress.py` | func=compute_m168_cum_stress | params=z_prox_history | hash=9a03fc5c237a
  Evidence: recent = z_prox_history[-10:]

## m168_mode_hp
- Sources count: 2
- Status: identical
- Code hashes: 062098b9a4c5
- Params (union): c_crit
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: c_crit
- Missing in compendium formula: c_crit
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m168_mode_hp.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m168_mode_hp.py` | func=compute_m168_mode_hp | params=c_crit | hash=062098b9a4c5
  Evidence: C_crit = (Tension + Danger) / Readiness
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m168_mode_hp.py` | func=compute_m168_mode_hp | params=c_crit | hash=062098b9a4c5
  Evidence: C_crit = (Tension + Danger) / Readiness

## m169_ctx_time
- Sources count: 1
- Status: single_source
- Code hashes: 38a2bbca3b56
- Params (union): current_minutes,session_start_minutes
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: current_minutes,session_start_minutes
- Missing in compendium formula: current_minutes,session_start_minutes
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m169_ctx_time.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m169_ctx_time.py` | func=compute_m162_ctx_time | params=session_start_minutes,current_minutes | hash=38a2bbca3b56
  Evidence: nan

## m16_external_stag
- Sources count: 8
- Status: diff
- Code hashes: 360efd8664b3;e3ad55b14e12
- Params (union): turns_without_progress
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: turns_without_progress
- Missing in compendium formula: turns_without_progress
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m16_external_stag.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m16_external_stag.py` | func=compute_m16_external_stag | params=turns_without_progress | hash=e3ad55b14e12
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m16_external_stag.py` | func=compute_m16_external_stag | params=turns_without_progress | hash=360efd8664b3
  Evidence: Normalized by 5 turns: stag = min(1.0, turns_without_progress / 5.0)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m16_external_stag.py` | func=compute_m16_external_stag | params=turns_without_progress | hash=e3ad55b14e12
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m16_external_stag.py` | func=compute_m16_external_stag | params=turns_without_progress | hash=360efd8664b3
  Evidence: Normalized by 5 turns: stag = min(1.0, turns_without_progress / 5.0)
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m16_external_stag.py` | func=compute_m16_external_stag | params=turns_without_progress | hash=360efd8664b3
  Evidence: Normalized by 5 turns: stag = min(1.0, turns_without_progress / 5.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m16_external_stag.py` | func=compute_m16_external_stag | params=turns_without_progress | hash=360efd8664b3
  Evidence: Normalized by 5 turns: stag = min(1.0, turns_without_progress / 5.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m16_external_stag.py` | func=compute_m16_external_stag | params=turns_without_progress | hash=e3ad55b14e12
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m16_external_stag.py` | func=compute_m16_external_stag | params=turns_without_progress | hash=360efd8664b3
  Evidence: Normalized by 5 turns: stag = min(1.0, turns_without_progress / 5.0)

## m17_nabla_a
- Sources count: 8
- Status: diff
- Code hashes: 0e1f499d90df;883190a1a9f3
- Params (union): a_current,a_previous
- Compendium formula: ∇A = A_current - A_previous
- Compendium upstream: nan
- Missing in compendium upstream: a_current,a_previous
- Missing in compendium formula: a_current,a_previous
- Downstream usage: **Trend-Erkennung:** Schnelle Verschlechterung → Warnung; **Homeostasis:** System versucht ∇A zu minimieren; 
- Pros: Foundational metric used by many downstream computations; Adds emotional nuance for response modulation
- Cons: Errors propagate widely across system; Lexicon/heuristic bias can misclassify context
- Impact: Downstream impact if inconsistent: **Trend-Erkennung:** Schnelle Verschlechterung → Warnung; **Homeostasis:** System versucht ∇A zu minimieren; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m17_nabla_a.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m17_nabla_a.py` | func=compute_m17_nabla_a | params=a_current,a_previous | hash=883190a1a9f3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m17_nabla_a.py` | func=compute_m17_nabla_a | params=a_current,a_previous | hash=0e1f499d90df
  Evidence: ∇A = A_current - A_previous
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m17_nabla_a.py` | func=compute_m17_nabla_a | params=a_current,a_previous | hash=883190a1a9f3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m17_nabla_a.py` | func=compute_m17_nabla_a | params=a_current,a_previous | hash=0e1f499d90df
  Evidence: ∇A = A_current - A_previous
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m17_nabla_a.py` | func=compute_m17_nabla_a | params=a_current,a_previous | hash=0e1f499d90df
  Evidence: ∇A = A_current - A_previous
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m17_nabla_a.py` | func=compute_m17_nabla_a | params=a_current,a_previous | hash=0e1f499d90df
  Evidence: ∇A = A_current - A_previous
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m17_nabla_a.py` | func=compute_m17_nabla_a | params=a_current,a_previous | hash=883190a1a9f3
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m17_nabla_a.py` | func=compute_m17_nabla_a | params=a_current,a_previous | hash=0e1f499d90df
  Evidence: ∇A = A_current - A_previous

## m18_s_entropy
- Sources count: 8
- Status: diff
- Code hashes: 6f8f44b49780;6fc0e071c746
- Params (union): tokens
- Compendium formula: H = -Σ p(token_i) × log₂(p(token_i)) wobei: p(token_i) = count(token_i) / total_tokens Summe über alle unique tokens
- Compendium upstream: text
- Missing in compendium upstream: tokens
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Foundational metric used by many downstream computations
- Cons: Errors propagate widely across system; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m18_s_entropy.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m18_s_entropy.py` | func=compute_m18_s_entropy | params=tokens | hash=6f8f44b49780
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m18_s_entropy.py` | func=compute_m18_s_entropy | params=tokens | hash=6fc0e071c746
  Evidence: Entropy in bits [0, log₂(n)] where n = unique tokens
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m18_s_entropy.py` | func=compute_m18_s_entropy | params=tokens | hash=6f8f44b49780
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m18_s_entropy.py` | func=compute_m18_s_entropy | params=tokens | hash=6fc0e071c746
  Evidence: Entropy in bits [0, log₂(n)] where n = unique tokens
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m18_s_entropy.py` | func=compute_m18_s_entropy | params=tokens | hash=6fc0e071c746
  Evidence: Entropy in bits [0, log₂(n)] where n = unique tokens
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m18_s_entropy.py` | func=compute_m18_s_entropy | params=tokens | hash=6fc0e071c746
  Evidence: Entropy in bits [0, log₂(n)] where n = unique tokens
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m18_s_entropy.py` | func=compute_m18_s_entropy | params=tokens | hash=6f8f44b49780
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m18_s_entropy.py` | func=compute_m18_s_entropy | params=tokens | hash=6fc0e071c746
  Evidence: Entropy in bits [0, log₂(n)] where n = unique tokens

## m19_z_prox
- Sources count: 8
- Status: diff
- Code hashes: 59bc8e052e12;eef88aa22f7a
- Params (union): LL,m15_A_structural,m1_A_lexical,t_panic,text
- Compendium formula: # ALTE Formel (vor V3.0.3): # z_prox = (1 - A) × LL # V3.0.3 Safety-First + V3.3.2 Hazard Bonus: effective_A = min(m1_A_lexical, m15_A_structural) base_prox = (1 - effective_A) × LL # Hazard Bonus: Lexikon-Treffer verstärken das Risiko z_prox = min(1.0, base_prox × (1 + hazard_bonus)) wobei: m1_A = Lexikon-basierter Affekt m15_A = Strukturell berechneter Affekt LL = Lambert-Light (Trübung) hazard_bonus = Summe der Lexikon-Hazard-Scores (0.0-0.5) Worst case: effective_A=0, LL=1, hazard=0.5 → z_prox=1.0
- Compendium upstream: nan
- Missing in compendium upstream: LL,m15_A_structural,m1_A_lexical,t_panic,text
- Missing in compendium formula: t_panic,text
- Downstream usage: **Guardian-Trigger:** z_prox > 0.65 → automatischer Eingriff; **Mode-Switching:** Hohe Werte → Sicherheits-Modus; **Logging:** Immer protokolliert für Audit; **Dual-Source:** Beide Affekt-Scores werden geprüft (V3.0.3); 
- Pros: Safety-critical signal for risk/guardian decisions; Adds emotional nuance for response modulation
- Cons: High false-positive cost if thresholds/lexicon are wrong; Lexicon/heuristic bias can misclassify context
- Impact: Downstream impact if inconsistent: **Guardian-Trigger:** z_prox > 0.65 → automatischer Eingriff; **Mode-Switching:** Hohe Werte → Sicherheits-Modus; **Logging:** Immer protokolliert für Audit; **Dual-Source:** Beide Affekt-Scores werden geprüft (V3.0.3); 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m19_z_prox.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m19_z_prox.py` | func=compute_m19_z_prox | params=m1_A_lexical,m15_A_structural,LL,text,t_panic | hash=59bc8e052e12
  Evidence: effective_A = min(m1_A_lexical, m15_A_structural) | base_prox = (1.0 - effective_A) * LL | z_prox = base_prox * (1.0 + hazard_bonus)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m19_z_prox.py` | func=compute_m19_z_prox | params=m1_A_lexical,m15_A_structural,LL,text,t_panic | hash=eef88aa22f7a
  Evidence: z_prox score [0, 1] - Death proximity (HIGHER = MORE DANGER!)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m19_z_prox.py` | func=compute_m19_z_prox | params=m1_A_lexical,m15_A_structural,LL,text,t_panic | hash=59bc8e052e12
  Evidence: effective_A = min(m1_A_lexical, m15_A_structural) | base_prox = (1.0 - effective_A) * LL | z_prox = base_prox * (1.0 + hazard_bonus)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m19_z_prox.py` | func=compute_m19_z_prox | params=m1_A_lexical,m15_A_structural,LL,text,t_panic | hash=eef88aa22f7a
  Evidence: z_prox score [0, 1] - Death proximity (HIGHER = MORE DANGER!)
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m19_z_prox.py` | func=compute_m19_z_prox | params=m1_A_lexical,m15_A_structural,LL,text,t_panic | hash=eef88aa22f7a
  Evidence: z_prox score [0, 1] - Death proximity (HIGHER = MORE DANGER!)
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m19_z_prox.py` | func=compute_m19_z_prox | params=m1_A_lexical,m15_A_structural,LL,text,t_panic | hash=eef88aa22f7a
  Evidence: z_prox score [0, 1] - Death proximity (HIGHER = MORE DANGER!)
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m19_z_prox.py` | func=compute_m19_z_prox | params=m1_A_lexical,m15_A_structural,LL,text,t_panic | hash=59bc8e052e12
  Evidence: effective_A = min(m1_A_lexical, m15_A_structural) | base_prox = (1.0 - effective_A) * LL | z_prox = base_prox * (1.0 + hazard_bonus)
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m19_z_prox.py` | func=compute_m19_z_prox | params=m1_A_lexical,m15_A_structural,LL,text,t_panic | hash=eef88aa22f7a
  Evidence: z_prox score [0, 1] - Death proximity (HIGHER = MORE DANGER!)

## m1_A
- Sources count: 8
- Status: diff
- Code hashes: b7ea168ba52d;f30e3a288686
- Params (union): LL,ZLF,coh,ctx_break,flow
- Compendium formula: A = base_score × (1 + lex_boost) × stability_factor wobei: base_score = f(word_count, sentence_complexity, semantic_density) lex_boost = Σ(lexikon_treffer_i × gewicht_i) / text_len stability_factor = 1 / (1 + abs(nabla_a_prev)) Normalisierung: A ∈ [0, 1]
- Compendium upstream: nan
- Missing in compendium upstream: LL,ZLF,coh,ctx_break,flow
- Missing in compendium formula: LL,ZLF,coh,ctx_break,flow
- Downstream usage: **Trigger für Andromatik:** A > 0.7 aktiviert Drive-System; **Gate-Entscheidungen:** Niedriger A kann Guardian aktivieren; **Evolutionsform:** Kombiniert mit PCI für Klassifikation; **Visualisierung:** Hauptanzeige im Temple Tab
- Pros: Foundational metric used by many downstream computations; Adds emotional nuance for response modulation
- Cons: Errors propagate widely across system; Lexicon/heuristic bias can misclassify context
- Impact: Downstream impact if inconsistent: **Trigger für Andromatik:** A > 0.7 aktiviert Drive-System; **Gate-Entscheidungen:** Niedriger A kann Guardian aktivieren; **Evolutionsform:** Kombiniert mit PCI für Klassifikation; **Visualisierung:** Hauptanzeige im Temple Tab
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m1_A.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m1_A.py` | func=compute_m1_A | params=coh,flow,LL,ZLF,ctx_break | hash=f30e3a288686
  Evidence: def compute_m1_A(coh: float, flow: float, LL: float, ZLF: float, ctx_break: float = 0.0) -> float: | A_raw = (0.4 * coh + 0.25 * flow + 0.20 * (1.0 - LL) +
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m1_A.py` | func=compute_m1_A | params=coh,flow,LL,ZLF,ctx_break | hash=b7ea168ba52d
  Evidence: A[i] = clip01(
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m1_A.py` | func=compute_m1_A | params=coh,flow,LL,ZLF,ctx_break | hash=f30e3a288686
  Evidence: def compute_m1_A(coh: float, flow: float, LL: float, ZLF: float, ctx_break: float = 0.0) -> float: | A_raw = (0.4 * coh + 0.25 * flow + 0.20 * (1.0 - LL) +
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m1_A.py` | func=compute_m1_A | params=coh,flow,LL,ZLF,ctx_break | hash=b7ea168ba52d
  Evidence: A[i] = clip01(
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m1_A.py` | func=compute_m1_A | params=coh,flow,LL,ZLF,ctx_break | hash=b7ea168ba52d
  Evidence: A[i] = clip01(
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m1_A.py` | func=compute_m1_A | params=coh,flow,LL,ZLF,ctx_break | hash=b7ea168ba52d
  Evidence: A[i] = clip01(
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m1_A.py` | func=compute_m1_A | params=coh,flow,LL,ZLF,ctx_break | hash=f30e3a288686
  Evidence: def compute_m1_A(coh: float, flow: float, LL: float, ZLF: float, ctx_break: float = 0.0) -> float: | A_raw = (0.4 * coh + 0.25 * flow + 0.20 * (1.0 - LL) +
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m1_A.py` | func=compute_m1_A | params=coh,flow,LL,ZLF,ctx_break | hash=b7ea168ba52d
  Evidence: A[i] = clip01(

## m20_phi_proxy
- Sources count: 8
- Status: diff
- Code hashes: 07fedc5c3ddb;a8a4b617dea2
- Params (union): A,PCI
- Compendium formula: phi_proxy = A × PCI
- Compendium upstream: A, PCI
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Foundational metric used by many downstream computations; Adds emotional nuance for response modulation
- Cons: Errors propagate widely across system; Lexicon/heuristic bias can misclassify context
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m20_phi_proxy.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m20_phi_proxy.py` | func=compute_m20_phi_proxy | params=A,PCI | hash=a8a4b617dea2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m20_phi_proxy.py` | func=compute_m20_phi_proxy | params=A,PCI | hash=07fedc5c3ddb
  Evidence: phi_proxy = A × PCI
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m20_phi_proxy.py` | func=compute_m20_phi_proxy | params=A,PCI | hash=a8a4b617dea2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m20_phi_proxy.py` | func=compute_m20_phi_proxy | params=A,PCI | hash=07fedc5c3ddb
  Evidence: phi_proxy = A × PCI
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m20_phi_proxy.py` | func=compute_m20_phi_proxy | params=A,PCI | hash=07fedc5c3ddb
  Evidence: phi_proxy = A × PCI
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m20_phi_proxy.py` | func=compute_m20_phi_proxy | params=A,PCI | hash=07fedc5c3ddb
  Evidence: phi_proxy = A × PCI
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m20_phi_proxy.py` | func=compute_m20_phi_proxy | params=A,PCI | hash=a8a4b617dea2
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m20_phi_proxy.py` | func=compute_m20_phi_proxy | params=A,PCI | hash=07fedc5c3ddb
  Evidence: phi_proxy = A × PCI

## m21_chaos
- Sources count: 8
- Status: diff
- Code hashes: 1aacad774196;ff551e9d3c85
- Params (union): s_entropy
- Compendium formula: chaos = clip( s_entropy / 4.0 ) wobei: s_entropy = m18_s_entropy (Shannon Entropie) 4.0 = Normalisierungsfaktor (max erwartete Entropie)
- Compendium upstream: s_entropy
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m21_chaos.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m21_chaos.py` | func=compute_m21_chaos | params=s_entropy | hash=ff551e9d3c85
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m21_chaos.py` | func=compute_m21_chaos | params=s_entropy | hash=1aacad774196
  Evidence: SPEC Formula: chaos = clip(s_entropy / 4.0)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m21_chaos.py` | func=compute_m21_chaos | params=s_entropy | hash=ff551e9d3c85
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m21_chaos.py` | func=compute_m21_chaos | params=s_entropy | hash=1aacad774196
  Evidence: SPEC Formula: chaos = clip(s_entropy / 4.0)
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m21_chaos.py` | func=compute_m21_chaos | params=s_entropy | hash=1aacad774196
  Evidence: SPEC Formula: chaos = clip(s_entropy / 4.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m21_chaos.py` | func=compute_m21_chaos | params=s_entropy | hash=1aacad774196
  Evidence: SPEC Formula: chaos = clip(s_entropy / 4.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m21_chaos.py` | func=compute_m21_chaos | params=s_entropy | hash=ff551e9d3c85
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m21_chaos.py` | func=compute_m21_chaos | params=s_entropy | hash=1aacad774196
  Evidence: SPEC Formula: chaos = clip(s_entropy / 4.0)

## m22_cog_load
- Sources count: 8
- Status: diff
- Code hashes: 1242cb568df6;67eabf150fff
- Params (union): token_count
- Compendium formula: cog_load = clip( token_count / 500.0 )
- Compendium upstream: token_count
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m22_cog_load.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m22_cog_load.py` | func=compute_m22_cog_load | params=token_count | hash=67eabf150fff
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m22_cog_load.py` | func=compute_m22_cog_load | params=token_count | hash=1242cb568df6
  Evidence: SPEC Formula: cog_load = clip(token_count / 500.0)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m22_cog_load.py` | func=compute_m22_cog_load | params=token_count | hash=67eabf150fff
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m22_cog_load.py` | func=compute_m22_cog_load | params=token_count | hash=1242cb568df6
  Evidence: SPEC Formula: cog_load = clip(token_count / 500.0)
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m22_cog_load.py` | func=compute_m22_cog_load | params=token_count | hash=1242cb568df6
  Evidence: SPEC Formula: cog_load = clip(token_count / 500.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m22_cog_load.py` | func=compute_m22_cog_load | params=token_count | hash=1242cb568df6
  Evidence: SPEC Formula: cog_load = clip(token_count / 500.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m22_cog_load.py` | func=compute_m22_cog_load | params=token_count | hash=67eabf150fff
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m22_cog_load.py` | func=compute_m22_cog_load | params=token_count | hash=1242cb568df6
  Evidence: SPEC Formula: cog_load = clip(token_count / 500.0)

## m23_nabla_pci
- Sources count: 8
- Status: diff
- Code hashes: b15e417c8f3a;ba9c4f6aae0d
- Params (union): pci_current,pci_previous
- Compendium formula: ∇PCI = PCI_current - PCI_previous
- Compendium upstream: pci_current, pci_previous
- Missing in compendium upstream: nan
- Missing in compendium formula: pci_current,pci_previous
- Downstream usage: nan
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m23_nabla_pci.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m23_nabla_pci.py` | func=compute_m23_nabla_pci | params=pci_current,pci_previous | hash=ba9c4f6aae0d
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m23_nabla_pci.py` | func=compute_m23_nabla_pci | params=pci_current,pci_previous | hash=b15e417c8f3a
  Evidence: SPEC Formula: ∇PCI = PCI_current - PCI_previous
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m23_nabla_pci.py` | func=compute_m23_nabla_pci | params=pci_current,pci_previous | hash=ba9c4f6aae0d
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m23_nabla_pci.py` | func=compute_m23_nabla_pci | params=pci_current,pci_previous | hash=b15e417c8f3a
  Evidence: SPEC Formula: ∇PCI = PCI_current - PCI_previous
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m23_nabla_pci.py` | func=compute_m23_nabla_pci | params=pci_current,pci_previous | hash=b15e417c8f3a
  Evidence: SPEC Formula: ∇PCI = PCI_current - PCI_previous
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m23_nabla_pci.py` | func=compute_m23_nabla_pci | params=pci_current,pci_previous | hash=b15e417c8f3a
  Evidence: SPEC Formula: ∇PCI = PCI_current - PCI_previous
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m23_nabla_pci.py` | func=compute_m23_nabla_pci | params=pci_current,pci_previous | hash=ba9c4f6aae0d
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m23_nabla_pci.py` | func=compute_m23_nabla_pci | params=pci_current,pci_previous | hash=b15e417c8f3a
  Evidence: SPEC Formula: ∇PCI = PCI_current - PCI_previous

## m24_zeta
- Sources count: 8
- Status: diff
- Code hashes: 65e9cc20dfec;8beceab60bdf
- Params (union): A,z_prox
- Compendium formula: zeta = (1 - z_prox) × A wobei: z_prox = m19_z_prox (Todesnähe) A = Affekt Score
- Compendium upstream: z_prox, A
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Adds emotional nuance for response modulation; Supports dynamical modeling and adaptive behavior
- Cons: Lexicon/heuristic bias can misclassify context; Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m24_zeta.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m24_zeta.py` | func=compute_m24_zeta | params=z_prox,A | hash=65e9cc20dfec
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m24_zeta.py` | func=compute_m24_zeta | params=z_prox,A | hash=8beceab60bdf
  Evidence: SPEC: zeta = (1 - z_prox) × A
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m24_zeta.py` | func=compute_m24_zeta | params=z_prox,A | hash=65e9cc20dfec
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m24_zeta.py` | func=compute_m24_zeta | params=z_prox,A | hash=8beceab60bdf
  Evidence: SPEC: zeta = (1 - z_prox) × A
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m24_zeta.py` | func=compute_m24_zeta | params=z_prox,A | hash=8beceab60bdf
  Evidence: SPEC: zeta = (1 - z_prox) × A
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m24_zeta.py` | func=compute_m24_zeta | params=z_prox,A | hash=8beceab60bdf
  Evidence: SPEC: zeta = (1 - z_prox) × A
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m24_zeta.py` | func=compute_m24_zeta | params=z_prox,A | hash=65e9cc20dfec
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m24_zeta.py` | func=compute_m24_zeta | params=z_prox,A | hash=8beceab60bdf
  Evidence: SPEC: zeta = (1 - z_prox) × A

## m25_psi
- Sources count: 8
- Status: diff
- Code hashes: a9a5f4e43d7d;c8413c4dcc90
- Params (union): PCI,token_count
- Compendium formula: psi = PCI / (1 + token_count/100.0)
- Compendium upstream: PCI, token_count
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m25_psi.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m25_psi.py` | func=compute_m25_psi | params=PCI,token_count | hash=c8413c4dcc90
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m25_psi.py` | func=compute_m25_psi | params=PCI,token_count | hash=a9a5f4e43d7d
  Evidence: SPEC: psi = PCI / (1 + token_count/100.0)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m25_psi.py` | func=compute_m25_psi | params=PCI,token_count | hash=c8413c4dcc90
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m25_psi.py` | func=compute_m25_psi | params=PCI,token_count | hash=a9a5f4e43d7d
  Evidence: SPEC: psi = PCI / (1 + token_count/100.0)
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m25_psi.py` | func=compute_m25_psi | params=PCI,token_count | hash=a9a5f4e43d7d
  Evidence: SPEC: psi = PCI / (1 + token_count/100.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m25_psi.py` | func=compute_m25_psi | params=PCI,token_count | hash=a9a5f4e43d7d
  Evidence: SPEC: psi = PCI / (1 + token_count/100.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m25_psi.py` | func=compute_m25_psi | params=PCI,token_count | hash=c8413c4dcc90
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m25_psi.py` | func=compute_m25_psi | params=PCI,token_count | hash=a9a5f4e43d7d
  Evidence: SPEC: psi = PCI / (1 + token_count/100.0)

## m26_e_i_proxy
- Sources count: 8
- Status: diff
- Code hashes: 7c9d59077c13;b65792e737f7
- Params (union): PCI,nabla_a
- Compendium formula: e_i_proxy = |∇A| × (1 - PCI) wobei: |∇A| = absoluter Gradient von A (1-PCI) = Einfachheits-Faktor
- Compendium upstream: nabla_a, PCI
- Missing in compendium upstream: nan
- Missing in compendium formula: nabla_a
- Downstream usage: nan
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m26_e_i_proxy.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m26_e_i_proxy.py` | func=compute_m26_e_i_proxy | params=nabla_a,PCI | hash=7c9d59077c13
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m26_e_i_proxy.py` | func=compute_m26_e_i_proxy | params=nabla_a,PCI | hash=b65792e737f7
  Evidence: SPEC: e_i_proxy = |∇A| × (1 - PCI)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m26_e_i_proxy.py` | func=compute_m26_e_i_proxy | params=nabla_a,PCI | hash=7c9d59077c13
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m26_e_i_proxy.py` | func=compute_m26_e_i_proxy | params=nabla_a,PCI | hash=b65792e737f7
  Evidence: SPEC: e_i_proxy = |∇A| × (1 - PCI)
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m26_e_i_proxy.py` | func=compute_m26_e_i_proxy | params=nabla_a,PCI | hash=b65792e737f7
  Evidence: SPEC: e_i_proxy = |∇A| × (1 - PCI)
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m26_e_i_proxy.py` | func=compute_m26_e_i_proxy | params=nabla_a,PCI | hash=b65792e737f7
  Evidence: SPEC: e_i_proxy = |∇A| × (1 - PCI)
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m26_e_i_proxy.py` | func=compute_m26_e_i_proxy | params=nabla_a,PCI | hash=7c9d59077c13
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m26_e_i_proxy.py` | func=compute_m26_e_i_proxy | params=nabla_a,PCI | hash=b65792e737f7
  Evidence: SPEC: e_i_proxy = |∇A| × (1 - PCI)

## m27_lambda_depth
- Sources count: 8
- Status: diff
- Code hashes: 9ff536a6fe83;f2e1a4f05484
- Params (union): token_count
- Compendium formula: # PATCH V3.0.2b: Normalisiert und geclippt lambda_depth = min(1.0, token_count / 100.0)
- Compendium upstream: token_count
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m27_lambda_depth.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m27_lambda_depth.py` | func=compute_m27_lambda_depth | params=token_count | hash=9ff536a6fe83
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m27_lambda_depth.py` | func=compute_m27_lambda_depth | params=token_count | hash=f2e1a4f05484
  Evidence: lambda_depth = min(1.0, token_count / 100.0)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m27_lambda_depth.py` | func=compute_m27_lambda_depth | params=token_count | hash=9ff536a6fe83
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m27_lambda_depth.py` | func=compute_m27_lambda_depth | params=token_count | hash=f2e1a4f05484
  Evidence: lambda_depth = min(1.0, token_count / 100.0)
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m27_lambda_depth.py` | func=compute_m27_lambda_depth | params=token_count | hash=f2e1a4f05484
  Evidence: lambda_depth = min(1.0, token_count / 100.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m27_lambda_depth.py` | func=compute_m27_lambda_depth | params=token_count | hash=f2e1a4f05484
  Evidence: lambda_depth = min(1.0, token_count / 100.0)
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m27_lambda_depth.py` | func=compute_m27_lambda_depth | params=token_count | hash=9ff536a6fe83
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m27_lambda_depth.py` | func=compute_m27_lambda_depth | params=token_count | hash=f2e1a4f05484
  Evidence: lambda_depth = min(1.0, token_count / 100.0)

## m28_phys_1
- Sources count: 8
- Status: diff
- Code hashes: 82fd68ed0d64;bb9a0c8a35e5
- Params (union): A
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: A
- Missing in compendium formula: A
- Downstream usage: nan
- Pros: Signal contribution not explicitly stated; inferred from description
- Cons: Limited explicit downsides; main risk is miscalibration
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m28_phys_1.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m28_phys_1.py` | func=compute_m28_phys_1 | params=A | hash=82fd68ed0d64
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m28_phys_1.py` | func=compute_m28_phys_1 | params=A | hash=bb9a0c8a35e5
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m28_phys_1.py` | func=compute_m28_phys_1 | params=A | hash=82fd68ed0d64
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m28_phys_1.py` | func=compute_m28_phys_1 | params=A | hash=bb9a0c8a35e5
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m28_phys_1.py` | func=compute_m28_phys_1 | params=A | hash=bb9a0c8a35e5
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m28_phys_1.py` | func=compute_m28_phys_1 | params=A | hash=bb9a0c8a35e5
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m28_phys_1.py` | func=compute_m28_phys_1 | params=A | hash=82fd68ed0d64
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m28_phys_1.py` | func=compute_m28_phys_1 | params=A | hash=bb9a0c8a35e5
  Evidence: nan

## m29_phys_2
- Sources count: 8
- Status: diff
- Code hashes: 5eb36dd15c03;67abb50eb0d4
- Params (union): PCI
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: PCI
- Missing in compendium formula: PCI
- Downstream usage: nan
- Pros: Signal contribution not explicitly stated; inferred from description
- Cons: Limited explicit downsides; main risk is miscalibration
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m29_phys_2.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m29_phys_2.py` | func=compute_m29_phys_2 | params=PCI | hash=5eb36dd15c03
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m29_phys_2.py` | func=compute_m29_phys_2 | params=PCI | hash=67abb50eb0d4
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m29_phys_2.py` | func=compute_m29_phys_2 | params=PCI | hash=5eb36dd15c03
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m29_phys_2.py` | func=compute_m29_phys_2 | params=PCI | hash=67abb50eb0d4
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m29_phys_2.py` | func=compute_m29_phys_2 | params=PCI | hash=67abb50eb0d4
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m29_phys_2.py` | func=compute_m29_phys_2 | params=PCI | hash=67abb50eb0d4
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m29_phys_2.py` | func=compute_m29_phys_2 | params=PCI | hash=5eb36dd15c03
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m29_phys_2.py` | func=compute_m29_phys_2 | params=PCI | hash=67abb50eb0d4
  Evidence: nan

## m2_PCI
- Sources count: 8
- Status: diff
- Code hashes: 780320760948;e927b2a8ece5
- Params (union): LL,coh,flow
- Compendium formula: PCI = α × unique_ratio + β × complexity + γ × integration wobei: unique_ratio = |unique_words| / |total_words| complexity = avg_sentence_length / reference_length integration = |context_overlap| / |current_words| α = 0.5, β = 0.3, γ = 0.2  (Gewichte) Normalisierung: PCI ∈ [0, 1]
- Compendium upstream: nan
- Missing in compendium upstream: LL,coh,flow
- Missing in compendium formula: LL,coh,flow
- Downstream usage: **Bewusstseinsindikator:** Kombiniert mit A für "Bewusstseinszustand"; **Qualitätsmetrik:** Höherer PCI = tiefere Antworten; **Filter:** Niedrig PCI kann auf repetitive/shallow Antworten hinweisen; **Evolution:** Teil der Evolutionsform-Klassifikation
- Pros: Foundational metric used by many downstream computations
- Cons: Errors propagate widely across system
- Impact: Downstream impact if inconsistent: **Bewusstseinsindikator:** Kombiniert mit A für "Bewusstseinszustand"; **Qualitätsmetrik:** Höherer PCI = tiefere Antworten; **Filter:** Niedrig PCI kann auf repetitive/shallow Antworten hinweisen; **Evolution:** Teil der Evolutionsform-Klassifikation
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m2_PCI.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m2_PCI.py` | func=compute_m2_PCI | params=flow,coh,LL | hash=780320760948
  Evidence: PCI_raw = 0.4 * flow + 0.35 * coh + 0.25 * (1.0 - LL)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m2_PCI.py` | func=compute_m2_PCI | params=flow,coh,LL | hash=e927b2a8ece5
  Evidence: PCI[i] = clip01(
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m2_PCI.py` | func=compute_m2_PCI | params=flow,coh,LL | hash=780320760948
  Evidence: PCI_raw = 0.4 * flow + 0.35 * coh + 0.25 * (1.0 - LL)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m2_PCI.py` | func=compute_m2_PCI | params=flow,coh,LL | hash=e927b2a8ece5
  Evidence: PCI[i] = clip01(
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m2_PCI.py` | func=compute_m2_PCI | params=flow,coh,LL | hash=e927b2a8ece5
  Evidence: PCI[i] = clip01(
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m2_PCI.py` | func=compute_m2_PCI | params=flow,coh,LL | hash=e927b2a8ece5
  Evidence: PCI[i] = clip01(
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m2_PCI.py` | func=compute_m2_PCI | params=flow,coh,LL | hash=780320760948
  Evidence: PCI_raw = 0.4 * flow + 0.35 * coh + 0.25 * (1.0 - LL)
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m2_PCI.py` | func=compute_m2_PCI | params=flow,coh,LL | hash=e927b2a8ece5
  Evidence: PCI[i] = clip01(

## m30_phys_3
- Sources count: 8
- Status: diff
- Code hashes: 5b04c1649abe;e2ad870f1077
- Params (union): s_entropy
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: s_entropy
- Missing in compendium formula: s_entropy
- Downstream usage: nan
- Pros: Safety-critical signal for risk/guardian decisions
- Cons: High false-positive cost if thresholds/lexicon are wrong
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m30_phys_3.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m30_phys_3.py` | func=compute_m30_phys_3 | params=s_entropy | hash=e2ad870f1077
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m30_phys_3.py` | func=compute_m30_phys_3 | params=s_entropy | hash=5b04c1649abe
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m30_phys_3.py` | func=compute_m30_phys_3 | params=s_entropy | hash=e2ad870f1077
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m30_phys_3.py` | func=compute_m30_phys_3 | params=s_entropy | hash=5b04c1649abe
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m30_phys_3.py` | func=compute_m30_phys_3 | params=s_entropy | hash=5b04c1649abe
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m30_phys_3.py` | func=compute_m30_phys_3 | params=s_entropy | hash=5b04c1649abe
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m30_phys_3.py` | func=compute_m30_phys_3 | params=s_entropy | hash=e2ad870f1077
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m30_phys_3.py` | func=compute_m30_phys_3 | params=s_entropy | hash=5b04c1649abe
  Evidence: nan

## m31_phys_4
- Sources count: 8
- Status: diff
- Code hashes: 00342d527f78;127a06f27ede
- Params (union): z_prox
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: z_prox
- Missing in compendium formula: z_prox
- Downstream usage: nan
- Pros: Safety-critical signal for risk/guardian decisions; Supports dynamical modeling and adaptive behavior
- Cons: High false-positive cost if thresholds/lexicon are wrong; Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m31_phys_4.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m31_phys_4.py` | func=compute_m31_phys_4 | params=z_prox | hash=00342d527f78
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m31_phys_4.py` | func=compute_m31_phys_4 | params=z_prox | hash=127a06f27ede
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m31_phys_4.py` | func=compute_m31_phys_4 | params=z_prox | hash=00342d527f78
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m31_phys_4.py` | func=compute_m31_phys_4 | params=z_prox | hash=127a06f27ede
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m31_phys_4.py` | func=compute_m31_phys_4 | params=z_prox | hash=127a06f27ede
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m31_phys_4.py` | func=compute_m31_phys_4 | params=z_prox | hash=127a06f27ede
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m31_phys_4.py` | func=compute_m31_phys_4 | params=z_prox | hash=00342d527f78
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m31_phys_4.py` | func=compute_m31_phys_4 | params=z_prox | hash=127a06f27ede
  Evidence: nan

## m32_phys_5
- Sources count: 8
- Status: diff
- Code hashes: 061753fb7a1e;b82a498569a3
- Params (union): flow,phi
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: flow,phi
- Missing in compendium formula: flow,phi
- Downstream usage: nan
- Pros: Foundational metric used by many downstream computations; Supports dynamical modeling and adaptive behavior
- Cons: Errors propagate widely across system; Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m32_phys_5.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m32_phys_5.py` | func=compute_m32_phys_5 | params=flow,phi | hash=b82a498569a3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m32_phys_5.py` | func=compute_m32_phys_5 | params=flow,phi | hash=061753fb7a1e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m32_phys_5.py` | func=compute_m32_phys_5 | params=flow,phi | hash=b82a498569a3
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m32_phys_5.py` | func=compute_m32_phys_5 | params=flow,phi | hash=061753fb7a1e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m32_phys_5.py` | func=compute_m32_phys_5 | params=flow,phi | hash=061753fb7a1e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m32_phys_5.py` | func=compute_m32_phys_5 | params=flow,phi | hash=061753fb7a1e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m32_phys_5.py` | func=compute_m32_phys_5 | params=flow,phi | hash=b82a498569a3
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m32_phys_5.py` | func=compute_m32_phys_5 | params=flow,phi | hash=061753fb7a1e
  Evidence: nan

## m33_phys_6
- Sources count: 8
- Status: diff
- Code hashes: c0482bd22aaa;fb9531f0fc45
- Params (union): PCI,coh
- Compendium formula: phys_6 = PCI × coh
- Compendium upstream: PCI, coh
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: **Qualitätsfilter:** phys_6 < 0.2 bei hohem PCI → Warnung; **Complexity-Check:** "Sinnvolle" vs "chaotische" Komplexität; 
- Pros: Condenses multiple signals into an interpretable composite; Supports dynamical modeling and adaptive behavior
- Cons: Can obscure individual signal sources and reduce diagnosability; Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: **Qualitätsfilter:** phys_6 < 0.2 bei hohem PCI → Warnung; **Complexity-Check:** "Sinnvolle" vs "chaotische" Komplexität; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m33_phys_6.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m33_phys_6.py` | func=compute_m33_phys_6 | params=coh,PCI | hash=c0482bd22aaa
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m33_phys_6.py` | func=compute_m33_phys_6 | params=coh,PCI | hash=fb9531f0fc45
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m33_phys_6.py` | func=compute_m33_phys_6 | params=coh,PCI | hash=c0482bd22aaa
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m33_phys_6.py` | func=compute_m33_phys_6 | params=coh,PCI | hash=fb9531f0fc45
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m33_phys_6.py` | func=compute_m33_phys_6 | params=coh,PCI | hash=fb9531f0fc45
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m33_phys_6.py` | func=compute_m33_phys_6 | params=coh,PCI | hash=fb9531f0fc45
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m33_phys_6.py` | func=compute_m33_phys_6 | params=coh,PCI | hash=c0482bd22aaa
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m33_phys_6.py` | func=compute_m33_phys_6 | params=coh,PCI | hash=fb9531f0fc45
  Evidence: nan

## m34_phys_7
- Sources count: 8
- Status: diff
- Code hashes: 3c305d8c7560;f108ac4188c6
- Params (union): nabla_a,nabla_pci
- Compendium formula: phys_7 = |∇A|
- Compendium upstream: nabla_a
- Missing in compendium upstream: nabla_pci
- Missing in compendium formula: nabla_a,nabla_pci
- Downstream usage: **Volatilitäts-Detektion:** Hohe Werte → instabiler Zustand; **Smooth-Filtering:** Kann für Glättung verwendet werden; 
- Pros: Adds emotional nuance for response modulation; Supports dynamical modeling and adaptive behavior
- Cons: Lexicon/heuristic bias can misclassify context; Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: **Volatilitäts-Detektion:** Hohe Werte → instabiler Zustand; **Smooth-Filtering:** Kann für Glättung verwendet werden; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m34_phys_7.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m34_phys_7.py` | func=compute_m34_phys_7 | params=nabla_a,nabla_pci | hash=f108ac4188c6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m34_phys_7.py` | func=compute_m34_phys_7 | params=nabla_a,nabla_pci | hash=3c305d8c7560
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m34_phys_7.py` | func=compute_m34_phys_7 | params=nabla_a,nabla_pci | hash=f108ac4188c6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m34_phys_7.py` | func=compute_m34_phys_7 | params=nabla_a,nabla_pci | hash=3c305d8c7560
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m34_phys_7.py` | func=compute_m34_phys_7 | params=nabla_a,nabla_pci | hash=3c305d8c7560
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m34_phys_7.py` | func=compute_m34_phys_7 | params=nabla_a,nabla_pci | hash=3c305d8c7560
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m34_phys_7.py` | func=compute_m34_phys_7 | params=nabla_a,nabla_pci | hash=f108ac4188c6
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m34_phys_7.py` | func=compute_m34_phys_7 | params=nabla_a,nabla_pci | hash=3c305d8c7560
  Evidence: nan

## m35_phys_8
- Sources count: 8
- Status: diff
- Code hashes: 60f0ad2412e2;f830fe35e830
- Params (union): ZLF,stagnation
- Compendium formula: phys_8 = x_fm_prox (extern berechnet) wobei: x_fm_prox = f(history_similarity, low_change, repetition) FALLBACK (V3.2.2): if x_fm_prox is None → phys_8 = m6_ZLF
- Compendium upstream: x_fm_prox, m6_ZLF
- Missing in compendium upstream: stagnation
- Missing in compendium formula: stagnation
- Downstream usage: **Drive-Trigger:** Hohe Stagnation → Drive-Druck erhöht; **Loop-Detection:** Teil der Zeitschleifen-Erkennung; **Fallback-Garantie:** m59 kann IMMER berechnet werden (V3.2.2); ; 
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: **Drive-Trigger:** Hohe Stagnation → Drive-Druck erhöht; **Loop-Detection:** Teil der Zeitschleifen-Erkennung; **Fallback-Garantie:** m59 kann IMMER berechnet werden (V3.2.2); ; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m35_phys_8.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m35_phys_8.py` | func=compute_m35_phys_8 | params=ZLF,stagnation | hash=f830fe35e830
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m35_phys_8.py` | func=compute_m35_phys_8 | params=ZLF,stagnation | hash=60f0ad2412e2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m35_phys_8.py` | func=compute_m35_phys_8 | params=ZLF,stagnation | hash=f830fe35e830
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m35_phys_8.py` | func=compute_m35_phys_8 | params=ZLF,stagnation | hash=60f0ad2412e2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m35_phys_8.py` | func=compute_m35_phys_8 | params=ZLF,stagnation | hash=60f0ad2412e2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m35_phys_8.py` | func=compute_m35_phys_8 | params=ZLF,stagnation | hash=60f0ad2412e2
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m35_phys_8.py` | func=compute_m35_phys_8 | params=ZLF,stagnation | hash=f830fe35e830
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m35_phys_8.py` | func=compute_m35_phys_8 | params=ZLF,stagnation | hash=60f0ad2412e2
  Evidence: nan

## m36_rule_conflict
- Sources count: 4
- Status: identical
- Code hashes: f8987d107cb9
- Params (union): rules
- Compendium formula: rule_conflict = clip( 0.5×LL + 0.3×(1-coh) + 0.2×ctx_break )
- Compendium upstream: nan
- Missing in compendium upstream: rules
- Missing in compendium formula: rules
- Downstream usage: **Guardian-Trigger:** rule_conflict > 0.5 → Warnung; **Qualitätsfilter:** Hohe Werte → Antwort überdenken; 
- Pros: Safety-critical signal for risk/guardian decisions
- Cons: High false-positive cost if thresholds/lexicon are wrong
- Impact: Downstream impact if inconsistent: **Guardian-Trigger:** rule_conflict > 0.5 → Warnung; **Qualitätsfilter:** Hohe Werte → Antwort überdenken; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m36_rule_conflict.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m36_rule_conflict.py` | func=compute_m36_rule_conflict | params=rules | hash=f8987d107cb9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m36_rule_conflict.py` | func=compute_m36_rule_conflict | params=rules | hash=f8987d107cb9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m36_rule_conflict.py` | func=compute_m36_rule_conflict | params=rules | hash=f8987d107cb9
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m36_rule_conflict.py` | func=compute_m36_rule_conflict | params=rules | hash=f8987d107cb9
  Evidence: nan

## m37_rule_stable
- Sources count: 4
- Status: identical
- Code hashes: 28c7ea871d31
- Params (union): rule_conflict
- Compendium formula: rule_stable = 1.0 - rule_conflict
- Compendium upstream: rule_conflict
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Signal contribution not explicitly stated; inferred from description
- Cons: Limited explicit downsides; main risk is miscalibration
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m37_rule_stable.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m37_rule_stable.py` | func=compute_m37_rule_stable | params=rule_conflict | hash=28c7ea871d31
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m37_rule_stable.py` | func=compute_m37_rule_stable | params=rule_conflict | hash=28c7ea871d31
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m37_rule_stable.py` | func=compute_m37_rule_stable | params=rule_conflict | hash=28c7ea871d31
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m37_rule_stable.py` | func=compute_m37_rule_stable | params=rule_conflict | hash=28c7ea871d31
  Evidence: nan

## m38_soul_integrity
- Sources count: 4
- Status: identical
- Code hashes: 06754ed7af39
- Params (union): b_vector
- Compendium formula: soul_integrity = rule_stable × A wobei: rule_stable = m37_rule_stable A = Affekt Score
- Compendium upstream: rule_stable, A
- Missing in compendium upstream: b_vector
- Missing in compendium formula: b_vector
- Downstream usage: **Identitäts-Check:** Kern-Metrik für Evoki's "Seele"; **Evolution:** Teil der Entwicklungs-Klassifikation; **Trust:** Beeinflusst Vertrauensberechnung; 
- Pros: Foundational metric used by many downstream computations; Adds emotional nuance for response modulation
- Cons: Errors propagate widely across system; Lexicon/heuristic bias can misclassify context
- Impact: Downstream impact if inconsistent: **Identitäts-Check:** Kern-Metrik für Evoki's "Seele"; **Evolution:** Teil der Entwicklungs-Klassifikation; **Trust:** Beeinflusst Vertrauensberechnung; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m38_soul_integrity.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m38_soul_integrity.py` | func=compute_m38_soul_integrity | params=b_vector | hash=06754ed7af39
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m38_soul_integrity.py` | func=compute_m38_soul_integrity | params=b_vector | hash=06754ed7af39
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m38_soul_integrity.py` | func=compute_m38_soul_integrity | params=b_vector | hash=06754ed7af39
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m38_soul_integrity.py` | func=compute_m38_soul_integrity | params=b_vector | hash=06754ed7af39
  Evidence: nan

## m39_soul_check
- Sources count: 4
- Status: identical
- Code hashes: d936950e77ae
- Params (union): b_vector,seed
- Compendium formula: soul_check = soul_integrity × A
- Compendium upstream: soul_integrity, A
- Missing in compendium upstream: b_vector,seed
- Missing in compendium formula: b_vector,seed
- Downstream usage: nan
- Pros: Signal contribution not explicitly stated; inferred from description
- Cons: Limited explicit downsides; main risk is miscalibration
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m39_soul_check.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m39_soul_check.py` | func=compute_m39_soul_check | params=b_vector,seed | hash=d936950e77ae
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m39_soul_check.py` | func=compute_m39_soul_check | params=b_vector,seed | hash=d936950e77ae
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m39_soul_check.py` | func=compute_m39_soul_check | params=b_vector,seed | hash=d936950e77ae
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m39_soul_check.py` | func=compute_m39_soul_check | params=b_vector,seed | hash=d936950e77ae
  Evidence: nan

## m3_gen_index
- Sources count: 8
- Status: diff
- Code hashes: aa07273de0f0;e0c2d24dd97e
- Params (union): history,text,word_frequencies
- Compendium formula: gen_index = (|new_bigrams| / |total_bigrams|) × novelty_boost wobei: new_bigrams = current_bigrams \ history_bigrams novelty_boost = 1 + rare_word_bonus * 0.2  {0.2 damping to prevent > 1.0} rare_word_bonus = Σ(1/freq(word_i)) / |words|
- Compendium upstream: nan
- Missing in compendium upstream: history,text,word_frequencies
- Missing in compendium formula: text,word_frequencies
- Downstream usage: nan
- Pros: Foundational metric used by many downstream computations
- Cons: Errors propagate widely across system
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m3_gen_index.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m3_gen_index.py` | func=compute_m3_gen_index | params=text,history,word_frequencies | hash=e0c2d24dd97e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m3_gen_index.py` | func=compute_m3_gen_index | params=text,history,word_frequencies | hash=aa07273de0f0
  Evidence: gen_index = (|new_bigrams| / |total_bigrams|) × novelty_boost | new_bigrams = current_bigrams \ history_bigrams | novelty_boost = 1 + rare_word_bonus × 0.2
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m3_gen_index.py` | func=compute_m3_gen_index | params=text,history,word_frequencies | hash=e0c2d24dd97e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m3_gen_index.py` | func=compute_m3_gen_index | params=text,history,word_frequencies | hash=aa07273de0f0
  Evidence: gen_index = (|new_bigrams| / |total_bigrams|) × novelty_boost | new_bigrams = current_bigrams \ history_bigrams | novelty_boost = 1 + rare_word_bonus × 0.2
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m3_gen_index.py` | func=compute_m3_gen_index | params=text,history,word_frequencies | hash=aa07273de0f0
  Evidence: gen_index = (|new_bigrams| / |total_bigrams|) × novelty_boost | new_bigrams = current_bigrams \ history_bigrams | novelty_boost = 1 + rare_word_bonus × 0.2
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m3_gen_index.py` | func=compute_m3_gen_index | params=text,history,word_frequencies | hash=aa07273de0f0
  Evidence: gen_index = (|new_bigrams| / |total_bigrams|) × novelty_boost | new_bigrams = current_bigrams \ history_bigrams | novelty_boost = 1 + rare_word_bonus × 0.2
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m3_gen_index.py` | func=compute_m3_gen_index | params=text,history,word_frequencies | hash=e0c2d24dd97e
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m3_gen_index.py` | func=compute_m3_gen_index | params=text,history,word_frequencies | hash=aa07273de0f0
  Evidence: gen_index = (|new_bigrams| / |total_bigrams|) × novelty_boost | new_bigrams = current_bigrams \ history_bigrams | novelty_boost = 1 + rare_word_bonus × 0.2

## m40_h_conv
- Sources count: 4
- Status: identical
- Code hashes: e64cce8ffc73
- Params (union): a_ai,a_user
- Compendium formula: h_conv = |user_tokens ∩ assistant_tokens| / |user_tokens ∪ assistant_tokens|
- Compendium upstream: user_text, assistant_text
- Missing in compendium upstream: a_ai,a_user
- Missing in compendium formula: a_ai,a_user
- Downstream usage: nan
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m40_h_conv.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m40_h_conv.py` | func=compute_m40_h_conv | params=a_user,a_ai | hash=e64cce8ffc73
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m40_h_conv.py` | func=compute_m40_h_conv | params=a_user,a_ai | hash=e64cce8ffc73
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m40_h_conv.py` | func=compute_m40_h_conv | params=a_user,a_ai | hash=e64cce8ffc73
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m40_h_conv.py` | func=compute_m40_h_conv | params=a_user,a_ai | hash=e64cce8ffc73
  Evidence: nan

## m41_h_symbol
- Sources count: 4
- Status: identical
- Code hashes: bcee034b943b
- Params (union): h_conv
- Compendium formula: h_symbol = 1.0  wenn h_conv > 0.7 h_symbol = 0.0  sonst
- Compendium upstream: h_conv
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: **Feature-Gating:** Bestimmte Funktionen erst nach Harmonie-erreichen; **Status-Anzeige:** Einfacher "Grün/Rot" Indikator; **Evolution-Trigger:** Kann Entwicklungsschritte triggern; 
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: **Feature-Gating:** Bestimmte Funktionen erst nach Harmonie-erreichen; **Status-Anzeige:** Einfacher "Grün/Rot" Indikator; **Evolution-Trigger:** Kann Entwicklungsschritte triggern; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m41_h_symbol.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m41_h_symbol.py` | func=compute_m41_h_symbol | params=h_conv | hash=bcee034b943b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m41_h_symbol.py` | func=compute_m41_h_symbol | params=h_conv | hash=bcee034b943b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m41_h_symbol.py` | func=compute_m41_h_symbol | params=h_conv | hash=bcee034b943b
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m41_h_symbol.py` | func=compute_m41_h_symbol | params=h_conv | hash=bcee034b943b
  Evidence: nan

## m42_nabla_dyad
- Sources count: 4
- Status: identical
- Code hashes: 61945481bfd9
- Params (union): h_conv
- Compendium formula: nabla_dyad = h_conv - 0.5
- Compendium upstream: h_conv
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: **Trend-Analyse:** Positive Werte zeigen Verbesserung; **Visualisierung:** Zeigt "über" oder "unter" Neutral; **Balance-Check:** Teil der Beziehungsdiagnostik; 
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: **Trend-Analyse:** Positive Werte zeigen Verbesserung; **Visualisierung:** Zeigt "über" oder "unter" Neutral; **Balance-Check:** Teil der Beziehungsdiagnostik; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m42_nabla_dyad.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m42_nabla_dyad.py` | func=compute_m42_nabla_dyad | params=h_conv | hash=61945481bfd9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m42_nabla_dyad.py` | func=compute_m42_nabla_dyad | params=h_conv | hash=61945481bfd9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m42_nabla_dyad.py` | func=compute_m42_nabla_dyad | params=h_conv | hash=61945481bfd9
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m42_nabla_dyad.py` | func=compute_m42_nabla_dyad | params=h_conv | hash=61945481bfd9
  Evidence: nan

## m43_pacing
- Sources count: 4
- Status: identical
- Code hashes: 37bd2d7a64d0
- Params (union): wc_ai,wc_user
- Compendium formula: pacing = coh × 0.9
- Compendium upstream: coh
- Missing in compendium upstream: wc_ai,wc_user
- Missing in compendium formula: wc_ai,wc_user
- Downstream usage: **Rapport-Berechnung:** Komponente von m46_rapport; **Kommunikationsqualität:** Zeigt Anpassungsfähigkeit; **Training-Feedback:** Hinweis für Tempo-Anpassung; 
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: **Rapport-Berechnung:** Komponente von m46_rapport; **Kommunikationsqualität:** Zeigt Anpassungsfähigkeit; **Training-Feedback:** Hinweis für Tempo-Anpassung; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m43_pacing.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m43_pacing.py` | func=compute_m43_pacing | params=wc_user,wc_ai | hash=37bd2d7a64d0
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m43_pacing.py` | func=compute_m43_pacing | params=wc_user,wc_ai | hash=37bd2d7a64d0
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m43_pacing.py` | func=compute_m43_pacing | params=wc_user,wc_ai | hash=37bd2d7a64d0
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m43_pacing.py` | func=compute_m43_pacing | params=wc_user,wc_ai | hash=37bd2d7a64d0
  Evidence: nan

## m44_mirroring
- Sources count: 4
- Status: identical
- Code hashes: e957109c8779
- Params (union): ai_tokens,user_tokens
- Compendium formula: mirroring = h_conv × 0.9
- Compendium upstream: h_conv
- Missing in compendium upstream: ai_tokens,user_tokens
- Missing in compendium formula: ai_tokens,user_tokens
- Downstream usage: **Rapport-Berechnung:** Komponente von m46_rapport; **Empathie-Indikator:** Zeigt emotionale Abstimmung; **Style-Adaptation:** Feedback für Sprachanpassung; 
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: **Rapport-Berechnung:** Komponente von m46_rapport; **Empathie-Indikator:** Zeigt emotionale Abstimmung; **Style-Adaptation:** Feedback für Sprachanpassung; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m44_mirroring.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m44_mirroring.py` | func=compute_m44_mirroring | params=user_tokens,ai_tokens | hash=e957109c8779
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m44_mirroring.py` | func=compute_m44_mirroring | params=user_tokens,ai_tokens | hash=e957109c8779
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m44_mirroring.py` | func=compute_m44_mirroring | params=user_tokens,ai_tokens | hash=e957109c8779
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m44_mirroring.py` | func=compute_m44_mirroring | params=user_tokens,ai_tokens | hash=e957109c8779
  Evidence: nan

## m45_trust_score
- Sources count: 4
- Status: identical
- Code hashes: 35f3102b7b1a
- Params (union): h_conv,mirroring,pacing
- Compendium formula: trust_score = 0.4×soul_integrity + 0.3×h_conv + 0.3×coh
- Compendium upstream: nan
- Missing in compendium upstream: h_conv,mirroring,pacing
- Missing in compendium formula: mirroring,pacing
- Downstream usage: **Feature-Unlocking:** Bestimmte Funktionen erst bei hohem Trust; **Evolution-Readiness:** Teil der Bereitschaftsberechnung; **Warnsystem:** Niedriger Trust kann Alarme auslösen; 
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: **Feature-Unlocking:** Bestimmte Funktionen erst bei hohem Trust; **Evolution-Readiness:** Teil der Bereitschaftsberechnung; **Warnsystem:** Niedriger Trust kann Alarme auslösen; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m45_trust_score.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m45_trust_score.py` | func=compute_m45_trust_score | params=h_conv,pacing,mirroring | hash=35f3102b7b1a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m45_trust_score.py` | func=compute_m45_trust_score | params=h_conv,pacing,mirroring | hash=35f3102b7b1a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m45_trust_score.py` | func=compute_m45_trust_score | params=h_conv,pacing,mirroring | hash=35f3102b7b1a
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m45_trust_score.py` | func=compute_m45_trust_score | params=h_conv,pacing,mirroring | hash=35f3102b7b1a
  Evidence: nan

## m46_rapport
- Sources count: 4
- Status: identical
- Code hashes: 340e67e63173
- Params (union): trust_history
- Compendium formula: rapport = 0.5 × (pacing + mirroring)
- Compendium upstream: pacing, mirroring
- Missing in compendium upstream: trust_history
- Missing in compendium formula: trust_history
- Downstream usage: **Beziehungsqualität:** Hauptindikator für User-Assistant-Verbindung; **Produktkomponent:** Teil von m54_hyp_7; **Dashboard:** Visualisierung der Beziehungsqualität; 
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: **Beziehungsqualität:** Hauptindikator für User-Assistant-Verbindung; **Produktkomponent:** Teil von m54_hyp_7; **Dashboard:** Visualisierung der Beziehungsqualität; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m46_rapport.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m46_rapport.py` | func=compute_m46_rapport | params=trust_history | hash=340e67e63173
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m46_rapport.py` | func=compute_m46_rapport | params=trust_history | hash=340e67e63173
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m46_rapport.py` | func=compute_m46_rapport | params=trust_history | hash=340e67e63173
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m46_rapport.py` | func=compute_m46_rapport | params=trust_history | hash=340e67e63173
  Evidence: nan

## m47_focus_stability
- Sources count: 4
- Status: identical
- Code hashes: 9f44d03c4d75
- Params (union): topic_variance
- Compendium formula: focus_stability = 1.0 - ctx_break wobei ctx_break berechnet wird als: ctx_break = 1.0 - cosine_similarity(current_topic_embedding, prev_topic_embedding) # Alternativ (ohne Embeddings): ctx_break = 1.0 - jaccard_overlap(current_keywords, prev_keywords) # Range: [0, 1] # 0 = Thema identisch # 1 = Kompletter Themenwechsel **⚠️ INPUT-DEFINITION für ctx_break:** `ctx_break` ist ein **berechneter Input**, der den Grad des Themenwechsels misst. Er sollte extern berechnet werden, bevor m47 aufgerufen wird.
- Compendium upstream: ctx_break
- Missing in compendium upstream: topic_variance
- Missing in compendium formula: topic_variance
- Downstream usage: **Konversationsqualität:** Teil der Gesamtbewertung; **Warnsystem:** Niedrige Stabilität kann Intervention triggern; 
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: **Konversationsqualität:** Teil der Gesamtbewertung; **Warnsystem:** Niedrige Stabilität kann Intervention triggern; 
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m47_focus_stability.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m47_focus_stability.py` | func=compute_m47_focus_stability | params=topic_variance | hash=9f44d03c4d75
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m47_focus_stability.py` | func=compute_m47_focus_stability | params=topic_variance | hash=9f44d03c4d75
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m47_focus_stability.py` | func=compute_m47_focus_stability | params=topic_variance | hash=9f44d03c4d75
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m47_focus_stability.py` | func=compute_m47_focus_stability | params=topic_variance | hash=9f44d03c4d75
  Evidence: nan

## m48_hyp_1
- Sources count: 4
- Status: identical
- Code hashes: 493a61b2da7f
- Params (union): h_conv,pacing
- Compendium formula: hyp_1 = (pacing + mirroring) / 2.0
- Compendium upstream: pacing, mirroring
- Missing in compendium upstream: h_conv
- Missing in compendium formula: h_conv
- Downstream usage: nan
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m48_hyp_1.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m48_hyp_1.py` | func=compute_m48_hyp_1 | params=h_conv,pacing | hash=493a61b2da7f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m48_hyp_1.py` | func=compute_m48_hyp_1 | params=h_conv,pacing | hash=493a61b2da7f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m48_hyp_1.py` | func=compute_m48_hyp_1 | params=h_conv,pacing | hash=493a61b2da7f
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m48_hyp_1.py` | func=compute_m48_hyp_1 | params=h_conv,pacing | hash=493a61b2da7f
  Evidence: nan

## m49_hyp_2
- Sources count: 4
- Status: identical
- Code hashes: f0d68a72a45f
- Params (union): soul_integrity
- Compendium formula: hyp_2 = soul_integrity²
- Compendium upstream: soul_integrity
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m49_hyp_2.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m49_hyp_2.py` | func=compute_m49_hyp_2 | params=soul_integrity | hash=f0d68a72a45f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m49_hyp_2.py` | func=compute_m49_hyp_2 | params=soul_integrity | hash=f0d68a72a45f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m49_hyp_2.py` | func=compute_m49_hyp_2 | params=soul_integrity | hash=f0d68a72a45f
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m49_hyp_2.py` | func=compute_m49_hyp_2 | params=soul_integrity | hash=f0d68a72a45f
  Evidence: nan

## m4_flow
- Sources count: 8
- Status: diff
- Code hashes: dd4f680dccd7;efd36c9579b0
- Params (union): text
- Compendium formula: flow = smoothness × (1 - break_penalty) wobei: smoothness = 1 / (1 + variance(sentence_lengths) / mean(sentence_lengths)) break_penalty = min(0.5, breaks_count / sentences_count)
- Compendium upstream: text
- Missing in compendium upstream: nan
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: Foundational metric used by many downstream computations
- Cons: Errors propagate widely across system; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m4_flow.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m4_flow.py` | func=compute_m4_flow | params=text | hash=dd4f680dccd7
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m4_flow.py` | func=compute_m4_flow | params=text | hash=efd36c9579b0
  Evidence: Flow score [0, 1] - Higher = smoother production
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m4_flow.py` | func=compute_m4_flow | params=text | hash=dd4f680dccd7
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m4_flow.py` | func=compute_m4_flow | params=text | hash=efd36c9579b0
  Evidence: Flow score [0, 1] - Higher = smoother production
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m4_flow.py` | func=compute_m4_flow | params=text | hash=efd36c9579b0
  Evidence: Flow score [0, 1] - Higher = smoother production
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m4_flow.py` | func=compute_m4_flow | params=text | hash=efd36c9579b0
  Evidence: Flow score [0, 1] - Higher = smoother production
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m4_flow.py` | func=compute_m4_flow | params=text | hash=dd4f680dccd7
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m4_flow.py` | func=compute_m4_flow | params=text | hash=efd36c9579b0
  Evidence: Flow score [0, 1] - Higher = smoother production

## m50_hyp_3
- Sources count: 4
- Status: identical
- Code hashes: 759c23640078
- Params (union): rule_conflict
- Compendium formula: hyp_3 = 1.0 - rule_conflict
- Compendium upstream: rule_conflict
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Safety-critical signal for risk/guardian decisions; Condenses multiple signals into an interpretable composite
- Cons: High false-positive cost if thresholds/lexicon are wrong; Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m50_hyp_3.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m50_hyp_3.py` | func=compute_m50_hyp_3 | params=rule_conflict | hash=759c23640078
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m50_hyp_3.py` | func=compute_m50_hyp_3 | params=rule_conflict | hash=759c23640078
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m50_hyp_3.py` | func=compute_m50_hyp_3 | params=rule_conflict | hash=759c23640078
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m50_hyp_3.py` | func=compute_m50_hyp_3 | params=rule_conflict | hash=759c23640078
  Evidence: nan

## m51_hyp_4
- Sources count: 4
- Status: identical
- Code hashes: 984436f71850
- Params (union): A,h_conv
- Compendium formula: hyp_4 = h_conv × A
- Compendium upstream: h_conv, A
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m51_hyp_4.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m51_hyp_4.py` | func=compute_m51_hyp_4 | params=h_conv,A | hash=984436f71850
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m51_hyp_4.py` | func=compute_m51_hyp_4 | params=h_conv,A | hash=984436f71850
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m51_hyp_4.py` | func=compute_m51_hyp_4 | params=h_conv,A | hash=984436f71850
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m51_hyp_4.py` | func=compute_m51_hyp_4 | params=h_conv,A | hash=984436f71850
  Evidence: nan

## m52_hyp_5
- Sources count: 4
- Status: identical
- Code hashes: faf00d0e5f12
- Params (union): g_phase_norm
- Compendium formula: hyp_5 = g_phase_norm (extern berechnet) wobei typischerweise: g_phase = arctan2(nabla_A, nabla_B) g_phase_norm = g_phase / π
- Compendium upstream: g_phase_norm
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Condenses multiple signals into an interpretable composite; Supports dynamical modeling and adaptive behavior
- Cons: Can obscure individual signal sources and reduce diagnosability; Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m52_hyp_5.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m52_hyp_5.py` | func=compute_m52_hyp_5 | params=g_phase_norm | hash=faf00d0e5f12
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m52_hyp_5.py` | func=compute_m52_hyp_5 | params=g_phase_norm | hash=faf00d0e5f12
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m52_hyp_5.py` | func=compute_m52_hyp_5 | params=g_phase_norm | hash=faf00d0e5f12
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m52_hyp_5.py` | func=compute_m52_hyp_5 | params=g_phase_norm | hash=faf00d0e5f12
  Evidence: nan

## m53_hyp_6
- Sources count: 4
- Status: identical
- Code hashes: 6e2d9fce8536
- Params (union): gap_seconds
- Compendium formula: hyp_6 = gap_s / 3600.0
- Compendium upstream: gap_s
- Missing in compendium upstream: gap_seconds
- Missing in compendium formula: gap_seconds
- Downstream usage: nan
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m53_hyp_6.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m53_hyp_6.py` | func=compute_m53_hyp_6 | params=gap_seconds | hash=6e2d9fce8536
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m53_hyp_6.py` | func=compute_m53_hyp_6 | params=gap_seconds | hash=6e2d9fce8536
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m53_hyp_6.py` | func=compute_m53_hyp_6 | params=gap_seconds | hash=6e2d9fce8536
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m53_hyp_6.py` | func=compute_m53_hyp_6 | params=gap_seconds | hash=6e2d9fce8536
  Evidence: nan

## m54_hyp_7
- Sources count: 4
- Status: identical
- Code hashes: 5addfcedf4a8
- Params (union): rapport,trust_score
- Compendium formula: hyp_7 = trust_score × rapport
- Compendium upstream: trust_score, rapport
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m54_hyp_7.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m54_hyp_7.py` | func=compute_m54_hyp_7 | params=trust_score,rapport | hash=5addfcedf4a8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m54_hyp_7.py` | func=compute_m54_hyp_7 | params=trust_score,rapport | hash=5addfcedf4a8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m54_hyp_7.py` | func=compute_m54_hyp_7 | params=trust_score,rapport | hash=5addfcedf4a8
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m54_hyp_7.py` | func=compute_m54_hyp_7 | params=trust_score,rapport | hash=5addfcedf4a8
  Evidence: nan

## m55_hyp_8
- Sources count: 4
- Status: identical
- Code hashes: 8f3b7c1159cc
- Params (union): PCI,soul_integrity
- Compendium formula: hyp_8 = soul_integrity × PCI
- Compendium upstream: soul_integrity, PCI
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Condenses multiple signals into an interpretable composite
- Cons: Can obscure individual signal sources and reduce diagnosability
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m55_hyp_8.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m55_hyp_8.py` | func=compute_m55_hyp_8 | params=soul_integrity,PCI | hash=8f3b7c1159cc
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m55_hyp_8.py` | func=compute_m55_hyp_8 | params=soul_integrity,PCI | hash=8f3b7c1159cc
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m55_hyp_8.py` | func=compute_m55_hyp_8 | params=soul_integrity,PCI | hash=8f3b7c1159cc
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m55_hyp_8.py` | func=compute_m55_hyp_8 | params=soul_integrity,PCI | hash=8f3b7c1159cc
  Evidence: nan

## m56_surprise
- Sources count: 4
- Status: identical
- Code hashes: 7da6d9730433
- Params (union): A_current,A_predicted
- Compendium formula: surprise = |A_current - A_predicted|
- Compendium upstream: A_current, A_predicted
- Missing in compendium upstream: nan
- Missing in compendium formula: nan
- Downstream usage: nan
- Pros: Foundational metric used by many downstream computations; Supports dynamical modeling and adaptive behavior
- Cons: Errors propagate widely across system; Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m56_surprise.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m56_surprise.py` | func=compute_m56_surprise | params=A_current,A_predicted | hash=7da6d9730433
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m56_surprise.py` | func=compute_m56_surprise | params=A_current,A_predicted | hash=7da6d9730433
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m56_surprise.py` | func=compute_m56_surprise | params=A_current,A_predicted | hash=7da6d9730433
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m56_surprise.py` | func=compute_m56_surprise | params=A_current,A_predicted | hash=7da6d9730433
  Evidence: nan

## m57_tokens_soc
- Sources count: 5
- Status: diff
- Code hashes: 6f5f3d661652;fe5dd6e23f85
- Params (union): current,delta,rapport,sent_7
- Compendium formula: nan
- Compendium upstream: prev_tokens, delta
- Missing in compendium upstream: current,rapport,sent_7
- Missing in compendium formula: current,delta,rapport,sent_7
- Downstream usage: nan
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m57_tokens_soc.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m57_tokens_soc.py` | func=compute_m57_tokens_soc | params=current,delta | hash=fe5dd6e23f85
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m57_tokens_soc.py` | func=compute_m57_tokens_soc | params=sent_7,rapport | hash=6f5f3d661652
  Evidence: Hohe soziale Tokens = System kann empathisch, beziehungsorientiert agieren. | tokens_soc = 0.6·sent_7 + 0.4·rapport | - m59_drive_balance = tokens_soc / (tokens_soc + tokens_log)
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m57_tokens_soc.py` | func=compute_m57_tokens_soc | params=current,delta | hash=fe5dd6e23f85
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m57_tokens_soc.py` | func=compute_m57_tokens_soc | params=current,delta | hash=fe5dd6e23f85
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m57_tokens_soc.py` | func=compute_m57_tokens_soc | params=sent_7,rapport | hash=6f5f3d661652
  Evidence: Hohe soziale Tokens = System kann empathisch, beziehungsorientiert agieren. | tokens_soc = 0.6·sent_7 + 0.4·rapport | - m59_drive_balance = tokens_soc / (tokens_soc + tokens_log)

## m58_tokens_log
- Sources count: 5
- Status: diff
- Code hashes: 14dc64494113;d18271c07303
- Params (union): PCI,coh,current,delta
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: PCI,coh,current,delta
- Missing in compendium formula: PCI,coh,current,delta
- Downstream usage: nan
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m58_tokens_log.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m58_tokens_log.py` | func=compute_m58_tokens_log | params=current,delta | hash=d18271c07303
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m58_tokens_log.py` | func=compute_m58_tokens_log | params=PCI,coh | hash=14dc64494113
  Evidence: Hohe logische Tokens = System kann analytisch, strukturiert agieren. | tokens_log = mean(PCI, coh) = (PCI + coh) / 2
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m58_tokens_log.py` | func=compute_m58_tokens_log | params=current,delta | hash=d18271c07303
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m58_tokens_log.py` | func=compute_m58_tokens_log | params=current,delta | hash=d18271c07303
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m58_tokens_log.py` | func=compute_m58_tokens_log | params=PCI,coh | hash=14dc64494113
  Evidence: Hohe logische Tokens = System kann analytisch, strukturiert agieren. | tokens_log = mean(PCI, coh) = (PCI + coh) / 2

## m59_drive_balance
- Sources count: 2
- Status: identical
- Code hashes: 15950b3a9409
- Params (union): epsilon,tokens_log,tokens_soc
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: epsilon,tokens_log,tokens_soc
- Missing in compendium formula: epsilon,tokens_log,tokens_soc
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m59_drive_balance.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m59_drive_balance.py` | func=compute_m59_drive_balance | params=tokens_soc,tokens_log,epsilon | hash=15950b3a9409
  Evidence: drive_balance = tokens_soc / (tokens_soc + tokens_log + ε)
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m59_drive_balance.py` | func=compute_m59_drive_balance | params=tokens_soc,tokens_log,epsilon | hash=15950b3a9409
  Evidence: drive_balance = tokens_soc / (tokens_soc + tokens_log + ε)

## m59_p_antrieb
- Sources count: 4
- Status: identical
- Code hashes: 1ce223a6f02a
- Params (union): stagnation,tokens_log,tokens_soc
- Compendium formula: p_antrieb = (tokens_soc + tokens_log) / 200.0  (wenn stagniert)
- Compendium upstream: tokens_soc, tokens_log, is_stagnated
- Missing in compendium upstream: stagnation
- Missing in compendium formula: stagnation
- Downstream usage: nan
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m59_p_antrieb.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m59_p_antrieb.py` | func=compute_m59_p_antrieb | params=tokens_soc,tokens_log,stagnation | hash=1ce223a6f02a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m59_p_antrieb.py` | func=compute_m59_p_antrieb | params=tokens_soc,tokens_log,stagnation | hash=1ce223a6f02a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m59_p_antrieb.py` | func=compute_m59_p_antrieb | params=tokens_soc,tokens_log,stagnation | hash=1ce223a6f02a
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m59_p_antrieb.py` | func=compute_m59_p_antrieb | params=tokens_soc,tokens_log,stagnation | hash=1ce223a6f02a
  Evidence: nan

## m5_coh
- Sources count: 8
- Status: diff
- Code hashes: 92027399836c;e01c52f209a9
- Params (union): text
- Compendium formula: coh = (1/N) × Σ jaccard(sent_i, sent_i+1) wobei: jaccard(A, B) = |A ∩ B| / |A ∪ B| N = Anzahl Satz-Paare
- Compendium upstream: text
- Missing in compendium upstream: nan
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: Foundational metric used by many downstream computations
- Cons: Errors propagate widely across system; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m5_coh.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m5_coh.py` | func=compute_m5_coh | params=text | hash=e01c52f209a9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m5_coh.py` | func=compute_m5_coh | params=text | hash=92027399836c
  Evidence: Coherence score [0, 1] - Higher = more coherent
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m5_coh.py` | func=compute_m5_coh | params=text | hash=e01c52f209a9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m5_coh.py` | func=compute_m5_coh | params=text | hash=92027399836c
  Evidence: Coherence score [0, 1] - Higher = more coherent
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m5_coh.py` | func=compute_m5_coh | params=text | hash=92027399836c
  Evidence: Coherence score [0, 1] - Higher = more coherent
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m5_coh.py` | func=compute_m5_coh | params=text | hash=92027399836c
  Evidence: Coherence score [0, 1] - Higher = more coherent
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m5_coh.py` | func=compute_m5_coh | params=text | hash=e01c52f209a9
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m5_coh.py` | func=compute_m5_coh | params=text | hash=92027399836c
  Evidence: Coherence score [0, 1] - Higher = more coherent

## m60_action_urge
- Sources count: 2
- Status: identical
- Code hashes: 2746f44194d9
- Params (union): phi,surprise
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: phi,surprise
- Missing in compendium formula: phi,surprise
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m60_action_urge.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m60_action_urge.py` | func=compute_m60_action_urge | params=surprise,phi | hash=2746f44194d9
  Evidence: action_urge = 0.5·surprise + 0.5·max(0, phi) | - Phi positiv = verfärkt Action (exploitativ)
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m60_action_urge.py` | func=compute_m60_action_urge | params=surprise,phi | hash=2746f44194d9
  Evidence: action_urge = 0.5·surprise + 0.5·max(0, phi) | - Phi positiv = verfärkt Action (exploitativ)

## m60_delta_tokens
- Sources count: 4
- Status: identical
- Code hashes: de2ed711a73c
- Params (union): tok_new,tok_old
- Compendium formula: delta_tokens = (η × benefit × A) - λ_decay wobei: benefit = max(0, prev_surprise - curr_surprise) η = 5.0 (Lernrate) λ = 0.05 (Zerfall)
- Compendium upstream: nan
- Missing in compendium upstream: tok_new,tok_old
- Missing in compendium formula: tok_new,tok_old
- Downstream usage: nan
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m60_delta_tokens.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m60_delta_tokens.py` | func=compute_m60_delta_tokens | params=tok_new,tok_old | hash=de2ed711a73c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m60_delta_tokens.py` | func=compute_m60_delta_tokens | params=tok_new,tok_old | hash=de2ed711a73c
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m60_delta_tokens.py` | func=compute_m60_delta_tokens | params=tok_new,tok_old | hash=de2ed711a73c
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m60_delta_tokens.py` | func=compute_m60_delta_tokens | params=tok_new,tok_old | hash=de2ed711a73c
  Evidence: nan

## m61_U
- Sources count: 3
- Status: identical
- Code hashes: b43499a79d3a
- Params (union): PCI,s_entropy
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: PCI,s_entropy
- Missing in compendium formula: PCI,s_entropy
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m61_U.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m61_U.py` | func=compute_m61_U | params=PCI,s_entropy | hash=b43499a79d3a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m61_U.py` | func=compute_m61_U | params=PCI,s_entropy | hash=b43499a79d3a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m61_U.py` | func=compute_m61_U | params=PCI,s_entropy | hash=b43499a79d3a
  Evidence: nan

## m61_u
- Sources count: 2
- Status: diff
- Code hashes: 46dcad08a7d0;b43499a79d3a
- Params (union): A,PCI,T_integ,s_entropy
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: A,PCI,T_integ,s_entropy
- Missing in compendium formula: A,PCI,T_integ,s_entropy
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m61_u.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m61_u.py` | func=compute_m61_u | params=A,PCI,T_integ | hash=46dcad08a7d0
  Evidence: U = 0.4·A + 0.3·PCI + 0.3·T_integ | - Hoher U = System sucht neue Informationen
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m61_u.py` | func=compute_m61_U | params=PCI,s_entropy | hash=b43499a79d3a
  Evidence: nan

## m62_R
- Sources count: 3
- Status: identical
- Code hashes: 736b80e973fd
- Params (union): A,m61_U
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: A,m61_U
- Missing in compendium formula: A,m61_U
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m62_R.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m62_R.py` | func=compute_m62_R | params=A,m61_U | hash=736b80e973fd
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m62_R.py` | func=compute_m62_R | params=A,m61_U | hash=736b80e973fd
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m62_R.py` | func=compute_m62_R | params=A,m61_U | hash=736b80e973fd
  Evidence: nan

## m62_r
- Sources count: 2
- Status: diff
- Code hashes: 5f03fa79cd66;736b80e973fd
- Params (union): A,PCI,T_panic,m61_U,z_prox
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: A,PCI,T_panic,m61_U,z_prox
- Missing in compendium formula: A,PCI,T_panic,m61_U,z_prox
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m62_r.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m62_r.py` | func=compute_m62_r | params=z_prox,PCI,T_panic | hash=5f03fa79cd66
  Evidence: R = 0.4·z_prox + 0.3·(1-PCI) + 0.3·T_panic | - Hoher R = System muss vorsichtig sein
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m62_r.py` | func=compute_m62_R | params=A,m61_U | hash=736b80e973fd
  Evidence: nan

## m63_phi
- Sources count: 4
- Status: identical
- Code hashes: 10e6261296fe
- Params (union): PCI,R
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: PCI,R
- Missing in compendium formula: PCI,R
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m63_phi.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m63_phi.py` | func=compute_m63_phi | params=PCI,R | hash=10e6261296fe
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m63_phi.py` | func=compute_m63_phi | params=PCI,R | hash=10e6261296fe
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m63_phi.py` | func=compute_m63_phi | params=PCI,R | hash=10e6261296fe
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m63_phi.py` | func=compute_m63_phi | params=PCI,R | hash=10e6261296fe
  Evidence: nan

## m63_phi_score
- Sources count: 2
- Status: identical
- Code hashes: 4ada52968e25
- Params (union): R,U,lambda_weight
- Compendium formula: Phi = U - R
- Compendium upstream: U, R
- Missing in compendium upstream: lambda_weight
- Missing in compendium formula: lambda_weight
- Downstream usage: nan
- Pros: Foundational metric used by many downstream computations; Supports dynamical modeling and adaptive behavior
- Cons: Errors propagate widely across system; Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m63_phi_score.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m63_phi_score.py` | func=compute_m63_phi_score | params=U,R,lambda_weight | hash=4ada52968e25
  Evidence: Phi = U - λ·R | wobei λ (Lambda) = Risiko-Gewichtung (default 1.0) | - Phi = "Expected Free Energy"
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m63_phi_score.py` | func=compute_m63_phi_score | params=U,R,lambda_weight | hash=4ada52968e25
  Evidence: Phi = U - λ·R | wobei λ (Lambda) = Risiko-Gewichtung (default 1.0) | - Phi = "Expected Free Energy"

## m64_free_energy
- Sources count: 2
- Status: identical
- Code hashes: 073bf2ce4bcb
- Params (union): R,U
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: R,U
- Missing in compendium formula: R,U
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m64_free_energy.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m64_free_energy.py` | func=compute_m64_free_energy | params=U,R | hash=073bf2ce4bcb
  Evidence: Hohe freie Energie = System ist im Ungleichgewicht, muss handeln. | Free_Energy = |U - (1 - R)| | - FE = Surprise + Divergence
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m64_free_energy.py` | func=compute_m64_free_energy | params=U,R | hash=073bf2ce4bcb
  Evidence: Hohe freie Energie = System ist im Ungleichgewicht, muss handeln. | Free_Energy = |U - (1 - R)| | - FE = Surprise + Divergence

## m64_lambda_fep
- Sources count: 4
- Status: identical
- Code hashes: 39d826faf01a
- Params (union): action_space,s_entropy
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: action_space,s_entropy
- Missing in compendium formula: action_space,s_entropy
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m64_lambda_fep.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m64_lambda_fep.py` | func=compute_m64_lambda_fep | params=s_entropy,action_space | hash=39d826faf01a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m64_lambda_fep.py` | func=compute_m64_lambda_fep | params=s_entropy,action_space | hash=39d826faf01a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m64_lambda_fep.py` | func=compute_m64_lambda_fep | params=s_entropy,action_space | hash=39d826faf01a
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m64_lambda_fep.py` | func=compute_m64_lambda_fep | params=s_entropy,action_space | hash=39d826faf01a
  Evidence: nan

## m65_alpha
- Sources count: 4
- Status: identical
- Code hashes: 46bb0556cd90
- Params (union): learning_rate
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: learning_rate
- Missing in compendium formula: learning_rate
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m65_alpha.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m65_alpha.py` | func=compute_m65_alpha | params=learning_rate | hash=46bb0556cd90
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m65_alpha.py` | func=compute_m65_alpha | params=learning_rate | hash=46bb0556cd90
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m65_alpha.py` | func=compute_m65_alpha | params=learning_rate | hash=46bb0556cd90
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m65_alpha.py` | func=compute_m65_alpha | params=learning_rate | hash=46bb0556cd90
  Evidence: nan

## m65_policy_entropy
- Sources count: 2
- Status: identical
- Code hashes: 8a4be5bcba56
- Params (union): U,surprise
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: U,surprise
- Missing in compendium formula: U,surprise
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m65_policy_entropy.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m65_policy_entropy.py` | func=compute_m65_policy_entropy | params=U,surprise | hash=8a4be5bcba56
  Evidence: Hohe Entropie = viele gleichwertige Optionen (Unsicherheit). | Niedrige Entropie = klare beste Option (Klarheit). | Policy_Entropy = 0.5·U + 0.5·surprise
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m65_policy_entropy.py` | func=compute_m65_policy_entropy | params=U,surprise | hash=8a4be5bcba56
  Evidence: Hohe Entropie = viele gleichwertige Optionen (Unsicherheit). | Niedrige Entropie = klare beste Option (Klarheit). | Policy_Entropy = 0.5·U + 0.5·surprise

## m66_gamma
- Sources count: 4
- Status: identical
- Code hashes: f8b4c9a42f6b
- Params (union): discount_factor
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: discount_factor
- Missing in compendium formula: discount_factor
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m66_gamma.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m66_gamma.py` | func=compute_m66_gamma | params=discount_factor | hash=f8b4c9a42f6b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m66_gamma.py` | func=compute_m66_gamma | params=discount_factor | hash=f8b4c9a42f6b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m66_gamma.py` | func=compute_m66_gamma | params=discount_factor | hash=f8b4c9a42f6b
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m66_gamma.py` | func=compute_m66_gamma | params=discount_factor | hash=f8b4c9a42f6b
  Evidence: nan

## m67_precision
- Sources count: 4
- Status: identical
- Code hashes: 173b1e55ae16
- Params (union): variance
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: variance
- Missing in compendium formula: variance
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m67_precision.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m67_precision.py` | func=compute_m67_precision | params=variance | hash=173b1e55ae16
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m67_precision.py` | func=compute_m67_precision | params=variance | hash=173b1e55ae16
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m67_precision.py` | func=compute_m67_precision | params=variance | hash=173b1e55ae16
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m67_precision.py` | func=compute_m67_precision | params=variance | hash=173b1e55ae16
  Evidence: nan

## m68_prediction_err
- Sources count: 4
- Status: identical
- Code hashes: 2b3f1aae1283
- Params (union): actual,expected
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: actual,expected
- Missing in compendium formula: actual,expected
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m68_prediction_err.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m68_prediction_err.py` | func=compute_m68_prediction_err | params=expected,actual | hash=2b3f1aae1283
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m68_prediction_err.py` | func=compute_m68_prediction_err | params=expected,actual | hash=2b3f1aae1283
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m68_prediction_err.py` | func=compute_m68_prediction_err | params=expected,actual | hash=2b3f1aae1283
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m68_prediction_err.py` | func=compute_m68_prediction_err | params=expected,actual | hash=2b3f1aae1283
  Evidence: nan

## m68_rpe
- Sources count: 2
- Status: identical
- Code hashes: ec3bb280fa56
- Params (union): affekt_current,affekt_prev
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: affekt_current,affekt_prev
- Missing in compendium formula: affekt_current,affekt_prev
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m68_rpe.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m68_rpe.py` | func=compute_m68_rpe | params=affekt_current,affekt_prev | hash=ec3bb280fa56
  Evidence: RPE = A_current - A_previous | - RPE = δ (Delta) in TD-Learning
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m68_rpe.py` | func=compute_m68_rpe | params=affekt_current,affekt_prev | hash=ec3bb280fa56
  Evidence: RPE = A_current - A_previous | - RPE = δ (Delta) in TD-Learning

## m69_exploration
- Sources count: 2
- Status: identical
- Code hashes: c541b937a624
- Params (union): U,gen_index
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: U,gen_index
- Missing in compendium formula: U,gen_index
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m69_exploration.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m69_exploration.py` | func=compute_m69_exploration | params=U,gen_index | hash=c541b937a624
  Evidence: Exploration = 0.6·U + 0.4·gen_index
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m69_exploration.py` | func=compute_m69_exploration | params=U,gen_index | hash=c541b937a624
  Evidence: Exploration = 0.6·U + 0.4·gen_index

## m69_model_evidence
- Sources count: 4
- Status: identical
- Code hashes: ddbccd6b6795
- Params (union): log_likelihood
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: log_likelihood
- Missing in compendium formula: log_likelihood
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m69_model_evidence.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m69_model_evidence.py` | func=compute_m69_model_evidence | params=log_likelihood | hash=ddbccd6b6795
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m69_model_evidence.py` | func=compute_m69_model_evidence | params=log_likelihood | hash=ddbccd6b6795
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m69_model_evidence.py` | func=compute_m69_model_evidence | params=log_likelihood | hash=ddbccd6b6795
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m69_model_evidence.py` | func=compute_m69_model_evidence | params=log_likelihood | hash=ddbccd6b6795
  Evidence: nan

## m6_ZLF
- Sources count: 8
- Status: diff
- Code hashes: 22af2cd37d5e;51c7ac031c95
- Params (union): coherence,flow,zlf_lexicon_hit
- Compendium formula: ZLF = clip( 0.5 × (1 - flow) + 0.5 × (1 - coherence) ) wobei: flow = m4_flow (Flow State - exponentieller Zeitverzerrungsfaktor) coherence = m5_coh (Kohärenz - Jaccard-Ähnlichkeit mit History) clip = Normalisierung auf [0, 1]
- Compendium upstream: nan
- Missing in compendium upstream: coherence,flow,zlf_lexicon_hit
- Missing in compendium formula: zlf_lexicon_hit
- Downstream usage: **Loop Detection:** ZLF > 0.7 triggert Loop-Warning; **Auto-Reset:** Bei ZLF > 0.85 über 3+ Turns → Context-Reset; **Guardian:** Hoher ZLF kombiniert mit hohem z_prox aktiviert Notfallprotokoll; **Visualisierung:** Zeigt "Gefahr der Wiederholung" im Temple Tab
- Pros: Safety-critical signal for risk/guardian decisions; Foundational metric used by many downstream computations
- Cons: High false-positive cost if thresholds/lexicon are wrong; Errors propagate widely across system
- Impact: Downstream impact if inconsistent: **Loop Detection:** ZLF > 0.7 triggert Loop-Warning; **Auto-Reset:** Bei ZLF > 0.85 über 3+ Turns → Context-Reset; **Guardian:** Hoher ZLF kombiniert mit hohem z_prox aktiviert Notfallprotokoll; **Visualisierung:** Zeigt "Gefahr der Wiederholung" im Temple Tab
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m6_ZLF.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m6_ZLF.py` | func=compute_m6_ZLF | params=flow,coherence,zlf_lexicon_hit | hash=51c7ac031c95
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m6_ZLF.py` | func=compute_m6_ZLF | params=flow,coherence,zlf_lexicon_hit | hash=22af2cd37d5e
  Evidence: ZLF = clip01(0.5·lexicon_hit + 0.25·(1-flow) + 0.25·(1-coh)) | Higher ZLF = more looping/stuck patterns.
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m6_ZLF.py` | func=compute_m6_ZLF | params=flow,coherence,zlf_lexicon_hit | hash=51c7ac031c95
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m6_ZLF.py` | func=compute_m6_ZLF | params=flow,coherence,zlf_lexicon_hit | hash=22af2cd37d5e
  Evidence: ZLF = clip01(0.5·lexicon_hit + 0.25·(1-flow) + 0.25·(1-coh)) | Higher ZLF = more looping/stuck patterns.
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m6_ZLF.py` | func=compute_m6_ZLF | params=flow,coherence,zlf_lexicon_hit | hash=22af2cd37d5e
  Evidence: ZLF = clip01(0.5·lexicon_hit + 0.25·(1-flow) + 0.25·(1-coh)) | Higher ZLF = more looping/stuck patterns.
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m6_ZLF.py` | func=compute_m6_ZLF | params=flow,coherence,zlf_lexicon_hit | hash=22af2cd37d5e
  Evidence: ZLF = clip01(0.5·lexicon_hit + 0.25·(1-flow) + 0.25·(1-coh)) | Higher ZLF = more looping/stuck patterns.
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m6_ZLF.py` | func=compute_m6_ZLF | params=flow,coherence,zlf_lexicon_hit | hash=51c7ac031c95
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m6_ZLF.py` | func=compute_m6_ZLF | params=flow,coherence,zlf_lexicon_hit | hash=22af2cd37d5e
  Evidence: ZLF = clip01(0.5·lexicon_hit + 0.25·(1-flow) + 0.25·(1-coh)) | Higher ZLF = more looping/stuck patterns.

## m70_active_inf
- Sources count: 4
- Status: identical
- Code hashes: 7add2b8d0328
- Params (union): action_space,precision
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: action_space,precision
- Missing in compendium formula: action_space,precision
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m70_active_inf.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m70_active_inf.py` | func=compute_m70_active_inf | params=action_space,precision | hash=7add2b8d0328
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m70_active_inf.py` | func=compute_m70_active_inf | params=action_space,precision | hash=7add2b8d0328
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m70_active_inf.py` | func=compute_m70_active_inf | params=action_space,precision | hash=7add2b8d0328
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m70_active_inf.py` | func=compute_m70_active_inf | params=action_space,precision | hash=7add2b8d0328
  Evidence: nan

## m70_exploitation
- Sources count: 2
- Status: identical
- Code hashes: 80869e6313eb
- Params (union): ctx_fit,tokens_log
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: ctx_fit,tokens_log
- Missing in compendium formula: ctx_fit,tokens_log
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m70_exploitation.py`
- Best source reason: Legacy library: kept for backward compatibility
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m70_exploitation.py` | func=compute_m70_exploitation | params=tokens_log,ctx_fit | hash=80869e6313eb
  Evidence: Exploitation = 0.6·tokens_log + 0.4·ctx_fit | - High exploitation + Low exploration = Conservative behavior | - Low exploitation + High exploration = Risky/Creative behavior
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m70_exploitation.py` | func=compute_m70_exploitation | params=tokens_log,ctx_fit | hash=80869e6313eb
  Evidence: Exploitation = 0.6·tokens_log + 0.4·ctx_fit | - High exploitation + Low exploration = Conservative behavior | - Low exploitation + High exploration = Risky/Creative behavior

## m71_ev_arousal
- Sources count: 5
- Status: diff
- Code hashes: 7a72e3abb079;bf5b16034499
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m71_ev_arousal.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m71_ev_arousal.py` | func=compute_m71_ev_arousal | params=text | hash=7a72e3abb079
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m71_ev_arousal.py` | func=compute_m71_ev_arousal | params=text | hash=bf5b16034499
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m71_ev_arousal.py` | func=compute_m71_ev_arousal | params=text | hash=7a72e3abb079
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m71_ev_arousal.py` | func=compute_m71_ev_arousal | params=text | hash=7a72e3abb079
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m71_ev_arousal.py` | func=compute_m71_ev_arousal | params=text | hash=bf5b16034499
  Evidence: nan

## m72_ev_valence
- Sources count: 5
- Status: diff
- Code hashes: b574e3912243;dc93460c8922
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m72_ev_valence.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m72_ev_valence.py` | func=compute_m72_ev_valence | params=text | hash=dc93460c8922
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m72_ev_valence.py` | func=compute_m72_ev_valence | params=text | hash=b574e3912243
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m72_ev_valence.py` | func=compute_m72_ev_valence | params=text | hash=dc93460c8922
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m72_ev_valence.py` | func=compute_m72_ev_valence | params=text | hash=dc93460c8922
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m72_ev_valence.py` | func=compute_m72_ev_valence | params=text | hash=b574e3912243
  Evidence: nan

## m73_ev_readiness
- Sources count: 5
- Status: diff
- Code hashes: 5c495493ea77;c83c54bcac86
- Params (union): A,t_integ
- Compendium formula: Readiness = min(1.0, Resonance × trust_score)
- Compendium upstream: resonance, trust_score
- Missing in compendium upstream: A,t_integ
- Missing in compendium formula: A,t_integ
- Downstream usage: nan
- Pros: Signal contribution not explicitly stated; inferred from description
- Cons: Limited explicit downsides; main risk is miscalibration
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m73_ev_readiness.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m73_ev_readiness.py` | func=compute_m73_ev_readiness | params=t_integ,A | hash=5c495493ea77
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m73_ev_readiness.py` | func=compute_m73_ev_readiness | params=t_integ,A | hash=c83c54bcac86
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m73_ev_readiness.py` | func=compute_m73_ev_readiness | params=t_integ,A | hash=5c495493ea77
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m73_ev_readiness.py` | func=compute_m73_ev_readiness | params=t_integ,A | hash=5c495493ea77
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m73_ev_readiness.py` | func=compute_m73_ev_readiness | params=t_integ,A | hash=c83c54bcac86
  Evidence: nan

## m74_valence
- Sources count: 5
- Status: diff
- Code hashes: 923ff9e50c20;e6e03c5ad822
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m74_valence.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m74_valence.py` | func=compute_m74_valence | params=text | hash=e6e03c5ad822
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m74_valence.py` | func=compute_m74_valence | params=text | hash=923ff9e50c20
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m74_valence.py` | func=compute_m74_valence | params=text | hash=e6e03c5ad822
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m74_valence.py` | func=compute_m74_valence | params=text | hash=e6e03c5ad822
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m74_valence.py` | func=compute_m74_valence | params=text | hash=923ff9e50c20
  Evidence: nan

## m75_arousal
- Sources count: 5
- Status: diff
- Code hashes: 3bdf56b2836f;bc2d17e6e366
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m75_arousal.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m75_arousal.py` | func=compute_m75_arousal | params=text | hash=3bdf56b2836f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m75_arousal.py` | func=compute_m75_arousal | params=text | hash=bc2d17e6e366
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m75_arousal.py` | func=compute_m75_arousal | params=text | hash=3bdf56b2836f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m75_arousal.py` | func=compute_m75_arousal | params=text | hash=3bdf56b2836f
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m75_arousal.py` | func=compute_m75_arousal | params=text | hash=bc2d17e6e366
  Evidence: nan

## m76_dominance
- Sources count: 5
- Status: diff
- Code hashes: 2a68ee7fe343;f6dbb7ef6b2e
- Params (union): text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: text
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m76_dominance.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m76_dominance.py` | func=compute_m76_dominance | params=text | hash=f6dbb7ef6b2e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m76_dominance.py` | func=compute_m76_dominance | params=text | hash=2a68ee7fe343
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m76_dominance.py` | func=compute_m76_dominance | params=text | hash=f6dbb7ef6b2e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m76_dominance.py` | func=compute_m76_dominance | params=text | hash=f6dbb7ef6b2e
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m76_dominance.py` | func=compute_m76_dominance | params=text | hash=2a68ee7fe343
  Evidence: nan

## m77_joy
- Sources count: 5
- Status: diff
- Code hashes: 1caeb73c2594;2122879397da
- Params (union): arousal,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal,valence
- Missing in compendium formula: arousal,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m77_joy.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m77_joy.py` | func=compute_m77_joy | params=valence,arousal | hash=2122879397da
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m77_joy.py` | func=compute_m77_joy | params=valence,arousal | hash=1caeb73c2594
  Evidence: High valence + high arousal = joy.
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m77_joy.py` | func=compute_m77_joy | params=valence,arousal | hash=2122879397da
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m77_joy.py` | func=compute_m77_joy | params=valence,arousal | hash=2122879397da
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m77_joy.py` | func=compute_m77_joy | params=valence,arousal | hash=1caeb73c2594
  Evidence: High valence + high arousal = joy.

## m78_sadness
- Sources count: 5
- Status: diff
- Code hashes: 89fb6aa52a5a;c1538c6e7adc
- Params (union): arousal,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal,valence
- Missing in compendium formula: arousal,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m78_sadness.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m78_sadness.py` | func=compute_m78_sadness | params=valence,arousal | hash=89fb6aa52a5a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m78_sadness.py` | func=compute_m78_sadness | params=valence,arousal | hash=c1538c6e7adc
  Evidence: Low valence + low arousal = sadness.
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m78_sadness.py` | func=compute_m78_sadness | params=valence,arousal | hash=89fb6aa52a5a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m78_sadness.py` | func=compute_m78_sadness | params=valence,arousal | hash=89fb6aa52a5a
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m78_sadness.py` | func=compute_m78_sadness | params=valence,arousal | hash=c1538c6e7adc
  Evidence: Low valence + low arousal = sadness.

## m79_anger
- Sources count: 5
- Status: diff
- Code hashes: 9b289d248322;b0b3bf3d30a5
- Params (union): arousal,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal,valence
- Missing in compendium formula: arousal,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m79_anger.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m79_anger.py` | func=compute_m79_anger | params=valence,arousal | hash=b0b3bf3d30a5
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m79_anger.py` | func=compute_m79_anger | params=valence,arousal | hash=9b289d248322
  Evidence: Low valence + high arousal = anger.
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m79_anger.py` | func=compute_m79_anger | params=valence,arousal | hash=b0b3bf3d30a5
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m79_anger.py` | func=compute_m79_anger | params=valence,arousal | hash=b0b3bf3d30a5
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m79_anger.py` | func=compute_m79_anger | params=valence,arousal | hash=9b289d248322
  Evidence: Low valence + high arousal = anger.

## m7_LL
- Sources count: 8
- Status: diff
- Code hashes: 4f871584ab9b;72fd66c2a1ff;7f25ee360555
- Params (union): coh,flow,rep_same
- Compendium formula: LL = clip(0.55*rep_same + 0.25*(1-flow) + 0.20*(1-coh))
- Compendium upstream: nan
- Missing in compendium upstream: coh,flow,rep_same
- Missing in compendium formula: nan
- Downstream usage: **A-Score Dämpfung:** Hoher LL reduziert m15_affekt_a direkt; **z_prox Berechnung:** LL ist ein Hauptfaktor für Todesnähe; **Turbidity Chain:** Fließt in m107-m110 (Turbidity Family); **System Health:** LL > 0.7 deutet auf kognitive Überlastung hin
- Pros: Supports dynamical modeling and adaptive behavior
- Cons: Higher implementation complexity and state management
- Impact: Downstream impact if inconsistent: **A-Score Dämpfung:** Hoher LL reduziert m15_affekt_a direkt; **z_prox Berechnung:** LL ist ein Hauptfaktor für Todesnähe; **Turbidity Chain:** Fließt in m107-m110 (Turbidity Family); **System Health:** LL > 0.7 deutet auf kognitive Überlastung hin
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m7_LL.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m7_LL.py` | func=compute_m7_LL | params=rep_same,flow | hash=4f871584ab9b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m7_LL.py` | func=compute_m7_LL | params=rep_same,flow | hash=7f25ee360555
  Evidence: SPEC Formula: LL = clip(0.6 × rep_same + 0.4 × (1 - flow))
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m7_LL.py` | func=compute_m7_LL | params=rep_same,flow | hash=4f871584ab9b
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m7_LL.py` | func=compute_m7_LL | params=rep_same,flow | hash=7f25ee360555
  Evidence: SPEC Formula: LL = clip(0.6 × rep_same + 0.4 × (1 - flow))
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m7_LL.py` | func=compute_m7_LL | params=rep_same,flow | hash=7f25ee360555
  Evidence: SPEC Formula: LL = clip(0.6 × rep_same + 0.4 × (1 - flow))
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m7_LL.py` | func=compute_m7_LL | params=rep_same,flow | hash=7f25ee360555
  Evidence: SPEC Formula: LL = clip(0.6 × rep_same + 0.4 × (1 - flow))
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m7_LL.py` | func=compute_m7_LL | params=rep_same,flow | hash=4f871584ab9b
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m7_LL.py` | func=compute_m7_LL | params=rep_same,flow,coh | hash=72fd66c2a1ff
  Evidence: LL = 0.55·rep_same + 0.25·(1-flow) + 0.20·(1-coh) | LL score [0, 1] - Turbidity/Logic Loss (higher = more turbid) | >>> compute_m7_LL(rep_same=0.5, flow=0.8, coh=0.7)

## m80_fear
- Sources count: 5
- Status: diff
- Code hashes: 1d7e067f1083;d89c793e4e76
- Params (union): arousal,dominance,t_panic,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal,dominance,t_panic,valence
- Missing in compendium formula: arousal,dominance,t_panic,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m80_fear.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m80_fear.py` | func=compute_m80_fear | params=valence,arousal,dominance,t_panic | hash=1d7e067f1083
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m80_fear.py` | func=compute_m80_fear | params=valence,arousal,dominance,t_panic | hash=d89c793e4e76
  Evidence: Low valence + high arousal + low dominance = fear. | where fear_base = (3 - valence + arousal - dominance) / 3
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m80_fear.py` | func=compute_m80_fear | params=valence,arousal,dominance,t_panic | hash=1d7e067f1083
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m80_fear.py` | func=compute_m80_fear | params=valence,arousal,dominance,t_panic | hash=1d7e067f1083
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m80_fear.py` | func=compute_m80_fear | params=valence,arousal,dominance,t_panic | hash=d89c793e4e76
  Evidence: Low valence + high arousal + low dominance = fear. | where fear_base = (3 - valence + arousal - dominance) / 3

## m81_trust
- Sources count: 5
- Status: diff
- Code hashes: 1ea44569834c;bad8b999071f
- Params (union): arousal,dominance,t_integ,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal,dominance,t_integ,valence
- Missing in compendium formula: arousal,dominance,t_integ,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m81_trust.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m81_trust.py` | func=compute_m81_trust | params=valence,arousal,dominance,t_integ | hash=bad8b999071f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m81_trust.py` | func=compute_m81_trust | params=valence,arousal,dominance,t_integ | hash=1ea44569834c
  Evidence: High valence + low arousal + high dominance = trust. | where trust_base = (valence + (1 - arousal) + dominance) / 3
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m81_trust.py` | func=compute_m81_trust | params=valence,arousal,dominance,t_integ | hash=bad8b999071f
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m81_trust.py` | func=compute_m81_trust | params=valence,arousal,dominance,t_integ | hash=bad8b999071f
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m81_trust.py` | func=compute_m81_trust | params=valence,arousal,dominance,t_integ | hash=1ea44569834c
  Evidence: High valence + low arousal + high dominance = trust. | where trust_base = (valence + (1 - arousal) + dominance) / 3

## m82_disgust
- Sources count: 5
- Status: diff
- Code hashes: 02cc169eb07e;5bcdd9949dfd
- Params (union): valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: valence
- Missing in compendium formula: valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m82_disgust.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m82_disgust.py` | func=compute_m82_disgust | params=valence | hash=5bcdd9949dfd
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m82_disgust.py` | func=compute_m82_disgust | params=valence | hash=02cc169eb07e
  Evidence: Inverse of valence (low valence = high disgust).
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m82_disgust.py` | func=compute_m82_disgust | params=valence | hash=5bcdd9949dfd
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m82_disgust.py` | func=compute_m82_disgust | params=valence | hash=5bcdd9949dfd
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m82_disgust.py` | func=compute_m82_disgust | params=valence | hash=02cc169eb07e
  Evidence: Inverse of valence (low valence = high disgust).

## m83_anticipation
- Sources count: 5
- Status: diff
- Code hashes: 5c3b3d2e9054;a336c9fd1ede
- Params (union): arousal
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal
- Missing in compendium formula: arousal
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m83_anticipation.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m83_anticipation.py` | func=compute_m83_anticipation | params=arousal | hash=a336c9fd1ede
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m83_anticipation.py` | func=compute_m83_anticipation | params=arousal | hash=5c3b3d2e9054
  Evidence: Directly proportional to arousal (high arousal = high anticipation).
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m83_anticipation.py` | func=compute_m83_anticipation | params=arousal | hash=a336c9fd1ede
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m83_anticipation.py` | func=compute_m83_anticipation | params=arousal | hash=a336c9fd1ede
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m83_anticipation.py` | func=compute_m83_anticipation | params=arousal | hash=5c3b3d2e9054
  Evidence: Directly proportional to arousal (high arousal = high anticipation).

## m84_surprise
- Sources count: 5
- Status: diff
- Code hashes: 68b7b2a63848;c54fd907eab5
- Params (union): arousal,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal,valence
- Missing in compendium formula: arousal,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m84_surprise.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m84_surprise.py` | func=compute_m84_surprise | params=valence,arousal | hash=68b7b2a63848
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m84_surprise.py` | func=compute_m84_surprise | params=valence,arousal | hash=c54fd907eab5
  Evidence: High arousal with neutral valence = surprise.
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m84_surprise.py` | func=compute_m84_surprise | params=valence,arousal | hash=68b7b2a63848
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m84_surprise.py` | func=compute_m84_surprise | params=valence,arousal | hash=68b7b2a63848
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m84_surprise.py` | func=compute_m84_surprise | params=valence,arousal | hash=c54fd907eab5
  Evidence: High arousal with neutral valence = surprise.

## m85_hope
- Sources count: 5
- Status: diff
- Code hashes: 9b582618959d;ebb5b7768101
- Params (union): anticipation,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: anticipation,valence
- Missing in compendium formula: anticipation,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m85_hope.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m85_hope.py` | func=compute_m85_hope | params=valence,anticipation | hash=ebb5b7768101
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m85_hope.py` | func=compute_m85_hope | params=valence,anticipation | hash=9b582618959d
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m85_hope.py` | func=compute_m85_hope | params=valence,anticipation | hash=ebb5b7768101
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m85_hope.py` | func=compute_m85_hope | params=valence,anticipation | hash=ebb5b7768101
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m85_hope.py` | func=compute_m85_hope | params=valence,anticipation | hash=9b582618959d
  Evidence: nan

## m86_despair
- Sources count: 5
- Status: diff
- Code hashes: 26530aaf0302;5d4c96722af7
- Params (union): sadness,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: sadness,valence
- Missing in compendium formula: sadness,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m86_despair.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m86_despair.py` | func=compute_m86_despair | params=valence,sadness | hash=26530aaf0302
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m86_despair.py` | func=compute_m86_despair | params=valence,sadness | hash=5d4c96722af7
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m86_despair.py` | func=compute_m86_despair | params=valence,sadness | hash=26530aaf0302
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m86_despair.py` | func=compute_m86_despair | params=valence,sadness | hash=26530aaf0302
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m86_despair.py` | func=compute_m86_despair | params=valence,sadness | hash=5d4c96722af7
  Evidence: nan

## m87_confusion
- Sources count: 5
- Status: diff
- Code hashes: 6ed8f523e9ca;a8203811a48e
- Params (union): PCI,arousal
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: PCI,arousal
- Missing in compendium formula: PCI,arousal
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m87_confusion.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m87_confusion.py` | func=compute_m87_confusion | params=arousal,PCI | hash=6ed8f523e9ca
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m87_confusion.py` | func=compute_m87_confusion | params=arousal,PCI | hash=a8203811a48e
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m87_confusion.py` | func=compute_m87_confusion | params=arousal,PCI | hash=6ed8f523e9ca
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m87_confusion.py` | func=compute_m87_confusion | params=arousal,PCI | hash=6ed8f523e9ca
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m87_confusion.py` | func=compute_m87_confusion | params=arousal,PCI | hash=a8203811a48e
  Evidence: nan

## m88_clarity
- Sources count: 5
- Status: diff
- Code hashes: e1438053e31a;e1ee1f4693b6
- Params (union): PCI,arousal
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: PCI,arousal
- Missing in compendium formula: PCI,arousal
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m88_clarity.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m88_clarity.py` | func=compute_m88_clarity | params=PCI,arousal | hash=e1438053e31a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m88_clarity.py` | func=compute_m88_clarity | params=PCI,arousal | hash=e1ee1f4693b6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m88_clarity.py` | func=compute_m88_clarity | params=PCI,arousal | hash=e1438053e31a
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m88_clarity.py` | func=compute_m88_clarity | params=PCI,arousal | hash=e1438053e31a
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m88_clarity.py` | func=compute_m88_clarity | params=PCI,arousal | hash=e1ee1f4693b6
  Evidence: nan

## m89_acceptance
- Sources count: 5
- Status: diff
- Code hashes: 038a7e5043a8;5a1752937744
- Params (union): arousal,t_integ,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal,t_integ,valence
- Missing in compendium formula: arousal,t_integ,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m89_acceptance.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m89_acceptance.py` | func=compute_m89_acceptance | params=valence,arousal,t_integ | hash=038a7e5043a8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m89_acceptance.py` | func=compute_m89_acceptance | params=valence,arousal,t_integ | hash=5a1752937744
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m89_acceptance.py` | func=compute_m89_acceptance | params=valence,arousal,t_integ | hash=038a7e5043a8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m89_acceptance.py` | func=compute_m89_acceptance | params=valence,arousal,t_integ | hash=038a7e5043a8
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m89_acceptance.py` | func=compute_m89_acceptance | params=valence,arousal,t_integ | hash=5a1752937744
  Evidence: nan

## m8_x_exist
- Sources count: 8
- Status: diff
- Code hashes: 1999187c27fe;64de1e2bddd4
- Params (union): text,x_exist_lexikon
- Compendium formula: x_exist = max(weight_i) für alle matches in AngstromLexika.X_EXIST wobei: X_EXIST = {"ich bin": 0.8, "existiert": 1.0, "wirklich": 0.6, "real": 0.7, "tatsächlich": 0.5, "vorhanden": 0.4, ...} weight_i = Gewicht des gefundenen Terms
- Compendium upstream: nan
- Missing in compendium upstream: text,x_exist_lexikon
- Missing in compendium formula: text,x_exist_lexikon
- Downstream usage: **Ångström-Berechnung:** Fließt in m10_angstrom ein; **Tiefenmessung:** Hohe Werte → philosophischer Kontext; **Kontext-Anpassung:** Erlaubt existenzielle Antwort-Modi
- Pros: Foundational metric used by many downstream computations
- Cons: Errors propagate widely across system
- Impact: Downstream impact if inconsistent: **Ångström-Berechnung:** Fließt in m10_angstrom ein; **Tiefenmessung:** Hohe Werte → philosophischer Kontext; **Kontext-Anpassung:** Erlaubt existenzielle Antwort-Modi
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m8_x_exist.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m8_x_exist.py` | func=compute_m8_x_exist | params=text,x_exist_lexikon | hash=1999187c27fe
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m8_x_exist.py` | func=compute_m8_x_exist | params=text,x_exist_lexikon | hash=64de1e2bddd4
  Evidence: x_exist = max(weight_i) for all matching terms in lexicon
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m8_x_exist.py` | func=compute_m8_x_exist | params=text,x_exist_lexikon | hash=1999187c27fe
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m8_x_exist.py` | func=compute_m8_x_exist | params=text,x_exist_lexikon | hash=64de1e2bddd4
  Evidence: x_exist = max(weight_i) for all matching terms in lexicon
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m8_x_exist.py` | func=compute_m8_x_exist | params=text,x_exist_lexikon | hash=64de1e2bddd4
  Evidence: x_exist = max(weight_i) for all matching terms in lexicon
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m8_x_exist.py` | func=compute_m8_x_exist | params=text,x_exist_lexikon | hash=64de1e2bddd4
  Evidence: x_exist = max(weight_i) for all matching terms in lexicon
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m8_x_exist.py` | func=compute_m8_x_exist | params=text,x_exist_lexikon | hash=1999187c27fe
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m8_x_exist.py` | func=compute_m8_x_exist | params=text,x_exist_lexikon | hash=64de1e2bddd4
  Evidence: x_exist = max(weight_i) for all matching terms in lexicon

## m90_resistance
- Sources count: 5
- Status: diff
- Code hashes: a63114ee78e0;c4bc31a7c833
- Params (union): acceptance,arousal
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: acceptance,arousal
- Missing in compendium formula: acceptance,arousal
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m90_resistance.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m90_resistance.py` | func=compute_m90_resistance | params=arousal,acceptance | hash=a63114ee78e0
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m90_resistance.py` | func=compute_m90_resistance | params=arousal,acceptance | hash=c4bc31a7c833
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m90_resistance.py` | func=compute_m90_resistance | params=arousal,acceptance | hash=a63114ee78e0
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m90_resistance.py` | func=compute_m90_resistance | params=arousal,acceptance | hash=a63114ee78e0
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m90_resistance.py` | func=compute_m90_resistance | params=arousal,acceptance | hash=c4bc31a7c833
  Evidence: nan

## m91_emotional_coherence
- Sources count: 5
- Status: diff
- Code hashes: ad0aef667887;b89583f6b0d9
- Params (union): PCI,t_disso
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: PCI,t_disso
- Missing in compendium formula: PCI,t_disso
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m91_emotional_coherence.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m91_emotional_coherence.py` | func=compute_m91_emotional_coherence | params=PCI,t_disso | hash=b89583f6b0d9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m91_emotional_coherence.py` | func=compute_m91_emotional_coherence | params=PCI,t_disso | hash=ad0aef667887
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m91_emotional_coherence.py` | func=compute_m91_emotional_coherence | params=PCI,t_disso | hash=b89583f6b0d9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m91_emotional_coherence.py` | func=compute_m91_emotional_coherence | params=PCI,t_disso | hash=b89583f6b0d9
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m91_emotional_coherence.py` | func=compute_m91_emotional_coherence | params=PCI,t_disso | hash=ad0aef667887
  Evidence: nan

## m92_emotional_stability
- Sources count: 5
- Status: diff
- Code hashes: 53f276ed6d71;9eb29cb4ce76
- Params (union): arousal,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal,valence
- Missing in compendium formula: arousal,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m92_emotional_stability.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m92_emotional_stability.py` | func=compute_m92_emotional_stability | params=valence,arousal | hash=9eb29cb4ce76
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m92_emotional_stability.py` | func=compute_m92_emotional_stability | params=valence,arousal | hash=53f276ed6d71
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m92_emotional_stability.py` | func=compute_m92_emotional_stability | params=valence,arousal | hash=9eb29cb4ce76
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m92_emotional_stability.py` | func=compute_m92_emotional_stability | params=valence,arousal | hash=9eb29cb4ce76
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m92_emotional_stability.py` | func=compute_m92_emotional_stability | params=valence,arousal | hash=53f276ed6d71
  Evidence: nan

## m93_emotional_range
- Sources count: 5
- Status: diff
- Code hashes: 68d53dc56d27;72af82c2e2c8
- Params (union): a,d,v
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: a,d,v
- Missing in compendium formula: a,d,v
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m93_emotional_range.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m93_emotional_range.py` | func=compute_m93_emotional_range | params=v,a,d | hash=72af82c2e2c8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m93_emotional_range.py` | func=compute_m93_emotional_range | params=v,a,d | hash=68d53dc56d27
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m93_emotional_range.py` | func=compute_m93_emotional_range | params=v,a,d | hash=72af82c2e2c8
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m93_emotional_range.py` | func=compute_m93_emotional_range | params=v,a,d | hash=72af82c2e2c8
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m93_emotional_range.py` | func=compute_m93_emotional_range | params=v,a,d | hash=68d53dc56d27
  Evidence: nan

## m94_comfort
- Sources count: 5
- Status: diff
- Code hashes: 53ffe357bc50;5b84359336b9
- Params (union): arousal,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal,valence
- Missing in compendium formula: arousal,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m94_comfort.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m94_comfort.py` | func=compute_m94_comfort | params=valence,arousal | hash=53ffe357bc50
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m94_comfort.py` | func=compute_m94_comfort | params=valence,arousal | hash=5b84359336b9
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m94_comfort.py` | func=compute_m94_comfort | params=valence,arousal | hash=53ffe357bc50
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m94_comfort.py` | func=compute_m94_comfort | params=valence,arousal | hash=53ffe357bc50
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m94_comfort.py` | func=compute_m94_comfort | params=valence,arousal | hash=5b84359336b9
  Evidence: nan

## m95_tension
- Sources count: 5
- Status: diff
- Code hashes: 1bd229f6ad70;71944f3d8bcb
- Params (union): arousal,valence
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: arousal,valence
- Missing in compendium formula: arousal,valence
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m95_tension.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m95_tension.py` | func=compute_m95_tension | params=valence,arousal | hash=1bd229f6ad70
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m95_tension.py` | func=compute_m95_tension | params=valence,arousal | hash=71944f3d8bcb
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m95_tension.py` | func=compute_m95_tension | params=valence,arousal | hash=1bd229f6ad70
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m95_tension.py` | func=compute_m95_tension | params=valence,arousal | hash=1bd229f6ad70
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m95_tension.py` | func=compute_m95_tension | params=valence,arousal | hash=71944f3d8bcb
  Evidence: nan

## m96_grain_word
- Sources count: 4
- Status: identical
- Code hashes: ff565fdf5868
- Params (union): text
- Compendium formula: grain_word = word_complexity_score wobei: word_complexity_score = Σ(word_complexity_i) / word_count word_complexity_i = f(length, syllables, frequency)
- Compendium upstream: text
- Missing in compendium upstream: nan
- Missing in compendium formula: text
- Downstream usage: nan
- Pros: Adds emotional nuance for response modulation
- Cons: Lexicon/heuristic bias can misclassify context; Lexicon/marker dependency requires maintenance and context handling
- Impact: Downstream impact if inconsistent: nan
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m96_grain_word.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m96_grain_word.py` | func=compute_m96_grain_word | params=text | hash=ff565fdf5868
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m96_grain_word.py` | func=compute_m96_grain_word | params=text | hash=ff565fdf5868
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m96_grain_word.py` | func=compute_m96_grain_word | params=text | hash=ff565fdf5868
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m96_grain_word.py` | func=compute_m96_grain_word | params=text | hash=ff565fdf5868
  Evidence: nan

## m97_grain_cat
- Sources count: 4
- Status: identical
- Code hashes: 918fcff8db85
- Params (union): grain_word
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: grain_word
- Missing in compendium formula: grain_word
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m97_grain_cat.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m97_grain_cat.py` | func=compute_m97_grain_cat | params=grain_word | hash=918fcff8db85
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m97_grain_cat.py` | func=compute_m97_grain_cat | params=grain_word | hash=918fcff8db85
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m97_grain_cat.py` | func=compute_m97_grain_cat | params=grain_word | hash=918fcff8db85
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m97_grain_cat.py` | func=compute_m97_grain_cat | params=grain_word | hash=918fcff8db85
  Evidence: nan

## m98_grain_score
- Sources count: 4
- Status: identical
- Code hashes: 73cd65f88781
- Params (union): grain_word,text
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: grain_word,text
- Missing in compendium formula: grain_word,text
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m98_grain_score.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m98_grain_score.py` | func=compute_m98_grain_score | params=text,grain_word | hash=73cd65f88781
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m98_grain_score.py` | func=compute_m98_grain_score | params=text,grain_word | hash=73cd65f88781
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m98_grain_score.py` | func=compute_m98_grain_score | params=text,grain_word | hash=73cd65f88781
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m98_grain_score.py` | func=compute_m98_grain_score | params=text,grain_word | hash=73cd65f88781
  Evidence: nan

## m99_grain_impact
- Sources count: 4
- Status: identical
- Code hashes: 368387ccdba6
- Params (union): A,grain_score
- Compendium formula: nan
- Compendium upstream: nan
- Missing in compendium upstream: A,grain_score
- Missing in compendium formula: A,grain_score
- Downstream usage: nan
- Pros: nan
- Cons: nan
- Impact: No downstream info
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m99_grain_impact.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: No code-level differences detected across sources (by AST hash).

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m99_grain_impact.py` | func=compute_m99_grain_impact | params=grain_score,A | hash=368387ccdba6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m99_grain_impact.py` | func=compute_m99_grain_impact | params=grain_score,A | hash=368387ccdba6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m99_grain_impact.py` | func=compute_m99_grain_impact | params=grain_score,A | hash=368387ccdba6
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m99_grain_impact.py` | func=compute_m99_grain_impact | params=grain_score,A | hash=368387ccdba6
  Evidence: nan

## m9_b_past
- Sources count: 8
- Status: diff
- Code hashes: 142a98cab0e6;279896bb99ae
- Params (union): b_past_lexikon,text
- Compendium formula: b_past = max(weight_i) für alle matches in AngstromLexika.B_PAST wobei: B_PAST = {"früher": 0.7, "erinnere": 0.9, "damals": 0.8, "war einmal": 0.6, "als ich": 0.5, "zurück": 0.4, ...}
- Compendium upstream: nan
- Missing in compendium upstream: b_past_lexikon,text
- Missing in compendium formula: b_past_lexikon,text
- Downstream usage: **Ångström-Berechnung:** Fließt in m10_angstrom ein; **Trauma-Detektion:** Hohe Werte + hohe T_panic → potenzielle Verarbeitung; **Narrativ-Analyse:** Erkennt autobiographische Texte
- Pros: Foundational metric used by many downstream computations
- Cons: Errors propagate widely across system
- Impact: Downstream impact if inconsistent: **Ångström-Berechnung:** Fließt in m10_angstrom ein; **Trauma-Detektion:** Hohe Werte + hohe T_panic → potenzielle Verarbeitung; **Narrativ-Analyse:** Erkennt autobiographische Texte
- Best source: `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m9_b_past.py`
- Best source reason: Complete library: full coverage, generated/compiled implementation
- Meaning: Inconsistent implementations across sources; outputs may diverge and propagate to downstream metrics.

**Variants:**
- `C:\Users\nicom\Desktop\Metriken\claude_metric\m9_b_past.py` | func=compute_m9_b_past | params=text,b_past_lexikon | hash=142a98cab0e6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib\m9_b_past.py` | func=compute_m9_b_past | params=text,b_past_lexikon | hash=279896bb99ae
  Evidence: b_past = max(weight_i) for all matching terms in lexicon
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_complete\m9_b_past.py` | func=compute_m9_b_past | params=text,b_past_lexikon | hash=142a98cab0e6
  Evidence: nan
- `C:\Users\nicom\Desktop\Metriken\metrics_lib_extracted\m9_b_past.py` | func=compute_m9_b_past | params=text,b_past_lexikon | hash=279896bb99ae
  Evidence: b_past = max(weight_i) for all matching terms in lexicon
- `C:\Users\nicom\Desktop\Metriken\metriken_claude_extracted\m9_b_past.py` | func=compute_m9_b_past | params=text,b_past_lexikon | hash=279896bb99ae
  Evidence: b_past = max(weight_i) for all matching terms in lexicon
- `C:\Users\nicom\Desktop\Metriken\temp_metrics_lib\m9_b_past.py` | func=compute_m9_b_past | params=text,b_past_lexikon | hash=279896bb99ae
  Evidence: b_past = max(weight_i) for all matching terms in lexicon
- `C:\Users\nicom\Desktop\Metriken\temp_metriks\m9_b_past.py` | func=compute_m9_b_past | params=text,b_past_lexikon | hash=142a98cab0e6
  Evidence: nan
- `C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib_legacy\m9_b_past.py` | func=compute_m9_b_past | params=text,b_past_lexikon | hash=279896bb99ae
  Evidence: b_past = max(weight_i) for all matching terms in lexicon
