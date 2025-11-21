'use client';

import { useEffect, useState } from 'react';

import type { AIPrediction } from '../services/deepseek';
import { deepSeekService } from '../services/deepseek';

interface MarketSpread {
  exchange: string;
  price: number;
  liquidity: number;
}

export default function ArbitrageDetector() {
  const [spreads, setSpreads] = useState<MarketSpread[]>([]);
  const [prediction, setPrediction] = useState<AIPrediction | null>(null);

  useEffect(() => {
    const run = async () => {
      const sampleSpreads: MarketSpread[] = [
        { exchange: 'Binance', price: 45_200 + Math.random() * 200, liquidity: 85 },
        { exchange: 'Coinbase', price: 45_050 + Math.random() * 200, liquidity: 70 },
        { exchange: 'Kraken', price: 45_400 + Math.random() * 200, liquidity: 60 },
      ];
      setSpreads(sampleSpreads);
      const aiPrediction = await deepSeekService.detectArbitrageOpportunities(sampleSpreads);
      setPrediction(aiPrediction);
    };

    void run();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
        <h2 className="text-xl font-semibold mb-4">🔍 Exchange Price Spreads</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {spreads.map((spread) => (
            <div key={spread.exchange} className="bg-gray-900 rounded-xl p-4 border border-gray-700">
              <h3 className="font-semibold text-white mb-2">{spread.exchange}</h3>
              <p className="text-gray-300">Price: ${spread.price.toLocaleString()}</p>
              <p className="text-gray-400 text-sm">Liquidity Score: {spread.liquidity}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
        <h2 className="text-xl font-semibold mb-4">🤖 AI Arbitrage Insight</h2>
        {prediction ? (
          <div>
            <p className="text-blockchain-purple text-lg font-semibold">
              {prediction.prediction}
            </p>
            <p className="text-gray-300 mt-3 whitespace-pre-line">{prediction.reasoning}</p>
            <div className="mt-4 text-sm text-gray-400 flex justify-between">
              <span>Confidence: {Math.round(prediction.confidence * 100)}%</span>
              <span>{new Date(prediction.timestamp).toLocaleTimeString()}</span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {prediction.factors.map((factor) => (
                <span
                  key={factor}
                  className="px-3 py-1 bg-gray-900 border border-gray-700 rounded-full text-sm text-gray-300"
                >
                  {factor}
                </span>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-gray-300">Generating AI prediction...</p>
        )}
      </div>
    </div>
  );
}
