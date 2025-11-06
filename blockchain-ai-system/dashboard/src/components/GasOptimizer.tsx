'use client';

import { useEffect, useState } from 'react';

import type { AIPrediction } from '../services/deepseek';
import { deepSeekService } from '../services/deepseek';

interface GasMetrics {
  baseFee: number;
  priorityFee: number;
  pendingTransactions: number;
  blockUtilization: number;
}

export default function GasOptimizer() {
  const [metrics, setMetrics] = useState<GasMetrics | null>(null);
  const [prediction, setPrediction] = useState<AIPrediction | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const run = async () => {
      const sampleMetrics: GasMetrics = {
        baseFee: 24 + Math.random() * 10,
        priorityFee: 1.5 + Math.random(),
        pendingTransactions: Math.floor(100_000 + Math.random() * 75_000),
        blockUtilization: 0.7 + Math.random() * 0.2,
      };
      setMetrics(sampleMetrics);
      const aiPrediction = await deepSeekService.predictGasOptimization(sampleMetrics);
      setPrediction(aiPrediction);
      setLoading(false);
    };

    void run();
  }, []);

  if (loading || !metrics || !prediction) {
    return (
      <div className="bg-gray-800 rounded-2xl p-6 text-gray-300">
        Loading gas optimization insights...
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
        <h2 className="text-xl font-semibold mb-4">⚙️ Network Metrics</h2>
        <dl className="space-y-3 text-gray-300">
          <div className="flex justify-between">
            <dt>Base Fee</dt>
            <dd className="text-white">{metrics.baseFee.toFixed(2)} Gwei</dd>
          </div>
          <div className="flex justify-between">
            <dt>Priority Fee</dt>
            <dd className="text-white">{metrics.priorityFee.toFixed(2)} Gwei</dd>
          </div>
          <div className="flex justify-between">
            <dt>Pending Transactions</dt>
            <dd className="text-white">{metrics.pendingTransactions.toLocaleString()}</dd>
          </div>
          <div className="flex justify-between">
            <dt>Block Utilisation</dt>
            <dd className="text-white">{Math.round(metrics.blockUtilization * 100)}%</dd>
          </div>
        </dl>
      </div>

      <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
        <h2 className="text-xl font-semibold mb-4">🤖 AI Recommendation</h2>
        <p className="text-blockchain-green text-lg font-semibold">
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
    </div>
  );
}
