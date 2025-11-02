import { NextResponse } from 'next/server'

import { analyzeRealPortfolio } from '../../../../services/real-portfolio-analysis'

export async function POST(request: Request) {
  try {
    const { walletAddress, tokens } = await request.json().catch(() => ({})) as {
      walletAddress?: string
      tokens?: string[]
    }

    if (!walletAddress) {
      return NextResponse.json({
        status: 'error',
        error: 'Wallet address required'
      }, { status: 400 })
    }

    const analysis = await analyzeRealPortfolio(walletAddress, tokens)

    return NextResponse.json({
      status: 'success',
      data: analysis,
      message: 'Real portfolio analysis completed'
    })
  } catch (error: any) {
    console.error('[real-portfolio] error', error)
    return NextResponse.json({
      status: 'error',
      error: 'Portfolio analysis failed',
      message: error?.message || 'Unknown error'
    }, { status: 500 })
  }
}
