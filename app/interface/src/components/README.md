# 📱 FRONTEND STRUCTURE - APK-READY

**Zweck:** Organisierte Komponenten-Struktur für zukünftige APK-Deployment

---

## 📁 STRUKTUR

```
components/
  ├─ core/              # V3.0 Core Komponenten
  │   ├─ DeepEarthTab.tsx      (Deep Earth Memory Viewer)
  │   ├─ MetricsDashboard.tsx  (Live 153 Metriken)
  │   ├─ TempleTab.tsx         (Evoki Temple Chat)
  │   └─ TrialogPanel.tsx      (Trialog Interface)
  │
  ├─ v2_tabs/           # V2.0 Legacy Tabs (Migration)
  │
  └─ README.md          # Diese Datei
```

---

## 🎯 DESIGN-PRINZIPIEN

### **APK-READY:**
- ✅ Relative Imports (keine absolute Pfade)
- ✅ Komponenten in logischen Ordnern
- ✅ Klare Trennung: Core vs. Legacy
- ✅ Vorbereitet für Capacitor/Cordova Build

### **SERVER-BACKEND-READY:**
- ✅ API-Calls über Umgebungsvariablen (`VITE_API_URL`)
- ✅ Keine localhost-Hardcodes
- ✅ Zukünftig: Backend läuft auf separatem Server

---

## 📦 ZUKÜNFTIGE APK-DEPLOYMENT

```bash
# Frontend als PWA/APK bauen:
npm run build

# Mit Capacitor zu Android APK:
npx cap init evoki com.evoki.app
npx cap add android
npx cap sync
npx cap open android
```

**Wichtig:** Alle Komponenten-Imports bleiben stabil!

---

## 🔗 API-KONFIGURATION

```typescript
// .env.development
VITE_API_URL=http://localhost:8000

// .env.production
VITE_API_URL=https://api.evoki.app
```

**Komponenten verwenden:**
```typescript
const API_URL = import.meta.env.VITE_API_URL;
fetch(`${API_URL}/api/temple/process-stream`, ...);
```

---

## ✅ MIGRATION-STATUS

- ✅ **Core-Komponenten:** In `core/` verschoben
- 📋 **V2-Migration:** `v2_tabs/` bereit für Import
- 🚀 **APK-Ready:** Struktur vorbereitet

**Keine Pfad-Änderungen mehr nötig!**
