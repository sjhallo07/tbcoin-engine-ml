'use client';

import { useEffect, useState } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import type { CoinData } from '../services/coingecko';

function formatTimestamp(timestamp: number) {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default function RealTimeCharts({ data }: { data: CoinData[] }) {
  const [chartData, setChartData] = useState(() =>
    data.slice(0, 10).map((coin) => ({
      name: coin.name,
      prices: coin.sparkline_in_7d.price.slice(-24).map((price, idx) => ({
        timestamp: Date.now() - (24 - idx) * 60 * 60 * 1_000,
        price,
      })),
    })),
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setChartData((prev) =>
        prev.map((entry) => ({
          ...entry,
          prices: [...entry.prices.slice(1), { timestamp: Date.now(), price: entry.prices.at(-1)?.price ?? 0 }],
        })),
      );
    }, 10_000);

    return () => clearInterval(interval);
  }, []);

  if (!chartData.length) {
    return <div className="text-gray-300">No chart data available.</div>;
  }

  return (
    <div className="space-y-6">
      {chartData.map((coin) => (
        <div key={coin.name} className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">{coin.name}</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={coin.prices}>
                <defs>
                  <linearGradient id={`color${coin.name}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatTimestamp}
                  stroke="#9CA3AF"
                  tick={{ fill: '#9CA3AF' }}
                />
                <YAxis stroke="#9CA3AF" tick={{ fill: '#9CA3AF' }} domain={['auto', 'auto']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', color: '#E5E7EB' }}
                  labelFormatter={(timestamp) => formatTimestamp(Number(timestamp))}
                  formatter={(value: number) => [`$${value.toLocaleString()}`, 'Price']}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="#3B82F6"
                  fillOpacity={1}
                  fill={`url(#color${coin.name})`}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      ))}
    </div>
  );
}
