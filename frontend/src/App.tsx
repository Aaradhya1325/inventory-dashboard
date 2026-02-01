import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { SummaryCards } from './components/SummaryCards';
import { BinGrid } from './components/BinGrid';
import { AlertPanel } from './components/AlertPanel';
import { AnalyticsCharts } from './components/AnalyticsCharts';
import { useInventory, useAlerts, useWebSocket } from './hooks';
import { BinDisplayData, AlertLog } from './types';

function App() {
  const [highlightedBinId, setHighlightedBinId] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analytics'>('dashboard');

  const {
    bins,
    summary,
    loading: inventoryLoading,
    error: inventoryError,
    refresh: refreshInventory,
    updateBin,
  } = useInventory();

  const {
    activeAlerts,
    loading: alertsLoading,
    acknowledgeAlert,
    acknowledgeAll,
    addAlert,
    refresh: refreshAlerts,
  } = useAlerts();

  // Handle bin update from WebSocket
  const handleBinUpdate = useCallback((data: BinDisplayData | AlertLog) => {
    if ('current_quantity' in data) {
      updateBin(data as BinDisplayData);
      setHighlightedBinId(data.bin_id);
      setLastUpdate(new Date().toISOString());
      
      // Clear highlight after animation
      setTimeout(() => setHighlightedBinId(null), 1500);
    }
  }, [updateBin]);

  // Handle alert from WebSocket
  const handleAlert = useCallback((data: BinDisplayData | AlertLog) => {
    if ('alert_type' in data) {
      addAlert(data as AlertLog);
    }
  }, [addAlert]);

  // WebSocket connection
  const { isConnected } = useWebSocket({
    onBinUpdate: handleBinUpdate,
    onAlert: handleAlert,
    onConnect: () => {
      console.log('WebSocket connected');
      refreshInventory();
      refreshAlerts();
    },
  });

  // Handle refresh
  const handleRefresh = () => {
    refreshInventory();
    refreshAlerts();
    setLastUpdate(new Date().toISOString());
  };

  // Handle alert acknowledgement
  const handleAcknowledge = async (alertId: number) => {
    try {
      await acknowledgeAlert(alertId);
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const handleAcknowledgeAll = async () => {
    try {
      await acknowledgeAll();
    } catch (error) {
      console.error('Failed to acknowledge all alerts:', error);
    }
  };

  return (
    <div className="min-h-screen bg-industrial-100">
      {/* Header */}
      <Header
        summary={summary}
        isConnected={isConnected}
        lastUpdate={lastUpdate}
        onRefresh={handleRefresh}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Error Banner */}
        {inventoryError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-red-700">{inventoryError}</p>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="mb-6 border-b border-industrial-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`pb-4 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'dashboard'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-industrial-500 hover:text-industrial-700'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`pb-4 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'analytics'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-industrial-500 hover:text-industrial-700'
              }`}
            >
              Analytics
            </button>
          </nav>
        </div>

        {activeTab === 'dashboard' ? (
          <>
            {/* Summary Cards */}
            <section className="mb-6">
              <SummaryCards summary={summary} loading={inventoryLoading} />
            </section>

            {/* Main Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
              {/* Bin Grid - Takes 3 columns */}
              <section className="xl:col-span-3">
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h2 className="text-lg font-semibold text-industrial-800 mb-4">
                    Bin Status Overview
                  </h2>
                  <BinGrid
                    bins={bins}
                    highlightedBinId={highlightedBinId}
                    loading={inventoryLoading}
                  />
                </div>
              </section>

              {/* Alert Panel - Takes 1 column */}
              <section className="xl:col-span-1">
                <AlertPanel
                  alerts={activeAlerts}
                  loading={alertsLoading}
                  onAcknowledge={handleAcknowledge}
                  onAcknowledgeAll={handleAcknowledgeAll}
                />
              </section>
            </div>
          </>
        ) : (
          /* Analytics Tab */
          <AnalyticsCharts bins={bins} />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-8 py-4 border-t border-industrial-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-industrial-400">
            Smart Bin Inventory Dashboard • Real-time Tracking System
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
