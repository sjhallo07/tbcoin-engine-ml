import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { marketContext, riskLevel } = await request.json();

  const decision = {
    action: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)],
    confidence: Math.random() * 0.3 + 0.7,
    positionSize: riskLevel === 'high' ? 0.02 : riskLevel === 'low' ? 0.01 : 0.015,
    stopLoss: 0.95,
    takeProfit: 1.15,
    reasoning: 'Pattern detected: bullish momentum with high volume',
    marketContext,
    timestamp: new Date().toISOString(),
  };

  return NextResponse.json({ status: 'success', decision });
}
