import React from 'react';
import { 
  Activity, 
  Bell, 
  RefreshCw, 
  Wifi, 
  WifiOff,
  Download
} from 'lucide-react';
import { InventorySummary } from '../types';
import { formatRelativeTime } from '../utils/helpers';
import { exportApi, downloadFile } from '../services/api';

interface HeaderProps {
  summary: InventorySummary | null;
  isConnected: boolean;
  lastUpdate: string | null;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  summary,
  isConnected,
  lastUpdate,
  onRefresh,
}) => {
  const handleExport = () => {
    downloadFile(exportApi.getReportUrl(), 'inventory_report.xlsx');
  };

  return (
    <header className="bg-white shadow-sm border-b border-industrial-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary-600 text-white">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-industrial-900">
                Inventory Dashboard
              </h1>
              <p className="text-xs text-industrial-500">
                Smart Bin Tracking System
              </p>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="flex items-center space-x-6">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <>
                  <Wifi className="w-4 h-4 text-status-normal" />
                  <span className="text-sm text-status-normal font-medium">
                    Connected
                  </span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-status-critical" />
                  <span className="text-sm text-status-critical font-medium">
                    Disconnected
                  </span>
                </>
              )}
            </div>

            {/* Last Update */}
            {lastUpdate && (
              <div className="text-sm text-industrial-500">
                Last sync: {formatRelativeTime(lastUpdate)}
              </div>
            )}

            {/* Alert Count */}
            {summary && summary.alerts_active > 0 && (
              <div className="flex items-center space-x-1 px-3 py-1 rounded-full bg-status-critical/10 text-status-critical">
                <Bell className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {summary.alerts_active} Alert{summary.alerts_active !== 1 ? 's' : ''}
                </span>
              </div>
            )}

            {/* Export Button */}
            <button
              onClick={handleExport}
              className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-industrial-600 hover:text-industrial-900 hover:bg-industrial-100 rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>

            {/* Refresh Button */}
            <button
              onClick={onRefresh}
              className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
