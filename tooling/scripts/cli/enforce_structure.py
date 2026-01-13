#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Directory Structure Enforcer - Evoki V3.0
==========================================
Automatisches Tool zur Durchsetzung der Datenmanagement-Regeln:

1. Keine gemischten Verzeichnisse (nur Dateien ODER nur Ordner)
2. README.md in jedem Ordner aktuell halten
3. Automatische Sortierung bei Verstößen

Verwendung:
    python enforce_structure.py check      # Nur prüfen
    python enforce_structure.py fix        # Prüfen und beheben
    python enforce_structure.py readme     # README.md Dateien generieren
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional

# V3.0 Root
V3_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")

# Ausnahmen laut datamanagement.md
ROOT_EXCEPTIONS = {"README.md", "ARCHITECTURE.txt", ".geminiignore"}
TEMPLE_EXCEPTIONS = {"main.py", "pyproject.toml", "requirements.txt", "__init__.py"}

# Ordner die komplett ignoriert werden (inkl. Strukturprüfung)
IGNORED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", ".vscode"}

# Ordner mit erlaubter gemischter Struktur (Standard-Projektstrukturen)
MIXED_ALLOWED = {
    ".github",           # GitHub standard: workflows/ + config files
    "interface",         # Vite/React: src/, public/ + config files
    "src",               # Standard src dir mit components/ + entry files
    "dashboard",         # Dashboard: templates/ + server.py
    "status",            # Synapse: backups/ + JSON status files
}


class DirectoryEnforcer:
    """Nico: Dieses Tool sorgt dafür, dass die Ordnerstruktur sauber bleibt."""
    
    def __init__(self, root: Path):
        self.root = root
        self.violations: List[Dict] = []
        self.fixes_applied: List[Dict] = []
    
    def check_directory(self, path: Path, depth: int = 0) -> Tuple[int, int]:
        """Prüft ein Verzeichnis auf Verstöße.
        
        Returns:
            Tuple[files_count, dirs_count]
        """
        if not path.is_dir():
            return (0, 0)
        
        # Ignorierte Ordner überspringen
        if path.name in IGNORED_DIRS:
            return (0, 0)
        
        files = []
        dirs = []
        
        for item in path.iterdir():
            if item.name in IGNORED_DIRS:
                continue
            if item.is_file():
                files.append(item.name)
            elif item.is_dir():
                dirs.append(item.name)
        
        # Ausnahmen prüfen
        is_root = path == self.root
        is_temple = path.name == "temple" and path.parent.name == "app"
        
        allowed_files = set()
        if is_root:
            allowed_files = ROOT_EXCEPTIONS
        elif is_temple:
            allowed_files = TEMPLE_EXCEPTIONS
        
        # Filtere erlaubte Dateien
        files_filtered = [f for f in files if f not in allowed_files]
        
        # Gemischtes Verzeichnis erkennen (außer erlaubte Strukturen)
        if files_filtered and dirs and path.name not in MIXED_ALLOWED:
            self.violations.append({
                "path": str(path.relative_to(self.root)),
                "type": "MIXED_DIRECTORY",
                "files": files_filtered,
                "dirs": dirs,
                "severity": "WARNING"
            })
        
        # Rekursiv prüfen
        for d in dirs:
            self.check_directory(path / d, depth + 1)
        
        return (len(files), len(dirs))
    
    def check_all(self) -> List[Dict]:
        """Prüft die gesamte Struktur."""
        print(f"🔍 Prüfe Verzeichnisstruktur: {self.root}")
        print()
        
        self.violations = []
        self.check_directory(self.root)
        
        if not self.violations:
            print("✅ Keine Verstöße gefunden!")
        else:
            print(f"⚠️  {len(self.violations)} Verstoß/Verstöße gefunden:\n")
            for v in self.violations:
                print(f"  📁 {v['path']}")
                print(f"     Typ: {v['type']}")
                print(f"     Dateien: {', '.join(v['files'][:5])}{'...' if len(v['files']) > 5 else ''}")
                print(f"     Ordner: {', '.join(v['dirs'][:5])}{'...' if len(v['dirs']) > 5 else ''}")
                print()
        
        return self.violations
    
    def fix_violations(self) -> List[Dict]:
        """Behebt gefundene Verstöße automatisch."""
        if not self.violations:
            self.check_all()
        
        if not self.violations:
            return []
        
        print("\n🔧 Behebe Verstöße...\n")
        
        for v in self.violations:
            if v["type"] == "MIXED_DIRECTORY":
                self._fix_mixed_directory(v)
        
        return self.fixes_applied
    
    def _fix_mixed_directory(self, violation: Dict):
        """Behebt ein gemischtes Verzeichnis.
        
        Strategie: Log-Dateien in logs/ verschieben
        """
        path = self.root / violation["path"]
        
        for filename in violation["files"]:
            file_path = path / filename
            
            # Log-Dateien → logs/ Unterordner
            if filename.endswith(".log"):
                logs_dir = path / "logs"
                logs_dir.mkdir(exist_ok=True)
                new_path = logs_dir / filename
                
                print(f"  📦 Verschiebe: {filename} → logs/{filename}")
                file_path.rename(new_path)
                
                self.fixes_applied.append({
                    "action": "MOVE",
                    "from": str(file_path.relative_to(self.root)),
                    "to": str(new_path.relative_to(self.root)),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            # test_*.txt Dateien löschen
            elif filename.startswith("test_") and filename.endswith(".txt"):
                print(f"  🗑️  Lösche Test-Datei: {filename}")
                file_path.unlink()
                
                self.fixes_applied.append({
                    "action": "DELETE",
                    "file": str(file_path.relative_to(self.root)),
                    "reason": "test file",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
    def generate_readme(self, path: Path) -> str:
        """Generiert README.md Inhalt für einen Ordner."""
        rel_path = path.relative_to(self.root)
        
        files = []
        dirs = []
        
        for item in path.iterdir():
            if item.name in IGNORED_DIRS or item.name == "README.md":
                continue
            if item.is_file():
                files.append(item.name)
            elif item.is_dir():
                dirs.append(item.name)
        
        # Header
        content = f"# {path.name}\n\n"
        content += f"**Pfad:** `{rel_path}`\n\n"
        content += f"*Automatisch generiert am {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        
        # Inhalt
        if dirs:
            content += "## Unterordner\n\n"
            for d in sorted(dirs):
                content += f"- 📁 `{d}/`\n"
            content += "\n"
        
        if files:
            content += "## Dateien\n\n"
            for f in sorted(files):
                content += f"- 📄 `{f}`\n"
            content += "\n"
        
        return content
    
    def update_readmes(self, start_path: Optional[Path] = None):
        """Aktualisiert README.md in allen Ordnern."""
        if start_path is None:
            start_path = self.root / "tooling"
        
        print(f"📝 Aktualisiere README.md Dateien in: {start_path.relative_to(self.root)}")
        
        updated = 0
        for dirpath in start_path.rglob("*"):
            if not dirpath.is_dir():
                continue
            if any(part in IGNORED_DIRS for part in dirpath.parts):
                continue
            
            readme_path = dirpath / "README.md"
            content = self.generate_readme(dirpath)
            
            # Nur schreiben wenn Inhalt sinnvoll
            if "## Unterordner" in content or "## Dateien" in content:
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(content)
                updated += 1
                print(f"  ✅ {readme_path.relative_to(self.root)}")
        
        print(f"\n📊 {updated} README.md Dateien aktualisiert")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    enforcer = DirectoryEnforcer(V3_ROOT)
    
    if command == "check":
        violations = enforcer.check_all()
        sys.exit(1 if violations else 0)
    
    elif command == "fix":
        enforcer.fix_violations()
        if enforcer.fixes_applied:
            print(f"\n✅ {len(enforcer.fixes_applied)} Fixes angewendet")
            # Verifiziere
            enforcer.violations = []
            remaining = enforcer.check_all()
            if remaining:
                print(f"\n⚠️  Noch {len(remaining)} Verstöße übrig")
        else:
            print("\n✅ Keine Fixes nötig")
    
    elif command == "readme":
        enforcer.update_readmes()
    
    else:
        print(f"❌ Unbekannter Befehl: {command}")
        print("Verwendung: check | fix | readme")
        sys.exit(1)


if __name__ == "__main__":
    main()
