# Implementation Plan - V2.1 Protocol Compliance

## Objective
Update the Evoki V3.0 backend to strictly enforce the "V2.1 Sealed Protocol" (Hash calculation by System, Passive Trigger).

## Components to Modify

### 1. `app/temple/automation/synapse_logic.py`
**Goal:** Implement System-Managed Hashing and relax Validation for Agent Placeholders.
- **`_validate_protocol_v13`**:
  - Update to accept "PENDING_GENERATION" in `window_hash`.
- **`add_status_window`**:
  - Calculate `window_hash` based on content (with placeholder).
  - **INJECT** the calculated hash back into `status_window["window_hash"]` before saving.
  - This ensures the persistent history contains the valid hash for the *next* turn (Chain Integrity).

### 2. `.geminiignore`
**Goal:** Prevent Context Pollution.
- Exclude `tooling/data/synapse/history/` and `backups/`.

### 3. Workflows
**Goal:** Create standard workflows for verification.
- Create `.agent/workflows/evoki_verify.md`.

## Execution Steps
1.  **Modify `synapse_logic.py`**: Apply the logic changes.
2.  **Create `.geminiignore`**: Write the file.
3.  **Test**: Trigger a status save and verify `window_hash` is replaced.

---
**Status:** APPROVED
**Execution Mode:** IMMEDIATE
