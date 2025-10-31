import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { symbol, historicalData, features } = await request.json();

  const basePrices: Record<string, number> = { SOL: 145, TBCOIN: 0.000123, BTC: 42000 };
  const currentPrice = basePrices[symbol as keyof typeof basePrices] ?? 1;

  const priceShift = Math.random() * 0.1 - 0.05;
  const prediction = {
    predictedPrice: Number((currentPrice * (1 + priceShift)).toFixed(4)),
    confidence: Math.random() * 0.3 + 0.7,
    timeframe: '24h',
    direction: priceShift >= 0 ? 'up' : 'down',
    inputs: { historicalDataLength: Array.isArray(historicalData) ? historicalData.length : 0, features },
    timestamp: new Date().toISOString(),
  };

  return NextResponse.json({ status: 'success', prediction });
}
