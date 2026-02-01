import logging
from pathlib import Path
import random

from app.database.connection import get_database

logger = logging.getLogger(__name__)


async def run_migrations() -> None:
    """Run database migrations"""
    db = await get_database()
    
    logger.info("Running database migrations...")
    
    # Read schema
    schema_path = Path(__file__).parent / "schema.sql"
    schema = schema_path.read_text()
    
    # Use executescript for SQLite which handles multiple statements properly
    try:
        await db.executescript(schema)
        logger.info("Schema executed successfully")
    except Exception as e:
        logger.warning(f"Schema execution warning (may be normal for existing tables): {e}")
    
    # Insert default settings
    default_settings = [
        ('default_low_threshold', '10', 'Default low stock threshold for new bins'),
        ('default_critical_threshold', '5', 'Default critical stock threshold for new bins'),
        ('data_retention_days', '90', 'Number of days to retain historical data'),
        ('alert_cooldown_minutes', '30', 'Minimum time between repeated alerts for same bin'),
    ]
    
    for key, value, desc in default_settings:
        try:
            await db.execute(
                """INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
                   VALUES (?, ?, ?)""",
                (key, value, desc)
            )
        except Exception:
            pass
    
    logger.info("Database migrations completed successfully")


async def seed_default_bins() -> None:
    """Seed default bin configurations"""
    db = await get_database()
    
    logger.info("Checking for existing bins...")
    
    # Check if bins already exist
    result = await db.fetch_one("SELECT COUNT(*) as count FROM bin_configurations")
    if result and result.get('count', 0) > 0:
        logger.info("Bins already exist, skipping seed")
        return
    
    logger.info("Seeding default bin configurations...")
    
    # Article types for bins
    article_types = [
        ('screws', 'M4 Screws', 2.5),
        ('nuts', 'M4 Nuts', 1.8),
        ('washers', 'M4 Washers', 0.5),
        ('bolts', 'M6 Bolts', 8.2),
        ('clips', 'Cable Clips', 1.2),
        ('connectors', 'Wire Connectors', 3.5),
        ('terminals', 'Ring Terminals', 2.1),
        ('grommets', 'Rubber Grommets', 4.0),
        ('spacers', 'Nylon Spacers', 0.8),
        ('rivets', 'Pop Rivets', 1.5),
    ]
    
    article_index = 0
    for row in range(1, 3):  # 2 rows
        for position in range(1, 6):  # 5 positions
            bin_id = f"BIN-R{row}P{position}"
            article_type, article_name, article_weight = article_types[article_index]
            
            # Insert bin configuration
            await db.execute(
                """INSERT INTO bin_configurations 
                   (bin_id, row, position, article_type, article_name, article_weight_grams, 
                    min_threshold, critical_threshold, max_capacity)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (bin_id, row, position, article_type, article_name, article_weight, 10, 5, 100)
            )
            
            # Initialize current inventory with random starting quantity
            initial_qty = random.randint(20, 80)
            initial_weight = initial_qty * article_weight
            
            await db.execute(
                """INSERT INTO current_inventory (bin_id, weight_grams, calculated_quantity, last_updated)
                   VALUES (?, ?, ?, datetime('now'))""",
                (bin_id, initial_weight, initial_qty)
            )
            
            # Create default alert configurations
            await db.execute(
                """INSERT INTO alert_configurations (bin_id, alert_type, threshold_value, is_enabled)
                   VALUES (?, 'low_stock', 10, 1)""",
                (bin_id,)
            )
            await db.execute(
                """INSERT INTO alert_configurations (bin_id, alert_type, threshold_value, is_enabled)
                   VALUES (?, 'critical_stock', 5, 1)""",
                (bin_id,)
            )
            
            article_index += 1
    
    logger.info("Default bin configurations seeded successfully")
