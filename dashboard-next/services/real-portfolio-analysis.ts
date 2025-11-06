import { TOKEN_PROGRAM_ID } from '@solana/spl-token'

import { createSolanaConnection, toPublicKey } from './solana-utils'
import { getRealMarketData } from './real-market-data'

export type PortfolioAnalysis = {
  wallet: string
  totalValueUsd: number
  holdings: Array<{
    mint: string
    amountRaw: string
    uiAmount: number
    decimals: number
    priceUsd: number
    valueUsd: number
    source: string
  }>
  solBalance?: {
    lamports: number
    sol: number
    priceUsd: number
    valueUsd: number
    source: string
  }
  summary: {
    tokens: number
    largestHolding?: string
    riskLevel: 'low' | 'medium' | 'high'
  }
}

export async function analyzeRealPortfolio(walletAddress: string, filterTokens?: string[]): Promise<PortfolioAnalysis> {
  if (!walletAddress) {
    throw new Error('Wallet address is required')
  }

  const connection = createSolanaConnection()
  const ownerKey = toPublicKey(walletAddress)

  const tokenAccounts = await connection.getParsedTokenAccountsByOwner(ownerKey, {
    programId: TOKEN_PROGRAM_ID
  })

  const tokenFilterSet = filterTokens && filterTokens.length > 0 ? new Set(filterTokens.map((t) => t.toLowerCase())) : null

  const holdings = tokenAccounts.value
    .map((account) => {
      const info = account.account.data.parsed?.info
      const tokenAmount = info?.tokenAmount
      const mint = info?.mint as string | undefined

      if (!mint || !tokenAmount) return null
      if (Number(tokenAmount.amount) === 0) return null

      if (tokenFilterSet && !tokenFilterSet.has(mint.toLowerCase())) {
        return null
      }

      const decimals = Number(tokenAmount.decimals)
      const uiAmount = Number(tokenAmount.uiAmountString ?? tokenAmount.uiAmount ?? 0)

      return {
        mint,
        decimals,
        amountRaw: tokenAmount.amount as string,
        uiAmount
      }
    })
    .filter(Boolean) as Array<{ mint: string; decimals: number; amountRaw: string; uiAmount: number }>

  const enrichedHoldings = await Promise.all(
    holdings
      .sort((a, b) => b.uiAmount - a.uiAmount)
      .slice(0, 20)
      .map(async (holding) => {
        const marketData = await getRealMarketData('UNKNOWN', holding.mint)
        const price = marketData?.price ?? 0
        const value = Number((holding.uiAmount * price).toFixed(2))

        return {
          mint: holding.mint,
          amountRaw: holding.amountRaw,
          uiAmount: Number(holding.uiAmount.toFixed(holding.decimals > 4 ? 4 : holding.decimals)),
          decimals: holding.decimals,
          priceUsd: Number(price.toFixed(holding.decimals > 2 ? 6 : 4)),
          valueUsd: value,
          source: marketData.source
        }
      })
  )

  const solLamports = await connection.getBalance(ownerKey)
  const sol = solLamports / 1_000_000_000
  const solMarketData = await getRealMarketData('SOL', 'So11111111111111111111111111111111111111112')
  const solValueUsd = Number((sol * solMarketData.price).toFixed(2))

  const totalValue = enrichedHoldings.reduce((sum, holding) => sum + holding.valueUsd, 0) + solValueUsd

  const largestHolding = [...enrichedHoldings]
    .sort((a, b) => b.valueUsd - a.valueUsd)[0]?.mint

  const riskLevel = determinePortfolioRisk(enrichedHoldings, solValueUsd, totalValue)

  return {
    wallet: walletAddress,
    totalValueUsd: Number(totalValue.toFixed(2)),
    holdings: enrichedHoldings,
    solBalance: {
      lamports: solLamports,
      sol: Number(sol.toFixed(4)),
      priceUsd: solMarketData.price,
      valueUsd: solValueUsd,
      source: solMarketData.source
    },
    summary: {
      tokens: enrichedHoldings.length,
      largestHolding,
      riskLevel
    }
  }
}

function determinePortfolioRisk(holdings: PortfolioAnalysis['holdings'], solValueUsd: number, totalValue: number): PortfolioAnalysis['summary']['riskLevel'] {
  if (totalValue === 0) return 'medium'

  const concentrationThreshold = totalValue * 0.5
  const hasConcentration = holdings.some((h) => h.valueUsd > concentrationThreshold) || solValueUsd > concentrationThreshold

  if (hasConcentration) return 'high'

  const lowExposureCounts = holdings.filter((h) => h.valueUsd < totalValue * 0.05).length

  if (lowExposureCounts / Math.max(holdings.length, 1) > 0.6) {
    return 'medium'
  }

  return 'low'
}
