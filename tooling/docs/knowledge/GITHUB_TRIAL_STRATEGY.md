# GitHub Enterprise & Advanced Security: 30-Day High-Impact Strategy

**Ziel:** Maximale Nutzung der 30-Tage-Testphase, um Evoki V3.0 dauerhaft sicherer und intelligenter zu machen.
**Fokus:** Features, die "Sticky" sind (d.h. Konfiguration bleibt oft erhalten oder schafft bleibenden Wert) oder die sofortigen Audit-Nutzen bringen.

---

## 1. Advanced Security (GHAS) - Sofort aktivieren!
*Diese Features finden Sicherheitslücken und Leaks, bevor sie Schaden anrichten.*

### A. Secret Scanning & Push Protection (Critical)
*   **Was:** Scannt Kommits nach API-Keys (Google Cloud, OpenAI, etc.) und blockiert den Push, wenn einer gefunden wird.
*   **Warum:** Verhindert versehentliche Leaks in `pending_status.json` oder Logs.
*   **Action:**
    1. Repo Settings -> **Code Security and Analysis**.
    2. **Secret scanning** -> Enable.
    3. **Push protection** -> Enable. 
    *   *Pro-Tipp: Wenn aktiviert, führen Sie einmalig einen kompletten History-Scan durch, um alte Leaks zu finden.*

### B. Code Scanning (CodeQL)
*   **Was:** Tiefe Analyse des Python/JS Codes auf Sicherheitslücken (SQL Injection, Unsafe Deserialization).
*   **Warum:** Findet Schwachstellen in `synapse_logic.py` oder API-Endpunkten, die Linter übersehen.
*   **Action:**
    1. Repo Settings -> **Code Security and Analysis**.
    2. **Code scanning** -> Set up -> Default setup (oder Advanced für mehr Kontrolle).
    3. Dies erstellt einen Workflow, der bei jedem Push läuft.

### C. Dependency Review
*   **Was:** Prüft in Pull Requests, ob neue Dependencies (pip/npm) Vulnerabilities haben.
*   **Action:**
    1. Repo Settings -> **Code Security and Analysis**.
    2. **Dependency graph** -> Enable.
    3. **Dependency review** -> Enable (falls verfügbar).

---

## 2. Copilot Enterprise - Knowledge Integration
*Nutze die AI, um deine eigene Doku zu verstehen.*

### A. Knowledge Bases (The "Killer Feature")
*   **Was:** Du kannst Copilot Zugriff auf deine Markdown-Doku (`tooling/docs`) geben.
*   **Warum:** Du kannst im GitHub Chat fragen: *"Was sind die V5 Regeln für Status Windows?"* und Copilot antwortet basierend auf `GEMINI_V13_UPDATE.md`.
*   **Action:**
    1. GitHub Organization Settings -> **Copilot**.
    2. **Knowledge bases** -> New knowledge base.
    3. Wähle das Evoki Repo und den Pfad `tooling/docs` aus.
    4. Jetzt steht dieses Wissen im Chat zur Verfügung!

### B. Pull Request Summaries
*   **Was:** AI schreibt Zusammenfassungen für deine PRs.
*   **Warum:** Spart Zeit bei der Doku von Changes.
*   **Action:** Einfach PR erstellen und auf das "Copilot" Icon im Description-Feld klicken.

---

## 3. GitHub Enterprise Features
*Management und Rules.*

### A. Repository Rulesets
*   **Was:** Granulare Kontrolle über Branch-Schutz (besser als alte Branch Protection).
*   **Action:**
    1. Repo Settings -> **Rules** -> **Rulesets**.
    2. Erstelle Ruleset für `main` Branch.
    3. Aktiviere **"Require status checks to pass"** (und wähle unseren neuen `Evoki V3.0 CI` Job aus!).
    4. Aktiviere **"Block force pushes"**.

### B. Environments
*   **Was:** Definiere "Production" oder "Staging" Environments mit Secrets und Protection Rules.
*   **Action:**
    1. Repo Settings -> **Environments**.
    2. Erstelle `Production`.
    3. Füge "Required reviewers" hinzu (z.B. dich selbst), damit Deployments manuell genehmigt werden müssen.

---

## Empfohlener Zeitplan

| Tag | Aktion |
|-----|--------|
| **Heute** | Secret Scanning & Push Protection aktivieren (Dauert 2 Min). Knowledge Base erstellen (Indexierung dauert etwas). |
| **Morgen** | CodeQL Scanning Setup und ersten Scan analysieren (Fixes machen). |
| **Woche 1** | Rulesets für `main` definieren. CI Checks zur Pflicht machen. |
| **Woche 4** | Letzter Audit: Alles exportieren (Security Reports). |

*Hinweis: Wenn die Trial endet, bleiben die Code-Scanning Alerts oft sichtbar (read-only), aber neue Scans funktionieren evtl. nicht mehr mit Enterprise-Features. Die Konfiguration (YAML Files) bleibt aber im Repo.*
