-- Seed data for inventory tracking system
-- Insert default bin configurations (2 rows x 5 positions = 10 bins)

INSERT OR IGNORE INTO bin_configurations (bin_id, row, position, article_type, article_name, article_weight_grams, min_threshold, critical_threshold, max_capacity)
VALUES 
    ('BIN-001', 1, 1, 'raw_material', 'Steel Bolts M8', 25.0, 200, 50, 1000),
    ('BIN-002', 1, 2, 'raw_material', 'Aluminum Washers', 5.0, 500, 100, 2000),
    ('BIN-003', 1, 3, 'component', 'Circuit Boards PCB-A', 150.0, 50, 10, 200),
    ('BIN-004', 1, 4, 'component', 'LED Modules', 10.0, 300, 75, 1500),
    ('BIN-005', 1, 5, 'finished', 'Sensor Units', 250.0, 30, 10, 150),
    ('BIN-006', 2, 1, 'raw_material', 'Copper Wires 2mm', 50.0, 100, 25, 500),
    ('BIN-007', 2, 2, 'raw_material', 'Plastic Casings', 75.0, 80, 20, 400),
    ('BIN-008', 2, 3, 'component', 'Power Connectors', 20.0, 150, 40, 800),
    ('BIN-009', 2, 4, 'component', 'Heat Sinks', 100.0, 60, 15, 300),
    ('BIN-010', 2, 5, 'finished', 'Control Modules', 500.0, 20, 5, 100);

-- Insert default alert configurations for each bin
INSERT OR IGNORE INTO alert_configurations (bin_id, alert_type, threshold_value, is_enabled)
SELECT bin_id, 'low_stock', min_threshold, 1 FROM bin_configurations;

INSERT OR IGNORE INTO alert_configurations (bin_id, alert_type, threshold_value, is_enabled)
SELECT bin_id, 'critical_stock', critical_threshold, 1 FROM bin_configurations;

-- Insert initial inventory (random starting values)
INSERT OR IGNORE INTO current_inventory (bin_id, weight_grams, calculated_quantity, last_updated)
VALUES
    ('BIN-001', 12500.0, 500, datetime('now')),
    ('BIN-002', 7500.0, 1500, datetime('now')),
    ('BIN-003', 15000.0, 100, datetime('now')),
    ('BIN-004', 8000.0, 800, datetime('now')),
    ('BIN-005', 18750.0, 75, datetime('now')),
    ('BIN-006', 12500.0, 250, datetime('now')),
    ('BIN-007', 15000.0, 200, datetime('now')),
    ('BIN-008', 8000.0, 400, datetime('now')),
    ('BIN-009', 10000.0, 100, datetime('now')),
    ('BIN-010', 25000.0, 50, datetime('now'));

-- Insert default system settings
INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
VALUES 
    ('alert_cooldown_minutes', '5', 'Minutes between repeated alerts for the same bin'),
    ('data_retention_days', '90', 'Days to keep historical inventory data'),
    ('refresh_interval_seconds', '5', 'Dashboard auto-refresh interval'),
    ('weight_tolerance_grams', '10', 'Tolerance for weight measurement fluctuations');
