from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, List
from datetime import datetime
from enum import Enum


class BinStatus(str, Enum):
    NORMAL = "normal"
    LOW = "low"
    CRITICAL = "critical"
    EMPTY = "empty"
    OVERFILL = "overfill"


class AlertType(str, Enum):
    LOW_STOCK = "low_stock"
    CRITICAL_STOCK = "critical_stock"
    EMPTY = "empty"
    OVERFILL = "overfill"


# Request Models
class BinDataPayload(BaseModel):
    """Payload received from hardware sensors"""
    bin_id: str = Field(..., pattern=r"^BIN-R[1-2]P[1-5]$", description="Bin identifier")
    row: int = Field(..., ge=1, le=2, description="Row number (1-2)")
    position: int = Field(..., ge=1, le=5, description="Position in row (1-5)")
    weight_grams: float = Field(..., ge=0, description="Total weight in grams")
    article_weight_grams: float = Field(..., gt=0, description="Single article weight")
    calculated_quantity: int = Field(..., ge=0, description="Calculated quantity")
    timestamp: datetime = Field(..., description="ISO8601 timestamp")


class BinConfigUpdate(BaseModel):
    """Update bin configuration"""
    article_type: Optional[str] = Field(None, min_length=1, max_length=50)
    article_name: Optional[str] = Field(None, min_length=1, max_length=100)
    article_weight_grams: Optional[float] = Field(None, gt=0)
    min_threshold: Optional[int] = Field(None, ge=0)
    critical_threshold: Optional[int] = Field(None, ge=0)
    max_capacity: Optional[int] = Field(None, gt=0)


class AlertConfigUpdate(BaseModel):
    """Update alert configuration"""
    threshold_value: Optional[int] = Field(None, ge=0)
    is_enabled: Optional[bool] = None


class AcknowledgeRequest(BaseModel):
    """Acknowledge alert request"""
    acknowledged_by: str = Field(default="system", max_length=100)


# Response Models
class BinConfiguration(BaseModel):
    """Bin configuration from database"""
    id: int
    bin_id: str
    row: int
    position: int
    article_type: str
    article_name: str
    article_weight_grams: float
    min_threshold: int
    critical_threshold: int
    max_capacity: int
    created_at: str
    updated_at: str


class BinDisplayData(BaseModel):
    """Bin data for dashboard display"""
    bin_id: str
    row: int
    position: int
    article_type: str
    article_name: str
    current_quantity: int
    max_capacity: int
    fill_percentage: int
    status: BinStatus
    min_threshold: int
    critical_threshold: int
    last_updated: str
    weight_grams: float


class InventorySummary(BaseModel):
    """Summary statistics for dashboard"""
    total_bins: int
    normal_count: int
    low_count: int
    critical_count: int
    empty_count: int
    total_items: int
    alerts_active: int


class AlertLog(BaseModel):
    """Alert log entry"""
    id: int
    bin_id: str
    alert_type: str
    message: str
    quantity_at_alert: int
    threshold_value: int
    is_acknowledged: bool
    acknowledged_at: Optional[str]
    acknowledged_by: Optional[str]
    created_at: str


class AlertConfiguration(BaseModel):
    """Alert configuration"""
    id: int
    bin_id: str
    alert_type: str
    threshold_value: int
    is_enabled: bool
    created_at: str
    updated_at: str


class HistoricalDataPoint(BaseModel):
    """Single historical data point"""
    timestamp: str
    quantity: int
    weight_grams: float


class ConsumptionRate(BaseModel):
    """Consumption rate data"""
    bin_id: str
    article_name: Optional[str] = None
    daily_average: float
    weekly_average: float
    trend: Literal["increasing", "decreasing", "stable"]


class StatusDistribution(BaseModel):
    """Status distribution for charts"""
    status: str
    count: int
    color: str


# API Response wrappers
class ApiResponse(BaseModel):
    """Standard API response"""
    success: bool
    data: Optional[dict | list] = None
    message: Optional[str] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated API response"""
    success: bool
    data: list
    pagination: dict


# WebSocket message types
class WSMessageType(str, Enum):
    BIN_UPDATE = "bin_update"
    ALERT = "alert"
    CONNECTION = "connection"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class WSMessage(BaseModel):
    """WebSocket message structure"""
    type: WSMessageType
    payload: dict
    timestamp: str
