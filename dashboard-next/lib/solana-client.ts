// Minimal stub implementations to support dev/test without external Solana APIs.
// These functions are imported by services that gracefully handle nulls/missing data.

export async function getTokenMetadata(identifier: string): Promise<{
  name?: string
  symbol?: string
  image?: string
  description?: string
  externalUrl?: string
  updateAuthority?: string
  createdAt?: number
  uri?: string
} | null> {
  const id = String(identifier || '').toUpperCase()
  if (id === 'SOL' || id === 'SO1111111111111111111111111111111111111112') {
    return {
      name: 'Solana',
      symbol: 'SOL',
      image: 'https://assets.coingecko.com/coins/images/4128/large/solana.png?1640133422',
      description: 'Solana network token (stub metadata)',
      externalUrl: 'https://solana.com',
      updateAuthority: null as any,
    }
  }
  return null
}

export async function getTokenSupply(_mint: string): Promise<{
  amount: string
  decimals: number
  uiAmountString: string
}> {
  // Return a synthetic 9-decimal supply
  return { amount: '1000000000000', decimals: 9, uiAmountString: '1000000' }
}

export async function getAccountInfo(_address: string): Promise<any> {
  // Minimal parsed layout to satisfy consumers
  return {
    owner: 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
    data: { parsed: { info: { decimals: 9, supply: '1000000000000', mintAuthority: null, freezeAuthority: null } } },
  }
}

export async function getTokenLargestAccounts(_mint: string): Promise<Array<{ address: string; amount: string; uiAmount: number; uiAmountString: string }>> {
  // Ten synthetic holder accounts
  return Array.from({ length: 10 }).map((_, i) => ({
    address: `StubHolder${i + 1}`,
    amount: '1000000000',
    uiAmount: 1_000_000,
    uiAmountString: '1000000',
  }))
}

export async function getPriceFromPublicApis(_symbol: string, _mint?: string): Promise<{ price: number; volume24h: number; priceChange24h: number }>{
  // Helper used by services; provide stable demo values
  return { price: 1, volume24h: 0, priceChange24h: 0 }
}

export type PublicPrice = Awaited<ReturnType<typeof getPriceFromPublicApis>>

// --- Analytics helpers used by services/token-analysis.ts ---
export function calculateGiniCoefficient(items: Array<{ amount: number }>): number {
  const values = items.map((i) => Math.max(0, Number(i.amount) || 0)).sort((a, b) => a - b)
  const n = values.length
  if (n === 0) return 0
  const cum = values.reduce((acc, v, i) => acc + v * (i + 1), 0)
  const total = values.reduce((a, b) => a + b, 0)
  if (total === 0) return 0
  return (2 * cum) / (n * total) - (n + 1) / n
}

export function calculateTopNPercentage(items: Array<{ amount: number }>, total: number, n: number): number {
  if (!items.length || total <= 0) return 0
  const top = [...items].sort((a, b) => b.amount - a.amount).slice(0, n)
  const sumTop = top.reduce((sum, it) => sum + (Number(it.amount) || 0), 0)
  return (sumTop / total) * 100
}

export function calculateAverageBalance(items: Array<{ amount: number }>): number {
  if (!items.length) return 0
  const total = items.reduce((sum, it) => sum + (Number(it.amount) || 0), 0)
  return total / items.length
}
