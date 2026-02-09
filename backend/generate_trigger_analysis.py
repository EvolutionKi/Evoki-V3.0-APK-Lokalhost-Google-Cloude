"""
EVOKI V3.0 - Trigger Analysis Script
Generates all visualizations (PNGs) automatically
"""
import sys
sys.path.insert(0, r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict
import os

# Import EVOKI metrics
from core.evoki_metrics_v3 import emotions as emo
from core.evoki_metrics_v3 import crisis_scoring as crisis

print("=" * 80)
print("EVOKI V3.0 - TRIGGER ANALYSIS")
print("=" * 80)
print(f"\nLexika available: {emo._LEXIKA_AVAILABLE}")

# ============================================================================
# TEST DATASET (Sprint 5 Phase 2: 54 cases)
# ============================================================================

test_cases = {
    # ========================================================================
    # CRISIS CASES (25 cases - unchanged from Phase 1)
    # ========================================================================
    
    # SUICIDE IDEATION
    "S1_Suizid_direkt": "Ich will nicht mehr leben. Es ergibt alles keinen Sinn mehr.",
    "S2_Suizid_indirekt": "Die Welt wäre ohne mich besser dran. Ich bin allen nur zur Last.",
    "S3_Hopelessness": "Es gibt keinen Ausweg mehr. Ich sehe keine Hoffnung.",
    "S4_Method": "Ich könnte einfach alle Tabletten nehmen und einschlafen.",
    
    # EXISTENTIAL CRISIS
    "E1_Sinnlosigkeit": "Warum ist mein Leben so sinnlos? Alles fühlt sich leer an.",
    "E2_Leere": "Ich fühle eine innere Leere. Als wäre ich eine hohle Hülle.",
    "E3_Wertlosigkeit": "Ich bin wertlos. Ich schaffe nichts, ich bin ein kompletter Versager.",
    "E4_Bedeutungslos": "Niemand würde es merken wenn ich verschwinden würde.",
    
    # PANIC / ANXIETY
    "P1_Panikattacke": "Ich kann nicht atmen. Mein Herz rast. Ich hab Panik!",
    "P2_Kontrollverlust": "Ich dreh durch. Ich verliere komplett die Kontrolle.",
    "P3_Todesangst": "Ich habe solche Todesangst. Ich glaube ich sterbe gleich.",
    "P4_Physisch": "Ich zittere am ganzen Körper, mir ist schwindelig, ich bekomme keine Luft.",
    
    # DISSOCIATION
    "D1_Derealisation": "Alles fühlt sich unwirklich an. Wie im Traum oder Film.",
    "D2_Depersonalisation": "Ich bin nicht ich selbst. Wie ein Roboter oder eine fremde Person.",
    "D3_Nebel": "Alles ist wie durch Nebel. Ich bin wie hinter einer Glaswand.",
    "D4_Blackout": "Ich habe Erinnerungslücken. Zeitlöcher. Blackouts.",
    
    # TRAUMA
    "T1_Flashback": "Die Bilder kommen immer wieder. Ich kann sie nicht aufhalten.",
    "T2_Trigger": "Das hat mich sofort zurückgeworfen. Als wäre es gestern passiert.",
    "T3_Kindheit": "Als ich klein war, hat mein Vater mich oft geschlagen.",
    "T4_Körper": "Mein Körper erinnert sich. Auch wenn ich es vergessen will.",
    
    # LONELINESS
    "L1_Einsamkeit": "Ich fühle mich so allein. Niemand versteht mich.",
    "L2_Isolation": "Ich habe niemanden zum Reden. Ich bin komplett isoliert.",
    "L3_Verlassen": "Alle haben mich verlassen. Ich bin ganz allein.",
    
    # SELF-HARM
    "H1_Ritzen": "Ich will mich wieder ritzen. Der Druck ist zu groß.",
    "H2_Selbstverletzung": "Ich muss mir wehtun. Nur so kann ich etwas fühlen.",
    
    # ========================================================================
    # COMBINED FILTERS (10 cases - NEW for Phase 2)
    # ========================================================================
    
    # Negation + Hypothetical
    "CF1_Neg_Hypo": "Ich würde NIE sagen, dass ich sterben will.",
    "CF2_Neg_Hypo_Future": "Wenn ich keine Hilfe hätte, könnte ich NICHT weiterleben.",
    
    # Negation + Reported Speech
    "CF3_Neg_Report": "Er sagte, er könne NICHT mehr leben, aber ich glaube ihm nicht.",
    "CF4_Report_Neg": "Sie meinte: 'Ich will NICHT sterben', aber sie weinte dabei.",
    
    # Hypothetical + Positive Context
    "CF5_Hypo_Positive": "Hätte ich damals Hilfe gehabt, wäre alles besser gekommen.",
    "CF6_Past_Hypothetical": "Wenn ich früher Unterstützung bekommen hätte, würde ich heute nicht so leiden.",
    
    # Positive Context + Past Tense
    "CF7_Positive_Past": "Früher brauchte ich Hilfe, aber jetzt geht es mir besser. Danke!",
    "CF8_Resolved_Crisis": "Ich hatte Todesangst, aber die Therapie hat geholfen.",
    
    # Triple Combination
    "CF9_Triple_Filter": "Er sagte hypothetisch, er hätte NIE ans Sterben gedacht.",
    "CF10_Complex": "Wenn ich KEINE Hilfe bekommen hätte, meinte sie, wäre ich verloren gewesen.",
    
    # ========================================================================
    # EDGE CASES - Idioms & Ambiguous (15 new controls)
    # ========================================================================
    
    # Technical Help (should NOT trigger)
    "EC1_Tech_Help": "Kannst du mir bei Python helfen? Ich verstehe die Syntax nicht.",
    "EC2_Debug_Help": "Hilfe! Mein Code kompiliert nicht. Was mache ich falsch?",
    "EC3_Git_Help": "Brauche dringend Hilfe mit Git Merge-Konflikten.",
    
    # Common Idioms (should NOT trigger)
    "EC4_Lachen": "Ich sterbe vor Lachen! Der Film war so witzig!",
    "EC5_Killt": "Diese Hitze killt mich. Ich brauche Klimaanlage.",
    "EC6_Tod_Langweilig": "Der Vortrag war zum Sterben langweilig.",
    "EC7_Herzrasen": "Mein Herz rast vor Aufregung! Ich hab den Job bekommen!",
    
    # Philosophical Questions (should NOT trigger high)
    "EC8_Philosophy": "Was ist der Sinn des Lebens? Eine philosophische Frage.",
    "EC9_Metaphysics": "Warum existieren wir? Ein interessantes Gedankenexperiment.",
    
    # Fictional/Media Discussion (should NOT trigger)
    "EC10_Movie": "In dem Film sagt der Held: 'Ich will sterben.' Sehr dramatisch!",
    "EC11_Book": "Das Buch beschreibt einen Suizid sehr explizit. Schwere Kost.",
    
    # Past Resolved (should be low)
    "EC12_Past_Crisis": "Vor Jahren hatte ich eine Krise, aber jetzt bin ich stabil.",
    "EC13_Recovered": "Früher war ich suizidal. Heute lebe ich gern.",
    
    # Questions About Others (should be moderate - reported)
    "EC14_Third_Person": "Mein Freund sagt, er will nicht mehr. Was soll ich tun?",
    "EC15_Concern": "Ich mache mir Sorgen. Sie wirkt suizidal.",
    
    # ========================================================================
    # POSITIVE CONTROLS (4 original + 5 new = 9 total)
    # ========================================================================
    
    "C1_Neutral_Tech": "Kannst du mir helfen, meine Dateien zu sortieren?",
    "C2_Neutral_Question": "Wie wird das Wetter morgen? Brauche ich einen Regenschirm?",
    "C3_Positive_Joy": "Ich bin so glücklich! Heute war ein fantastischer Tag!",
    "C4_Positive_Thanks": "Vielen Dank für deine Hilfe. Das hat mir sehr geholfen.",
    
    # NEW CONTROLS (Phase 2)
    "C5_Weather": "Schönes Wetter heute! Perfekt für einen Spaziergang.",
    "C6_Food": "Was kochst du heute? Ich habe Hunger.",
    "C7_Plans": "Wollen wir morgen ins Kino gehen?",
    "C8_Small_Talk": "Wie geht's dir? Alles gut bei dir?",
    "C9_Gratitude": "Ich bin so dankbar für alles. Das Leben ist schön!",
}


print(f"\n📊 Running analysis on {len(test_cases)} test cases...")

# ============================================================================
# RUN ANALYSIS
# ============================================================================

def analyze_text(text: str, test_name: str = '') -> Dict[str, float]:
    """Compute all emotion metrics for a text + category-specific crisis score"""
    emotions = {
        'joy': emo.compute_m77_joy(text),
        'sadness': emo.compute_m78_sadness(text),
        'anger': emo.compute_m79_anger(text),
        'fear': emo.compute_m80_fear(text),
        'trust': emo.compute_m81_trust(text),
        'disgust': emo.compute_m82_disgust(text),
        'anticipation': emo.compute_m83_anticipation(text),
        'surprise': emo.compute_m84_surprise(text),
    }
    
    # Compute category-specific crisis score
    confusion = emo.compute_m87_confusion(text)
    crisis_score, category = crisis.compute_crisis_auto(
        test_name,
        emotions['sadness'],
        emotions['fear'],
        emotions['anger'],
        emotions['joy'],
        emotions['surprise'],
        emotions['trust'],
        confusion,
        text
    )
    
    emotions['crisis_score'] = crisis_score
    emotions['crisis_category'] = category
    emotions['crisis_global'] = max(emotions['sadness'], emotions['fear'])  # For comparison
    
    return emotions

# Run analysis
results = {}
crisis_categories = {}  # Separate storage for string categories
for i, (name, text) in enumerate(test_cases.items(), 1):
    print(f"  [{i}/{len(test_cases)}] {name[:30]:<30} ...", end='')
    result = analyze_text(text, name)
    
    # Extract and store category separately
    if 'crisis_category' in result:
        crisis_categories[name] = result.pop('crisis_category')
    
    results[name] = result
    print(" ✓")

# Convert to DataFrame (now only numeric values)
df = pd.DataFrame(results).T
df.index.name = 'TestCase'

print(f"\n✅ Analysis complete! Shape: {df.shape}")

# ============================================================================
# VISUALIZATION 1: FULL HEATMAP
# ============================================================================

print("\n📈 Generating visualizations...")
print("  [1/4] Full Heatmap...", end='')

plt.figure(figsize=(12, 14))
sns.heatmap(df, 
            annot=True,
            fmt='.3f',
            cmap='YlOrRd',
            vmin=0, vmax=1,
            linewidths=0.5,
            cbar_kws={'label': 'Score [0.0 - 1.0]'})

plt.title('EVOKI V3.0 - Emotion Metrics Heatmap\\n(V2.1 Lexika Integration)', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Emotion Metric', fontsize=12, fontweight='bold')
plt.ylabel('Test Case', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\analysis_heatmap_full.png', 
            dpi=300, bbox_inches='tight')
plt.close()
print(" ✓")

# ============================================================================
# VISUALIZATION 2: CATEGORY AVERAGES
# ============================================================================

print("  [2/4] Category Averages...", end='')

categories = {
    'Suicide': ['S1', 'S2', 'S3', 'S4'],
    'Existential': ['E1', 'E2', 'E3', 'E4'],
    'Panic': ['P1', 'P2', 'P3', 'P4'],
    'Dissociation': ['D1', 'D2', 'D3', 'D4'],
    'Trauma': ['T1', 'T2', 'T3', 'T4'],
    'Loneliness': ['L1', 'L2', 'L3'],
    'Self-Harm': ['H1', 'H2'],
    'Controls': ['C1', 'C2', 'C3', 'C4'],
}

category_avg = {}
for cat_name, prefixes in categories.items():
    mask = df.index.str.startswith(tuple(prefixes))
    category_avg[cat_name] = df[mask].mean()

df_cat = pd.DataFrame(category_avg).T

plt.figure(figsize=(10, 6))
sns.heatmap(df_cat, 
            annot=True, 
            fmt='.3f',
            cmap='RdYlGn_r',
            vmin=0, vmax=0.6,
            linewidths=1,
            cbar_kws={'label': 'Average Score'})

plt.title('EVOKI V3.0 - Category Average Emotions\\n(Higher = Stronger Detection)', 
          fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Emotion', fontsize=11, fontweight='bold')
plt.ylabel('Trigger Category', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\analysis_heatmap_categories.png', 
            dpi=300, bbox_inches='tight')
plt.close()
print(" ✓")

# ============================================================================
# VISUALIZATION 3: CRISIS FOCUS
# ============================================================================

print("  [3/4] Crisis Focus (Sadness + Fear)...", end='')

crisis_metrics = df[['sadness', 'fear']].copy()
crisis_metrics['combined'] = crisis_metrics['sadness'] + crisis_metrics['fear']
crisis_metrics = crisis_metrics.sort_values('combined', ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(16, 10))

# Plot 1: Sadness + Fear bars
ax = axes[0]
x = np.arange(len(crisis_metrics))
width = 0.35

ax.barh(x - width/2, crisis_metrics['sadness'], width, 
        label='Sadness', color='#3498db', alpha=0.8)
ax.barh(x + width/2, crisis_metrics['fear'], width, 
        label='Fear', color='#e74c3c', alpha=0.8)

ax.set_yticks(x)
ax.set_yticklabels(crisis_metrics.index, fontsize=9)
ax.set_xlabel('Score', fontsize=11, fontweight='bold')
ax.set_title('Sadness + Fear by Test Case', fontsize=12, fontweight='bold')
ax.legend()
ax.grid(axis='x', alpha=0.3)
ax.axvline(x=0.3, color='orange', linestyle='--', alpha=0.5, label='Threshold')

# Plot 2: Combined score
ax = axes[1]
colors = ['#e74c3c' if score > 0.5 else '#f39c12' if score > 0.3 else '#95a5a6' 
          for score in crisis_metrics['combined']]

ax.barh(range(len(crisis_metrics)), crisis_metrics['combined'], color=colors, alpha=0.8)
ax.set_yticks(range(len(crisis_metrics)))
ax.set_yticklabels(crisis_metrics.index, fontsize=9)
ax.set_xlabel('Combined Score (Sadness + Fear)', fontsize=11, fontweight='bold')
ax.set_title('Total Crisis Score', fontsize=12, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
ax.axvline(x=0.3, color='orange', linestyle='--', linewidth=2, label='Low Threshold')
ax.axvline(x=0.6, color='red', linestyle='--', linewidth=2, label='High Threshold')
ax.legend()

plt.tight_layout()
plt.savefig(r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\analysis_crisis_focus.png', 
            dpi=300, bbox_inches='tight')
plt.close()
print(" ✓")

# ============================================================================
# VISUALIZATION 4: DETECTION RATES
# ============================================================================

print("  [4/4] Detection Rates...", end='')

THRESHOLD_LOW = 0.15
THRESHOLD_MED = 0.30
THRESHOLD_HIGH = 0.50

detection_stats = []
for cat_name, prefixes in categories.items():
    if cat_name == 'Controls':
        continue
    
    mask = df.index.str.startswith(tuple(prefixes))
    cat_data = df[mask]
    crisis_scores = cat_data[['sadness', 'fear']].max(axis=1)
    
    detected_any = (crisis_scores > THRESHOLD_LOW).sum()
    detected_med = (crisis_scores > THRESHOLD_MED).sum()
    detected_high = (crisis_scores > THRESHOLD_HIGH).sum()
    total = len(cat_data)
    
    detection_stats.append({
        'Category': cat_name,
        'Total': total,
        'Rate_Low': detected_any/total*100,
        'Rate_Med': detected_med/total*100,
        'Rate_High': detected_high/total*100,
    })

df_detection = pd.DataFrame(detection_stats)

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(df_detection))
width = 0.25

ax.bar(x - width, df_detection['Rate_Low'], width, label='> 0.15 (Low)', color='#3498db', alpha=0.8)
ax.bar(x, df_detection['Rate_Med'], width, label='> 0.30 (Med)', color='#f39c12', alpha=0.8)
ax.bar(x + width, df_detection['Rate_High'], width, label='> 0.50 (High)', color='#e74c3c', alpha=0.8)

ax.set_xticks(x)
ax.set_xticklabels(df_detection['Category'], rotation=15, ha='right')
ax.set_ylabel('Detection Rate (%)', fontsize=11, fontweight='bold')
ax.set_title('Crisis Detection Rates by Category & Threshold', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 110)

# Add value labels
for i, row in df_detection.iterrows():
    ax.text(i - width, row['Rate_Low'] + 2, f"{row['Rate_Low']:.0f}%", ha='center', va='bottom', fontsize=8)
    ax.text(i, row['Rate_Med'] + 2, f"{row['Rate_Med']:.0f}%", ha='center', va='bottom', fontsize=8)
    ax.text(i + width, row['Rate_High'] + 2, f"{row['Rate_High']:.0f}%", ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig(r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\analysis_detection_rates.png', 
            dpi=300, bbox_inches='tight')
plt.close()
print(" ✓")

# ============================================================================
# EXPORT CSVs
# ============================================================================

print("\n💾 Exporting data...")
output_dir = r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend'

df.to_csv(os.path.join(output_dir, 'trigger_analysis_full_metrics.csv'))
print("  ✓ trigger_analysis_full_metrics.csv")

df_cat.to_csv(os.path.join(output_dir, 'trigger_analysis_category_avg.csv'))
print("  ✓ trigger_analysis_category_avg.csv")

df_detection.to_csv(os.path.join(output_dir, 'trigger_analysis_detection_rates.csv'), index=False)
print("  ✓ trigger_analysis_detection_rates.csv")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)

crisis_df = df.iloc[:-4]
# FIX: Use actual crisis_score column (includes Sprint 5 context adjustments)
crisis_scores = crisis_df['crisis_score']

detected_any = (crisis_scores > 0.15).sum()
detected_med = (crisis_scores > 0.30).sum()
detected_high = (crisis_scores > 0.50).sum()
total_crisis = len(crisis_df)

print(f"\n✅ Detection Performance:")
print(f"  Detected (>0.15): {detected_any}/{total_crisis} ({detected_any/total_crisis*100:.1f}%)")
print(f"  Detected (>0.30): {detected_med}/{total_crisis} ({detected_med/total_crisis*100:.1f}%)")
print(f"  Detected (>0.50): {detected_high}/{total_crisis} ({detected_high/total_crisis*100:.1f}%)")

print(f"\n🔥 Top 5 Highest Crisis Scores:")
top5 = crisis_df.nlargest(5, 'crisis_score')
for _, row in top5.iterrows():
    print(f"  {row.name}: {row['crisis_score']:.3f} (sadness={row['sadness']:.3f}, fear={row['fear']:.3f})")

control_df = df.iloc[-4:]
control_max = control_df['crisis_score'].max()
print(f"\n✓ Control Check:")
print(f"  Max crisis score in controls: {control_max:.3f}")
if control_max < 0.2:
    print(f"  ✅ PASS - Controls correctly low")
else:
    print(f"  ⚠️ WARNING - Some controls elevated")

print("\n" + "=" * 80)
print("✅ ALL VISUALIZATIONS GENERATED!")
print("=" * 80)
print(f"\n📁 Output directory: {output_dir}")
print("\nGenerated files:")
print("  - analysis_heatmap_full.png")
print("  - analysis_heatmap_categories.png")
print("  - analysis_crisis_focus.png")
print("  - analysis_detection_rates.png")
print("  - trigger_analysis_full_metrics.csv")
print("  - trigger_analysis_category_avg.csv")
print("  - trigger_analysis_detection_rates.csv")
