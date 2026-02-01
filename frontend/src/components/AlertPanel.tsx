import React from 'react';
import { AlertTriangle, Bell, Check, CheckCheck, X } from 'lucide-react';
import { AlertLog } from '../types';
import { formatRelativeTime } from '../utils/helpers';
import clsx from 'clsx';

interface AlertPanelProps {
  alerts: AlertLog[];
  loading: boolean;
  onAcknowledge: (alertId: number) => void;
  onAcknowledgeAll: () => void;
}

export const AlertPanel: React.FC<AlertPanelProps> = ({
  alerts,
  loading,
  onAcknowledge,
  onAcknowledgeAll,
}) => {
  const getAlertIcon = (alertType: string) => {
    switch (alertType) {
      case 'critical_stock':
      case 'empty':
        return <AlertTriangle className="w-4 h-4 text-status-empty" />;
      case 'low_stock':
        return <Bell className="w-4 h-4 text-status-low" />;
      default:
        return <Bell className="w-4 h-4 text-status-critical" />;
    }
  };

  const getAlertColor = (alertType: string) => {
    switch (alertType) {
      case 'critical_stock':
      case 'empty':
        return 'border-l-status-empty bg-red-50';
      case 'low_stock':
        return 'border-l-status-low bg-yellow-50';
      default:
        return 'border-l-status-critical bg-orange-50';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="h-6 bg-industrial-200 rounded w-1/3 mb-4 animate-pulse"></div>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-16 bg-industrial-100 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-industrial-100 bg-industrial-50">
        <div className="flex items-center space-x-2">
          <Bell className="w-5 h-5 text-industrial-600" />
          <h3 className="font-semibold text-industrial-800">Active Alerts</h3>
          {alerts.length > 0 && (
            <span className="px-2 py-0.5 bg-status-critical text-white text-xs font-medium rounded-full">
              {alerts.length}
            </span>
          )}
        </div>
        {alerts.length > 0 && (
          <button
            onClick={onAcknowledgeAll}
            className="flex items-center space-x-1 text-xs font-medium text-primary-600 hover:text-primary-700"
          >
            <CheckCheck className="w-4 h-4" />
            <span>Acknowledge All</span>
          </button>
        )}
      </div>

      {/* Alert List */}
      <div className="max-h-80 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="p-8 text-center">
            <Check className="w-12 h-12 text-status-normal mx-auto mb-2" />
            <p className="text-industrial-600 font-medium">All Clear</p>
            <p className="text-sm text-industrial-400">No active alerts</p>
          </div>
        ) : (
          <div className="divide-y divide-industrial-100">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={clsx(
                  'p-3 border-l-4 transition-colors',
                  getAlertColor(alert.alert_type),
                  'alert-pulse'
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="mt-0.5">{getAlertIcon(alert.alert_type)}</div>
                    <div>
                      <p className="text-sm font-medium text-industrial-800">
                        {alert.message}
                      </p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs font-mono text-industrial-500">
                          {alert.bin_id}
                        </span>
                        <span className="text-xs text-industrial-400">•</span>
                        <span className="text-xs text-industrial-400">
                          {formatRelativeTime(alert.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => onAcknowledge(alert.id)}
                    className="p-1 hover:bg-industrial-200 rounded transition-colors"
                    title="Acknowledge"
                  >
                    <X className="w-4 h-4 text-industrial-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
