const API_BASE_URL = '/api';

// Generic fetch wrapper with error handling
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || error.detail || 'Request failed');
  }

  return response.json();
}

// Bins API
export const binsApi = {
  getAll: () => fetchApi<{ success: boolean; data: unknown[] }>('/bins'),
  
  getSummary: () => fetchApi<{ success: boolean; data: unknown }>('/bins/summary'),
  
  getById: (binId: string) => 
    fetchApi<{ success: boolean; data: unknown }>(`/bins/${binId}`),
  
  updateConfig: (binId: string, config: Record<string, unknown>) =>
    fetchApi<{ success: boolean; data: unknown }>(`/bins/${binId}/config`, {
      method: 'PUT',
      body: JSON.stringify(config),
    }),
  
  getHistory: (binId: string, startDate: string, endDate: string) =>
    fetchApi<{ success: boolean; data: unknown[] }>(
      `/bins/${binId}/history?start_date=${startDate}&end_date=${endDate}`
    ),
  
  getConsumption: (binId: string) =>
    fetchApi<{ success: boolean; data: unknown }>(`/bins/${binId}/consumption`),
};

// Alerts API
export const alertsApi = {
  getActive: () => fetchApi<{ success: boolean; data: unknown[] }>('/alerts/active'),
  
  getHistory: (page = 1, limit = 50, binId?: string) => {
    const params = new URLSearchParams({ page: String(page), limit: String(limit) });
    if (binId) params.append('bin_id', binId);
    return fetchApi<{ success: boolean; data: unknown[]; pagination: unknown }>(
      `/alerts/history?${params}`
    );
  },
  
  acknowledge: (alertId: number, acknowledgedBy = 'user') =>
    fetchApi<{ success: boolean; message: string }>(`/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      body: JSON.stringify({ acknowledged_by: acknowledgedBy }),
    }),
  
  acknowledgeAll: (acknowledgedBy = 'user') =>
    fetchApi<{ success: boolean; message: string }>('/alerts/acknowledge-all', {
      method: 'POST',
      body: JSON.stringify({ acknowledged_by: acknowledgedBy }),
    }),
  
  getConfigurations: (binId?: string) => {
    const params = binId ? `?bin_id=${binId}` : '';
    return fetchApi<{ success: boolean; data: unknown[] }>(`/alerts/configurations${params}`);
  },
  
  updateConfiguration: (binId: string, alertType: string, updates: Record<string, unknown>) =>
    fetchApi<{ success: boolean; message: string }>(
      `/alerts/configurations/${binId}/${alertType}`,
      {
        method: 'PUT',
        body: JSON.stringify(updates),
      }
    ),
};

// Analytics API
export const analyticsApi = {
  getTrends: (startDate: string, endDate: string) =>
    fetchApi<{ success: boolean; data: unknown[] }>(
      `/analytics/trends?start_date=${startDate}&end_date=${endDate}`
    ),
  
  getConsumption: () =>
    fetchApi<{ success: boolean; data: unknown[] }>('/analytics/consumption'),
  
  getComparison: () =>
    fetchApi<{ success: boolean; data: unknown[] }>('/analytics/comparison'),
  
  getStatusDistribution: () =>
    fetchApi<{ success: boolean; data: { distribution: unknown[]; total: number } }>(
      '/analytics/status-distribution'
    ),
};

// Export API - returns download URLs
export const exportApi = {
  getInventoryUrl: () => `${API_BASE_URL}/export/inventory`,
  
  getHistoryUrl: (startDate: string, endDate: string, binIds?: string[]) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    if (binIds?.length) params.append('bin_ids', binIds.join(','));
    return `${API_BASE_URL}/export/history?${params}`;
  },
  
  getAlertsUrl: (startDate?: string, endDate?: string, includeAcknowledged = true) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    params.append('include_acknowledged', String(includeAcknowledged));
    return `${API_BASE_URL}/export/alerts?${params}`;
  },
  
  getReportUrl: () => `${API_BASE_URL}/export/report`,
};

// Health check
export const healthApi = {
  check: () => fetchApi<{ status: string; websocket_clients: number }>('/health'.replace('/api', '')),
};

// Helper function to download files
export function downloadFile(url: string, filename: string): void {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
