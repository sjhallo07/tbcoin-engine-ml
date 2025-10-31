import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  console.log('🌐 API Route: /api/solana/test (POST) called');
  const body = await request.json();
  const responseData = {
    processed: true,
    action: body.action,
    timestamp: new Date().toISOString(),
    analysis: {
      sentiment: 'bullish',
      confidence: 0.78,
      recommendation: 'hold',
      riskLevel: 'medium',
    },
  };
  return NextResponse.json({
    status: 'success',
    data: responseData,
    message: 'Test data processed successfully',
  });
}
