import { NextResponse } from 'next/server'

// Demo endpoint disabled. Use /api/real/market-analysis or /api/real/token-info.
export async function GET() {
  return NextResponse.json(
    { status: 'gone', message: 'This demo endpoint has been removed. Use /api/real/*.' },
    { status: 410 }
  )
}
