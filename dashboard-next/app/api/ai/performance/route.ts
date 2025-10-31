import { NextResponse } from 'next/server';

export async function GET() {
  const performance = {
    models: {
      pricePrediction: { accuracy: 0.87, lastTraining: '2024-01-15T10:00:00Z' },
      sentimentAnalysis: { accuracy: 0.92, lastTraining: '2024-01-15T09:30:00Z' },
      anomalyDetection: { accuracy: 0.95, lastTraining: '2024-01-14T15:00:00Z' },
    },
    tradingPerformance: {
      totalTrades: 154,
      winRate: 0.73,
      totalProfit: 0.154,
      sharpeRatio: 1.45,
    },
    lastUpdated: new Date().toISOString(),
  };

  return NextResponse.json({ status: 'success', performance });
}
