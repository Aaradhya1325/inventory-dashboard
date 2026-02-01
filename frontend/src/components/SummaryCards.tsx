import React from 'react';
import { Package, AlertTriangle, XCircle, TrendingUp } from 'lucide-react';
import { InventorySummary } from '../types';
import { formatNumber } from '../utils/helpers';

interface SummaryCardsProps {
  summary: InventorySummary | null;
  loading: boolean;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ summary, loading }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-xl p-6 shadow-sm animate-pulse">
            <div className="h-4 bg-industrial-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-industrial-200 rounded w-1/3"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!summary) return null;

  const cards = [
    {
      title: 'Total Items',
      value: formatNumber(summary.total_items),
      subtitle: `${summary.total_bins} bins`,
      icon: Package,
      color: 'text-primary-600',
      bgColor: 'bg-primary-50',
    },
    {
      title: 'Normal Stock',
      value: summary.normal_count,
      subtitle: 'bins operating normally',
      icon: TrendingUp,
      color: 'text-status-normal',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Low Stock',
      value: summary.low_count + summary.critical_count,
      subtitle: `${summary.critical_count} critical`,
      icon: AlertTriangle,
      color: 'text-status-low',
      bgColor: 'bg-yellow-50',
    },
    {
      title: 'Empty Bins',
      value: summary.empty_count,
      subtitle: 'require restocking',
      icon: XCircle,
      color: 'text-status-empty',
      bgColor: 'bg-red-50',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.title}
          className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-industrial-500">{card.title}</p>
              <p className={`text-3xl font-bold mt-1 ${card.color}`}>
                {card.value}
              </p>
              <p className="text-xs text-industrial-400 mt-1">{card.subtitle}</p>
            </div>
            <div className={`p-3 rounded-xl ${card.bgColor}`}>
              <card.icon className={`w-6 h-6 ${card.color}`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
