#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evoki V3.0 - Metrics API Routes
================================

Endpoints für Metriken-Berechnung und Spektrum-Analyse.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

# Relative imports (backend/ is the root when running main.py)
from core.evoki_metrics_v3 import compute_full_spectrum
from core.spectrum_types import (
    get_all_metric_names,
    get_metric_info,
    validate_spectrum,
    FullSpectrum168
)
logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class MetricsRequest(BaseModel):
    """Request model for metrics computation."""
    user_text: str
    ai_text: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_text": "Ich fühle mich heute etwas unsicher.",
                "ai_text": "Das verstehe ich. Möchtest du darüber sprechen?",
                "context": {
                    "conversation_id": "abc123",
                    "turn_number": 5
                }
            }
        }


class MetricsResponse(BaseModel):
    """Response model with computed metrics."""
    success: bool
    spectrum: Optional[FullSpectrum168] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/compute", response_model=MetricsResponse)
async def compute_metrics(request: MetricsRequest):
    """
    Compute full FullSpectrum168 metrics for given text inputs.
    
    Returns all 168 EVOKI metrics including:
    - Core metrics (A-Score, PCI, Flow, etc.)
    - Physics metrics
    - Trauma/Safety metrics
    - B-Vector metrics
    - Evolution metrics
    - Timeline 4D metrics
    """
    try:
        logger.info(f"Computing metrics for user_text length: {len(request.user_text)}")
        
        # Compute full spectrum
        spectrum = compute_full_spectrum(
            user_text=request.user_text,
            ai_text=request.ai_text or "",
            context=request.context or {}
        )
        
        # Validate
        if not validate_spectrum(spectrum):
            raise ValueError("Generated spectrum failed validation")
        
        return MetricsResponse(
            success=True,
            spectrum=spectrum,
            metadata={
                "user_text_length": len(request.user_text),
                "ai_text_length": len(request.ai_text) if request.ai_text else 0,
                "context_keys": list(request.context.keys()) if request.context else []
            }
        )
        
    except Exception as e:
        logger.error(f"Metrics computation failed: {e}", exc_info=True)
        return MetricsResponse(
            success=False,
            error=str(e)
        )


@router.get("/health")
async def health_check():
    """Health check for metrics engine."""
    try:
        # Simple validation test
        test_spectrum = compute_full_spectrum(
            user_text="test",
            ai_text="response",
            context={}
        )
        
        return {
            "status": "healthy",
            "engine": "metrics_complete_v3",
            "spectrum_size": len(test_spectrum),
            "version": "3.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema")
async def get_schema():
    """
    Get the complete FullSpectrum168 schema definition.
    
    Returns all metric names, types, and ranges.
    """
    from core.spectrum_types import load_contract
    
    try:
        contract = load_contract()
        return {
            "success": True,
            "schema": contract["schema"],
            "spec": contract["spec"],
            "total_metrics": len(contract["items"]),
            "items": contract["items"]
        }
    except Exception as e:
        logger.error(f"Schema retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metric/{metric_key}")
async def get_metric_info(metric_key: str):
    """
    Get detailed information about a specific metric.
    
    Args:
        metric_key: Metric engine key (e.g., "m1_A")
    """
    from core.spectrum_types import get_metric_info
    
    info = get_metric_info(metric_key)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Metric '{metric_key}' not found"
        )
    
    return {
        "success": True,
        "metric": info
    }
