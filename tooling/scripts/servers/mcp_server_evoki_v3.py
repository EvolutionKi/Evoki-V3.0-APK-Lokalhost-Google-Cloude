#!/usr/bin/env python3
"""
MCP Server for Synapse Auto-Context Loading

This server automatically provides Regelwerk V12, backend state, and persistent context
to Antigravity at every prompt - NO manual copy-paste needed!

Resources:
- synapse://regelwerk - Regelwerk V12 
- synapse://backend_state - Current cycle, step-id, etc.
- synapse://persistent_context - Downloads path, user preferences, etc.
- synapse://project_awareness - Known components, architecture info

Usage:
    python scripts/mcp_server_synapse.py

MCP Config (.agent/mcp_config.json):
    {
      "mcpServers": {
        "synapse-context": {
          "command": "python",
          "args": ["scripts/mcp_server_synapse.py"],
          "autoStart": true
        }
      }
    }
"""

import asyncio
import json
import sqlite3
import os
import sys
from pathlib import Path
from typing import Any

# Try to import MCP - if not available, provide instructions
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("ERROR: MCP library not installed!")
    print("Install with: pip install mcp")
    print("Install with: pip install mcp")
    exit(1)

# Ensure repo/app is importable (temple.* lives under /app)
PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")
APP_DIR = PROJECT_ROOT / "app"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

try:
    # Dynamic path for automation modules
    automation_dir = Path(__file__).resolve().parent.parent / "automation"
    if automation_dir.exists() and str(automation_dir) not in sys.path:
        sys.path.append(str(automation_dir))
    from synapse_logic import StatusHistoryManager
    from search_chatverlauf import (
        SearchChatverlaufConfig,
        SearchChatverlaufError,
        search_chatverlauf as _search_chatverlauf,
    )
except ImportError as e:
    print(f"[WARN] Could not import automation modules: {e}", file=sys.stderr)
    StatusHistoryManager = None
    SearchChatverlaufConfig = None
    SearchChatverlaufError = Exception
    _search_chatverlauf = None

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REGELWERK_PATH = DATA_DIR / "prompts" / "EVOKI_SYSTEM_PROMPT_GEMINI_V12.txt"
BACKEND_STATE_PATH = DATA_DIR / "backend_state.json"
PERSISTENT_DB_PATH = DATA_DIR / "db" / "persistent_context.db"
PENDING_STATUS_PATH = DATA_DIR / "synapse" / "status" / "pending_status.json"

# Initialize MCP server
server = Server("synapse-context")

# File monitoring state
last_pending_mtime = None


def init_persistent_db():
    """Initialize SQLite database for persistent context"""
    db = sqlite3.connect(PERSISTENT_DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS context_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    
    # Insert default values if not exist
    defaults = {
        "downloads_path": "C:\\Users\\nicom\\Downloads",
        "evoki_version": "V2.0",
        "regelwerk_version": "V12",
        "project_name": "Evoki DeepEarth",
        "chatverlauf_faiss_index": "C:\\Evoki V3.0 APK-Lokalhost-Google Cloude\\tooling\\data\\faiss_indices\\chatverlauf_final_20251020plus_dedup_sorted.faiss",
        "chatverlauf_metadata": "C:\\Evoki V3.0 APK-Lokalhost-Google Cloude\\tooling\\data\\faiss_indices\\chatverlauf_final_20251020plus_dedup_sorted.metadata.json",
        "chatverlauf_sqlite": "C:\\Evoki V3.0 APK-Lokalhost-Google Cloude\\tooling\\data\\faiss_indices\\chatverlauf_final_20251020plus_dedup_sorted.db"
    }
    
    for key, value in defaults.items():
        db.execute("""
            INSERT OR IGNORE INTO context_store (key, value)
            VALUES (?, ?)
        """, (key, value))
    
    db.commit()
    db.close()


def load_regelwerk() -> str:
    """Load Regelwerk V12 from file"""
    if REGELWERK_PATH.exists():
        return REGELWERK_PATH.read_text(encoding='utf-8')
    else:
        return "# Regelwerk V12 not found\n\nPath: " + str(REGELWERK_PATH)


def load_backend_state() -> dict:
    """Load backend state from JSON"""
    if BACKEND_STATE_PATH.exists():
        return json.loads(BACKEND_STATE_PATH.read_text(encoding='utf-8'))
    else:
        return {
            "error": "Backend state not found",
            "path": str(BACKEND_STATE_PATH),
            "cycle": "1/5",
            "step_id": "UNKNOWN"
        }


def load_persistent_context() -> dict:
    """Load persistent context from SQLite"""
    if not PERSISTENT_DB_PATH.exists():
        init_persistent_db()
    
    db = sqlite3.connect(PERSISTENT_DB_PATH)
    cursor = db.execute("SELECT key, value FROM context_store")
    context = dict(cursor.fetchall())
    db.close()
    
    return context


def load_project_awareness() -> dict:
    """Load project awareness data"""
    return {
        "project_name": "EVOKI V3.0 - The Resonance Engine",
        "architecture": {
            "trinity_engine": ["Planner", "Executor", "Reflection"],
            "databases": [
                "evoki_kb_extended.faiss",
                "synapse_knowledge_base.faiss",
                "chatverlauf_final_20251020plus_dedup_sorted.faiss",
                "chatverlauf_final_20251020plus_dedup_sorted.db",
                "persistent_context.db",
                "backend_state.json"
            ],
            "workers": 18,
            "engines": 13,
            "v1_artifacts": 109848
        },
        "known_components": [
            "Trinity Engine",
            "FAISS Vector DBs",
            "Compliance Watcher",
            "Guardian Chain",
            "Chronos (Time Sync)",
            "6-Prompt Auto-Audit",
            "Status Window System",
            "Regelwerk V12 (881 rules)",
            "SHA256 Prompt Chain"
        ],
        "vision": "Seelen-Metrik für Sovereignty",
        "core_principle": "Trialog (User + Evoki + Synapse)"
    }


def load_prompt_chain_history(limit: int = 20) -> dict:
    """Load recent prompt chain history"""
    import sqlite3
    
    if not PERSISTENT_DB_PATH.exists():
        return {"error": "Prompt chain not initialized"}
    
    db = sqlite3.connect(PERSISTENT_DB_PATH)
    
    # Get chain stats
    cursor = db.execute("SELECT COUNT(*) FROM prompt_chain")
    total_entries = cursor.fetchone()[0]
    
    # Get recent entries
    cursor = db.execute("""
        SELECT id, timecode, source, destination, action, content, sha256_current
        FROM prompt_chain
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    entries = []
    for row in cursor.fetchall():
        id_, timecode, source, dest, action, content, hash_ = row
        entries.append({
            "id": id_,
            "timecode": timecode,
            "source": source,
            "destination": dest,
            "action": action,
            "content": content[:200] if content else "",  # Truncate long content
            "hash": hash_
        })
    
    db.close()
    
    return {
        "total_entries": total_entries,
        "recent_entries": entries,
        "chain_status": "verified" if total_entries > 0 else "empty"
    }


def load_conversation_history(limit: int = 20) -> dict:
    """Load recent conversation history from JSONL file"""
    history_file = DATA_DIR / "conversation_history.jsonl"
    
    if not history_file.exists():
        return {
            "error": "Conversation history not found",
            "path": str(history_file),
            "total_entries": 0,
            "recent_entries": []
        }
    
    # Read JSONL file (last N lines)
    entries = []
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Get last N lines
        recent_lines = lines[-limit:] if len(lines) > limit else lines
        
        for line in recent_lines:
            try:
                entry = json.loads(line.strip())
                # Truncate content for MCP response
                if "prompt" in entry:
                    entry["prompt_preview"] = entry["prompt"][:200]
                    entry.pop("prompt", None)
                if "response" in entry:
                    entry["response_preview"] = entry["response"][:200]
                    entry.pop("response", None)
                entries.append(entry)
            except:
                continue
        
        return {
            "total_entries": len(lines),
            "recent_entries": entries,
            "limit": limit,
            "file_path": str(history_file)
        }
    except Exception as e:
        return {
            "error": str(e),
            "total_entries": 0,
            "recent_entries": []
        }


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List all available resources"""
    return [
        types.Resource(
            uri="synapse://regelwerk",
            name="Regelwerk V12",
            description="881 Regeln (A0-A67) - Complete rule system",
            mimeType="text/plain"
        ),
        types.Resource(
            uri="synapse://backend_state",
            name="Backend State",
            description="Current cycle, step-id, prompt count",
            mimeType="application/json"
        ),
        types.Resource(
            uri="synapse://persistent_context",
            name="Persistent Context",
            description="Downloads path, user preferences, persistent data",
            mimeType="application/json"
        ),
        types.Resource(
            uri="synapse://project_awareness",
            name="Project Awareness",
            description="EVOKI V3.0 architecture, Trinity Engine, Deep Earth layers",
            mimeType="application/json"
        ),
        types.Resource(
            uri="synapse://prompt_chain",
            name="SHA256 Prompt Chain",
            description="Recent prompt/response history with SHA256 verification",
            mimeType="application/json"
        ),
        types.Resource(
            uri="synapse://conversation_history",
            name="Conversation History (JSONL)",
            description="Complete conversation history in append-only JSONL format",
            mimeType="application/json"
        ),
        types.Resource(
            uri="synapse://chatverlauf_kb_info",
            name="Chatverlauf KB Info",
            description="Paths to chatverlauf FAISS index, metadata, and SQLite DB",
            mimeType="application/json"
        )
    ]


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="save_status",
            description="Natively save a Status Window (S2 Protocol) to history. Handles hashing and timestamping automatically.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status_window": {
                        "type": "object", 
                        "description": "The Status Window JSON block (Rules: 1-13)",
                        "additionalProperties": True
                    },
                },
                "required": ["status_window"],
            },
        ),
        types.Tool(
            name="search_chatverlauf",
            description="Semantic search across the chatverlauf FAISS index, optional full text from SQLite.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5},
                    "include_text": {"type": "boolean", "default": False},
                    "vector_backend": {"type": "string", "enum": ["faiss", "numpy"], "default": "faiss"},
                    "embedding_backend": {
                        "type": "string",
                        "enum": ["sentence_transformers", "hash"],
                        "default": "sentence_transformers"
                    },
                    "embedding_model": {"type": "string", "default": "all-MiniLM-L6-v2"},
                    "embedding_dim": {"type": "integer", "default": 384}
                },
                "required": ["query"]
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    if name == "save_status":
        status_window = arguments.get("status_window")
        if not status_window:
            return [types.TextContent(type="text", text="Error: No status_window provided.")]

        if not StatusHistoryManager:
             return [types.TextContent(type="text", text="Error: Status History Manager not loaded.")]
        
        try:
             # Use the Core Logic
             manager = StatusHistoryManager()
             success = manager.add_status_window(status_window, source="mcp_native_tool")
             
             if success:
                 # Check the hash of the last entry to return it
                 entries = manager.get_latest(1)
                 if entries:
                     latest_hash = entries[0].get("window_hash", "UNKNOWN")
                     return [types.TextContent(type="text", text=f"Status Saved. Hash: {latest_hash}")]
                 else:
                     return [types.TextContent(type="text", text="Status Saved (No Hash returned).")]
             else:
                 return [types.TextContent(type="text", text="Status Registry Failed (Protocol Violation or Error). Check stderr.")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"MCP Save Error: {str(e)}")]

    if name == "search_chatverlauf":
        query = (arguments.get("query") or "").strip()
        if not query:
            return [types.TextContent(type="text", text="Error: query required.")]

        top_k = int(arguments.get("top_k") or 5)
        include_text = bool(arguments.get("include_text") or False)

        if not _search_chatverlauf or not SearchChatverlaufConfig:
            return [types.TextContent(type="text", text="Error: chatverlauf search lib not available on server.")]

        # Prefer persistent context defaults (kept in DB)
        ctx = load_persistent_context()
        default_index = DATA_DIR / "faiss_indices" / "chatverlauf_final_20251020plus_dedup_sorted.faiss"
        default_meta = DATA_DIR / "faiss_indices" / "chatverlauf_final_20251020plus_dedup_sorted.metadata.json"
        default_db = DATA_DIR / "faiss_indices" / "chatverlauf_final_20251020plus_dedup_sorted.db"

        index_path = Path(ctx.get("chatverlauf_faiss_index") or default_index)
        meta_path = Path(ctx.get("chatverlauf_metadata") or default_meta)
        db_path = Path(ctx.get("chatverlauf_sqlite") or default_db)

        vector_backend = (arguments.get("vector_backend") or "faiss").strip()
        embedding_backend = (arguments.get("embedding_backend") or "sentence_transformers").strip()
        embedding_model = (arguments.get("embedding_model") or "all-MiniLM-L6-v2").strip()
        embedding_dim = int(arguments.get("embedding_dim") or 384)

        cfg = SearchChatverlaufConfig(
            index_path=index_path,
            meta_path=meta_path,
            db_path=db_path,
            vector_backend=vector_backend,
            embedding_backend=embedding_backend,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
        )

        try:
            results = _search_chatverlauf(
                query=query,
                top_k=top_k,
                include_text=include_text,
                config=cfg,
            )
            return [types.TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]
        except SearchChatverlaufError as e:
            return [types.TextContent(type="text", text=f"Retrieval Error: {e}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Retrieval Crash: {e}")]

    raise ValueError(f"Unknown tool: {name}")


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    
    if uri == "synapse://regelwerk":
        content = load_regelwerk()
        return content
    
    elif uri == "synapse://backend_state":
        state = load_backend_state()
        return json.dumps(state, indent=2, ensure_ascii=False)
    
    elif uri == "synapse://persistent_context":
        context = load_persistent_context()
        return json.dumps(context, indent=2, ensure_ascii=False)
    
    elif uri == "synapse://project_awareness":
        awareness = load_project_awareness()
        return json.dumps(awareness, indent=2, ensure_ascii=False)
    
    elif uri == "synapse://prompt_chain":
        chain = load_prompt_chain_history()
        return json.dumps(chain, indent=2, ensure_ascii=False)
    
    elif uri == "synapse://conversation_history":
        history = load_conversation_history()
        return json.dumps(history, indent=2, ensure_ascii=False)
    elif uri == "synapse://chatverlauf_kb_info":
        info = {
            "faiss_index": str(DATA_DIR / "faiss_indices" / "chatverlauf_final_20251020plus_dedup_sorted.faiss"),
            "metadata": str(DATA_DIR / "faiss_indices" / "chatverlauf_final_20251020plus_dedup_sorted.metadata.json"),
            "sqlite": str(DATA_DIR / "faiss_indices" / "chatverlauf_final_20251020plus_dedup_sorted.db")
        }
        return json.dumps(info, indent=2, ensure_ascii=False)
    else:
        raise ValueError(f"Unknown resource: {uri}")


async def monitor_pending_status():
    """Background task to monitor pending_status.json and auto-save"""
    global last_pending_mtime
    
    print("📡 Starting pending_status.json monitor...")
    
    while True:
        try:
            if PENDING_STATUS_PATH.exists():
                # Check if file was modified
                current_mtime = PENDING_STATUS_PATH.stat().st_mtime
                
                if last_pending_mtime is None or current_mtime != last_pending_mtime:
                    last_pending_mtime = current_mtime
                    
                    # Read and save
                    try:
                        with open(PENDING_STATUS_PATH, 'r', encoding='utf-8') as f:
                            status_window = json.load(f)
                        
                        # Validate basic structure
                        if status_window.get("step_id") and status_window.get("mcp_trigger"):
                            if StatusHistoryManager:
                                manager = StatusHistoryManager()
                                success = manager.add_status_window(
                                    status_window,
                                    source="pending_status_auto",
                                    metadata={"auto_saved": True}
                                )
                                
                                if success:
                                    print(f"✅ Auto-saved Status Window from pending_status.json (step_id: {status_window.get('step_id')})")
                                else:
                                    print(f"⚠️ Failed to save Status Window from pending_status.json", file=sys.stderr)
                    except Exception as e:
                        print(f"⚠️ Error processing pending_status.json: {e}", file=sys.stderr)
            
            # Check every 2 seconds
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"⚠️ Monitor error: {e}", file=sys.stderr)
            await asyncio.sleep(5)


async def main():
    """Run MCP server"""
    # Initialize database
    init_persistent_db()
    
    # Start background monitor
    enable_monitor = os.getenv("EVOKI_ENABLE_PENDING_MONITOR", "0").strip() in ("1", "true", "TRUE", "yes", "YES")
    monitor_task = None
    if enable_monitor:
        monitor_task = asyncio.create_task(monitor_pending_status())
    else:
        print("ℹ️ pending_status monitor DISABLED (set EVOKI_ENABLE_PENDING_MONITOR=1 to enable)", file=sys.stderr)
    
    # Run server
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    finally:
        # Cancel monitor on shutdown (if enabled)
        if monitor_task:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    print("🔥 Starting Synapse MCP Server...")
    print(f"📁 Base Dir: {BASE_DIR}")
    print(f"📋 Regelwerk: {REGELWERK_PATH}")
    print(f"💾 Backend State: {BACKEND_STATE_PATH}")
    print(f"🗄️ Persistent DB: {PERSISTENT_DB_PATH}")
    print("\n✅ Server ready - Antigravity can now auto-load context!")
    
    asyncio.run(main())
