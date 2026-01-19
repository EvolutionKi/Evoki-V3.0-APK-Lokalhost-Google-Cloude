"""
SEMANTISCHE NÄHE - STICHPROBEN-EXTRAKTION
==========================================
Extrahiert User-AI Paare für semantische Analyse
"""

import json
import re
from pathlib import Path
from datetime import datetime
import random

BASE_DIR = Path(r"C:\evoki\backend\VectorRegs_FORENSIC")

print("🔍 EXTRAHIERE SEMANTISCHE STICHPROBEN...")

# Finde einige Beispiel-Dateien
txt_files = sorted(list(BASE_DIR.glob('2025/**/*.txt')))
print(f"Gefundene Dateien: {len(txt_files):,}\n")

# Extrahiere verschiedene Stichproben
stichproben = []

# Stichprobe 1: Ganz früh (10%)
early_idx = len(txt_files) // 10
# Stichprobe 2: 25%
idx_25 = len(txt_files) // 4
# Stichprobe 3: Mitte (50%)
mid_idx = len(txt_files) // 2
# Stichprobe 4: 75%
idx_75 = 3 * len(txt_files) // 4
# Stichprobe 5: Aktuellste
last_idx = len(txt_files) - 1

indices = [early_idx, idx_25, mid_idx, idx_75, last_idx]

for sample_num, idx in enumerate(indices, 1):
    if idx < len(txt_files):
        fpath = txt_files[idx]
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n', 3)
            
            if len(lines) >= 4:
                timestamp = lines[0].replace('Timestamp: ', '').strip()
                speaker = lines[1].replace('Speaker: ', '').strip()
                text = lines[3].strip()
                words = len(text.split())
                
                stichproben.append({
                    'num': sample_num,
                    'idx': idx,
                    'timestamp': timestamp,
                    'speaker': speaker,
                    'text_preview': text[:250],
                    'words': words,
                    'file': fpath.name
                })
                
                print(f"✓ Stichprobe {sample_num}: {timestamp} ({speaker}, {words} Wörter)")
        except Exception as e:
            print(f"✗ Fehler bei Stichprobe {sample_num}: {e}")

# Zeige Stichproben
print("\n" + "="*80)
print("SEMANTISCHE NÄHE - STICHPROBEN (User ↔ AI Paare)")
print("="*80 + "\n")

for sample in stichproben:
    print(f"Stichprobe {sample['num']} ({sample['idx']:,}/{len(txt_files):,})")
    print(f"Datei: {sample['file']}")
    print(f"Timestamp: {sample['timestamp']}")
    print(f"Speaker: {sample['speaker']}")
    print(f"Wörter: {sample['words']}")
    print(f"Text-Ausschnitt: {sample['text_preview']}...")
    print(f"{'-'*80}\n")

# Speichere JSON für später
stichproben_json = Path(r"C:\evoki\backend\stichproben_samples.json")
with open(stichproben_json, 'w', encoding='utf-8') as f:
    json.dump(stichproben, f, indent=2, ensure_ascii=False)

print(f"✓ Stichproben gespeichert: {stichproben_json}")
