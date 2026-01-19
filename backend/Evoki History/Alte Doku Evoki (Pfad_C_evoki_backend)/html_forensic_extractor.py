"""
FORENSISCHE EXTRAKTION - Google Takeout MeineAktivitäten.html
==============================================================
Extrahiert ALLE Prompts wissenschaftlich sauber in TXT-Dateien
Struktur: YYYY/MM/DD/Prompt_N_speaker.txt

Keine Kompromisse bei Datenintegrität.
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup
import html as html_module

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forensic_extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== KONFIGURATION ====================
SOURCE_HTML = Path(r"C:\evoki\backend\Google Massenexport 16.10.25\MeineAktivitäten.html")
OUTPUT_BASE = Path(r"C:\evoki\backend\VectorRegs_FORENSIC")
SUMMARY_FILE = OUTPUT_BASE / "extraction_summary.json"
VERIFICATION_FILE = OUTPUT_BASE / "Verifizierung_Wortanzahl.txt"

# ==================== FORENSISCHE EXTRAKTION ====================
def extract_prompts_forensic(html_path: Path) -> List[Dict]:
    """
    Extrahiert Prompts FORENSISCH sauber aus Google Takeout HTML.
    
    Return:
        List[Dict] mit Keys:
        - timestamp: str "DD.MM.YYYY, HH:MM:SS MESZ"
        - speaker: str "user" oder "ai"
        - message: str (HTML-dekodiert, whitespace normalisiert)
        - raw_html: str (original HTML zum Debuggen)
    """
    logger.info(f"[START] Forensische Extraktion: {html_path}")
    logger.info(f"Dateigröße: {html_path.stat().st_size / (1024*1024):.2f} MB")
    
    entries = []
    error_count = 0
    
    try:
        # Parse HTML mit BeautifulSoup
        logger.info("[PARSE] Laden mit BeautifulSoup...")
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
        logger.info("[PARSE] HTML erfolgreich geladen")
        
        # Finde alle outer-cell Blöcke
        blocks = soup.find_all('div', class_='outer-cell')
        logger.info(f"[FOUND] {len(blocks)} outer-cell Blöcke gefunden")
        
        for block_idx, block in enumerate(blocks, 1):
            if block_idx % 500 == 0:
                logger.info(f"[PROGRESS] {block_idx}/{len(blocks)} Blöcke ({100*block_idx/len(blocks):.1f}%)")
            
            try:
                # Extrahiere content-cell
                content_cells = block.find_all('div', class_='content-cell')
                if not content_cells:
                    continue
                
                # Erste content-cell hat Prompt + Timestamp + Response
                for content_cell in content_cells:
                    text = content_cell.get_text(separator='\n', strip=True)
                    
                    # Suche nach "Eingegebener Prompt:"
                    if 'Eingegebener Prompt:' not in text:
                        continue
                    
                    # Split bei "Eingegebener Prompt:"
                    parts = text.split('Eingegebener Prompt:', 1)
                    if len(parts) != 2:
                        continue
                    
                    content = parts[1].strip()
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    
                    if len(lines) < 3:
                        logger.warning(f"Block {block_idx}: Ungültiges Format (zu wenig Zeilen)")
                        error_count += 1
                        continue
                    
                    # Lines[0] = Prompt, Lines[1] = Timestamp, Lines[2:] = Response
                    user_prompt = lines[0]
                    timestamp = lines[1]
                    ai_response = '\n'.join(lines[2:])
                    
                    # Validiere Timestamp
                    if not re.match(r'\d{2}\.\d{2}\.\d{4}, \d{2}:\d{2}:\d{2}', timestamp):
                        logger.warning(f"Block {block_idx}: Ungültiger Timestamp: {timestamp}")
                        error_count += 1
                        continue
                    
                    # HTML-Dekodieren (z.B. &#39; → ')
                    user_prompt = html_module.unescape(user_prompt)
                    ai_response = html_module.unescape(ai_response)
                    
                    # Unicode-Whitespace normalisieren
                    user_prompt = user_prompt.replace('\xa0', ' ').replace('\u00a0', ' ')
                    ai_response = ai_response.replace('\xa0', ' ').replace('\u00a0', ' ')
                    
                    # Füge beide Einträge hinzu (User + AI)
                    entries.append({
                        'timestamp': timestamp,
                        'speaker': 'user',
                        'message': user_prompt,
                        'block_idx': block_idx
                    })
                    
                    entries.append({
                        'timestamp': timestamp,
                        'speaker': 'ai',
                        'message': ai_response,
                        'block_idx': block_idx
                    })
                    
                    break  # Nur erste content-cell mit Prompt verarbeiten
            
            except Exception as e:
                logger.error(f"Block {block_idx}: Fehler - {e}")
                error_count += 1
                continue
        
        logger.info(f"[ERFOLG] {len(entries)} Einträge extrahiert ({error_count} Fehler)")
        return entries
    
    except Exception as e:
        logger.error(f"[FEHLER] Kritischer Fehler: {e}")
        raise

def sort_by_timestamp(entries: List[Dict]) -> List[Dict]:
    """Sortiert Einträge chronologisch nach Timestamp."""
    def parse_ts(entry):
        try:
            ts = entry['timestamp'].split(' MESZ')[0].split(' MEZ')[0].strip()
            return datetime.strptime(ts, '%d.%m.%Y, %H:%M:%S')
        except:
            return datetime.min
    
    sorted_entries = sorted(entries, key=parse_ts)
    logger.info(f"[SORT] Chronologisch sortiert")
    return sorted_entries

def write_txt_files(entries: List[Dict], output_base: Path) -> Dict:
    """
    Schreibt TXT-Dateien in Struktur YYYY/MM/DD/Prompt_N_speaker.txt
    
    Return:
        Dict mit Statistiken
    """
    output_base.mkdir(parents=True, exist_ok=True)
    
    stats = {
        'total_entries': len(entries),
        'total_files': 0,
        'total_words': 0,
        'by_date': {},
        'errors': 0
    }
    
    # Gruppiere nach Datum
    by_date = {}
    for entry in entries:
        try:
            ts = entry['timestamp'].split(' MESZ')[0].split(' MEZ')[0].strip()
            date_obj = datetime.strptime(ts, '%d.%m.%Y, %H:%M:%S')
            date_key = date_obj.strftime('%Y-%m-%d')
            
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append(entry)
        except Exception as e:
            logger.warning(f"Datum-Parse-Fehler: {entry['timestamp']}")
            stats['errors'] += 1
    
    # Schreibe Dateien
    for date_str in sorted(by_date.keys()):
        date_entries = by_date[date_str]
        
        # Erstelle Ordner YYYY/MM/DD
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        folder = output_base / date_obj.strftime('%Y') / date_obj.strftime('%m') / date_obj.strftime('%d')
        folder.mkdir(parents=True, exist_ok=True)
        
        # Gruppiere User + AI Paare
        prompt_num = 1
        for entry in date_entries:
            filename = folder / f"Prompt{prompt_num}_{entry['speaker']}.txt"
            
            # Schreibe Header + Content
            content = f"Timestamp: {entry['timestamp']}\nSpeaker: {entry['speaker']}\n\n{entry['message']}"
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                words = len(entry['message'].split())
                stats['total_words'] += words
                stats['total_files'] += 1
                
                if date_str not in stats['by_date']:
                    stats['by_date'][date_str] = {'files': 0, 'words': 0}
                stats['by_date'][date_str]['files'] += 1
                stats['by_date'][date_str]['words'] += words
                
            except Exception as e:
                logger.error(f"Schreib-Fehler {filename}: {e}")
                stats['errors'] += 1
            
            # Erhöhe Prompt-Nummer bei User-Einträgen
            if entry['speaker'] == 'ai':
                prompt_num += 1
    
    logger.info(f"[WRITE] {stats['total_files']} TXT-Dateien geschrieben")
    logger.info(f"[WORDS] {stats['total_words']:,} Wörter insgesamt")
    
    return stats

def write_summary(stats: Dict, output_base: Path):
    """Schreibt Zusammenfassungs-JSON und Verifizierung."""
    
    # Summary JSON
    summary = {
        'source': str(SOURCE_HTML),
        'extraction_time': datetime.now().isoformat(),
        'total_entries': stats['total_entries'],
        'total_files': stats['total_files'],
        'total_words': stats['total_words'],
        'dates': sorted(stats['by_date'].keys()),
        'errors': stats['errors'],
        'by_date': stats['by_date']
    }
    
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    logger.info(f"[SUMMARY] Gespeichert: {SUMMARY_FILE}")
    
    # Verifizierung
    with open(VERIFICATION_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Quelle: {SOURCE_HTML}\n")
        f.write(f"Extraktions-Zeit: {datetime.now().isoformat()}\n")
        f.write(f"Gesamt-Einträge: {stats['total_entries']}\n")
        f.write(f"Gesamt-Dateien: {stats['total_files']}\n")
        f.write(f"Gesamt-Wörter: {stats['total_words']:,}\n")
        f.write(f"Fehler: {stats['errors']}\n")
        f.write(f"Datums-Bereich: {sorted(stats['by_date'].keys())[0]} bis {sorted(stats['by_date'].keys())[-1]}\n")
        f.write(f"\n[OK] Forensische Extraktion abgeschlossen\n")
    
    logger.info(f"[VERIFY] Gespeichert: {VERIFICATION_FILE}")

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("FORENSISCHE EXTRAKTION - Google Takeout")
    logger.info("=" * 80)
    
    try:
        # 1. Extrahiere
        entries = extract_prompts_forensic(SOURCE_HTML)
        
        # 2. Sortiere
        entries = sort_by_timestamp(entries)
        
        # 3. Schreibe TXT-Dateien
        stats = write_txt_files(entries, OUTPUT_BASE)
        
        # 4. Schreibe Zusammenfassung
        write_summary(stats, OUTPUT_BASE)
        
        logger.info("\n" + "=" * 80)
        logger.info("EXTRAKTION ABGESCHLOSSEN")
        logger.info("=" * 80)
        logger.info(f"Output-Verzeichnis: {OUTPUT_BASE}")
        logger.info(f"Gesamt Einträge: {stats['total_entries']}")
        logger.info(f"Gesamt Dateien: {stats['total_files']}")
        logger.info(f"Gesamt Wörter: {stats['total_words']:,}")
        logger.info(f"Fehler: {stats['errors']}")
        
    except Exception as e:
        logger.error(f"[KRITISCH] {e}")
        raise
