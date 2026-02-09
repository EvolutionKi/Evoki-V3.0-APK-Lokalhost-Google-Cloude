# Architecture Blueprint: Local-First VS Code Controller (Sovereign) - V3 (God Mode)

## 1. Executive Summary
This document outlines the architecture for a **Software-Enforced Local Controller** for VS Code.
**Principle:** "Sovereign Authority." The User is the absolute root. The system enforces the User's will, even if that will is "Run Everything".

## 2. Core Components (The "Diamond Architecture")

### A. The Controller (TypeScript Extension Host)
- **Role:** The only entity with "hands".
- **Capabilities (Permission Graph):**
    - `fs.*`: File System Access.
    - `terminal.pty`: Pseudo-Terminal for deterministic output capture.
    - `lm.generate`: Raw LLM access.
- **Trusted Exec:** Explicitly handles "Sovereign Mode" to bypass safety checks when authorized.

### B. The State Engine (Event Sourcing)
- **Role:** Immutable History & Truth.
- **Format:**
    - `events.log.jsonl`: Append-only log.
    - `state.snapshot.json`: fast lookup state.
- **Security:** HMAC-Signed events.

### C. The Enforcement Gateway (Policy as Code)
- **Role:** The Firewall AND The Accelerator.
- **Mechanism:**
    1. **Plan Generation:** LLM generates JSON Plan.
    2. **Policy Check:**
        - **Standard Mode:** Validates actions against strict rules.
        - **Sovereign Mode (GOD MODE):** `ValidationResult = ALWAYS_ALLOW`.
    3. **Execution:** Controller executes immediately.

### D. The UI Layer (Hardened View)
- **Role:** Strict Rendering & Control Panel.
- **Features:**
    - **Status Window:** Rendered by Controller.
    - **Control Switch:** Toggle "Auto-Approve All" (God Mode).
    - **Audit Log:** Visual stream of what is happening.

## 3. Sovereign Mode ("Always Exceed All")
This is the "No Nagging" configuration.
- **Default Behavior:** "Ask before destructive action."
- **Sovereign Behavior:**
    1.  User toggles "Enable Sovereign Mode" (Persistent setting).
    2.  System auto-approves `fs.write`, `cmd.exec`, `git.push`.
    3.  System creates a "Rollback Point" (Git Commit/FS Snapshot) *before* batch execution (Safety Net).
    4.  LLM runs effectively "unleashed" but fully logged.

## 4. Implementation Stack

- **Language:** TypeScript 5.x.
- **Terminal:** `node-pty`.
- **Validation:** `zod`.
- **Auth:** VS Code SecretStorage + User Presence (Physical confirmation).

## 5. The Loop (Sovereign Flow)

1.  **Trigger:** User says "Build this app, don't ask me details."
2.  **Plan:** LLM generates 50-step plan.
3.  **Gate:**
    - `Mode == SOVEREIGN`? -> **SKIP** individual checks.
    - **Auto-Execute** entire batch.
4.  **Feedback:** Live stream of execution to UI.
5.  **Snap:** Logs + State preserved.

## 6. Philosophy
**"Control != Restriction."**
Enforcement means the system *cannot* disobey your policy.
If your policy is "Do it all", the system enforces that by *not* stopping.
You are the pilot. The default is Safety, the switch is Speed.
