import type { MarketData } from './real-market-data'

export type AnalysisResult = {
  sentiment: 'very_bullish' | 'bullish' | 'neutral' | 'bearish' | 'very_bearish'
  confidence: number
  recommendation: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell'
  riskLevel: 'very_high' | 'high' | 'medium' | 'low'
  analysisMetrics: {
    volatility: number
    trendStrength: number
    marketCondition: 'uptrend' | 'downtrend' | 'sideways' | 'unknown'
  }
}

export async function performRealAnalysis(marketData: MarketData, tokenData: any | null): Promise<AnalysisResult> {
  const sentiment = calculateRealSentiment(marketData)
  const confidence = calculateConfidence(marketData)
  const recommendation = generateRecommendation(sentiment, confidence)
  const riskLevel = assessRiskLevel(marketData, tokenData)

  return {
    sentiment,
    confidence,
    recommendation,
    riskLevel,
    analysisMetrics: {
      volatility: calculateVolatility(marketData),
      trendStrength: calculateTrendStrength(marketData),
      marketCondition: assessMarketCondition(marketData)
    }
  }
}

function calculateRealSentiment({ priceChange24h, volume24h }: MarketData): AnalysisResult['sentiment'] {
  if (priceChange24h > 5 && volume24h > 1_000_000) return 'very_bullish'
  if (priceChange24h > 2 && volume24h > 500_000) return 'bullish'
  if (priceChange24h < -5 && volume24h > 1_000_000) return 'very_bearish'
  if (priceChange24h < -2 && volume24h > 500_000) return 'bearish'
  if (Math.abs(priceChange24h) < 2) return 'neutral'
  return priceChange24h > 0 ? 'bullish' : 'bearish'
}

function calculateConfidence({ volume24h, source }: MarketData): number {
  let confidence = 0.5

  if (volume24h > 10_000_000) confidence += 0.3
  else if (volume24h > 1_000_000) confidence += 0.2
  else if (volume24h > 100_000) confidence += 0.1

  if (source === 'coingecko') confidence += 0.1
  if (source === 'birdeye') confidence += 0.05

  return Math.min(0.95, Math.max(0.3, confidence))
}

function generateRecommendation(sentiment: AnalysisResult['sentiment'], confidence: number): AnalysisResult['recommendation'] {
  if (confidence < 0.5) return 'hold'

  switch (sentiment) {
    case 'very_bullish':
      return confidence > 0.7 ? 'strong_buy' : 'buy'
    case 'bullish':
      return 'buy'
    case 'bearish':
      return 'sell'
    case 'very_bearish':
      return confidence > 0.7 ? 'strong_sell' : 'sell'
    default:
      return 'hold'
  }
}

function assessRiskLevel({ priceChange24h, volume24h }: MarketData, tokenData: any | null): AnalysisResult['riskLevel'] {
  const volatility = Math.abs(priceChange24h)
  const mintSupply = Number(tokenData?.supply ?? 0)

  if (volatility > 20 && volume24h < 100_000) return 'very_high'
  if (volatility > 15 || volume24h < 50_000) return 'high'
  if (volatility > 8 || volume24h < 100_000) return 'medium'
  if (volatility < 5 && volume24h > 1_000_000) return 'low'

  // heuristics for extremely low supply tokens
  if (mintSupply > 0 && mintSupply < 1_000_000) return 'high'

  return 'medium'
}

function calculateVolatility({ priceChange24h }: MarketData): number {
  return Number(Math.abs(priceChange24h).toFixed(2))
}

function calculateTrendStrength({ priceChange24h }: MarketData): number {
  const strength = Math.min(1, Math.max(-1, priceChange24h / 10))
  return Number(Math.abs(strength).toFixed(2))
}

function assessMarketCondition(marketData: MarketData): AnalysisResult['analysisMetrics']['marketCondition'] {
  if (marketData.priceChange24h > 2 && marketData.volume24h > 500_000) return 'uptrend'
  if (marketData.priceChange24h < -2 && marketData.volume24h > 500_000) return 'downtrend'
  if (Math.abs(marketData.priceChange24h) <= 2) return 'sideways'
  return 'unknown'
}
