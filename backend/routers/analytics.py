from fastapi import APIRouter, Query
import logging

from models import ApiResponse, StatusDistribution
from services import inventory_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/trends", response_model=ApiResponse)
async def get_trends(
    start_date: str = Query(..., description="Start date (ISO8601)"),
    end_date: str = Query(..., description="End date (ISO8601)")
):
    """Get inventory trends for all bins"""
    trends = await inventory_service.get_all_historical_data(start_date, end_date)
    
    return ApiResponse(
        success=True,
        data=trends
    )


@router.get("/consumption", response_model=ApiResponse)
async def get_consumption_rates():
    """Get consumption rates for all bins"""
    bins = await inventory_service.get_all_bin_configurations()
    
    consumption_data = []
    for bin_config in bins:
        rate = await inventory_service.get_consumption_rate(bin_config.bin_id)
        consumption_data.append({
            "bin_id": bin_config.bin_id,
            "article_name": bin_config.article_name,
            **rate
        })
    
    return ApiResponse(
        success=True,
        data=consumption_data
    )


@router.get("/comparison", response_model=ApiResponse)
async def get_inventory_comparison():
    """Get current inventory levels comparison for chart"""
    inventory = await inventory_service.get_current_inventory()
    
    comparison = [
        {
            "bin_id": bin_data.bin_id,
            "article_name": bin_data.article_name,
            "current_quantity": bin_data.current_quantity,
            "max_capacity": bin_data.max_capacity,
            "fill_percentage": bin_data.fill_percentage,
            "status": bin_data.status.value
        }
        for bin_data in inventory
    ]
    
    return ApiResponse(
        success=True,
        data=comparison
    )


@router.get("/status-distribution", response_model=ApiResponse)
async def get_status_distribution():
    """Get distribution of bin statuses for pie chart"""
    summary = await inventory_service.get_inventory_summary()
    
    distribution = [
        {"status": "Normal", "count": summary.normal_count, "color": "#22c55e"},
        {"status": "Low", "count": summary.low_count, "color": "#eab308"},
        {"status": "Critical", "count": summary.critical_count, "color": "#f97316"},
        {"status": "Empty", "count": summary.empty_count, "color": "#ef4444"}
    ]
    
    return ApiResponse(
        success=True,
        data={
            "distribution": distribution,
            "total": summary.total_bins
        }
    )
