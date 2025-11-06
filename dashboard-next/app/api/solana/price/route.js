import { NextResponse } from 'next/server'

export async function GET() {
  console.log('🌐 API Route: /api/solana/price called')
  const solanaData = {
    price: 145.67,
    change24h: 2.34,
    marketCap: 64500000000,
    volume24h: 2500000000,
    timestamp: new Date().toISOString(),
  }
  return NextResponse.json({
    status: 'success',
    data: solanaData,
    message: 'Solana price data fetched successfully',
  })
}
