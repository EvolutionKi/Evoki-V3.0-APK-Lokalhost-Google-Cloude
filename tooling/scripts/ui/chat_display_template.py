# SYNAPSE Chat Display Template V1.0
# Dieses Template definiert das menschenlesbare Ausgabeformat für den Chat.
# Es wird aus den Feldern von pending_status.json befüllt.

DISPLAY_TEMPLATE = """
╔══════════════════════════════════════════════════════════════════╗
║                    🧠 SYNAPSE STATUS #{entry_index}                        ║
╠══════════════════════════════════════════════════════════════════╣
║ ZIEL:      {goal:<56} ║
║ CHAIN:     {chain_status:<56} ║
║ KONFIDENZ: {confidence:<56} ║
║ SCHEMA:    {schema_version:<56} ║
╠══════════════════════════════════════════════════════════════════╣
║ 📝 DEIN PROMPT (Auszug):                                        ║
║ {raw_user_request_line1:<64} ║
║ {raw_user_request_line2:<64} ║
╠══════════════════════════════════════════════════════════════════╣
║ 🔄 REFLEXION:                                                    ║
║                                                                  ║
║ DELTA (Was war?):                                                ║
║   {delta_line1:<62} ║
║   {delta_line2:<62} ║
║                                                                  ║
║ CORRECTION (Was wurde korrigiert?):                              ║
║   {correction_line1:<62} ║
║   {correction_line2:<62} ║
║                                                                  ║
║ NEXT (Was kommt als nächstes?):                                  ║
║   {next:<62} ║
╚══════════════════════════════════════════════════════════════════╝
"""

# Schema-Felder, die das Display befüllen:
REQUIRED_FIELDS = {
    "entry_index": "int (from history count)",
    "goal": "string (max 56 chars)",
    "chain_status": "🟢 GREEN / 🟡 YELLOW / 🔴 RED + count",
    "confidence": "float 0.0-1.0",
    "schema_version": "string (e.g. 3.2)",
    "raw_user_request": "string (truncated to 2 lines)",
    "reflection_curve.delta": "string (truncated to 2 lines)",
    "reflection_curve.correction": "string (truncated to 2 lines)", 
    "reflection_curve.next": "string (1 line)"
}

def format_status_display(status: dict, entry_count: int) -> str:
    """
    Formatiert ein Status-Window-Dict in das lesbare Display-Format.
    """
    import textwrap
    
    def wrap(text, width, lines=2):
        wrapped = textwrap.wrap(str(text), width=width)
        result = wrapped[:lines] if wrapped else [""]
        while len(result) < lines:
            result.append("")
        return result
    
    rc = status.get("reflection_curve", {})
    raw = status.get("inputs", {}).get("raw_user_request", "")
    
    raw_lines = wrap(raw, 62, 2)
    delta_lines = wrap(rc.get("delta", ""), 60, 2)
    correction_lines = wrap(rc.get("correction", ""), 60, 2)
    
    chain_icon = "🟢" if status.get("critical_summary", {}).get("status") == "GREEN" else "🟡"
    chain_text = f"{chain_icon} {status.get('critical_summary', {}).get('status', 'UNKNOWN')} ({entry_count} Einträge)"
    
    return DISPLAY_TEMPLATE.format(
        entry_index=entry_count,
        goal=status.get("goal", "")[:56],
        chain_status=chain_text[:56],
        confidence=status.get("confidence", 0.0),
        schema_version=status.get("schema_version", "?")[:56],
        raw_user_request_line1=raw_lines[0],
        raw_user_request_line2=raw_lines[1],
        delta_line1=delta_lines[0],
        delta_line2=delta_lines[1],
        correction_line1=correction_lines[0],
        correction_line2=correction_lines[1],
        next=rc.get("next", "")[:62]
    )


if __name__ == "__main__":
    # Test mit Beispiel-Daten
    import json
    from pathlib import Path
    
    # Dynamic Root
    PROJECT_ROOT = Path(os.getenv("EVOKI_PROJECT_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))).resolve()
    if not (PROJECT_ROOT / "tooling").exists():
        PROJECT_ROOT = Path(os.path.abspath(".")).resolve()

    pending = PROJECT_ROOT / "tooling/data/synapse/status/pending_status.json"
    if pending.exists():
        status = json.loads(pending.read_text(encoding="utf-8"))
        print(format_status_display(status, 58))
