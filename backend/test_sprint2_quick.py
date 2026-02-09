"""Quick test for Dissociation/Trauma detection (Sprint 2)"""
import sys
sys.path.insert(0, r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend')

from core.evoki_metrics_v3 import emotions as emo

tests = {
    "D1_Derealisation": "Alles fühlt sich unwirklich an. Wie im Traum oder Film.",
    "D2_Depersonalisation": "Ich bin nicht ich selbst. Wie ein Roboter oder eine fremde Person.",
    "D3_Nebel": "Alles ist wie durch Nebel. Ich bin wie hinter einer Glaswand.",
    "D4_Blackout": "Ich habe Erinnerungslücken. Zeitlöcher. Blackouts.",
    "T1_Flashback": "Die Bilder kommen immer wieder. Ich kann sie nicht aufhalten.",
    "T2_Trigger": "Das hat mich sofort zurückgeworfen. Als wäre es gestern passiert.",
    "T3_Kindheit": "Als ich klein war, hat mein Vater mich oft geschlagen.",
    "T4_Körper": "Mein Körper erinnert sich. Auch wenn ich es vergessen will.",
}

print("=" * 80)
print("SPRINT 2 - DISSOCIATION & TRAUMA DETECTION TEST")
print("=" * 80)

print(f"\nLexika available: {emo._LEXIKA_AVAILABLE}")

print("\n" + "=" * 80)
print("RESULTS (Before: all 0.000, Target: >0.15)")
print("=" * 80)

for name, text in tests.items():
    fear = emo.compute_m80_fear(text)
    sadness = emo.compute_m78_sadness(text)
    crisis = max(fear, sadness)
    
    status = "✅" if crisis > 0.15 else "❌"
    print(f"{status} {name:25} | fear={fear:.3f}, sadness={sadness:.3f}, crisis={crisis:.3f}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

all_scores = [(name, max(emo.compute_m80_fear(text), emo.compute_m78_sadness(text))) 
              for name, text in tests.items()]

detected_low = sum(1 for _, score in all_scores if score > 0.15)
detected_med = sum(1 for _, score in all_scores if score > 0.30)
total = len(tests)

print(f"\nDetected (>0.15): {detected_low}/{total} ({detected_low/total*100:.0f}%)")
print(f"Detected (>0.30): {detected_med}/{total} ({detected_med/total*100:.0f}%)")

if detected_low >= 5:  # >60% of 8 tests
    print("\n✅ SPRINT 2: SUCCESS - Dissociation/Trauma coverage added!")
else:
    print(f"\n⚠️ SPRINT 2: PARTIAL - Only {detected_low}/8 detected")
