from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import logging

from app.models import (
    BinDataPayload, BinConfigUpdate, BinDisplayData,
    ApiResponse, InventorySummary, HistoricalDataPoint
)
from app.services import inventory_service, alert_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bins", tags=["Bins"])

# WebSocket broadcast function (set by main app)
_broadcast_bin_update = None

def set_broadcast_bin_update(func):
    global _broadcast_bin_update
    _broadcast_bin_update = func


@router.post("/data", response_model=ApiResponse)
async def receive_bin_data(data: BinDataPayload):
    """
    Receive bin data from hardware sensors.
    This endpoint is called by the edge router when new weight data is available.
    """
    logger.info(f"Received bin data: {data.bin_id} - qty: {data.calculated_quantity}")
    
    # Check if bin configuration exists
    bin_config = await inventory_service.get_bin_configuration(data.bin_id)
    if not bin_config:
        raise HTTPException(status_code=404, detail=f"Bin configuration not found for {data.bin_id}")
    
    # Record inventory data
    await inventory_service.record_inventory_data(
        bin_id=data.bin_id,
        weight_grams=data.weight_grams,
        calculated_quantity=data.calculated_quantity,
        timestamp=data.timestamp.isoformat()
    )
    
    # Get updated bin display data
    bin_display_data = await inventory_service.get_bin_display_data(data.bin_id)
    
    if bin_display_data:
        # Broadcast update via WebSocket
        if _broadcast_bin_update:
            await _broadcast_bin_update(bin_display_data)
        
        # Check for alerts
        await alert_service.check_alerts(bin_display_data)
    
    return ApiResponse(
        success=True,
        message="Bin data received and processed",
        data=bin_display_data.model_dump() if bin_display_data else None
    )


@router.get("", response_model=ApiResponse)
async def get_all_bins():
    """Get all bins with current inventory levels"""
    inventory = await inventory_service.get_current_inventory()
    return ApiResponse(
        success=True,
        data=[bin_data.model_dump() for bin_data in inventory]
    )


@router.get("/summary", response_model=ApiResponse)
async def get_inventory_summary():
    """Get inventory summary statistics"""
    summary = await inventory_service.get_inventory_summary()
    return ApiResponse(
        success=True,
        data=summary.model_dump()
    )


@router.get("/{bin_id}", response_model=ApiResponse)
async def get_bin(bin_id: str):
    """Get single bin details"""
    bin_data = await inventory_service.get_bin_display_data(bin_id)
    
    if not bin_data:
        raise HTTPException(status_code=404, detail=f"Bin {bin_id} not found")
    
    return ApiResponse(
        success=True,
        data=bin_data.model_dump()
    )


@router.put("/{bin_id}/config", response_model=ApiResponse)
async def update_bin_config(bin_id: str, updates: BinConfigUpdate):
    """Update bin configuration"""
    success = await inventory_service.update_bin_configuration(bin_id, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Failed to update bin {bin_id}")
    
    updated_bin = await inventory_service.get_bin_configuration(bin_id)
    
    return ApiResponse(
        success=True,
        message="Configuration updated",
        data=updated_bin.model_dump() if updated_bin else None
    )


@router.get("/{bin_id}/history", response_model=ApiResponse)
async def get_bin_history(
    bin_id: str,
    start_date: str = Query(..., description="Start date (ISO8601)"),
    end_date: str = Query(..., description="End date (ISO8601)"),
    limit: int = Query(1000, ge=1, le=10000)
):
    """Get historical data for a bin"""
    history = await inventory_service.get_historical_data(bin_id, start_date, end_date, limit)
    
    return ApiResponse(
        success=True,
        data=[h.model_dump() for h in history]
    )


@router.get("/{bin_id}/consumption", response_model=ApiResponse)
async def get_bin_consumption(bin_id: str):
    """Get consumption rate for a bin"""
    consumption_rate = await inventory_service.get_consumption_rate(bin_id)
    
    return ApiResponse(
        success=True,
        data=consumption_rate
    )
