import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { BarChart3, TrendingUp, PieChartIcon } from 'lucide-react';
import { analyticsApi, binsApi } from '../services/api';
import { BinDisplayData, StatusDistribution, HistoricalDataPoint } from '../types';
import { getDaysAgoISO, getTodayISO } from '../utils/helpers';

interface AnalyticsChartsProps {
  bins: BinDisplayData[];
}

export const AnalyticsCharts: React.FC<AnalyticsChartsProps> = ({ bins }) => {
  const [selectedBin, setSelectedBin] = useState<string>(bins[0]?.bin_id || '');
  const [historicalData, setHistoricalData] = useState<HistoricalDataPoint[]>([]);
  const [statusDistribution, setStatusDistribution] = useState<StatusDistribution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedBin]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      // Fetch historical data for selected bin
      if (selectedBin) {
        const historyResponse = await binsApi.getHistory(
          selectedBin,
          getDaysAgoISO(7),
          getTodayISO()
        );
        if (historyResponse.success) {
          setHistoricalData(historyResponse.data as HistoricalDataPoint[]);
        }
      }

      // Fetch status distribution
      const statusResponse = await analyticsApi.getStatusDistribution();
      if (statusResponse.success) {
        setStatusDistribution(statusResponse.data.distribution as StatusDistribution[]);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Prepare data for bar chart (current inventory levels)
  const inventoryBarData = bins.map((bin) => ({
    name: bin.bin_id.replace('BIN-', ''),
    quantity: bin.current_quantity,
    capacity: bin.max_capacity,
    fill: bin.status === 'normal' ? '#22c55e' : 
          bin.status === 'low' ? '#eab308' :
          bin.status === 'critical' ? '#f97316' : '#ef4444',
  }));

  // Format historical data for line chart
  const lineChartData = historicalData.map((point) => ({
    time: new Date(point.timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
    }),
    quantity: point.quantity,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 shadow-lg rounded-lg border border-industrial-200">
          <p className="text-sm font-medium text-industrial-800">{label}</p>
          <p className="text-sm text-industrial-600">
            Quantity: <span className="font-bold">{payload[0].value}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Current Inventory Levels - Bar Chart */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center space-x-2 mb-4">
          <BarChart3 className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-industrial-800">
            Current Inventory Levels
          </h3>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={inventoryBarData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#e2e8f0' }}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#e2e8f0' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="quantity" 
                radius={[4, 4, 0, 0]}
                fill="#3b82f6"
              >
                {inventoryBarData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row - Trend and Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quantity Trend - Line Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-semibold text-industrial-800">
                Quantity Trend
              </h3>
            </div>
            <select
              value={selectedBin}
              onChange={(e) => setSelectedBin(e.target.value)}
              className="text-sm border border-industrial-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {bins.map((bin) => (
                <option key={bin.bin_id} value={bin.bin_id}>
                  {bin.bin_id} - {bin.article_name}
                </option>
              ))}
            </select>
          </div>
          <div className="h-48">
            {loading ? (
              <div className="h-full flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>
            ) : lineChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={lineChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis 
                    dataKey="time" 
                    tick={{ fontSize: 10, fill: '#64748b' }}
                    axisLine={{ stroke: '#e2e8f0' }}
                  />
                  <YAxis 
                    tick={{ fontSize: 12, fill: '#64748b' }}
                    axisLine={{ stroke: '#e2e8f0' }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line 
                    type="monotone" 
                    dataKey="quantity" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6', r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-industrial-400">
                No historical data available
              </div>
            )}
          </div>
        </div>

        {/* Status Distribution - Pie Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center space-x-2 mb-4">
            <PieChartIcon className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-industrial-800">
              Status Distribution
            </h3>
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusDistribution.filter(s => s.count > 0)}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={2}
                  dataKey="count"
                  nameKey="status"
                  label={({ status, count }) => `${status}: ${count}`}
                  labelLine={false}
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend 
                  verticalAlign="bottom" 
                  height={36}
                  formatter={(value) => <span className="text-sm text-industrial-600">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
