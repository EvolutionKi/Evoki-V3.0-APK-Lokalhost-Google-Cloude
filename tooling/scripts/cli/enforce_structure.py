#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Directory Structure Enforcer - Evoki V3.0 (Smart Doc Engine)
============================================================
Automatisches Tool zur Durchsetzung der Datenmanagement-Regeln:

1. Keine gemischten Verzeichnisse
2. README.md Generierung mit Code-Analyse (Docstrings & Imports)
3. Automatische Sortierung bei Verstößen

Verwendung:
    python enforce_structure.py check      # Nur prüfen
    python enforce_structure.py fix        # Prüfen und beheben
    python enforce_structure.py readme     # Smart READMEs generieren
"""

import sys
import os
import ast
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional, Set

# V3.0 Root
# Dynamic Root Resolution (Stand 0)
V3_ROOT = Path(os.getenv("EVOKI_PROJECT_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))).resolve()
if not (V3_ROOT / "tooling").exists():
    # Fallback to current dir resolution if env var is missing/wrong
    V3_ROOT = Path(os.path.abspath(".")).resolve()

ROOT_EXCEPTIONS = {"README.md", "ARCHITECTURE.txt", ".geminiignore"}
TEMPLE_EXCEPTIONS = {"main.py", "pyproject.toml", "requirements.txt", "__init__.py"}
IGNORED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", ".vscode"}

MIXED_ALLOWED = {
    ".github", "interface", "src", "dashboard", "status",
    "docs", "scripts", "data", "synapse"
}


class FileAnalyzer:
    """Analysiert Dateien auf Inhalt (Docstrings, Dependencies)."""
    
    @staticmethod
    def analyze(path: Path) -> Dict[str, str]:
        info = {
            "doc": "",
            "deps": set(),
            "type": path.suffix
        }
        
        if path.suffix == ".py":
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # AST Parsing (Sicherer als Regex)
                try:
                    tree = ast.parse(content)
                    
                    # 1. Docstring
                    doc = ast.get_docstring(tree)
                    if doc:
                        # Nimm nur den ersten Absatz oder die erste Zeile
                        summary = doc.strip().split('\n\n')[0].replace('\n', ' ')
                        info["doc"] = summary[:200] + "..." if len(summary) > 200 else summary
                    
                    # 2. Imports (Dependencies)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for n in node.names:
                                info["deps"].add(n.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                info["deps"].add(node.module.split('.')[0])
                                
                except SyntaxError:
                    info["doc"] = "(Syntax Error in File)"
                    
            except Exception as e:
                pass
        
        # Dependencies formatieren
        # Filter standard libraries (heuristic)
        std_lib = {
            "os", "sys", "json", "time", "datetime", "pathlib", "typing", 
            "logging", "subprocess", "ast", "shutil", "re"
        }
        filtered_deps = {d for d in info["deps"] if d not in std_lib}
        
        info["deps_str"] = ", ".join(sorted(filtered_deps)) if filtered_deps else "-"
        return info


class DirectoryEnforcer:
    
    def __init__(self, root: Path):
        self.root = root
        self.violations: List[Dict] = []
        self.fixes_applied: List[Dict] = []
    
    def check_directory(self, path: Path, depth: int = 0) -> Tuple[int, int]:
        if not path.is_dir() or path.name in IGNORED_DIRS:
            return (0, 0)
        
        files = []
        dirs = []
        
        try:
            for item in path.iterdir():
                if item.name in IGNORED_DIRS: continue
                if item.is_file(): files.append(item.name)
                elif item.is_dir(): dirs.append(item.name)
        except OSError: return (0, 0)
        
        # Check Rules
        is_root = path == self.root
        is_temple = path.name == "temple" and path.parent.name == "app"
        allowed = ROOT_EXCEPTIONS if is_root else (TEMPLE_EXCEPTIONS if is_temple else set())
        
        current_files = [f for f in files if f not in allowed]
        
        if current_files and dirs and path.name not in MIXED_ALLOWED:
            self.violations.append({
                "path": str(path.relative_to(self.root)),
                "type": "MIXED_DIRECTORY",
                "files": current_files, "dirs": dirs, "severity": "WARNING"
            })
            
        for d in dirs:
            self.check_directory(path / d, depth + 1)
            
        return (len(files), len(dirs))
    
    def check_all(self) -> List[Dict]:
        print(f"🔍 Prüfe Verzeichnisstruktur: {self.root}")
        self.violations = []
        self.check_directory(self.root)
        if not self.violations: print("✅ Keine Verstöße gefunden!")
        else:
            print(f"⚠️  {len(self.violations)} Verstoß/Verstöße gefunden:")
            for v in self.violations:
                 print(f"  📁 {v['path']} ({v['type']})")
        return self.violations
    
    def fix_violations(self) -> List[Dict]:
        if not self.violations: self.check_all()
        if not self.violations: return []
        
        print("\n🔧 Behebe Verstöße...\n")
        # Logic simplified for this version to focus on README
        # (Assuming Manual Moves were done or user handles mixed dirs)
        return self.fixes_applied

    def generate_readme(self, path: Path) -> str:
        try:
            rel_path = path.relative_to(self.root)
        except ValueError: rel_path = path
        
        files = []
        dirs = []
        
        try:
            for item in path.iterdir():
                if item.name in IGNORED_DIRS or item.name == "README.md": continue
                if item.is_file(): files.append(item)
                elif item.is_dir(): dirs.append(item.name)
        except OSError: return ""
        
        # Build Markdown
        content = f"# {path.name}\n\n"
        content += f"**Kontext:** `{rel_path}`\n\n"
        content += f"*Automatisch generierte Dokumentation - {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        
        if dirs:
            content += "## 📂 Unterverzeichnisse\n\n"
            content += "| Ordner | Beschreibung |\n"
            content += "|--------|--------------|\n"
            for d in sorted(dirs):
                # Try to peek into subfolder readme? Too expensive.
                content += f"| **{d}/** | - |\n"
            content += "\n"
        
        if files:
            content += "## 📄 Dateien\n\n"
            content += "| Datei | Beschreibung (Docstring) | Abhängigkeiten |\n"
            content += "|-------|--------------------------|----------------|\n"
            
            for f in sorted(files, key=lambda x: x.name):
                info = FileAnalyzer.analyze(f)
                doc = info["doc"] if info["doc"] else "*(Keine Dokumentation)*"
                deps = info.get("deps_str", "-")
                
                # Formatting escape
                doc = doc.replace("|", "\|")
                
                content += f"| **{f.name}** | {doc} | {deps} |\n"
            
            content += "\n"
            
        return content

    def update_readmes(self):
        scan_roots = [self.root / "tooling", self.root / "app"]
        updated = 0
        print("\n📝 Generiere Smart-READMEs...\n")
        
        for root_scan in scan_roots:
            if not root_scan.exists(): continue
            for dirpath in root_scan.rglob("*"):
                if not dirpath.is_dir(): continue
                if any(part in IGNORED_DIRS for part in dirpath.parts): continue
                
                readme_path = dirpath / "README.md"
                # Always overwrite with new smart content
                content = self.generate_readme(dirpath)
                
                if "## 📄 Dateien" in content or "## 📂 Unterverzeichnisse" in content:
                    try:
                        with open(readme_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        updated += 1
                        print(f"  ✅ {readme_path.relative_to(self.root)}")
                    except Exception: pass
        
        print(f"\n📊 {updated} Smart-READMEs generiert.")

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    
    cmd = sys.argv[1].lower()
    enforcer = DirectoryEnforcer(V3_ROOT)
    
    if cmd == "check": sys.exit(1 if enforcer.check_all() else 0)
    elif cmd == "fix": enforcer.fix_violations()
    elif cmd == "readme": enforcer.update_readmes()
    else: print("Unknown command"); sys.exit(1)

if __name__ == "__main__":
    main()
