'use client';

import { motion } from 'framer-motion';

import type { AIPrediction } from '../services/deepseek';

interface PredictionCardProps {
  title: string;
  coin: { name: string; symbol: string; current_price: number };
  prediction: AIPrediction;
}

function PredictionCard({ title, coin, prediction }: PredictionCardProps) {
  return (
    <motion.div
      className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-lg"
      whileHover={{ scale: 1.01 }}
      transition={{ type: 'spring', stiffness: 200, damping: 15 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xl font-semibold text-white">{title}</h3>
          <p className="text-gray-400 uppercase text-sm">{coin.symbol}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-blockchain-blue">
            ${coin.current_price.toLocaleString()}
          </p>
          <p className="text-sm text-gray-400">Current Price</p>
        </div>
      </div>

      <div className="bg-gray-900 rounded-xl p-4 border border-gray-700 mb-4">
        <p className="text-lg font-semibold text-blockchain-green">
          {prediction.prediction}
        </p>
        <p className="text-sm text-gray-300 mt-2 whitespace-pre-line">
          {prediction.reasoning}
        </p>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {prediction.factors.map((factor) => (
          <span
            key={factor}
            className="px-3 py-1 bg-gray-900 border border-gray-700 rounded-full text-sm text-gray-300"
          >
            {factor}
          </span>
        ))}
      </div>

      <div className="flex justify-between items-center text-sm text-gray-400">
        <span>
          Confidence: <strong className="text-white">{Math.round(prediction.confidence * 100)}%</strong>
        </span>
        <span>{new Date(prediction.timestamp).toLocaleString()}</span>
      </div>
    </motion.div>
  );
}

export default function AIPredictions({ predictions }: { predictions: any[] }) {
  if (!predictions.length) {
    return (
      <div className="bg-gray-800 rounded-2xl p-6 text-gray-300">
        AI predictions will appear here once enough market data is collected.
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {predictions.map((item) => (
        <div key={item.id ?? item.name}>
          <PredictionCard
            title={`${item.name} (${item.symbol.toUpperCase()})`}
            coin={item}
            prediction={item.prediction}
          />
        </div>
      ))}
    </div>
  );
}
