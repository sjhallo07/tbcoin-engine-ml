'use client';

import React, { useEffect, useState } from 'react';
import RealTimeCharts from '../components/RealTimeCharts';

interface CoinData {
  id: string;
  name: string;
  symbol: string;
  current_price: number;
  price_change_percentage_24h: number;
  market_cap: number;
  sparkline_in_7d?: { price?: number[] };
}

export default function Dashboard() {
  const [coins, setCoins] = useState<CoinData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void fetchMarketData();
  }, []);

  const fetchMarketData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/market/data?limit=10');
      const data = await response.json();
      setCoins(Array.isArray(data.data) ? data.data : []);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-6">AI Blockchain Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {coins.map((coin) => (
          <div key={coin.id} className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-xl font-semibold">{coin.name}</h3>
            <p className="text-gray-400">{coin.symbol.toUpperCase()}</p>
            <div className="mt-4">
              <p className="text-2xl">${coin.current_price.toLocaleString()}</p>
              <p
                className={
                  coin.price_change_percentage_24h >= 0 ? 'text-green-400' : 'text-red-400'
                }
              >
                {coin.price_change_percentage_24h.toFixed(2)}%
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Live view section */}
      <div className="mt-12">
        <h2 className="text-2xl font-semibold mb-4">Live view</h2>
        <RealTimeCharts data={coins.slice(0, 6)} />
      </div>

      <div className="mt-8">
        <button
          onClick={() => void fetchMarketData()}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg"
        >
          Refresh Data
        </button>
      </div>
    </div>
  );
}
