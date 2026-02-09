"""
Evoki V3.0 - Integrity API

Endpoint für Frontend Integrity Status Checks.
"""
from fastapi import APIRouter

try:
    from core.genesis_anchor import validate_full_integrity
    from core.enforcement_gates import is_lockdown
except ImportError:  # fallback when backend is a package
    from backend.core.genesis_anchor import validate_full_integrity
    from backend.core.enforcement_gates import is_lockdown

router = APIRouter()


@router.get("/status")
async def get_integrity_status():
    """
    GET /api/integrity/status
    
    Returns full integrity status including:
    - verified: bool (all checks passed)
    - lockdown: bool (system locked)
    - mode: "prod" | "dev" (ENV or meta.integrity)
    - expected: {genesis, registry, combined}
    - calculated: {genesis, registry, combined}
    - checks: {genesis_ok, registry_ok, combined_ok}
    - error: Optional error message
    
    Frontend uses this for IntegrityGuard.
    """
    # Check lockdown first
    lockdown, lockdown_reason = is_lockdown()
    
    if lockdown:
        return {
            "verified": False,
            "lockdown": True,
            "mode": "unknown",
            "error": lockdown_reason,
            "checks": {
                "genesis_ok": False,
                "registry_ok": False,
                "combined_ok": False
            }
        }
    
    # Run full integrity check
    result = validate_full_integrity(strict=True)
    
    return {
        "verified": result.get("verified", False),
        "lockdown": result.get("lockdown", False),
        "mode": result.get("mode", "dev"),
        "expected": result.get("expected", {}),
        "calculated": result.get("calculated", {}),
        "checks": result.get("checks", {}),
        "error": result.get("error")
    }
