import logging
from typing import Optional
from datetime import datetime, timedelta

from database import get_database
from models import AlertLog, AlertConfiguration, BinDisplayData, AlertType

logger = logging.getLogger(__name__)

# WebSocket broadcast function will be set by the main app
_broadcast_alert = None

def set_broadcast_alert(func):
    """Set the broadcast alert function"""
    global _broadcast_alert
    _broadcast_alert = func


class AlertService:
    """Service for managing alerts"""
    
    async def check_alerts(self, bin_data: BinDisplayData) -> list[AlertLog]:
        """Check and generate alerts for a bin"""
        alerts = []
        db = await get_database()
        
        # Get alert configurations for this bin
        configs = await db.fetch_all(
            "SELECT * FROM alert_configurations WHERE bin_id = ? AND is_enabled = 1",
            (bin_data.bin_id,)
        )
        
        for config in configs:
            should_alert = False
            message = ""
            
            alert_type = config['alert_type']
            threshold = config['threshold_value']
            
            if alert_type == AlertType.LOW_STOCK.value:
                if 0 < bin_data.current_quantity <= threshold:
                    should_alert = True
                    message = f"Low stock alert: {bin_data.article_name} in {bin_data.bin_id} is at {bin_data.current_quantity} units (threshold: {threshold})"
            
            elif alert_type == AlertType.CRITICAL_STOCK.value:
                if 0 < bin_data.current_quantity <= threshold:
                    should_alert = True
                    message = f"CRITICAL: {bin_data.article_name} in {bin_data.bin_id} is critically low at {bin_data.current_quantity} units"
            
            elif alert_type == AlertType.EMPTY.value:
                if bin_data.current_quantity <= 0:
                    should_alert = True
                    message = f"EMPTY: {bin_data.article_name} in {bin_data.bin_id} is empty!"
            
            elif alert_type == AlertType.OVERFILL.value:
                if bin_data.current_quantity > bin_data.max_capacity:
                    should_alert = True
                    message = f"Overfill warning: {bin_data.article_name} in {bin_data.bin_id} exceeds capacity ({bin_data.current_quantity}/{bin_data.max_capacity})"
            
            if should_alert:
                # Check cooldown
                recent_alert = await self.get_recent_alert(bin_data.bin_id, alert_type, 30)
                
                if not recent_alert:
                    alert = await self.create_alert(
                        bin_id=bin_data.bin_id,
                        alert_type=alert_type,
                        message=message,
                        quantity_at_alert=bin_data.current_quantity,
                        threshold_value=threshold
                    )
                    
                    if alert:
                        alerts.append(alert)
                        # Broadcast alert via WebSocket
                        if _broadcast_alert:
                            await _broadcast_alert(alert)
        
        return alerts
    
    async def create_alert(
        self,
        bin_id: str,
        alert_type: str,
        message: str,
        quantity_at_alert: int,
        threshold_value: int
    ) -> Optional[AlertLog]:
        """Create a new alert"""
        db = await get_database()
        
        try:
            row_id = await db.execute(
                """INSERT INTO alert_logs (bin_id, alert_type, message, quantity_at_alert, threshold_value)
                   VALUES (?, ?, ?, ?, ?)""",
                (bin_id, alert_type, message, quantity_at_alert, threshold_value)
            )
            
            logger.warning(f"Alert created: {message}")
            
            row = await db.fetch_one(
                "SELECT * FROM alert_logs WHERE id = ?",
                (row_id,)
            )
            
            if row:
                return AlertLog(
                    id=row['id'],
                    bin_id=row['bin_id'],
                    alert_type=row['alert_type'],
                    message=row['message'],
                    quantity_at_alert=row['quantity_at_alert'],
                    threshold_value=row['threshold_value'],
                    is_acknowledged=bool(row['is_acknowledged']),
                    acknowledged_at=row['acknowledged_at'],
                    acknowledged_by=row['acknowledged_by'],
                    created_at=row['created_at']
                )
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
        
        return None
    
    async def get_recent_alert(
        self,
        bin_id: str,
        alert_type: str,
        cooldown_minutes: int
    ) -> Optional[AlertLog]:
        """Check for recent alert of same type (for cooldown)"""
        db = await get_database()
        cooldown_time = (datetime.now() - timedelta(minutes=cooldown_minutes)).isoformat()
        
        row = await db.fetch_one(
            """SELECT * FROM alert_logs 
               WHERE bin_id = ? AND alert_type = ? AND created_at >= ?
               ORDER BY created_at DESC LIMIT 1""",
            (bin_id, alert_type, cooldown_time)
        )
        
        if row:
            return AlertLog(
                id=row['id'],
                bin_id=row['bin_id'],
                alert_type=row['alert_type'],
                message=row['message'],
                quantity_at_alert=row['quantity_at_alert'],
                threshold_value=row['threshold_value'],
                is_acknowledged=bool(row['is_acknowledged']),
                acknowledged_at=row['acknowledged_at'],
                acknowledged_by=row['acknowledged_by'],
                created_at=row['created_at']
            )
        return None
    
    async def get_active_alerts(self) -> list[AlertLog]:
        """Get all unacknowledged alerts"""
        db = await get_database()
        
        rows = await db.fetch_all(
            """SELECT al.*, bc.article_name, bc.row, bc.position
               FROM alert_logs al
               JOIN bin_configurations bc ON al.bin_id = bc.bin_id
               WHERE al.is_acknowledged = 0
               ORDER BY al.created_at DESC"""
        )
        
        return [AlertLog(
            id=row['id'],
            bin_id=row['bin_id'],
            alert_type=row['alert_type'],
            message=row['message'],
            quantity_at_alert=row['quantity_at_alert'],
            threshold_value=row['threshold_value'],
            is_acknowledged=bool(row['is_acknowledged']),
            acknowledged_at=row['acknowledged_at'],
            acknowledged_by=row['acknowledged_by'],
            created_at=row['created_at']
        ) for row in rows]
    
    async def get_alert_history(
        self,
        page: int = 1,
        limit: int = 50,
        bin_id: Optional[str] = None
    ) -> tuple[list[AlertLog], int]:
        """Get alert history with pagination"""
        db = await get_database()
        offset = (page - 1) * limit
        
        if bin_id:
            count_result = await db.fetch_one(
                "SELECT COUNT(*) as count FROM alert_logs WHERE bin_id = ?",
                (bin_id,)
            )
            rows = await db.fetch_all(
                """SELECT * FROM alert_logs WHERE bin_id = ?
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (bin_id, limit, offset)
            )
        else:
            count_result = await db.fetch_one(
                "SELECT COUNT(*) as count FROM alert_logs"
            )
            rows = await db.fetch_all(
                """SELECT * FROM alert_logs
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (limit, offset)
            )
        
        total = count_result.get('count', 0) if count_result else 0
        
        alerts = [AlertLog(
            id=row['id'],
            bin_id=row['bin_id'],
            alert_type=row['alert_type'],
            message=row['message'],
            quantity_at_alert=row['quantity_at_alert'],
            threshold_value=row['threshold_value'],
            is_acknowledged=bool(row['is_acknowledged']),
            acknowledged_at=row['acknowledged_at'],
            acknowledged_by=row['acknowledged_by'],
            created_at=row['created_at']
        ) for row in rows]
        
        return alerts, total
    
    async def acknowledge_alert(self, alert_id: int, acknowledged_by: str = "system") -> bool:
        """Acknowledge an alert"""
        db = await get_database()
        
        await db.execute(
            """UPDATE alert_logs 
               SET is_acknowledged = 1, acknowledged_at = datetime('now'), acknowledged_by = ?
               WHERE id = ?""",
            (acknowledged_by, alert_id)
        )
        
        logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        return True
    
    async def acknowledge_all_alerts(self, acknowledged_by: str = "system") -> int:
        """Acknowledge all active alerts"""
        db = await get_database()
        
        count_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM alert_logs WHERE is_acknowledged = 0"
        )
        count = count_result.get('count', 0) if count_result else 0
        
        await db.execute(
            """UPDATE alert_logs 
               SET is_acknowledged = 1, acknowledged_at = datetime('now'), acknowledged_by = ?
               WHERE is_acknowledged = 0""",
            (acknowledged_by,)
        )
        
        logger.info(f"Acknowledged {count} alerts by {acknowledged_by}")
        return count
    
    async def get_alert_configurations(self, bin_id: Optional[str] = None) -> list[AlertConfiguration]:
        """Get alert configurations"""
        db = await get_database()
        
        if bin_id:
            rows = await db.fetch_all(
                "SELECT * FROM alert_configurations WHERE bin_id = ?",
                (bin_id,)
            )
        else:
            rows = await db.fetch_all("SELECT * FROM alert_configurations")
        
        return [AlertConfiguration(
            id=row['id'],
            bin_id=row['bin_id'],
            alert_type=row['alert_type'],
            threshold_value=row['threshold_value'],
            is_enabled=bool(row['is_enabled']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        ) for row in rows]
    
    async def update_alert_configuration(
        self,
        bin_id: str,
        alert_type: str,
        threshold_value: Optional[int] = None,
        is_enabled: Optional[bool] = None
    ) -> bool:
        """Update alert configuration"""
        db = await get_database()
        
        updates = []
        params = []
        
        if threshold_value is not None:
            updates.append("threshold_value = ?")
            params.append(threshold_value)
        
        if is_enabled is not None:
            updates.append("is_enabled = ?")
            params.append(1 if is_enabled else 0)
        
        if not updates:
            return False
        
        params.extend([bin_id, alert_type])
        
        await db.execute(
            f"""UPDATE alert_configurations 
                SET {', '.join(updates)}, updated_at = datetime('now')
                WHERE bin_id = ? AND alert_type = ?""",
            tuple(params)
        )
        
        return True


# Singleton instance
alert_service = AlertService()
