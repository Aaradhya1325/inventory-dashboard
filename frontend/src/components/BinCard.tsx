import React, { useState, useEffect } from 'react';
import { Clock, Package } from 'lucide-react';
import { BinDisplayData } from '../types';
import {
  getStatusColor,
  getStatusBorderColor,
  getStatusTextColor,
  getFillBarColor,
  formatRelativeTime,
} from '../utils/helpers';
import clsx from 'clsx';

interface BinCardProps {
  bin: BinDisplayData;
  isHighlighted?: boolean;
  onClick?: () => void;
}

export const BinCard: React.FC<BinCardProps> = ({ bin, isHighlighted, onClick }) => {
  const [showHighlight, setShowHighlight] = useState(false);

  useEffect(() => {
    if (isHighlighted) {
      setShowHighlight(true);
      const timer = setTimeout(() => setShowHighlight(false), 1500);
      return () => clearTimeout(timer);
    }
  }, [isHighlighted]);

  const fillBarColor = getFillBarColor(bin.fill_percentage, bin.status);
  const statusColor = getStatusColor(bin.status);
  const statusBorderColor = getStatusBorderColor(bin.status);
  const statusTextColor = getStatusTextColor(bin.status);

  return (
    <div
      onClick={onClick}
      className={clsx(
        'bin-card bg-white rounded-xl shadow-sm border-2 p-4 cursor-pointer',
        statusBorderColor,
        showHighlight && 'update-highlight'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-mono font-medium text-industrial-600">
            {bin.bin_id}
          </span>
          <span
            className={clsx(
              'px-2 py-0.5 rounded-full text-xs font-medium capitalize',
              statusColor,
              'text-white'
            )}
          >
            {bin.status}
          </span>
        </div>
        <span className="text-xs text-industrial-400">
          R{bin.row}P{bin.position}
        </span>
      </div>

      {/* Article Name */}
      <div className="flex items-center space-x-2 mb-3">
        <Package className="w-4 h-4 text-industrial-400" />
        <span className="text-sm font-medium text-industrial-700 truncate">
          {bin.article_name}
        </span>
      </div>

      {/* Quantity Display */}
      <div className="text-center mb-3">
        <span className={clsx('text-4xl font-bold', statusTextColor)}>
          {bin.current_quantity}
        </span>
        <span className="text-sm text-industrial-400 ml-1">
          / {bin.max_capacity}
        </span>
      </div>

      {/* Fill Bar */}
      <div className="mb-3">
        <div className="h-3 bg-industrial-100 rounded-full overflow-hidden">
          <div
            className={clsx('h-full fill-bar rounded-full', fillBarColor)}
            style={{ width: `${Math.min(bin.fill_percentage, 100)}%` }}
          />
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-xs text-industrial-400">0%</span>
          <span className="text-xs font-medium text-industrial-600">
            {bin.fill_percentage}%
          </span>
          <span className="text-xs text-industrial-400">100%</span>
        </div>
      </div>

      {/* Thresholds */}
      <div className="flex justify-between text-xs text-industrial-500 mb-2">
        <span>Low: {bin.min_threshold}</span>
        <span>Critical: {bin.critical_threshold}</span>
      </div>

      {/* Last Updated */}
      <div className="flex items-center justify-center space-x-1 text-xs text-industrial-400 pt-2 border-t border-industrial-100">
        <Clock className="w-3 h-3" />
        <span>{formatRelativeTime(bin.last_updated)}</span>
      </div>
    </div>
  );
};
