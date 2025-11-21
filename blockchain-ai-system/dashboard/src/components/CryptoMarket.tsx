'use client';

import { useState } from 'react';
import { TrendingDown, TrendingUp, Star, RefreshCw } from 'lucide-react';

import type { CoinData } from '../services/coingecko';
import { coinGeckoService } from '../services/coingecko';

interface CryptoMarketProps {
  data: CoinData[];
}

export default function CryptoMarket({ data }: CryptoMarketProps) {
  const [coins, setCoins] = useState<CoinData[]>(data);
  const [refreshing, setRefreshing] = useState(false);
  const [favorites, setFavorites] = useState<string[]>([]);

  const refreshData = async () => {
    setRefreshing(true);
    try {
      const newData = await coinGeckoService.getTopCryptos(20);
      setCoins(newData);
    } catch (error) {
      console.error('Failed to refresh data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const toggleFavorite = (coinId: string) => {
    setFavorites((prev) =>
      prev.includes(coinId) ? prev.filter((id) => id !== coinId) : [...prev, coinId],
    );
  };

  const formatPrice = (price: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: price < 1 ? 4 : 2,
    }).format(price);

  const formatPercent = (percent: number) => `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">📊 Live Crypto Market</h2>
        <button
          type="button"
          onClick={refreshData}
          disabled={refreshing}
          className="flex items-center space-x-2 bg-blockchain-blue px-4 py-2 rounded-lg disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="grid gap-4">
        {coins.map((coin) => {
          const sparkline = coin.sparkline_in_7d.price.slice(-20);
          const min = Math.min(...sparkline);
          const max = Math.max(...sparkline);

          return (
            <div
              key={coin.id}
              className="bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <button
                    type="button"
                    onClick={() => toggleFavorite(coin.id)}
                    className="text-yellow-400 hover:text-yellow-300"
                  >
                    <Star
                      className={`w-5 h-5 ${favorites.includes(coin.id) ? 'fill-current' : ''}`}
                    />
                  </button>
                  <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-sm font-semibold uppercase">
                    {coin.symbol}
                  </div>
                  <div>
                    <h3 className="font-semibold">{coin.name}</h3>
                    <p className="text-gray-400 text-sm uppercase">{coin.symbol}</p>
                  </div>
                </div>

                <div className="text-right">
                  <div className="font-bold text-lg">{formatPrice(coin.current_price)}</div>
                  <div
                    className={`flex items-center space-x-1 ${
                      coin.price_change_percentage_24h >= 0
                        ? 'text-green-400'
                        : 'text-red-400'
                    }`}
                  >
                    {coin.price_change_percentage_24h >= 0 ? (
                      <TrendingUp className="w-4 h-4" />
                    ) : (
                      <TrendingDown className="w-4 h-4" />
                    )}
                    <span>{formatPercent(coin.price_change_percentage_24h)}</span>
                  </div>
                </div>
              </div>

              <div className="mt-3 h-10 w-full">
                <svg viewBox="0 0 100 40" className="w-full h-full">
                  <path
                    d={sparkline
                      .map((price, index) => {
                        const x = (index / (sparkline.length - 1)) * 100;
                        const y = 40 - ((price - min) / (max - min || 1)) * 40;
                        return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
                      })
                      .join(' ')}
                    stroke={coin.price_change_percentage_24h >= 0 ? '#10B981' : '#EF4444'}
                    strokeWidth="2"
                    fill="none"
                  />
                </svg>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
