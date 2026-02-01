-- Inventory Dashboard Database Schema
-- Compatible with SQLite and Cloudflare D1

-- Bin configurations table
CREATE TABLE IF NOT EXISTS bin_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id TEXT UNIQUE NOT NULL,
    row INTEGER NOT NULL,
    position INTEGER NOT NULL,
    article_type TEXT NOT NULL DEFAULT 'general',
    article_name TEXT NOT NULL DEFAULT 'Unknown Article',
    article_weight_grams REAL NOT NULL DEFAULT 100,
    min_threshold INTEGER NOT NULL DEFAULT 10,
    critical_threshold INTEGER NOT NULL DEFAULT 5,
    max_capacity INTEGER NOT NULL DEFAULT 100,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(row, position)
);

-- Real-time inventory data table
CREATE TABLE IF NOT EXISTS inventory_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id TEXT NOT NULL,
    weight_grams REAL NOT NULL,
    calculated_quantity INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (bin_id) REFERENCES bin_configurations(bin_id) ON DELETE CASCADE
);

-- Create index for faster queries on inventory_data
CREATE INDEX IF NOT EXISTS idx_inventory_bin_id ON inventory_data(bin_id);
CREATE INDEX IF NOT EXISTS idx_inventory_timestamp ON inventory_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_inventory_bin_timestamp ON inventory_data(bin_id, timestamp);

-- Current inventory snapshot (latest values per bin)
CREATE TABLE IF NOT EXISTS current_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id TEXT UNIQUE NOT NULL,
    weight_grams REAL NOT NULL,
    calculated_quantity INTEGER NOT NULL,
    last_updated TEXT NOT NULL,
    FOREIGN KEY (bin_id) REFERENCES bin_configurations(bin_id) ON DELETE CASCADE
);

-- Alert configurations table
CREATE TABLE IF NOT EXISTS alert_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id TEXT NOT NULL,
    alert_type TEXT NOT NULL CHECK(alert_type IN ('low_stock', 'critical_stock', 'empty', 'overfill')),
    threshold_value INTEGER NOT NULL,
    is_enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (bin_id) REFERENCES bin_configurations(bin_id) ON DELETE CASCADE,
    UNIQUE(bin_id, alert_type)
);

-- Alert logs table
CREATE TABLE IF NOT EXISTS alert_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    message TEXT NOT NULL,
    quantity_at_alert INTEGER NOT NULL,
    threshold_value INTEGER NOT NULL,
    is_acknowledged INTEGER NOT NULL DEFAULT 0,
    acknowledged_at TEXT,
    acknowledged_by TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (bin_id) REFERENCES bin_configurations(bin_id) ON DELETE CASCADE
);

-- Create index for alert logs
CREATE INDEX IF NOT EXISTS idx_alert_logs_bin_id ON alert_logs(bin_id);
CREATE INDEX IF NOT EXISTS idx_alert_logs_created_at ON alert_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_alert_logs_acknowledged ON alert_logs(is_acknowledged);

-- System settings table
CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
