import logging
from typing import Optional
from datetime import datetime, timedelta

from database import get_database
from models import (
    BinConfiguration, BinDisplayData, BinStatus, 
    InventorySummary, HistoricalDataPoint, BinConfigUpdate
)

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for managing inventory data"""
    
    async def get_all_bin_configurations(self) -> list[BinConfiguration]:
        """Get all bin configurations"""
        db = await get_database()
        rows = await db.fetch_all(
            "SELECT * FROM bin_configurations ORDER BY row, position"
        )
        return [BinConfiguration(**row) for row in rows]
    
    async def get_bin_configuration(self, bin_id: str) -> Optional[BinConfiguration]:
        """Get bin configuration by ID"""
        db = await get_database()
        row = await db.fetch_one(
            "SELECT * FROM bin_configurations WHERE bin_id = ?",
            (bin_id,)
        )
        return BinConfiguration(**row) if row else None
    
    async def update_bin_configuration(self, bin_id: str, updates: BinConfigUpdate) -> bool:
        """Update bin configuration"""
        db = await get_database()
        
        # Build update query dynamically
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values()) + [bin_id]
        
        await db.execute(
            f"UPDATE bin_configurations SET {set_clause}, updated_at = datetime('now') WHERE bin_id = ?",
            tuple(values)
        )
        return True
    
    async def record_inventory_data(
        self, 
        bin_id: str, 
        weight_grams: float, 
        calculated_quantity: int,
        timestamp: str
    ) -> int:
        """Record new inventory data from bin sensor"""
        db = await get_database()
        
        # Insert into historical data
        row_id = await db.execute(
            """INSERT INTO inventory_data (bin_id, weight_grams, calculated_quantity, timestamp)
               VALUES (?, ?, ?, ?)""",
            (bin_id, weight_grams, calculated_quantity, timestamp)
        )
        
        # Update or insert current inventory
        existing = await db.fetch_one(
            "SELECT id FROM current_inventory WHERE bin_id = ?",
            (bin_id,)
        )
        
        if existing:
            await db.execute(
                """UPDATE current_inventory 
                   SET weight_grams = ?, calculated_quantity = ?, last_updated = ?
                   WHERE bin_id = ?""",
                (weight_grams, calculated_quantity, timestamp, bin_id)
            )
        else:
            await db.execute(
                """INSERT INTO current_inventory (bin_id, weight_grams, calculated_quantity, last_updated)
                   VALUES (?, ?, ?, ?)""",
                (bin_id, weight_grams, calculated_quantity, timestamp)
            )
        
        logger.debug(f"Recorded inventory data for {bin_id}: qty={calculated_quantity}")
        return row_id
    
    async def get_current_inventory(self) -> list[BinDisplayData]:
        """Get current inventory for all bins with display data"""
        db = await get_database()
        
        rows = await db.fetch_all("""
            SELECT 
                bc.bin_id,
                bc.row,
                bc.position,
                bc.article_type,
                bc.article_name,
                bc.min_threshold,
                bc.critical_threshold,
                bc.max_capacity,
                COALESCE(ci.weight_grams, 0) as weight_grams,
                COALESCE(ci.calculated_quantity, 0) as calculated_quantity,
                COALESCE(ci.last_updated, datetime('now')) as last_updated
            FROM bin_configurations bc
            LEFT JOIN current_inventory ci ON bc.bin_id = ci.bin_id
            ORDER BY bc.row, bc.position
        """)
        
        result = []
        for row in rows:
            status = self._calculate_status(
                row['calculated_quantity'],
                row['min_threshold'],
                row['critical_threshold'],
                row['max_capacity']
            )
            fill_percentage = min(100, round((row['calculated_quantity'] / row['max_capacity']) * 100))
            
            result.append(BinDisplayData(
                bin_id=row['bin_id'],
                row=row['row'],
                position=row['position'],
                article_type=row['article_type'],
                article_name=row['article_name'],
                current_quantity=row['calculated_quantity'],
                max_capacity=row['max_capacity'],
                fill_percentage=fill_percentage,
                status=status,
                min_threshold=row['min_threshold'],
                critical_threshold=row['critical_threshold'],
                last_updated=row['last_updated'],
                weight_grams=row['weight_grams']
            ))
        
        return result
    
    async def get_bin_display_data(self, bin_id: str) -> Optional[BinDisplayData]:
        """Get single bin display data"""
        inventory = await self.get_current_inventory()
        for bin_data in inventory:
            if bin_data.bin_id == bin_id:
                return bin_data
        return None
    
    def _calculate_status(
        self,
        quantity: int,
        min_threshold: int,
        critical_threshold: int,
        max_capacity: int
    ) -> BinStatus:
        """Calculate bin status based on quantity and thresholds"""
        if quantity <= 0:
            return BinStatus.EMPTY
        if quantity > max_capacity:
            return BinStatus.OVERFILL
        if quantity <= critical_threshold:
            return BinStatus.CRITICAL
        if quantity <= min_threshold:
            return BinStatus.LOW
        return BinStatus.NORMAL
    
    async def get_inventory_summary(self) -> InventorySummary:
        """Get inventory summary statistics"""
        inventory = await self.get_current_inventory()
        db = await get_database()
        
        active_alerts = await db.fetch_one(
            "SELECT COUNT(*) as count FROM alert_logs WHERE is_acknowledged = 0"
        )
        
        return InventorySummary(
            total_bins=len(inventory),
            normal_count=sum(1 for b in inventory if b.status == BinStatus.NORMAL),
            low_count=sum(1 for b in inventory if b.status == BinStatus.LOW),
            critical_count=sum(1 for b in inventory if b.status == BinStatus.CRITICAL),
            empty_count=sum(1 for b in inventory if b.status == BinStatus.EMPTY),
            total_items=sum(b.current_quantity for b in inventory),
            alerts_active=active_alerts.get('count', 0) if active_alerts else 0
        )
    
    async def get_historical_data(
        self,
        bin_id: str,
        start_date: str,
        end_date: str,
        limit: int = 1000
    ) -> list[HistoricalDataPoint]:
        """Get historical data for a bin"""
        db = await get_database()
        
        rows = await db.fetch_all(
            """SELECT timestamp, calculated_quantity as quantity, weight_grams
               FROM inventory_data
               WHERE bin_id = ? AND timestamp BETWEEN ? AND ?
               ORDER BY timestamp ASC
               LIMIT ?""",
            (bin_id, start_date, end_date, limit)
        )
        
        return [HistoricalDataPoint(**row) for row in rows]
    
    async def get_all_historical_data(
        self,
        start_date: str,
        end_date: str
    ) -> list[dict]:
        """Get historical data for all bins"""
        bins = await self.get_all_bin_configurations()
        
        result = []
        for bin_config in bins:
            data = await self.get_historical_data(bin_config.bin_id, start_date, end_date)
            result.append({
                "bin_id": bin_config.bin_id,
                "data": [d.model_dump() for d in data]
            })
        
        return result
    
    async def get_consumption_rate(self, bin_id: str) -> dict:
        """Calculate consumption rate for a bin"""
        db = await get_database()
        
        # Get data from last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        rows = await db.fetch_all(
            """SELECT timestamp, calculated_quantity as quantity
               FROM inventory_data
               WHERE bin_id = ? AND timestamp >= ?
               ORDER BY timestamp ASC""",
            (bin_id, thirty_days_ago)
        )
        
        if len(rows) < 2:
            return {
                "daily_average": 0,
                "weekly_average": 0,
                "trend": "stable"
            }
        
        # Calculate daily consumption
        total_consumption = 0
        for i in range(1, len(rows)):
            diff = rows[i-1]['quantity'] - rows[i]['quantity']
            if diff > 0:
                total_consumption += diff
        
        # Calculate days covered
        first_ts = datetime.fromisoformat(rows[0]['timestamp'].replace('Z', '+00:00'))
        last_ts = datetime.fromisoformat(rows[-1]['timestamp'].replace('Z', '+00:00'))
        days_covered = max(1, (last_ts - first_ts).days)
        
        daily_average = total_consumption / days_covered
        weekly_average = daily_average * 7
        
        # Determine trend
        midpoint = len(rows) // 2
        first_half_avg = sum(r['quantity'] for r in rows[:midpoint]) / max(1, midpoint)
        second_half_avg = sum(r['quantity'] for r in rows[midpoint:]) / max(1, len(rows) - midpoint)
        
        threshold = 0.1
        change_ratio = (second_half_avg - first_half_avg) / max(1, first_half_avg)
        
        if change_ratio > threshold:
            trend = "increasing"
        elif change_ratio < -threshold:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "daily_average": round(daily_average, 1),
            "weekly_average": round(weekly_average, 1),
            "trend": trend
        }
    
    async def cleanup_old_data(self, retention_days: int = 90) -> int:
        """Clean up old historical data"""
        db = await get_database()
        cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()
        
        result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM inventory_data WHERE timestamp < ?",
            (cutoff_date,)
        )
        count = result.get('count', 0) if result else 0
        
        await db.execute(
            "DELETE FROM inventory_data WHERE timestamp < ?",
            (cutoff_date,)
        )
        
        logger.info(f"Cleaned up {count} old inventory records")
        return count


# Singleton instance
inventory_service = InventoryService()
