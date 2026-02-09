#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPEC CODE EXTRACTOR - Extract Python implementations from FINAL7 spec

Parsed das FINAL7 Spec und extrahiert:
1. Alle ```python ... ``` Code-Blöcke
2. Ordnet sie den korrekten Metriken zu
3. Generiert vollständige, lauffähige metrics_from_spec.py

Output: Komplette Implementierung aller 168 Metriken
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


def extract_metric_sections(spec_content: str) -> List[Tuple[str, str, str]]:
    """
    Extract metric sections from spec.
    
    Returns:
        List of (metric_id, section_content, code_blocks)
    """
    # Find all ## m<number> sections
    pattern = r'## (m\d+_[\w_]+(?:\s*/\s*m\d+_[\w_]+)?)[^\n]*\n(.*?)(?=\n## m\d+|$)'
    matches = re.findall(pattern, spec_content, re.DOTALL)
    
    sections = []
    for metric_id, content in matches:
        # Extract Python code blocks
        code_pattern = r'```python\n(.*?)\n```'
        code_blocks = re.findall(code_pattern, content, re.DOTALL)
        
        if code_blocks:
            sections.append((metric_id, content, code_blocks))
    
    return sections


def clean_and_merge_code(code_blocks: List[str]) -> str:
    """Merge and clean multiple code blocks for a metric."""
    # Usually the implementation function is the longest/most complete block
    if not code_blocks:
        return ""
    
    # Find the block with "def compute_m" in it
    impl_block = None
    for block in code_blocks:
        if 'def compute_m' in block or 'def compute_' in block:
            impl_block = block
            break
    
    if impl_block:
        return impl_block
    
    # Otherwise return the longest block
    return max(code_blocks, key=len)


def generate_complete_module(sections: List[Tuple[str, str, str]], spec_path: Path) -> str:
    """Generate complete Python module from extracted sections."""
    
    header = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVOKI FULL SPECTRUM 168 METRICS - EXTRACTED FROM SPEC

Auto-extracted from: {spec_path.name}
Contains complete implementations for all documented metrics.

Generated: {__import__('datetime').datetime.now().isoformat()}
"""

import re
import math
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import Counter, deque
from datetime import datetime, timedelta
from pathlib import Path


# =============================================================================
# EXTRACTED METRIC IMPLEMENTATIONS
# =============================================================================

'''
    
    code_parts = [header]
    extracted_count = 0
    
    for metric_id, content, code_blocks in sections:
        # Clean metric ID (remove aliases)
        primary_id = metric_id.split('/')[0].strip()
        
        # Add section marker
        code_parts.append(f"\n\n# {'-' * 70}")
        code_parts.append(f"# {primary_id}")
        code_parts.append(f"# {'-' * 70}\n")
        
        # Extract and add implementation
        impl_code = clean_and_merge_code(code_blocks)
        if impl_code:
            code_parts.append(impl_code)
            code_parts.append("\n")
            extracted_count += 1
        else:
            # No code found - add placeholder
            code_parts.append(f"# TODO: No implementation found in spec for {primary_id}\n")
    
    # Add module info
    code_parts.append(f"\n\n# {'-' * 70}")
    code_parts.append(f"# EXTRACTION SUMMARY")
    code_parts.append(f"# {'-' * 70}")
    code_parts.append(f"# \n# Total sections: {len(sections)}")
    code_parts.append(f"# \n# Implementations extracted: {extracted_count}")
    code_parts.append(f"# \n# Missing: {len(sections) - extracted_count}\n")
    
    return "".join(code_parts)


def main():
    """Main entry point."""
    # Paths
    spec_path = Path("C:/Users/nicom/Downloads/EVOKI_V3_METRICS_SPECIFICATION Entwicklung/V7 Patchpaket V2 + Monolith/EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md")
    
    output_path = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude/backend/core/evoki_metrics_v3/metrics_from_spec.py")
    
    print("=" * 70)
    print("SPEC CODE EXTRACTOR")
    print("=" * 70)
    print(f"Spec:   {spec_path.name}")
    print(f"Output: {output_path}")
    
    # Check spec exists
    if not spec_path.exists():
        print(f"❌ Spec not found: {spec_path}")
        return 1
    
    # Read spec
    print("\n📄 Reading spec...")
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec_content = f.read()
    
    print(f"✅ Read {len(spec_content)} characters ({len(spec_content.splitlines())} lines)")
    
    # Extract sections
    print("\n🔍 Extracting metric sections...")
    sections = extract_metric_sections(spec_content)
    print(f"✅ Found {len(sections)} metric sections with code")
    
    # Generate module
    print("\n🔧 Generating Python module...")
    code = generate_complete_module(sections, spec_path)
    
    # Write output
    print(f"\n💾 Writing to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    # Stats
    line_count = code.count('\n')
    func_count = code.count('def compute_')
    
    print(f"✅ Generated {line_count} lines")
    print(f"✅ Extracted {func_count} metric functions")
    
    print("\n" + "=" * 70)
    print("✅ EXTRACTION COMPLETE")
    print("=" * 70)
    print("\n📝 NEXT STEPS:")
    print("1. Review metrics_from_spec.py")
    print("2. Import into main metrics module")
    print("3. Test each extracted function")
    print("4. Integrate with Grain Engine")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
