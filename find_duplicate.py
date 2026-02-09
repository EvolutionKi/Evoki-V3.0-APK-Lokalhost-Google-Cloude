#!/usr/bin/env python3
"""Find duplicate metric IDs in contract"""
import json

contract = json.load(open('evoki_fullspectrum168_contract.json', encoding='utf-8'))

ids = [m['id'] for m in contract['metrics']]
names = [m['name'] for m in contract['metrics']]

print(f"Total metrics: {len(ids)}")
print(f"Unique IDs: {len(set(ids))}")
print(f"Unique names: {len(set(names))}")

# Find duplicates
from collections import Counter
id_counts = Counter(ids)
duplicates = {k: v for k, v in id_counts.items() if v > 1}

if duplicates:
    print(f"\n🚨 DUPLICATE IDs found:")
    for id_num, count in duplicates.items():
        print(f"  ID {id_num}: appears {count} times")
        # Show which names have this ID
        dupe_metrics = [m for m in contract['metrics'] if m['id'] == id_num]
        for m in dupe_metrics:
            print(f"    - {m['name']} (function: {m['source']['function']})")
else:
    print("\n✅ No duplicate IDs")

# Check for missing IDs
all_ids = set(range(1, 169))
present_ids = set(ids)
missing = all_ids - present_ids

if missing:
    print(f"\n⚠️  MISSING IDs: {sorted(missing)}")
else:
    print("\n✅ All IDs 1-168 present")

#Missing m100
if 100 in present_ids:
    print("\n✅ m100 present")
else:
    print("\n⚠️  m100 MISSING (gap between m99 and m101!)")
