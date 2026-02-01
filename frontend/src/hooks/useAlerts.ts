import { useState, useEffect, useCallback } from 'react';
import { alertsApi } from '../services/api';
import { AlertLog } from '../types';

export function useAlerts() {
  const [activeAlerts, setActiveAlerts] = useState<AlertLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    try {
      setError(null);
      const response = await alertsApi.getActive();
      if (response.success) {
        setActiveAlerts(response.data as AlertLog[]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch alerts');
      console.error('Failed to fetch alerts:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const addAlert = useCallback((alert: AlertLog) => {
    setActiveAlerts((prev) => [alert, ...prev]);
  }, []);

  const acknowledgeAlert = useCallback(async (alertId: number) => {
    try {
      await alertsApi.acknowledge(alertId);
      setActiveAlerts((prev) => prev.filter((a) => a.id !== alertId));
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
      throw err;
    }
  }, []);

  const acknowledgeAll = useCallback(async () => {
    try {
      await alertsApi.acknowledgeAll();
      setActiveAlerts([]);
    } catch (err) {
      console.error('Failed to acknowledge all alerts:', err);
      throw err;
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
    
    // Refresh alerts every minute
    const interval = setInterval(fetchAlerts, 60000);
    
    return () => clearInterval(interval);
  }, [fetchAlerts]);

  return {
    activeAlerts,
    loading,
    error,
    refresh: fetchAlerts,
    addAlert,
    acknowledgeAlert,
    acknowledgeAll,
  };
}
