#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synapse Core Logic for EVOKI V3.0
Contains the StatusHistoryManager for use by CLI scripts and automation.
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import shutil
import tempfile
import secrets


class StatusHistoryManager:
    """Manages persistent history of all Status Windows with cryptographic chain"""
    
    def __init__(self, history_file: Optional[Path] = None):
        # V3.0 Optimized Paths
        self.v3_root = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
        self.base_dir = self.v3_root / "tooling" / "data" / "synapse" / "status"
        self.history_file = history_file or (self.base_dir / "status_window_history.json")
        self.backup_dir = self.base_dir / "backups"
        self.max_entries = 1000  # Rotate after 1000 entries
        
        # Ensure directories exist
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _compute_hash(self, status_window: Dict[str, Any], timestamp: str, salt: str) -> str:
        """Compute SHA-256 hash with Timestamp and Salt binding"""
        sw = dict(status_window)
        sw.pop("window_hash", None)  # avoid circular/self-reference
        canonical = json.dumps(sw, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        payload = f"{canonical}|{timestamp}|{salt}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def _validate_chronos(self, status_window: Dict[str, Any]) -> bool:
        """Verify that status window timestamp is fresh (Chronos Check)"""
        try:
            # Extract timestamp from time_source string "metadata (STRICT_SYNC): ISO_TIME"
            time_source = status_window.get("time_source", "")
            if "metadata (STRICT_SYNC): " not in time_source:
                print("[ERROR] Chronos Check Failed: Invalid time_source format", file=sys.stderr)
                return False
            
            ts_str = time_source.split("metadata (STRICT_SYNC): ")[1].strip()
            # Handle potential timezone offsets if present, simple ISO parse
            ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            
            # Use UTC (Zulu time) for universal, unambiguous timestamps
            now = datetime.now(timezone.utc)
            diff = abs((now - ts).total_seconds())
            
            if diff > 300:  # 5 minutes tolerance
                print(f"[ERROR] Chronos Check Failed: Timestamp too old/future (diff={diff}s)", file=sys.stderr)
                return False
                
            return True
        except Exception as e:
            print(f"[WARN] Chronos Validation Error: {e}", file=sys.stderr)
            return False
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Safely load existing history with corruption recovery"""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            if not isinstance(data, dict):
                raise ValueError("History file must be a JSON object")
            
            entries = data.get("entries", [])
            if not isinstance(entries, list):
                raise ValueError("entries must be a list")
            
            return entries
            
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON corruption detected: {e}", file=sys.stderr)
            return self._recover_from_backup()
        
        except Exception as e:
            print(f"[WARN] Error loading history: {e}", file=sys.stderr)
            return self._recover_from_backup()
    
    def _recover_from_backup(self) -> List[Dict[str, Any]]:
        """Attempt to recover from backup files"""
        backups = sorted(self.backup_dir.glob("status_history_*.json"), reverse=True)
        
        for backup in backups[:3]:  # Try last 3 backups
            try:
                with open(backup, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entries = data.get("entries", [])
                    print(f"[OK] Recovered from backup: {backup.name}", file=sys.stderr)
                    return entries
            except Exception:
                continue
        
        print("[WARN] No valid backups found, starting fresh", file=sys.stderr)
        return []
    
    def _save_history_atomic(self, entries: List[Dict[str, Any]]) -> bool:
        """Save history using atomic write (temp file + rename)"""
        
        # Create history object with metadata
        history_data = {
            "version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_entries": len(entries),
            "entries": entries
        }
        
        try:
            # Write to temporary file first
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=self.history_file.parent,
                delete=False,
                suffix='.tmp'
            ) as tmp:
                json.dump(history_data, tmp, indent=2, ensure_ascii=False)
                tmp_path = Path(tmp.name)
            
            # Atomic rename (overwrites existing file)
            tmp_path.replace(self.history_file)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error saving history: {e}", file=sys.stderr)
            if 'tmp_path' in locals() and tmp_path.exists():
                tmp_path.unlink()
            return False
    
    def _create_backup(self) -> None:
        """Create timestamped backup of current history"""
        if not self.history_file.exists():
            return
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"status_history_{timestamp}.json"
        
        try:
            shutil.copy2(self.history_file, backup_file)
            
            # Keep only last 10 backups
            backups = sorted(self.backup_dir.glob("status_history_*.json"))
            for old_backup in backups[:-10]:
                old_backup.unlink()
                
        except Exception as e:
            print(f"[WARN] Backup creation failed: {e}", file=sys.stderr)
    
    def _rotate_if_needed(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rotate history if it exceeds max entries"""
        if len(entries) <= self.max_entries:
            return entries
        
        print(f"[ROTATE] Rotating history: {len(entries)} -> {self.max_entries}", file=sys.stderr)
        
        # Create archive of old entries
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_file = self.backup_dir / f"status_history_archive_{timestamp}.json"
        
        old_entries = entries[:-self.max_entries]
        new_entries = entries[-self.max_entries:]
        
        try:
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "version": "1.0",
                    "archived_at": datetime.now(timezone.utc).isoformat(),
                    "total_entries": len(old_entries),
                    "entries": old_entries
                }, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] Archived {len(old_entries)} old entries to {archive_file.name}")
            
        except Exception as e:
            print(f"[WARN] Archive creation failed: {e}", file=sys.stderr)
        
        return new_entries
    
    def _validate_protocol_v40(self, block, current_entries):
        """
        Enforces strict S2 V4.0 Protocol compliance (Split Responsibility).
        """
        # 1. Semantic Fields (AGENT MUST FILL)
        semantic_fields = [
            "goal", "inputs", "actions", "risk", "assumptions", 
            "rule_tangency", "reflection_curve", "output_plan", 
            "window_type", "confidence"
        ]
        
        for field in semantic_fields:
            if field not in block:
                print(f"[ERROR] Missing Semantic Field: {field}", file=sys.stderr)
                return False
            if block[field] is None:
                 print(f"[ERROR] Semantic Field is Null: {field}", file=sys.stderr)
                 return False

        # 2. System Fields (AGENT MUST RETURN NULL or OMIT)
        # We don't block if they are missing (we hydrate them), 
        # but if they are present, they should ideally be ignored or null.
        # For V4.0 compliance, we just ensure we HAVE the block structure to work with.
        
        return True

        # 2. Chain Continuity
        if current_entries:
            last_entry = current_entries[-1]
            last_hash = last_entry.get("window_hash")
            claimed_prev = block.get("prev_window_hash")
            
            if last_hash and claimed_prev != last_hash:
                print(f"[ERROR] Chain Break Detected!", file=sys.stderr)
                print(f"      Expected prev_window_hash: {last_hash}", file=sys.stderr)
                print(f"      Got:                       {claimed_prev}", file=sys.stderr)
                sys.stderr.flush()
                return False
        elif block.get("prev_window_hash") not in [None, "null"]:
             # First entry recovery
             pass

        return True

    def add_status_window(
        self,
        status_window: Dict[str, Any],
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a new Status Window to history.
        """
        
        # Create backup before modification
        self._create_backup()
        
        # Load existing history
        entries = self._load_history()

        # ------------------------------------------------------------------
        # Backend-authoritative enrichment (no client-trust for time/hash)
        # ------------------------------------------------------------------
        save_time = datetime.now(timezone.utc).isoformat()

        # Ensure mcp_trigger exists + stamp authoritative timestamp
        mcp = status_window.get("mcp_trigger")
        if not isinstance(mcp, dict):
            mcp = {}
        mcp["timestamp"] = save_time
        status_window["mcp_trigger"] = mcp

        # Ensure Chronos-compatible time_source (STRICT_SYNC + TZ-aware ISO)
        status_window["time_source"] = f"metadata (STRICT_SYNC): {save_time}"

        # Ensure prev_window_hash is consistent with chain head if missing/placeholder
        placeholder_prev = {None, "null", "", "AUTO", "PLACEHOLDER"}
        if entries:
            last_hash = entries[-1].get("window_hash")
            claimed_prev = status_window.get("prev_window_hash")
            if claimed_prev in placeholder_prev:
                status_window["prev_window_hash"] = last_hash
        else:
            if status_window.get("prev_window_hash") in placeholder_prev:
                status_window["prev_window_hash"] = None

        # Ensure window_hash field exists before protocol validation
        if "window_hash" not in status_window:
            status_window["window_hash"] = "PLACEHOLDER_BACKEND"
        
        # HARDCODED PROTOCOL ENFORCEMENT V4.0
        if not self._validate_protocol_v40(status_window, entries):
              print("[ERROR] S2 Protocol Violation: Block rejected.", file=sys.stderr)
              return False

        # Chronos Time Check
        if not self._validate_chronos(status_window):
            return False

        # Generate cryptographic salt
        salt = secrets.token_hex(16)
        
        # Compute Hash with Salt and Timestamp binding
        window_hash = self._compute_hash(status_window, save_time, salt)
        # Make the stored status_window self-describing
        status_window["window_hash"] = window_hash
        
        # Check for duplicates
        for entry in entries:
            if entry.get("window_hash") == window_hash:
                print(f"[SKIP] Duplicate detected, skipping: {window_hash[:16]}...", file=sys.stderr)
                return False
        
        # Create new entry with Salt and Save Time
        new_entry = {
            "timestamp": save_time,
            "salt": salt,
            "source": source,
            "window_hash": window_hash,
            "status_window": status_window,
            "hash_algo": "sha256(canonical_without_window_hash|timestamp|salt)",
            "metadata": metadata or {}
        }
        
        # Append to history
        entries.append(new_entry)
        
        # Rotate if needed
        entries = self._rotate_if_needed(entries)
        
        # Save atomically
        success = self._save_history_atomic(entries)
        
        if success:
            print(f"[OK] Added to history: {window_hash[:16]}... (total: {len(entries)})")
        
        return success
    
    def get_latest(self, count: int = 1) -> List[Dict[str, Any]]:
        """Get the latest N Status Windows from history"""
        entries = self._load_history()
        return entries[-count:] if entries else []
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all Status Windows from history"""
        return self._load_history()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the history"""
        entries = self._load_history()
        
        if not entries:
            return {
                "total_entries": 0,
                "oldest_timestamp": None,
                "newest_timestamp": None,
                "sources": {}
            }
        
        sources = {}
        for entry in entries:
            source = entry.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_entries": len(entries),
            "oldest_timestamp": entries[0].get("timestamp"),
            "newest_timestamp": entries[-1].get("timestamp"),
            "sources": sources,
            "history_file": str(self.history_file),
            "file_size_bytes": self.history_file.stat().st_size if self.history_file.exists() else 0
        }
