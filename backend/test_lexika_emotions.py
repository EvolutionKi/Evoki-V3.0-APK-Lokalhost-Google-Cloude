# -*- coding: utf-8 -*-
"""
Test new lexika-integrated emotion metrics
"""

import sys
sys.path.insert(0, r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend')

from core.evoki_metrics_v3 import emotions as emo

# Test on REAL crisis prompts from llm_training_data.jsonl
crisis_prompts = [
    "Mache 20 Beispiele für Sätze die meinen Selbstwert zerstören",
    "Ich hasse mein Leben. Was soll ich noch hier?",
    "Warum ist mein Leben so sinnlos?",
    "Die Welt wäre ohne mich besser dran",
    "Ich fühle mich so allein. Was soll ich tun?",
]

neutral_prompts = [
    "Spiel das Lied von vorne",
    "Wie wird das Wetter morgen?",
    "Erzähl mir einen Witz",
]

print("=" * 80)
print("LEXIKA-INTEGRATED EMOTION TEST")
print("=" * 80)

print("\n### CRISIS PROMPTS (expect HIGH sadness/fear)")
for text in crisis_prompts:
    m77 = emo.compute_m77_joy(text)
    m78 = emo.compute_m78_sadness(text)
    m79 = emo.compute_m79_anger(text)
    m80 = emo.compute_m80_fear(text)
    
    print(f"\nTEXT: \"{text[:60]}...\"")
    print(f"  joy={m77:.3f}  sadness={m78:.3f}  anger={m79:.3f}  fear={m80:.3f}")
    
    # Verify detection
    if m78 < 0.3 and m80 < 0.3:
        print(f"  ❌ FAILED TO DETECT CRISIS")
    else:
        print(f"  ✅ DETECTED ({m78:.2f} sadness, {m80:.2f} fear)")

print("\n### NEUTRAL PROMPTS (expect LOW emotions)")
for text in neutral_prompts:
    m77 = emo.compute_m77_joy(text)
    m78 = emo.compute_m78_sadness(text)
    m79 = emo.compute_m79_anger(text)
    m80 = emo.compute_m80_fear(text)
    
    print(f"\nTEXT: \"{text}\"")
    print(f"  joy={m77:.3f}  sadness={m78:.3f}  anger={m79:.3f}  fear={m80:.3f}")

print("\n" + "=" * 80)
print("VERDICT:")
print("If crisis prompts show sadness/fear > 0.3, lexika integration WORKS!")
print("=" * 80)
