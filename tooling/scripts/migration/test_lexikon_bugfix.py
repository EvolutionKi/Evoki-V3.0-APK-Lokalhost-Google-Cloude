#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST: Lexikon Word-Boundary Bug-Fix
Validiert dass Substring-Matches nicht mehr auftreten
"""

import sys
sys.path.insert(0, r'C:\Evoki V3.0 APK-Lokalhost-Google Cloude')

from tooling.scripts.migration.lexika_v12 import (
    compute_lexicon_score,
    S_SELF,
    X_EXIST,
    T_PANIC
)

print("=" * 80)
print("LEXIKON WORD-BOUNDARY BUG-FIX TEST")
print("=" * 80)

# Test 1: "ich" soll NICHT in "nicht" matchen
print("\n📋 Test 1: 'nicht ich' (sollte NUR 'ich' matchen, NICHT 'nicht')")
score, matches = compute_lexicon_score("nicht ich", S_SELF)
print(f"   Score: {score:.3f}")
print(f"   Matches: {matches}")
print(f"   ✅ PASS" if "nicht" not in matches and "ich" in matches else "   ❌ FAIL")

# Test 2: "leer" soll NICHT in "leeren" matchen
print("\n📋 Test 2: 'leeren kopf' (sollte NICHT 'leer' matchen)")
score, matches = compute_lexicon_score("leeren kopf", X_EXIST)
print(f"   Score: {score:.3f}")
print(f"   Matches: {matches}")
print(f"   ✅ PASS" if "leer" not in matches else "   ❌ FAIL")

# Test 3: "angst" soll NICHT in "angstfrei" matchen
print("\n📋 Test 3: 'ich bin angstfrei' (sollte NICHT 'angst' matchen)")
score_s, matches_s = compute_lexicon_score("ich bin angstfrei", S_SELF)
score_p, matches_p = compute_lexicon_score("ich bin angstfrei", T_PANIC)
print(f"   S_SELF: Score={score_s:.3f}, Matches={matches_s}")
print(f"   T_PANIC: Score={score_p:.3f}, Matches={matches_p}")
print(f"   ✅ PASS" if "angst" not in matches_p and "ich" in matches_s else "   ❌ FAIL")

# Test 4: Multi-Word-Phrases sollen funktionieren
print("\n📋 Test 4: 'ich kann nicht atmen' (sollte Multi-Word matchen)")
score, matches = compute_lexicon_score("ich kann nicht atmen", T_PANIC)
print(f"   Score: {score:.3f}")
print(f"   Matches: {matches}")
print(f"   ✅ PASS" if "kann nicht atmen" in matches else "   ❌ FAIL (erwartet: 'kann nicht atmen')")

# Test 5: Echtes Suizid-Beispiel
print("\n📋 Test 5: 'ich will nicht mehr leben' (KRITISCH!)")
from tooling.scripts.migration.lexika_v12 import compute_hazard_score
hazard, is_critical, h_matches = compute_hazard_score("ich will nicht mehr leben")
print(f"   Hazard Score: {hazard:.3f}")
print(f"   Is Critical: {is_critical}")
print(f"   Matches: {h_matches[:3]}")
print(f"   ✅ PASS" if is_critical and hazard > 0.8 else "   ❌ FAIL")

print("\n" + "=" * 80)
print("TESTS ABGESCHLOSSEN")
print("=" * 80)
