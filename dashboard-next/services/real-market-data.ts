export type MarketData = {
  price: number
  priceChange24h: number
  volume24h: number
  marketCap?: number
  source: 'coingecko' | 'birdeye' | 'jupiter' | 'fallback'
}

const COINGECKO_TOKEN_MAP: Record<string, string> = {
  SOL: 'solana',
  USDC: 'usd-coin',
  USDT: 'tether',
  BONK: 'bonk',
  JUP: 'jupiter-exchange-token',
  RAY: 'raydium'
}

export async function getRealMarketData(symbol: string, mintAddress?: string): Promise<MarketData> {
  const normalisedSymbol = symbol?.toUpperCase() || 'SOL'

  const attempts = [
    () => getCoinGeckoData(normalisedSymbol),
    () => getBirdeyeData(mintAddress || normalisedSymbol),
    () => getJupiterPriceData(mintAddress)
  ]

  for (const attempt of attempts) {
    try {
      const result = await attempt()
      if (result) return result
    } catch (error) {
      console.warn('[market-data] provider failed', error)
    }
  }

  return getFallbackMarketData(normalisedSymbol)
}

async function getCoinGeckoData(symbol: string): Promise<MarketData | null> {
  const coinId = COINGECKO_TOKEN_MAP[symbol] || symbol.toLowerCase()

  try {
    const response = await fetch(
      `https://api.coingecko.com/api/v3/simple/price?ids=${coinId}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true`,
      {
        headers: { Accept: 'application/json' },
        next: { revalidate: 30 }
      }
    )

    if (!response.ok) return null

    const payload = (await response.json()) as Record<string, any>
    const coinData = payload[coinId]
    if (!coinData) return null

    return {
      price: Number(coinData.usd ?? 0),
      priceChange24h: Number(coinData.usd_24h_change ?? 0),
      volume24h: Number(coinData.usd_24h_vol ?? 0),
      marketCap: Number(coinData.usd_market_cap ?? 0),
      source: 'coingecko'
    }
  } catch (error) {
    console.warn('CoinGecko lookup failed', error)
    return null
  }
}

async function getBirdeyeData(identifier: string): Promise<MarketData | null> {
  if (!identifier) return null

  try {
    const response = await fetch(`https://public-api.birdeye.so/public/price?address=${identifier}`,
      {
        headers: {
          'Accept': 'application/json',
          'X-API-KEY': process.env.BIRDEYE_API_KEY || ''
        },
        next: { revalidate: 15 }
      }
    )

    if (!response.ok) return null

    const payload = (await response.json()) as { data?: any }
    const data = payload?.data
    if (!data || data.value === undefined) return null

    return {
      price: Number(data.value ?? 0),
      priceChange24h: Number(data.change24h ?? 0),
      volume24h: Number(data.volume24h ?? 0),
      source: 'birdeye'
    }
  } catch (error) {
    console.warn('Birdeye lookup failed', error)
    return null
  }
}

async function getJupiterPriceData(mintAddress?: string): Promise<MarketData | null> {
  if (!mintAddress) return null

  try {
    const response = await fetch(`https://price.jup.ag/v4/price?ids=${mintAddress}`, {
      headers: { Accept: 'application/json' },
      next: { revalidate: 10 }
    })

    if (!response.ok) return null

    const payload = (await response.json()) as { data?: Record<string, any> }
    const data = payload?.data?.[mintAddress]
    if (!data || data.price === undefined) return null

    return {
      price: Number(data.price ?? 0),
      priceChange24h: Number(data.priceChange24h ?? 0),
      volume24h: Number(data.volume24h ?? 0),
      source: 'jupiter'
    }
  } catch (error) {
    console.warn('Jupiter lookup failed', error)
    return null
  }
}

function getFallbackMarketData(symbol: string): MarketData {
  const fallbackTable: Record<string, MarketData> = {
    SOL: { price: 98.45, priceChange24h: 2.1, volume24h: 0, source: 'fallback' },
    USDC: { price: 1.0, priceChange24h: 0, volume24h: 0, source: 'fallback' },
    USDT: { price: 1.0, priceChange24h: 0, volume24h: 0, source: 'fallback' },
    BONK: { price: 0.000012, priceChange24h: -3.2, volume24h: 0, source: 'fallback' }
  }

  const base = fallbackTable[symbol] || { price: 0.01, priceChange24h: 0, volume24h: 0, source: 'fallback' }
  return { ...base }
}
