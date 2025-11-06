import { NextResponse } from 'next/server'

import { fetchLiquidityAnalysis } from '../../../../../services/token-analysis'

export async function GET(request: Request, { params }: { params: { mint: string } }) {
  const { mint } = params

  try {
    const liquidity = await fetchLiquidityAnalysis(mint)
    return NextResponse.json(liquidity)
  } catch (error: any) {
    return NextResponse.json({ error: String(error?.message || error) }, { status: 500 })
  }
}
