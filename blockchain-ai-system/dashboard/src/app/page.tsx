'use client';

import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';

import ArbitrageDetector from '../components/ArbitrageDetector';
import AIPredictions from '../components/AIPredictions';
import CryptoMarket from '../components/CryptoMarket';
import GasOptimizer from '../components/GasOptimizer';
import { coinGeckoService, type CoinData } from '../services/coingecko';
import { deepSeekService } from '../services/deepseek';

const RealTimeCharts = dynamic(() => import('../components/RealTimeCharts'), {
  ssr: false,
  loading: () => <div className="text-white">Loading charts...</div>,
});

type PredictionEntry = CoinData & { prediction: Awaited<ReturnType<typeof deepSeekService.analyzeMarketTrends>> };

export default function DashboardPage() {
  const [marketData, setMarketData] = useState<CoinData[]>([]);
  const [predictions, setPredictions] = useState<PredictionEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'market' | 'predictions' | 'gas' | 'arbitrage' | 'charts'>(
    'market',
  );

  useEffect(() => {
    const initialize = async () => {
      try {
        const key = process.env.NEXT_PUBLIC_DEEPSEEK_API_KEY;
        if (key) {
          deepSeekService.initialize(key);
        }
        const coins = await coinGeckoService.getTopCryptos(20);
        setMarketData(coins);
        const aiPredictions = await Promise.all(
          coins.slice(0, 5).map(async (coin) => ({
            ...coin,
            prediction: await deepSeekService.analyzeMarketTrends(coin),
          })),
        );
        setPredictions(aiPredictions);
      } catch (error) {
        console.error('Dashboard initialization error:', error);
      } finally {
        setLoading(false);
      }
    };

    void initialize();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-blockchain-dark flex items-center justify-center">
        <div className="text-white text-xl">Loading AI Blockchain Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-blockchain-dark text-white">
      <header className="bg-gray-900 border-b border-gray-700 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blockchain-purple">
            🤖 AI Blockchain Predictive Dashboard
          </h1>
          <div className="flex space-x-4">
            <button
              type="button"
              className="bg-blockchain-blue px-4 py-2 rounded-lg hover:bg-blue-600 transition"
            >
              Connect Wallet
            </button>
            <button
              type="button"
              className="bg-blockchain-green px-4 py-2 rounded-lg hover:bg-green-600 transition"
            >
              Settings
            </button>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto flex space-x-8 p-4">
          {(['market', 'predictions', 'gas', 'arbitrage', 'charts'] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg capitalize ${
                activeTab === tab ? 'bg-blockchain-purple text-white' : 'text-gray-300 hover:text-white'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </nav>

      <main className="container mx-auto p-6 space-y-6">
        {activeTab === 'market' && <CryptoMarket data={marketData} />}
        {activeTab === 'predictions' && <AIPredictions predictions={predictions} />}
        {activeTab === 'gas' && <GasOptimizer />}
        {activeTab === 'arbitrage' && <ArbitrageDetector />}
        {activeTab === 'charts' && <RealTimeCharts data={marketData} />}
      </main>
    </div>
  );
}
