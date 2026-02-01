import React, { useMemo } from 'react';
import { BinCard } from './BinCard';
import { BinDisplayData } from '../types';

interface BinGridProps {
  bins: BinDisplayData[];
  highlightedBinId?: string | null;
  onBinClick?: (bin: BinDisplayData) => void;
  loading?: boolean;
}

export const BinGrid: React.FC<BinGridProps> = ({
  bins,
  highlightedBinId,
  onBinClick,
  loading,
}) => {
  // Organize bins into rows
  const rows = useMemo(() => {
    const rowMap = new Map<number, BinDisplayData[]>();
    
    bins.forEach((bin) => {
      const existing = rowMap.get(bin.row) || [];
      existing.push(bin);
      rowMap.set(bin.row, existing);
    });

    // Sort each row by position
    rowMap.forEach((rowBins) => {
      rowBins.sort((a, b) => a.position - b.position);
    });

    // Convert to array sorted by row number
    return Array.from(rowMap.entries())
      .sort(([a], [b]) => a - b)
      .map(([rowNum, rowBins]) => ({ rowNum, bins: rowBins }));
  }, [bins]);

  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2].map((rowNum) => (
          <div key={rowNum} className="space-y-2">
            <div className="h-4 bg-industrial-200 rounded w-16 animate-pulse"></div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="bg-white rounded-xl p-4 shadow-sm animate-pulse h-64"
                >
                  <div className="h-4 bg-industrial-200 rounded w-3/4 mb-4"></div>
                  <div className="h-6 bg-industrial-200 rounded w-1/2 mb-4"></div>
                  <div className="h-12 bg-industrial-200 rounded w-full mb-4"></div>
                  <div className="h-3 bg-industrial-200 rounded w-full"></div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (bins.length === 0) {
    return (
      <div className="bg-white rounded-xl p-12 text-center shadow-sm">
        <p className="text-industrial-500">No bins configured</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {rows.map(({ rowNum, bins: rowBins }) => (
        <div key={rowNum} className="space-y-3">
          {/* Row Label */}
          <div className="flex items-center space-x-2">
            <span className="text-sm font-semibold text-industrial-700 bg-industrial-100 px-3 py-1 rounded-lg">
              Row {rowNum}
            </span>
            <div className="flex-1 h-px bg-industrial-200"></div>
          </div>

          {/* Bin Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {rowBins.map((bin) => (
              <BinCard
                key={bin.bin_id}
                bin={bin}
                isHighlighted={bin.bin_id === highlightedBinId}
                onClick={() => onBinClick?.(bin)}
              />
            ))}
          </div>
        </div>
      ))}

      {/* Rack Visualization Label */}
      <div className="flex justify-center pt-4">
        <div className="flex items-center space-x-4 text-xs text-industrial-400">
          <span>← Position 1</span>
          <div className="w-24 h-px bg-industrial-200"></div>
          <span className="font-medium text-industrial-600">Physical Rack Layout</span>
          <div className="w-24 h-px bg-industrial-200"></div>
          <span>Position 5 →</span>
        </div>
      </div>
    </div>
  );
};
