---
description: Verify Evoki System Health and Chain Integrity
---

# Evoki System Verification Workflow

This workflow checks the integrity of the S2 Status Chain and verifies that the automation pipeline is functioning correctly.

1. **Check MCP Server Status**
   - Ensure the MCP server process is running.
   - Command: `tasklist /FI "IMAGENAME eq python.exe"` (Windows)

2. **Verify Pending Status Watcher**
   - Ensure the watcher is active.
   - Check log: `tooling/data/synapse/pending_watcher.log`

3. **Verify Status Chain Integrity**
   - Run the verification tool to check cryptographic links.
   // turbo
   - Command: `python "app/temple/automation/status_history_manager.py" verify`

4. **Check Latest Status**
   - View the last status window to ensure correct hashing.
   // turbo
   - Command: `python "app/temple/automation/status_history_manager.py" latest --count 1`

5. **Backup Hygiene**
   - Clean up old backups if needed.
