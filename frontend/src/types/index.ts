// Bin status types
export type BinStatus = 'normal' | 'low' | 'critical' | 'empty' | 'overfill';

// Bin display data from API
export interface BinDisplayData {
  bin_id: string;
  row: number;
  position: number;
  article_type: string;
  article_name: string;
  current_quantity: number;
  max_capacity: number;
  fill_percentage: number;
  status: BinStatus;
  min_threshold: number;
  critical_threshold: number;
  last_updated: string;
  weight_grams: number;
}

// Bin configuration
export interface BinConfiguration {
  id: number;
  bin_id: string;
  row: number;
  position: number;
  article_type: string;
  article_name: string;
  article_weight_grams: number;
  min_threshold: number;
  critical_threshold: number;
  max_capacity: number;
  created_at: string;
  updated_at: string;
}

// Inventory summary
export interface InventorySummary {
  total_bins: number;
  normal_count: number;
  low_count: number;
  critical_count: number;
  empty_count: number;
  total_items: number;
  alerts_active: number;
}

// Alert log
export interface AlertLog {
  id: number;
  bin_id: string;
  alert_type: string;
  message: string;
  quantity_at_alert: number;
  threshold_value: number;
  is_acknowledged: boolean;
  acknowledged_at: string | null;
  acknowledged_by: string | null;
  created_at: string;
}

// Alert configuration
export interface AlertConfiguration {
  id: number;
  bin_id: string;
  alert_type: string;
  threshold_value: number;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}

// Historical data point
export interface HistoricalDataPoint {
  timestamp: string;
  quantity: number;
  weight_grams: number;
}

// Consumption rate
export interface ConsumptionRate {
  bin_id: string;
  article_name: string;
  daily_average: number;
  weekly_average: number;
  trend: 'increasing' | 'decreasing' | 'stable';
}

// Status distribution for charts
export interface StatusDistribution {
  status: string;
  count: number;
  color: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

// WebSocket message types
export type WSMessageType = 'bin_update' | 'alert' | 'connection' | 'heartbeat' | 'error';

export interface WSMessage {
  type: WSMessageType;
  payload: unknown;
  timestamp: string;
}

export interface BinUpdateMessage extends WSMessage {
  type: 'bin_update';
  payload: BinDisplayData;
}

export interface AlertMessage extends WSMessage {
  type: 'alert';
  payload: AlertLog;
}
