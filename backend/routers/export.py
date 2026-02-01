from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
from io import BytesIO
import logging

from services import export_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/inventory")
async def export_inventory():
    """Export current inventory to Excel"""
    excel_data = await export_service.export_current_inventory()
    
    filename = f"inventory_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    
    return StreamingResponse(
        BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/history")
async def export_history(
    start_date: str = Query(..., description="Start date (ISO8601)"),
    end_date: str = Query(..., description="End date (ISO8601)"),
    bin_ids: Optional[str] = Query(None, description="Comma-separated bin IDs")
):
    """Export historical data to Excel"""
    bin_id_list = bin_ids.split(",") if bin_ids else None
    
    excel_data = await export_service.export_historical_data(
        start_date=start_date,
        end_date=end_date,
        bin_ids=bin_id_list
    )
    
    filename = f"historical_data_{start_date}_{end_date}.xlsx".replace(":", "-")
    
    return StreamingResponse(
        BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/alerts")
async def export_alerts(
    start_date: Optional[str] = Query(None, description="Start date (ISO8601)"),
    end_date: Optional[str] = Query(None, description="End date (ISO8601)"),
    include_acknowledged: bool = Query(True)
):
    """Export alerts to Excel"""
    excel_data = await export_service.export_alerts(
        start_date=start_date,
        end_date=end_date,
        include_acknowledged=include_acknowledged
    )
    
    filename = f"alerts_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    
    return StreamingResponse(
        BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/report")
async def export_report():
    """Export comprehensive summary report to Excel"""
    excel_data = await export_service.export_summary_report()
    
    filename = f"inventory_report_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    
    return StreamingResponse(
        BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
