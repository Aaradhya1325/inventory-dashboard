import { useState, useEffect, useCallback } from 'react';
import { binsApi } from '../services/api';
import { BinDisplayData, InventorySummary } from '../types';

export function useInventory() {
  const [bins, setBins] = useState<BinDisplayData[]>([]);
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInventory = useCallback(async () => {
    try {
      setError(null);
      const [binsResponse, summaryResponse] = await Promise.all([
        binsApi.getAll(),
        binsApi.getSummary(),
      ]);

      if (binsResponse.success) {
        setBins(binsResponse.data as BinDisplayData[]);
      }
      if (summaryResponse.success) {
        setSummary(summaryResponse.data as InventorySummary);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch inventory');
      console.error('Failed to fetch inventory:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateBin = useCallback((updatedBin: BinDisplayData) => {
    setBins((prevBins) =>
      prevBins.map((bin) =>
        bin.bin_id === updatedBin.bin_id ? updatedBin : bin
      )
    );
    // Refresh summary when a bin is updated
    binsApi.getSummary().then((response) => {
      if (response.success) {
        setSummary(response.data as InventorySummary);
      }
    });
  }, []);

  useEffect(() => {
    fetchInventory();
    
    // Set up auto-refresh fallback every 30 seconds
    const interval = setInterval(fetchInventory, 30000);
    
    return () => clearInterval(interval);
  }, [fetchInventory]);

  return {
    bins,
    summary,
    loading,
    error,
    refresh: fetchInventory,
    updateBin,
  };
}
