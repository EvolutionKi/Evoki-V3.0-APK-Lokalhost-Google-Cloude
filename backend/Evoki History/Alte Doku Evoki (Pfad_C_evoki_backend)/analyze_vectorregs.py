#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  VectorRegs Vollständigkeits-Analyse                                          ║
║  Analysiert die Struktur und Integrität der BRAIN_EVOKI VectorReg-Blöcke     ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import json
from pathlib import Path
from collections import defaultdict

BASE_PATH = Path("C:/evoki/backend/VectorRegs_in_Use/01_BRAIN_EVOKI")

def analyze_vectorreg_block(block_path):
    """Analysiert einen VectorReg-Block auf Vollständigkeit."""
    stats = {
        'total_files': 0,
        'total_size_mb': 0,
        'vectors_count': 0,
        'dimensions': set(),
        'categories': defaultdict(int),
        'errors': [],
        'sample_entries': []
    }
    
    if not block_path.exists():
        stats['errors'].append(f"Pfad existiert nicht: {block_path}")
        return stats
    
    for json_file in block_path.rglob('*.json'):
        stats['total_files'] += 1
        try:
            file_size = json_file.stat().st_size
            stats['total_size_mb'] += file_size / (1024 * 1024)
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Analysiere Struktur
            if 'vector' in data:
                vec = data['vector']
                if isinstance(vec, list):
                    stats['vectors_count'] += 1
                    stats['dimensions'].add(len(vec))
                    
                    # Kategorie aus Pfad extrahieren
                    category = json_file.parent.name
                    stats['categories'][category] += 1
                    
                    # Sample speichern (erste 3)
                    if len(stats['sample_entries']) < 3:
                        stats['sample_entries'].append({
                            'file': json_file.name,
                            'category': category,
                            'text_preview': data.get('text', '')[:100],
                            'dimension': len(vec),
                            'has_metadata': 'metadata' in data
                        })
            else:
                stats['errors'].append(f"Kein 'vector'-Feld in {json_file.name}")
                
        except Exception as e:
            stats['errors'].append(f"{json_file.name}: {str(e)}")
    
    return stats

def main():
    print("=" * 80)
    print("📊 VectorRegs BRAIN_EVOKI Vollständigkeits-Analyse")
    print("=" * 80)
    print()
    
    # Analysiere alle Unterordner
    blocks = [
        'chunk', 'prompt', 'metrik',
        'trajectory_past_5', 'trajectory_past_25',
        'trajectory_future_5', 'trajectory_future_25',
        'causal_past_1', 'causal_past_2',
        'causal_future_1', 'causal_future_2'
    ]
    
    total_stats = {
        'blocks': {},
        'grand_total_files': 0,
        'grand_total_vectors': 0,
        'grand_total_size_mb': 0,
        'all_dimensions': set()
    }
    
    for block_name in blocks:
        block_path = BASE_PATH / block_name
        print(f"🔍 Analysiere Block: {block_name}")
        print(f"   Pfad: {block_path}")
        
        stats = analyze_vectorreg_block(block_path)
        total_stats['blocks'][block_name] = stats
        
        total_stats['grand_total_files'] += stats['total_files']
        total_stats['grand_total_vectors'] += stats['vectors_count']
        total_stats['grand_total_size_mb'] += stats['total_size_mb']
        total_stats['all_dimensions'].update(stats['dimensions'])
        
        print(f"   ✓ Dateien: {stats['total_files']}")
        print(f"   ✓ Vektoren: {stats['vectors_count']}")
        print(f"   ✓ Größe: {stats['total_size_mb']:.2f} MB")
        
        if stats['dimensions']:
            print(f"   ✓ Dimensionen: {', '.join(map(str, sorted(stats['dimensions'])))}")
        
        if stats['errors']:
            print(f"   ⚠️  Fehler: {len(stats['errors'])}")
            for err in stats['errors'][:3]:  # Zeige ersten 3
                print(f"      - {err}")
        
        print()
    
    # Zusammenfassung
    print("=" * 80)
    print("📈 GESAMT-STATISTIK")
    print("=" * 80)
    print(f"Analysierte Blöcke:     {len(total_stats['blocks'])}")
    print(f"Gesamt Dateien:         {total_stats['grand_total_files']:,}")
    print(f"Gesamt Vektoren:        {total_stats['grand_total_vectors']:,}")
    print(f"Gesamt Größe:           {total_stats['grand_total_size_mb']:.2f} MB")
    print(f"Vektor-Dimensionen:     {', '.join(map(str, sorted(total_stats['all_dimensions'])))}")
    print()
    
    # Vollständigkeits-Check
    print("=" * 80)
    print("✅ VOLLSTÄNDIGKEITS-CHECK")
    print("=" * 80)
    
    expected_blocks = set(blocks)
    found_blocks = set(total_stats['blocks'].keys())
    missing_blocks = expected_blocks - found_blocks
    
    if missing_blocks:
        print(f"⚠️  Fehlende Blöcke: {', '.join(missing_blocks)}")
    else:
        print("✓ Alle erwarteten Blöcke vorhanden")
    
    # Prüfe auf leere Blöcke
    empty_blocks = [name for name, stats in total_stats['blocks'].items() if stats['vectors_count'] == 0]
    if empty_blocks:
        print(f"⚠️  Leere Blöcke (0 Vektoren): {', '.join(empty_blocks)}")
    else:
        print("✓ Alle Blöcke enthalten Vektoren")
    
    # Prüfe Dimensions-Konsistenz
    if len(total_stats['all_dimensions']) == 1:
        print(f"✓ Konsistente Vektor-Dimension: {list(total_stats['all_dimensions'])[0]}D")
    elif len(total_stats['all_dimensions']) > 1:
        print(f"⚠️  Inkonsistente Dimensionen gefunden: {sorted(total_stats['all_dimensions'])}")
    
    print()
    
    # Sample-Einträge anzeigen
    print("=" * 80)
    print("📝 BEISPIEL-EINTRÄGE (erste 3)")
    print("=" * 80)
    
    for block_name, stats in total_stats['blocks'].items():
        if stats['sample_entries']:
            for sample in stats['sample_entries'][:1]:  # Zeige 1 pro Block
                print(f"\n[{block_name}] {sample['file']}")
                print(f"  Dimension: {sample['dimension']}D")
                print(f"  Text: {sample['text_preview']}...")
                print(f"  Metadata: {'✓' if sample['has_metadata'] else '✗'}")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
