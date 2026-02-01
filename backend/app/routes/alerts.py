from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from app.models import (
    ApiResponse, PaginatedResponse, AcknowledgeRequest,
    AlertConfigUpdate, AlertLog, AlertConfiguration
)
from app.services import alert_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("/active", response_model=ApiResponse)
async def get_active_alerts():
    """Get all active (unacknowledged) alerts"""
    alerts = await alert_service.get_active_alerts()
    
    return ApiResponse(
        success=True,
        data=[alert.model_dump() for alert in alerts]
    )


@router.get("/history", response_model=PaginatedResponse)
async def get_alert_history(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    bin_id: Optional[str] = Query(None)
):
    """Get alert history with pagination"""
    alerts, total = await alert_service.get_alert_history(page, limit, bin_id)
    
    return PaginatedResponse(
        success=True,
        data=[alert.model_dump() for alert in alerts],
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    )


@router.post("/{alert_id}/acknowledge", response_model=ApiResponse)
async def acknowledge_alert(alert_id: int, request: AcknowledgeRequest = None):
    """Acknowledge a specific alert"""
    acknowledged_by = request.acknowledged_by if request else "system"
    
    success = await alert_service.acknowledge_alert(alert_id, acknowledged_by)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    
    return ApiResponse(
        success=True,
        message=f"Alert {alert_id} acknowledged"
    )


@router.post("/acknowledge-all", response_model=ApiResponse)
async def acknowledge_all_alerts(request: AcknowledgeRequest = None):
    """Acknowledge all active alerts"""
    acknowledged_by = request.acknowledged_by if request else "system"
    
    count = await alert_service.acknowledge_all_alerts(acknowledged_by)
    
    return ApiResponse(
        success=True,
        message=f"Acknowledged {count} alerts"
    )


@router.get("/configurations", response_model=ApiResponse)
async def get_alert_configurations(bin_id: Optional[str] = Query(None)):
    """Get alert configurations"""
    configs = await alert_service.get_alert_configurations(bin_id)
    
    return ApiResponse(
        success=True,
        data=[config.model_dump() for config in configs]
    )


@router.put("/configurations/{bin_id}/{alert_type}", response_model=ApiResponse)
async def update_alert_configuration(
    bin_id: str,
    alert_type: str,
    updates: AlertConfigUpdate
):
    """Update alert configuration for a specific bin and alert type"""
    success = await alert_service.update_alert_configuration(
        bin_id=bin_id,
        alert_type=alert_type,
        threshold_value=updates.threshold_value,
        is_enabled=updates.is_enabled
    )
    
    if not success:
        raise HTTPException(
            status_code=404, 
            detail=f"Alert configuration not found for {bin_id}/{alert_type}"
        )
    
    return ApiResponse(
        success=True,
        message="Alert configuration updated"
    )
