# GitHub Models Free Tier & Prototyping API

**Datum der Erfassung:** 2026-01-13
**Status:** Knowledge Base
**Tags:** API, AI, Prototyping, Free Tier, GitHub

## Übersicht
GitHub bietet über den Marketplace Zugriff auf diverse KI-Modelle (OpenAI, Microsoft, DeepSeek, Mistral, etc.) mit einem **kostenlosen "Playground"-Tier** für Experimente und Prototyping. Dies ist ideal für Evoki "Deep Earth" Tests, ohne eigene API-Keys kostenpflichtig belasten zu müssen.

## Nutzungsszenarien für Evoki
1. **Model Evaluation:** Testen verschiedener Modelle (z.B. Vergleich R1 vs gpt-4o) mit identischen Prompts.
2. **Integration Tests:** Implementierung des OpenAI-kompatiblen API-Clients (`Azure AI Inference SDK` oder `REST`) ohne Kostenrisiko.
3. **Fallback:** Nutzung als Fallback für Low-Priority Tasks.

## Verfügbare Modelle (Auszug)
- **OpenAI:** GPT-4o, o1-preview, o1-mini
- **DeepSeek:** R1, V3
- **Microsoft:** Phi-3.5
- **Meta:** Llama 3.x
- **Mistral:** Large, Small

## Technische Integration

### Endpunkt
Verfügbar via `github.com/marketplace/models`.

### Authentifizierung
- Benötigt **GitHub Personal Access Token (PAT)**.
- Scope keine speziellen Scopes außer User-Gültigkeit (Tokens mit `models:read` Berechtigungen, falls separat geführt).
- CodeSpaces haben Token oft injected.

### SDKs
- **Azure AI Inference SDK** (Empfohlen für Model-Agnostik)
- **REST API** (Direkt)
- **OpenAI SDK** (Oft kompatibel durch Base-URL Change)

## Einschränkungen (Free Tier Limits)

Die Limits (Rate Limits) variieren je nach Modell-Tier ("Low", "High", "Embedding").

| Modell-Typ | Requests/Min | Requests/Tag | Token/Request | Concurrent |
|------------|--------------|--------------|---------------|------------|
| **Low** (z.B. kleine Modelle) | 15 | 150 | 8k In / 4k Out | 5 |
| **High** (z.B. GPT-4o) | 10 | 50 | 8k In / 4k Out | 2 |
| **DeepSeek R1** | 1 | 8 | 4k In / 4k Out | 1 |
| **Embeddings** | 15 | 150 | 64k | 5 |

*Hinweis: Diese Limits können sich ändern (Stand Jan 2026).*

## Vorgehen im Playground
1. Modell wählen
2. Parameter einstellen (Temp, TopP)
3. "Code" Tab öffnen -> Snippet für Python/JS kopieren.

## Referenzen
- [GitHub Marketplace Models](https://github.com/marketplace/models)
- [Azure AI Inference SDK](https://pypi.org/project/azure-ai-inference/)
