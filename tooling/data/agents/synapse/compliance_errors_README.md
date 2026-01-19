# Compliance Error Log

Diese Datei wird automatisch von der Synapse Extension geschrieben.

**Zweck:** Agent (Antigravity) bekommt diese Datei automatisch in seinen Context und sieht sofort wenn etwas schief läuft.

**Format:**
```json
[
  {
    "timestamp": "2026-01-14T01:35:00.000Z",
    "type": "breach",
    "message": "Kein Status Window nach 65s",
    "prompt": "User fragte etwas...",
    "timeSincePrompt": 65
  }
]
```

**Typen:**
- `warning` - 50% Zeit abgelaufen
- `breach` - Max Zeit überschritten, kein Status Window

**Agent Reaction:**
Wenn Agent diese Datei sieht und neue Errors findet → automatisch Status Window schreiben!
