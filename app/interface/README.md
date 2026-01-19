# Evoki V3.0 - Frontend Interface

**Modern React + TypeScript frontend for the Evoki V3.0 therapeutic AI chat system.**

---

## 🎨 Features Implemented

### **Settings Panel (Complete)**
- ✅ **11 Themes:** 10 curated presets + 1 fully customizable theme
- ✅ **Custom Theme Editor:** 14 color pickers for complete UI customization
- ✅ **3 Display Modes:** Mobile (📱), Tablet (📱💻), Desktop (💻) with responsive sizing
- ✅ **7 Settings Tabs:**
  - 🎨 **Appearance** (Functional) - Themes + Display Modes
  - 👤 **Account** (Placeholder) - Google Login, Profile, Sessions
  - 🤖 **Agents** (Placeholder) - Agent Configuration, Personalization
  - 📥 **Export** (Placeholder) - Data Export (JSON/MD/CSV/PDF)
  - 🔒 **Privacy** (Placeholder) - Data Control, GDPR
  - ♿ **Accessibility** (Placeholder) - High Contrast, Screen Reader
  - 🎤 **Voice** (Placeholder) - TTS/STT Settings
- ✅ **localStorage Persistence:** All settings saved across sessions

### **UI Theming System**
- 24 CSS custom properties injected into `:root`
- Theme variables: 14 colors (backgrounds, text, borders, accents, status)
- Display mode variables: 10 sizing values (fonts, spacing, containers, icons)
- All components theme-aware via CSS variables

### **Temple Tab (Core Chat Interface)**
- Real-time chat with Gemini 2.0 Flash backend
- SSE streaming for gradual responses
- Custom styled input and send button
- Responsive to theme and display mode changes

---

## 🛠️ Tech Stack

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite 7
- **Styling:** Tailwind CSS + CSS Custom Properties
- **State Management:** React Hooks (useState, useEffect, useRef)
- **Backend Communication:** Server-Sent Events (SSE)

---

## 📁 Project Structure

```
app/interface/
├── src/
│   ├── components/
│   │   ├── core/
│   │   │   ├── SettingsPanel.tsx      # 7-tab settings with theme/display
│   │   │   ├── CustomThemeEditor.tsx  # 14 color pickers
│   │   │   └── TempleTab.tsx          # Main chat interface
│   │   ├── Tabs.tsx                   # Tab navigation
│   │   └── TabPanels.tsx              # Other tab content
│   ├── hooks/
│   │   └── useTheme.ts                # Theme + display mode management
│   ├── utils/
│   │   └── sse-parser.ts              # SSE stream consumption
│   ├── themes.ts                      # 11 theme definitions
│   ├── displayModes.ts                # 3 display mode configs
│   ├── types.ts                       # TypeScript interfaces
│   ├── App.tsx                        # Root component
│   └── main.tsx                       # Entry point
├── public/                            # Static assets
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## 🚀 Development

### **Prerequisites**
- Node.js 18+ and npm
- Backend running on `http://localhost:8000`

### **Install Dependencies**
```bash
cd app/interface
npm install
```

### **Run Dev Server**
```bash
npm run dev
# Opens on http://localhost:5173
```

### **Build for Production**
```bash
npm run build
# Output: dist/
```

---

## 🎨 Theming

### **Available Themes**
1. **Navy** - Dark blue (V2.0 original)
2. **Matrix** - Black/green hacker aesthetic
3. **Sunset** - Orange/red warm tones
4. **Cyberpunk** - Purple/magenta/cyan neon
5. **Ocean** - Blue/turquoise water tones
6. **Forest** - Green nature tones
7. **Midnight** - Dark blue/purple night sky
8. **Rose Gold** - Pink/gold elegant tones
9. **Arctic** - Ice blue/white cool tones
10. **Ember** - Dark orange/red fire tones
11. **Custom** - User-defined via color pickers

### **Custom Theme**
Access via Settings → Appearance → "🎨 Custom Theme (Eigene Farben)"

**14 Customizable Colors:**
- 3 Background colors
- 3 Text colors
- 2 Border colors
- 2 Accent colors
- 4 Status colors (success, warning, error, info)

---

## 📱 Display Modes

### **Mobile (📱)**
- Font: 14px base, 20px heading
- Spacing: Compact (8-16px)
- Best for: Small screens, mobile devices

### **Tablet (📱💻)**
- Font: 16px base, 24px heading
- Spacing: Balanced (12-24px)
- Best for: Tablets, small laptops

### **Desktop (💻)**
- Font: 18px base, 28px heading
- Spacing: Airy (16-32px)
- Best for: Desktop monitors, large screens

---

## 🔧 Configuration

### **localStorage Keys**
- `evoki_theme` - Selected theme name
- `evoki_custom_theme` - Custom theme color values (JSON)
- `evoki_display_mode` - Selected display mode

### **Backend Integration**
Default backend URL: `http://localhost:8000`

Update in code or via environment variable:
```typescript
// src/components/core/TempleTab.tsx
const response = await fetch('http://localhost:8000/stream', { ... });
```

---

## 📊 Statistics

- **Total Components:** 15+
- **CSS Variables:** 24 (14 theme + 10 display)
- **Themes:** 11
- **Display Modes:** 3
- **Settings Tabs:** 7
- **Color Pickers:** 14
- **Type Safety:** 100% TypeScript
- **Build Time:** <5s

---

## 🐛 Troubleshooting

### **White Screen on Load**
- Clear browser cache: Ctrl+Shift+Delete
- Clear Vite cache: `rm -rf node_modules/.vite`
- Restart dev server

### **Theme Not Persisting**
- Check browser's localStorage is enabled
- Open DevTools → Application → Local Storage
- Verify `evoki_theme` and `evoki_custom_theme` exist

### **TypeScript Errors**
- Ensure `verbatimModuleSyntax` is enabled in `tsconfig.json`
- Use `import type { Type }` for type-only imports

---

## 📝 Development Notes

### **Adding a New Theme**
1. Add entry to `src/themes.ts` → `THEMES` object
2. Follow existing color structure (14 properties)
3. Theme auto-appears in Settings

### **Adding Display Mode**
1. Add entry to `src/displayModes.ts` → `DISPLAY_MODES` object
2. Define font sizes, spacing, container width, icon sizes
3. Mode auto-appears in Settings

### **Implementing a Settings Tab**
1. Open `src/components/core/SettingsPanel.tsx`
2. Find the tab's placeholder section (e.g., `activeTab === 'account'`)
3. Replace `<ul>` list with actual UI components
4. Connect to backend APIs as needed

---

## 🚀 Next Steps

**Planned Implementations:**
- Account tab: Google integration, profile management
- Agents tab: Multi-agent configuration UI
- Export tab: Data export functionality (JSON/MD/CSV/PDF)
- Privacy tab: Data control toggles, GDPR tools
- Accessibility tab: High contrast, screen reader support
- Voice tab: TTS/STT integration

---

## 📄 License

Part of Evoki V3.0 project. See root LICENSE file.

---

**Last Updated:** 2026-01-19  
**Version:** 3.0.0-alpha  
**Status:** Settings Panel Complete ✅
