# Evoki V3.0 To-Do List (V3 Upgrade)

## Completed
- [x] Create Project Architecture Map (`ARCHITECTURE.txt`)
- [x] Fix MCP Server Startup (Path & Imports)
- [x] Restore `mcp.json`
- [x] Implement Auto-Logging Watcher (`pending_status_watcher.py`)
- [x] Integrate SHA-256 Chain
- [x] Resolve "Chain Break" via `prev_window_hash` override
- [x] Establish V3.0 Directory Structure (`tooling/` vs `app/`)
- [x] Implement Workflows (`.agent/workflows/`)
- [x] **Adoption of V4.0 Sealed Protocol** (Split Responsibility)
- [x] Update Backend Logic for V4.0 Compliance (`synapse_logic.py`)
- [x] Verify V4.0 Chain Integrity
- [x] Update History Manager CLI (`status_history_manager.py`)
- [x] **Enforce Deterministic V4.0 State in Repo**
  - [x] Hardened Writer (Atomic)
  - [x] Hardened MCP (Monitor Gating)
  - [x] Hardened Logic (Backend-Auth Hashing)
  - [x] Hardened Verify (Recompute Check)

## In Progress
- [ ] Clean up redundant log files

## Pending
- [ ] Investigate Github Models Integration
- [ ] Stabilize FAISS Vector Search (dependent on MCP)
