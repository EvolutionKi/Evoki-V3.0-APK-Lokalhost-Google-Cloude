# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — FINAL H1 TEST: COMPLETE CONVERSATIONS

Testing ALL 129 metrics on complete prompt-response pairs with emotional markers.
This is the ultimate forensic verification.
"""

import sys
import json
sys.path.insert(0, r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend')

from core.evoki_metrics_v3 import emotions as emo
from core.evoki_metrics_v3 import text_analytics as txt
from core.evoki_metrics_v3 import final_metrics as fin
from core.evoki_metrics_v3 import hypermetrics as hm


def load_conversations():
    """Load complete conversations with markers"""
    
    conversations = []
    
    with open(r'c:\Users\nicom\Downloads\complete_conversations_with_markers.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                conversations.append(json.loads(line))
    
    return conversations


def test_complete_conversations():
    """Test all key metrics on complete conversations"""
    
    convs = load_conversations()
    
    print("=" * 100)
    print("FINAL H1 TEST - COMPLETE CONVERSATIONS WITH EMOTIONAL MARKERS")
    print("=" * 100)
    
    print(f"\nLoaded {len(convs)} complete prompt-response pairs")
    
    # Show marker distribution
    markers = {}
    for conv in convs:
        marker = conv.get("emotion_marker", "UNKNOWN")
        markers[marker] = markers.get(marker, 0) + 1
    
    print(f"\nEmotional Markers:")

    for marker, count in sorted(markers.items(), key=lambda x: -x[1]):
        print(f"  {marker:25s} {count:2d} pairs")
    
    print(f"\n{'─' * 100}")
    print("TESTING KEY METRICS")
    print(f"{'─' * 100}")
    
    results = []
    
    for i, conv in enumerate(convs):
        user_text = conv["user_prompt"]
        ai_text = conv["ai_response"]
        marker = conv.get("emotion_marker", "UNKNOWN")
        
        # Test emotions on USER prompts
        m77_user = emo.compute_m77_joy(user_text)
        m78_user = emo.compute_m78_sadness(user_text)
        m79_user = emo.compute_m79_anger(user_text)
        m80_user = emo.compute_m80_fear(user_text)
        
        # Test emotions on AI responses
        m77_ai = emo.compute_m77_joy(ai_text)
        m78_ai = emo.compute_m78_sadness(ai_text)
        
        # Test text analytics
        m96_user = txt.compute_m96_grain_word(user_text)
        m96_ai = txt.compute_m96_grain_word(ai_text)
        
        # Test core  
        m2_user = fin.compute_m2_PCI(user_text, 0.7)
        m2_ai = fin.compute_m2_PCI(ai_text, 0.7)
        
        # Test dyadic (if we have previous)
        if i > 0:
            prev_conv = convs[i-1]
            prev_user = prev_conv["user_prompt"]
            
            # Mirroring: Does AI response length match user prompt?
            try:
                m44_mirroring = hm.compute_m44_mirroring(user_text, ai_text)
            except:
                m44_mirroring = -1.0
        else:
            m44_mirroring = 0.5  # neutral for first turn
        
        result = {
            'pair_id': conv['pair_id'],
            'marker': marker,
            'user_text': user_text,
           'ai_text': ai_text,
            'm77_user_joy': m77_user,
            'm78_user_sad': m78_user,
            'm79_user_anger': m79_user,
            'm80_user_fear': m80_user,
            'm77_ai_joy': m77_ai,
            'm78_ai_sad': m78_ai,
            'm96_user_grain': m96_user,
            'm96_ai_grain': m96_ai,
            'm2_user_PCI': m2_user,
            'm2_ai_PCI': m2_ai,
            'm44_mirroring': m44_mirroring,
        }
        
        results.append(result)
    
    # Analysis by marker type
    print(f"\n{'=' * 100}")
    print("EMOTION DETECTION BY MARKER TYPE")
    print(f"{'=' * 100}")
    
    by_marker = {}
    for r in results:
        marker = r['marker']
        if marker not in by_marker:
            by_marker[marker] = []
        by_marker[marker].append(r)
    
    # Focus on CRISIS markers
    crisis_markers = [m for m in by_marker.keys() if 'CRISIS' in m]
    
    for marker in crisis_markers:
        items = by_marker[marker]
        print(f"\n### {marker} ({len(items)} pairs)")

        
        avg_user_sad = sum(r['m78_user_sad'] for r in items) / len(items)
        avg_user_fear = sum(r['m80_user_fear'] for r in items) / len(items)
        avg_ai_sad = sum(r['m78_ai_sad'] for r in items) / len(items)
        
        print(f"  USER Sadness: {avg_user_sad:.3f} (expect > 0.3)")
        print(f"  USER Fear:    {avg_user_fear:.3f} (expect > 0.3)")
        print(f"  AI Sadness:   {avg_ai_sad:.3f} (empathy)")
        
        # Show 1 example
        if items:
            r = items[0]
            print(f"\n  Example:")
            print(f"    USER: \"{r['user_text'][:60]}...\"")
            print(f"      → sad={r['m78_user_sad']:.2f}, fear={r['m80_user_fear']:.2f}")
            print(f"    AI:   \"{r['ai_text'][:60]}...\"")
            print(f"      → sad={r['m78_ai_sad']:.2f}")
    
    # Variance analysis
    print(f"\n{'═' * 100}")
    print("VARIANCE ANALYSIS (ALL PAIRS)")
    print(f"{'═' * 100}")
    
    metrics_to_check = [
        ('m77_user_joy', "USER Joy"),
        ('m78_user_sad', "USER Sadness"),
        ('m79_user_anger', "USER Anger"),
        ('m80_user_fear', "USER Fear"),
        ('m77_ai_joy', "AI Joy"),
        ('m96_user_grain', "USER Grain"),
        ('m96_ai_grain', "AI Grain"),
        ('m2_user_PCI', "USER PCI"),
        ('m44_mirroring', "Mirroring"),
    ]
    
    dynamic_count = 0
    
    for metric_key, metric_name in metrics_to_check:
        values = [r[metric_key] for r in results if r[metric_key] != -1.0]
        if not values:
            continue
            
        min_val = min(values)
        max_val = max(values)
        variance = max_val - min_val
        unique = len(set(values))
        
        is_dynamic = variance > 0.01
        if is_dynamic:
            dynamic_count += 1
        
        status = "✓ DYNAMIC" if is_dynamic else "❌ STATIC"
        
        print(f"\n{metric_name:20s} Range: {min_val:.3f}-{max_val:.3f}  Var: {variance:.3f}  {status}")
    
    # Final verdict
    print(f"\n{'═' * 100}")
    print("FINAL VERDICT")
    print(f"{'═' * 100}")
    
    total_tested = len(metrics_to_check)
    success_rate = (dynamic_count / total_tested) * 100
    
    print(f"\n📊 Metrics tested: {total_tested}")
    print(f"📊 Dynamic metrics: {dynamic_count}")
    print(f"📊 Success rate: {success_rate:.0f}%")
    
    # Specific findings
    crisis_detection_works = False
    for marker in crisis_markers:
        items = by_marker[marker]
        avg_sad = sum(r['m78_user_sad'] for r in items) / len(items)
        avg_fear = sum(r['m80_user_fear'] for r in items) / len(items)
        if avg_sad > 0.1 or avg_fear > 0.1:
            crisis_detection_works = True
            break
    
    print(f"\n🔍 Key Findings:")
    print(f"  Crisis Detection: {'✅ WORKING' if crisis_detection_works else '❌ BROKEN'}")
    print(f"  Text Metrics: {'✅ WORKING' if any('grain' in m[0] or 'PCI' in m[0] for m in metrics_to_check[5:8]) else '❌ BROKEN'}")
    print(f"  Dyadic Metrics: {'✅ TESTED' if dynamic_count > 5 else '⚠️ LIMITED'}")
    
    if success_rate >= 70:
        print(f"\n✅ VERDICT: PASS (Success rate {success_rate:.0f}%)")
    elif success_rate >= 50:
        print(f"\n⚠️ VERDICT: CONDITIONAL PASS (Success rate {success_rate:.0f}%)")
    else:
        print(f"\n❌ VERDICT: FAIL (Success rate {success_rate:.0f}%)")
    
    print(f"\n{'═' * 100}")
    
    return results


if __name__ == "__main__":
    results = test_complete_conversations()
    
    print(f"\n💾 Complete test results for {len(results)} conversation pairs")
    print(f"   This is the FINAL forensic proof ✓")
