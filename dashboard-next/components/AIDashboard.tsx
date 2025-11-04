'use client';

import { useEffect, useState } from 'react';

type TokenDisplay = {
  name: string;
  symbol: string;
  logo: string | null;
};

type SolanaOverview = {
  price: number;
  change24h: number;
  marketCap: number;
  volume24h: number;
  timestamp: string;
  display?: TokenDisplay;
};

type MarketAnalysis = {
  status: string;
  analysis: {
    sentiment: string;
    confidence: number;
    recommendation: string;
    keyLevels: { support: number; resistance: number };
    timestamp: string;
  };
};

type PredictionResponse = {
  status: string;
  prediction: {
    predictedPrice: number;
    confidence: number;
    timeframe: string;
    direction: string;
    timestamp: string;
  };
};

type PerformanceResponse = {
  status: string;
  performance: {
    models: {
      pricePrediction: { accuracy: number; lastTraining: string };
      sentimentAnalysis: { accuracy: number; lastTraining: string };
      anomalyDetection: { accuracy: number; lastTraining: string };
    };
    tradingPerformance: {
      totalTrades: number;
      winRate: number;
      totalProfit: number;
      sharpeRatio: number;
    };
    lastUpdated: string;
  };
};

export function AIDashboard() {
  const [solanaOverview, setSolanaOverview] = useState<SolanaOverview | null>(null);
  const [marketAnalysis, setMarketAnalysis] = useState<MarketAnalysis | null>(null);
  const [predictions, setPredictions] = useState<PredictionResponse | null>(null);
  const [performance, setPerformance] = useState<PerformanceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSolanaOverview = async () => {
      try {
        const res = await fetch('/api/solana/price');
        if (!res.ok) throw new Error(`Failed to load Solana price (${res.status})`);
        const json = await res.json();
        setSolanaOverview(json.data ?? null);
      } catch (err) {
        console.warn('[AIDashboard] Failed to fetch Solana price overview', err);
      }
    };

    fetchSolanaOverview();
  }, []);

  const testAISystem = async () => {
    setLoading(true);
    setError(null);
    try {
      const analysisRes = await fetch('/api/ai/market-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          marketData: { prices: { SOL: 145.67 }, volumes: { SOL: 2500000 } },
          symbols: ['SOL'],
          timeframe: '1h',
        }),
      });
      setMarketAnalysis(await analysisRes.json());

      const predictionRes = await fetch('/api/ai/predict-price', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: 'SOL',
          historicalData: [],
          features: ['price', 'volume'],
        }),
      });
      setPredictions(await predictionRes.json());

      const performanceRes = await fetch('/api/ai/performance');
      setPerformance(await performanceRes.json());
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <button
        onClick={testAISystem}
        className="bg-blue-600 text-white px-4 py-2 rounded"
        disabled={loading}
      >
        {loading ? 'Testing AI System…' : 'Test AI System'}
      </button>

      {error && <div className="p-3 bg-rose-100 border border-rose-300 text-rose-800">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="p-4 border rounded-lg bg-white shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-lg">
                {solanaOverview?.display?.name ?? 'Solana'}
                {solanaOverview?.display?.symbol ? ` (${solanaOverview.display.symbol})` : ''}
              </h3>
              <p className="text-xs text-slate-500">
                Updated: {solanaOverview ? new Date(solanaOverview.timestamp).toLocaleString() : '—'}
              </p>
            </div>
            {solanaOverview?.display?.logo && (
              <img
                src={solanaOverview.display.logo}
                alt={solanaOverview.display.name ?? 'Solana'}
                className="h-10 w-10 rounded-full object-cover"
              />
            )}
          </div>
          {solanaOverview ? (
            <dl className="mt-3 space-y-1 text-sm text-slate-600">
              <div className="flex justify-between">
                <dt>Price</dt>
                <dd className="font-mono">${solanaOverview.price.toFixed(2)}</dd>
              </div>
              <div className="flex justify-between">
                <dt>24h Change</dt>
                <dd className="font-mono">{solanaOverview.change24h}%</dd>
              </div>
              <div className="flex justify-between">
                <dt>Market Cap</dt>
                <dd className="font-mono">${solanaOverview.marketCap.toLocaleString()}</dd>
              </div>
            </dl>
          ) : (
            <p className="mt-3 text-sm text-slate-500">Fetching Solana price overview…</p>
          )}
        </div>

        <div className="p-4 border rounded-lg bg-white shadow-sm">
          <h3 className="font-semibold text-lg">🧠 Market Analysis</h3>
          {marketAnalysis ? (
            <div className="mt-3 space-y-1 text-sm text-slate-600">
              <p>Sentiment: {marketAnalysis.analysis.sentiment}</p>
              <p>Confidence: {(marketAnalysis.analysis.confidence * 100).toFixed(1)}%</p>
              <p>Recommendation: {marketAnalysis.analysis.recommendation}</p>
              <p className="text-xs text-slate-500">Updated: {new Date(marketAnalysis.analysis.timestamp).toLocaleString()}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-500">Run the AI system test to see analysis.</p>
          )}
        </div>

        <div className="p-4 border rounded-lg bg-white shadow-sm">
          <h3 className="font-semibold text-lg">📈 Price Prediction</h3>
          {predictions ? (
            <div className="mt-3 space-y-1 text-sm text-slate-600">
              <p>Predicted: ${predictions.prediction.predictedPrice.toFixed(2)}</p>
              <p>Direction: {predictions.prediction.direction}</p>
              <p>Confidence: {(predictions.prediction.confidence * 100).toFixed(1)}%</p>
              <p className="text-xs text-slate-500">Timeframe: {predictions.prediction.timeframe}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-500">Run the AI system test to see predictions.</p>
          )}
        </div>

        <div className="p-4 border rounded-lg bg-white shadow-sm">
          <h3 className="font-semibold text-lg">📊 AI Performance</h3>
          {performance ? (
            <div className="mt-3 space-y-1 text-sm text-slate-600">
              <p>Price Model Accuracy: {(performance.performance.models.pricePrediction.accuracy * 100).toFixed(1)}%</p>
              <p>Win Rate: {(performance.performance.tradingPerformance.winRate * 100).toFixed(1)}%</p>
              <p>Total Trades: {performance.performance.tradingPerformance.totalTrades}</p>
              <p className="text-xs text-slate-500">Last Updated: {new Date(performance.performance.lastUpdated).toLocaleString()}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-500">Run the AI system test to see performance.</p>
          )}
        </div>
      </div>
    </div>
  );
}
