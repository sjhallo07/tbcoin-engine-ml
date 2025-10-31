import { NextResponse } from 'next/server'

export async function GET() {
  console.log('🌐 API Route: /api/tbcoin/data called')
  const tbCoinData = {
    price: 0.000123,
    holders: 1542,
    transactions: 89234,
    marketCap: 189500,
    timestamp: new Date().toISOString(),
  }
  return NextResponse.json({
    status: 'success',
    data: tbCoinData,
    message: 'TB Coin data fetched successfully',
  })
}
