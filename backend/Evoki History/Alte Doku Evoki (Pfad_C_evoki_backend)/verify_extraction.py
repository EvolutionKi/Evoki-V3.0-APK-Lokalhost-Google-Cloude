"""
EVOKI DATEN-VERIFIKATION - Wortgenaue Zählung
==============================================
Zählt Wörter in allen exportierten TXT-Dateien und vergleicht mit Ursprungsdaten.
Identisch zur Methode in Verifizierung_Wortanzahl.txt
"""

import re
from pathlib import Path
from collections import defaultdict
import html

# ==================== CONFIGURATION ====================
EXPORT_DIR = Path(r"C:\evoki\backend\VectorRegs_TXT_Export")
OUTPUT_FILE = Path(r"C:\evoki\backend\Verifizierung_Export_Neu.txt")

# ==================== WORD COUNTING ====================
def count_words(text: str) -> int:
    """
    Zählt Wörter exakt wie im Original.
    - HTML entities dekodieren
    - Whitespace normalisieren
    - Nach Whitespace splitten
    """
    # HTML entities dekodieren
    text = html.unescape(text)
    
    # Whitespace normalisieren und splitten
    words = text.split()
    
    return len(words)

def parse_file(file_path: Path) -> str:
    """Liest Datei und extrahiert Content (ohne Header)."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # HTML entities dekodieren
        content = html.unescape(content)
        
        # Header entfernen (alles nach ===)
        if '===' in content:
            parts = content.split('===', 1)
            if len(parts) == 2:
                return parts[1].strip()
        
        # Fallback: erste 2 Zeilen überspringen
        lines = content.split('\n')
        if len(lines) > 2:
            return '\n'.join(lines[2:]).strip()
        
        return ""
        
    except Exception as e:
        print(f"FEHLER beim Lesen {file_path}: {e}")
        return ""

# ==================== MAIN VERIFICATION ====================
def verify_extraction():
    """Hauptfunktion für Daten-Verifikation."""
    
    print("=" * 80)
    print("EVOKI DATEN-VERIFIKATION")
    print("=" * 80)
    print(f"Export-Verzeichnis: {EXPORT_DIR}")
    print()
    
    # Sammle alle Dateien
    user_files = sorted(EXPORT_DIR.rglob("*_user.txt"))
    ai_files = sorted(EXPORT_DIR.rglob("*_ai.txt"))
    
    print(f"Gefundene USER-Dateien: {len(user_files)}")
    print(f"Gefundene AI-Dateien:   {len(ai_files)}")
    print(f"Fehlende AI-Dateien:    {len(user_files) - len(ai_files)}")
    print()
    
    # Zähle Wörter
    print("Zähle Wörter in USER-Dateien...")
    user_words = 0
    user_empty = 0
    
    for i, file in enumerate(user_files, 1):
        content = parse_file(file)
        words = count_words(content)
        user_words += words
        
        if words == 0:
            user_empty += 1
        
        if i % 1000 == 0:
            print(f"  {i}/{len(user_files)} verarbeitet... ({user_words:,} Wörter)")
    
    print(f"✓ USER-Dateien: {user_words:,} Wörter ({user_empty} leere Dateien)")
    print()
    
    print("Zähle Wörter in AI-Dateien...")
    ai_words = 0
    ai_empty = 0
    
    for i, file in enumerate(ai_files, 1):
        content = parse_file(file)
        words = count_words(content)
        ai_words += words
        
        if words == 0:
            ai_empty += 1
        
        if i % 1000 == 0:
            print(f"  {i}/{len(ai_files)} verarbeitet... ({ai_words:,} Wörter)")
    
    print(f"✓ AI-Dateien:   {ai_words:,} Wörter ({ai_empty} leere Dateien)")
    print()
    
    # Gesamtstatistik
    total_words = user_words + ai_words
    total_files = len(user_files) + len(ai_files)
    
    print("=" * 80)
    print("STATISTIK")
    print("=" * 80)
    print(f"Gesamt-Dateien:        {total_files:,}")
    print(f"  - USER-Dateien:      {len(user_files):,}")
    print(f"  - AI-Dateien:        {len(ai_files):,}")
    print(f"  - Fehlende AI:       {len(user_files) - len(ai_files):,}")
    print()
    print(f"Gesamt-Wörter:         {total_words:,}")
    print(f"  - USER-Wörter:       {user_words:,}")
    print(f"  - AI-Wörter:         {ai_words:,}")
    print()
    print(f"Leere Dateien:")
    print(f"  - USER leer:         {user_empty}")
    print(f"  - AI leer:           {ai_empty}")
    print()
    
    # Vergleich mit Original (wenn vorhanden)
    original_verification = Path(r"C:\evoki\backend\Master Massenexport Extraktor\Verifizierung_Wortanzahl.txt")
    if original_verification.exists():
        try:
            with open(original_verification, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrahiere ursprüngliche Wortzahl
            match = re.search(r'Wörter Ursprungsdaten:\s*(\d+)', content)
            if match:
                original_words = int(match.group(1))
                print(f"Vergleich mit Original-Extraktion:")
                print(f"  - Original:          {original_words:,} Wörter")
                print(f"  - Aktueller Export:  {total_words:,} Wörter")
                print(f"  - Differenz:         {total_words - original_words:,} Wörter")
                print(f"  - Verhältnis:        {total_words / original_words:.5f}")
                
                if abs(total_words - original_words) < 100:
                    print(f"\n✓✓✓ [OK] Export ist lückenlos! ✓✓✓")
                else:
                    print(f"\n⚠⚠⚠ [WARNUNG] Export weicht vom Original ab! ⚠⚠⚠")
        except Exception as e:
            print(f"Konnte Original-Verifizierung nicht lesen: {e}")
    
    print("=" * 80)
    
    # Schreibe Ergebnis
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Wörter exportiert (USER): {user_words}\n")
        f.write(f"Wörter exportiert (AI): {ai_words}\n")
        f.write(f"Wörter exportiert (alle): {total_words}\n")
        f.write(f"USER-Dateien: {len(user_files)}\n")
        f.write(f"AI-Dateien: {len(ai_files)}\n")
        f.write(f"Fehlende AI-Dateien: {len(user_files) - len(ai_files)}\n")
        f.write(f"Leere USER-Dateien: {user_empty}\n")
        f.write(f"Leere AI-Dateien: {ai_empty}\n")
        
        if original_verification.exists():
            try:
                with open(original_verification, 'r', encoding='utf-8') as orig:
                    content = orig.read()
                match = re.search(r'Wörter Ursprungsdaten:\s*(\d+)', content)
                if match:
                    original_words = int(match.group(1))
                    f.write(f"Wörter Ursprungsdaten: {original_words}\n")
                    f.write(f"Verhältnis Export/Original: {total_words / original_words:.5f}\n")
                    
                    if abs(total_words - original_words) < 100:
                        f.write(f"[OK] Lückenlose Extraktion!\n")
                    else:
                        f.write(f"[WARNUNG] Export weicht ab!\n")
            except:
                pass
    
    print(f"\nErgebnis gespeichert: {OUTPUT_FILE}")
    print()

if __name__ == "__main__":
    verify_extraction()
