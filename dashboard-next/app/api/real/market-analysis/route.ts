import { NextResponse } from 'next/server'

import { createSolanaConnection, toPublicKey } from '../../../../services/solana-utils'
import { getRealMarketData } from '../../../../services/real-market-data'
import { performRealAnalysis } from '../../../../services/real-analysis-engine'

export async function POST(request: Request) {
  try {
    const { mintAddress, symbol = 'SOL' } = await request.json().catch(() => ({})) as {
      mintAddress?: string
      symbol?: string
    }

    if (!mintAddress && !symbol) {
      return NextResponse.json({
        status: 'error',
        error: 'Symbol or mint address required'
      }, { status: 400 })
    }

    console.log(`[real-analysis] request`, { mintAddress, symbol })

    const connection = createSolanaConnection('confirmed')

    // Optional: fetch token details when the SPL-Token helper is available.
    // In this minimal build, we skip fetching token mint data to avoid version/API mismatches.
    const tokenData: any | null = null

    const marketData = await getRealMarketData(symbol, mintAddress)
    const analysis = await performRealAnalysis(marketData, tokenData)

    return NextResponse.json({
      status: 'success',
      data: {
        processed: true,
        action: 'real_market_analysis',
        timestamp: new Date().toISOString(),
        analysis,
        liveData: {
          symbol,
          mintAddress,
          currentPrice: marketData.price,
          priceChange24h: marketData.priceChange24h,
          volume24h: marketData.volume24h,
          marketCap: marketData.marketCap,
          source: marketData.source
        }
      },
      message: 'Real market analysis completed successfully'
    })
  } catch (error: any) {
    console.error('[real-analysis] unexpected error', error)
    return NextResponse.json({
      status: 'error',
      error: 'Failed to perform real analysis',
      message: error?.message || 'Unknown error'
    }, { status: 500 })
  }
}
