#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evoki V3.0 - Integrity Database

SQLite-basierte Datenbank für Integrity-Event-Logging und Hash-Chain-Tracking.
Forensische Analyse bei Integrity Breaches.
"""
import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List


# Database Path
DB_PATH = Path(__file__).parent.parent / "data" / "integrity.db"


def ensure_db_exists():
    """Stellt sicher dass integrity.db existiert mit korrektem Schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Table 1: Integrity Events (Breaches, Validations)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS integrity_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            genesis_sha256 TEXT,
            registry_sha256 TEXT,
            combined_sha256 TEXT,
            calculated_genesis TEXT,
            calculated_registry TEXT,
            error_message TEXT,
            details TEXT
        )
    """)
    
    # Table 2: Interaction Chain (Hash-Chain für Prompts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS integrity_chain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            interaction_id INTEGER,
            content_sha256 TEXT NOT NULL,
            prev_chain_sha256 TEXT,
            chain_sha256 TEXT NOT NULL,
            prompt_length INTEGER,
            response_length INTEGER
        )
    """)
    
    conn.commit()
    conn.close()


def log_breach(
    event_type: str,
    error_message: str,
    integrity_result: Optional[Dict] = None,
    details: Optional[Dict] = None
):
    """
    Loggt Integrity Breach in DB.
    
    Args:
        event_type: "LOCKDOWN", "GENESIS_BREACH", "REGISTRY_BREACH", etc.
        error_message: Fehlermeldung
        integrity_result: Optional dict von validate_genesis_anchor()
        details: Optional zusätzliche Details
    """
    ensure_db_exists()
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    timestamp = datetime.utcnow().isoformat()
    
    # Severity basierend auf event_type
    severity_map = {
        "LOCKDOWN": "CRITICAL",
        "GENESIS_BREACH": "CRITICAL",
        "REGISTRY_BREACH": "HIGH",
        "VALIDATION_SUCCESS": "INFO"
    }
    severity = severity_map.get(event_type, "MEDIUM")
    
    # Extrahiere Daten aus integrity_result
    genesis_sha256 = None
    registry_sha256 = None
    combined_sha256 = None
    calculated_genesis = None
    calculated_registry = None
    
    if integrity_result:
        genesis_sha256 = integrity_result.get("expected_genesis")
        calculated_genesis = integrity_result.get("calculated_genesis")
        # registry/combined falls später implementiert
    
    cursor.execute("""
        INSERT INTO integrity_events (
            timestamp, event_type, severity,
            genesis_sha256, registry_sha256, combined_sha256,
            calculated_genesis, calculated_registry,
            error_message, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp, event_type, severity,
        genesis_sha256, registry_sha256, combined_sha256,
        calculated_genesis, calculated_registry,
        error_message,
        json.dumps(details) if details else None
    ))
    
    conn.commit()
    conn.close()
    
    print(f"📝 Integrity Event logged: {event_type} ({severity})")


def compute_content_sha256(prompt: str, response: str = "") -> str:
    """
    Berechnet SHA256 über Prompt + Response Content.
    
    Args:
        prompt: User Prompt
        response: System Response (optional)
    
    Returns:
        SHA256 hex string
    """
    content = json.dumps({
        "prompt": prompt,
        "response": response
    }, ensure_ascii=False, sort_keys=True)
    
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compute_chain_sha256(content_sha256: str, prev_chain_sha256: Optional[str]) -> str:
    """
    Berechnet Chain SHA256 (verketteter Hash).
    
    Args:
        content_sha256: Hash des aktuellen Contents
        prev_chain_sha256: Hash der vorherigen Chain (None für erste Interaktion)
    
    Returns:
        Chain SHA256 hex string
    """
    if prev_chain_sha256 is None:
        # Erste Interaktion: chain = content
        return content_sha256
    
    # Folge-Interaktion: chain = SHA256(prev_chain + content)
    combined = f"{prev_chain_sha256}|{content_sha256}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def log_interaction(
    interaction_id: int,
    prompt: str,
    response: str = ""
):
    """
    Loggt Interaktion in Hash-Chain.
    
    Args:
        interaction_id: Eindeutige Interaktions-ID
        prompt: User Prompt
        response: System Response
    """
    ensure_db_exists()
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Hole vorherigen Chain-Hash
    cursor.execute("""
        SELECT chain_sha256 FROM integrity_chain
        ORDER BY id DESC LIMIT 1
    """)
    result = cursor.fetchone()
    prev_chain_sha256 = result[0] if result else None
    
    # Berechne Hashes
    content_sha256 = compute_content_sha256(prompt, response)
    chain_sha256 = compute_chain_sha256(content_sha256, prev_chain_sha256)
    
    timestamp = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO integrity_chain (
            timestamp, interaction_id,
            content_sha256, prev_chain_sha256, chain_sha256,
            prompt_length, response_length
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp, interaction_id,
        content_sha256, prev_chain_sha256, chain_sha256,
        len(prompt), len(response)
    ))
    
    conn.commit()
    conn.close()


def get_recent_events(limit: int = 10) -> List[Dict]:
    """
    Holt die letzten Integrity Events.
    
    Args:
        limit: Anzahl der Events
    
    Returns:
        Liste von Event-Dicts
    """
    ensure_db_exists()
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM integrity_events
        ORDER BY id DESC LIMIT ?
    """, (limit,))
    
    events = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return events


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("INTEGRITY DB - TESTING")
    print("=" * 80)
    
    # Test 1: DB Creation
    print("\n1. Creating/Ensuring DB...")
    ensure_db_exists()
    print(f"   ✅ DB exists: {DB_PATH}")
    
    # Test 2: Log Breach
    print("\n2. Logging test breach...")
    log_breach(
        event_type="GENESIS_BREACH",
        error_message="Test breach for demonstration",
        integrity_result={
            "expected_genesis": "abc123",
            "calculated_genesis": "def456"
        },
        details={"test": True}
    )
    print("   ✅ Breach logged")
    
    # Test 3: Log Interaction
    print("\n3. Logging test interaction...")
    log_interaction(
        interaction_id=1,
        prompt="Test prompt",
        response="Test response"
    )
    print("   ✅ Interaction logged")
    
    # Test 4: Get Recent Events
    print("\n4. Fetching recent events...")
    events = get_recent_events(limit=5)
    print(f"   ✅ Found {len(events)} events")
    for event in events:
        print(f"      - {event['event_type']}: {event['error_message']}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)
