"""
FORENSISCHE EXTRAKTION v2 - REGEX + STREAMING
================================================
Schneller & präziser Parser für Google Takeout HTML
Extrahiert ALLE Prompts forensisch sauber

Pattern:
  Eingegebener Prompt: [TEXT]<br>
  [DD.MM.YYYY, HH:MM:SS MESZ/MEZ]<br>
  [AI RESPONSE HTML]
  <br></div>...Eingegebener Prompt: [NEXT USER]
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import html as html_module

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forensic_extraction_v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== KONFIGURATION ====================
SOURCE_HTML = Path(r"C:\evoki\backend\Google Massenexport 16.10.25\MeineAktivitäten.html")
OUTPUT_BASE = Path(r"C:\evoki\backend\VectorRegs_FORENSIC")
SUMMARY_FILE = OUTPUT_BASE / "extraction_summary.json"
VERIFICATION_FILE = OUTPUT_BASE / "Verifizierung_Wortanzahl.txt"

# ==================== FORENSISCHE EXTRAKTION - REGEX VERSION ====================
def extract_prompts_regex(html_path: Path) -> List[Dict]:
    """
    Extrahiert Prompts mit REGEX (SCHNELL!) aus Google Takeout HTML.
    
    Pattern:
      Eingegebener Prompt: [TEXT]<br[^>]*>(\d{2}\.\d{2}\.\d{4}, \d{2}:\d{2}:\d{2} [A-Z]+)<br[^>]*>(.+?)(?=<br></div>.*?Eingegebener Prompt:|</body>)
    """
    logger.info(f"[START] Forensische Extraktion v2 (REGEX): {html_path}")
    logger.info(f"Dateigröße: {html_path.stat().st_size / (1024*1024):.2f} MB")
    
    entries = []
    
    try:
        # Lese KOMPLETTE Datei (für Regex brauchen wir den vollständigen Text)
        logger.info("[LOAD] Lade HTML-Datei...")
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        logger.info(f"[LOADED] {len(html_content):,} Zeichen geladen")
        
        # Ersetze <br> mit Newline für Pattern-Matching
        html_content = html_content.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        
        # Entferne die meisten HTML-Tags (außer Struktur)
        html_clean = re.sub(r'<[^>]+?>', ' ', html_content)
        
        # HAUPTPATTERN: Finde alle "Eingegebener Prompt:" Blöcke
        # Pattern: "Eingegebener Prompt: [Text]\n[TIMESTAMP]\n[RESPONSE bis zur nächsten Eingegebener Prompt oder Ende]"
        pattern = r'Eingegebener Prompt:\s*([^\n]+)\n(\d{2}\.\d{2}\.\d{4}, \d{2}:\d{2}:\d{2}\s+(?:MESZ|MEZ|UTC))\n(.*?)(?=Eingegebener Prompt:|$)'
        
        matches = re.finditer(pattern, html_clean, re.DOTALL)
        
        for match_num, match in enumerate(matches, 1):
            if match_num % 500 == 0:
                logger.info(f"[PROGRESS] {match_num} Prompts gefunden...")
            
            user_prompt = match.group(1).strip()
            timestamp = match.group(2).strip()
            ai_response = match.group(3).strip()
            
            # Cleanup AI-Response (entferne "Produkte:", "Warum steht..." etc.)
            ai_response = re.sub(r'Produkte:.*?(?=Eingegebener Prompt:|$)', '', ai_response, flags=re.DOTALL)
            ai_response = re.sub(r'Diese Aktivität.*?(?=Eingegebener Prompt:|$)', '', ai_response, flags=re.DOTALL)
            ai_response = re.sub(r'Warum steht.*?(?=Eingegebener Prompt:|$)', '', ai_response, flags=re.DOTALL)
            ai_response = ai_response.strip()
            
            # HTML-Dekodierung
            user_prompt = html_module.unescape(user_prompt)
            ai_response = html_module.unescape(ai_response)
            
            # Unicode-Whitespace normalisieren
            user_prompt = user_prompt.replace('\xa0', ' ').replace('\u00a0', ' ').replace('Â', '')
            ai_response = ai_response.replace('\xa0', ' ').replace('\u00a0', ' ').replace('Â', '')
            
            # Mehrfache Leerzeichen normalisieren
            user_prompt = ' '.join(user_prompt.split())
            ai_response = ' '.join(ai_response.split())
            
            # Validierung
            if not user_prompt or len(user_prompt) < 2:
                logger.warning(f"Match {match_num}: User-Prompt zu kurz")
                continue
            
            if not ai_response or len(ai_response) < 2:
                logger.debug(f"Match {match_num}: Keine AI-Response (OK für manche Einträge)")
            
            # Füge Einträge hinzu
            entries.append({
                'timestamp': timestamp,
                'speaker': 'user',
                'message': user_prompt,
                'match_idx': match_num
            })
            
            if ai_response and len(ai_response) > 2:
                entries.append({
                    'timestamp': timestamp,
                    'speaker': 'ai',
                    'message': ai_response,
                    'match_idx': match_num
                })
        
        logger.info(f"[ERFOLG] {len(entries)} Einträge extrahiert")
        return entries
    
    except Exception as e:
        logger.error(f"[FEHLER] Kritischer Fehler: {e}")
        raise

def sort_by_timestamp(entries: List[Dict]) -> List[Dict]:
    """Sortiert Einträge chronologisch nach Timestamp."""
    def parse_ts(entry):
        try:
            ts = entry['timestamp'].split(' MESZ')[0].split(' MEZ')[0].split(' UTC')[0].strip()
            return datetime.strptime(ts, '%d.%m.%Y, %H:%M:%S')
        except:
            logger.warning(f"Timestamp-Parse-Fehler: {entry['timestamp']}")
            return datetime.min
    
    sorted_entries = sorted(entries, key=parse_ts)
    logger.info(f"[SORT] {len(sorted_entries)} Einträge chronologisch sortiert")
    return sorted_entries

def write_txt_files(entries: List[Dict], output_base: Path) -> Dict:
    """Schreibt TXT-Dateien in Struktur YYYY/MM/DD/Prompt_N_speaker.txt"""
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
            ts = entry['timestamp'].split(' MESZ')[0].split(' MEZ')[0].split(' UTC')[0].strip()
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
        
        # Schreibe Dateien
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
            
            # Erhöhe Prompt-Nummer bei AI-Einträgen (User + AI = ein Pair)
            if entry['speaker'] == 'ai' or (entry != date_entries[-1] and 
                date_entries[date_entries.index(entry)+1]['speaker'] == 'user'):
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
        'extraction_method': 'REGEX + Streaming',
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
        f.write(f"Extraktions-Methode: REGEX + Streaming\n")
        f.write(f"Gesamt-Einträge: {stats['total_entries']}\n")
        f.write(f"Gesamt-Dateien: {stats['total_files']}\n")
        f.write(f"Gesamt-Wörter: {stats['total_words']:,}\n")
        f.write(f"Fehler: {stats['errors']}\n")
        if stats['by_date']:
            sorted_dates = sorted(stats['by_date'].keys())
            f.write(f"Datums-Bereich: {sorted_dates[0]} bis {sorted_dates[-1]}\n")
        f.write(f"\n[OK] Forensische Extraktion abgeschlossen\n")
    
    logger.info(f"[VERIFY] Gespeichert: {VERIFICATION_FILE}")

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("FORENSISCHE EXTRAKTION v2 - Google Takeout")
    logger.info("=" * 80)
    
    try:
        # 1. Extrahiere
        entries = extract_prompts_regex(SOURCE_HTML)
        
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
