export type SupportedNetwork = 'solana' | 'ethereum' | 'polygon'

export type TokenSpec = {
  address: string
  network: SupportedNetwork
}

export type TokenAnalysisOptions = {
  minLiquidityUSD?: number
  liquidityFloorUSD?: number
  concentrationThreshold?: number
}

export type SimpleTokenMetrics = {
  address: string
  network: SupportedNetwork
  score: number
  liquidityUSD: number
  holders?: number
  notes?: string[]
}

function pseudoRandomFromString(input: string): number {
  let hash = 0
  for (let i = 0; i < input.length; i += 1) {
    hash = (hash * 31 + input.charCodeAt(i)) >>> 0
  }
  return hash / 0xffffffff
}

function generateMockMetrics(token: TokenSpec, options: TokenAnalysisOptions = {}): SimpleTokenMetrics {
  const seed = `${token.network}:${token.address}`
  const rnd = pseudoRandomFromString(seed)
  const baseLiquidity = 10_000 + Math.floor(rnd * 250_000)
  const score = Math.max(1, Math.min(100, Math.floor(40 + rnd * 60)))
  const liquidityUSD = Math.max(
    options.minLiquidityUSD ?? 0,
    options.liquidityFloorUSD ?? 0,
    baseLiquidity
  )
  const holders = 100 + Math.floor(rnd * 50_000)
  const notes: string[] = []

  if ((options.concentrationThreshold ?? 0) > 0) {
    notes.push(`Applied concentrationThreshold=${options.concentrationThreshold}`)
  }
  if ((options.minLiquidityUSD ?? 0) > 0) {
    notes.push(`Enforced minLiquidityUSD=${options.minLiquidityUSD}`)
  }
  if ((options.liquidityFloorUSD ?? 0) > 0) {
    notes.push(`Applied liquidityFloorUSD=${options.liquidityFloorUSD}`)
  }

  return { address: token.address, network: token.network, score, liquidityUSD, holders, notes }
}

export async function getTokenAnalysis(
  tokens: TokenSpec[],
  options: TokenAnalysisOptions = {}
): Promise<SimpleTokenMetrics[]> {
  // In a real implementation, call out to chain/indexers and market APIs here
  return tokens.map((t) => generateMockMetrics(t, options))
}

export async function postTokenAnalysis(
  tokens: TokenSpec[],
  options: TokenAnalysisOptions = {}
): Promise<{ status: 'ok'; processed: number; data: SimpleTokenMetrics[] }> {
  const data = await getTokenAnalysis(tokens, options)
  return { status: 'ok', processed: data.length, data }
}
